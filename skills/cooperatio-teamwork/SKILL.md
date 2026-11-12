---
name: cooperatio-teamwork
description: Create the teamwork files for a target — brief, canon, artifact graph, role cards, gates, review rubric, notes and stopping criterion — so that several roles (people, agents or code) can cooperate on it without drifting. The distributed validator measures documents; a target whose non-negotiables are domain measurements (identity of results, speed, mass) needs the cell's own code to write them as results the validator reads, or its exit 0 says nothing about them. Use when the user wants to organize work as a production cell of narrow roles with explicit artifacts, measurable gates and a review by someone who did not produce, or says "set up the teamwork for X", "turn this process into roles and gates", "make a cooperatio workspace". NOT for a single document or a one-off checklist, and NOT for executing the work itself.
---

# Cooperatio teamwork files

Turns a target (a product, a document, a library) into a small folder of
files that define how a team cooperates on it: who does what, what they hand
to each other, how quality is measured, and when to stop.

**Status: a working hypothesis, with a documentary validator; the gates of
a target's domain enter as results the cell's own code produces and the
validator checks; one executed instance, documentary, by the owner,
auditable.** The method (version 0.7.2) stands on that one execution and
three designed sketches, not executed;
it holds for a target with a declarable brief and stop, a discrete
assemblable artifact, separable sources of truth per content type, and an
acyclic dependency graph. Do not claim it was validated on this target: the
first review round does that. The terms follow the
[canon](../../02-reflexive-application/01-canon.md) of the reflexive
application.

This folder holds the procedure (this file), the scaffold and the installer
(`scripts/`; `scripts/install.py` links this folder into every agent harness
it finds, see the README of the material) and
the templates (`references/`), but not the instrument: the validator, the
sensitivity test and the contracts of the notes, of their state and of the
round record live in the cooperatio
material (`../../02-reflexive-application/`), and the scaffold copies them
into the new cell when the skill folder sits inside that material. Copied
alone, the skill still creates the cell, says what it could not copy, and
the cell has no validator until you copy one in. The full method is in
`../../01-principle.md`. The distributed validator measures documents; a
gate of the target's domain (the identity of results, a speedup, a mass) is
named `d-<name>`, measured by the cell's own code, and read by the validator
from the result file the layout lists under `domain-results` (contract
`05-contracts/domain-result.schema.json`); what no code can measure stays
"contract + agent". Requirements: Python 3.9 or later; `pytest` for a test
suite.

## When to use

- The user names a target and wants it split among roles, with contracts and
  checks between them.
- A recurring process should become something an agent (or a new teammate)
  can run from files alone.
- An existing folder of ad-hoc notes should be restructured into this layout.

Do not use it for a throwaway draft: the method costs a production round plus
a review per round, and pays off only when being wrong is
expensive [hypothesis] — an assumption, not a measurement: no production has
yet run against a baseline without the method.

## The one idea

Produce the target by compiling a graph of typed **artifacts**, each with one
owner, a contract and a **gate**; separate **roles** talk only through
artifacts and **notes**; quality is what the system delivered (measured), not
what was asked; each review is made by someone who did not produce, with a
**rubric** frozen before it, so rounds are comparable; every error that
escapes becomes a new gate; stop at a **stopping criterion** declared in
advance.

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

The cell has one note ledger, `open-notes.json` (a JSON list, passed to the
validator with `--notes`); `state/` holds the state of each of its notes
(`notes-status.jsonl`) and the round record (`round-record.jsonl`: one JSON
line per round, per `05-contracts/round-record.schema.json` — the method
version, its `kind` (`production` or `maintenance`), the roles of the round
and the executor of each by family and effort (never a model identifier),
the reviewer's relation to the producer, a summary, and, when a rubric is
frozen, the frozen rubric hash; no dates). Both state files are
append-only: a line may carry `prev`, the sha256 of the file as it stood
before the line was appended, and once a line carries it every later one
does; the validator recomputes the chain.
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
   round budget, stopping criterion. No brief, no canon. Give each
   non-negotiable an id in a code span (`nn-<name>`): a note names the ones
   it affects (`affects`), and an open high or blocking note that affects one
   is blocking at the stop unless the owner decided it. Record each decision
   only the owner can take as a line of `state/owner-decisions.jsonl` (name,
   status `open` or `decided`, what it blocks, the version, and, once
   decided, the notes it `covers`).
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
   nothing and stays pending. Each list is a JSON list of plain strings,
   and the origin labels keep their brackets, for example
   `"terms to avoid": ["pipeline", "checkpoint"]`,
   `"role card fields": ["Decides", "Does not decide", "Inputs", "Outputs",
   "Exit gate", "Notes it emits", "Code-conversion degree"]`,
   `"origin labels": ["[method]", "[brief]", "[hypothesis]"]`. List under
   `"documents outside the artifact list"` (paths or globs) the Markdown
   documents of the cell that belong to no artifact, such as
   `"01-sources-of-truth.md"` or `"08-validator/*.md"`: every other one has
   to belong to an artifact, or the validator reports it.
6. **`03-artifacts.json`** — every intermediate and final artifact: name,
   single owner, dependencies, schema, paths, gates. Its `gates` field is
   the one source of the map from gate to artifact: the validator runs each
   gate on the documents this list assigns it to. Draw the graph; a cycle
   means the graph is wrong. Owner decisions are artifacts too. A record's
   `command` is resolved against the paths it names (each has to exist; the
   validator never runs it), and a path or command may carry `{version}`,
   which takes the layout's `version-label` (for example `v2`), so moving to
   a new version changes one key.
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
   row here is a finding, and a gate with two rows is a tool failure. The
   validator reads the minimum words of `p-limit` and the minimum steps of
   `p-recipe` from their rows, and compares the numbers of each Limit cell
   with the limit it applies. A gate of the domain is a row `d-<name>`:
   the cell's code measures it and writes a result file (gate, magnitude,
   limit, result, and the sha256 of each input, in the contract the scaffold
   copies), the layout lists the file under `domain-results`, and the
   validator reads it; a declared `d-*` row without a result is pending. Any
   other id the validator does not implement exits 2. Keep each magnitude short; when
   what a gate reads needs paragraphs (its declared reading, exceptions,
   reach), write them in a separate semantics document the row points to,
   so the gates file stays readable (the reflexive application keeps
   `06-gate-semantics.md`; a layout may name it with the key
   `gate-semantics`).
10. **`07-rubric.md`** — the review rubric: dimensions scored 1–5 with
    anchors for 1, 3 and 5; severity scale; a mechanical verdict rule
    (`rejected` / `accepted with conditions` / `accepted`); report format.
    Freeze it before the first review with the validator —
    `python3 08-validator/validator.py --folder . --layout layout.json
    --freeze-rubric 07-rubric.sha256` (the freeze resolves the rubric
    through the layout's `artifacts.rubric` key, which points at this
    file). The command refuses to overwrite an existing pin: replacing a
    frozen rubric is a deliberate act via `--re-freeze-rubric`, with the
    reason recorded in the cell's changelog.
11. **Validator (`08-validator/`).** Specify (or write, preferably as code)
    the check that reads every artifact against the canon and its neighbours
    and emits notes by itself; the scaffold copies the material's
    `validator.py`, `sensitivity.py` and `perturbation_set.py` here. Give it a sensitivity test:
    inject one known defect per gate and confirm each gate fails on its own.
    The defects are data, `08-validator/perturbations.json` (layout key
    `artifacts.perturbations`); the scaffold writes three generic ones, to
    adapt to the cell's text and extend to one per gate. Run
    `python3 08-validator/sensitivity.py --folder . --layout layout.json`;
    it writes the report to `08-validator/sensitivity.md`, where the layout
    key `artifacts.sensitivity` points — the validator's
    `p-sensitivity` gate reads the report through that key, and verifies its
    provenance (the sha256 of the validator that produced it, of the gates
    file, of the canon and of the resolved gate map it was made against, and
    the perturbation set; a report the instrument cannot have produced, or
    made against other gates, another canon or another map, is blocking,
    never a pass); a cell with no report yet gets a blocking note with the
    path it looked for, never a crash or a pending. A perturbation that
    changes the result of another row is noisy and fails the report, unless
    it declares that row's gate in `also`. The sensitivity script
    takes the validator's inputs (`--case`, `--rubric-hash`, `--notes`): a
    row whose gate needs a missing input is not measured, and `p-sensitivity`
    refuses a report that measured fewer rows than its set. A gate the
    artifact list assigns with no perturbation in the report, or fewer than
    a quarter of the (document, gate) pairs perturbed, leaves
    `p-sensitivity` pending, with the reason, never passing. `layout.json`
    carries only the keys the validator reads; a misspelled key
    (`sensitivty`) exits 2, naming it. A run exits 0 only when every gate
    was measured or its pending was accepted by name
    (`--allow-pending p-anonymity`, for a cell with no forbidden list; the
    list is closed: `p-anonymity`, `p-prior`, `p-prior-pin`); any other
    pending exits 4, so freeze the rubric and pass `--notes open-notes.json`
    and `--rubric-hash 07-rubric.sha256` before you expect a green run; a
    note that is high or blocking exits 1, and a tool failure exits 2. With
    `--output`, one summary line goes to the error stream.
    The validator writes no bytecode cache into the cell by itself (a copy
    from v0.4.2 on; an older copy does, until it is replaced); a pytest
    suite, if the cell keeps one, runs as `python3 -B -m pytest -p
    no:cacheprovider`, since pytest imports the files before their code can
    switch the cache off.
12. **Assembly engine (`09-engine/`).** Specify how artifacts compose into
    the target: contracts that refuse ambiguity, rebuild only what is stale
    (hash), route notes, name outputs by version label.
13. **Quick first version, then the review.** v1 exists to be
    reviewed, not to be good. The reviewer has no access to the producers'
    reasoning and uses the frozen rubric; record the reviewer's relation to
    the producer in the round record.
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

### The commands of a cell

From inside the cell, after the files are filled:

```text
python3 08-validator/validator.py --folder . --layout layout.json --self-test
python3 08-validator/validator.py --folder . --layout layout.json \
    --freeze-rubric 07-rubric.sha256
python3 08-validator/sensitivity.py --folder . --layout layout.json \
    --rubric-hash 07-rubric.sha256 --notes open-notes.json --work SCRATCH_FOLDER
python3 08-validator/validator.py --folder . --layout layout.json \
    --rubric-hash 07-rubric.sha256 --notes open-notes.json \
    --allow-pending p-anonymity --determinism --output 08-validator/report.md
python3 -B -m pytest -p no:cacheprovider tests/
```

The last line only if the cell keeps a test suite. Add `--case` for each
registered prior the cell cites, and `--forbidden` with the cell's list of
forbidden identifiers kept outside the cell (then drop `--allow-pending`).

A failing test is a rejection of its gate (a `d-*` gate of the tests, or
the cell's own), with a note to the implementation where the defect was
born; whether the test itself is wrong is the verifier's decision, recorded
as a note to the tests. A regression that escaped every gate is recorded in
the state ledger as `escaped`, and closes with the `gate` it became or a
`no_gate` reason.

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
  parameter, not content); version labels are state, dates are not. A hash
  of a host or user name is not a pseudonym (a dictionary reverses it); keep
  a map held by the owner, or a salted hash, and pass the forbidden list as
  names or as `sha256:<hex>` entries.
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
  experiment whose status is `executed` and whose record gives the sha256 of
  its inputs and outputs (a designed or pending one is not evidence yet),
  `[lessons:<title>]` naming an entry of the lessons file by its heading, or
  `[hypothesis]` (which, on a claim with a number or "every", "always",
  "none", gets a low note).
- With a single agent (or a single model) playing several roles, separation
  is weak: the rubric and the review must come from outside.

## Several models

Roles may be executed by different language models. What the method says
about it, and what has been measured, is in one place: the principle,
section 2, "Using several models across the roles"
(`../../01-principle.md`), with the experiments it cites in
`../../02-reflexive-application/60-experiments.md`. In short, for the files
you write: decide the executor per role in the Code-conversion degree field;
match capability to the role; let the gate, never the model's confidence,
accept an output; record each executor in the round record by family (a
stable letter) and effort, never by model identifier, and the reviewer's
relation to the producer (`reviewer_relation`); a reviewer of another family
is recommended, a hypothesis with the cost of a second provider, and a second
session of the producing model is recorded as such, never as independent.
A pilot showed a rubric frozen before the review, with a mechanical verdict
rule, turning a finding into a verdict [experiment:E3]; the measurement that
followed withdrew the claim that the review apparatus (the validator and the
review with the frozen rubric) adds to a careful review without it: on seeded
defects it let no fewer escape than a careful review with a checklist, for
more input tokens, and its verdict did not tell a clean copy from a seeded one
[against:E4]. Freeze the rubric so that rounds compare, and do not promise
the people you set up that it finds more. An alias or a route is not a family:
check what each name maps to.

## Quality check before handing over

Run through `references/review-checklist.md`. At minimum confirm: every
document points to the canon; every gate has magnitude, limit and justified
origin label; the artifact graph is acyclic; every owner is a role or the
owner; every role card has the seven fields; the rubric hash is recorded.

## Output

Report the folder created, the list of files, the assumptions marked
`[hypothesis]`, and the decisions that remain with the owner. Do not claim the
method was validated on this target: the first review round does that.
