#!/usr/bin/env python3
"""Sensitivity test of the validator (a gate on the gates).

Copies the production folder to a scratch directory, injects one known defect
at a time, runs the validator, and records whether the expected gate failed on
the expected document. A gate that never fails proves nothing.

A perturbation whose gate needs an input that was not provided (the prior
method documents, the frozen rubric hash, the note ledger) is reported as
not measured, never as caught. The registry is copied into the scratch
directory next to the copy of the folder, so a perturbation can edit it
without touching the real one.

The set of perturbations is data (v0.5.0): this corpus keeps it in the
PERTURBATIONS tuple below; a cell names a JSON file with the layout key
artifacts.perturbations (a list of objects with the fields of Perturbation:
name, document, old, new, gate, and optionally expect, delete and the
needs_* flags). --layout reads a cell's layout, as in the validator.

Exit codes: 0 every measured perturbation caught; 1 at least one missed;
2 invalid input or tool failure.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
import hashlib

# No bytecode cache in the material (v0.4.2): the switch is set here, and
# every validator run this script starts gets -B explicitly, since a child
# process inherits neither the switch nor the caller's -B.
sys.dont_write_bytecode = True
NO_BYTECODE_FLAG = "-B"

# The validator is the one place that reads a layout and computes the
# provenance digests; it sits next to this script (corpus and cell alike)
# and is imported after the switch above, so it leaves no cache.
import validator  # noqa: E402

VALIDATOR = Path(__file__).with_name("validator.py")
OUTPUT_HEADING = "# Validator sensitivity"
SENSITIVITY_DEFAULT = "80-validator/sensitivity.md"
REGISTRY_DEFAULT_REL = Path("../instances/registry.json")
EXIT_OK, EXIT_MISSED, EXIT_TOOL_FAILURE = 0, 1, 2
# The results a perturbation can expect of its gate on its document: a fail,
# or a pending (an emptied list of the canon measures nothing, CR3).
EXPECTED_RESULTS = ("fail", "pending")
# Words appended by the p-size perturbation: more than any maximum of the
# "Size ranges" table, so the document leaves its range whatever its size.
SIZE_PADDING_WORDS = 10000
SIZE_PADDING = " ".join(["padding"] * SIZE_PADDING_WORDS)


class ToolFailure(Exception):
    """Raised when the validator cannot run or a perturbation locator is missing."""


class PerturbationDataError(ValueError):
    """Raised when a cell's perturbation file is not the documented list."""


@dataclass(frozen=True)
class Perturbation:
    """One known defect. 'old' -> 'new' is replaced once in 'document'
    (relative to the folder; '../instances/registry.json' is the copied
    registry); with 'delete' the document is removed instead. The needs_*
    flags name the validator inputs the expected gate cannot run without
    (needs_registry: the perturbed document is the copied registry).
    'expect' is the result the gate has to give on the document: 'fail',
    or 'pending' for a defect that empties what the gate reads."""
    name: str
    document: str
    old: str
    new: str
    gate: str
    needs_case: bool = False
    needs_rubric_hash: bool = False
    needs_notes: bool = False
    delete: bool = False
    needs_registry: bool = False
    expect: str = "fail"


# Locators of the v0.5.0 perturbations that span whole lines. The date is
# assembled at run time, so that the source itself carries none.
RECIPE_GATE_ROW = (
    "| `p-recipe` | `recipe` | steps missing one of the fields \"Reads\", \"Creates\", \"Does\", "
    "\"Done when\"; steps in total | 0 missing a field; ≥ 12 steps | [method] the request "
    "demands created files and a done criterion per step; 12 is the number of steps in the "
    "principle's recipe, which this one details |\n")
AVOID_TABLE_ROWS = (
    "| quality gate | gate | canonical term |\n"
    "| checkpoint | gate | suggests a stop point without magnitude |\n"
    "| pipeline | artifact graph | \"pipeline\" hides dependencies and hash |\n"
    "| feedback | note | a note has fixed fields; \"feedback\" does not |\n"
    "| iteration | round | a single name for one pass of the loop |\n"
    "| single source of truth | canon | canonical term |\n"
    "| bible | canon | the term changed in v0.2; the old name is legitimate only as cited history |\n"
    "| ruler | rubric | canonical term |\n"
    "| review board | independent review | canonical term; the review is done by whoever did "
    "not produce |\n")
NAMED_DATE_SAMPLE = " ".join(("29", "October", "2026"))
LESSONS_V050_HEADING = "## The v0.5.0 round: exit 0 is not green"

PERTURBATIONS = (
    Perturbation("avoid-word inserted", "10-generic-recipe.md",
                 "## The orchestrator in pseudocode", "## The orchestrator of the pipeline", "p-terms"),
    Perturbation("absolute path inserted", "00-brief.md",
                 "## For whom", "## For whom (see /etc/target/brief.txt)", "p-anonymity"),
    Perturbation("HTML tag inserted", "00-brief.md",
                  "# Brief of this production", "# Brief <b>of this</b> production", "p-form"),
    Perturbation("instantiation table row deleted", "20-instance-car.md",
                  "| Stopping criterion | release", "| Stopping criteria | release", "p-table"),
    Perturbation("owner that is not a role", "20-instance-car.md",
                  "| `bom` | cost engineer |", "| `bom` | ghost engineer |", "p-references"),
    Perturbation("prior number altered", "10-generic-recipe.md",
                 "the validator gave 38", "the validator gave 39", "p-prior", needs_case=True),
    Perturbation("step field deleted", "10-generic-recipe.md",
                  "- **Done when:** the tree exists;", "- the tree exists;", "p-recipe"),
    Perturbation("gate justification deleted", "22-instance-hpc.md",
                  "| \u2264 1.10 | [hypothesis] the owner accepts little extra spending; the magnitude forces "
                  "declaring the cost of each lever that trades memory for time |",
                  "| \u2264 1.10 |  |", "p-limit"),
    Perturbation("cycle in the graph", "02-artifacts.md",
                 "| `brief` | `00-brief.md` | writer | `corpus` |",
                 "| `brief` | `00-brief.md` | writer | `corpus`, `readme` |", "p-references"),
    Perturbation("note aimed at a missing artifact", "21-instance-text-2027.md",
                 "to the `domain-dossier`, per error found in a source",
                 "to the `corpus`, per error found in a source", "p-references"),
    Perturbation("card field deleted", "03-roles/reviewer.md",
                 "**Does not decide:**", "**Also:**", "p-card"),
    Perturbation("statement about the prior without the mark", "10-generic-recipe.md",
                 "(sections 1.10 and 4.14 of the case) [prior:000-av-production]",
                 "(sections 1.10 and 4.14 of the case)",
                 "p-prior-mark"),
    Perturbation("method component omitted", "22-instance-hpc.md",
                  "The artifact graph:", "The design:", "p-components"),
    Perturbation("schema cell points to a missing file", "02-artifacts.md",
                 "the contract in `05-contracts/notes.schema.json`",
                 "the contract in `05-contracts/gone.schema.json`", "p-contract-shape"),
    # v0.4.0 (I1 of the panel): one perturbation per gate that had none.
    Perturbation("link to the canon does not resolve", "00-brief.md",
                 "[canon](01-canon.md)", "[canon](../01-canon.md)", "p-canon-link"),
    Perturbation("document pushed above its size range", "00-brief.md",
                 "## What is not a goal", "## What is not a goal\n\n" + SIZE_PADDING, "p-size"),
    Perturbation("mandatory section heading removed", "20-instance-car.md",
                 "## 7. Validator", "## 7. Consistency checker", "p-sections"),
    Perturbation("prior pin altered in the registry", "../instances/registry.json",
                 '"sha256": "02f6', '"sha256": "f2f6', "p-prior-pin", needs_case=True),
    Perturbation("rubric edited after the freeze", "04-gates-and-rubric.md",
                 "Mechanical, applied to the scores and findings:",
                 "Mechanical, applied to the scores and to the findings:",
                 "p-frozen-rubric", needs_rubric_hash=True),
    Perturbation("note with an invalid severity", "90-review/notes.json",
                 '"severity": "low"', '"severity": "trivial"', "p-notes", needs_notes=True),
    Perturbation("declared document deleted", "21-instance-text-2027.md",
                 "", "", "p-declared", delete=True),
    Perturbation("claim of efficacy without a label", "10-generic-recipe.md",
                 "It pays off when erring is expensive [hypothesis].",
                 "It pays off when erring is expensive.", "p-efficacy-mark"),
    # The review of v0.4.0 (C1): '21' occurs once in the prior's document, in
    # an unrelated sentence, so presence in the whole document passed it.
    Perturbation("prior number without a recorded fact", "10-generic-recipe.md",
                 "and 26 low open\n  notes [prior:000-av-production]",
                 "and 26 low open\n  notes, kept by 21 roles [prior:000-av-production]",
                 "p-prior", needs_case=True),
    # v0.4.1: the contract of a registry entry by status (C16), and a claim
    # backed by an experiment that has not run (S4 of the v0.4.0 review).
    Perturbation("executed registry entry without a locator", "../instances/registry.json",
                 '"locator": "instances/004-adoption-guide"', '"locator": null', "p-contract-shape",
                 needs_registry=True),
    Perturbation("claim backed by a designed experiment", "10-generic-recipe.md",
                 "for one of another family [experiment:E1].",
                 "for one of another family [experiment:E2].", "p-efficacy-mark"),
    # v0.4.2: p-anonymity covers the round record, whose executor strings
    # are the likeliest place for a machine-local path or an identifier.
    Perturbation("absolute path in the round record", "state/round-record.jsonl",
                 "family C (a third family, neither A nor B)",
                 "family C (see /etc/executors/c.txt)", "p-anonymity"),
    # v0.5.0: one perturbation per false green the panel that reviewed
    # v0.4.2 demonstrated, so each correction stays measured.
    Perturbation("gate row deleted", "04-gates-and-rubric.md",
                 RECIPE_GATE_ROW, "", "p-references"),
    Perturbation("prior mark inside a code span", "10-generic-recipe.md",
                 "the validator gave 38\n  notes, 2 of them high, and both were false "
                 "[prior:000-av-production]",
                 "the validator gave 39\n  notes, 2 of them high, and both were false "
                 "`[prior:000-av-production]`", "p-prior-mark", needs_case=True),
    Perturbation("placeholder in a card field", "03-roles/writer.md",
                 "**Decides:**", "**Decides:** <fill in>", "p-card"),
    Perturbation("canon list emptied", "01-canon.md",
                 AVOID_TABLE_ROWS, "", "p-terms", expect="pending"),
    Perturbation("placeholder in a gate row", "04-gates-and-rubric.md",
                 "| 11 of 11 |", "| <to be set> |", "p-limit"),
    Perturbation("date written with the month's name", "00-brief.md",
                 "## Assumptions", "## Assumptions (as of " + NAMED_DATE_SAMPLE + ")",
                 "p-anonymity"),
    Perturbation("claim of efficacy in the lessons", "99-lessons.md",
                 LESSONS_V050_HEADING,
                 LESSONS_V050_HEADING + "\n\nSeparate roles are the only way to stop a defect.",
                 "p-efficacy-mark"),
    Perturbation("limit raised in the gate table", "04-gates-and-rubric.md",
                 "or with fewer than 6 words", "or with fewer than 60 words", "p-limit"),
    Perturbation("note without a status line", "state/notes-status.jsonl",
                 '{"ref": "notes:1", ', '{"ref": "panel:0.4.2:XX1", ', "p-notes", needs_notes=True),
)


def perturbation_set(folder: Path, layout: dict) -> tuple[Perturbation, ...]:
    """The perturbations of a production: the data file a cell names with
    the layout key artifacts.perturbations, or this corpus's set (read at
    call time, so a test may swap it)."""
    data_file = layout["artifacts"].get("perturbations")
    if data_file is None:
        return tuple(PERTURBATIONS)
    return load_perturbations(folder / data_file)


def load_perturbations(path: Path) -> tuple[Perturbation, ...]:
    """A cell's perturbation file: a JSON list of objects with the fields of
    Perturbation (name, document, old, new, gate required; expect, delete
    and the needs_* flags optional). Anything else is refused by name."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PerturbationDataError(f"could not read the perturbation file {path.name}: {exc}") from exc
    if not isinstance(data, list) or not data:
        raise PerturbationDataError(f"{path.name}: expected a non-empty JSON list of perturbations")
    perts = tuple(perturbation_from(item, i, path.name) for i, item in enumerate(data))
    names = [pert.name for pert in perts]
    if len(names) != len(set(names)):
        raise PerturbationDataError(f"{path.name}: two perturbations share a name")
    return perts


PERTURBATION_FIELDS = {f.name: f.type for f in dataclasses.fields(Perturbation)}
REQUIRED_FIELDS = ("name", "document", "gate")


def perturbation_from(item: object, i: int, source: str) -> Perturbation:
    """One perturbation of a data file, its keys and types checked."""
    where = f"{source}: perturbation {i}"
    if not isinstance(item, dict):
        raise PerturbationDataError(f"{where} is not an object")
    unknown = sorted(set(item) - set(PERTURBATION_FIELDS))
    missing = [key for key in REQUIRED_FIELDS if key not in item]
    if not item.get("delete"):
        missing += [key for key in ("old", "new") if key not in item]
    if unknown or missing:
        raise PerturbationDataError(f"{where}: unknown keys {unknown}, missing keys {missing}")
    for key, value in item.items():
        expected = bool if PERTURBATION_FIELDS[key] == "bool" else str
        if not isinstance(value, expected):
            raise PerturbationDataError(f"{where}: '{key}' has to be a {expected.__name__}")
    if item.get("expect", "fail") not in EXPECTED_RESULTS:
        raise PerturbationDataError(f"{where}: 'expect' is one of {', '.join(EXPECTED_RESULTS)}")
    return Perturbation(**{"old": "", "new": "", **item})


@dataclass(frozen=True)
class Inputs:
    """The validator inputs every run forwards (absolute paths). --case is
    repeatable, as in the validator; --rubric-hash and --notes are optional
    there too, and the perturbation of their gate is not measured without
    them."""
    cases: tuple[Path, ...] = ()
    forbidden: Path | None = None
    registry: Path | None = None
    rubric_hash: Path | None = None
    notes: Path | None = None
    layout: Path | None = None


def validator_command(folder: Path, inputs: Inputs) -> list[str]:
    command = [sys.executable, NO_BYTECODE_FLAG, str(VALIDATOR), "--folder", str(folder)]
    for case in inputs.cases:
        command += ["--case", str(case)]
    for flag, value in (("--forbidden", inputs.forbidden), ("--registry", inputs.registry),
                        ("--rubric-hash", inputs.rubric_hash), ("--notes", inputs.notes),
                        ("--layout", inputs.layout)):
        if value is not None:
            command += [flag, str(value)]
    return command


def run_validator(folder: Path, inputs: Inputs) -> str:
    proc = subprocess.run(validator_command(folder, inputs),
                           capture_output=True, text=True, check=False)
    if proc.returncode == EXIT_TOOL_FAILURE:
        raise ToolFailure("tool failure: " + proc.stderr.strip()[-300:])
    return proc.stdout


def caught(report: str, document: str, gate: str, expect: str = "fail") -> bool:
    return any(line.startswith(f"| `{document}` | `{gate}` |")
               and line.rstrip().endswith(f"| {expect} |")
               for line in report.splitlines())


def missing_input(pert: Perturbation, inputs: Inputs) -> bool:
    """True when the gate of the perturbation cannot run without an input
    that was not provided: the row is not measured, never caught."""
    return ((pert.needs_case and (not inputs.cases or inputs.registry is None))
            or (pert.needs_registry and inputs.registry is None)
            or (pert.needs_rubric_hash and inputs.rubric_hash is None)
            or (pert.needs_notes and inputs.notes is None))


def into_copy(path: Path | None, folder: Path, copy: Path) -> Path | None:
    """A path inside the folder, mapped to the same place in its copy (so a
    perturbation of that file reaches the run); any other path unchanged."""
    if path is None:
        return None
    try:
        return copy / path.relative_to(folder)
    except ValueError:
        return path


def copy_inputs(folder: Path, copy: Path, inputs: Inputs) -> Inputs:
    """The inputs of a run on the copy: the registry is copied to where the
    folder's default registry path resolves from the copy (so the registry
    document is measured, and perturbable, in the copy), and the rubric hash
    and the note ledger map into the copy when they live in the folder."""
    registry = into_copy(inputs.registry, folder, copy)
    if inputs.registry is not None and registry == inputs.registry:
        # A registry outside the folder (the corpus's) is copied to where
        # the folder's default registry path resolves from the copy.
        registry = (copy / REGISTRY_DEFAULT_REL).resolve()
        registry.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(inputs.registry, registry)
    return Inputs(inputs.cases, inputs.forbidden, registry,
                  into_copy(inputs.rubric_hash, folder, copy), into_copy(inputs.notes, folder, copy),
                  into_copy(inputs.layout, folder, copy))


def apply(target: Path, pert: Perturbation) -> None:
    """Inject the defect into the copied document (replace once, or delete)."""
    if pert.delete:
        if not target.is_file():
            raise ToolFailure(f"the document of the perturbation '{pert.name}' does not exist: "
                              f"{pert.document}")
        target.unlink()
        return
    text = target.read_text(encoding="utf-8")
    if pert.old not in text:
        raise ToolFailure(f"locator of the perturbation '{pert.name}' not found in {pert.document}")
    target.write_text(text.replace(pert.old, pert.new, 1), encoding="utf-8")


def inject(folder: Path, work: Path, pert: Perturbation, inputs: Inputs) -> str:
    """Return the validator report on a copy of folder with one defect injected."""
    with tempfile.TemporaryDirectory(dir=work) as tmp:
        copy = Path(tmp) / "copy"
        shutil.copytree(folder, copy)
        copied = copy_inputs(folder, copy, inputs)
        apply(copy / pert.document, pert)
        return run_validator(copy, copied)


def provenance_header(folder: Path, layout: dict, perts: tuple[Perturbation, ...]) -> str:
    """The provenance of this report (v0.3.0, C3 of the panel): the sha256 of
    the validator that ran it, of the gate section and of the canon it was
    made against (v0.5.0, CR1: the inputs that define what is measured), and
    the ids and count of the perturbations, so the p-sensitivity gate can
    refuse a report this instrument cannot have produced."""
    validator_py = Path(__file__).resolve().with_name("validator.py")
    sha = hashlib.sha256(validator_py.read_bytes()).hexdigest()
    digests = validator.provenance_inputs(folder, layout)
    ids = ", ".join(pert.name for pert in perts)
    return (f"validator sha256: {sha}\ngates sha256: {digests['gates']}\n"
            f"canon sha256: {digests['canon']}\nperturbations: {len(perts)} ({ids})\n")


def render(header: str, rows: list[str], caught_count: int, measured: int,
           not_measured: int) -> str:
    out = [OUTPUT_HEADING, "", *header.splitlines(), "",
           "Generated by `sensitivity.py`: each row injects one known defect into a copy of",
           "the folder and checks that the expected gate fails on the expected document (or,",
           "for a defect that empties what the gate reads, is pending there), and did not",
           "before the injection. A row whose gate needs an input that was not provided is",
           "not measured.", "",
           "| Perturbation | Document | Expected gate | Result |", "| --- | --- | --- | --- |", *rows, "",
           f"Caught {caught_count} of {measured}."]
    if not_measured:
        out.append(f"Not measured: {not_measured}.")
    return "\n".join(out) + "\n"


def resolve_output(output: Path | None, folder: Path, layout: dict | None = None) -> Path:
    """The report's write path (v0.2.3): an explicit --output passes through
    unchanged; without one, the report goes where the layout key
    artifacts.sensitivity points, under the folder (v0.5.0; the corpus
    default is 80-validator/sensitivity.md), never to the caller's working
    directory."""
    if output is not None:
        return output
    return folder / (layout["artifacts"]["sensitivity"] if layout else SENSITIVITY_DEFAULT)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    p.add_argument("--folder", type=Path, default=Path("."),
                   help="production folder to copy and perturb (default: the current folder)")
    p.add_argument("--case", type=Path, action="append",
                   help="prior method document, repeatable as in the validator; without "
                        "any, the rows that need a prior are not measured")
    p.add_argument("--forbidden", type=Path, help="list of forbidden identifiers, one per line")
    p.add_argument("--registry", type=Path,
                   help="instance registry; default is ../instances/registry.json relative "
                        "to the folder, when present")
    p.add_argument("--rubric-hash", type=Path,
                   help="frozen sha256 of the rubric, forwarded to the validator; without "
                        "it, the p-frozen-rubric row is not measured")
    p.add_argument("--notes", type=Path,
                   help="note ledger, forwarded to the validator; without it, the p-notes "
                        "row is not measured")
    p.add_argument("--work", type=Path, default=None,
                   help="scratch folder for the copies (default: a temporary folder)")
    p.add_argument("--output", type=Path, default=None,
                   help="where the report is written (default: the layout key "
                        "artifacts.sensitivity relative to the folder)")
    p.add_argument("--layout", type=Path,
                   help="the cell's layout.json, as in the validator; it also names the "
                        "cell's perturbation file (artifacts.perturbations)")
    return p.parse_args(argv)


def resolve_inputs(args: argparse.Namespace, folder: Path, layout: dict) -> Inputs:
    """Absolute paths of every input; the registry defaults to the one the
    layout names (next to the corpus folder, or a cell's own), when present."""
    def absolute(path: Path | None) -> Path | None:
        return None if path is None else path.resolve()
    registry = args.registry
    if registry is None:
        candidate = folder / layout["registry"]
        registry = candidate if candidate.exists() else None
    return Inputs(tuple(path.resolve() for path in args.case or []), absolute(args.forbidden),
                  absolute(registry), absolute(args.rubric_hash), absolute(args.notes),
                  absolute(args.layout))


def measure(folder: Path, work: Path, inputs: Inputs,
            perts: tuple[Perturbation, ...]) -> tuple[list[str], int, int, int]:
    """Run the baseline and every perturbation: rows, caught, measured, not measured."""
    baseline = run_validator(folder, inputs)
    rows: list[str] = []
    caught_count = measured = not_measured = 0
    for pert in perts:
        row = f"| {pert.name} | `{pert.document}` | `{pert.gate}` |"
        if missing_input(pert, inputs):
            not_measured += 1
            rows.append(f"{row} not measured |")
            continue
        report = inject(folder, work, pert, inputs)
        ok = (caught(report, pert.document, pert.gate, pert.expect)
              and not caught(baseline, pert.document, pert.gate, pert.expect))
        measured += 1
        caught_count += 1 if ok else 0
        rows.append(f"{row} {'caught' if ok else 'MISSED'} |")
    return rows, caught_count, measured, not_measured


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    folder = args.folder.resolve()
    try:
        layout = validator.load_layout(args)
        perts = perturbation_set(folder, layout)
        inputs = resolve_inputs(args, folder, layout)
        work = args.work.resolve() if args.work is not None else Path(tempfile.mkdtemp())
        work.mkdir(parents=True, exist_ok=True)
        rows, caught_count, measured, not_measured = measure(folder, work, inputs, perts)
        # Inside the try (v0.2.3 rework): a write OSError is a tool failure
        # (exit 2), not a traceback with exit 1 ("missed").
        resolve_output(args.output, folder, layout).write_text(
            render(provenance_header(folder, layout, perts), rows, caught_count, measured,
                   not_measured), encoding="utf-8")
    except (ToolFailure, PerturbationDataError, validator.InputError, OSError,
            UnicodeDecodeError) as exc:
        print(f"sensitivity: {exc}", file=sys.stderr)
        return EXIT_TOOL_FAILURE
    return EXIT_OK if caught_count == measured else EXIT_MISSED


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
