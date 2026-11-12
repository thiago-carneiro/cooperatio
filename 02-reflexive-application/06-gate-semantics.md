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
its rows and kept a green report: the gates simply stopped running. Since
v0.6.0 the map itself is pinned and complete: the sensitivity report records
the sha256 of the resolved map (the sorted pairs of gate and document path,
not the text of the table, so a reformatted table keeps it and a repointed
file changes it), and `p-declared` reports a Markdown document of the folder
that no artifact declares and the canon does not list as outside the table,
a file that belongs to two artifacts, and a document of the "Size ranges"
table that no artifact declares. The panel that reviewed v0.5.0 had
repointed a file of an artifact and kept every gate green. A gate id that
the validator does not implement, in either table, is a tool failure
(exit 2), except a gate of the target's domain (see "Domain gates" below).
A gate with two rows in the gate table is a tool failure too: the second
row used to measure the gate twice, with whichever limit, in silence.

The numeric limits of `p-limit` (the minimum words of a justification, "fewer
than N words" in its magnitude) and of `p-recipe` (the minimum steps, "≥ N
steps" in its limit) are read from their rows; a row that does not state
the number leaves the gate pending. The other limits follow from the canon's
lists ("14 of 14") or are zero. Since v0.6.0 the Limit column is checked:
when a Limit cell states numbers, they have to be the numbers of the limit
the validator applied to that gate's measured rows, and a divergence is a
note of `p-references` on the gates file. A cell with no number names where
the limit lives ("equal", "within the range in the 'Size ranges' table") and
is not compared; the check reads numbers, not words, so a limit rewritten
in words with the same numbers passes.

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
from 1 (a high or blocking note) and 2 (a tool failure). Since v0.6.0 the
list of gates a caller may accept is closed: `p-anonymity`, `p-prior` and
`p-prior-pin`, the halves that need an input a cell may not
distribute (the forbidden list, the document of a prior held outside its
material), and, since
the rework of v0.6.0, `p-sensitivity-synthetic`, the row of a sensitivity
report made with a synthetic prior, which a caller accepts only by naming
it. Any other gate named there is a tool failure, `p-sensitivity` included, and a missing
sensitivity report is blocking: the panel that reviewed v0.5.0 deleted the
report, accepted the gate by name and got exit 0, so deleting the evidence
was cheaper than keeping it current. A gate accepted with nothing pending is
printed as such. This corpus runs with `--allow-pending p-anonymity` (see
below).

A declared deviation from recommendation 4 of the orchestrator for v0.6.0,
which asked that a clone run print the notice "owner-held evidence, not
measured here" instead of "pending accepted": the rows keep the status
"pending accepted" and carry the notice inside the magnitude. A pending row
is the one status that cannot be read as a pass, and the exit code and the
list of accepted gates are computed from it; replacing it by a notice would
add a fourth status for the same fact. The notice is on every row of a
prior held outside the material, so the reader sees whose gap it is; this
material registers no such prior, so its report prints none.

## The hash policy

Every sha256 the instrument computes (the documents passed with `--case`,
the rubric, the gate section, the canon, the resolved map, the validator
itself, the inputs of a domain result and the lines of a chained ledger) is
the sha256 of the text as the validator reads it: UTF-8, a byte-order mark
dropped, every line break read as LF (since v0.6.0). The validator was
hashed as bytes until then, so a checkout converted to CRLF stayed red until
the report was regenerated. A file that is not UTF-8 text (a domain input only) is hashed as
its bytes. The material carries a `.gitattributes` that checks every text
file out with LF, and the scripts write UTF-8 to the console whatever its
code page; they require Python 3.9 or later and exit 2 below it (an
interpreter older than 3.7 refuses the file before any line runs).

## Domain gates

A gate of the target's domain (identity of results, a speedup, a mass) is
named `d-<name>` in the cell's gate table (every gate table of the gates
file is read, so domain gates may keep a table of their own) and is never
run by the validator:
the cell's own code measures it and writes a result file in the contract
`05-contracts/domain-result.schema.json` (the validator's own contract,
written out for the cells): the gate, the magnitude, the limit applied, the
result (`pass`, `fail` or `tool-failure`) and the sha256 of every input it
measured. The layout lists the result files under `domain-results`. The
validator reads each result and recomputes the sha256 of its inputs: an
input changed or missing makes the result stale (blocking), a result that
names no input is blocking too, `fail` is a note with the severity of the
gate's row (an optional Severity column, else high), `tool-failure` or a
result that breaks the contract is a tool failure (exit 2), and a declared
`d-*` gate with no result is pending, which no caller can accept by name.
Since the rework of v0.6.0 three more cases are blocking, because each let
a result pass for something it did not measure: inputs that do not include
every file of the artifacts the gate's row names (a result over the canon
alone passed while the candidate changed); a result its own numbers
contradict, compared only when the limit starts with a comparison and a
number (`≤ 2 s`, `at least 1.5 x`) or is a bare zero (`0 divergent`), the
value being the first number of the magnitude, and any other limit is not
read; and a Severity column below high counts only for a gate a decided
owner decision covers (`covers` names the gate), so a failed identity of
results cannot become a low note by a cell's own column. Declared reach: a
result whose inputs were recomputed by hand, the candidate changed and its
new sha256 written in, passes; it is the same act as running the gate again
without running it, which the validator, reading results and never running
the cell's code, cannot tell apart.
The validator does not run the cell's code and its sensitivity test perturbs
documents: the sensitivity of a domain gate is the cell's own (mutants, a
reference with a known defect), and the coverage of `p-sensitivity` leaves
domain gates out. The seat of the panel that instantiated a library had
the validator at exit 0 with its identity gate and its tests failing; that
regression is a test of the suite now.

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
the one executed instance, distributed under `../instances/` since
v0.5.0, kept its list in its state folder; that file stayed with the owner,
outside the material. An empty list measures nothing either: it leaves the
half pending, as no list does. Model identifiers belong to that list (form
rule 4 of the canon: an executor is named by family and effort).

The path-and-date half reads, since v0.5.0, the forms the panel that
reviewed v0.4.2 let through: a date written with the month's name (day
first or month first) or with dots, an absolute path of one
segment under a common root, a file URL and a home folder by user name. A
month and a year with no day, a version number and a relative path are not
hits. Since v0.6.0 it also reads the months in Portuguese and Spanish (a day, "de", the
month and the year), a date year first with slashes, a UNC path, an e-mail
address and a host name under a private suffix (`.local`, `.lan`,
`.internal`, `.intranet`, `.corp`); public domain names are not identifiers.
Since the rework of v0.6.0 it carries the months of French, German (a day
may end in a dot) and Italian as well. The brief declares the languages of
its documents on a line "Languages: en, pt" (two-letter codes); a declared
language with no built-in months and no row of the canon's table "Month
names" (the code and twelve names) leaves the dates in that language
pending on the brief under a name of its own, `p-anonymity-language`, never
a pass; since the closing pass of v0.6.0 `--allow-pending` does not accept
it (accepting `p-anonymity` stands for the forbidden list the material does
not distribute, not for a language the cell declared and gave no month
names), so the run exits 4 until the canon lists the months. A root of one segment is read
when another segment follows it, when it is one of the common roots the
validator carries (`tmp`, `home`, `scratch` and the others it lists), or when the canon's table "Machine roots" names it; any other
root alone is not read, a decision: a bare `/name` in prose is too often no
path, and the cell that has a root of its own names it.
A false positive has a valve: an interpreter line (`#!`) on line 1 is not
read, and a path the canon's table "Accepted paths" declares for one
document, with its reason, is not counted in that document (a final
period, the end of a sentence, is no part of the path compared, since the
closing pass). Since the rework of v0.6.0 the entry is a path and nothing else (an entry of another
shape is a tool failure), only a path hit equal to it is dropped, and no
text is blanked before the checks of identifiers and dates: the valve used
to blank whatever it listed, so a forbidden word or a date listed as
"accepted" vanished before every check. The canon cannot accept a path for
itself (a tool failure): it would let the judge pass its own text. A forbidden
list may hold entries `sha256:<hex>`, compared with the sha256 of each word
of the text, lowercased, so a list can measure without containing what it
forbids; such an entry matches one word, never a phrase. A pseudonym made of
the hash of a host name is no anonymity: it is reversed by trying the names
of a dictionary; keep a map held by the owner, or a salt.

**The commitment to the map of families.** The round record names the
executors by family letter; the map from letter to family stays with the
owner. Since the rework of v0.6.0 a chained line of the round record of
method version 0.6.0 or later carries `family_map_commitment`, a salted
commitment to that map, so a later reader can check that the letters were
not reassigned after the fact without the material naming any family. Its
canonical form is the sha256, over UTF-8, of
`json.dumps(map, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n' + salt`,
where `map` is the object from letter to the description of the family and
`salt` a string of 64 hex characters the owner keeps. `p-contract-shape`
checks the form only (64 hex characters on every such line); the owner
proves the commitment by revealing the map and the salt, and nothing in the
material lets anyone else check it.

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

## `p-form`: one reader of fences

Since v0.6.0 one tokenizer reads fenced blocks for every gate (the form,
the tables, the number check and the sections of a prior document), in the
CommonMark rules: a fence of three or more backticks or tildes, indented by
up to three spaces, closed by a line of the same character at least as long;
an unclosed fence runs to the end and is a note. A fence passes when its
info string is exactly `text`. An HTML comment (`<!--`) outside code is a
note like a tag: it hides text from every reader but this gate. Until then a
tilde fence and a fence indented in a list item went unread, a four-backtick
`text` fence failed, and the info string of a fence opened as `~~~python`
read as a home folder. A fence indented four or more spaces inside a list item is read as
indented code, not as a fence (declared).

## `p-prior`: what the number check reads

A prior mark has one reading in every gate since v0.6.0: any bracketed
`[prior:...]` is a mark, and its id has to be lowercase letters, digits and
hyphens; a mark outside that grammar, outside code spans, is a blocking
"malformed mark". Three readings coexisted until then, so a mark with a
capital letter satisfied `p-prior-mark` and switched off the number check.
A unit is marked by a mark outside code spans, and its numbers are read in
code spans too: a number between backticks used to pass unread. Numbers
written in words are not read.

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
  around it: the sentence "1054 words" passes if 1054 appears there,
  whatever it counts. The "Recorded facts" section of the canon is exempt by
  name, being the definition of the facts (since v0.6.0; it used to be
  exempt only because its marks sit in code spans).
- **Section commitments.** The canon commits to the sha256 of each cited
  section of a prior's document, as the reader
  of this gate delimits a section (the lines under a numbered heading, up to
  the next numbered heading, joined by LF). With `--case`, `p-prior` on the
  canon compares them, so a rewrite of a cited section after the fact is
  detectable and named. For a prior held outside its material, a run
  without the document says "owner-held evidence, not measured here", and
  the commitments reveal nothing of the text: they let nobody swap the
  document unseen. This material commits to the cited sections of
  `004-adoption-guide`, distributed and pinned whole.
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
checked none of the unit's numbers: an invented number passed both. Since
v0.6.0 a mark whose id breaks the grammar is no mark here either, and the
note says so. Statements about the registry itself are data, verified
by `p-contract-shape`, not by this mark. The frozen "Rubric" section of
`04-gates-and-rubric.md` keeps its original words: history, exempt by
design, like the review ledger.

For `p-prior-pin`, `--case` is **repeatable**: one document per executed
prior, each identified by its sha256 against the registry. Since the rework
of v0.6.0 the gate is measured prior by prior. A cited owner-held prior
whose document was not passed is pending by name ("1 of 2 executed priors
pinned; the id of that prior not measured"), so a clone measures the pin of
the prior it has; a cited distributed prior whose registered sha256 matches none
of the documents passed is blocking, and so is a document passed that is
the pin of no executed instance (a note on the registry, not a tool
failure; with such a document even the owner-held prior is blocking, since
the stray may be that prior, edited), and so is a cited executed instance
without a pinned sha256. The registry it checks against
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

## `p-sensitivity`: coverage, specificity and provenance

There is at least one perturbation per gate the validator implements: 20 of
its 21 gates, in 65 perturbations (six each on `p-anonymity`, `p-contract-shape`, `p-efficacy-mark`, `p-form` and `p-references`; five on `p-prior`; four each on `p-declared` and `p-frozen-rubric`; three each on `p-card`, `p-limit` and `p-terms`; two each on `p-canon-link`, `p-notes`, `p-prior-mark` and `p-size`; one each on `p-components`, `p-prior-pin`, `p-recipe`, `p-sections` and `p-table`). The 21st is this gate, which cannot
carry a perturbation without circularity: the baseline of the run reads the
report being regenerated. Its own defects (a fabricated report, another
validator, another set, a table that does not add up, another gate table,
canon or map, a missing report) are regression tests, and the measurement
`m-determinism` (the equality of the report across two runs, a measurement
of the instrument listed under "Measurements" in `04-gates-and-rubric.md`)
has none by definition. One perturbation empties a list of the canon and
expects the gate pending, not failing; the others expect a fail. Sixteen,
added in v0.6.0, measure the corrections of that version (most of them a
probe of the panel that reviewed v0.5.0, turned into a known defect), and
eight more cover (document, gate) pairs no earlier one reached; the second
pass added six for the frozen records, the ledger of the owner's decisions
and the skill's references.

**The copy is the material.** Since v0.6.0 each perturbation runs on a copy
of the whole material the folder belongs to (the folder and everything its
artifact table and registry reach above it). Until then the copy was the
folder alone: every perturbed run lost the root documents the baseline had,
and no perturbation could reach the principle, the root README, the skill or
the changelog.

**Specificity.** The perturbed report is compared with the baseline row by
row: a perturbation that changes the result of another row is noisy, listed
under the table, and a noisy perturbation fails this gate like a missed one.
Not counted: the expected row; the row of this gate, which reads the
provenance an edit of an input pins on purpose, under either of its names
(`p-sensitivity-synthetic` since the rework of v0.6.0: a perturbed pin makes
a recorded case read as synthetic); the rows of a document that
left the report (deleted or unmapped); and the gates a perturbation declares
it also reaches by design (`also`), which the report lists. Eleven of the
corpus's perturbations declare one: a pin decides which document is the
prior, so altering it moves `p-prior`; one list of the canon feeds a gate on
every document; a placeholder in angle brackets also reads as an HTML tag;
an edited old line of a chained ledger breaks its chain.

**Coverage by gate and by pair.** The gates the artifact table assigns,
except this one, the measurements (`m-*`) and the domain gates, are compared
with the expected gates of the report's rows; and the (document, gate) rows
of the baseline report, except this gate's, are compared with the pairs the
measured perturbations target. The magnitude reads "k of n gates covered, p
of q pairs (r %), 0 missed of m, 0 noisy". An assigned gate without a
perturbation, or fewer than 25 % of the pairs perturbed, leaves this gate
pending with the reason, never a pass. The floor is a hypothesis: the panel
measured 18 %, a quarter is the first floor this version commits to, and it
is raised, never lowered; this corpus covers 54 of 182 pairs. The three
generic perturbations of a new cell cover the three gates and three pairs
of the smallest filled cell; each gate a cell adds needs one of its own.

**Provenance.** A row whose gate needs an input not passed (`--case`,
`--rubric-hash`, `--notes`, a registry for a perturbation that edits it, or
the document of the very prior it names) is not measured, and a report that
measured fewer rows than the set fails here; a row whose prior's document was
not passed is not measured, never missed, prior by prior (since the rework of
v0.6.0). The report carries its provenance: the sha256 of the validator that
produced it, the sha256 of the gate section of the gates file (its "Gates"
section; a cell's whole gates file), of the canon and of the resolved gate
map, the ids and count of the perturbation set, and, since the rework of
v0.6.0, one line `case sha256: <id> <sha256>` per prior document the report
was made with (`case sha256: none` without any), computed by
`sensitivity.py`. The validator recomputes the others and compares; a
report without the case lines is refused; the validator sha has to match both the validator that is
running and the `validator.py` next to the report (since v0.6.0: the
neighbor alone let an edited copy run against an old report). It counts the
rows of the table against the "Caught" line. An edit of the gate table, of
the canon, of the artifact table's map or of the validator makes the report
stale: regenerate it before the next run. A gate the validator does not
implement in the set (a domain gate, a typo) is a tool failure of the
sensitivity test, never a miss. This corpus keeps its set in
`perturbation_set.py` (since v0.6.0 a module of its own, which the validator
reads without importing the sensitivity script; the two used to import each
other); a cell keeps its own as data (the layout key
`perturbations`, a JSON list of the fields of a perturbation, a name without
a comma), and `sensitivity.py --layout` reads a cell like the validator
does. The set is written by whoever wrote the gates: it measures the defects
its author imagined, and the panel's probes were defects that authorship
had not; since v0.6.0 part of the set comes from those probes.

**A synthetic prior, for a clone of a cell whose prior is held elsewhere.**
This material registers no such prior and does not use it; the mechanism
stays for a cell that does. `sensitivity.py --synthetic-prior PRIOR_ID`
generates a document from the canon's recorded facts (one
numbered section per label the facts cite or the marked units reference,
holding the facts' numbers in the prior's number format), passes it as
`--case`, and patches its sha256 and its section digests into the registry
and the canon of every copy, never of the material. Since the rework of
v0.6.0 its headings follow the `heading_style` the registry declares for the
real document (a pattern each for a section, a subsection and a step; a
label the canon cites as a step is written as a step), so
a reader of `p-prior` that stops reading the real style fails on the
synthetic too; without `heading_style` the headings are plain and test no
format. The synthetic does not test the reading of the real document's
format beyond what the registry declares: a style the registry does not
know, or text between headings the reader mistakes, passes on the synthetic
and fails on the real document.

The report records the synthetic document's sha256 on its `case sha256`
line, and the validator tells a synthetic prior by that sha256 differing
from the registry's pin, never by a line that declares it (the line
`synthetic priors:` of the first draft could be deleted, and the report then
read as the owner's). A report made with a synthetic prior is never a pass:
in a run without that prior's document its row is `p-sensitivity-synthetic`,
pending, accepted only when the caller names that gate with
`--allow-pending`; in a run with the document it is refused, since the
published report is made with it. What it covers: that each gate fails its
known defect, so a maintainer who edits the instrument without the document
can see the gates react. What it does not cover: that the real document
holds those facts, and that the validator reads its format; both stay with
whoever holds the document, who regenerates the report with it.

**The attestation, and what it leaves.** The pin of the registry is
public, so a `case sha256` line can be written by hand with the real pin
over a report made with the synthetic document. Until the closing pass of
v0.6.0 that line passed the run without the document and the run with it,
and a regeneration with the document came out byte-identical to the forged report whenever the real
and the synthetic document gave the same rows, which is the common case:
the detector this section used to name did not detect. Since the closing
pass the report records, for each document it was made with, a line
`case attestation: <id> <sha256>`. The sha256 is taken over the document's
text followed by the validator, gates, canon and map digests of the report,
one per line, and only whoever holds the text computes it. A run that
passes the document recomputes it, and a report whose case line holds the
pin with an attestation that does not match is blocking: for a distributed
document, every run that passes it. A published attestation
holds only for the inputs it was made over, so copying it into a tree with
a re-pinned canon does not match either. What it leaves: a run without the
document compares nothing, so a forged line for a prior held elsewhere still
passes there, and
a frozen record re-pinned in the canon shows there only in the diff against
a signed version (the anchor outside the tree, the owner's).

A synthetic report is held to the same floor as the published one (closing
pass of v0.6.0): an assigned gate without a perturbation, or fewer than a
quarter of the pairs, leaves `p-sensitivity` pending with the reason, which
no name accepts; the synthetic name applies only to a report that would
otherwise pass. Before, the synthetic path returned first, and accepting
`p-sensitivity-synthetic` took away a pending no name accepts.

## `p-frozen-rubric`: frozen records

Since v0.6.0 the canon's table "Frozen records" pins the sha256 of the
records that are never edited: the reviewer's report and ledger of round 1,
the derived note ledger, the replies, the pin of the rubric, and the part of
`99-lessons.md` above the heading the efficacy gate reads from. Each is a row
of this gate, blocking when it changed; the panel that reviewed v0.5.0
rewrote "Rejected" as "Accepted" in the reviewer's report and no gate saw
it. The reach is the chain's: an edit nobody announced, not whoever
controls the whole tree.

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
gap. The mitigation is a careful reading of the prose, not the gate; a
frozen rubric does not make that reading find more, as far as E4 measured
(the seeded claim of efficacy passed the gate on three copies, and reviewers
with the rubric let no fewer seeded defects escape than reviewers with a
checklist) [against:E4]. The gap stays open for the maintenance rounds of
this material, read by a review in some rounds and by none in others
(declared). A claim labeled `[hypothesis]` that states a number or a
universal quantifier ("every", "always", "none", a percentage) is a low
note since v0.6.0: the label stays valid, and the row passes. The founding
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
a gate about labels, and the version history was expected to show any
edit of that part. That expectation was wrong for whoever clones the
material: the published history has two commits and does not carry the
rewrites earlier rounds admitted (corrected in v0.6.0). The two ledgers that
were append-only by rule, and the ledger of the owner's decisions added in
v0.6.0, now carry a hash chain (below), and the history of
the lessons above its measured heading, the review's report, notes and
replies are pinned as frozen records of the canon (see `p-frozen-rubric`).

## `p-efficacy-mark`: what an experiment label cites

An `[experiment:<id>]` label backs a claim only when `<id>` is an executed
experiment of `60-experiments.md`: a level-2 heading `## E<n> — ...` whose
block declares the status `executed` (a "Status" row of its field table, or
a "Status:" line). A label that cites a designed or pending experiment is a
note ("cites a designed experiment as evidence"): a design is not evidence
yet. An id the record does not open with such a heading is not registered;
a subheading such as "Question" or "Cost" never names an experiment (since
v0.4.1, after the review of v0.4.0 found that any heading word registered
an id). Since v0.6.0 an executed experiment backs a label only with its
provenance: a "### Provenance" table in its block whose rows give the kind
(`input` or `output`) and the sha256 of each file, with at least one of each.
Without it the label reads as `[hypothesis]`, with a note: `executed` is a
word the producer writes, and the hashes are what an owner holding the raw
files can re-verify. The validator checks that the table is there, not that
the hashes match files it never sees.

A `[lessons:<title>]` label backs a claim with one entry of the lessons
file (layout key `lessons`): its title is the text of a level-2 or level-3
heading there, and a title that names no heading is a note. A bare
`[lessons]`, which pointed at a whole file, is no label since v0.6.0.

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

Since v0.6.0 the state ledger and the round record are append-only by
mechanism, not only by rule. Each line written from v0.6.0 on carries
`prev`, the sha256 of every line above it, each followed by LF (for a file
with no blank line, the sha256 of the file before the line was appended), and
`p-contract-shape` recomputes the chain: an earlier line edited, removed or
reordered breaks the first chained line after it. The canon's table "Chained
ledgers" counts the lines written before the chain (10 and 48 here), and
every line after them has to carry `prev`, so stripping the chain is a
finding too; a ledger the canon does not list starts its chain at its first
chained line. A change of status of a note is a new chained line, and the
last line of a ref is its state. A chained line of the round record also
declares its `kind` (`production` or `maintenance`), the
`reviewer_relation` when a reviewer role is listed, no verdict of the canon
when it is a maintenance round, and, when `rubric_applied` is true, a
`rubric_hash` equal to the frozen rubric; since the rework of v0.6.0, the
`family_map_commitment` of a line of version 0.6.0 or later, and a low note
when `rubric_applied` is true and `rubric_author` is `producer` ("rubric
written by the producer": a verdict under the producer's own criteria). The
reach is declared: the chain detects an edit made without recomputing it,
the careless maintainer and the honest error; it does not detect an edit
that recomputed it, which costs one sha256 per line (a script of ten lines
did it in the review of this round, with exit 0), and only an anchor
outside the tree (a signed tag per version, the owner's) answers that. Nor
does it cover the last line of a ledger: a line's `prev` covers the lines
above it, so the last one can be rewritten with no sign until a line is
appended after it (the round line of 0.6.0 was rewritten that way in this
round, openly, before the next line).

## `p-notes`: the rules of the state

Since v0.6.0 the last line of each tracked note in the state ledger is read
against four rules:

- **Golden rule 4.** A note that is a regression that escaped every gate
  (`escaped: true`) closes with the gate it became (`gate`) or with the
  recorded reason not to make one (`no_gate`); closed with neither, it is a
  high note. Since the rework of v0.6.0 the gate is a row of the cell's gate
  table (any name of a domain gate used to count, even one no table
  declares), and the reason has at least 8 distinct words or the line's
  `decision` is exactly the name of a decided owner decision (`no_gate:
  "x"` used to count; since the closing pass, a substring of a name, or a
  decision with an empty name, no longer counts, and the contract refuses an
  empty name); a decision reopened later no longer counts. The count of
  words measures the form of the reason, not its content: eight distinct
  words that say nothing pass, and the review reads whether they say why.
- **Age.** An open note is counted in rounds of the round record from the
  version it was opened in (`opened_in`, the version of a panel ref, or
  0.1.0 for the frozen ledger of round 1). Past 3 rounds, and not scheduled
  for a version still ahead (`due`), it is a low note: schedule it, dispute
  it or close it with the reason. Three rounds is a hypothesis: the panel
  counted 16 of the 22 notes of round 1 open nine rounds later.
- **Non-negotiables.** The brief gives each non-negotiable an id in a code
  span (`nn-<name>`); a note names those it affects (`affects`). An open note
  of severity high or blocking that affects one is blocking, unless a
  decided entry of `state/owner-decisions.jsonl` covers it (`covers`). The
  owner's decisions are a chained ledger of their own, with a contract
  (name, status, what it blocks, the version, the notes it covers). Since
  the rework of v0.6.0 the fields the writer of a line controls cannot
  undo the protection: the severity is the highest of the note ledger's and
  of every line of the ref (lowering it is an owner decision, which covers
  the note instead), the non-negotiables are the union of every line's
  `affects`, a decision covers only while its last line is `decided`, and a
  high or blocking note opened in 0.6.0 or later names what it affects
  (`affects`, an empty list when nothing), or it is a high note.
- **Evidence.** A note of a ledger passed with `--notes` whose evidence names
  a file of the material (a path ending in `.md`, `.json`, `.jsonl` or
  `.py`) needs that file to exist; the frozen ledger keeps the names of its
  time and is exempt by design.

## `p-size`, `p-limit` and `m-determinism`: what they count

`p-size` counts words separated by whitespace, and since v0.6.0 the pipes
and separators of a table are not words; the ranges were set before, so the
counts dropped by about a tenth and every document stayed inside its range.
`p-limit` is a lexical proxy: it reads the origin label and the number of
words of a justification, so six words of any kind pass; the review reads
whether they justify. `m-determinism` compares the report of two runs, the
second with another hash seed and the C locale; the working folder and the
Python version (3.9 and 3.12) were varied by hand, not by the measurement.

## `p-references`: commands and versions

A record of a JSON artifact list may carry the `command` that produces it.
Since v0.6.0 the validator resolves it against the folder: every path it
names (the script, its inputs, its outputs) has to exist, and the command is
never run; a cell whose command pointed at the wrong version kept writing
the results of v1 into v2 unseen. The paths and commands may carry
`{version}`, which takes the layout's `version-label` (`v2`), so a cell that
moves to a new version changes one key; and `closed_in` in the state ledger
takes that label too.

## The instrument: families and data

Since v0.6.0 the checker of the validator is one class per family of gates
(form, prior, contracts, records and sensitivity, domain) over a core that
holds the state of a run and the interface every family uses (`record`,
`pending`); the split moved the methods unchanged, and the report of the
corpus was byte-identical before and after it. The self-test stays embedded
in the validator: the runbook and every cell use it without pytest, and the
suite runs it.

## `p-declared`: the sub-cases

Two rules of the instrument itself, added in v0.3.0 after the critical
panel. First, `p-declared`: a declared path that matches nothing on disk is
a blocking note naming it (since v0.6.0 each literal path has to exist and
each glob to match at least once; deleting one of the two literal files of
an artifact used to pass); a
declared artifact marked `proposed` is pending with its reason, and one
declared with no paths at all is pending ("declared without paths"), never
silent. Second, outside any gate row: a run that measures zero documents is
a blocking note on `artifacts`. A production with no documents is not green,
so a newly scaffolded cell fails high until it has real artifacts.

## The false greens of the gates

A failure-mode analysis of the validator's gates, since the rework of
v0.6.0, for the one failure mode that matters to a verdict: the false green,
a defect the gate lets through with a pass. Each row names the cause, what
detects it today, the probe that first found it, and the perturbation of
`perturbation_set.py` that covers it now. The causes are the ones found so
far, not an exhaustive list; a new probe that passes a gate adds a row and a
perturbation. Domain gates are the cell's, and their false greens are the
cell's to analyze; the three cases the validator closes are under "Domain
gates" above.

| Gate | Cause of a false green | Current detection | Probe that found it | Perturbation that covers it |
| --- | --- | --- | --- | --- |
| `p-terms` | a synonym of a canonical term written in a way the lexical match does not see (inflected, hyphenated, in a link text) | the list of the canon and whole-word matching; the review reads the prose | not recorded (the changelog entered the gate's map in v0.5.0) | avoid-word in the changelog |
| `p-canon-link` | a link that names the canon from the wrong folder | the target is resolved relative to the document's folder since v0.4.0 | the review of v0.3.1 (a card linking the canon from inside its folder) | link to the canon does not resolve |
| `p-anonymity` | a path, a date or an identifier in a form the patterns do not know, or hidden by the valve | the patterns of the gate, the month names of six languages and the canon's own, the forbidden list by name or sha256; an accepted path is dropped only by equality | the panel that reviewed v0.5.0 (a date in Portuguese, a UNC path) and the independent review of v0.6.0 (a forbidden word listed as an accepted path) | date written with the month's name |
| `p-form` | an HTML tag or comment hidden in a block the reader skips | one reader of fences (backtick and tilde, indented), comments read | the panel that reviewed v0.5.0 (a tilde fence and a comment) | HTML comment |
| `p-size` | a document pushed past its range when the range is not declared, or words counted wrong | the declared ranges; the pipes of a table are no words since v0.6.0 | the panel that reviewed v0.5.0 (a table inflating the count) | canon pushed above its size range |
| `p-table` | an instantiation table missing a row the canon requires | the canon's fixed list of rows | not recorded (a gate of round 1) | instantiation table row deleted |
| `p-sections` | an instance missing a mandatory section | the canon's fixed list of sections | not recorded (a gate of round 1) | mandatory section heading removed |
| `p-card` | a role card with a field empty, deleted or filled with a placeholder | the canon's seven fields, the placeholder detector | not recorded | placeholder in a card field |
| `p-limit` | a justification of six words of any kind, or a limit raised in the table | the origin label and the word count; the Limit column compared since v0.6.0 | the panel that reviewed v0.5.0 (a limit cell nobody compared) | limit raised in the gate table |
| `p-references` | a reference to a role, an artifact or a gate that does not exist | the artifact table, the graph without cycles, the commands resolved against their paths | the panel that reviewed v0.5.0 (a Limit cell nobody compared) | limit cell diverges from the applied limit |
| `p-prior` | an invented number about a prior: in a code span, under a malformed mark, in a section the reader does not find, or a reader that stops reading the real heading style | each number checked in the sections its recorded fact cites, in the prior's number format; section commitments on the canon; the synthetic prior written in the registry's heading style | the panel that reviewed v0.5.0 (a number in a code span, a malformed mark) and the independent review of v0.6.0 (the step headings left unread) | prior number in a code span |
| `p-prior-mark` | a statement about a prior with no mark, or with the mark in a code span | the canon's triggers, read outside code spans | the review the gate was created after (a qualitative statement about the prior passed) | prior mark inside a code span |
| `p-prior-pin` | a prior document swapped or edited, or a pin no run compares | the registry's sha256 compared with each document passed, prior by prior | the critical panel before v0.2.1 (a pin only the owner could check) and the independent review of v0.6.0 (a clone run that measured no pin) | prior pin altered in the registry |
| `p-contract-shape` | a ledger line rewritten, a contract of another version, a registry entry that breaks its status | the schemas line by line, the hash chain of the three ledgers (an edit that recomputes it is not detected) | the panel that reviewed v0.5.0 (an old line rewritten) | old line of the round record edited |
| `p-recipe` | a step of the recipe without one of its fields | the canon's step fields | not recorded (a gate of round 1) | step field deleted |
| `p-components` | a method component the principle names and an instance omits | the canon's list of components | not recorded (a gate of round 1) | method component omitted |
| `p-efficacy-mark` | a claim that the method works, without a label or with a label citing nothing executed | the canon's triggers (lexical: a paraphrase escapes), the provenance table of an experiment, a lessons title that resolves | the panel that reviewed v0.5.0 (an experiment label without provenance) | claim backed by a designed experiment |
| `p-notes` | a note without a state, a regression closed with a gate that does not exist, a protection undone by a later line | the state ledger, golden rule 4 against the gate table, the highest severity and the union of `affects` over every line | the independent review of v0.6.0 (a closure with an undeclared gate, a severity lowered by a later line) | note without a status line |
| `p-frozen-rubric` | a rubric or a frozen record rewritten after the fact | the sha256 of the rubric and of each record the canon freezes; a re-pinned canon makes the sensitivity report stale, and a report regenerated with a synthetic prior is never a pass, and a `case` line forged with the real pin is refused by the attestation in a run that passes the document; a re-pin of the canon shows only in the diff against a signed version | the second pass of v0.6.0 (no record of the review was pinned) and the independent review of v0.6.0 (a verdict rewritten with the canon re-pinned) | frozen review report rewritten |
| `p-sensitivity` | a report the instrument did not produce, a stale one, or one made without the real prior document read as made with it | the provenance header, the case lines against the registry's pins, the attestation of each document a run passes, a synthetic prior never a pass and held to the floor of the pairs (a case line forged with the real pin passes where the document is not passed, which needs a prior held elsewhere) | the panel that reviewed v0.5.0 (a deleted report accepted) and the independent review of v0.6.0 (a synthetic report with its marking line deleted) | none: the baseline reads the report; its defects are regression tests |
| `p-declared` | a declared path that matches nothing, a repointed file, a document no artifact declares | each literal path and each glob, the resolved map pinned in the sensitivity's provenance | the panel that reviewed v0.5.0 (a repointed file) | file of an artifact repointed |

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
table. No gate was retired in v0.4.0, v0.4.1, v0.4.2, v0.5.0 or v0.6.0.

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
