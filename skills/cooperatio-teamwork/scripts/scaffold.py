#!/usr/bin/env python3
"""Create an empty cooperatio production-cell folder for a target.

Usage:
    scaffold.py --target "Quarterly report" --roles writer verifier reviewer \
        --out ./teamwork

Creates the layout of the generic recipe (the tree that
``assemble_production_cell`` starts from): brief, sources of truth, canon as
data, artifact list, one role card per role, the gates file, the rubric (with
its hash placeholder), the contracts, validator and engine folders, state
(with the empty note ledger and round record), review, lessons, open notes
and the registry of prior instances. Each file is filled with the skeleton
from references/templates.md. The canon of the target carries the sections
the recipe prescribes (numbers, variants, names, rules) and the empty
sections the validator consumes (terms, lists, triggers, recorded facts):
the method's own vocabulary belongs to the corpus of the method, not to a
target.

The cell ships its ``layout.json`` (every gate on the ``builtin-json-canon``
parser, registry at ``priors.json``, rubric at ``07-rubric.md``, sensitivity
report at ``08-validator/sensitivity.md`` and perturbation set at
``08-validator/perturbations.json`` — the paths the validator's
``p-frozen-rubric`` and ``p-sensitivity`` gates read through the
``artifacts.rubric``, ``artifacts.sensitivity`` and ``artifacts.perturbations``
layout keys), a minimal perturbation set of three generic defects, and, when
the corpus is reachable relative to this script, copies of ``validator.py``
and ``sensitivity.py`` under ``08-validator/`` and of the note, note state
and round contracts under ``05-contracts/``. The skill needs the corpus for those
copies: copied alone, it creates the cell without them, says so, and the cell
has no validator until one is copied in.

Refuses to touch an existing non-empty folder: it never overwrites.

Exit codes: 0 created; 2 invalid input, destination not empty or I/O error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROLE_ID = re.compile(r"[a-z][a-z0-9-]*")
ROLE_CARD_FIELDS = (
    "Decides",
    "Does not decide",
    "Inputs",
    "Outputs",
    "Exit gate",
    "Notes it emits",
    "Code-conversion degree",
)
# Sections of the canon of a target, per the generic recipe (step 3): no
# "Method terms", no "Terms to avoid", no "Fixed lists" — those are sections
# of the reflexive application of the method, not of a target. The validator
# consumes the sections below, so a new cell writes them all, as empty lists.
CANON_SECTIONS = (
    "canonical numbers",
    "accepted variants",
    "names and terms",
    "rules",
)
CANON_CONSUMED_KEYS = (
    "terms to avoid",
    "instantiation table rows",
    "mandatory sections",
    "role card fields",
    "origin labels",
    "method components",
    "prior-statement triggers",
    "recorded facts",
    "efficacy triggers",
)
# Embedded copy of the validator's builtin gates: the skill may be copied
# alone, without the corpus, so it cannot import the validator module.
BUILTIN_GATES = (
    "p-terms", "p-canon-link", "p-anonymity", "p-form", "p-size",
    "p-table", "p-sections", "p-card", "p-limit", "p-references",
    "p-prior", "p-prior-mark", "p-prior-pin", "p-contract-shape",
    "p-recipe", "p-components", "p-efficacy-mark",
)
CORPUS_APPLICATION = Path(__file__).resolve().parents[3] / "02-reflexive-application"
VALIDATOR_SRC = CORPUS_APPLICATION / "80-validator" / "validator.py"
# What the cell copies from the corpus when it is reachable (v0.5.0): the
# two scripts, so the cell measures its own sensitivity, and the contracts
# of the note ledger, of the state of its notes (state/notes-status.jsonl)
# and of the round record the skill names. Paths relative
# to the corpus application and to the cell.
CORPUS_COPIES = (
    ("80-validator/validator.py", "08-validator/validator.py"),
    ("80-validator/sensitivity.py", "08-validator/sensitivity.py"),
    ("05-contracts/notes.schema.json", "05-contracts/notes.schema.json"),
    ("05-contracts/notes-status.schema.json", "05-contracts/notes-status.schema.json"),
    ("05-contracts/round-record.schema.json", "05-contracts/round-record.schema.json"),
)
EMPTY_DIRS = ("05-contracts", "08-validator", "09-engine", "review")
# The contract version the validator reads (IM21, v0.5.0); the canon
# contract written here declares it like the corpus contracts.
CONTRACT_VERSION = "1"


class ScaffoldError(Exception):
    """Raised when the arguments or the destination are unusable."""


def brief_text(target: str) -> str:
    return f"""# Brief: {target}

Target: <what is delivered, one sentence>
Audience: <who uses it>

## Non-negotiables

- <constraint that no role may trade away>

## Owner decisions

| Decision | Status | Blocks |
| --- | --- | --- |
| <decision only the owner can take> | open | <artifact that depends on it> |

## Budget and stopping criterion

- Maximum rounds per artifact: <n>
- Stop when: <condition declared before the last round>
"""


def sources_text(target: str) -> str:
    return f"""# Sources of truth: {target}

One source per content type; the source that errs least, never the writer.

| Content type | Source that errs least | Who consults it | Forbidden as a source |
| --- | --- | --- | --- |
| fact | <primary source> | <role> | the writer; a generative tool |
| number | <instrument or canon> | <role> | the prose that cites it |
| exact text | <original or the engine> | <role> | a generative tool |
"""


def canon_doc(target: str, owner_role: str) -> dict:
    """The canon of the target as data: numbers, variants, names, rules,
    plus the sections the validator consumes, as empty lists."""
    sections = []
    for name in CANON_SECTIONS:
        sections.append({
            "name": name,
            "owner": owner_role,
            "version": "v1",
            "state": "pending",
        })
    canon = {
        "target": target,
        "note": "single source of numbers, names, variants and rules; "
                "every section has an owner and a version",
        "version": "v1",
        "sections": sections,
        "canonical numbers": [
            {"value": None, "unit": None,
             "spelling": {"table": "", "prose": "", "code": ""},
             "nature": "fact or hypothesis", "source": ""},
        ],
        "accepted variants": [
            {"variant": "", "holds where": "", "why": ""},
        ],
        "names and terms": [
            {"name": "", "prefer": "", "gloss marker": ""},
        ],
        "rules": [],
    }
    for key in CANON_CONSUMED_KEYS:
        canon[key] = []
    return canon


# The numbers the cell itself states about registered priors: one object per
# number, the prior named by the [prior:<id>] mark in the context, the
# section(s) of that prior's method document where the number lives. The
# validator fails a prior number without its row (v0.4.0).
RECORDED_FACTS_SCHEMA = {
    "type": "array",
    "description": "The numbers this cell states about registered priors, each "
                   "with the sections of the prior's method document where it lives.",
    "items": {
        "type": "object",
        "required": ["number", "context", "section"],
        "additionalProperties": False,
        "properties": {
            "number": {"type": "string", "description": "the number as written, e.g. '18'"},
            "context": {"type": "string",
                        "description": "what it counts, with the mark, e.g. "
                                       "'roles with a card [prior:000-example]'"},
            "section": {"type": "string",
                        "description": "section label(s) of the prior's method document, e.g. '1.1'"},
        },
    },
}


def canon_schema_doc() -> dict:
    """The contract of the canon, in the keyword subset the validator
    applies (anything outside it would be censused in the cell itself)."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "02-canon.schema.json",
        "contract_version": CONTRACT_VERSION,
        "title": "Canon contract",
        "description": "The canon of a target. The sections the validator "
                       "consumes are lists of strings; the target's own "
                       "sections (numbers, variants, names, rules) are free.",
        "type": "object",
        "required": ["version", *CANON_CONSUMED_KEYS],
        "properties": {
            "version": {
                "type": "string",
                "description": "The canon schema version this cell's canon "
                               "declares; the validator refuses a different one."
            },
            **{key: {"type": "array", "items": {"type": "string"}}
               for key in CANON_CONSUMED_KEYS},
            "recorded facts": RECORDED_FACTS_SCHEMA},
    }


def artifacts_doc(target: str) -> list:
    """One record per artifact, in the format of the generic recipe."""
    return [{
        "name": "<artifact>",
        "owner": "<role or owner>",
        "paths": ["<relative path>"],
        "depends_on": [],
        "schema": None,
        "command": None,
        "gates": ["<gate ids>"],
        "resource": "code | agent | human | machine",
        "proposed": False,
    }]


def layout_doc() -> dict:
    """The layout the cell ships: the JSON parser for the canon and the
    artifact list, and the cell's own registry of priors."""
    return {
        "version": 1,
        "artifacts": {
            "canon": "02-canon.json",
            "artifacts": "03-artifacts.json",
            "gates-and-rubric": "06-gates.md",
            "roles-dir": "04-roles",
            "rubric": "07-rubric.md",
            "sensitivity": "08-validator/sensitivity.md",
            "perturbations": "08-validator/perturbations.json",
        },
        "gates": {gate: "builtin-json-canon" for gate in BUILTIN_GATES},
        "registry": "priors.json",
    }


def role_card_text(role: str) -> str:
    """The card in bold fields — the format the `p-card` gate reads."""
    fields = "\n\n".join(f"**{field}:**\n\n- <fill in>"
                          for field in ROLE_CARD_FIELDS)
    return f"""# Role card: {role}

Canon: [02-canon.json](../02-canon.json)

{fields}
"""


def gates_text(target: str) -> str:
    return f"""# Gates: {target}

| Gate | Artifact | Magnitude | Limit | Justification |
| --- | --- | --- | --- | --- |

One row per gate once the cell names its gates (the builtin ids the
validator implements, e.g. `p-terms`, `p-form`); a placeholder row here
would make the first real run exit 2 on "no implementation".

### Size ranges

| Document | Minimum | Maximum |
| --- | --- | --- |
"""


def rubric_text(target: str) -> str:
    return f"""# Rubric: {target}

Frozen before the first review; its sha256 is stored in `07-rubric.sha256`.

## Dimensions

| Dimension | What is measured | 1 | 3 | 5 |
| --- | --- | --- | --- | --- |
| D1 <name> | <measurable statement> | <failing anchor> | <middling anchor> | <passing anchor> |

## Finding severity

| Severity | When |
| --- | --- |
| blocking | <defect that invalidates the target> |
| high | <gap that stops a role from executing a step> |
| medium | <imprecision without a hypothesis mark> |
| low | <style or local readability> |

## Verdict rule

```text
if any blocking finding or any dimension scores <= 2:
    verdict = rejected
else if no high finding and every dimension >= 4:
    verdict = accepted
else:
    verdict = accepted with conditions
```
"""


def lessons_text(target: str) -> str:
    return f"""# Lessons: {target}

What each round taught; what became code, contract or gate.
"""


def write_new(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(content)


def write_json_new(path: Path, data: object) -> None:
    write_new(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def copy_corpus_files(out: Path, created: list[Path]) -> None:
    """Copy the corpus scripts and contracts into the cell (CORPUS_COPIES).

    The skill may be copied alone, without the corpus around it: then the
    copies are skipped with a printed note naming what is missing, and the
    cell has no validator until someone copies one in (v0.5.0: the earlier
    note said the cell "works all the same", which was not true).
    """
    missing = []
    for source, relative in CORPUS_COPIES:
        try:
            content = (CORPUS_APPLICATION / source).read_text(encoding="utf-8")
        except OSError:
            missing.append(relative)
            continue
        write_new(out / relative, content)
        created.append(out / relative)
    if missing:
        print(f"note: not found corpus-relative, so not copied: {', '.join(missing)}; "
              "the cell has no validator or sensitivity test until you copy them in "
              "from the cooperatio material")


def perturbations_doc(first_role: str) -> list[dict]:
    """The minimal perturbation set of a new cell (v0.5.0): three generic
    defects the cell's sensitivity test injects. They assume the brief keeps
    its template headings, a card of the first role keeps '**Decides:**' and
    the canon avoids 'pipeline'; edit them to the cell's own text and add one
    per gate the cell assigns."""
    return [
        {"name": "avoid-word inserted", "document": "00-brief.md", "old": "## Non-negotiables",
         "new": "## Non-negotiables of the pipeline", "gate": "p-terms"},
        {"name": "absolute path inserted", "document": "00-brief.md", "old": "## Owner decisions",
         "new": "## Owner decisions (see /etc/brief.txt)", "gate": "p-anonymity"},
        {"name": "card field deleted", "document": f"04-roles/{first_role}.md",
         "old": "**Decides:**", "new": "**Also:**", "gate": "p-card"},
    ]


def layout_files(target: str, roles: list[str], out: Path) -> tuple[dict[Path, str], dict[Path, object]]:
    """The files of the production-cell layout: markdown and JSON skeletons."""
    files: dict[Path, str] = {
        out / "00-brief.md": brief_text(target),
        out / "01-sources-of-truth.md": sources_text(target),
        out / "06-gates.md": gates_text(target),
        out / "07-rubric.md": rubric_text(target),
        out / "07-rubric.sha256": "not-frozen\n",
        out / "lessons.md": lessons_text(target),
        out / "open-notes.json": "[]\n",
        out / "state" / "notes.jsonl": "",
        out / "state" / "notes-status.jsonl": "",
        out / "state" / "round-record.jsonl": "",
    }
    json_files: dict[Path, object] = {
        out / "02-canon.json": canon_doc(target, roles[0]),
        out / "03-artifacts.json": artifacts_doc(target),
        out / "priors.json": {"instances": []},
        out / "08-validator" / "perturbations.json": perturbations_doc(roles[0]),
    }
    for role in roles:
        files[out / "04-roles" / f"{role}.md"] = role_card_text(role)
    return files, json_files


def build_cell(target: str, roles: list[str], staging: Path) -> list[Path]:
    """Write the whole cell into the staging folder (C14 helper)."""
    files, json_files = layout_files(target, roles, staging)
    created: list[Path] = []
    for name in EMPTY_DIRS:
        (staging / name).mkdir(parents=True, exist_ok=True)
    for path, content in files.items():
        write_new(path, content)
        created.append(path)
    canon_schema_path = staging / "05-contracts" / "02-canon.schema.json"
    for path, data in json_files.items():
        write_json_new(path, data)
        created.append(path)
    write_json_new(canon_schema_path, canon_schema_doc())
    created.append(canon_schema_path)
    write_json_new(staging / "layout.json", layout_doc())
    created.append(staging / "layout.json")
    copy_corpus_files(staging, created)
    return sorted(created)


def scaffold(target: str, roles: list[str], out: Path) -> list[Path]:
    if not target.strip():
        raise ScaffoldError("--target must not be empty")
    if not roles:
        raise ScaffoldError("at least one role is required")
    for role in roles:
        if not ROLE_ID.fullmatch(role):
            raise ScaffoldError(f"invalid role id {role!r}: use lowercase letters, digits, hyphens")
    if len(set(roles)) != len(roles):
        raise ScaffoldError("duplicate role ids")
    if out.exists() and any(out.iterdir()):
        raise ScaffoldError(f"destination {out} is not empty; refusing to overwrite")
    # C14 (second critical panel): the cell is built in a staging folder
    # SIBLING of the destination (same filesystem, so the rename is atomic)
    # and only then renamed into place — a failure in the middle of the
    # build leaves no partial cell, and no staging folder behind.
    staging = out.with_name(f".{out.name}.scaffold-staging-{os.getpid()}")
    if staging.exists():
        raise ScaffoldError(f"staging folder {staging} already exists; refusing to overwrite")
    try:
        created = build_cell(target, roles, staging)
        os.rename(staging, out)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return [out / path.relative_to(staging) for path in created]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--target", required=True, help="name of the target")
    parser.add_argument("--roles", nargs="+", required=True, help="role ids, e.g. writer verifier")
    parser.add_argument("--out", required=True, type=Path, help="destination folder")
    args = parser.parse_args(argv)
    try:
        created = scaffold(args.target, args.roles, args.out)
    except ScaffoldError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    for path in created:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
