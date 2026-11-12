# Cooperatio

**Status: a working hypothesis, with a documentary validator; the gates of
a target's domain enter as results the cell's own code produces and the
validator checks; one executed instance, documentary, by the owner,
auditable from this material.** See "Status" below for what that covers and what it does not.

Method version 0.7.2 (see `VERSION`; the history of the changes, in
`CHANGELOG.md`). The terms follow the
[canon](02-reflexive-application/01-canon.md) of the reflexive application.

A method for organizing a team — people, agents and code — around a complex
target, and a skill that creates the files that set that team up.

The idea in one sentence: produce the target by compiling a graph of typed
artifacts, each with an owner, a contract and a measurable gate; let separate
roles talk only through artifacts and notes; measure what the system delivered
rather than what was requested; have each review made by someone who did not
produce, with a rubric frozen before it, so that rounds are comparable; turn
every error that escapes into a new gate; and stop at a criterion declared in
advance. A reviewer of another family than the producer's is recommended, a
hypothesis with a cost (a second provider), not a rule: the one datum is
against it as a rule. A pilot showed a frozen rubric with a mechanical
verdict rule turning a finding into a verdict; the one measurement of the
review apparatus that followed, experiment E4, withdrew the claim that it
adds to a careful review: on seeded defects, reviewers with the validator
and the frozen rubric let no fewer escape than reviewers with a checklist,
for more input tokens [against:E4] (the principle, sections 2, 7 and 9).

## Contents

| Path | What it is |
| --- | --- |
| [`01-principle.md`](01-principle.md) | The method: the idea, the scheme, the components, the golden rules, what changes by domain, how to instantiate it, warning signs, limits, what would promote or withdraw a claim, and ontological assumptions |
| [`02-reflexive-application/`](02-reflexive-application/) | The method applied to itself: a generic recipe, three designed sketches of instances (a physical product, a long text, a software library; designed, not executed), the role cards, the gates and rubric, a validator and a sensitivity test written as code, the experiments about the method, the review of its first round and the lessons of every round |
| [`skills/cooperatio-teamwork/`](skills/cooperatio-teamwork/) | An agent skill that creates the teamwork files (brief, canon, artifact graph, role cards, gates, rubric, notes) for a target whose quality documents can carry, or whose domain measurements the cell's own code can write as results; its scaffold copies the validator and the sensitivity test of this material into the new cell |
| [`benchmark/`](benchmark/) | The seeded material of experiment E4 and its annotated answer keys, kept unchanged so that a later run compares with it: a guide with three seeded copies, and three anonymized open-source program excerpts with their seeded copies, licenses and notices. It holds the answers: never give it to a reviewer (see its `README.md`) |
| [`instances/`](instances/) | The registry of the known instances (`registry.json`) and the cell of the one executed instance (`004-adoption-guide/`), the record of an execution under method version 0.2.2: read its [`ERRATA.md`](instances/004-adoption-guide/ERRATA.md) first; it is not an example to copy. Its list of forbidden identifiers stayed with the owner, outside the material, since it contains what it forbids |
| [`docs/`](docs/) | The manual of the method and of its instrument (`docs/manual/manual.pdf`, its Markdown source and diagrams), with a chapter on installing the skill, and a curated record of the sessions that produced the material (`docs/history/`); where the manual and the material disagree, the material wins |
| `VERSION`, `CHANGELOG.md`, `LICENSE`, `.gitattributes` | The version of the method, its history, the license, and the rule that checks every text file out with LF line breaks (the hash policy of the material) |

## Where to start

- To understand the method, read [`01-principle.md`](01-principle.md).
- To apply it to a new target, read
  [`02-reflexive-application/10-generic-recipe.md`](02-reflexive-application/10-generic-recipe.md);
  the three instances there are designed sketches that show what an
  artifact, a gate and a rubric are in each domain, not executions.
- For a guided reading of all of it, with diagrams and the commands
  verified, read the manual, `docs/manual/manual.pdf`.
- To have an agent create the files for you, install the skill in
  [`skills/cooperatio-teamwork/`](skills/cooperatio-teamwork/) (see its
  `SKILL.md`) and ask it to set up teamwork for your target.

Requirements: Python 3.9 or later for the scripts (they exit 2 below it),
the standard library only; `pytest` for the test suites.

### The ten-minute path

1. Read the first section and section 7 of
   [`01-principle.md`](01-principle.md) (the idea and the recipe).
2. Run `python3 skills/cooperatio-teamwork/scripts/scaffold.py --target
   "My target" --roles writer reviewer --out ./teamwork` from inside the
   material.
3. Fill the brief, give each non-negotiable an id (`nn-<name>`), fill the
   lists of `02-canon.json` the validator reads and one card per role
   (the skill's `references/templates.md` has a filled example).
4. Freeze the rubric, run the sensitivity test, then the validator, with the
   commands of the skill ("The commands of a cell"); read every pending row
   before reading the exit code.

### What an adopter carries

Separated from the research the material also is (the reflexive
application, the experiments, the panels): the fixed cost of a cell is the
24 files the scaffold writes with two roles, among them the instrument it
copies, about 5,700 lines of Python (the validator 4,857, the sensitivity
test 550, its perturbation set 336) that the adopter runs and does not have to read, plus
one review per round. The history that matters to an adopter is the
"Migration note" of each version in `CHANGELOG.md`; the rest of the
changelog is the research.

## Using the skill

Install the skill into every agent harness found on the machine with its
installer, run from inside the material:

```text
python3 skills/cooperatio-teamwork/scripts/install.py --list   # what it knows and finds
python3 skills/cooperatio-teamwork/scripts/install.py          # link the skill
```

It detects a harness by its configuration folder in the home directory
(Claude Code, GitHub Copilot, pi, OpenCode, Codex, Gemini CLI, Cursor,
Windsurf and about twenty more; `--list` shows the table) and puts a
symbolic link to this folder in that harness's user-level skills folder, so
the scaffold still reaches the validator and a `git pull` updates every
harness. It never replaces an entry it did not make; `--copy` copies instead
of linking, `--harness NAME` picks harnesses, `--dry-run` changes nothing and
`--uninstall` removes what it installed. A harness that also reads another's
folder (OpenCode and Cursor read the skills folder of Claude Code) may list the skill twice.
Copying or linking the folder by hand works as well.

Then ask your agent for the teamwork files for a target. The skill also ships a small scaffolding script that creates the empty
folder structure without overwriting anything. The scaffold copies the
validator, the sensitivity test and four contracts from this material into
the new cell, so run it from inside the material (or keep the skill folder
inside it); copied alone, the skill creates the cell without them, says so,
and the cell has no validator until you copy one in:

```text
python3 skills/cooperatio-teamwork/scripts/scaffold.py \
    --target "My target" --roles writer verifier reviewer --out ./teamwork
```

## Running the validator

The validator in `02-reflexive-application/80-validator/` reads the
canon, the artifact list and the gates and measures every gate on every
document the artifact list assigns it to. Its self-test needs no inputs:

```text
python3 02-reflexive-application/80-validator/validator.py --self-test
```

The validator measures documents: terms, sections, links, form, numbers
stated about registered priors, the contracts and the chains of its
ledgers. A gate of a target's domain (the identity of a library's results,
a speedup, a mass) is measured by the cell's own code, which writes a
result file in the contract `domain-result.schema.json`; the validator reads
the result, refuses it when an input changed since it was written, and turns
a failure into a note and a missing result into a pending. It does not run
the cell's code. A run exits 0 only when every gate was measured, or its
pending was accepted by name with `--allow-pending`, whose closed list exists
for inputs a cell may not distribute (`p-anonymity`, `p-prior`, `p-prior-pin`
and `p-sensitivity-synthetic`); this material needs only `p-anonymity`, since
it has no forbidden list to distribute. A gate left unmeasured exits 4. The runbook is in
[`02-reflexive-application/README.md`](02-reflexive-application/README.md).

## What a clone verifies, and what rests on the owner

The validator checks the internal coherence of the material; the integrity
of its past rests on the version history, and the raw files of the
experiments rest on the owner.

| A clone verifies | Only the owner verifies |
| --- | --- |
| every gate on every document; the pin and every number stated about the one executed prior, `004-adoption-guide`, whose document is distributed (passed with `--case`); the frozen rubric; the provenance of the sensitivity report, the sha256 and the attestation of the prior document it was made with included; the hash chain of the three ledgers | no number stated about a registered prior: the one executed prior registered here is distributed |
| that a ledger line written since v0.6.0 was not edited without recomputing the chain (an honest or careless edit) | an edit that recomputed the chain (one sha256 per line, which no gate detects), the lines before the chain, the history of the lessons and the record of the experiments' raw files, the method document of a prior held by the owner that experiments E1 and E3 used as an input among them |
| the family letter each round line records, and the form of its salted commitment | the map from a family letter to a family, and its salt, which stay outside the material and prove the commitment |

A clone reaches exit 0 with the run the runbook gives: the document of
`004-adoption-guide` passed with `--case`, so its pin, its numbers and the
sections the canon commits to are measured, and only the identifier half of
`p-anonymity` accepted by name. The published sensitivity report is made with
the same distributed document; its header records the sha256 and the
attestation of that document, and the validator recomputes both, so a clone
that edits the validator, the canon, the "Gates" section of the gates file or
the gate map of the artifact table regenerates the report with the command of
the runbook, and a report whose `case` line does not match is refused. A
deleted report is blocking, and `p-sensitivity` cannot be accepted by name.
The instrument keeps, for a cell whose prior is held outside its material,
the generic mechanism: the reserved locator of the registry, a synthetic
prior that lets a clone regenerate a report (never read as a pass, pending
under `p-sensitivity-synthetic`) and an attestation only a holder of the text
can compute. This material registers no such prior; the runbook and
`02-reflexive-application/06-gate-semantics.md` say what the mechanism does.
The chain detects an edit nobody recomputed; it does not stop whoever
controls the whole tree, and an anchor outside it (a signed tag per
version) is the owner's to add. The git history distributes the name of the
author and the dates of the commits; the gates measure the content, not the
history. A pseudonym made of the hash of a host name or a user name is not
anonymity (a dictionary reverses it): the material uses family letters and
commits to their map with a salted hash the owner holds (since the rework
of v0.6.0; the canonical form is in `02-reflexive-application/06-gate-semantics.md`).

## Freeze policy

After 0.6.0 the instrument (the validator, the sensitivity test, the
scaffold) changes only for a failure that changes a verdict, for a new
execution, or by a decision of the owner recorded in the changelog (0.7.0
changed its data and comments that way, and no reading of a gate). The
budget of 0.7.1 went to measuring value: experiment E4, the seeded-escape
design of `02-reflexive-application/60-experiments.md`, ran and withdrew the
claim that the review apparatus adds to a careful review without it
[against:E4], and its seeded material is kept in `benchmark/`. What is left
to measure is portability (an execution outside the documentary domain by
someone who is not the owner), not more instrument.

## License

The material in this folder is licensed under the Apache License 2.0; the
full text is in [`LICENSE`](LICENSE).

## Status

**Working hypothesis — one executed instance, documentary, by the owner.**
One part of the method has never been exercised: the recompilation by hash.
In the one execution no engine rebuilt a stale artifact from the hash of its
inputs; the validator resolves the command an artifact declares against the
paths it names, and does not run it. The method stands on one executed
instance, registered in [`instances/registry.json`](instances/registry.json):
`004-adoption-guide`, the adoption guide of this method itself, whose cell is
distributed here and whose method document is pinned by sha256. The method
was generalized from earlier production work that is not part of this
material, and no claim here relies on it. Three designed instances (car,
text, HPC) are sketches, not executed. The scope of that evidence is narrow,
and it is declared rather than implied: one execution, a documentary
production by the owner, so portability beyond the documentary domain is an
assumption, not a result, and a rule the material states has at most that
one execution and the rounds of this material behind it. Claims
tagged `[hypothesis]` are assumptions awaiting confirmation on executed
instances, and the principle says, in a table written before the data, what
would promote or withdraw each kind of claim; one of them, that the review
apparatus adds to a careful review without it, was withdrawn by experiment
E4 in 0.7.1, and the other two are open.

That execution ran under method version 0.2.2; no production has run under
0.4, 0.5, 0.6 or 0.7, and the cell of `004-adoption-guide` does not run under
the current validator without a migration: it is the record of that
execution, with its errata beside the guide.

The first round of the reflexive application was a production under the
method and received one review, from a separate session; its blocking and
high findings were fixed, and the remaining notes are kept in
`02-reflexive-application/90-review/`, with their state (fixed or open) in
`02-reflexive-application/state/notes-status.jsonl`. The rounds after it
are maintenance rounds of the material, not productions under the method:
each one is recorded in the round record with `kind` maintenance, its scope
and the reviewer's relation to the producer, and none emits a verdict of the
canon. Their decisions are recorded in `CHANGELOG.md`.

In v0.2 the corpus was corrected: seven unsupported claims and two numbers
that the review of round 1 found in `01-principle.md` were removed or aligned
with the recorded facts (see the appended entry in
`02-reflexive-application/99-lessons.md`). The vocabulary was also settled in
v0.2 (production cell, canon, position key, new review verdicts); the history
of the old names is recorded in the canon of the reflexive application.
