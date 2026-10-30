# Declared semantics of the gates

The gate table of [`04-gates-and-rubric.md`](04-gates-and-rubric.md) keeps,
for each gate, a short magnitude, the limit and the justification. What a
gate reads in detail is declared here: its declared reading, its
exceptions, its reach, the provenance it requires, and the sub-cases it
reports. A row of the table whose semantics live here says so ("semantics:
`06-gate-semantics.md`"). The page also holds how a gate is retired and
where the rubric came from. The terms follow the [canon](01-canon.md).

This page changes when the validator changes what a gate reads; the
validator reads no table from it.

## The gate map, the limits and the exit codes

Since v0.5.0 the artifact table of [`02-artifacts.md`](02-artifacts.md) is
the one source of the map from gate to artifact: its Gates column decides
which gate runs on which document, and the Artifact column of the gate
table mirrors it. `p-references`, on the gates file, reports a gate the
artifact table assigns with no row in the gate table, and a row that names
other artifacts than the ones assigned. Until v0.4.2 the map was read from
the gate table alone, and the panel that reviewed v0.4.2 deleted twenty of
its rows and kept a green report: the gates simply stopped running. A gate
id that the validator does not implement, in either table, is a tool
failure (exit 2) that says what the distributed validator measures:
documents. A gate of the target's domain is "contract + agent" or the
cell's own code; this version has no extension point.

The numeric limits of `p-limit` (the minimum words of a justification, "fewer
than N words" in its magnitude) and of `p-recipe` (the minimum steps, "≥ N
steps" in its limit) are read from their rows; a row that does not state
the number leaves the gate pending. The other limits follow from the canon's
lists ("14 of 14") or are zero.

A gate whose object is a list of the canon (terms to avoid, instantiation
rows, mandatory sections, card fields, origin labels, components, prior
and efficacy triggers) is pending when that list is empty, never a pass of
0 of 0. A placeholder (an angle-bracket word such as `<fill in>`, or `TBD`,
`TODO`) outside code spans is an unfilled field: it fails `p-card` in a
card, `p-limit` in a gate row, `p-table` in an instantiation cell and
`p-references` in an artifact record. Its reach is those four places and
no other: a placeholder in prose (a `TBD` in a paragraph of the brief, an
angle-bracket word in running text, which `p-form` reports only as far as
it reads like an HTML tag) passes every gate. The detector reads fields,
not prose; an unfilled paragraph is the review's to find. A run exits 0 only when every gate was
measured, or its pending was accepted by name with `--allow-pending`, which
the report prints; a pending the caller did not accept exits 4, distinct
from 1 (a high or blocking note) and 2 (a tool failure). This corpus runs
with `--allow-pending p-anonymity` (see below).

## `p-terms`: the frozen ledger

The terms are counted outside code and link targets; in the canon, outside
the "Terms to avoid" table itself. The frozen ledger under `90-review/` is
exempt by design: vocabulary rules govern living documents, and a frozen
historical record is never edited to satisfy a later vocabulary.

## `p-anonymity`: the identifier half

The identifier half of the gate is supplied per cell, as the cell's own
`--forbidden` list, kept apart from the documents it checks and out of the
distributed material, since the list contains what it forbids. This corpus
runs the gate with no list: the identifier half is pending by design, not
forgotten, the published report is made without `--forbidden`, and the run
accepts that pending by name (`--allow-pending p-anonymity`). The cell of
the second executed instance, distributed under `../instances/` since
v0.5.0, kept its list in its state folder; that file stayed with the owner,
outside the material. An empty list measures nothing either: it leaves the
half pending, as no list does. Model identifiers belong to that list (form
rule 4 of the canon: an executor is named by family and effort).

The path-and-date half reads, since v0.5.0, the forms the panel that
reviewed v0.4.2 let through: a date written with the month's name (day
first or month first) or with dots, an absolute path of one
segment under a common root, a file URL and a home folder by user name. A
month and a year with no day, a version number and a relative path are not
hits.

Declared reach, since v0.4.2: the gate also measures the round record and
the principle (`round-record`, `corpus`), the two documents it left out in
v0.4.1, with a perturbation on the round record (a machine-local path in an
executor string). Its path-and-date half runs on them; its identifier half
is the cell's forbidden list, pending in this corpus by design. Since
v0.5.0 it measures also the root README, the skill and the state ledger of
the notes (`readme-root`, `skill`, `notes-status`). A search by
the names of providers or routes is no gate: the identifier rule is checked
by the list a cell supplies, and in this corpus by a sweep each round runs
by hand, recorded outside the material.

The registry carries no identifier: the locator field is a re-walkable path,
or the reserved string, which declares the absence of a locator; the
owner's map from letter to identifier is not a locator and stays outside the
material.

## `p-prior`: what the number check reads

A number inside a unit marked `[prior:<id>]` is verified in the method
document of `<id>`: the `--case` document whose sha256 is the pin of `<id>`.
A unit that cites several priors is checked in the document of each; a
cited prior with no such document is pending by name, never checked
against another prior's document.

- **A row is required.** A number needs a row of that prior in the canon's
  "Recorded facts" table and is checked in the union of the sections that
  row cites. A number without a row **fails**: since the review of v0.4.0,
  because presence anywhere in the document let an invented number pass —
  it occurred once there, in an unrelated sentence.
- **Section references.** A reference such as "section 2.1" or "step 16" is
  checked by the existence of that label in the document. A following label
  continues the reference only before punctuation, the end, a connector or
  "of": in "section 1.4 and 7 rounds" the 7 is a number.
- **Declared reading.** Every number of a marked unit is a fact about that
  prior; a number that is not (the instance's own limit, a year) goes in
  another unit.
- **Three exceptions.** The full id of a registered instance
  ("004-adoption-guide") names that instance and is not read; since v0.4.1
  only the full id does, so a bare "004" is a number again, and "the prior
  has 003 phases" is checked like any count (in a marked unit, cite an
  instance by its full id). Read as 3, that count still passes by presence
  where 3 has a row and occurs in the cited sections: the rule closes the
  exclusion, not the coincidence. A section reference is checked as a label, as
  above. A digit attached to a letter ("p95") is a name, so a "v7" is no
  longer checked at all.
- **A cell's JSON canon** records its rows as objects: the number, the
  context carrying the mark, and the section.
- **Presence, not the claim.** The check verifies the presence of the
  number's tokens in the cited sections, not the equality of the claim
  around it: the sentence "49 artifacts" passes if 49 appears there,
  whatever it counts. The "Recorded facts" table itself is exempt (its cells
  are code spans, removed before the check).
- **Number format.** Each token of a prior's document has one reading, in
  the `number_format` its registry entry declares, or its literal spelling
  only when it does not parse in that format. A token of these documents is
  read point-decimal, plus its literal. Values only meet values and literals
  only meet literals: "1.2" here never matches a comma-decimal "1.200" (one
  thousand two hundred), "1.200" here never matches the literal "1.2" of a
  section number, and "1.10" still matches a section number.

## `p-prior-mark` and `p-prior-pin`: reach

The triggers of `p-prior-mark` cover statements about the **content** of
registered priors. The trigger and the mark are read outside code spans and
fenced blocks, the reading `p-prior` gives the mark (since v0.5.0): a
trigger in a code span is notation, as the canon says, and a mark in a code
span is no mark, so the unit fails with a note that says so. Before, a mark
between backticks satisfied this gate while `p-prior`, which strips code,
checked none of the unit's numbers: an invented number passed both. Statements about the registry itself are data, verified
by `p-contract-shape`, not by this mark. The frozen "Rubric" section of
`04-gates-and-rubric.md` keeps its original words: history, exempt by
design, like the review ledger.

For `p-prior-pin`, `--case` is **repeatable**: one document per executed
prior, each identified by its sha256 against the registry. A cited executed
prior whose registered sha256 matches none of the documents passed is
blocking, and so is a document passed that is the pin of no executed
instance (a note on the registry, not a tool failure), and so is a cited
executed instance without a pinned sha256. The registry it checks against
is data under `p-contract-shape`.

## `p-contract-shape`: the registry entry by status

The registry is one list, and the status of an entry decides its fields.
An `executed` entry carries `document`, `sha256`, `locator` and
`number_format`, none of them null: the locator is a path relative to the
root of this material or the reserved string `owner-held, not
distributable`, and the number format has no default. A `designed` entry
keeps the four null or absent, so it can never pass for a pinned prior. The
mini-validator of the contracts applies no conditional keyword, so the
schema describes this contract and the validator enforces it; a violation
is a note of this gate on the registry, never a tool failure. One list, not
one file per status: two files would need a cross-check of their own. A
misspelled reserved string passes as a relative path: the validator cannot
tell the two apart.

## `p-sensitivity`: coverage and provenance

There is at least one perturbation per gate the validator implements: 20 of
its 21 gates, in 35 perturbations (four on `p-references`; three each on
`p-anonymity`, `p-limit` and `p-efficacy-mark`; two each on `p-terms`,
`p-prior`, `p-card`, `p-prior-mark`, `p-contract-shape` and `p-notes`). The
21st is this gate, which cannot carry a perturbation without circularity:
the baseline of the run reads the report being regenerated. Its own defects
(a fabricated report, another validator, another set, a table that does
not add up, another gate table or canon) are regression tests, and the
measurement `m-determinism` (the equality of the report across two runs, a
measurement of the instrument listed under "Measurements" in
`04-gates-and-rubric.md`) has none by definition. One perturbation empties
a list of the canon and expects the gate pending, not failing; the others
expect a fail.

Coverage is measured per gate since the closing pass of v0.5.0: the gates
the artifact table assigns, except this one and the measurements (`m-*`),
are compared with the expected gates of the report's rows, and the
magnitude reads "k of n gates covered, 0 missed of m". An assigned gate
with no perturbation leaves this gate pending, with the gates named
("gates without a perturbation: ..."), never a pass; before, a cell with
one perturbation and four assigned gates read "0 missed of 1" and passed.
This corpus covers 20 of 20. The three generic perturbations of a new cell
cover the three gates of the smallest filled cell; each gate a cell adds
needs one of its own.

A row whose gate needs an input not passed (`--case`, `--rubric-hash`,
`--notes`, or a registry for a perturbation that edits it) is not measured,
and a report that measured fewer rows than the set fails here. The report
carries its provenance: the sha256 of the validator that produced it (the
`validator.py` next to the report), the sha256 of the gate section of the
gates file (its "Gates" section; a cell's whole gates file) and of the
canon, and the ids and count of the perturbation set. The validator
recomputes them and compares, and it counts the rows of the table against
the "Caught" line. Since v0.5.0 an edit of the gate table or of the canon
makes the report stale, like an edit of the validator: regenerate it before
the next run. This corpus keeps its set in `sensitivity.py`; a cell keeps
its own as data (the layout key `perturbations`, a JSON list of the fields
of a perturbation), and `sensitivity.py --layout` reads a cell like the
validator does. The set is written by whoever wrote the gates: it measures
the defects its author imagined, and the panel's probes were defects that
authorship had not.

## `p-frozen-rubric`: the freeze refuses

The rubric is resolved through the layout: the dedicated rubric file (the
cell's `artifacts.rubric`) when the layout names one, else the "Rubric"
section of `04-gates-and-rubric.md`. The freeze that records its sha256
**refuses an existing pin**; a replacement is deliberate, via
`--re-freeze-rubric`, with the reason recorded in the CHANGELOG.

## `p-efficacy-mark`: a lexical gate

The gate reads the closed list of trigger phrases of the canon, and the
labels, outside code spans (since v0.5.0, the reading of the other mark
gates: a label between backticks is notation). It is lexical: a claim that
the method works written in other words escapes it ("narrow roles make
fewer mistakes" passes where "err less" fails), and no list closes that
gap. The mitigation is the independent review, not the gate. The founding
phrases of the principle the panel that reviewed v0.4.2 found unlabeled are
triggers since v0.5.0, and their units carry a label.

An append-only document is measured from the heading the canon's table
"Efficacy mark in append-only documents" names on: in `99-lessons.md`, from
the entry of v0.5.0. The units above are history, exempt the way the
frozen ledger is exempt from the vocabulary; a declared heading that is not
in the document is a finding, never an exemption of the whole.

The history above that heading has no pin: no gate compares it with the
text an earlier round left, so an edit there, or a new sentence placed
there without a label, passes every gate. Its append-only rule is checked by
hand at each round (the old file has to be a prefix of the new one).
Recording a sha256 of that part in the canon's table was weighed in the
closing pass of v0.5.0 and left out: it would put an integrity check inside
a gate about labels, and once the material is under version control its
history shows any edit of that part.

## `p-efficacy-mark`: what an experiment label cites

An `[experiment:<id>]` label backs a claim only when `<id>` is an executed
experiment of `60-experiments.md`: a level-2 heading `## E<n> — ...` whose
block declares the status `executed` (a "Status" row of its field table, or
a "Status:" line). A label that cites a designed or pending experiment is a
note ("cites a designed experiment as evidence"): a design is not evidence
yet. An id the record does not open with such a heading is not registered;
a subheading such as "Question" or "Cost" never names an experiment (since
v0.4.1, after the review of v0.4.0 found that any heading word registered
an id).

## `p-notes` and `p-contract-shape`: state and versions

The note ledger of round 1 is frozen and never edited, so the state of its
notes lives in a ledger of its own, `state/notes-status.jsonl` (layout key
`notes-status`, contract `05-contracts/notes-status.schema.json`): one line
per note of the ledger passed with `--notes` (`notes:<n>`, 1-based) or per
finding of a critical panel that became a correction (`panel:<version>:<id>`),
with its status (`open`, `fixed`, `disputed`, `out of scope`) and the version
that closed it. `p-notes` fails a note with no line or two, and a closing
status with no version; without `--notes`, both rows are pending. A note
may also carry `status` and `closed_in` itself. The round of a note is a
string, as in the round record; the integer of the frozen ledger is its
legacy form. Every contract declares `contract_version` at its top level,
and `p-contract-shape` reports one without it, or of a version other than
the one the validator reads.

## `p-declared`: the sub-cases

Two rules of the instrument itself, added in v0.3.0 after the critical
panel. First, `p-declared`: an artifact declared in the artifact table whose
files match nothing on disk is a blocking note naming the declared paths; a
declared artifact marked `proposed` is pending with its reason, and one
declared with no paths at all is pending ("declared without paths"), never
silent. Second, outside any gate row: a run that measures zero documents is
a blocking note on `artifacts`. A production with no documents is not green,
so a newly scaffolded cell fails high until it has real artifacts.

## Gate lifecycle

A gate is born from a regression that escaped every gate (golden rule 4 of
the principle), together with its perturbation in the sensitivity test. It
lives while its object exists. It is retired deliberately, never by
neglect: when its object is gone, or when its rule moved into a contract
that refuses the defect earlier. The row of the gate table and the
perturbation leave together, and the CHANGELOG records "retired gate:
`<id>`", the reason and the rounds the gate stayed silent. The instrument
detects half a retirement: removing a gate and keeping its perturbation
makes the perturbation missed, and removing the perturbation of a gate that
still runs fails the test that every gate has one. Removing both and
regenerating the sensitivity report passes everything; only the declaration
in the CHANGELOG records that retirement. Since v0.5.0 a gate the artifact
table still assigns with no row in the gate table is a finding of
`p-references`, so a retirement also removes the gate from the artifact
table. No gate was retired in v0.4.0, v0.4.1, v0.4.2 or v0.5.0.

## Provenance of the rubric

The rubric of `04-gates-and-rubric.md` was written by the producing agent
in the first round, against step 8 of the generic recipe
(`10-generic-recipe.md`), which gives it to the
owner and the reviewer (recorded in `99-lessons.md`, lesson 4 of "What
reflexivity showed about the method"). It stays frozen and in force because
the one review round already applied it: rewriting it now would make that
verdict incomparable. If another review round opens, a new rubric is
written by the reviewing side, frozen through `--re-freeze-rubric` with the
reason in the CHANGELOG, and the round record names its author
(`rubric_author`).
