#!/usr/bin/env python3
"""The owner's authorization of the vault's sensitive actions, by a TOTP code (Google Authenticator and the like).

Usage:
    authorizer.py new-secret [--secret FILE]
        creates the secret (0600) and FILE.uri with the otpauth:// line to enroll in the app
    authorizer.py serve [--host 127.0.0.1] [--port 8765] [--secret FILE] [--cell C] [--store S]
        GET  /pending                                      the pending requests (action, artifact, role, reason)
        POST /authorize {"request": "...", "code": "123456"}
             authorizes the request for 5 minutes; 5 failures in a row lock the service for 5 minutes
    authorizer.py self-test

The codes follow RFC 6238 (SHA-1, 6 digits, 30-second steps), accepted one step either side, and each
code is used once: a code of a step already used is refused. The secret stays outside the cell (default
~/.config/cooperatio/totp, or the COOPERATIO_TOTP_SECRET variable), so whoever holds only the cell does
not hold the code; new-secret refuses a path inside a cell that holds a vault. The requests are the
vault's (vault.py request), found with the same --cell and --store as vault.py. The service listens on
127.0.0.1 by default: it is for the owner's own machine.

Exit codes: 0 done; 1 a failed self-test; 2 invalid input or Python below 3.9.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import base64  # noqa: E402
import hashlib  # noqa: E402
import hmac  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import secrets  # noqa: E402
import struct  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  # noqa: E402
from pathlib import Path  # noqa: E402

MIN_PYTHON = (3, 9)  # the interpreter the material is tested on (v0.6.0)
HERE = Path(__file__).resolve().parent
STEP_S = 30
MAX_FAILURES = 5
LOCKOUT_S = 300
MAX_BODY = 4096


def load_vault():
    name = "cooperatio_vault"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, HERE / "vault.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


vault = load_vault()


def default_secret() -> Path:
    return Path(os.environ.get("COOPERATIO_TOTP_SECRET") or Path.home() / ".config" / "cooperatio" / "totp")


def totp(secret_b32: str, t: float | None = None, digits: int = 6, step: int = STEP_S, alg=hashlib.sha1) -> str:
    key = base64.b32decode(secret_b32.upper() + "=" * (-len(secret_b32) % 8))
    counter = struct.pack(">Q", int((time.time() if t is None else t) // step))
    h = hmac.new(key, counter, alg).digest()
    o = h[-1] & 0x0F
    return str((struct.unpack(">I", h[o:o + 4])[0] & 0x7FFFFFFF) % 10 ** digits).zfill(digits)


def matching_step(secret_b32: str, code, t: float | None = None) -> int | None:
    """The time step whose code equals `code`, within one step either side; None when none does."""
    t = time.time() if t is None else t
    code = str(code).strip()
    for d in (-1, 0, 1):
        if hmac.compare_digest(totp(secret_b32, t + d * STEP_S), code):
            return int((t + d * STEP_S) // STEP_S)
    return None


def new_secret(path: Path, cell: Path) -> str:
    if path.exists():
        raise ValueError(f"{path} already exists; delete it yourself to replace the secret")
    if (cell / ".vault" / "config").exists() and vault.inside(path, cell):
        raise ValueError("the secret has to stay outside the cell")
    path.parent.mkdir(parents=True, exist_ok=True)
    s = base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")
    uri = f"otpauth://totp/cooperatio:vault?secret={s}&issuer=cooperatio&digits=6&period={STEP_S}\n"
    for f, text in ((path, s), (Path(str(path) + ".uri"), uri)):
        fd = os.open(f, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
    return f"secret created at {path}; enroll the key or the otpauth:// line of {path}.uri in the app (0600)"


def make_handler(store, secret_b32: str):
    """A request handler bound to one vault and one secret, with its own failure counter."""
    failures = {"n": 0, "until": 0.0}
    guard = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def _reply(self, code: int, obj) -> None:
            body = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args) -> None:
            pass

        def do_GET(self) -> None:
            if self.path != "/pending":
                return self._reply(404, {"error": "route"})
            self._reply(200, store.pending())

        def do_POST(self) -> None:
            if self.path != "/authorize":
                return self._reply(404, {"error": "route"})
            with guard:
                if time.time() < failures["until"]:
                    return self._reply(429, {"error": "too many attempts; wait"})
            try:
                length = int(self.headers.get("Content-Length", 0) or 0)
                if length > MAX_BODY:
                    return self._reply(413, {"error": "body too large"})
                body = json.loads(self.rfile.read(length) or b"{}")
                if not isinstance(body, dict):
                    raise ValueError
            except ValueError:
                return self._reply(400, {"error": "json"})
            rid = str(body.get("request"))
            with store.lock():
                pending = store.read_state("pending", {})
                r = pending.get(rid)
                if not r or r["status"] != "pending":
                    return self._reply(404, {"error": "no such request, or already handled"})
                step = matching_step(secret_b32, body.get("code", ""))
                used = store.read_state("totp", {}).get("last_step", -1)
                if step is None or step <= used:
                    with guard:
                        failures["n"] += 1
                        if failures["n"] >= MAX_FAILURES:
                            failures.update(n=0, until=time.time() + LOCKOUT_S)
                    store.journal({"event": "authorization_denied", "request": rid})
                    return self._reply(403, {"error": "invalid code" if step is None else "code already used"})
                with guard:
                    failures["n"] = 0
                store.write_state("totp", {"last_step": step})
                store.authorize(rid)
            self._reply(200, {"ok": True, "request": rid, "valid_for_s": vault.AUTHORIZATION_VALIDITY_S})

    return Handler


def serve(args) -> int:
    cell = args.cell or vault.default_cell()
    store = vault.Vault(cell, args.store or vault.default_store(cell))
    store.config()
    secret = Path(args.secret or default_secret()).read_text(encoding="utf-8").strip()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(store, secret))
    print(f"authorizer at http://{server.server_address[0]}:{server.server_address[1]} (vault {store.store})")
    server.serve_forever()
    return 0


def self_test() -> int:
    import tempfile
    import urllib.error
    import urllib.request

    checks = []
    rfc = base64.b32encode(b"12345678901234567890").decode()  # the vectors of RFC 6238 (SHA-1, 8 digits)
    for t, expected in ((59, "94287082"), (1111111109, "07081804"), (1234567890, "89005924"),
                        (2000000000, "69279037")):
        checks.append((f"RFC 6238 t={t}", totp(rfc, t, 8) == expected))
    checks.append(("one step either side", matching_step(rfc, totp(rfc, 1000 - STEP_S), 1000) is not None
                   and matching_step(rfc, totp(rfc, 1000 - 3 * STEP_S), 1000) is None))
    with tempfile.TemporaryDirectory() as tmp:
        store = vault.Vault(Path(tmp), Path(tmp) / ".vault")
        (Path(tmp) / ".vault" / "objects").mkdir(parents=True)
        store.write_state("pending", {"abc123": {"action": "delete", "id": "x", "role": "A", "reason": "m",
                                                 "new_owner": None, "status": "pending", "created": time.time()},
                                      "def456": {"action": "delete", "id": "y", "role": "A", "reason": "m",
                                                 "new_owner": None, "status": "pending", "created": time.time()}})
        secret = base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")
        try:
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(store, secret))
        except OSError as error:
            print(f"skipped: the service checks (cannot bind 127.0.0.1: {error})")
            server = None
        if server is not None:
            threading.Thread(target=server.serve_forever, daemon=True).start()
            url = f"http://127.0.0.1:{server.server_address[1]}"
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

            def post(body) -> int:
                req = urllib.request.Request(url + "/authorize", json.dumps(body).encode(),
                                             {"Content-Type": "application/json"})
                try:
                    return opener.open(req).status
                except urllib.error.HTTPError as error:
                    return error.code
            try:
                checks.append(("lists the pending", "abc123" in json.load(opener.open(url + "/pending"))))
                code = totp(secret)
                wrong = str((int(code) + 1) % 10 ** 6).zfill(6)
                checks.append(("a wrong code is refused", post({"request": "abc123", "code": wrong}) == 403))
                checks.append(("the right code authorizes", post({"request": "abc123", "code": code}) == 200))
                checks.append(("the vault records it",
                               store.read_state("pending", {})["abc123"]["status"] == "authorized"))
                checks.append(("no second authorization", post({"request": "abc123", "code": code}) == 404))
                checks.append(("a code is used once", post({"request": "def456", "code": code}) == 403))
            finally:
                server.shutdown()
                server.server_close()
    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"{'ok' if ok else 'FAILED'}: {name}")
    print("self-test:", "FAILED" if failed else "ok")
    return 1 if failed else 0


def parse_args(argv: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("new-secret")
    p.add_argument("--secret", type=Path)
    p.add_argument("--cell", type=Path)
    p = sub.add_parser("serve")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--secret", type=Path)
    p.add_argument("--cell", type=Path)
    p.add_argument("--store", type=Path)
    sub.add_parser("self-test")
    return parser.parse_args(argv)


def main(argv: list | None = None) -> int:
    if sys.version_info < MIN_PYTHON:
        print("error: Python 3.9 or later is required", file=sys.stderr)
        return 2
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.command == "self-test":
            return self_test()
        if args.command == "new-secret":
            print(new_secret(args.secret or default_secret(), args.cell or vault.default_cell()))
            return 0
        return serve(args)
    except (vault.VaultError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
