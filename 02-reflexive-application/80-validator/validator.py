#!/usr/bin/env python3
"""Validator for the reflexive-application production.

Reads the production canon (01-canon.md), the artifact list (02-artifacts.md)
and the gates (04-gates-and-rubric.md), then measures every gate on every
document the artifact list assigns it to. The artifact list is the one
source of the map from gate to artifact (v0.5.0); the Artifact column of the
gate table is checked against it under p-references. Lists and limits live
in those Markdown files only; this script keeps no copy of them.

The layout (which file holds which control document, which parser a gate
uses) can be remapped with --layout; the default is the markdown layout of
this corpus. The prior-instance registry and the prior method documents
(--case, repeatable: each one is identified by its sha256 in the registry)
are optional inputs. Without a registry, the prior gate is reported as
pending (not measured); with a registry but without a prior document, the
labels are measured and the numbers of that prior are not; without the
forbidden-identifier list, that part of the anonymity gate is pending. A
pending gate is neither a pass nor a fail. An input that cannot be read or
decoded as UTF-8, or a layout key this validator does not know, is a tool
failure (exit 2), never a finding.

Exit codes: 0 every gate measured and no high/blocking note; 1 at least one
high/blocking note; 2 invalid input or tool failure; 4 no such note, but a
gate was not measured (pending) and the caller did not accept it with
--allow-pending (v0.5.0: exit 0 used to mix "all passed" with "nothing was
measured"). The report is deterministic: no date, relative paths, sorted
output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from decimal import Decimal, InvalidOperation
from pathlib import Path

# No bytecode cache in the material (v0.4.2). This module imports the
# sensitivity script at run time (a local module, written next to it), and
# a -B on the caller's command line does not reach every run: the switch
# lives here, before that import, and every child process gets -B
# explicitly (python_command), since a child inherits neither.
sys.dont_write_bytecode = True
NO_BYTECODE_FLAG = "-B"

CANON_FILE = "01-canon.md"
ARTIFACTS_FILE = "02-artifacts.md"
GATES_FILE = "04-gates-and-rubric.md"
ROLES_DIR = "03-roles"
VALIDATOR_DIR = "80-validator"
REPORT_FILE = f"{VALIDATOR_DIR}/report.md"
# The corpus default of the layout key artifacts.sensitivity; a cell points
# it at its own sensitivity report (e.g. 08-validator/sensitivity.md).
SENSITIVITY_FILE = f"{VALIDATOR_DIR}/sensitivity.md"
# The sha256 recorded in the provenance header of a sensitivity report
# (v0.3.0, C3 of the panel): the gate refuses a report the running
# instrument cannot have produced.
SENSITIVITY_SHA_LINE = re.compile(r"^validator sha256: ([0-9a-f]{64})$", re.M)
SENSITIVITY_SET_LINE = re.compile(r"^perturbations: (\d+) \((.*)\)$", re.M)
# Since v0.5.0 (CR1 of the panel that reviewed v0.4.2) the provenance also
# pins the inputs that define what is measured: the gate section of the
# gates file and the canon. Deleting the gate table used to leave the report
# green, because only the validator's own sha was compared.
SENSITIVITY_INPUT_LINES = {
    "gates": re.compile(r"^gates sha256: ([0-9a-f]{64})$", re.M),
    "canon": re.compile(r"^canon sha256: ([0-9a-f]{64})$", re.M),
}
SENSITIVITY_ROW_RESULT = re.compile(r"^\|.*\| (caught|MISSED|not measured) \|$", re.M)
# The expected gate of a row of the report's table (the third cell).
SENSITIVITY_ROW_GATE = re.compile(
    r"^\| .+ \| `[^`]*` \| `([^`]+)` \| (?:caught|MISSED|not measured) \|$", re.M)
# Coverage per gate (M1 of the review of v0.5.0): every gate the artifact
# table assigns needs a perturbation, except p-sensitivity itself (its
# perturbation would be circular) and the measurements of the instrument.
SENSITIVITY_GATE = "p-sensitivity"
MEASUREMENT_PREFIX = "m-"
SENSITIVITY_LIMIT = "every gate covered, 0 missed"
GATES_HEADING = "## Gates"
RUBRIC_HEADING = "## Rubric"
# The placeholder a scaffolded cell ships in its rubric pin until the owner
# freezes the rubric for real: freezing replaces it, a real pin is refused.
RUBRIC_UNFROZEN = "not-frozen"
# The review ledger is frozen history: vocabulary rules apply to living
# documents, never retroactively to `90-review/` (exemption by design).
FROZEN_LEDGER_PREFIX = "90-review/"
PRIOR_TAG = re.compile(r"\[prior:([0-9a-z-]+)\]")
PRIOR_MARK = "[prior:"
# Headings of the prior method document that open a numbered section
# ("## 1.4 ..." / "### Passo 15 ..."); used by the section check of p-prior.
CASE_SECTION_HEADING = re.compile(r"^#{1,6}\s+(?:Passo\s+)?(\d+(?:\.\d+)*)", re.M)
SECTION_TOKEN = re.compile(r"\d+(?:\.\d+)*")
# The note ledger of the first round was frozen with the vocabulary of v0.1;
# its targets are mapped to the renamed artifacts instead of editing history.
ARTIFACT_ALIASES = {"bible": "canon"}
# [hypothesis] a gate that rejects more than this is better read from its
# magnitude than from a flood of notes; the number is the cap of the prior
# instance 000-av-production (section 1.4 of its method document), cited as
# support, not inherited as a limit. It only truncates the listing (an
# "omitted" note follows); it never decides a pass or a fail.
MAX_NOTES_PER_GATE = 50
# The numeric limits of p-limit and p-recipe are read from their rows of the
# gate table (IM16, v0.5.0): the script used to keep 6 and 12 as constants
# and print them whatever the table said.
MIN_WORDS_IN_ROW = re.compile(r"fewer than (\d+) words")
MIN_STEPS_IN_ROW = re.compile(r"≥\s*(\d+) steps")
# A placeholder left in a card field, a gate row, an instantiation cell or
# an artifact record (CR3, v0.5.0): '<fill in>' and any '<word ...>', or the
# markers TBD and TODO. Read outside code spans, where '<id>' is notation.
PLACEHOLDER = re.compile(r"<[A-Za-z][^<>\n]*>|\bTBD\b|\bTODO\b")
VALID_SEVERITIES = ("low", "medium", "high", "blocking")
BLOCKING = ("high", "blocking")
NOTE_FIELDS = ("target_artifact", "severity", "text", "origin", "evidence", "round")
OWNER_HUMAN = "owner"
NO_DEPENDENCY = {"\u2014", "-", ""}
AVOID_ALTERNATIVE_SEPARATOR = " / "
# Letters of Latin-1 count as word characters, so that an accented word is
# never split in two by a boundary (escapes keep the source plain ASCII).
WORD_CHARS = r"0-9A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF_"
EXIT_OK, EXIT_BLOCKING, EXIT_TOOL_FAILURE = 0, 1, 2
# A gate not measured that the caller did not accept with --allow-pending
# (IM15, v0.5.0): distinct from 1 (notes) and 2 (tool failure).
EXIT_PENDING = 4
REGISTRY_DEFAULT_REL = "../instances/registry.json"
# The registry path is resolved against the production folder (not the root
# that contains it), so the same spelling works in the corpus and in a cell.
# The default layout is this corpus's markdown layout; --layout overlays a
# file onto it (artifact names to paths, gate names to parsers).
PARSERS = ("builtin-markdown", "builtin-json-canon")
# Keywords the stdlib mini-validator applies; a schema that uses a keyword
# outside this set gets a note (the keyword is measured, never silently
# ignored as if fully validated).
SUPPORTED_KEYWORDS = frozenset(
    ("$schema", "$id", "title", "description", "type", "enum", "pattern",
     "required", "properties", "additionalProperties", "items", "minimum",
     "contract_version"))
# Every contract declares the version of its shape at its top level (IM21,
# v0.5.0), and this validator reads one version: a contract without it, or
# of another version, is a note of p-contract-shape, never read as if it
# were the shape the code expects.
CONTRACT_VERSION_KEY = "contract_version"
CONTRACT_VERSION = "1"
BUILTIN_GATES = ("p-terms", "p-canon-link", "p-anonymity", "p-form", "p-size",
                 "p-table", "p-sections", "p-card", "p-limit", "p-references",
                 "p-prior", "p-prior-mark", "p-prior-pin", "p-contract-shape",
                 "p-recipe", "p-components", "p-efficacy-mark")
# The gates measured once per run, not per document (check_global).
GLOBAL_GATES = ("p-notes", "p-frozen-rubric", "p-sensitivity", "p-declared")
# The record of the experiments about the method itself (v0.4.0): the
# [experiment:<id>] label of p-efficacy-mark cites an id registered there.
EXPERIMENTS_FILE = "60-experiments.md"
# The declared semantics of the gates (v0.4.1): the long prose split out of
# the gate table, so the gates file stays under its ceiling. No gate reads a
# table from it; it is measured as a document under the gates of its own
# artifact row. The key is known so that a cell may name its own.
GATE_SEMANTICS_FILE = "06-gate-semantics.md"
# The state of each note (IM10, v0.5.0): one JSON line per tracked note or
# panel finding, with its status and the version that closed it. The frozen
# ledger is never edited; its state lives here, and p-notes reads it.
NOTES_STATUS_FILE = "state/notes-status.jsonl"
NOTE_STATUSES = ("open", "fixed", "disputed", "out of scope")
# A reference to a note of the ledger passed with --notes ('notes:<n>',
# 1-based, the order of the file) or to a finding of a critical panel
# ('panel:<version>:<id>', e.g. 'panel:0.4.2:CR1').
STATUS_REF = re.compile(r"^(?:notes:([1-9]\d*)|panel:\d+\.\d+\.\d+:[A-Z]+\d+)$")
DEFAULT_LAYOUT: dict = {
    "version": 1,
    "artifacts": {
        "canon": CANON_FILE,
        "artifacts": ARTIFACTS_FILE,
        "gates-and-rubric": GATES_FILE,
        "roles-dir": ROLES_DIR,
        "sensitivity": SENSITIVITY_FILE,
        "experiments": EXPERIMENTS_FILE,
        "gate-semantics": GATE_SEMANTICS_FILE,
        "notes-status": NOTES_STATUS_FILE,
    },
    "gates": {gate: "builtin-markdown" for gate in BUILTIN_GATES},
    "registry": REGISTRY_DEFAULT_REL,
}
# The closed key sets of a layout file (I12 of the panel): a key this
# validator never reads is a typo until proven otherwise, so it is refused
# (exit 2) instead of silently falling back to the default it meant to
# override. 'rubric' and 'perturbations' are the artifact keys with no
# default: a cell names its dedicated rubric file, the corpus falls back to
# the gates file; a cell names the data file of its perturbations (v0.5.0),
# the corpus keeps its set in sensitivity.py.
LAYOUT_TOP_KEYS = ("version", "artifacts", "gates", "registry")
LAYOUT_ARTIFACT_KEYS = (*DEFAULT_LAYOUT["artifacts"], "rubric", "perturbations")
# The number formats a registered prior declares (I16 of the panel): a token
# of a prior method document has one value reading, in its own format. The
# documents of this production are point-decimal (form rule 1, English).
NUMBER_FORMATS = ("point-decimal", "comma-decimal")
DOCUMENT_NUMBER_FORMAT = "point-decimal"
FORMAT_SEPARATORS = {"point-decimal": (",", "."), "comma-decimal": (".", ",")}
# The labels that back a claim of efficacy about the method (I10): a prior,
# an experiment of the experiments record, the lessons of this application,
# or an explicit hypothesis.
EXPERIMENT_TAG = re.compile(r"\[experiment:([0-9A-Za-z-]+)\]")
EFFICACY_LABEL = re.compile(r"\[(?:prior:[0-9a-z-]+|experiment:[0-9A-Za-z-]+|lessons|hypothesis)\]")
# Every bracketed mark is removed before the numbers of a unit are read, so
# that the digits of an id ('000-...', 'E1') are never checked as numbers.
MARK_TAGS = re.compile(r"\[(?:prior|experiment):[0-9A-Za-z-]+\]")
# An experiment of the experiments record is a level-2 heading 'E<n> — ...'
# whose block declares its status, as a 'Status' row of its field table or a
# 'Status:' line (S4 of the v0.4.0 review: any heading word used to register
# an id, and a designed experiment backed a claim as well as an executed one).
EXPERIMENT_HEADING = re.compile(r"^##\s+(E\d+)\s+[—-]\s", re.M)
EXPERIMENT_STATUS = re.compile(r"^(?:\|\s*Status\s*\||Status:)\s*`?([a-z]+)", re.M)
LEVEL_TWO_HEADING = re.compile(r"^##\s", re.M)
EXECUTED = "executed"
# The contract of a registry entry by status (C16, v0.4.1): one list is the
# single source of instances, and the status decides the fields an entry
# carries. The mini-validator applies no if/then, so the rule lives here and
# is reported under p-contract-shape: an executed entry carries all four
# fields, a designed one none of them.
STATUS_FIELDS = ("document", "sha256", "locator", "number_format")
LOCATOR_OWNER_HELD = "owner-held, not distributable"
NON_RELATIVE_LOCATOR = re.compile(r"^(?:/|~|[A-Za-z]:[\\/]|[A-Za-z][A-Za-z0-9+.-]*://)")


class InputError(Exception):
    """Raised when an input file is missing or lacks a required structure."""


class SelfTestError(Exception):
    """Raised when a self-test case does not give the expected result."""


@dataclass(frozen=True)
class Note:
    target: str
    severity: str
    text: str
    evidence: str

    def sort_key(self) -> tuple[str, str, str, str]:
        return (self.target, self.severity, self.text, self.evidence)


@dataclass(frozen=True)
class Measurement:
    document: str
    gate: str
    magnitude: str
    limit: str
    passed: bool | None  # None = not measured (pending)


# ---------------------------------------------------------------- parsing

def blank_fences(text: str) -> str:
    """Replace every fenced block by its line breaks, so that a line number
    measured on the result is the line number of the document."""
    return re.sub(r"^```.*?^```[ \t]*$", lambda m: "\n" * m.group(0).count("\n"), text,
                  flags=re.S | re.M)


def strip_code(text: str) -> str:
    """Remove fenced blocks, inline code spans and link targets.

    A fenced block leaves its line breaks behind, so that a line number
    measured on the stripped text is the line number of the document.
    """
    text = blank_fences(text)
    text = re.sub(r"`[^`\n]*`", "", text)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    return text


def section(text: str, heading_regex: str, level: int = 2) -> str:
    """Return the body of the first heading matching heading_regex at level."""
    hashes = "#" * level
    out: list[str] = []
    inside = False
    for line in text.splitlines():
        is_heading = re.match(rf"^{hashes} (?!#)", line) is not None
        upper = re.match(rf"^#{{1,{level - 1}}} (?!#)", line) is not None if level > 1 else False
        if inside and (is_heading or upper):
            break
        if is_heading and re.search(heading_regex, line[len(hashes) + 1:]):
            inside = True
            continue
        if inside:
            out.append(line)
    return "\n".join(out)


def parse_tables(text: str) -> list[list[list[str]]]:
    """Return every Markdown table as a list of rows (header first), cells stripped."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        stripped = line.strip()
        if not in_fence and stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                continue
            current.append(cells)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def first_table(text: str) -> list[list[str]]:
    tables = parse_tables(text)
    if not tables:
        raise InputError("expected table not found")
    return tables[0]


def column(table: list[list[str]], name: str) -> int:
    header = [h.lower() for h in table[0]]
    if name.lower() not in header:
        raise InputError(f"column '{name}' missing from the table with header {table[0]}")
    return header.index(name.lower())


def cell_at(row: list[str], index: int, where: str) -> str:
    """One cell of a table row; a truncated row is malformed input (IM17,
    v0.5.0): it used to raise IndexError and leave with exit 1, the code
    of a blocking note, instead of 2."""
    if index >= len(row):
        raise InputError(f"{where}: a table row has {len(row)} cells, expected at least "
                         f"{index + 1}: | {' | '.join(row)} |")
    return row[index]


def backticked(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


def clean_cell(cell: str) -> str:
    return re.sub(r"[*`]", "", cell).strip()


@dataclass
class RecordedFact:
    """One row of the canon's 'Recorded facts' table: numbers and the
    sections of the prior's method document where each one lives. The row's
    [prior:<id>] mark names the prior those sections belong to (v0.4.0, one
    table for several priors); a row without a mark applies to every prior."""
    numbers: list[str]
    sections: list[str]
    prior_id: str | None = None


@dataclass
class Canon:
    avoid_terms: list[str]
    instantiation_rows: list[str]
    instance_sections: list[str]
    card_fields: list[str]
    limit_tags: list[str]
    components: list[str]
    prior_triggers: list[str]
    recorded_facts: list[RecordedFact]
    efficacy_triggers: list[str] = dataclass_field(default_factory=list)
    # Append-only documents measured by p-efficacy-mark from a declared
    # heading on (CR7, v0.5.0): document -> heading line.
    efficacy_starts: dict[str, str] = dataclass_field(default_factory=dict)


def split_alternatives(cell: str) -> list[str]:
    """An avoid-table cell such as 'client / sponsor' holds alternatives."""
    return [t.strip() for t in cell.split(AVOID_ALTERNATIVE_SEPARATOR) if t.strip()]


def load_recorded_facts(text: str) -> list[RecordedFact]:
    """The canon's 'Recorded facts' table; a canon without a prior has none."""
    try:
        table = first_table(section(text, r"^Recorded facts$", 2))
    except InputError:
        return []
    facts = []
    where = "canon: the 'Recorded facts' table"
    for row in table[1:]:
        ids = PRIOR_TAG.findall(cell_at(row, 1, where))
        # The Number cell is read as numbers ('1,200' is one token), the
        # section cell as section labels.
        facts.append(RecordedFact(
            numbers=NUMBER.findall(clean_cell(row[0])),
            sections=SECTION_TOKEN.findall(clean_cell(cell_at(row, 2, where))),
            prior_id=ids[0] if ids else None))
    return facts


def load_canon(path: Path) -> Canon:
    text = read(path)
    check_canon_version(canon_schema_row_version(text), "the Sections table of the corpus canon")

    def single_column(heading: str, level: int) -> list[str]:
        table = first_table(section(text, heading, level))
        return [clean_cell(r[0]) for r in table[1:]]

    def optional_column(heading: str, level: int) -> list[str]:
        """A canon without a prior needs no trigger list or recorded facts."""
        try:
            return single_column(heading, level)
        except InputError:
            return []

    components_text = section(text, r"^Method components$", 3)
    match = re.search(r":\s*(.+?)\.\s*$", components_text.replace("\n", " ").strip())
    if not match:
        raise InputError("canon: list of method components not found")
    components = [c.strip() for c in match.group(1).split(",") if c.strip()]
    avoid_terms = [t for cell in single_column(r"^Terms to avoid$", 2) for t in split_alternatives(cell)]
    return Canon(
        avoid_terms=avoid_terms,
        instantiation_rows=single_column(r"^Instantiation table rows$", 3),
        instance_sections=single_column(r"^Mandatory sections of an instance$", 3),
        card_fields=single_column(r"^Role card fields$", 3),
        limit_tags=single_column(r"^Origin labels of a limit$", 3),
        components=components,
        prior_triggers=optional_column(r"^Prior-statement triggers$", 3),
        recorded_facts=load_recorded_facts(text),
        efficacy_triggers=optional_column(r"^Efficacy triggers$", 3),
        efficacy_starts=load_efficacy_starts(text),
    )


EFFICACY_STARTS_HEADING = r"^Efficacy mark in append-only documents$"


def load_efficacy_starts(text: str) -> dict[str, str]:
    """The canon's optional table of append-only documents the efficacy gate
    reads from a declared heading on: the units above it are history,
    exempt the way the frozen ledger is exempt from the vocabulary."""
    try:
        table = first_table(section(text, EFFICACY_STARTS_HEADING, 3))
    except InputError:
        return {}
    starts = {}
    for row in table[1:]:
        document, heading = (backticked(cell_at(row, i, "the efficacy-mark start table"))
                             for i in (0, 1))
        if len(document) != 1 or len(heading) != 1:
            raise InputError("canon: each row of the efficacy-mark start table names one "
                             "document and one heading, each in a code span")
        starts[document[0]] = heading[0]
    return starts


# Keys of the JSON canon (emitted by the scaffold) that this validator
# consumes; the scaffold writes them all, as empty lists for a new cell.
JSON_CANON_KEYS = ("terms to avoid", "instantiation table rows",
                   "mandatory sections", "role card fields", "origin labels",
                   "method components", "prior-statement triggers",
                   "recorded facts")
# Optional keys of the JSON canon: added after cells were already running
# (v0.4.0), so a canon without them still loads, with the list empty.
JSON_CANON_OPTIONAL_KEYS = ("efficacy triggers",)
# The canon schema version this validator consumes (I5 of the panel): a
# canon that declares a different version is refused, not misread — the
# requirement the recipe's validator step states. The markdown corpus
# canon declares it in the "Canon schema" row of its Sections table; a
# JSON canon declares it in the top-level "version" field.
CANON_SCHEMA_VERSION = "v1"


def check_canon_version(version: str | None, source: str) -> None:
    if version is None:
        raise InputError(f"canon: {source} does not declare the canon schema "
                         f"version (expected '{CANON_SCHEMA_VERSION}')")
    if version != CANON_SCHEMA_VERSION:
        raise InputError(f"canon: this validator reads canon schema version "
                         f"'{CANON_SCHEMA_VERSION}', {source} declares '{version}'")


def canon_schema_row_version(text: str) -> str | None:
    """The version declared in the 'Canon schema' row of the Sections table
    (the first table of the corpus canon)."""
    for row in first_table(text)[1:]:
        if clean_cell(row[0]).lower() == "canon schema":
            return clean_cell(row[2]) if len(row) > 2 else ""
    return None


def load_canon_json(path: Path) -> Canon:
    """Load the Canon from the JSON the scaffold emits (builtin-json-canon)."""
    try:
        data = json.loads(read(path))
    except json.JSONDecodeError as exc:
        raise InputError(f"canon: invalid JSON ({exc.msg}, line {exc.lineno})") from exc
    if not isinstance(data, dict):
        raise InputError("canon: the JSON canon has to be an object")
    check_canon_version(data.get("version"), "the JSON canon")
    missing = [key for key in JSON_CANON_KEYS if key not in data]
    if missing:
        raise InputError(f"canon: JSON canon misses the sections {missing}")
    for key in (*JSON_CANON_KEYS, *(k for k in JSON_CANON_OPTIONAL_KEYS if k in data)):
        if key == "recorded facts":
            continue
        if not isinstance(data[key], list) or not all(isinstance(v, str) for v in data[key]):
            raise InputError(f"canon: section '{key}' has to be a list of strings")
    return Canon(
        avoid_terms=[t for cell in data["terms to avoid"] for t in split_alternatives(cell)],
        instantiation_rows=data["instantiation table rows"],
        instance_sections=data["mandatory sections"],
        card_fields=data["role card fields"],
        limit_tags=data["origin labels"],
        components=data["method components"],
        prior_triggers=data["prior-statement triggers"],
        recorded_facts=json_recorded_facts(data["recorded facts"]),
        efficacy_triggers=data.get("efficacy triggers", []),
    )


JSON_FACT_FIELDS = ("number", "context", "section")


def json_recorded_facts(items: object) -> list[RecordedFact]:
    """The 'recorded facts' of a JSON canon: the numbers the cell itself
    states about registered priors, each with the sections of that prior's
    method document where it lives (v0.4.0 rework: the list used to have to
    be empty, which left a cell no way to cite a prior number once the gate
    required a row). The prior is the [prior:<id>] mark in the context, as
    in the markdown table; a fact without a mark applies to every prior."""
    expected = ('a list of objects {"number": "18", "context": "roles with a card '
                '[prior:<id>]", "section": "1.1"}')
    if not isinstance(items, list):
        raise InputError(f"canon: 'recorded facts' has to be {expected}")
    facts = []
    for i, item in enumerate(items):
        if (not isinstance(item, dict) or set(item) != set(JSON_FACT_FIELDS)
                or not all(isinstance(item[key], str) for key in JSON_FACT_FIELDS)):
            raise InputError(f"canon: 'recorded facts' item {i} is malformed; expected {expected}")
        numbers, sections = NUMBER.findall(item["number"]), SECTION_TOKEN.findall(item["section"])
        if not numbers or not sections:
            raise InputError(f"canon: 'recorded facts' item {i} needs a number in 'number' "
                             f"and a section label in 'section'; expected {expected}")
        ids = PRIOR_TAG.findall(item["context"])
        facts.append(RecordedFact(numbers, sections, ids[0] if ids else None))
    return facts


@dataclass
class Artifact:
    name: str
    files: list[str]
    owner: str
    deps: list[str]
    schema: str = ""  # first *.schema.json cited in the Schema cell, if any
    proposed: bool = False  # declared but not yet produced (C2, panel v0.2.3)
    # The gates the artifact list assigns (v0.5.0: the one source of the
    # map from gate to artifact; the gate table's Artifact column mirrors it).
    gates: list[str] = dataclass_field(default_factory=list)
    # Every raw field, for the placeholder check of p-references (CR3).
    fields: list[str] = dataclass_field(default_factory=list)


def column_if_present(table: list[list[str]], name: str) -> int | None:
    return column(table, name) if name.lower() in [h.lower() for h in table[0]] else None


def load_artifact_table(table: list[list[str]]) -> dict[str, Artifact]:
    i_name, i_owner = column(table, "Artifact"), column(table, "Owner")
    i_deps, i_gates = column(table, "Depends on"), column(table, "Gates")
    i_file, i_schema = column_if_present(table, "File"), column_if_present(table, "Schema")
    artifacts: dict[str, Artifact] = {}
    where = "artifacts: the artifact table"
    for row in table[1:]:
        names = backticked(cell_at(row, i_name, where))
        if not names:
            continue
        cells = [cell_at(row, i, where) for i in (i_owner, i_deps, i_gates)]
        files = backticked(cell_at(row, i_file, where)) if i_file is not None else []
        deps = [] if cells[1].strip() in NO_DEPENDENCY else backticked(cells[1])
        refs = [r for r in backticked(cell_at(row, i_schema, where)) if r.endswith(".schema.json")] \
            if i_schema is not None else []
        artifacts[names[0]] = Artifact(names[0], files, clean_cell(cells[0]).lower(), deps,
                                       refs[0] if refs else "", gates=backticked(cells[2]),
                                       fields=list(row))
    return artifacts


def load_artifact_records(data: object) -> dict[str, Artifact]:
    """Load the artifacts from the JSON list the scaffold emits."""
    if not isinstance(data, list) or not all(isinstance(rec, dict) for rec in data):
        raise InputError("artifacts: the JSON artifact list has to be a list of objects")
    artifacts: dict[str, Artifact] = {}
    for rec in data:
        if not isinstance(rec.get("name"), str) or not rec["name"]:
            raise InputError("artifacts: every record needs a non-empty string 'name'")
        paths, deps, gates = (rec.get(key, []) for key in ("paths", "depends_on", "gates"))
        if not all(isinstance(value, list) for value in (paths, deps, gates)):
            raise InputError(f"artifacts: 'paths', 'depends_on' and 'gates' of '{rec['name']}' "
                             "have to be lists")
        schema = rec.get("schema")
        schema = schema if isinstance(schema, str) and schema.endswith(".schema.json") else ""
        owner = rec.get("owner", "")
        proposed = rec.get("proposed", False)
        if not isinstance(proposed, bool):
            raise InputError(f"artifacts: 'proposed' of '{rec['name']}' has to be a boolean")
        fields = [str(value) for value in (rec["name"], owner, *paths, *deps, *gates)]
        artifacts[rec["name"]] = Artifact(rec["name"], list(paths), str(owner).lower(),
                                         list(deps), schema, proposed, [str(g) for g in gates],
                                         fields)
    return artifacts


def schema_refs(artifacts: dict[str, Artifact]) -> list[tuple[str, str]]:
    """(artifact, *.schema.json) pairs cited by the artifact documents."""
    return [(artifacts[name].name, artifacts[name].schema)
            for name in sorted(artifacts) if artifacts[name].schema]


def schema_ref_hits(refs: list[tuple[str, str]], folder: Path) -> list[str]:
    """Cited *.schema.json paths must exist and parse.

    An artifact without a schema (or a cell that says "free text") passes:
    the gate measures the promise a schema cell makes, not the absence of a
    schema.
    """
    hits = []
    for name, ref in refs:
        path = folder / ref
        if not path.exists():
            hits.append(f"{name}: schema '{ref}' does not exist")
            continue
        try:
            json.loads(read(path))
        except json.JSONDecodeError as exc:
            hits.append(f"{name}: schema '{ref}' is not valid JSON ({exc.msg})")
    return hits


def alias_target(target: str) -> str:
    """Map a note target written with the v0.1 vocabulary to its v0.2 name."""
    return ARTIFACT_ALIASES.get(target, target)


def validate_registry(data: object) -> dict:
    """Check the shape of an already-parsed instance registry."""
    if not isinstance(data, dict) or not isinstance(data.get("instances"), list):
        raise InputError("registry: expected an object with an 'instances' list")
    for i, inst in enumerate(data["instances"]):
        if not isinstance(inst, dict) or not isinstance(inst.get("id"), str) or not inst["id"]:
            raise InputError(f"registry: instance {i} has no non-empty string 'id'")
    return data


def load_registry(path: Path) -> dict:
    try:
        data = json.loads(read(path))
    except json.JSONDecodeError as exc:
        raise InputError(f"registry: invalid JSON ({exc.msg}, line {exc.lineno})") from exc
    return validate_registry(data)


def check_layout_keys(override: dict, artifacts: dict) -> None:
    """Refuse a layout key this validator never reads (I12 of the panel):
    a misspelled key would otherwise leave the default in force in silence."""
    for where, keys, known in (("top-level", override, LAYOUT_TOP_KEYS),
                               ("'artifacts'", artifacts, LAYOUT_ARTIFACT_KEYS)):
        unknown = sorted(str(key) for key in keys if key not in known)
        if unknown:
            raise InputError(f"layout: unknown {where} key(s) {', '.join(map(repr, unknown))}; "
                             f"the known {where} keys are {', '.join(known)}")


def mixed_parsers_message(base: dict, gates: dict) -> str:
    """Name the gates a layout's map leaves on the default parser: a cell
    layout from before a gate existed (p-efficacy-mark, v0.4.0) lacks it."""
    left = sorted(gate for gate in base["gates"] if gate not in gates)
    hint = (f"; gates the layout does not map, left on the default parser: {', '.join(left)} "
            "(add them to the layout's gate map)" if gates and left else "")
    return ("layout: the merged gate map names more than one parser; "
            "a layout runs on exactly one of them" + hint)


def merge_layout(base: dict, override: dict) -> dict:
    """Overlay a layout file onto the default layout, validating its shape."""
    if not isinstance(override, dict) or override.get("version") != base["version"]:
        raise InputError("layout: expected an object with 'version' equal to "
                         f"{base['version']}")
    artifacts = override.get("artifacts", {})
    gates = override.get("gates", {})
    if not isinstance(artifacts, dict) or not isinstance(gates, dict):
        raise InputError("layout: 'artifacts' and 'gates' have to be objects")
    check_layout_keys(override, artifacts)
    for gate, parser in gates.items():
        if gate not in base["gates"]:
            raise InputError(f"layout: gate '{gate}' is not one of the builtin gates")
        if parser not in PARSERS:
            raise InputError(f"layout: gate '{gate}' asks for the '{parser}' parser; "
                             f"available parsers are 'builtin-markdown' and "
                             f"'builtin-json-canon'")
    merged = dict(base)
    merged["artifacts"] = {**base["artifacts"], **artifacts}
    merged["gates"] = {**base["gates"], **gates}
    if len(set(merged["gates"].values())) != 1:
        raise InputError(mixed_parsers_message(base, gates))
    if "registry" in override:
        if not isinstance(override["registry"], str):
            raise InputError("layout: 'registry' has to be a path string")
        merged["registry"] = override["registry"]
    return merged


def layout_parser(layout: dict) -> str:
    """The single parser the layout's gate map names."""
    parsers = set(layout["gates"].values())
    if len(parsers) != 1:
        raise InputError("layout: the gate map has to name exactly one parser "
                         f"({', '.join(PARSERS)})")
    return parsers.pop()


def check_parser_extension(parser: str, layout: dict) -> None:
    """A parser reads one file kind: markdown or JSON, never a mix."""
    expected = ".json" if parser == "builtin-json-canon" else ".md"
    for key in ("canon", "artifacts"):
        path = layout["artifacts"][key]
        if not path.endswith(expected):
            raise InputError(f"layout: the '{parser}' parser reads '{expected}' files; "
                             f"the '{key}' artifact is '{path}'")


# ------------------------------------------------- mini schema validator

def schema_keyword_set(schema: object, found: set[str] | None = None) -> set[str]:
    """Every keyword used in schema position; the names inside 'properties'
    are field names, not keywords, so the census never reports them."""
    if found is None:
        found = set()
    if not isinstance(schema, dict):
        return found
    found.update(str(key) for key in schema)
    for key, value in schema.items():
        if key == "properties" and isinstance(value, dict):
            for subschema in value.values():
                schema_keyword_set(subschema, found)
        elif key == "items":
            subschemas = value if isinstance(value, list) else [value]
            for subschema in subschemas:
                schema_keyword_set(subschema, found)
    return found


def unsupported_keywords(schema: object) -> list[str]:
    return sorted(k for k in schema_keyword_set(schema) if k not in SUPPORTED_KEYWORDS)


def type_matches(value: object, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def check_against_schema(value: object, schema: dict, path: str) -> list[str]:
    """Apply the supported subset of JSON Schema; unknown keywords are ignored
    here (they are a note of the keyword census, never a silent pass)."""
    hits: list[str] = []
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(type_matches(value, t) for t in types):
            hits.append(f"{path}: expected type {' or '.join(map(str, types))}")
            return hits
    if "enum" in schema and value not in schema["enum"]:
        hits.append(f"{path}: {value!r} is not one of the allowed values")
    if "pattern" in schema and isinstance(value, str) and not re.search(schema["pattern"], value):
        hits.append(f"{path}: {value!r} does not match the required pattern")
    if ("minimum" in schema and isinstance(value, (int, float))
            and not isinstance(value, bool) and value < schema["minimum"]):
        hits.append(f"{path}: {value} is below the minimum {schema['minimum']}")
    if isinstance(value, dict):
        for required in schema.get("required", []):
            if required not in value:
                hits.append(f"{path}: required field '{required}' is missing")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in sorted(value):
                if key not in properties:
                    hits.append(f"{path}: unknown field '{key}'")
        for key in sorted(properties):
            if key in value:
                hits += check_against_schema(value[key], properties[key], f"{path}.{key}")
    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for i, item in enumerate(value):
            hits += check_against_schema(item, schema["items"], f"{path}[{i}]")
    return hits


def validate_data_text(text: str, schema: dict, origin: str) -> list[str]:
    """Validate one JSON document (or each line of a JSONL file)."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"{origin}: not valid JSON ({exc.msg}, line {exc.lineno})"]
    return [f"{origin}: {hit}" for hit in check_against_schema(data, schema, "$")]


def role_name(card: Path) -> str:
    """Role name from the card title '# Role card: <name>'."""
    content = read(card)
    first = content.splitlines()[0] if content else ""
    m = re.match(r"^# Role card: (.+)$", first)
    if not m:
        raise InputError(f"card {card.name} has no title '# Role card: name'")
    return m.group(1).strip().lower()


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"could not read {path.name}: {exc.strerror}") from exc
    except UnicodeDecodeError as exc:
        # I15 of the panel: undecodable bytes are a tool failure (exit 2),
        # never a finding about the document's content.
        raise InputError(f"could not decode {path.name} as UTF-8 at byte {exc.start} "
                         f"({exc.reason}); the documents are read as UTF-8 only") from exc


# ---------------------------------------------------------------- checks

ABS_PATH = re.compile(rf"(?<![{WORD_CHARS}.\]/~-])/(?:[{WORD_CHARS}.-]+/)+[{WORD_CHARS}.-]*|~/|\b[A-Z]:\\")
ISO_DATE = re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b")
DMY_DATE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
MONTH = (r"(?:January|February|March|April|May|June|July|August|September|October|November|December"
         r"|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b")
MADE_ON = re.compile(rf"\b(?:made|written|generated)\s+on\s+(?:\d|{MONTH})", re.I)
# IM18 (v0.5.0): the forms the gate let through — a date written with the
# month's name ("29 October 2026", "October 29, 2026", "Oct 29 2026") or
# with dots ("29.10.2026"), an absolute path of one segment under a common
# root ("/tmp", "/scratch"), a file URL, and a home folder by user name
# ("~joe/work"). A month and a year with no day is not a date.
NAMED_DATE = re.compile(rf"\b\d{{1,2}}\s+{MONTH}\.?,?\s+(?:19|20)\d{{2}}\b"
                        rf"|\b{MONTH}\.?\s+\d{{1,2}},?\s+(?:19|20)\d{{2}}\b")
DOTTED_DATE = re.compile(r"\b\d{1,2}\.\d{1,2}\.(?:19|20)\d{2}\b")
ROOT_SEGMENT = re.compile(rf"(?<![{WORD_CHARS}.\]/~-])/(?:tmp|etc|home|users?|usr|var|opt|root"
                          rf"|srv|mnt|media|scratch|data|proj|private|Volumes)(?![{WORD_CHARS}./-])",
                          re.I)
FILE_URL = re.compile(r"\bfile:/+", re.I)
USER_HOME = re.compile(rf"(?<![{WORD_CHARS}/])~[a-z_][a-z0-9_.-]*", re.I)
HTML_TAG = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>\n]*)?/?>")
# A number with optional decimal/thousands separators; a group joined by a
# no-break space or a narrow no-break space is a thousands group.
NUMBER = re.compile(r"\d{1,3}(?:[\u00A0\u202F]\d{3})+(?![\d.,])|\d+(?:[.,]\d+)*")
# A number written in this production's documents, as the prior-number gate
# reads it: a digit attached to a letter is a name ('p95', 'v1', 'D6', 'E1'),
# not a count (the rule the prior instance fixed at the root, step 9 of the
# recipe). The prior's own document keeps the plain NUMBER reading.
DOCUMENT_NUMBER = re.compile(rf"(?<![{WORD_CHARS}.,])(?:{NUMBER.pattern})")
# A reference to a section of the prior's method document ('section 2.1',
# 'sections 1.10 and 4.14', 'step 16'): checked as a section label that has
# to exist there, not as a number that needs a recorded fact.
# A continuation label ('and 4.14') is taken only when what follows it is
# punctuation, the end, another connector or 'of' — never another word: in
# 'section 1.4 and 7 rounds' the 7 counts rounds (re-review of v0.4.0).
SECTION_REF = re.compile(r"\b(?:sections?|steps?)\s+(\d+(?:\.\d+)*(?:(?:\s*,\s*|\s+and\s+|\s+or\s+)"
                         r"\d+(?:\.\d+)*(?=\s*(?:[,.;:)\]]|$)|\s+(?:and|or|of)\b))*)", re.I)
# The two spaces of a formatted reading (I6 of the v0.4.0 review): a value
# only meets a value, a literal only meets a literal.
VALUE_TAG, LITERAL_TAG = "value:", "literal:"
PLURAL_SUFFIX = "(?:s|es)?"


def word_pattern(term: str) -> str:
    """Whole-word, plural-tolerant pattern for an avoid-word or identifier."""
    return rf"(?<![{WORD_CHARS}]){re.escape(term)}{PLURAL_SUFFIX}(?![{WORD_CHARS}])"


def count_avoid_terms(text: str, terms: list[str]) -> list[tuple[str, int]]:
    body = strip_code(text)
    found = []
    for term in terms:
        n = len(re.findall(word_pattern(term), body, flags=re.I))
        if n:
            found.append((term, n))
    return found


def anonymity_hits(text: str, forbidden: list[str] | None) -> list[str]:
    hits = [f"absolute path '{m.group(0)}'" for pattern in (ABS_PATH, ROOT_SEGMENT, FILE_URL, USER_HOME)
            for m in pattern.finditer(text)]
    hits += [f"date '{m.group(0)}'" for pattern in (ISO_DATE, DMY_DATE, NAMED_DATE, DOTTED_DATE)
             for m in pattern.finditer(text)]
    hits += [f"authoring date '{m.group(0)}'" for m in MADE_ON.finditer(text)]
    for item in forbidden or []:
        pattern = rf"(?<![{WORD_CHARS}]){re.escape(item)}(?![{WORD_CHARS}])"
        if re.search(pattern, text, flags=re.I):
            hits.append("forbidden identifier (from the external list)")
    return hits


def form_hits(text: str) -> list[str]:
    hits = [f"HTML tag '{m.group(0)}'" for m in HTML_TAG.finditer(strip_code(text))]
    in_fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            if not in_fence and line.strip() != "```text":
                hits.append(f"fenced block without the text mark at line {n}")
            in_fence = not in_fence
    if in_fence:
        hits.append("unclosed fenced block")
    return hits


def text_units(text: str) -> list[tuple[int, str]]:
    """Split Markdown into units (paragraph, list item, table row) with their first line.

    The prior-number gate first worked per line and missed a number whose
    sentence wrapped onto the line carrying the [prior:<id>] marker (caught
    by the sensitivity test); units fix that at the root.
    """
    units: list[tuple[int, str]] = []
    start, buf = 0, []
    for n, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        new_unit = (not stripped or stripped.startswith("|")
                    or re.match(r"^\s*(?:[-*]|\d+\.)\s", line) is not None or line.startswith("#"))
        if new_unit and buf:
            units.append((start, " ".join(buf)))
            buf = []
        if stripped:
            if not buf:
                start = n
            buf.append(stripped)
            if stripped.startswith("|") or line.startswith("#"):
                units.append((start, " ".join(buf)))
                buf = []
    if buf:
        units.append((start, " ".join(buf)))
    return units


def _decimal_text(digits: str) -> str | None:
    try:
        return format(Decimal(digits).normalize(), "f")
    except InvalidOperation:
        return None


def format_value(token: str, number_format: str) -> str | None:
    """The one value of a token in a declared number format, or None when
    the token does not parse in it (a separator counts as thousands only
    before groups of exactly three digits: '1.10' is no comma-decimal
    number, it is a section number)."""
    grouped = re.sub(r"[\u00A0\u202F]", "", token)
    if grouped != token:
        return _decimal_text(grouped)
    thousands, decimal = FORMAT_SEPARATORS[number_format]
    parts = token.split(decimal)
    if len(parts) > 2 or (len(parts) == 2 and thousands in parts[1]):
        return None
    groups = parts[0].split(thousands)
    if len(groups) > 1 and (not all(len(g) == 3 for g in groups[1:])
                            or not 1 <= len(groups[0]) <= 3):
        return None
    return _decimal_text("".join(groups) + ("." + parts[1] if len(parts) == 2 else ""))


def number_readings(token: str, number_format: str | None = None) -> set[str]:
    """Every value a number token can denote, as canonical decimal text.

    With a declared format (I16 of the panel) the token has one value
    reading, in that format, or its literal spelling only when it does not
    parse there \u2014 so a comma-decimal '1.200' is 1200 and never 1.2, and
    '1.10' still matches itself. Values and literals live in separate
    spaces (tagged), so the value 1.2 never meets the literal '1.2' of a
    section number (rework of the v0.4.0 review). Without a format (legacy:
    a prior registered before the format was declared) the token is read
    both ways plus its literal, untagged, so that '0.546' equals '0,546' and
    '1,200' equals '1.200'. '39' never equals '139' or '0,39'.
    """
    if number_format is not None:
        value = format_value(token, number_format)
        return {VALUE_TAG + value} if value is not None else {LITERAL_TAG + token}
    readings = {token}
    for name in NUMBER_FORMATS:
        value = format_value(token, name)
        if value is not None:
            readings.add(value)
    return readings


def document_readings(token: str, case_format: str | None) -> set[str]:
    """The readings of a number written in this production's documents.

    Against a prior with a declared format, the document token is read in
    the documents' own format plus its literal spelling (the literal is what
    meets a section number that does not parse in the prior's format, and
    only another literal); a legacy prior keeps the two-way reading on both
    sides."""
    if case_format is None:
        return number_readings(token)
    return number_readings(token, DOCUMENT_NUMBER_FORMAT) | {LITERAL_TAG + token}


def case_number_index(case_text: str, number_format: str | None = None) -> set[str]:
    """All readings of every number in the case method document."""
    index: set[str] = set()
    for token in NUMBER.findall(case_text):
        index |= number_readings(token, number_format)
    return index


def trigger_pattern(trigger: str) -> str:
    """Whole-word pattern of a prior-statement trigger; plurals do not match
    ('prior instances' is not the trigger 'prior instance')."""
    words = [re.escape(word) for word in trigger.split()]
    return rf"(?<![{WORD_CHARS}])" + r"\s+".join(words) + rf"(?![{WORD_CHARS}])"


def prior_mark_hits(text: str, triggers: list[str]) -> list[str]:
    """Every unit that talks about a registered prior carries [prior:<id>].

    Kept from the first review: a qualitative claim about the prior, absent
    from the prior's document, passed every gate because only numeric claims
    had to be marked (regression turned into a gate). The phrases that
    require the mark come from the canon's 'Prior-statement triggers' table,
    not from a rule of this script.

    Since v0.5.0 (CR2 of the panel that reviewed v0.4.2) the trigger and the
    mark are both read outside code, the reading p-prior gives the mark: a
    trigger in a code span is notation (the canon exempts it), and a mark in
    a code span is no mark. A mark between backticks used to satisfy this
    gate while p-prior, which strips code, checked none of the unit's
    numbers, so an invented number passed both.
    """
    hits = []
    for n, unit in text_units(blank_fences(text)):
        body = strip_code(unit)
        if PRIOR_MARK in body:
            continue
        trigger = first_trigger(body, triggers)
        if trigger is None:
            continue
        where = (" (the mark is inside a code span, which is not a mark)"
                 if PRIOR_MARK in unit else "")
        hits.append(f"line {n}: statement about the prior ('{trigger}') "
                    f"without a {PRIOR_MARK}<id>] mark{where}")
    return hits


def first_trigger(body: str, triggers: list[str]) -> str | None:
    """The first trigger phrase the text uses, whole-word, case-insensitive."""
    for trigger in triggers:
        if re.search(trigger_pattern(trigger), body, flags=re.I):
            return trigger
    return None


def case_section_indexes(case_text: str,
                         number_format: str | None = None) -> dict[str, set[str]]:
    """Number index of each numbered section of the prior method document.

    Headings such as '## 1.4 ...' or '### Passo 15 ...' open a section that
    runs to the next such heading; headings inside fenced blocks do not
    count (a comment line in a command block is not a section).
    """
    sections: dict[str, list[str]] = {}
    current, buf, in_fence = None, [], False
    for line in case_text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else CASE_SECTION_HEADING.match(line)
        if m:
            if current is not None:
                sections[current] = buf
            current, buf = m.group(1), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = buf
    return {label: case_number_index("\n".join(lines), number_format)
            for label, lines in sections.items()}


@dataclass(frozen=True)
class CaseDocument:
    """One prior method document passed with --case, indexed in the number
    format its registry entry declares (None: legacy two-way reading)."""
    index: frozenset[str]
    sections: dict[str, set[str]]
    number_format: str | None = None


def case_document(case_text: str, number_format: str | None = None) -> CaseDocument:
    return CaseDocument(frozenset(case_number_index(case_text, number_format)),
                        case_section_indexes(case_text, number_format), number_format)


def fact_rows_for(readings: set[str], facts: list[RecordedFact],
                  case_format: str | None = None) -> list[RecordedFact]:
    """The recorded-fact rows that carry a number with one of these readings."""
    return [fact for fact in facts
            if any(readings & document_readings(token, case_format) for token in fact.numbers)]


def facts_of(prior_id: str | None, facts: list[RecordedFact]) -> list[RecordedFact]:
    """The recorded-fact rows of one prior: its own rows and the unmarked ones."""
    return [fact for fact in facts if fact.prior_id in (None, prior_id)]


def number_hits(where: str, number: str, doc: CaseDocument, facts: list[RecordedFact],
                require_row: bool = False) -> tuple[list[str], bool]:
    """Check one number of a [prior:...] unit against one prior document.

    A number with a row in the canon's 'Recorded facts' is checked in the
    union of the sections that row cites. A number without a row fails when
    require_row is set (the gate, since the v0.4.0 review: presence in the
    whole document let an invented '21 roles' pass, because 21 occurs once
    in the prior's document in an unrelated sentence); otherwise (the
    single-document primitive of the reading rules) it is checked for
    presence in the whole document. Returns the hits and whether the
    presence check ran."""
    readings = document_readings(number, doc.number_format)
    rows = fact_rows_for(readings, facts, doc.number_format) if facts else []
    if not rows and require_row:
        return [f"{where}: '{number}' has no row of that prior in the canon's 'Recorded "
                "facts'; a number about a prior is checked in the section its row cites, "
                "never by presence in the whole document"], False
    if not rows:
        found = bool(readings & doc.index)
        return ([] if found else [f"{where}: '{number}' is not in the prior method document"]), True
    labels = sorted(set().union(*(row.sections for row in rows)))
    hits: list[str] = []
    index: set[str] = set()
    for label in labels:
        if label not in doc.sections:
            hits.append(f"{where}: '{number}' cites section '{label}' of the "
                        "prior method document, which does not exist")
        else:
            index |= doc.sections[label]
    # A cited section with no numbers verifies nothing: an empty union must
    # still be a hit, not a silent pass (rework fix of v0.2.1).
    if not readings & index:
        hits.append(f"{where}: '{number}' is not in section(s) {', '.join(labels)} of "
                    "the prior method document")
    return hits, False


def prior_number_findings(text: str, case_index: set[str],
                          facts: list[RecordedFact] | None = None,
                          sections: dict[str, set[str]] | None = None
                          ) -> tuple[list[str], int]:
    """Numbers in [prior:...] units checked against one prior's document.

    The single-document form (one prior, legacy number reading). Every mark
    (including its id digits) is removed before the numbers are read, so an
    id such as '000-av-production' is never itself checked; the returned
    count of global checks lets the report say which verification ran.
    """
    doc = CaseDocument(frozenset(case_index), sections or {})
    hits: list[str] = []
    global_checks = 0
    for n, unit in text_units(strip_code(text)):
        if PRIOR_MARK not in unit:
            continue
        for number in NUMBER.findall(MARK_TAGS.sub("", unit)):
            found, was_global = number_hits(f"line {n}", number, doc, facts or [])
            hits += found
            global_checks += was_global
    return hits, global_checks


def prior_number_hits(text: str, case_index: set[str],
                      facts: list[RecordedFact] | None = None,
                      sections: dict[str, set[str]] | None = None) -> list[str]:
    return prior_number_findings(text, case_index, facts, sections)[0]


@dataclass
class PriorCheck:
    """The outcome of the number check of one document against several priors."""
    hits: list[str] = dataclass_field(default_factory=list)
    checked: int = 0
    references: int = 0
    unmeasured: set[str] = dataclass_field(default_factory=set)


def section_references(text: str) -> tuple[list[str], str]:
    """The section labels a unit cites ('section 2.1', 'step 16') and the
    text with those references removed, so the labels are not read as
    numbers that need a recorded fact."""
    labels = [label for m in SECTION_REF.finditer(text) for label in SECTION_TOKEN.findall(m.group(1))]
    return labels, SECTION_REF.sub(" ", text)


def without_instance_ids(text: str, instance_ids: frozenset[str]) -> str:
    """The text with every full registered id ('004-adoption-guide') removed:
    the full id names an instance, it is not a number about it. Only the full
    id counts (v0.4.1): a bare '004' is a number again, so 'the prior has 003
    phases' is checked like any count."""
    if not instance_ids:
        return text
    alternatives = "|".join(re.escape(i) for i in sorted(instance_ids, key=len, reverse=True))
    return re.sub(rf"(?<![{WORD_CHARS}-])(?:{alternatives})(?![{WORD_CHARS}-])", " ", text)


def unit_number_check(n: int, unit: str, docs: dict[str, CaseDocument],
                      facts: list[RecordedFact], out: PriorCheck,
                      instance_ids: frozenset[str] = frozenset()) -> None:
    """Check one marked unit against the document of each prior it cites
    (I14 of the panel): every number and every cited section is verified in
    the document of each id, never in the document of another id; an id with
    no document passed leaves the unit unmeasured for that id, by name. A
    full registered id in the text names an instance and is not read."""
    ids = sorted(set(PRIOR_TAG.findall(unit)))
    labels, body = section_references(without_instance_ids(MARK_TAGS.sub("", unit), instance_ids))
    numbers = DOCUMENT_NUMBER.findall(body)
    if not ids or not (labels or numbers):
        return
    for pid in ids:
        if pid not in docs:
            out.unmeasured.add(pid)
            continue
        where = f"line {n}, prior '{pid}'"
        for label in labels:
            out.references += 1
            if label not in docs[pid].sections:
                out.hits.append(f"{where}: cites section '{label}' of the prior method document, "
                                "which does not exist")
        for number in numbers:
            out.checked += 1
            out.hits += number_hits(where, number, docs[pid], facts_of(pid, facts), require_row=True)[0]


def multi_prior_findings(text: str, docs: dict[str, CaseDocument], facts: list[RecordedFact],
                         instance_ids: frozenset[str] = frozenset()) -> PriorCheck:
    """Numbers in [prior:<id>] units, each checked in the document of <id>."""
    out = PriorCheck()
    for n, unit in text_units(strip_code(text)):
        unit_number_check(n, unit, docs, facts, out, instance_ids)
    return out


def instance_ids_of(registry: dict) -> frozenset[str]:
    """The full registered ids ('000-av-production', '004-adoption-guide'):
    in a marked unit they name an instance, they are not numbers about it.
    Until v0.4.1 the bare numeric prefix ('004') was excluded too, which let
    a count with leading zeros ('003 phases') pass unread."""
    return frozenset(str(inst["id"]) for inst in registry.get("instances", [])
                     if isinstance(inst, dict) and inst.get("id"))


def pin_findings(cited_ids: set[str], registry: dict | None,
                 case_digests: set[str] | None) -> tuple[list[str], int]:
    """The sha256 pin of every executed prior cited in the corpus.

    The gate `p-prior-pin` was created after the critical panel found that a
    true pin existed only on the owner's machine: the sha256 in the registry
    was never compared with the documents actually passed as priors. A cited
    executed instance with no pinned sha256, or pinned to a sha256 that none
    of the --case documents has, is a blocking note; so is a --case document
    that is the pin of no executed instance (I14). Without any prior document
    the gate is pending, never a pass.
    """
    if registry is None:
        return [], 0
    executed = {inst["id"]: inst for inst in registry.get("instances", [])
                if isinstance(inst, dict) and inst.get("status") == "executed"}
    cited = sorted(i for i in cited_ids if i in executed)
    pinned = {inst.get("sha256") for inst in executed.values()}
    stray = sorted((case_digests or set()) - pinned)
    # A document passed that pins nothing suggests a wrong or edited prior;
    # with none, the cited prior's document was simply not passed (S5).
    cause = ("wrong or edited prior document" if stray
             else "its method document was not passed")
    hits: list[str] = []
    for pid in cited:
        recorded = executed[pid].get("sha256")
        if not isinstance(recorded, str) or not recorded:
            hits.append(f"cited prior '{pid}' is executed and has no sha256 "
                        "pinned in the registry")
        elif case_digests is not None and recorded not in case_digests:
            hits.append(f"cited prior '{pid}': no document passed as --case matches the "
                        f"sha256 pinned for it ({cause})")
    for digest in stray:
        hits.append(f"document passed as --case matches no executed instance "
                    f"(sha256 {digest[:12]}...)")
    return hits, len(cited)


def canon_links(doc_path: Path, text: str, canon_path: Path) -> tuple[int, list[str]]:
    """Links naming the canon file: how many resolve to it, and the targets
    that do not.

    The gate counted links by name until v0.4.0, so a card linking
    `02-canon.json` from inside `04-roles/` passed while leading nowhere
    (the v0.3.1 review); the target now has to resolve, relative to the
    folder of the document, to the canon file of the layout.
    """
    targets = re.findall(rf"\]\(([^)]*{re.escape(canon_path.name)})\)", text)
    canon = canon_path.resolve()
    unresolved = [target for target in targets if (doc_path.parent / target).resolve() != canon]
    return len(targets) - len(unresolved), unresolved


def efficacy_mark_hits(text: str, triggers: list[str]) -> list[str]:
    """Every unit that claims the method's efficacy carries its evidence
    label (I10 of the panel): [prior:<id>], [experiment:<id>], [lessons] or
    [hypothesis]. The triggers and the labels are read outside code spans,
    link targets and fenced blocks (v0.5.0: one reading for the three mark
    gates; a label between backticks is notation, not a label). The gate
    is lexical: it reads the closed list of trigger phrases of the canon,
    and a paraphrase of a claim escapes it."""
    hits = []
    for n, unit in text_units(blank_fences(text)):
        body = strip_code(unit)
        if EFFICACY_LABEL.search(body):
            continue
        trigger = first_trigger(body, triggers)
        if trigger is not None:
            hits.append(f"line {n}: claim of efficacy ('{trigger}') without one of the "
                        "labels [prior:<id>], [experiment:<id>], [lessons], [hypothesis]")
    return hits


def from_heading(text: str, heading: str) -> str | None:
    """The text with every line above the declared heading blanked (line
    numbers kept), or None when the heading is not a line of the text."""
    lines = text.split("\n")
    if heading not in lines:
        return None
    start = lines.index(heading)
    return "\n" * start + "\n".join(lines[start:])


def experiment_statuses(text: str) -> dict[str, str | None]:
    """Every experiment of the record and the status its block declares
    (None when it declares none). The block of '## E1 — ...' runs to the next
    level-2 heading; a subheading ('### Question') never names an id."""
    headings = list(EXPERIMENT_HEADING.finditer(text))
    statuses: dict[str, str | None] = {}
    for m in headings:
        block = text[m.end():]
        end = LEVEL_TWO_HEADING.search(block)
        status = EXPERIMENT_STATUS.search(block[:end.start()] if end else block)
        statuses[m.group(1)] = status.group(1) if status else None
    return statuses


def registered_experiments(text: str) -> set[str]:
    """The ids the experiments record registers as evidence: the experiments
    whose block declares the status 'executed' (S4 of the v0.4.0 review)."""
    return {eid for eid, status in experiment_statuses(text).items() if status == EXECUTED}


def experiment_label_hits(eid: str, statuses: dict[str, str | None], record: str) -> list[str]:
    """An [experiment:<id>] label backs a claim only with an executed
    experiment: an unknown id is not registered, and a designed (or pending)
    one is not evidence yet."""
    if eid not in statuses:
        return [f"[experiment:{eid}] is not registered in {record}"]
    status = statuses[eid]
    if status == EXECUTED:
        return []
    kind = f"a {status}" if status else "an undeclared-status"
    return [f"[experiment:{eid}] cites {kind} experiment as evidence; only an executed "
            "experiment backs a claim"]


def executed_entry_hits(where: str, inst: dict) -> list[str]:
    """An executed entry carries its document, its sha256 pin, its locator (a
    relative path or the reserved owner-held string) and its number format
    (I16 of the panel: never a silent default)."""
    hits = [f"{where}: executed instance '{inst.get('id')}' declares no {name}"
            for name in ("document", "sha256", "locator")
            if not isinstance(inst.get(name), str) or not inst[name]]
    locator = inst.get("locator")
    if isinstance(locator, str) and locator and locator != LOCATOR_OWNER_HELD \
            and NON_RELATIVE_LOCATOR.match(locator):
        hits.append(f"{where}: the locator of '{inst.get('id')}' is neither a relative path "
                    f"nor '{LOCATOR_OWNER_HELD}'")
    if inst.get("number_format") not in NUMBER_FORMATS:
        hits.append(f"{where}: executed instance '{inst.get('id')}' declares no "
                    f"number_format (expected one of {', '.join(NUMBER_FORMATS)}); "
                    "its numbers are never read by a default")
    return hits


def designed_entry_hits(where: str, inst: dict) -> list[str]:
    """A designed entry has not run: it carries none of the fields of an
    executed one (null or absent), so it can never pass for a pinned prior."""
    return [f"{where}: designed instance '{inst.get('id')}' carries '{name}'; a designed "
            f"entry keeps {', '.join(STATUS_FIELDS)} null or absent until it runs"
            for name in STATUS_FIELDS if inst.get(name) is not None]


def registry_status_hits(text: str) -> list[str]:
    """The contract of each registry entry by its status (C16, v0.4.1)."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []  # reported by the schema validation of the same document
    hits = []
    for i, inst in enumerate(data.get("instances", []) if isinstance(data, dict) else []):
        if not isinstance(inst, dict):
            continue
        if inst.get("status") == EXECUTED:
            hits += executed_entry_hits(f"$.instances[{i}]", inst)
        elif inst.get("status") == "designed":
            hits += designed_entry_hits(f"$.instances[{i}]", inst)
    return hits


def find_cycle(graph: dict[str, list[str]]) -> list[str]:
    """Return one cycle as a list of nodes, or [] if the graph is acyclic."""
    white, grey, black = 0, 1, 2
    color = {node: white for node in graph}
    stack: list[str] = []

    def visit(node: str) -> list[str]:
        color[node] = grey
        stack.append(node)
        for dep in sorted(graph.get(node, [])):
            if dep not in color:
                continue
            if color[dep] == grey:
                return stack[stack.index(dep):] + [dep]
            if color[dep] == white:
                cycle = visit(dep)
                if cycle:
                    return cycle
        stack.pop()
        color[node] = black
        return []

    for node in sorted(graph):
        if color[node] == white:
            cycle = visit(node)
            if cycle:
                return cycle
    return []


def gate_tables(text: str) -> list[list[list[str]]]:
    return [t for t in parse_tables(text) if t and clean_cell(t[0][0]).lower() == "gate"]


def limit_hits(text: str, tags: list[str], min_words: int) -> list[str]:
    """Gate rows with an empty field, a justification without an origin
    label or shorter than min_words (read from the p-limit row of the gate
    table, IM16), or a placeholder in any field (CR3, v0.5.0)."""
    hits = []
    for table in gate_tables(text):
        i_mag, i_lim, i_just = (column(table, c) for c in ("Magnitude", "Limit", "Justification"))
        for row in table[1:]:
            gate = clean_cell(row[0])
            for idx, label in ((i_mag, "magnitude"), (i_lim, "limit"), (i_just, "justification")):
                if idx >= len(row) or clean_cell(row[idx]) in NO_DEPENDENCY:
                    hits.append(f"{gate}: empty {label}")
            just = row[i_just].strip() if i_just < len(row) else ""
            if just and not any(just.startswith(t.replace("`", "")) for t in tags):
                hits.append(f"{gate}: justification without an origin label")
            if just and len(just.split()) < min_words:
                hits.append(f"{gate}: justification with fewer than {min_words} words")
            hits += [f"{gate}: placeholder {p}" for p in placeholders(" | ".join(row))]
    return hits


def placeholders(text: str) -> list[str]:
    """The placeholders of a field, outside code spans, quoted (CR3)."""
    return [f"'{m.group(0)}'" for m in PLACEHOLDER.finditer(strip_code(text))]


def role_blocks(text: str) -> dict[str, str]:
    body = section(text, r"Role cards", 2)
    blocks: dict[str, str] = {}
    current = None
    for line in body.splitlines():
        m = re.match(r"^### (?!#)(.+)$", line)
        if m:
            current = clean_cell(m.group(1)).lower()
            blocks[current] = ""
        elif current is not None:
            blocks[current] += line + "\n"
    return blocks


def card_hits(text: str, fields: list[str], whole_document: bool) -> list[str]:
    blocks = {"card": text} if whole_document else role_blocks(text)
    if not blocks:
        return ["no card found in the role cards section"]
    hits = []
    for role, block in sorted(blocks.items()):
        for field in fields:
            if f"**{field}:**" not in block:
                hits.append(f"{role}: field '{field}' missing")
        # CR3 (v0.5.0): a card whose fields still say '<fill in>' used to
        # pass with "0 fields missing"; a placeholder is an unfilled field.
        hits += [f"{role}: placeholder {p} in the card" for p in placeholders(blank_fences(block))]
    return hits


def heading_titles(text: str) -> set[str]:
    titles = set()
    for line in text.splitlines():
        m = re.match(r"^## (?!#)(?:\d+\.\s*)?(.+)$", line)
        if m:
            titles.add(m.group(1).strip().lower())
    return titles


def instantiation_hits(text: str, rows: list[str]) -> tuple[int, int, list[str]]:
    body = section(text, r"Instantiation table", 2)
    tables = parse_tables(body)
    if not tables:
        return 0, 0, ["instantiation table missing"]
    table = tables[0]
    present = {clean_cell(r[0]).lower(): r for r in table[1:]}
    hits, empty, found = [], 0, 0
    for row in rows:
        cells = present.get(row.lower())
        if cells is None:
            hits.append(f"row '{row}' missing")
            continue
        found += 1
        if len(cells) < 2 or clean_cell(cells[1]) in NO_DEPENDENCY:
            empty += 1
            hits.append(f"row '{row}' empty")
        elif placeholders(cells[1]):
            hits += [f"row '{row}' holds the placeholder {p}" for p in placeholders(cells[1])]
    return found, empty, hits


def instance_reference_hits(text: str) -> list[str]:
    art_tables = [t for t in parse_tables(section(text, r"Artifacts and graph", 2))
                  if t and clean_cell(t[0][0]).lower() == "artifact"]
    if not art_tables:
        return ["artifact table missing from the 'Artifacts and graph' section"]
    artifacts = load_artifact_table(art_tables[0])
    blocks = role_blocks(text)
    roles = set(blocks) | {OWNER_HUMAN}
    hits = reference_hits(artifacts, roles, gate_tables(text))
    for role, block in sorted(blocks.items()):
        hits += note_target_hits(block, set(artifacts), role)
    return hits


def note_target_hits(card: str, artifact_names: set[str], role: str) -> list[str]:
    """Backticked names in the 'Notes it emits' field must be declared artifacts.

    Added after a card pointed notes at an artifact the instance did not declare
    and no gate caught it (regression turned into a rule).
    """
    m = re.search(r"\*\*Notes it emits:\*\*(.*?)(?=^\s*-?\s*\*\*[^*]+:\*\*|\Z)", card, flags=re.S | re.M)
    if not m:
        return []
    hits = []
    # Only names introduced as a destination ("to `x`", "to the `x`") are note
    # targets; other code spans in the field (`text`, `[prior:<id>]`) are not
    # (root-cause fix of the rule's first false positives).
    targets = re.findall(rf"(?<![{WORD_CHARS}])[Tt]o\s+(?:the\s+)?`([^`]+)`", m.group(1))
    for name in targets:
        # The alias maps the v0.1 name to the v0.2 one, so a card may still
        # aim notes at `bible` the way the frozen round-1 ledger does.
        if name in VALID_SEVERITIES or alias_target(name) in artifact_names:
            continue
        hits.append(f"{role}: note aimed at '{name}', which is not a declared artifact")
    return hits


def reference_hits(artifacts: dict[str, Artifact], roles: set[str],
                   gates: list[list[list[str]]]) -> list[str]:
    hits = []
    for art in sorted(artifacts.values(), key=lambda a: a.name):
        if art.owner not in roles:
            hits.append(f"{art.name}: owner '{art.owner}' is not a declared role")
        for dep in art.deps:
            if dep not in artifacts:
                hits.append(f"{art.name}: depends on '{dep}', not declared")
    for table in gates:
        i_art = column(table, "Artifact")
        for row in table[1:]:
            for name in backticked(cell_at(row, i_art, "a gate table")):
                if name not in artifacts:
                    hits.append(f"gate {clean_cell(row[0])}: artifact '{name}' not declared")
    cycle = find_cycle({a.name: a.deps for a in artifacts.values()})
    if cycle:
        hits.append("cycle in the graph: " + " -> ".join(cycle))
    return hits


def declared_gate_map(artifacts: dict[str, Artifact]) -> dict[str, list[str]]:
    """Gate -> the artifacts the artifact list assigns it to: the one source
    of the map (v0.5.0). A placeholder in place of a gate id is no gate (it
    is a finding of p-references, not a gate to run)."""
    gate_map: dict[str, list[str]] = {}
    for art in sorted(artifacts.values(), key=lambda a: a.name):
        for gate in art.gates:
            if not PLACEHOLDER.fullmatch(gate):
                gate_map.setdefault(gate, []).append(art.name)
    return gate_map


def gate_map_hits(artifacts: dict[str, Artifact], table: list[list[str]]) -> list[str]:
    """The Artifact column of the gate table against the artifact list (CR1
    and IM16, v0.5.0): a gate the list assigns with no row, or a row that
    names another set of artifacts, is a finding. Deleting the gate table
    used to leave every gate silently unmeasured and the report green."""
    declared = declared_gate_map(artifacts)
    i_art = column(table, "Artifact")
    rows = {clean_cell(r[0]): set(backticked(cell_at(r, i_art, "the gate table"))) for r in table[1:]}
    hits = []
    for gate, arts in sorted(declared.items()):
        if gate not in rows:
            hits.append(f"gate `{gate}` declared for {', '.join(f'`{a}`' for a in arts)} "
                        "has no row in the gates table")
            continue
        missing = sorted(set(arts) - rows[gate])
        extra = sorted(a for a in rows[gate] - set(arts) if a in artifacts)
        hits += [f"the row of gate `{gate}` does not name `{a}`, which the artifact table "
                 "assigns it to" for a in missing]
        hits += [f"the row of gate `{gate}` names `{a}`, which the artifact table does not "
                 "assign it to" for a in extra]
    hits += [f"gate `{gate}` has a row in the gates table and no artifact the artifact "
             "table assigns it to" for gate in sorted(set(rows) - set(declared))]
    return hits


def artifact_placeholder_hits(artifacts: dict[str, Artifact]) -> list[str]:
    """CR3 (v0.5.0): an artifact record that still carries a placeholder."""
    return [f"artifact '{art.name}': placeholder {p}"
            for art in sorted(artifacts.values(), key=lambda a: a.name)
            for p in placeholders(" | ".join(art.fields))]


RECIPE_STEP_FIELDS = ("Reads", "Creates", "Does", "Done when")


def recipe_hits(text: str) -> tuple[int, list[str]]:
    blocks = re.split(r"^### (?=Step )", text, flags=re.M)[1:]
    hits = []
    for block in blocks:
        title = block.splitlines()[0].strip()
        for label in RECIPE_STEP_FIELDS:
            if f"**{label}:**" not in block:
                hits.append(f"{title}: field '{label}' missing")
    return len(blocks), hits


def inflected(word: str) -> str:
    """Singular or plural of one English word ('criterion'/'criteria', 'gate'/'gates')."""
    if word.lower().endswith("erion"):
        return re.escape(word[:-2]) + "(?:on|a)"
    if word.lower().endswith("y") and len(word) > 1 and word[-2].lower() not in "aeiou":
        return re.escape(word[:-1]) + "(?:y|ies)"
    return re.escape(word) + PLURAL_SUFFIX


def component_pattern(term: str) -> str:
    """Whole-word pattern of a method component, each word singular or plural."""
    words = [inflected(word) for word in term.split()]
    return rf"(?<![{WORD_CHARS}])" + r"\s+".join(words) + rf"(?![{WORD_CHARS}])"


def missing_components(text: str, components: list[str]) -> list[str]:
    return [c for c in components if not re.search(component_pattern(c), text, flags=re.I)]


def heading_section(text: str, heading: str) -> str | None:
    """The level-2 section that opens with the heading line, up to the next
    level-2 heading (subsections included), or None when it is absent."""
    start = text.find("\n" + heading + "\n")
    if start < 0:
        return None
    body = text[start + 1:]
    nxt = re.search(r"^## (?!#)", body[len(heading):], flags=re.M)
    return body[: len(heading) + nxt.start()] if nxt else body


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rubric_hash(gates_text: str, gates_file: str = GATES_FILE) -> str:
    body = heading_section(gates_text, RUBRIC_HEADING)
    if body is None:
        raise InputError("section 'Rubric' missing from " + gates_file)
    return sha256_text(body)


def provenance_inputs(folder: Path, layout: dict) -> dict[str, str]:
    """The sha256 of the inputs that define what the gates measure (CR1,
    v0.5.0): the gate section of the gates file (its '## Gates' section,
    or the whole file when it has none, as in a cell's gates file) and the
    canon file. A sensitivity report records both, and p-sensitivity
    refuses a report made against other ones."""
    gates_text = read(folder / layout["artifacts"]["gates-and-rubric"])
    gates_section = heading_section(gates_text, GATES_HEADING)
    return {"gates": sha256_text(gates_text if gates_section is None else gates_section),
            "canon": sha256_text(read(folder / layout["artifacts"]["canon"]))}


def rubric_digest(folder: Path, layout: dict) -> str:
    """The sha256 of the rubric as the layout resolves it (v0.3.0): the
    dedicated rubric file when the layout names one (a cell's
    artifacts.rubric), else the '## Rubric' section of the gates file (the
    corpus convention, unchanged behavior)."""
    rubric = layout["artifacts"].get("rubric")
    if rubric is not None:
        return hashlib.sha256(read(folder / rubric).encode("utf-8")).hexdigest()
    gates_file = layout["artifacts"]["gates-and-rubric"]
    return rubric_hash(read(folder / gates_file), gates_file)


def note_contract_hits(notes_path: Path, artifact_names: set[str]) -> tuple[int, list[str]]:
    try:
        data = json.loads(read(notes_path))
    except json.JSONDecodeError as exc:
        raise InputError(f"notes: invalid JSON ({exc.msg}, line {exc.lineno})") from exc
    if not isinstance(data, list):
        raise InputError("notes: the file has to be a JSON list")
    hits = []
    for i, note in enumerate(data):
        if not isinstance(note, dict):
            hits.append(f"note {i}: not a JSON object")
            continue
        missing = [f for f in NOTE_FIELDS if f not in note]
        if missing:
            hits.append(f"note {i}: missing fields {missing}")
            continue
        if note["severity"] not in VALID_SEVERITIES:
            hits.append(f"note {i}: invalid severity '{note['severity']}'")
        if alias_target(note["target_artifact"]) not in artifact_names:
            hits.append(f"note {i}: target '{note['target_artifact']}' outside the graph")
        hits += note_round_and_status_hits(i, note)
    return len(data), hits


def note_round_and_status_hits(i: int, note: dict) -> list[str]:
    """The round is a string, as in the round record (IM21, v0.5.0); a
    positive integer is the legacy form the frozen ledger of round 1 keeps.
    The optional status and closed_in fields carry the state of a note."""
    rnd = note["round"]
    legacy = isinstance(rnd, int) and not isinstance(rnd, bool) and rnd >= 1
    hits = [] if legacy or (isinstance(rnd, str) and rnd) else \
        [f"note {i}: round is neither a non-empty string nor a legacy positive integer"]
    if "status" in note and note["status"] not in NOTE_STATUSES:
        hits.append(f"note {i}: status '{note['status']}' is not one of {', '.join(NOTE_STATUSES)}")
    if "closed_in" in note and not (isinstance(note["closed_in"], str) and note["closed_in"]):
        hits.append(f"note {i}: closed_in is not a version string")
    return hits


CLOSING_STATUSES = ("fixed", "out of scope")


def notes_status_hits(text: str, note_count: int) -> tuple[dict[str, int], list[str]]:
    """The state ledger of the notes (IM10, v0.5.0), one JSON line per note
    of the frozen ledger ('notes:<n>') or panel finding ('panel:<v>:<id>'):
    every note has exactly one line, every status is one of the four, and a
    closing status names the version that closed it. Returns the count per
    status and the hits; the shape of each line is p-contract-shape's."""
    counts = {status: 0 for status in NOTE_STATUSES}
    hits, seen = [], set()
    for n, line in enumerate((ln for ln in text.splitlines() if ln.strip()), 1):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise InputError(f"notes status: line {n} is not valid JSON ({exc.msg})") from exc
        ref, status = (entry.get(key) if isinstance(entry, dict) else None for key in ("ref", "status"))
        hits += status_line_hits(n, ref, status, entry, note_count, seen)
        if status in counts:
            counts[status] += 1
    hits += [f"note {k} of the ledger has no status line" for k in range(1, note_count + 1)
             if f"notes:{k}" not in seen]
    return counts, hits


def status_line_hits(n: int, ref: object, status: object, entry: object, note_count: int,
                     seen: set[str]) -> list[str]:
    """The hits of one line of the state ledger (see notes_status_hits)."""
    m = STATUS_REF.match(ref) if isinstance(ref, str) else None
    if m is None:
        return [f"line {n}: ref {ref!r} is neither 'notes:<n>' nor 'panel:<version>:<id>'"]
    hits = [f"line {n}: ref '{ref}' appears twice"] if ref in seen else []
    seen.add(ref)
    if m.group(1) and int(m.group(1)) > note_count:
        hits.append(f"line {n}: '{ref}' names no note of the ledger ({note_count} notes)")
    if status not in NOTE_STATUSES:
        hits.append(f"line {n}: status {status!r} is not one of {', '.join(NOTE_STATUSES)}")
    elif status in CLOSING_STATUSES and not (isinstance(entry, dict) and entry.get("closed_in")):
        hits.append(f"line {n}: status '{status}' names no version in closed_in")
    return hits


def sensitivity_row_hits(content: str, count: int) -> list[str]:
    """The table of a sensitivity report has to add up (CR1, v0.5.0): one
    row per perturbation, all measured, and as many 'caught' rows as its
    'Caught' line says. A report of a header and one line used to pass."""
    caught = re.search(r"Caught (\d+) of (\d+)\.", content)
    if caught is None:
        return []  # the caller reports the missing line as a tool failure
    results = SENSITIVITY_ROW_RESULT.findall(content)
    if int(caught.group(2)) != count or len(results) != count:
        return [f"the report measures {caught.group(2)} of {count} perturbations in "
                f"{len(results)} rows — re-run sensitivity.py with all inputs"]
    if results.count("caught") != int(caught.group(1)):
        return [f"the report says 'Caught {caught.group(1)}' and its table has "
                f"{results.count('caught')} rows caught — re-run sensitivity.py"]
    return []


def unimplemented_gate_message(gate: str) -> str:
    """The tool failure of a gate this validator does not implement (K8 of
    the panel that reviewed v0.4.2): it names what the distributed
    validator is, so a domain gate is not mistaken for a typo."""
    return (f"gate '{gate}' has no implementation in the validator. This validator measures "
            "documents (terms, sections, links, numbers about priors, contracts); a gate of "
            "the target's domain (a speedup, a mass, a cost) is 'contract + agent' (step 5 of "
            "the principle's recipe) or code of the cell's own, and this version has no "
            "extension point for it")


# ---------------------------------------------------------------- runner

class Checker:
    def __init__(self, folder: Path, case_texts: list[str] | None, forbidden: list[str] | None,
                 rubric_hash_file: Path | None, notes_file: Path | None,
                 layout: dict | None = None, registry: dict | None = None) -> None:
        self.folder = folder
        self.load_cases(case_texts or [], registry)
        self.forbidden = forbidden
        self.rubric_hash_file = rubric_hash_file
        self.notes_file = notes_file
        self.layout = layout if layout is not None else dict(DEFAULT_LAYOUT)
        # Every artifact path is resolved through the layout, in this
        # constructor only: no check reads a module constant for a path.
        self.canon_file = self.layout["artifacts"]["canon"]
        self.artifacts_file = self.layout["artifacts"]["artifacts"]
        self.gates_file = self.layout["artifacts"]["gates-and-rubric"]
        self.roles_dir = self.layout["artifacts"]["roles-dir"]
        self.sensitivity_file = self.layout["artifacts"]["sensitivity"]
        # The rubric source is a layout key too (v0.3.0): a cell names its
        # dedicated rubric file; the corpus has none and falls back to the
        # "## Rubric" section of the gates file.
        self.rubric_file = self.layout["artifacts"].get("rubric")
        self.parser = layout_parser(self.layout)
        check_parser_extension(self.parser, self.layout)
        self.experiments_file = self.layout["artifacts"]["experiments"]
        self.registry = registry
        self.load_controls()
        self.load_gates()
        self.roles = {role_name(p) for p in (folder / self.roles_dir).glob("*.md")}
        self.measurements: list[Measurement] = []
        self.notes: list[Note] = []
        self.current_artifact = ""
        self.cited_prior_ids: set[str] = set()
        self.handlers: dict[str, Callable[[str, str], None]] = {
            "p-terms": self.check_terms, "p-canon-link": self.check_canon_link,
            "p-anonymity": self.check_anonymity, "p-form": self.check_form,
            "p-size": self.check_size, "p-table": self.check_table,
            "p-sections": self.check_sections, "p-card": self.check_card,
            "p-limit": self.check_limit, "p-references": self.check_references,
            "p-prior": self.check_prior, "p-prior-mark": self.check_prior_mark,
            "p-prior-pin": self.check_prior_pin,
            "p-contract-shape": self.check_contract_shape,
            "p-recipe": self.check_recipe, "p-components": self.check_components,
            "p-efficacy-mark": self.check_efficacy_mark,
        }
        # Measured once, in check_global; the determinism measurement of the
        # instrument is rendered by main(), which needs two runs to say it.
        self.global_gates = set(GLOBAL_GATES)

    def load_cases(self, case_texts: list[str], registry: dict | None) -> None:
        """Identify each --case document by its sha256 against the registry
        (I14 of the panel): digest -> executed instance id. The pin compares
        the digests passed with the ones recorded; the number check of a
        [prior:<id>] unit reads the document identified as <id>, in the
        number format its registry entry declares (I16)."""
        self.cases_given = bool(case_texts)
        self.case_digests = {hashlib.sha256(text.encode("utf-8")).hexdigest()
                             for text in case_texts}
        executed = {inst.get("sha256"): inst for inst in (registry or {}).get("instances", [])
                    if inst.get("status") == "executed"}
        self.case_docs: dict[str, CaseDocument] = {}
        for text in case_texts:
            inst = executed.get(hashlib.sha256(text.encode("utf-8")).hexdigest())
            if inst is not None:
                number_format = inst.get("number_format")
                fmt = number_format if number_format in NUMBER_FORMATS else None
                self.case_docs[inst["id"]] = case_document(text, fmt)

    def load_controls(self) -> None:
        """The canon and the artifact list, through the layout's parser."""
        if self.parser == "builtin-json-canon":
            self.canon = load_canon_json(self.folder / self.canon_file)
            try:
                data = json.loads(read(self.folder / self.artifacts_file))
            except json.JSONDecodeError as exc:
                raise InputError(f"artifacts: invalid JSON ({exc.msg}, line {exc.lineno})") from exc
            self.artifacts = load_artifact_records(data)
        else:
            self.canon = load_canon(self.folder / self.canon_file)
            artifact_table = first_table(section(read(self.folder / self.artifacts_file), r"^Table$"))
            self.artifacts = load_artifact_table(artifact_table)

    def load_gates(self) -> None:
        """The gate rows and the size ranges of the gates file, and the gate
        map of the artifact list (the one source, v0.5.0)."""
        gates_text = read(self.folder / self.gates_file)
        self.gates_text = gates_text
        tables = gate_tables(gates_text)
        if not tables:
            raise InputError(f"{self.gates_file}: gate table not found")
        self.gate_table = tables[0]
        self.gate_rows = {clean_cell(r[0]): r for r in self.gate_table[1:]}
        self.gate_map = declared_gate_map(self.artifacts)
        for gate in sorted(set(self.gate_rows) | set(self.gate_map)):
            if gate not in (*BUILTIN_GATES, *GLOBAL_GATES) and not PLACEHOLDER.fullmatch(gate):
                raise InputError(unimplemented_gate_message(gate))
        size_table = first_table(section(gates_text, r"^Size ranges$", 3))
        try:
            self.size_ranges = {clean_cell(r[0]): (int(r[1]), int(r[2])) for r in size_table[1:]}
        except (ValueError, IndexError) as exc:
            raise InputError(f"{self.gates_file}: invalid size range row ({exc})") from exc

    def row_number(self, gate: str, cell: str, pattern: re.Pattern[str]) -> int | None:
        """A number a gate's own row declares (IM16): the minimum words of a
        justification, the minimum steps of a recipe. None when the gate has
        no row or the row does not state it: the gate is then not measured."""
        row = self.gate_rows.get(gate)
        if row is None:
            return None
        i_cell = column(self.gate_table, cell)
        m = pattern.search(cell_at(row, i_cell, f"{self.gates_file}: the row of {gate}"))
        return int(m.group(1)) if m else None

    def files_of(self, artifact: str) -> list[str]:
        out = []
        for pattern in self.artifacts[artifact].files:
            if pattern.startswith("../"):
                # A pattern with '../' is a literal path out of the folder
                # (no wildcard expansion), so the corpus document above the
                # folder can be measured without sweeping outside it.
                literal = self.folder / pattern
                if literal.is_file():
                    out.append(literal.relative_to(self.folder).as_posix())
                continue
            matches = sorted(p.relative_to(self.folder).as_posix() for p in self.folder.glob(pattern))
            out.extend(matches)
        return out

    def record(self, doc: str, gate: str, magnitude: str, limit: str, hits: list[str],
               severity: str = "high", target: str | None = None) -> None:
        self.measurements.append(Measurement(doc, gate, magnitude, limit, not hits))
        for hit in hits[:MAX_NOTES_PER_GATE]:
            self.notes.append(Note(target or self.current_artifact, severity, f"{gate}: {hit}", doc))
        if len(hits) > MAX_NOTES_PER_GATE:
            self.notes.append(Note(target or self.current_artifact, severity,
                                   f"{gate}: {len(hits) - MAX_NOTES_PER_GATE} more notes omitted", doc))

    def pending(self, doc: str, gate: str, magnitude: str, limit: str) -> None:
        self.measurements.append(Measurement(doc, gate, magnitude, limit, None))

    def run(self) -> None:
        doc_gates: dict[str, list[tuple[str, str]]] = {}
        for gate, arts in self.gate_map.items():
            for art in arts:
                if art not in self.artifacts:
                    continue
                for doc in self.files_of(art):
                    doc_gates.setdefault(doc, []).append((gate, art))
        # The pin gate is self-collecting: the ids it has to pin are the
        # [prior:<id>] labels cited in the documents that carry p-prior,
        # whichever order the gates run in.
        for doc, pairs in doc_gates.items():
            if any(gate == "p-prior" for gate, _ in pairs):
                self.cited_prior_ids |= set(PRIOR_TAG.findall(read(self.folder / doc)))
        if not doc_gates:
            # C4a of the panel: a run that measures no documents is green
            # for nothing; a scaffolded cell fails here until it has real
            # artifacts ("files of the empty template match no file").
            self.notes.append(Note("artifacts", "blocking",
                                   "no documents were measured; a production with "
                                   "no documents is not green", self.artifacts_file))
        for doc in sorted(doc_gates):
            text = read(self.folder / doc)
            for gate, art in sorted(doc_gates[doc]):
                self.current_artifact = art
                self.check(doc, gate, text)
        self.check_global()

    def check(self, doc: str, gate: str, text: str) -> None:
        if gate in self.global_gates:
            return
        handler = self.handlers.get(gate)
        if handler is None:
            raise InputError(unimplemented_gate_message(gate))
        handler(doc, text)

    def pending_empty(self, doc: str, gate: str, canon_list: str, limit: str) -> None:
        """CR3 (v0.5.0): a gate whose object is a list of the canon, with the
        list empty, measured nothing; it is pending with the reason, never a
        pass of 0 of 0 (the scaffold ships every such list empty)."""
        self.pending(doc, gate, f"not measured (the canon's '{canon_list}' list is empty)", limit)

    # One method per document gate; each records exactly one measurement.

    def check_terms(self, doc: str, text: str) -> None:
        if doc.startswith(FROZEN_LEDGER_PREFIX):
            # Exemption by design: vocabulary rules govern living documents;
            # the review ledger is frozen history and is never edited to
            # satisfy a later vocabulary (regression turned into a rule).
            self.record(doc, "p-terms", "exempt by design (frozen ledger)", "0", [])
            return
        if not self.canon.avoid_terms:
            self.pending_empty(doc, "p-terms", "terms to avoid", "0")
            return
        body = text
        if doc == self.canon_file:
            # Up to the next level-2 heading, or the end (v0.5.0): a canon
            # whose avoid table was its last section counted its own table.
            body = re.sub(r"^## Terms to avoid$.*?(?=^## |\Z)", "", text, flags=re.S | re.M)
        found = count_avoid_terms(body, self.canon.avoid_terms)
        total = sum(n for _, n in found)
        self.record(doc, "p-terms", str(total), "0", [f"'{t}' x{n}" for t, n in found])

    def check_canon_link(self, doc: str, text: str) -> None:
        resolved, unresolved = canon_links(self.folder / doc, text, self.folder / self.canon_file)
        hits = [f"link to the canon does not resolve: `{target}`" for target in unresolved]
        if not resolved and not unresolved:
            hits.append("no link to the canon")
        self.record(doc, "p-canon-link", f"{resolved} resolved, {len(unresolved)} unresolved",
                    "\u2265 1 resolved, 0 unresolved", hits)

    def check_anonymity(self, doc: str, text: str) -> None:
        hits = anonymity_hits(text, self.forbidden)
        if not self.forbidden and not hits:
            # An empty list measures no identifier either (v0.5.0): it used
            # to turn the identifier half from pending into a pass.
            reason = "no list" if self.forbidden is None else "the list is empty"
            self.pending(doc, "p-anonymity",
                         f"0 paths and dates; identifiers not measured ({reason})", "0")
            return
        self.record(doc, "p-anonymity", str(len(hits)), "0", hits)

    def check_form(self, doc: str, text: str) -> None:
        hits = form_hits(text)
        self.record(doc, "p-form", str(len(hits)), "0", hits)

    def check_size(self, doc: str, text: str) -> None:
        words = len(text.split())
        bounds = self.size_ranges.get(doc)
        if bounds is None:
            self.record(doc, "p-size", str(words), "no range", [f"{doc} has no declared range"])
            return
        low, high = bounds
        ok = low <= words <= high
        self.record(doc, "p-size", str(words), f"{low} to {high}",
                    [] if ok else [f"{words} words outside {low} to {high}"])

    def check_table(self, doc: str, text: str) -> None:
        rows = self.canon.instantiation_rows
        if not rows:
            self.pending_empty(doc, "p-table", "instantiation table rows", "all rows, 0 empty")
            return
        found, empty, hits = instantiation_hits(text, rows)
        self.record(doc, "p-table", f"{found}/{len(rows)}, {empty} empty",
                    f"{len(rows)}/{len(rows)}, 0 empty", hits)

    def check_sections(self, doc: str, text: str) -> None:
        n = len(self.canon.instance_sections)
        if not n:
            self.pending_empty(doc, "p-sections", "mandatory sections", "all sections")
            return
        titles = heading_titles(text)
        missing = [s for s in self.canon.instance_sections if s.lower() not in titles]
        self.record(doc, "p-sections", f"{n - len(missing)}/{n}", f"{n}/{n}",
                    [f"section '{s}' missing" for s in missing])

    def check_card(self, doc: str, text: str) -> None:
        if not self.canon.card_fields:
            self.pending_empty(doc, "p-card", "role card fields", "0")
            return
        hits = card_hits(text, self.canon.card_fields,
                         whole_document=doc.startswith(self.roles_dir + "/"))
        missing = sum(1 for hit in hits if hit.endswith("' missing"))
        self.record(doc, "p-card", f"{missing} fields missing, {len(hits) - missing} placeholders",
                    "0", hits)

    def check_limit(self, doc: str, text: str) -> None:
        if not self.canon.limit_tags:
            # K4 of the panel: with the list empty, every justification was
            # reported "without an origin label" — a false red.
            self.pending_empty(doc, "p-limit", "origin labels", "0")
            return
        min_words = self.row_number("p-limit", "Magnitude", MIN_WORDS_IN_ROW)
        if min_words is None:
            self.pending(doc, "p-limit", "not measured (the gate table's row of p-limit "
                         "declares no minimum of words, 'fewer than N words')", "0")
            return
        hits = limit_hits(text, self.canon.limit_tags, min_words)
        self.record(doc, "p-limit", str(len(hits)), "0", hits)

    def check_references(self, doc: str, text: str) -> None:
        roles = self.roles | {OWNER_HUMAN}
        if doc == self.artifacts_file:
            hits = reference_hits(self.artifacts, roles, []) + artifact_placeholder_hits(self.artifacts)
        elif doc == self.gates_file:
            hits = (reference_hits(self.artifacts, roles, gate_tables(text))
                    + gate_map_hits(self.artifacts, self.gate_table))
        elif doc.startswith(self.roles_dir + "/"):
            hits = note_target_hits(text, set(self.artifacts), doc)
        else:
            hits = instance_reference_hits(text)
        severity = "blocking" if any(h.startswith("cycle") for h in hits) else "high"
        self.record(doc, "p-references", str(len(hits)), "0", hits, severity=severity)

    def check_prior(self, doc: str, text: str) -> None:
        if self.registry is None:
            self.pending(doc, "p-prior", "not measured (no instance registry)", "0")
            return
        ids = {inst["id"] for inst in self.registry["instances"]}
        tags = PRIOR_TAG.findall(text)
        unknown = sorted({i for i in tags if i not in ids})
        hits = [f"'{i}' is not an instance registered in the registry" for i in unknown]
        label_mag = f"{len(tags)} labels, {len(unknown)} unregistered"
        if not self.cases_given:
            # Without the prior document the labels are measured, the numbers
            # are not: the gate is pending, never a pass.
            magnitude = f"{label_mag}; numbers not measured (no prior document)"
            if unknown:
                self.record(doc, "p-prior", magnitude, "0", hits, severity="blocking")
            else:
                self.pending(doc, "p-prior", magnitude, "0")
            return
        check = multi_prior_findings(text, self.case_docs, self.canon.recorded_facts,
                                     instance_ids_of(self.registry))
        hits += check.hits
        magnitude = (f"{label_mag}, {check.checked} numbers and {check.references} section "
                     f"references checked, {len(check.hits)} unverified")
        if check.unmeasured:
            # I14: a cited prior with no --case document is pending by name.
            magnitude += (f"; numbers of {', '.join(sorted(check.unmeasured))} not measured "
                          "(no --case document identified as that prior)")
            if not hits:
                self.pending(doc, "p-prior", magnitude, "0")
                return
        self.record(doc, "p-prior", magnitude, "0", hits, severity="blocking")

    def check_prior_mark(self, doc: str, text: str) -> None:
        if not self.canon.prior_triggers:
            self.pending_empty(doc, "p-prior-mark", "prior-statement triggers", "0")
            return
        hits = prior_mark_hits(text, self.canon.prior_triggers)
        self.record(doc, "p-prior-mark", str(len(hits)), "0", hits)

    def check_prior_pin(self, doc: str, text: str) -> None:
        try:
            registry = json.loads(text)
            validate_registry(registry)
        except json.JSONDecodeError as exc:
            raise InputError(f"registry: invalid JSON ({exc.msg}, line {exc.lineno})") from exc
        hits, cited = pin_findings(self.cited_prior_ids, registry,
                                   self.case_digests if self.cases_given else None)
        if not self.cases_given:
            # A pin that passes without the prior document would be the
            # owner-only proof this gate exists to end.
            self.pending(doc, "p-prior-pin",
                         f"{cited} executed priors cited; not measured (no prior document)",
                         "equal")
            return
        self.record(doc, "p-prior-pin", f"{cited} executed priors pinned", "equal",
                    hits, severity="blocking")

    def check_contract_shape(self, doc: str, text: str) -> None:
        if doc == self.artifacts_file:
            refs = schema_refs(self.artifacts)
            hits = schema_ref_hits(refs, self.folder)
            self.record(doc, "p-contract-shape",
                        f"{len(refs)} schema cells, {len(hits)} broken", "0 broken", hits)
            return
        if doc.endswith(".schema.json"):
            self.check_schema_census(doc, text)
            return
        art = self.artifacts.get(self.current_artifact)
        schema_ref = art.schema if art is not None else ""
        if not schema_ref:
            self.record(doc, "p-contract-shape", "no schema declared", "no schema", [])
            return
        schema_path = self.folder / schema_ref
        if not schema_path.exists():
            self.record(doc, "p-contract-shape", "1 broken", "0 broken",
                        [f"schema '{schema_ref}' does not exist"])
            return
        try:
            schema = json.loads(read(schema_path))
        except json.JSONDecodeError as exc:
            self.record(doc, "p-contract-shape", "1 broken", "0 broken",
                        [f"schema '{schema_ref}' is not valid JSON ({exc.msg})"])
            return
        if doc.endswith(".jsonl"):
            hits = []
            lines = [ln for ln in text.splitlines() if ln.strip()]
            for i, line in enumerate(lines, 1):
                hits += validate_data_text(line, schema, f"line {i}")
            self.record(doc, "p-contract-shape",
                        f"{len(lines)} lines, {len(hits)} violations", "0", hits)
            return
        hits = validate_data_text(text, schema, "$")
        if doc == self.layout["registry"]:
            hits += registry_status_hits(text)
        self.record(doc, "p-contract-shape", f"{len(hits)} violations", "0", hits)

    def check_schema_census(self, doc: str, text: str) -> None:
        """A contract file has to parse and use only the keywords the
        stdlib mini-validator applies (a keyword outside the subset is a
        note, never silently ignored as if fully validated)."""
        try:
            schema = json.loads(text)
        except json.JSONDecodeError as exc:
            self.record(doc, "p-contract-shape", "1 broken", "0 broken",
                        [f"schema is not valid JSON ({exc.msg})"])
            return
        unsupported = unsupported_keywords(schema)
        hits = [f"keyword '{kw}' is outside the subset the validator applies"
                for kw in unsupported]
        declared = schema.get(CONTRACT_VERSION_KEY) if isinstance(schema, dict) else None
        if declared != CONTRACT_VERSION:
            hits.append(f"the contract declares {CONTRACT_VERSION_KEY} {declared!r}; this "
                        f"validator reads contract version '{CONTRACT_VERSION}' (IM21)")
        self.record(doc, "p-contract-shape",
                    f"{len(schema_keyword_set(schema))} keywords, "
                    f"{len(unsupported)} unsupported", "0 unsupported", hits)

    def check_efficacy_mark(self, doc: str, text: str) -> None:
        """I10 of the panel: the method's own doctrine of evidence applied to
        the claims about the method; an [experiment:<id>] label has to cite
        an executed experiment of the experiments record (S4, v0.4.1)."""
        if doc == self.canon_file:
            # The canon's table is the definition of the triggers, exempt.
            self.record(doc, "p-efficacy-mark", "exempt by design (the definition page)", "0", [])
            return
        text, hits = self.efficacy_scope(doc, text)
        hits += efficacy_mark_hits(text, self.canon.efficacy_triggers)
        record = self.folder / self.experiments_file
        statuses = experiment_statuses(read(record)) if record.is_file() else {}
        for eid in sorted(set(EXPERIMENT_TAG.findall(strip_code(text)))):
            hits += experiment_label_hits(eid, statuses, self.experiments_file)
        if not self.canon.efficacy_triggers and not hits:
            # S3 of the review: with no trigger list nothing was measured.
            self.pending(doc, "p-efficacy-mark",
                         "not measured (the canon lists no efficacy triggers)", "0")
            return
        self.record(doc, "p-efficacy-mark", str(len(hits)), "0", hits)

    def efficacy_scope(self, doc: str, text: str) -> tuple[str, list[str]]:
        """The part of an append-only document the gate reads (CR7, v0.5.0):
        from the heading the canon declares for it on; the units above are
        history, exempt like the frozen ledger. A declared heading that is
        not in the document is a finding, never an exemption of the whole."""
        heading = self.canon.efficacy_starts.get(doc)
        if heading is None:
            return text, []
        scoped = from_heading(text, heading)
        if scoped is None:
            return text, [f"the heading '{heading}' the canon declares as the start of the "
                          "measured part is not a line of the document"]
        return scoped, []

    def check_recipe(self, doc: str, text: str) -> None:
        min_steps = self.row_number("p-recipe", "Limit", MIN_STEPS_IN_ROW)
        if min_steps is None:
            self.pending(doc, "p-recipe", "not measured (the gate table's row of p-recipe "
                         "declares no minimum of steps, '\u2265 N steps')", "0 missing")
            return
        steps, hits = recipe_hits(text)
        if steps < min_steps:
            hits.append(f"{steps} steps, fewer than {min_steps}")
        self.record(doc, "p-recipe", f"{steps} steps, {len(hits)} missing",
                    f"\u2265 {min_steps} steps, 0 missing", hits)

    def check_components(self, doc: str, text: str) -> None:
        components = self.canon.components
        if not components:
            self.pending_empty(doc, "p-components", "method components", "all components")
            return
        missing = missing_components(text, components)
        n = len(components)
        self.record(doc, "p-components", f"{n - len(missing)}/{n}", f"{n}/{n}",
                    [f"component '{c}' not named" for c in missing])

    def check_global(self) -> None:
        if self.rubric_hash_file is None or not self.rubric_hash_file.exists():
            self.pending(self.rubric_doc(), "p-frozen-rubric", "rubric not frozen yet", "equal")
        else:
            recorded = read(self.rubric_hash_file).split()
            if not recorded:
                raise InputError(f"{self.rubric_hash_file.name} is empty")
            if recorded[0] == RUBRIC_UNFROZEN:
                # The placeholder a scaffolded cell ships: no pin yet.
                self.pending(self.rubric_doc(), "p-frozen-rubric", "rubric not frozen yet", "equal")
            else:
                current = self.current_rubric_digest()
                hits = [] if recorded[0] == current else ["the 'Rubric' section changed after being frozen"]
                self.record(self.rubric_doc(), "p-frozen-rubric", "equal" if not hits else "different", "equal",
                            hits, severity="blocking", target="review")
        self.check_declared_artifacts()
        self.check_sensitivity_report()
        self.check_notes()

    def check_notes(self) -> None:
        """p-notes: the note ledger passed with --notes, and the state
        ledger of its notes (IM10, v0.5.0) at the layout key notes-status."""
        status_file = self.layout["artifacts"]["notes-status"]
        if self.notes_file is None:
            # I4 of the panel: the gate stays visible without --notes — a
            # pending with its reason, never a row that quietly disappears.
            self.pending("open-notes", "p-notes",
                         "not measured (notes not supplied; the note ledger "
                         "was not measured)", "0 invalid")
            self.pending(status_file, "p-notes", "not measured (notes not supplied; the "
                         "state of the notes needs the ledger)", "every note tracked")
            return
        rel = Path(os.path.relpath(self.notes_file.resolve(), self.folder)).as_posix()
        count, hits = note_contract_hits(self.notes_file, set(self.artifacts))
        self.record(rel, "p-notes", f"{count} notes, {len(hits)} invalid", "0 invalid", hits,
                    target="open-notes")
        self.check_notes_status(status_file, count)

    def check_notes_status(self, status_file: str, note_count: int) -> None:
        path = self.folder / status_file
        if not path.is_file():
            self.pending(status_file, "p-notes", f"not measured (no state ledger at "
                         f"'{status_file}'; the layout key artifacts.notes-status points "
                         "there)", "every note tracked")
            return
        counts, hits = notes_status_hits(read(path), note_count)
        magnitude = ", ".join(f"{n} {status}" for status, n in counts.items()) + \
            f"; {len(hits)} invalid"
        self.record(status_file, "p-notes", magnitude, "every note tracked, 0 invalid", hits,
                    target="open-notes")

    def rubric_doc(self) -> str:
        """The document the frozen-rubric gate reports against: the cell's
        rubric file when the layout names one, else the gates file."""
        return self.rubric_file if self.rubric_file is not None else self.gates_file

    def current_rubric_digest(self) -> str:
        """The sha256 of the rubric as this run resolves it (same rule as
        rubric_digest, reusing the gates text already read)."""
        if self.rubric_file is not None:
            return hashlib.sha256(read(self.folder / self.rubric_file).encode("utf-8")).hexdigest()
        return rubric_hash(self.gates_text, self.gates_file)

    def check_declared_artifacts(self) -> None:
        """C2 of the panel: an artifact declared in the table whose files
        match nothing is never silently unmeasured — a real artifact (not
        'proposed') is blocking; a proposed one is pending with its reason.
        A JSON artifact declared with no paths at all is also visible (S3 of
        the v0.3.0 review): a pending that says so, never a silent skip."""
        for name in sorted(self.artifacts):
            artifact = self.artifacts[name]
            if not artifact.files:
                self.pending(name, "p-declared",
                             "declared without paths; no files to measure",
                             "at least one path")
                continue
            if self.files_of(name):
                continue
            joined = ", ".join(artifact.files)
            if artifact.proposed:
                self.pending(joined, "p-declared", "proposed, not yet produced", "exists")
            else:
                self.record(joined, "p-declared", "missing", "exists",
                            [f"declared artifact missing: {joined}"],
                            severity="blocking", target=name)

    def check_sensitivity_report(self) -> None:
        # The path comes from the layout (v0.2.3): the hardcoded directory
        # assumption left p-sensitivity pending in every scaffolded cell
        # (medium finding of instance 004, the first real run of v0.2).
        sens = self.folder / self.sensitivity_file
        if not sens.exists():
            self.pending(self.sensitivity_file, "p-sensitivity",
                         f"not measured (no sensitivity report at "
                         f"'{self.sensitivity_file}'; the layout key "
                         f"artifacts.sensitivity points there)", SENSITIVITY_LIMIT)
            return
        content = read(sens)
        self.current_artifact = "instrument-validator"
        provenance = self.sensitivity_provenance_hits(content, sens)
        if provenance:
            self.record(self.sensitivity_file, "p-sensitivity", "provenance mismatch",
                        "re-run sensitivity.py", provenance, severity="blocking")
            return
        m = re.search(r"Caught (\d+) of (\d+)\.", content)
        if not m:
            raise InputError(f"{self.sensitivity_file} has no line 'Caught X of Y.'")
        missed = int(m.group(2)) - int(m.group(1))
        covered, assigned, uncovered = self.sensitivity_coverage(content)
        magnitude = f"{covered} of {assigned} gates covered, {missed} missed of {m.group(2)}"
        if missed == 0 and uncovered:
            # A gate without a perturbation is not measured by the report:
            # pending with the reason, never a pass (M1).
            self.pending(self.sensitivity_file, "p-sensitivity",
                         f"not measured ({magnitude}; gates without a perturbation: "
                         + ", ".join(f"`{gate}`" for gate in uncovered) + ")",
                         SENSITIVITY_LIMIT)
            return
        self.record(self.sensitivity_file, "p-sensitivity", magnitude, SENSITIVITY_LIMIT,
                    [] if missed == 0 else [f"{missed} perturbations missed"])

    def sensitivity_coverage(self, content: str) -> tuple[int, int, list[str]]:
        """M1 of the review of v0.5.0: one perturbation and four assigned
        gates gave '0 missed of 1' and passed. The gates the artifact table
        assigns (but this gate and the measurements m-*) are compared with
        the expected gates of the report's rows. Returns the number covered,
        the number assigned and the assigned gates without a perturbation."""
        assigned = sorted(gate for gate in self.gate_map
                          if gate != SENSITIVITY_GATE and not gate.startswith(MEASUREMENT_PREFIX))
        perturbed = set(SENSITIVITY_ROW_GATE.findall(content))
        uncovered = [gate for gate in assigned if gate not in perturbed]
        return len(assigned) - len(uncovered), len(assigned), uncovered

    def sensitivity_provenance_hits(self, content: str, sens: Path) -> list[str]:
        """C3 of the panel: a report that says 'Caught 14 of 14.' proves
        nothing unless this instrument and this perturbation set produced it.
        The header records the sha256 of the validator that ran, the sha256
        of the gate section and of the canon (v0.5.0, CR1) and the ids and
        count of the perturbations; any divergence is blocking, and so is a
        table whose rows do not add up to its 'Caught' line."""
        sha_m = SENSITIVITY_SHA_LINE.search(content)
        set_m = SENSITIVITY_SET_LINE.search(content)
        if sha_m is None or set_m is None:
            return ["the sensitivity report carries no provenance header; it was "
                    "not produced by this instrument — re-run sensitivity.py"]
        neighbor = sens.parent / "validator.py"
        if not neighbor.exists():
            neighbor = Path(__file__).resolve().with_name("validator.py")
        if sha_m.group(1) != hashlib.sha256(neighbor.read_bytes()).hexdigest():
            return ["the sensitivity report was produced by a different "
                    "validator (sha256 mismatch) — re-run sensitivity.py"]
        return (self.input_digest_hits(content) or self.perturbation_set_hits(set_m)
                or sensitivity_row_hits(content, int(set_m.group(1))))

    def input_digest_hits(self, content: str) -> list[str]:
        """The gate section and the canon the report was made against."""
        current = provenance_inputs(self.folder, self.layout)
        hits = []
        for name, pattern in SENSITIVITY_INPUT_LINES.items():
            m = pattern.search(content)
            if m is None:
                hits.append(f"the sensitivity report records no sha256 of the {name} (a "
                            "report from before v0.5.0) — re-run sensitivity.py")
            elif m.group(1) != current[name]:
                hits.append(f"the {name} changed since the sensitivity report was made "
                            "(sha256 mismatch): what the gates measure is not what was "
                            "perturbed — re-run sensitivity.py")
        return hits

    def perturbation_set_hits(self, set_m: re.Match[str]) -> list[str]:
        count = int(set_m.group(1))
        ids = {part.strip() for part in set_m.group(2).split(",")}
        expected = {pert.name for pert in self.perturbation_set()}
        if count != len(expected):
            return [f"the report names {count} perturbations, the instrument "
                    f"runs {len(expected)} — re-run sensitivity.py"]
        if ids != expected:
            missing = ", ".join(sorted(expected - ids))
            extra = ", ".join(sorted(ids - expected))
            return [f"the report names a different perturbation set "
                    f"(missing: {missing or '—'}; unknown: {extra or '—'}) "
                    "— re-run sensitivity.py"]
        return []

    def perturbation_set(self) -> list:
        """The perturbations of this production, from the one place that
        reads them (the sensitivity script): the cell's data file the layout
        key artifacts.perturbations names, or the corpus set in the script.
        A missing script is a tool failure (IM17), never a traceback."""
        try:
            import sensitivity
        except ImportError as exc:
            raise InputError("p-sensitivity needs sensitivity.py next to validator.py, "
                             f"which reads the perturbation set ({exc})") from exc
        try:
            return list(sensitivity.perturbation_set(self.folder, self.layout))
        except sensitivity.PerturbationDataError as exc:
            raise InputError(str(exc)) from exc

    def pending_by_gate(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for m in self.measurements:
            if m.passed is None:
                counts[m.gate] = counts.get(m.gate, 0) + 1
        return dict(sorted(counts.items()))

    def unaccepted_pending(self, allowed: frozenset[str]) -> dict[str, int]:
        """IM15 (v0.5.0): the pending gates the caller did not accept with
        --allow-pending; any of them makes the exit 4, never 0."""
        return {gate: n for gate, n in self.pending_by_gate().items() if gate not in allowed}

    def pending_lines(self, allowed: frozenset[str]) -> list[str]:
        def listing(counts: dict[str, int]) -> str:
            return ", ".join(f"`{g}` ({n} {'row' if n == 1 else 'rows'})"
                             for g, n in counts.items()) or "none"
        accepted = {g: n for g, n in self.pending_by_gate().items() if g in allowed}
        unaccepted = self.unaccepted_pending(allowed)
        return ["", f"Pending accepted by the caller (--allow-pending): {listing(accepted)}.",
                f"Pending not accepted: {listing(unaccepted)}"
                + ("; the run exits 4 unless a note exits 1." if unaccepted else ".")]

    def report(self, allowed: frozenset[str] = frozenset()) -> str:
        lines = ["# Validator report", "",
                 f"Generated by `{VALIDATOR_DIR}/validator.py`. Deterministic: no date, relative paths,",
                 "sorted by document and gate. The prior method document and the list of forbidden",
                 "identifiers are passed as arguments and are not quoted here. A pending gate was not",
                 "measured, because its input was not provided; it is neither a pass nor a fail.", "",
                 "## Measurements", "",
                 "| Document | Gate | Magnitude | Limit | Result |",
                 "| --- | --- | --- | --- | --- |"]
        for m in sorted(self.measurements, key=lambda m: (m.document, m.gate)):
            result = "pending" if m.passed is None else ("pass" if m.passed else "fail")
            lines.append(f"| `{m.document}` | `{m.gate}` | {m.magnitude} | {m.limit} | {result} |")
        lines += self.pending_lines(allowed)
        lines += ["", "## Instrument measurement", "",
                  "`m-determinism` measures the instrument (this validator: two runs",
                  "on the same input produce the same report), not an artifact of the",
                  "corpus; it is a measurement, not a gate, and it is not measured",
                  "unless --determinism was passed.", "",
                  "| Measurement | Artifact | Magnitude | Expected | Result |",
                  "| --- | --- | --- | --- | --- |",
                  determinism_row("pending", "not measured (no --determinism flag)")]
        counts = {s: sum(1 for n in self.notes if n.severity == s) for s in VALID_SEVERITIES}
        lines += ["", "## Notes", "",
                  "Count: " + ", ".join(f"{counts[s]} {s}" for s in reversed(VALID_SEVERITIES)) + ".", ""]
        if self.notes:
            lines += ["| Target | Severity | Text | Evidence |", "| --- | --- | --- | --- |"]
            for n in sorted(set(self.notes), key=Note.sort_key):
                lines.append(f"| `{n.target}` | {n.severity} | {n.text.replace('|', '/')} | `{n.evidence}` |")
        else:
            lines.append("No notes.")
        return "\n".join(lines) + "\n"

    def blocking(self) -> bool:
        return any(n.severity in BLOCKING for n in self.notes)


# ---------------------------------------------------------------- self-test

class SelfTest:
    """Counts the checks so that the self-test reports how many it ran."""

    def __init__(self) -> None:
        self.count = 0

    def expect(self, condition: object, label: str) -> None:
        self.count += 1
        if not condition:
            raise SelfTestError(f"self-test case failed: {label}")


def self_test() -> int:
    """One positive and one negative case per rule; each root-cause fix adds one."""
    t = SelfTest()
    # p-terms: whole word, case-insensitive, outside code and link targets.
    t.expect(count_avoid_terms("a Pipeline here", ["pipeline"]) == [("pipeline", 1)], "avoid-word found")
    t.expect(count_avoid_terms("the `sprint` in code, [x](sprint.md) and a sprinter", ["sprint"]) == [],
             "avoid-word in code, link target or inside a longer word")
    t.expect(count_avoid_terms("two tickets", ["ticket"]) == [("ticket", 1)], "plural of an avoid-word")
    t.expect(count_avoid_terms("the ruler and the ruler\u00E9", ["ruler"]) == [("ruler", 1)],
             "accented letters are word characters")
    t.expect(split_alternatives("client / sponsor") == ["client", "sponsor"], "avoid cell alternatives")
    t.expect(split_alternatives("and/or") == ["and/or"], "a slash without spaces is not a separator")
    # p-anonymity.
    t.expect(anonymity_hits("see /etc/x/y", []) != [], "absolute path")
    t.expect(anonymity_hits("120 km/h, and/or, 1/255, ../01-principle.md, 03-roles/x.md", []) == [],
             "relative paths, units and fractions are not absolute paths")
    t.expect(anonymity_hits("v1 of 2027 and March 2027", []) == [], "a year alone is not a date")
    t.expect(anonymity_hits("made on 3 May", []) != [], "authoring date, day first")
    t.expect(anonymity_hits("written on May 3", []) != [], "authoring date, month first")
    # Sample dates are assembled at run time, so that the source itself carries no date.
    iso_sample, dmy_sample = "-".join(("2000", "01", "02")), "/".join(("02", "01", "2000"))
    t.expect(anonymity_hits(f"generated on {iso_sample}", []) != [], "authoring date, ISO")
    t.expect(anonymity_hits("decisions made on the brief", []) == [], "'made on' without a date")
    t.expect(anonymity_hits(f"on {dmy_sample}", []) != [], "day/month/year date")
    t.expect(anonymity_hits("built by acme-lab", ["acme-lab"]) != [], "forbidden identifier")
    t.expect(anonymity_hits("built by acme-labs", ["acme-lab"]) == [], "forbidden identifier is whole word")
    # p-form.
    t.expect(form_hits("text <b>x</b>") != [], "HTML tag")
    t.expect(form_hits("a `<b>` in code and x \u2264 2 -> y") == [], "tag in code, arrows, comparisons")
    t.expect(form_hits("```python\nx\n```\n") != [], "fenced block without text")
    t.expect(form_hits("```text\nx\n```\n") == [], "fenced block marked text")
    # p-prior: numbers in [prior:...] units, decimal point/comma normalised.
    case = case_number_index("49 items, 0,546 s and 1.200 notes; section 1.10")
    t.expect(prior_number_hits("there are 49 artifacts [prior:000-demo]", case) == [], "prior number present")
    t.expect(prior_number_hits("there are 48 artifacts [prior:000-demo]", case) != [], "prior number absent")
    t.expect(prior_number_hits("there are 48 artifacts", case) == [], "unmarked unit is not checked")
    t.expect(prior_number_hits("- it gave 48 notes, and the\n  two were false [prior:000-demo]", case) != [],
             "number wrapped onto the marked line (units, not lines)")
    t.expect(prior_number_hits("there are 46 artifacts [prior:000-demo]", case_number_index("146 items")) != [],
             "46 does not match inside 146")
    t.expect(prior_number_hits("a drift of 0.546 s [prior:000-demo]", case) == [], "decimal point equals decimal comma")
    t.expect(prior_number_hits("p95 of 0.39 s [prior:000-demo]", case_number_index("39 s")) != [],
             "0.39 is not 39")
    t.expect(prior_number_hits("it is 39 [prior:000-demo]", case_number_index("0,39 s")) != [], "39 is not 0,39")
    t.expect(prior_number_hits("1,200 notes [prior:000-demo]", case) == [], "English thousands equal Portuguese thousands")
    t.expect(prior_number_hits("section 1.10 [prior:000-demo]", case) == [], "section number matches itself")
    t.expect(prior_number_hits("0.10 s [prior:000-demo]", case_number_index("0,10 s")) == [], "trailing zero kept")
    t.expect(prior_number_hits("0.1 s [prior:000-demo]", case_number_index("0,10 s")) == [], "trailing zero dropped")
    t.expect(prior_number_hits("12,5 s [prior:000-demo]", case_number_index("12.5 s")) == [], "comma in the document")
    t.expect(prior_number_hits("1,200 [prior:000-demo]", case_number_index("1\u00A0200 notes")) == [],
             "no-break space as thousands separator")
    t.expect(prior_number_hits("the `1.11` code [prior:000-demo]", case) == [], "numbers in code are not checked")
    t.expect(prior_number_hits("```text\na\nb\n```\n\nit gave 48 [prior:000-demo]", case) == [
        "line 6: '48' is not in the prior method document"], "line numbers survive a fenced block")
    t.expect(prior_number_hits("the instance [prior:000-demo] gave 49", case) == [],
             "digits inside the mark are never checked")
    t.expect(PRIOR_TAG.findall("one [prior:000-demo] and [prior:001-other]") ==
             ["000-demo", "001-other"], "prior ids extracted")
    # p-prior, section check: a number with a recorded-fact row is verified
    # in the union of the sections that row cites.
    facts = [RecordedFact(numbers=["49"], sections=["2.1"]),
             RecordedFact(numbers=["38", "2"], sections=["14"])]
    sections = {"2.1": case_number_index("the graph had 49 artifacts"),
                "14": case_number_index("the validator gave 38 notes")}
    t.expect(prior_number_hits("49 artifacts [prior:000-demo]", case, facts, sections) == [],
             "number found in its cited section")
    t.expect(prior_number_hits("48 artifacts [prior:000-demo]", case, facts, sections) != [],
             "number absent from its cited sections and from the document")
    t.expect(prior_number_hits("38 notes [prior:000-demo]", case, facts, sections) == [],
             "second row of the union is used")
    unresolvable = [RecordedFact(numbers=["49"], sections=["9.9"])]
    t.expect(prior_number_hits("49 artifacts [prior:000-demo]", case, unresolvable, sections) != [],
             "unresolvable section label of a recorded fact")
    t.expect(prior_number_findings("2 of them high [prior:000-demo]", case, facts, sections)[1] == 0,
             "numbers with a row are not counted as global checks")
    t.expect(prior_number_findings("section 1.10 [prior:000-demo]", case, facts, sections)[1] == 1,
             "numbers without a row are counted as global checks")
    # p-prior-mark: the trigger phrases come from the canon's table.
    triggers = ["reference case", "reference-case", "prior instance", "of the case",
                "the executed instance", "instance 0"]
    t.expect(prior_mark_hits("In the reference case, one role compensated\nfor another's defect.", triggers) != [],
             "statement about the prior without the mark")
    t.expect(prior_mark_hits("In the reference case, the part arrived\nattenuated [prior:000-demo].", triggers) == [],
             "marked statement on a wrapped line")
    t.expect(prior_mark_hits("Lines marked `[prior:<id>]` say what happened in the reference case.", triggers) != [],
             "a mark inside a code span is no mark (v0.5.0)")
    t.expect(prior_mark_hits("In the prior instance, the engine delivered less [prior:000-demo].", triggers) == [],
             "trigger phrase with the mark present")
    t.expect(prior_mark_hits("In the prior instance, the engine delivered less.", triggers) != [],
             "trigger phrase without the mark")
    t.expect(prior_mark_hits("Prior instances differ from one another.", triggers) == [],
             "plural of a trigger does not match")
    t.expect(prior_mark_hits("It reproduces the case end to end.", triggers) == [],
             "'the case' alone is not a trigger")
    t.expect(prior_mark_hits("See the reference-case method document [prior:000-demo].", triggers) == [],
             "hyphenated trigger with the mark")
    t.expect(prior_mark_hits("The reference-case wording is banned.", triggers) != [],
             "hyphenated trigger without the mark")
    t.expect(re.search(trigger_pattern("instance 0"), "see instance 0 for this", re.I) is not None
             and re.search(trigger_pattern("instance 0"), "see instance 01", re.I) is None,
             "multiword trigger is whole word on both sides")
    # p-references.
    t.expect(find_cycle({"a": ["b"], "b": ["a"]}) != [], "cycle")
    t.expect(find_cycle({"a": ["b"], "b": []}) == [], "no cycle")
    card = "- **Notes it emits:** to the `x` (`high`); to `y`.\n- **Code-conversion degree:** (a) to `z`"
    t.expect(note_target_hits(card, {"x", "y"}, "r") == [], "declared note targets")
    t.expect(note_target_hits(card, {"x"}, "r") == ["r: note aimed at 'y', which is not a declared artifact"],
             "undeclared note target")
    fp = "**Notes it emits:** when a `[prior:<id>]` number is missing, or a block is not `text`, to the `x`.\n"
    t.expect(note_target_hits(fp, {"x"}, "r") == [], "code spans that are not destinations")
    t.expect(note_target_hits("**Notes it emits:** up to `high`, to the `x`.\n", {"x"}, "r") == [],
             "a severity after 'to' is not a target")
    t.expect(note_target_hits("**Notes it emits:** it turns into `y`, to the `x`.\n", {"x"}, "r") == [],
             "'to' inside a longer word is not a destination")
    # p-components.
    t.expect(re.search(component_pattern("role card"), "Role cards", flags=re.I), "plural component")
    t.expect(re.search(component_pattern("gate"), "the gates", flags=re.I), "plural gate")
    t.expect(not re.search(component_pattern("gate"), "investigate", flags=re.I), "word inside a word")
    t.expect(not re.search(component_pattern("stopping criterion"), "criterion", flags=re.I), "partial term")
    t.expect(re.search(component_pattern("stopping criterion"), "stopping criteria", flags=re.I),
             "Greek plural")
    t.expect(re.search(component_pattern("gate sensitivity test"), "the gate\nsensitivity tests", flags=re.I),
             "term across a line break")
    # p-limit.
    gates = ("| Gate | Artifact | Magnitude | Limit | Justification |\n| --- | --- | --- | --- | --- |\n"
             "| `g` | `a` | m | 1 | [method] six words make the minimum here |\n"
             "| `h` | `a` | m | 1 | four words only here |\n")
    t.expect(limit_hits(gates, ["[method]"], 6) == ["h: justification without an origin label",
                                                    "h: justification with fewer than 6 words"], "limit rules")
    # p-references: legacy note targets map to the renamed artifacts.
    t.expect(alias_target("bible") == "canon", "legacy note target aliased")
    t.expect(alias_target("canon") == "canon", "current note target untouched")
    t.expect(alias_target("corpus") == "corpus", "other targets untouched")
    legacy_card = "**Notes it emits:** to the `bible`, per finding.\n"
    t.expect(note_target_hits(legacy_card, {"canon"}, "r") == [],
             "card may aim a note at the legacy artifact name")
    # registry validation.
    t.expect(validate_registry({"instances": [{"id": "000-demo"}]})["instances"][0]["id"] == "000-demo",
             "registry with one valid instance")
    for bad in ({}, {"instances": {}}, {"instances": [{}]}, {"instances": [42]}):
        try:
            validate_registry(bad)
        except InputError:
            t.expect(True, "registry shape rejected")
        else:
            t.expect(False, "registry shape rejected")
    # layout overlay and the parser registry.
    custom = merge_layout(DEFAULT_LAYOUT, {"version": 1, "artifacts": {"canon": "canon.md"}})
    t.expect(custom["artifacts"]["canon"] == "canon.md", "layout remaps the canon path")
    t.expect(custom["artifacts"]["artifacts"] == DEFAULT_LAYOUT["artifacts"]["artifacts"],
             "layout keeps the unmapped paths")
    t.expect(layout_parser(custom) == "builtin-markdown", "default layout names the markdown parser")
    json_cell = merge_layout(DEFAULT_LAYOUT, {
        "version": 1,
        "artifacts": {"canon": "02-canon.json", "artifacts": "03-artifacts.json"},
        "gates": {gate: "builtin-json-canon" for gate in BUILTIN_GATES},
        "registry": "priors.json"})
    t.expect(layout_parser(json_cell) == "builtin-json-canon", "cell layout names the JSON parser")
    t.expect(check_parser_extension("builtin-json-canon", json_cell) is None,
             "JSON parser agrees with the JSON artifacts")
    for bad_layout in ({"version": 1, "gates": {"p-terms": "custom"}},
                       {"version": 1, "gates": {"not-a-gate": "builtin-markdown"}},
                       {"version": 1, "artifacts": {"canon": "02-canon.json"},
                        "gates": {"p-terms": "builtin-json-canon"}}):
        try:
            merge_layout(DEFAULT_LAYOUT, bad_layout)
        except InputError:
            t.expect(True, "layout rejected (unknown parser, unknown gate, mixed parsers)")
        else:
            t.expect(False, "layout rejected (unknown parser, unknown gate, mixed parsers)")
    try:
        check_parser_extension("builtin-markdown", json_cell)
    except InputError:
        t.expect(True, "parser disagrees with the file extension")
    else:
        t.expect(False, "parser disagrees with the file extension")
    # builtin-json-canon: the Canon loads from the scaffold's JSON.
    canon_json = {key: [] for key in JSON_CANON_KEYS}
    canon_json["version"] = CANON_SCHEMA_VERSION
    canon_json["terms to avoid"] = ["pipeline"]
    canon_json["method components"] = ["artifact graph", "gate"]
    with tempfile.TemporaryDirectory() as tmpdir:
        canon_path = Path(tmpdir) / "02-canon.json"
        canon_path.write_text(json.dumps(canon_json), encoding="utf-8")
        loaded = load_canon_json(canon_path)
        t.expect(loaded.avoid_terms == ["pipeline"] and loaded.components == ["artifact graph", "gate"],
                 "JSON canon loads with the consumed sections")
        t.expect(loaded.recorded_facts == [] and loaded.prior_triggers == [],
                 "JSON canon starts with empty facts and triggers")
        # I5 of the panel: a canon of a different schema version is
        # refused, not misread — both the JSON field and the markdown row.
        t.expect(canon_schema_row_version(
            "| Section | Owner | Version | State |\n| --- | --- | --- | --- |\n"
            "| Canon schema | verifier | v1 | ready |\n") == CANON_SCHEMA_VERSION,
            "markdown canon declares the schema version row")
        for bad in (None, "v9"):
            try:
                check_canon_version(bad, "fixture")
                t.expect(False, "canon of another schema version is refused")
            except InputError:
                t.expect(True, "canon of another schema version is refused")
        broken = Path(tmpdir) / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        try:
            load_canon_json(broken)
        except InputError:
            t.expect(True, "JSON canon that does not parse is rejected")
        else:
            t.expect(False, "JSON canon that does not parse is rejected")
    try:
        merge_layout(DEFAULT_LAYOUT, {"version": 2})
    except InputError:
        t.expect(True, "layout rejects another version")
    else:
        t.expect(False, "layout rejects another version")
    # p-prior-pin: the sha256 of the passed document against the registry.
    registry = {"instances": [{"id": "000-demo", "status": "executed",
                                "sha256": "a" * 64}]}
    t.expect(pin_findings({"000-demo"}, registry, {"a" * 64})[0] == [], "pin of the right document")
    t.expect(any("wrong or edited prior document" in h
                 for h in pin_findings({"000-demo"}, registry, {"b" * 64})[0]),
             "pin of a different document")
    null_registry = {"instances": [{"id": "000-demo", "status": "executed", "sha256": None}]}
    t.expect(any("no sha256 pinned" in h for h in pin_findings({"000-demo"}, null_registry, {"a" * 64})[0]),
             "executed prior without a pinned sha256")
    t.expect(pin_findings({"000-demo"}, registry, None)[0] == [],
             "without the prior document the pin finds nothing (pending, never a pass)")
    t.expect(pin_findings({"001-designed"}, registry, {"a" * 64}) == ([], 0),
             "a designed instance is not pinned")
    # p-contract-shape: keyword census and the stdlib mini-validator.
    t.expect(unsupported_keywords({"type": "string", "format": "date"}) == ["format"],
             "keyword outside the supported subset is flagged")
    t.expect(unsupported_keywords({"type": "object", "properties": {"a": {"enum": [1]}}}) == [],
             "supported keywords pass the census")
    schema = {"type": "object", "additionalProperties": False,
              "required": ["id", "sha256"],
              "properties": {"id": {"type": "string", "pattern": "^[0-9]{3}-"},
                             "sha256": {"type": ["string", "null"], "pattern": "^[0-9a-f]{64}$"},
                             "round": {"type": "integer", "minimum": 1}}}
    t.expect(check_against_schema({"id": "000-x", "sha256": "a" * 64, "round": 1}, schema, "$") == [],
             "data that satisfies the schema")
    bad = check_against_schema({"id": "x", "sha256": "zz", "round": 0, "extra": 1}, schema, "$")
    t.expect(len(bad) == 4, "type, pattern, minimum and unknown field are violations")
    t.expect(validate_data_text(json.dumps([{"id": "000-x"}]),
                                {"type": "array", "items": schema}, "$") != [],
             "items are validated one by one")
    # p-notes contract fields and rubric hash.
    t.expect(rubric_hash("x\n## Rubric\nA\n## Next\n") == rubric_hash("y\n## Rubric\nA\n"), "rubric hash scope")
    # m-determinism: a measurement of the instrument, not a corpus gate
    # (C13, second critical panel).
    t.expect(determinism_row("pending", "not measured (no --determinism flag)").startswith(
        "| `m-determinism` |"), "the instrument measurement names itself, not a document gate")
    t.expect("p-determinism" not in determinism_row("pass", "sha256 equal in 2 runs"),
             "the determinism row carries no gate name")
    return self_test_later_rules(t)


def self_test_later_rules(t: SelfTest) -> int:
    """The rules added after the self-test stopped growing (v0.4.0 on)."""
    self_test_rules_v04(t)
    return self_test_rules_v05(t)


def self_test_rules_v04(t: SelfTest) -> int:
    """The rules of v0.4.0 and v0.4.1, which until v0.4.1 only the pytest
    suite covered; one short function per rule keeps self_test from growing."""
    self_test_recorded_fact_rule(t)
    self_test_section_references(t)
    self_test_instance_ids(t)
    self_test_number_format(t)
    self_test_layout_keys(t)
    self_test_registry_status(t)
    self_test_experiment_status(t)
    self_test_no_bytecode(t)
    return t.count


def self_test_no_bytecode(t: SelfTest) -> None:
    """No bytecode cache in the material (v0.4.2): the switch is on in this
    process, and a child run carries -B, which it would not inherit."""
    t.expect(sys.dont_write_bytecode, "the bytecode switch is on in this process")
    t.expect(python_command("x.py", "--y")[1:] == [NO_BYTECODE_FLAG, "x.py", "--y"],
             "a child Python run carries -B")


def self_test_rules_v05(t: SelfTest) -> int:
    """The rules of v0.5.0 (the false greens of the panel that reviewed
    v0.4.2), one short function per rule."""
    self_test_marks_in_code(t)
    self_test_placeholders(t)
    self_test_anonymity_forms(t)
    self_test_pending_and_rows(t)
    self_test_status_ledger(t)
    self_test_gate_map(t)
    return t.count


def self_test_marks_in_code(t: SelfTest) -> None:
    """CR2: a mark or a label inside a code span is notation, not a mark."""
    triggers = ["reference case"]
    t.expect(prior_mark_hits("The phrase `reference case` is defined in the canon.", triggers) == [],
             "a trigger inside a code span is notation")
    t.expect("inside a code span" in prior_mark_hits("In the reference case `[prior:000-x]` it gave 3.",
                                                     triggers)[0], "the note says the mark is in code")
    t.expect(efficacy_mark_hits("It pays off `[hypothesis]`.", ["pays off"]) != [],
             "an efficacy label inside a code span is no label")
    t.expect(efficacy_mark_hits("It pays off [hypothesis].", ["pays off"]) == [], "a real label")


def self_test_placeholders(t: SelfTest) -> None:
    """CR3: a placeholder outside code is an unfilled field."""
    t.expect(placeholders("- <fill in>") == ["'<fill in>'"], "angle-bracket placeholder")
    t.expect(placeholders("Stopping criterion: TBD") == ["'TBD'"], "TBD marker")
    t.expect(placeholders("the `[prior:<id>]` mark, x <- y, a < b > c") == [],
             "notation in code, arrows and comparisons are not placeholders")
    card = "**Decides:** <fill in>\n**Does not decide:** the text\n"
    t.expect(card_hits(card, ["Decides", "Does not decide"], True) ==
             ["card: placeholder '<fill in>' in the card"], "a card with a placeholder")
    gates = ("| Gate | Artifact | Magnitude | Limit | Justification |\n| --- | --- | --- | --- | --- |\n"
             "| `g` | `a` | m | <limit> | [method] six words make the minimum here |\n")
    t.expect(limit_hits(gates, ["[method]"], 6) == ["g: placeholder '<limit>'"], "a gate row placeholder")


def self_test_anonymity_forms(t: SelfTest) -> None:
    """IM18: dates with the month's name or dots, one-segment roots, file
    URLs and home folders by user name."""
    day, month, year = "29", "October", "2026"
    for sample in (f"{day} {month} {year}", f"{month} {day}, {year}", f"Oct {day} {year}",
                   ".".join((day, "10", year)), "see /tmp for it", "file:///x", "~joe/work"):
        t.expect(anonymity_hits(sample, []) != [], f"anonymity form '{sample[:6]}...'")
    for sample in (f"{month} {year}", "version 0.4.2", "120 km/h", "about ~4 minutes", "a/tmp b"):
        t.expect(anonymity_hits(sample, []) == [], f"not an anonymity form '{sample[:6]}...'")


def self_test_pending_and_rows(t: SelfTest) -> None:
    """IM15 and IM17: --allow-pending names implemented gates; a truncated
    table row is malformed input, never an IndexError."""
    t.expect(allowed_pending("p-anonymity, p-notes") == frozenset({"p-anonymity", "p-notes"}),
             "--allow-pending reads a comma-separated list")
    for bad in (lambda: allowed_pending("p-anonymty"), lambda: cell_at(["a"], 2, "x")):
        try:
            bad()
            t.expect(False, "malformed input is an InputError")
        except InputError:
            t.expect(True, "malformed input is an InputError")


def self_test_status_ledger(t: SelfTest) -> None:
    """IM10: every note of the ledger has one status line."""
    lines = ('{"ref": "notes:1", "status": "fixed", "closed_in": "0.5.0"}\n'
             '{"ref": "panel:0.4.2:CR1", "status": "open"}\n')
    t.expect(notes_status_hits(lines, 1) == ({"open": 1, "fixed": 1, "disputed": 0,
                                              "out of scope": 0}, []), "a complete state ledger")
    t.expect(notes_status_hits(lines, 2)[1] == ["note 2 of the ledger has no status line"],
             "a note without a status line")
    t.expect(notes_status_hits('{"ref": "notes:1", "status": "fixed"}\n', 1)[1] != [],
             "a closing status without its version")


def self_test_gate_map(t: SelfTest) -> None:
    """CR1 and IM16: the gate table mirrors the artifact list."""
    arts = {"a": Artifact("a", ["a.md"], "w", [], gates=["p-form", "p-terms"])}
    table = [["Gate", "Artifact"], ["`p-form`", "`a`"]]
    t.expect(gate_map_hits(arts, table) == ["gate `p-terms` declared for `a` has no row in the "
                                            "gates table"], "a deleted gate row is a finding")
    t.expect(gate_map_hits(arts, table + [["`p-terms`", "`a`"]]) == [], "the two tables agree")


def self_test_recorded_fact_rule(t: SelfTest) -> None:
    """A number about a prior needs its row in 'Recorded facts' (v0.4.0)."""
    doc = case_document("# M\n\n## 1 Results\n\nThe tool gave 49 items and 21 runs.\n", "point-decimal")
    facts = [RecordedFact(numbers=["49"], sections=["1"])]
    t.expect(number_hits("x", "49", doc, facts, require_row=True)[0] == [],
             "number with its row, found in the section the row cites")
    t.expect(number_hits("x", "21", doc, facts, require_row=True)[0] != [],
             "number without a row fails even though the document contains it")
    t.expect(number_hits("x", "21", doc, facts)[0] == [],
             "the single-document primitive still checks presence")


def self_test_section_references(t: SelfTest) -> None:
    """A section reference is a label; a continuation needs the lookahead."""
    labels, rest = section_references("see section 1.4 and 7 rounds")
    t.expect(labels == ["1.4"] and DOCUMENT_NUMBER.findall(rest) == ["7"],
             "a count after a section reference stays a number")
    t.expect(section_references("sections 1.10 and 4.14 of the case")[0] == ["1.10", "4.14"],
             "a continued section reference before 'of'")
    t.expect(section_references("steps 15, 16 and 17.")[0] == ["15", "16", "17"],
             "a list of steps before punctuation")
    t.expect(DOCUMENT_NUMBER.findall("p95 and v1 of 3") == ["3"], "a digit attached to a letter is a name")


def self_test_instance_ids(t: SelfTest) -> None:
    """Only the full registered id is a name (v0.4.1); a bare prefix counts."""
    ids = instance_ids_of({"instances": [{"id": "003-hpc"}, {"id": "004-adoption-guide"}]})
    t.expect(DOCUMENT_NUMBER.findall(without_instance_ids("instance 004-adoption-guide gave 9", ids)) == ["9"],
             "a full instance id is not read as a number")
    t.expect(DOCUMENT_NUMBER.findall(without_instance_ids("the prior has 003 phases", ids)) == ["003"],
             "a bare id prefix is read as a number")
    out = PriorCheck()
    docs = {"000-demo": case_document("# M\n\n## 1 R\n\n49 items\n", "point-decimal")}
    unit_number_check(1, "the prior has 003 phases [prior:000-demo]", docs, [], out, ids)
    t.expect(any("'003' has no row" in hit for hit in out.hits), "a bare id prefix in a marked unit fails")


def self_test_number_format(t: SelfTest) -> None:
    """One reading per declared format; values and literals apart (I16, I6)."""
    t.expect(number_readings("1.200", "comma-decimal") == {VALUE_TAG + "1200"}, "comma-decimal thousands")
    t.expect(number_readings("1.10", "comma-decimal") == {LITERAL_TAG + "1.10"},
             "a token that does not parse in the format is its literal")
    t.expect(not document_readings("1.2", "comma-decimal") & number_readings("1.200", "comma-decimal"),
             "'1.2' never meets a comma-decimal '1.200'")
    t.expect(not document_readings("1.200", "comma-decimal") & number_readings("1.2", "comma-decimal"),
             "a value never meets the literal of a section number")
    t.expect(bool(document_readings("0.546", "comma-decimal") & number_readings("0,546", "comma-decimal")),
             "the same decimal in each one's format")


def self_test_layout_keys(t: SelfTest) -> None:
    """An unknown layout key is refused; gate-semantics is known (I12)."""
    for bad in ({"version": 1, "artifacts": {"sensitivty": "x.md"}}, {"version": 1, "registy": "x.json"}):
        try:
            merge_layout(DEFAULT_LAYOUT, bad)
            t.expect(False, "an unknown layout key is refused")
        except InputError as exc:
            t.expect("unknown" in str(exc), "an unknown layout key is refused")
    known = merge_layout(DEFAULT_LAYOUT, {"version": 1, "artifacts": {"gate-semantics": "g.md"}})
    t.expect(known["artifacts"]["gate-semantics"] == "g.md", "gate-semantics is a known layout key")


def self_test_registry_status(t: SelfTest) -> None:
    """The contract of a registry entry by status (C16, v0.4.1)."""
    def hits(*entries: dict) -> list[str]:
        return registry_status_hits(json.dumps({"instances": list(entries)}))
    executed = {"id": "000-demo", "status": "executed", "document": "m.md", "sha256": "a" * 64,
                "locator": "../cell", "number_format": "comma-decimal"}
    t.expect(hits(executed) == [], "a complete executed entry")
    t.expect(hits(dict(executed, locator=LOCATOR_OWNER_HELD)) == [], "the reserved locator")
    for name in STATUS_FIELDS:
        t.expect(any(name in hit for hit in hits(dict(executed, **{name: None}))),
                 f"an executed entry without its {name}")
    t.expect(hits(dict(executed, locator="/etc/cell")) != [], "an absolute locator")
    designed = {"id": "001-demo", "status": "designed", "document": None, "sha256": None}
    t.expect(hits(designed) == [], "a designed entry with null fields")
    t.expect(hits(dict(designed, locator="../x")) != [], "a designed entry that carries a locator")


def self_test_experiment_status(t: SelfTest) -> None:
    """Only an executed experiment backs a claim; a subheading is no id (S4)."""
    record = ("# Experiments\n\n## E1 — one\n\n| Field | Value |\n| --- | --- |\n"
              "| Status | `executed`; closed |\n\n### Question\n\nWhy.\n\n"
              "## E2 — two\n\nStatus: designed\n\n## E3 — three\n\nNo status.\n")
    statuses = experiment_statuses(record)
    t.expect(statuses == {"E1": EXECUTED, "E2": "designed", "E3": None}, "the status of each block")
    t.expect(registered_experiments(record) == {"E1"}, "only an executed experiment is registered")
    t.expect(experiment_label_hits("E1", statuses, "r") == [], "an executed experiment backs a claim")
    t.expect("cites a designed experiment as evidence" in experiment_label_hits("E2", statuses, "r")[0],
             "a designed experiment does not back a claim")
    t.expect("not registered" in experiment_label_hits("Question", statuses, "r")[0],
             "a subheading never names an experiment")


# ---------------------------------------------------------------- main

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validator of the reflexive-application production.",
        epilog="exit codes: 0 every gate measured (or its pending accepted with "
               "--allow-pending) and no high/blocking note; 1 at least one high/blocking "
               "note; 2 invalid input or tool failure; 4 no such note, but a gate not "
               "measured that --allow-pending does not accept.",
        allow_abbrev=False)
    p.add_argument("--folder", type=Path, default=Path("."))
    p.add_argument("--layout", type=Path,
                   help="layout.json that remaps artifacts to paths and gates to parsers; "
                        "default is the markdown layout of this corpus")
    p.add_argument("--registry", type=Path,
                   help="instance registry for [prior:<id>] labels; default is "
                        "../instances/registry.json relative to the folder, "
                        "when present; without a registry the p-prior gate is pending")
    p.add_argument("--case", type=Path, action="append",
                   help="prior method document, repeatable (one per executed prior; "
                        "each is identified by its sha256 in the registry); without "
                        "any, the numbers inside [prior:...] units are not measured")
    p.add_argument("--forbidden", type=Path,
                   help="list of forbidden identifiers, one per line; without it, that part of "
                        "the anonymity gate is pending")
    p.add_argument("--rubric-hash", type=Path, help="file with the frozen sha256 of the Rubric section")
    p.add_argument("--freeze-rubric", type=Path,
                   help="write the current sha256 of the rubric to this file and exit; "
                        "refuses if the file already exists")
    p.add_argument("--re-freeze-rubric", type=Path,
                   help="replace an existing frozen rubric deliberately "
                        "(record why in the CHANGELOG)")
    p.add_argument("--notes", type=Path, help="notes.json to validate against the contract")
    p.add_argument("--output", type=Path, help="write the report to this file")
    p.add_argument("--determinism", action="store_true",
                   help="run twice with different hash seeds and compare the reports")
    p.add_argument("--allow-pending", default="",
                   help="gates whose pending rows the caller accepts, comma-separated "
                        "(e.g. p-anonymity in a production with no forbidden list); "
                        "the report names them, and any other pending gate exits 4")
    p.add_argument("--self-test", action="store_true")
    return p.parse_args(argv)


def read_forbidden(path: Path | None) -> list[str] | None:
    if path is None:
        return None
    return [line.strip() for line in read(path).splitlines() if line.strip()]


def load_layout(args: argparse.Namespace) -> dict:
    """The default layout overlaid with --layout, when it is given."""
    if args.layout is None:
        return dict(DEFAULT_LAYOUT)
    try:
        return merge_layout(DEFAULT_LAYOUT, json.loads(read(args.layout)))
    except json.JSONDecodeError as exc:
        raise InputError(f"layout: invalid JSON ({exc.msg}, line {exc.lineno})") from exc


def allowed_pending(value: str) -> frozenset[str]:
    """The gates of --allow-pending; an id this validator does not implement
    is a typo until proven otherwise, a tool failure (exit 2)."""
    gates = frozenset(part.strip() for part in value.split(",") if part.strip())
    unknown = sorted(gates - set(BUILTIN_GATES) - set(GLOBAL_GATES))
    if unknown:
        raise InputError(f"--allow-pending names gates this validator does not implement: "
                         f"{', '.join(unknown)}")
    return gates


def exit_code(checker: Checker, allowed: frozenset[str]) -> int:
    """1 for a high/blocking note, else 4 for a pending the caller did not
    accept, else 0 (IM15, v0.5.0)."""
    if checker.blocking():
        return EXIT_BLOCKING
    return EXIT_PENDING if checker.unaccepted_pending(allowed) else EXIT_OK


def build_report(args: argparse.Namespace) -> tuple[str, int]:
    allowed = allowed_pending(args.allow_pending)
    folder = args.folder.resolve()
    layout = load_layout(args)
    registry_path = args.registry
    if registry_path is None:
        # The registry path of the layout is relative to the production
        # folder; the default resolves to the registry next to the folder.
        candidate = folder / layout["registry"]
        registry_path = candidate if candidate.exists() else None
    registry = load_registry(registry_path) if registry_path is not None else None
    case_texts = [read(path) for path in args.case or []]
    checker = Checker(folder, case_texts, read_forbidden(args.forbidden), args.rubric_hash,
                      args.notes, layout, registry)
    checker.run()
    return checker.report(allowed), exit_code(checker, allowed)


def without_option(argv: list[str], option: str, takes_value: bool) -> list[str]:
    out: list[str] = []
    skip = False
    for arg in argv:
        if skip:
            skip = False
            continue
        if arg == option:
            skip = takes_value
            continue
        if takes_value and arg.startswith(option + "="):
            continue
        out.append(arg)
    return out


def determinism_row(result: str, magnitude: str) -> str:
    """The `m-determinism` row: a measurement of the instrument, not a gate.

    The second critical panel (C13) found the report's determinism injected
    as a corpus-gate row after the table it itself promised was sorted; it
    is now a measurement with its own section, and the row it starts from
    is the pending one, replaced by main() when --determinism runs.
    """
    return f"| `m-determinism` | `{REPORT_FILE}` | {magnitude} | equal | {result} |"


def python_command(script: str, *args: str) -> list[str]:
    """The argv of a child Python run: -B explicitly, since the bytecode
    switch of this process is not inherited (v0.4.2)."""
    return [sys.executable, NO_BYTECODE_FLAG, script, *args]


def determinism_check(argv: list[str]) -> tuple[bool, list[str]]:
    base = without_option(without_option(argv, "--determinism", False), "--output", True)
    digests = []
    for seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        proc = subprocess.run(python_command(os.path.abspath(__file__), *base),
                              capture_output=True, env=env, check=False)
        if proc.returncode == EXIT_TOOL_FAILURE:
            raise InputError("tool failure in the determinism run: " + proc.stderr.decode()[-300:])
        digests.append(hashlib.sha256(proc.stdout).hexdigest())
    return digests[0] == digests[1], digests


def run_freeze(args: argparse.Namespace) -> int:
    """The freeze path (C1/C4b of the panel): the rubric resolves through
    the layout, and an existing pin is refused — replacement is deliberate."""
    if args.freeze_rubric is not None and args.re_freeze_rubric is not None:
        raise InputError("--freeze-rubric and --re-freeze-rubric are mutually "
                         "exclusive: pass the one you mean (the first freezes "
                         "a new pin, the second replaces an existing one)")
    if args.freeze_rubric is not None and args.freeze_rubric.exists():
        pinned = read(args.freeze_rubric).strip()
        # A scaffolded cell ships the 'not-frozen' placeholder in its pin:
        # an explicit absence, not a pin, so the first real freeze replaces it.
        if pinned != RUBRIC_UNFROZEN:
            raise InputError(
                f"the rubric is already frozen at {args.freeze_rubric}; to "
                "replace it deliberately pass --re-freeze-rubric FILE "
                "(and record why in the CHANGELOG)")
    target = args.freeze_rubric or args.re_freeze_rubric
    layout = load_layout(args)
    digest = rubric_digest(args.folder.resolve(), layout)
    target.write_text(digest + "\n", encoding="utf-8")
    print(digest)
    return EXIT_OK


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.self_test:
            count = self_test()
            print(f"self-test: all {count} checks passed")
            return EXIT_OK
        if args.freeze_rubric or args.re_freeze_rubric:
            return run_freeze(args)
        report, code = build_report(args)
        if args.determinism:
            report, same = with_determinism(report, argv)
            code = code if same else EXIT_BLOCKING
        if args.output:
            args.output.write_text(report, encoding="utf-8")
        else:
            sys.stdout.write(report)
    except (InputError, SelfTestError, OSError) as exc:
        print(f"validator: {exc}", file=sys.stderr)
        return EXIT_TOOL_FAILURE
    except Exception as exc:  # noqa: BLE001 - a tool failure is exit 2, never 1 (IM17)
        print(f"validator: unexpected tool failure: {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return EXIT_TOOL_FAILURE
    return code


def with_determinism(report: str, argv: list[str]) -> tuple[str, bool]:
    """The report with the m-determinism row measured (two child runs)."""
    same, digests = determinism_check(argv)
    row = determinism_row("pass" if same else "fail",
                          f"sha256 {'equal' if same else 'different'} in 2 runs")
    report = report.replace(determinism_row("pending", "not measured (no --determinism flag)"),
                            row, 1)
    if not same:
        report += f"\nHigh note: report differs between runs ({digests[0][:12]} and {digests[1][:12]}).\n"
    return report, same


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
