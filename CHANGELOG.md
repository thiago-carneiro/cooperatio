# Changelog

One entry per version of the method. Version is state; dates are not.

## 0.7.1

A maintenance round, not a production under the method: the record of
experiment E4, which the owner had approved and ran, and the benchmark it
leaves, executed by an orchestrator and a coder of family B, with no review.

- **Experiment E4, executed.** 39 single-shot reviews in two parts: the
  document part of the design (one guide, three seeded copies of ten
  defects each) and a code part the owner added before any seeded copy
  existed (three anonymized open-source programs, in Python, C and C++,
  twelve seeded classes each, the programs' own tests removed and the
  programs anonymized at the owner's request). 28 runs were valid and 11 were
  tool failures, all of family A, the producer's family, whose generation hit
  its output limit. By the owner's criteria, fixed before the runs: P1a and
  P1b refuted, P1c holds in both readings (with the failed runs counted as
  all escaped, 79 escapes against 67, -18 %, for +136 % added input tokens;
  with family D alone, 21 against 21, 0 %, for +135 %). P2 is not decidable
  (family A could not be measured); P3 was not computed (the confirmation
  about class 10 is not recorded). The record gains its executors, the
  execution, the results (per repetition, per part, the noise floor, the
  clean copies, the auxiliary arm, the instrument alone, the table by class,
  the agreement of the adjudicators), what it shows and does not show, the
  deviations, the cost and a provenance table of 16 files; the rest stays in
  the owner's working record. The question, the protocol and the predictions
  were not edited.
- **The claim withdrawn.** The principle's table "What would promote or
  withdraw a claim" gains a column "State after the data": the row of the
  review apparatus is withdrawn by E4, with both readings, the family row is
  open (not decidable), the portability row is open (E5 not run); a
  paragraph after the table bounds the withdrawal to what was measured. The
  living statements that presented the claim as open or likely now say it is
  withdrawn, with `[against:E4]`: the principle (sections 2, 7 in step 6,
  and 9: the costs, the baseline, the one-armed evidence, the reviews across
  families), the root README (the summary, the freeze policy, the status),
  the generic recipe ("When not to use"), the skill ("Several models") and
  the gate semantics (the mitigation of the lexical efficacy gate). The
  manual under `docs/` describes version 0.6.0, says the material wins, and
  was not edited.
- **The benchmark.** New folder `benchmark/` at the root: the clean guide,
  the three seeded guides, their defect sets as JSON and as annotated
  Markdown, the brief, canon, blind principle, blind method document of the
  prior, rubric, checklist, reviewer card, reports and prompts the reviewers
  received; for each program the anonymized pristine and seeded excerpts,
  the anonymized answer key in JSON and Markdown, the upstream license, a
  notice, the anonymization rules and the gates' detection table; the shared
  gates code (its absolute paths of the run read from the environment in the
  copy), the code rubric, checklist, reviewer card, brief and prompts; a
  README and `MANIFEST.sha256`. Every reviewer input was checked byte for
  byte against what a run received. It holds the answers and is never given
  to a reviewer. It is not in the artifact table: `p-declared` covers the
  documents of the reflexive application's folder, and the seeded copies
  hold, by design, defects the gates would report.
- **Size range.** `60-experiments.md` from 8500 to 11500 words, declared
  before writing (the record grows by experiment; it stood at 7541).
- **Open notes.** None was due at 0.7.1. This round edited the generic
  recipe for E4 only; a chained line restates `notes:8` (the recipe) as open,
  not addressed, due 0.8.0.
- **The owner's ledger.** Nothing appended: the two decisions about E4, the
  thresholds and the budget, were decided in 0.7.0 and did not change.
- **Migration note.** No cell has to change a file. A cell that adopted the
  review apparatus expecting it to find more than a careful review reads the
  new row of the principle's table and E4: that claim is withdrawn, for one
  design at the review stage; the frozen rubric still keeps rounds
  comparable. A cell that reuses the benchmark follows its README and checks
  its manifest before any run.

## 0.7.0

A maintenance round, not a production under the method: three decisions of
the owner, executed by an orchestrator and a coder of family B, with no
review.

- **One executed instance.** The references to a prior the owner held,
  not distributed, were removed from the living documents, and its registry
  entry too. The material now has one executed instance,
  `004-adoption-guide`, and every statement of the evidence says so: one
  execution, documentary, by the owner. The principle and the root README
  keep one neutral sentence of origin. A statement that only reported a fact
  of that prior was deleted; a rule whose only support was that prior keeps
  its text with `[hypothesis]` (exact text and a generative tool, the
  ambiguous position key as a contract error, the traps of the recipe) or
  says that no recorded execution supports it (the `p-notes` and
  `m-determinism` justifications, the window of `t-recheck`, the cap of notes
  per gate in the validator). Experiments E1 and E3 keep their results and
  provenance tables, in neutral wording ("the method document of a prior
  held by the owner, not distributed"); no result was altered.
- **The canon.** The recorded-fact rows of that prior and its section
  commitments are gone; commitments for the four cited sections of
  `004-adoption-guide` replace them, so the mechanism and its perturbation
  stay measured. One trigger left the list (it named only that prior);
  the other triggers stay, to catch a statement written again, and
  the frozen rubric still uses them. Sections bumped: Method terms v7, Fixed
  lists v8, Recorded facts v7.
- **The instrument, by the owner's decision.** The freeze of the README is
  lifted for this round for data and comments only: `perturbation_set.py`
  (seven perturbations that aimed at that prior now aim at
  `004-adoption-guide`, still 65 in all, every assigned gate covered,
  54 of 182 pairs, 29 %) and the comments and docstrings of `validator.py` and
  `sensitivity.py` that named it. No reading of a gate changed; every generic
  capability stays (the reserved locator, `--synthetic-prior`, the
  attestation, `heading_style`). The tests that do not depend on the real
  corpus keep their fixtures.
- **The runbook.** A clone now verifies every number stated about a prior;
  the clone run and the owner's run are one command, and `--allow-pending`
  accepts `p-anonymity` only, for this corpus.
- **Experiment E4, before any run.** The owner replaced the thresholds of
  the row of the review apparatus in the principle's table: promoted when,
  pooled over families, in at least 2 of 3 repetitions, arm A lets at most
  half as many seeded defects escape as arm B and consumes at most half its
  additional input tokens; withdrawn when, pooled over families and
  repetitions, arm A consumes more additional input tokens than arm B and
  its relative reduction of escapes is smaller than its relative increase in
  those tokens; between them, inconclusive. The record of E4 has P1a, P1b and
  P1c in place of P1, with the owner's measure of tokens (the input an arm
  adds, output and reasoning apart) and the plain declaration that this
  measure is expected to make P1b fail. A critique of the protocol added the
  clean copy, the verdict of each run, the rules for the seeder and for the
  authors of the rubric and of the checklist, two auxiliary comparisons, the
  degenerate cases, and the new refutations of P2 and P3. E4 stays `designed`.
- **Open notes.** The 17 open notes whose `due` was 0.7.0 (16 of the frozen
  ledger, one of a panel) were not addressed in this round; they are
  rescheduled to 0.8.0 by appended chained lines, so the age rule still
  counts them.
- **The owner's ledger.** Three decided lines: the extract of the prior
  (nothing to publish), the thresholds, and the budget of E4.
- **Migration note.** A cell that copied the validator and registers a prior
  held by its owner changes nothing: the mechanism stays. A cell that cited
  this material's removed prior removes the citation, or registers its own
  source. The numbers it stated about that prior have no support here any
  longer. A cell's own recorded facts and section commitments keep working.

## 0.6.0

A maintenance round, not a production under the method: the corrections of
the panel of the material's own team on v0.5.0 (nine seats of one family,
diverse by discipline and access, by the owner's choice) that do not depend
on the owner, and the execution of the orchestrator's recommendations on
the decisions the panel left open, which the owner asked for. The panel
drove the instrument to exit 0 with a file of an artifact repointed, with a
mark outside its grammar, with an invented number between backticks, with
the sensitivity report deleted and accepted by name, and with a domain
regression the validator never read; each is now a regression test and,
where it is a defect of a document, a perturbation. The ids below are the
panel's (CR, IM, SUG); `state/notes-status.jsonl` records the state of each,
appended as chained lines.

The instrument:

- **CR3 — one reading of a prior mark.** One expression, `[prior:...]`,
  for every gate; an id outside the grammar `[0-9a-z-]+`, outside code
  spans, is a blocking "malformed mark" (it used to satisfy `p-prior-mark`
  and switch the number check off); the numbers of a marked unit are read
  inside code spans too; the "Recorded facts" section of the canon is
  exempt by name. Perturbations "prior mark with an uppercase id" and
  "prior number in a code span".
- **CR2 and R1 — `--allow-pending` is closed, a missing report is
  blocking.** Only `p-anonymity`, `p-prior` and `p-prior-pin` can be
  accepted by name; any other gate is exit 2; `p-sensitivity` never; an
  accepted gate with nothing pending is printed (SUG10). This closes the
  path the panel used (a clone that edits the canon and deletes the report
  got exit 0); it did not by itself make a clone unable to get back to
  green, which the independent review of this round refuted with a
  synthetic report, closed in the rework below.
- **CR1 — the map in the provenance, and its completeness.** The
  sensitivity report records `map sha256`, over the sorted pairs of gate and
  resolved path; `p-declared` reports a Markdown document of the folder no
  artifact declares and the canon does not list (new canon table
  "Documents outside the artifact table"), a file of two artifacts, a
  document of "Size ranges" no artifact declares, and each literal path that
  does not exist. Perturbations "file of an artifact repointed", "literal
  file of an artifact deleted", "sensitivity report deleted".
- **IM1 — portability.** `.gitattributes` (`* text eol=lf`); one hash
  policy for every object, the validator included (the text read as UTF-8,
  BOM dropped, LF); UTF-8 streams and children; Python 3.9 or later, exit 2
  below it.
- **CR2 — the sensitivity test.** It copies the whole material; it compares
  each perturbed report with the baseline row by row (a noisy perturbation
  fails, unless it declares by design, `also`, what else it reaches; eleven
  do); it reports coverage by (document, gate) pair, pending below a
  quarter (a hypothesis); it refuses a gate the validator does not
  implement (exit 2); a row of a prior whose document was not passed is not
  measured, by prior (S5); a name with a comma is refused (SUG6). Sixteen
  perturbations for the corrections of this round and eight for pairs no
  one reached: the first pass ended at 59, caught 59, 0 noisy, 44 of 165
  pairs; the second pass and the rework at 65, caught 65, 0 noisy, 50 of
  182 pairs (27 %). The provenance
  compares both the running validator and the one next to the report
  (IM4).
- **CR4 and recommendation 1 — domain gates as results.** A `d-<name>`
  gate is measured by the cell's code, which writes a result file in the
  contract `05-contracts/domain-result.schema.json`; the layout lists them
  under `domain-results`; the validator recomputes the sha256 of the
  inputs (stale is blocking), turns `fail` into a note, `tool-failure` into
  exit 2, and a declared gate without a result into a pending. The
  regression of the seat that instantiated a library is a test.
- **IM2, IM3, IM5, SUG5 — limits, fences, instance tables, paths.** The
  numbers of a Limit cell are compared with the applied limit; a gate with
  two rows is exit 2; one CommonMark reader of fences in every reader, and
  `<!--` is an HTML tag; a placeholder in the artifact table of an instance
  fails; the `m-determinism` row and the report header name the layout's
  report path (new layout keys `report`, `lessons`, `round-record`).
- **CR5, first half — labels.** `[experiment:<id>]` needs an executed
  experiment with a provenance table (the sha256 of its inputs and
  outputs), else it reads as `[hypothesis]` with a note; E1 and E3 have
  theirs. `[lessons]` became `[lessons:<title>]`, checked against the
  headings of the lessons; a `[hypothesis]` claim with a number or
  "every", "always", "none" is a low note. Every label of the material was
  migrated.
- **CR5 and CR6, the mechanical part — ledgers.** The round record and the
  state ledger carry `prev` from their first line of this version on (the
  sha256 of everything above it); the canon's "Chained ledgers" table
  counts the lines before the chain (10 and 48), never edited; a chained
  round line declares `kind`, the `reviewer_relation` when a reviewer is
  listed, no verdict when it is maintenance, and a `rubric_hash` equal to
  the pin when `rubric_applied` is true. Declared reach: an edit nobody
  announced, not an insider.
- **Recommendation 4 — section commitments.** The canon commits to the
  sha256 of the twelve cited sections of the owner-held document of the
  first prior; with `--case`, `p-prior` on the canon compares them; without
  it, every row of that prior says "owner-held evidence, not measured here".
- **IM13 and SUG4 — the adopter's path.** An example of the JSON canon in
  the templates and the skill; canon links in the templates of the brief
  and the sources; one note ledger in the cell (`open-notes.json`; the
  empty `state/notes.jsonl` is gone); a summary line on stderr with
  `--output`; requirements declared; `python3` in the commands; `--out .`
  and a target with a line break refused with exit 2.
- **IM14 — panel ids out of the code and the adopter's path.** Comments and
  docstrings name the defect and the version; the skill and the READMEs
  carry no panel id. This changelog keeps them, as history.

The text:

- **CR6, CR7, IM10 — errata and positioning.** The root README, the
  skill and the principle open with the status; the
  instances of car, text and HPC are designed sketches, not executed; "two
  executed instances, one auditable"; "pinned by sha256" replaced by what a
  clone verifies and what rests on the owner; the guide of 004 leaves the
  adopter's path. The principle: independence across families as a
  recommendation with its cost; the pilot of E3 as the shown part; a table
  "What would promote or withdraw a claim"; the formula called a scheme;
  the frequency and the universal quantifiers out of the founding phrases
  (SUG1); "produced by the method" for round 1 only. The brief: the
  maintenance rounds and their protocol. The skill: the entry sentence names
  the limit of the instrument, and one block on several models, the
  principle's (SUG17).
- **CR7 and recommendation 7 — the cell of 004.** `ERRATA.md` beside the
  guide (three statements false now, and the sentence true now); the cell's
  copy of the validator refuses to run without `--historical`, the only
  change to the cell since it was distributed (the pin covers the method
  document, which did not change).
- **IM7 and recommendation 6 — experiments.** E3 reads as a pilot; E4, a
  seeded-escape design (two arms, two families, ten defect classes one of
  them outside the rubric, three repetitions, the same harness, provenance
  per run, refutation bands under half the space), and E5, an execution
  outside the documentary domain by a third party, designed.

The second pass of the round, on the owner's request to execute every
correction, closes the findings the first pass left open:

- **IM6 — golden rule 4, mechanical.** The rule now reads "becomes a gate,
  or a recorded decision not to make one"; a line of the state ledger marks
  an escaped regression (`escaped`) and closes it with its `gate` or a
  `no_gate` reason, and `p-notes` refuses one closed with neither. Six
  findings of the panel are recorded so.
- **IM8 — commands and versions.** The recompilation by hash is declared
  never exercised (README, principle). A record's `command` is resolved
  against the paths it names (never run), under `p-references`; paths and
  commands take `{version}` from the layout's `version-label`; `closed_in`
  takes the cell's label.
- **IM9 and SUG16 — costs.** Tokens per call, and a wall time only beside
  the throughput of the same run (principle, recipe); the round record takes
  optional tokens, calls and the end of the last call per role, and the
  round's wall time, crew, notes and rounds to the stop.
- **IM11 — the age of a note and the owner's decisions.** An open note
  older than 3 rounds (a hypothesis) and not scheduled (`due`) is a low
  note; the 16 open notes of round 1 are scheduled. The owner's decisions
  are a chained ledger, `state/owner-decisions.jsonl`, with a contract,
  holding the eight decisions the recommendations left to the owner.
- **IM12 — anonymity.** Months in Portuguese and Spanish, dates year first
  with slashes, UNC paths, e-mail addresses, host names under a private
  suffix; a `#!` line 1 and the canon's "Accepted paths" as the valve of a
  declared false positive; forbidden entries as `sha256:<hex>`.
- **IM14 — vocabulary.** Canon entries for unit, family, dispatch, wave,
  teamwork and runner; the role that runs the validator is the runner
  (`03-roles/runner.md`, the owner of the validation reports, in the corpus
  and the three instances), the instrument keeps the name; test functions
  without panel ids.
- **IM15 — maintenance by someone else.** The checker is one class per
  family of gates over a core with one interface, the methods moved
  unchanged (the corpus report byte-identical before and after); the
  perturbation set is a module of its own, `perturbation_set.py`, so the
  validator no longer imports the sensitivity script; `--synthetic-prior`
  regenerates a full sensitivity report in a clone, with a document built
  from the canon's recorded facts and pinned in the copies only, and says
  so. The self-test stays embedded (the runbook and the cells use it
  without pytest). The two perturbations that named the owner's sha now
  alter the pin of `004` and the label of a section commitment.
- **IM16 — the stop.** Non-negotiables with ids in the brief; `affects` on a
  tracked note; an open high or blocking note that affects one is blocking
  unless a decided owner decision covers it; evidence that names a file of
  the material has to exist (the frozen ledger exempt by design).
- **The suggestions.** SUG2 `[against:<id>]`; SUG3 the self-test count and
  the suite's sha256 in the report; SUG7 the templates and the checklist
  under the skill's gates; SUG8 an empty set exits 4; SUG9 a repeated key in
  a JSON line is a finding; SUG11 `p-size` without the pipes of a table;
  SUG12 `p-limit` declared a proxy; SUG13 the second determinism run changes
  the locale, and the protocol says what was varied by hand; SUG14 E1b, E1c
  and E3b as designs beside E4; SUG15 a table of equivalence with
  established practice in the principle; SUG17 a ten-minute path; SUG18 the
  warning on translated headings; SUG19 the base of each count; SUG20 a
  reversible hash is no pseudonym; SUG21 a failing test, a reproduction
  anchor, the producer's rubric as a gap; SUG22 the review's records and the
  history of the lessons pinned as frozen records of the canon
  (`p-frozen-rubric`), and the adopter's path separated in the README. SUG1,
  4, 5, 6 and 10 were closed in the first pass.

Recommendations adopted (the orchestrator's, on the owner's request): 1, the
validator reads domain results; 2, independence is a recommendation with
its cost, and each round line states the reviewer's relation; 3, the
maintenance rounds are outside the reflexive production, with a light
recorded protocol and no verdict; 4, two executed instances, one auditable,
and section commitments for the other; 5, internal coherence checked by the
validator, chained ledgers, and the signed tag left to the owner; 6, the
instrument freezes and the next budget measures value and portability; 7,
the cell of 004 stays a record, with errata; 8, the criteria to promote or
withdraw a claim, written before the data.

**Freeze policy.** After 0.6.0 the instrument (validator, sensitivity
test, scaffold) changes only for a failure that changes a verdict, or for a
new execution.

**Migration note.** A cell migrating to 0.6.0: lists its Markdown
documents outside the artifact list under "documents outside the artifact
list" in its canon; gives every literal path of its artifacts a file;
writes its `d-*` gates as result files and lists them under the layout key
`domain-results`; uses `[lessons:<title>]` and a provenance table for each
executed experiment it cites; freezes its rubric and passes `--notes`
(their pending can no longer be accepted); regenerates its sensitivity
report (map, specificity, pairs); copies `perturbation_set.py` beside the
two scripts; gives its non-negotiables ids and keeps its owner's decisions in
`state/owner-decisions.jsonl`; and schedules (`due`), disputes or closes the
open notes older than three rounds. The migration note of 0.5.0 lacked its
first two steps, completed here: a cell from before 0.4.0 adds
`p-efficacy-mark` to the gate map of its layout (else exit 2 "more than one
parser"), and its JSON canon declares `"version": "v1"`.

**Errata of earlier entries** (the entries are not rewritten): the
headings "Closing pass after the independent review" of 0.5.0 and "Rework
after the independent review of this round" of 0.4.0 name reviews of the
producer's family, in a separate session; read "after the review". The
sentence of the 0.5.0 README that a clone cannot get back to green without
the owner was false under 0.5.0 (a deleted report, accepted by name, gave
exit 0). Under 0.6.0 it was false again until the rework: a report
regenerated with a synthetic prior, its marking line deleted, gave exit 0
to a clone that had rewritten a verdict and re-pinned the canon. Since the
rework it reads: a clone gets back to green without the owner only by
accepting `p-sensitivity-synthetic` by name, which the report prints. The
rework said a hand edit of the recorded sha256 was detected by the owner's
regeneration; the re-review refuted that (the regeneration came out
identical to the forged report), and since the closing pass the owner's run
detects it by the attestation of the document, while a clone run does not.

**Rework after the independent review of this round** (a review of the
producer's family in a separate session, which saw the code and not the
coder's conclusions; verdict "needs work", three high, eight medium and
seven low findings, each reproduced before it was fixed and each fix a
regression test):

- **The sensitivity report records its case documents.** One line
  `case sha256: <id> <sha256>` per prior document, computed by
  `sensitivity.py`; a report without them is refused. A synthetic prior is
  told by its sha256 differing from the registry's pin, not by a line that
  declares it (the line `synthetic priors:` of the second pass could be
  deleted). A synthetic report is never a pass: pending under
  `p-sensitivity-synthetic`, accepted only by that name, without the
  owner's document; refused with it. The README's table of what a clone
  verifies and the two sentences above are corrected.
- **The synthetic prior in the real heading style.** The registry gains
  `heading_style` (a section, a subsection, a step; `### Passo {label}.`
  for 000), and the synthetic document writes each label in it, a label the
  canon cites as a step as a step: the reviewer's regression of the reader
  (the step headings left unread) passed on the old synthetic and fails on
  the new one. Declared: the synthetic does not test a format the registry
  does not describe.
- **The pin, prior by prior.** An owner-held cited prior without its
  document is pending by name; a distributed one stays blocking. The clone
  run of the runbook passes the document of 004, so its pin and numbers are
  measured (an edited document of 004, or an invented number about it, was
  exit 0 in the old clone run), and the sensitivity test with only that
  document catches the perturbation of the pin of 004 (it was a miss).
- **Accepted paths are paths.** An entry has the shape of a path or is a
  tool failure; only a path hit equal to it is dropped, nothing is blanked
  before the checks of identifiers and dates, and the canon cannot accept
  for itself.
- **Golden rule 4 and the protection of the non-negotiables.** An escape
  closes with a gate the gate table declares, or a reason of 8 words or
  more, or the name of a decided owner decision. The severity of a note is
  the highest any line or the note ledger gave it; `affects` is the union
  of every line; a decision covers while its last line is `decided`; a high
  or blocking note opened since 0.6.0 names what it affects.
- **Domain results bound to their row.** The inputs include every file of
  the artifacts of the gate's row; a result its own numbers contradict is
  blocking (a limit with a comparison, or a bare zero); a Severity column
  below high counts only for a gate a decided owner decision covers.
- **The parts of IM10, IM12 and CR5 left undone.** A table of when the
  method fits and what each gap costs, in the principle (one provider, no
  prior, a short target, no domain instrument); the months of French,
  German and Italian, the brief's "Languages:" line and the canon's "Month
  names" for any other language (pending by name without it); one-segment
  roots read when another segment follows, when common, or when the
  canon's "Machine roots" names them; `family_map_commitment`, a salted
  commitment to the map of families, required on a chained round line of
  0.6.0 or later, its form checked, its proof the owner's; a low note for a
  rubric the producer wrote and applied; a table of the false greens of the
  validator's gates in `06-gate-semantics.md`.
- **A defect the rework's own probe found.** With only the document of
  004, the perturbation of its pin made the recorded case read as
  synthetic, and the renamed row of `p-sensitivity` counted as noise; the
  specificity now leaves out the row of this gate under either name, and
  the report was regenerated a second time, byte-identical on reproduction.
- **Texts.** The canon and the gate table say that `p-prior` checks the
  section commitments (not `p-prior-pin`); the reach of the chain is "an
  edit that did not recompute it"; three chained ledgers, not two; the
  final counts of the sensitivity; the deviation from recommendation 4 (the
  notice inside the magnitude of a "pending accepted" row) declared in the
  gate semantics; the round-record line of 0.6.0 describes the three passes,
  the review and its family relation, and its commitment.

**Closing pass after the re-review** (the same reviewer, on the rework;
verdict "needs work" for three small points that change a verdict, and four
low ones):

- **The attestation of a prior document.** A `case sha256` line written by
  hand with the real pin, which the registry publishes, passed the clone
  run and the owner's run, and the owner's regeneration came out identical
  to the forged report: the detector the rework declared did not detect.
  The report now records `case attestation: <id> <sha256>` for each
  document, over its text and the provenance digests; a run with the
  document recomputes it and refuses a mismatch. Declared what remains: in
  a clone run the forged line passes, and a frozen record re-pinned in the
  canon shows only in the diff against a signed version.
- **The floor before the synthetic name.** A synthetic report below the
  floor of the pairs, or with a gate without a perturbation, became
  `p-sensitivity-synthetic`, which a caller accepts; the floor is read
  first now, and that pending is no name's to accept.
- **Golden rule 4, by name.** A decision counts when the line's `decision`
  is exactly its name (a substring and an empty name counted); the contract
  refuses an empty name; the eight words of `no_gate` are distinct words,
  declared a measure of form, not of content.
- **The low ones.** The chain does not cover the last line of a ledger and a
  domain result with hashes recomputed by hand is the same as running the
  gate again: both declared. Dates in a declared language without month
  names are pending under `p-anonymity-language`, which no caller accepts
  (accepting `p-anonymity` stands for the forbidden list only). An accepted
  path at the end of a sentence is compared without its final period.
- The round line of 0.6.0, the last of its ledger, was rewritten again to
  say so, before any line follows it.

**Round infra.** `VERSION`, the version citations bumped to 0.6.0; the
scripts changed first, then the canon, the gate section and the artifact
table the provenance pins, then the sensitivity report, then the other
documents; a round-record line added (the eleventh, the first chained,
`kind` maintenance, no review yet); the lessons appended. Still open, and
recorded as open: the anchor outside the tree (a signed tag, the owner's),
and, after the second pass and the rework, CR5 only for that anchor.

## 0.5.0

The corrections of the critical panel that reviewed v0.4.2 that do not
depend on the owner, and the preparation of the material for distribution.
The panel drove the instrument to exit 0 with the gate table deleted, with
an invented number under a mark between backticks, with placeholder cards
and with the canon's lists empty; each of these is now a regression test and
a perturbation. The owner's decisions the panel raised stay open, and each
one is now declared where the material was silent or contradicted itself.
The ids below are the panel's (CR, IM, SUG); `state/notes-status.jsonl`
records the state of each.

Priority 1, false greens of the instrument:

- **CR1 — the sensitivity report pins what defines the gates.** Its header
  records the sha256 of the gate section of the gates file (the "Gates"
  section; a cell's whole gates file) and of the canon, besides the
  validator's; the validator recomputes them and a mismatch is blocking. Its
  table has to add up: one row per perturbation, as many caught rows as its
  "Caught" line says (a header and one line used to pass). The artifact
  table is now the one source of the map from gate to artifact (IM16): the
  validator runs each gate on the documents its Gates column assigns, and
  `p-references`, on the gates file, reports a gate assigned with no row in
  the gate table ("gate `<id>` declared for `<artifact>` has no row in the
  gates table") or a row naming other artifacts. The corpus tables were
  reconciled first: `p-efficacy-mark` joined the Gates column of the brief,
  the recipe and the three instances, and `p-declared` that of the
  artifacts. New perturbation "gate row deleted".
- **CR2 — a mark in a code span is no mark.** `p-prior-mark` reads the
  trigger and the mark outside code spans and fenced blocks, as `p-prior`
  reads the mark: an invented number under a mark between backticks used to
  pass both. A trigger in a code span is notation, as the canon says (it
  used to fail, the panel's probe P27); `p-efficacy-mark` reads its labels
  the same way.
  One unit of the recipe that relied on the old reading was reworded. New
  perturbation "prior mark inside a code span", with a number altered.
- **CR3 — the scaffold has no vacuous green.** A gate whose object is a list
  of the canon (`p-terms`, `p-table`, `p-sections`, `p-card`, `p-limit`,
  `p-components`, `p-prior-mark`) is pending with the reason when the list
  is empty, never a pass of 0 of 0; `p-limit` with no origin labels used to
  fail every row (a false red). A placeholder (`<...>`, TBD, TODO) outside
  code fails `p-card`, `p-limit`, `p-table` and, in an artifact record,
  `p-references`. The card of `references/templates.md` is in bold fields,
  the form `p-card` reads and the scaffold writes; filled, it passes (it
  used to fail with seven notes). The "Size ranges" table of the scaffold
  has a separator of three columns (SUG11). `sensitivity.py` takes
  `--layout` and reads a cell's perturbations from a data file named by the
  layout key `perturbations` (a JSON list of the fields of a perturbation;
  the corpus keeps its set in the script); the scaffold copies
  `sensitivity.py`, writes a minimal `08-validator/perturbations.json` of
  three generic defects and names it in the layout. Checked by test: a
  scaffolded cell filled with the minimum runs its own sensitivity test
  (3 of 3) and `p-sensitivity` measures it. New perturbations "placeholder
  in a card field", "placeholder in a gate row" and "canon list emptied",
  the last expecting a pending (a perturbation may now expect `pending`).
- **IM15 — exit 0 means every gate was measured.** A pending gate the call
  did not accept exits 4, distinct from 1 (a note) and 2 (a tool failure);
  `--allow-pending <gate>[,<gate>]` accepts gates by name, and the report
  prints which were accepted and which were not. The corpus runs with
  `--allow-pending p-anonymity`, since it has no forbidden list. An empty
  `--forbidden` list leaves the identifier half pending (it used to pass).
- **IM17 — a tool failure is always exit 2.** The import of the sensitivity
  script is guarded (a validator copied without it left with a traceback
  and exit 1); a truncated table row is malformed input naming the row; an
  unexpected exception exits 2 with its type; the report is written inside
  the guard. Found in this round by a test: the canon's own avoid table was
  exempt from `p-terms` only when another level-2 section followed it; now
  also when it is the last one.

Priority 2, contradictions that do not depend on the owner:

- **IM1 — the method document of `004` says one thing about its reviewer.**
  Its section 8 said "revisão independente de outra família", against its
  sections 3 and 4.5; it now says the review came from the same model by
  another route. The document is re-pinned: its sha256 went from
  `ca308dec…6e10` to `2cf08aeb…0ed4` in `instances/registry.json`. By golden
  rule 4 it counts as a regression that escaped every gate: no gate reads
  claims that are not numbers, and none is added for it in this round.
- **IM2 — the truncated run of E1 is a tool failure.** By the rule E1
  itself adopted, the run that ended for length gives no verdict:
  `60-experiments.md` marks it so in the matrix, P3 is confirmed on the two
  valid controls, and the repetition no longer reads as a change of
  verdict — the stability of the verdict was not measured. The skill
  mirrors it; the lessons withdraw the reading of v0.4.0 in their new
  entry; the earlier entries and the round record are not rewritten.
- **IM3 — the effect of E3 belongs to the apparatus removed as a block.**
  The principle (step 6 of its recipe), the skill, the lessons and E3 say
  that the review apparatus, removed together (the rubric with its severity
  table and verdict rule, the card, the gates file and the framing of the
  dispatch), turned the finding into a verdict; the share of the severity
  table and the mechanical rule is a hypothesis. The change of framing of
  the dispatch prompt, checked against the prompts of the runs, is declared
  as a deviation of E3.
- **IM5 — a marked unit says what the prior says.** The principle's row
  "Instrument fixed at the root" dropped "notes above low were mostly
  false" and "only the real notes remained", which the prior does not say;
  it reads "10 of 12 notes were false, in the second pilot; each false rule
  was fixed at the root, with a test per case".
- **IM6 — counts of the instrument.** The gates document and the gate
  semantics say 35 perturbations (they said 25 when the set had 26), and a
  test compares the count in the semantics with the running set.
  Rectification, not rewriting: v0.4.0 closed with 23 perturbations, not
  the 22 that its "Round infra" and line 7 of the round record say.
- **IM10 — the notes carry a state.** The note contract gained the optional
  `status` (`open`, `fixed`, `disputed`, `out of scope`) and `closed_in`;
  the frozen ledger of round 1 does not change. The new
  `state/notes-status.jsonl` (artifact `notes-status`, contract
  `05-contracts/notes-status.schema.json`, layout key `notes-status`) holds
  one line per note of the ledger and per panel finding that became a
  correction; `p-notes` fails a note with no line and a closing status with
  no version. Of the 22 notes, 6 were found fixed by earlier rounds and 16
  are open; "22 open" was false.
- **IM11 — the adopter's surface is under the gates.** The root README and
  the skill are artifacts (`readme-root`, `skill`) under `p-anonymity`,
  `p-form`, `p-terms` and `p-canon-link`; both gained a link to the canon,
  and the skill a code span that no longer wraps. The skill no longer says
  that copying it alone loses nothing: the scaffold says what it could not
  copy, and the cell has no validator until one is copied in. The README
  lists the instances and the files at the root.
- **IM16 — the limits and the gate map have one source.** The minimum words
  of `p-limit` and the minimum steps of `p-recipe` are read from their rows
  of the gate table (the script kept 6 and 12 and printed 12 whatever the
  table said); a row that does not state the number leaves the gate
  pending. The map: see CR1. The `gates` field of a cell's artifact records
  is now read, the source of the map. New perturbation "limit raised in the
  gate table".
- **IM18 — more forms of `p-anonymity`.** Dates with the month's name or
  with dots, an absolute path of one segment under a common root, a file
  URL, a home folder by user name. The gate semantics keeps one statement
  about the forbidden list (this corpus has none), and the runbook is the
  command that made the published report. New perturbation "date written
  with the month's name".
- **IM21 — versioned contracts.** Every contract declares
  `contract_version` (1), and `p-contract-shape` reports a contract without
  it or of another version. The round of a note is a string, as in the
  round record; the integer of the frozen ledger stays valid as its legacy
  form. The scaffold copies the note and round contracts into the cell.
- **SUG4** — step 12 of the recipe gives the 31, 18 and 73 of the v2 round
  as the prior gives them, and says that the prior does not reconcile its
  38 validator notes of step 14 with the 18. **SUG6** — erratum: the
  abbreviation of the pin of `004` before 0.4.1 is `bad89a72…4845` (full:
  `bad89a722102be9efa71a2c8cdaea0de4801fff6677d97b5a123ae4b369d4845`); the
  entry of 0.4.1 reads `…d845`, left as written. **SUG7** — the share of
  reasoning in the output of E1 is 90 to 98 %, not about 90 %; "the
  effective limit stayed in place" is marked as an inference; the cost row
  names its log. **SUG8** — step 8 of the recipe cites the part of the
  prior's document on its first pilot, not its step 15, and states the
  causal reading as the recipe's; the justification of `m-determinism`
  cites the continuity ledger of the prior, which is what its document
  calls deterministic; the recorded fact of the 49 artifacts names the
  graph of the first pilot.

Priority 3, the doctrine of evidence on the founding claims (CR7):

- **CR7 — the lessons and the founding phrases are under the efficacy
  gate.** `99-lessons.md` is measured by `p-efficacy-mark` from the heading
  of its v0.5.0 entry on, declared in the canon's new table "Efficacy mark
  in append-only documents"; the entries above are history, exempt, and the
  file stays append-only. Five triggers joined the canon ("err less", "the
  only way", "observed in practice", "every rule below was born", "none
  was"), and the five units of the principle that used them carry
  `[hypothesis]` or `[lessons]`. The gate semantics declares the gate
  lexical: a paraphrase escapes it, and the mitigation is the independent
  review. New perturbation "claim of efficacy in the lessons".

Declarations of the owner's open decisions (nothing decided for the owner):

- **CR4** — the principle (section 6), the root README and the skill say
  that the distributed validator measures documents; a domain gate is
  "contract + agent" or the cell's own code, with no extension point in
  this version, and a domain gate in the tables exits 2 with a message that
  says so. Whether the method ships a documentary validator or a framework
  is the owner's decision.
- **CR5** — "Independence needs a different model" carries `[hypothesis]`
  in the principle, the skill and the recipe, with the datum against it
  (E1: the producer's own model in another session caught 2 of 2) and the
  note that no recorded production round met it with a frozen rubric. From
  this round on, the round record and its contract describe a reviewer by
  its relation to the producer, never as "independent" when the family is
  the same; the earlier lines keep their wording.
- **CR6** — the brief gained "Maintenance rounds after the stopping
  criterion": the rounds from v0.2 on are maintenance outside the brief,
  conducted by an orchestrator with delegated decisions, recorded here and
  in the round record; their protocol is the owner's decision. The two
  READMEs no longer say, unqualified, that the folder was produced by the
  method with one review. The principle had no such sentence.
- **IM7** — the registry gained the optional `method_version`; `004`
  declares 0.2.2. The READMEs say that no production ran under 0.4 or 0.5
  and that the cell does not run under the current validator without a
  migration (none is written).
- **IM9** — policy, from this round on: a pin and a line of the round record
  are never rewritten; a correction is a new line, an erratum here, or a
  re-pin the owner decides, recorded with both sha256. The two rewrites of
  0.4.1 keep their old values here: the pin of `004` before them is the
  full sha256 above (SUG6), and the round record before its rewrite (the
  seven lines of v0.4.0's close, which named model identifiers and are not
  reproduced) had the sha256
  `64e918dff7867ae3fce805f3ebfff77f5571a0e5858f92529b978f2409abb237`,
  re-verifiable by the owner, who keeps that copy.

Distribution:

- **The cell of `004` is part of the material.** It moved, with `mv`, to
  `instances/004-adoption-guide/`; its registry entry has the locator
  `instances/004-adoption-guide`, and the runbook passes its method document
  from there. Its content is unchanged but for the section 8 of IM1. Its
  forbidden list stayed with the owner, outside the material: it contains
  the model identifiers it forbids. This changelog's older entries keep the
  old relative path `../cooperatio-adocao` as history; no file of the cell
  carries it.
- **`.gitignore`** at the root: `__pycache__/`, `.pytest_cache/`, `*.pyc`.
- The method document of `000` stays with the owner, outside the material.

Open, declared: IM4 (no pinned copy of the predictions before the runs of
E1 and E3), IM8 (the prior of `000` verifiable only by the owner), IM12 (a
step of eligibility in the skill), IM13 and IM14 (cost fields, an execution
outside the documentary domain, E2), IM19 (no assembly engine for the
reflexive application), IM20 (the perturbations are written by the author
of the gates; declared in the gate semantics, not solved), and the
remaining suggestions. These are the owner's to schedule.

- **Size ranges.** Declared before writing: `00-brief.md` from 900 to 1200
  words (it stood at 697 and receives the section on maintenance rounds).
  No text was cut to fit a range.
- **Lesson.** `99-lessons.md` gained the entry of this round (append only):
  the control measured the easy part, again; exit 0 is not green; the
  doctrine of evidence reaches the founding claims through a closed list.
  The entry also withdraws two readings of the earlier entries (IM2, IM3).
- **Migration note.** A cell migrating to 0.5.0: gives its artifact records
  a `gates` list (the map) and keeps the gate table in step with it; fills
  the lists of its canon its gates read, or accepts their pending by name;
  removes its placeholders; writes its cards in bold fields; adds
  `contract_version` (1) to its contracts; gives each note of its ledger a
  line in `state/notes-status.jsonl`; copies `sensitivity.py`, writes its
  `perturbations.json`, names it in the layout and regenerates its
  sensitivity report, now also after a change of its gates file or canon;
  passes `--allow-pending` for what it does not measure, or expects exit 4.
- **Round infra.** `VERSION`, the version citations in the README, the
  principle and the skill bumped to 0.5.0; the validator, the sensitivity
  script and the scaffold changed first, then the canon and the gate
  section the provenance pins, then the sensitivity report (35 of 35, new
  header), then the other documents and the validation report; the
  self-test runs 169 checks; a round-record line added (the tenth), the
  executors by family, with the rectifications of earlier lines in its
  summary.
- **Closing pass after the independent review.** The review (same family
  as the producer, a separate session) gave READY with three medium and six
  low findings; this pass closed them before publication:
  - M1 — `p-sensitivity` measures coverage per gate: the gates the artifact
    table assigns (except itself and the measurements `m-*`) against the
    expected gates of the report's rows; an assigned gate without a
    perturbation is pending with the gates named, never a pass (a cell with
    one perturbation and four gates read "0 missed of 1" and passed). The
    magnitude reads "k of n gates covered, 0 missed of m" (the corpus: 20
    of 20, 35 perturbations); a regression test for each side, in a
    scaffolded cell. The validator changed and the "Gates" section with
    it, so the sensitivity report was regenerated (35 of 35) after both.
  - M2 — the runbook has a block for a clone without the owner-held
    document of `000` (no `--case`, `--allow-pending
    p-anonymity,p-prior,p-prior-pin`, exit 0; passing only `004` is
    blocking), and says the sensitivity report is regenerated only with the
    owner's document; the root README says the same, short.
  - M3 — the root README says the cell's forbidden list stayed with the
    owner and that the cell's commands passing it exit 2 in a copy.
  - B3 — the paragraph on `high` and `blocking` notes is back in the note
    section of the templates. B4 — the sentence above on the old path of
    the cell, which said the cell's files keep it, is corrected (only this
    changelog does). B5 — the runbook marks `--freeze-rubric` as only for
    a new rubric. B6 — the scaffold copies `notes-status.schema.json` into
    the cell, with a test.
  - B1 and B2 — declared in the gate semantics, not changed: the
    placeholder detector reads cards, gate rows, instantiation cells and
    artifact records, not prose; the history of the lessons above the
    exempt heading has no pin and its append-only rule is checked by hand
    (a sha256 of it in the canon was weighed and left out).
  - Size range declared before writing: `06-gate-semantics.md` from 3000 to
    3400 words. The pytest suites run 171 tests.

## 0.4.2

What 0.4.1 left declared open and the owner does not decide. Out, as the
owner's decisions: E2 in full and a second instance outside the
documentary domain.

- **No bytecode cache, at the root.** In 0.4.1 the cache was kept out by
  instructions (`-B`, then an environment variable in the runbook), because
  the validator imports the sensitivity script at run time and both scripts
  start child Python runs that inherit neither the caller's `-B` nor its
  switch. Now each script sets `sys.dont_write_bytecode` before it imports
  anything local, and every child run gets `-B` in its argument list
  (`python_command` in the validator; `validator_command` in the
  sensitivity). Checked: the validator with `--determinism` and the
  sensitivity test, both run without the variable, leave no cache. The one
  case the code cannot reach is the pytest suite (pytest imports the test
  file and the validator before any of their code runs): its command keeps
  `-B`, and `-p no:cacheprovider` keeps its own folder out. The runbook,
  the validator card and the skill dropped the variable. New tests: a copy
  of the two scripts runs `--determinism` without the variable, through the
  import, and leaves no `__pycache__`; the sensitivity's child command
  carries `-B`. The self-test checks the switch and the flag (140 checks).
- **`p-anonymity` measures the round record and the principle.** In 0.4.1
  the rule that no model identifier or machine path remains in them was
  checked by a separate sweep. Both are now assigned to the gate
  (`round-record`, `corpus`), with a new perturbation, "absolute path in
  the round record" (26 in all). The identifier half stays the forbidden
  list a cell supplies, pending in this corpus by design; a search by
  provider or route names is not a gate, and is declared as a sweep in
  `06-gate-semantics.md`. The artifact table's row of `corpus` also lists
  `p-efficacy-mark`, which it already carried in the gate table.
- **Size ranges raised, declared before writing.** The reflexive README
  from 900 to 1500 words (an index plus a runbook that grows with its
  flags; it stood at 896) and `99-lessons.md` from 2500 to 4000 (one entry
  per round; it stood at 2450). The justification of `p-size` now says that
  a range is raised before writing, never met by cutting text.
- **Lesson.** `99-lessons.md` gained the entry of this round (append only):
  a process flag does not cross into a child process; a property the
  material keeps is set where the code runs, and an instruction is only the
  fallback for what the code cannot reach.
- **Migration note.** A cell that carries a copy of the validator from
  before 0.4.2 keeps writing a bytecode cache beside it until the copy is
  replaced (the scaffold copies the current one); a cell that runs a pytest
  suite runs it with `python -B -m pytest -p no:cacheprovider`. A cell may
  add its round record and its method-level documents to `p-anonymity` the
  same way.
- **Round infra.** `VERSION`, the version citations in the README, the
  principle and the skill bumped to 0.4.2; the validator changed, so the
  sensitivity report was regenerated first (26 of 26, new sha in its
  header) and then the validation report; a round-record line added, the
  executors named by family and effort; no cache left in the corpus.

## 0.4.1

Closures of what 0.4.0 left open. Origin of every item: an owner-delegated
decision — the owner delegated the decisions on the items left open at the
close of 0.4.0, and the orchestrator of the round took them; the residual
risks of the second re-review of 0.4.0 are the source of most items.

- **One registry, with a contract by status (C16).** Executed and designed
  instances stay in one list, the single source: two files would need a
  cross-check of their own. The contract by status is now explicit and
  enforced by the validator under `p-contract-shape`: an executed entry
  carries `document`, `sha256`, `locator` (a relative path or the reserved
  string `owner-held, not distributable`) and `number_format`, none of them
  null; a designed entry keeps the four null or absent. A violation is a
  note on the registry, never exit 2. The registry schema describes the
  contract (its mini-validator applies no if/then; the rule lives in the
  code and is declared in `06-gate-semantics.md`). The entries of
  `instances/registry.json` already met it (checked; the only edit to the
  registry in this round is the re-pin of `004`, below). Tests in
  both directions; new perturbation "executed registry entry without a
  locator" (the sensitivity copies the registry for it: `needs_registry`).
- **Only the full instance id is a name.** Residual risk of the second
  re-review of 0.4.0: the bare numeric prefix of a registered id was
  excluded from the number check, so "the prior has 003 phases" passed
  unread. Now only the full id ("004-adoption-guide") names an instance; a
  bare "004" in a marked unit is a number and, without its row, fails.
  Tests: a bare "003" fails, "instance 003-designed" is not read. No unit of
  this corpus relied on the bare form.
- **The gates document is split, not raised.** It stood at 3583 of its 3600
  words. The long prose of the gate table's cells (the declared reading of
  `p-prior`, its three exceptions, its number format and its lost reach; the
  reach of `p-prior-mark` and `p-prior-pin`; the provenance of
  `p-sensitivity`; the refusal of `p-frozen-rubric`; the sub-cases of
  `p-declared`; the frozen-ledger exemption of `p-terms` and the identifier
  half of `p-anonymity`) and the subsections "Gate lifecycle" and
  "Provenance of the rubric" moved to the new
  `02-reflexive-application/06-gate-semantics.md` (artifact
  `gate-semantics`, owner verifier, range 400 to 3000). The gate table keeps
  a short magnitude, the limit, the justification and the pointer
  "semantics: `06-gate-semantics.md`". The gates document went from 3583 to
  2597 words. The "Rubric" section is byte-identical (its sha256 checked
  before and after the split). The new file has a row in the artifact
  table, a line in the index of the reflexive README, the gate columns of
  the gates document, a row in "Size ranges" and the layout key
  `gate-semantics` (a known key: a cell may name its own; no gate reads a
  table from it). The new `p-contract-shape` and `p-efficacy-mark`
  semantics of this round are declared there too.
- **The experiments record is a ledger.** It grows by experiment, like the
  lessons. Its ceiling, declared before writing E3: 6000 words (it stood at
  2971 of 3000). No split by file in this round.
- **S4 — only an executed experiment backs a claim.** An experiment is a
  level-2 heading `## E<n> — ...` whose block declares its status;
  `registered_experiments` registers only the executed ones, and a heading
  word such as "Question" or "Cost" never names an id. An
  `[experiment:<id>]` label that cites a designed (or pending) experiment is
  a finding of `p-efficacy-mark` ("cites a designed experiment as
  evidence"). New perturbation "claim backed by a designed experiment" (25
  perturbations in all).
- **S7 — more efficacy triggers.** The canon's "Efficacy triggers" gained
  "the method prevents", "the method finds", "the method catches", "the
  gates caught", "the gate caught", "the validator found" and "the review
  found". One unit of the corpus started to fire: in the experiments
  record, "that the method finds defects a reviewer without it would miss"
  (what E1 does not show, since it has no arm without the method); it got
  `[hypothesis]`. Test with the corpus canon.
- **The self-test covers the rules of 0.4.0 and 0.4.1.** Short functions
  called by the self-test, which did not grow: the recorded-fact rule,
  section references with the lookahead, the full instance id, the number
  format, the unknown layout key, the registry contract by status and the
  status of an experiment. It runs 138 checks (106 before). The declaration
  of 0.4.0 that the self-test did not cover these rules is replaced by this
  fact.
- **E3, the reviewer without the rubric — executed.** The experiments
  record carried its question, object, conditions, protocol and predictions
  before the runs (status `pending`, which the gate refuses as evidence):
  the object and the executors of E1, the inputs minus the review apparatus
  (the rubric and the reviewer card: no dimension, no severity table, no
  verdict rule), the output contract kept so the counts compare. Four runs,
  one per cell. Deviations, declared after the review of the round: the
  effective output limit was recorded for no run and the reason the
  generation ended only for X (Y has no raw record; its reports are
  complete); the runs read the copy of the principle at 0.3.1; the card
  and the gates file went with the rubric. All four predictions confirmed,
  P3 more strongly than predicted: both executors named both injected
  defects, but without the severity table classed the invented prior
  number as high, not blocking, and both perturbed runs ended in "accepted
  with conditions" — the same verdict as the controls. With the rubric (E1)
  the same findings gave `rejected`. What it shows, for two defects
  checkable against a source, one run per cell, with the card and the
  rubric removed together: the rubric was not what made the reviewer see
  the defects; its severity table and mechanical rule were what turned the
  finding into a verdict. The principle (step 6 of the principle's recipe,
  in its section 7) and the skill state it with `[experiment:E3]`. Cost of
  a run of the producer's model: about 56,000 input and 41,000 to 46,000
  output tokens, 633 and 770 s; the other family's figures are indicative
  (no raw record). The m4 of E3 was corrected after the review (X's high
  finding is the first version not going at once to the independent
  review; the stopping criterion was medium).
- **No model identifier anywhere in the material (owner's decision).** The
  round record names the executor of each role by family — a letter kept
  stable across the material, family A being that of the model that
  produced the guide of `004` — and by effort, never by model identifier; the
  map from letter to identifier stays with the owner, outside the material,
  like an owner-held prior document. Why: a product identifier is jargon
  that changes and leaks the provider, and the family is what the rule of
  independence uses. The seven earlier lines of the round record were
  rewritten that way (the only edit to earlier lines, by the same decision),
  and the cell of `004` had its round record, two cards and its method
  document rewritten likewise (an exception to "the cell is historical",
  decided by the owner). Mirrored in the principle ("The assignment is
  auditable", with its price: the letters are as good as the owner-held
  map, and the material alone cannot detect a mislabeled letter), step 5 of
  the generic recipe (the role cards, item 4), form rule 4 of the canon ("model
  identifier"), the semantics of `p-anonymity` (model identifiers belong to
  the forbidden list a cell supplies; no new code), the round-record schema
  (the `model` field), the experiments record, the README, the artifact
  table, the skill and its review checklist.
- **Correction: the review of `004` was not by another family.** Found in
  this round in the table that maps routing aliases to models: the
  alias recorded as the reviewer of the second executed instance maps to
  the producer's own model, through another route, at maximum effort. The
  review separated the session and the reasoning, not the family. The
  principle (its opening and two items in section 9), the experiments
  record (E1, the real round has the configuration of X, not of Y) and the
  skill were corrected; a consequence is declared in the principle and in
  the lessons: independence of family with a frozen rubric has not been
  exercised in any production round the round record lists, nor in that
  review; the one exception without it is the reading review of family A
  in v0.4.1, which had no frozen rubric, no verdict rule and no execution.
  The only reviews across families in the reviewer role, with a frozen
  rubric, are the runs of executor Y in E1 (E3 removed the rubric); the
  critical panels that reviewed this material (v0.1.0, v0.2.0 and v0.2.3) had seats
  of several families, but no frozen
  rubric, no verdict rule and no line in the round record (corrected after
  the review of the round, which found the first wording, "the first
  reviews across families are the runs of Y in E1 and E3", false). The
  verbatim review record of the cell (`review/round-1-notes.md`) keeps its
  original wording; the correction is in sections 3 and 4.5 of the method
  document and in the cards.
- **The method document of `004` was edited after its execution, and is
  re-pinned.** By the owner's decision above and the fact just verified,
  sections 3 and 4.5 of the cell's method document dropped the model
  identifiers and corrected the reviewer's family. Its sha256 went from
  `bad89a72…d845` to `ca308dec…6e10`; `instances/registry.json` pins the new
  one, and `p-prior-pin` passes with both priors. The numbers the corpus
  cites from it (1054 words, the range 900 to 1400, the lowest score 4)
  are unchanged and still checked in their sections.
- **Lessons.** `99-lessons.md` gained the entry of this round (append only):
  the rubric turns detection into a verdict (E3), and an alias is not a
  family, with the rule of naming executors by family and effort.
- **Not executed, still declared.** E2 (the full counterfactual) and a
  second instance outside the documentary domain: each costs whole
  productions, and the choice of target is the owner's.
- **Migration note.** A cell migrating to 0.4.1 cites an instance inside a
  marked unit by its full id: a bare "004" there is now a number and fails
  without its row (until 0.4.0 the cell's own registry entry made the bare
  prefix a name). Its priors registry gives every executed entry a
  `locator` (a relative path or the reserved string) and a `number_format`,
  and keeps the four fields null or absent on a designed entry. An
  `[experiment:<id>]` label cites an executed experiment, whose block
  declares its status. A layout may name `gate-semantics`. Its round record
  names executors by family and effort; model identifiers go to the
  forbidden list it supplies to `p-anonymity`.
- **Round infra.** `VERSION`, the version citations in the README, the
  principle and the SKILL bumped to 0.4.1; the SKILL mirrors the full
  instance id, the semantics document and the new triggers; the verifier
  card lists the new document among its outputs; a
  round-record line added; the sensitivity report regenerated (25 of 25)
  and then the validation report; `__pycache__` and `.pytest_cache` removed
  from the corpus. The second pass (E3, identifiers, the correction of the
  family, the re-pin) and the rework after the two reviews of the round
  (one per family) touched neither the validator nor the sensitivity
  script, so the sensitivity report stands and was reproduced byte for
  byte; the validation report was regenerated. The validator imports the
  sensitivity script at run time, so a run can write a bytecode cache into
  the folder: the validator card and the skill run Python with `-B`, and
  the runbook also exports `PYTHONDONTWRITEBYTECODE=1`, because the
  determinism run and the sensitivity test start further Python processes
  that `-B` alone does not reach (checked: with `-B` only, the determinism
  run left a cache; with the variable, none). The instruction for the test
  suite (export the variable before running pytest) is in step 11 of the
  skill, not in the reflexive README: the README stands at 896 of its 900
  words, so its next edit has to shorten it or declare a new ceiling
  before writing. Every step reference now names its recipe: "the
  generic recipe" (`10-generic-recipe.md`) or "the principle's recipe" (its
  section 7). The rule that no model identifier remains was checked by a
  separate sweep, not by a gate (`p-anonymity` covers neither the round
  record nor the principle; gate coverage is left to the next round). Left
  as history: the cell's own validation report (`08-validator/report.md`)
  still shows the size of its method document before the edit (2167 words;
  2215 now, inside its range), and is not regenerated.

## 0.4.0

The epistemic round (the IMPORTANT findings I1, I7-I12 and I14-I18 of the
critical panel that reviewed v0.2.3, plus the residual risk of the v0.3.1
review). The panel found that the evidence base of the method is
self-referential and that the method exempted itself from its own doctrine
of evidence. This round measures what it can (experiment E1), declares with
a label what it cannot (the counterfactual, the break-even), and closes the
instrument holes that still let a false green through.

- **I1 — every gate has a perturbation, and the canon link has to
  resolve.** Seven new perturbations, one per gate that had none:
  `p-canon-link` (the brief's link retargeted so it no longer resolves),
  `p-size` (a document pushed above its range by a padding block larger than
  any maximum), `p-sections` (a mandatory heading renamed away), `p-prior-pin`
  (the sha256 of `000` altered in a copy of the registry: the sensitivity now
  copies the registry next to the copy of the folder and passes
  `--registry`), `p-frozen-rubric` (the "Rubric" section edited in the copy;
  the sensitivity takes `--rubric-hash`), `p-notes` (an invalid severity in
  the copied ledger; the sensitivity takes `--notes`) and `p-declared` (a
  declared document deleted from the copy). Without the input its gate needs,
  a row is "not measured", never "caught". `p-canon-link` now checks that the
  target of the link resolves, relative to the folder of the document, to
  the canon file of the layout; a link that names the canon and leads
  nowhere is a finding ("link to the canon does not resolve"), which closes
  the risk the v0.3.1 review left open (the card that linked `02-canon.json`
  from inside `04-roles/`).
- **A correction to the spec of this round, by the source.** The spec asked
  the `p-sensitivity` magnitude to say "one per gate the validator
  implements, 21 of 21". The validator implements 21 gates, and the
  perturbations cover 20 of them: the 21st is `p-sensitivity` itself. It
  cannot carry a perturbation without circularity — the baseline of the
  sensitivity run reads the very report the run is regenerating — so its
  defects (a fabricated report, another validator, another set) are
  regression tests. The magnitude says so: 20 of 21 gates, 23 perturbations
  (three on `p-references`, two on `p-prior`). A test fails if any other
  gate is left without a perturbation.
- **I7 — the provenance of the rubric, declared.** The gates document says,
  above the frozen section and never inside it, that the rubric was written
  by the producing agent against step 8 of the generic recipe (lesson 4 of the
  first round), and why it stays frozen. The round record gained the
  optional field `rubric_author`; the line of this round declares
  `producer`, the historical truth. Step 8's "Done when" now asks the round
  record to name the author.
- **I8 and I9 — experiment E1, the reviewer under a known perturbation.**
  New document `02-reflexive-application/60-experiments.md` (artifact
  `experiments`, owner verifier): the guide of instance `004` reviewed with
  and without two injected defects (an invented prior number, a method term
  with its sense swapped) by the producer's own model in another session
  (X: the same model identifier, not only the same family — the protocol
  said "family", corrected in place) and by a model of another family (Y),
  one run each, with the protocol and the predictions written before
  measuring, and what the experiment cannot show declared before the
  results. Result (five runs: the four of the matrix and one re-run):
  predictions P1-P3 confirmed for both executors — in B both gave
  `rejected` with the invented number as `blocking` and the swapped term as
  `high`, and every control run was accepted or accepted with conditions;
  P4 refuted in one run of five, a generation that ended for length at an
  effective limit of 65,536 output tokens the dispatch had not declared
  (the budget it asked for was not applied by the endpoint; the re-run did
  not remove the limit, it fit under it). Side findings: the output
  contract of the reviewer did not cover how the executor's generation
  ends; and the one repetition gave five findings each time, almost all
  different, with scores and verdict that moved while the rule was applied
  right both times — the rule is stable, the scores and the findings are
  not. Deviation declared: each run received five files, not the whole
  corpus nor the rubric's pin, so only verdicts compare with the real round.
  What it does not show stays declared: no arm without the method, one run
  per cell, no difference between executors, and nothing against a second
  session of the producer's model (X caught 2 of 2, once). The numbers of
  Y are indicative (no raw record). E2, the counterfactual, is designed and
  carries no number.
- **Derived from E1: an incomplete review report is a tool failure.** The
  reviewer card and step 11 of the generic recipe now say it: the dispatch of the
  review records the effective output limit of the executor and the reason
  its generation ended; an ending for length, or a report that lacks a
  section of the format, is a tool failure that produces no verdict.
- **Found after E1, not by it: a number without a recorded fact passed
  `p-prior`.** Both perturbed runs said the cell's `p-prior` should catch
  the invented number. The review of this round checked it: the cell's
  validator, run on the perturbed copy with the prior's document, passed —
  the count had no row in the cell's "Recorded facts", so it was checked
  for presence in the whole document, and the invented number occurs there
  once, in an unrelated sentence. By golden rule 4 it is a gate: a number in
  a `[prior:<id>]` unit without a row of that prior fails; presence in the
  whole document verifies nothing any more. Two readings had to be made
  precise for the rule to hold on this corpus: a section reference
  ("section 2.1", "step 16") is checked as a section label that has to exist
  in the prior's document, not as a number; and a digit attached to a
  letter ("p95", "v1") is a name, not a count (the prior's own fix, step 9 of
  the generic recipe). The "Number" cell of "Recorded facts" is read as numbers
  ("1,200" is one token). New perturbation "prior number without a recorded
  fact" (`needs_case`; 23 in all) and regression tests. In the corpus the
  last two numbers without a row were rectified: an instance's own limit,
  in a row that also cites the prior, is now written in words (the rule
  reads every number of a marked unit), and the "4" cited about `004` got
  its row (section 4.5); the unused "6" row of `004` was replaced by it.
- **The skill's one-model fallback follows the principle.** Its "Do not let
  a model grade itself" accepted "another session with the rubric only"
  when a single model is available, which contradicts "Independence needs a
  different model" of the principle. It now says that another session of
  the producing model is not an independent review; the review comes from
  another executor, ideally of another family, and with a single model the
  rubric and the review come from outside the producing run, with the gap
  declared. The correction follows from the principle, not from E1 (it was
  noted before the results, and X's 2 of 2 is, if anything, a datum against
  it). The bullet on what E1 measured mirrors its one run per condition and
  what that cannot prove.
- **I10 — the doctrine of evidence applies to the method.** The canon gained
  an "Efficacy triggers" table ("pays off", "the method found", "would have
  caught" and six more), the four labels that back such a claim
  (`[prior:<id>]`, `[experiment:<id>]`, `[lessons]`, `[hypothesis]`) and form
  rule 8. New gate `p-efficacy-mark` on the corpus, the brief, the recipe,
  the instances, the readme and the experiments record, with its
  perturbation; an `[experiment:<id>]` label has to name a section of the
  experiments record. The existing claims were labeled, and the principle
  gained the paragraph "Evidence of efficacy is one-armed".
- **I11 — a limit never inherits a prior's number.** The recipe's "In the
  reference case" lines of step 7 of the generic recipe say that the cap, the exit code and the
  drift limit are facts about that prior, not limits for a new instance;
  step 7 gained the rule; golden rule 2 of the principle, one sentence.
  Checked and declared: no gate of `04-gates-and-rubric.md` uses 0.15 s, 50
  or 24 h as a limit of its own. One inherited number was found outside the
  gates document: the validator caps the notes it lists per gate at 50, the
  prior's cap. It truncates the listing (with an "omitted" note) and never
  decides a pass or a fail; it is left unchanged, and its comment now
  carries its own origin label: `[hypothesis]`, with the prior's cap cited
  as support.
- **I12 — an unknown layout key is exit 2.** A top-level key outside
  `version`, `artifacts`, `gates`, `registry`, or an artifact key outside the
  ones the validator reads (`canon`, `artifacts`, `gates-and-rubric`,
  `roles-dir`, `sensitivity`, `experiments`, `rubric`), is refused, naming the
  unknown key and the known ones. The scaffold emits known keys only (test).
- **I14 — `--case` is repeatable.** Each document passed is identified by
  its sha256 against the registry. A `[prior:<id>]` unit is checked in the
  document of `<id>`, with the "Recorded facts" rows of `<id>` (a row belongs
  to the prior its mark names); a unit that cites several priors is checked
  in the document of each of them (corrected after the review: it used to
  pass when one present document verified it, which checked a prior with no
  document against another prior's document); a cited prior with no
  document passed is pending by name; a cited executed prior whose pin
  matches no document passed is blocking (the note says whether a document
  passed pins nothing — wrong or edited — or the prior's document was
  simply not passed), and so is a document passed that pins no executed
  instance. The final run passes both executed priors, and the statements
  about `004` in the principle and the experiments record carry
  `[prior:004-adoption-guide]` with numbers checked in its method document
  (three new rows in "Recorded facts").
- **I15 — invalid UTF-8 is exit 2.** A document that does not decode is a
  tool failure naming the file and the byte, never a finding.
- **I16 — the number format is declared.** The registry schema gained
  `number_format` (`point-decimal` or `comma-decimal`, null only while
  designed); an executed entry without it is a `p-contract-shape`
  violation; `000` and `004` declare `comma-decimal`. A token of a prior's
  document has one reading in that format, or its literal only when it does
  not parse there, so "1.2" here no longer matches a pt-BR "1.200"; values
  and literals live in separate spaces (corrected after the review: the
  value 1.2 of a document's "1.200" used to meet the literal "1.2" of a
  section number in a comma-decimal prior). A
  token of these documents is read point-decimal (form rule 1); a cell that
  writes its own documents in comma-decimal would be misread — declared, not
  solved in this round.
- **I17 — the cost, measured where it can be.** The principle and the
  recipe state the one cost measured, a review run of E1 (`[experiment:E1]`):
  about 58,000 input tokens (most of them the prior's method document, not
  the guide under review), 55,000 to 66,000 output tokens (about 90 %
  reasoning) and 8 to 10 minutes for one executor, about 4 minutes of wall
  time for one of another family (indicative: tokens not separable, no raw
  record there); the
  cost of a production round and of the instruments was not measured. They
  state the break-even only as a labeled hypothesis:
  the probability of an error times its cost against the cost per round
  times the rounds until the stop, with the baseline (a strong model, a
  checklist and continuous integration) as the unmeasured control arm of E2.
- **I18 — the gate lifecycle.** The gates document gained "Gate lifecycle":
  a gate is born from a regression with its perturbation, lives while its
  object exists, and is retired deliberately, with its perturbation, the
  reason and the rounds it stayed silent recorded here as "retired gate:
  `<id>`". Golden rule 4 of the principle, one clause. No gate was retired in
  this round.
- **Size ranges.** Declared before writing: `99-lessons.md` from 1500 to
  2500 words (it stood at 1450 and receives this round's entry);
  `60-experiments.md`, 400 to 3000. Raised when this round's additions
  crossed the old ceiling of 3000: `01-canon.md` to 3600 (3250 with the
  efficacy tables, two terms, rule 8 and three recorded facts) and
  `04-gates-and-rubric.md` to 3600 (3367 with the new gate, the declared
  semantics, the lifecycle and the rubric provenance).
- **Registry.** `instances/registry.json` changed in this round (the
  `number_format` of `000` and `004`), declared as the spec required.
- **Migration note.** A cell from before 0.4.0 needs, on migration: the gate
  `p-efficacy-mark` in its layout's gate map (otherwise the merged map names
  two parsers, exit 2; the error now names the gates the map lacks),
  `number_format` on its executed priors, a row in the "recorded facts" of
  its JSON canon for every number it states about a prior — one object per
  number with the fields `number`, `context` (carrying the `[prior:<id>]`
  mark that names the prior) and `section` (without
  the row, `p-prior` fails under this validator; until the second rework
  the JSON canon had to keep that list empty, which made this step
  impossible) — with its canon contract accepting that form (the scaffold's
  does), its own entry in its priors registry (step 14 of the generic recipe; that
  is also what makes the token of its own id, such as "004", read as a
  name), card links whose target resolves, and a regenerated sensitivity
  report. Its JSON canon may add "efficacy triggers" (optional: a canon
  without it loads with the list empty, and `p-efficacy-mark` is then
  pending, not a pass). Checked on a copy of the cell of `004`, migrated by
  hand: with its two rows (18 in section 1.1, 49 in section 2.1 of the first
  prior's document) and its own registry entry, `p-prior` passes on its
  guide and its method document; with the guide's count changed to 21, it
  fails ("'21' has no row"); without its own registry entry it fails on
  the token "004". The cell of instance `004` is historical and was not
  touched.
- **Second rework after the review.** A JSON canon carries real recorded
  facts (the objects above; a malformed item is exit 2 with the accepted
  form); the reason the list had to be empty ("facts about a prior live in
  the method's own corpus") was replaced by the rule that holds: a cell
  records the numbers it itself states about priors. A token equal to the
  numeric prefix of a registered id is an instance identifier, not a
  number about the prior. A section reference continues past "and", "or"
  or a comma only before punctuation, the end, a connector or "of" (in
  "section 1.4 and 7 rounds" the 7 had been read as a section and never
  checked). The self-test of the validator gained cases for the rules of
  this round in 0.4.1 (see there).
- **Rework after the independent review of this round.** Besides the items
  marked above (the recorded-fact rule, the per-prior check of a
  multi-prior unit, values apart from literals, the reviewer's output
  limit, the facts of E1 corrected against its raw outputs): the gate
  lifecycle no longer claims that a silent retirement cannot pass unseen —
  removing one of a gate and its perturbation is detected, removing both
  and regenerating the report is not, and only the declaration here records
  it; `p-efficacy-mark` with an empty trigger list is pending; the pin note
  tells a missing document from a wrong one; the exit 2 of an old cell
  layout names the gate it lacks. Declared open: `registered_experiments`
  accepts the first word of any heading of the experiments record as an
  id, and a designed experiment as well as an executed one; and the
  efficacy triggers are the closed list the spec fixed ("prevents",
  "catches" or "finds" outside it are not read).
- **Round infra.** `VERSION`, the version citations in the README, the
  principle and the SKILL bumped to 0.4.0; the SKILL mirrors the repeatable
  `--case`, the sensitivity flags, the layout keys, the `number_format` of
  the registry and what E1 measures and does not; a round-record line added;
  the sensitivity report regenerated (22 of 22) and then the validation
  report; `__pycache__` and `.pytest_cache` removed from the corpus.

## 0.3.1

Cheap closures (5 SUGGESTIONs of the v0.3.0 review plus the IMPORTANTE
I2-I6 of the critical panel). Nothing here changes a verdict; it removes
silences and declares semantics the instrument already had.

- **S1 — the provenance note is proactive.** The runbook and the verifier's
  card now say it before the failure, not only in the blocking message:
  editing `80-validator/validator.py` changes the sha its sensitivity
  report records — regenerate `80-validator/sensitivity.md` (and then the
  report) before the next run, or `p-sensitivity` fails on provenance.
- **S2 — the refusal is in the gate's own description.** The
  `p-frozen-rubric` magnitude in the gates document now carries the
  clause: the freeze refuses an existing pin; a replacement is deliberate,
  via `--re-freeze-rubric`, with the reason recorded here.
- **S3 — two silences closed.** `--freeze-rubric` and `--re-freeze-rubric`
  passed together now exit 2 ("mutually exclusive") instead of silently
  ignoring the second flag; and an artifact declared with no paths at all
  (a JSON record with `paths: []`, or a table row with no backticked file)
  is a visible pending of `p-declared` ("declared without paths; no files
  to measure"), never a silent skip.
- **S4 — the old `p-determinism` name is gone from the cards.** The
  verifier's and validator's cards now say `m-determinism`, the name the
  report has used since the determinism check became a measurement of the
  instrument, not a gate on a document.
- **S5 — the locator convention, stated directly.** The registry schema
  describes the field in one breath: a path relative to the root of this
  material (the directory that contains `instances/`, so a sibling cell is
  `../sibling-cell`, no leading slash), or the string "owner-held, not
  distributable".
- **I2 — the semantics of `p-prior`, declared.** The gate's magnitude now
  says it: the number check verifies the presence of the number's tokens
  in the cited sections, not the equality of the claim around it; and the
  canon's "Recorded facts" table is exempt (its cells are code spans,
  removed before the check). A declared limitation, not new semantics.
- **I3 — the reach of `p-prior-mark` and `p-prior-pin`, declared.** The
  trigger covers statements about the content of registered priors;
  statements about the registry itself are data, under `p-contract-shape`.
  The pin takes a single `--case` document — one prior per run (the
  limitation behind the multi-prior gap, declared open).
- **I4 — `p-notes` without `--notes` stays visible.** A run without the
  notes ledger emits a pending row with its reason ("notes not supplied;
  the note ledger was not measured"); the gate no longer disappears.
- **I5 — the validator refuses a canon of a different schema version.**
  The recipe's requirement, implemented: the canon declares its schema
  version (`v1`) — the markdown corpus canon in a "Canon schema" row of
  its Sections table, a JSON canon in the top-level `version` field — and
  the validator refuses a different (or missing) one with exit 2. The
  scaffold emits the field, the canon contract requires it, and the cell's
  own canon passes its own contract. Cells from before this round would
  need the field added on migration, like the sensitivity header of
  0.3.0.
- **I6 — the scaffold ships no traps.** The gates template no longer
  carries the `g-<name>` placeholder row (a filled cell would exit 2 on
  "no implementation" on its first real run); the template's schema cell
  is `null` (the placeholder string it carried never matched the
  validator's `.schema.json` detection); and the role card references the
  canon as a link, the form `p-canon-link` reads.
- **Rework after the review (one IMPORTANT, two SUGGESTIONs).** The link the
  scaffold wrote in the role card pointed at `02-canon.json` from inside
  `04-roles/`, a target that does not exist there; the card now links
  `../02-canon.json` (the template follows), and the scaffold test asserts
  that the target resolves to the cell's canon, not only that a link is
  present — `p-canon-link` counts links by name and does not check that
  they resolve, a gap that stays declared open. The `p-declared` magnitude
  names its paths-empty pending case, and the runbook's list of pendings
  names `--notes` beside `--case` and `--forbidden`.
- **Round infra.** `VERSION` and the citations in the README, the principle
  and the SKILL bumped to 0.3.1; a round-record line added; the validation
  report regenerated (the validator did not change in the rework, so the
  sensitivity report and its provenance sha stand); `__pycache__` and
  `.pytest_cache` removed from the corpus.

## 0.3.0

The instrument verifies itself (fixes C1-C7 of the critical panel that
reviewed v0.2.3; its probes became regression tests). The theme the panel
found: four criticals were one family — the instrument trusted signals it
never re-verified (a file present, a line present, a declared path, a
re-recordable hash).

- **The freeze refuses an existing pin (C1).** `--freeze-rubric` exits 2 with
  "the rubric is already frozen at the named path" when the pin file already
  holds a sha256; a deliberate replacement goes through the new
  `--re-freeze-rubric FILE`, with the reason recorded here. The placeholder a
  scaffolded cell ships ("not-frozen") is an explicit absence, not a pin: the
  first real freeze replaces it. The runbook and the SKILL's rubric step
  document both.
- **A declared artifact that does not exist is blocking (C2).** New gate
  `p-declared`: an artifact declared in the table whose files match nothing
  on disk is a blocking note naming the path ("declared artifact missing"
  plus the path itself); an artifact marked `proposed` (the JSON cell
  format) is pending with "proposed, not yet produced" — never silence,
  never a pass. Removing a declared document now fails the run instead of
  quietly unmeasuring it.
- **The sensitivity report carries provenance (C3).** `sensitivity.py` writes
  a header with the sha256 of the validator that ran it and the ids and
  count of the perturbation set; `p-sensitivity` verifies the header, the
  sha against the `validator.py` next to the report, the ids and count
  against the running instrument, and that "Caught X of Y" has Y equal to
  the perturbation count. A report this instrument cannot have produced is
  blocking. **Migration note:** historical cells (instance 004) hold reports
  without the header; re-running the new validator against them fails
  `p-sensitivity` by design — the cell re-runs `sensitivity.py` to migrate.
  The cell 004 itself is historical and was not touched.
- **A production with no documents is not green (C4a).** A run that measures
  zero documents is a blocking note; a freshly scaffolded cell (empty
  template artifacts) now fails high instead of exiting 0 with three
  pendings. The scaffold's integration test asserts the new contract.
- **The freeze and the rubric resolve through the layout (C4b).** New
  layout key `artifacts.rubric` (a cell: `07-rubric.md`; this corpus: absent,
  falling back to the "## Rubric" section of the gates file — behavior
  unchanged). `--freeze-rubric`, `--re-freeze-rubric` and `--rubric-hash`
  resolve the rubric through it, so a cell freezes its own rubric; the
  scaffold emits the key and the SKILL's step 10 tells the cell owner how.
- **The registry is distributed and covered (C5).** The locator of
  `004-adoption-guide` is now relative to the root of this material
  (`../cooperatio-adocao`), the schema documents the convention (no leading
  slash), and `p-anonymity` measures `instances/registry.json` — a
  machine-local locator is a note. The identifier half of `p-anonymity` is
  supplied per cell (its own `--forbidden` list); in this corpus it is
  pending by design (no list), now declared in the gates document.
- **The scope of the evidence is declared (C6/C7).** The README and the
  principle now say it outright: both executed instances are documentary
  productions by the same owner of this material (`000` an audiovisual
  production method, owner-held; `004` this method's own adoption guide);
  the inter-domain instances (car, text, HPC) remain designed.
- **Correction of a 0.2.2 record.** The 0.2.2 deferral note named
  contract-shape among the sensitivity gaps; contract-shape has had a
  perturbation since 0.2.1 ("schema cell points to a missing file"). The
  real gaps then (and still now) are the pin gate, the notes ledger, and
  perturbation coverage for `p-canon-link`, `p-size` and `p-sections`: no
  perturbation injects a wrong sha256 into the registry (`p-prior-pin`),
  and none exercises `p-notes` (both open).
- **Regression tests.** The panel's probes are tests: missing declared
  document (blocking), freeze refusal and deliberate re-freeze, fabricated
  sensitivity report (no header, alien sha, alien set, wrong count), empty
  production (blocking), scaffolded cell freezing its own rubric through
  the layout, registry anonymity (absolute locator caught, relative passes).

## 0.2.3

The sensitivity report path resolves through the layout — closing the open
item the first real execution of v0.2 found (instance `004-adoption-guide`,
medium finding: `p-sensitivity` stayed pending in a cell because the path
was hardcoded to the corpus convention).

- **The defect.** The validator read the sensitivity report from
  `SENSITIVITY_FILE`, a constant derived from the validator's own folder,
  ignoring `--layout`. In the corpus the path resolves
  (`80-validator/sensitivity.md`); in every scaffolded cell, which keeps
  the instrument under `08-validator/`, the gate was pending — measuring
  nothing, with no reason named.
- **The fix.** The path now resolves through the same central point as
  canon, artifacts, gates, rubric and registry: `DEFAULT_LAYOUT` gained the
  key `artifacts.sensitivity` (default `80-validator/sensitivity.md`,
  folder-relative; corpus behavior unchanged). A cell without the key
  inherits the default and, when no report is there, the gate is pending
  with the path it looked for and the layout key that points there — never
  a crash, never a silent pass. `sensitivity.py` writes its default output
  folder-relative too (the report lands next to what it measures, not in
  the caller's working directory).
- **The scaffold names the cell's report.** The `layout.json` of a new cell
  points `artifacts.sensitivity` at `08-validator/sensitivity.md`, and the
  SKILL's validator step says to write the report there.
- **Rework after the v0.2.3 review (same version).** The folder-relative
  write default of `sensitivity.py` gained a regression test driven through
  `main()` (the report must land at the folder's
  `80-validator/sensitivity.md` when `--output` is absent — the default
  used to be working-directory relative), and the report write moved inside the module's error handling:
  an `OSError` on the write is now a tool failure (exit 2), not a
  traceback with exit 1 ("missed"). The `resolve_output` docstring no
  longer claims the write default follows the layout — a cell whose
  `artifacts.sensitivity` sits elsewhere passes `--output` to match it.
- **Verification.** Regression tests (layout-declared path honored; pending
  reason; missing "Caught" line is a tool failure; folder-relative write
  default) and a scaffold test for the emitted key; the instance-004 cell
  itself was not touched — a probe with a copy of its layout plus the new
  key shows `p-sensitivity` measured and passing against its stored
  10-of-10 report.

## 0.2.2

Closing the cheap residues the v0.2.1 review left open (three suggestions,
the round-record line of the SKILL, and two panel items deferred in v0.2.1:
C13 and C14).

- **Prior mentions marked (S1).** `00-brief.md`, the root `README.md` and
  the reflexive `README.md` now mark their mentions of the executed prior
  with `[prior:000-av-production]`; the `p-prior` justification of the
  gates file says "the registered prior" instead of the trigger phrase.
  The rework of this entry also declares two things the round itself
  left unrecorded. First, the freeze incident: the first edit of the
  gates file landed inside the frozen "Rubric" section, `p-frozen-rubric`
  blocked the first run (exit 1), the edit was reverted byte for byte
  against the pre-round backup, and the frozen phrase is now covered by
  the declared exemption (history, like the review ledger). Second, the
  `p-frozen-rubric` row was inadvertently carried into the new
  "Measurements" table when the determinism row left the gates table; the
  review returned it to the gates table (it applies to corpus artifacts
  and can fail a document — it did, in the incident above), leaving
  `m-determinism` as the only measurement.
- **Tilde path gone (S4).** The root README's install instruction names the
  `skills/cooperatio-teamwork/` folder instead of a `~`-prefixed path; no
  tilde path remains in the corpus.
- **Open note 5 closed.** The 0.15 s drift limit and the 24 h recheck
  window entered the "Recorded facts" table with their sections in the
  prior's method document (sections 1.10 and 13 for 0.15 s; sections 2.4,
  6 and 4.5 for 24 h), so both are now verified in the cited sections
  instead of globally — closes open note 5, opened in the round-1 replies
  (the frozen `90-review/replies.md` is history and stays as it was).
- **SKILL round-record line prescribed.** The round record of a cell now
  prescribes the method version and, when a rubric is frozen, the frozen
  rubric hash, per `05-contracts/round-record.schema.json`.
- **Determinism is a measurement (C13, second panel).** `m-determinism`
  measures the instrument itself (two runs, same input, same report) and
  has its own section in the report and its own table in the gates file;
  it is no longer presented as a corpus gate. The two tables and the
  READMEs were aligned; the validator's global-gate set no longer carries
  it.
- **Atomic scaffold (C14, second panel).** The cell is built in a staging
  folder sibling of the destination and renamed into place in one step; a
  failure in the middle leaves no partial cell and no staging folder. The
  OSError → exit 2 contract is unchanged; an existing non-empty destination
  is still refused, an empty one is replaced whole.

Deferred (owner decisions recorded for the next rounds): the sensitivity
gap (no perturbations for the pin and contract-shape gates — a design task
of its own); the executed/designed mix in the registry (C16); the execution
of the first v0.2 instance — the material keeps declaring "working
hypothesis — one executed instance".

Post-release update (no version bump — the method did not change):

- **Instance 004 registered.** The first real execution of the v0.2 method
  (an adoption guide for the method itself, produced in a cell that
  followed the generic recipe end to end) is registered as
  `004-adoption-guide`: status executed, method document pinned by sha256,
  locator in the registry. The README, the principle and the SKILL now
  count two executed instances instead of one.
- **Corpus defect found by that execution (open item).** The validator
  resolves the sensitivity report through a constant derived from its own
  folder (`SENSITIVITY_FILE` → `80-validator/sensitivity.md`), which
  ignores `--layout`: in a cell that keeps the instrument under
  `08-validator/`, `p-sensitivity` stays pending — the gate measures
  nothing because it looks for the file at the corpus path. The fix
  belongs to the corpus owner: derive the path from the layout. The
  corpus run is unaffected (the default folder is the correct one here).

## 0.2.1

Executable core delivered, verifiable pin, real contracts and a license,
applying the seven recommendations of the second critical panel. This entry
also declares what the v0.2.0 entry left undeclared (see "History declared
late" below).

- **Executable core delivered.** The validator has a parser registry
  (`builtin-markdown`, `builtin-json-canon`; an unknown parser is rejected
  with the list of the available ones) and one-point path resolution through
  the layout: `--layout` is an overlay on the default, every artifact path
  and the registry come from the layout, and the registry default is
  `../instances/registry.json` relative to the folder, resolving the same
  file as before. The scaffold emits a self-contained cell: `layout.json`,
  role cards in bold fields, a JSON canon with the sections the validator
  consumes, `05-contracts/02-canon.schema.json`, the "Size ranges" table and
  a copy of `validator.py`; the cell runs on its own copied validator
  (integration test included). `p-contract-shape` became a five-branch
  dispatcher with real validation through a stdlib mini-validator (type,
  enum, pattern, required, properties, additionalProperties, items,
  minimum); contracts are censused against the supported keyword subset.
- **Pin verifiable by adopters.** The registry gained a `locator` field per
  instance. The new gate `p-prior-pin` compares the sha256 of the prior
  document passed with `--case` against the sha256 registered for each cited
  executed instance (mismatch or a missing hash is blocking); without the
  prior document the pin is pending, never a pass. The sensitivity report
  was regenerated with the prior document (caught 14 of 14); the bare mode
  (caught 13 of 13, one not measured) is the run without the prior document.
- **Ledgers armored against the method's own governance.** `p-terms` exempts
  the frozen review ledger by design (vocabulary rules govern living
  documents; a frozen historical record is never edited to satisfy a later
  vocabulary). The fifth lesson of `99-lessons.md` was restored to the
  pre-v0.2 wording (the false positive of `iteration`), keeping the three
  `bible`→`canon` swaps. The rubric is versioned:
  `05-contracts/round-record.schema.json` (method version, round, models,
  summary, verdict, rubric hash) validates the round record line by line,
  and the round of this version carries the frozen rubric hash.
- **Scope and fact residues fixed.** `01-principle.md` entered the scope of
  `p-prior` and `p-prior-mark`; the 15 s fact now has the trail as its
  subject (the early exit was the symptom, not the subject); the "medium"
  parameter and the "closing passage" exemplar lost the case claim; "worked
  instances" became "designed instances (not executed)"; "any target" is
  qualified by the four conditions the principle states.
- **Stronger `p-prior` and `p-prior-mark`.** The trigger phrases come from
  the canon's new "Prior-statement triggers" table (whole-word,
  case-insensitive, no plural); a number with a row in "Recorded facts" is
  verified in the union of the cited sections of the prior's method
  document, and the report records which kind of verification ran.
- **The `[prior]` origin label resolved.** The origin-label table no longer
  has `[prior]`: a limit never inherits from the prior. The two gate
  justifications that used the label migrated to `[hypothesis]` with the
  prior fact cited as marked support, and the canon's definition of "prior
  instance" says the same.
- **License: Apache 2.0** (`LICENSE`, a section in the README, no per-file
  headers). The "License: undecided" line of v0.2.0 stays as history.
- **Round infra.** `VERSION` and the citations in the README, the principle
  and the SKILL bumped to 0.2.1; a round-record line added; the validation
  report and the sensitivity report regenerated with the prior document;
  `__pycache__` and `.pytest_cache` removed from the corpus.

History declared late (edits made in the v0.2.0 round and not declared
then):

- `99-lessons.md` received three `bible`→`canon` swaps (the term was retired
  by that same version; the retro-edit of the lessons file was the undeclared
  part; this version restores the original wording of entry 5 while keeping
  the swaps).
- The v0.2.0 round removed `replies` from the scope of `p-terms` — a
  loosening of a gate, not declared in the v0.2.0 entry; this version
  replaces it with the by-design exemption declared above.
- The rubric hash of round 1,
  `9ee608643db08c79d544efa1c553c7951c1fe30f1ff9035d60657d366f8cc21b`, is
  recorded here as the historical witness of what the first review was
  judged against; v0.2.0 re-froze the rubric after the vocabulary rename
  (current freeze `f4e842264469459eeaaeac1b8e922f626964b8318174ed9ca6e72938c2e808e0`).
- At least thirteen edits to `02-reflexive-application/README.md` were made
  during v0.2.0 and not declared then.
- Residual `__pycache__` and `.pytest_cache` folders were left inside the
  corpus by the v0.2.0 round.
- Correction applied in this round's rework: the v0.2.0 entry above claimed
  "`SKILL.md` is self-contained"; the skill had already become a folder
  (`SKILL.md` + `scripts/` + `references/`), so the claim is now "the skill
  folder is self-contained" — the correction this entry declares late,
  in the same discipline as the items above.

Deferred (owner decisions recorded for the next rounds): the determinism row
as a Measurement of its own; the atomicity of the scaffold (except the
OSError contract, now exit 2); open note 5 (the 0,15 s and 24 h numbers
outside the "Recorded facts" table); the execution of the first v0.2
instance — the material keeps declaring "working hypothesis — one executed
instance".

## 0.2.0

Refactor for genericity, applying the seven recommendations of a critical
panel (eight review seats plus a consolidation) and the corpus correction
found by the first independent review of the reflexive application.

- **Vocabulary decided before publishing.** The organization assembled for
  one target is a *production cell* (the former media term is retired). The
  single source of numbers, names, terms and rules is the *canon* (the file
  `01-bible.md` became `01-canon.md`; the recipe's `02-bible.json` became
  `02-canon.json`). The word *anchor* was split into its three senses:
  *rubric anchor* (a written score description), *position key* (the value
  that fixes where a part lands in assembly) and the gate `p-canon-link`
  (was `p-anchor`). Review verdicts are `accepted`, `accepted with
  conditions` and `rejected` (were `acceptable`, `acceptable with minor
  corrections`, `rejected`). "hand-off sheet" is kept as generic production
  vocabulary. The avoid-table no longer bans vocabulary that is canonical in
  other industries (stage gate, sprint, ticket, deliverable, acceptance
  criterion, client, sponsor); the continuity-checker entry became a
  historical note about the prior instance.
- **Corpus corrected.** The seven unsourced claims and two wrong numbers
  about the prior instance that the first review found in `01-principle.md`
  were aligned to the recorded facts or generalized without attribution.
  The correction is declared in the README and recorded in
  `02-reflexive-application/99-lessons.md`; the frozen review ledgers were
  not edited.
- **Origin normative demoted.** Golden rules 1 and 2 are stated as one
  general rule each; the media exemplars moved to examples per content
  type. The anonymity gate is off by default in the method and on by
  option in the brief of each instance (the reflexive application keeps it
  on).
- **The prior instance demoted and pinned.** The quarantine mark became
  `[prior:<id>]`, backed by `instances/registry.json`, which registers the
  executed instance `000-av-production` (method document pinned by sha256)
  and the three designed instances. The gates `p-case` and `p-case-mark`
  became `p-prior` and `p-prior-mark`; prior numbers are no longer a
  contract between instances. Recipe traps are stated abstractly with
  examples from at least two domains; the media example is attributed to
  the prior.
- **Packaging aligned.** The scaffold now generates the recipe layout
  (`production-cell-TARGET/` with `02-canon.json`, `03-artifacts.json`,
  `05-contracts/`, `priors.json` instead of `case-method.md`), the canon of
  a target no longer carries the method's own sections, and the skill folder
  is self-contained (works when copied alone).
- **Executable core promoted.** The validator accepts `--layout` (artifact
  to paths, gate to parser; default is this corpus's markdown layout),
  `--registry` (default `instances/registry.json` when present), validates
  `*.schema.json` contracts through the new gate `p-contract-shape`, maps
  the legacy note target `bible` to `canon`, and documents exit codes
  0/1/2 in `--help`. The recipe specifies the content-hash algorithm
  (sha256 over the canonical form). Tests were added
  (`80-validator/test_validator.py`, extended `test_scaffold.py`).
- **Versioned and pinned.** `VERSION` (this file), the version cited in the
  README, the principle and the SKILL, and `state/round-record.jsonl` with
  one entry per round (model and version, no dates).
- **Rubric re-frozen.** The "Rubric" section of
  `02-reflexive-application/04-gates-and-rubric.md` changed with the verdict
  rename and the canon vocabulary; `90-review/rubric.sha256` was re-frozen
  after the edit and the `p-frozen-rubric` gate passes with the new hash.

License: undecided (owner decision, out of scope for this version).

## 0.1.0

First complete form: principle, reflexive application (brief, canon, artifact
graph, role cards, gates and rubric, generic recipe, three designed
instances), validator with sensitivity test, one independent review round.
