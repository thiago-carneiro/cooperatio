# Cooperatio

Method version 0.5.0 (see `VERSION`; the history of the changes, in
`CHANGELOG.md`). The terms follow the
[canon](02-reflexive-application/01-canon.md) of the reflexive application.

A method for organizing a team — people, agents and code — around a complex
target, and a skill that creates the files that set that team up.

The idea in one sentence: produce the target by compiling a graph of typed
artifacts, each with an owner, a contract and a measurable gate; let separate
roles talk only through artifacts and notes; measure what the system delivered
rather than what was requested; make every review independent and comparable
across rounds; turn every error that escapes into a new gate; and stop at a
criterion declared in advance. That the review is independent of the
producer's family is the method's rule and still a hypothesis: no recorded
production round has met it with a frozen rubric (see the principle,
sections 2 and 9).

## Contents

| Path | What it is |
| --- | --- |
| [`01-principle.md`](01-principle.md) | The method: the idea, the formula, the components, the golden rules, what changes by domain, how to instantiate it, warning signs, limits and ontological assumptions |
| [`02-reflexive-application/`](02-reflexive-application/) | The method applied to itself: a generic recipe, three designed instances (a physical product, a long text, a software library), the role cards, the gates and rubric, a validator and a sensitivity test written as code, the experiments about the method, an independent review and the lessons of every round |
| [`skills/cooperatio-teamwork/`](skills/cooperatio-teamwork/) | An agent skill that creates the teamwork files (brief, canon, artifact graph, role cards, gates, rubric, notes) for a given task, process or product; its scaffold copies the validator and the sensitivity test of this material into the new cell |
| [`instances/`](instances/) | The registry of the known instances (`registry.json`) and the cell of the second executed instance (`004-adoption-guide/`, executed under method version 0.2.2, kept as history). The cell's list of forbidden identifiers (`state/forbidden.txt`) stayed with the owner, outside the material, since it contains what it forbids: the cell's commands that pass `--forbidden state/forbidden.txt` exit 2 in a copy, and the cell is kept as it is, its files still naming the list |
| `VERSION`, `CHANGELOG.md`, `LICENSE` | The version of the method, its history, the license |

## Where to start

- To understand the method, read [`01-principle.md`](01-principle.md).
- To apply it to a new target, read
  [`02-reflexive-application/10-generic-recipe.md`](02-reflexive-application/10-generic-recipe.md),
  then the instance closest to your target.
- To have an agent create the files for you, install the skill in
  [`skills/cooperatio-teamwork/`](skills/cooperatio-teamwork/) (see its
  `SKILL.md`) and ask it to set up teamwork for your task or process.

## Using the skill

Copy or link the `skills/cooperatio-teamwork/` folder into your agent's
skills directory, and ask for the teamwork files for a
target. The skill also ships a small scaffolding script that creates the empty
folder structure without overwriting anything. The scaffold copies the
validator, the sensitivity test and three contracts from this material into
the new cell, so run it from inside the material (or keep the skill folder
inside it); copied alone, the skill creates the cell without them, and the
cell has no validator until you copy one in:

```text
python skills/cooperatio-teamwork/scripts/scaffold.py \
    --target "My target" --roles writer verifier reviewer --out ./teamwork
```

## Running the validator

The validator in `02-reflexive-application/80-validator/` reads the
canon, the artifact list and the gates and measures every gate on every
document the artifact list assigns it to. Its self-test needs no inputs:

```text
python 02-reflexive-application/80-validator/validator.py --self-test
```

The validator measures documents: terms, sections, links, form, numbers
stated about registered priors, the contracts of its ledgers. A gate of a
target's domain (a speedup, a mass, a cost) is not one it implements: it
is "contract + agent", or code the cell writes and runs itself, and this
version has no extension point for it (the scope of the validator is an
open decision of the owner). A run exits 0 only when every gate was
measured or its pending was accepted by name with `--allow-pending`; a gate
left unmeasured exits 4. The runbook is in
[`02-reflexive-application/README.md`](02-reflexive-application/README.md).

The method document of the prior instance `000` is owner-held, so a clone
of this material does not have it. A clone reaches exit 0 with the run the
runbook gives for that case (no `--case`, the three gates that need it
accepted by name; passing only the document of `004` is blocking), and it
cannot regenerate the sensitivity report: a clone that edits the
validator, the canon or the "Gates" section of the gates file cannot get
back to green without the owner.

## License

The material in this folder is licensed under the Apache License 2.0; the
full text is in [`LICENSE`](LICENSE).

## Status

**Working hypothesis — two executed instances.** The method stands on two
executed instances (`000-av-production` and `004-adoption-guide`, both
registered in [`instances/registry.json`](instances/registry.json) and pinned
by sha256) and on three designed instances, not executed. The scope of that
evidence is narrow, and it is declared rather than implied: both executions
are documentary productions by the same owner of this material — `000` is
an audiovisual production method (owner-held, not distributable) and `004`
is the adoption guide of this method itself; the inter-domain instances
(car, text, HPC) remain designed, not executed, so cross-domain portability
is an assumption, not a result. Claims tagged `[hypothesis]` are assumptions
awaiting confirmation on executed instances.

Of the two executions, the second ran under method version 0.2.2; no
production has run under 0.4 or 0.5, and the cell of `004`, distributed in
`instances/004-adoption-guide/`, does not run under the current validator
without a migration.

The first round of the reflexive application was produced by the method and
received one independent review; its blocking and high findings were
fixed, and the remaining notes are kept in
`02-reflexive-application/90-review/`, with their state (fixed or open) in
`02-reflexive-application/state/notes-status.jsonl`. The rounds after it
are maintenance rounds outside the brief of that production, run by an
orchestrator with decisions the owner delegated and recorded in
`CHANGELOG.md`.

In v0.2 the corpus was corrected: seven unsupported claims and two numbers
that the review of round 1 found in `01-principle.md` were removed or aligned
with the recorded facts of the prior instance [prior:000-av-production] (see the appended entry in
`02-reflexive-application/99-lessons.md`). The vocabulary was also settled in
v0.2 (production cell, canon, position key, new review verdicts); the history
of the old names is recorded in the canon of the reflexive application.
