#!/usr/bin/env python3
"""The perturbation set of the sensitivity test, as data (v0.6.0).

The known defects of this corpus, the dataclass of a perturbation and the
reader of a cell's perturbation file live here, apart from the script that
runs them, so that the validator reads the set (to check the provenance of
a report) without importing the sensitivity script, and the sensitivity
script imports the validator without a cycle. Standard library only.
"""

from __future__ import annotations

import dataclasses
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True


class PerturbationDataError(ValueError):
    """Raised when a cell's perturbation file is not the documented list."""


# The results a perturbation can expect of its gate on its document: a fail,
# or a pending (an emptied list of the canon measures nothing, v0.5.0).
EXPECTED_RESULTS = ("fail", "pending")
# Words appended by the p-size perturbation: more than any maximum of the
# "Size ranges" table, so the document leaves its range whatever its size.
SIZE_PADDING_WORDS = 10000
SIZE_PADDING = " ".join(["padding"] * SIZE_PADDING_WORDS)


@dataclass(frozen=True)
class Perturbation:
    """One known defect. 'old' -> 'new' is replaced once in 'document'
    (relative to the folder; '../instances/registry.json' is the copied
    registry); with 'delete' the document is removed instead. The needs_*
    flags name the validator inputs the expected gate cannot run without
    (needs_registry: the perturbed document is the copied registry).
    'expect' is the result the gate has to give on the document: 'fail',
    or 'pending' for a defect that empties what the gate reads. 'prior'
    (v0.6.0) names the registered prior whose method document the gate
    needs: without a --case document identified as it, the row is not
    measured, whatever other prior was passed."""
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
    prior: str = ""
    # Gates the defect also reaches by design, comma-separated (v0.6.0): a
    # pin decides which document is the prior, so p-prior moves with
    # p-prior-pin. Their rows are not counted as noise, and the report
    # prints them, so the cross-talk is declared rather than hidden.
    also: str = ""


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
PRIOR_004 = "004-adoption-guide"
NAMED_DATE_SAMPLE = " ".join(("29", "October", "2026"))
LESSONS_V050_HEADING = "## The v0.5.0 round: exit 0 is not green"
# Headings of the recipe a perturbation of the prior gates writes after.
STEP_13_HEADING = "### Step 13. Declare the stop and record the open notes"
STEP_14_HEADING = "### Step 14. Write the case method document and register the instance"

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
    Perturbation("prior number altered", "../01-principle.md",
                 "produced a guide of 1054 words", "produced a guide of 1055 words", "p-prior",
                 needs_case=True, prior=PRIOR_004),
    Perturbation("step field deleted", "10-generic-recipe.md",
                  "- **Done when:** the tree exists;", "- the tree exists;", "p-recipe"),
    Perturbation("gate justification deleted", "22-instance-hpc.md",
                  "| \u2264 1.10 | [hypothesis] the owner accepts little extra spending; the magnitude forces "
                  "declaring the cost of each lever that trades memory for time |",
                  "| \u2264 1.10 |  |", "p-limit"),
    Perturbation("cycle in the graph", "02-artifacts.md",
                 "| `brief` | `00-brief.md` | writer | `corpus` |",
                 "| `brief` | `00-brief.md` | writer | `corpus`, `readme` |", "p-references",
                 also="p-references"),
    Perturbation("note aimed at a missing artifact", "21-instance-text-2027.md",
                 "to the `domain-dossier`, per error found in a source",
                 "to the `corpus`, per error found in a source", "p-references"),
    Perturbation("card field deleted", "03-roles/reviewer.md",
                 "**Does not decide:**", "**Also:**", "p-card"),
    Perturbation("statement about the prior without the mark", "10-generic-recipe.md",
                 STEP_14_HEADING,
                 STEP_14_HEADING + "\n\nIn the reference case, the review accepted the guide.",
                 "p-prior-mark"),
    Perturbation("method component omitted", "22-instance-hpc.md",
                  "The artifact graph:", "The design:", "p-components"),
    Perturbation("schema cell points to a missing file", "02-artifacts.md",
                 "the contract in `05-contracts/notes.schema.json`",
                 "the contract in `05-contracts/gone.schema.json`", "p-contract-shape",
                 also="p-contract-shape"),
    # v0.4.0: one perturbation per gate that had none.
    Perturbation("link to the canon does not resolve", "00-brief.md",
                 "[canon](01-canon.md)", "[canon](../01-canon.md)", "p-canon-link"),
    Perturbation("document pushed above its size range", "00-brief.md",
                 "## What is not a goal", "## What is not a goal\n\n" + SIZE_PADDING, "p-size"),
    Perturbation("mandatory section heading removed", "20-instance-car.md",
                 "## 7. Validator", "## 7. Consistency checker", "p-sections"),
    Perturbation("prior pin altered in the registry", "../instances/registry.json",
                 '"sha256": "2cf0', '"sha256": "fcf0', "p-prior-pin", needs_case=True, also="p-prior",
                 prior="004-adoption-guide"),
    Perturbation("rubric edited after the freeze", "04-gates-and-rubric.md",
                 "Mechanical, applied to the scores and findings:",
                 "Mechanical, applied to the scores and to the findings:",
                 "p-frozen-rubric", needs_rubric_hash=True),
    Perturbation("note with an invalid severity", "90-review/notes.json",
                 '"severity": "low"', '"severity": "trivial"', "p-notes", needs_notes=True,
                 also="p-contract-shape, p-frozen-rubric"),
    Perturbation("declared document deleted", "21-instance-text-2027.md",
                 "", "", "p-declared", delete=True),
    Perturbation("claim of efficacy without a label", "10-generic-recipe.md",
                 "It pays off when erring is expensive [hypothesis].",
                 "It pays off when erring is expensive.", "p-efficacy-mark"),
    # Found by the review of v0.4.0: a number that occurs in the prior's
    # document, in an unrelated sentence, passed by presence in the whole
    # document; a number needs its row in "Recorded facts".
    Perturbation("prior number without a recorded fact", "60-experiments.md",
                 "and no dimension below 4 [prior:004-adoption-guide].",
                 "and no dimension below 4, over 77 notes [prior:004-adoption-guide].",
                 "p-prior", needs_case=True, prior=PRIOR_004),
    # v0.4.1: the contract of a registry entry by status, and a claim
    # backed by an experiment that has not run.
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
                 "family C (see /etc/executors/c.txt)", "p-anonymity", also="p-contract-shape"),
    # v0.5.0: one perturbation per false green the panel that reviewed
    # v0.4.2 demonstrated, so each correction stays measured.
    Perturbation("gate row deleted", "04-gates-and-rubric.md",
                 RECIPE_GATE_ROW, "", "p-references", also="p-recipe"),
    Perturbation("prior mark inside a code span", "60-experiments.md",
                 "The product of the executed adoption-guide instance: its guide, of 1054\n"
                 "words, which its one review accepted [prior:004-adoption-guide].",
                 "The product of the executed instance: its guide, of 1054\n"
                 "words, which its one review accepted `[prior:004-adoption-guide]`.",
                 "p-prior-mark"),
    Perturbation("placeholder in a card field", "03-roles/writer.md",
                 "**Decides:**", "**Decides:** <fill in>", "p-card", also="p-form"),
    Perturbation("canon list emptied", "01-canon.md",
                 AVOID_TABLE_ROWS, "", "p-terms", expect="pending", also="p-terms"),
    Perturbation("placeholder in a gate row", "04-gates-and-rubric.md",
                 "| 11 of 11 |", "| <to be set> |", "p-limit", also="p-form"),
    Perturbation("date written with the month's name", "00-brief.md",
                 "## Assumptions", "## Assumptions (as of " + NAMED_DATE_SAMPLE + ")",
                 "p-anonymity"),
    Perturbation("claim of efficacy in the lessons", "99-lessons.md",
                 LESSONS_V050_HEADING,
                 LESSONS_V050_HEADING + "\n\nSeparate roles are the only way to stop a defect.",
                 "p-efficacy-mark"),
    Perturbation("limit raised in the gate table", "04-gates-and-rubric.md",
                 "or with fewer than 6 words", "or with fewer than 60 words", "p-limit",
                 also="p-limit"),
    Perturbation("note without a status line", "state/notes-status.jsonl",
                 '{"ref": "notes:1", ', '{"ref": "panel:0.4.2:XX1", ', "p-notes", needs_notes=True,
                 also="p-contract-shape"),
    # v0.6.0: the probes of the panel that reviewed v0.5.0 that became a
    # correction, so each stays measured.
    Perturbation("file of an artifact repointed", "02-artifacts.md",
                 "| `instance-hpc` | `22-instance-hpc.md` |", "| `instance-hpc` | `20-instance-car.md` |",
                 "p-declared"),
    Perturbation("literal file of an artifact deleted", "80-validator/report.md",
                 "", "", "p-declared", delete=True),
    Perturbation("sensitivity report deleted", "80-validator/sensitivity.md",
                 "", "", "p-declared", delete=True),
    Perturbation("prior mark with an uppercase id", "20-instance-car.md",
                 "## 7. Validator", "## 7. Validator\n\nSee [prior:004-ADOPTION-guide].",
                 "p-prior"),
    Perturbation("prior number in a code span", "10-generic-recipe.md",
                 STEP_13_HEADING,
                 STEP_13_HEADING + "\n\nThe guide has `1056` words [prior:004-adoption-guide].",
                 "p-prior", needs_case=True, prior=PRIOR_004),
    Perturbation("placeholder in an instance artifact table", "22-instance-hpc.md",
                 "| `specification` | public headers |", "| `specification` | TBD |", "p-references"),
    Perturbation("tilde fence without the text mark", "00-brief.md",
                 "## What is not a goal", "## What is not a goal\n\n~~~sh\nls\n~~~", "p-form"),
    Perturbation("indented fence without the text mark", "00-brief.md",
                 "## Budget and stopping criterion",
                 "## Budget and stopping criterion\n\n- item\n\n  ```sh\n  ls\n  ```", "p-form"),
    Perturbation("HTML comment", "00-brief.md", "## Target", "## Target\n\n<!-- a hidden note -->",
                 "p-form"),
    Perturbation("claim of efficacy without a label in the principle", "../01-principle.md",
                 "and err less** [hypothesis].", "and err less**.", "p-efficacy-mark"),
    Perturbation("label citing a designed experiment in the record", "60-experiments.md",
                 "compare [lessons:The v0.4.0 round: evidence about the method is subject to the method]",
                 "compare [experiment:E2]", "p-efficacy-mark"),
    Perturbation("limit cell diverges from the applied limit", "04-gates-and-rubric.md",
                 "| 0 | [method] a synonym outside the canon", "| 5 | [method] a synonym outside the canon",
                 "p-references"),
    Perturbation("old line of the round record edited", "state/round-record.jsonl",
                 "seven panel recommendations applied", "eight panel recommendations applied",
                 "p-contract-shape"),
    Perturbation("old line of the state ledger edited", "state/notes-status.jsonl",
                 "does not match its symptom", "matches its symptom", "p-contract-shape"),
    Perturbation("lessons label naming no entry", "99-lessons.md",
                 "[lessons:The v0.5.0 round: exit 0 is not green]",
                 "[lessons:The v0.5.0 round: a round that never was]", "p-efficacy-mark"),
    Perturbation("section commitment altered", "01-canon.md",
                 "| `[prior:004-adoption-guide]` | 4.4 | `", "| `[prior:004-adoption-guide]` | 5 | `",
                 "p-prior", needs_case=True, prior=PRIOR_004),
    # Coverage by (document, gate) pair (v0.6.0): one known defect on
    # documents and gates no earlier perturbation reached.
    Perturbation("absolute path in the root README", "../README.md",
                 "## License", "## License (see /etc/license/notes.txt)", "p-anonymity"),
    Perturbation("HTML tag in the skill", "../skills/cooperatio-teamwork/SKILL.md",
                 "## The one idea", "## The <b>one</b> idea", "p-form"),
    Perturbation("avoid-word in the changelog", "../CHANGELOG.md",
                 "# Changelog", "# Changelog of the pipeline", "p-terms"),
    Perturbation("link to the canon broken in the README", "README.md",
                 "[canon](01-canon.md).", "[canon](../01-canon.md).", "p-canon-link"),
    Perturbation("contract of another version", "05-contracts/round-record.schema.json",
                 '"contract_version": "1"', '"contract_version": "2"', "p-contract-shape"),
    Perturbation("date in the gate semantics", "06-gate-semantics.md",
                 "## `p-terms`: the frozen ledger",
                 "## `p-terms`: the frozen ledger (as of " + NAMED_DATE_SAMPLE + ")", "p-anonymity"),
    Perturbation("canon pushed above its size range", "01-canon.md",
                 "## Form rules", "## Form rules\n\n" + SIZE_PADDING, "p-size"),
    Perturbation("card field deleted in the runner card", "03-roles/runner.md",
                 "**Does not decide:**", "**Also:**", "p-card"),
    # The second pass of v0.6.0: the records frozen by the canon, the ledger
    # of the owner's decisions and the skill's references under their gates.
    Perturbation("frozen review report rewritten", "90-review/auditor-report.md",
                 "verdict as `rejected`.", "verdict as `accepted`.", "p-frozen-rubric"),
    Perturbation("frozen replies rewritten", "90-review/replies.md",
                 "# Replies to the review notes", "# Replies to the notes", "p-frozen-rubric"),
    Perturbation("history of the lessons edited", "99-lessons.md",
                 "## What became a gate or a rule in this round",
                 "A sentence added to the history.\n\n## What became a gate or a rule in this round",
                 "p-frozen-rubric"),
    Perturbation("owner decision line edited", "state/owner-decisions.jsonl",
                 '"name": "sign the tag of the version"', '"name": "sign the tag"',
                 "p-contract-shape"),
    Perturbation("HTML tag in the templates", "../skills/cooperatio-teamwork/references/templates.md",
                 "# Templates", "# <b>Templates</b>", "p-form"),
    Perturbation("absolute path in the review checklist",
                 "../skills/cooperatio-teamwork/references/review-checklist.md",
                 "## Structure", "## Structure (see /etc/review/notes.txt)", "p-anonymity"),
)


def select(folder: Path, layout: dict, corpus: tuple[Perturbation, ...] = PERTURBATIONS
           ) -> tuple[Perturbation, ...]:
    """The perturbations of a production: the data file a cell names with
    the layout key artifacts.perturbations, or the corpus set."""
    data_file = layout["artifacts"].get("perturbations")
    if data_file is None:
        return tuple(corpus)
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
    if "," in item["name"]:
        # The provenance header lists the names comma-separated.
        raise PerturbationDataError(f"{where}: a name carries no comma")
    return Perturbation(**{"old": "", "new": "", **item})
