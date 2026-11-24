"""Tests for vault.py (run: python -m pytest test_vault.py)."""

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

import vault

OWNERS = {"roles": ["writer", "verifier"], "owners": {"draft-*": "writer", "draft-canon": "verifier",
                                                       "report": "verifier"},
          "export_to": "artifacts", "suffix": ".json"}


@pytest.fixture(autouse=True)
def no_real_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """The tests use cells of their own; the caller's environment must not leak in."""
    monkeypatch.delenv("COOPERATIO_CELL", raising=False)
    monkeypatch.delenv("COOPERATIO_VAULT_DIR", raising=False)


class Cell:
    def __init__(self, tmp_path: Path) -> None:
        self.tmp = tmp_path
        self.path = tmp_path / "cell"
        self.path.mkdir()
        (tmp_path / "owners.json").write_text(json.dumps(OWNERS), encoding="utf-8")
        assert self.run("init", "--owners", str(tmp_path / "owners.json"),
                        "--keys-out", str(tmp_path / "keys.json")) == vault.EXIT_OK
        self.keys = json.loads((tmp_path / "keys.json").read_text(encoding="utf-8"))
        for role, key in self.keys.items():
            (tmp_path / f"{role}.key").write_text(key + "\n", encoding="utf-8")

    def run(self, *argv: str) -> int:
        return vault.main([*argv, "--cell", str(self.path)])

    def key(self, role: str) -> list:
        return ["--key-file", str(self.tmp / f"{role}.key")]

    def file(self, name: str, text: str) -> str:
        f = self.tmp / name
        f.write_text(text, encoding="utf-8")
        return str(f)

    def write(self, ident: str, text: str, role: str, reason: str = "a reason") -> int:
        return self.run("write", ident, self.file("in.json", text), *self.key(role), "--reason", reason)

    def export(self, ident: str) -> Path:
        return self.path / "artifacts" / f"{ident}.json"


@pytest.fixture
def cell(tmp_path: Path) -> Cell:
    return Cell(tmp_path)


def test_the_owner_writes_and_everyone_reads(cell: Cell, capsys: pytest.CaptureFixture) -> None:
    assert cell.write("draft-1", '{"x": 1}', "writer") == vault.EXIT_OK
    capsys.readouterr()
    assert cell.run("read", "draft-1") == vault.EXIT_OK
    assert json.loads(capsys.readouterr().out) == {"x": 1}
    assert json.loads(cell.export("draft-1").read_text(encoding="utf-8")) == {"x": 1}


def test_another_role_or_a_wrong_key_is_refused(cell: Cell) -> None:
    assert cell.write("draft-1", '{"x": 1}', "verifier") == vault.EXIT_REFUSED
    assert cell.run("write", "draft-1", cell.file("a.json", "{}"), "--key", "vk-wrong",
                    "--reason", "r") == vault.EXIT_REFUSED
    assert cell.write("unowned", '{"x": 1}', "writer") == vault.EXIT_REFUSED
    assert not cell.export("draft-1").exists()


def test_an_exact_id_wins_over_a_prefix(cell: Cell) -> None:
    assert cell.write("draft-canon", "{}", "writer") == vault.EXIT_REFUSED
    assert cell.write("draft-canon", "{}", "verifier") == vault.EXIT_OK


def test_a_write_needs_a_reason_and_valid_json(cell: Cell) -> None:
    assert cell.run("write", "draft-1", cell.file("a.json", "{}"), *cell.key("writer")) == vault.EXIT_USAGE
    assert cell.write("draft-1", "{not json", "writer") == vault.EXIT_REFUSED


def test_every_write_is_a_new_version_with_author_and_reason(cell: Cell, capsys: pytest.CaptureFixture) -> None:
    cell.write("draft-1", '{"x": 1}', "writer", "first draft")
    cell.write("draft-1", '{"x": 2}', "writer", "second draft")
    capsys.readouterr()
    assert cell.write("draft-1", '{"x": 2}', "writer") == vault.EXIT_OK
    assert "no change" in capsys.readouterr().out
    assert cell.run("history", "draft-1") == vault.EXIT_OK
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 2
    assert lines[0].startswith("v1") and "writer" in lines[0] and lines[0].endswith("first draft")
    assert cell.run("read", "draft-1", "--version", "1") == vault.EXIT_OK
    assert json.loads(capsys.readouterr().out) == {"x": 1}
    assert cell.run("diff", "draft-1", "1", "2") == vault.EXIT_OK
    out = capsys.readouterr().out
    assert '-{"x": 1}' in out and '+{"x": 2}' in out
    assert cell.run("read", "draft-1", "--version", "9") == vault.EXIT_USAGE


def test_revert_creates_a_new_version_equal_to_the_old_one(cell: Cell, capsys: pytest.CaptureFixture) -> None:
    cell.write("draft-1", '{"x": 1}', "writer")
    cell.write("draft-1", '{"x": 2}', "writer")
    assert cell.run("revert", "draft-1", "1", *cell.key("verifier"), "--reason", "r") == vault.EXIT_REFUSED
    assert cell.run("revert", "draft-1", "1", *cell.key("writer"), "--reason", "back") == vault.EXIT_OK
    capsys.readouterr()
    cell.run("history", "draft-1")
    assert capsys.readouterr().out.count("\n") == 3
    assert json.loads(cell.export("draft-1").read_text(encoding="utf-8")) == {"x": 1}


def test_an_edit_outside_the_vault_is_detected_and_export_repairs_it(cell: Cell) -> None:
    cell.write("draft-1", '{"x": 1}', "writer")
    exported = cell.export("draft-1")
    assert os.stat(exported).st_mode & 0o222 == 0
    assert cell.run("verify") == vault.EXIT_OK
    os.chmod(exported, 0o644)
    exported.write_text('{"x": 99}', encoding="utf-8")
    assert cell.run("verify") == vault.EXIT_REFUSED
    (cell.path / "artifacts" / "stray.json").write_text("{}", encoding="utf-8")
    assert cell.run("export") == vault.EXIT_OK
    assert cell.run("verify") == vault.EXIT_REFUSED  # the stray file is not the vault's
    (cell.path / "artifacts" / "stray.json").unlink()
    assert cell.run("verify") == vault.EXIT_OK


def test_a_broken_journal_chain_is_detected(cell: Cell) -> None:
    cell.write("draft-1", '{"x": 1}', "writer")
    cell.write("draft-1", '{"x": 2}', "writer")
    journal = cell.path / ".vault" / "journal"
    lines = journal.read_bytes().splitlines()
    del lines[1]
    journal.write_bytes(b"\n".join(lines) + b"\n")
    assert cell.run("verify") == vault.EXIT_REFUSED


def test_the_store_is_obfuscated(cell: Cell) -> None:
    cell.write("draft-1", '{"marker": "plain text"}', "writer")
    store = cell.path / ".vault"
    blob = b"".join(f.read_bytes() for f in store.rglob("*") if f.is_file())
    assert b"plain text" not in blob and b"draft-1" not in blob and b"writer" not in blob
    assert all(len(f.name) == 64 for f in (store / "objects").iterdir())


def test_the_keys_are_written_once_0600_and_outside_the_cell(tmp_path: Path) -> None:
    c = Cell(tmp_path)
    assert stat.S_IMODE(os.stat(tmp_path / "keys.json").st_mode) == 0o600
    assert set(c.keys) == {"writer", "verifier"}
    other = tmp_path / "other"
    other.mkdir()
    owners = str(tmp_path / "owners.json")
    assert vault.main(["init", "--owners", owners, "--keys-out", str(other / "k.json"),
                       "--cell", str(other)]) == vault.EXIT_USAGE
    assert not (other / "k.json").exists() and not (other / ".vault").exists()
    assert vault.main(["init", "--owners", owners, "--keys-out", str(tmp_path / "keys.json"),
                       "--cell", str(other)]) == vault.EXIT_USAGE
    assert c.run("init", "--owners", owners, "--keys-out", str(tmp_path / "k2.json")) == vault.EXIT_USAGE


def make_admin(cell: Cell) -> list:
    assert cell.run("new-admin", "--key-out", str(cell.tmp / "admin.key")) == vault.EXIT_OK
    return ["--key-file", str(cell.tmp / "admin.key")]


def test_new_admin_is_once_0600_and_outside_the_cell(cell: Cell) -> None:
    assert cell.run("new-admin", "--key-out", str(cell.path / "admin.key")) == vault.EXIT_USAGE
    assert not (cell.path / "admin.key").exists()
    make_admin(cell)
    assert stat.S_IMODE(os.stat(cell.tmp / "admin.key").st_mode) == 0o600
    assert cell.run("new-admin", "--key-out", str(cell.tmp / "admin2.key")) == vault.EXIT_REFUSED
    assert not (cell.tmp / "admin2.key").exists()


def test_without_an_administrator_nothing_is_deleted(cell: Cell) -> None:
    cell.write("draft-1", '{"x": 1}', "writer")
    assert cell.run("delete", "draft-1", *cell.key("writer"), "--reason", "r") == vault.EXIT_REFUSED
    assert cell.export("draft-1").exists()


def test_a_role_key_cannot_delete_or_reassign(cell: Cell) -> None:
    cell.write("draft-1", '{"x": 1}', "writer")
    make_admin(cell)
    for role in ("writer", "verifier"):
        assert cell.run("delete", "draft-1", *cell.key(role), "--reason", "r") == vault.EXIT_REFUSED
        assert cell.run("change-owner", "draft-1", "verifier", *cell.key(role),
                        "--reason", "r") == vault.EXIT_REFUSED
        assert cell.run("assign", "new-1", role, *cell.key(role)) == vault.EXIT_REFUSED
        assert cell.run("add-role", "extra", *cell.key(role),
                        "--key-out", str(cell.tmp / "extra.key")) == vault.EXIT_REFUSED
    assert not (cell.tmp / "extra.key").exists()
    assert cell.export("draft-1").exists()
    assert cell.write("draft-1", '{"x": 2}', "writer") == vault.EXIT_OK


def test_the_administrator_deletes_and_the_versions_stay(cell: Cell) -> None:
    cell.write("draft-1", '{"x": 1}', "writer")
    admin = make_admin(cell)
    assert cell.run("delete", "draft-1", *admin) == vault.EXIT_USAGE  # a reason is required
    assert cell.run("delete", "draft-1", *admin, "--reason", "obsolete") == vault.EXIT_OK
    assert not cell.export("draft-1").exists()
    assert cell.run("delete", "draft-1", *admin, "--reason", "again") == vault.EXIT_USAGE
    assert cell.run("verify") == vault.EXIT_OK
    v = vault.Vault(cell.path)
    assert v.index()["draft-1"]["versions"], "the versions stay in the vault"
    last = v.journal_entries()[-1]
    assert last["event"] == "delete" and last["id"] == "draft-1" and last["reason"] == "obsolete"


def test_the_administrator_changes_the_owner(cell: Cell) -> None:
    cell.write("draft-1", '{"x": 1}', "writer")
    admin = make_admin(cell)
    assert cell.run("change-owner", "draft-1", "nobody", *admin, "--reason", "r") == vault.EXIT_USAGE
    assert cell.run("change-owner", "never-written", "verifier", *admin, "--reason", "r") == vault.EXIT_USAGE
    assert cell.run("change-owner", "draft-1", "verifier", *admin, "--reason", "handed over") == vault.EXIT_OK
    assert cell.write("draft-1", '{"x": 2}', "writer") == vault.EXIT_REFUSED
    assert cell.write("draft-1", '{"x": 2}', "verifier") == vault.EXIT_OK
    entry = [e for e in vault.Vault(cell.path).journal_entries() if e["event"] == "change-owner"][0]
    assert (entry["from"], entry["to"], entry["reason"]) == ("writer", "verifier", "handed over")
    assert cell.run("verify") == vault.EXIT_OK


def test_add_role_and_assign(cell: Cell) -> None:
    cell.write("draft-1", '{"x": 1}', "writer")
    admin = make_admin(cell)
    assert cell.run("add-role", "editor", *admin, "--key-out", str(cell.path / "e.key")) == vault.EXIT_USAGE
    assert cell.run("add-role", "editor", *admin, "--key-out", str(cell.tmp / "editor.key")) == vault.EXIT_OK
    assert stat.S_IMODE(os.stat(cell.tmp / "editor.key").st_mode) == 0o600
    assert cell.run("add-role", "editor", *admin, "--key-out", str(cell.tmp / "e2.key")) == vault.EXIT_USAGE
    assert cell.run("assign", "notes", "nobody", *admin) == vault.EXIT_USAGE
    assert cell.run("assign", "notes", "editor", *admin) == vault.EXIT_OK
    assert cell.write("notes", "{}", "writer") == vault.EXIT_REFUSED
    assert cell.write("notes", "{}", "editor") == vault.EXIT_OK
    assert cell.run("assign", "draft-1", "editor", *admin) == vault.EXIT_REFUSED  # it has versions
    assert cell.run("assign", "notes", "writer", *admin) == vault.EXIT_REFUSED
    assert cell.write("draft-1", '{"x": 2}', "writer") == vault.EXIT_OK


def test_the_cell_defaults_to_the_current_folder(cell: Cell, monkeypatch: pytest.MonkeyPatch,
                                                 capsys: pytest.CaptureFixture) -> None:
    cell.write("draft-1", '{"x": 1}', "writer")
    monkeypatch.chdir(cell.path)
    capsys.readouterr()
    assert vault.main(["list"]) == vault.EXIT_OK
    assert capsys.readouterr().out.startswith("draft-1\towner=writer\tversion=1")
    monkeypatch.chdir(cell.tmp)
    monkeypatch.setenv("COOPERATIO_CELL", str(cell.path))
    assert vault.main(["verify"]) == vault.EXIT_OK


def test_an_invalid_artifact_id_is_refused(cell: Cell) -> None:
    assert cell.write("../escape", "{}", "writer") == vault.EXIT_USAGE
    assert not (cell.path / "escape.json").exists()


def test_the_self_test_passes() -> None:
    result = subprocess.run([sys.executable, "-B", str(Path(vault.__file__)), "self-test"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.rstrip().endswith("self-test: ok")
