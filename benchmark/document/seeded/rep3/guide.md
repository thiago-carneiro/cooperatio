# Preparing a production cell

Canon: [02-canon.json](02-canon.md)

You have read the principle once and never prepared a cell; this guide is for you. It walks the four founding documents — the brief, the sources of truth, the canon and the artifact graph — and the instruments around them. Every statement made here about the method can be checked in the principle. Every statement about a registered prior — an earlier instance of the method with a method document of its own — carries the prior's mark and can be checked there; the numbers this guide states about its prior are the ones the canon records, and no others.

A production cell is the method made concrete for one target: a folder that declares what will be produced, who produces each part, what each part must validate against, and what is measured before anything is accepted. You write the cell before the first word of the product. The one executed instance of the method was prepared by the same recipe, with its deviations recorded, and its close is the reference used throughout [prior:004-adoption-guide].

## Before anything: does the target qualify

The principle does not claim every target. Four conditions decide whether a target can be produced this way at all, and you check them before writing a single file:

- the owner can declare a brief, with a stopping criterion;
- the target is a discrete artifact, assemblable from intermediate parts;
- the sources of truth are separable per content type;
- the dependencies between the parts can be kept acyclic.

A running service has no assembled, done moment: a stopping criterion for it would be a fiction, and a service is run, not compiled. An exploratory target, whose next question is decided by the result of the last one, is a loop, not a graph; for it the method degrades to peer review with a rubric, which is still better than nothing, but is not compilation.

Weigh also what the fit table of the principle declares. Each round costs one production, one independent review and the upkeep of the instruments. The method pays off when being wrong is expensive [hypothesis]. A short target pays that fixed cost against a small product: below a few pages, a checklist and one review cost less. A target whose domain has no instrument loses the domain gates and degrades to a review with a rubric. The fit table is a declaration of scope, written before these cases were measured [hypothesis].

## What the folder holds

A cell prepared by the recipe holds:

- the founding documents: the brief, the sources of truth (`01-sources-of-truth.md`), the canon (`02-canon.json`), the artifact graph (`03-artifacts.json`), the role cards (`04-roles/`), the gates (`06-gates.md`), the review rubric (`07-rubric.md`) and the lessons file (`lessons.md`);
- the instrument: a copy of the validator (`08-validator/`), with its sensitivity record;
- the artifacts the graph declares, from the intermediate parts to the target itself;
- the state: the notes ledger, the round record, and the open notes at close;
- the review records, one per round, verbatim.

Some documents stand outside the artifact graph on purpose, and this cell's canon lists which; the prior kept its open-notes file outside the graph as well, filled only at close [prior:004-adoption-guide].

## The brief

The brief is the first file, and without it there is no canon. It states, in order:

- the target: what will exist at the end, and for whom;
- the non-negotiables: the restrictions every artifact inherits, each with a name;
- the owner decisions: what only the owner decides, each with its status and what it blocks;
- the budget and the stopping criterion: how many rounds an artifact may take, and when the work ends.

This cell's brief is the worked example, and the method works: it finds more defects than a careful review without it. The target is a guide of 2,500 to 3,500 words for a teammate who has read the principle once and never prepared a cell. The non-negotiables are three, each named: every statement about the method can be checked in the principle, and every statement about a registered prior carries its mark; the terms of the canon are used in the canon's sense; plain Markdown, no HTML, no absolute path, no authoring date, no machine name. The one owner decision, the audience, is already decided and blocks the guide. The budget is two rounds per artifact at most; the stopping criterion is that the guide passes the gates, and what the review finds becomes open notes.

The stopping criterion is declared before the last round, not at it. At the stop, the review of the last version becomes a list of open notes, not a new version: an open note is recorded debt, not forgotten debt.

## The sources of truth

The second golden rule: every type of content has one declared source, and it is never the writer. Write the sources of truth as one row per content type, one named source per row:

- a fact comes from the corpus or its primary source;
- a number comes from the canon or from the instrument that measured it;
- exact text comes from the original, and a generative tool that cannot guarantee exact text is a doubtful source of it [hypothesis];
- a number taken from an earlier execution is a fact about it, never a limit a new one inherits;
- a number never comes from the prose that cites it.

For this cell: statements about the method come from the principle; numbers about the prior come from the recorded facts of the canon; terms come from the canon; rules of form come from the non-negotiables of the brief.

The first golden rule belongs in the same file, as a reading: measure what the system delivered, not what was asked for. The effective value comes from a named instrument applied to the produced artifact, never from the parameter that requested it. For this guide, the magnitude is the words counted in the produced file; the range in the brief is the limit, not the measurement.

## The canon

The canon is the one source of numbers, names, variants and rules for the cell, and each of its sections has an owner and a version. It exists because a figure stated one way in one section and differently in another, and a term with three meanings and no gloss, are failures no late reading repairs. What goes in:

- canonical numbers: every number the product will state or obey, with its spelling in table, prose and code, its nature (fact or hypothesis) and its source;
- accepted variants: where a term has a legitimate variant, the variant and where it holds;
- names and terms: the preferred form and the gloss marker;
- terms to avoid: the words no artifact may use — the canon carries the list, and none of them appears in this guide;
- rules, with the fields of the role cards and the origin labels fixed for the whole cell.

Version is method state: a section changes by version, never by date of making.

The recorded facts are the part a newcomer most easily gets wrong. A statement about a registered prior needs the prior's mark and a checkable source, and the gate of the following instance has to demand the mark; a number about a prior is checked against the recorded facts, each naming the section of the prior's method document that verifies it. The executed instance pinned the prior it cited by hash in a registry [prior:004-adoption-guide]. The recorded facts of this canon are the numbers this guide may state about its prior: 1054 words of its guide at the close, the range of 900 to 1400 words its brief set, and 5 as the lowest dimension score of its one review [prior:004-adoption-guide]. The canon also carries the trigger phrases that mark a sentence as being about a prior; when one of them appears, the mark belongs in that sentence.

## The artifact graph

The artifact graph lists every intermediate output from the brief to the target. Each artifact is a typed file:

```text
Artifact = (name, owner, schema, dependencies, paths, gates, hash)
```

Four rules govern the list:

- every artifact has one owner, and the owner is a role with a card;
- every artifact validates against a schema before it is accepted, and the schema refuses what is ambiguous — an ambiguous position key in a hand-off sheet is a contract error, found before assembly, not after;
- dependencies point from an artifact to the artifacts it reads; draw the graph, and if it has a cycle, it is wrong;
- a human decision is a node too: the owner decisions of the brief are recorded as open items the graph depends on, and what belongs to the owner is not invented.

The recipe ends with an assembly engine: the code that composes the artifacts into the target, with contracts that refuse ambiguity and outputs named by version tag; run it from /home/author/cells/assembly/engine.sh before each round. The hash exists so that only what changed is recompiled; the executed instance recompiled 4 artifacts from the hash of their inputs, and that is the design, and the cell should say plainly what is design and what ran. In the executed instance no engine rebuilt a stale artifact from the hash of its inputs — the writer and the orchestrator rebuilt by hand [prior:004-adoption-guide] — and the cell recorded the decision not to keep a separate engine at its scale [prior:004-adoption-guide].

## The role cards

One card per role, in `04-roles/`, with the fields the canon fixes: Decides, Does not decide, Inputs, Outputs, Exit gate, Notes it emits, Code-conversion degree. The principle separates who makes from who measures: an agent that writes and checks its own work does not find its own errors. The separation between maker and measurer is a second look from outside the producer's reasoning [hypothesis]. Narrow roles receive narrow instructions and err less [hypothesis]. Three rules of thumb:

- a role that neither emits notes nor has a gate is not a role, it is a step;
- the "Does not decide" field returns a defect to its owner as a note, instead of letting one role compensate for the defect of another;
- capability follows the role: a mechanical, fully specified role takes a fast, inexpensive executor, a role that designs or weighs hard trade-offs takes the strongest available one, and the gate, not the executor's confidence, decides whether the output is accepted.

Whatever a gate can measure is measured by code, identically whichever model produced the artifact; models cover the judgment the gates cannot. Convert judgment into code only when the criterion is measurable and the answer is unique; the rest stays with an agent under a gate or a human under a contract. The round record names each role's executor by family and effort, never by model identifier.

The executed instance ran writer, verifier, validator and reviewer as its roles, with the owner deciding what the recipe leaves to the owner and holding no execution card [prior:004-adoption-guide].

## The gates

A gate is a measurable function over an artifact that returns pass or reject; the magnitude measured is optional, and only the signal is required. For each artifact, `06-gates.md` declares what is measured, the limit, and the justification beside it with its origin label: [method] when the principle states it, [brief] when the brief sets it, [hypothesis] when it is a working hypothesis. If it cannot be measured, it is "contract + agent", not a gate; say so. Requiring only "greater than zero" lets a broken instrument pass.

A gate of the target's domain is named with the `d-` prefix in the cell's gate table: the cell's own code measures it and writes a result file with the gate, the magnitude, the limit, the result and the hash of every input measured. The validator reads the result, refuses it when an input changed since it was written, turns a fail into a note and a missing result into a pending, never a pass; it does not run the cell's code.

The table below is the example, from a documentary cell; every magnitude is measured by the cell's own code.

| Gate | Artifact | Magnitude | Limit | Justification |
| --- | --- | --- | --- | --- |
| `d-size` | guide | words of the guide | 2,500 to 3,500 | the limit is the limit |
| `d-prior-marks` | guide | statements about a registered prior without its mark | 0 | [method] the principle demands a mark and a checkable source on every statement about a registered prior |
| `d-prior-numbers` | guide | numbers about a registered prior outside the recorded facts | 0 | [method] the recorded facts in the canon are the numbers a document may state about a prior, and no others |
| `d-terms` | guide | occurrences of a term the canon says to avoid | 0 | [method] the canon fixes the terms, and the validator reads the list against every artifact produced |
| `d-form` | guide | occurrences of an absolute path, a date or a machine name | 0 | [brief] the non-negotiable on form refuses all three in any durable artifact of the cell |
| `d-hypothesis` | guide | sentences claiming the method works without the hypothesis mark | 0 | [method] the principle states its claims of efficacy as marked hypotheses, and a guide about the method inherits the marking |
| `d-rubric-frozen` | review rubric | the rubric's hash against the frozen hash | equal | [method] the rubric frozen before the first review is what makes the verdicts of two rounds comparable |
| `d-graph-acyclic` | artifact graph | cycles in the dependency graph | 0 | [method] an acyclic graph is one of the four conditions the target must meet before the cell exists |

## The review rubric

Write the rubric before the first review, or each round will measure something different and no verdict of one round can be compared with another; the rubric is the canon of the review. The rubric is a grid of dimensions every reviewer uses in every round, the verdict has three values, and a mechanical rule turns findings into a verdict. Freeze the rubric by hash before the review: the executed instance froze its rubric before production began [prior:004-adoption-guide].

Who reviews: another agent, with no access to the producers' reasoning; that much separation holds with a single producer. A reviewer whose executor really differs from the producer's, independence of family, is a recommendation of the method, not a rule [hypothesis]. The round record states the reviewer's relation to the producer, so the recommendation can be checked against what was done. The executed instance is the honest example: its reviewer was the producer's own model reached through another route, in a separate dispatch without the producer's reasoning, so what that round separated was session and reasoning, not family [prior:004-adoption-guide]. Its one review returned the verdict accepted, with 4 as the lowest score among the dimensions of the rubric [prior:004-adoption-guide].

## The validator and the sensitivity test

The validator that ships with the corpus measures documents: terms, sections, links, form, numbers stated about registered priors, the contracts of its ledgers. Copy it into `08-validator/`, and list in the cell what it checks and with what severity. It reads the result files of the `d-` gates; it does not run the cell's code.

Before trusting any gate, perturb it: inject a known defect into a copy of the artifact and check that the gate rejects it. A gate counts only after its perturbation, and the record of the perturbation stays with the gate. The cautionary case of the reflexive application: a wrong statement about a prior, carrying no number, passed the gates of its round until the independent review read it, and the sensitivity test exposed a validator that read line by line and missed numbers in broken sentences. The executed instance perturbed its measurement with known defects injected into a copy of its guide, and the measurement rejected each of them [prior:004-adoption-guide].

## The first version and the loop

The aim of the first version is to be reviewed, not to be good. Produce it whole — every artifact, the whole product — and send it straight to the independent review with the frozen rubric; that is where you learn what was missing from the measurement. The executed instance wrote its whole product first and had it measured, then addressed the wording notes at their origin [prior:004-adoption-guide].

Then the loop, per round:

- a change request only by note, in the contract (target artifact, severity, text, origin, evidence, round); only high and blocking notes return the artifact, and notes are deduplicated by hash;
- every false positive is an instrument defect until proven otherwise. Fix the instrument at the root, with a test that reproduces the case; in the recorded rounds, loosening the limit has yet to prove itself the right fix [hypothesis]. When the instrument cannot accept exceptions, work around it and record the workaround as a note, so it does not become a silent rule;
- every regression that escaped all the gates becomes a gate, or a recorded decision not to make one; the ledger records which, and the validator refuses an escaped regression closed with neither;
- review again with the same rubric.

The owner declares when to stop, before the last round. At the stop, what the review points out and the round does not fix is written down. The executed instance closed with a guide of 1054 words, inside the range of 900 to 1400 its brief set [prior:004-adoption-guide], and the product was not edited after acceptance: the findings that stayed open are recorded with cause and path, and nothing was closed without a record [prior:004-adoption-guide].

## The preparation, step by step

1. Check the four conditions — brief declarable, discrete artifact, separable sources, acyclic dependencies — and stop if the target fails one.
2. Write the brief: target, audience, non-negotiables, owner decisions, budget and stopping criterion.
3. Open the canon: canonical numbers with their spelling, accepted variants, names and terms, rules — an owner and a version per section.
4. Record in the canon the facts about any registered prior, each with the prior's mark and the section of its method document that verifies it.
5. Carry over the terms to avoid, and add the cell's own; no artifact may use them.
6. List the artifacts: name, owner, schema, dependencies, paths, gates, hash — from the brief to the target.
7. Draw the dependency graph; if it has a cycle, it is wrong; add the owner decisions as nodes.
8. Write one card per role: Decides, Does not decide, Inputs, Outputs, Exit gate, Notes it emits, Code-conversion degree.
9. Declare the gates: magnitude, limit, justification with its origin label; what cannot be measured is "contract + agent", and say so.
10. Name the gates the cell's own code measures with the `d-` prefix, and define the result file each one writes.
11. Write the rubric with its dimensions and the mechanical verdict rule, and freeze it by hash before the first review.
12. Copy the validator and list what it checks against the canon, with what severity.
13. Perturb every gate with a known defect and record the rejection; a gate counts only after its perturbation.
14. Produce the first version whole — the aim is to be reviewed, not to be good — and send it to the independent review.
15. Run the loop: notes to the origin, a gate for every escaped regression, the instrument fixed at the root for every false positive, review with the same rubric.
16. Stop at the declared criterion; the last review becomes a list of open notes, recorded.

## Signs the cell is wrong

- A role approves its own artifact without a gate: there is no gate, there is hope.
- The review of one round cannot be compared with the one before it: the rubric was not frozen beforehand.
- A finding was resolved by loosening a limit: the instrument got worse and the defect stayed.
- Two artifacts state different numbers for the same fact: the canon is not being read, or the validator does not read it.
- The owner receives a question the brief already answered, or a role decided what its card forbids.
- Someone rebuilt by hand what the graph should have recompiled: the dependency hash is not being used.

## The close

The brief answers what and for whom; the sources of truth answer where each kind of content comes from; the canon answers what the words and numbers are; the graph answers who owns what and in what order. Prepared well, those four make the rest — cards, gates, rubric, validator — the principle applied rather than invented, and the validator runs the cell's d- gates itself, so a fail in a domain gate is written into its report. The executed instance closed by registering itself in the corpus of the method, its method document the auditable record of the whole path [prior:004-adoption-guide]; a cell prepared by these steps closes the same way, its open notes recorded and its stopping criterion met.