# Answer key: document, rep3

Ten seeded defects, one per class, in `seeded/rep3/guide.md`; each is an exact replacement of
text of `clean/guide.md` (an omitted step is a removed line, and the list is renumbered).
"Reported by the validator" says whether the automatic checks report that arm A received
(`automatic-checks/rep3.md`) names the defect. This file is an answer: never give it to a reviewer.

## Class 1: an invented number about the registered prior

Reported by the validator: yes.

**Replaced text.**

```text
The recorded facts of this canon are the numbers this guide may state about its prior: 1054 words of its guide at the close, the range of 900 to 1400 words its brief set, and 4 as the lowest dimension score of its one review [prior:004-adoption-guide].
```

**New text.**

```text
The recorded facts of this canon are the numbers this guide may state about its prior: 1054 words of its guide at the close, the range of 900 to 1400 words its brief set, and 5 as the lowest dimension score of its one review [prior:004-adoption-guide].
```

**Where an input common to both arms shows it.** In 02-canon.json: { "number": "4", "context": "the lowest dimension score of its one review [prior:004-adoption-guide]", "section": "4.5" }.

**A note counts as a find if it says:** The lowest dimension score of the prior's one review is 4, as the canon records, not 5; the stated number is not among the recorded facts.

## Class 2: a number that exists in the source but in another context

Reported by the validator: no.

**Replaced text.**

```text
The hash exists so that only what changed is recompiled; that is the design, and the cell should say plainly what is design and what ran.
```

**New text.**

```text
The hash exists so that only what changed is recompiled; the executed instance recompiled 4 artifacts from the hash of their inputs, and that is the design, and the cell should say plainly what is design and what ran.
```

**Where an input common to both arms shows it.** In 02-canon.json recorded facts, 4 is "the lowest dimension score of its one review [prior:004-adoption-guide]"; the principle says no engine rebuilt a stale artifact from the hash of its inputs in the one execution.

**A note counts as a find if it says:** The number 4 belongs to the prior's lowest review score, not to any recompilation by hash; and the prior recorded that no engine rebuilt by hash.

## Class 3: a term used in a sense the canon does not give

Reported by the validator: no.

**Replaced text.**

```text
Write the rubric before the first review, or each round will measure something different and no verdict of one round can be compared with another.
```

**New text.**

```text
Write the rubric before the first review, or each round will measure something different and no verdict of one round can be compared with another; the rubric is the canon of the review.
```

**Where an input common to both arms shows it.** The canon is defined as the single source of numbers, names, terms and decisions with an owner and a version per section (principle, section 3 scheme and section 4); the rubric is not a canon in the canon's sense.

**A note counts as a find if it says:** The rubric is not a canon: the canon is the numbered, versioned source of numbers, names, terms and rules, and the rubric is a separate instrument.

## Class 4: a sentence that contradicts the principle

Reported by the validator: no.

**Replaced text.**

```text
A gate is a measurable function over an artifact that returns pass or reject with the magnitude measured, never only a signal.
```

**New text.**

```text
A gate is a measurable function over an artifact that returns pass or reject; the magnitude measured is optional, and only the signal is required.
```

**Where an input common to both arms shows it.** Principle, section 3: "Gate = measurable function over an artifact that returns pass/reject with the magnitude measured, never only a signal"; section 4: requiring only "greater than zero" lets a broken instrument pass.

**A note counts as a find if it says:** The principle requires a gate to return the magnitude measured, never only a signal; the guide contradicts it by making the magnitude optional.

## Class 5: an absolute path

Reported by the validator: yes.

**Replaced text.**

```text
The recipe ends with an assembly engine: the code that composes the artifacts into the target, with contracts that refuse ambiguity and outputs named by version tag.
```

**New text.**

```text
The recipe ends with an assembly engine: the code that composes the artifacts into the target, with contracts that refuse ambiguity and outputs named by version tag; run it from /home/author/cells/assembly/engine.sh before each round.
```

**Where an input common to both arms shows it.** Listing of the cell: no such path exists in the cell, and the non-negotiable nn-form refuses absolute paths in any durable artifact; principle golden rule 6: absolute paths do not enter a durable artifact.

**A note counts as a find if it says:** The guide carries an absolute machine path, which the brief's nn-form forbids and which points outside the cell.

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

**Where an input common to both arms shows it.** Listing of the cell: the file is 02-canon.json; there is no 02-canon.md among the cell's files.

**A note counts as a find if it says:** The canon link points to 02-canon.md, a file that does not exist in the cell; the canon is 02-canon.json.

## Class 7: a claim of efficacy without a label

Reported by the validator: no.

**Replaced text.**

```text
This cell's brief is the worked example.
```

**New text.**

```text
This cell's brief is the worked example, and the method works: it finds more defects than a careful review without it.
```

**Where an input common to both arms shows it.** Principle section 9: efficacy evidence is one-armed; the claim that the method finds more than its absence is a hypothesis [hypothesis], and no unlabelled claim of efficacy is allowed.

**A note counts as a find if it says:** The sentence claims the method works without any evidence and without the hypothesis mark; the principle states such efficacy claims only as marked hypotheses.

## Class 8: an omitted step of the list of steps

Reported by the validator: no.

**Replaced text.**

```text
3. Write the sources of truth: one row per content type, one named source per row, none of them the writer.
```

**New text.**

(the line is removed)

**Where an input common to both arms shows it.** Listing of the cell contains 01-sources-of-truth.md; the principle recipe step 2 and golden rule 2 require one row per content type with one named source per row.

**A note counts as a find if it says:** the numbered list of steps lacks the step that the principle's recipe requires here (3. Write the sources of truth)

**Corrected before sealing.** the seeder shortened the step; made a real omission.

## Class 9: a limit without a justification

Reported by the validator: yes.

**Replaced text.**

```text
| `d-size` | guide | words of the guide | 2,500 to 3,500 | [brief] the brief sets the range and the owner owns it, so the writer inherits the limit instead of choosing it |
```

**New text.**

```text
| `d-size` | guide | words of the guide | 2,500 to 3,500 | the limit is the limit |
```

**Where an input common to both arms shows it.** The guide itself states each gate declares its justification with an origin label; the principle section 7 step 5 requires the justification of the limit written beside it.

**A note counts as a find if it says:** The d-size row's justification says nothing and carries no origin label; the gate table requires each limit to be justified with [method], [brief] or [hypothesis].

## Class 10: a factual error outside every class the rubric anticipates

Reported by the validator: no.

**Replaced text.**

```text
Prepared well, those four make the rest — cards, gates, rubric, validator — the principle applied rather than invented.
```

**New text.**

```text
Prepared well, those four make the rest — cards, gates, rubric, validator — the principle applied rather than invented, and the validator runs the cell's d- gates itself, so a fail in a domain gate is written into its report.
```

**Where an input common to both arms shows it.** The guide's own gates section: "the validator reads the result, refuses it when an input changed since it was written, turns a fail into a note and a missing result into a pending, never a pass; it does not run the cell's code."

**A note counts as a find if it says:** The validator does not run the cell's code or its d- gates; it only reads the result files they write, so the sentence states the opposite of how the instrument works.
