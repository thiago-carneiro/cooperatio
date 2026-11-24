#!/usr/bin/env python3
"""The vault of a cell: the one write path for its artifacts, one owner per artifact, versions and a journal.

Usage (from the cell folder, or with --cell; every command takes --cell and --store):
    vault.py init --owners owners.json --keys-out FILE      (FILE outside the cell; written once, 0600)
    vault.py list
    vault.py read ID [--version N]
    vault.py history ID
    vault.py diff ID VERSION_A VERSION_B
    vault.py write ID FILE --key-file F --reason "..."      (only the owner of ID; creates version N+1; FILE - is stdin)
    vault.py revert ID VERSION --key-file F --reason "..."  (only the owner; a new version equal to the old one)
    vault.py export [--dir D]                               (read-only copies of the latest versions)
    vault.py verify [--dir D]                               (exports equal to the vault; journal chain intact)
    vault.py request delete|change-owner ID [--new-owner ROLE] --key-file F --reason "..."
    vault.py execute REQUEST --key-file F                   (only after the owner authorized it with authorizer.py)
    vault.py self-test

Every command that takes a key accepts --key K or --key-file F; prefer --key-file, so that a key never
appears in a transcript. The key file holds one role's key and nothing else.

owners.json: {"roles": ["writer", ...], "owners": {"<id or prefix*>": "<role>"},
              "export_to": "artifacts", "suffix": ".json"}
An exact id wins over a prefix pattern, and a longer prefix over a shorter one. Once an artifact has a
version, its owner is the one recorded in the vault, and only an authorized change-owner moves it.

It is not strong security. The store is compressed, XORed with a stream keyed by each file's name and
encoded in base85, under hashed object names: enough that an agent does not edit an artifact around the
tool on its own initiative, not enough to stop anyone who reads this script. Everyone can read every
artifact (read, the exports); only the owner's key writes it. Every write is a new immutable version,
addressed by the sha256 of its content, with its author and reason; nothing is ever overwritten. The
journal is append-only and each line carries the sha256 of the line before it. Deleting an artifact or
changing its owner is a request that runs only after the owner authorizes it with a TOTP code
(authorizer.py). The store records a timestamp per version and per journal line: keep it out of a material
distributed for anonymity.

The cell is --cell, else the COOPERATIO_CELL variable, else the current folder; the store is --store,
else COOPERATIO_VAULT_DIR, else <cell>/.vault.

Exit codes: 0 done; 1 refused (a wrong key, not the owner, not authorized, a failed verify);
2 invalid input, a vault in an unexpected state, or Python below 3.9.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import base64  # noqa: E402
import contextlib  # noqa: E402
import difflib  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import secrets  # noqa: E402
import stat  # noqa: E402
import time  # noqa: E402
import zlib  # noqa: E402
from pathlib import Path  # noqa: E402

try:
    import fcntl
except ImportError:  # Windows
    fcntl = None
    import msvcrt

MIN_PYTHON = (3, 9)  # the interpreter the material is tested on (v0.6.0)
SENSITIVE_ACTIONS = ("delete", "change-owner")
AUTHORIZATION_VALIDITY_S = 300
KEY_PREFIX = "vk-"
ARTIFACT_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9][A-Za-z0-9._-]*)*")
GENESIS = "0" * 64

EXIT_OK = 0
EXIT_REFUSED = 1
EXIT_USAGE = 2


class Refused(Exception):
    """The vault refused the action: a wrong key, not the owner, not authorized."""


class VaultError(Exception):
    """Invalid input or a vault in an unexpected state."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stream(seed: bytes, n: int) -> bytes:
    out, i = bytearray(), 0
    while len(out) < n:
        out += hashlib.sha256(seed + i.to_bytes(4, "big")).digest()
        i += 1
    return bytes(out[:n])


def obfuscate(data: bytes, seed: bytes) -> bytes:
    z = zlib.compress(data, 9)
    return base64.b85encode(bytes(a ^ b for a, b in zip(z, _stream(b"vault:" + seed, len(z)))))


def deobfuscate(text: bytes, seed: bytes) -> bytes:
    z = base64.b85decode(text)
    return zlib.decompress(bytes(a ^ b for a, b in zip(z, _stream(b"vault:" + seed, len(z)))))


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def inside(path: Path, folder: Path) -> bool:
    try:
        path.resolve().relative_to(folder.resolve())
        return True
    except ValueError:
        return False


def default_cell() -> Path:
    return Path(os.environ.get("COOPERATIO_CELL") or os.getcwd())


def default_store(cell: Path) -> Path:
    return Path(os.environ.get("COOPERATIO_VAULT_DIR") or cell / ".vault")


class Vault:
    def __init__(self, cell: Path, store: Path | None = None) -> None:
        self.cell = Path(cell)
        self.store = Path(store) if store is not None else default_store(self.cell)

    # The obfuscated state files.
    def _path(self, *parts: str) -> Path:
        return self.store.joinpath(*parts)

    def read_state(self, name: str, default):
        f = self._path(name)
        if not f.exists():
            return default
        return json.loads(deobfuscate(f.read_bytes(), name.encode()))

    def write_state(self, name: str, obj) -> None:
        tmp = self._path(name + ".tmp")
        data = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()
        tmp.write_bytes(obfuscate(data, name.encode()))
        os.replace(tmp, self._path(name))

    @contextlib.contextmanager
    def lock(self):
        """One writer at a time; never nested (a second lock in the same process waits for the first)."""
        with open(self._path("lock"), "a+b") as handle:
            if fcntl is not None:
                fcntl.flock(handle, fcntl.LOCK_EX)
            else:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                if fcntl is not None:
                    fcntl.flock(handle, fcntl.LOCK_UN)
                else:
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)

    def journal(self, event: dict) -> None:
        """Append one obfuscated line carrying the sha256 of the line before it."""
        f = self._path("journal")
        lines = f.read_bytes().splitlines() if f.exists() else []
        entry = {"ts": now(), **event, "prev": sha256(lines[-1]) if lines else GENESIS}
        with open(f, "ab") as handle:
            handle.write(obfuscate(json.dumps(entry, ensure_ascii=False, sort_keys=True).encode(),
                                   b"journal") + b"\n")

    def journal_entries(self) -> list:
        f = self._path("journal")
        if not f.exists():
            return []
        return [json.loads(deobfuscate(line, b"journal")) for line in f.read_bytes().splitlines()]

    def config(self) -> dict:
        cfg = self.read_state("config", None)
        if cfg is None:
            raise VaultError(f"no vault at {self.store} (vault.py init)")
        return cfg

    def index(self) -> dict:
        return self.read_state("index", {})

    # Keys and owners.
    def role_for(self, key: str | None) -> str:
        if not key:
            raise VaultError("missing --key or --key-file")
        cfg = self.config()
        hashed = sha256((cfg["salt"] + key).encode())
        for role, h in cfg["keys"].items():
            if secrets.compare_digest(h, hashed):
                return role
        raise Refused("invalid key")

    def owner_of(self, ident: str) -> str | None:
        entry = self.index().get(ident)
        if entry and entry.get("owner"):
            return entry["owner"]
        owners = self.config()["owners"]
        if ident in owners:
            return owners[ident]
        prefixes = [p for p in owners if p.endswith("*") and ident.startswith(p[:-1])]
        return owners[max(prefixes, key=len)] if prefixes else None

    # Objects and versions.
    def object(self, h: str) -> bytes:
        return deobfuscate(self._path("objects", h).read_bytes(), h.encode())

    def version(self, ident: str, n=None) -> tuple:
        entry = self.index().get(ident)
        if not entry or entry.get("deleted"):
            raise VaultError(f"'{ident}' is not in the vault")
        versions = entry["versions"]
        if n is None:
            v = versions[-1]
        else:
            try:
                wanted = int(n)
            except ValueError:
                raise VaultError(f"'{n}' is not a version number") from None
            v = next((x for x in versions if x["n"] == wanted), None)
        if v is None:
            raise VaultError(f"'{ident}' has no version {n}")
        return v, self.object(v["obj"])

    # Commands.
    def init(self, owners_file: Path, keys_out: Path) -> str:
        if self._path("config").exists():
            raise VaultError(f"a vault already exists at {self.store}")
        try:
            owners = json.loads(Path(owners_file).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise VaultError(f"cannot read the owners file: {error}") from None
        roles = owners.get("roles")
        if not isinstance(roles, list) or not roles or not all(isinstance(r, str) and r for r in roles):
            raise VaultError("the owners file needs 'roles', a non-empty list of role names")
        mapping = owners.get("owners", {})
        if not isinstance(mapping, dict) or any(r not in roles for r in mapping.values()):
            raise VaultError("every role in 'owners' has to be one of 'roles'")
        if inside(Path(keys_out), self.cell):
            raise VaultError("--keys-out has to be outside the cell, so that no role reads another's key")
        self._path("objects").mkdir(parents=True, exist_ok=True)
        salt = secrets.token_hex(16)
        keys = {role: KEY_PREFIX + secrets.token_urlsafe(18) for role in roles}
        try:
            fd = os.open(keys_out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            raise VaultError(f"{keys_out} already exists; the keys are written once") from None
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(keys, handle, indent=1)
        self.write_state("config", {
            "salt": salt,
            "keys": {role: sha256((salt + key).encode()) for role, key in keys.items()},
            "owners": mapping,
            "export_to": owners.get("export_to", "exported"),
            "suffix": owners.get("suffix", ""),
        })
        self.journal({"event": "init", "roles": roles})
        return f"vault created at {self.store}; keys written to {keys_out} (0600)"

    def write(self, ident: str, data: bytes | None, key: str | None, reason: str | None,
              revert_to=None) -> str:
        cfg = self.config()
        if not ARTIFACT_ID.fullmatch(ident or ""):
            raise VaultError(f"'{ident}' is not a valid artifact id (letters, digits, '.', '_', '-', '/')")
        role = self.role_for(key)
        owner = self.owner_of(ident)
        if owner != role:
            raise Refused(f"'{ident}' belongs to {owner or 'no role'}, not to {role}")
        if not reason:
            raise VaultError("missing --reason")
        if revert_to is not None:
            data = self.version(ident, revert_to)[1]
        if cfg["suffix"] == ".json":
            try:
                json.loads(data)
            except ValueError as error:
                raise Refused(f"not valid JSON ({error})") from None
        with self.lock():
            h = sha256(data)
            obj = self._path("objects", h)
            if not obj.exists():
                obj.write_bytes(obfuscate(data, h.encode()))
            idx = self.index()
            entry = idx.setdefault(ident, {"owner": owner, "versions": []})
            was_deleted = entry.pop("deleted", None)
            if entry["versions"] and entry["versions"][-1]["obj"] == h and not was_deleted:
                return f"{ident}: no change (version {entry['versions'][-1]['n']})"
            n = entry["versions"][-1]["n"] + 1 if entry["versions"] else 1
            version = {"n": n, "obj": h, "author": role, "reason": reason, "ts": now(), "bytes": len(data)}
            if revert_to is not None:
                version["reverts_to"] = int(revert_to)
            entry["versions"].append(version)
            self.write_state("index", idx)
            self.journal({"event": "revert" if revert_to is not None else "write", "id": ident,
                          "version": n, "obj": h, "author": role, "reason": reason})
            self.export()
        return f"{ident}: version {n} written by {role}"

    def export_dir(self, override: str | None = None) -> Path:
        return self.cell / (override or self.config()["export_to"])

    def export(self, override: str | None = None) -> Path:
        cfg = self.config()
        out = self.export_dir(override)
        out.mkdir(parents=True, exist_ok=True)
        for ident, entry in self.index().items():
            f = out / (ident + cfg["suffix"])
            if entry.get("deleted"):
                if f.exists():
                    os.chmod(f, 0o644)
                    f.unlink()
                continue
            data = self.object(entry["versions"][-1]["obj"])
            if f.exists():
                if f.read_bytes() != data:
                    os.chmod(f, 0o644)
                    f.write_bytes(data)
            else:
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes(data)
            os.chmod(f, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        return out

    def verify(self, override: str | None = None) -> list:
        cfg = self.config()
        out = self.export_dir(override)
        idx = self.index()
        errors = []
        for ident, entry in sorted(idx.items()):
            for v in entry["versions"]:
                obj = self._path("objects", v["obj"])
                try:
                    if sha256(self.object(v["obj"])) != v["obj"]:
                        errors.append(f"{ident}: version {v['n']} does not match its content hash")
                except (OSError, ValueError, zlib.error):
                    errors.append(f"{ident}: version {v['n']} is missing or unreadable ({obj.name})")
            if entry.get("deleted"):
                continue
            f = out / (ident + cfg["suffix"])
            if not f.exists() or sha256(f.read_bytes()) != entry["versions"][-1]["obj"]:
                errors.append(f"{ident}: export missing or edited outside the vault")
        if out.is_dir():
            known = {ident + cfg["suffix"] for ident, e in idx.items() if not e.get("deleted")}
            for f in sorted(p for p in out.rglob("*") if p.is_file()):
                rel = f.relative_to(out).as_posix()
                if rel.endswith(cfg["suffix"]) and rel not in known:
                    errors.append(f"{rel}: a file in the export that is not in the vault")
        prev = GENESIS
        journal = self._path("journal")
        if journal.exists():
            for i, line in enumerate(journal.read_bytes().splitlines(), 1):
                try:
                    entry = json.loads(deobfuscate(line, b"journal"))
                except (ValueError, zlib.error):
                    errors.append(f"journal: line {i} is unreadable")
                    break
                if entry.get("prev") != prev:
                    errors.append(f"journal: line {i} breaks the hash chain")
                    break
                prev = sha256(line)
        return errors

    def request(self, action: str, ident: str, key: str | None, reason: str | None,
                new_owner: str | None = None) -> str:
        cfg = self.config()
        role = self.role_for(key)
        if action not in SENSITIVE_ACTIONS:
            raise VaultError(f"unknown sensitive action: {action}")
        if not reason:
            raise VaultError("missing --reason")
        self.version(ident)  # the artifact has to exist
        if self.owner_of(ident) != role:
            raise Refused(f"only the owner of '{ident}' requests {action}")
        if action == "change-owner" and new_owner not in cfg["keys"]:
            raise VaultError(f"--new-owner has to be one of the roles: {', '.join(sorted(cfg['keys']))}")
        with self.lock():
            pending = self.read_state("pending", {})
            rid = secrets.token_hex(3)
            while rid in pending:
                rid = secrets.token_hex(3)
            pending[rid] = {"action": action, "id": ident, "role": role, "reason": reason,
                            "new_owner": new_owner if action == "change-owner" else None,
                            "status": "pending", "created": time.time()}
            self.write_state("pending", pending)
            self.journal({"event": "request", "request": rid, "action": action, "id": ident,
                          "role": role, "reason": reason})
        return (f"request {rid} pending: the owner authorizes it with a TOTP code at POST /authorize "
                "of authorizer.py")

    def pending(self) -> dict:
        return {rid: {k: r[k] for k in ("action", "id", "role", "reason", "new_owner")}
                for rid, r in self.read_state("pending", {}).items() if r["status"] == "pending"}

    def authorize(self, rid: str) -> None:
        """Mark a pending request authorized; called by the authorizer after a valid code, under the lock."""
        pending = self.read_state("pending", {})
        r = pending.get(rid)
        if not r or r["status"] != "pending":
            raise VaultError(f"request {rid} does not exist or was already handled")
        r.update(status="authorized", authorized_at=time.time())
        self.write_state("pending", pending)
        self.journal({"event": "authorized", "request": rid, "action": r["action"], "id": r["id"]})

    def execute(self, rid: str, key: str | None) -> str:
        cfg = self.config()
        role = self.role_for(key)
        with self.lock():
            pending = self.read_state("pending", {})
            r = pending.get(rid)
            if not r or r["role"] != role:
                raise Refused("no such request, or it belongs to another role")
            if r["status"] != "authorized" or time.time() > r.get("authorized_at", 0) + AUTHORIZATION_VALIDITY_S:
                raise Refused(f"request {rid} is not authorized, or its authorization expired ({r['status']})")
            idx = self.index()
            if r["id"] not in idx:
                raise VaultError(f"'{r['id']}' is no longer in the vault")
            if r["action"] == "delete":
                idx[r["id"]]["deleted"] = True  # the versions stay in the vault; only the export goes
            else:
                if r["new_owner"] not in cfg["keys"]:
                    raise VaultError("the new owner is not a role")
                idx[r["id"]]["owner"] = r["new_owner"]
            self.write_state("index", idx)
            r["status"] = "executed"
            self.write_state("pending", pending)
            self.journal({"event": "execute", "request": rid, "action": r["action"], "id": r["id"],
                          "role": role})
            self.export()
        return f"request {rid} executed: {r['action']} {r['id']}"


def read_key(args) -> str | None:
    if getattr(args, "key", None):
        return args.key
    if getattr(args, "key_file", None):
        try:
            return Path(args.key_file).read_text(encoding="utf-8").strip()
        except OSError as error:
            raise VaultError(f"cannot read --key-file: {error}") from None
    return None


def self_test() -> int:
    import subprocess
    import tempfile

    script = str(Path(__file__).resolve())
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        cell = t / "cell"
        cell.mkdir()
        (t / "owners.json").write_text(json.dumps(
            {"roles": ["A", "B"], "owners": {"a*": "A", "a-special": "B", "b1": "B"},
             "export_to": "exp", "suffix": ".json"}), encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k not in ("COOPERATIO_CELL", "COOPERATIO_VAULT_DIR")}

        def run(*a):
            return subprocess.run([sys.executable, "-B", "-I", script, *a, "--cell", str(cell)],
                                  env=env, capture_output=True, text=True)

        checks.append(("keys inside the cell refused",
                       run("init", "--owners", str(t / "owners.json"), "--keys-out",
                           str(cell / "k.json")).returncode == 2 and not (cell / "k.json").exists()))
        init = run("init", "--owners", str(t / "owners.json"), "--keys-out", str(t / "keys.json"))
        checks.append(("init", init.returncode == 0))
        checks.append(("keys file is 0600", stat.S_IMODE(os.stat(t / "keys.json").st_mode) == 0o600))
        keys = json.loads((t / "keys.json").read_text(encoding="utf-8"))
        (t / "ka").write_text(keys["A"], encoding="utf-8")
        (t / "v1.json").write_text('{"x": 1}', encoding="utf-8")
        (t / "v2.json").write_text('{"x": 2}', encoding="utf-8")
        ka = ("--key-file", str(t / "ka"))
        checks.append(("the owner writes", run("write", "a1", str(t / "v1.json"), *ka, "--reason", "m").returncode == 0))
        checks.append(("another role is refused",
                       run("write", "a1", str(t / "v2.json"), "--key", keys["B"], "--reason", "m").returncode == 1))
        checks.append(("an exact id wins over a prefix",
                       run("write", "a-special", str(t / "v1.json"), *ka, "--reason", "m").returncode == 1))
        checks.append(("an invalid key is refused",
                       run("write", "a1", str(t / "v2.json"), "--key", "vk-x", "--reason", "m").returncode == 1))
        checks.append(("version 2", run("write", "a1", str(t / "v2.json"), *ka, "--reason", "m").returncode == 0))
        checks.append(("read version 1", json.loads(run("read", "a1", "--version", "1").stdout) == {"x": 1}))
        checks.append(("history has 2", run("history", "a1").stdout.count("\n") == 2))
        checks.append(("diff names both versions", "v1" in run("diff", "a1", "1", "2").stdout))
        reverted = run("revert", "a1", "1", *ka, "--reason", "m")
        checks.append(("revert creates version 3",
                       reverted.returncode == 0 and json.loads(run("read", "a1").stdout) == {"x": 1}))
        exported = cell / "exp" / "a1.json"
        checks.append(("the export is read-only", os.stat(exported).st_mode & 0o222 == 0))
        checks.append(("verify passes", run("verify").returncode == 0))
        os.chmod(exported, 0o644)
        exported.write_text('{"x": 99}', encoding="utf-8")
        checks.append(("an edit outside the vault is detected", run("verify").returncode == 1))
        checks.append(("export repairs it", run("export").returncode == 0 and run("verify").returncode == 0))
        objects = cell / ".vault" / "objects"
        checks.append(("the store is not readable",
                       b'"x"' not in b"".join(f.read_bytes() for f in objects.iterdir())))
        requested = run("request", "delete", "a1", *ka, "--reason", "m")
        rid = requested.stdout.split()[1] if requested.returncode == 0 else ""
        checks.append(("execute without authorization fails", run("execute", rid, *ka).returncode == 1))
        Vault(cell).authorize(rid)
        checks.append(("execute after authorization", run("execute", rid, *ka).returncode == 0
                       and not exported.exists()))
        checks.append(("an authorization is single use", run("execute", rid, *ka).returncode == 1))
        checks.append(("the journal chain holds", run("verify").returncode == 0))
    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"{'ok' if ok else 'FAILED'}: {name}")
    print("self-test:", "FAILED" if failed else "ok")
    return EXIT_REFUSED if failed else EXIT_OK


def parse_args(argv: list) -> argparse.Namespace:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--cell", type=Path, help="the cell folder (default: COOPERATIO_CELL or the current folder)")
    common.add_argument("--store", type=Path, help="the store (default: COOPERATIO_VAULT_DIR or <cell>/.vault)")
    keyed = argparse.ArgumentParser(add_help=False)
    keyed.add_argument("--key", help="the role's key (prefer --key-file)")
    keyed.add_argument("--key-file", help="a file holding the role's key")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init", parents=[common])
    p.add_argument("--owners", required=True, type=Path)
    p.add_argument("--keys-out", required=True, type=Path)
    sub.add_parser("list", parents=[common])
    p = sub.add_parser("read", parents=[common])
    p.add_argument("id")
    p.add_argument("--version")
    p = sub.add_parser("history", parents=[common])
    p.add_argument("id")
    p = sub.add_parser("diff", parents=[common])
    p.add_argument("id")
    p.add_argument("a")
    p.add_argument("b")
    p = sub.add_parser("write", parents=[common, keyed])
    p.add_argument("id")
    p.add_argument("file")
    p.add_argument("--reason")
    p = sub.add_parser("revert", parents=[common, keyed])
    p.add_argument("id")
    p.add_argument("version")
    p.add_argument("--reason")
    for name in ("export", "verify"):
        p = sub.add_parser(name, parents=[common])
        p.add_argument("--dir", help="the export folder, relative to the cell")
    p = sub.add_parser("request", parents=[common, keyed])
    p.add_argument("action", choices=SENSITIVE_ACTIONS)
    p.add_argument("id")
    p.add_argument("--new-owner")
    p.add_argument("--reason")
    p = sub.add_parser("execute", parents=[common, keyed])
    p.add_argument("request")
    sub.add_parser("self-test")
    return parser.parse_args(argv)


def run_command(args: argparse.Namespace) -> int:
    if args.command == "self-test":
        return self_test()
    cell = args.cell or default_cell()
    vault = Vault(cell, args.store or default_store(cell))
    c = args.command
    if c == "init":
        print(vault.init(args.owners, args.keys_out))
    elif c == "list":
        for ident, e in sorted(vault.index().items()):
            v = e["versions"][-1]
            print(f"{ident}\towner={e['owner']}\tversion={v['n']}\t{v['bytes']} bytes"
                  f"{chr(9) + 'DELETED' if e.get('deleted') else ''}")
    elif c == "read":
        sys.stdout.flush()
        sys.stdout.buffer.write(vault.version(args.id, args.version)[1])
        sys.stdout.buffer.flush()
    elif c == "history":
        entry = vault.index().get(args.id)
        if not entry:
            raise VaultError(f"'{args.id}' is not in the vault")
        for v in entry["versions"]:
            print(f"v{v['n']}\t{v['ts']}\t{v['author']}\t{v['bytes']} bytes\t{v['reason']}")
    elif c == "diff":
        a = vault.version(args.id, args.a)[1].decode("utf-8", "replace").splitlines()
        b = vault.version(args.id, args.b)[1].decode("utf-8", "replace").splitlines()
        print("\n".join(difflib.unified_diff(a, b, f"v{args.a}", f"v{args.b}", lineterm="")))
    elif c == "write":
        try:
            data = sys.stdin.buffer.read() if args.file == "-" else Path(args.file).read_bytes()
        except OSError as error:
            raise VaultError(f"cannot read {args.file}: {error}") from None
        print(vault.write(args.id, data, read_key(args), args.reason))
    elif c == "revert":
        print(vault.write(args.id, None, read_key(args), args.reason, revert_to=args.version))
    elif c == "export":
        out = vault.export(args.dir)
        print(f"exported to {out} (read-only; edit through the vault)")
    elif c == "verify":
        errors = vault.verify(args.dir)
        print("\n".join(errors) or "ok: the exports equal the vault and the journal chain holds")
        return EXIT_REFUSED if errors else EXIT_OK
    elif c == "request":
        print(vault.request(args.action, args.id, read_key(args), args.reason, args.new_owner))
    elif c == "execute":
        print(vault.execute(args.request, read_key(args)))
    return EXIT_OK


def main(argv: list | None = None) -> int:
    if sys.version_info < MIN_PYTHON:
        print("error: Python 3.9 or later is required", file=sys.stderr)
        return EXIT_USAGE
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return run_command(args)
    except Refused as error:
        print(f"refused: {error}", file=sys.stderr)
        return EXIT_REFUSED
    except (VaultError, OSError, ValueError, zlib.error) as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
