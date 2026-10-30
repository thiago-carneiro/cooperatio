# Generic recipe: how to set up a production cell for a new target

A step-by-step procedure, independent of domain, for applying the method of
`../01-principle.md` to a new target. It serves a person and an orchestrator
agent: each step says who performs it, what it reads, which files it creates,
what it does, in what order, and when it is done. The terms follow the
[canon](01-canon.md); where a step uses one of its terms, it uses it in the
canon's sense.

**How to read.**

- The paths of the created files are relative to the production cell folder,
  which step 0 creates. The names are suggestions; what matters is that each
  artifact has one file, one owner and one schema.
- "Done when" is always verifiable: a count, an equality, a file that exists
  and validates. If a done criterion calls for judgment, the step says who
  judges.
- The lines marked `[prior:<id>]` state what happened in an earlier
  registered instance from which the method came, and every number in them is in that
  prior's method document (registered in `../instances/registry.json`, cited
  relative to its own repository root, and kept outside this repository
  unless its cell is distributed under `../instances/`). They
  are here to show the size of the error that the step prevents.

## The map: this recipe and the principle's recipe

The principle has twelve steps. This recipe details them in fifteen, because
three things that sit inside other steps there cost a lot when forgotten and
deserve a step of their own: preparing the folder (step 0), taking inventory of
the sources of truth (step 2) and writing the contracts (step 6).

| Step here | Principle step | What it produces |
| --- | --- | --- |
| 0. Production cell folder | (implicit) | the numbered structure and the empty note ledger |
| 1. Brief | 1 | `00-brief.md` |
| 2. Sources of truth | 1 and 2 | `01-sources-of-truth.md` |
| 3. Initial canon | 2 | `02-canon.json` |
| 4. Artifacts and graph | 3 | `03-artifacts.json` and the graph |
| 5. Role cards | 4 | `04-roles/*.md` |
| 6. Contracts | 3 and 8 | `05-contracts/*` |
| 7. Gates | 5 | `06-gates.md` and the gate code |
| 8. Rubric | 6 | `07-rubric.md`, frozen |
| 9. Validator | 7 | `08-validator/` |
| 10. Assembly engine | 8 | `09-engine/` |
| 11. Quick first version and immediate review | 9 | `v1/`, `review/v1-*` |
| 12. Round loop | 10 | `review/vN-*`, new gates, `lessons.md` |
| 13. Stop | 11 | `open-notes.json` |
| 14. Case method document | 12 | `method-TARGET.md`, `priors.json` |

## The orchestrator in pseudocode

```text
assemble_production_cell(owner_request, corpus):
    folder ← step_0()
    brief ← step_1(owner_request)                # the owner approves; without approval, stop
    sources ← step_2(brief, corpus)
    canon ← step_3(brief, sources, corpus)
    graph ← step_4(brief, canon)                 # must be acyclic
    cards ← step_5(graph, canon)
    contracts ← step_6(graph, cards)
    gates ← step_7(graph, contracts, canon)
    rubric ← step_8(brief)                       # frozen: hash recorded
    validator ← step_9(canon, graph)
    engine ← step_10(graph, contracts, gates, validator)
    v ← 1
    product ← engine.compile(graph)              # the whole v1, quickly
    review ← independent_reviewer(product, rubric)
    repeat:
        if stopping_criterion(review, v): step_13(review); exit
        step_12(review)                          # notes, new gates, instrument fixed at the root
        v ← v + 1
        product ← engine.compile(graph)          # only what is stale
        review ← independent_reviewer(product, rubric)
    step_14()
```

The orchestrator is a step, not a role: it passes paths (never summaries) to
each role, runs the engine and imports the notes. It decides nothing that a
card assigns to a role or to the owner.

## The production cell folder

```text
production-cell-TARGET/
  00-brief.md
  01-sources-of-truth.md
  02-canon.json           (the canon as data, with a schema)
  03-artifacts.json       (the graph: one record per artifact)
  04-roles/               (one card per role)
  05-contracts/           (one schema per artifact that passes between roles)
  06-gates.md             (gate catalog; the code lives in the engine)
  07-rubric.md            (frozen; 07-rubric.sha256 next to it)
  08-validator/  (rules, code, tests)
  09-engine/              (assembly, graph, note router)
  state/                  (status of each artifact, note ledger, round record, logs)
  v1/ v2/ ...             (outputs named by version label; created in step 11)
  review/                 (reports and notes of each round)
  lessons.md
  open-notes.json
  priors.json             (the registry of prior instances this cell knows)
  method-TARGET.md        (the case method document; created in step 14)
```

## The steps

### Step 0. Prepare the production cell folder

- **Who:** the orchestrator.
- **Reads:** the owner's request.
- **Creates:** the tree from the previous section, with an empty
  `state/notes.jsonl`, an empty `state/round-record.jsonl` and an empty
  `priors.json`.
- **Does:**
  1. creates the numbered folders;
  2. decides where everything that stays out of version control goes
     (generated files, large files, sensitive data) and records it in
     `00-brief.md`, in the available sources of truth;
  3. decides how machine-dependent paths enter: always as a command-line
     variable, never written into an artifact.
- **Done when:** the tree exists; `state/notes.jsonl` exists and is empty; the
  `priors.json` parses and has no instances.
- **Trap:** starting to write the brief inside a conversation and only then
  creating the folder. What is not in a file has no hash, and what has no hash
  makes nobody stale.

### Step 1. Write the brief

- **Who:** the role that translates the owner's intent (in the prior instance
  `000-av-production`, the role that wrote the brief, section 2.1 of the
  case) [prior:000-av-production]; the owner approves.
- **Reads:** the owner's request, the corpus.
- **Creates:** `00-brief.md`, with fixed sections: target; for whom;
  non-negotiables; owner decisions (a named list, each with a status); available
  sources of truth; budget (maximum rounds per artifact, review rounds,
  deadline); provisional stopping criterion; what is not an objective;
  assumptions.
- **Does:**
  1. writes each section with a source, or labels it `[hypothesis]`;
  2. turns every "the owner decides" in the request into a line of the owner
     decisions table;
  3. writes the non-negotiables as sentences that a gate could measure
     ("byte-identical result", not "correct result");
  4. takes it to the owner.
- **Done when:** all sections are filled in or say "owner decision pending";
  every assumption is labeled; the owner recorded the approval (a line in the
  brief itself or a decision file).
- **Trap:** a vague non-negotiable. "Safe", "good", "fast" do not become gates;
  "mass ≤ X kg", "no fact without a source", "speedup ≥ Y" do.

### Step 2. Take inventory of the sources of truth

- **Who:** the brief's writer together with the domain's fact verifier.
- **Reads:** `00-brief.md`, the corpus.
- **Creates:** `01-sources-of-truth.md`: a table with content type, the source
  that errs least, who consults it, and what is forbidden as a source.
- **Does:**
  1. lists every content type the target will have (fact, number, text, image,
     physical measurement, performance, standard, cost...);
  2. for each one, picks exactly one source of truth and writes why it errs less
     than the others;
  3. writes what is never a source for that type: the writer is never a source
     of fact; a generative tool is never a source of exact text; the number never
     comes from the paragraph that cites it.
- **Done when:** every content type in the brief has exactly one source; no
  line has the writer as a source of fact; each line says what is forbidden.
- **Trap:** two content types with the same source "because it is easier". A
  type of content inherits the source of another because the second is at
  hand, and the confusion surfaces only when the target is checked. In the
  prior instance, exact text composed by a generative tool came out with wrong
  characters in every probe; hence the rule that all exact text comes from the
  engine (section 1.8 of the case) [prior:000-av-production]. A vehicle: a
  supplier's marketing sheet is never the source of a tolerance. A library: a
  colleague's memory is never the source of a version number.

### Step 3. Write the initial canon

- **Who:** one owner per section (each section belongs to whoever uses it
  most).
- **Reads:** `00-brief.md`, `01-sources-of-truth.md`, the corpus.
- **Creates:** `02-canon.json`, with a schema in `05-contracts/`.
- **Does:**
  1. creates the sections with owner, version and status (`ready`,
     `provisional`, `pending`);
  2. records the canonical numbers: spelling by medium (table, prose,
     code, data file), unit, rounding, nature (fact or hypothesis), source;
  3. records the accepted variants, each with where it holds and why;
  4. records names, terms to prefer and terms to gloss (with the marker the
     validator looks for);
  5. records the rules that two roles could apply differently;
  6. leaves `pending` whatever is not yet known, without assumption.
- **Done when:** every section has an owner and a version; every number that
  appears in the brief is in the canon with its canonical spelling; no
  `pending` section has invented content; the schema validates.
- **Trap:** a canon that cites an old version of an asset while the artifacts
  use the new one. The canon is an artifact: it has an owner, a version and
  dependents, and the validator reads it on every pass.

### Step 4. List the artifacts and draw the graph

- **Who:** the orchestrator with the brief's owner.
- **Reads:** `00-brief.md`, `02-canon.json`.
- **Creates:** `03-artifacts.json` (or a table), with one record per artifact:
  name, owner, paths, depends on, schema, the command that generates it (if
  any), gates, resource (`code`, `agent`, `human`, `machine`).
- **Does:**
  1. starts from the target and walks backward: what does the target need? And
     that, what does it need?
  2. gives each artifact a single owner;
  3. turns every owner decision into an artifact with resource `human`, which
     the artifacts that depend on it depend on;
  4. marks as "proposed" the artifact that does not yet have a file, without
     making it a dependency of one that already exists;
  5. computes the topological order.
- **Done when:** the topological order exists (the graph is acyclic); every
  artifact has exactly one owner; every artifact has at least one gate (at
  minimum "exists and is not empty", and that alone is a sign that the real
  gate is still missing); every owner decision is an artifact; every artifact,
  except the target, has at least one consumer.
- **Trap:** the note that has nowhere to go. A finding lands on the nearest
  artifact because the right target is not in the graph, and the fix misses
  its origin. In the prior instance, several notes of the v2 round went to
  the nearest artifact because the right target (canon, concept, legal
  opinion, engine) was not an artifact in the graph; the more the graph
  covers, the better the notes hit their origin (step 16 of the case)
  [prior:000-av-production]. A vehicle: a homologation doubt routed to the
  CAD owner because no artifact holds the regulation reading. A book: a
  fact-check note parked on the chapter because the claims register is not an
  artifact.

### Step 5. Write the role cards

- **Who:** the orchestrator; each card is reviewed by whoever will perform the
  role.
- **Reads:** `03-artifacts.json`, `02-canon.json`.
- **Creates:** `04-roles/ROLE.md`, one per artifact owner, with the seven
  fields (decides, does not decide, inputs, outputs, exit gate, notes it emits,
  code-conversion degree), plus "questions it always asks" and the base prompt
  that the orchestrator hands to the agent.
- **Does:**
  1. for each owner in the table, writes the card;
  2. in "does not decide", writes explicitly the neighboring decisions that the
     role would be tempted to make, and whose they are;
  3. in "notes it emits", writes the typical target and severity;
  4. in "degree", chooses (a), (b) or (c) and says what the code does, and
     names the executor of the role: a person, code, or a kind of language
     model (fast and inexpensive for mechanical, fully specified roles; the
     strongest available for design, planning and hard reasoning). A role
     that audits another gets a model different from the one that produced the
     artifact, ideally from another family, because that is what makes the
     second look independent [hypothesis] (the rule of the principle,
     section 2, with the one datum against it: experiment E1). The round
     record names each executor by family
     (a letter stable across the material) and effort, never by model
     identifier; the map from letter to identifier stays with the owner,
     outside the material. A route or an alias is not a family: check what
     each name maps to before calling two executors different;
  5. checks exclusivity: no decision in "decides" of two cards.
- **Done when:** every artifact owner has a card; every card has the seven
  fields; no decision appears in "decides" of two cards; every role has an exit
  gate, emits at least one type of note and has a named executor; no auditing
  role shares an executor with the role it audits.
- **Trap:** a role compensating for another's defect. When a downstream
  consumer silently works around an upstream defect, the defect stays and the
  workaround is lost. In the reference case, a parameter declared in the
  request reached the output attenuated: the engine delivered less than was
  asked, and the fix was made in the engine, which began applying the
  intensity to the farthest layer; the pseudocode of the role that requests
  the effect says that, when the engine lacks the requested component, it
  must not improvise and must emit a note to the owner of the request
  (sections 1.10 and 4.14 of the case) [prior:000-av-production]. A vehicle:
  the test driver who "fixes" a misaligned fixture by holding the part by
  hand. "Does not decide" exists so that the defect returns to whoever has
  it, instead of being compensated downstream.

### Step 6. Write the contracts

- **Who:** the owner of each artifact that passes between roles, reviewed by
  the engine owner.
- **Reads:** `03-artifacts.json`, `04-roles/`.
- **Creates:** `05-contracts/ARTIFACT.schema.json` (or the schema format of the
  domain) and, for each schema, one valid example and one invalid example.
- **Does:**
  1. chooses, for each artifact, the format that a program reads without
     interpreting (data, not prose, wherever possible);
  2. writes the schema rejecting unknown fields and ambiguous values;
  3. writes the invalid example with the domain's most likely ambiguity and
     confirms that the schema rejects it;
  4. marks as "free text, degree (c)" the artifact that does not yet have a
     schema, and writes what is missing to have one.
- **Done when:** every artifact consumed by another role has a schema or is
  marked "free text"; every schema rejects its invalid example; validation runs
  in seconds, before any expensive work.
- **Trap:** the ambiguous position key. The key that fixes where a part lands
  has to be unique at the moment of the assembly, or the assembler picks an
  occurrence and does not tell which. In the reference case, the trail left
  15 s early in v3 because new text introduced another occurrence of the key
  that anchored its position, and nothing rejected the repeated key
  [prior:000-av-production]. A vehicle: two parts of the wiring harness carry
  the same connector code and the line picks one. A library: two public
  functions with the same name in different modules, and the build binds one
  of them. Hence the rule: an ambiguous position key is a contract error,
  caught before the expensive step runs.

### Step 7. Define the gates

- **Who:** the owner of each artifact proposes; the domain verifier checks the
  magnitude; the project owner approves the limits that come from the brief.
- **Reads:** `03-artifacts.json`, `05-contracts/`, `02-canon.json`,
  `00-brief.md`.
- **Creates:** `06-gates.md`, with a table with the columns Gate, Artifact,
  Magnitude, Limit, Justification, How it is measured (code, agent, human); and
  the code of each gate of degree (a) or (b).
- **Does:**
  1. for each artifact, asks "which measurement, if wrong, would make the target
     fail?" and writes the magnitude;
  2. writes the limit and, next to it, the justification with the origin
     (method, prior, brief or hypothesis) and why that number and not another;
  3. gives every signal gate a magnitude limit on both sides (an absurd value
     also rejects, because it signals a broken instrument);
  4. measures what the system delivered, not the parameter requested;
  5. separates "rejects" from "tool failure": a tool that does not run returns
     its own code, never an empty list;
  6. sets a cap on notes per gate, so that a gate that rejects everything does
     not drown the note ledger;
  7. tests each gate with a known perturbation: it has to reject;
  8. never lets a limit inherit a prior's number: a `[hypothesis]` limit may
     cite the prior as support, never as the limit itself.
- **Done when:** every gate returns a magnitude; every limit has a justification
  with an origin; every code gate rejected its known perturbation; the
  non-measurable criteria are marked "contract + agent", with the agent named.
- **In the reference case:** the cap is 50 notes per gate and a tool that fails
  exits with code 3 (facts about that prior, not limits for a new instance)
  [prior:000-av-production]; the drift gate between two representations of
  the same content has a limit of p95 ≤ 0.15 s (a fact about that prior, not
  a limit for a new instance).
- **Trap:** the gate that measures the instrument. A gate compared against a
  reference that is itself wrong rejects good work and passes bad work, and
  only a second instrument catches it. In the reference case, the drift came
  out at p95 of 0.546 s and rejected the target, but the error was in the
  reference measurement used as the baseline; once the instrument was fixed,
  v2 passed with 0.10 s [prior:000-av-production]. A vehicle: a correlation
  gate judged against a simulation that was itself misaligned. A library: a
  speedup gate measured on a node other than the pinned one.

### Step 8. Write and freeze the rubric

- **Who:** the owner, with whoever will review; never whoever will produce,
  alone.
- **Reads:** `00-brief.md`, `06-gates.md`.
- **Creates:** `07-rubric.md` and `07-rubric.sha256`.
- **Does:**
  1. chooses from six to ten dimensions that cover what the brief promises and
     what the gates do not measure;
  2. writes, for each dimension, anchors for scores 1, 3 and 5;
  3. writes the severity scale of the findings (`low`, `medium`, `high`,
     `blocking`) with examples from the domain;
  4. writes the verdict rule as a function of the scores and the findings, with
     the three values (`rejected`, `accepted with conditions`, `accepted`),
     starting from the "Verdict rule" template in this recipe;
  5. writes the report format: verdict; scores by dimension; findings by
     severity; verified and correct; not verified; out of scope; from the second
     round on, the item-by-item table of the previous round (resolved, partial,
     remained, worsened); notes in the contract;
  6. records the hash.
- **Done when:** the rubric has dimensions with anchors, a severity scale, a
  mechanical verdict rule and a report format; the hash is recorded before the
  first review; the round record names who wrote it (`rubric_author`).
- **Trap:** a rubric invented anew each round. Without it, there is no saying
  whether v4 is better than v3. In the reference case, the five reviews of
  its first pilot used the same rubric (the part of its method document on
  that pilot, end to end) [prior:000-av-production]; a rubric that holds
  across versions is what lets a round count how many of v1's findings v2
  resolved. A vehicle: two design reviews that score
  different dimensions cannot be compared. A library: a review that invents
  its own dimensions re-argues every round what was already settled.

### Step 9. Build the validator

- **Who:** the verifier (maintains the instrument); the validator runs
  it.
- **Reads:** `02-canon.json`, `03-artifacts.json`.
- **Creates:** `08-validator/rules.md` (what it checks, with
  severity), the code, and one test per rule with a case that must pass and one
  that must be rejected.
- **Does:**
  1. lists what two artifacts could say differently: numbers, names, terms,
     versions of assets and dependencies, units, identities;
  2. for each item, writes the rule, the severity and the target of the note
     (the owner of the artifact where the defect originates, or the canon
     section);
  3. makes the validator read the canon as data, with no list of its
     own;
  4. makes the report deterministic: no date, relative paths, sorted;
  5. makes the validator refuse a canon of a different schema version
     than the one it consumes.
- **Done when:** two runs on the same input give an identical report; every rule
  has both test cases; the validator refuses the canon of a different
  version.
- **In the reference case:** in the v2 round, the validator gave 38
  notes, 2 of them high, and both were false [prior:000-av-production]; the two
  rules were fixed at the root (a digit attached to a letter is not a number; a
  hypothesis on the sources card does not require a seal).
- **Trap:** trusting the eye for consistency. Nobody checks by eye, across dozens
  of parts, that a number never changed its spelling.

### Step 10. Build the assembly engine

- **Who:** the engine owner (an engineering role, or the orchestrator if the
  engine is small).
- **Reads:** `03-artifacts.json`, `05-contracts/`, `06-gates.md`,
  `08-validator/`.
- **Creates:** `09-engine/`: the graph core (state, hash per artifact, plan,
  execute), the note router, the assembly of the target and the tests.
- **Does:**
  1. computes the content hash of each artifact as sha256 over the canonical
     form of the file — UTF-8 bytes, the whitespace at the end of each line
     normalized, a single final newline, and no reordering of lines or keys —
     with no modification date, cache or stamp fields;
  2. plans: each artifact comes out `current`, `stale`, `missing`, `returned` or
     `escalated`, with the reason;
  3. executes only what is stale, in topological order, and runs the gates on
     each output;
  4. routes the notes: refuses a target the graph does not know, deduplicates by
     identity (target, severity, text, origin, evidence), writes to a ledger that
     only grows; only `high` and `blocking` return the artifact;
  5. counts rounds per artifact and escalates to the owner once the maximum is
     exceeded;
  6. assembles the target validating all the contracts before the expensive
     work, and names the output with the version label;
  7. writes, per role, the code-conversion degree and what the code does.
- **Done when:** assembling twice with the same inputs gives the same product
  (or the source of nondeterminism is declared and isolated); an invalid
  contract fails before the expensive work; the output carries a version label;
  the router refuses a note with an unknown target.
- **Trap:** the namesake file. Two files with the same name, one from an old
  version, and every reader silently picks one of them. In the reference case,
  three final files with the same name, one from an old version, were the high
  process finding of the v2 review, and the automatic reviewer probably read
  the old version's file (inference recorded by the review itself, step 15 of
  the case) [prior:000-av-production]. A vehicle: two drawings with the same
  part number, one of them superseded. Hence the version label in the name of
  every output.

### Step 11. Make the whole first version and review it

- **Who:** all roles, quickly; the independent reviewer right afterward.
- **Reads:** everything that the previous steps created.
- **Creates:** `v1/` (the whole target, end to end), `review/v1-report.md` and
  `review/v1-notes.json`.
- **Does:**
  1. produces all the artifacts, even bad ones, instead of polishing the first
     ones;
  2. passes the gates that already exist, without waiting for those that are
     missing;
  3. assembles the target;
  4. hands the reviewer only the files and the rubric, never the reasoning of
     whoever produced them, and records in the dispatch the effective
     output limit of the reviewer's executor and the reason its generation
     ended: an ending for length, or a report that lacks a section of the
     format, is a tool failure and produces no verdict (one such report,
     which stopped at a limit the dispatch had not declared, is recorded in
     experiment E1 of `60-experiments.md`);
  5. imports the review's notes into the ledger.
- **Done when:** every artifact in the graph exists; the target assembled; the
  review report follows the rubric's format; the notes entered the ledger
  without refusal.
- **In the reference case:** the v1 review gave 3 blocking, 4 high, 12 medium
  and 12 low [prior:000-av-production], and four of the highs were things that
  no gate measured; that is what v1 is for.
- **Trap:** polishing v1. Its goal is to discover what is missing to be
  measured; each day spent polishing is a day without knowing what the review
  will find.

### Step 12. Run the round loop

- **Who:** the orchestrator; each owner answers their own notes.
- **Reads:** the report and the notes of the last review, the validator's report, the graph state.
- **Creates:** `review/vN-report.md`, `review/vN-notes.json`,
  `review/vN-replies.md`, new gates and rules with tests, and one entry in
  `lessons.md` per round.
- **Does:**
  1. classifies each finding:
     - **product defect**: note to the artifact where it originated;
     - **regression that escaped every gate**: first creates the gate (which
       rejects the current version), then fixes;
     - **false positive**: fixes the instrument's rule at the root, with a test
       that reproduces the case, and redoes the previous round to prove that no
       real finding disappeared; never loosens the limit;
  2. imports the notes; the router refuses an unknown target;
  3. generates the work orders by wave, in graph order, with each wave's fronts
     in parallel;
  4. each owner answers note by note: done (where), partial (what is missing),
     contested (reason) or out of scope (for whom);
  5. the engine recompiles what is stale; the gates run; the validator
     runs;
  6. the reviewer reviews with the same rubric and makes the item-by-item table;
  7. records in `lessons.md` what the round taught and what became code,
     contract or gate.
- **Done when:** every `high` or `blocking` note has a reply; every new gate has
  a test and rejected the version that motivated it; the item-by-item table of
  the previous round is in the report; `lessons.md` has the round's entry.
- **In the reference case:** the 31 findings of the review of v1 and 18
  notes of the validator became 73 notes, imported in the v2 round
  [prior:000-av-production] (the prior gives the three counts and no
  arithmetic between them); they were answered by role in waves. Its step
  14 counts 38 notes of the validator in the v2 round and does not
  reconcile the 38 with the 18.
- **Trap:** the duration of the round growing without the notes falling. It is a
  sign that the loop fixes symptoms and not origins.

### Step 13. Declare the stop and record the open notes

- **Who:** the owner declares; the orchestrator records.
- **Reads:** the brief (provisional criterion), the last review.
- **Creates:** the stopping criterion line in the brief (before the last round)
  and `open-notes.json`.
- **Does:**
  1. the owner declares the criterion before the last round (for example: "stop
     when the review gives accepted" or "stop at vN, whatever the verdict");
  2. the review of the last version does not open another round: what it finds
     becomes an open note, in the contract, awaiting a decision to resume;
  3. checks that no non-negotiable in the brief was left as an open note: a
     violated non-negotiable is not an open note, it is an undelivered target.
- **Done when:** the criterion is written in terms of rounds or verdict (not
  calendar); `open-notes.json` validates against the contract; no non-negotiable
  is among the open notes.
- **In the reference case:** v5 was the last version, with the verdict
  `accepted` (in that prior's own vocabulary, "publishable") and 26 low open
  notes [prior:000-av-production].
- **Trap:** rounds without end. Every round finds something; without a declared
  stop, production does not finish.

### Step 14. Write the case method document and register the instance

- **Who:** the orchestrator, with the role owners.
- **Reads:** everything, especially `lessons.md` and the replies of each round.
- **Creates:** `method-TARGET.md` (the case method document, named after the
  target) and `priors.json`.
- **Does:**
  1. writes the ideas, each with the concrete defect it prevents and where it
     lives (code, contract, card);
  2. draws the graph and the dependency table;
  3. writes the step-by-step with the real commands;
  4. writes, per role, the work's pseudocode and the conversion degree, with
     what is missing to move up a degree;
  5. lists the owner decisions, what is not automated, the known false
     positives and the stopping criterion;
  6. marks `[unverified]` whatever was not checked against a file or a
     measurement;
  7. registers the instance in `priors.json`: id, status (`executed` or
     `designed`), the method document's path relative to its own repository
     root, and the sha256 that pins it.
- **Done when:** the sections above exist; every claim points to a file or a
  measurement, or is marked; the known false positives have a status (fixed,
  open, limit documented); the instance is registered and pinned.
- **Trap:** a document that repeats the READMEs. It says the why and the order,
  and points to where the detail is.

## Templates to copy

### Artifact record

```text
{ "name": "...", "owner": "ROLE", "paths": ["..."], "depends_on": ["..."],
  "schema": "05-contracts/....schema.json" or null, "command": "..." or null,
  "gates": ["..."], "resource": "code" | "agent" | "human" | "machine",
  "proposed": false }
```

### Note

```text
{ "target_artifact": "name in the graph", "severity": "low|medium|high|blocking",
  "text": "what is wrong and what is expected", "origin": "role or instrument",
  "evidence": "file, excerpt, measurement", "round": N }
```

### Gate row

```text
| gate | artifact | magnitude (unit) | limit | [origin] why this number |
```

### Verdict rule

Starting point for step 8; the instance may change the numbers, as long as the
rule stays mechanical and is frozen with the rubric.

```text
if there is a blocking finding or any dimension has a score ≤ 2:
    verdict = rejected
else if there is no high finding and all dimensions have a score ≥ 4:
    verdict = accepted
else:
    verdict = accepted with conditions
```

### Instantiation table

The fourteen fixed rows are in the [canon](01-canon.md) (section "Fixed
lists"). Fill each one with the domain's content; none stays empty, and a row
that would serve any target is badly filled in.

## Signs that the instance is wrong, and which step catches them

| Sign | Step that should have caught it |
| --- | --- |
| A role approves its own artifact without a gate | 5 (exit gate) and 7 |
| The review of round N is not comparable with that of N-1 | 8 (frozen rubric) |
| A finding was "resolved" by loosening a limit | 12 (root-cause fix) |
| Two artifacts state different numbers for the same fact | 3 and 9 |
| The owner gets a question the brief already answered, or a role decided what the card said "does not decide" | 1 and 5 |
| The round gets longer and the notes do not fall | 12 (origin, not symptom) |
| Someone redid by hand what the graph should have recompiled | 4 and 10 (hash) |

## When not to use

The method costs, per round, one production, one independent review and the
maintenance of the instruments; the costs measured so far, those of review
runs, are recorded with experiments E1 and E3 in `60-experiments.md`. In E1,
about 58,000 input tokens (most of them the prior's method document the reviewer
checks against, not the guide of about a thousand words under review),
55,000 to 66,000 output tokens and 8 to 10 minutes for one executor, about 4
minutes (indicative) for one of another family [experiment:E1].
In E3, without the rubric and the card, about 56,000 input tokens, 41,000
to 46,000 output tokens and 10 to 13 minutes for the first executor
[experiment:E3].

It pays off when erring is expensive [hypothesis]. Stated as a condition,
still unmeasured: the probability of an error times its cost has to exceed
the cost per round times the rounds until the stop; and the baseline to
beat, a strong model with a checklist and continuous integration, is the
control arm of experiment E2, designed and not run.

For a throwaway draft, use only steps 1, 3 and 11 (brief, canon, one version
and a read from outside); if the draft becomes a real target, resume from
step 2.
