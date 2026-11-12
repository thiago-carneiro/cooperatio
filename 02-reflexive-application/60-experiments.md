# Experiments about the method

The record of the measurements this production makes about the method
itself, not about a target. The terms follow the [canon](01-canon.md); the
gate that reads this record is `p-efficacy-mark`, and a claim elsewhere
backed by an experiment carries the label `[experiment:<id>]` with the id of
an executed experiment here.

Each experiment is written before it is measured: the question, the
protocol and the predictions come first and are not edited after the runs,
and any later correction is marked in place; the results, what they show
and what they do not show come after. The
executors are named by family (a letter stable across the material) and
effort, never by model identifier, here and in the round record
(`state/round-record.jsonl`); the map from letter to identifier stays with
the owner, outside the material. Family A is that of the model that produced
the guide of the one executed instance. The status of an
experiment is `executed`, `pending` (protocol and predictions fixed, results
not yet recorded) or `designed`, declared in the "Status" row of its field
table; only an executed experiment backs a claim, and a designed one
carries no number.

## E1 — reviewer sensitivity and family swap

| Field | Value |
| --- | --- |
| Id | E1 |
| Status | `executed`; protocol and predictions fixed before the runs; two descriptions in the protocol were corrected after them, marked in place, and the predictions were not edited |
| Origin | the critical panel that reviewed v0.2.3: the independence of the reviewer and the swappability of models were asserted and never measured, and the reviewer, the one truly independent role, never received a known perturbation |
| Owner | verifier |

### Question

Does the independent review, run from the reviewer's card and the frozen
rubric, reject a product with known injected defects and accept the same
product without them? Does the answer change with the family of the model
that executes the review?

### Object

The product of the executed adoption-guide instance: its guide, of 1054
words, which its one review accepted [prior:004-adoption-guide].

The cell's frozen rubric (the "Rubric" section of the cell's gates file,
pinned at `ba88324b…f67f`) and the cell's reviewer card are used as they
are. Every run works on copies; the historical cell is never touched.

### Conditions

- **A, the control.** The guide untouched.
- **B, the perturbed product.** The guide with two injected defects:
  - an invented number about a prior held by the owner, not distributed:
    the guide's count of that prior's roles is replaced by a larger,
    invented count; the frozen rubric classes a false claim about the corpus
    as `blocking` (*reworded in v0.7.0, by the owner's decision: this item
    named that prior and its count; the injected defect and the results are
    unchanged, and the two copies of the guide are pinned by sha256 in the
    provenance table*);
  - a method term with its sense swapped, which also contradicts the
    principle: the guide's sentence saying that several models do not
    create independence by themselves (models of one family share blind
    spots) is replaced by one saying that the independent review may be
    done by the same model that produced, in another session; the rubric
    classes a term used in another sense as `high`, and the sentence
    contradicts "Independence needs a different model" in
    `../01-principle.md`.

### Executors

- **X** — a model of the producer's family (the guide was produced by that
  family), in a separate dispatch, never the producing run. *Corrected
  after the runs: X is the producer's own model, the same model identifier
  that produced the guide, in another session — not only its family.*
- **Y** — a model of another family, in a separate dispatch.
- *Named in v0.4.1 by the letters of the round record: X is family A, Y is
  family B.*

One dispatch per run. Each run receives the guide (A or B), the cell's gates
file with its rubric, the cell's reviewer card and its base prompt,
`../01-principle.md` and the method document of a prior held by the owner, not distributed, to check
the guide's counts of roles and artifacts against it. No run sees the
producer's reasoning or the output of another run. *Corrected after the
runs: the cell's card has no base prompt; the prompt was written from the
card by whoever conducted the experiment, and these five files were all a
run received (see "Deviations from the protocol").*

### Protocol

- Runs: four, the matrix {A, B} × {X, Y}, one run per cell. This is a
  declared limitation: without repetition there is no estimate of the
  sampling noise of a model, and a difference between X and Y is a datum
  about one run, not about the family.
- Measures, per run: (m1) the verdict; (m2) in B, whether each injected
  defect is named in a finding, and with which severity; (m3) conformity
  with the contract: the report has the sections of the rubric's report
  format, and its notes carry the six fields with a valid severity (a tight
  contract is what makes the executor swappable); (m4) findings in A that
  the real review round did not raise (the noise of the executor); (m5) the
  cost: input and output tokens and wall time.

### Predictions (written before measuring)

| Prediction | Statement | It is refuted if |
| --- | --- | --- |
| P1 | in B, both executors give `rejected`, with the invented number named as `blocking` | either executor lets the invented number pass, which refutes "the reviewer catches a false claim about a prior" |
| P2 | in B, both executors name the swapped term with a severity of `high` or more | either executor misses it or names it lower |
| P3 | in A, both executors give `accepted` or `accepted with conditions` (the real round gave `accepted`) | either executor rejects the control |
| P4 | the outputs of X and Y validate against the contract (m3) in the four runs | one run breaks the report format or the note contract |

X catching less than Y, or the reverse, is a datum about family, not a
conclusion: one run per cell cannot separate the family from the run.

### Results

Five runs: the four of the matrix and A-X2, a re-run of A-X after its
report stopped at an output limit (see "Deviations from the protocol"). The
scores are those of the six dimensions of the frozen rubric, in order.

| Run | Condition | Executor | Verdict | Findings (blocking / high / medium / low) | Scores | Invented number | Swapped term | Contract (m3) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-X | control | X, the producer's model | none: a tool failure (the truncated text read `accepted with conditions`) | 0 / 0 / 3 / 2 | 3, 4, 4, 5, 5, 5 | — | — | broken: generation ended for length at 65,536 output tokens, 3 of the 7 sections, no notes in JSON |
| A-X2 | control, re-run | X | `accepted` | 0 / 0 / 3 / 2 | 5, 4, 4, 5, 5, 4 | — | — | conforming, 5 notes, generation ended normally |
| B-X | perturbed | X | `rejected` | 1 / 2 / 0 / 1 | 5, 2, 4, 5, 5, 4 | named, `blocking` | named, `high` | conforming, 4 notes |
| A-Y | control | Y, another family | `accepted with conditions` | 0 / 1 / 9 / 3 | 3, 3, 4, 5, 5, 3 | — | — | conforming, 13 notes |
| B-Y | perturbed | Y | `rejected` | 1 / 1 / 6 / 4 | 4, 2, 4, 5, 4, 3 | named, `blocking` | named, `high` | conforming, 12 notes |

The real review round of the instance had given `accepted`, with one medium
and one low finding and no dimension below 4 [prior:004-adoption-guide].
That round received the whole corpus and the rubric's pin as inputs; the
runs of E1 received five files, so only the verdicts compare with it, not
the findings. *Corrected in v0.4.1: that round was recorded as reviewed by
another family; its reviewer was the producer's own model through another
route, the configuration of X, not of Y.* *Corrected in v0.5.0, after the
critical panel that reviewed v0.4.2: A-X ended for length, which the rule
this record adopted (see "Side findings") makes a tool failure, never a
verdict. Its verdict, scores and findings are kept in the table as observed
and count for no measure that needs a verdict; the valid runs are four.*

| Prediction | Result |
| --- | --- |
| P1 | confirmed for both executors: in B both gave `rejected` and named the invented count of roles as `blocking`, against the prior's method document; both also scored the second dimension 2, a second path to `rejected` under the rule |
| P2 | confirmed for both: both named the swapped term, cited "Independence needs a different model" of the principle and classed it `high` |
| P3 | confirmed in the two valid control runs: A-Y gave `accepted with conditions` and A-X2 gave `accepted`, the verdict of the real round; A-X is a tool failure and gave no verdict (*corrected in v0.5.0: this row first counted it, "in the three control runs"*) |
| P4 | refuted in one run of five: the generation of A-X ended for length at 65,536 output tokens, a limit the endpoint applied and not the budget the dispatch declared; the other four conform (sections in the order of the report format, notes with exactly the six fields, valid severities and targets) |

Measures:

- **m1, m2.** Each executor named both injected defects, with the predicted
  severity: 2 of 2 per executor, one run per cell.
- **m3.** 4 of 5 reports conform; the one that does not ended for length,
  a matter of the executor's generation, not of the rubric, and a tool
  failure with no verdict.
- **m4.** Findings in the controls beyond the two of the real round: X gave
  five in A-X and five in A-X2 (3 medium, 2 low each), but the two lists
  are almost disjoint — a component omitted, the first review postponed
  and an undefined term in one; an omitted hash, an undefined term and a
  count of the generic recipe's steps that is a false positive (the generic
  recipe has the steps 0 to 14) in the other. Y gave 13 (1 high, 9 medium,
  3 low). *Added in v0.4.1, checked against the raw outputs: in A-X the
  anatomy that omits one of the eleven components (the sensitivity test)
  and the postponed first review were both medium; in A-Y the anatomy of
  eight items against the eleven components was medium.* Part of
  this noise comes from the inputs, not from the executors: each run
  received five files, not the whole corpus (Y scored the first dimension 3
  saying the brief was not provided; the false count came from a run without
  the recipe). No control run produced a blocking finding. The findings and
  the scores vary from run to run and between executors more than the
  verdict does. *Corrected in v0.5.0: the five findings of A-X are those of
  a truncated report, a tool failure; they are listed as observed, not as
  a measure of noise.*
- **m5.** See "Cost" below.

### What it shows and what it does not show

What it shows: with the frozen rubric and the prior's method document in
hand, two executors — X, the producer's own model in another session, and
Y, a model of another family — each named 2 of 2 injected defects at the
predicted severity, and neither rejected a valid control; the mechanical
verdict rule was applied correctly in every complete run, and it made the
verdicts (not the findings) comparable with one another and with the real
round.

What it does not show, declared before the runs and still true after them:

- that the method finds defects a reviewer without it would miss — there
  is no arm without the method; that is experiment E2, designed below
  [hypothesis];
- a rate: one run per cell measures one object once;
- defects the rubric does not anticipate: both injected defects belong to
  classes the frozen rubric names, so the experiment tests the review
  against the defects its rubric was written for;
- independence from the corpus: the principle and the method document of
  that prior are inputs of every run, as the conductor's prompt
  prescribed (the card names the inputs, and the prompt was written from
  it).

What the runs added to that list:

- that the family of the executor changes what is caught: both executors
  caught 2 of 2, so this experiment cannot tell them apart;
- that another session of the producer's model is not enough as a review:
  X is exactly that configuration, and it caught 2 of 2 — one run per
  cell, a datum against the intuition of the principle, not a conclusion
  (the real round of the instance, found in v0.4.1 to be the same
  configuration, is no second datum: it had no injected defect);
- stability across repetitions: the only repetition (A-X and A-X2) pairs a
  tool failure with a complete run, so neither the instability nor the
  stability of the verdict is measured (*corrected in v0.5.0: this item
  first read the pair as a change of verdict*).

Side findings:

- **The output contract of the reviewer did not cover how the executor's
  generation ends.** The dispatch asked for an output budget the endpoint
  did not apply (another run of X produced more than that and ended
  normally); A-X stopped at an effective limit of 65,536 tokens, ended for
  length, and delivered a report with no verdict a reader can verify. The
  re-run did not remove that limit: it fit under it. The rule this round
  adopted (reviewer card and step 11 of the generic recipe): the dispatch records
  the effective output limit and the reason the generation ended; an
  ending for length, or a report that lacks a section of the format, is a
  tool failure, never a verdict.
- **The rule is stable; the scores and the findings are not.** The same
  executor, in the same condition, with the same prompt and context, gave
  five findings in each run, almost all different, and scores that moved
  (the first dimension from 3 to 5), so the verdict went from `accepted
  with conditions` to `accepted`. The mechanical rule was applied correctly
  both times. A verdict is exactly as stable as the dimension scores that
  decide it. One caveat weakens the pair: the first of the two reports was
  the one that ended for length. *Corrected in v0.5.0: by the rule of the
  side finding above, that report is a tool failure and its verdict is no
  verdict, so the pair does not measure the stability of the verdict; what
  stands is that two runs of one executor in one condition produced almost
  disjoint findings and different scores.*
- **A hole of the validator, confirmed after the runs (not a measure of
  E1).** Both perturbed runs remarked that the cell's `p-prior` gate should
  catch the invented number. A check made after the runs, in the review of
  this round, ran the cell's validator on the perturbed copy with the
  prior's document: the gate passed. The count of roles had no row in the
  cell's "Recorded facts", so it was checked for presence in the whole
  document, and the invented number occurs there once, in an unrelated
  sentence. By golden rule 4 it became a gate in this round: a number in a
  `[prior:<id>]` unit without a row of that prior fails (`p-prior`, with its
  perturbation).

### Deviations from the protocol

- The generation of A-X ended for length at an effective limit of 65,536
  output tokens; the budget the dispatch asked for was not applied by the
  endpoint. A-X2 re-ran it with no budget asked, the same prompt and
  context, and ended normally at 55,511 output tokens, under that limit.
  *Corrected in v0.5.0: this item said "the effective limit stayed in
  place"; that is an inference, since no run measured the limit after A-X.*
  Both runs are recorded, and the truncated report still counts as a
  contract violation of the run it belongs to.
- Inputs: five files per run (the guide, the cell's gates file with the
  rubric, the reviewer card, the principle, the method document of that
  prior), not the whole corpus nor the rubric's pin the cell's card
  and the real round had; the prompt was written from the card by whoever
  conducted the experiment, since the card has no base prompt.
- The two runs of Y ran in parallel with each other; the three of X ran in
  series.

### Cost

The first cost of the method this production measured (m5), one review
run:

| Executor | Input tokens | Output tokens | Wall time |
| --- | --- | --- | --- |
| X (three runs, from the client's log of the usage the endpoint returned) | about 58,000, most of them the method document of a prior held by the owner, not distributed (the guide has about a thousand words) | 55,511 to 65,536, 90 to 98 % of them reasoning (*corrected in v0.5.0 from "about 90 %"*) | 473 to 600 s, 8 to 10 minutes |
| Y (two runs, indicative only) | not separable per call: no raw record; the dispatch reported agent totals, reading the inputs included, of about 173,000 and 154,000 | not separable | the dispatch reported 204 and 226 s; the files were written 224 and 247 s after the start; about 4 minutes |

The numbers of Y were not measured by the same instrument as those of X.

### What became a gate or a lesson

- A rule in the reviewer card and in step 11 of the generic recipe: the dispatch
  records the effective output limit and the reason the generation ended;
  an ending for length, or an incomplete report, is a tool failure, never a
  verdict.
- A new rule of `p-prior`, from the hole confirmed after the runs: a number
  about a prior needs its row in "Recorded facts"; presence in the whole
  document no longer verifies anything.
- A lesson, appended to `99-lessons.md` in the v0.4.0 round.
- The record itself is under a gate: an `[experiment:<id>]` label anywhere
  in the corpus has to name a section of this page (`p-efficacy-mark`).

The correction of the skill made in the same round (another session of the
producing model is not an independent review) follows from the principle,
not from this experiment: it was noted before the results, and X's 2 of 2
is, if anything, a datum against it.

### Provenance

The files of the runs, by role, with the sha256 of each under the material's
hash policy (its text as UTF-8, no byte-order mark, line breaks as LF; for
these files, equal to the sha256 of their bytes), recorded in v0.6.0 from
the raw files the owner keeps outside the material. They let the owner,
and anyone the owner hands the files to, check that the results above come
from these inputs; they do not show that the protocol text above is the
text that was fixed before the runs, since that text was not hashed before
them (declared). The model behind each family letter stays with the owner.

| File | Kind | sha256 |
| --- | --- | --- |
| system prompt | input | `43a2eaa9b6a13dedf9e569a80e4c8b39e3ec9e804a504a62bdce9757c8cfb101` |
| task prompt | input | `c5b97983767f22730aac6f480ce2d3ccabb77f0c6a039c880181fb86721c34d4` |
| reviewer card | input | `d4fac843d9e284c711f43c57719cec6623c59e919ba2848739a19342ca0b0cbd` |
| gates and rubric copy | input | `e2254ae601527a5e04f42cb19a97b8040c4eb4de71e5aeba727fcba5418045c3` |
| principle copy (v0.3.1) | input | `7bf6e8a242fdd17c3f575b80f352538360e7228674adeebd476f025d8d405267` |
| guide, arm A | input | `d6c149b0a35cbcacbf159c6e85be88e946e2ef7ac802e3e9af75957181b51fff` |
| guide, arm B | input | `694a188d2c8f304a1dc0b8f2324a209cb9416afc5103417e5193b7ad442ae75a` |
| method document of a prior held by the owner, not distributed | input | `02f61349c00de94d93c64abcbbdf401f64216a555071bdb86e7d4bea643d25a0` |
| dispatch script of X | input | `27c144559a2f1777941663dfbac48e75c9c86dd35f9f2e5f656333539823eb99` |
| dispatch script of X, repetition | input | `2e6f20aaa4f8d1139cb29f79c33862537a4867e61d493c716a1d43e184a4554c` |
| report A-X | output | `ed62aa279b473104563c868e68def190c06688a7fc3ad4c939fc6dea38b63a21` |
| raw response A-X | output | `08a716d9c352c50a8bd9279b305b7b930e1fe87d91bf0da2b0acebf798c437ed` |
| report A-X2 | output | `f09ee36ae7dfceb6a430e832f124dbc385e6aa86ff6b582f59ce5bbd2c98d981` |
| raw response A-X2 | output | `8ae42e4dbbfcba9aea8c479bccbe4deda7ca3770d28e86fe0948c3bd2cf5fa47` |
| report B-X | output | `9f9f58e89cb8d790c15d0df20ec5d28d5e7a01a012237047475ca5464539b6d6` |
| raw response B-X | output | `f89e4e750560c6fa073e4a5908b42ee4055e0dcaf09d03083ff9a5cc55755977` |
| report A-Y | output | `2d2b8a1a9c96259ec0fa5ce8af0a2e8cb9a6edd16b4bb3978c70a8b5cf5cd169` |
| report B-Y | output | `5924c8cdc6d49e119c1f07e45da3b556602e049d8ac20a6b99b1f8422d264d06` |
| dispatch log of X | output | `f485110ba705a438acf9e2f9cad95c73c490c0d2fe34b5e0a5b6bde3fa40e303` |
| run log of X | output | `04f7ff56cd4c5cccec9b3b0751ff080198901f000b933b1451d3fe16f426f148` |
| start mark of Y | output | `2d0e467fcad39770dc4b821b853d329cac0f49e197835e494ca34222d97c87f6` |
| end mark of Y | output | `6b04c108a1de22da9886014253cc07d71fd4ec534c1dfcb3085d6b4928e1a8dc` |

## E2 — the counterfactual, designed and not executed

| Field | Value |
| --- | --- |
| Id | E2 |
| Status | `designed` |
| Origin | the same panel: everything the method found was found under the method, so there is no escape rate to compare [lessons:The v0.4.0 round: evidence about the method is subject to the method] |
| Owner | verifier |

### Question

On the same target and with the same injected defects, how many defects
escape a production made with the method, and how many escape one made
without it?

### Design

- **Method arm.** A production cell as the recipe prescribes: brief, canon,
  gates with a sensitivity test, a validator, a frozen rubric and an
  independent review from another family.
- **Control arm.** The baseline the method has to beat: a strong model with
  a checklist, continuous integration on whatever can be checked by code,
  and a review without a rubric.
- **Measure.** The escape rate per arm: the injected defects present in the
  delivered product, over the defects injected, with the same injection
  protocol in both arms.
- **Predictions.** Written before the first run, as in E1; none yet.

### Cost, estimated

Two complete productions per target, plus the review runs of each arm;
more than one target before any rate is read as a property of the method.
No number is stated until the design runs.

## E3 — the reviewer without the rubric

*Read as a pilot since v0.6.0.* One run per cell, the whole review
apparatus removed at once (rubric, card, gates file and the framing of the
dispatch), and a task prompt that points at the two classes of defect
injected: the design isolates no factor, and its prediction P3 was close to
forced by the prompt. Its result is what a pilot shows (a direction worth
measuring), and every unit that cites it reads it so; E4 below is the
design that measures it.

| Field | Value |
| --- | --- |
| Id | E3 |
| Status | `executed`, as a pilot (reclassified in v0.6.0); protocol and predictions fixed before the runs and not edited after them; four runs, no re-run; deviations declared below |
| Origin | the cheap counterfactual of the v0.4.1 round: E1 measured the reviewer with the frozen rubric, and E2, the full counterfactual, costs two productions and stays designed; E3 removes the review apparatus, the rubric and the reviewer card, and keeps the output contract (*corrected after the runs: this row first said "one element, the rubric"*) |
| Owner | verifier |

### Question

Does the frozen rubric (its dimensions, its anchors, its severity table and
its mechanical verdict rule) change what the reviewer catches and the
verdict it gives, for the same defects and the same executor?

### Object

The object of E1, unchanged: the two copies of the guide, A (the control)
and B (with the two injected defects of E1: the invented count of roles,
and the sentence saying that the same model, in another session, may do the
independent review). Every run works on copies; the historical cell is
never touched.

### Conditions

- **Inputs.** The inputs of E1 without the rubric: the reviewer receives
  the guide (A or B), `../01-principle.md` and the method document of that
  prior. No reviewer card, no dimension, no anchor, no severity table,
  no verdict rule.
- **Output contract, kept.** The report keeps the format of E1 (the seven
  sections, the notes in JSON with the six fields), so that the counts
  compare with E1. The arm removes the rubric, not the output contract.

### Executors

As in E1: **X**, the producer's own model in another session, and **Y**, a
model of another family, each in a separate dispatch. No run sees the
producer's reasoning or the output of another run. *Named after the runs
by the letters of the round record: X is family A, Y is family B.*

### Protocol

- Runs: four, the matrix {A, B} × {X, Y}, one run per cell (the limitation
  of E1, declared again: no estimate of the sampling noise of a model).
- The dispatch records the effective output limit and the reason each
  generation ended; an ending for length is a tool failure, as in E1.
- Measures, per run: (m1) the verdict, free (`accepted`, `accepted with
  conditions` or `rejected`, by the reviewer's own judgment); (m2) in B,
  whether each injected defect is named, and with which severity, on the
  reviewer's own scale; (m3) the output contract met; (m4) the findings in
  the control; (m5) the cost.

### Predictions (written before measuring)

| Prediction | Statement | It is refuted if |
| --- | --- | --- |
| P1 | in B, both executors name the invented number: the prior's method document is in hand, and the rubric is not what makes the number visible | either executor lets the invented number pass |
| P2 | in B, at least one of the two names the swapped term: without the table that classes a method term in another sense as `high`, the catch and its severity are left to judgment | neither names it |
| P3 | without the mechanical rule, at least one of the two runs of B ends with a verdict other than `rejected`: free judgment softens the verdict even with a defect the rubric would class as `blocking` | both runs of B give `rejected` |
| P4 | in A, neither executor raises a finding it would call blocking | either does |

### Results

Four runs, one per cell. The verdict and the severities are the reviewer's
own, since no rubric fixed them.

| Run | Condition | Executor | Verdict (free) | Findings (blocking / high / medium / low) | Invented number | Swapped term | Contract (m3) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A-X | control | X, family A | `accepted with conditions` | 0 / 1 / 4 / 4 | — | — | conforming, 9 notes, generation ended normally |
| B-X | perturbed | X, family A | `accepted with conditions` | 0 / 2 / 4 / 5 | named, `high` | named, `high` | conforming, 11 notes, generation ended normally |
| A-Y | control | Y, family B | `accepted with conditions` | 0 / 2 / 9 / 4 | — | — | conforming, 15 notes |
| B-Y | perturbed | Y, family B | `accepted with conditions` | 0 / 2 / 5 / 4 | named, `high` | named, `high` | conforming, 11 notes |

With the rubric, in E1, the same executors on the same copies gave
`rejected` in B, with the invented number as `blocking` and the swapped
term as `high`, and none rejected the control.

| Prediction | Result |
| --- | --- |
| P1 | confirmed: both executors named the invented count of roles, against the prior's method document |
| P2 | confirmed for both, not only one: both named the swapped term as `high`, citing "Independence needs a different model" of the principle |
| P3 | confirmed, and stronger than predicted: both runs of B ended in `accepted with conditions`. Without the severity table, the invented fact about the prior was classed `high`, as a localized and correctable error of fact (a paraphrase of the reviewers), not `blocking`; without the mechanical rule, two high findings did not bring the verdict down |
| P4 | confirmed: no blocking finding in either control |

Measures:

- **m1, m2.** Each executor named both injected defects, 2 of 2, as in E1;
  the severity of the invented number fell from `blocking` to `high` in
  both. The four verdicts are the same, control and perturbed alike.
- **m3.** 4 of 4 reports conform: the seven sections in order, notes with
  exactly the six fields, valid severities and targets.
- **m4.** X raised 9 findings in its control (one high: the first version
  does not go at once to the independent review, since the first wave is
  measured only by the validator; the missing round loop and stopping
  criterion came as medium), Y raised 15 (two high: the same order of the
  first review; an anatomy of eight items against the eleven components of
  the principle). In E1 these two fidelity items had come as medium (see
  m4 of E1); *precised in v0.5.0: in A-X, the truncated run that is a tool
  failure, and in A-Y; the order of the first review appeared only in A-X.* Without the rubric each executor scored aspects of its own, so
  the findings do not compare between runs. *Corrected after the review of
  this round: the first version of this record gave the stopping criterion
  as X's high finding.*
- **m5.** See "Cost" below.

### What it shows and what it does not show

Declared before the runs: the experiment compares the review with the
rubric (the runs of E1) and without it (these runs), for the reviewer
alone. It does not measure the gates of the validator, which E2 would;
it measures one run per cell; and its two defects are the ones the rubric
of E1 anticipates, so it says nothing about defects no rubric names.

What the runs show, for these two defects checkable against a source,
these executors, one run per cell, and with the card and the rubric removed
together: the rubric is not what made the reviewer see the defects — both
perturbed runs without it named the two injected defects that the perturbed
runs with it named. The rubric is what turned the finding into a verdict: its severity table fixes a false claim about a prior as `blocking`,
and its mechanical rule turns a blocking finding into `rejected`; without
them the same finding became `high` and the verdict `accepted with
conditions`, in both executors. A verdict without a rubric neither compares
between runs (each executor judged aspects of its own) nor tells the control
from the perturbed product (all four verdicts were the same). *Corrected in
v0.5.0, after the critical panel that reviewed v0.4.2: the arm removed the
review apparatus as a block (the rubric with its severity table and verdict
rule, the reviewer card, the gates file and the framing of the dispatch;
see the deviations), so the data support "the apparatus, removed together,
changed the verdict". That its severity table and its mechanical rule are
the parts that did it is a hypothesis the design does not separate
[hypothesis], plausible because the reports of E1 cite the table when they
class the invented number as blocking.*

What it does not show, beyond the declared list: stability across
repetitions (one run per cell); other kinds of defect (an invented number
and an inverted rule, both checkable against a source); and which part of
the apparatus does what — the card and the gates file went with the rubric,
so the severity table is not separated from the mechanical rule.

Side finding: in both controls the reviewers without the rubric listed the
same two defects of fidelity to the principle that the runs with it in E1
had classed medium (the order of the first review; the anatomy against the
eleven components). The guide carries both; its real review round, which
received the whole corpus and the rubric's pin, accepted it.

### Deviations from the protocol

Four runs, one per cell, no re-run; the runs of Y ran in parallel with each
other, those of X in series. Declared after the review of this round:

- The protocol asked for the effective output limit and the reason each
  generation ended. The effective limit was recorded for no run (no output
  budget was asked, and the endpoint's ceiling was not measured here); the
  reason was recorded only for X (both ended normally). Y has no raw
  record; its reports are complete (seven sections, valid notes), which
  makes an ending for length unlikely — an inference, not a record.
- The runs received the copy of `../01-principle.md` made for E1, of method
  version 0.3.1, not the current principle.
- Without the rubric the runs also went without the reviewer card and the
  gates file: the arm removes the review apparatus, as the origin row now
  says.
- *Declared in v0.5.0, after the critical panel that reviewed v0.4.2 read
  the dispatch prompts:* the framing of the dispatch changed with the arm.
  The system prompt of E1 named the independent reviewer that applies the
  frozen rubric and decides the verdict by its mechanical rule; that of E3
  named an experienced reviewer of technical documentation who judges by
  its own criteria. The verdict labels of E3 were the words of a free
  judgment, and the gates file left the targets of the notes. The framing
  is part of what the arm removed, not a separate factor.

### Cost

| Executor | Input tokens | Output tokens | Wall time |
| --- | --- | --- | --- |
| X (two runs, measured by the endpoint's log) | 56,086 and 56,087, about 2,000 fewer than in E1 (no rubric, no card) | 41,073 and 46,071, of which 33,768 and 37,960 reasoning | 633 and 770 s |
| Y (two runs, indicative only) | no raw record | no raw record | the dispatch reported 217 and 214 s; the files were written 236 and 237 s after the start |

### What became a gate or a lesson

- A sentence in step 6 of the principle's recipe (its section 7) and in the skill: for two
  source-checkable defects, one run per cell, the review apparatus removed
  as a block is what turned a finding into a verdict (*corrected in v0.5.0:
  the sentence named the severity table and the mechanical rule, which the
  design does not separate; they stay as a hypothesis*).
- A lesson, appended to `99-lessons.md` in the v0.4.1 round.

### Provenance

The files of the runs, by role, with the sha256 of each under the material's
hash policy (its text as UTF-8, no byte-order mark, line breaks as LF; for
these files, equal to the sha256 of their bytes), recorded in v0.6.0 from
the raw files the owner keeps outside the material. They let the owner,
and anyone the owner hands the files to, check that the results above come
from these inputs; they do not show that the protocol text above is the
text that was fixed before the runs, since that text was not hashed before
them (declared). The model behind each family letter stays with the owner.

| File | Kind | sha256 |
| --- | --- | --- |
| system prompt | input | `7e985f2b5772c9340c98160bde75200a9d1f41cb3b5f02fc376933eba267ff6b` |
| task prompt | input | `0aa21c04ce2c1704a3108103604a00f86138e8b43d0106c6606a379bdd14d452` |
| principle copy (v0.3.1) | input | `7bf6e8a242fdd17c3f575b80f352538360e7228674adeebd476f025d8d405267` |
| guide, arm A | input | `d6c149b0a35cbcacbf159c6e85be88e946e2ef7ac802e3e9af75957181b51fff` |
| guide, arm B | input | `694a188d2c8f304a1dc0b8f2324a209cb9416afc5103417e5193b7ad442ae75a` |
| method document of a prior held by the owner, not distributed | input | `02f61349c00de94d93c64abcbbdf401f64216a555071bdb86e7d4bea643d25a0` |
| dispatch script of X | input | `759f5d870c65a434d6efff2264f046ead80d37155a372ab0b6acf8ad17508f33` |
| report A-X | output | `28bc9693f72dfecf18f66a46cb023dd8e36db6c15ff10b926c4eb8a1ddfe8186` |
| raw response A-X | output | `76bcca32522682aec81d65dff9e43d361bc11a05a23513cc6c18c65e2a52c28f` |
| report B-X | output | `f894e48c233b4b5139ace81ef31cb819ad01f0a35d10ca99357653890374b144` |
| raw response B-X | output | `e977c3537d06e19a68c2ec5a96192f05cb2f76be0944b2a61836c1d3915d4802` |
| report A-Y | output | `915af4cff0efb568a43866609f357723d544da79ab619ca49de90255dce29645` |
| report B-Y | output | `b4c30b9fa410d7102f6a48d6c7c1949459da5d34f2a304a774f99e46f99cca88` |
| dispatch log of X | output | `159288432a35258ef702f26dc09d3e4fb8d0b6afe6180da99cd073bee9249b7d` |
| run log of X | output | `43eabcc3c6778278bf04a502bf2d2ed5819576bcf000bbe37c68c82ecd414aef` |
| start mark of Y | output | `911f9fab29cbd25de647bf5696591dcc3fd1c9d6124ddd1e39087d95601eb01c` |
| end mark of Y | output | `b5dbbc2712ebaac0d28413387d42546af229ea946b9b58f18af5f9589e61ecc3` |

## E4 — seeded escape, designed and not executed

| Field | Value |
| --- | --- |
| Id | E4 |
| Status | `designed` (v0.6.0); protocol and predictions written before any run, for the owner to approve, budget and run; in v0.7.0, before any run, the owner changed the thresholds of the first prediction and set the measure of its tokens, and a critique of the protocol added the clean copy, the auxiliary comparisons and the cases below |
| Origin | the panel of the material's own team on v0.5.0: E2 needs two productions per target, and a seeded-escape design answers the same question, what the apparatus adds to a careful review, at about a tenth of the cost; E1 and E3 had both defects in one arm, a prompt pointing at the classes injected and two harnesses |
| Owner | verifier |

### Question

On the same product, with the same seeded defects, does the review
apparatus of the method (the validator and a review with the frozen rubric
and its mechanical rule) let fewer defects escape than a careful review
without it (a checklist and a free review)? And does a reviewer of another
family let fewer escape than one of the producer's family?

### Object

The output of one writer, before any review: a document of a few thousand
words written under a cell of the method, with its canon and its sources,
copied once per run.

### Conditions

- **Arm A, the apparatus.** The validator of the cell, run first, then a
  review with the frozen rubric, the reviewer card and the mechanical
  verdict rule.
- **Arm B, the careful baseline.** A checklist of the same length as the
  rubric, written by someone who did not write the rubric, and a free
  review with the same sources.
- **Families.** Within each arm, one reviewer of the producer's family and
  one of another family, the same harness and the same dispatch for both.
- **Clean copy.** Four runs on the clean copy (arm by family), to see false
  alarms.
- **Verdict.** Every run also emits a verdict: arm A by the mechanical rule,
  arm B free.
- **Seeded defects.** k = 10 per copy, one per class: an invented number
  about a registered prior (`004-adoption-guide`), a number that exists in the source but in
  another context, a term used in a sense the canon does not give, a
  sentence that contradicts the principle, an absolute path, a broken link
  to the canon, a claim of efficacy without a label, an omitted step of the
  recipe, a limit without a justification, and a factual error outside every
  class the rubric anticipates (class 10). The positions and the wording are drawn once
  by a third party and sealed (their sha256 recorded in the protocol row of
  the provenance table before the first run).
- **Who seeds, and who writes the apparatus.** The seeder does not see the
  validator, the gate table or the perturbation set; every seeded defect
  must be decidable from the inputs common to both arms. The rubric and the
  checklist are written by sessions that have not seen the protocol or the
  class list.
- **Auxiliary comparisons, outside the decision.** A
  checklist-plus-validator-report arm on the other family (3 runs), and one
  defect set repeated on both arms of that family (2 runs), as a floor of
  noise.

### Protocol

1. Seal the ten defects and the clean copy; record their sha256.
2. For each of the four cells (arm by family), three repetitions in a
   randomized order, one defect set per repetition, the same set across
   the four cells of a repetition.
3. Each run receives the copy, the sources and its arm's apparatus, and no
   hint of how many defects there are or of their classes; the task prompt
   is the same in the two arms but for the apparatus it names.
4. A defect counts as found when a note names its location and its nature;
   two readers who did not run the review adjudicate, blind to the arm, and
   their disagreements are recorded.
5. Each run records its provenance: the sha256 of every input and output,
   the parameters of sampling, the tokens per call and the reason the
   generation ended; a run that ends for length is a tool failure and is
   re-run once.
6. Reported beside the pooled result: the validator alone, A versus B on the
   defects the validator does not report, and B on those it reports.

### Predictions (written before measuring)

The tokens of a run, for P1b and P1c, are the input tokens its arm adds to
what both arms read (arm A: the rubric, the reviewer card and the validator's
report; arm B: the checklist), as the endpoint counts them on a call holding
only those added files. Output and reasoning do not count, by the owner's
decision, and are reported apart, with the total input.

- **P1a (fewer errors).** The escape rate of arm A is at most half that of
  arm B, pooled over families, in at least 2 of 3 repetitions. Refuted when
  it is more than half in at least 2 of 3 repetitions.
- **P1b (fewer tokens).** The additional input tokens of a review run of arm
  A are at most half those of arm B, pooled over families, in at least 2 of
  3 repetitions. Refuted when they are more than half in at least 2 of 3
  repetitions.
- **P1c (the owner's failure criterion).** Pooled over families and
  repetitions, arm A consumes more additional input tokens than arm B and
  (escapes_B - escapes_A) / escapes_B is smaller than
  (tokens_A - tokens_B) / tokens_B. The claim is withdrawn when P1c holds.
- **P2 (the family).** Within arm A, the reviewer of another family finds
  at least 1 more defect of 10 than the reviewer of the producer's family,
  in at least 2 of 3 repetitions. Refuted when the difference (other family
  minus producer's family) is ≤ 0 in all 3 repetitions.
- **P3 (outside the rubric).** In both arms, the defect outside every class
  the rubric anticipates (class 10) escapes at least as often as the median
  class. Computed per arm over the classes the validator does not report.
  Refuted when class 10 escapes strictly less often than their median; not
  decidable when both are 0 % or both 100 %.

A repetition with escapes_B = 0 does not count for P1a. If pooled escapes_B = 0, P1c is undefined and the result is inconclusive.

Since arm A adds more files than arm B by construction, this measure is
expected to make P1b fail and may make P1c hold whatever the escapes; it is
the owner's definition, written before any run. It is about the review
stage only: the cost of building the cell (canon, gates, rubric, validator
setup) is outside E4.

With three counted repetitions, P1a and P1b are each confirmed or refuted and
cannot be neither: at most half and more than half are the two sides of one
line. A repetition that does not count can leave P1a undecided. P1c is a
criterion of withdrawal, not a band: the claim is promoted when P1a and P1b
are both confirmed, withdrawn when P1c holds, and inconclusive otherwise, as
the principle's table "What would promote or withdraw a claim" says. The
band of P2 is the case of a difference at or below zero in all 3 repetitions,
and a mixed record neither confirms nor refutes it; P3 can be not decidable,
as declared. The owner changed the thresholds of the first prediction before
any run (they were a difference of at least 20 points, refuted under 5
points), and accepted them in the principle's table. The family and
portability rows of that table keep the proposed thresholds; the refutation
of P2 above, a difference at or below zero, is wider than the family row's
withdrawal, a nil difference, and was written from the critique, not by the
owner's change of the table.

### Cost, estimated

Twelve review runs on the defect sets, four on the clean copy and five
auxiliary, plus the validator runs, and the adjudication of the two
readers: by the costs of E1, an order of magnitude below the two
productions per target of E2 [hypothesis].

### What it would show and what it would not

It would measure escape rates on one kind of product, with seeded defects
whose classes the designer chose, and nothing about defects nobody thought
to seed. It would not measure a whole production, nor the cost of the
instruments over a production.

**What this does not settle.** The defects are a third party's, so they do
not exercise blind spots shared with the producer. There are three
repetitions. A validator-clean copy overstates precision. The baseline had no
tools. There is one object, one writer, and classes chosen by the designer.
The cost of building the cell is outside.

### Smaller designs that can run before it

Proposed by the panel's seat of metrology, recorded here as designs, not
yet experiments with an id of their own:

- **E1b, the floor of noise.** The same review, one executor, five
  repetitions per cell of {control, only the invented number, only the
  swapped term}, in a randomized order, with the throughput of each run:
  the agreement per dimension and per verdict across repetitions, and the
  rate of detection with its interval.
- **E1c, a defect outside the rubric.** A number that exists in the source
  but in another context, and a step of the recipe omitted in silence: what
  "defects the rubric does not anticipate" are worth.
- **E3b, one factor at a time.** The arm with the defects, one executor, the
  apparatus removed piece by piece (the rubric without the card, the card
  without the rubric, only the framing, only the verdict rule), three
  repetitions each: the share of each part, which E3 left a hypothesis.

## E5 — an execution outside the documentary domain, designed and not executed

| Field | Value |
| --- | --- |
| Id | E5 |
| Status | `designed` (v0.6.0); for the owner to approve and to find who runs it |
| Origin | the same panel: a seat instantiated a small software library from the material and found that, with no reading of the domain's measurements, the validator stayed at exit 0 with the identity gate and the tests failing; v0.6.0 added that reading |
| Owner | verifier |

### Question

Can someone who is not the owner take the material as distributed, set up a
cell for a target whose non-negotiables are domain measurements, and reach a
verdict of the canon without improvising instrument?

### Design

- **Who.** A third party who did not write the material, with the material
  as distributed and no help from the owner beyond the brief.
- **Target.** A small software library with two non-negotiables: identity
  of results against a frozen reference, and a speedup at a declared point.
  The cell of the panel's seat is the starting point of the design, not of
  the run: the third party writes its own cell.
- **Instrument.** The domain gates are `d-*` rows whose results the cell's
  code writes; the validator reads them; a regression is seeded once (a
  candidate that breaks identity) and has to leave the run red.
- **Record.** The round record of the cell, its notes, and a log of every
  point where the material did not say what to do, which counts as an
  improvisation.

### Predictions (written before measuring)

- **P1.** The cell reaches a verdict of the canon with at most two
  improvisations, none of them in the instrument. Refuted when it cannot
  reach a verdict without writing instrument the material does not ship.
- **P2.** The seeded regression leaves the validator at exit 1. Refuted
  when the run with the regression exits 0.

### Cost, estimated

One production of a small target by a third party, and the owner's time to
brief them; not estimated in tokens.
