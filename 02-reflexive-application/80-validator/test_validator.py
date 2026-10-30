"""Tests for validator.py (run: python -m pytest test_validator.py).

The fixtures are domain-neutral: a minimal production folder with a canon,
an artifact table, a gates file, one document, one role card, contracts, a
registry and a prior document. No real corpus and no media vocabulary.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import validator
import sensitivity

VALIDATOR = Path(__file__).with_name("validator.py")
SCAFFOLD = Path(__file__).resolve().parents[2] / "skills" / "cooperatio-teamwork" / \
    "scripts" / "scaffold.py"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# Since v0.5.0 the artifact list is the one source of the map from gate to
# artifact, and the gate table mirrors it (a divergence is a p-references
# finding). The fixtures declare their gates in the gate table, as before;
# these helpers write the same map into the Gates column of the artifact
# list, so each fixture keeps exactly the scope it had.
EXIT_PENDING = validator.EXIT_PENDING


def gates_by_artifact(gates_md: str) -> dict[str, list[str]]:
    table = validator.gate_tables(gates_md)[0]
    i_art = validator.column(table, "Artifact")
    by_artifact: dict[str, list[str]] = {}
    for row in table[1:]:
        for name in validator.backticked(row[i_art]):
            by_artifact.setdefault(name, []).append(validator.clean_cell(row[0]))
    return by_artifact


def mirror_artifact_gates(artifacts_md: str, gates_md: str) -> str:
    """The artifact table with its Gates column (the last) rewritten to the
    map of the gate table."""
    by_artifact = gates_by_artifact(gates_md)
    out = []
    for line in artifacts_md.splitlines():
        cells = line.split(" | ")
        names = validator.backticked(cells[0]) if line.startswith("| `") else []
        if names:
            gates = ", ".join(f"`{g}`" for g in by_artifact.get(names[0], [])) or "none"
            line = " | ".join(cells[:-1] + [gates + " |"])
        out.append(line)
    return "\n".join(out) + "\n"


def mirror_json_gates(records: list[dict], gates_md: str) -> list[dict]:
    by_artifact = gates_by_artifact(gates_md)
    return [dict(rec, gates=by_artifact.get(rec["name"], [])) for rec in records]


def write_gates(folder: Path, gates_md: str, artifacts_md: str | None = None) -> None:
    """Write the gates file and the artifact list that mirrors its map."""
    if artifacts_md is None:
        artifacts_md = (folder / "02-artifacts.md").read_text(encoding="utf-8")
    write(folder / "04-gates-and-rubric.md", gates_md)
    write(folder / "02-artifacts.md", mirror_artifact_gates(artifacts_md, gates_md))


CANON = """# Canon: fixture

| Section | Owner | Version | State |
| --- | --- | --- | --- |
| Canon schema | verifier | v1 | ready |
| Method terms | writer | v1 | ready |

## Method terms

| Term | Canonical definition |
| --- | --- |
| target | the thing handed over |

## Terms to avoid

| Avoid | Use | Reason |
| --- | --- | --- |
| pipeline | artifact graph | hides dependencies |

### Instantiation table rows

| Row |
| --- |
| Target |

### Mandatory sections of an instance

| Section |
| --- |
| Brief |

### Role card fields

| Field |
| --- |
| Decides |

### Origin labels of a limit

| Label | Meaning |
| --- | --- |
| `[method]` | the limit follows from the method itself |

### Method components

The components that every instance has to name: artifact graph, gate, note.

### Prior-statement triggers

| Trigger phrase |
| --- |
| `reference case` |
"""

ARTIFACTS = """# Artifacts: fixture

## Table

| Artifact | File | Owner | Depends on | Schema | Gates |
| --- | --- | --- | --- | --- | --- |
| `canon` | `01-canon.md` | writer | — | tables read by the validator | `p-terms` |
| `graph` | `02-artifacts.md` | writer | `canon` | free text | `p-contract-shape` |
| `doc1` | `10-doc1.md` | writer | `canon`, `graph` | free text | `p-terms`, `p-prior`, `p-prior-mark`, `p-canon-link` |
| `notes-ledger` | `90-notes/notes.json` | verifier | `doc1` | the contract in `05-contracts/notes.schema.json` | `p-contract-shape` |
| `contracts` | `05-contracts/notes.schema.json`, `05-contracts/registry.schema.json` | verifier | `canon` | JSON Schema | `p-contract-shape` |
| `registry` | `../instances/registry.json` | verifier | `doc1` | the contract in `05-contracts/registry.schema.json` | `p-prior-pin`, `p-contract-shape` |
"""

GATES = """# Gates: fixture

| Gate | Artifact | Magnitude | Limit | Justification |
| --- | --- | --- | --- | --- |
| `p-terms` | `doc1` | avoid words | 0 | [method] the canon is the single source of terms |
| `p-canon-link` | `doc1` | links to the canon | ≥ 1 | [method] readers need the definitions one hop away |
| `p-prior` | `doc1` | unregistered prior labels | 0 | [method] a prior without a registry entry is not a source |
| `p-prior-mark` | `doc1` | unmarked prior talk | 0 | [method] marked statements are the checkable ones |
| `p-prior-pin` | `registry` | executed priors pinned by sha256 | equal | [method] a pin nobody can re-verify is not a pin |
| `p-contract-shape` | `graph`, `contracts`, `notes-ledger`, `registry` | broken schema cells and contract violations | 0 | [method] a contract that is never applied is not a contract |

### Size ranges

| Document | Minimum | Maximum |
| --- | --- | --- |
| `10-doc1.md` | 1 | 500 |

## Rubric

Fixture rubric, never changed.
"""

CARD = """# Role card: writer

| Field | Content |
| --- | --- |
| Decides | the text of the documents |
"""

DOC1 = """# Document one

Terms follow the [canon](01-canon.md).

In the reference case [prior:000-fixture], the tool gave 49 items.
"""

PRIOR_DOC = "# Prior method document\n\n## 1 Results\n\nThe tool gave 49 items and 2 notes.\n"
# Since the v0.4.0 review (C1) a number about a prior needs a row of that
# prior in "Recorded facts"; the default fixture canon carries the one its
# document cites. A test that writes its own canon writes its own rows.
CANON_FACTS = """
## Recorded facts

| Number | In what context | Where in the prior's method document |
| --- | --- | --- |
| 49 | items the tool gave `[prior:000-fixture]` | section 1 |
"""
PRIOR_SHA = hashlib.sha256(PRIOR_DOC.encode("utf-8")).hexdigest()
# Since v0.4.1 (C16) an executed entry carries its locator too: a relative
# path or this reserved string.
OWNER_HELD = "owner-held, not distributable"

REGISTRY = {"instances": [
    {"id": "000-fixture", "status": "executed",
     "document": "prior-method.md", "sha256": PRIOR_SHA,
     "locator": OWNER_HELD, "number_format": "point-decimal"}]}

NOTES_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "notes.schema.json",
    "contract_version": validator.CONTRACT_VERSION,
    "title": "Note contract",
    "description": "Fixture note contract.",
    "type": "array",
    "items": {
        "type": "object",
        "required": ["target_artifact", "severity", "text", "origin", "evidence", "round"],
        "additionalProperties": False,
        "properties": {
            "target_artifact": {"type": "string"},
            "severity": {"type": "string", "enum": ["low", "medium", "high", "blocking"]},
            "text": {"type": "string"},
            "origin": {"type": "string"},
            "evidence": {"type": "string"},
            "round": {"type": "integer", "minimum": 1}}}}

REGISTRY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "registry.schema.json",
    "contract_version": validator.CONTRACT_VERSION,
    "title": "Instance registry contract",
    "description": "Fixture registry contract.",
    "type": "object",
    "required": ["instances"],
    "additionalProperties": False,
    "properties": {
        "instances": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "status", "document", "sha256"],
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string", "pattern": "^[0-9]{3}-[a-z0-9-]+$"},
                    "status": {"type": "string", "enum": ["executed", "designed"]},
                    "document": {"type": ["string", "null"]},
                    "sha256": {"type": ["string", "null"], "pattern": "^[0-9a-f]{64}$"},
                    "locator": {"type": ["string", "null"]},
                    "number_format": {"type": ["string", "null"],
                                      "enum": ["point-decimal", "comma-decimal", None]}}}}}}

ROUND_RECORD_SCHEMA = {
    "contract_version": validator.CONTRACT_VERSION,
    "type": "object",
    "additionalProperties": False,
    "required": ["method_version", "round", "models", "summary"],
    "properties": {
        "method_version": {"type": "string"},
        "round": {"type": "string"},
        "models": {"type": "array", "items": {
            "type": "object", "required": ["role", "model"],
            "additionalProperties": False,
            "properties": {"role": {"type": "string"},
                           "model": {"type": "string"}}}},
        "summary": {"type": "string"},
        "verdict": {"type": "string", "enum": ["accepted"]},
        "rubric_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    },
}

NOTES = [{"target_artifact": "bible", "severity": "low", "text": "a legacy note",
          "origin": "reviewer", "evidence": "10-doc1.md", "round": 1}]


def build_fixture(root: Path, doc1: str = DOC1, artifacts: str = ARTIFACTS) -> Path:
    folder = root / "cell"
    write(folder / "01-canon.md", CANON + CANON_FACTS)
    write_gates(folder, GATES, artifacts)
    write(folder / "03-roles" / "writer.md", CARD)
    write(folder / "10-doc1.md", doc1)
    write(folder / "05-contracts" / "notes.schema.json", json.dumps(NOTES_SCHEMA))
    write(folder / "05-contracts" / "registry.schema.json", json.dumps(REGISTRY_SCHEMA))
    write(folder / "90-notes" / "notes.json", json.dumps(NOTES))
    write(root / "instances" / "registry.json", json.dumps(REGISTRY))
    write(root / "prior-method.md", PRIOR_DOC)
    return folder


def run_validator(folder: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--folder", str(folder), *extra],
        capture_output=True, text=True, check=False)


@pytest.fixture()
def fixture(tmp_path: Path) -> Path:
    return build_fixture(tmp_path)


# ------------------------------------------------------------ layout, parsers

def test_clean_fixture_reports_the_doc_gate_rows(fixture: Path) -> None:
    """doc1 is in the scope of the four doc gates, so the report must carry
    one row per gate for it (presence checked, not just absence of fail)."""
    proc = run_validator(fixture, "--registry", str(fixture.parent / "instances" / "registry.json"))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    for gate in ("p-terms", "p-canon-link", "p-prior", "p-prior-mark"):
        assert f"| `10-doc1.md` | `{gate}` |" in proc.stdout


def test_clean_fixture_has_no_failing_gate_row(fixture: Path) -> None:
    """A clean fixture produces no fail row anywhere in the report."""
    proc = run_validator(fixture, "--registry", str(fixture.parent / "instances" / "registry.json"))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| fail |" not in proc.stdout


def test_layout_remaps_the_canon_path(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    (fixture / "01-canon.md").rename(fixture / "canon.md")
    write(fixture / "canon.md", CANON.replace("[canon](01-canon.md)", "[canon](canon.md)"))
    write(fixture / "10-doc1.md", DOC1.replace("(01-canon.md)", "(canon.md)"))
    # Since v0.3.0 a declared artifact has to exist: a cell that renames its
    # canon declares the renamed path in its artifact table (p-declared).
    write(fixture / "02-artifacts.md", ARTIFACTS.replace("`01-canon.md`", "`canon.md`"))
    layout = tmp_path / "layout.json"
    layout.write_text(json.dumps(
        {"version": 1, "artifacts": {"canon": "canon.md"}, "gates": {"p-terms": "builtin-markdown"}}),
        encoding="utf-8")
    proc = run_validator(fixture, "--layout", str(layout))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr


def test_layout_rejects_an_unknown_parser(fixture: Path) -> None:
    layout = fixture / "layout.json"
    layout.write_text(json.dumps(
        {"version": 1, "gates": {"p-terms": "custom-parser"}}), encoding="utf-8")
    proc = run_validator(fixture, "--layout", str(layout))
    assert proc.returncode == 2
    assert "available parsers are 'builtin-markdown' and 'builtin-json-canon'" in proc.stderr


def test_layout_rejects_mixed_parsers(fixture: Path) -> None:
    layout = fixture / "layout.json"
    layout.write_text(json.dumps(
        {"version": 1, "gates": {"p-terms": "builtin-markdown", "p-prior": "builtin-json-canon"}}),
        encoding="utf-8")
    proc = run_validator(fixture, "--layout", str(layout))
    assert proc.returncode == 2
    assert "names more than one parser" in proc.stderr


def test_json_canon_parser_validates_a_cell(tmp_path: Path) -> None:
    """The builtin-json-canon parser runs a cell whose canon and artifact
    list are the JSON the scaffold emits."""
    folder = tmp_path / "cell"
    canon_json = {key: [] for key in validator.JSON_CANON_KEYS}
    canon_json["version"] = "v1"
    canon_json["terms to avoid"] = ["pipeline"]
    canon_json["method components"] = ["artifact graph", "gate", "note"]
    canon_json["prior-statement triggers"] = ["reference case"]
    write(folder / "02-canon.json", json.dumps(canon_json))
    artifacts_json = [
        {"name": "graph", "paths": ["03-artifacts.json"], "owner": "writer",
         "depends_on": [], "schema": ""},
        {"name": "doc1", "paths": ["10-doc1.md"], "owner": "writer",
         "depends_on": ["graph"], "schema": ""},
        {"name": "registry", "paths": ["../instances/registry.json"], "owner": "verifier",
         "depends_on": [], "schema": "05-contracts/registry.schema.json"}]
    gates = GATES.replace("`02-artifacts.md`", "`03-artifacts.json`")
    write(folder / "03-artifacts.json", json.dumps(mirror_json_gates(artifacts_json, gates)))
    write(folder / "06-gates.md", gates)
    write(folder / "04-roles" / "writer.md", CARD)
    write(folder / "10-doc1.md", DOC1.replace("(01-canon.md)", "(02-canon.json)"))
    write(folder / "05-contracts" / "registry.schema.json", json.dumps(REGISTRY_SCHEMA))
    write(tmp_path / "instances" / "registry.json", json.dumps(REGISTRY))
    write(tmp_path / "prior-method.md", PRIOR_DOC)
    layout = folder / "layout.json"
    layout.write_text(json.dumps(
        {"version": 1,
         "artifacts": {"canon": "02-canon.json", "artifacts": "03-artifacts.json",
                       "gates-and-rubric": "06-gates.md", "roles-dir": "04-roles"},
         "gates": {gate: "builtin-json-canon" for gate in validator.BUILTIN_GATES},
         "registry": "../instances/registry.json"}), encoding="utf-8")
    proc = run_validator(folder, "--layout", str(layout))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `10-doc1.md` | `p-prior-mark` | 0 | 0 | pass |" in proc.stdout
    assert "| `../instances/registry.json` | `p-prior-pin` |" in proc.stdout


def test_json_parser_rejects_markdown_artifacts(fixture: Path) -> None:
    layout = fixture / "layout.json"
    layout.write_text(json.dumps(
        {"version": 1,
         "artifacts": {"canon": "01-canon.json", "artifacts": "02-artifacts.md"},
         "gates": {gate: "builtin-json-canon" for gate in validator.BUILTIN_GATES}}),
        encoding="utf-8")
    proc = run_validator(fixture, "--layout", str(layout))
    assert proc.returncode == 2
    assert "reads '.json' files" in proc.stderr
    assert "the 'artifacts' artifact is '02-artifacts.md'" in proc.stderr


def test_markdown_parser_rejects_a_json_canon(fixture: Path) -> None:
    (fixture / "01-canon.json").write_text("{}", encoding="utf-8")
    layout = fixture / "layout.json"
    layout.write_text(json.dumps(
        {"version": 1, "artifacts": {"canon": "01-canon.json"}}), encoding="utf-8")
    proc = run_validator(fixture, "--layout", str(layout))
    assert proc.returncode == 2
    assert "reads '.md' files" in proc.stderr


# ------------------------------------------------------------ p-prior, pin

def test_registry_default_is_resolved_next_to_the_parent(fixture: Path) -> None:
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "`p-prior` | 1 labels, 0 unregistered" in proc.stdout


def test_unregistered_prior_label_fails_p_prior(fixture: Path) -> None:
    write(fixture / "10-doc1.md",
          DOC1.replace("[prior:000-fixture]", "[prior:999-unknown]"))
    proc = run_validator(fixture)
    assert proc.returncode == 1
    assert "'999-unknown' is not an instance registered" in proc.stdout


def test_prior_number_outside_the_document_fails_p_prior(fixture: Path) -> None:
    write(fixture / "10-doc1.md",
          DOC1.replace("the tool gave 49 items", "the tool gave 48 items"))
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert proc.returncode == 1
    assert "'48' has no row of that prior in the canon's 'Recorded facts'" in proc.stdout


def test_number_without_a_recorded_fact_fails_even_if_present_in_the_document(
        fixture: Path) -> None:
    """Regression (C1 of the v0.4.0 review): a number without a row used to
    be checked by presence in the whole prior document, so the invented
    '21 roles' of experiment E1 passed the cell's gate (21 occurs once there,
    in an unrelated sentence). '49' is in the document; without its row it
    fails."""
    write(fixture / "01-canon.md", CANON)
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "'49' has no row of that prior in the canon's 'Recorded facts'" in proc.stdout
    assert "checked globally" not in proc.stdout


def test_section_references_are_checked_as_sections_not_as_numbers(fixture: Path) -> None:
    """A cited section ('section 1', 'step 9') has to exist in the prior's
    document and needs no recorded fact; a digit attached to a letter ('v1')
    is a name, not a number."""
    write(fixture / "10-doc1.md", DOC1.replace(
        "the tool gave 49 items.", "the tool gave 49 items in v1 (section 1 of the case)."))
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "1 numbers and 1 section references checked, 0 unverified" in proc.stdout
    write(fixture / "10-doc1.md", DOC1.replace("the tool gave 49 items.",
                                               "the tool gave 49 items (step 9 of the case)."))
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert proc.returncode == 1
    assert "cites section '9' of the prior method document, which does not exist" in proc.stdout


def test_a_count_after_a_section_reference_is_still_a_number(fixture: Path) -> None:
    """Regression (re-review of v0.4.0): the continuation of a section
    reference swallowed the next number, so in 'section 1 and 7 rounds' the
    7 became 'section 7' and was never checked as a count. A label continues
    the reference only before punctuation, the end, a connector or 'of'."""
    write(fixture / "10-doc1.md", DOC1.replace(
        "the tool gave 49 items.", "the tool gave 49 items (section 1 and 7 rounds)."))
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert proc.returncode == 1
    assert "'7' has no row of that prior in the canon's 'Recorded facts'" in proc.stdout
    assert validator.section_references("see sections 1.10 and 4.14 of the case")[0] == ["1.10", "4.14"]
    assert validator.section_references("section 1.4 and 7 rounds")[0] == ["1.4"]


def test_prior_number_is_verified_in_the_cited_section(tmp_path: Path) -> None:
    prior = ("# Prior method document\n\n"
             "## 1 Design\n\nThe tool gave 30 items.\n\n"
             "## 2 Report\n\nThe tool gave 49 items.\n")
    canon = CANON + """
## Recorded facts

| Number | In what context | Where in the prior's method document |
| --- | --- | --- |
| 49 | items in the report `[prior:000-fixture]` | section 2 |
| 30 | items in the report `[prior:000-fixture]` | section 2 |
"""
    fixture = build_fixture(tmp_path, doc1=DOC1)
    write(tmp_path / "prior-method.md", prior)
    write(fixture / "01-canon.md", canon)
    registry = {"instances": [{"id": "000-fixture", "status": "executed",
                               "document": "prior-method.md",
                               "sha256": hashlib.sha256(prior.encode("utf-8")).hexdigest(),
                               "locator": OWNER_HELD, "number_format": "point-decimal"}]}
    write(tmp_path / "instances" / "registry.json", json.dumps(registry))
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "1 numbers and 0 section references checked, 0 unverified" in proc.stdout
    # the same number in the wrong section is an invented fact
    write(fixture / "10-doc1.md",
          DOC1.replace("the tool gave 49 items", "the tool gave 30 items"))
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"))
    assert proc.returncode == 1
    assert "is not in section(s) 2 of the prior method document" in proc.stdout


def test_number_with_a_row_citing_a_numberless_section_is_a_hit(tmp_path: Path) -> None:
    """Regression (rework of the v0.2.1 review): a "Recorded facts" row that
    cites a section containing no numbers used to short-circuit the section
    check (the empty union made `index` falsy), letting an invented number
    pass without any verification."""
    prior = "# Prior method document\n\n## 1 Design\n\nOnly prose lives in this section.\n"
    canon = CANON + """
## Recorded facts

| Number | In what context | Where in the prior's method document |
| --- | --- | --- |
| 49 | items in the design `[prior:000-fixture]` | section 1 |
"""
    fixture = build_fixture(tmp_path)
    write(tmp_path / "prior-method.md", prior)
    write(fixture / "01-canon.md", canon)
    registry = {"instances": [{"id": "000-fixture", "status": "executed",
                               "document": "prior-method.md",
                               "sha256": hashlib.sha256(prior.encode("utf-8")).hexdigest(),
                               "locator": OWNER_HELD, "number_format": "point-decimal"}]}
    write(tmp_path / "instances" / "registry.json", json.dumps(registry))
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"))
    assert proc.returncode == 1
    assert "is not in section(s) 1 of the prior method document" in proc.stdout


def test_unresolvable_section_label_is_a_blocking_note(tmp_path: Path) -> None:
    prior = "# Prior method document\n\n## 1 Design\n\nThe tool gave 49 items.\n"
    canon = CANON + """
## Recorded facts

| Number | In what context | Where in the prior's method document |
| --- | --- | --- |
| 49 | items in the design `[prior:000-fixture]` | section 9 |
"""
    fixture = build_fixture(tmp_path)
    write(tmp_path / "prior-method.md", prior)
    write(fixture / "01-canon.md", canon)
    registry = {"instances": [{"id": "000-fixture", "status": "executed",
                               "document": "prior-method.md",
                               "sha256": hashlib.sha256(prior.encode("utf-8")).hexdigest(),
                               "locator": OWNER_HELD, "number_format": "point-decimal"}]}
    write(tmp_path / "instances" / "registry.json", json.dumps(registry))
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"))
    assert proc.returncode == 1
    assert "cites section '9' of the prior method document, which does not exist" in proc.stdout


def test_without_a_registry_p_prior_is_pending(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    (tmp_path / "instances" / "registry.json").unlink()
    # Since v0.3.0 a declared artifact has to exist, so a folder without a
    # registry does not declare one in its table either (nor cite it in its
    # gates, which p-references would otherwise flag).
    write(fixture / "02-artifacts.md", ARTIFACTS.replace(
        "| `registry` | `../instances/registry.json` | verifier | `doc1` | "
        "the contract in `05-contracts/registry.schema.json` | `p-prior-pin`, `p-contract-shape` |\n", ""))
    write_gates(fixture, GATES.replace(
        "| `p-prior-pin` | `registry` | executed priors pinned by sha256 | equal | "
        "[method] a pin nobody can re-verify is not a pin |\n", "").replace(
        "| `p-contract-shape` | `graph`, `contracts`, `notes-ledger`, `registry` |",
        "| `p-contract-shape` | `graph`, `contracts`, `notes-ledger` |"))
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `10-doc1.md` | `p-prior` | not measured (no instance registry) | 0 | pending |" \
        in proc.stdout


def test_clean_prior_labels_without_the_document_are_pending(fixture: Path) -> None:
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `10-doc1.md` | `p-prior` | 1 labels, 0 unregistered; " \
        "numbers not measured (no prior document) | 0 | pending |" in proc.stdout


def test_registry_that_cannot_be_read_is_a_tool_failure(fixture: Path) -> None:
    proc = run_validator(fixture, "--registry", str(fixture / "nope.json"))
    assert proc.returncode == 2
    assert "could not read nope.json" in proc.stderr


def test_pin_of_the_prior_document_passes(fixture: Path) -> None:
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `../instances/registry.json` | `p-prior-pin` | 1 executed priors pinned | equal | pass |" \
        in proc.stdout


def test_pin_of_a_wrong_document_is_blocking(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    write(tmp_path / "prior-method.md", "# Prior method document\n\nA different text.\n")
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"))
    assert proc.returncode == 1
    assert "wrong or edited prior document" in proc.stdout


def test_pin_of_an_executed_prior_without_sha256_is_blocking(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    registry = {"instances": [{"id": "000-fixture", "status": "executed",
                               "document": "prior-method.md", "sha256": None}]}
    write(tmp_path / "instances" / "registry.json", json.dumps(registry))
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"))
    assert proc.returncode == 1
    assert "no sha256 pinned" in proc.stdout


def test_without_the_prior_document_the_pin_is_pending(fixture: Path) -> None:
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `../instances/registry.json` | `p-prior-pin` | 1 executed priors cited; " \
        "not measured (no prior document) | equal | pending |" in proc.stdout


def test_unmarked_prior_talk_fails_p_prior_mark(fixture: Path) -> None:
    write(fixture / "10-doc1.md",
          DOC1.replace("[prior:000-fixture], the tool gave 49 items",
                       "the tool gave 49 items"))
    proc = run_validator(fixture)
    assert proc.returncode == 1
    assert "without a [prior:<id>] mark" in proc.stdout


def test_trigger_phrases_come_from_the_canon(fixture: Path) -> None:
    """A trigger removed from the canon's table stops being a trigger."""
    canon = CANON.replace("### Prior-statement triggers\n\n| Trigger phrase |\n| --- |\n"
                          "| `reference case` |\n", "")
    write(fixture / "01-canon.md", canon)
    write(fixture / "10-doc1.md",
          DOC1.replace("[prior:000-fixture], the tool gave 49 items",
                       "the tool gave 49 items"))
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr


def test_trigger_matching_is_whole_word_case_insensitive_and_singular() -> None:
    triggers = ["prior instance", "reference case"]
    assert len(validator.prior_mark_hits("In the PRIOR INSTANCE the tool failed.", triggers)) == 1
    assert validator.prior_mark_hits("Prior instances differ from one another.", triggers) == []
    assert validator.prior_mark_hits("It reproduces the case end to end.", triggers) == []


# ------------------------------------------------------------ contracts

def test_missing_schema_file_fails_p_contract_shape(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path, artifacts=ARTIFACTS.replace(
        "`05-contracts/notes.schema.json`", "`05-contracts/gone.schema.json`"))
    proc = run_validator(fixture)
    assert proc.returncode == 1
    assert "schema '05-contracts/gone.schema.json' does not exist" in proc.stdout


def test_invalid_schema_json_fails_p_contract_shape(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    write(fixture / "05-contracts" / "notes.schema.json", "{not json")
    proc = run_validator(fixture)
    assert proc.returncode == 1
    assert "is not valid JSON" in proc.stdout


def test_schema_outside_the_supported_subset_is_a_note(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    schema = dict(REGISTRY_SCHEMA)
    schema["format"] = "date"
    write(fixture / "05-contracts" / "registry.schema.json", json.dumps(schema))
    proc = run_validator(fixture)
    assert proc.returncode == 1
    assert "keyword 'format' is outside the subset the validator applies" in proc.stdout


def test_registry_data_is_validated_against_its_schema(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    registry = {"instances": [{"id": "000-fixture", "status": "imagined",
                               "document": None, "sha256": None}]}
    write(tmp_path / "instances" / "registry.json", json.dumps(registry))
    proc = run_validator(fixture)
    assert proc.returncode == 1
    assert "'imagined' is not one of the allowed values" in proc.stdout


def test_notes_ledger_is_validated_against_its_schema(fixture: Path) -> None:
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `90-notes/notes.json` | `p-contract-shape` | 0 violations | 0 | pass |" \
        in proc.stdout


def test_notes_ledger_with_an_unknown_field_fails(fixture: Path) -> None:
    notes = [dict(NOTES[0], extra=1)]
    write(fixture / "90-notes" / "notes.json", json.dumps(notes))
    proc = run_validator(fixture)
    assert proc.returncode == 1
    assert "unknown field 'extra'" in proc.stdout


def test_mini_validator_applies_each_supported_keyword() -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "sha256", "models", "round"],
        "properties": {
            "id": {"type": "string", "pattern": "^[0-9]{3}-[a-z]+$"},
            "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "models": {"type": "array", "items": {
                "type": "object",
                "required": ["role"],
                "additionalProperties": False,
                "properties": {"role": {"type": "string"}}}},
            "round": {"type": "integer", "minimum": 1},
            "verdict": {"type": "string", "enum": ["accepted"]},
        },
    }
    bad = {"id": "x", "sha256": "zz", "models": [{"role": 1}],
           "round": 0, "extra": 1, "verdict": "rejected"}
    hits = validator.check_against_schema(bad, schema, "$")
    assert len(hits) == 6
    assert "$.id: 'x' does not match the required pattern" in hits
    assert "$.sha256: 'zz' does not match the required pattern" in hits
    assert "$.models[0].role: expected type string" in hits
    assert "$.round: 0 is below the minimum 1" in hits
    assert "$: unknown field 'extra'" in hits
    assert "$.verdict: 'rejected' is not one of the allowed values" in hits
    missing = {"id": "000-x", "sha256": "a" * 64, "round": 1}
    assert "$: required field 'models' is missing" in validator.check_against_schema(
        missing, schema, "$")


def test_round_record_is_validated_line_by_line(tmp_path: Path) -> None:
    artifacts = ARTIFACTS + (
        "| `round-record` | `state/round-record.jsonl` | writer | — | "
        "the contract in `05-contracts/round-record.schema.json` | `p-contract-shape` |\n")
    gates = GATES.replace(
        "`notes-ledger`, `registry` |",
        "`notes-ledger`, `registry`, `round-record` |")
    fixture = build_fixture(tmp_path, artifacts=artifacts)
    write_gates(fixture, gates)
    write(fixture / "05-contracts" / "round-record.schema.json",
          json.dumps(ROUND_RECORD_SCHEMA))
    valid = {"method_version": "0.2.0", "round": "v0.2",
             "models": [{"role": "coder", "model": "fixture"}], "summary": "ok"}
    write(fixture / "state" / "round-record.jsonl", json.dumps(valid) + "\n")
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `state/round-record.jsonl` | `p-contract-shape` | 1 lines, 0 violations " \
        "| 0 | pass |" in proc.stdout
    invalid = dict(valid, verdict="maybe")
    write(fixture / "state" / "round-record.jsonl",
          json.dumps(valid) + "\n" + json.dumps(invalid) + "\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1
    assert "2 lines, 1 violations" in proc.stdout
    assert "line 2" in proc.stdout and "'maybe' is not one of the allowed values" in proc.stdout


# ------------------------------------------------------------ notes, help

def test_p_notes_accepts_the_legacy_bible_target(fixture: Path) -> None:
    proc = run_validator(fixture, "--notes", str(fixture / "90-notes" / "notes.json"))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| 1 notes, 0 invalid | 0 invalid | pass |" in proc.stdout


def test_p_notes_rejects_a_target_outside_the_graph(fixture: Path) -> None:
    notes = list(NOTES) + [dict(NOTES[0], target_artifact="ghost")]
    write(fixture / "90-notes" / "notes.json", json.dumps(notes))
    proc = run_validator(fixture, "--notes", str(fixture / "90-notes" / "notes.json"))
    assert proc.returncode == 1
    assert "'ghost' outside the graph" in proc.stdout


def test_replies_ledger_is_exempt_from_p_terms(tmp_path: Path) -> None:
    artifacts = ARTIFACTS + (
        "| `replies` | `90-review/replies.md` | writer | — | free text | `p-terms` |\n")
    gates = GATES.replace("| `p-terms` | `doc1` |", "| `p-terms` | `doc1`, `replies` |")
    fixture = build_fixture(tmp_path, artifacts=artifacts)
    write_gates(fixture, gates)
    write(fixture / "90-review" / "replies.md",
          "# Replies\n\nThis pipeline is frozen history.\n")
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `90-review/replies.md` | `p-terms` | exempt by design (frozen ledger) " \
        "| 0 | pass |" in proc.stdout


def test_card_may_aim_notes_at_the_legacy_bible_target(tmp_path: Path) -> None:
    artifacts = ARTIFACTS + (
        "| `writer-card` | `03-roles/writer.md` | writer | — | free text | `p-references` |\n")
    gates = GATES.replace(
        "\n### Size ranges",
        "| `p-references` | `writer-card` | undeclared note targets | 0 | "
        "[method] notes have to aim at a declared artifact |\n\n### Size ranges")
    fixture = build_fixture(tmp_path, artifacts=artifacts)
    write_gates(fixture, gates)
    write(fixture / "03-roles" / "writer.md",
          CARD + "\n**Notes it emits:** to the `bible`, per finding.\n")
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `03-roles/writer.md` | `p-references` | 0 | 0 | pass |" in proc.stdout


def test_files_of_reads_a_literal_parent_path_and_non_markdown(tmp_path: Path) -> None:
    artifacts = ARTIFACTS + (
        "| `outside` | `../prior-method.md` | writer | — | free text | `p-form` |\n"
        "| `contract-json` | `05-contracts/notes.schema.json` | writer | — | free text "
        "| `p-form` |\n")
    gates = GATES.replace(
        "\n### Size ranges",
        "| `p-form` | `outside`, `contract-json` | HTML | 0 | "
        "[method] form rules apply to every measured document |\n\n### Size ranges")
    fixture = build_fixture(tmp_path, artifacts=artifacts)
    write_gates(fixture, gates)
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `../prior-method.md` | `p-form` |" in proc.stdout
    assert "| `05-contracts/notes.schema.json` | `p-form` |" in proc.stdout


def test_freeze_rubric_reads_the_gates_file_named_by_the_layout(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    custom = GATES.replace("Fixture rubric, never changed.",
                           "Custom rubric, frozen by the cell.")
    write(fixture / "custom-gates.md", custom)
    layout = fixture / "layout.json"
    layout.write_text(json.dumps(
        {"version": 1, "artifacts": {"gates-and-rubric": "custom-gates.md"}}),
        encoding="utf-8")
    frozen = tmp_path / "frozen.sha256"
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--folder", str(fixture),
         "--layout", str(layout), "--freeze-rubric", str(frozen)],
        capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert frozen.read_text(encoding="utf-8").strip() == validator.rubric_hash(
        custom, "custom-gates.md")
    assert frozen.read_text(encoding="utf-8").strip() != validator.rubric_hash(GATES)


def test_help_documents_the_exit_codes() -> None:
    proc = subprocess.run([sys.executable, str(VALIDATOR), "--help"],
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 0
    assert "exit codes: 0" in proc.stdout
    assert "invalid input or tool failure" in proc.stdout


# ------------------------------------------------------------ cell integration

def test_scaffolded_cell_runs_the_copied_validator(tmp_path: Path) -> None:
    """Integration: the cell the scaffold emits runs on its own copied
    validator, with the layout it ships (D1.4). Since v0.3.0 (C4a/C2 of the
    panel) a freshly scaffolded cell is NOT green: it measures zero
    documents and its template artifact matches no file — both blocking."""
    proc = subprocess.run(
        [sys.executable, str(SCAFFOLD), "--target", "integration-test",
         "--roles", "writer", "verifier", "--out", str(tmp_path / "cell")],
        capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    cell_validator = tmp_path / "cell" / "08-validator" / "validator.py"
    if not cell_validator.exists():
        pytest.skip("scaffold shipped without the validator copy (skill copied alone)")
    run = subprocess.run(
        [sys.executable, str(cell_validator), "--folder", str(tmp_path / "cell"),
         "--layout", str(tmp_path / "cell" / "layout.json")],
        capture_output=True, text=True, check=False)
    assert run.returncode == 1, run.stdout + run.stderr
    assert "# Validator report" in run.stdout
    assert "no documents were measured; a production with no documents is not green" in run.stdout
    assert "declared artifact missing" in run.stdout


def test_scaffolded_cell_freezes_its_own_rubric(tmp_path: Path) -> None:
    """Probe C of the panel (C4b): in a cell, --freeze-rubric resolves the
    rubric through the layout (artifacts.rubric -> 07-rubric.md), not
    through the corpus default; the freeze refuses an existing pin and
    --re-freeze-rubric replaces it deliberately."""
    proc = subprocess.run(
        [sys.executable, str(SCAFFOLD), "--target", "freeze-test",
         "--roles", "writer", "--out", str(tmp_path / "cell")],
        capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    cell = tmp_path / "cell"
    cell_validator = cell / "08-validator" / "validator.py"
    if not cell_validator.exists():
        pytest.skip("scaffold shipped without the validator copy (skill copied alone)")
    pin = cell / "07-rubric.sha256"
    first = subprocess.run(
        [sys.executable, str(cell_validator), "--folder", str(cell),
         "--layout", str(cell / "layout.json"), "--freeze-rubric", str(pin)],
        capture_output=True, text=True, check=False)
    assert first.returncode == 0, first.stdout + first.stderr
    recorded = pin.read_text(encoding="utf-8").strip()
    assert recorded == hashlib.sha256(
        (cell / "07-rubric.md").read_bytes()).hexdigest()
    again = subprocess.run(
        [sys.executable, str(cell_validator), "--folder", str(cell),
         "--layout", str(cell / "layout.json"), "--freeze-rubric", str(pin)],
        capture_output=True, text=True, check=False)
    assert again.returncode == 2
    assert "the rubric is already frozen at" in again.stderr
    assert "--re-freeze-rubric" in again.stderr
    re_freeze = subprocess.run(
        [sys.executable, str(cell_validator), "--folder", str(cell),
         "--layout", str(cell / "layout.json"), "--re-freeze-rubric", str(pin)],
        capture_output=True, text=True, check=False)
    assert re_freeze.returncode == 0, re_freeze.stdout + re_freeze.stderr
    assert pin.read_text(encoding="utf-8").strip() == recorded


# --------------------------------------------------- m-determinism (C13, v0.2.2)

def test_report_presents_m_determinism_as_a_pending_measurement(fixture: Path) -> None:
    """C13 (second critical panel): the report's determinism is a
    measurement of the instrument, never a corpus-gate row."""
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "## Instrument measurement" in proc.stdout
    assert ("| `m-determinism` | `80-validator/report.md` | "
            "not measured (no --determinism flag) | equal | pending |") in proc.stdout
    assert "`p-determinism`" not in proc.stdout


def test_determinism_flag_replaces_the_pending_measurement(fixture: Path) -> None:
    """With --determinism the pending row becomes the measured one; the
    corpus table above is untouched (the measurement has its own section)."""
    proc = run_validator(fixture, "--determinism")
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert ("| `m-determinism` | `80-validator/report.md` | "
            "sha256 equal in 2 runs | equal | pass |") in proc.stdout
    assert "not measured (no --determinism flag)" not in proc.stdout


# ------------------------------------------------- sensitivity path (v0.2.3)

def valid_sensitivity_header(folder: Path, sha: str | None = None,
                              ids: list[str] | None = None,
                              count: int | None = None) -> str:
    """A provenance header the running instrument accepts: the sha256 of
    the validator.py next to this test (the gate's fallback neighbor), of
    the folder's gate section and canon (v0.5.0) and the current
    perturbation set — or deliberate divergences."""
    if sha is None:
        sha = hashlib.sha256(
            Path(validator.__file__).resolve().with_name("validator.py").read_bytes()).hexdigest()
    if ids is None:
        ids = [pert.name for pert in sensitivity.PERTURBATIONS]
    n = len(ids) if count is None else count
    digests = validator.provenance_inputs(folder, validator.DEFAULT_LAYOUT)
    return (f"validator sha256: {sha}\ngates sha256: {digests['gates']}\n"
            f"canon sha256: {digests['canon']}\nperturbations: {n} ({', '.join(ids)})")


# The size of the running perturbation set (22 since v0.4.0): the tests
# follow the instrument instead of a literal count that each round changes.
# Since v0.5.0 the table has to add up to its 'Caught' line, so the
# fabricated reports carry one row per perturbation.
N_PERTURBATIONS = len(sensitivity.PERTURBATIONS)
CAUGHT_ALL = ("| Perturbation | Document | Expected gate | Result |\n| --- | --- | --- | --- |\n"
              + "".join(f"| {pert.name} | `{pert.document}` | `{pert.gate}` | caught |\n"
                        for pert in sensitivity.PERTURBATIONS)
              + f"\nCaught {N_PERTURBATIONS} of {N_PERTURBATIONS}.")


def test_sensitivity_path_resolves_through_the_layout(tmp_path: Path) -> None:
    """Regression (v0.2.3, medium finding of instance 004): the sensitivity
    report used to be read from a hardcoded directory, so every scaffolded
    cell (08-validator/) showed p-sensitivity as pending; the path now
    resolves through the layout, like canon, gates, rubric and registry."""
    fixture = build_fixture(tmp_path)
    write(fixture / "alt-sensitivity.md",
          "# Validator sensitivity\n\n" + valid_sensitivity_header(fixture) +
          "\n\n" + CAUGHT_ALL + "\n")
    layout = tmp_path / "layout-alt-sensitivity.json"
    layout.write_text(json.dumps(
        {"version": 1, "artifacts": {"sensitivity": "alt-sensitivity.md"}}),
        encoding="utf-8")
    proc = run_validator(fixture, "--layout", str(layout))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert re.search(r"^\| `alt-sensitivity\.md` \| `p-sensitivity` \| (\d+) of \1 gates covered, "
                     f"0 missed of {N_PERTURBATIONS} \\| every gate covered, 0 missed \\| pass \\|$",
                     proc.stdout, re.M), proc.stdout


def test_sensitivity_without_a_report_is_pending_with_the_reason(fixture: Path) -> None:
    """A cell whose report is missing gets a pending that names the path it
    looked for and the layout key that points there — never a crash, never a
    silent pass."""
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert ("| `80-validator/sensitivity.md` | `p-sensitivity` | not measured "
            "(no sensitivity report at '80-validator/sensitivity.md'; the "
            "layout key artifacts.sensitivity points there) | every gate covered, 0 missed | "
            "pending |") in proc.stdout


def test_sensitivity_report_without_a_caught_line_is_a_tool_failure(tmp_path: Path) -> None:
    """A report with a valid provenance header but no Caught line is
    malformed input: tool failure (exit 2), not a blocking note."""
    fixture = build_fixture(tmp_path)
    write(fixture / "80-validator" / "sensitivity.md",
          "# Validator sensitivity\n\n" + valid_sensitivity_header(fixture) + "\n")
    proc = run_validator(fixture)
    assert proc.returncode == 2
    assert "has no line 'Caught X of Y.'" in proc.stderr


def test_fabricated_sensitivity_report_without_provenance_is_blocking(tmp_path: Path) -> None:
    """Probe D of the panel (C3): a file that says 'Caught 14 of 14.' but
    was not produced by this instrument proves nothing — the gate refuses
    it as blocking, never as a pass."""
    fixture = build_fixture(tmp_path)
    write(fixture / "80-validator" / "sensitivity.md",
          "# Validator sensitivity\n\nCaught 14 of 14. Not measured: 0.\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "provenance mismatch" in proc.stdout
    assert "carries no provenance header" in proc.stdout
    assert ("| `80-validator/sensitivity.md` | `p-sensitivity` | provenance "
            "mismatch | re-run sensitivity.py | fail |") in proc.stdout


def test_sensitivity_report_from_a_different_validator_is_blocking(tmp_path: Path) -> None:
    """Probe D, second half (C3): a provenance header whose sha256 does not
    match the validator that would exercise the report is blocking."""
    fixture = build_fixture(tmp_path)
    alien = "0" * 64
    write(fixture / "80-validator" / "sensitivity.md",
          "# Validator sensitivity\n\n" + valid_sensitivity_header(fixture, sha=alien) +
          "\n\n" + CAUGHT_ALL + "\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "produced by a different validator (sha256 mismatch)" in proc.stdout


def test_sensitivity_report_of_a_different_perturbation_set_is_blocking(tmp_path: Path) -> None:
    """C3: the header may carry the right sha and still name another
    perturbation set (or a count that does not match the Caught line) —
    both divergences are blocking."""
    fixture = build_fixture(tmp_path)
    ids = [pert.name for pert in sensitivity.PERTURBATIONS]
    swapped = ids[:-1] + ["alien perturbation"]
    write(fixture / "80-validator" / "sensitivity.md",
          "# Validator sensitivity\n\n" + valid_sensitivity_header(fixture, ids=swapped) +
          "\n\n" + CAUGHT_ALL + "\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "names a different perturbation set" in proc.stdout
    short = N_PERTURBATIONS - 1
    short_count = valid_sensitivity_header(fixture, count=short)  # full ids, wrong count
    write(fixture / "80-validator" / "sensitivity.md",
          "# Validator sensitivity\n\n" + short_count +
          "\n\n" + CAUGHT_ALL + "\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert (f"the report names {short} perturbations, the instrument runs "
            f"{N_PERTURBATIONS}") in proc.stdout


def test_sensitivity_default_write_path_is_folder_relative(fixture: Path, tmp_path: Path,
                                                            monkeypatch) -> None:
    """Regression (v0.2.3 rework): with no --output, the report lands at the
    folder-relative corpus default (<folder>/80-validator/sensitivity.md),
    not next to the caller's working directory — the default used to be
    CWD-relative, so a run from anywhere but the folder wrote the report
    elsewhere (or nowhere). The perturbation set is emptied so the run is
    one baseline validator call, and main() is driven in process."""
    monkeypatch.setattr(sensitivity, "PERTURBATIONS", [])
    (fixture / "80-validator").mkdir(parents=True, exist_ok=True)
    code = sensitivity.main(["--folder", str(fixture),
                             "--work", str(tmp_path / "work")])
    report = fixture / "80-validator" / "sensitivity.md"
    assert code == sensitivity.EXIT_OK
    assert "Caught 0 of 0." in report.read_text(encoding="utf-8")
    # The unit contract behind the default: None -> the folder's corpus
    # default; an explicit path passes through unchanged.
    assert sensitivity.resolve_output(None, fixture) == report
    assert sensitivity.resolve_output(Path("elsewhere.md"), fixture) == Path("elsewhere.md")


# ------------------------------------------- panel v0.2.3 fixes (C1, C2, C4a, C5)

def test_missing_declared_document_is_blocking(tmp_path: Path) -> None:
    """Probe A of the panel (C2): an artifact declared in the table whose
    file does not exist used to be skipped in silence — a green report with
    a missing document. Now it is a blocking note naming the path, and the
    report keeps the row."""
    fixture = build_fixture(tmp_path)
    (fixture / "10-doc1.md").unlink()
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "declared artifact missing: 10-doc1.md" in proc.stdout
    assert ("| `10-doc1.md` | `p-declared` | missing | exists | fail |") in proc.stdout


def test_proposed_artifact_missing_is_pending_not_blocking(tmp_path: Path) -> None:
    """C2: a declared-but-proposed artifact that does not exist yet is a
    pending with its reason — never silent, never blocking (the JSON cell
    format is the one that carries 'proposed')."""
    proc = subprocess.run(
        [sys.executable, str(SCAFFOLD), "--target", "proposed-test",
         "--roles", "writer", "--out", str(tmp_path / "cell")],
        capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    cell = tmp_path / "cell"
    cell_validator = cell / "08-validator" / "validator.py"
    if not cell_validator.exists():
        pytest.skip("scaffold shipped without the validator copy (skill copied alone)")
    records = json.loads((cell / "03-artifacts.json").read_text(encoding="utf-8"))
    records[0]["proposed"] = True
    (cell / "03-artifacts.json").write_text(json.dumps(records), encoding="utf-8")
    run = subprocess.run(
        [sys.executable, str(cell_validator), "--folder", str(cell),
         "--layout", str(cell / "layout.json")],
        capture_output=True, text=True, check=False)
    assert "# Validator report" in run.stdout
    assert ("| `<relative path>` | `p-declared` | proposed, not yet produced | "
            "exists | pending |") in run.stdout
    assert "declared artifact missing: <relative path>" not in run.stdout


def test_freeze_rubric_refuses_an_existing_pin(tmp_path: Path) -> None:
    """Probe B of the panel (C1): freezing over an existing pin used to
    re-pin the rubric silently, making every verdict incomparable. Now the
    freeze refuses (exit 2) and names --re-freeze-rubric; the deliberate
    replacement is explicit and works."""
    fixture = build_fixture(tmp_path)
    frozen = tmp_path / "frozen.sha256"
    first = subprocess.run(
        [sys.executable, str(VALIDATOR), "--folder", str(fixture),
         "--freeze-rubric", str(frozen)],
        capture_output=True, text=True, check=False)
    assert first.returncode == 0, first.stdout + first.stderr
    recorded = frozen.read_text(encoding="utf-8").strip()
    again = subprocess.run(
        [sys.executable, str(VALIDATOR), "--folder", str(fixture),
         "--freeze-rubric", str(frozen)],
        capture_output=True, text=True, check=False)
    assert again.returncode == 2
    assert f"the rubric is already frozen at {frozen}" in again.stderr
    assert "--re-freeze-rubric" in again.stderr
    assert "(and record why in the CHANGELOG)" in again.stderr
    deliberate = subprocess.run(
        [sys.executable, str(VALIDATOR), "--folder", str(fixture),
         "--re-freeze-rubric", str(frozen)],
        capture_output=True, text=True, check=False)
    assert deliberate.returncode == 0, deliberate.stdout + deliberate.stderr
    assert frozen.read_text(encoding="utf-8").strip() == recorded


def test_registry_anonymity_catches_an_absolute_locator(tmp_path: Path) -> None:
    """C5 of the panel: the instance registry carries paths (the locator),
    so p-anonymity measures it — an absolute locator is a note, a relative
    one (the documented convention) passes."""
    fixture = build_fixture(tmp_path)
    gates = GATES.replace(
        "| `p-prior-pin` | `registry` |",
        "| `p-anonymity` | `registry` | absolute paths and dates in the registry | 0 | "
        "[method] the locator is a path an adopter re-walks, never a machine-local one |\n"
        "| `p-prior-pin` | `registry` |")
    write_gates(fixture, gates)
    registry_dir = tmp_path / "instances"
    absolute = {"instances": [{"id": "000-fixture", "status": "executed",
                               "document": "prior-method.md", "sha256": PRIOR_SHA,
                               "locator": "/srv/cells/somewhere"}]}
    write(registry_dir / "registry.json", json.dumps(absolute))
    proc = run_validator(fixture, "--registry", str(registry_dir / "registry.json"))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "| `../instances/registry.json` | `p-anonymity` | 1 | 0 | fail |" in proc.stdout
    relative = {"instances": [{"id": "000-fixture", "status": "executed",
                               "document": "prior-method.md", "sha256": PRIOR_SHA,
                               "number_format": "point-decimal",
                               "locator": "instances/000-fixture"}]}
    write(registry_dir / "registry.json", json.dumps(relative))
    proc = run_validator(fixture, "--registry", str(registry_dir / "registry.json"))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert ("| `../instances/registry.json` | `p-anonymity` | 0 paths and dates; "
            "identifiers not measured (no list) | 0 | pending |") in proc.stdout


# ------------------------------------------ panel v0.2.3 + review v0.3.0 (v0.3.1)

def test_freeze_and_re_freeze_together_are_rejected(tmp_path: Path) -> None:
    """S3 of the review: --freeze-rubric and --re-freeze-rubric used together
    used to ignore the second flag in silence; they are mutually exclusive
    and the run says so."""
    fixture = build_fixture(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--folder", str(fixture),
         "--freeze-rubric", str(tmp_path / "a.sha256"),
         "--re-freeze-rubric", str(tmp_path / "b.sha256")],
        capture_output=True, text=True, check=False)
    assert proc.returncode == 2
    assert "mutually exclusive" in proc.stderr
    assert not (tmp_path / "a.sha256").exists()
    assert not (tmp_path / "b.sha256").exists()


def test_artifact_declared_without_paths_is_a_visible_pending(tmp_path: Path) -> None:
    """S3 of the review: an artifact declared with no paths at all (a JSON
    record with paths: [], or a table row with no backticked file) used to
    be skipped in silence by p-declared; it is now a pending row that says
    so — never a silent skip."""
    fixture = build_fixture(tmp_path)
    write(fixture / "02-artifacts.md", ARTIFACTS.replace(
        "| `contracts` |",
        "| `ghost` | — | writer | `canon` | free text | — |\n| `contracts` |"))
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert ("| `ghost` | `p-declared` | declared without paths; no files to "
            "measure | at least one path | pending |") in proc.stdout


def test_without_notes_the_p_notes_row_is_pending(fixture: Path) -> None:
    """I4 of the panel: without --notes the ledger gate stays visible as a
    pending row with its reason, never a row that quietly disappears."""
    proc = run_validator(fixture)  # no --notes
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert ("| `open-notes` | `p-notes` | not measured (notes not supplied; "
            "the note ledger was not measured) | 0 invalid | pending |") in proc.stdout


def test_markdown_canon_of_a_different_schema_version_is_refused(tmp_path: Path) -> None:
    """I5 of the panel: the corpus canon declares its schema version in the
    'Canon schema' row; a different version (or no row) is refused, not
    misread."""
    fixture = build_fixture(tmp_path)
    write(fixture / "01-canon.md",
          CANON.replace("| Canon schema | verifier | v1 | ready |",
                        "| Canon schema | verifier | v2 | ready |"))
    proc = run_validator(fixture)
    assert proc.returncode == 2
    assert "this validator reads canon schema version 'v1'" in proc.stderr
    assert "declares 'v2'" in proc.stderr
    write(fixture / "01-canon.md",
          CANON.replace("| Canon schema | verifier | v1 | ready |\n", ""))
    proc = run_validator(fixture)
    assert proc.returncode == 2
    assert "does not declare the canon schema version" in proc.stderr


def test_json_canon_of_a_different_schema_version_is_refused(tmp_path: Path) -> None:
    """I5 of the panel, JSON side: the canon carries the schema version the
    validator consumes; a different value (or none) is refused."""
    folder = tmp_path / "cell"
    canon_json = {key: [] for key in validator.JSON_CANON_KEYS}
    canon_json["method components"] = ["artifact graph", "gate", "note"]
    write(folder / "02-canon.json", json.dumps(canon_json))  # no "version"
    write(folder / "03-artifacts.json", "[]")  # empty list: the artifacts
    # never load (the canon version refusal fires first)
    layout = folder / "layout.json"
    layout.write_text(json.dumps(
        {"version": 1, "artifacts": {"canon": "02-canon.json",
                                     "artifacts": "03-artifacts.json"},
         "gates": {gate: "builtin-json-canon" for gate in validator.BUILTIN_GATES}}),
        encoding="utf-8")
    proc = run_validator(folder, "--layout", str(layout))
    assert proc.returncode == 2
    assert "does not declare the canon schema version" in proc.stderr
    canon_json["version"] = "v9"
    write(folder / "02-canon.json", json.dumps(canon_json))
    proc = run_validator(folder, "--layout", str(layout))
    assert proc.returncode == 2
    assert "declares 'v9'" in proc.stderr


# ------------------------------------------ panel v0.2.3, epistemic round (v0.4.0)

GATE_ROWS_EXTRA = {
    "p-size": "| `p-size` | `doc1` | words | within the range | "
              "[method] the size range is declared before the writing starts |\n",
    "p-sections": "| `p-sections` | `doc1` | mandatory sections present | 1 of 1 | "
                  "[method] each mandatory section is a step of the recipe |\n",
    "p-efficacy-mark": "| `p-efficacy-mark` | `doc1` | unlabeled claims of efficacy | 0 | "
                       "[method] a claim about the method carries its evidence label |\n",
}
EFFICACY_TRIGGERS = "\n### Efficacy triggers\n\n| Trigger phrase |\n| --- |\n| `pays off` |\n"
# An experiments record with one executed and one designed experiment, each
# declaring its status the way the corpus record does (a field-table row).
EXPERIMENTS_RECORD = ("# Experiments\n\n## E1 — the first one\n\n| Field | Value |\n| --- | --- |\n"
                      "| Status | `executed` |\n\n### Question\n\nDoes it?\n\n"
                      "## E2 — the second one\n\n| Field | Value |\n| --- | --- |\n"
                      "| Status | `designed` |\n")


def fixture_with_gates(tmp_path: Path, gates: list[str], doc1: str = DOC1) -> Path:
    """The fixture with extra gate rows on doc1 (and the efficacy triggers
    in its canon, which the extra gate p-efficacy-mark reads)."""
    fixture = build_fixture(tmp_path, doc1=doc1)
    rows = "".join(GATE_ROWS_EXTRA[gate] for gate in gates)
    write_gates(fixture, GATES.replace("\n### Size ranges", rows + "\n### Size ranges"))
    write(fixture / "01-canon.md", CANON + EFFICACY_TRIGGERS)
    return fixture


def run_sensitivity(fixture: Path, tmp_path: Path, monkeypatch, perts: list,
                    *extra: str) -> tuple[int, str]:
    """Drive sensitivity.main in process with a fixture-specific set."""
    monkeypatch.setattr(sensitivity, "PERTURBATIONS", tuple(perts))
    output = tmp_path / "sensitivity-out.md"
    code = sensitivity.main(["--folder", str(fixture), "--work", str(tmp_path / "work"),
                             "--output", str(output), *extra])
    return code, output.read_text(encoding="utf-8") if output.exists() else ""


def row_result(report: str, name: str) -> str:
    for line in report.splitlines():
        if line.startswith(f"| {name} |"):
            return line.rstrip(" |").rsplit("| ", 1)[1]
    raise AssertionError(f"no row '{name}' in the sensitivity report:\n{report}")


def test_sensitivity_catches_a_canon_link_that_does_not_resolve(tmp_path: Path, monkeypatch) -> None:
    """I1 of the panel: p-canon-link had no perturbation; the target now
    has to resolve, so a link that names the canon from the wrong folder is
    a known defect the gate must reject."""
    fixture = build_fixture(tmp_path)
    pert = sensitivity.Perturbation("canon link broken", "10-doc1.md", "[canon](01-canon.md)",
                                    "[canon](../01-canon.md)", "p-canon-link")
    code, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert])
    assert code == sensitivity.EXIT_OK, report
    assert row_result(report, "canon link broken") == "caught"


def test_sensitivity_catches_a_document_out_of_its_size_range(tmp_path: Path, monkeypatch) -> None:
    """I1: the p-size perturbation appends more words than any maximum."""
    fixture = fixture_with_gates(tmp_path, ["p-size"])
    pert = sensitivity.Perturbation("too long", "10-doc1.md", "# Document one",
                                    "# Document one\n\n" + sensitivity.SIZE_PADDING, "p-size")
    code, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert])
    assert code == sensitivity.EXIT_OK, report
    assert row_result(report, "too long") == "caught"


def test_sensitivity_catches_a_removed_mandatory_section(tmp_path: Path, monkeypatch) -> None:
    """I1: a mandatory section heading renamed away fails p-sections."""
    fixture = fixture_with_gates(tmp_path, ["p-sections"], doc1=DOC1 + "\n## Brief\n\nThe brief.\n")
    pert = sensitivity.Perturbation("section gone", "10-doc1.md", "## Brief", "## Summary",
                                    "p-sections")
    code, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert])
    assert code == sensitivity.EXIT_OK, report
    assert row_result(report, "section gone") == "caught"


def test_sensitivity_alters_the_pin_in_a_copy_of_the_registry(tmp_path: Path, monkeypatch) -> None:
    """I1: the registry lives outside the copied folder; the sensitivity
    copies it next to the copy and passes --registry, so the pin can be
    perturbed without touching the real registry. Without --case the row
    is not measured, never caught."""
    fixture = build_fixture(tmp_path)
    registry = tmp_path / "instances" / "registry.json"
    before = registry.read_bytes()
    pert = sensitivity.Perturbation("pin altered", "../instances/registry.json",
                                    f'"sha256": "{PRIOR_SHA}"', '"sha256": "' + "0" * 64 + '"',
                                    "p-prior-pin", needs_case=True)
    code, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert],
                                   "--case", str(tmp_path / "prior-method.md"))
    assert code == sensitivity.EXIT_OK, report
    assert row_result(report, "pin altered") == "caught"
    assert registry.read_bytes() == before
    _, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert])
    assert row_result(report, "pin altered") == "not measured"


def test_sensitivity_without_rubric_hash_does_not_measure_the_frozen_rubric(
        tmp_path: Path, monkeypatch) -> None:
    """I1: --rubric-hash is forwarded to the validator; without it the
    p-frozen-rubric row is 'not measured', never 'caught'."""
    fixture = build_fixture(tmp_path)
    pin = fixture / "rubric.sha256"
    pin.write_text(validator.rubric_hash(GATES) + "\n", encoding="utf-8")
    pert = sensitivity.Perturbation("rubric edited", "04-gates-and-rubric.md",
                                    "Fixture rubric, never changed.", "Fixture rubric, changed.",
                                    "p-frozen-rubric", needs_rubric_hash=True)
    _, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert])
    assert row_result(report, "rubric edited") == "not measured"
    assert "Caught 0 of 0." in report and "Not measured: 1." in report
    code, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert], "--rubric-hash", str(pin))
    assert code == sensitivity.EXIT_OK, report
    assert row_result(report, "rubric edited") == "caught"


def test_sensitivity_forwards_the_notes_and_catches_an_invalid_severity(
        tmp_path: Path, monkeypatch) -> None:
    """I1: --notes is forwarded (mapped into the copy, where the perturbed
    ledger lives); without it the p-notes row is not measured."""
    fixture = build_fixture(tmp_path)
    pert = sensitivity.Perturbation("bad severity", "90-notes/notes.json", '"severity": "low"',
                                    '"severity": "trivial"', "p-notes", needs_notes=True)
    code, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert],
                                   "--notes", str(fixture / "90-notes" / "notes.json"))
    assert code == sensitivity.EXIT_OK, report
    assert row_result(report, "bad severity") == "caught"
    _, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert])
    assert row_result(report, "bad severity") == "not measured"


def test_sensitivity_catches_a_deleted_declared_document(tmp_path: Path, monkeypatch) -> None:
    """I1: a deletion perturbation removes a declared file from the copy;
    p-declared has to fail on it."""
    fixture = build_fixture(tmp_path)
    pert = sensitivity.Perturbation("doc deleted", "10-doc1.md", "", "", "p-declared", delete=True)
    code, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert])
    assert code == sensitivity.EXIT_OK, report
    assert row_result(report, "doc deleted") == "caught"
    assert (fixture / "10-doc1.md").exists()


def test_every_gate_the_validator_implements_has_a_perturbation() -> None:
    """I1 and I18: one perturbation per gate the validator implements; the
    only exception is p-sensitivity, the gate on the report the perturbations
    produce (exercised by the provenance tests above). A gate retired
    without its perturbation, or the reverse, fails here."""
    implemented = set(validator.BUILTIN_GATES) | set(validator.GLOBAL_GATES)
    perturbed = {pert.gate for pert in sensitivity.PERTURBATIONS}
    assert implemented - perturbed == {"p-sensitivity"}
    assert perturbed <= implemented
    names = [pert.name for pert in sensitivity.PERTURBATIONS]
    assert len(names) == len(set(names))


def build_json_cell(tmp_path: Path, card_link: str) -> Path:
    """A JSON cell whose writer card (in 04-roles/) is under p-canon-link."""
    folder = tmp_path / "cell"
    canon_json = {key: [] for key in validator.JSON_CANON_KEYS}
    canon_json["version"] = "v1"
    write(folder / "02-canon.json", json.dumps(canon_json))
    gates = ("# Gates\n\n| Gate | Artifact | Magnitude | Limit | Justification |\n"
             "| --- | --- | --- | --- | --- |\n| `p-canon-link` | `card` | resolved links | 1 | "
             "[method] a link that leads nowhere links nothing |\n\n### Size ranges\n\n"
             "| Document | Minimum | Maximum |\n| --- | --- | --- |\n")
    write(folder / "03-artifacts.json", json.dumps(mirror_json_gates([
        {"name": "graph", "paths": ["03-artifacts.json"], "owner": "writer", "depends_on": []},
        {"name": "card", "paths": ["04-roles/writer.md"], "owner": "writer", "depends_on": []}],
        gates)))
    write(folder / "06-gates.md", gates)
    write(folder / "04-roles" / "writer.md", f"# Role card: writer\n\nCanon: [02-canon.json]({card_link})\n")
    write(folder / "layout.json", json.dumps(
        {"version": 1, "artifacts": {"canon": "02-canon.json", "artifacts": "03-artifacts.json",
                                     "gates-and-rubric": "06-gates.md", "roles-dir": "04-roles"},
         "gates": {gate: "builtin-json-canon" for gate in validator.BUILTIN_GATES}}))
    return folder


def test_canon_link_that_does_not_resolve_fails_p_canon_link(tmp_path: Path) -> None:
    """Regression (risk left open by the v0.3.1 review): the scaffold's card
    linked `02-canon.json` from inside `04-roles/`; the gate counted the link
    by name and passed it. The target now has to resolve to the canon."""
    cell = build_json_cell(tmp_path / "broken", "02-canon.json")
    proc = run_validator(cell, "--layout", str(cell / "layout.json"))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "link to the canon does not resolve: `02-canon.json`" in proc.stdout
    assert ("| `04-roles/writer.md` | `p-canon-link` | 0 resolved, 1 unresolved | "
            "≥ 1 resolved, 0 unresolved | fail |") in proc.stdout
    cell = build_json_cell(tmp_path / "fixed", "../02-canon.json")
    proc = run_validator(cell, "--layout", str(cell / "layout.json"))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `04-roles/writer.md` | `p-canon-link` | 1 resolved, 0 unresolved |" in proc.stdout


def test_claim_of_efficacy_needs_an_evidence_label(tmp_path: Path) -> None:
    """I10 of the panel: the method's doctrine of evidence applies to the
    claims about the method; a trigger in a code span is not a claim."""
    claim = DOC1 + "\nThe method pays off when errors are costly.\n"
    fixture = fixture_with_gates(tmp_path / "a", ["p-efficacy-mark"], doc1=claim)
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "claim of efficacy ('pays off') without one of the labels" in proc.stdout
    labeled = claim.replace("costly.", "costly [hypothesis].")
    fixture = fixture_with_gates(tmp_path / "b", ["p-efficacy-mark"], doc1=labeled)
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    quoted = DOC1 + "\nThe trigger `pays off` is defined in the canon.\n"
    fixture = fixture_with_gates(tmp_path / "c", ["p-efficacy-mark"], doc1=quoted)
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr


def test_experiment_label_has_to_be_registered(tmp_path: Path) -> None:
    """I10: an [experiment:<id>] label cites an experiment of the record the
    layout key artifacts.experiments names (60-experiments.md); since v0.4.1
    the experiment has to be executed (see the designed case below)."""
    claim = DOC1 + "\nThe review pays off here [experiment:E9].\n"
    fixture = fixture_with_gates(tmp_path, ["p-efficacy-mark"], doc1=claim)
    write(fixture / "60-experiments.md", EXPERIMENTS_RECORD)
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "[experiment:E9] is not registered in 60-experiments.md" in proc.stdout
    write(fixture / "10-doc1.md", claim.replace("E9", "E1"))
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr


def test_layout_with_an_unknown_key_is_a_tool_failure(fixture: Path) -> None:
    """I12 of the panel: a misspelled layout key used to be ignored, leaving
    the default in force in silence; it is now exit 2 naming the key and
    the keys this validator reads."""
    layout = fixture / "layout.json"
    layout.write_text(json.dumps({"version": 1, "artifacts": {"sensitivty": "x.md"}}),
                      encoding="utf-8")
    proc = run_validator(fixture, "--layout", str(layout))
    assert proc.returncode == 2
    assert "unknown 'artifacts' key(s) 'sensitivty'" in proc.stderr
    assert "sensitivity" in proc.stderr.split("known 'artifacts' keys are", 1)[1]
    layout.write_text(json.dumps({"version": 1, "registy": "x.json"}), encoding="utf-8")
    proc = run_validator(fixture, "--layout", str(layout))
    assert proc.returncode == 2
    assert "unknown top-level key(s) 'registy'" in proc.stderr


OTHER_DOC = "# Other method document\n\n## 3 Runs\n\nThe other prior gave 77 runs.\n"
OTHER_SHA = hashlib.sha256(OTHER_DOC.encode("utf-8")).hexdigest()
TWO_PRIORS = {"instances": [
    dict(REGISTRY["instances"][0]),
    {"id": "001-other", "status": "executed", "document": "other-method.md",
     "sha256": OTHER_SHA, "locator": OWNER_HELD, "number_format": "point-decimal"}]}
DOC_TWO_PRIORS = DOC1 + "\nThe other prior gave 77 runs [prior:001-other].\n"


def build_two_prior_fixture(tmp_path: Path, doc1: str = DOC_TWO_PRIORS) -> Path:
    fixture = build_fixture(tmp_path, doc1=doc1)
    write(tmp_path / "instances" / "registry.json", json.dumps(TWO_PRIORS))
    write(tmp_path / "other-method.md", OTHER_DOC)
    # One "Recorded facts" table for both priors: each row belongs to the
    # prior its mark names (the 49 row of 001-other never applies to 000).
    write(fixture / "01-canon.md", CANON + "\n## Recorded facts\n\n"
          "| Number | In what context | Where in the prior's method document |\n"
          "| --- | --- | --- |\n"
          "| 49 | items `[prior:000-fixture]` | section 1 |\n"
          "| 77 | runs `[prior:000-fixture]` | section 1 |\n"
          "| 77 | runs `[prior:001-other]` | section 3 |\n"
          "| 49 | items `[prior:001-other]` | section 9 |\n")
    return fixture


def test_each_prior_label_is_checked_in_its_own_document(tmp_path: Path) -> None:
    """I14 of the panel: --case is repeatable; each document is identified
    by its sha256 in the registry and a [prior:<id>] unit is checked in the
    document of <id>, with the recorded-fact rows of <id> only."""
    fixture = build_two_prior_fixture(tmp_path)
    cases = ("--case", str(tmp_path / "prior-method.md"), "--case", str(tmp_path / "other-method.md"))
    proc = run_validator(fixture, *cases)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `../instances/registry.json` | `p-prior-pin` | 2 executed priors pinned | equal | pass |" \
        in proc.stdout
    write(fixture / "10-doc1.md", DOC_TWO_PRIORS.replace("gave 49 items", "gave 77 items"))
    proc = run_validator(fixture, *cases)
    assert proc.returncode == 1
    assert "prior '000-fixture': '77' is not in section(s) 1 of the prior method document" \
        in proc.stdout


def test_a_unit_citing_two_priors_is_checked_in_each_document(tmp_path: Path) -> None:
    """I5 of the v0.4.0 review: a unit that cites two priors was passed when
    one present document verified it, so a prior without its document was
    silently checked in the other one. Each id is checked in its own
    document; an id with no document is pending by name."""
    both = DOC1 + "\nBoth gave 49 items [prior:000-fixture] [prior:001-other].\n"
    fixture = build_two_prior_fixture(tmp_path, doc1=both)
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"))
    assert ("numbers of 001-other not measured (no --case document identified as that prior) "
            "| 0 | pending |") in proc.stdout
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"),
                         "--case", str(tmp_path / "other-method.md"))
    assert proc.returncode == 1
    assert "prior '001-other': '49' cites section '9' of the prior method document" in proc.stdout


def test_a_cited_prior_without_its_document_is_pending_by_name(tmp_path: Path) -> None:
    """I14: with one of two cited priors passed, the units of the other are
    pending by name (never checked against the wrong document), and its pin
    is blocking."""
    fixture = build_two_prior_fixture(tmp_path)
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"))
    assert proc.returncode == 1
    assert ("numbers of 001-other not measured (no --case document identified as that prior) "
            "| 0 | pending |") in proc.stdout
    assert ("cited prior '001-other': no document passed as --case matches the sha256 pinned "
            "for it (its method document was not passed)") in proc.stdout


def test_a_case_document_that_pins_no_instance_is_a_blocking_note(tmp_path: Path) -> None:
    """I14: a document passed as --case that is the pin of no executed
    instance is a finding on the registry (exit 1), not a tool failure."""
    fixture = build_fixture(tmp_path)
    write(tmp_path / "stray.md", "# A stray document\n")
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"),
                         "--case", str(tmp_path / "stray.md"))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "document passed as --case matches no executed instance" in proc.stdout


def test_undecodable_document_is_a_tool_failure(fixture: Path) -> None:
    """I15 of the panel: invalid UTF-8 is exit 2 naming the file and the
    byte, never a finding (and never a traceback)."""
    (fixture / "10-doc1.md").write_bytes(b"# Document one\n\n\xff broken\n")
    proc = run_validator(fixture)
    assert proc.returncode == 2
    assert "could not decode 10-doc1.md as UTF-8 at byte 16" in proc.stderr


@pytest.mark.parametrize(("document_token", "case_token", "verified"), [
    ("1.2", "1.200", False),   # 1.2 is never the comma-decimal one thousand two hundred
    ("1,200", "1.200", True),  # the same thousand, in each one's format
    ("0.546", "0,546", True),  # the same decimal, in each one's format
    ("1.10", "1.10", True),    # no comma-decimal number: a section number, literal
    ("1.200", "1.2", False),   # I6 of the review: the value 1.2 never meets the literal '1.2'
])
def test_numbers_are_read_in_the_declared_format(tmp_path: Path, document_token: str,
                                                 case_token: str, verified: bool) -> None:
    """I16 of the panel: the registry declares the prior's number format and
    a token has one reading in it; the two-way reading let '1.2' pass
    against a pt-BR '1.200' (one thousand two hundred). Values and literals
    live apart (I6 of the v0.4.0 review)."""
    prior = f"# Prior method document\n\n## 1 Items\n\nThe tool gave {case_token} items.\n"
    fixture = build_fixture(tmp_path, doc1=DOC1.replace("gave 49 items", f"gave {document_token} items"))
    write(fixture / "01-canon.md", CANON + CANON_FACTS.replace("| 49 |", f"| {document_token} |"))
    write(tmp_path / "prior-method.md", prior)
    entry = dict(REGISTRY["instances"][0], number_format="comma-decimal",
                 sha256=hashlib.sha256(prior.encode("utf-8")).hexdigest())
    write(tmp_path / "instances" / "registry.json", json.dumps({"instances": [entry]}))
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"))
    assert (proc.returncode == EXIT_PENDING) is verified, proc.stdout + proc.stderr
    assert ("1 numbers and 0 section references checked, 0 unverified"
            in proc.stdout) is verified


def test_executed_prior_without_a_number_format_violates_the_contract(tmp_path: Path) -> None:
    """I16: an executed entry without number_format is a p-contract-shape
    violation, never a silent default; a designed one may keep it null."""
    fixture = build_fixture(tmp_path)
    entry = {key: value for key, value in REGISTRY["instances"][0].items() if key != "number_format"}
    designed = {"id": "001-designed", "status": "designed", "document": None, "sha256": None,
                "number_format": None}
    write(tmp_path / "instances" / "registry.json", json.dumps({"instances": [entry, designed]}))
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "executed instance '000-fixture' declares no number_format" in proc.stdout
    assert "'001-designed' declares no number_format" not in proc.stdout


# ------------------------------------------------- rework of the v0.4.0 review

def test_efficacy_gate_without_triggers_is_pending_not_a_pass(tmp_path: Path) -> None:
    """S3 of the review: with an empty trigger list nothing was measured;
    a 'pass 0' would read like evidence."""
    fixture = fixture_with_gates(tmp_path, ["p-efficacy-mark"])
    write(fixture / "01-canon.md", CANON)
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert ("| `10-doc1.md` | `p-efficacy-mark` | not measured (the canon lists no "
            "efficacy triggers) | 0 | pending |") in proc.stdout


def test_cell_layout_without_a_new_gate_names_it(fixture: Path) -> None:
    """S6 of the review: a cell layout from before v0.4.0 maps every gate but
    p-efficacy-mark to the JSON parser; the exit 2 names the gate it lacks."""
    layout = fixture / "layout.json"
    gates = {gate: "builtin-json-canon" for gate in validator.BUILTIN_GATES if gate != "p-efficacy-mark"}
    layout.write_text(json.dumps({"version": 1, "gates": gates}), encoding="utf-8")
    proc = run_validator(fixture, "--layout", str(layout))
    assert proc.returncode == 2
    assert "names more than one parser" in proc.stderr
    assert "left on the default parser: p-efficacy-mark" in proc.stderr


# ------------------------------------------------ second rework of the v0.4.0 review

def build_json_prior_cell(tmp_path: Path, facts: object, doc1: str = DOC1) -> Path:
    """A JSON cell (the scaffold's format) whose document cites a prior number."""
    folder = tmp_path / "cell"
    canon_json = {key: [] for key in validator.JSON_CANON_KEYS}
    canon_json.update({"version": "v1", "method components": ["artifact graph", "gate", "note"],
                       "prior-statement triggers": ["reference case"], "recorded facts": facts})
    write(folder / "02-canon.json", json.dumps(canon_json))
    gates = GATES.replace("`02-artifacts.md`", "`03-artifacts.json`")
    write(folder / "03-artifacts.json", json.dumps(mirror_json_gates([
        {"name": "graph", "paths": ["03-artifacts.json"], "owner": "writer", "depends_on": []},
        {"name": "doc1", "paths": ["10-doc1.md"], "owner": "writer", "depends_on": ["graph"]},
        {"name": "registry", "paths": ["../instances/registry.json"], "owner": "verifier",
         "depends_on": [], "schema": "05-contracts/registry.schema.json"}], gates)))
    write(folder / "06-gates.md", gates)
    write(folder / "04-roles" / "writer.md", CARD)
    write(folder / "10-doc1.md", doc1.replace("(01-canon.md)", "(02-canon.json)"))
    write(folder / "05-contracts" / "registry.schema.json", json.dumps(REGISTRY_SCHEMA))
    write(tmp_path / "instances" / "registry.json", json.dumps(REGISTRY))
    write(tmp_path / "prior-method.md", PRIOR_DOC)
    write(folder / "layout.json", json.dumps(
        {"version": 1, "artifacts": {"canon": "02-canon.json", "artifacts": "03-artifacts.json",
                                     "gates-and-rubric": "06-gates.md", "roles-dir": "04-roles"},
         "gates": {gate: "builtin-json-canon" for gate in validator.BUILTIN_GATES},
         "registry": "../instances/registry.json"}))
    return folder


def run_json_cell(cell: Path) -> subprocess.CompletedProcess[str]:
    return run_validator(cell, "--layout", str(cell / "layout.json"),
                         "--case", str(cell.parent / "prior-method.md"))


FACT_49 = {"number": "49", "context": "items the tool gave [prior:000-fixture]", "section": "1"}


def test_json_cell_records_the_prior_numbers_it_states(tmp_path: Path) -> None:
    """Rework 2 of the v0.4.0 review: a JSON canon had to keep 'recorded
    facts' empty, so once a prior number needed its row no cell could cite
    one. The cell now records its own rows; with the row the number is
    checked in its section, without it the gate fails."""
    cell = build_json_prior_cell(tmp_path / "with", [FACT_49])
    proc = run_json_cell(cell)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "1 numbers and 0 section references checked, 0 unverified" in proc.stdout
    cell = build_json_prior_cell(tmp_path / "without", [])
    proc = run_json_cell(cell)
    assert proc.returncode == 1
    assert "'49' has no row of that prior in the canon's 'Recorded facts'" in proc.stdout


@pytest.mark.parametrize("bad", [
    ["49 in section 1"],
    [{"number": "49", "context": "items [prior:000-fixture]"}],
    [{"number": "many", "context": "items [prior:000-fixture]", "section": "1"}],
    {"number": "49"},
])
def test_malformed_json_recorded_fact_is_a_tool_failure(tmp_path: Path, bad: object) -> None:
    """A malformed item is refused with the form that would be accepted."""
    cell = build_json_prior_cell(tmp_path, bad)
    proc = run_json_cell(cell)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "'recorded facts'" in proc.stderr and '"number": "18"' in proc.stderr


def test_instance_identifier_is_not_a_number_about_the_prior(fixture: Path) -> None:
    """Rework 2: a registered instance named in a [prior:...] unit is not a
    number that needs a recorded fact. Since v0.4.1 only the full id names
    it ('000-fixture'; a bare '000' is a number, see the next test). A
    number that merely looks like an id prefix but is not one still counts."""
    write(fixture / "10-doc1.md", DOC1.replace(
        "the tool gave 49 items.", "the tool gave 49 items, as instance 000-fixture reported."))
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "1 numbers and 0 section references checked, 0 unverified" in proc.stdout
    write(fixture / "10-doc1.md", DOC1.replace(
        "the tool gave 49 items.", "the tool gave 49 items, as run 007 reported."))
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert proc.returncode == 1
    assert "'007' has no row" in proc.stdout


# ------------------------------------------------- v0.4.1 (owner-delegated closures)

DESIGNED_003 = {"id": "003-designed", "status": "designed", "document": None, "sha256": None}


def write_registry(fixture: Path, *entries: dict) -> None:
    write(fixture.parent / "instances" / "registry.json", json.dumps({"instances": list(entries)}))


def test_a_bare_instance_prefix_is_a_number_about_the_prior(fixture: Path) -> None:
    """Residual risk of the v0.4.0 re-review: the bare numeric prefix of a
    registered id was excluded, so 'the prior has 003 phases' passed unread.
    Only the full id names an instance now; a bare '003' needs its row."""
    write_registry(fixture, REGISTRY["instances"][0], DESIGNED_003)
    case = ("--case", str(fixture.parent / "prior-method.md"))
    write(fixture / "10-doc1.md", DOC1.replace("the tool gave 49 items.",
                                               "the tool gave 49 items; the prior has 003 phases."))
    proc = run_validator(fixture, *case)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "'003' has no row of that prior" in proc.stdout
    write(fixture / "10-doc1.md", DOC1.replace("the tool gave 49 items.",
                                               "the tool gave 49 items, unlike instance 003-designed."))
    proc = run_validator(fixture, *case)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "1 numbers and 0 section references checked, 0 unverified" in proc.stdout


def test_executed_registry_entry_needs_every_field_of_its_status(fixture: Path) -> None:
    """C16 (v0.4.1): one registry, with the contract by status enforced by
    the validator under p-contract-shape. An executed entry without its
    locator, or with a locator that is not relative, is a finding."""
    entry = {key: value for key, value in REGISTRY["instances"][0].items() if key != "locator"}
    write_registry(fixture, entry)
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "executed instance '000-fixture' declares no locator" in proc.stdout
    write_registry(fixture, dict(entry, locator="~/cells/000"))
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "the locator of '000-fixture' is neither a relative path nor" in proc.stdout
    write_registry(fixture, dict(entry, locator="../cell-000"))
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr


def test_designed_registry_entry_carries_none_of_the_executed_fields(fixture: Path) -> None:
    """C16, the other direction: a designed entry keeps document, sha256,
    locator and number_format null or absent; one that carries a pin could
    pass for an executed prior."""
    write_registry(fixture, REGISTRY["instances"][0], DESIGNED_003)
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    write_registry(fixture, REGISTRY["instances"][0], dict(DESIGNED_003, sha256="b" * 64))
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "designed instance '003-designed' carries 'sha256'" in proc.stdout


def test_experiment_label_on_a_designed_experiment_is_a_finding(tmp_path: Path) -> None:
    """S4 of the v0.4.0 review: any heading word registered an id, and a
    designed experiment backed a claim like an executed one. Only a
    '## E<n> — ...' block that declares 'executed' backs a claim now."""
    claim = DOC1 + "\nThe review pays off here [experiment:E2].\n"
    fixture = fixture_with_gates(tmp_path, ["p-efficacy-mark"], doc1=claim)
    write(fixture / "60-experiments.md", EXPERIMENTS_RECORD)
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "[experiment:E2] cites a designed experiment as evidence" in proc.stdout
    write(fixture / "10-doc1.md", claim.replace("E2", "Question"))
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "[experiment:Question] is not registered in 60-experiments.md" in proc.stdout


CORPUS_CANON = Path(__file__).resolve().parents[1] / "01-canon.md"
NEW_EFFICACY_TRIGGERS = ("the method prevents", "the method finds", "the method catches",
                         "the gates caught", "the gate caught", "the validator found",
                         "the review found")


def test_corpus_canon_reads_the_new_efficacy_triggers() -> None:
    """S7 of the v0.4.0 review: claims such as 'the gates caught' or 'the
    review found' escaped the closed trigger list. The corpus canon lists
    them, and a unit using one without a label is a finding."""
    triggers = validator.load_canon(CORPUS_CANON).efficacy_triggers
    assert set(NEW_EFFICACY_TRIGGERS) <= set(triggers)
    assert validator.efficacy_mark_hits("In that round the gates caught the drift.\n", triggers)
    assert not validator.efficacy_mark_hits("In that round the gates caught the drift [lessons].\n",
                                            triggers)


def test_layout_accepts_the_gate_semantics_key(fixture: Path) -> None:
    """v0.4.1: the declared semantics of the gates moved to their own
    document; its layout key is known (I12), so a cell may name it."""
    assert validator.DEFAULT_LAYOUT["artifacts"]["gate-semantics"] == "06-gate-semantics.md"
    layout = fixture / "layout.json"
    layout.write_text(json.dumps({"version": 1, "artifacts": {"gate-semantics": "06-semantics.md"}}),
                      encoding="utf-8")
    proc = run_validator(fixture, "--layout", str(layout))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr


def test_sensitivity_perturbs_the_registry_contract_only_with_a_registry(
        tmp_path: Path, monkeypatch) -> None:
    """v0.4.1: the perturbation of the registry contract edits the copied
    registry; without a registry the row is not measured, never caught."""
    fixture = build_fixture(tmp_path)
    pert = sensitivity.Perturbation("locator dropped", "../instances/registry.json",
                                    f'"locator": "{OWNER_HELD}"', '"locator": null',
                                    "p-contract-shape", needs_registry=True)
    code, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert])
    assert code == sensitivity.EXIT_OK, report
    assert row_result(report, "locator dropped") == "caught"
    (tmp_path / "instances" / "registry.json").unlink()
    _, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert])
    assert row_result(report, "locator dropped") == "not measured"


# The self-test ran 106 checks before v0.4.1; the functions of v0.4.1 add 32
# and the bytecode check of v0.4.2 adds 2; the functions of v0.5.0 add 29.
# The counts are pinned, so a lost or a silently added check shows here.
SELF_TEST_BEFORE_V041 = 106
SELF_TEST_RULES_V04 = 32 + 2
SELF_TEST_RULES_V05 = 29


def test_self_test_covers_the_rules_of_v04() -> None:
    """v0.4.1: the self-test gained one short function per rule of v0.4.0
    and v0.4.1 (recorded facts, section references, full ids, number
    format, layout keys, registry status, experiment status); v0.5.0 one
    per false green of the panel that reviewed v0.4.2."""
    rules_v04 = validator.self_test_rules_v04(validator.SelfTest())
    assert rules_v04 == SELF_TEST_RULES_V04
    rules_v05 = validator.self_test_rules_v05(validator.SelfTest())
    assert rules_v05 == SELF_TEST_RULES_V05
    proc = subprocess.run([sys.executable, "-B", str(VALIDATOR), "--self-test"],
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    total = int(proc.stdout.split("all ", 1)[1].split()[0])
    assert total - rules_v04 - rules_v05 == SELF_TEST_BEFORE_V041


# ------------------------------------------------- v0.4.2 (what v0.4.1 left open)

def env_without_bytecode_switch() -> dict[str, str]:
    """The caller's environment without PYTHONDONTWRITEBYTECODE: the run
    has to keep caches out by itself."""
    return {key: value for key, value in os.environ.items() if key != "PYTHONDONTWRITEBYTECODE"}


def test_determinism_run_writes_no_bytecode_cache(tmp_path: Path) -> None:
    """v0.4.2: the validator imports the sensitivity script at run time and
    its determinism run starts child processes, which did not inherit -B;
    a run without the environment variable left __pycache__ next to the
    scripts. A copy of the two scripts, with a report whose provenance
    forces that import, now runs --determinism and leaves no cache."""
    tool = tmp_path / "tool"
    tool.mkdir()
    for name in ("validator.py", "sensitivity.py"):
        (tool / name).write_bytes(VALIDATOR.with_name(name).read_bytes())
    fixture = build_fixture(tmp_path / "cell")
    sha = hashlib.sha256((tool / "validator.py").read_bytes()).hexdigest()
    write(fixture / "alt-sensitivity.md", "# Validator sensitivity\n\n"
          + valid_sensitivity_header(fixture, sha=sha) + "\n\n" + CAUGHT_ALL + "\n")
    layout = tmp_path / "layout.json"
    layout.write_text(json.dumps({"version": 1, "artifacts": {"sensitivity": "alt-sensitivity.md"}}),
                      encoding="utf-8")
    proc = subprocess.run([sys.executable, str(tool / "validator.py"), "--folder", str(fixture),
                           "--layout", str(layout), "--determinism"],
                          capture_output=True, text=True, check=False, env=env_without_bytecode_switch())
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `m-determinism` | `80-validator/report.md` | sha256 equal in 2 runs | equal | pass |" \
        in proc.stdout
    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("__pycache__")) == []


def test_child_runs_of_the_sensitivity_carry_the_bytecode_flag(fixture: Path) -> None:
    """v0.4.2: each validator run the sensitivity starts gets -B itself."""
    command = sensitivity.validator_command(fixture, sensitivity.Inputs())
    assert command[:3] == [sys.executable, "-B", str(sensitivity.VALIDATOR)]


CORPUS_FOLDER = Path(__file__).resolve().parents[1]


def test_corpus_measures_the_round_record_and_the_principle_for_anonymity() -> None:
    """v0.4.2: p-anonymity did not cover the round record nor the principle,
    so the rule that no model identifier or machine path remains there was
    checked by a separate sweep; both are now assigned to the gate."""
    proc = subprocess.run([sys.executable, str(VALIDATOR), "--folder", str(CORPUS_FOLDER)],
                          capture_output=True, text=True, check=False)
    assert proc.returncode in (0, 1, EXIT_PENDING), proc.stderr
    for document in ("state/round-record.jsonl", "../01-principle.md"):
        assert f"| `{document}` | `p-anonymity` |" in proc.stdout, document


def test_absolute_path_in_a_round_record_line_fails_p_anonymity(tmp_path: Path) -> None:
    """v0.4.2: a machine-local path in an executor string of the round
    record is a note of p-anonymity, like a path in any measured document."""
    artifacts = ARTIFACTS + ("| `round-record` | `state/round-record.jsonl` | verifier | `doc1` "
                             "| free text | `p-anonymity` |\n")
    fixture = build_fixture(tmp_path, artifacts=artifacts)
    write_gates(fixture, GATES.replace(
        "| `p-prior-pin` | `registry` |",
        "| `p-anonymity` | `round-record` | absolute paths and dates | 0 | "
        "[method] a round line names executors by family, never by a local path |\n"
        "| `p-prior-pin` | `registry` |"))
    line = {"method_version": "0.4.2", "round": "v0.4.2", "summary": "fixture",
            "models": [{"role": "coder", "model": "family A, high effort"}]}
    write(fixture / "state" / "round-record.jsonl", json.dumps(line) + "\n")
    proc = run_validator(fixture)
    assert "| `state/round-record.jsonl` | `p-anonymity` |" in proc.stdout
    assert "| `state/round-record.jsonl` | `p-anonymity` | 1 |" not in proc.stdout
    line["models"][0]["model"] = "family A (see /etc/executors/a.txt)"
    write(fixture / "state" / "round-record.jsonl", json.dumps(line) + "\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "| `state/round-record.jsonl` | `p-anonymity` | 1 | 0 | fail |" in proc.stdout


# ------------------------------- v0.5.0 (the panel that reviewed v0.4.2)
# One regression test per probe of that panel (K1 to K13 and the truncated
# row), each failing on the validator of v0.4.2.

GATES_ROW_REFERENCES = ("| `p-references` | `gates` | undeclared artifacts and a gate map that "
                        "diverges from the artifact table | 0 | [method] the artifact table "
                        "assigns the gates and this table mirrors it |\n")
ARTIFACT_ROW_GATES = ("| `gates` | `04-gates-and-rubric.md` | writer | `canon` | gate table "
                      "| `p-references` |\n")


def fixture_with_gate_map_check(tmp_path: Path) -> Path:
    """The fixture whose gates file is itself under p-references."""
    fixture = build_fixture(tmp_path, artifacts=ARTIFACTS + ARTIFACT_ROW_GATES)
    write_gates(fixture, GATES.replace("\n### Size ranges", GATES_ROW_REFERENCES + "\n### Size ranges"))
    # The owners of the fixture's artifacts have to be roles for p-references.
    write(fixture / "03-roles" / "verifier.md", "# Role card: verifier\n")
    return fixture


def test_k1_a_gate_row_deleted_from_the_gate_table_is_a_finding(tmp_path: Path) -> None:
    """K1: with the gate table emptied the report stayed green, because
    the gate map came from that table alone. The artifact table is now the
    source; a gate it assigns without a row is a p-references finding, and
    the gate still runs on its documents."""
    fixture = fixture_with_gate_map_check(tmp_path)
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    gates = (fixture / "04-gates-and-rubric.md").read_text(encoding="utf-8")
    row = next(line for line in gates.splitlines() if line.startswith("| `p-prior-mark` |"))
    write(fixture / "04-gates-and-rubric.md", gates.replace(row + "\n", ""))
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "gate `p-prior-mark` declared for `doc1` has no row in the gates table" in proc.stdout
    assert "| `10-doc1.md` | `p-prior-mark` | 0 | 0 | pass |" in proc.stdout


def test_k1_a_report_made_against_another_gate_table_or_canon_is_blocking(tmp_path: Path) -> None:
    """K1: the provenance pinned only the validator's sha. It pins the gate
    section and the canon too; editing either after the report is blocking."""
    fixture = build_fixture(tmp_path)
    report = fixture / "80-validator" / "sensitivity.md"
    write(report, "# Validator sensitivity\n\n" + valid_sensitivity_header(fixture)
          + "\n\n" + CAUGHT_ALL + "\n")
    assert re.search(r"^\| `80-validator/sensitivity\.md` \| `p-sensitivity` \| \d+ of \d+ gates "
                     r"covered, 0 missed of \d+ \| [^|]+ \| pass \|$", run_validator(fixture).stdout, re.M)
    for name in ("04-gates-and-rubric.md", "01-canon.md"):
        original = (fixture / name).read_text(encoding="utf-8")
        write(fixture / name, original.replace("| target |", "| target  |")
              .replace("| `p-terms` | `doc1` |", "| `p-terms` | `doc1`  |"))
        proc = run_validator(fixture)
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert "changed since the sensitivity report was made" in proc.stdout, name
        write(fixture / name, original)


def test_k1_a_report_whose_table_does_not_add_up_is_blocking(tmp_path: Path) -> None:
    """Probe P5 of the panel: a header and a 'Caught' line, with no row,
    passed. The table has to have one row per perturbation, and as many
    caught rows as the line says."""
    fixture = build_fixture(tmp_path)
    report = fixture / "80-validator" / "sensitivity.md"
    header = "# Validator sensitivity\n\n" + valid_sensitivity_header(fixture) + "\n\n"
    write(report, header + f"Caught {N_PERTURBATIONS} of {N_PERTURBATIONS}.\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "in 0 rows" in proc.stdout
    write(report, header + CAUGHT_ALL.replace("| caught |", "| MISSED |", 1) + "\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "rows caught" in proc.stdout


def test_k2_a_prior_mark_inside_a_code_span_fails_p_prior_mark(fixture: Path) -> None:
    """K2: with the mark between backticks, p-prior checked none of the
    unit's numbers and p-prior-mark accepted the mark, so an invented
    number passed both. A mark in a code span is no mark now."""
    invented = DOC1.replace("[prior:000-fixture], the tool gave 49 items",
                            "`[prior:000-fixture]`, the tool gave 48 items")
    write(fixture / "10-doc1.md", invented)
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "(the mark is inside a code span, which is not a mark)" in proc.stdout
    assert "| `10-doc1.md` | `p-prior-mark` | 1 | 0 | fail |" in proc.stdout


SCAFFOLD_CARD_FIELDS = ["Decides", "Does not decide", "Inputs", "Outputs", "Exit gate",
                        "Notes it emits", "Code-conversion degree"]


def scaffold_cell(tmp_path: Path, roles: tuple[str, ...] = ("writer",)) -> Path:
    cell = tmp_path / "cell"
    proc = subprocess.run([sys.executable, "-B", str(SCAFFOLD), "--target", "probe",
                           "--roles", *roles, "--out", str(cell)],
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return cell


def fill_minimal_cell(cell: Path, card_text: str | None = None) -> None:
    """The scaffolded cell with the least an adopter fills: a brief, one
    card, the canon lists three gates read, the artifacts and their gates."""
    canon = json.loads((cell / "02-canon.json").read_text(encoding="utf-8"))
    canon.update({"terms to avoid": ["pipeline"], "role card fields": SCAFFOLD_CARD_FIELDS,
                  "origin labels": ["[method]", "[brief]", "[hypothesis]"]})
    write(cell / "02-canon.json", json.dumps(canon))
    write(cell / "00-brief.md", "# Brief: probe\n\nA short guide for new readers.\n\n"
          "## Non-negotiables\n\n- plain text only\n\n## Owner decisions\n\n- the title\n")
    if card_text is None:
        card_text = (cell / "04-roles" / "writer.md").read_text(encoding="utf-8").replace(
            "<fill in>", "the wording of the guide")
    write(cell / "04-roles" / "writer.md", card_text)
    records = [{"name": "brief", "owner": "writer", "paths": ["00-brief.md"], "depends_on": [],
                "gates": ["p-terms", "p-anonymity"]},
               {"name": "cards", "owner": "writer", "paths": ["04-roles/*.md"], "depends_on": [],
                "gates": ["p-card"]}]
    write(cell / "03-artifacts.json", json.dumps(records))
    rows = "".join(f"| `{g}` | `{a}` | {m} | 0 | [method] the cell measures this on its own "
                   "documents from the first run |\n"
                   for g, a, m in (("p-terms", "brief", "terms to avoid"),
                                   ("p-anonymity", "brief", "paths and dates"),
                                   ("p-card", "cards", "fields missing")))
    gates = (cell / "06-gates.md").read_text(encoding="utf-8")
    write(cell / "06-gates.md", gates.replace("| --- | --- | --- | --- | --- |\n",
                                              "| --- | --- | --- | --- | --- |\n" + rows, 1))


def run_cell(cell: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-B", str(cell / "08-validator" / "validator.py"),
                           "--folder", str(cell), "--layout", str(cell / "layout.json"), *extra],
                          capture_output=True, text=True, check=False)


def test_k4_k5_empty_canon_lists_leave_their_gates_pending_and_exit_4(tmp_path: Path) -> None:
    """K4 and K5: with the scaffold's empty lists, p-card, p-terms and
    p-limit passed 0 of 0 (p-limit even failed every row, a false red), and
    the cell left with exit 0. Each is pending with its reason now."""
    cell = scaffold_cell(tmp_path)
    fill_minimal_cell(cell)
    canon = json.loads((cell / "02-canon.json").read_text(encoding="utf-8"))
    canon.update({"terms to avoid": [], "role card fields": [], "origin labels": []})
    write(cell / "02-canon.json", json.dumps(canon))
    proc = run_cell(cell)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert ("| `04-roles/writer.md` | `p-card` | not measured (the canon's 'role card fields' "
            "list is empty) | 0 | pending |") in proc.stdout
    assert "the canon's 'terms to avoid' list is empty" in proc.stdout


def test_k5_k6_a_placeholder_in_a_card_field_fails_p_card(tmp_path: Path) -> None:
    """K5 and K6: cards with seven '<fill in>' passed p-card with '0 fields
    missing', the fields declared in the canon."""
    cell = scaffold_cell(tmp_path)
    fill_minimal_cell(cell, card_text=(cell / "04-roles" / "writer.md").read_text(encoding="utf-8"))
    proc = run_cell(cell)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "| `04-roles/writer.md` | `p-card` | 0 fields missing, 7 placeholders | 0 | fail |" \
        in proc.stdout
    assert "card: placeholder '<fill in>' in the card" in proc.stdout


TEMPLATES = SCAFFOLD.parents[1] / "references" / "templates.md"


def template_card() -> str:
    """The block of '04-roles/<role>.md' in the skill's templates."""
    text = TEMPLATES.read_text(encoding="utf-8")
    block = text.split("## 04-roles/<role>.md", 1)[1].split("```text\n", 1)[1]
    return block.split("```", 1)[0]


def test_k7_the_card_of_the_templates_filled_in_passes_p_card(tmp_path: Path) -> None:
    """K7: the card of templates.md was a table the gate does not read, so
    the filled template failed with seven notes while the placeholder card
    passed. The template now has the bold fields; filled, it passes."""
    card = re.sub(r"<[^<>\n]+>", "the agreed content", template_card())
    assert validator.card_hits(card, SCAFFOLD_CARD_FIELDS, True) == []
    assert validator.card_hits(template_card(), SCAFFOLD_CARD_FIELDS, True) != []
    cell = scaffold_cell(tmp_path)
    fill_minimal_cell(cell, card_text=card)
    proc = run_cell(cell)
    assert "| `04-roles/writer.md` | `p-card` | 0 fields missing, 0 placeholders | 0 | pass |" \
        in proc.stdout, proc.stdout + proc.stderr


def test_k8_a_domain_gate_is_a_tool_failure_that_names_contract_and_agent(fixture: Path) -> None:
    """K8: a gate of the target's domain has no implementation; the exit 2
    now says what the distributed validator measures and what is left."""
    gates = (fixture / "04-gates-and-rubric.md").read_text(encoding="utf-8")
    write_gates(fixture, gates.replace("\n### Size ranges",
                                       "| `g-speedup` | `doc1` | speedup | ≥ 1.3 | [hypothesis] "
                                       "a library has to be faster to be worth it |\n\n### Size ranges"))
    proc = run_validator(fixture)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "gate 'g-speedup' has no implementation" in proc.stderr
    assert "'contract + agent'" in proc.stderr


def test_k9_the_sensitivity_test_runs_in_a_scaffolded_cell(tmp_path: Path) -> None:
    """K9: the corpus's sensitivity script could not read a cell (no
    --layout, perturbations bound to the corpus), and the scaffold did not
    copy it. A minimally filled cell now runs its own sensitivity test from
    its data file, and p-sensitivity measures the report."""
    cell = scaffold_cell(tmp_path)
    fill_minimal_cell(cell)
    sens = subprocess.run([sys.executable, "-B", str(cell / "08-validator" / "sensitivity.py"),
                           "--folder", str(cell), "--layout", str(cell / "layout.json"),
                           "--work", str(tmp_path / "work")],
                          capture_output=True, text=True, check=False)
    assert sens.returncode == 0, sens.stdout + sens.stderr
    report = (cell / "08-validator" / "sensitivity.md").read_text(encoding="utf-8")
    assert "Caught 3 of 3." in report
    proc = run_cell(cell, "--allow-pending", "p-frozen-rubric,p-notes,p-anonymity")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert ("| `08-validator/sensitivity.md` | `p-sensitivity` | 3 of 3 gates covered, 0 missed "
            "of 3 | every gate covered, 0 missed | pass |" in proc.stdout)
    assert "Pending accepted by the caller (--allow-pending): `p-anonymity` (1 row)" in proc.stdout
    assert sorted(p.name for p in tmp_path.rglob("__pycache__")) == []


def test_a_gate_assigned_without_a_perturbation_leaves_p_sensitivity_pending(
        tmp_path: Path) -> None:
    """Regression (the review of v0.5.0): a cell with one perturbation and
    more gates assigned got '0 missed of 1' and a pass. The gates the
    artifact list assigns without a perturbation are named, and the gate is
    pending (exit 4), never a pass; the covered cell above passes."""
    cell = scaffold_cell(tmp_path)
    fill_minimal_cell(cell)
    perts = cell / "08-validator" / "perturbations.json"
    write(perts, json.dumps(json.loads(perts.read_text(encoding="utf-8"))[:1]))
    sens = subprocess.run([sys.executable, "-B", str(cell / "08-validator" / "sensitivity.py"),
                           "--folder", str(cell), "--layout", str(cell / "layout.json"),
                           "--work", str(tmp_path / "work")],
                          capture_output=True, text=True, check=False)
    assert sens.returncode == 0, sens.stdout + sens.stderr
    proc = run_cell(cell, "--allow-pending", "p-frozen-rubric,p-notes,p-anonymity")
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert ("| `08-validator/sensitivity.md` | `p-sensitivity` | not measured (1 of 3 gates "
            "covered, 0 missed of 1; gates without a perturbation: `p-anonymity`, `p-card`) | "
            "every gate covered, 0 missed | pending |" in proc.stdout)
    assert "Pending not accepted: `p-sensitivity` (1 row)" in proc.stdout


def test_sensitivity_counts_an_emptied_list_as_caught_when_it_expects_a_pending(
        tmp_path: Path, monkeypatch) -> None:
    """CR3: emptying a list of the canon has to leave its gate pending, not
    passing; the perturbation that does it expects 'pending'."""
    fixture = build_fixture(tmp_path)
    gates = (fixture / "04-gates-and-rubric.md").read_text(encoding="utf-8")
    write_gates(fixture, gates.replace("| `p-terms` | `doc1` |", "| `p-terms` | `canon`, `doc1` |"))
    rows = "| pipeline | artifact graph | hides dependencies |\n"
    pending = sensitivity.Perturbation("list emptied", "01-canon.md", rows, "", "p-terms",
                                       expect="pending")
    failing = sensitivity.Perturbation("list emptied, fail expected", "01-canon.md", rows, "",
                                       "p-terms")
    code, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pending, failing])
    assert row_result(report, "list emptied") == "caught"
    assert row_result(report, "list emptied, fail expected") == "MISSED"
    assert code == sensitivity.EXIT_MISSED


def test_a_perturbation_file_that_is_not_the_documented_list_is_a_tool_failure(
        tmp_path: Path) -> None:
    """The perturbation data of a cell is refused by name, never guessed."""
    cell = scaffold_cell(tmp_path)
    fill_minimal_cell(cell)
    write(cell / "08-validator" / "perturbations.json",
          json.dumps([{"name": "x", "document": "00-brief.md", "gate": "p-terms", "olt": "a"}]))
    sens = subprocess.run([sys.executable, "-B", str(cell / "08-validator" / "sensitivity.py"),
                           "--folder", str(cell), "--layout", str(cell / "layout.json")],
                          capture_output=True, text=True, check=False)
    assert sens.returncode == 2, sens.stdout + sens.stderr
    assert "unknown keys ['olt']" in sens.stderr


CORPUS_PRINCIPLE = CORPUS_CANON.parents[1] / "01-principle.md"


def test_k12_the_founding_phrases_are_triggers_and_a_paraphrase_escapes() -> None:
    """K12: the founding claims of the principle passed unlabeled. The five
    phrases are triggers of the corpus canon now; a paraphrase still
    escapes, which 06-gate-semantics.md declares (the gate is lexical)."""
    triggers = validator.load_canon(CORPUS_CANON).efficacy_triggers
    claim = "Separating the roles is the only way to stop every silent defect, and narrow roles err less.\n"
    assert validator.efficacy_mark_hits(claim, triggers)
    assert not validator.efficacy_mark_hits("Narrow roles make fewer mistakes.\n", triggers)
    for phrase in ("err less", "the only way", "observed in practice", "every rule below was born",
                   "none was"):
        assert phrase in triggers


def test_k12_the_lessons_are_measured_from_the_declared_heading(fixture: Path) -> None:
    """K12 (c): the lessons were outside the efficacy gate. An append-only
    document is measured from the heading its canon declares; above it,
    history is exempt; a declared heading that is missing is a finding."""
    lessons = ("# Lessons\n\nThe gate pays off, said round 1.\n\n## Round 2\n\n"
               "The rubric pays off here.\n")
    canon = (CANON + EFFICACY_TRIGGERS + "\n### Efficacy mark in append-only documents\n\n"
             "| Document | Measured from the heading |\n| --- | --- |\n| `10-doc1.md` | `## Round 2` |\n")
    fixture = fixture_with_gates(fixture.parent / "k12", ["p-efficacy-mark"], doc1=lessons)
    write(fixture / "01-canon.md", canon)
    proc = run_validator(fixture)
    assert "line 7: claim of efficacy ('pays off')" in proc.stdout, proc.stdout
    assert "line 3:" not in proc.stdout
    write(fixture / "10-doc1.md", lessons.replace("## Round 2", "## Round two"))
    proc = run_validator(fixture)
    assert "the heading '## Round 2' the canon declares" in proc.stdout


def test_a_truncated_table_row_is_a_tool_failure(fixture: Path) -> None:
    """Probe P9 of the panel: a row of the artifact table with two cells
    raised IndexError and left with exit 1, the code of a blocking note."""
    artifacts = (fixture / "02-artifacts.md").read_text(encoding="utf-8")
    write(fixture / "02-artifacts.md", artifacts + "| `stub` | `x.md` |\n")
    proc = run_validator(fixture)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "a table row has 2 cells" in proc.stderr
    assert "Traceback" not in proc.stderr


def test_an_unexpected_error_is_a_tool_failure(fixture: Path, monkeypatch) -> None:
    """IM17: any exception the validator does not expect exits 2, never 1."""
    def broken(*_: object) -> None:
        raise RuntimeError("probe")
    monkeypatch.setattr(validator.Checker, "run", broken)
    assert validator.main(["--folder", str(fixture)]) == validator.EXIT_TOOL_FAILURE


def test_a_missing_sensitivity_script_is_a_tool_failure(tmp_path: Path) -> None:
    """IM17: the import of the sensitivity script was outside any guard, so
    a validator copied without it left with a traceback and exit 1."""
    tool = tmp_path / "tool"
    tool.mkdir()
    (tool / "validator.py").write_bytes(VALIDATOR.read_bytes())
    fixture = build_fixture(tmp_path / "cell")
    sha = hashlib.sha256((tool / "validator.py").read_bytes()).hexdigest()
    write(fixture / "80-validator" / "sensitivity.md", "# Validator sensitivity\n\n"
          + valid_sensitivity_header(fixture, sha=sha) + "\n\n" + CAUGHT_ALL + "\n")
    proc = subprocess.run([sys.executable, "-B", str(tool / "validator.py"), "--folder", str(fixture)],
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "p-sensitivity needs sensitivity.py next to validator.py" in proc.stderr


def test_im15_pending_exits_4_unless_the_caller_accepts_it_by_name(fixture: Path) -> None:
    """IM15: exit 0 mixed 'everything passed' with 'nothing was measured'."""
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING
    assert "Pending not accepted: `p-frozen-rubric` (1 row)" in proc.stdout
    every = "p-frozen-rubric,p-notes,p-prior,p-prior-pin,p-sensitivity"
    proc = run_validator(fixture, "--allow-pending", every)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "Pending not accepted: none." in proc.stdout
    proc = run_validator(fixture, "--allow-pending", "p-frozen-rubic")
    assert proc.returncode == 2
    assert "does not implement: p-frozen-rubic" in proc.stderr


def test_im16_the_limits_of_p_recipe_and_p_limit_are_read_from_the_gate_table(tmp_path: Path) -> None:
    """IM16 (probe P28): the table said '>= 20 steps' and the report printed
    the constant 12. The limit is read from the row; without a stated limit
    the gate is pending."""
    recipe = "".join(f"### Step {n}. S\n\n**Reads:** a\n**Creates:** b\n**Does:** c\n**Done when:** d\n\n"
                     for n in range(3))
    artifacts = ARTIFACTS + "| `recipe` | `10-recipe.md` | writer | — | steps | `p-recipe` |\n"
    fixture = build_fixture(tmp_path, artifacts=artifacts)
    write(fixture / "10-recipe.md", recipe)
    row = ("| `p-recipe` | `recipe` | steps | 0 missing a field; ≥ {n} steps | [method] the "
           "recipe needs enough steps to reach the target |\n")
    for limit, result in (("2", "pass"), ("4", "fail")):
        write_gates(fixture, GATES.replace("\n### Size ranges", row.format(n=limit) + "\n### Size ranges"))
        proc = run_validator(fixture)
        assert "| `10-recipe.md` | `p-recipe` | 3 steps, " in proc.stdout
        assert f"≥ {limit} steps, 0 missing | {result} |" in proc.stdout, proc.stdout
    write_gates(fixture, GATES.replace("\n### Size ranges", row.replace("≥ {n} steps", "enough")
                                       + "\n### Size ranges"))
    assert "declares no minimum of steps" in run_validator(fixture).stdout


def test_im10_every_note_of_the_ledger_has_one_status_line(fixture: Path) -> None:
    """IM10: the ledger said '22 open' while some were closed. The state
    ledger gives every note of the ledger one line, read by p-notes."""
    notes = ["--notes", str(fixture / "90-notes" / "notes.json")]
    assert "no state ledger at 'state/notes-status.jsonl'" in run_validator(fixture, *notes).stdout
    write(fixture / "state" / "notes-status.jsonl",
          '{"ref": "notes:1", "status": "fixed", "closed_in": "0.5.0", "summary": "done"}\n')
    proc = run_validator(fixture, *notes)
    assert ("| `state/notes-status.jsonl` | `p-notes` | 0 open, 1 fixed, 0 disputed, 0 out of scope; "
            "0 invalid | every note tracked, 0 invalid | pass |") in proc.stdout
    write(fixture / "state" / "notes-status.jsonl",
          '{"ref": "panel:0.4.2:CR1", "status": "open", "summary": "x"}\n')
    proc = run_validator(fixture, *notes)
    assert proc.returncode == 1
    assert "note 1 of the ledger has no status line" in proc.stdout


def test_im21_a_contract_without_its_version_is_a_finding_and_a_round_is_a_string(
        fixture: Path) -> None:
    """IM21: no contract declared a version, and the round of a note was an
    integer where the round record has a string."""
    schema = dict(NOTES_SCHEMA)
    del schema["contract_version"]
    write(fixture / "05-contracts" / "notes.schema.json", json.dumps(schema))
    proc = run_validator(fixture)
    assert "the contract declares contract_version None" in proc.stdout
    notes = [dict(NOTES[0], round="v0.5.0", status="open")]
    write(fixture / "90-notes" / "notes.json", json.dumps(notes))
    assert validator.note_contract_hits(fixture / "90-notes" / "notes.json", {"canon"})[1] == []


@pytest.mark.parametrize("sample", [
    "on " + " ".join(("29", "October", "2026")),
    "on " + ".".join(("29", "10", "2026")),
    "kept in /scratch for now",
    "see file:///x/y",
    "under ~joe/work",
])
def test_im18_anonymity_reads_the_forms_it_let_through(fixture: Path, sample: str) -> None:
    """IM18 (probe P22): dates with the month's name or dots, a path of one
    segment under a common root, a file URL and a home folder by user name."""
    gates = (fixture / "04-gates-and-rubric.md").read_text(encoding="utf-8")
    write_gates(fixture, gates.replace("\n### Size ranges",
                                       "| `p-anonymity` | `doc1` | paths and dates | 0 | [method] the "
                                       "documents carry no machine path or authoring date |\n\n"
                                       "### Size ranges"))
    write(fixture / "10-doc1.md", DOC1 + f"\nIt was {sample}.\n")
    proc = run_validator(fixture)
    assert "| `10-doc1.md` | `p-anonymity` | 1 | 0 | fail |" in proc.stdout, proc.stdout


def test_an_empty_forbidden_list_leaves_the_identifier_half_pending(fixture: Path) -> None:
    """Probe P2: an empty --forbidden turned the identifier half into a pass."""
    gates = (fixture / "04-gates-and-rubric.md").read_text(encoding="utf-8")
    write_gates(fixture, gates.replace("\n### Size ranges",
                                       "| `p-anonymity` | `doc1` | paths and dates | 0 | [method] the "
                                       "documents carry no machine path or authoring date |\n\n"
                                       "### Size ranges"))
    write(fixture / "forbidden.txt", "")
    proc = run_validator(fixture, "--forbidden", str(fixture / "forbidden.txt"))
    assert "identifiers not measured (the list is empty) | 0 | pending |" in proc.stdout


def test_the_avoid_table_of_the_canon_is_exempt_when_it_is_the_last_section(fixture: Path) -> None:
    """Found in this round: the canon's own avoid table was exempt only when
    another level-2 section followed it."""
    gates = (fixture / "04-gates-and-rubric.md").read_text(encoding="utf-8")
    write_gates(fixture, gates.replace("| `p-terms` | `doc1` |", "| `p-terms` | `canon`, `doc1` |"))
    write(fixture / "01-canon.md", CANON)
    proc = run_validator(fixture)
    assert "| `01-canon.md` | `p-terms` | 0 | 0 | pass |" in proc.stdout, proc.stdout


GATE_SEMANTICS = CORPUS_CANON.parent / "06-gate-semantics.md"


def test_the_declared_count_of_perturbations_follows_the_instrument() -> None:
    """IM6: the prose said 25 while the instrument ran 26. The count in the
    gate semantics and in the gate table is the running set's."""
    declared = re.findall(r"(\d+) perturbations\b", GATE_SEMANTICS.read_text(encoding="utf-8"))
    assert declared and set(declared) == {str(N_PERTURBATIONS)}, declared
    gates_doc = (CORPUS_CANON.parent / "04-gates-and-rubric.md").read_text(encoding="utf-8")
    assert f"20 of 20 gates, {N_PERTURBATIONS} perturbations" in gates_doc


def test_the_corpus_gate_table_mirrors_its_artifact_table() -> None:
    """IM16: six divergences between the two maps of the corpus; the gate
    table mirrors the artifact table now, and p-references checks it."""
    canon_folder = CORPUS_CANON.parent
    artifacts = validator.load_artifact_table(validator.first_table(validator.section(
        (canon_folder / "02-artifacts.md").read_text(encoding="utf-8"), r"^Table$")))
    table = validator.gate_tables((canon_folder / "04-gates-and-rubric.md").read_text(encoding="utf-8"))[0]
    assert validator.gate_map_hits(artifacts, table) == []
