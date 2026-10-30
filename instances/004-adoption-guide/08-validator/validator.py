#!/usr/bin/env python3
"""Validator for the reflexive-application production.

Reads the production canon (01-canon.md), the artifact list (02-artifacts.md)
and the gates (04-gates-and-rubric.md), then measures every gate on every
document the gate table assigns it to. Lists and limits live in those
Markdown files only; this script keeps no copy of them.

The layout (which file holds which control document, which parser a gate
uses) can be remapped with --layout; the default is the markdown layout of
this corpus. The prior-instance registry and the prior method document are
optional inputs. Without a registry, the prior gate is reported as pending
(not measured); with a registry but without the prior document, the labels
are measured and the numbers are not; without the forbidden-identifier list,
that part of the anonymity gate is pending. A pending gate is neither a pass
nor a fail.

Exit codes: 0 no high/blocking note; 1 at least one; 2 invalid input or tool
failure. The report is deterministic: no date, relative paths, sorted output.
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
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

CANON_FILE = "01-canon.md"
ARTIFACTS_FILE = "02-artifacts.md"
GATES_FILE = "04-gates-and-rubric.md"
ROLES_DIR = "03-roles"
VALIDATOR_DIR = "80-validator"
REPORT_FILE = f"{VALIDATOR_DIR}/report.md"
SENSITIVITY_FILE = f"{VALIDATOR_DIR}/sensitivity.md"
RUBRIC_HEADING = "## Rubric"
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
MAX_NOTES_PER_GATE = 50
MIN_JUSTIFICATION_WORDS = 6
MIN_RECIPE_STEPS = 12
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
     "required", "properties", "additionalProperties", "items", "minimum"))
BUILTIN_GATES = ("p-terms", "p-canon-link", "p-anonymity", "p-form", "p-size",
                 "p-table", "p-sections", "p-card", "p-limit", "p-references",
                 "p-prior", "p-prior-mark", "p-prior-pin", "p-contract-shape",
                 "p-recipe", "p-components")
DEFAULT_LAYOUT: dict = {
    "version": 1,
    "artifacts": {
        "canon": CANON_FILE,
        "artifacts": ARTIFACTS_FILE,
        "gates-and-rubric": GATES_FILE,
        "roles-dir": ROLES_DIR,
    },
    "gates": {gate: "builtin-markdown" for gate in BUILTIN_GATES},
    "registry": REGISTRY_DEFAULT_REL,
}


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

def strip_code(text: str) -> str:
    """Remove fenced blocks, inline code spans and link targets.

    A fenced block leaves its line breaks behind, so that a line number
    measured on the stripped text is the line number of the document.
    """
    text = re.sub(r"^```.*?^```[ \t]*$", lambda m: "\n" * m.group(0).count("\n"), text,
                  flags=re.S | re.M)
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


def backticked(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


def clean_cell(cell: str) -> str:
    return re.sub(r"[*`]", "", cell).strip()


@dataclass
class RecordedFact:
    """One row of the canon's 'Recorded facts' table: numbers and the
    sections of the prior's method document where each one lives."""
    numbers: list[str]
    sections: list[str]


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


def split_alternatives(cell: str) -> list[str]:
    """An avoid-table cell such as 'client / sponsor' holds alternatives."""
    return [t.strip() for t in cell.split(AVOID_ALTERNATIVE_SEPARATOR) if t.strip()]


def load_canon(path: Path) -> Canon:
    text = read(path)

    def single_column(heading: str, level: int) -> list[str]:
        table = first_table(section(text, heading, level))
        return [clean_cell(r[0]) for r in table[1:]]

    def optional_column(heading: str, level: int) -> list[str]:
        """A canon without a prior needs no trigger list or recorded facts."""
        try:
            return single_column(heading, level)
        except InputError:
            return []

    def recorded_facts() -> list[RecordedFact]:
        try:
            table = first_table(section(text, r"^Recorded facts$", 2))
        except InputError:
            return []
        facts = []
        for row in table[1:]:
            facts.append(RecordedFact(
                numbers=SECTION_TOKEN.findall(clean_cell(row[0])),
                sections=SECTION_TOKEN.findall(clean_cell(row[2]))))
        return facts

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
        recorded_facts=recorded_facts(),
    )


# Keys of the JSON canon (emitted by the scaffold) that this validator
# consumes; the scaffold writes them all, as empty lists for a new cell.
JSON_CANON_KEYS = ("terms to avoid", "instantiation table rows",
                   "mandatory sections", "role card fields", "origin labels",
                   "method components", "prior-statement triggers",
                   "recorded facts")


def load_canon_json(path: Path) -> Canon:
    """Load the Canon from the JSON the scaffold emits (builtin-json-canon)."""
    try:
        data = json.loads(read(path))
    except json.JSONDecodeError as exc:
        raise InputError(f"canon: invalid JSON ({exc.msg}, line {exc.lineno})") from exc
    if not isinstance(data, dict):
        raise InputError("canon: the JSON canon has to be an object")
    missing = [key for key in JSON_CANON_KEYS if key not in data]
    if missing:
        raise InputError(f"canon: JSON canon misses the sections {missing}")
    for key in JSON_CANON_KEYS:
        if not isinstance(data[key], list) or not all(isinstance(v, str) for v in data[key]):
            raise InputError(f"canon: section '{key}' has to be a list of strings")
    if "recorded facts" in data and data["recorded facts"]:
        raise InputError("canon: 'recorded facts' of a JSON canon has to be empty "
                         "(facts about a prior live in the method's own corpus)")
    return Canon(
        avoid_terms=[t for cell in data["terms to avoid"] for t in split_alternatives(cell)],
        instantiation_rows=data["instantiation table rows"],
        instance_sections=data["mandatory sections"],
        card_fields=data["role card fields"],
        limit_tags=data["origin labels"],
        components=data["method components"],
        prior_triggers=data["prior-statement triggers"],
        recorded_facts=[],
    )


@dataclass
class Artifact:
    name: str
    files: list[str]
    owner: str
    deps: list[str]
    schema: str = ""  # first *.schema.json cited in the Schema cell, if any


def load_artifact_table(table: list[list[str]]) -> dict[str, Artifact]:
    i_name = column(table, "Artifact")
    i_owner = column(table, "Owner")
    i_deps = column(table, "Depends on")
    i_file = column(table, "File") if "file" in [h.lower() for h in table[0]] else None
    i_schema = column(table, "Schema") if "schema" in [h.lower() for h in table[0]] else None
    artifacts: dict[str, Artifact] = {}
    for row in table[1:]:
        names = backticked(row[i_name])
        if not names:
            continue
        files = backticked(row[i_file]) if i_file is not None else []
        deps_cell = row[i_deps].strip()
        deps = [] if deps_cell in NO_DEPENDENCY else backticked(deps_cell)
        schema = ""
        if i_schema is not None:
            refs = [r for r in backticked(row[i_schema]) if r.endswith(".schema.json")]
            schema = refs[0] if refs else ""
        artifacts[names[0]] = Artifact(names[0], files, clean_cell(row[i_owner]).lower(), deps, schema)
    return artifacts


def load_artifact_records(data: object) -> dict[str, Artifact]:
    """Load the artifacts from the JSON list the scaffold emits."""
    if not isinstance(data, list) or not all(isinstance(rec, dict) for rec in data):
        raise InputError("artifacts: the JSON artifact list has to be a list of objects")
    artifacts: dict[str, Artifact] = {}
    for rec in data:
        if not isinstance(rec.get("name"), str) or not rec["name"]:
            raise InputError("artifacts: every record needs a non-empty string 'name'")
        paths = rec.get("paths", [])
        deps = rec.get("depends_on", [])
        if not isinstance(paths, list) or not isinstance(deps, list):
            raise InputError(f"artifacts: 'paths' and 'depends_on' of '{rec['name']}' "
                             "have to be lists")
        schema = rec.get("schema")
        schema = schema if isinstance(schema, str) and schema.endswith(".schema.json") else ""
        owner = rec.get("owner", "")
        artifacts[rec["name"]] = Artifact(rec["name"], list(paths), str(owner).lower(),
                                         list(deps), schema)
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


def merge_layout(base: dict, override: dict) -> dict:
    """Overlay a layout file onto the default layout, validating its shape."""
    if not isinstance(override, dict) or override.get("version") != base["version"]:
        raise InputError("layout: expected an object with 'version' equal to "
                         f"{base['version']}")
    artifacts = override.get("artifacts", {})
    gates = override.get("gates", {})
    if not isinstance(artifacts, dict) or not isinstance(gates, dict):
        raise InputError("layout: 'artifacts' and 'gates' have to be objects")
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
        raise InputError("layout: the merged gate map names more than one parser; "
                         "a layout runs on exactly one of them")
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


# ---------------------------------------------------------------- checks

ABS_PATH = re.compile(rf"(?<![{WORD_CHARS}.\]/~-])/(?:[{WORD_CHARS}.-]+/)+[{WORD_CHARS}.-]*|~/|\b[A-Z]:\\")
ISO_DATE = re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b")
DMY_DATE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
MONTH = (r"(?:January|February|March|April|May|June|July|August|September|October|November|December"
         r"|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b")
MADE_ON = re.compile(rf"\b(?:made|written|generated)\s+on\s+(?:\d|{MONTH})", re.I)
HTML_TAG = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>\n]*)?/?>")
# A number with optional decimal/thousands separators; a group joined by a
# no-break space or a narrow no-break space is a thousands group.
NUMBER = re.compile(r"\d{1,3}(?:[\u00A0\u202F]\d{3})+(?![\d.,])|\d+(?:[.,]\d+)*")
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
    hits = [f"absolute path '{m.group(0)}'" for m in ABS_PATH.finditer(text)]
    hits += [f"date '{m.group(0)}'" for m in ISO_DATE.finditer(text)]
    hits += [f"date '{m.group(0)}'" for m in DMY_DATE.finditer(text)]
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


def number_readings(token: str) -> set[str]:
    """Every value a number token can denote, as canonical decimal text.

    The documents use the English decimal point; the case method document
    uses the decimal comma and the point as thousands separator. A token is
    read both ways (a separator counts as thousands only before groups of
    exactly three digits), plus its literal spelling, so that '0.546' equals
    '0,546', '1,200' equals '1.200', and a section number such as '1.10'
    still matches itself. '39' never equals '139' or '0,39'.
    """
    readings = {token}
    grouped = re.sub(r"[\u00A0\u202F]", "", token)
    if grouped != token:
        readings.add(_decimal_text(grouped) or grouped)
        return readings
    for thousands, decimal in ((",", "."), (".", ",")):
        parts = token.split(decimal)
        if len(parts) > 2:
            continue
        integer = parts[0]
        groups = integer.split(thousands)
        if len(groups) > 1 and not all(len(g) == 3 for g in groups[1:]):
            continue
        if len(groups) > 1 and not 1 <= len(groups[0]) <= 3:
            continue
        if len(parts) == 2 and thousands in parts[1]:
            continue
        digits = "".join(groups) + ("." + parts[1] if len(parts) == 2 else "")
        value = _decimal_text(digits)
        if value is not None:
            readings.add(value)
    return readings


def case_number_index(case_text: str) -> set[str]:
    """All readings of every number in the case method document."""
    index: set[str] = set()
    for token in NUMBER.findall(case_text):
        index |= number_readings(token)
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
    not from a rule of this script. Code spans count, so the unit that
    explains the marker itself is not flagged.
    """
    hits = []
    for n, unit in text_units(text):
        if PRIOR_MARK in unit:
            continue
        for trigger in triggers:
            if re.search(trigger_pattern(trigger), unit, flags=re.I):
                hits.append(f"line {n}: statement about the prior ('{trigger}') "
                            f"without a {PRIOR_MARK}<id>] mark")
                break
    return hits


def case_section_indexes(case_text: str) -> dict[str, set[str]]:
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
    return {label: case_number_index("\n".join(lines))
            for label, lines in sections.items()}


def fact_rows_for(readings: set[str], facts: list[RecordedFact]) -> list[RecordedFact]:
    """The recorded-fact rows that carry a number with one of these readings."""
    return [fact for fact in facts
            if any(readings & number_readings(token) for token in fact.numbers)]


def prior_number_findings(text: str, case_index: set[str],
                          facts: list[RecordedFact] | None = None,
                          sections: dict[str, set[str]] | None = None
                          ) -> tuple[list[str], int]:
    """Numbers in [prior:...] units checked against the prior's document.

    The whole mark (including its id digits) is removed before the numbers
    are read, so an id such as '000-av-production' is never itself checked.
    A number with a row in the canon's 'Recorded facts' is checked in the
    union of the sections that row cites; a number without a row is checked
    for presence in the whole document (the returned count of global checks
    lets the report say which kind of verification ran).
    """
    hits: list[str] = []
    global_checks = 0
    for n, unit in text_units(strip_code(text)):
        if PRIOR_MARK not in unit:
            continue
        for number in NUMBER.findall(PRIOR_TAG.sub("", unit)):
            readings = number_readings(number)
            rows = fact_rows_for(readings, facts) if facts else []
            if not rows:
                global_checks += 1
                if not readings & case_index:
                    hits.append(f"line {n}: '{number}' is not in the prior method document")
                continue
            labels: set[str] = set()
            for row in rows:
                labels |= set(row.sections)
            index: set[str] = set()
            for label in sorted(labels):
                if sections is None or label not in sections:
                    hits.append(f"line {n}: '{number}' cites section '{label}' of the "
                                "prior method document, which does not exist")
                else:
                    index |= sections[label]
            # A cited section with no numbers verifies nothing: an empty
            # union must still be a hit, not a silent pass (rework fix —
            # the old `index and ...` short-circuited the check away).
            if not readings & index:
                cited = ", ".join(sorted(labels))
                hits.append(f"line {n}: '{number}' is not in section(s) {cited} of "
                            "the prior method document")
    return hits, global_checks


def prior_number_hits(text: str, case_index: set[str],
                      facts: list[RecordedFact] | None = None,
                      sections: dict[str, set[str]] | None = None) -> list[str]:
    return prior_number_findings(text, case_index, facts, sections)[0]


def pin_findings(cited_ids: set[str], registry: dict | None,
                 case_digest: str | None) -> tuple[list[str], int]:
    """The sha256 pin of every executed prior cited in the corpus.

    The gate `p-prior-pin` was created after the critical panel found that a
    true pin existed only on the owner's machine: the sha256 in the registry
    was never compared with the document actually passed as the prior. A
    cited executed instance with no pinned sha256, or pinned to another
    document, is a blocking note; without the prior document the gate is
    pending, never a pass.
    """
    if registry is None:
        return [], 0
    executed = {inst["id"]: inst for inst in registry.get("instances", [])
                if isinstance(inst, dict) and inst.get("status") == "executed"}
    cited = sorted(i for i in cited_ids if i in executed)
    hits: list[str] = []
    for pid in cited:
        recorded = executed[pid].get("sha256")
        if not isinstance(recorded, str) or not recorded:
            hits.append(f"cited prior '{pid}' is executed and has no sha256 "
                        "pinned in the registry")
        elif case_digest is not None and recorded != case_digest:
            hits.append(f"cited prior '{pid}' is pinned to another sha256 than "
                        "the prior document passed: wrong or edited prior document")
    return hits, len(cited)


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


def limit_hits(text: str, tags: list[str]) -> list[str]:
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
            if just and len(just.split()) < MIN_JUSTIFICATION_WORDS:
                hits.append(f"{gate}: justification with fewer than {MIN_JUSTIFICATION_WORDS} words")
    return hits


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
            for name in backticked(row[i_art]):
                if name not in artifacts:
                    hits.append(f"gate {clean_cell(row[0])}: artifact '{name}' not declared")
    cycle = find_cycle({a.name: a.deps for a in artifacts.values()})
    if cycle:
        hits.append("cycle in the graph: " + " -> ".join(cycle))
    return hits


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


def rubric_hash(gates_text: str, gates_file: str = GATES_FILE) -> str:
    start = gates_text.find("\n" + RUBRIC_HEADING + "\n")
    if start < 0:
        raise InputError("section 'Rubric' missing from " + gates_file)
    body = gates_text[start + 1:]
    nxt = re.search(r"^## (?!#)", body[len(RUBRIC_HEADING):], flags=re.M)
    if nxt:
        body = body[: len(RUBRIC_HEADING) + nxt.start()]
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


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
        if not isinstance(note["round"], int) or isinstance(note["round"], bool):
            hits.append(f"note {i}: round is not an integer")
    return len(data), hits


# ---------------------------------------------------------------- runner

class Checker:
    def __init__(self, folder: Path, case_text: str | None, forbidden: list[str] | None,
                 rubric_hash_file: Path | None, notes_file: Path | None,
                 layout: dict | None = None, registry: dict | None = None) -> None:
        self.folder = folder
        self.case_index = None if case_text is None else case_number_index(case_text)
        # The pin compares the sha256 of the document passed as the prior
        # with the one recorded in the registry.
        self.case_digest = (None if case_text is None
                            else hashlib.sha256(case_text.encode("utf-8")).hexdigest())
        self.case_sections = ({} if case_text is None else case_section_indexes(case_text))
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
        self.parser = layout_parser(self.layout)
        check_parser_extension(self.parser, self.layout)
        self.registry = registry
        if self.parser == "builtin-json-canon":
            self.canon = load_canon_json(folder / self.canon_file)
            try:
                data = json.loads(read(folder / self.artifacts_file))
            except json.JSONDecodeError as exc:
                raise InputError(f"artifacts: invalid JSON ({exc.msg}, line {exc.lineno})") from exc
            self.artifacts = load_artifact_records(data)
        else:
            self.canon = load_canon(folder / self.canon_file)
            artifact_table = first_table(section(read(folder / self.artifacts_file), r"^Table$"))
            self.artifacts = load_artifact_table(artifact_table)
        gates_text = read(folder / self.gates_file)
        self.gates_text = gates_text
        tables = gate_tables(gates_text)
        if not tables:
            raise InputError(f"{self.gates_file}: gate table not found")
        gate_table = tables[0]
        i_art = column(gate_table, "Artifact")
        self.gate_assignments = {clean_cell(r[0]): backticked(r[i_art]) for r in gate_table[1:]}
        size_table = first_table(section(gates_text, r"^Size ranges$", 3))
        try:
            self.size_ranges = {clean_cell(r[0]): (int(r[1]), int(r[2])) for r in size_table[1:]}
        except (ValueError, IndexError) as exc:
            raise InputError(f"{self.gates_file}: invalid size range row ({exc})") from exc
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
        }
        # Measured once, in check_global; the determinism measurement of the
        # instrument is rendered by main(), which needs two runs to say it.
        self.global_gates = {"p-notes", "p-frozen-rubric", "p-sensitivity"}

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
        for gate, arts in self.gate_assignments.items():
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
            raise InputError(f"gate '{gate}' has no implementation in the validator")
        handler(doc, text)

    # One method per document gate; each records exactly one measurement.

    def check_terms(self, doc: str, text: str) -> None:
        if doc.startswith(FROZEN_LEDGER_PREFIX):
            # Exemption by design: vocabulary rules govern living documents;
            # the review ledger is frozen history and is never edited to
            # satisfy a later vocabulary (regression turned into a rule).
            self.record(doc, "p-terms", "exempt by design (frozen ledger)", "0", [])
            return
        body = text
        if doc == self.canon_file:
            body = re.sub(r"^## Terms to avoid$.*?(?=^## )", "", text, flags=re.S | re.M)
        found = count_avoid_terms(body, self.canon.avoid_terms)
        total = sum(n for _, n in found)
        self.record(doc, "p-terms", str(total), "0", [f"'{t}' x{n}" for t, n in found])

    def check_canon_link(self, doc: str, text: str) -> None:
        canon_name = re.escape(Path(self.canon_file).name)
        n = len(re.findall(rf"\]\([^)]*{canon_name}\)", text))
        self.record(doc, "p-canon-link", str(n), "\u2265 1", [] if n >= 1 else ["no link to the canon"])

    def check_anonymity(self, doc: str, text: str) -> None:
        hits = anonymity_hits(text, self.forbidden)
        if self.forbidden is None and not hits:
            self.pending(doc, "p-anonymity", "0 paths and dates; identifiers not measured (no list)", "0")
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
        found, empty, hits = instantiation_hits(text, rows)
        self.record(doc, "p-table", f"{found}/{len(rows)}, {empty} empty",
                    f"{len(rows)}/{len(rows)}, 0 empty", hits)

    def check_sections(self, doc: str, text: str) -> None:
        titles = heading_titles(text)
        missing = [s for s in self.canon.instance_sections if s.lower() not in titles]
        n = len(self.canon.instance_sections)
        self.record(doc, "p-sections", f"{n - len(missing)}/{n}", f"{n}/{n}",
                    [f"section '{s}' missing" for s in missing])

    def check_card(self, doc: str, text: str) -> None:
        hits = card_hits(text, self.canon.card_fields,
                         whole_document=doc.startswith(self.roles_dir + "/"))
        self.record(doc, "p-card", f"{len(hits)} fields missing", "0", hits)

    def check_limit(self, doc: str, text: str) -> None:
        hits = limit_hits(text, self.canon.limit_tags)
        self.record(doc, "p-limit", str(len(hits)), "0", hits)

    def check_references(self, doc: str, text: str) -> None:
        roles = self.roles | {OWNER_HUMAN}
        if doc == self.artifacts_file:
            hits = reference_hits(self.artifacts, roles, [])
        elif doc == self.gates_file:
            hits = reference_hits(self.artifacts, roles, gate_tables(text))
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
        if self.case_index is None:
            # Without the prior document the labels are measured, the numbers
            # are not: the gate is pending, never a pass.
            magnitude = f"{label_mag}; numbers not measured (no prior document)"
            if unknown:
                self.record(doc, "p-prior", magnitude, "0", hits, severity="blocking")
            else:
                self.pending(doc, "p-prior", magnitude, "0")
            return
        number_hits, global_checks = prior_number_findings(
            text, self.case_index, self.canon.recorded_facts, self.case_sections)
        self.record(doc, "p-prior",
                    f"{label_mag}, {len(number_hits)} numbers unverified, "
                    f"{global_checks} checked globally",
                    "0", hits + number_hits, severity="blocking")

    def check_prior_mark(self, doc: str, text: str) -> None:
        hits = prior_mark_hits(text, self.canon.prior_triggers)
        self.record(doc, "p-prior-mark", str(len(hits)), "0", hits)

    def check_prior_pin(self, doc: str, text: str) -> None:
        try:
            registry = json.loads(text)
            validate_registry(registry)
        except json.JSONDecodeError as exc:
            raise InputError(f"registry: invalid JSON ({exc.msg}, line {exc.lineno})") from exc
        hits, cited = pin_findings(self.cited_prior_ids, registry, self.case_digest)
        if self.case_digest is None:
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
            try:
                schema = json.loads(text)
            except json.JSONDecodeError as exc:
                self.record(doc, "p-contract-shape", "1 broken", "0 broken",
                            [f"schema is not valid JSON ({exc.msg})"])
                return
            unsupported = unsupported_keywords(schema)
            hits = [f"keyword '{kw}' is outside the subset the validator applies"
                    for kw in unsupported]
            self.record(doc, "p-contract-shape",
                        f"{len(schema_keyword_set(schema))} keywords, "
                        f"{len(unsupported)} unsupported", "0 unsupported", hits)
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
        self.record(doc, "p-contract-shape", f"{len(hits)} violations", "0", hits)

    def check_recipe(self, doc: str, text: str) -> None:
        steps, hits = recipe_hits(text)
        if steps < MIN_RECIPE_STEPS:
            hits.append(f"{steps} steps, fewer than {MIN_RECIPE_STEPS}")
        self.record(doc, "p-recipe", f"{steps} steps, {len(hits)} missing",
                    f"\u2265 {MIN_RECIPE_STEPS} steps, 0 missing", hits)

    def check_components(self, doc: str, text: str) -> None:
        components = self.canon.components
        missing = missing_components(text, components)
        n = len(components)
        self.record(doc, "p-components", f"{n - len(missing)}/{n}", f"{n}/{n}",
                    [f"component '{c}' not named" for c in missing])

    def check_global(self) -> None:
        if self.rubric_hash_file is None or not self.rubric_hash_file.exists():
            self.pending(self.gates_file, "p-frozen-rubric", "rubric not frozen yet", "equal")
        else:
            recorded = read(self.rubric_hash_file).split()
            if not recorded:
                raise InputError(f"{self.rubric_hash_file.name} is empty")
            current = rubric_hash(self.gates_text, self.gates_file)
            hits = [] if recorded[0] == current else ["the 'Rubric' section changed after being frozen"]
            self.record(self.gates_file, "p-frozen-rubric", "equal" if not hits else "different", "equal",
                        hits, severity="blocking", target="review")
        self.check_sensitivity_report()
        if self.notes_file is not None:
            rel = Path(os.path.relpath(self.notes_file.resolve(), self.folder)).as_posix()
            count, hits = note_contract_hits(self.notes_file, set(self.artifacts))
            self.record(rel, "p-notes", f"{count} notes, {len(hits)} invalid", "0 invalid", hits,
                        target="open-notes")

    def check_sensitivity_report(self) -> None:
        sens = self.folder / SENSITIVITY_FILE
        if not sens.exists():
            self.pending(SENSITIVITY_FILE, "p-sensitivity", "not measured", "0 missed")
            return
        content = read(sens)
        m = re.search(r"Caught (\d+) of (\d+)\.", content)
        if not m:
            raise InputError(f"{SENSITIVITY_FILE} has no line 'Caught X of Y.'")
        unmeasured = re.search(r"Not measured: (\d+)\.", content)
        not_run = int(unmeasured.group(1)) if unmeasured else 0
        missed = int(m.group(2)) - int(m.group(1))
        magnitude = f"{missed} missed of {m.group(2)}"
        self.current_artifact = "instrument-validator"
        if missed == 0 and not_run:
            self.pending(SENSITIVITY_FILE, "p-sensitivity", f"{magnitude}, {not_run} not measured", "0 missed")
            return
        self.record(SENSITIVITY_FILE, "p-sensitivity", magnitude, "0 missed",
                    [] if missed == 0 else [f"{missed} perturbations missed"])

    def report(self) -> str:
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
    t.expect(prior_mark_hits("Lines marked `[prior:<id>]` say what happened in the reference case.", triggers) == [],
             "the unit that explains the marker itself")
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
    t.expect(limit_hits(gates, ["[method]"]) == ["h: justification without an origin label",
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
    t.expect(pin_findings({"000-demo"}, registry, "a" * 64)[0] == [], "pin of the right document")
    t.expect(any("wrong or edited prior document" in h
                 for h in pin_findings({"000-demo"}, registry, "b" * 64)[0]),
             "pin of a different document")
    null_registry = {"instances": [{"id": "000-demo", "status": "executed", "sha256": None}]}
    t.expect(any("no sha256 pinned" in h for h in pin_findings({"000-demo"}, null_registry, "a" * 64)[0]),
             "executed prior without a pinned sha256")
    t.expect(pin_findings({"000-demo"}, registry, None)[0] == [],
             "without the prior document the pin finds nothing (pending, never a pass)")
    t.expect(pin_findings({"001-designed"}, registry, "a" * 64) == ([], 0),
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
    return t.count


# ---------------------------------------------------------------- main

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validator of the reflexive-application production.",
        epilog="exit codes: 0 no high/blocking note; 1 at least one high/blocking "
               "note; 2 invalid input or tool failure.",
        allow_abbrev=False)
    p.add_argument("--folder", type=Path, default=Path("."))
    p.add_argument("--layout", type=Path,
                   help="layout.json that remaps artifacts to paths and gates to parsers; "
                        "default is the markdown layout of this corpus")
    p.add_argument("--registry", type=Path,
                   help="instance registry for [prior:<id>] labels; default is "
                        "../instances/registry.json relative to the folder, "
                        "when present; without a registry the p-prior gate is pending")
    p.add_argument("--case", type=Path,
                   help="prior method document; without it, the numbers inside "
                        "[prior:...] units are not measured")
    p.add_argument("--forbidden", type=Path,
                   help="list of forbidden identifiers, one per line; without it, that part of "
                        "the anonymity gate is pending")
    p.add_argument("--rubric-hash", type=Path, help="file with the frozen sha256 of the Rubric section")
    p.add_argument("--freeze-rubric", type=Path, help="write the current sha256 of the Rubric section to this file and exit")
    p.add_argument("--notes", type=Path, help="notes.json to validate against the contract")
    p.add_argument("--output", type=Path, help="write the report to this file")
    p.add_argument("--determinism", action="store_true",
                   help="run twice with different hash seeds and compare the reports")
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


def build_report(args: argparse.Namespace) -> tuple[str, bool]:
    folder = args.folder.resolve()
    layout = load_layout(args)
    registry_path = args.registry
    if registry_path is None:
        # The registry path of the layout is relative to the production
        # folder; the default resolves to the registry next to the folder.
        candidate = folder / layout["registry"]
        registry_path = candidate if candidate.exists() else None
    registry = load_registry(registry_path) if registry_path is not None else None
    case_text = None if args.case is None else read(args.case)
    checker = Checker(folder, case_text, read_forbidden(args.forbidden), args.rubric_hash,
                      args.notes, layout, registry)
    checker.run()
    return checker.report(), checker.blocking()


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


def determinism_check(argv: list[str]) -> tuple[bool, list[str]]:
    base = without_option(without_option(argv, "--determinism", False), "--output", True)
    digests = []
    for seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        proc = subprocess.run([sys.executable, os.path.abspath(__file__), *base],
                              capture_output=True, env=env, check=False)
        if proc.returncode == EXIT_TOOL_FAILURE:
            raise InputError("tool failure in the determinism run: " + proc.stderr.decode()[-300:])
        digests.append(hashlib.sha256(proc.stdout).hexdigest())
    return digests[0] == digests[1], digests


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.self_test:
            count = self_test()
            print(f"self-test: all {count} checks passed")
            return EXIT_OK
        if args.freeze_rubric:
            # Freezing reads the gates file through the layout, so a cell
            # freezes its own gates document, not the corpus default.
            layout = load_layout(args)
            digest = rubric_hash(read(args.folder.resolve() / layout["artifacts"]["gates-and-rubric"]),
                                layout["artifacts"]["gates-and-rubric"])
            args.freeze_rubric.write_text(digest + "\n", encoding="utf-8")
            print(digest)
            return EXIT_OK
        report, blocking = build_report(args)
        if args.determinism:
            same, digests = determinism_check(argv)
            status = "pass" if same else "fail"
            row = determinism_row(status, f"sha256 {'equal' if same else 'different'} in 2 runs")
            report = report.replace(determinism_row("pending", "not measured (no --determinism flag)"),
                                    row, 1)
            if not same:
                blocking = True
                report += f"\nHigh note: report differs between runs ({digests[0][:12]} and {digests[1][:12]}).\n"
    except (InputError, SelfTestError) as exc:
        print(f"validator: {exc}", file=sys.stderr)
        return EXIT_TOOL_FAILURE
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    return EXIT_BLOCKING if blocking else EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
