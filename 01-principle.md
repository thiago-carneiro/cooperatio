# The principle behind the method, generalized

Method version 0.5.0 (see `VERSION`; the history of the changes, in
`CHANGELOG.md`).

**Working hypothesis — two executed instances.** This document states the
idea that sustains the method, writes that idea as a formula and says how
to apply it to a target. It is not about any one kind of product, and it
does not claim every target: it holds where the target has (a) a brief
that an owner can declare, with a stopping criterion; (b) a discrete
artifact, assemblable from intermediate parts; (c) sources of truth
separable per content type; and (d) dependencies between those parts that
can be kept acyclic. Two executed instances and three designed instances
(not executed) stand behind what is here, and the scope of that support is
declared, not implied: both executions are documentary productions by the
same owner of this material (an audiovisual production method, owner-held,
and the adoption guide of this method itself), so the inter-domain instances
(car, text, HPC) carry the design, not a result — every rule below was born
from an error that cost a round or that a review or a critical panel found
[lessons], and the last column of the component table in section 4 gives a
typical example of the error each component prevents.

The second execution produced a guide of 1054 words, inside the range of 900
to 1400 its brief set, and its one review, in a separate dispatch without the
producer's reasoning, gave `accepted` [prior:004-adoption-guide]. That review
was first recorded as coming from another family; it came from the
producer's own model, through another route, so it separated the session
and the reasoning, not the family [prior:004-adoption-guide].

## 1. The idea in one sentence

**Producing a complex artifact is compiling a graph of typed artifacts, each
with an owner, a contract and a gate, in which separate roles communicate only
through artifacts and notes, quality is measured by what the system delivered
and not by what was asked for, every review is independent and comparable
between rounds, and every error that escapes becomes a new gate, until a
declared stopping criterion.**

Put another way: it replaces "one very capable agent does everything" with "a
small organization, with explicit contracts, in which intelligence is raw
material and code is the glue that composes, checks and remembers".

## 2. Why separate into roles, if a single model could do everything

Three reasons, each observed in practice, none measured against a production
without the roles [hypothesis]:

1. **An agent that writes and checks its own work does not find its own
   errors.** A first version is typically rejected by independent review with
   blocking findings that correspond to pending items the work itself had
   noted and let go. The separation between who makes and who measures is
   not bureaucracy; it is the only way to get a second look that does not
   share the same blind spots [hypothesis] (in the first round of the
   reflexive application, the separate review found the blocker that every
   gate let through [lessons]).
2. **Narrow roles receive narrow instructions and err less** [hypothesis]. The writer who
   only writes, with a glossary and a canon in hand, produces text that the
   validator approves; a model "doing everything" mixes text with layout
   and data-sourcing decisions and tends to leave all three half done.
3. **Contracts between roles make the error locatable.** When a section lands
   at the wrong position, the problem may be a position key in a hand-off
   sheet, written by one role and read by another. Without the contract, the
   symptom is "the end of the product came out wrong"; with it, it is "the
   position key is ambiguous", and it becomes a rule: an ambiguous position
   key is a contract error, found before assembly.

### Using several models across the roles

Separating roles also makes it possible to give each role a different
executor: a person, code, or a language model of a chosen kind. This is not
an optional extra; it is one of the cheapest ways to get the second look that
the first reason above asks for.

- **Capability follows the role.** A mechanical, fully specified role takes a
  fast, inexpensive model; a role that designs, plans or weighs hard
  trade-offs takes the strongest available one. The card says which, in the
  code-conversion degree field, and the gate (not the model's confidence)
  decides whether the output is accepted.
- **Independence needs a different model** [hypothesis]. The independent
  review, and any role that audits another, runs on a model different from
  the one that produced the artifact, ideally from a different family or
  provider, so that the two do not share the same blind spots. For
  high-stakes targets, two reviewers from different families look at the
  same product; where they disagree, the disagreement becomes a note, not a
  silent choice. The rule is a hypothesis, and the one datum is against it:
  in experiment E1 the producer's own model, in another session, caught 2 of
  2 injected defects, as the model of another family did, one run per cell
  [experiment:E1]. No recorded production round has met the rule with a
  frozen rubric (section 9). Whether it stays a norm, becomes a gate on the
  round record or is relaxed is a decision of the owner, still open.
- **Code is not a model.** Whatever a gate can measure is measured by code,
  identically whichever model produced the artifact; models only cover the
  judgment the gates cannot.
- **Contracts make models swappable.** Because roles hand off only through
  artifacts that validate against a contract, replacing the model behind a
  role must not change any other file. If it does, the contract is too loose.
- **The assignment is auditable.** The round record names the executor of
  each role by family (a letter kept stable across the material) and by
  effort, never by model identifier, so that a change in verdict can be told
  apart from a change of executor. The map from letter to identifier stays
  with the owner, outside the material, like an owner-held prior document: a
  product identifier is jargon that changes and leaks the provider, and the
  family is what the rule of independence uses. A route or an alias is not a
  family: whether two executors differ is checked on what each name maps to,
  never on the name. The price of this rule is declared: the letters are as
  good as the owner-held map, and the material alone cannot detect a
  mislabeled letter.

## 3. The formula

Let a target `A` (the final product), a brief `B` (what the owner wants and
the non-negotiable restrictions) and a corpus `F` (the facts, materials and
references available). The method is:

```text
A = Compile( Graph( Roles, Artifacts, Gates ), B, F )  until  Stop

where:
  Artifact   = (name, owner, schema, dependencies, paths, gates, hash)
  Role       = (responsibility, inputs, outputs, decides, does not decide,
                exit gate, notes it emits, code-conversion degree)
  Gate       = measurable function over an artifact that returns pass/reject
               with the magnitude measured, never only a signal
  Note       = (target_artifact, severity, text, origin, evidence, round)
  Canon      = single source of numbers, names, terms and decisions, with a
                version per section and an owner per section
  Review     = independent reading of the product with a fixed rubric,
               comparable between rounds, that returns notes and a verdict
  Stop       = criterion declared by the owner before the last round
```

And the loop:

```text
compile(graph, brief, corpus):
    canon ← extract(brief, corpus)                  # numbers, terms, names, rules
    repeat:
        for each artifact in topological order:
            if inputs changed (hash) or there is a high/blocking note against it:
                output ← owner_role.produce(inputs, canon, open_notes)
                for each gate of the artifact:
                    measure ← gate(output)          # magnitude, not only a signal
                    if rejected: note(artifact, severity, measure) ; return to owner
                validator.check(output, canon)  # terms, numbers, names, assets
        product ← assemble(final artifacts)
        review ← independent_reviewer(product, fixed_rubric)
        for each finding of the review:
            if it is an instrument defect (false positive): fix the instrument at the root
            if it is a regression that no gate caught: create the gate, then fix
            otherwise: note to the originating artifact
        if stopping_criterion: record open notes and exit
    until stop
```

## 4. The eleven components and what each one solves

| Component | What it is | The error it prevents (example) |
| --- | --- | --- |
| **Artifact graph** | Each intermediate output is a typed file with an owner, schema, dependencies and hash; the core recompiles only what changed | Work redone for nothing and, worse, work **not** redone when the input changed (a section keeps stale text because nobody knew its source outline had changed) |
| **Role cards** | Each role has a card: what it decides, what it does not decide, inputs, outputs, exit gate, notes it usually emits | One role compensating for the defect of another: the engine delivered less than the request asked, and the fix belonged in the engine, not in a workaround downstream; the card's "does not decide" returns the defect to its owner as a note, and the role never improvises |
| **Contracts (schemas)** | Every artifact validates against a schema before being accepted; the schema refuses what is ambiguous | Ambiguous position key in a hand-off sheet (a section at the wrong position); an unknown field in an input layer (the assembly refuses it at validation, not later); a free-text field that must not carry numerals containing one |
| **Gates with magnitude** | A gate returns the measure, and the limit is declared with a justification; requiring only "greater than zero" lets a broken instrument pass | Offset between two aligned parts of the artifact, measured against a reference that was itself wrong (the "rejected" offset was the instrument) |
| **Routed notes** | A change request only by note, with target, severity, evidence and round; only high and blocking return the artifact; deduplication by hash | Loose conversation between roles, a lost request, the same note three times |
| **Canon** | Single source of numbers, names, terms to avoid, accepted variants, rules; each section with an owner and a version | A figure stated one way in one section and differently in another; one term used with three meanings and no gloss |
| **Validator** | A verifier that reads all artifacts against the canon and emits notes by itself | An old version of an asset cited by the canon while the sections used the new one (a flood of high notes at once) |
| **Independent review with a fixed rubric** | Another agent, with no access to the producers' reasoning, measures the product with the same grid each round; the verdict has three values | The team approving its own work; and the impossibility of saying whether v4 is better than v3 when each review invents its own rubric |
| **Instrument fixed at the root** | A false positive is never "ignored"; it becomes a fix to the rule, with a test that reproduces the case, and the previous round is redone to prove that no real finding disappeared | An automatic reviewer of which 10 of 12 notes were false, in the second pilot [prior:000-av-production]; each false rule was fixed at the root, with a test per case |
| **Stopping criterion** | The owner declares when to stop: the review of the last version becomes a list of open notes, not a new version | Endless rounds; every round finds something |
| **Gate sensitivity test** | Before trusting a gate, inject a known defect and check that it rejects; a gate that only measures what is easy to measure lets the defect that matters through | The reflexive application of this principle: the gate checked numbers, the non-negotiable was "nothing about the case outside the source", and a wrong statement without a number passed through everything until the independent review; the sensitivity test found, before the review, a validator that read line by line and missed numbers in broken sentences [lessons] |

## 5. The golden rules, with the reason

1. **Measure what the system delivered, not what was asked for.** The
   effective value comes from a named instrument applied to the produced
   artifact, never from the parameter that requested it. Media profile: the
   pixel, the second, the byte — a parameter set to "medium" is a request,
   and the value the system applies may be a fraction of it. A vehicle: the
   measured mass and cycle time of the prototype, not the targets in the
   brief. A library: the benchmark on the pinned node, not the requested
   speedup.
2. **Every type of content has one declared source of truth, and it is never
   the writer.** A fact comes from the corpus or its primary source; a
   number comes from the canon or from the instrument that measured it;
   exact text comes from the original. A number taken from an earlier
   execution is a fact about it, never a limit a new one inherits. Media profile: exact text never comes
   from a generative tool that cannot guarantee it, and a number never comes
   from the prose that cites it.
3. **Every false positive is an instrument defect until proven otherwise.**
   The easy path is to loosen the limit; the right path is to understand why
   the instrument read wrongly. Of the times loosening seemed right, none
   was [hypothesis] (an observation of the recorded rounds, not a count).
   There is a third way out, legitimate when the instrument has no way
   to accept exceptions: work around it (swap the word, move the element) and
   record the workaround as a note, so that it does not become a silent rule.
4. **Every regression that escaped all the gates becomes a gate.** Before
   fixing the defect, create the detector; otherwise it comes back. A gate
   leaves the same way, deliberately: when its object is gone or its rule
   moved into a contract, the gate and its perturbation are retired
   together, with the reason written down.
5. **The contract refuses ambiguity before the expensive work starts.**
   Failing in 2 s at validation is better than failing in 10 min at assembly,
   and better still than not failing and delivering wrong.
6. **Dates, machine names and absolute paths do not enter a durable
   artifact** if anonymity or reproducibility matters. The checking date is a
   command-line parameter, not content.
7. **A human decision is an artifact too**: it has a name, it is recorded as
   an open item for the owner, and the graph knows it depends on it. What
   belongs to the owner is not invented.
8. **Convert judgment into code only when the criterion is measurable and the
   answer is unique.** The rest stays with an agent under a gate, or with a
   human under a contract. The three degrees (code / agent under gate /
   contract + gate) are explicit per role and rise over time.
9. **Version is method state; date of making is not.** v1 → v5 appears in
   the document; "made on such a day" does not.
10. **What the review points out and the round does not fix is written down.**
    An open note is recorded debt, not forgotten debt.

## 6. What changes from domain to domain and what does not

**Does not change:** the graph, the role cards, the contracts, the gates with
magnitude, the notes, the canon, the validator, the independent
review with a fixed rubric, the instrument fixed at the root, the declared
stop, the sensitivity test of the gates. These eleven are the method.

**Changes:** which roles there are, which artifacts there are, what each gate
measures, what the review rubric is, which sources of truth exist for each
type of content, and what code-conversion degree the domain already allows.

**What the distributed validator measures.** The validator that ships with
this material (`02-reflexive-application/80-validator/`) measures
documents: terms, sections, links, form, numbers stated about registered
priors, the contracts of its ledgers. A gate of a target's domain (the
speedup of a library, the mass of a vehicle, the cost of a part) is not one
it implements: such a gate is "contract + agent" (step 5 of the recipe in
section 7) or code the cell writes and runs itself, and this version has
no extension point that would let the validator run it or its sensitivity
test cover it. Whether the method ships a documentary validator or a
general framework with an interface for domain gates is a decision of
scope that belongs to the owner and is still open; until then, the
portability of the method across domains is a portability of vocabulary
and of structure, not of instrument [hypothesis].

The table below shows three instantiations, only to calibrate what an
"artifact", a "gate" and a "rubric" are in each case.

| Element | Physical product (car) | Long text (the world in 2027) | HPC software |
| --- | --- | --- | --- |
| Target | homologable vehicle | publishable manuscript | library with measured speedup and identical result |
| Sources of truth by content | requirement → brief; physics → simulation; standard → legal text; cost → supplier | fact → primary source; projection → declared model; style → guide | correctness → output oracle; performance → measurement on a pinned node; API → contract |
| Intermediate artifacts | requirements, architecture, CAD per subsystem, BOM, test plan | thesis, outline, chapters, glossary, source notes | spec, interface, implementation per module, benchmark, attribution report |
| Gates with magnitude | mass, cost, safety margin, emissions, cycle time | citation density, facts without source = 0, readability, size per chapter | byte-for-byte identity, speedup per arm, memory use, coverage |
| Review rubric | FMEA, design review per discipline, testing | blind reading by target audience, fact check, internal coherence | independent code review, benchmark reproduction by a third party |
| Validator | part nomenclature, tolerances, CAD versions | names, dates, numbers, terms | API names, units, dependency versions |
| What stays with the human | homologation, safety, target cost | thesis, tone, what is a projection | what to optimize, what is acceptable to lose |

## 7. Recipe to instantiate on a new target

In order, and each step produces a file:

1. **Brief**: what the target is, for whom, what is non-negotiable, what is
   the owner's decision. Without a brief there is no canon.
2. **Initial canon**: numbers, names, terms to avoid and to prefer, rules,
   with an owner and a version per section. Everything that two roles could
   write differently goes here.
3. **List of artifacts**: from the brief to the target, which intermediate
   files exist, whose they are, what they depend on, what schema they have.
   Draw the graph; if it has a cycle, it is wrong.
4. **Role cards**: one per role, with decides / does not decide / inputs /
   outputs / exit gate / notes it emits / conversion degree. A role that
   neither emits notes nor has a gate is not a role, it is a step.
5. **Gates**: for each artifact, what is measured and what the limit is, with
   the justification of the limit written beside it. If it cannot be
   measured, it is "contract + agent", not a gate; say so.
6. **Independent review rubric**: the grid of dimensions that every reviewer
   will use in every round, and the three verdicts. Write it before the first
   review, otherwise each round measures something different. What the
   review apparatus adds was measured once, for two defects checkable
   against a source, one run per cell, with the card and the rubric removed
   together: without them, two reviewers still named both defects injected
   into a product, but classed an invented fact about a prior as high and
   accepted the product with conditions; with them, the same finding was
   blocking and the verdict was `rejected` [experiment:E3]. Within that
   scope, the rubric is not what made the defects visible; the review
   apparatus, removed as a block (the rubric with its severity table and
   verdict rule, the reviewer card, the gates file and the framing of the
   dispatch), is what turned the finding into a verdict [experiment:E3].
   That the severity table and the mechanical rule are the parts that did
   it is a hypothesis the design does not separate [hypothesis].
7. **Validator**: the list of what it checks against the canon
   (terms, numbers, names, asset versions) and with what severity.
8. **Assembly engine**: the code that composes the artifacts into the target,
   with contracts that refuse ambiguity and outputs named by version tag.
9. **Quick first version, whole, and immediate independent review**: the aim
   of v1 is to be reviewed, not to be good. That is where one finds out what
   was missing from the measurement.
10. **Round loop**: notes → fix at the origin → new gate for each regression →
    instrument fixed for each false positive → review with the same rubric.
    Record what each round taught and what became code.
11. **Declared stopping criterion** and open notes recorded.
12. **Case method document**: ideas, graph, step by step, pseudocode per role
    with conversion degree, open items for the owner. It is what allows the
    next target to be instantiated faster.

## 8. Signs that the instance is wrong

- A role "approves" its own artifact without a gate: there is no gate, there
  is hope.
- The review of round N is not comparable with that of N-1: the rubric was
  not written beforehand.
- A finding was "resolved" by loosening a limit: the instrument got worse and
  the defect stayed.
- Two artifacts state different numbers for the same fact: the canon is not
  the single source, or the validator does not read it.
- The owner receives a question that the brief already answered, or a
  decision was made by a role whose card said "does not decide".
- The duration of the round grows without the number of notes dropping: the
  loop is fixing symptoms.
- Someone rebuilt by hand what the graph should have recompiled: the
  dependency hash is not being used.

## 9. Limits of the method

- It costs: per round, one production plus one independent review plus the
  maintenance of instruments. The costs measured so far are those of review
  runs, in experiments E1 and E3 of the reflexive application. In E1: about
  58,000 input tokens (most of them the prior's method document the reviewer
  checks against; the reviewed guide has about a thousand words), 55,000 to
  66,000 output tokens (90 to 98 % of them reasoning) and 8 to 10 minutes
  for one executor; about 4 minutes of wall time, an indicative figure, for
  an executor of another family [experiment:E1]. In E3, without the rubric
  and the card: about 56,000 input tokens, 41,000 to 46,000 output tokens
  and 10 to 13 minutes for the first executor, and again about 4 minutes,
  indicative, for the other [experiment:E3]. The cost of a production
  round and of the instruments was not measured.
- It pays off when being wrong is expensive [hypothesis]; for a throwaway
  draft, it is dead weight. As a condition, still unmeasured: the
  probability of an error times its cost has to exceed the cost per round
  times the rounds until the stop. The baseline to beat (a strong model with
  a checklist and continuous integration) is the control arm of experiment
  E2, designed and not run.
- **Evidence of efficacy is one-armed.** Everything the method found, it
  found under the method: no production of the same target ran without the
  gates, so there is no escape rate to compare, and the reflexive
  application cannot say what a careful reviewer without the method would
  have missed. The counterfactual is experiment E2, designed and not run;
  until it runs, the claim that the method finds more than its absence is a
  hypothesis [hypothesis].
- It depends on there being separate sources of truth per type of content.
  Where only opinion exists, the gate becomes a contract and the method
  degrades to "peer review with a rubric", which is still better than
  nothing, but is not compilation.
- Roles played by language models drift: the same card produces different
  outputs on different days. The contracts and the gates exist to absorb that
  drift; without them, the method does not work with agents.
- The method does not choose the target nor judge whether it is worth it.
  That belongs to the brief and the owner.
- A document like this one becomes corpus for the next instance: what it says
  wrongly about a registered prior enters the following documents as fact.
  Every statement about a registered prior needs the `[prior:<id>]` mark and
  a checkable source, and the gate of the following instance has to demand the
  mark.
- With a single agent playing several roles, the separation is weak: it
  writes the rubric that will judge it. The role that can be independent is
  the external reviewer: in session and reasoning always, in family only
  where its executor really differs (see the next two items). In the first
  round of the reflexive application, it was that review that found the
  blocker [lessons]. Where there is only one agent, at least the rubric and
  the review have to come from outside.
- Using several models does not by itself create independence: two models
  from the same family, trained on similar data, can share the same blind
  spots, and a model that sees the producer's reasoning inherits it. Where
  the models are interchangeable in practice, the rubric and the review still
  have to come from outside the producing run.
- Independence of family has not been exercised in production with a
  frozen rubric: in no round the round record of the reflexive application
  lists, nor in the one review of the second execution, did a reviewer with
  a frozen rubric come from another family than the producer's. The one
  exception, without it, is the reading review of family A in v0.4.1, which
  had no frozen rubric, no verdict rule and no execution
  [prior:004-adoption-guide] [lessons].
- The only reviews across families in the reviewer role, with a frozen
  rubric, are the runs of executor Y in experiment E1 [experiment:E1];
  experiment E3 ran the same executor without the rubric [experiment:E3].
  The critical panels that reviewed this material (the panels that reviewed
  v0.1.0, v0.2.0 and v0.2.3) had seats of several families, but no frozen
  rubric, no verdict rule and no line in the round record [lessons].

## 10. Ontological assumptions

The formula above is not neutral about what a target is. It assumes:

- **The target is a discrete, assemblable artifact.** It has a shape declared
  before the work starts and a moment at which it is done. A continuous
  process or an ongoing service has no assembled, done moment: there the
  stopping criterion would be a fiction, and the method does not apply — a
  service is run, not compiled.
- **The target decomposes into parts with acyclic dependencies.** An
  exploratory target, whose next question is decided by the result of the
  last one, is a loop, not a graph; for it the method degrades to peer
  review with a rubric, which is still better than nothing, but is not
  compilation.
- **Quality is measurable by instruments that do not include the
  producer.** Where only taste decides, every gate becomes a contract and
  the independent review becomes the only instrument.
- **The knowledge the target needs exists, or is produced by declared
  roles.** An emergent target — one whose content only exists after the
  audience reacts to it — cannot declare its sources of truth in advance;
  its canon would be written after the fact, which is not a canon.
