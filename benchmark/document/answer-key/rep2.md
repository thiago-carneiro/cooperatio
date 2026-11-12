# Answer key: document, rep2

Ten seeded defects, one per class, in `seeded/rep2/guide.md`; each is an exact replacement of
text of `clean/guide.md` (an omitted step is a removed line, and the list is renumbered).
"Reported by the validator" says whether the automatic checks report that arm A received
(`automatic-checks/rep2.md`) names the defect. This file is an answer: never give it to a reviewer.

## Class 1: an invented number about the registered prior

Reported by the validator: yes.

**Replaced text.**

```text
In the executed instance no engine rebuilt a stale artifact from the hash of its inputs — the writer and the orchestrator rebuilt by hand [prior:004-adoption-guide] — and the cell recorded the decision not to keep a separate engine at its scale [prior:004-adoption-guide].
```

**New text.**

```text
In the executed instance no engine rebuilt a stale artifact from the hash of its inputs — the writer and the orchestrator rebuilt by hand [prior:004-adoption-guide] — and the cell recorded the decision not to keep a separate engine at its scale, after 3 rounds of manual assembly [prior:004-adoption-guide].
```

**Where an input common to both arms shows it.** The recorded facts of this canon are the numbers this guide may state about its prior: 1054 words of its guide at the close, the range of 900 to 1400 words its brief set, and 4 as the lowest dimension score of its one review.

**A note counts as a find if it says:** States that '3 rounds' is a number about the prior that does not appear among the recorded facts of the canon.

## Class 2: a number that exists in the source but in another context

Reported by the validator: no.

**Replaced text.**

```text
The executed instance perturbed its measurement with known defects injected into a copy of its guide, and the measurement rejected each of them [prior:004-adoption-guide].
```

**New text.**

```text
The executed instance perturbed its measurement with 4 known defects injected into a copy of its guide, and the measurement rejected each of them [prior:004-adoption-guide].
```

**Where an input common to both arms shows it.** O teste de sensibilidade do instrumento injetou dez defeitos conhecidos em cópia em memória do guia e a replicação pegou os dez.

**A note counts as a find if it says:** States that the prior injected ten defects, not 4; 4 is the lowest dimension score of its review, a different context.

## Class 3: a term used in a sense the canon does not give

Reported by the validator: no.

**Replaced text.**

```text
The canon is the one source of numbers, names, variants and rules for the cell, and each of its sections has an owner and a version.
```

**New text.**

```text
The canon is a starting point for numbers and names for the cell: it may be extended by any role during a round, as long as the sections have an owner and a version.
```

**Where an input common to both arms shows it.** The canon is the one source of numbers, names, variants and rules for the cell, and each of its sections has an owner and a version.

**A note counts as a find if it says:** States that the canon is used as a permissive starting point, not as the one source of numbers, names, variants and rules.

## Class 4: a sentence that contradicts the principle

Reported by the validator: no.

**Replaced text.**

```text
- Two artifacts state different numbers for the same fact: the canon is not being read, or the validator does not read it.
```

**New text.**

```text
- Two artifacts state different numbers for the same fact: that is acceptable, since each artifact has its own owner and version.
```

**Where an input common to both arms shows it.** Two artifacts state different numbers for the same fact: the canon is not the single source, or the validator does not read it.

**A note counts as a find if it says:** States that the sentence contradicts the principle, which treats divergent numbers for the same fact as a failure of the canon and the validator.

## Class 5: an absolute path

Reported by the validator: yes.

**Replaced text.**

```text
The one owner decision, the audience, is already decided and blocks the guide.
```

**New text.**

```text
The one owner decision, the audience, is already decided and blocks the guide; the brief file is kept at /home/author/cells/guide/00-brief.md.
```

**Where an input common to both arms shows it.** nn-form: plain Markdown, no HTML, no absolute path, no authoring date, no machine name.

**A note counts as a find if it says:** States that an absolute path of a machine was introduced, violating the nn-form non-negotiable.

## Class 6: a broken link to the canon

Reported by the validator: yes.

**Replaced text.**

```text
Canon: [02-canon.json](02-canon.json)
```

**New text.**

```text
Canon: [02-canon.json](02-canon.md)
```

**Where an input common to both arms shows it.** The file listing of the cell is: 00-brief.md, 01-sources-of-truth.md, 02-canon.json, 03-artifacts.json, 04-roles/, 05-contracts/, 06-gates.md, 07-rubric.md, 08-validator/, 09-engine/, guide.md, lessons.md, open-notes.json, priors.json, review/, state/.

**A note counts as a find if it says:** States that the canon link points to 02-canon.md, a file that is not in the cell listing (the canon is 02-canon.json).

## Class 7: a claim of efficacy without a label

Reported by the validator: no.

**Replaced text.**

```text
Write the rubric before the first review, or each round will measure something different and no verdict of one round can be compared with another.
```

**New text.**

```text
Write the rubric before the first review, or each round will measure something different and no verdict of one round can be compared with another; a rubric written beforehand makes reviewers find substantially more defects than one written after.
```

**Where an input common to both arms shows it.** The efficacy triggers of the canon list 'the method finds', and no attached file supports that a rubric written beforehand makes reviewers find substantially more defects; the one pilot (experiment E3) says the rubric is not what made the defects visible.

**A note counts as a find if it says:** States that an unlabeled efficacy claim about finding more defects was added, and that the principle/corpus carries no evidence for it.

## Class 8: an omitted step of the list of steps

Reported by the validator: no.

**Replaced text.**

```text
8. Draw the dependency graph; if it has a cycle, it is wrong; add the owner decisions as nodes.
```

**New text.**

(the line is removed)

**Where an input common to both arms shows it.** The principle's recipe and section 7 fix the steps; step 3 says 'Draw the graph; if it has a cycle, it is wrong' and step 7 of the method makes a human decision a node, so omitting the step breaks the numbered sequence of the preparation.

**A note counts as a find if it says:** States that step 8 (draw the dependency graph, reject a cycle, add owner decisions as nodes) was silently removed from the numbered list.

## Class 9: a limit without a justification

Reported by the validator: yes.

**Replaced text.**

```text
| `d-hypothesis` | guide | sentences claiming the method works without the hypothesis mark | 0 | [method] the principle states its claims of efficacy as marked hypotheses, and a guide about the method inherits the marking |
```

**New text.**

```text
| `d-hypothesis` | guide | sentences claiming the method works without the hypothesis mark | 0 | follows from the rules |
```

**Where an input common to both arms shows it.** A gate is declared with what is measured, the limit, and the justification beside it with its origin label: [method] when the principle states it, [brief] when the brief sets it, [hypothesis] when it is a working hypothesis.

**A note counts as a find if it says:** States that the Justification cell of the d-hypothesis row lost its origin label and now says nothing (no [method]/[brief]/[hypothesis] justification).

## Class 10: a factual error outside every class the rubric anticipates

Reported by the validator: no.

**Replaced text.**

```text
In the executed instance no engine rebuilt a stale artifact from the hash of its inputs — the writer and the orchestrator rebuilt by hand [prior:004-adoption-guide] — and the cell recorded the decision not to keep a separate engine at its scale [prior:004-adoption-guide].
```

**New text.**

```text
In the executed instance the engine rebuilt a stale artifact from the hash of its inputs, and the cell recorded the decision not to keep a separate engine at its scale [prior:004-adoption-guide].
```

**Where an input common to both arms shows it.** In the one execution no engine rebuilt a stale artifact from the hash of its inputs; the writer and the orchestrator rebuilt by hand.

**A note counts as a find if it says:** States that the sentence contradicts the prior and the principle: in the executed instance no engine rebuilt from the hash; the writer and orchestrator rebuilt by hand.
