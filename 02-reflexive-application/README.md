# Reflexive application of the method

How to assemble the production cell that applies the method of
`../01-principle.md` to any target that meets the four conditions the
principle states: a generic recipe and three designed instances (a
brand-new car, a long text about the world in 2027, an HPC library). The
first round of this folder was produced by the method: a brief, a canon, an
artifact graph, cards, gates, a validator in code, one independent review
with a frozen rubric, notes and lessons. The rounds after it (v0.2 on) are
maintenance rounds outside that brief's stopping criterion, run by an
orchestrator with decisions the owner delegated, and recorded in
`../CHANGELOG.md` and the round record (see `00-brief.md`, "Maintenance
rounds after the stopping criterion"). The terms follow the
[canon](01-canon.md).

## Where to start

- To apply the method to a new target: `10-generic-recipe.md`, then the
  instance most similar to your target.
- To see how this folder was made: `00-brief.md`, `02-artifacts.md`,
  `04-gates-and-rubric.md` and `99-lessons.md`.

## Index

| File or folder | What it is |
| --- | --- |
| `00-brief.md` | the brief of this production: target, non-negotiables, owner decisions, budget and stopping criterion (one review round), and the maintenance rounds after it |
| `01-canon.md` | method terms with canonical definition, terms to avoid, fixed lists the validator reads, form rules, recorded facts of the prior instance [prior:000-av-production] |
| `02-artifacts.md` | the list and the graph of the artifacts of this folder, with owner, dependencies, schema and gates |
| `03-roles/` | the cards of the four roles: writer, verifier, validator, reviewer |
| `04-gates-and-rubric.md` | the gates with magnitude, limit and justification; the size ranges; the instrument measurements; the review rubric, frozen by hash |
| `05-contracts/` | the JSON schemas of the contracts: the note ledger, the instance registry and the round record |
| `06-gate-semantics.md` | what each gate reads in detail (declared readings, exceptions, reach, provenance); the gate lifecycle; the provenance of the rubric |
| `10-generic-recipe.md` | the step by step, from 0 to 14, with what each step reads, creates, does and when it is done; templates to copy |
| `20-instance-car.md` | instance 1: brand-new electric vehicle up to release for tooling |
| `21-instance-text-2027.md` | instance 2: nonfiction book about the world in 2027 |
| `22-instance-hpc.md` | instance 3: HPC library with measured speedup and identical result |
| `60-experiments.md` | the experiments about the method itself: protocol and predictions written before measuring, results, what each shows and does not show |
| `80-validator/` | the validator (`validator.py`), the sensitivity test (`sensitivity.py`), their tests and their reports |
| `90-review/` | frozen rubric (`rubric.sha256`), the reviewer's report and notes, replies, open notes (`notes.json`) |
| `99-lessons.md` | what each round taught about the documents and about the method |
| `state/round-record.jsonl` | one line per round: method version, executors by family and effort, summary |
| `state/notes-status.jsonl` | the state of each note of the frozen ledger and of each panel finding that became a correction |

At the root of the material: `../VERSION` and `../CHANGELOG.md` (the version
of the method and its history), `../instances/registry.json` (the
registered instances; each executed prior is pinned by sha256) and
`../instances/004-adoption-guide/`, the cell of the second executed
instance, distributed with the material since v0.5.0. That cell ran under
method version 0.2.2 and is history: it does not run under the current
validator without a migration (the migration notes of the changelog).

## Status

The independent review gave `rejected` for the version it read (one
blocking, two high). The three were fixed and checked by the gates, without
a second review, per the stopping criterion of the brief. The 22 remaining
notes are kept, frozen, in `90-review/notes.json`; their state is in
`state/notes-status.jsonl`, which `p-notes` reads: 6 were fixed by later
rounds and 16 are open. The same ledger records the findings of the panel
that reviewed v0.4.2 that became corrections. The v0.2 round renamed the
vocabulary, corrected the corpus and registered the prior instance
[prior:000-av-production]; see
`../CHANGELOG.md`.

## How to run the validator

```text
# only for a new rubric; this corpus is already frozen (the command refuses)
python 80-validator/validator.py --folder . --freeze-rubric 90-review/rubric.sha256
python 80-validator/sensitivity.py --folder . \
    --case PRIOR_000_DOCUMENT_PATH \
    --case ../instances/004-adoption-guide/metodo-de-producao.md \
    --rubric-hash 90-review/rubric.sha256 --notes 90-review/notes.json \
    --work SCRATCH_FOLDER --output 80-validator/sensitivity.md
python 80-validator/validator.py --folder . \
    --case PRIOR_000_DOCUMENT_PATH \
    --case ../instances/004-adoption-guide/metodo-de-producao.md \
    --rubric-hash 90-review/rubric.sha256 --notes 90-review/notes.json \
    --allow-pending p-anonymity --determinism --output 80-validator/report.md
python 80-validator/validator.py --self-test
python -B -m pytest -p no:cacheprovider 80-validator/test_validator.py \
    ../skills/cooperatio-teamwork/scripts/test_scaffold.py
```

The two scripts write no bytecode cache into the folder by themselves:
each switches the cache off before it imports anything local, and each
child Python run they start gets `-B` (since v0.4.2; before, a cache was
left beside the scripts, an undeclared file in the material). The test
suites are the one exception the scripts cannot cover: pytest imports the
test files and the validator before any of their code runs (the scaffold
suite loads the validator too), so every pytest command of the material
carries `-B`, and `-p no:cacheprovider` keeps its own cache folder out.

`--freeze-rubric` refuses to overwrite an existing pin: re-freezing the
rubric after a review would make the verdicts incomparable, so a deliberate
replacement goes through `--re-freeze-rubric FILE`, with the reason recorded
in `../CHANGELOG.md`. The freeze resolves the rubric through the layout: a
cell that names its rubric in `artifacts.rubric` freezes that file; this
corpus, without the key, freezes the "## Rubric" section of
`04-gates-and-rubric.md`.

Operational note (provenance): editing `80-validator/validator.py`, the
"Gates" section of `04-gates-and-rubric.md` (its size ranges included) or
`01-canon.md` changes a sha its sensitivity report records — regenerate
`80-validator/sensitivity.md` with the command above (and then the report)
before the next validator run, or `p-sensitivity` fails on provenance.

Exit codes: 0 when every gate was measured, or its pending was accepted by
name, and no note is high or blocking; 1 with such a note; 2 for a tool
failure (a layout key the validator does not read, a file that is not
UTF-8, a truncated table row, a gate it does not implement); 4 when a gate
is pending and `--allow-pending` does not name it. Since v0.5.0 exit 0 is
no longer "nothing failed, whatever was measured".

The list of forbidden identifiers stays out of the material, so that it does
not contain what it forbids; this corpus has none, so the identifier part of
`p-anonymity` is pending in every document, and the run above accepts that
pending by name, which the report prints. The published report is made
with exactly that command. The instance registry (`../instances/registry.json`)
is found by default; each prior method document is passed with its own
`--case` (each is identified by its sha256 in the registry). Without
`--case`, the number check of the `p-prior` gate and the sha256 pin
of the `p-prior-pin` gate are pending, and a cited prior whose document was
not passed is pending by name; without `--notes`, so is the note ledger gate
`p-notes`, with the state ledger of the notes. A pending gate is neither a
pass nor a fail, and it exits 4 unless accepted. The sensitivity test takes
the same inputs: without `--case`, `--rubric-hash` or `--notes`, the rows
that need them are not measured, and `p-sensitivity` refuses the report.

### Without the owner-held document of 000

The method document of the prior instance 000 stays with the owner (the
registry says "owner-held, not distributable"), so a clone of this material
does not have it. Without it, the run that reaches exit 0 passes no
`--case` at all and accepts by name the gates that need it:

```text
python 80-validator/validator.py --folder . \
    --rubric-hash 90-review/rubric.sha256 --notes 90-review/notes.json \
    --allow-pending p-anonymity,p-prior,p-prior-pin --determinism
```

Expected: exit 0, no notes, the report on the standard output, and the
three gates listed as pending accepted by the caller. Passing only the
document of 004 is not a smaller form of the same run: the prior 000, cited
in the documents, then has no document that matches its pin, which is a
blocking note of `p-prior-pin` (exit 1), not a pending.

The sensitivity report can only be regenerated with the owner's document.
Without it, the four rows that need a prior are not measured, the report
reads "Caught 31 of 31. Not measured: 4.", and `p-sensitivity` refuses it
as measuring 31 of 35. The published report stays valid only while the
validator, the canon and the "Gates" section of `04-gates-and-rubric.md`
stay as they are: a clone that edits any of them cannot get back to green
without the owner.
