# Gates and rubric of this production

The gates each document has to pass before the review, with magnitude, limit
and justification, and the rubric of the independent review, written and
frozen before the first (and only) review. The terms follow the
[canon](01-canon.md); the artifacts are in
[`02-artifacts.md`](02-artifacts.md).

## Gates

All of them are measured by the validator
(`80-validator/validator.py`), except `p-notes`, which the
verifier runs through the same script with another option. A tool that does
not run is a tool failure (code 2), never a pass or a fail; a gate that was
not measured is pending, and a run with a pending gate the caller did not
accept by name (`--allow-pending`) exits 4, never 0. The artifact table of
[`02-artifacts.md`](02-artifacts.md) assigns the gates to the artifacts;
the Artifact column below mirrors it, and `p-references` reports any
divergence. The determinism
of the report is not a gate on a document: it is a measurement of the
instrument (see "Measurements" below). What a gate reads in detail, how a
gate is retired and where the rubric came from are declared in
[`06-gate-semantics.md`](06-gate-semantics.md).

| Gate | Artifact | Magnitude | Limit | Justification |
| --- | --- | --- | --- | --- |
| `p-terms` | `brief`, `canon`, `artifacts`, `cards`, `gates-and-rubric`, `gate-semantics`, `recipe`, `instance-car`, `instance-text-2027`, `instance-hpc`, `lessons`, `readme`, `readme-root`, `skill`, `changelog`, `replies`, `experiments` | occurrences of terms from the canon's "Terms to avoid" table, outside code and link targets; the frozen ledger is exempt (semantics: `06-gate-semantics.md`) | 0 | [method] a synonym outside the canon is the first sign of drift, and replacing it with a canonical term costs one word; there is no reason to tolerate a single one |
| `p-canon-link` | `brief`, `artifacts`, `cards`, `gates-and-rubric`, `gate-semantics`, `recipe`, `instance-car`, `instance-text-2027`, `instance-hpc`, `lessons`, `readme`, `readme-root`, `skill`, `experiments` | links naming `01-canon.md` that resolve, relative to the document's folder, to the canon file of the layout + links naming it that do not resolve | ≥ 1 resolved, 0 unresolved | [method] a reader who lands on a loose document needs to know where the definitions are; one link is enough, and a link that leads nowhere links nothing |
| `p-anonymity` | `corpus`, `brief`, `canon`, `artifacts`, `cards`, `gates-and-rubric`, `gate-semantics`, `recipe`, `instance-car`, `instance-text-2027`, `instance-hpc`, `replies`, `lessons`, `readme`, `readme-root`, `skill`, `changelog`, `registry`, `round-record`, `notes-status`, `experiments` | absolute paths (one segment under a common root, file URLs and home folders by user name included) + dates in year-month-day, day/month/year or day.month.year format or with the month's name + the expressions "made on", "written on", "generated on" followed by a date + identifiers of the forbidden list, model identifiers included, pending in this corpus (semantics: `06-gate-semantics.md`) | 0 | [brief] the brief of this instance forbids absolute paths, authoring dates, machine names and user names; in the method this gate is an option of the instance, declared in its brief, and this brief keeps it on |
| `p-form` | `brief`, `canon`, `artifacts`, `cards`, `gates-and-rubric`, `gate-semantics`, `recipe`, `instance-car`, `instance-text-2027`, `instance-hpc`, `replies`, `lessons`, `readme`, `readme-root`, `skill`, `changelog`, `experiments` | HTML tags outside code + fenced blocks without the `text` mark | 0 | [brief] plain Markdown and pseudocode only in `text` are non-negotiables of the brief |
| `p-size` | `brief`, `canon`, `artifacts`, `cards`, `gates-and-rubric`, `gate-semantics`, `recipe`, `instance-car`, `instance-text-2027`, `instance-hpc`, `lessons`, `readme`, `experiments` | words in the document (separated by whitespace, tables included) | within the range in the "Size ranges" table | [hypothesis] below the minimum, the instance does not fit the fourteen sections with domain content; above the maximum, the reader does not read all of it; ranges estimated before writing, and a range is raised before writing, never met by cutting text: the README is an index plus a runbook that grows with its flags, and the lessons grow by one entry per round |
| `p-table` | `instance-car`, `instance-text-2027`, `instance-hpc` | rows present from the canon's "Instantiation table rows" list, and empty cells or cells holding a placeholder | 14 of 14, 0 empty | [method] the table is the summary that makes instances comparable; a missing row is a forgotten component |
| `p-sections` | `instance-car`, `instance-text-2027`, `instance-hpc` | sections present from the canon's "Mandatory sections of an instance" list | 14 of 14 | [method] each section corresponds to a step of the recipe; missing one is skipping a step |
| `p-card` | `cards`, `instance-car`, `instance-text-2027`, `instance-hpc` | fields present from the "Role card fields" list, per card, and placeholders left in a card | 7 of 7 in every card, 0 placeholders | [method] the principle says that a role without a gate and without a note is a step; the seven fields are what makes this verifiable |
| `p-limit` | `gates-and-rubric`, `instance-car`, `instance-text-2027`, `instance-hpc` | gate table rows with an empty magnitude, limit or justification, a justification without an origin label or with fewer than 6 words, or a placeholder in a field | 0 | [method] "no gate without a limit and a justification" is in the request; 6 words is the minimum to say where the number comes from and why not another one |
| `p-references` | `artifacts`, `cards`, `gates-and-rubric`, `instance-car`, `instance-text-2027`, `instance-hpc` | artifacts cited in gates, dependencies or notes a card emits and not declared + owners that are neither a role nor `owner` + cycles in the graph + gates the artifact table assigns with no row in this table, or rows naming other artifacts than it assigns + placeholders in an artifact record | 0 | [method] a loose reference is the written form of "the old text nobody knew had changed"; a cycle means a wrong graph |
| `p-prior` | `corpus`, `canon`, `recipe`, `instance-car`, `instance-text-2027`, `instance-hpc`, `lessons`, `experiments` | prior labels whose id is not registered in `../instances/registry.json` + numbers of units marked `[prior:<id>]` not verified in the method document of `<id>` (a number needs its row in the canon's "Recorded facts" and is checked in the sections the row cites) + section references whose label does not exist there (semantics: `06-gate-semantics.md`) | 0 | [brief] the brief forbids inventing facts about the registered prior; a number absent from the prior's method document is an invented fact until proven otherwise, and prior numbers are facts about that prior, never limits for a new instance |
| `p-prior-mark` | `corpus`, `recipe`, `instance-car`, `instance-text-2027`, `instance-hpc`, `experiments` | paragraphs, list items and table rows that use a phrase of the canon's "Prior-statement triggers" table without the `[prior:...]` mark (reach: `06-gate-semantics.md`) | 0 | [method] created after the review: a qualitative statement about the prior, absent from its document, passed every gate because only numeric statements needed a mark; with the mark, the verifier checks each one |
| `p-prior-pin` | `registry` | executed priors cited in documents that carry `p-prior`, whose registered sha256 is compared with the documents passed with `--case` (reach: `06-gate-semantics.md`) | equal | [method] a pin nobody can re-verify is not a pin; comparing the registered sha256 with the document that was actually passed turns the registry entry into a checkable fact |
| `p-contract-shape` | `artifacts`, `contracts`, `registry`, `open-notes`, `notes-status`, `round-record` | schema cells of the artifact table citing a `*.schema.json` file that is missing or does not parse as JSON + keywords of each contract outside the subset the validator applies, or a contract version other than the one it reads + registry, note ledger, state ledger and round record validated line by line against their schemas + registry entries that break the contract of their status (semantics: `06-gate-semantics.md`) | 0 | [method] a schema cell that promises a contract has to point at a file a program can read, and a contract that exists but is never applied is not a contract; validation happens before the expensive work |
| `p-recipe` | `recipe` | steps missing one of the fields "Reads", "Creates", "Does", "Done when"; steps in total | 0 missing a field; ≥ 12 steps | [method] the request demands created files and a done criterion per step; 12 is the number of steps in the principle's recipe, which this one details |
| `p-components` | `instance-car`, `instance-text-2027`, `instance-hpc` | method components (the canon's list) named in the document | 11 of 11 | [method] the principle says the eleven components do not change with the domain; an instance without one of them is not the method |
| `p-sensitivity` | `instrument-validator` | known defects injected into a copy of the folder that the expected gate lets through, with at least one perturbation per gate the artifact table assigns except this one (20 of 20 gates, 35 perturbations; reported as "k of n gates covered, 0 missed of m", and an assigned gate without a perturbation leaves this gate pending with the gate named, never passing) + an incomplete report, a table that does not add up to its count, or a provenance (validator, gate section, canon, perturbation set) that does not match the running instrument and its inputs (semantics: `06-gate-semantics.md`) | every gate covered, 0 missed | [method] a gate that never fails proves nothing; each gate of the validator has to fail its known perturbation before it counts — and a report this instrument cannot have produced proves nothing either, so a provenance mismatch is blocking |
| `p-notes` | `open-notes`, `notes-status` | notes missing one of the six fields, with a severity outside the four, or with a target outside the graph of `02-artifacts.md` + notes of the ledger without exactly one line in the state ledger, or with a closing status and no version | 0 | [hypothesis] a note aimed at an artifact the graph does not know is undeliverable; the note router of the prior instance rejected such a target before touching anything [prior:000-av-production], and here the same contract is checked by code |
| `p-frozen-rubric` | `gates-and-rubric`, `review` | equality between the sha256 recorded when the review was launched and the current sha256 of the rubric as the layout resolves it (semantics: `06-gate-semantics.md`) | equal | [method] a rubric changed after the review makes the verdict incomparable; the principle requires the rubric to be written beforehand |
| `p-efficacy-mark` | `corpus`, `brief`, `recipe`, `instance-car`, `instance-text-2027`, `instance-hpc`, `lessons`, `readme`, `experiments` | paragraphs, list items and table rows that use a phrase of the canon's "Efficacy triggers" table, outside code spans, without one of the labels `[prior:<id>]`, `[experiment:<id>]`, `[lessons]`, `[hypothesis]` outside code spans + `[experiment:<id>]` labels that do not name an executed experiment of `60-experiments.md`; in the lessons, from the heading the canon declares on (semantics: `06-gate-semantics.md`) | 0 | [method] the method demands a checkable source for every statement about a prior; a claim that the method itself works is a statement of the same kind, and exempting it was the double standard the critical panel found |
| `p-declared` | `artifacts` | artifacts declared in the table whose files match nothing on disk (sub-cases: `06-gate-semantics.md`) | 0 | [method] a declared document that silently matches no file is a promise the instrument never kept: the missing path is a blocking note naming it, never an absent line |

### Measurements

A measurement applies to the instrument (the validator itself), not to an
artifact of the corpus; it cannot fail a document.

| Measurement | Artifact | Magnitude | Expected | Justification |
| --- | --- | --- | --- | --- |
| `m-determinism` | `instrument-validator`, `validation-report` | equality of the report's sha256 across two consecutive runs on the same input | equal | [hypothesis] a report that changes by itself is not evidence; the continuity ledger the validator of the prior instance wrote was deterministic (no date, relative paths) [prior:000-av-production], which is the fact that supports this limit, not the limit itself |

### Size ranges

Declared before writing, in words.

| Document | Minimum | Maximum |
| --- | --- | --- |
| `README.md` | 150 | 1500 |
| `00-brief.md` | 300 | 1200 |
| `01-canon.md` | 800 | 3600 |
| `02-artifacts.md` | 400 | 1800 |
| `03-roles/validator.md` | 250 | 900 |
| `03-roles/writer.md` | 250 | 900 |
| `03-roles/reviewer.md` | 250 | 900 |
| `03-roles/verifier.md` | 250 | 900 |
| `04-gates-and-rubric.md` | 900 | 3600 |
| `06-gate-semantics.md` | 400 | 3400 |
| `10-generic-recipe.md` | 3000 | 7500 |
| `20-instance-car.md` | 3500 | 8500 |
| `21-instance-text-2027.md` | 3500 | 8500 |
| `22-instance-hpc.md` | 3500 | 8500 |
| `60-experiments.md` | 400 | 6000 |
| `99-lessons.md` | 300 | 4000 |

### Gate rounds

Each document goes back to the writer up to 2 times per failed gate
(`[brief]`); on the third time, it is escalated to the owner. A validator
note that the writer disputes goes to the verifier, who decides whether it
is a false positive and, if it is, fixes the rule in the script with a test
case.

## Rubric

This section is frozen before the review: its sha256 is recorded in
`90-review/rubric.sha256` at launch, and the `p-frozen-rubric` gate compares
it.

### Dimensions

Each dimension receives a score from 1 to 5, with evidence (file and excerpt).

| Dimension | What is measured | 1 | 3 | 5 |
| --- | --- | --- | --- | --- |
| D1 Fidelity to the principle | the eleven components and the golden rules of `../01-principle.md` are applied without contradiction; nothing about the reference case was invented | contradicts the principle or invents a fact about the case | applies the principle with omissions that do not change the application | applies every component and rule, every statement about the case checks out |
| D2 Recipe executability | a person or an agent follows the recipe without asking: each step says what it reads, what it creates, what it does and when it is done | vague steps, with no file or no done criterion | most steps are executable; some call for interpretation | every step is executable and the done criterion is verifiable |
| D3 Concreteness of instances | each instance fills each element with domain content, not with text that would serve any target | generic rows, roles and artifacts without a domain name | concrete for the most part, generic in some elements | a domain expert recognizes the artifacts, roles and gates |
| D4 Gates and numbers | gates with magnitude; plausible limits; justifications that say why that number; hypotheses marked | signal gates, limits without justification or implausible | plausible limits, some weak justifications or unmarked hypotheses | every limit is defensible and its origin is marked |
| D5 Internal coherence | canon terms used in their sense; the same number equal everywhere; references between documents close | terms with different senses, divergent numbers | coherent, with local slips | no divergence found |
| D6 Reflexivity | the production followed its own method (brief, canon, artifacts, cards, gates, validator, review, notes, stopping, lessons) and is honest where it did not | the method is described but not followed | followed with undeclared gaps | followed, and the gaps are declared |
| D7 Form | American English, plain Markdown, simple tables, pseudocode in `text`, no absolute path, authoring date or machine, sizes within range | violates constraints of the brief | isolated form slips | no violation |
| D8 Epistemic honesty | distinguishes method, prior instance and domain; marks hypotheses; does not state what it cannot support | states as fact what is an assumption | marks most of the assumptions | every assumption marked, limits of the text itself declared |

### Finding severity

| Severity | When |
| --- | --- |
| `blocking` | invented fact about the prior instance; contradiction with the principle that would change the application; missing mandatory document; instance that cannot be executed |
| `high` | gap that prevents an agent from executing a step; signal gate or unjustifiable limit; term used in a sense different from the canon; instance element filled with generic text |
| `medium` | domain imprecision without a `[hypothesis]` mark; weak example; redundancy that confuses |
| `low` | style, local readability, word choice |

### Verdict rule

Mechanical, applied to the scores and findings:

```text
if a blocking finding exists or some dimension has a score ≤ 2:
    verdict = rejected
else if no high finding and every dimension has a score ≥ 4:
    verdict = accepted
else:
    verdict = accepted with conditions
```

### Report format

1. **Verdict**, with the application of the rule (which scores and findings
   decided it).
2. **Scores by dimension**: table with dimension, score, evidence.
3. **Findings by severity**: each one with target artifact (graph name from
   `02-artifacts.md`, or `corpus`), severity, text, evidence.
4. **Verified and correct**: what was checked and is right, one line of
   evidence each.
5. **Not verified**: what the reviewer could not check, and why.
6. **Out of scope**: what was noticed and does not belong in this production.
7. **Notes in JSON**: the list of findings in the note contract (six fields;
   `origin` = `reviewer`; `round` = 1).
