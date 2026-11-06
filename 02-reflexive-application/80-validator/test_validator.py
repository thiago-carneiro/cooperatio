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

### Documents outside the artifact table

| Document | Why |
| --- | --- |
| `80-validator/*.md` | the instrument's outputs in a fixture |
| `60-experiments.md` | the experiments record some tests write |
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
| `gates` | `04-gates-and-rubric.md` | writer | `canon` | gate table | none |
| `cards` | `03-roles/*.md` | writer | `canon` | role cards | none |
"""
CARDS_ROW = "| `cards` | `03-roles/*.md` | writer | `canon` | role cards | none |\n"

GATES = """# Gates: fixture

| Gate | Artifact | Magnitude | Limit | Justification |
| --- | --- | --- | --- | --- |
| `p-terms` | `doc1` | avoid words | 0 | [method] the canon is the single source of terms |
| `p-canon-link` | `doc1` | links to the canon | ≥ 1 resolved, 0 unresolved | [method] readers need the definitions one hop away |
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


# Since v0.6.0 a missing sensitivity report is blocking, so a fixture run
# carries a report the running instrument accepts, rewritten before each run
# for the fixture as it stands (its provenance pins the gates, the canon and
# the map). A test that writes its own report (no mark) keeps it; a test
# that needs no report passes sensitivity_report=False.
FIXTURE_REPORT_MARK = "Written by the test fixture for the fixture as it stands."


def run_layout(folder: Path, extra: tuple[str, ...]) -> dict:
    """The layout a run of the validator with these arguments resolves."""
    if "--layout" not in extra:
        return validator.DEFAULT_LAYOUT
    path = Path(extra[extra.index("--layout") + 1])
    return validator.merge_layout(validator.DEFAULT_LAYOUT, json.loads(path.read_text(encoding="utf-8")))


def write_fixture_sensitivity(folder: Path, layout: dict) -> None:
    report = folder / layout["artifacts"]["sensitivity"]
    if report.exists() and FIXTURE_REPORT_MARK not in report.read_text(encoding="utf-8"):
        return
    try:
        header = valid_sensitivity_header(folder, layout=layout)
    except validator.InputError:
        return  # the run itself reports the broken input
    write(report, "# Validator sensitivity\n\n" + header + "\n\n" + FIXTURE_REPORT_MARK
          + "\n\n" + CAUGHT_ALL + "\n")


def run_validator(folder: Path, *extra: str,
                  sensitivity_report: bool = True) -> subprocess.CompletedProcess[str]:
    if sensitivity_report:
        try:
            write_fixture_sensitivity(folder, run_layout(folder, extra))
        except (validator.InputError, ValueError, OSError):
            pass  # a broken layout or input is what the run itself reports
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
    canon_json["documents outside the artifact list"] = JSON_CELL_OUTSIDE
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
        "numbers not measured (no prior document; 000-fixture: owner-held evidence, not " \
        "measured here) | 0 | pending |" in proc.stdout


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
        "not measured (no prior document; 000-fixture: owner-held evidence, not measured " \
        "here) | equal | pending |" in proc.stdout


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
    # The card is its own artifact here; since v0.6.0 a file belongs to one.
    artifacts = ARTIFACTS.replace(CARDS_ROW, "") + (
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
    # The contract file is its own artifact here; a file belongs to one.
    artifacts = ARTIFACTS.replace("`05-contracts/notes.schema.json`, ", "") + (
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
                              count: int | None = None, layout: dict | None = None,
                              cases: str = "case sha256: none\n") -> str:
    """A provenance header the running instrument accepts: the sha256 of
    the validator.py next to this test (the running one), of the folder's
    gate section, canon and resolved gate map (v0.6.0), the current
    perturbation set and the case documents (rework of v0.6.0) — or
    deliberate divergences."""
    if sha is None:
        sha = validator.content_digest(Path(validator.__file__).resolve().with_name("validator.py"))
    if ids is None:
        ids = [pert.name for pert in sensitivity.PERTURBATIONS]
    n = len(ids) if count is None else count
    digests = validator.provenance_inputs(folder, layout or validator.DEFAULT_LAYOUT)
    return (f"validator sha256: {sha}\ngates sha256: {digests['gates']}\n"
            f"canon sha256: {digests['canon']}\nmap sha256: {digests['map']}\n"
            f"perturbations: {n} ({', '.join(ids)})\n{cases}").rstrip("\n")


# The size of the running perturbation set (22 since v0.4.0): the tests
# follow the instrument instead of a literal count that each round changes.
# Since v0.5.0 the table has to add up to its 'Caught' line, so the
# fabricated reports carry one row per perturbation; since v0.6.0 they also
# carry the specificity and the pair coverage.
N_PERTURBATIONS = len(sensitivity.PERTURBATIONS)
CAUGHT_ALL = ("| Perturbation | Document | Expected gate | Result |\n| --- | --- | --- | --- |\n"
              + "".join(f"| {pert.name} | `{pert.document}` | `{pert.gate}` | caught |\n"
                        for pert in sensitivity.PERTURBATIONS)
              + f"\nCaught {N_PERTURBATIONS} of {N_PERTURBATIONS}.\n"
              + f"Noisy: 0 of {N_PERTURBATIONS}.\nPairs covered: 1 of 1.")
# The limit p-sensitivity applies, as the report prints it.
SENS_LIMIT = validator.SENSITIVITY_LIMIT


def test_sensitivity_path_resolves_through_the_layout(tmp_path: Path) -> None:
    """Regression (v0.2.3, medium finding of instance 004): the sensitivity
    report used to be read from a hardcoded directory, so every scaffolded
    cell (08-validator/) showed p-sensitivity as pending; the path now
    resolves through the layout, like canon, gates, rubric and registry."""
    fixture = build_fixture(tmp_path)
    write(fixture / "80-validator" / "alt-sensitivity.md",
          "# Validator sensitivity\n\n" + valid_sensitivity_header(fixture) +
          "\n\n" + CAUGHT_ALL + "\n")
    layout = tmp_path / "layout-alt-sensitivity.json"
    layout.write_text(json.dumps(
        {"version": 1, "artifacts": {"sensitivity": "80-validator/alt-sensitivity.md"}}),
        encoding="utf-8")
    proc = run_validator(fixture, "--layout", str(layout))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert re.search(r"^\| `80-validator/alt-sensitivity\.md` \| `p-sensitivity` \| (\d+) of \1 "
                     rf"gates covered, 1 of 1 pairs \(100 %\), 0 missed of {N_PERTURBATIONS}, 0 noisy "
                     rf"\| {re.escape(SENS_LIMIT)} \| pass \|$", proc.stdout, re.M), proc.stdout


def test_sensitivity_without_a_report_is_blocking_with_the_reason(fixture: Path) -> None:
    """A cell whose report is missing gets a blocking note that names the
    path it looked for and the layout key that points there — never a crash,
    never a silent pass, and since v0.6.0 never a pending either: a pending
    could be accepted by name, so deleting the report was cheaper than
    keeping it current (probe X1 of the panel that reviewed v0.5.0)."""
    proc = run_validator(fixture, sensitivity_report=False)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert (f"| `80-validator/sensitivity.md` | `p-sensitivity` | no report | {SENS_LIMIT} | "
            "fail |") in proc.stdout
    assert ("no sensitivity report at '80-validator/sensitivity.md' (the layout key "
            "artifacts.sensitivity points there)") in proc.stdout


def test_sensitivity_report_without_a_caught_line_is_a_tool_failure(tmp_path: Path) -> None:
    """A report with a valid provenance header but no Caught line is
    malformed input: tool failure (exit 2), not a blocking note."""
    fixture = build_fixture(tmp_path)
    write(fixture / "80-validator" / "sensitivity.md",
          "# Validator sensitivity\n\n" + valid_sensitivity_header(fixture)
          + "\n\nNoisy: 0 of 0.\nPairs covered: 0 of 0.\n")
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
            f"mismatch | {SENS_LIMIT} | fail |") in proc.stdout


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
    assert "produced by a different validator (sha256 mismatch" in proc.stdout


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
    # v0.6.0: an empty set measured nothing, so it exits 4, like a pending.
    assert code == sensitivity.EXIT_EMPTY
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
# Since v0.6.0 an executed experiment backs a label only with its
# provenance table (an input and an output, each with a sha256).
PROVENANCE_TABLE = ("### Provenance\n\n| File | Kind | sha256 |\n| --- | --- | --- |\n"
                    f"| task prompt | input | `{'a' * 64}` |\n| report | output | `{'b' * 64}` |\n\n")
EXPERIMENTS_RECORD = ("# Experiments\n\n## E1 — the first one\n\n| Field | Value |\n| --- | --- |\n"
                      "| Status | `executed` |\n\n### Question\n\nDoes it?\n\n" + PROVENANCE_TABLE +
                      "## E2 — the second one\n\n| Field | Value |\n| --- | --- |\n"
                      "| Status | `designed` |\n")
# The documents of a JSON test cell outside its artifact list (v0.6.0).
JSON_CELL_OUTSIDE = ["04-roles/*.md", "06-gates.md", "80-validator/*.md"]


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
                                    "p-prior-pin", needs_case=True, also="p-prior")
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
                                    '"severity": "trivial"', "p-notes", needs_notes=True,
                                    also="p-contract-shape")
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
    canon_json["documents outside the artifact list"] = JSON_CELL_OUTSIDE
    write(folder / "02-canon.json", json.dumps(canon_json))
    gates = ("# Gates\n\n| Gate | Artifact | Magnitude | Limit | Justification |\n"
             "| --- | --- | --- | --- | --- |\n| `p-canon-link` | `card` | resolved links | "
             "≥ 1 resolved, 0 unresolved | "
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
    assert ("numbers of 001-other not measured (no --case document identified as that prior; "
            "001-other: owner-held evidence, not measured here) | 0 | pending |") in proc.stdout
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"),
                         "--case", str(tmp_path / "other-method.md"))
    assert proc.returncode == 1
    assert "prior '001-other': '49' cites section '9' of the prior method document" in proc.stdout


def test_a_cited_prior_without_its_document_is_pending_by_name(tmp_path: Path) -> None:
    """I14: with one of two cited priors passed, the units of the other are
    pending by name (never checked against the wrong document), and its pin
    is pending by name too when that prior is owner-held (rework of v0.6.0:
    it was blocking, so a clone could not measure the prior it has); a
    distributed prior without its document stays blocking."""
    fixture = build_two_prior_fixture(tmp_path)
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert ("numbers of 001-other not measured (no --case document identified as that prior; "
            "001-other: owner-held evidence, not measured here) | 0 | pending |") in proc.stdout
    assert ("| `p-prior-pin` | 1 of 2 executed priors pinned; 001-other not measured (no prior "
            "document; 001-other: owner-held evidence") in proc.stdout
    registry = tmp_path / "instances" / "registry.json"
    write(registry, registry.read_text(encoding="utf-8").replace(OWNER_HELD, "instances/001-other"))
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"))
    assert proc.returncode == 1
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
                       "prior-statement triggers": ["reference case"], "recorded facts": facts,
                       "documents outside the artifact list": JSON_CELL_OUTSIDE})
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
    assert not validator.efficacy_mark_hits(
        "In that round the gates caught the drift [lessons:The v0.5.0 round: exit 0 is not green].\n",
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
# v0.6.0: two more checks of the closed --allow-pending list in a v0.5.0
# function, and one function per false green of the panel that reviewed v0.5.0.
SELF_TEST_RULES_V05 = 29 + 2
SELF_TEST_RULES_V06 = 14


def test_self_test_covers_the_rules_of_v04() -> None:
    """v0.4.1: the self-test gained one short function per rule of v0.4.0
    and v0.4.1 (recorded facts, section references, full ids, number
    format, layout keys, registry status, experiment status); v0.5.0 one
    per false green of the panel that reviewed v0.4.2."""
    rules_v04 = validator.self_test_rules_v04(validator.SelfTest())
    assert rules_v04 == SELF_TEST_RULES_V04
    rules_v05 = validator.self_test_rules_v05(validator.SelfTest())
    assert rules_v05 == SELF_TEST_RULES_V05
    rules_v06 = validator.self_test_rules_v06(validator.SelfTest())
    assert rules_v06 == SELF_TEST_RULES_V06
    proc = subprocess.run([sys.executable, "-B", str(VALIDATOR), "--self-test"],
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    total = int(proc.stdout.split("all ", 1)[1].split()[0])
    assert total - rules_v04 - rules_v05 - rules_v06 == SELF_TEST_BEFORE_V041


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
    for name in ("validator.py", "sensitivity.py", "perturbation_set.py"):
        (tool / name).write_bytes(VALIDATOR.with_name(name).read_bytes())
    fixture = build_fixture(tmp_path / "cell")
    sha = hashlib.sha256((tool / "validator.py").read_bytes()).hexdigest()
    write(fixture / "80-validator" / "alt-sensitivity.md", "# Validator sensitivity\n\n"
          + valid_sensitivity_header(fixture, sha=sha) + "\n\n" + CAUGHT_ALL + "\n")
    layout = tmp_path / "layout.json"
    layout.write_text(json.dumps({"version": 1,
                                  "artifacts": {"sensitivity": "80-validator/alt-sensitivity.md"}}),
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


def test_a_gate_row_deleted_from_the_gate_table_is_a_finding(tmp_path: Path) -> None:
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


def test_a_report_made_against_another_gate_table_or_canon_is_blocking(tmp_path: Path) -> None:
    """K1: the provenance pinned only the validator's sha. It pins the gate
    section and the canon too; editing either after the report is blocking."""
    fixture = build_fixture(tmp_path)
    report = fixture / "80-validator" / "sensitivity.md"
    write(report, "# Validator sensitivity\n\n" + valid_sensitivity_header(fixture)
          + "\n\n" + CAUGHT_ALL + "\n")
    assert re.search(r"^\| `80-validator/sensitivity\.md` \| `p-sensitivity` \| \d+ of \d+ gates "
                     r"covered, .* 0 missed of \d+, 0 noisy \| [^|]+ \| pass \|$",
                     run_validator(fixture).stdout, re.M)
    for name in ("04-gates-and-rubric.md", "01-canon.md"):
        original = (fixture / name).read_text(encoding="utf-8")
        write(fixture / name, original.replace("| target |", "| target  |")
              .replace("| `p-terms` | `doc1` |", "| `p-terms` | `doc1`  |"))
        proc = run_validator(fixture)
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert "changed since the sensitivity report was made" in proc.stdout, name
        write(fixture / name, original)


def test_a_report_whose_table_does_not_add_up_is_blocking(tmp_path: Path) -> None:
    """Probe P5 of the panel: a header and a 'Caught' line, with no row,
    passed. The table has to have one row per perturbation, and as many
    caught rows as the line says."""
    fixture = build_fixture(tmp_path)
    report = fixture / "80-validator" / "sensitivity.md"
    header = "# Validator sensitivity\n\n" + valid_sensitivity_header(fixture) + "\n\n"
    write(report, header + f"Caught {N_PERTURBATIONS} of {N_PERTURBATIONS}.\n"
          f"Noisy: 0 of {N_PERTURBATIONS}.\nPairs covered: 1 of 1.\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "in 0 rows" in proc.stdout
    write(report, header + CAUGHT_ALL.replace("| caught |", "| MISSED |", 1) + "\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "rows caught" in proc.stdout


def test_a_prior_mark_inside_a_code_span_fails_p_prior_mark(fixture: Path) -> None:
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
                  "origin labels": ["[method]", "[brief]", "[hypothesis]"],
                  "documents outside the artifact list": CELL_OUTSIDE})
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


# The documents of a minimal cell its artifact list does not declare
# (v0.6.0: every Markdown document belongs to an artifact or to this list).
CELL_OUTSIDE = ["01-sources-of-truth.md", "06-gates.md", "07-rubric.md", "lessons.md",
                "08-validator/*.md"]


def measured_inputs(cell: Path) -> tuple[str, ...]:
    """Freeze the cell's rubric and name its note ledger: since v0.6.0 a
    pending p-frozen-rubric or p-notes cannot be accepted by name."""
    pin = cell / "07-rubric.sha256"
    proc = run_cell(cell, "--freeze-rubric", str(pin))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return ("--rubric-hash", str(pin), "--notes", str(cell / "open-notes.json"))


def run_cell(cell: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-B", str(cell / "08-validator" / "validator.py"),
                           "--folder", str(cell), "--layout", str(cell / "layout.json"), *extra],
                          capture_output=True, text=True, check=False)


def test_empty_canon_lists_leave_their_gates_pending_and_exit_4(tmp_path: Path) -> None:
    """K4 and K5: with the scaffold's empty lists, p-card, p-terms and
    p-limit passed 0 of 0 (p-limit even failed every row, a false red), and
    the cell left with exit 0. Each is pending with its reason now. (Since
    v0.6.0 the cell without its sensitivity report also exits 1 on that
    blocking note, the only one.)"""
    cell = scaffold_cell(tmp_path)
    fill_minimal_cell(cell)
    canon = json.loads((cell / "02-canon.json").read_text(encoding="utf-8"))
    canon.update({"terms to avoid": [], "role card fields": [], "origin labels": []})
    write(cell / "02-canon.json", json.dumps(canon))
    proc = run_cell(cell)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "Count: 1 blocking, 0 high" in proc.stdout
    assert "no sensitivity report at '08-validator/sensitivity.md'" in proc.stdout
    assert ("| `04-roles/writer.md` | `p-card` | not measured (the canon's 'role card fields' "
            "list is empty) | 0 | pending |") in proc.stdout
    assert "the canon's 'terms to avoid' list is empty" in proc.stdout


def test_a_placeholder_in_a_card_field_fails_p_card(tmp_path: Path) -> None:
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
    block = text.split("## `04-roles/<role>.md`", 1)[1].split("```text\n", 1)[1]
    return block.split("```", 1)[0]


def test_the_card_of_the_templates_filled_in_passes_p_card(tmp_path: Path) -> None:
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


def test_a_domain_gate_is_a_tool_failure_that_names_contract_and_agent(fixture: Path) -> None:
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


def test_the_sensitivity_test_runs_in_a_scaffolded_cell(tmp_path: Path) -> None:
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
    proc = run_cell(cell, *measured_inputs(cell), "--allow-pending", "p-anonymity")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert ("| `08-validator/sensitivity.md` | `p-sensitivity` | 3 of 3 gates covered, 3 of 7 "
            f"pairs (42 %), 0 missed of 3, 0 noisy | {SENS_LIMIT} | pass |" in proc.stdout)
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
    proc = run_cell(cell, *measured_inputs(cell), "--allow-pending", "p-anonymity")
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert ("| `08-validator/sensitivity.md` | `p-sensitivity` | not measured (1 of 3 gates "
            "covered, 1 of 7 pairs (14 %), 0 missed of 1, 0 noisy; gates without a "
            "perturbation: `p-anonymity`, `p-card`; fewer than 25 % of the (document, gate) "
            f"pairs perturbed) | {SENS_LIMIT} | pending |" in proc.stdout)
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


def test_the_founding_phrases_are_triggers_and_a_paraphrase_escapes() -> None:
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


def test_the_lessons_are_measured_from_the_declared_heading(fixture: Path) -> None:
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
    assert "p-sensitivity needs perturbation_set.py next to validator.py" in proc.stderr


def test_pending_exits_4_unless_the_caller_accepts_it_by_name(fixture: Path) -> None:
    """IM15: exit 0 mixed 'everything passed' with 'nothing was measured'."""
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING
    assert "Pending not accepted: `p-frozen-rubric` (1 row)" in proc.stdout
    pin = fixture / "rubric.sha256"
    pin.write_text(validator.rubric_hash(GATES) + "\n", encoding="utf-8")
    write(fixture / "state" / "notes-status.jsonl",
          '{"ref": "notes:1", "status": "open", "summary": "a legacy note"}\n')
    measured = ("--rubric-hash", str(pin), "--notes", str(fixture / "90-notes" / "notes.json"))
    proc = run_validator(fixture, *measured, "--allow-pending", "p-prior,p-prior-pin")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "Pending not accepted: none." in proc.stdout
    proc = run_validator(fixture, "--allow-pending", "p-frozen-rubic")
    assert proc.returncode == 2
    assert "does not implement: p-frozen-rubic" in proc.stderr


def test_the_limits_of_p_recipe_and_p_limit_are_read_from_the_gate_table(tmp_path: Path) -> None:
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


def test_every_note_of_the_ledger_has_one_status_line(fixture: Path) -> None:
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


def test_a_contract_without_its_version_is_a_finding_and_a_round_is_a_string(
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
def test_anonymity_reads_the_forms_it_let_through(fixture: Path, sample: str) -> None:
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


# ------------------------------- v0.6.0 (the panel that reviewed v0.5.0)
# One regression test per probe of that panel that became a correction,
# each failing on the validator of v0.5.0.

def notes_of(proc: subprocess.CompletedProcess[str]) -> str:
    return proc.stdout.split("## Notes", 1)[1]


def test_a_file_of_an_artifact_repointed_is_a_finding(fixture: Path) -> None:
    """Probe G1: repointing a file of an artifact took a document out of
    every gate with exit 0. The shared file, the orphan document and the
    stale map of the sensitivity report are now findings."""
    run_validator(fixture)  # writes the fixture's report for the map as it stands
    write(fixture / "11-doc2.md", "# Document two\n")
    write(fixture / "02-artifacts.md", (fixture / "02-artifacts.md").read_text(encoding="utf-8")
          .replace("| `doc1` | `10-doc1.md` |", "| `doc1` | `01-canon.md` |"))
    proc = run_validator(fixture, sensitivity_report=False)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "`01-canon.md` belongs to 2 artifacts (canon, doc1)" in proc.stdout
    assert "document `10-doc1.md` belongs to no artifact" in proc.stdout
    assert "document `11-doc2.md` belongs to no artifact" in proc.stdout
    assert "the size range of `10-doc1.md` names a document no artifact declares" in proc.stdout
    assert "the map changed since the sensitivity report was made" in proc.stdout


def test_a_document_outside_every_artifact_is_a_finding_unless_declared(fixture: Path) -> None:
    """Probe G2: a new document with HTML, a path and a date passed with exit
    0, since no artifact named it. The canon's list of documents outside the
    artifact table is the only exemption."""
    write(fixture / "23-extra.md", "# Extra\n\nA <b>claim</b>, see /home/x/notes.md.\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "document `23-extra.md` belongs to no artifact" in proc.stdout
    write(fixture / "01-canon.md", (fixture / "01-canon.md").read_text(encoding="utf-8").replace(
        "| `60-experiments.md` |", "| `23-extra.md` | a scratch page |\n| `60-experiments.md` |"))
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr


def test_each_literal_path_of_an_artifact_has_to_exist(tmp_path: Path) -> None:
    """Probe PD1: deleting one of the two literal files of an artifact passed,
    because the artifact still matched something."""
    artifacts = ARTIFACTS.replace("| `doc1` | `10-doc1.md` |", "| `doc1` | `10-doc1.md`, `12-doc3.md` |")
    fixture = build_fixture(tmp_path, artifacts=artifacts)
    write(fixture / "12-doc3.md", "# Doc three\n\nTerms follow the [canon](01-canon.md).\n")
    assert run_validator(fixture).returncode == EXIT_PENDING
    (fixture / "12-doc3.md").unlink()
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "| `12-doc3.md` | `p-declared` | missing | exists | fail |" in proc.stdout


@pytest.mark.parametrize("mark", ["[prior:000-FIXTURE]", "[prior: 000-fixture]", "[prior:]",
                                  "[prior:000_fixture]"])
def test_a_malformed_prior_mark_is_blocking(fixture: Path, mark: str) -> None:
    """Probes M1, M2, M3 and M7: a mark outside the id grammar satisfied
    p-prior-mark and switched off the number check; an invented number
    passed with exit 0. One reading of the mark now, and it is blocking."""
    write(fixture / "10-doc1.md", DOC1.replace("[prior:000-fixture], the tool gave 49 items",
                                               f"{mark}, the tool gave 48 items"))
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert f"malformed mark {mark}" in proc.stdout


def test_a_number_in_a_code_span_of_a_marked_unit_is_read(fixture: Path) -> None:
    """Probe M4: an invented number between backticks, under a valid mark,
    was never read."""
    write(fixture / "10-doc1.md", DOC1.replace("gave 49 items", "gave `48` items"))
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "'48' has no row of that prior" in proc.stdout
    write(fixture / "10-doc1.md", DOC1.replace("gave 49 items", "gave `49` items"))
    proc = run_validator(fixture, "--case", str(fixture.parent / "prior-method.md"))
    assert "| `10-doc1.md` | `p-prior` | 1 labels, 0 unregistered, 1 numbers" in proc.stdout


def test_p_sensitivity_is_never_accepted_by_name(fixture: Path) -> None:
    """Probe X1 (it refuted the README): with the report deleted, accepting
    p-sensitivity by name gave exit 0. A missing report is blocking, and the
    acceptance list is closed (p-anonymity, p-prior, p-prior-pin)."""
    proc = run_validator(fixture, "--allow-pending", "p-sensitivity", sensitivity_report=False)
    assert proc.returncode == 2
    assert "has to be measured, never accepted by name" in proc.stderr
    proc = run_validator(fixture, "--allow-pending", "p-prior,p-prior-pin,p-frozen-rubric")
    assert proc.returncode == 2
    proc = run_validator(fixture, "--allow-pending", "p-anonymity")
    assert "Accepted but not pending: `p-anonymity`." in proc.stdout


def test_a_placeholder_in_an_instance_artifact_table_is_a_finding() -> None:
    """Probe IP1: 'TBD' in the artifact table of an instance passed."""
    text = ("## Artifacts and graph\n\n| Artifact | File | Owner | Depends on | Gates |\n"
            "| --- | --- | --- | --- | --- |\n| `a` | TBD | owner | — | none |\n")
    assert "artifact 'a': placeholder 'TBD'" in validator.instance_reference_hits(text)


@pytest.mark.parametrize("block, fails", [
    ("~~~sh\nls\n~~~\n", True), ("- item\n\n  ```sh\n  ls\n  ```\n", True),
    ("<!-- a hidden note -->\n", True), ("````text\nplain\n````\n", False),
    ("~~~text\nplain\n~~~\n", False)])
def test_fences_and_comments_follow_commonmark(fixture: Path, block: str,
                                                             fails: bool) -> None:
    """Probes F1b, F2b, F3 and F4: a tilde fence, an indented fence and an
    HTML comment passed p-form; a four-backtick text fence failed it."""
    assert bool(validator.form_hits(block)) is fails
    assert validator.anonymity_hits(block, []) == []


def test_a_crlf_checkout_keeps_every_pin(tmp_path: Path) -> None:
    """Probes W1 and W2: the validator was hashed as bytes, so a checkout
    converted to CRLF was red for good. One hash policy for every object:
    the text read as UTF-8, BOM dropped, line breaks as LF."""
    lf = tmp_path / "lf.py"
    crlf = tmp_path / "crlf.py"
    lf.write_bytes(VALIDATOR.read_bytes())
    crlf.write_bytes(b"\xef\xbb\xbf" + VALIDATOR.read_bytes().replace(b"\n", b"\r\n"))
    assert validator.content_digest(lf) == validator.content_digest(crlf)
    assert validator.read(crlf) == validator.read(lf)


def test_a_cp1252_console_does_not_end_the_run(fixture: Path) -> None:
    """Probe E1: with stdout in cp1252, '≥' ended the run in exit 2."""
    write_fixture_sensitivity(fixture, validator.DEFAULT_LAYOUT)
    env = dict(os.environ, PYTHONIOENCODING="cp1252")
    proc = subprocess.run([sys.executable, "-B", str(VALIDATOR), "--folder", str(fixture)],
                          capture_output=True, check=False, env=env)
    assert proc.returncode == EXIT_PENDING, proc.stderr
    assert "≥ 1 resolved".encode("utf-8") in proc.stdout


def test_a_limit_cell_that_diverges_from_the_applied_limit_is_a_finding(fixture: Path) -> None:
    """Probes LC1 and LC2: the Limit column was decorative."""
    gates = (fixture / "04-gates-and-rubric.md").read_text(encoding="utf-8")
    write_gates(fixture, gates.replace("| avoid words | 0 |", "| avoid words | 5 |"))
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "the Limit cell of `p-terms` states 5; the validator applies 0" in proc.stdout


def test_a_gate_with_two_rows_is_a_tool_failure(fixture: Path) -> None:
    """Probe DUP1: a second row of a gate measured it twice in silence."""
    gates = (fixture / "04-gates-and-rubric.md").read_text(encoding="utf-8")
    row = "| `p-terms` | `doc1` | avoid words | 0 | [method] the canon is the single source of terms |\n"
    write(fixture / "04-gates-and-rubric.md", gates.replace(row, row + row))
    proc = run_validator(fixture, sensitivity_report=False)
    assert proc.returncode == 2
    assert "more than one row for p-terms" in proc.stderr


def test_m_determinism_and_the_header_name_the_report_of_the_layout(tmp_path: Path) -> None:
    """S2 of the instrument seat: a cell's m-determinism row named the
    corpus path 80-validator/report.md."""
    cell = scaffold_cell(tmp_path)
    proc = run_cell(cell)
    assert "| `m-determinism` | `08-validator/report.md` |" in proc.stdout
    assert "Generated by `08-validator/validator.py`" in proc.stdout


def test_with_output_a_summary_goes_to_stderr(fixture: Path, tmp_path: Path) -> None:
    """The adopter's diary: with --output a failing run printed nothing."""
    proc = run_validator(fixture, "--output", str(tmp_path / "out.md"))
    assert proc.stdout == ""
    assert proc.stderr.startswith(f"validator: exit {EXIT_PENDING}; notes: 0 blocking")


def test_an_interpreter_below_the_minimum_is_a_tool_failure(monkeypatch, capsys) -> None:
    """Requirements (v0.6.0): Python 3.9 or later; below it, exit 2."""
    monkeypatch.setattr(validator.sys, "version_info", (3, 8, 0))
    assert validator.main(["--self-test"]) == validator.EXIT_TOOL_FAILURE
    assert "3.9 or later is required" in capsys.readouterr().err


# The domain gates of a cell (recommendation 1; the regression of seat 7:
# exit 0 with the identity gate and the tests failing).

DOMAIN_ROW = ("| `d-identity` | `doc1` | divergent cases against the frozen reference | "
              "0 divergent | [method] identity of results is the non-negotiable |\n")


def domain_fixture(fixture: Path, result: str = "pass", magnitude: str = "0 divergent of 38",
                   inputs: list | None = None) -> tuple[str, ...]:
    gates = (fixture / "04-gates-and-rubric.md").read_text(encoding="utf-8")
    if DOMAIN_ROW not in gates:
        write_gates(fixture, gates.replace("\n### Size ranges", DOMAIN_ROW + "\n### Size ranges", 1))
    if inputs is None:
        inputs = [{"path": "10-doc1.md",
                   "sha256": validator.content_digest(fixture / "10-doc1.md")}]
    write(fixture / "results" / "identity.json", json.dumps(
        {"contract_version": "1", "gate": "d-identity", "magnitude": magnitude,
         "limit": "0 divergent", "result": result, "inputs": inputs}))
    layout = fixture.parent / "domain-layout.json"
    layout.write_text(json.dumps({"version": 1, "domain-results": ["results/*.json"]}),
                      encoding="utf-8")
    return ("--layout", str(layout))


def test_a_failing_domain_gate_is_a_note_and_exit_1(fixture: Path) -> None:
    """Seat 7's regression: the candidate of v1 copied over v2, identity 7
    divergent of 38, and the validator said exit 0. The cell's result is
    now read: a fail is a note with the severity of the gate's row."""
    layout = domain_fixture(fixture)
    assert "| `results/identity.json` | `d-identity` | 0 divergent of 38 | 0 divergent | pass |" \
        in run_validator(fixture, *layout).stdout
    layout = domain_fixture(fixture, "fail", "7 divergent of 38")
    proc = run_validator(fixture, *layout)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "| `results/identity.json` | `d-identity` | 7 divergent of 38 | 0 divergent | fail |" \
        in proc.stdout


def test_a_stale_domain_result_is_blocking(fixture: Path) -> None:
    """Seat 7, I1: a result whose candidate sha256 differed from the current
    file was accepted. The inputs are recomputed."""
    layout = domain_fixture(fixture, inputs=[{"path": "10-doc1.md", "sha256": "0" * 64}])
    proc = run_validator(fixture, *layout)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "stale domain result: input `10-doc1.md` changed" in proc.stdout


def test_a_domain_tool_failure_or_a_broken_result_is_exit_2(fixture: Path) -> None:
    layout = domain_fixture(fixture, "tool-failure", "the benchmark did not run")
    assert run_validator(fixture, *layout).returncode == 2
    layout = domain_fixture(fixture)
    write(fixture / "results" / "identity.json", json.dumps({"gate": "d-identity"}))
    proc = run_validator(fixture, *layout)
    assert proc.returncode == 2 and "breaks domain-result.schema.json" in proc.stderr


def test_a_declared_domain_gate_without_a_result_is_pending(fixture: Path) -> None:
    layout = domain_fixture(fixture)
    (fixture / "results" / "identity.json").unlink()
    proc = run_validator(fixture, *layout)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `04-gates-and-rubric.md` | `d-identity` | not measured (no domain result" in proc.stdout


def test_a_domain_gate_in_a_table_of_its_own_is_read(fixture: Path) -> None:
    """The cell of seat 7 kept its d-* rows in a second table, which no gate
    read: its rows count like the first table's."""
    layout = domain_fixture(fixture)
    gates = (fixture / "04-gates-and-rubric.md").read_text(encoding="utf-8").replace(DOMAIN_ROW, "")
    table = ("\n## Domain gates\n\n| Gate | Artifact | Magnitude | Limit | Justification |\n"
             "| --- | --- | --- | --- | --- |\n" + DOMAIN_ROW)
    write_gates(fixture, gates.replace("\n### Size ranges", table + "\n### Size ranges", 1))
    (fixture / "results" / "identity.json").unlink()
    proc = run_validator(fixture, *layout)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `04-gates-and-rubric.md` | `d-identity` | not measured" in proc.stdout


def test_a_domain_result_that_does_not_measure_its_artifact_is_blocking(fixture: Path) -> None:
    """Rework of v0.6.0 (the review's D2): a result whose inputs held only
    the canon passed while the candidate of its gate row changed."""
    layout = domain_fixture(fixture, inputs=[{"path": "01-canon.md", "sha256": validator.content_digest(
        fixture / "01-canon.md")}])
    proc = run_validator(fixture, *layout)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "the result does not measure `10-doc1.md`, a file of the artifacts of its gate row" \
        in proc.stdout


@pytest.mark.parametrize("result, magnitude, limit, caught", [
    ("pass", "7 divergent of 38", "0 divergent", True),
    ("pass", "0 divergent of 38", "0 divergent", False),
    ("fail", "0 divergent of 38", "0 divergent", True),
    ("pass", "1.2 s", "\u2264 2 s", False),
    ("pass", "2.5 s", "\u2264 2 s", True),
    ("pass", "1.2 x", "at least 1.5 x", True),
    ("pass", "38 identical", "every case identical", False)])
def test_a_domain_result_its_numbers_contradict_is_caught(
        result: str, magnitude: str, limit: str, caught: bool) -> None:
    """Rework of v0.6.0 (the review's D1): 'pass' with '7 divergent of 38'
    against '0 divergent' was a pass; a limit with a comparison or a bare zero
    is compared, any other is not read."""
    hits = validator.contradiction_hits({"result": result, "magnitude": magnitude, "limit": limit})
    assert bool(hits) is caught, hits


def test_a_failed_domain_gate_is_at_least_high_unless_the_owner_decided(fixture: Path) -> None:
    """Rework of v0.6.0 (the review's D4): a Severity column 'low' on the row
    of d-identity made a failed identity of results a low note."""
    layout = domain_fixture(fixture, "fail", "7 divergent of 38")
    gates = (fixture / "04-gates-and-rubric.md").read_text(encoding="utf-8")
    lines = []
    for line in gates.split("\n"):
        if line.startswith("| Gate |"):
            line += " Severity |"
        elif line.startswith("| --- | --- | --- | --- | --- |"):
            line += " --- |"
        elif line.startswith("| `"):
            line += " low |" if line.startswith("| `d-identity`") else " high |"
        lines.append(line)
    write_gates(fixture, "\n".join(lines))
    proc = run_validator(fixture, *layout)
    assert proc.returncode == 1 and "| high | d-identity:" in proc.stdout, proc.stdout
    write(fixture / "state" / "owner-decisions.jsonl", json.dumps(
        {"name": "identity may drift this round", "status": "decided", "blocks": [],
         "version": "0.6.0", "summary": "s", "covers": ["d-identity"]}) + "\n")
    proc = run_validator(fixture, *layout)
    assert "| low | d-identity:" in proc.stdout, proc.stdout


def test_the_shipped_domain_result_contract_is_the_validators() -> None:
    shipped = CORPUS_CANON.parent / "05-contracts" / "domain-result.schema.json"
    assert json.loads(shipped.read_text(encoding="utf-8")) == validator.DOMAIN_RESULT_SCHEMA


def test_a_domain_gate_in_the_perturbations_is_a_tool_failure(fixture: Path, tmp_path: Path,
                                                              monkeypatch) -> None:
    """Seat 7, C2: a perturbation of d-identity came out MISSED (exit 1)."""
    pert = sensitivity.Perturbation("domain", "10-doc1.md", "items", "things", "d-identity")
    code, _ = run_sensitivity(fixture, tmp_path, monkeypatch, [pert])
    assert code == sensitivity.EXIT_TOOL_FAILURE


# The ledgers (CR5 and CR6 of the panel): a hash chain from the first new
# line on, and the rules of a chained line of the round record.

CHAINED_ARTIFACTS = ARTIFACTS + (
    "| `round-record` | `state/round-record.jsonl` | verifier | — | the contract in "
    "`05-contracts/round-record.schema.json` | `p-contract-shape` |\n")
CORPUS_ROUND_SCHEMA = CORPUS_CANON.parent / "05-contracts" / "round-record.schema.json"
OLD_LINE = {"method_version": "0.1.0", "round": "v0.1", "summary": "old",
            "models": [{"role": "coder", "model": "family A"}]}


def ledger_fixture(tmp_path: Path, new: dict) -> Path:
    fixture = build_fixture(tmp_path, artifacts=CHAINED_ARTIFACTS)
    write_gates(fixture, GATES.replace("`notes-ledger`, `registry` |",
                                       "`notes-ledger`, `registry`, `round-record` |"))
    write(fixture / "05-contracts" / "round-record.schema.json",
          CORPUS_ROUND_SCHEMA.read_text(encoding="utf-8"))
    write(fixture / "01-canon.md", (fixture / "01-canon.md").read_text(encoding="utf-8") +
          "\n### Chained ledgers\n\n| Ledger | Lines before the chain |\n| --- | --- |\n"
          "| `state/round-record.jsonl` | 1 |\n")
    old = json.dumps(OLD_LINE)
    line = dict(new, prev=validator.chain_prev([old], 1))
    write(fixture / "state" / "round-record.jsonl", old + "\n" + json.dumps(line) + "\n")
    return fixture


NEW_LINE = {"method_version": "0.6.0", "round": "v0.6.0", "summary": "new", "kind": "maintenance",
            "reviewer_relation": "same family, separate session",
            "models": [{"role": "reviewer", "model": "family B"}],
            "family_map_commitment": "c" * 64}


def test_an_old_ledger_line_edited_breaks_the_chain(tmp_path: Path) -> None:
    """Probe P01 of the integrity seat: an old line of the round record
    rewritten, and another deleted, gave no note."""
    fixture = ledger_fixture(tmp_path, NEW_LINE)
    assert "| `state/round-record.jsonl` | `p-contract-shape` | 2 lines, 0 violations" \
        in run_validator(fixture).stdout
    path = fixture / "state" / "round-record.jsonl"
    path.write_text(path.read_text(encoding="utf-8").replace('"old"', '"rewritten"'), encoding="utf-8")
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "'prev' is not the sha256 of the ledger above it" in proc.stdout


def test_an_unchained_line_after_the_declared_ones_is_a_finding(tmp_path: Path) -> None:
    fixture = ledger_fixture(tmp_path, NEW_LINE)
    path = fixture / "state" / "round-record.jsonl"
    path.write_text(path.read_text(encoding="utf-8") + json.dumps(OLD_LINE) + "\n", encoding="utf-8")
    proc = run_validator(fixture)
    assert proc.returncode == 1
    assert "line 3 carries no 'prev'" in proc.stdout


@pytest.mark.parametrize("change, hit", [
    ({"kind": "review"}, "'kind' is 'review'"),
    ({"reviewer_relation": None}, "names its 'reviewer_relation'"),
    ({"verdict": "accepted"}, "a maintenance round emits none"),
    ({"rubric_applied": True, "rubric_hash": "0" * 64}, "'rubric_applied' is true"),
    ({"family_map_commitment": None}, "carries 'family_map_commitment'"),
    ({"family_map_commitment": "not a sha"}, "carries 'family_map_commitment'")])
def test_the_rules_of_a_chained_round_line(tmp_path: Path, change: dict, hit: str) -> None:
    """CR6 (the mechanical part) and recommendations 2 and 3: kind, the
    reviewer's relation, no verdict in a maintenance round, and the rubric
    hash of a line that says it applied the rubric."""
    line = {k: v for k, v in dict(NEW_LINE, **change).items() if v is not None}
    proc = run_validator(ledger_fixture(tmp_path, line))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert hit in proc.stdout


def test_a_rubric_the_producer_wrote_and_applied_is_a_low_note() -> None:
    """Rework of v0.6.0: a verdict under the producer's own rubric was
    recorded and said nothing; it is a low note now, and only when applied."""
    line = dict(NEW_LINE, rubric_applied=True, rubric_author="producer")
    assert validator.round_line_advisories(line) == ["round v0.6.0: rubric written by the producer"]
    assert validator.round_line_advisories(dict(line, rubric_applied=False)) == []
    assert validator.round_line_advisories(dict(line, rubric_author="owner")) == []


def test_the_family_map_commitment_has_a_canonical_form() -> None:
    """Rework of v0.6.0 (CR5): the commitment is reproducible by whoever
    holds map and salt, and its form is all the validator reads."""
    family_map, salt = {"A": "first family", "B": "second family"}, "5" * 64
    payload = json.dumps(family_map, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256((payload + "\n" + salt).encode("utf-8")).hexdigest()
    assert validator.round_line_hits(dict(NEW_LINE, family_map_commitment=digest),
                                     lambda: "") == []
    assert any("family_map_commitment" in hit for hit in validator.round_line_hits(
        dict(NEW_LINE, family_map_commitment=digest.upper()), lambda: ""))


def test_a_restated_status_line_is_chained_and_the_last_one_counts() -> None:
    old = '{"ref": "notes:1", "status": "open", "summary": "x"}'
    new = json.dumps({"ref": "notes:1", "status": "fixed", "closed_in": "0.6.0", "summary": "x",
                      "prev": validator.chain_prev([old], 1)})
    counts, hits = validator.notes_status_hits(old + "\n" + new + "\n", 1)
    assert hits == [] and counts["fixed"] == 1 and counts["open"] == 0
    counts, hits = validator.notes_status_hits(old + "\n" + old + "\n", 1)
    assert "line 2: ref 'notes:1' appears twice" in hits


# The labels (CR5, first half).

def test_an_executed_experiment_without_provenance_reads_as_a_hypothesis(tmp_path: Path) -> None:
    """Probe L1: 'executed' is a word the producer writes; without the
    provenance table the label is a note."""
    claim = DOC1 + "\nThe review pays off here [experiment:E1].\n"
    fixture = fixture_with_gates(tmp_path, ["p-efficacy-mark"], doc1=claim)
    write(fixture / "60-experiments.md", EXPERIMENTS_RECORD.replace(PROVENANCE_TABLE, ""))
    proc = run_validator(fixture)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "cites an executed experiment with no provenance table" in proc.stdout


def test_a_lessons_label_names_an_entry_that_exists(tmp_path: Path) -> None:
    claim = DOC1 + "\nThe review pays off here [lessons:The first round].\n"
    fixture = fixture_with_gates(tmp_path, ["p-efficacy-mark"], doc1=claim)
    write(fixture / "99-lessons.md", "# Lessons\n\n## The first round\n\nIt taught.\n")
    write(fixture / "01-canon.md", (fixture / "01-canon.md").read_text(encoding="utf-8").replace(
        "| `60-experiments.md` |", "| `99-lessons.md` | the lessons |\n| `60-experiments.md` |"))
    assert run_validator(fixture).returncode == EXIT_PENDING
    write(fixture / "10-doc1.md", claim.replace("The first round", "A round that never was"))
    proc = run_validator(fixture)
    assert proc.returncode == 1
    assert "[lessons:A round that never was] names no entry" in proc.stdout
    write(fixture / "10-doc1.md", claim.replace("[lessons:The first round]", "[lessons]"))
    assert "a bare [lessons] names no entry" in run_validator(fixture).stdout


def test_a_numeric_hypothesis_is_a_low_note_and_keeps_the_exit(tmp_path: Path) -> None:
    claim = DOC1 + "\nThe review pays off in every round [hypothesis].\n"
    fixture = fixture_with_gates(tmp_path, ["p-efficacy-mark"], doc1=claim)
    proc = run_validator(fixture)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `10-doc1.md` | `p-efficacy-mark` | 0, 1 advisory | 0 | pass |" in proc.stdout
    assert "| low | p-efficacy-mark: line 7: a [hypothesis] claim" in proc.stdout


# The section commitments of a prior (recommendation 4).

def commitment_canon(fixture: Path, digest: str) -> None:
    write(fixture / "01-canon.md", CANON + CANON_FACTS +
          "\n### Section commitments\n\n| Prior | Section | sha256 |\n| --- | --- | --- |\n"
          f"| `[prior:000-fixture]` | 1 | `{digest}` |\n")


def test_a_rewritten_section_of_a_prior_breaks_its_commitment(fixture: Path) -> None:
    """Recommendation 4: the canon commits to the sha256 of each cited section
    of the owner-held prior; p-prior on the canon compares them."""
    write_gates(fixture, GATES.replace("| `p-prior` | `doc1` |", "| `p-prior` | `canon`, `doc1` |"))
    good = validator.section_digests(PRIOR_DOC)["1"]
    commitment_canon(fixture, good)
    case = ("--case", str(fixture.parent / "prior-method.md"))
    assert "1 section commitments checked, 0 broken | 0 | pass |" in run_validator(fixture, *case).stdout
    commitment_canon(fixture, "f" * 64)
    proc = run_validator(fixture, *case)
    assert proc.returncode == 1
    assert "section 1 of the method document of '000-fixture' does not match" in proc.stdout
    proc = run_validator(fixture)
    assert "000-fixture: owner-held evidence, not measured here" in proc.stdout


# The sensitivity test (CR2): the copy, the specificity, the prior per row.

def test_the_sensitivity_copy_holds_the_documents_above_the_folder(tmp_path: Path,
                                                                   monkeypatch) -> None:
    """Seat 3, C1: the copy was the folder alone, so a perturbation could
    not reach a document above it and every perturbed run lost them."""
    artifacts = ARTIFACTS + "| `outside` | `../prior-method.md` | writer | — | free text | `p-form` |\n"
    fixture = build_fixture(tmp_path, artifacts=artifacts)
    write_gates(fixture, GATES.replace("\n### Size ranges",
                                       "| `p-form` | `outside` | HTML | 0 | [method] form rules "
                                       "apply to every document |\n\n### Size ranges"))
    pert = sensitivity.Perturbation("tag above", "../prior-method.md", "# Prior method document",
                                    "# Prior <b>method</b> document", "p-form")
    code, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert])
    assert row_result(report, "tag above") == "caught", report
    assert "Noisy: 0 of 1." in report and code == sensitivity.EXIT_OK


def test_a_perturbation_that_changes_another_row_is_noisy() -> None:
    base = {("a.md", "p-form"): frozenset({"pass"}), ("a.md", "p-terms"): frozenset({"pass"})}
    hit = {("a.md", "p-form"): frozenset({"fail"}), ("a.md", "p-terms"): frozenset({"fail"})}
    pert = sensitivity.Perturbation("x", "a.md", "o", "n", "p-form")
    assert sensitivity.noisy_rows(base, hit, pert) == ["`a.md` `p-terms`"]
    declared = sensitivity.Perturbation("x", "a.md", "o", "n", "p-form", also="p-terms")
    assert sensitivity.noisy_rows(base, hit, declared) == []


def test_the_synthetic_row_of_the_report_is_no_noise() -> None:
    """Rework of v0.6.0: with only the document of 004, the perturbation of
    its pin made the recorded case read as synthetic, and the renamed row of
    p-sensitivity counted as noise of another gate."""
    sens = ("80-validator/sensitivity.md", validator.SENSITIVITY_GATE)
    synth = ("80-validator/sensitivity.md", validator.SYNTHETIC_GATE)
    base = {sens: frozenset({"pass"}), ("r.json", "p-prior-pin"): frozenset({"pending"})}
    hit = {synth: frozenset({"pending"}), ("r.json", "p-prior-pin"): frozenset({"fail"})}
    pert = sensitivity.Perturbation("pin", "r.json", "o", "n", "p-prior-pin")
    assert sensitivity.noisy_rows(base, hit, pert) == []


def test_a_row_of_a_prior_not_passed_is_not_measured(tmp_path: Path, monkeypatch) -> None:
    """S5: with only another prior's document, the rows of the first prior
    came out MISSED; they are not measured, by prior."""
    fixture = build_fixture(tmp_path)
    pert = sensitivity.Perturbation("number", "10-doc1.md", "gave 49", "gave 48", "p-prior",
                                    needs_case=True, prior="000-other")
    _, report = run_sensitivity(fixture, tmp_path, monkeypatch, [pert],
                                "--case", str(tmp_path / "prior-method.md"))
    assert row_result(report, "number") == "not measured"


CELL_004 = CORPUS_CANON.parents[1] / "instances" / "004-adoption-guide"


def test_the_validator_of_the_cell_004_runs_only_as_a_record() -> None:
    """Probe C004 and CR7: the cell distributed under 0.2.2 ran with the
    semantics later versions corrected (exit 0 with pending gates). Its copy
    refuses to run without --historical, and its errata sit beside the guide."""
    script = CELL_004 / "08-validator" / "validator.py"
    proc = subprocess.run([sys.executable, "-B", str(script), "--folder", str(CELL_004),
                           "--layout", str(CELL_004 / "layout.json")],
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 2
    assert "--historical" in proc.stderr
    assert (CELL_004 / "ERRATA.md").is_file()


def test_a_perturbation_name_with_a_comma_is_refused() -> None:
    with pytest.raises(sensitivity.PerturbationDataError, match="no comma"):
        sensitivity.perturbation_from({"name": "a, b", "document": "x", "old": "o", "new": "n",
                                       "gate": "p-form"}, 0, "f.json")


# ------------------------------- v0.6.0, second pass (the findings left open)

@pytest.mark.parametrize("sample", ["29 de outubro de 2026", "2026/10/29", "\\\\server\\share",
                                    "mail me at someone@example.com", "node01.cluster.local"])
def test_anonymity_reads_the_forms_the_second_pass_added(sample: str) -> None:
    """IM12: dates in Portuguese and year first, UNC paths, e-mail addresses
    and host names under a private suffix passed the gate."""
    assert validator.anonymity_hits(f"See {sample} for it.", []) != []


def test_an_interpreter_line_and_an_accepted_path_are_not_read() -> None:
    """IM12, the valve: '#!' on line 1, and a path the canon accepts for one
    document, are declared false positives; the same path elsewhere fails."""
    accepted = ("/usr/share/doc",)
    text = "#!/usr/bin/env python3\nsee /usr/share/doc here\n"
    assert validator.anonymity_hits(validator.anonymity_scope(text), [], accepted) == []
    assert validator.anonymity_hits(validator.anonymity_scope(text), []) != []


def test_an_accepted_entry_hides_no_identifier_and_no_date() -> None:
    """Rework of v0.6.0: the valve blanked any text it listed, so a forbidden
    word or a date listed as 'accepted' vanished before every check; only a
    path equal to the match is dropped now, and a non-path entry is refused."""
    text = "built by Zorblaxian on 2026-10-29 under /usr/share/doc\n"
    hits = validator.anonymity_hits(text, ["Zorblaxian"], ("/usr/share/doc",))
    assert any("forbidden" in h for h in hits) and any("date" in h for h in hits)
    assert not any("absolute path" in h for h in hits)
    for entry in ("Zorblaxian", "2026-10-29", "/usr/share/doc and more"):
        table = ("### Accepted paths\n\n| Document | Path | Why it is accepted |\n| --- | --- | --- |\n"
                 f"| `a.md` | `{entry}` | quoted |\n")
        with pytest.raises(validator.InputError, match="is a path, nothing else"):
            validator.load_accepted_paths(table)


def test_an_accepted_path_at_the_end_of_a_sentence_is_accepted() -> None:
    """Closing pass of v0.6.0 (the re-review's N5b): the match took the
    final period, and the comparison by equality failed (a false red)."""
    hits = validator.anonymity_hits("See /usr/share/doc. And /usr/share/doc, too.\n", [],
                                    ("/usr/share/doc",))
    assert hits == []


def test_the_canon_cannot_accept_a_path_for_itself(fixture: Path) -> None:
    """Rework of v0.6.0: the canon declares what is accepted, so a row
    accepting a path in the canon itself is a tool failure (exit 2)."""
    canon = fixture / "01-canon.md"
    write(canon, canon.read_text(encoding="utf-8") + "\n### Accepted paths\n\n| Document | Path | Why it is accepted |\n"
          "| --- | --- | --- |\n| `01-canon.md` | `/usr/share/doc` | quoted |\n")
    proc = run_validator(fixture)
    assert proc.returncode == validator.EXIT_TOOL_FAILURE, proc.stdout + proc.stderr
    assert "names the canon itself" in proc.stderr


@pytest.mark.parametrize("sample", ["29 octobre 2026", "29. Oktober 2026", "29 ottobre 2026",
                                    "1 d\u00e9cembre 2025", "M\u00e4rz 3, 2026"])
def test_dates_in_french_german_and_italian_are_read(sample: str) -> None:
    """Rework of v0.6.0 (IM12): the months of three more languages."""
    assert validator.anonymity_hits(f"Done {sample}.", []) != []


DUTCH = ("### Month names\n\n| Language | Months |\n| --- | --- |\n| nl | "
         + ", ".join(f"`{m}`" for m in "januari februari maart april mei juni juli augustus "
                     "september oktober november december".split()) + " |\n")


def test_the_canon_adds_the_months_of_another_language_and_one_segment_roots() -> None:
    """Rework of v0.6.0 (IM12): a language without built-in months needs the
    canon's list; a root of one segment is read when the canon names it."""
    text = "Done 3 maart 2026 under /scr01 and /scr01/x.\n"
    assert not any("date" in h for h in validator.anonymity_hits(text, []))
    assert not any("'/scr01'" in h for h in validator.anonymity_hits(text, []))
    roots = "### Machine roots\n\n| Root | Why |\n| --- | --- |\n| `/scr01` | local scratch |\n"
    tables = validator.load_anonymity_tables(DUTCH + "\n" + roots)
    hits = validator.anonymity_hits(text, [], (), validator.canon_anonymity_patterns(tables))
    assert "date '3 maart 2026'" in hits and "absolute path '/scr01'" in hits
    with pytest.raises(validator.InputError, match="one segment"):
        validator.load_anonymity_tables(roots.replace("`/scr01`", "`scr01 x`"))


def test_a_brief_language_without_month_names_is_pending(fixture: Path) -> None:
    """Rework of v0.6.0 (IM12): the brief declares its languages; one the
    validator cannot read the dates of is pending by name, never a pass."""
    brief_with_ids(fixture)
    write(fixture / "00-brief.md", "# Brief\n\nLanguages: en, nl\n")
    proc = run_validator(fixture, "--allow-pending", "p-anonymity,p-prior,p-prior-pin")
    assert "| `00-brief.md` | `p-anonymity-language` | dates in nl not measured" in proc.stdout, \
        proc.stdout
    # Closing pass of v0.6.0: accepting p-anonymity does not accept it.
    assert proc.returncode == EXIT_PENDING, proc.stdout
    assert re.search(r"^Pending not accepted: .*`p-anonymity-language` \(1 row\)", proc.stdout, re.M)
    proc = run_validator(fixture, "--allow-pending", "p-anonymity-language")
    assert proc.returncode == validator.EXIT_TOOL_FAILURE
    canon = fixture / "01-canon.md"
    write(canon, canon.read_text(encoding="utf-8") + "\n" + DUTCH)
    assert "dates in nl not measured" not in run_validator(fixture).stdout
    write(fixture / "00-brief.md", "# Brief\n\nLanguages: Dutch\n")
    proc = run_validator(fixture)
    assert proc.returncode == validator.EXIT_TOOL_FAILURE and "two-letter codes" in proc.stderr


def test_a_forbidden_identifier_listed_by_its_sha256_is_found() -> None:
    """IM12: the list can measure without containing what it forbids."""
    entry = "sha256:" + hashlib.sha256(b"hostx").hexdigest()
    assert validator.forbidden_hits("ran on HostX.", [entry]) != []
    assert validator.forbidden_hits("ran on another.", [entry]) == []


def status_fixture(fixture: Path, *lines: dict) -> tuple[str, ...]:
    """A fixture with a state ledger of the given lines, run with --notes."""
    write(fixture / "state" / "notes-status.jsonl",
          '{"ref": "notes:1", "status": "open", "summary": "a legacy note"}\n'
          + "".join(json.dumps(line) + "\n" for line in lines))
    return ("--notes", str(fixture / "90-notes" / "notes.json"))


def test_an_escaped_regression_closes_with_a_gate_or_a_reason(fixture: Path) -> None:
    """IM6, golden rule 4: an escaped regression closed with neither is a finding."""
    line = {"ref": "panel:0.5.0:CR9", "status": "fixed", "closed_in": "0.6.0", "summary": "x",
            "escaped": True}
    proc = run_validator(fixture, *status_fixture(fixture, line))
    assert proc.returncode == 1 and "an escaped regression closed with neither" in proc.stdout
    for extra in ({"gate": "p-prior"},
                  {"no_gate": "the rule moved into the contract of the notes, read there"}):
        proc = run_validator(fixture, *status_fixture(fixture, dict(line, **extra)))
        assert "an escaped regression" not in proc.stdout, proc.stdout


@pytest.mark.parametrize("extra", [{"gate": "d-does-not-exist"}, {"no_gate": "x"},
                                   {"no_gate": "see the owner"},
                                   {"no_gate": "x x x x x x x x"}])
def test_an_escape_closed_with_an_undeclared_gate_or_a_token_reason_is_a_finding(
        fixture: Path, extra: dict) -> None:
    """Rework of v0.6.0 (the review's N1, N1b): any name of a domain gate,
    even one no table declares, and a one-word reason closed golden rule 4."""
    line = {"ref": "panel:0.5.0:CR9", "status": "fixed", "closed_in": "0.6.0", "summary": "x",
            "escaped": True, **extra}
    proc = run_validator(fixture, *status_fixture(fixture, line))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "an escaped regression closed with neither a gate of the gate table" in proc.stdout


def test_an_escape_closed_by_a_decided_owner_decision_is_accepted(fixture: Path) -> None:
    """Rework of v0.6.0: a short reason counts when its 'decision' names a
    decided owner decision exactly; reopened, the decision no longer counts."""
    line = {"ref": "panel:0.5.0:CR9", "status": "fixed", "closed_in": "0.6.0", "summary": "x",
            "escaped": True, "no_gate": "see the decision", "decision": "keep it manual"}
    decision = {"name": "keep it manual", "status": "decided", "blocks": [], "version": "0.6.0",
                "summary": "s"}
    write(fixture / "state" / "owner-decisions.jsonl", json.dumps(decision) + "\n")
    proc = run_validator(fixture, *status_fixture(fixture, line))
    assert "an escaped regression" not in proc.stdout, proc.stdout
    write(fixture / "state" / "owner-decisions.jsonl", json.dumps(decision) + "\n"
          + json.dumps(dict(decision, status="open")) + "\n")
    proc = run_validator(fixture, *status_fixture(fixture, line))
    assert "an escaped regression closed with neither" in proc.stdout


def test_an_old_open_note_is_a_low_note_until_scheduled(fixture: Path) -> None:
    """IM11: the age of a note is counted in rounds of the round record."""
    rounds = "".join(json.dumps({"method_version": f"0.{k}.0", "round": f"v0.{k}", "summary": "r",
                                 "models": []}) + "\n" for k in range(2, 8))
    write(fixture / "state" / "round-record.jsonl", rounds)
    proc = run_validator(fixture, *status_fixture(fixture))
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "notes:1 has been open for 6 rounds" in proc.stdout and "| low |" in proc.stdout
    due = {"ref": "notes:1", "status": "open", "summary": "scheduled", "due": "0.9.0",
           "prev": validator.chain_prev(['{"ref": "notes:1", "status": "open", "summary": '
                                         '"a legacy note"}'], 1)}
    proc = run_validator(fixture, *status_fixture(fixture, due))
    assert "has been open for" not in proc.stdout, proc.stdout


def brief_with_ids(fixture: Path) -> None:
    write(fixture / "00-brief.md", "# Brief\n\n## Non-negotiables\n\n- `nn-identity`: results "
          "are identical.\n")
    write(fixture / "01-canon.md", (fixture / "01-canon.md").read_text(encoding="utf-8").replace(
        "| `60-experiments.md` |", "| `00-brief.md` | the brief |\n| `60-experiments.md` |"))


def test_an_open_high_note_on_a_non_negotiable_is_blocking_unless_decided(fixture: Path) -> None:
    """IM16: the stop accepted an open high note on a non-negotiable."""
    brief_with_ids(fixture)
    line = {"ref": "panel:0.6.0:IM99", "status": "open", "summary": "x", "severity": "high",
            "affects": ["nn-identity"]}
    proc = run_validator(fixture, *status_fixture(fixture, line))
    assert proc.returncode == 1 and "unprotected non-negotiable" in proc.stdout
    assert "| blocking | p-notes:" in proc.stdout
    write(fixture / "state" / "owner-decisions.jsonl", json.dumps(
        {"name": "ship with it", "status": "decided", "blocks": [], "version": "0.6.0",
         "summary": "s", "covers": ["panel:0.6.0:IM99"]}) + "\n")
    proc = run_validator(fixture, *status_fixture(fixture, line))
    assert "unprotected non-negotiable" not in proc.stdout, proc.stdout
    proc = run_validator(fixture, *status_fixture(fixture, dict(line, affects=["nn-speed"])))
    assert "affects 'nn-speed', which is no non-negotiable of the brief" in proc.stdout


@pytest.mark.parametrize("name, line_extra", [("", {"no_gate": "x"}),
                                              ("keep", {"no_gate": "keep it manual"}),
                                              ("keep it manual", {"no_gate": "x",
                                                                  "decision": "keep it"})])
def test_a_decision_counts_only_by_its_exact_name(fixture: Path, name: str,
                                                   line_extra: dict) -> None:
    """Closing pass of v0.6.0 (the re-review's N1e): a decided decision with
    an empty name, or one whose name was a substring of the reason, closed
    golden rule 4 with any reason."""
    line = {"ref": "panel:0.5.0:CR9", "status": "fixed", "closed_in": "0.6.0", "summary": "x",
            "escaped": True, **line_extra}
    write(fixture / "state" / "owner-decisions.jsonl", json.dumps(
        {"name": name, "status": "decided", "blocks": [], "version": "0.6.0", "summary": "s"}) + "\n")
    proc = run_validator(fixture, *status_fixture(fixture, line))
    assert "an escaped regression closed with neither" in proc.stdout, proc.stdout


def test_a_later_line_cannot_lower_the_severity_of_a_protected_note(fixture: Path) -> None:
    """Rework of v0.6.0 (the review's N2b): a later line of the same ref with
    'severity': 'medium', or without 'affects', unprotected the note."""
    brief_with_ids(fixture)
    line = {"ref": "panel:0.6.0:IM99", "status": "open", "summary": "x", "severity": "high",
            "affects": ["nn-identity"]}
    for later in ({"severity": "medium"}, {"affects": []}, {}):
        relined = {k: v for k, v in line.items() if k not in ("severity", "affects")} | later
        proc = run_validator(fixture, *status_fixture(fixture, line, relined))
        assert proc.returncode == 1 and "unprotected non-negotiable" in proc.stdout, later


def test_a_reopened_owner_decision_no_longer_covers_its_notes(fixture: Path) -> None:
    """Rework of v0.6.0 (the review's N2d): 'covered' read any 'decided' line
    of a decision, not its last one."""
    brief_with_ids(fixture)
    line = {"ref": "panel:0.6.0:IM99", "status": "open", "summary": "x", "severity": "high",
            "affects": ["nn-identity"]}
    decision = {"name": "ship with it", "status": "decided", "blocks": [], "version": "0.6.0",
                "summary": "s", "covers": ["panel:0.6.0:IM99"]}
    write(fixture / "state" / "owner-decisions.jsonl", json.dumps(decision) + "\n"
          + json.dumps(dict(decision, status="open")) + "\n")
    proc = run_validator(fixture, *status_fixture(fixture, line))
    assert proc.returncode == 1 and "unprotected non-negotiable" in proc.stdout


def test_a_new_high_note_names_what_it_affects(fixture: Path) -> None:
    """Rework of v0.6.0 (the review's N2e): without 'affects' a high note was
    never blocking; a note opened since 0.6.0 names it, an empty list when
    none, and an older one is not required to."""
    line = {"ref": "panel:0.6.0:IM99", "status": "open", "summary": "x", "severity": "high"}
    proc = run_validator(fixture, *status_fixture(fixture, line))
    assert "names the non-negotiables it affects" in proc.stdout, proc.stdout
    proc = run_validator(fixture, *status_fixture(fixture, dict(line, affects=[])))
    assert "names the non-negotiables it affects" not in proc.stdout
    proc = run_validator(fixture, *status_fixture(fixture, dict(line, ref="panel:0.5.0:IM99")))
    assert "names the non-negotiables it affects" not in proc.stdout


def test_evidence_that_names_a_missing_file_is_a_finding(fixture: Path) -> None:
    """IM16: a note's evidence named a log that did not exist, and passed."""
    notes = fixture / "open-notes.json"
    write(notes, json.dumps([dict(NOTES[0], evidence="10-doc1.md and logs/run.log.md")]))
    write(fixture / "state" / "notes-status.jsonl",
          '{"ref": "notes:1", "status": "open", "summary": "x"}\n')
    write(fixture / "01-canon.md", (fixture / "01-canon.md").read_text(encoding="utf-8"))
    proc = run_validator(fixture, "--notes", str(notes))
    assert "evidence names 'logs/run.log.md', which does not exist" in proc.stdout
    assert "'10-doc1.md'" not in proc.stdout


def test_the_version_label_fills_the_paths_and_commands_are_resolved(tmp_path: Path) -> None:
    """IM8: the command of the graph was inert data and the graph had no
    version; '{version}' takes the layout's label, and every path a command
    names has to exist (it is never run)."""
    arts = {"a": validator.Artifact("a", ["{version}/out.md"], "writer", [],
                                    command="python3 tools/make.py --out {version}/out.md")}
    validator.with_version(arts, "v2")
    assert arts["a"].files == ["v2/out.md"]
    write(tmp_path / "tools" / "make.py", "")
    assert validator.command_hits(arts, tmp_path) == [
        "artifact 'a': its command names `v2/out.md`, which does not exist"]
    write(tmp_path / "v2" / "out.md", "")
    assert validator.command_hits(arts, tmp_path) == []
    with pytest.raises(validator.InputError, match="version-label"):
        validator.with_version({"b": validator.Artifact("b", ["{version}/x.md"], "w", [])}, None)


def test_a_repeated_key_in_a_jsonl_line_is_a_finding() -> None:
    """SUG9: the last value of a repeated key won in silence."""
    hits = validator.validate_data_text('{"a": 1, "a": 2}', {"type": "object"}, "line 1")
    assert hits == ["line 1: key 'a' appears twice in one object"]


def test_p_size_does_not_count_the_pipes_of_a_table(fixture: Path) -> None:
    """SUG11: every pipe and separator of a table counted as a word."""
    write(fixture / "10-doc1.md", DOC1 + "\n| a | b |\n| --- | --- |\n| c | d |\n")
    write_gates(fixture, GATES.replace("| `p-terms` | `doc1` |", "| `p-size` | `doc1` | words | "
                                       "within the range | [method] the reader reads it all |\n"
                                       "| `p-terms` | `doc1` |"))
    words = len(DOC1.split()) + 4
    assert f"| `10-doc1.md` | `p-size` | {words} |" in run_validator(fixture).stdout


def test_against_labels_counter_evidence(tmp_path: Path) -> None:
    """SUG2: a claim may carry the experiment whose result goes against it."""
    claim = DOC1 + "\nThe review pays off here [against:E1].\n"
    fixture = fixture_with_gates(tmp_path, ["p-efficacy-mark"], doc1=claim)
    write(fixture / "60-experiments.md", EXPERIMENTS_RECORD)
    assert run_validator(fixture).returncode == EXIT_PENDING
    write(fixture / "10-doc1.md", claim.replace("E1", "E2"))
    assert "cites a designed experiment" in run_validator(fixture).stdout


def test_the_report_records_the_self_test_and_the_suite_it_was_made_with(fixture: Path) -> None:
    """SUG3: the report did not say which instrument tests stood behind it."""
    proc = run_validator(fixture)
    digest = validator.content_digest(Path(__file__).resolve())
    assert f"checks passed. Test suite sha256: {digest}." in proc.stdout


def test_a_frozen_record_rewritten_is_blocking(fixture: Path) -> None:
    """CR5 and SUG22: the reviewer's verdict could be rewritten unseen."""
    write(fixture / "80-validator" / "verdict.md", "Rejected.\n")
    digest = validator.sha256_text("Rejected.\n")
    write(fixture / "01-canon.md", (fixture / "01-canon.md").read_text(encoding="utf-8") +
          f"\n### Frozen records\n\n| Record | sha256 | Frozen part |\n| --- | --- | --- |\n"
          f"| `80-validator/verdict.md` | `{digest}` | the whole file |\n")
    assert "| `80-validator/verdict.md` | `p-frozen-rubric` | equal |" in run_validator(fixture).stdout
    write(fixture / "80-validator" / "verdict.md", "Accepted.\n")
    proc = run_validator(fixture)
    assert proc.returncode == 1 and "the frozen record `80-validator/verdict.md` changed" in proc.stdout


def test_the_validator_reads_the_set_without_importing_the_sensitivity_script() -> None:
    """IM15: validator.py and sensitivity.py imported each other."""
    source = VALIDATOR.read_text(encoding="utf-8")
    assert "import sensitivity" not in source and "import perturbation_set" in source
    assert sensitivity.PERTURBATIONS is sensitivity.perturbation_set_module.PERTURBATIONS
    families = [c.__name__ for c in validator.Checker.__mro__[1:-1]]
    assert families == ["FormGates", "PriorGates", "ContractGates", "RecordGates",
                        "DomainGates", "CheckerCore"]


def test_a_synthetic_prior_carries_the_sections_and_numbers_of_its_facts(fixture: Path) -> None:
    """IM15: a clone has no document of an owner-held prior; the synthetic
    one holds each recorded number in its cited section, in the prior's
    number format, so the rows that need the prior can be measured."""
    text = sensitivity.synthetic_document(fixture, validator.DEFAULT_LAYOUT, "000-fixture",
                                          "point-decimal")
    sections = validator.case_sections(text)
    assert "49" in " ".join(sections["1"])
    comma = sensitivity.synthetic_document(fixture, validator.DEFAULT_LAYOUT, "000-fixture",
                                           "comma-decimal")
    assert "## 1 Section" in comma


def test_the_synthetic_prior_is_written_in_the_heading_style_of_the_real_document(
        fixture: Path) -> None:
    """Rework of v0.6.0 (the review's matR): the synthetic headings were
    '## <label> Section', so a reader that stopped reading 'Passo N' still
    passed on the synthetic; the registry's heading style is used now, and a
    reader without it misses the steps of the synthetic document too."""
    style = {"section": "## {label}.", "subsection": "### {label}", "step": "### Passo {label}."}
    canon = fixture / "01-canon.md"
    write(canon, canon.read_text(encoding="utf-8").replace("| section 1 |", "| step 15 |"))
    text = sensitivity.synthetic_document(fixture, validator.DEFAULT_LAYOUT, "000-fixture",
                                          "point-decimal", style)
    assert "### Passo 15. Section" in text
    assert "49" in " ".join(validator.case_sections(text)["15"])
    regressed = re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*)", re.M)
    assert "15" not in {m.group(1) for m in regressed.finditer(text)}


def sensitivity_report_with(folder: Path, cases: str) -> None:
    """A fixture report whose header records the given case documents."""
    write(folder / validator.DEFAULT_LAYOUT["artifacts"]["sensitivity"],
          "# Validator sensitivity\n\n" + valid_sensitivity_header(folder, cases=cases)
          + "\n\n" + FIXTURE_REPORT_MARK + "\n\n" + CAUGHT_ALL + "\n")


def test_a_report_without_its_case_documents_is_refused(fixture: Path) -> None:
    """Rework of v0.6.0 (the review's H1): nothing tied a report to the prior
    documents it was made with; a report that records none is refused."""
    sensitivity_report_with(fixture, "")
    proc = run_validator(fixture, sensitivity_report=False)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "the sensitivity report records no case document" in proc.stdout


def test_a_report_made_with_a_synthetic_prior_is_never_a_pass(fixture: Path, tmp_path: Path) -> None:
    """Rework of v0.6.0 (the review's H1, P24full): a report made with a
    synthetic prior, its marking line deleted, read as the owner's. The sha
    the header records differs from the registry's pin: in a clone run the
    row is pending under p-sensitivity-synthetic, accepted only by that name;
    with the owner's document passed it is refused."""
    synthetic = "case sha256: 000-fixture " + "e" * 64 + "\n"
    sensitivity_report_with(fixture, synthetic)
    proc = run_validator(fixture, sensitivity_report=False)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert "| `p-sensitivity-synthetic` | not measured against the owner's document" in proc.stdout
    assert "| `p-sensitivity` |" not in proc.stdout
    proc = run_validator(fixture, "--allow-pending", "p-sensitivity-synthetic,p-prior,p-prior-pin,"
                         "p-anonymity", sensitivity_report=False)
    assert "Pending accepted by the caller (--allow-pending): " in proc.stdout
    assert "`p-sensitivity-synthetic` (1 row)" in proc.stdout
    proc = run_validator(fixture, "--case", str(tmp_path / "prior-method.md"),
                         sensitivity_report=False)
    assert proc.returncode == 1
    assert "the report was made with a synthetic 000-fixture while its document was passed" \
        in proc.stdout
    real = validator.sha256_text((tmp_path / "prior-method.md").read_text(encoding="utf-8"))
    sensitivity_report_with(fixture, f"case sha256: 000-fixture {real}\n")
    proc = run_validator(fixture, sensitivity_report=False)
    assert "| `p-sensitivity` |" in proc.stdout and "p-sensitivity-synthetic" not in proc.stdout


def test_a_synthetic_report_below_the_pair_floor_is_not_accepted_by_name(fixture: Path) -> None:
    """Closing pass of v0.6.0 (the re-review's S1): the synthetic path
    returned before the floor of the pairs, so accepting
    p-sensitivity-synthetic took away a pending no name accepts."""
    low = CAUGHT_ALL.replace("Pairs covered: 1 of 1.", "Pairs covered: 1 of 100.")
    write(fixture / "80-validator" / "sensitivity.md", "# Validator sensitivity\n\n"
          + valid_sensitivity_header(fixture, cases="case sha256: 000-fixture " + "ab" * 32 + "\n")
          + "\n\n" + low + "\n")
    proc = run_validator(fixture, "--allow-pending",
                         "p-anonymity,p-prior,p-prior-pin,p-sensitivity-synthetic",
                         sensitivity_report=False)
    assert proc.returncode == EXIT_PENDING, proc.stdout + proc.stderr
    assert re.search(r"^Pending not accepted: .*`p-sensitivity` \(1 row\)", proc.stdout, re.M), \
        proc.stdout
    assert "fewer than 25 % of the (document, gate) pairs perturbed" in proc.stdout


def test_a_case_line_copied_from_the_registry_is_caught_with_the_document(
        fixture: Path, tmp_path: Path) -> None:
    """Closing pass of v0.6.0 (the re-review's P24 with a forged line): the
    pin is public, so a hand-written case line read as the owner's; the
    attestation hashes the document's text and only its holder computes it.
    Without the document the forged line still passes, as declared."""
    text = (tmp_path / "prior-method.md").read_text(encoding="utf-8")
    real = validator.sha256_text(text)
    digests = validator.provenance_inputs(fixture, validator.DEFAULT_LAYOUT)
    sha = validator.content_digest(Path(validator.__file__).resolve().with_name("validator.py"))
    case = tmp_path / "prior-method.md"
    for attestation, code in (("", 1), ("0" * 64, 1),
                              (validator.case_attestation(text, digests, sha), EXIT_PENDING)):
        line = f"case attestation: 000-fixture {attestation}\n" if attestation else ""
        sensitivity_report_with(fixture, f"case sha256: 000-fixture {real}\n{line}")
        proc = run_validator(fixture, "--case", str(case), "--allow-pending", "p-anonymity",
                             sensitivity_report=False)
        assert proc.returncode == code, (attestation, proc.stdout + proc.stderr)
        assert ("the report's attestation of 000-fixture does not match" in proc.stdout) \
            is (code == 1)
    sensitivity_report_with(fixture, f"case sha256: 000-fixture {real}\n")
    proc = run_validator(fixture, "--allow-pending", "p-anonymity,p-prior,p-prior-pin",
                         sensitivity_report=False)
    assert "| `p-sensitivity` |" in proc.stdout and "attestation" not in proc.stdout


def test_the_owner_decisions_ledger_is_a_chained_contract() -> None:
    """IM11: the owner's decisions are an artifact the validator reads."""
    schema = json.loads((CORPUS_CANON.parent / "05-contracts" / "owner-decisions.schema.json")
                        .read_text(encoding="utf-8"))
    lines = (CORPUS_CANON.parent / "state" / "owner-decisions.jsonl").read_text(
        encoding="utf-8").splitlines()
    assert lines and all(validator.validate_data_text(line, schema, "x") == [] for line in lines)
    entries = [json.loads(line) for line in lines]
    assert validator.chain_hits(lines, entries, 0) == []

