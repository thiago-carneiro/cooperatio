# Canon of this production

Single source of the method terms, the fixed lists and the form rules that
every document in this folder uses. The validator
(`80-validator/`) reads the tables on this page directly: changing a
table changes what it checks. Each section has an owner and a version; a
section that changes bumps its version.

| Section | Owner | Version | State |
| --- | --- | --- | --- |
| Canon schema | verifier | v1 | ready |
| Method terms | writer | v6 | ready |
| Terms to avoid | writer | v2 | ready |
| Fixed lists | writer | v7 | ready |
| Form rules | writer | v6 | ready |
| Recorded facts | verifier | v6 | ready |

## Method terms

Canonical definitions. A document that uses one of these terms uses it in
this sense; a method concept that is not here must not appear under a name of
its own before it enters this table.

| Term | Canonical definition |
| --- | --- |
| target | The final product that the production cell hands over (a car, a manuscript, a library). |
| owner | The person who commissions the target, approves the brief, makes the decisions no role can make and declares the stop. It is not an agent role. |
| brief | The owner's document: what the target is, for whom, what is non-negotiable, what is an owner decision, the round budget. Without a brief there is no canon. |
| corpus | The facts, materials, standards and references available before the production. The production reads the corpus and does not edit it; an error found in it becomes a note to the target `corpus`. |
| source of truth | For each content type, the only source accepted as origin (a fact comes from the corpus, a number comes from the canon, performance comes from the measurement). The writer is never a source of fact. |
| production cell | The organization assembled for one target: roles, artifacts, gates, canon, validator, review and assembly engine. The term is domain-neutral manufacture vocabulary, chosen in v0.2 to replace the media term the method was born with. |
| artifact | An intermediate or final output, typed, with a name, a single owner, paths, a schema, dependencies, gates and content identified by hash. An owner decision is also an artifact. |
| artifact graph | The set of artifacts with the dependencies between them; it has to be acyclic. The engine rebuilds only what became stale. |
| stale | State of an artifact whose input changed (different hash) since it passed its gates. |
| role | A narrow responsibility exercised by an agent, a person or code, which communicates with other roles only through artifacts and notes. A role that neither emits notes nor has a gate is a step, not a role. |
| role card | The sheet of a role with seven fixed fields: decides, does not decide, inputs, outputs, exit gate, notes it emits, code-conversion degree. |
| contract | The schema an artifact has to validate before it is accepted; it rejects the ambiguous before the expensive work. |
| gate | A measurable function over an artifact that returns pass or fail together with the measured magnitude. It has a limit and a written justification. A tool that does not run is a tool failure, never a pass or a fail. |
| domain gate | A gate of the target's domain (identity of results, a speedup, a mass), named `d-<name>`: the cell's own code measures it and writes a result file in the contract `domain-result.schema.json`, and the validator reads the result, checks the sha256 of its inputs and turns it into a row (since v0.6.0). |
| magnitude | The measured value the gate returns (seconds, kilograms, count, ratio), never just a sign. |
| limit | The value that separates pass from fail, with the justification and the origin label next to it. |
| signal gate | A gate that only tests existence or "greater than zero"; it lets a broken instrument through. A signal gate has to gain a magnitude limit. |
| gate sensitivity test | Before trusting a gate, inject a known defect and check that the gate rejects it; a gate that never rejects proves nothing. Its shorthand is sensitivity test. |
| note | The only change request between roles: target artifact, severity, text, origin, evidence, round. It aims at where the defect was born, not where it was seen. |
| severity | One of four values: `low`, `medium`, `high`, `blocking`. Only `high` and `blocking` send the artifact back to its owner. |
| open note | A note recorded and not resolved when the production stops; it is written debt, not forgotten debt. |
| round | One pass of the loop: produce, pass the gates, assemble, review, notes. It also counts, per artifact, each return caused by a serious note. |
| maintenance round | A round that corrects the material of the method itself after its stopping criterion, outside the reflexive production: recorded in the round record as `kind: maintenance`, with its scope and the reviewer's relation, and with no verdict of the canon (since v0.6.0). |
| maximum rounds | How many returns an artifact accepts before it is escalated to the owner. |
| escalated | State of an artifact that exceeded its maximum rounds: nothing that depends on it runs until the owner decides. |
| canon | The single source of numbers, names, terms to prefer and to avoid, accepted variants and rules, with an owner and a version per section. The word replaced a publishing metaphor in v0.2; the old name stays legitimate only where the history of this production is told, and always cited, never used. |
| accepted variant | Another spelling of a number or term that the canon admits in a declared place and for a declared reason. |
| validator | A checking instrument, preferably in code, that reads all artifacts against the canon and against their neighbors and emits notes on its own. The role that runs it and routes its notes is the runner (named "validator" until v0.6.0). |
| runner | The role that runs the validator and routes its notes to the owners of the artifacts; it decides nothing beyond the rules the validator executes. |
| independent review | A reading of the product by someone who did not produce it and has no access to the producer's reasoning, with the fixed rubric, returning notes and a verdict. Since v0.6.0 the round record states the reviewer's relation to the producer (`reviewer_relation`); a reviewer of another family is recommended, a hypothesis with a cost (a second provider), not a rule. |
| rubric | The fixed grid of dimensions, anchors and verdict rule that every independent review uses in every round; written before the first review. |
| rubric anchor | The written description of what a score of 1, 3 or 5 means in one rubric dimension, so that two reviewers read the same anchor the same way. One of the three senses the word "anchor" had before v0.2 disambiguated them. |
| position key | The value that fixes where a part of the target lands during assembly (a word of the script, a heading of a chapter). An ambiguous position key is a contract error, found before the expensive work. One of the three senses the word "anchor" had before v0.2 disambiguated them. |
| verdict | Result of the independent review, with three values: `rejected`, `accepted with conditions`, `accepted`. In the prior instance `000-av-production`, the values were "rejected", "publishable with minor corrections" and "publishable" (step 17 and the version table of the prior's method document) [prior:000-av-production]. |
| hand-off sheet | The artifact one role writes for another role to consume (a cue sheet, a section spec, a work order). Kept as a term in v0.2: it is generic production vocabulary, and the position key it carries is where ambiguity between roles is caught. |
| prior instance | An instance of the method that ran before the current one and is registered in the instance registry. A statement about a prior carries `[prior:<id>]`; a number inside the mark is checked against that prior's method document. Numbers of a prior are facts about that prior, citable with the mark; a limit of a new instance never inherits from them without its own domain justification (a `[hypothesis]` label may cite a prior fact as support, never as the limit itself). |
| instance registry | The record of the known instances (`instances/registry.json`, at the root of this material): each one with an id, a status (`executed` or `designed`), the path of its method document relative to that document's own repository root, and the sha256 that pins it. Cited ids have to be registered. |
| instrument | Anything that measures: gate, validator, reviewer, simulation, benchmark. |
| experiment | A measurement about the method itself, not about a target, registered in `60-experiments.md` with its question, protocol and predictions written before measuring; status `executed`, `pending` (protocol fixed, results not yet recorded) or `designed`. Only an executed experiment backs a claim; a designed one carries no number. |
| retired gate | A gate removed deliberately, with its perturbation, because its object is gone or its rule moved into a contract; the changelog records the gate, the reason and the rounds it stayed silent. |
| false positive | A note the instrument emits when there is no defect. It is a defect of the instrument until proven otherwise. |
| false negative | A real defect that no instrument reported. |
| root-cause fix | Handling a false positive by fixing the instrument's rule, with a test that reproduces the case, and redoing the previous round to prove that no real finding disappeared. Loosening the limit is not a root-cause fix. |
| regression | A defect that comes back or appears in a new version; if it escaped every gate, it gains a gate before it is fixed. |
| assembly engine | The code that composes the artifacts into the target, rejects ambiguity, rebuilds by hash, routes notes and names the outputs by version label. |
| code-conversion degree | How much of a role's work the code does: (a) converted, the code does it and the person or the model decides exceptions; (b) partial under gate, the code does or measures a part; (c) contract and gate only, the role is exercised by an agent or a person and the code only validates the output. |
| first version | The v1: the whole target, end to end, made quickly to be reviewed, not to be good. |
| stopping criterion | The condition, declared by the owner before the last round, under which the review becomes a list of open notes and not a new version. |
| case method document | The document that, at the end, records the ideas, graph, step by step, pseudocode per role with its degree, the owner's pending items and the known false positives of an instance. |
| instantiation table | The table of fourteen fixed rows (section "Fixed lists") that summarizes an instance. |
| unit | What a gate reads as one statement: a paragraph, a list item, a table row or a heading. A mark or a label applies to the unit it sits in. |
| family | The provider and line of models an executor belongs to, named by a stable letter (family A, family B); two executors differ in family when what their names map to differs, never by their names. |
| dispatch | One call of an executor with its inputs (the files, the prompt, the card), recorded with what the endpoint returned (tokens, the reason the generation ended). |
| wave | A batch of dispatches run in parallel, whose outputs are read together before the next step. |
| teamwork | The files that set up a production cell for a target (brief, canon, artifact graph, cards, gates, rubric, notes); the name of the skill that creates them. |
| executor | Whoever or whatever exercises a role: a person, code, or a language model of a declared kind. Different roles may have different executors, and the executor of the independent review differs from the executor of the artifact it reviews. It is declared in the code-conversion degree field of the role card. |
| orchestrator | Whoever executes the recipe: passes paths (not summaries) to the roles, runs the engine and imports notes. It is a step, not a role. |

## Terms to avoid

Synonyms that would make the text drift. The validator searches for
each one as a whole word, case-insensitive, outside code and link targets.
The table controls intra-method synonyms only: vocabulary that is canonical
in another industry is not banned here.

| Avoid | Use | Reason |
| --- | --- | --- |
| quality gate | gate | canonical term |
| checkpoint | gate | suggests a stop point without magnitude |
| pipeline | artifact graph | "pipeline" hides dependencies and hash |
| feedback | note | a note has fixed fields; "feedback" does not |
| iteration | round | a single name for one pass of the loop |
| single source of truth | canon | canonical term |
| bible | canon | the term changed in v0.2; the old name is legitimate only as cited history |
| ruler | rubric | canonical term |
| review board | independent review | canonical term; the review is done by whoever did not produce |

## Fixed lists

### Instantiation table rows

Every instance opens with a two-column table (`Element`, `In this instance`)
with these rows, in this order, none of them empty:

| Row |
| --- |
| Target |
| Owner and owner decisions |
| Sources of truth by content type |
| Main artifacts |
| Roles |
| Main gates |
| Independent review rubric |
| Validator verifies |
| Assembly engine |
| Quick first version |
| Round loop |
| Stopping criterion |
| Case method document |
| What stays with the human |

### Mandatory sections of an instance

| Section |
| --- |
| Instantiation table |
| Brief |
| Initial canon |
| Artifacts and graph |
| Role cards |
| Gates |
| Independent review rubric |
| Validator |
| Assembly engine |
| Quick first version |
| Round loop |
| Stopping criterion |
| Case method document |
| What stays with the human |

### Role card fields

| Field |
| --- |
| Decides |
| Does not decide |
| Inputs |
| Outputs |
| Exit gate |
| Notes it emits |
| Code-conversion degree |

### Origin labels of a limit

Every limit justification starts with one of these labels.

| Label | Meaning |
| --- | --- |
| `[method]` | the limit follows from the method itself (for example, zero terms outside the canon) |
| `[brief]` | the limit was set by the owner in the brief |
| `[hypothesis]` | the limit is an assumption about the domain, plausible and justified, to be confirmed in a real instance |

### Method components

The eleven components that every instance has to name: artifact graph, role
card, contract, gate, note, canon, validator, independent review,
instrument, stopping criterion, gate sensitivity test.

### Prior-statement triggers

A unit that uses one of these phrases talks about a registered prior and
carries `[prior:<id>]`; the mark is what makes the statement checkable. The
phrases are matched whole-word, case-insensitive, with no plural
("prior instances" is not the trigger "prior instance"); the words "the
case" alone are not a trigger. Phrases on this page and in code spans are
exempt: this table is the definition, not a statement about the prior. A
mark inside a code span is notation too, not a mark (since v0.5.0).

| Trigger phrase |
| --- |
| `reference case` |
| `reference-case` |
| `prior instance` |
| `of the case` |
| `the executed instance` |
| `instance 0` |

### Efficacy triggers

A unit that uses one of these phrases claims that the method works, and the
method's own doctrine of evidence applies to it: it carries one of the
labels of the table below it. The phrases are matched like the
prior-statement triggers (whole-word, case-insensitive, outside code spans);
this page is exempt, being the definition.

| Trigger phrase |
| --- |
| `pays off` |
| `pays for itself` |
| `the method found` |
| `the method caught` |
| `the method prevented` |
| `would have caught` |
| `would have been caught` |
| `found the blocker` |
| `found the error` |
| `the method prevents` |
| `the method finds` |
| `the method catches` |
| `the gates caught` |
| `the gate caught` |
| `the validator found` |
| `the review found` |
| `err less` |
| `the only way` |
| `observed in practice` |
| `every rule below was born` |
| `none was` |

| Label | Where the evidence is registered |
| --- | --- |
| `[prior:<id>]` | the method document of that registered prior |
| `[experiment:<id>]` | the section of that id in `60-experiments.md`, whose status is `executed` and whose "Provenance" table gives the sha256 of at least one input and one output (since v0.6.0; without it the label reads as `[hypothesis]`, with a note) |
| `[against:<id>]` | an executed experiment of `60-experiments.md`, with its provenance, whose result goes against the claim: counter-evidence is labeled like evidence (since v0.6.0) |
| `[lessons:<title>]` | the entry of `99-lessons.md` whose heading is that title (since v0.6.0; a bare `[lessons]` named the whole file) |
| `[hypothesis]` | nowhere yet: an assumption, to be measured |

A label counts outside code spans only. The list is closed and the
matching is lexical: a paraphrase of a claim escapes it. A claim labeled
`[hypothesis]` that states a number or a universal quantifier ("every",
"always", "none", a percentage) gets a low note: the label
stays valid, the claim has the shape of a measurement with none behind it.

### Efficacy mark in append-only documents

An append-only document is measured by `p-efficacy-mark` from the heading
below on; the units above it are history, never rewritten to satisfy a
later rule, as the frozen ledger is for the vocabulary.

| Document | Measured from the heading |
| --- | --- |
| `99-lessons.md` | `## The v0.5.0 round: exit 0 is not green` |

### Documents outside the artifact table

Every Markdown document of this folder belongs to an artifact of
`02-artifacts.md` or is listed below, by path or glob in a code span, with
the reason (`p-declared`, since v0.6.0). This production lists none: every
document it holds is an artifact.

| Document | Why it is outside the artifact table |
| --- | --- |

### Chained ledgers

An append-only ledger carries a hash chain from its first line written in
v0.6.0 on: each new line holds `prev`, the sha256 of every line above it.
The lines written before the chain are counted here and are never edited;
every line after them carries `prev` (`p-contract-shape`).

| Ledger | Lines before the chain |
| --- | --- |
| `state/round-record.jsonl` | 10 |
| `state/notes-status.jsonl` | 48 |
| `state/owner-decisions.jsonl` | 0 |

### Frozen records

The records of the review of round 1 and the history of the lessons are
never edited; their sha256 is pinned here and compared under
`p-frozen-rubric` (since v0.6.0), as the rubric is. A row with a heading
pins the part of the file above that heading.

| Record | sha256 | Frozen part |
| --- | --- | --- |
| `90-review/auditor-report.md` | `bf7c5f131cce1f0cd64d329aa59c8b1d170f4017d41099d6e5b760581adafaf0` | the whole file |
| `90-review/auditor-notes.json` | `d2b4946348d3e54fdd53101dc5da7d8622be37b0f5d9f86a6fb5dd374465a044` | the whole file |
| `90-review/notes.json` | `80b3eddf121bfd77c7df88860c6d58d905a9da7cf46bed1c833edf3201b04842` | the whole file |
| `90-review/replies.md` | `a9da78519ae6b1bc4cc8f462b3416abf34c49d151915f7c7a8281efa9ba113f3` | the whole file |
| `90-review/rubric.sha256` | `99ace405d569251017cc6b545c23b6fad76860c2305342fe2e3fe156238b8f1f` | the whole file |
| `99-lessons.md` | `029053a1f0d227a5088f06395a5820f6a6968606f840a1aa8063c8cd89364fd7` | `## The v0.5.0 round: exit 0 is not green` |

### Accepted paths

A path that `p-anonymity` reads in a document and that is not a path of a
machine (a system path a document quotes) is declared here, with the
reason. Since the rework of v0.6.0 an entry is a path and nothing else (its
whole text has the shape of an absolute, root or UNC path; any other entry
is a tool failure), the gate drops only a path hit equal to the entry, in
that document only, and blanks no text before the checks of identifiers and
dates, and the canon cannot accept a path for itself. An interpreter line
(`#!`) on line 1 is always accepted. This production declares none.

| Document | Path | Why it is accepted |
| --- | --- | --- |

### Month names

The month names of a language whose dates `p-anonymity` reads besides the
ones the validator carries (English, Portuguese, Spanish, French, German and
Italian, since the rework of v0.6.0): the code of the language and its
twelve names, each in a code span. A language the brief declares on its
"Languages:" line with neither is pending under `p-anonymity-language`,
which `--allow-pending` does not accept. This production writes
in English and declares none.

| Language | Months |
| --- | --- |

### Machine roots

The roots of one segment that name a machine of this production (a scratch
or project root like `/scr01`), each in a code span, with the reason. A root
of one segment is read by `p-anonymity` when another segment follows it,
when it is one of the common roots the validator carries, or when it is
here; any other one alone is not read (since the rework of v0.6.0, a
decision: a bare `/name` in prose is too often no path). This production
declares none.

| Root | Why it names a machine |
| --- | --- |

## Form rules

1. American English; plain Markdown, no HTML tag; simple tables.
2. Pseudocode only in fenced blocks marked `text`; no other kind of block.
3. Paths relative to the folder; a prior's method document is cited relative
   to its own repository root and is kept outside this repository, unless
   its whole cell is distributed with the material (since v0.5.0 the cell
   of `004-adoption-guide` is, under `instances/`).
4. No absolute path, machine name, user name, model identifier or authoring
   date; an executor is named by family (a stable letter) and effort.
5. Every unit that states something numeric about a registered prior carries
   `[prior:<id>]`, and names an instance by its full id
   (`004-adoption-guide`): a bare `004` there is read as a number.
6. A domain assumption carries `[hypothesis]`.
7. Every document, except this canon, points to it by link, with a target
   that resolves.
8. Every unit that claims the method's efficacy (a phrase of "Efficacy
   triggers") carries `[prior:<id>]`, `[experiment:<id>]`,
   `[against:<id>]`, `[lessons:<title>]` or `[hypothesis]`, outside code
   spans.
9. A prior mark is `[prior:<id>]` with an id of lowercase letters, digits
   and hyphens; any other bracketed `[prior:...]` outside code spans is a
   malformed mark (blocking), never a silent skip (since v0.6.0).

## Recorded facts

The numbers this production states about the registered priors
`000-av-production` and `004-adoption-guide`, each one checked in the method
document of the prior its row marks (registered in `instances/registry.json`,
pinned by sha256); the sections a row cites are sections of that document. A
number about a prior that is not here does not enter the documents before it
is checked and added. These are facts about that prior, not limits for a new
instance.

| Number | In what context | Where in the prior's method document |
| --- | --- | --- |
| 18 | roles with a card `[prior:000-av-production]` | sections 1.1 and 2.1 |
| 49 | artifacts in the graph of its first pilot `[prior:000-av-production]` | section 2.1 |
| 2 | maximum rounds per artifact `[prior:000-av-production]` | section 1.4 |
| 3, 4, 12, 12 | blocking, high, medium and low notes from the review of v1 `[prior:000-av-production]` | step 15 |
| 26 | low notes open at v5 `[prior:000-av-production]` | step 17 |
| 0.546 s and 0.10 s | p95 of the drift between two representations of the same content at v1 (wrong instrument) and at v2 (fixed) `[prior:000-av-production]` | section 1.10 |
| 15 s | the trail that left early at v3 because of an ambiguous position key `[prior:000-av-production]` | section 1.10 |
| 38 and 2 | validator notes at v2, two of them high and false `[prior:000-av-production]` | step 14 |
| 12 and 10 | notes from an automatic reviewer, ten of them false `[prior:000-av-production]` | step 15 |
| 31, 18 and 73 | review findings, validator notes and notes imported in the v2 round, three separate counts and not a sum `[prior:000-av-production]` | step 16 |
| 50 | ceiling of notes per gate `[prior:000-av-production]` | section 1.4 |
| 3 | exit code of a tool that failed `[prior:000-av-production]` | section 1.4 |
| 0.15 s | p95 limit of the drift gate between two representations of the same content `[prior:000-av-production]` | sections 1.10 and step 13 |
| 24 h | window for rechecking volatile claims before delivery `[prior:000-av-production]` | sections 2.4, step 6 and 4.5 |
| 1054 | words of the adoption guide at the close `[prior:004-adoption-guide]` | sections 4.4 and 5 |
| 900 and 1400 | the size range of the guide in words, set in its brief `[prior:004-adoption-guide]` | sections 1, 4.4 and 5 |
| 4 | the lowest dimension score of its one review, which accepted it `[prior:004-adoption-guide]` | section 4.5 |

### Section commitments

The sha256 of the text of each section of the owner-held method document of
`000-av-production` that a row above cites (the lines under its numbered
heading, up to the next numbered heading, joined by LF; the reader of
`p-prior`), since v0.6.0. They reveal nothing of the text and make a later
rewrite of a cited section detectable: with `--case`, `p-prior` compares
them on the row of this canon; without it, the row says "owner-held
evidence, not measured here". The document of `004-adoption-guide` is distributed and pinned whole.

| Prior | Section | sha256 |
| --- | --- | --- |
| `[prior:000-av-production]` | 1.1 | `1f608646a782bf537e5292907ee540736ec29a428dc559b37d2e7b8d6d623e96` |
| `[prior:000-av-production]` | 1.4 | `8fb80bb5d892b26c5ee1c646664ba073e50d255c848455b6a90204fc0f33b4eb` |
| `[prior:000-av-production]` | 1.10 | `b0302c18530e834602923dd64ed15f306728efe29112512f82a79ef95f92e46f` |
| `[prior:000-av-production]` | 2.1 | `65ec3d92ecd2302759cc4fbc21e2e391082d394a1deec71dc86b7ae207aa869b` |
| `[prior:000-av-production]` | 2.4 | `c6cb59af5c56d7a451c589d9f70c47919fd9b2f55210f54254530f3adecbbf16` |
| `[prior:000-av-production]` | 4.5 | `7e9727b6f47a35cb461f17264675fd5075979f1b6a1618100bda3d1c3b1b42b1` |
| `[prior:000-av-production]` | 6 | `d469baff73d6d589e04291bb807b99bc4aa50767f54a277662f5828165410f1b` |
| `[prior:000-av-production]` | 13 | `f1d37761ec7c993c0bb9aac2f5822d9196b81b7d7cc87b48d1d1a375be7a8c57` |
| `[prior:000-av-production]` | 14 | `ff54424959483dea6aa2437be13a20d7fbf38ebcdc739bc3eb6fba4277026263` |
| `[prior:000-av-production]` | 15 | `9b50a7dc272ae44f3b5b024431959e8d1b83bdf345f7bee843fa5c0b6e2a1e3d` |
| `[prior:000-av-production]` | 16 | `368b9dfd80b34b2ed3b8a8360a8bb12f10512cf397871b3ffd18ca1d429d7ecb` |
| `[prior:000-av-production]` | 17 | `90e791ff6ab2ea3321cce9a50bdb6001a02f19012d4b0eeaf2315153653ce60d` |

## Historical vocabulary of the prior instance

Recorded so the older documents (the frozen review of round 1, above all) can
be read without confusion; none of these words is live vocabulary of this
production.

- The prior instance called its validator the "continuity checker" (also
  "continuity editor"); in this production the instrument is the validator.
- The review verdicts of the prior were "publishable", "publishable with
  minor corrections" and "rejected"; this production uses `accepted`,
  `accepted with conditions` and `rejected`.
- The organization assembled for one target carried a media term until v0.2;
  the production cell is the canonical name since then, and the gate that
  counts links to this page is `p-canon-link`.
- The quarantine mark that a bracketed word carried until v0.2 became
  `[prior:<id>]`; the ledgers of round 1 keep the old marks and are never
  edited.
