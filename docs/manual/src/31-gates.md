
# The gate catalogue

This chapter is the reference of the gates the validator implements at
version 0.6.0: 17 builtin gates measured per document, 4 global gates
measured once per run, one measurement of the instrument, and the family
of domain gates a cell supplies. For each gate: the artifacts the
reflexive application assigns it to, what it reads, its limit, when it is
pending, and the semantics worth knowing before reading a note. The
authoritative text is the gate table of `04-gates-and-rubric.md` and the
declared semantics of `06-gate-semantics.md`.

## Conventions shared by every gate

- **Units.** A gate reads a document in units: a paragraph, a list item, a
  table row or a heading. A mark or a label applies to the unit it sits in.
- **Code spans and fences.** Since v0.6.0 one tokenizer reads fenced
  blocks for every gate, in the CommonMark rules (three or more backticks
  or tildes, indented up to three spaces, closed by a line of the same
  character at least as long; an unclosed fence runs to the end and is a
  note). Marks, labels and triggers are read outside code spans: a mark
  between backticks is notation, not a mark.
- **Placeholders.** An angle-bracket word (`<fill in>`), `TBD` or `TODO`
  outside code spans is an unfilled field in exactly four places: a card
  (`p-card`), a gate row (`p-limit`), an instantiation cell (`p-table`) and
  an artifact record (`p-references`). A placeholder in prose passes every
  gate and is the review's to find.
- **Empty lists.** A gate whose object is a list of the canon is pending
  when that list is empty, never a pass of 0 of 0.
- **Severity.** A hit is a high note unless the gate's semantics say
  blocking (a cycle, an invented prior number, a malformed mark, a missing
  declared file, a broken chain, a changed frozen record, a stale domain
  result) or low (an advisory).
- **Cap.** 50 notes per gate; the 51st is replaced by a count.

## Gates measured per document

### `p-terms` — terms to avoid

- **Assigned to:** every prose document of the material, the changelog, the
  replies, the experiments and the skill's files.
- **Reads:** occurrences of each term of the canon's "Terms to avoid" table
  (`quality gate`, `checkpoint`, `pipeline`, `feedback`, `iteration`,
  `single source of truth`, `bible`, `ruler`, `review board`), as whole
  words, case-insensitive, with a plural suffix, outside code and link
  targets; in the canon, outside the table itself.
- **Limit:** 0. `[method]`: a synonym outside the canon is the first sign
  of drift, and replacing it costs one word.
- **Exempt:** the frozen ledger under `90-review/`, by design: vocabulary
  rules govern living documents.

### `p-canon-link` — a link to the canon

- **Assigned to:** every document except the canon and the frozen records.
- **Reads:** links naming `01-canon.md` (or the cell's canon file) that
  resolve, relative to the document's own folder, to the canon of the
  layout; and links naming it that do not resolve.
- **Limit:** ≥ 1 resolved, 0 unresolved. `[method]`: a reader who lands on
  a loose document needs to know where the definitions are.

### `p-anonymity` — paths, dates, identifiers

- **Assigned to:** every document, the registry, the three ledgers, the
  principle, the root README and the skill.
- **Reads, the path-and-date half:** absolute paths (a segment under a
  common root such as `/tmp`, `/home`, `/opt`; a path of two or more
  segments; file URLs; home folders by user name; UNC paths); dates in
  year-month-day, day/month/year, year/month/day and day.month.year
  formats; dates written with a month's name in English, Portuguese,
  Spanish, French, German or Italian, and in a language the canon's "Month
  names" table adds; the expressions "made on", "written on", "generated
  on" followed by a date; e-mail addresses; host names under a private
  suffix (`.local`, `.lan`, `.internal`, `.intranet`, `.corp`); a root of
  one segment the canon's "Machine roots" table names. A month and a year
  with no day, a version number, a relative path and a public domain name
  are not hits.
- **Reads, the identifier half:** the entries of the `--forbidden` list,
  by name or as `sha256:<hex>` entries compared with the sha256 of each
  lowercased word. Model identifiers belong to that list. The list is kept
  outside the material, since it contains what it forbids; the corpus runs
  with none, so this half is **pending by design** and accepted by name.
- **Limit:** 0. `[brief]`: the brief forbids absolute paths, authoring
  dates, machine names and user names; in the method the gate is an option
  of the instance.
- **Valves:** an interpreter line (`#!`) on line 1 is not read; a path hit
  equal to an entry of the canon's "Accepted paths" table for that document
  is dropped (the entry has to be a path and nothing else; the canon
  cannot accept a path for itself); a final period is not part of the path
  compared.
- **Languages:** the brief declares the languages of its documents on a
  line `Languages: en, pt`; a declared language with no built-in months and
  no row of the canon's table is pending on the brief under
  `p-anonymity-language`, which no caller accepts.

### `p-form` — plain Markdown

- **Assigned to:** every prose document and the changelog.
- **Reads:** HTML tags and comments outside code; fenced blocks (backtick
  or tilde, indented up to three spaces) whose info string is not exactly
  `text`.
- **Limit:** 0. `[brief]`: plain Markdown and pseudocode only in `text`
  blocks are non-negotiables of the brief.

### `p-size` — words in range

- **Assigned to:** the documents of the "Size ranges" table of the gates
  file.
- **Reads:** words separated by whitespace; since v0.6.0 the pipes and
  separators of a table are not words.
- **Limit:** within the range declared, before writing, in the "Size
  ranges" table. `[hypothesis]`: a range is raised before writing, never
  met by cutting text.

### `p-table` — the instantiation table

- **Assigned to:** the three instances.
- **Reads:** the rows of the canon's "Instantiation table rows" list
  present in the two-column table that opens the instance; empty cells or
  cells holding a placeholder.
- **Limit:** 14 of 14, 0 empty. `[method]`: the table is the summary that
  makes instances comparable.

### `p-sections` — the mandatory sections

- **Assigned to:** the three instances.
- **Reads:** the headings of the canon's "Mandatory sections of an
  instance" list.
- **Limit:** 14 of 14. `[method]`: each section corresponds to a step of
  the recipe.

### `p-card` — the seven fields

- **Assigned to:** the role cards and the three instances (which carry
  cards of their own).
- **Reads:** per card, the fields of the canon's "Role card fields" list
  missing (as bold labels), and placeholders left in a field.
- **Limit:** 0 missing, 0 placeholders. `[method]`: a role without a gate
  and without a note is a step; the seven fields make that verifiable.

### `p-limit` — justified limits

- **Assigned to:** the gates file and the three instances.
- **Reads:** gate table rows with an empty magnitude, limit or
  justification; a justification without an origin label or with fewer
  than 6 words (the number is read from the gate's own row); a placeholder
  in a field.
- **Limit:** 0. `[method]`: 6 words is the minimum to say where the number
  comes from and why not another one. It is a lexical proxy: six words of
  any kind pass, and the review reads whether they justify.

### `p-references` — the graph closes

- **Assigned to:** the artifact table, the cards, the gates file and the
  three instances.
- **Reads:** artifacts cited in gates, dependencies or notes a card emits
  and not declared; owners that are neither a role nor `owner`; cycles in
  the graph (blocking); gates the artifact table assigns with no row in
  the gate table, or rows naming other artifacts than it assigns;
  placeholders in an artifact record; paths an artifact's `command` names
  that do not exist; Limit cells whose numbers are not the numbers of the
  limit the validator applied.
- **Limit:** 0. `[method]`: a loose reference is the written form of "the
  old text nobody knew had changed"; a cycle means a wrong graph.

### `p-prior` — numbers about a registered prior

- **Assigned to:** the principle, the canon, the recipe, the three
  instances, the lessons and the experiments.
- **Reads:** prior labels whose id is not registered, or whose id breaks
  the grammar `[0-9a-z-]+` (a malformed mark, blocking); every number of a
  unit marked `[prior:<id>]`, code spans included, which needs a row of
  that prior in the canon's "Recorded facts" and is checked by presence in
  the union of the sections the row cites, in the method document passed
  with `--case` whose sha256 is the pin of `<id>`, read in the
  `number_format` the registry declares; section references ("section
  2.1", "step 16") checked by the existence of that label; on the canon,
  the section commitments compared with the sections of the documents
  passed.
- **Limit:** 0. `[brief]`: a number absent from the prior's method
  document is an invented fact until proven otherwise.
- **Pending:** without a registry; without the `--case` document of a cited
  prior (pending by name: a cited owner-held prior reads "owner-held
  evidence, not measured here").
- **Exceptions:** the full id of a registered instance
  (`004-adoption-guide`) is a name, a bare `004` is a number; a digit
  attached to a letter (`p95`, `v7`) is a name; numbers written in words
  are not read. The check verifies the presence of the number's tokens in
  the cited sections, not the claim around it; the "Recorded facts" section
  of the canon is exempt by name.

### `p-prior-mark` — statements about a prior carry the mark

- **Assigned to:** the principle, the recipe, the three instances and the
  experiments.
- **Reads:** paragraphs, list items and table rows that use a phrase of
  the canon's "Prior-statement triggers" without a `[prior:...]` mark
  outside code spans (a mark in a code span is no mark; a mark outside the
  grammar is no mark either).
- **Limit:** 0. `[method]`: created after the first review, where a
  qualitative statement about the prior, absent from its document, passed
  every gate because only numeric statements needed a mark.
- **Exempt:** the frozen "Rubric" section of the gates file, by design.

### `p-prior-pin` — the pin of each executed prior

- **Assigned to:** the registry.
- **Reads:** for each executed prior cited in a document that carries
  `p-prior`, the registered sha256 compared with the documents passed with
  `--case`, prior by prior: a cited owner-held prior whose document was not
  passed is pending by name; a cited distributed prior whose pin matches
  none of the documents passed is blocking; a document passed that is the
  pin of no executed instance is blocking (with such a document even the
  owner-held prior is blocking, since the stray may be that prior, edited);
  a cited executed instance without a pin is blocking.
- **Limit:** equal. `[method]`: a pin nobody can re-verify is not a pin.

### `p-contract-shape` — the contracts hold

- **Assigned to:** the artifact table, the contracts, the registry, the
  note ledger, the state ledger, the round record and the owner decisions.
- **Reads:** schema cells of the artifact table citing a `*.schema.json`
  file that is missing or does not parse; keywords of each contract outside
  the subset the validator applies, or a `contract_version` other than the
  one it reads (`1`); the registry, the note ledger, the state ledger, the
  round record and the owner decisions validated line by line against
  their schemas; registry entries that break the contract of their status;
  the hash chain of the three append-only ledgers (chapter 15) and the
  rules of a chained line of the round record (its `kind`, its
  `reviewer_relation`, no verdict on a maintenance line, a `rubric_hash`
  equal to the frozen rubric when `rubric_applied` is true, the form of
  `family_map_commitment`).
- **Limit:** 0. `[method]`: a contract that exists but is never applied is
  not a contract.

### `p-recipe` — the steps of the recipe

- **Assigned to:** the recipe.
- **Reads:** steps missing one of the fields "Reads", "Creates", "Does",
  "Done when"; the number of steps (the minimum is read from the gate's
  row).
- **Limit:** 0 missing a field; ≥ 12 steps. `[method]`: 12 is the number
  of steps in the principle's recipe, which this one details.

### `p-components` — the eleven components named

- **Assigned to:** the three instances.
- **Reads:** the method components of the canon's list named in the
  document (inflected forms accepted).
- **Limit:** 11 of 11. `[method]`: an instance without one of them is not
  the method.

### `p-efficacy-mark` — claims of efficacy carry their evidence

- **Assigned to:** the principle, the brief, the recipe, the three
  instances, the lessons (from the heading the canon declares on), the
  README and the experiments.
- **Reads:** units that use a phrase of the canon's "Efficacy triggers"
  without one of the labels `[prior:<id>]`, `[experiment:<id>]`,
  `[against:<id>]`, `[lessons:<title>]`, `[hypothesis]` outside code
  spans; `[experiment:<id>]` and `[against:<id>]` labels that do not name
  an executed experiment with a "Provenance" table in `60-experiments.md`
  (a label citing a designed or pending experiment is a note; one without
  provenance reads as `[hypothesis]`, with a note); `[lessons:<title>]`
  labels that name no level-2 or level-3 heading of the lessons file; a
  `[hypothesis]` claim with a number or a universal quantifier (a low
  note).
- **Limit:** 0. `[method]`: a claim that the method itself works is a
  statement of the same kind as a statement about a prior, and exempting it
  was the double standard a critical panel found.

## Gates measured once per run

### `p-notes` — the note ledgers

- **Assigned to:** `open-notes` and `notes-status`.
- **Reads:** notes of the ledger passed with `--notes` missing one of the
  six fields, with a severity outside the four, or with a target outside
  the graph; notes without a line in the state ledger, or with two, or
  with a closing status and no version; evidence naming a file of the
  material (`.md`, `.json`, `.jsonl`, `.py`) that does not exist; the
  rules of the state (chapter 15): an escaped regression closed with
  neither a gate of the gate table nor a reason (high); an open high or
  blocking note that affects a non-negotiable and no decided owner decision
  covers (blocking); an open note older than 3 rounds and not scheduled
  (low).
- **Limit:** 0. `[hypothesis]`: a note aimed at an artifact the graph
  does not know is undeliverable; the note router of the first instance
  rejected such a target `[prior:000-av-production]`.
- **Pending:** without `--notes`; that pending cannot be accepted.

### `p-frozen-rubric` — the rubric and the frozen records

- **Assigned to:** the gates file and the review.
- **Reads:** the sha256 recorded at the launch of the review
  (`--rubric-hash`) against the current sha256 of the rubric as the layout
  resolves it; and the sha256 of each record the canon's "Frozen records"
  table pins (the reviewer's report and notes of round 1, the derived
  note ledger, the replies, the pin of the rubric, and the part of the
  lessons above the heading the efficacy gate reads from).
- **Limit:** equal (blocking when a record changed). `[method]`: a rubric
  changed after the review makes the verdict incomparable. The panel that
  reviewed v0.5.0 rewrote "Rejected" as "Accepted" in the reviewer's report
  and no gate saw it; since v0.6.0 the records are pinned.

### `p-sensitivity` — the gate on the gates

- **Assigned to:** `instrument-validator`.
- **Reads:** the sensitivity report named by the layout: a missing report
  (blocking); an incomplete one; a table that does not add up to its
  "Caught" line; a provenance that does not match (the running validator
  and the one next to the report, the "Gates" section, the canon, the
  resolved gate map, the perturbation set, the `case sha256` of each prior
  document and its `case attestation`); known defects the expected gate let
  through (missed) or that changed another row (noisy); an assigned gate
  without a perturbation, or fewer than 25 % of the (document, gate)
  pairs perturbed (pending with the reason, never a pass); a report made
  with a synthetic prior (pending under `p-sensitivity-synthetic` in a run
  without that prior's document, refused in a run with it).
- **Limit:** every gate covered, ≥ 25 % of pairs, 0 missed, 0 noisy.
  `[method]`: a gate that never fails proves nothing, and a report this
  instrument cannot have produced proves nothing either; `[hypothesis]`:
  the floor of a quarter of the pairs is the first this version commits
  to, above the 18 % a panel measured, to be raised and never lowered. The
  corpus covers 50 of 182 pairs.

### `p-declared` — what is declared exists, and what exists is declared

- **Assigned to:** the artifact table.
- **Reads:** declared paths that match nothing on disk (each literal path,
  and each glob at least once; blocking, naming the path); Markdown
  documents of the folder no artifact declares and the canon does not list
  as outside the table; files that belong to two artifacts; documents of
  the "Size ranges" table no artifact declares; a declared artifact marked
  `proposed` (pending with its reason) or declared with no paths (pending).
- **Limit:** 0. `[method]`: a declared document that silently matches no
  file is a promise the instrument never kept.

## The measurement of the instrument

### `m-determinism`

Not a gate on a document: a measurement of the validator itself, which
cannot fail a document. It is the equality of the report's sha256 across
two consecutive runs on the same input, the second with another hash seed
and the C locale; measured only with `--determinism`, and a difference is
a high note. `[hypothesis]`: a report that changes by itself is not
evidence; the continuity ledger the validator of the first instance wrote
was deterministic `[prior:000-av-production]`.

## Domain gates

### `d-<name>`

A gate of the target's domain, declared as a row of the cell's gate table
(every gate table of the gates file is read, so domain gates may keep a
table of their own) and never run by the validator. The cell's own code
measures it and writes a result file in the contract
`domain-result.schema.json`; the layout lists the result files under
`domain-results`. The validator reads each result and:

| Case | What the validator does |
| --- | --- |
| an input changed or is missing since the result was written (its sha256 recomputed) | blocking: the result is stale |
| the result names no input | blocking |
| the inputs do not include every file of the artifacts the gate's row names | blocking (a result over the canon alone passed while the candidate changed) |
| the result's own numbers contradict it, when the limit starts with a comparison and a number (`≤ 2 s`, `at least 1.5 x`) or is a bare zero (`0 divergent`) | blocking |
| `result: fail` | a note with the severity of the gate's row (an optional Severity column, else high); a severity below high counts only for a gate a decided owner decision covers |
| `result: tool-failure`, or a result that breaks the contract | exit 2 |
| a declared `d-*` gate with no result | pending, which no caller can accept |

Declared reach: a result whose inputs were recomputed by hand, the
candidate changed and its new sha256 written in, passes; it is the same act
as running the gate again without running it, which the validator, reading
results and never running the cell's code, cannot tell apart. The
sensitivity of a domain gate is the cell's own (mutants, a reference with
a known defect), and the coverage of `p-sensitivity` leaves domain gates
out. Chapter 21 shows how a cell writes one.

## The false greens

`06-gate-semantics.md` keeps a failure-mode analysis of the validator's
gates for the one failure mode that matters to a verdict: the **false
green**, a defect the gate lets through with a pass. For each gate it names
the cause, what detects it today, the probe that first found it and the
perturbation that covers it now. The table is reproduced in appendix D;
the summary is that most of the causes found so far came from the critical
panels that reviewed v0.4.2 and v0.5.0 and from the independent review of
v0.6.0, each probe turned into a regression test and, where it is a defect
of a document, a perturbation. The causes are the ones found so far, not an
exhaustive list; a new probe that passes a gate adds a row and a
perturbation.
