"""Tests for authorizer.py (run: python -m pytest test_authorizer.py).

The service tests open a port on 127.0.0.1; where binding is not permitted (a sandbox), they are
skipped with the reason, and the code tests still run.
"""

import base64
import json
import os
import secrets
import stat
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import authorizer

vault = authorizer.vault
RFC_SECRET = base64.b32encode(b"12345678901234567890").decode()


@pytest.mark.parametrize("t, expected", [(59, "94287082"), (1111111109, "07081804"),
                                         (1234567890, "89005924"), (2000000000, "69279037")])
def test_the_codes_follow_rfc_6238(t: int, expected: str) -> None:
    assert authorizer.totp(RFC_SECRET, t, 8) == expected


def test_a_code_is_accepted_one_step_either_side_and_no_further() -> None:
    t = 1_000_000
    for d in (-1, 0, 1):
        assert authorizer.matching_step(RFC_SECRET, authorizer.totp(RFC_SECRET, t + d * 30), t) is not None
    for d in (-3, 3):
        assert authorizer.matching_step(RFC_SECRET, authorizer.totp(RFC_SECRET, t + d * 30), t) is None


def test_new_secret_is_0600_written_once_and_outside_a_cell(tmp_path: Path) -> None:
    secret = tmp_path / "outside" / "totp"
    authorizer.new_secret(secret, tmp_path / "cell")
    assert stat.S_IMODE(os.stat(secret).st_mode) == 0o600
    uri = Path(str(secret) + ".uri").read_text(encoding="utf-8")
    assert uri.startswith("otpauth://totp/") and secret.read_text(encoding="utf-8") in uri
    with pytest.raises(ValueError):
        authorizer.new_secret(secret, tmp_path / "cell")
    cell = tmp_path / "cell"
    (cell / ".vault").mkdir(parents=True)
    (cell / ".vault" / "config").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        authorizer.new_secret(cell / "totp", cell)
    assert not (cell / "totp").exists()


class Service:
    def __init__(self, tmp_path: Path) -> None:
        self.store = vault.Vault(tmp_path, tmp_path / ".vault")
        (tmp_path / ".vault" / "objects").mkdir(parents=True)
        self.store.write_state("pending", {
            rid: {"action": "delete", "id": rid, "role": "writer", "reason": "r", "new_owner": None,
                  "status": "pending", "created": time.time()} for rid in ("aaa111", "bbb222", "ccc333")})
        self.secret = base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")
        try:
            self.server = ThreadingHTTPServer(("127.0.0.1", 0), authorizer.make_handler(self.store, self.secret))
        except OSError as error:
            pytest.skip(f"cannot bind 127.0.0.1 here: {error}")
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def post(self, body) -> int:
        req = urllib.request.Request(self.url + "/authorize", json.dumps(body).encode(),
                                     {"Content-Type": "application/json"})
        try:
            return self.opener.open(req).status
        except urllib.error.HTTPError as error:
            return error.code

    def wrong(self) -> str:
        return str((int(authorizer.totp(self.secret)) + 500000) % 10 ** 6).zfill(6)


@pytest.fixture
def service(tmp_path: Path):
    s = Service(tmp_path)
    yield s
    s.server.shutdown()
    s.server.server_close()


def test_the_service_lists_and_authorizes_with_the_right_code(service: Service) -> None:
    listed = json.load(service.opener.open(service.url + "/pending"))
    assert set(listed) == {"aaa111", "bbb222", "ccc333"}
    assert service.post({"request": "aaa111", "code": service.wrong()}) == 403
    assert service.post({"request": "aaa111", "code": authorizer.totp(service.secret)}) == 200
    assert service.store.read_state("pending", {})["aaa111"]["status"] == "authorized"
    assert "aaa111" not in json.load(service.opener.open(service.url + "/pending"))
    events = [e["event"] for e in service.store.journal_entries()]
    assert events == ["authorization_denied", "authorized"]


def test_a_request_and_a_code_are_each_used_once(service: Service) -> None:
    code = authorizer.totp(service.secret)
    assert service.post({"request": "aaa111", "code": code}) == 200
    assert service.post({"request": "aaa111", "code": code}) == 404
    assert service.post({"request": "bbb222", "code": code}) == 403


def test_five_failures_lock_the_service(service: Service) -> None:
    for _ in range(authorizer.MAX_FAILURES):
        assert service.post({"request": "aaa111", "code": service.wrong()}) == 403
    assert service.post({"request": "aaa111", "code": authorizer.totp(service.secret)}) == 429
    assert service.store.read_state("pending", {})["aaa111"]["status"] == "pending"


def test_a_malformed_body_or_route_is_refused(service: Service) -> None:
    req = urllib.request.Request(service.url + "/authorize", b"{not json", {"Content-Type": "application/json"})
    with pytest.raises(urllib.error.HTTPError) as error:
        service.opener.open(req)
    assert error.value.code == 400
    assert service.post({"request": "nope", "code": "000000"}) == 404
    with pytest.raises(urllib.error.HTTPError) as error:
        service.opener.open(service.url + "/elsewhere")
    assert error.value.code == 404


def test_the_self_test_passes(capsys: pytest.CaptureFixture) -> None:
    assert authorizer.main(["self-test"]) == 0
    assert capsys.readouterr().out.rstrip().endswith("self-test: ok")
