# Instance 2: a long text about the world in 2027

The recipe in `10-generic-recipe.md` applied to writing a nonfiction book
about the world in 2027. The method terms follow the
[canon](01-canon.md). Whatever is an assumption about the publishing domain
is marked `[hypothesis]`.

What sets this instance apart: the target mixes three natures of statement
(fact, projection and opinion), and the reader has to tell the three apart
on every page. Here, the separation becomes a contract of the claims register
and a gate on the chapters.

## 0. Instantiation table

| Element | In this instance |
| --- | --- |
| Target | a publishable manuscript, in Brazilian Portuguese (pt-BR), of about 90 thousand words in 12 chapters, on what the world will look like in 2027 `[hypothesis: length and number of chapters]` |
| Owner and owner decisions | the author: central thesis and sub-theses, tone, what counts as the author's own opinion, approval of the outline, sensitive topics, release to the publisher |
| Sources of truth by content type | fact → primary source (official statistic, original document, peer-reviewed article); projection → declared model (a published projection with its edition identified, or own calculation with assumptions in the register); number → claims register; quotation → original text; figure → data file plus the script that draws it; style → canon; thesis and tone → author |
| Main artifacts | `thesis`, `theme-map`, `domain-dossier`, `claims-register`, `projections`, `outline`, `alternative-scenarios`, `chapters`, `figures`, `fact-check`, `manuscript` |
| Roles | structure editor, domain researcher, fact verifier, projection modeler, scenario critic, writer, text editor, data designer, manuscript assembler, validator, independent reader |
| Main gates | every claim with a register identifier, every projection marked and with a resolution criterion, primary source, single edition per series, source density, readability, size per chapter, overlap between chapters, recheck of volatile claims |
| Independent review rubric | blind reading by readers from the target audience (agents with a declared profile, and people): accuracy by reopened sample, fact × projection × opinion distinction, thesis, coverage and balance, calibration, readability, structure, value |
| Validator verifies | names, acronyms and offices; numbers with unit and source edition; dates; glossary terms; projection mark; cited register identifiers |
| Assembly engine | code that assembles the manuscript, generates the endnotes from the register, draws the figures from the data, measures readability and overlap, and runs the validator; agents research, write, check and read under a gate |
| Quick first version | the "skeleton manuscript": the 12 chapters at about 15% of the final size, each with a sub-thesis, key claims, one projection, one alternative scenario and the link to the next chapter, assembled and read at once |
| Round loop | skeleton, full draft, edited text, final text; in each one, notes to the origin (register, projection, outline or chapter), new gates, and a root-cause fix of the claim detector |
| Stopping criterion | the author declares: release when the reading comes out accepted, the fact-check has zero "does not match" and the volatile claims have been rechecked inside the window; the rest becomes open notes for proofreading |
| Case method document | `book-method.md`: graph, roles with degree, contracts of the register and of the projections, false positives of the detector, history of the discarded theses |
| What stays with the human | thesis, tone, authorial opinion, the decision to label something as a projection or as an opinion, approval of the outline, topics with legal risk, release and the relationship with the publisher |

## 1. Brief

- **Target:** a nonfiction book about the state of the world in 2027, written
  before or at the beginning of the year, which combines what is already
  known with what is projected, and says in every passage which is which.
- **For whom:** a cultured non-specialist reader, in Brazilian Portuguese
  `[hypothesis]`.
- **Non-negotiables**, written as something measurable:
  - no factual claim without an identifier in the register;
  - no projection presented as fact;
  - every point projection with a range or a probability and a resolution
    criterion;
  - no figure whose number does not come from a data file.
- **Owner decisions:** central thesis and sub-theses; tone; which passages
  are signed opinion; approval of the outline; treatment of topics with legal
  risk; release.
- **Budget:** maximum rounds per artifact = 2 before escalating to the
  author; one independent reading per version.
- **Provisional stopping criterion:** the one in section 11.
- **What is not an objective:** predicting single events (elections, sports
  results) as a bet; covering every country.

## 2. Initial canon

| Section | Owner | Initial content |
| --- | --- | --- |
| Thesis | author (as `thesis`, a separate artifact) | pointer to the `thesis` artifact; the canon does not copy the thesis, so that there are not two versions |
| Canonical numbers | fact verifier | per number: spelling in the text, spelling in a table, unit, rounding, nature (fact or projection), identifier in the register, source edition |
| Names and acronyms | text editor | canonical spelling of people, countries, institutions; acronym with its first mention spelled out in each chapter; office with the period it refers to |
| Terms | text editor | terms to prefer and to avoid, terms to gloss with a marker (for example, "artificial general intelligence", defined at the first mention in each chapter) |
| Nature marks | text editor | how the text marks a projection ("according to the projection by..., between X and Y") and an opinion ("in my reading"); accepted variants and where |
| Style | text editor | sentence, paragraph, use of the first person, numbers spelled out up to ten, dates spelled out |
| Volatile claims | fact verifier | categories of claim that change (price, office, status of a conflict, count in progress) and the recheck window |

## 3. Artifacts and graph

| Artifact | Owner | Depends on | Schema | Gates |
| --- | --- | --- | --- | --- |
| `brief` | owner | — | fixed sections of the recipe | approved by the author |
| `thesis` | owner | `brief` | central thesis in one paragraph; three to seven sub-theses, each with what would falsify it | exists; approved |
| `canon` | text editor | `brief`, `thesis` | JSON per section, with owner and version | schema |
| `theme-map` | structure editor | `brief`, `thesis` | domains (geopolitics, economy, climate and energy, technology, demography and health, society), with questions per domain | each sub-thesis covered by a domain |
| `domain-dossier` | domain researcher | `theme-map`, `canon` | per domain: sources read, candidate claims with source and excerpt | every candidate with source and excerpt |
| `claims-register` | fact verifier | `domain-dossier` | per claim: identifier, canonical text, nature, source, source type, edition, confidence level, volatile or not, chapters | `t-primary-source`, `t-single-edition`, `t-recheck` |
| `projections` | projection modeler | `domain-dossier`, `canon` | per projection: identifier, magnitude, range or probability, model or source, edition, assumptions, resolution criterion | `t-resolution`, `t-single-edition` |
| `outline` | structure editor | `thesis`, `theme-map`, `claims-register`, `projections` | per chapter: sub-thesis, questions, claims and projections it uses, link to the next chapter | `t-thesis-in-outline`, `t-regional-coverage` |
| `alternative-scenarios` | scenario critic | `thesis`, `outline`, `projections` | per sub-thesis: the strongest alternative scenario, the signal that would distinguish it, the probability the critic gives it | `t-alternative-scenario` |
| `chapters` | writer | `outline`, `claims-register`, `projections`, `alternative-scenarios`, `canon` | one file per chapter; claims and projections marked by identifier in the source file | `t-claim-with-id`, `t-projection-marked`, `t-source-density`, `t-readability`, `t-chapter-size`, `t-overlap`, `t-direct-quote` |
| `figures` | data designer | `claims-register`, `projections`, `canon` | per figure: data file, script, identifiers it shows | `t-data-figure` |
| `fact-check` | fact verifier | `chapters`, `claims-register` | per chapter: claims reopened, verdict (matches, does not match, rephrase), source reopened | `t-sample-check` |
| `manuscript` | manuscript assembler | `chapters`, `figures`, `claims-register`, `canon` | the assembled book with a version tag; endnotes generated from the register | `t-assembly` |
| `validation-report` | validator | `manuscript`, `canon`, `claims-register`, `projections` | deterministic report | `t-validation` |
| `independent-reading` | independent reader | `manuscript`, `validation-report`, `fact-check` | report format of the rubric | frozen rubric |
| `editorial-release` | owner | `independent-reading`, `fact-check` | recorded decision, with the accepted open notes | signed |

The artifact graph:

```text
brief ─> thesis ─┬─> canon
                 └─> theme-map ─> domain-dossier ─┬─> claims-register
                                                  └─> projections
thesis + theme-map + claims-register + projections ─> outline
thesis + outline + projections ─> alternative-scenarios
outline + register + projections + alternative-scenarios + canon ─> chapters
register + projections + canon ─> figures
chapters + register ─> fact-check
chapters + figures + register + canon ─> manuscript ─> validation-report
manuscript + validation-report + fact-check ─> independent-reading ─> editorial-release
```

Two graph choices that matter:

- The **thesis is an owner artifact**, on which almost everything depends.
  Changing a sub-thesis makes the outline, the scenarios and the affected
  chapters stale, and the engine knows which ones.
- The **claims register is separate from the chapters**. The writer does not
  create claims: a sentence with a fact and no identifier is cut or becomes a
  note to the fact verifier. The general formulation, "the fact never comes from
  the writer", belongs to the principle; here it becomes a contract.

## 4. Role cards

### Structure editor

- **Decides:** the domains, the order and the cut of the chapters, and which
  claims and projections each chapter uses.
- **Does not decide:** the thesis (author); whether a claim enters the
  register (fact verifier).
- **Inputs:** `thesis`, `theme-map`, `claims-register`, `projections`.
- **Outputs:** `theme-map`, `outline`.
- **Exit gate:** `t-thesis-in-outline`, `t-regional-coverage`.
- **Notes it emits:** to the `thesis`, when a sub-thesis does not hold up with
  the register available (`high`, with the claims that are missing).
- **Code-conversion degree:** (b) the coverage of sub-theses and regions is
  code over the outline in data; cutting is an agent under a gate, approved
  by the author.

### Domain researcher

One card per domain, with the same format.

- **Decides:** which sources to read and which candidate claims to propose.
- **Does not decide:** whether the candidate enters the register (fact
  verifier); the projection (modeler).
- **Inputs:** `theme-map`, `canon`.
- **Outputs:** `domain-dossier`.
- **Exit gate:** every candidate with a source and a literal excerpt.
- **Notes it emits:** to the `theme-map`, when a domain has no accessible
  primary source for a question (`medium`).
- **Code-conversion degree:** (c) research is an agent with web access; the
  code checks that the source and the excerpt exist.

### Fact verifier

- **Decides:** whether a claim enters the register, with what confidence
  level, and the verdict of each check.
- **Does not decide:** the chapter text (note to the writer); labeling
  something as an opinion (author).
- **Inputs:** `domain-dossier`, `chapters`, primary sources.
- **Outputs:** `claims-register`, `fact-check`.
- **Exit gate:** `t-primary-source`, `t-single-edition`, `t-recheck`,
  `t-sample-check`.
- **Notes it emits:** to the writer, per claim that does not match
  (`blocking`); to the `domain-dossier`, per error found in a source, so that
  no claim uses it again (`medium`).
- **Code-conversion degree:** (b) the register contract, the single edition
  and the window of the volatile claims are code; opening the source and
  judging is an agent with web access, with a sample checked by a person.

### Projection modeler

- **Decides:** which model or published projection to use for each
  magnitude, the assumptions and the resolution criterion.
- **Does not decide:** turning a projection into a fact; choosing the
  projection that favors the thesis (the scenario critic checks).
- **Inputs:** `domain-dossier`, `canon`.
- **Outputs:** `projections`.
- **Exit gate:** `t-resolution`, `t-single-edition`.
- **Notes it emits:** to the outline, when a sub-thesis depends on a
  projection whose range is too wide to support the claim (`high`).
- **Code-conversion degree:** (b) own calculations are versioned code;
  choosing the source is an agent under a gate.

### Scenario critic

- **Decides:** the strongest alternative scenario for each sub-thesis and the
  probability it assigns to it.
- **Does not decide:** changing the thesis (note to the author).
- **Inputs:** `thesis`, `outline`, `projections`.
- **Outputs:** `alternative-scenarios`.
- **Exit gate:** `t-alternative-scenario`.
- **Notes it emits:** to the `thesis`, when the alternative scenario is more
  probable than the thesis scenario according to the register's own
  projections (`high`).
- **Code-conversion degree:** (c) agent, preferably a model other than the
  writer's, so as not to share blind spots.

### Writer

- **Decides:** the text, the order of the paragraphs, the examples, within the
  outline.
- **Does not decide:** creating a claim or a projection (note to the fact
  verifier or to the modeler); changing the chapter's sub-thesis (note to the
  structure editor).
- **Inputs:** `outline`, `claims-register`, `projections`,
  `alternative-scenarios`, `canon`.
- **Outputs:** `chapters`.
- **Exit gate:** `t-claim-with-id`, `t-projection-marked`,
  `t-source-density`, `t-readability`, `t-chapter-size`, `t-overlap`,
  `t-direct-quote`.
- **Notes it emits:** to the `claims-register`, when it needs a fact that is
  not there (`medium`).
- **Code-conversion degree:** (c) agent under a gate; the code measures
  everything the exit gate lists.

### Text editor

- **Decides:** style, terms, names and nature marks in the canon; the form of
  each sentence when there is a style note.
- **Does not decide:** the factual content; the thesis.
- **Inputs:** `brief`, `thesis`, `chapters`.
- **Outputs:** `canon`.
- **Exit gate:** the canon schema; every section with an owner and a version.
- **Notes it emits:** to the writer, per sentence outside the style (`low` or
  `medium`); to the `canon`, per term that two chapters use in different
  senses (`high`).
- **Code-conversion degree:** (b) terms to avoid, sentence length and
  acronyms are code; the rest is an agent or a person.

### Data designer

- **Decides:** the chart type and the design.
- **Does not decide:** the number (it comes from the register or from the
  projections).
- **Inputs:** `claims-register`, `projections`, `canon`.
- **Outputs:** `figures`.
- **Exit gate:** `t-data-figure`.
- **Notes it emits:** to the register, when the series lacks the granularity
  for the requested chart (`medium`).
- **Code-conversion degree:** (a) a figure is a script over data; the
  designer decides the design.

### Manuscript assembler

- **Decides:** nothing about content.
- **Does not decide:** the order of the chapters (outline); the text.
- **Inputs:** `chapters`, `figures`, `claims-register`, `canon`.
- **Outputs:** `manuscript`, with a version tag.
- **Exit gate:** `t-assembly`.
- **Notes it emits:** to the chapter with a reference that does not resolve
  (`high`).
- **Code-conversion degree:** (a).

### Validator

- **Decides:** nothing outside the rules it executes.
- **Does not decide:** whether a note of its own is a false positive (the
  fact verifier or the text editor contest it; the owner of the instrument
  decides).
- **Inputs:** `manuscript`, `canon`, `claims-register`, `projections`.
- **Outputs:** `validation-report`.
- **Exit gate:** a report identical across two executions.
- **Notes it emits:** those of section 7.
- **Code-conversion degree:** (a).

### Independent reader

- **Decides:** the scores per dimension and the severity of the findings.
- **Does not decide:** the rubric; what gets corrected; the release.
- **Inputs:** `manuscript`, `validation-report`, `fact-check`; never the
  conversations of the production.
- **Outputs:** `independent-reading`.
- **Exit gate:** a report in the format of the rubric.
- **Notes it emits:** to any artifact of the graph.
- **Code-conversion degree:** (c) agents with a declared reader profile and at
  least two people from the audience `[hypothesis]`.

## 5. Gates

| Gate | Artifact | Magnitude | Limit | Justification |
| --- | --- | --- | --- | --- |
| `t-claim-with-id` | `chapters` | sentences with a number, a date, a named institution or an attribution verb ("according to", "shows", "points out") without a register identifier | 0 | [method] the fact never comes from the writer; the detector is wide on purpose and the exceptions become a tested rule |
| `t-projection-marked` | `chapters` | quantitative claims about 2027 without a projection mark and without a `projections` identifier | 0 | [method] the reader has to tell fact from projection in every passage, so the separation is a gate and not a matter of style |
| `t-primary-source` | `claims-register` | fraction of the factual claims whose final source is primary; claims with a tertiary source (encyclopedia, aggregator) as the final source | ≥ 80%; 0 tertiary | [hypothesis] part of the claims exists only in quality reporting, which is an acceptable secondary source; a tertiary source is never the final source because it does not answer for the data |
| `t-single-edition` | `claims-register`, `projections` | series cited with more than one edition of the same source in the manuscript | 0 | [method] two editions of the same series give two numbers for the same fact, the divergence the canon exists to prevent |
| `t-resolution` | `projections` | point projections without a range or probability, or without a resolution criterion verifiable by the end of 2027 | 0 | [hypothesis] calibrated-forecasting practice: a projection without a resolution criterion cannot be judged wrong, and therefore does not inform |
| `t-alternative-scenario` | `alternative-scenarios` | sub-theses without an alternative scenario and without an observable signal that distinguishes them | 0 | [method] a thesis without an explicit alternative is the editorial version of the agent that approves its own work |
| `t-source-density` | `chapters` | claim identifiers per thousand words in the factual chapters | ≥ 4 | [hypothesis] nonfiction books with endnotes usually carry one note every two hundred to three hundred words in the factual passages; four per thousand is the floor, not the goal |
| `t-readability` | `chapters` | mean sentence length; reading-ease index adapted to Portuguese | ≤ 22 words; index ≥ 40 | [hypothesis] a comfortable reading range for a cultured non-specialist reader; the index is a coarse instrument and serves to find passages off the curve, not to write by |
| `t-chapter-size` | `chapters` | words per chapter | 6 000 to 9 000 | [hypothesis] 12 chapters of about 7 500 words give the size of the brief; outside the range, the chapter is two chapters or a footnote |
| `t-overlap` | `chapters` | fraction of eight-word sequences repeated across different chapters | ≤ 1% | [hypothesis] long repetition across chapters indicates a recycled paragraph; short stock phrases stay below the limit |
| `t-direct-quote` | `chapters` | words per direct quotation; quotations without a source | ≤ 60 words; 0 without a source | [hypothesis] a prudent limit for quotation in a commercial work, to be confirmed with the publisher's legal guidance |
| `t-recheck` | `claims-register` | volatile claims not rechecked inside the window before delivery | none in a window of fourteen days (written in words: a row that cites a prior's number has every number in it checked against that prior) | [hypothesis] the reference case used a window of 24 h before delivery [prior:000-av-production]; a book has a longer production time, and the window follows the time between closing and printing |
| `t-data-figure` | `figures` | figures without a data file and script; figure numbers that differ from the register | 0 | [method] the number never comes from the drawing; the figure is a function of the data |
| `t-sample-check` | `fact-check` | claims reopened at the source; claims with the verdict "does not match" | all the prominent ones (title, opening, figure) and at least 20% drawn at random from the rest; 0 "does not match" | [hypothesis] reopening everything is expensive; the prominent claims are what the reader remembers most, and the random sample estimates the error rate of the rest |
| `t-regional-coverage` | `outline` | fraction of chapters with evidence from at least three regions of the world | ≥ 75% | [hypothesis] a book about the world that cites only one continent is about that continent; some chapters are regional by nature |
| `t-thesis-in-outline` | `outline` | sub-theses without a chapter; chapters without a sub-thesis | 0 | [method] an artifact without a consumer or a consumer without a source is a badly drawn graph |
| `t-assembly` | `manuscript` | cross-references and notes that do not resolve; identifiers cited that do not exist in the register | 0 | [method] the contract refuses ambiguity before the file goes to the publisher |
| `t-validation` | `validation-report` | open high and blocking notes from the validator | 0 to release | [method] a name, number or office with two spellings is the defect the attentive reader finds first |

Gate sensitivity test of each code gate: a paragraph with "according to the
report" and a number without an identifier must fail `t-claim-with-id`; a
figure with the number swapped in the data must fail `t-data-figure`.

## 6. Independent review rubric

Three agent readers with declared profiles (economics reader, science
reader, generalist reader), from models different from the writer's, and two
people from the target audience `[hypothesis]`. All of them receive only the
manuscript, the fact-check and the validator's report.

| Dimension | What is measured | 1 | 3 | 5 |
| --- | --- | --- | --- | --- |
| Accuracy | sampled claims reopened by the reader | error in a prominent claim | errors only in details | no divergence in the sample |
| Nature of claims | the reader knows, in each passage, whether it is fact, projection or opinion | projection read as fact | marks present, sometimes ambiguous | always clear |
| Thesis | the reader summarizes the sub-thesis of each chapter in one sentence, and the summary matches the outline's | fewer than half match | most match | all match |
| Coverage and balance | domains, regions and perspectives | one domain or one region dominates | balance with declared gaps | balance with no relevant gap |
| Calibration | ranges, resolution criteria, alternative scenarios present and honest | certainties without a range | ranges present, weak alternatives | strong ranges and alternatives |
| Readability and pacing | a reader of the profile finishes the chapter without rereading | unreadable passages | readable with slow passages | fluid |
| Structure | progression between chapters, links, repetition | loose or repeated chapters | progression with jumps | clear progression |
| Value | the text says something a summary of the cited reports would not | it is a summary | partly interpretation | sustained own interpretation |

The "Thesis" dimension has a measure: agreement between the reader's summary
and the outline's sub-thesis in at least 10 of the 12 chapters for a score
of 5 `[hypothesis]`. Severity: `blocking` for a prominent claim that does not
match and for a projection presented as fact; `high` for a sub-thesis the
reader does not recognize; `medium` for an imbalance of coverage; `low` for
style.

Verdict by the mechanical rule (the same as the "Verdict rule" template of
the recipe): `rejected` if there is a blocking finding or any dimension with a
score ≤ 2; `accepted` if there is no high finding and all dimensions have a
score ≥ 4; otherwise, `accepted with conditions`.

## 7. Validator

| Verifies | Against | Severity | Note to |
| --- | --- | --- | --- |
| spelling of names, acronyms and first mention spelled out | "names and acronyms" section | `medium` | writer |
| office of a person cited | "names and acronyms" section, with the period | `high` | fact verifier (it is volatile) |
| numbers: spelling, unit, rounding, edition | "canonical numbers" section and register | `high` | writer, or `claims-register` if the register diverges from the canon |
| numbers spelled out ("one quarter", "two thirds") | register | `high` | writer |
| nature mark (projection, opinion) | "nature marks" section | `high` | writer |
| terms to avoid and terms to gloss | "terms" section | `medium` | writer |
| identifiers cited | register and projections | `blocking` if nonexistent | writer |

## 8. Assembly engine

| Part | Code | Agent under a gate | Human |
| --- | --- | --- | --- |
| Assembly | joins chapters and figures, generates the endnotes from the register, resolves references, names by tag | — | approves the proof |
| Register and projections | validates the contract, single edition, window of the volatile claims | proposes claims and projections | decides what is opinion |
| Chapters | measures identifiers, marks, readability, size, overlap, quotations | writes | approves the tone |
| Figures | draws from the data | — | chooses the design |
| Fact-check | draws the sample, compares numbers | reopens sources on the web | checks a subsample |
| Reading | joins reports, applies the verdict rule | reads with a profile | two people read |
| Notes | routes, deduplicates, counts rounds, escalates | — | answers the author's |

## 9. Quick first version

The "skeleton manuscript": the 12 chapters at about a thousand words each,
each with the sub-thesis, five key claims from the register, one projection
with a resolution criterion, the alternative scenario and the link to the
next chapter; assembled with endnotes and provisional figures generated from
the data; immediate independent reading.

What it is expected to reveal: sub-theses the register does not support,
domains without a primary source, chapters that say the same thing,
projections without a model, and whatever the rubric measures and no gate
measures (for example, the "Value" dimension).

## 10. Round loop

Versions: v1 skeleton, v2 full draft, v3 edited text, v4 final text
`[hypothesis]`. Examples of what the loop does here:

- **False positive, fixed at the root:** the detector `t-claim-with-id`
  flags "Chapter 3", the year in the title "in 2027" and ordinal numbers as
  claims without a source. The fix is not to switch the detector off in
  titles; it is to write the rule (a chapter number, an enumeration ordinal
  and the year that is the subject of the book are not claims), with a test
  for each case, and to redo the previous round to prove that no real claim
  stopped being flagged.
- **Regression that slipped through:** a chapter rewritten after a note goes
  back to carrying the share of an energy source from an old edition, written
  out in words ("one quarter"), and the validator only read digits.
  Before fixing it, the validator gains a reading of numbers spelled
  out, which fails the current version; then the writer corrects it.
- **Instrument corrected:** the readability index fails chapters with many
  long proper names of institutions. The fix is to measure without the names
  in the canon's "names and acronyms" section, with a test, and to redo the
  previous round's measurements; the limit does not change.

## 11. Stopping criterion

Declared by the author before the last round: release when the independent
reading comes out `accepted`, the fact-check has zero "does not match" and
the volatile claims have been rechecked inside the window. `low` and `medium`
notes become open notes for proofreading. A condition specific to this
target: if the release goes past a deadline declared by the author (for
example, mid-2027), the projections already resolved become fact or error,
and the book calls for another version instead of stopping `[hypothesis]`.

## 12. Case method document

`book-method.md`, with: the graph; the contracts of the register and of the
projections; per role, the pseudocode of the work and the code-conversion
degree; the false positives of the claim detector and how each one was
fixed; the theses and sub-theses discarded and why; the author's decisions;
the stopping criterion applied. After publication, an appendix with the
scoreboard of the projections at the end of 2027, by the resolution
criterion of each one: the method applied to its own error.

## 13. What stays with the human

- The thesis and the sub-theses, and the decision to abandon one.
- The tone and the voice.
- What is signed opinion and what is projection.
- The approval of the outline.
- Topics with legal risk (living people, accusations).
- The release and the relationship with the publisher.

The code prepares these decisions (the register, the coverage, the
scoreboard of the projections); it does not make them.
