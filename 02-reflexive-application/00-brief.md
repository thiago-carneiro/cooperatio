# Brief of this production

One page. It says what this folder has to hand over, for whom, what is not
negotiable, what is an owner decision and when the production stops. The
terms follow the [canon](01-canon.md).

## Target

A set of documents that shows, as concretely as possible, **how to assemble
the production cell** that applies the method of `../01-principle.md` to any
target that meets the four conditions the principle states (a brief an owner
can declare, with a stopping criterion; a discrete artifact assemblable from
intermediate parts; sources of truth separable per content type; dependencies
between the parts that can be kept acyclic): brief, initial canon, artifact
graph, role cards, gates with magnitude and justified limit, independent
review rubric, validator, assembly engine, quick first version, round loop,
stopping criterion and case method document.

There are two layers:

1. **The generic recipe** (`10-generic-recipe.md`), a step by step that a
   person or an orchestrator agent executes, with the files each step creates
   and the "done" criterion of each step.
2. **Three designed instances (not executed)**, chosen because they differ
   from each other: a brand-new car (`20-instance-car.md`), a long text about
   the world in 2027 (`21-instance-text-2027.md`) and an HPC library with
   measured performance gain and identical result (`22-instance-hpc.md`).

## For whom

First, whoever is going to instantiate the method on a new target and did
not follow the reference case [prior:000-av-production]. Then, an orchestrator agent that receives the
recipe as an instruction. Both need to execute without asking what a term
means.

## Non-negotiables

- This production itself follows the method: brief, canon, artifacts, cards,
  gates, validator, one independent review with a fixed rubric,
  routed notes and a stopping criterion.
- Nothing is stated about the prior instance that is not in its method
  document (registered in `../instances/registry.json`, pinned by sha256,
  kept outside this repository and cited relative to its own repository
  root). That document and `../01-principle.md` form the **corpus**; the
  production does not edit them.
- An assumption about a domain (car, text, HPC) comes marked `[hypothesis]`.
- American English, plain Markdown, simple tables, pseudocode in `text`
  blocks.
- No absolute path, machine name, user name or authoring date in the
  documents. Versions (v1, v2) may appear. The anonymity rules are an
  option of the instance in the method, declared in the brief; this brief
  keeps them on.

## Owner decisions

The owner is whoever commissioned this production. These decisions are the
owner's, and the production does not make them:

| Decision | Status |
| --- | --- |
| Choice of the three example targets | made in the request |
| Stopping criterion | made in the request: one review round |
| Whether the `[hypothesis]` limits of the instances hold for a real case | open: each real instance decides its own |
| Correcting the divergences found between `../01-principle.md` and the prior instance's document | made in the v0.2 round, from the review of round 1 (see `../CHANGELOG.md`) |

## Budget and stopping criterion

- **Gate rounds:** each document can go back to the writer up to 2 times per
  failed gate; on the third time, the artifact is escalated to the owner.
- **Independent review:** exactly **one** round. A single auditor, without
  access to the reasoning of whoever produced it, receives the files and the
  rubric of `04-gates-and-rubric.md` and returns a verdict and notes.
- **After the review:** the `high` and `blocking` notes are applied; the
  validator runs again and has to pass; the `low` and `medium` notes
  become open notes in `90-review/notes.json`. **There is no second review**,
  whatever the verdict. What the round taught goes into `99-lessons.md`.

## Maintenance rounds after the stopping criterion

The stopping criterion above closed the production after its one review
round. Every round after it, from v0.2 on, is a maintenance round outside
this brief: it corrects or extends the material from the findings of
critical panels and reviews, it is conducted by an orchestrator with the
decisions the owner delegated (the CHANGELOG names them), and each one is
recorded in `../CHANGELOG.md` and as a line of `state/round-record.jsonl`.
Those rounds did not follow this brief: it declares no budget and no
stopping criterion for them, and in every round whose line names a
reviewer the review came from the producer's family, but for one reading
review of v0.4.1, without a frozen rubric. A protocol for
maintenance rounds (a stopping criterion declared before each, and the
delegated decisions recorded as artifacts of the owner) is an open decision
of the owner, and so are, since the panel that reviewed v0.4.2, the scope of
the distributed validator and the status of the rule of independence.

## What is not a goal

- Writing the method again: it is in `../01-principle.md`. Here we write how
  to apply it.
- Giving domain numbers as truth: the limits of the instances are plausible
  and justified, not normative.
- Producing the car, the text or the library.

## Assumptions

- `[hypothesis]` The reader knows the basics of each example domain; the
  generic recipe assumes no domain at all.
- `[hypothesis]` An orchestrator agent can follow the recipe if each step
  says what it reads, what it creates and when it is done.
