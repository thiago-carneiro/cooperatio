# Canon of this production

Single source of the method terms, the fixed lists and the form rules that
every document in this folder uses. The validator
(`80-validator/`) reads the tables on this page directly: changing a
table changes what it checks. Each section has an owner and a version; a
section that changes bumps its version.

| Section | Owner | Version | State |
| --- | --- | --- | --- |
| Canon schema | verifier | v1 | ready |
| Method terms | writer | v5 | ready |
| Terms to avoid | writer | v2 | ready |
| Fixed lists | writer | v6 | ready |
| Form rules | writer | v5 | ready |
| Recorded facts | verifier | v5 | ready |

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
| magnitude | The measured value the gate returns (seconds, kilograms, count, ratio), never just a sign. |
| limit | The value that separates pass from fail, with the justification and the origin label next to it. |
| signal gate | A gate that only tests existence or "greater than zero"; it lets a broken instrument through. A signal gate has to gain a magnitude limit. |
| gate sensitivity test | Before trusting a gate, inject a known defect and check that the gate rejects it; a gate that never rejects proves nothing. Its shorthand is sensitivity test. |
| note | The only change request between roles: target artifact, severity, text, origin, evidence, round. It aims at where the defect was born, not where it was seen. |
| severity | One of four values: `low`, `medium`, `high`, `blocking`. Only `high` and `blocking` send the artifact back to its owner. |
| open note | A note recorded and not resolved when the production stops; it is written debt, not forgotten debt. |
| round | One pass of the loop: produce, pass the gates, assemble, review, notes. It also counts, per artifact, each return caused by a serious note. |
| maximum rounds | How many returns an artifact accepts before it is escalated to the owner. |
| escalated | State of an artifact that exceeded its maximum rounds: nothing that depends on it runs until the owner decides. |
| canon | The single source of numbers, names, terms to prefer and to avoid, accepted variants and rules, with an owner and a version per section. The word replaced a publishing metaphor in v0.2; the old name stays legitimate only where the history of this production is told, and always cited, never used. |
| accepted variant | Another spelling of a number or term that the canon admits in a declared place and for a declared reason. |
| validator | A checking instrument, preferably in code, that reads all artifacts against the canon and against their neighbors and emits notes on its own. |
| independent review | A reading of the product by someone who did not produce it and has no access to the producer's reasoning, with the fixed rubric, returning notes and a verdict. |
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
| `[experiment:<id>]` | the section of that id in `60-experiments.md`, whose status is `executed` |
| `[lessons]` | `99-lessons.md`, the history of this reflexive application |
| `[hypothesis]` | nowhere yet: an assumption, to be measured |

A label counts outside code spans only. The list is closed and the
matching is lexical: a paraphrase of a claim escapes it.

### Efficacy mark in append-only documents

An append-only document is measured by `p-efficacy-mark` from the heading
below on; the units above it are history, never rewritten to satisfy a
later rule, as the frozen ledger is for the vocabulary.

| Document | Measured from the heading |
| --- | --- |
| `99-lessons.md` | `## The v0.5.0 round: exit 0 is not green` |

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
   triggers") carries `[prior:<id>]`, `[experiment:<id>]`, `[lessons]` or
   `[hypothesis]`, outside code spans.

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
