# Reflexive application of the method

How to assemble the production cell that applies the method of
`../01-principle.md` to any target that meets the four conditions the
principle states: a generic recipe and three designed sketches of
instances, not executed (a brand-new car, a long text about the world in
2027, an HPC library). The first round of this folder, and only that round,
was a production under the method: a brief, a canon, an artifact graph,
cards, gates, a validator in code, one review from a separate session with a
frozen rubric, notes and lessons. The rounds after it (v0.2 on) are
maintenance rounds of the material, not productions: each is recorded in
the round record with `kind` maintenance, its scope and the reviewer's
relation to the producer, emits no verdict of the canon, and its decisions
are in `../CHANGELOG.md` (see `00-brief.md`, "Maintenance rounds after the
stopping criterion"). The terms follow the [canon](01-canon.md).

## Where to start

- To apply the method to a new target: `10-generic-recipe.md`; the three
  instances show what an artifact, a gate and a rubric are in each domain,
  as designed sketches, not executions.
- To see how this folder was made: `00-brief.md`, `02-artifacts.md`,
  `04-gates-and-rubric.md` and `99-lessons.md`.

## Index

| File or folder | What it is |
| --- | --- |
| `00-brief.md` | the brief of this production: target, non-negotiables, owner decisions, budget and stopping criterion (one review round), and the maintenance rounds after it |
| `01-canon.md` | method terms with canonical definition, terms to avoid, fixed lists the validator reads, form rules, the recorded facts of the one executed prior |
| `02-artifacts.md` | the list and the graph of the artifacts of this folder, with owner, dependencies, schema and gates |
| `03-roles/` | the cards of the four roles: writer, verifier, runner (who runs the validator), reviewer |
| `04-gates-and-rubric.md` | the gates with magnitude, limit and justification; the size ranges; the instrument measurements; the review rubric, frozen by hash |
| `05-contracts/` | the JSON schemas of the contracts: the note ledger, its state ledger, the instance registry, the round record and the result of a domain gate |
| `06-gate-semantics.md` | what each gate reads in detail (declared readings, exceptions, reach, provenance); the gate lifecycle; the provenance of the rubric |
| `10-generic-recipe.md` | the step by step, from 0 to 14, with what each step reads, creates, does and when it is done; templates to copy |
| `20-instance-car.md` | instance 1: brand-new electric vehicle up to release for tooling |
| `21-instance-text-2027.md` | instance 2: nonfiction book about the world in 2027 |
| `22-instance-hpc.md` | instance 3: HPC library with measured speedup and identical result |
| `60-experiments.md` | the experiments about the method itself: protocol and predictions written before measuring, results, what each shows and does not show |
| `80-validator/` | the validator (`validator.py`), the sensitivity test (`sensitivity.py`), their tests and their reports |
| `90-review/` | frozen rubric (`rubric.sha256`), the reviewer's report and notes, replies, open notes (`notes.json`) |
| `99-lessons.md` | what each round taught about the documents and about the method |
| `state/round-record.jsonl` | one line per round: method version, executors by family and effort, summary; since v0.6.0 its kind, the reviewer's relation and the hash chain |
| `state/notes-status.jsonl` | the state of each note of the frozen ledger and of each panel finding that became a correction; append-only and chained since v0.6.0, the last line of a note is its state |

At the root of the material: `../VERSION` and `../CHANGELOG.md` (the version
of the method and its history), `../instances/registry.json` (the
registered instances; each executed prior is pinned by sha256) and
`../instances/004-adoption-guide/`, the cell of the one executed
instance, distributed with the material since v0.5.0. That cell ran under
method version 0.2.2 and is a record, not an example: it does not run under
the current validator without a migration (the migration note of the
changelog), its own validator refuses to run without `--historical`, and
its `ERRATA.md` lists what its guide says that is no longer true. Also at
the root, since v0.7.1, `../benchmark/`: the seeded material and the
annotated answer keys of experiment E4, kept unchanged for later runs; it
holds the answers and is never a reviewer's input.

## Status

The review of round 1 gave `rejected` for the version it read (one
blocking, two high). The three were fixed and checked by the gates, without
a second review, per the stopping criterion of the brief. The 22 remaining
notes are kept, frozen, in `90-review/notes.json`; their state is in
`state/notes-status.jsonl`, which `p-notes` reads: of those 22 notes, 6
were fixed by later rounds and 16 are open, each scheduled since v0.6.0 for
the round that next edits its document and rescheduled in v0.7.0, whose scope
was the owner's decisions (the counts of the report's
`p-notes` row are of every tracked line, the panels' findings included, not
of these 22). The same ledger records the findings of the panels
that reviewed v0.4.2 and v0.5.0, with the state of each (since v0.6.0 a new
line restates a finding whose state changed). The v0.2 round renamed the
vocabulary and corrected the corpus; since v0.7.0 the one executed instance
behind this material is `004-adoption-guide` (one execution, documentary, by
the owner); see `../CHANGELOG.md`.

## How to run the validator

```text
# only for a new rubric; this corpus is already frozen (the command refuses)
python3 80-validator/validator.py --folder . --freeze-rubric 90-review/rubric.sha256
python3 80-validator/sensitivity.py --folder . \
    --case ../instances/004-adoption-guide/metodo-de-producao.md \
    --rubric-hash 90-review/rubric.sha256 --notes 90-review/notes.json \
    --work SCRATCH_FOLDER --output 80-validator/sensitivity.md
python3 80-validator/validator.py --folder . \
    --case ../instances/004-adoption-guide/metodo-de-producao.md \
    --rubric-hash 90-review/rubric.sha256 --notes 90-review/notes.json \
    --allow-pending p-anonymity --determinism --output 80-validator/report.md
python3 80-validator/validator.py --self-test
python3 -B -m pytest -p no:cacheprovider 80-validator/test_validator.py \
    ../skills/cooperatio-teamwork/scripts/test_scaffold.py \
    ../skills/cooperatio-teamwork/scripts/test_install.py
```

The scripts need Python 3.9 or later and the standard library; the suites
need `pytest`. They write no bytecode cache into the folder by themselves:
each switches the cache off before it imports anything local, and each
child Python run they start gets `-B` (since v0.4.2). The test suites are
the one exception the scripts cannot cover: pytest imports the test files
and the validator before any of their code runs, so every pytest command of
the material carries `-B`, and `-p no:cacheprovider` keeps its own cache
folder out. With `--output`, the report goes to the file and one line with
the exit code, the notes and the pending not accepted goes to the error
stream.

`--freeze-rubric` refuses to overwrite an existing pin: re-freezing the
rubric after a review would make the verdicts incomparable, so a deliberate
replacement goes through `--re-freeze-rubric FILE`, with the reason recorded
in `../CHANGELOG.md`. The freeze resolves the rubric through the layout: a
cell that names its rubric in `artifacts.rubric` freezes that file; this
corpus, without the key, freezes the "## Rubric" section of
`04-gates-and-rubric.md`.

Operational note (provenance): editing `80-validator/validator.py`, the
"Gates" section of `04-gates-and-rubric.md` (its size ranges included),
`01-canon.md` or the map of the artifact table (which file each artifact
names, and which gates) changes a sha its sensitivity report records —
regenerate `80-validator/sensitivity.md` with the command above (and then
the report) before the next validator run, or `p-sensitivity` fails on
provenance. Every sha256 is taken over the text read as UTF-8, without a
byte-order mark and with LF line breaks, so a CRLF checkout keeps them.

Exit codes: 0 when every gate was measured, or its pending was accepted by
name, and no note is high or blocking; 1 with such a note; 2 for a tool
failure (a layout key the validator does not read, a file that is not
UTF-8, a truncated table row, a gate it does not implement, a gate with two
rows, a gate named by `--allow-pending` outside its closed list, a domain
result that breaks its contract); 4 when a gate is pending and
`--allow-pending` does not name it. `--allow-pending` accepts only
`p-anonymity`, `p-prior`, `p-prior-pin` and `p-sensitivity-synthetic`, a
closed list that exists for what a cell may not distribute (the second and
third for a prior held outside its material, the last for a report made with
a synthetic prior, never a pass); this corpus needs only `p-anonymity`. A
missing sensitivity report is blocking, never a pending.

The list of forbidden identifiers stays out of the material, so that it does
not contain what it forbids; this corpus has none, so the identifier part of
`p-anonymity` is pending in every document, and the run above accepts that
pending by name, which the report prints. The published report is made
with exactly that command, and a clone that runs it measures every number
stated about a prior, since the one executed prior is distributed. The
instance registry (`../instances/registry.json`)
is found by default; the prior method document is passed with `--case`
(identified by its sha256 in the registry). Without
`--case`, the number check of the `p-prior` gate, the section commitments
of the canon and the sha256 pin of the `p-prior-pin` gate are pending; without
`--notes`, so is the note ledger gate `p-notes`, with the state ledger of
the notes, and that pending cannot be accepted. A pending gate is neither a
pass nor a fail, and it exits 4 unless accepted. The sensitivity test takes
the same inputs: without `--case`, `--rubric-hash` or `--notes`, the rows
that need them are not measured, and `p-sensitivity` refuses the report.

### What a clone runs, and the mechanism for a prior held elsewhere

A clone of this material runs the commands above as they are: the document
of `004-adoption-guide` is distributed, so its pin, its numbers and the
sections the canon commits to are measured (its edited document, or an
invented number about it, is a blocking note, exit 1), and the sensitivity
report can be regenerated by anyone who edits the instrument. Its header
records the sha256 of the prior document it was made with (`case sha256:`
line) and an attestation of it (`case attestation:`, over the document's text
and the provenance), and a run with the document recomputes both. Without
any `--case`, the five rows of the set that need the prior are not measured,
and `p-sensitivity` refuses the report for the rows it did not measure; the
report stays valid only while the validator, the canon, the "Gates" section
of `04-gates-and-rubric.md` and the gate map stay as they are, and deleting
it does not help, since a missing report is blocking.

The instrument keeps a generic mechanism for a cell whose prior is held
outside its material, which this material does not use. Its registry entry
carries the reserved locator `owner-held, not distributable`; the run without
that document leaves the rows of that prior pending by name, with the notice
"owner-held evidence, not measured here", accepted only with
`--allow-pending p-prior,p-prior-pin`. A maintainer without the document
regenerates the sensitivity report with `sensitivity.py --synthetic-prior
PRIOR_ID`, which generates a document from the canon's recorded facts in the
heading style the registry declares and pins it in the copies only; the
validator tells that report by its `case sha256` differing from the pin and
never reads it as a pass (`p-sensitivity-synthetic`, pending, accepted only
by name, and refused in a run that passes the real document). What that
report does not show is that the real document holds the facts, nor that the
validator reads the real format. `06-gate-semantics.md` has the detail.
