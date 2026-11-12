"""Tests for install.py (run: python -m pytest test_install.py)."""

from pathlib import Path

import pytest

import install


@pytest.fixture(autouse=True)
def no_real_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """The tests use a home of their own; the real environment must not leak in."""
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)


def make_home(tmp_path: Path, *markers: str) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    for marker in markers:
        (home / marker).mkdir(parents=True)
    return home


def entry(home: Path, skills_dir: str) -> Path:
    return home / skills_dir / install.SKILL_NAME


def test_links_the_skill_only_into_the_detected_harnesses(tmp_path: Path) -> None:
    home = make_home(tmp_path, ".claude", ".config/opencode")
    assert install.main(["--home", str(home)]) == install.EXIT_OK
    for skills_dir in (".claude/skills", ".config/opencode/skills"):
        link = entry(home, skills_dir)
        assert link.is_symlink()
        assert link.resolve() == install.SKILL_DIR
    assert not (home / ".copilot").exists()
    assert not (home / ".gemini").exists()


def test_a_second_run_changes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    home = make_home(tmp_path, ".copilot")
    install.main(["--home", str(home)])
    capsys.readouterr()
    assert install.main(["--home", str(home)]) == install.EXIT_OK
    assert "already installed" in capsys.readouterr().out


def test_harnesses_sharing_a_folder_get_one_entry(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    home = make_home(tmp_path, ".codex", ".cline")
    assert install.main(["--home", str(home)]) == install.EXIT_OK
    out = capsys.readouterr().out
    assert out.count("linked") == 1
    assert "codex, cline" in out
    assert entry(home, ".agents/skills").is_symlink()


def test_a_foreign_entry_is_a_conflict_and_is_left_untouched(tmp_path: Path) -> None:
    home = make_home(tmp_path, ".claude", ".gemini")
    foreign = entry(home, ".claude/skills")
    foreign.mkdir(parents=True)
    (foreign / "SKILL.md").write_text("someone else's\n", encoding="utf-8")
    assert install.main(["--home", str(home)]) == install.EXIT_CONFLICT
    assert (foreign / "SKILL.md").read_text(encoding="utf-8") == "someone else's\n"
    assert entry(home, ".gemini/skills").is_symlink()


def test_a_link_to_somewhere_else_is_a_conflict(tmp_path: Path) -> None:
    home = make_home(tmp_path, ".pi/agent")
    other = tmp_path / "other"
    other.mkdir()
    link = entry(home, ".pi/agent/skills")
    link.parent.mkdir(parents=True)
    link.symlink_to(other)
    assert install.main(["--home", str(home)]) == install.EXIT_CONFLICT
    assert link.resolve() == other


def test_uninstall_removes_only_what_it_installed(tmp_path: Path) -> None:
    home = make_home(tmp_path, ".claude", ".cursor")
    install.main(["--home", str(home)])
    foreign = entry(home, ".cursor/skills")
    foreign.unlink()
    foreign.mkdir()
    assert install.main(["--home", str(home), "--uninstall"]) == install.EXIT_CONFLICT
    assert not entry(home, ".claude/skills").exists()
    assert foreign.is_dir()
    assert install.SKILL_DIR.is_dir()


def test_copy_mode_marks_the_copy_and_uninstall_removes_it(tmp_path: Path) -> None:
    home = make_home(tmp_path, ".kiro")
    assert install.main(["--home", str(home), "--copy"]) == install.EXIT_OK
    copy = entry(home, ".kiro/skills")
    assert not copy.is_symlink()
    assert (copy / "SKILL.md").is_file()
    assert (copy / install.COPY_MARKER).is_file()
    assert not list(copy.rglob("__pycache__"))
    assert install.main(["--home", str(home), "--copy"]) == install.EXIT_OK
    assert install.main(["--home", str(home), "--uninstall"]) == install.EXIT_OK
    assert not copy.exists()


def test_switching_between_link_and_copy_needs_an_uninstall(tmp_path: Path) -> None:
    home = make_home(tmp_path, ".qwen")
    install.main(["--home", str(home)])
    assert install.main(["--home", str(home), "--copy"]) == install.EXIT_CONFLICT
    assert entry(home, ".qwen/skills").is_symlink()


def test_a_named_harness_is_installed_even_when_not_detected(tmp_path: Path) -> None:
    home = make_home(tmp_path, ".claude")
    assert install.main(["--home", str(home), "--harness", "gemini-cli"]) == install.EXIT_OK
    assert entry(home, ".gemini/skills").is_symlink()
    assert not entry(home, ".claude/skills").exists()


def test_dry_run_changes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    home = make_home(tmp_path, ".claude")
    assert install.main(["--home", str(home), "--dry-run"]) == install.EXIT_OK
    assert "would link" in capsys.readouterr().out
    assert not (home / ".claude/skills").exists()


def test_no_harness_detected_exits_three(tmp_path: Path) -> None:
    home = make_home(tmp_path)
    assert install.main(["--home", str(home)]) == install.EXIT_NONE_DETECTED


def test_list_shows_every_known_harness(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    home = make_home(tmp_path, ".claude")
    assert install.main(["--home", str(home), "--list"]) == install.EXIT_OK
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == len(install.HARNESSES)
    assert any(line.startswith("claude-code") and "detected" in line for line in lines)


def test_claude_config_dir_is_followed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    custom = tmp_path / "claude-config"
    custom.mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(custom))
    bases = install.Bases(tmp_path / "nohome", tmp_path / "nohome" / ".config")
    chosen = dict(install.select(bases, ["claude-code"], explicit_home=False))
    harness = next(iter(chosen))
    assert chosen[harness] is True
    assert bases.resolve(harness.skills) == custom / "skills"


def test_an_unknown_harness_name_is_refused(tmp_path: Path) -> None:
    home = make_home(tmp_path)
    with pytest.raises(SystemExit) as exc:
        install.main(["--home", str(home), "--harness", "nonexistent"])
    assert exc.value.code == install.EXIT_USAGE
