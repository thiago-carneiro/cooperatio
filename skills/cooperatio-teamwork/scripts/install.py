#!/usr/bin/env python3
"""Install the cooperatio-teamwork skill into every agent harness found.

Usage:
    install.py                      # detect the harnesses and link the skill
    install.py --list               # show every known harness and its state
    install.py --dry-run            # say what would change, change nothing
    install.py --harness codex      # only these harnesses, detected or not
    install.py --copy               # copy the folder instead of linking it
    install.py --uninstall          # remove what this installer put there

A harness is detected when its own configuration folder exists in the home
directory (``~/.claude``, ``~/.copilot``, ``~/.config/opencode`` and so on);
the installer then puts the skill in that harness's user-level skills folder,
creating only the ``skills`` folder inside a configuration folder that already
exists. It never creates the configuration folder of a harness that was not
found, unless that harness is named with ``--harness``.

The default is a symbolic link to this skill folder, inside the material: the
scaffold copies the validator from the material through the path it resolves,
so a link keeps that working, and a ``git pull`` of the material updates every
harness at once. ``--copy`` writes an independent copy (with a marker file so
``--uninstall`` and a later ``--copy`` recognise it); a copied skill creates
cells without the validator, as SKILL.md says.

It never replaces what it did not install: an entry of the same name that is a
real folder without the marker, or a link to somewhere else, is reported as a
conflict and left untouched.

The table of harnesses follows the user-level skills paths listed by the
vercel-labs/skills project (docs/agents.md) and each harness's own
documentation where one was found; several harnesses share ``~/.agents/skills``
and get one entry there. Some harnesses also read the folders of others
(OpenCode and Cursor read ``~/.claude/skills``, for instance) and may list the
skill twice; ``--uninstall --harness <name>`` removes one copy.

Exit codes: 0 done (or nothing to do); 1 at least one conflict or I/O error;
2 invalid input or Python below 3.9; 3 no harness detected.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

MIN_PYTHON = (3, 9)
SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_NAME = SKILL_DIR.name
COPY_MARKER = ".cooperatio-install"
COPY_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")

EXIT_OK = 0
EXIT_CONFLICT = 1
EXIT_USAGE = 2
EXIT_NONE_DETECTED = 3


@dataclass(frozen=True)
class Harness:
    """A harness, the folder whose existence says it is installed, and the
    user-level skills folder it reads. Paths are relative to a base: ``home``
    or ``config`` (``$XDG_CONFIG_HOME``, default ``~/.config``)."""

    name: str
    marker: tuple[str, str]
    skills: tuple[str, str]


HARNESSES: tuple[Harness, ...] = (
    Harness("claude-code", ("home", ".claude"), ("home", ".claude/skills")),
    Harness("github-copilot", ("home", ".copilot"), ("home", ".copilot/skills")),
    Harness("pi", ("home", ".pi/agent"), ("home", ".pi/agent/skills")),
    Harness("opencode", ("config", "opencode"), ("config", "opencode/skills")),
    Harness("codex", ("home", ".codex"), ("home", ".agents/skills")),
    Harness("gemini-cli", ("home", ".gemini"), ("home", ".gemini/skills")),
    Harness("cursor", ("home", ".cursor"), ("home", ".cursor/skills")),
    Harness("windsurf", ("home", ".codeium/windsurf"), ("home", ".codeium/windsurf/skills")),
    Harness("droid", ("home", ".factory"), ("home", ".factory/skills")),
    Harness("goose", ("config", "goose"), ("config", "goose/skills")),
    Harness("kiro-cli", ("home", ".kiro"), ("home", ".kiro/skills")),
    Harness("qwen-code", ("home", ".qwen"), ("home", ".qwen/skills")),
    Harness("cline", ("home", ".cline"), ("home", ".agents/skills")),
    Harness("kimi-code-cli", ("home", ".kimi"), ("home", ".agents/skills")),
    Harness("roo", ("home", ".roo"), ("home", ".roo/skills")),
    Harness("amp", ("config", "amp"), ("config", "agents/skills")),
    Harness("continue", ("home", ".continue"), ("home", ".continue/skills")),
    Harness("crush", ("config", "crush"), ("config", "crush/skills")),
    Harness("augment", ("home", ".augment"), ("home", ".augment/skills")),
    Harness("kilo", ("home", ".kilo"), ("home", ".kilo/skills")),
    Harness("junie", ("home", ".junie"), ("home", ".junie/skills")),
    Harness("openhands", ("home", ".openhands"), ("home", ".openhands/skills")),
    Harness("trae", ("home", ".trae"), ("home", ".trae/skills")),
    Harness("mistral-vibe", ("home", ".vibe"), ("home", ".vibe/skills")),
    Harness("devin", ("config", "devin"), ("config", "devin/skills")),
)
HARNESS_NAMES = tuple(h.name for h in HARNESSES)


class InstallError(Exception):
    """An entry that cannot be installed or removed; the message says why."""


@dataclass(frozen=True)
class Bases:
    home: Path
    config: Path

    def resolve(self, ref: tuple[str, str]) -> Path:
        base, rel = ref
        return (self.home if base == "home" else self.config) / rel


def default_bases(home: Path | None) -> Bases:
    """The home folder, and the XDG config folder (only when it is set and
    no explicit home was given: a test home must not read the real one)."""
    if home is not None:
        return Bases(home, home / ".config")
    real_home = Path.home()
    xdg = os.environ.get("XDG_CONFIG_HOME")
    return Bases(real_home, Path(xdg) if xdg else real_home / ".config")


def claude_override(bases: Bases, harness: Harness, explicit_home: bool) -> Harness:
    """Claude Code honours CLAUDE_CONFIG_DIR; follow it when set."""
    configured = os.environ.get("CLAUDE_CONFIG_DIR")
    if harness.name != "claude-code" or not configured or explicit_home:
        return harness
    path = Path(configured)
    return Harness(harness.name, ("home", str(path)), ("home", str(path / "skills")))


def is_detected(bases: Bases, harness: Harness) -> bool:
    return bases.resolve(harness.marker).is_dir()


def entry_state(entry: Path) -> str:
    """One of: absent, ours-link, ours-copy, foreign."""
    if entry.is_symlink():
        try:
            return "ours-link" if entry.resolve(strict=True) == SKILL_DIR else "foreign"
        except (OSError, RuntimeError):
            return "foreign"  # a broken or looping link we did not make
    if not entry.exists():
        return "absent"
    if entry.is_dir() and (entry / COPY_MARKER).is_file():
        return "ours-copy"
    return "foreign"


def install_entry(entry: Path, copy: bool, dry_run: bool) -> str:
    state = entry_state(entry)
    wanted = "ours-copy" if copy else "ours-link"
    if state == wanted and not copy:
        return "already installed"
    if state == "foreign":
        raise InstallError(f"{entry} exists and was not installed by this script; left untouched")
    if state != "absent" and state != wanted:
        raise InstallError(f"{entry} is installed as a {state.split('-')[1]}; "
                           f"run --uninstall first to switch to a {wanted.split('-')[1]}")
    if dry_run:
        return f"would {'refresh the copy' if state == wanted else ('copy' if copy else 'link')}"
    entry.parent.mkdir(parents=True, exist_ok=True)
    if copy:
        if state == "ours-copy":
            shutil.rmtree(entry)
        shutil.copytree(SKILL_DIR, entry, ignore=COPY_IGNORE)
        (entry / COPY_MARKER).write_text(f"copied from {SKILL_DIR}\n", encoding="utf-8")
        return "refreshed the copy" if state == "ours-copy" else "copied"
    entry.symlink_to(SKILL_DIR, target_is_directory=True)
    return "linked"


def uninstall_entry(entry: Path, dry_run: bool) -> str:
    state = entry_state(entry)
    if state == "absent":
        return "not installed"
    if state == "foreign":
        raise InstallError(f"{entry} was not installed by this script; left untouched")
    if dry_run:
        return "would remove"
    if state == "ours-link":
        entry.unlink()
    else:
        shutil.rmtree(entry)
    return "removed"


def select(bases: Bases, names: list[str] | None, explicit_home: bool) -> list[tuple[Harness, bool]]:
    chosen = [claude_override(bases, h, explicit_home) for h in HARNESSES
              if names is None or h.name in names]
    return [(h, is_detected(bases, h)) for h in chosen]


def list_harnesses(bases: Bases, explicit_home: bool) -> int:
    for harness, detected in select(bases, None, explicit_home):
        entry = bases.resolve(harness.skills) / SKILL_NAME
        state = entry_state(entry)
        print(f"{harness.name:15} {'detected' if detected else 'absent  '}  {state:9}  {entry}")
    return EXIT_OK


def run(bases: Bases, names: list[str] | None, copy: bool, uninstall: bool,
        dry_run: bool, explicit_home: bool) -> int:
    targets: dict[Path, list[str]] = {}
    for harness, detected in select(bases, names, explicit_home):
        if detected or names is not None:
            targets.setdefault(bases.resolve(harness.skills) / SKILL_NAME, []).append(harness.name)
    if not targets:
        print("no known harness detected; name one with --harness, or see --list", file=sys.stderr)
        return EXIT_NONE_DETECTED
    failed = False
    for entry, owners in targets.items():
        try:
            outcome = uninstall_entry(entry, dry_run) if uninstall else install_entry(entry, copy, dry_run)
            print(f"{', '.join(owners)}: {outcome}: {entry}")
        except (InstallError, OSError) as exc:
            failed = True
            print(f"{', '.join(owners)}: conflict: {exc}", file=sys.stderr)
    if copy and not uninstall and not failed:
        print("note: a copied skill creates cells without the validator (see SKILL.md)")
    return EXIT_CONFLICT if failed else EXIT_OK


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Install the {SKILL_NAME} skill into the agent harnesses found.")
    parser.add_argument("--list", action="store_true", help="show every known harness and its state")
    parser.add_argument("--harness", action="append", choices=HARNESS_NAMES, metavar="NAME",
                        help="only this harness, detected or not (repeatable): "
                             + ", ".join(HARNESS_NAMES))
    parser.add_argument("--copy", action="store_true", help="copy the folder instead of linking it")
    parser.add_argument("--uninstall", action="store_true", help="remove what this script installed")
    parser.add_argument("--dry-run", action="store_true", help="say what would change, change nothing")
    parser.add_argument("--home", type=Path, help="home folder to use instead of the real one")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < MIN_PYTHON:
        print(f"install.py needs Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or later", file=sys.stderr)
        return EXIT_USAGE
    args = parse_args(sys.argv[1:] if argv is None else argv)
    explicit_home = args.home is not None
    if explicit_home and not args.home.is_dir():
        print(f"--home {args.home} is not a folder", file=sys.stderr)
        return EXIT_USAGE
    bases = default_bases(args.home)
    if args.list:
        return list_harnesses(bases, explicit_home)
    return run(bases, args.harness, args.copy, args.uninstall, args.dry_run, explicit_home)


if __name__ == "__main__":
    sys.exit(main())
