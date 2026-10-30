---
name: cooperatio-teamwork
description: Create the teamwork files for a given task, process, project or product — brief, canon, artifact graph, role cards, gates, review rubric, notes and stopping criterion — so that several roles (people, agents or code) can cooperate on it without drifting. Use when the user wants to organize work as a production cell of narrow roles with explicit artifacts, measurable gates and independent review, or says "set up the teamwork for X", "turn this process into roles and gates", "make a cooperatio workspace". NOT for a single document or a one-off checklist, and NOT for executing the work itself.
---

# Cooperatio teamwork files

Turns a task, process or product (the **target**) into a small folder of
files that define how a team cooperates on it: who does what, what they hand
to each other, how quality is measured, and when to stop.

**Working hypothesis — two executed instances.** The method (version 0.5.0)
stands on two executed instances and three designed instances, not executed;
it holds for a target with a declarable brief and stop, a discrete
assemblable artifact, separable sources of truth per content type, and an
acyclic dependency graph. Do not claim it was validated on this target: the
first review round does that. The terms follow the
[canon](../../02-reflexive-application/01-canon.md) of the reflexive
application.

This folder holds the procedure (this file), the scaffold (`scripts/`) and
the templates (`references/`), but not the instrument: the validator, the
sensitivity test and the contracts of the notes, of their state and of the
round record live in the cooperatio
material (`../../02-reflexive-application/`), and the scaffold copies them
into the new cell when the skill folder sits inside that material. Copied
alone, the skill still creates the cell, says what it could not copy, and
the cell has no validator until you copy one in. The full method is in
`../../01-principle.md`. The distributed validator measures documents; a
gate of the target's domain (a speedup, a mass, a cost) is "contract +
agent" or the cell's own code, and the validator has no extension point
for it in this version.

## When to use

- The user names a target and wants it split among roles, with contracts and
  checks between them.
- A recurring process should become something an agent (or a new teammate)
  can run from files alone.
- An existing folder of ad-hoc notes should be restructured into this layout.

Do not use it for a throwaway draft: the method costs a production round plus
an independent review per round, and pays off only when being wrong is
expensive [hypothesis] — an assumption, not a measurement: no production has
yet run against a baseline without the method.

## The one idea

Produce the target by compiling a graph of typed **artifacts**, each with one
owner, a contract and a **gate**; separate **roles** talk only through
artifacts and **notes**; quality is what the system delivered (measured), not
what was asked; every review is **independent** and comparable across rounds
(fixed **rubric**); every error that escapes becomes a new gate; stop at a
**stopping criterion** declared in advance.

## Vocabulary (use it exactly)

- **production cell** — the organization assembled for one target: roles,
  artifacts, gates, canon, validator, review, engine.
- **canon** — the single source of numbers, names, terms to prefer, accepted
  variants and rules, with an owner and a version per section.
- **gate** — a measurable function over an artifact returning pass or fail
  with the measured magnitude; a limit is not a limit without a justification.
- **position key** — the value that fixes where a part lands during
  assembly; ambiguity in it is a contract error.
- **rubric anchor** — the written meaning of a score in one rubric dimension.
- **prior instance** — a registered earlier instance of the method; a claim
  about it carries `[prior:<id>]`, and numbers under that mark are checked
  against its method document.
- **verdicts** — `rejected`, `accepted with conditions`, `accepted`.
- **note** — the only change request between roles: target artifact,
  severity, text, origin, evidence, round.

## The folder the skill creates

```text
production-cell-TARGET/
  00-brief.md          01-sources-of-truth.md   02-canon.json
  03-artifacts.json    04-roles/<role>.md       05-contracts/
  06-gates.md          07-rubric.md             07-rubric.sha256
  08-validator/        09-engine/               state/
  review/              lessons.md               open-notes.json
  priors.json
```

`state/` holds the note ledger (`notes.jsonl`), the state of each note
(`notes-status.jsonl`) and the round record
(`round-record.jsonl`: one JSON line per round, per
`05-contracts/round-record.schema.json` — the method version, the roles of
the round and the executor of each by family and effort (never a model
identifier), a summary, and, when a rubric is frozen, the frozen rubric
hash; no dates).
`priors.json` registers prior instances this cell knows (id, status, method
document path, sha256, locator, and the `number_format` the document is
written in: `point-decimal` or `comma-decimal`). The status decides the
fields: an executed entry carries document, sha256, locator (a relative
path, or `owner-held, not distributable`) and number format, none of them
null; a designed entry keeps the four null or absent. The validator checks
this contract. The
canon of a target (a JSON file) carries numbers,
variants, names and rules — it does not carry the method's own vocabulary
sections.

## Procedure

Work in this order. Each step writes one file; do not start a step before the
previous file exists. Templates are in `references/templates.md`.

1. **Interview, briefly.** Get the target, its audience, the non-negotiables,
   the owner's decisions, the budget of rounds, and what source material
   exists. Ask only what you cannot infer; write assumptions as
   `[hypothesis]`. If the target is missing, stop and ask.
2. **Scaffold.** Run `scripts/scaffold.py` to create the folder and the empty
   files (it refuses to overwrite). Or create them by hand from the templates.
3. **`00-brief.md`** — target, audience, non-negotiables, owner decisions,
   round budget, stopping criterion. No brief, no canon.
4. **`01-sources-of-truth.md`** — per content type, the one source that errs
   least, who consults it, and what is forbidden as a source. The writer is
   never a source of fact; a generative tool is never a source of exact text;
   a number never comes from the prose that cites it.
5. **`02-canon.json`** — canonical numbers (spelling, unit, rounding, nature,
   source), accepted variants, names and terms, rules; one owner and one
   version per section. Anything two roles could write differently goes here.
   Every number the cell states about a prior instance gets a row in
   "recorded facts", one object per number:
   `{"number": "18", "context": "roles with a card [prior:<id>]", "section": "1.1"}`,
   the section of that prior's method document where the number lives;
   the validator fails a prior number without its row. Fill the lists the
   validator reads (terms to avoid, card fields, origin labels and the
   others the scaffold writes empty): a gate whose list is empty measured
   nothing and stays pending.
6. **`03-artifacts.json`** — every intermediate and final artifact: name,
   single owner, dependencies, schema, paths, gates. Its `gates` field is
   the one source of the map from gate to artifact: the validator runs each
   gate on the documents this list assigns it to. Draw the graph; a cycle
   means the graph is wrong. Owner decisions are artifacts too.
7. **`04-roles/<role>.md`** — one role card per role with seven fixed fields,
   each a bold label (`**Decides:**`), the form the gate reads: Decides,
   Does not decide, Inputs, Outputs, Exit gate, Notes it emits,
   Code-conversion degree. A field that still holds a placeholder fails.
   A role with no exit gate and no notes is a step,
   not a role. Name the **executor** of each role (a person, code, or a
   language model) inside the Code-conversion degree field; see "Several
   models" below.
8. **`05-contracts/`** — one schema per artifact that passes between roles;
   each schema rejects unknown fields and its domain's most likely ambiguity
   (an invalid example must fail).
9. **`06-gates.md`** — for each artifact, what is measured, the limit and a
   written justification starting with an origin label
   (`[method]`, `[brief]`, `[hypothesis]`). One row per gate of the
   artifact list, naming the same artifacts: a gate assigned there with no
   row here is a finding. The validator reads the minimum words of
   `p-limit` and the minimum steps of `p-recipe` from their rows. A gate
   of the domain the validator does not implement exits 2: write it as
   "contract + agent" or as the cell's own code. Keep each magnitude short; when
   what a gate reads needs paragraphs (its declared reading, exceptions,
   reach), write them in a separate semantics document the row points to,
   so the gates file stays readable (the reflexive application keeps
   `06-gate-semantics.md`; a layout may name it with the key
   `gate-semantics`).
10. **`07-rubric.md`** — the review rubric: dimensions scored 1–5 with
    anchors for 1, 3 and 5; severity scale; a mechanical verdict rule
    (`rejected` / `accepted with conditions` / `accepted`); report format.
    Freeze it before the first review with the validator —
    `python 08-validator/validator.py --folder . --layout layout.json
    --freeze-rubric 07-rubric.sha256` (the freeze resolves the rubric
    through the layout's `artifacts.rubric` key, which points at this
    file). The command refuses to overwrite an existing pin: replacing a
    frozen rubric is a deliberate act via `--re-freeze-rubric`, with the
    reason recorded in the cell's changelog.
11. **Validator (`08-validator/`).** Specify (or write, preferably as code)
    the check that reads every artifact against the canon and its neighbours
    and emits notes by itself; the scaffold copies the material's
    `validator.py` and `sensitivity.py` here. Give it a sensitivity test:
    inject one known defect per gate and confirm each gate fails on its own.
    The defects are data, `08-validator/perturbations.json` (layout key
    `artifacts.perturbations`); the scaffold writes three generic ones, to
    adapt to the cell's text and extend to one per gate. Run
    `python 08-validator/sensitivity.py --folder . --layout layout.json`;
    it writes the report to `08-validator/sensitivity.md`, where the layout
    key `artifacts.sensitivity` points — the validator's
    `p-sensitivity` gate reads the report through that key, and verifies its
    provenance (the sha256 of the validator that produced it, of the gates
    file and of the canon it was made against, and the perturbation set; a
    report the instrument cannot have produced, or made against other gates
    or another canon, is blocking, never a pass); a cell whose report sits
    elsewhere, or has none yet, shows the gate as pending with the path it
    looked for, never as a crash or a silent pass. The sensitivity script
    takes the validator's inputs (`--case`, `--rubric-hash`, `--notes`): a
    row whose gate needs a missing input is not measured, and `p-sensitivity`
    refuses a report that measured fewer rows than its set. A gate the
    artifact list assigns with no perturbation in the report leaves
    `p-sensitivity` pending, naming the gate ("k of n gates covered"), never
    passing. `layout.json`
    carries only the keys the validator reads; a misspelled key
    (`sensitivty`) exits 2, naming it. A run exits 0 only when every gate
    was measured or its pending was accepted by name
    (`--allow-pending p-anonymity`, for a cell with no forbidden list);
    any other pending exits 4, a note that is high or blocking exits 1, and
    a tool failure exits 2.
    The validator writes no bytecode cache into the cell by itself (a copy
    from v0.4.2 on; an older copy does, until it is replaced); a pytest
    suite, if the cell keeps one, runs as `python -B -m pytest -p
    no:cacheprovider`, since pytest imports the files before their code can
    switch the cache off.
12. **Assembly engine (`09-engine/`).** Specify how artifacts compose into
    the target: contracts that refuse ambiguity, rebuild only what is stale
    (hash), route notes, name outputs by version label.
13. **Quick first version, then independent review.** v1 exists to be
    reviewed, not to be good. The reviewer has no access to the producers'
    reasoning and uses the frozen rubric.
14. **Round loop.** Notes go to the artifact where the defect was born; a
    false positive fixes the instrument at the root (with a test that
    reproduces it, then redo the previous round); a regression that escaped
    every gate gets a gate before it gets a fix.
15. **Stop as declared.** Remaining notes become open notes in
    `open-notes.json`, and the state of each note (open, fixed, disputed, out
    of scope, with the version that closed it) goes to
    `state/notes-status.jsonl`, which the gate `p-notes` reads; record
    lessons in `lessons.md`; register the instance
    in `priors.json`. A cell that cites several priors passes each method
    document with its own `--case`: the validator identifies each by its
    sha256 and checks every `[prior:<id>]` number in the document of `<id>`.

## Rules that must hold in every file you write

- Measure what the system delivered, not what was requested; a gate returns
  the magnitude, never only a sign. A gate that only tests "greater than
  zero" lets a broken instrument pass: give it a magnitude limit.
- Every limit has a justification of at least six words and an origin label.
  Unverifiable assumptions are `[hypothesis]`; never state them as fact.
- Each type of content has one declared source of truth (facts from the
  corpus, numbers from the canon, performance from measurement). The writer
  is never a source of fact.
- A false positive is an instrument defect until proven otherwise. Loosening
  a limit is not a root-cause fix.
- Human decisions are named artifacts; the graph depends on them.
- Converting judgment to code only where the criterion is measurable and the
  answer unique; say the degree per role (converted / partial under gate /
  contract and gate only).
- No absolute paths, machine names, user names or authoring dates in durable
  artifacts if anonymity or reproducibility matters (the checking date is a
  parameter, not content); version labels are state, dates are not.
- One term per concept, defined in the canon; list the synonyms to avoid.
- A claim about a prior instance carries `[prior:<id>]`; a number under the
  mark is checked against that prior's method document, and it is a fact
  about the prior — citable as support for a limit, never the limit itself.
  Inside such a claim, name an instance by its full id
  (`004-adoption-guide`): a bare `004` is read as a number and fails
  without its row.
- A claim that the method works ("pays off", "the method catches", "the
  gates caught", "the review found" and the other efficacy triggers of the
  canon) carries its evidence: `[prior:<id>]`, `[experiment:<id>]` of an
  experiment whose status is `executed` (a designed or pending one is not
  evidence yet), `[lessons]`, or `[hypothesis]`.
- With a single agent (or a single model) playing several roles, separation
  is weak: the rubric and the review must come from outside.

## Several models

Roles may be executed by different language models; the method encourages it.
Decide it per role while writing the role cards, and record it in the
Code-conversion degree field (for example: "(b) partial under gate; executor:
fast mid-tier model") or in the executor table of the artifact list.

- **Match capability to the role.** Mechanical, fully specified roles take a
  fast, cheap model; roles that design, plan or reason about hard trade-offs
  take the strongest one. The gate, not the model's confidence, decides
  whether the output is accepted.
- **Independence needs a different model** [hypothesis]. The independent
  reviewer, and any role that audits another, runs on a different model
  (ideally a different family or provider) from the one that produced the
  artifact, and never sees the producer's reasoning. Two reviewers from
  different families on the same product are cheap insurance when being
  wrong is expensive; disagreements become notes, not silent choices. It
  is the method's rule and a hypothesis: the one datum, experiment E1, has
  the producer's own model in another session catching 2 of 2 injected
  defects, as the other family did, one run per cell [experiment:E1], and
  no recorded production round has met the rule with a frozen rubric.
  Its status (norm, gate or relaxed) is the owner's open decision. In the
  round record, describe a reviewer by its relation to the producer
  ("reviewer, same family as the producer" or "reviewer, another family"),
  never as "independent" when the family is the same.
- **Code is not a model.** Whatever a gate can measure is measured by code,
  identically for every executor; models handle only the judgment the gates
  cannot.
- **Contracts absorb the differences.** Because roles hand off only through
  artifacts that validate against a contract, swapping the model behind a role
  must not change any other file. If it does, the contract is too loose.
- **Make the assignment auditable.** The round record names the executor of
  each role by family (a letter kept stable across the material: "family
  A") and effort, never by model identifier — a product identifier is jargon
  that changes and leaks the provider, and the family is what independence
  is judged on. The map from letter to identifier stays with the owner,
  outside the files. A change of verdict can then be told apart from a
  change of executor. Models drift: the same role card gives different
  output on different days.
- **Do not let a model grade itself.** Another session of the producing
  model is not an independent review: it shares the producer's blind spots,
  and the principle says independence needs a different model. The review
  comes from another executor, ideally of another family. If only one model
  is available, the rubric and the review come from outside the producing
  run (another person, or another model later); declare the gap in the round
  record rather than calling a second session independent. **An alias or a
  route is not a family**: check what each name maps to. The review of the
  second executed instance was recorded as coming from another family and
  came from the producer's own model through another route; no recorded
  production round has yet had a reviewer of another family with a frozen
  rubric (the one exception without it, a reading review of family A in
  v0.4.1, had no frozen rubric, no verdict rule and no execution).
- **What has been measured about this.** Experiment E1 of the reflexive
  application (`../../02-reflexive-application/60-experiments.md`) ran the
  same review on one product, with and without two injected defects (an
  invented prior number; the claim that the same model in another session is
  an independent review), by the producer's own model in another session and
  by a model of another family, one run per condition plus one re-run. Both
  caught 2 of 2 at the predicted severity, and neither valid control run
  rejected the clean product [experiment:E1]. That is what each executor
  caught once, on one product whose defects the rubric anticipates — not a
  rate, not a difference between executors, and not evidence against (or
  for) a second session of the producer's model. One control report stopped
  at an output limit the dispatch had not declared: it is a tool failure by
  the experiment's own rule, not a verdict, so its re-run is the only valid
  control of that executor, and the stability of the verdict across
  repetitions was not measured. Record the effective limit and the reason
  the generation ended, and treat an ending for length, or a report missing
  a section, as a tool failure, never a verdict. Experiment E3 ran the same
  four reviews without the review apparatus (the rubric with its
  dimensions, severity table and verdict rule, the card, the gates file and
  the framing of the dispatch, removed together): both executors still
  named both defects, but classed the invented prior number as high instead
  of blocking and ended the perturbed product at "accepted with conditions"
  instead of `rejected` [experiment:E3]. For two defects checkable against
  a source, one run per cell, the apparatus was not what made the reviewer
  see the defects; removed as a block, it was what turned the finding into
  a verdict. That the severity table and the mechanical rule are the parts
  that did it is a hypothesis [hypothesis]; keep the whole apparatus. No
  experiment yet compares a production with the method against one without
  it.

## Quality check before handing over

Run through `references/review-checklist.md`. At minimum confirm: every
document points to the canon; every gate has magnitude, limit and justified
origin label; the artifact graph is acyclic; every owner is a role or the
owner; every role card has the seven fields; the rubric hash is recorded.

## Output

Report the folder created, the list of files, the assumptions marked
`[hypothesis]`, and the decisions that remain with the owner. Do not claim the
method was validated on this target: the first review round does that.
