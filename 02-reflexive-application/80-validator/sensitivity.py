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

Since v0.6.0 the copy is the whole material the folder belongs to (the
folder and everything its artifact table and registry reach above it), so a
perturbation reaches the root documents and the baseline and the perturbed
runs read the same object; each perturbed report is compared with the
baseline row by row (specificity: a perturbation that changes the result of
another row is noisy), and the coverage is also reported by (document, gate)
pair. A perturbation whose gate the validator does not implement is a tool
failure, never a miss.

Exit codes: 0 every measured perturbation caught and none noisy; 1 at least
one missed or noisy; 2 invalid input or tool failure.
"""

from __future__ import annotations

import argparse
import dataclasses
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

# No bytecode cache in the material (v0.4.2): the switch is set here, and
# every validator run this script starts gets -B explicitly, since a child
# process inherits neither the switch nor the caller's -B.
sys.dont_write_bytecode = True
NO_BYTECODE_FLAG = "-B"

# The validator is the one place that reads a layout and computes the
# provenance digests; it sits next to this script (corpus and cell alike)
# and is imported after the switch above, so it leaves no cache.
import validator  # noqa: E402
# The perturbation data (v0.6.0): its own module, read by the validator too.
import perturbation_set as perturbation_set_module  # noqa: E402
from perturbation_set import (  # noqa: E402,F401
    AVOID_TABLE_ROWS, EXPECTED_RESULTS, LESSONS_V050_HEADING, NAMED_DATE_SAMPLE,
    PERTURBATION_FIELDS, PERTURBATIONS, PRIOR_000, RECIPE_GATE_ROW, REQUIRED_FIELDS,
    SIZE_PADDING, SIZE_PADDING_WORDS, Perturbation, PerturbationDataError,
    load_perturbations, perturbation_from,
)

VALIDATOR = Path(__file__).with_name("validator.py")
OUTPUT_HEADING = "# Validator sensitivity"
SENSITIVITY_DEFAULT = "80-validator/sensitivity.md"
EXIT_OK, EXIT_MISSED, EXIT_TOOL_FAILURE = 0, 1, 2
EXIT_EMPTY = 4  # an empty set (v0.6.0), the code of a pending in the validator
# A measurement row of a validator report: document, gate, result.
REPORT_ROW = re.compile(r"^\| `([^`]+)` \| `([^`]+)` \| .* \| (pass|fail|pending) \|$")


class ToolFailure(Exception):
    """Raised when the validator cannot run or a perturbation locator is missing."""


def perturbation_set(folder: Path, layout: dict) -> tuple[Perturbation, ...]:
    """The perturbations of a production: the cell's data file, or this
    corpus's set (read at call time, so a test may swap PERTURBATIONS)."""
    return perturbation_set_module.select(folder, layout, PERTURBATIONS)


def check_gates(perts: tuple[Perturbation, ...]) -> None:
    """Every expected gate is one the validator implements (v0.6.0): a gate of
    the domain, or a typo, used to come out MISSED (exit 1) for a gate this
    script never ran; it is a tool failure. A domain gate's sensitivity is the
    cell's own (its mutants), not a perturbation of a document."""
    known = (*validator.BUILTIN_GATES, *validator.GLOBAL_GATES)
    unknown = sorted({pert.gate for pert in perts if pert.gate not in known})
    if unknown:
        raise ToolFailure(f"perturbations name gates the validator does not implement: "
                          f"{', '.join(unknown)}; the sensitivity test perturbs documents, and "
                          "a domain gate's sensitivity is measured by the cell's own code")


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
    # The registered priors the --case documents are identified as (v0.6.0).
    case_priors: tuple[str, ...] = ()
    # Replacements applied to every copy (path relative to the material, old,
    # new): the pin and the section commitments of a synthetic prior.
    patches: tuple[tuple[str, str, str], ...] = ()
    synthetic: tuple[tuple[str, str], ...] = ()  # (prior id, sha256 of its synthetic document)


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
    """The report of one validator run, read as UTF-8 whatever the console
    (v0.6.0: the child inherited a cp1252 console and died on '≥')."""
    env = dict(os.environ, PYTHONIOENCODING=validator.CHILD_ENCODING)
    proc = subprocess.run(validator_command(folder, inputs), capture_output=True, text=True,
                          encoding=validator.CHILD_ENCODING, env=env, check=False)
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
            or (pert.prior and pert.prior not in inputs.case_priors)
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


def copy_inputs(root: Path, copy_root: Path, inputs: Inputs) -> Inputs:
    """The inputs of a run on the copy of the material: the registry, the
    rubric hash, the note ledger and the layout map into the copy when they
    live in the material (so the registry is measured, and perturbable, in
    the copy); the --case documents stay the originals, never perturbed."""
    return dataclasses.replace(inputs, registry=into_copy(inputs.registry, root, copy_root),
                               rubric_hash=into_copy(inputs.rubric_hash, root, copy_root),
                               notes=into_copy(inputs.notes, root, copy_root),
                               layout=into_copy(inputs.layout, root, copy_root))


def material_root(folder: Path, layout: dict, registry: Path | None) -> Path:
    """The material a folder belongs to (v0.6.0): the deepest folder that
    contains the production folder, every literal '../' path of its artifact
    table and its registry. The copy used to be the folder alone, so every
    perturbed run lost the documents above it while the baseline had them."""
    _, artifacts = validator.load_control_documents(folder, layout)
    reached = [folder] + [(folder / p).resolve() for art in artifacts.values()
                          for p in art.files if p.startswith("../")]
    if registry is not None:
        reached.append(registry.resolve())
    return Path(os.path.commonpath([str(p) for p in reached]))


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


COPY_IGNORED = (".git", "__pycache__", ".pytest_cache")


def inject(folder: Path, root: Path, work: Path, pert: Perturbation | None, inputs: Inputs) -> str:
    """Return the validator report on a copy of the material with one defect
    injected into its copy of the folder (the work folder, when it lies inside
    the material, is not copied into itself)."""
    def ignored(directory: str, names: list[str]) -> list[str]:
        return [n for n in names if n in COPY_IGNORED
                or (Path(directory) / n).resolve() == work.resolve()]
    with tempfile.TemporaryDirectory(dir=work) as tmp:
        copy_root = Path(tmp) / "copy"
        shutil.copytree(root, copy_root, ignore=ignored)
        copy = copy_root / folder.relative_to(root)
        for rel, old, new in inputs.patches:
            target = copy_root / rel
            target.write_text(target.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
        if pert is not None:
            apply(copy / pert.document, pert)
        return run_validator(copy, copy_inputs(root, copy_root, inputs))


def provenance_header(folder: Path, layout: dict, perts: tuple[Perturbation, ...]) -> str:
    """The provenance of this report (since v0.3.0): the sha256 of
    the validator that ran it, of the gate section and of the canon it was
    made against (since v0.5.0: the inputs that define what is measured), and
    the ids and count of the perturbations, so the p-sensitivity gate can
    refuse a report this instrument cannot have produced."""
    sha = validator.content_digest(VALIDATOR.resolve())
    digests = validator.provenance_inputs(folder, layout)
    ids = ", ".join(pert.name for pert in perts)
    return (f"validator sha256: {sha}\ngates sha256: {digests['gates']}\n"
            f"canon sha256: {digests['canon']}\nmap sha256: {digests['map']}\n"
            f"perturbations: {len(perts)} ({ids})\n")


def case_lines(inputs: Inputs, folder: Path, layout: dict) -> str:
    """The prior documents the report was made with (v0.6.0, rework): one
    line 'case sha256: <id> <sha256>' per --case document identified as a
    registered prior, synthetic ones included, computed, never declared;
    'case sha256: none' without any. The validator compares each sha256 with
    the pin of the registry, so a synthetic prior is told by its hash. Since
    the closing pass, one line 'case attestation: <id> <sha256>' per document
    too, over its text and the provenance, which only its holder computes."""
    pins = {}
    if inputs.registry is not None:
        pins = {i.get("sha256"): i["id"] for i in validator.load_registry(inputs.registry)["instances"]
                if i.get("status") == validator.EXECUTED}
    pins.update({sha: pid for pid, sha in inputs.synthetic})
    texts = {validator.sha256_text(t): t for t in (validator.read(c) for c in inputs.cases)}
    found = sorted((pins[d], d) for d in texts if d in pins)
    if not found:
        return "case sha256: none\n"
    digests = validator.provenance_inputs(folder, layout)
    sha = validator.content_digest(VALIDATOR.resolve())
    return ("".join(f"case sha256: {pid} {d}\n" for pid, d in found)
            + "".join(f"case attestation: {pid} "
                      f"{validator.case_attestation(texts[d], digests, sha)}\n" for pid, d in found))


def report_results(report: str) -> dict[tuple[str, str], frozenset[str]]:
    """The results of every (document, gate) row of a validator report."""
    results: dict[tuple[str, str], set[str]] = {}
    for line in report.splitlines():
        m = REPORT_ROW.match(line)
        if m:
            results.setdefault((m.group(1), m.group(2)), set()).add(m.group(3))
    return {key: frozenset(value) for key, value in results.items()}


def noisy_rows(baseline: dict, perturbed: dict, pert: Perturbation) -> list[str]:
    """The rows whose result the perturbation changed besides its own
    (v0.6.0, specificity). Not counted: the expected row; the p-sensitivity
    row, which reads the provenance an edit of an input pins on purpose, and
    its other name p-sensitivity-synthetic (rework of v0.6.0: a perturbed pin
    makes the recorded case read as synthetic); and the rows of a document
    that left the report (deleted or unmapped)."""
    present = {doc for doc, _ in perturbed}
    declared = {gate.strip() for gate in pert.also.split(",") if gate.strip()}
    out = []
    for key in sorted(set(baseline) | set(perturbed)):
        doc, gate = key
        if key == (pert.document, pert.gate) or gate in declared \
                or gate in (validator.SENSITIVITY_GATE, validator.SYNTHETIC_GATE):
            continue
        if key not in perturbed and (doc not in present or (pert.delete and doc == pert.document)):
            continue
        if baseline.get(key) != perturbed.get(key):
            out.append(f"`{doc}` `{gate}`")
    return out


@dataclass
class Outcome:
    """What a sensitivity run measured (v0.6.0 adds the noise and the pairs)."""
    rows: list[str] = dataclasses.field(default_factory=list)
    caught: int = 0
    measured: int = 0
    not_measured: int = 0
    noisy: list[tuple[str, list[str]]] = dataclasses.field(default_factory=list)
    pairs_covered: int = 0
    pairs_total: int = 0
    declared: list[tuple[str, str]] = dataclasses.field(default_factory=list)


def render(header: str, outcome: Outcome) -> str:
    out = [OUTPUT_HEADING, "", *header.splitlines(), "",
           "Generated by `sensitivity.py`: each row injects one known defect into a copy of",
           "the material and checks that the expected gate fails on the expected document (or,",
           "for a defect that empties what the gate reads, is pending there), and did not",
           "before the injection. A row whose gate needs an input that was not provided is",
           "not measured. A perturbation is noisy when another row of the report changed its",
           "result; the pairs are the (document, gate) rows of the baseline report that at",
           "least one measured perturbation targets.", "",
           "| Perturbation | Document | Expected gate | Result |", "| --- | --- | --- | --- |",
           *outcome.rows, "", f"Caught {outcome.caught} of {outcome.measured}."]
    if outcome.not_measured:
        out.append(f"Not measured: {outcome.not_measured}.")
    out += [f"Noisy: {len(outcome.noisy)} of {outcome.measured}.",
            f"Pairs covered: {outcome.pairs_covered} of {outcome.pairs_total}."]
    for name, rows in outcome.noisy:
        out.append(f"- noisy: {name} also changed {', '.join(rows)}")
    for name, gates in outcome.declared:
        out.append(f"- declared: {name} also reaches {gates} by design")
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
    p.add_argument("--synthetic-prior", action="append", default=[],
                   help="an executed prior whose method document you do not have (e.g. "
                        "000-av-production): a synthetic document is generated from the "
                        "canon's recorded facts and pinned in the copies only, so the rows "
                        "that need it are measured; the report says so (v0.6.0)")
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
    cases = tuple(path.resolve() for path in args.case or [])
    return Inputs(cases, absolute(args.forbidden), absolute(registry), absolute(args.rubric_hash),
                  absolute(args.notes), absolute(args.layout), case_priors(cases, registry))


def case_priors(cases: tuple[Path, ...], registry: Path | None) -> tuple[str, ...]:
    """The ids of the executed priors the --case documents are pinned as,
    by the validator's own reading of a document and of the registry."""
    if registry is None:
        return ()
    pins = {inst.get("sha256"): inst["id"] for inst in validator.load_registry(registry)["instances"]
            if inst.get("status") == validator.EXECUTED}
    digests = {validator.sha256_text(validator.read(case)) for case in cases}
    return tuple(sorted(pins[d] for d in digests if d in pins))


# The headings of a synthetic document when the registry declares no
# 'heading_style' for the prior: a numbered section and a numbered step.
DEFAULT_HEADINGS = {"section": "## {label}", "subsection": "### {label}", "step": "## {label}"}


def synthetic_document(folder: Path, layout: dict, prior_id: str, number_format: str,
                       headings: dict | None = None) -> str:
    """A method document for a prior whose real one is owner-held (v0.6.0):
    one numbered section per label the canon's recorded facts of that prior
    cite, or the marked units of the material reference, holding the numbers
    of its rows written in the prior's number format. Since the rework of
    v0.6.0 each heading is written in the style the registry declares for
    the real document ('heading_style': a section, a subsection, a step),
    so a reader that stops reading that style fails on the synthetic too.
    It lets the rows that need the prior be measured in a clone; it proves
    nothing about the real document, which only the owner can check."""
    canon, artifacts = validator.load_control_documents(folder, layout)
    sections: dict[str, list[str]] = {}
    for fact in validator.facts_of(prior_id, canon.recorded_facts):
        for label in fact.sections:
            sections.setdefault(label, []).extend(fact.numbers)
    steps = step_labels(validator.read(folder / layout["artifacts"]["canon"]))
    for gate, doc in validator.gate_map_pairs(folder, artifacts):
        if gate != "p-prior":
            continue
        text = validator.strip_fences_and_links(validator.read(folder / doc))
        for _, unit in validator.text_units(text):
            if prior_id in validator.prior_ids(validator.strip_code(unit)):
                opened = validator.open_code_spans(unit)
                steps |= step_labels(opened)
                for label in validator.section_references(opened)[0]:
                    sections.setdefault(label, [])
    comma = number_format == "comma-decimal"
    style = {**DEFAULT_HEADINGS, **(headings or {})}
    body = [heading_line(label, label in steps, style) + "\n\nNumbers: "
            + " ; ".join(n.replace(".", ",") if comma else n for n in nums) + "\n"
            for label, nums in sorted(sections.items())]
    return f"# Synthetic method document of {prior_id}\n\n" + "\n".join(body)


def step_labels(text: str) -> set[str]:
    """The labels a text cites as steps ('step 15', 'steps 13 and 14')."""
    return {label for m in validator.SECTION_REF.finditer(text)
            if m.group(0).lower().startswith("step")
            for label in validator.SECTION_TOKEN.findall(m.group(1))}


def heading_line(label: str, is_step: bool, style: dict) -> str:
    """The heading of one synthetic section in the real document's style."""
    kind = "step" if is_step else "subsection" if "." in label else "section"
    return style[kind].format(label=label) + " Section"


def with_synthetic_prior(folder: Path, root: Path, layout: dict, inputs: Inputs,
                         prior_id: str, work: Path) -> Inputs:
    """The inputs with a synthetic document standing for an owner-held prior:
    passed as --case, and its sha256 and section digests patched into every
    copy's registry and canon (never into the material itself)."""
    if inputs.registry is None:
        raise ToolFailure("--synthetic-prior needs the registry")
    entry = next((i for i in validator.load_registry(inputs.registry)["instances"]
                  if i.get("id") == prior_id and i.get("status") == validator.EXECUTED), None)
    if entry is None or not entry.get("sha256"):
        raise ToolFailure(f"--synthetic-prior: '{prior_id}' is no executed, pinned prior")
    text = synthetic_document(folder, layout, prior_id, entry.get("number_format", ""),
                              entry.get("heading_style"))
    path = work / f"synthetic-{prior_id}.md"
    path.write_text(text, encoding="utf-8")
    digests = validator.section_digests(text)
    canon_rel = (folder / layout["artifacts"]["canon"]).relative_to(root).as_posix()
    canon = validator.load_control_documents(folder, layout)[0]
    patches = [(inputs.registry.relative_to(root).as_posix(), entry["sha256"],
                validator.sha256_text(text))]
    patches += [(canon_rel, row.sha256, digests.get(row.section, "0" * 64))
                for row in canon.section_commitments if row.prior_id == prior_id]
    return dataclasses.replace(inputs, cases=inputs.cases + (path,),
                               case_priors=tuple(sorted({*inputs.case_priors, prior_id})),
                               patches=inputs.patches + tuple(patches),
                               synthetic=inputs.synthetic + ((prior_id, validator.sha256_text(text)),))


def measure(folder: Path, root: Path, work: Path, inputs: Inputs,
            perts: tuple[Perturbation, ...]) -> Outcome:
    """Run the baseline and every perturbation on a copy of the material."""
    # With a synthetic prior the baseline runs on a patched copy too.
    baseline_report = (inject(folder, root, work, None, inputs) if inputs.patches
                       else run_validator(folder, inputs))
    baseline = report_results(baseline_report)
    outcome, targeted = Outcome(), set()
    for pert in perts:
        row = f"| {pert.name} | `{pert.document}` | `{pert.gate}` |"
        if missing_input(pert, inputs):
            outcome.not_measured += 1
            outcome.rows.append(f"{row} not measured |")
            continue
        report = inject(folder, root, work, pert, inputs)
        ok = (caught(report, pert.document, pert.gate, pert.expect)
              and not caught(baseline_report, pert.document, pert.gate, pert.expect))
        noise = noisy_rows(baseline, report_results(report), pert)
        if noise:
            outcome.noisy.append((pert.name, noise))
        if pert.also:
            outcome.declared.append((pert.name, pert.also))
        outcome.measured += 1
        outcome.caught += 1 if ok else 0
        targeted.add((pert.document, pert.gate))
        outcome.rows.append(f"{row} {'caught' if ok else 'MISSED'} |")
    pairs = {key for key in baseline if key[1] != validator.SENSITIVITY_GATE
             and not key[0].startswith(validator.MEASUREMENT_PREFIX)}
    outcome.pairs_covered, outcome.pairs_total = len(pairs & targeted), len(pairs)
    return outcome


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < validator.MIN_PYTHON:
        print("sensitivity: Python 3.9 or later is required", file=sys.stderr)
        return EXIT_TOOL_FAILURE
    validator.utf8_streams()
    args = parse_args(argv)
    folder = args.folder.resolve()
    try:
        layout = validator.load_layout(args)
        perts = perturbation_set(folder, layout)
        check_gates(perts)
        inputs = resolve_inputs(args, folder, layout)
        root = material_root(folder, layout, inputs.registry)
        work = args.work.resolve() if args.work is not None else Path(tempfile.mkdtemp())
        work.mkdir(parents=True, exist_ok=True)
        for prior_id in args.synthetic_prior:
            inputs = with_synthetic_prior(folder, root, layout, inputs, prior_id, work)
        outcome = measure(folder, root, work, inputs, perts)
        # Inside the try (v0.2.3 rework): a write OSError is a tool failure
        # (exit 2), not a traceback with exit 1 ("missed").
        header = provenance_header(folder, layout, perts) + case_lines(inputs, folder, layout)
        resolve_output(args.output, folder, layout).write_text(render(header, outcome),
                                                               encoding="utf-8")
    except (ToolFailure, PerturbationDataError, validator.InputError, OSError,
            UnicodeDecodeError) as exc:
        print(f"sensitivity: {exc}", file=sys.stderr)
        return EXIT_TOOL_FAILURE
    if not perts:
        # v0.6.0: an empty set measured nothing; like a pending, never 0.
        print("sensitivity: Caught 0 of 0; the set is empty, nothing was measured", file=sys.stderr)
        return EXIT_EMPTY
    clean = outcome.caught == outcome.measured and not outcome.noisy
    return EXIT_OK if clean else EXIT_MISSED


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
