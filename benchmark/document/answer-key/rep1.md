# Answer key: document, rep1

Ten seeded defects, one per class, in `seeded/rep1/guide.md`; each is an exact replacement of
text of `clean/guide.md` (an omitted step is a removed line, and the list is renumbered).
"Reported by the validator" says whether the automatic checks report that arm A received
(`automatic-checks/rep1.md`) names the defect. This file is an answer: never give it to a reviewer.

## Class 1: an invented number about the registered prior

Reported by the validator: yes.

**Replaced text.**

```text
The executed instance perturbed its measurement with known defects injected into a copy of its guide, and the measurement rejected each of them [prior:004-adoption-guide].
```

**New text.**

```text
The executed instance perturbed its measurement with 12 known defects injected into a copy of its guide, and the measurement rejected each of them [prior:004-adoption-guide].
```

**Where an input common to both arms shows it.** The canon's recorded facts list 1054 words, 900, 1400 and 4 as the numbers this guide may state about its prior; the prior's method document records 'o teste de sensibilidade do instrumento injetou dez defeitos conhecidos' (10 defects, not 12).

**A note counts as a find if it says:** The guide states '12 known defects' for the prior's sensitivity test under its prior mark, but the recorded fact in the prior's method document is ten (10) defects.

## Class 2: a number that exists in the source but in another context

Reported by the validator: no.

**Replaced text.**

```text
The hash exists so that only what changed is recompiled; that is the design, and the cell should say plainly what is design and what ran.
```

**New text.**

```text
The hash exists so that only what changed is recompiled; that is the design, and the executed instance proved it, rebuilding stale artifacts from the hash of their inputs.
```

**Where an input common to both arms shows it.** The principle: 'In the one execution no engine rebuilt a stale artifact from the hash of its inputs; the writer and the orchestrator rebuilt by hand.'

**A note counts as a find if it says:** The guide now claims the hash-based recompilation ran in the executed instance, contradicting the principle's statement that no engine rebuilt a stale artifact and that the writer and orchestrator rebuilt by hand.

## Class 3: a term used in a sense the canon does not give

Reported by the validator: yes.

**Replaced text.**

```text
The non-negotiables are three, each named: every statement about the method can be checked in the principle, and every statement about a registered prior carries its mark; the terms of the canon are used in the canon's sense; plain Markdown, no HTML, no absolute path, no authoring date, no machine name.
```

**New text.**

```text
The non-negotiables are three, each named: every statement about the method can be checked in the principle, and every statement about a registered prior carries its mark; the terms of the canon are used in the canon's sense; plain Markdown, quality gate before every acceptance, no HTML, no absolute path, no authoring date, no machine name.
```

**Where an input common to both arms shows it.** The canon's 'terms to avoid' lists 'quality gate', and the brief's `nn-form` non-negotiable contains no such phrase.

**A note counts as a find if it says:** The brief's form non-negotiable is quoted with 'quality gate' inserted, a term the canon lists under 'terms to avoid'.

## Class 4: a sentence that contradicts the principle

Reported by the validator: no.

**Replaced text.**

```text
A running service has no assembled, done moment: a stopping criterion for it would be a fiction, and a service is run, not compiled.
```

**New text.**

```text
A running service has no assembled, done moment: a stopping criterion for it would be a fiction, so it qualifies only when its deployment plan is a discrete artifact that can be declared done.
```

**Where an input common to both arms shows it.** The principle, section 10: 'A continuous process or an ongoing service has no assembled, done moment: there the stopping criterion would be a fiction, and the method does not apply — a service is run, not compiled.'

**A note counts as a find if it says:** The guide now lets a running service qualify via a deployment plan, contradicting the principle's statement that the method does not apply to a service at all.

## Class 5: an absolute path

Reported by the validator: yes.

**Replaced text.**

```text
Freeze the rubric by hash before the review: the executed instance froze its rubric before production began [prior:004-adoption-guide].
```

**New text.**

```text
Freeze the rubric by hash before the review: save it to /home/author/cells/rubric.sha256 before production begins [prior:004-adoption-guide].
```

**Where an input common to both arms shows it.** The brief's `nn-form` non-negotiable: 'no absolute path'; the prior wrote its hash to a relative `07-rubric.sha256` inside the cell.

**A note counts as a find if it says:** An absolute path of a machine (/home/author/cells/rubric.sha256) is written into a durable artifact, violating the brief's form non-negotiable.

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

**Where an input common to both arms shows it.** The cell listing shows `02-canon.json`; `02-canon.md` is not present.

**A note counts as a find if it says:** The link to the canon near the top points to 02-canon.md, a file that is not in the cell; the canon is 02-canon.json.

## Class 7: a claim of efficacy without a label

Reported by the validator: no.

**Replaced text.**

```text
The canon is the one source of numbers, names, variants and rules for the cell, and each of its sections has an owner and a version.
```

**New text.**

```text
The canon is the one source of numbers, names, variants and rules for the cell, and each of its sections has an owner and a version; keeping the canon is what makes the method work in practice.
```

**Where an input common to both arms shows it.** The principle's efficacy triggers include the unmarked claim pattern, and section 9 states 'Evidence of efficacy is one-armed' and that 'the claim that the method finds more than its absence is a hypothesis [hypothesis]'.

**A note counts as a find if it says:** The sentence 'keeping the canon is what makes the method work in practice' asserts the method works with no evidence and no [hypothesis] label.

## Class 8: an omitted step of the list of steps

Reported by the validator: no.

**Replaced text.**

```text
4. Open the canon: canonical numbers with their spelling, accepted variants, names and terms, rules — an owner and a version per section.
```

**New text.**

(the line is removed)

**Where an input common to both arms shows it.** The guide's numbered list of steps begins '1. Check the four conditions', then 2. Write the brief, 3. Write the sources of truth, 4. Open the canon, and the following item is now empty with no content while the numbering remains fixed.

**A note counts as a find if it says:** the numbered list of steps lacks the step that the principle's recipe requires here (4. Open the canon)

**Corrected before sealing.** the seeder shortened the step; made a real omission.

## Class 9: a limit without a justification

Reported by the validator: yes.

**Replaced text.**

```text
| `d-graph-acyclic` | artifact graph | cycles in the dependency graph | 0 | [method] an acyclic graph is one of the four conditions the target must meet before the cell exists |
```

**New text.**

```text
| `d-graph-acyclic` | artifact graph | cycles in the dependency graph | 0 | it is good to check |
```

**Where an input common to both arms shows it.** The principle's section 7, step 5: 'If it cannot be measured, it is "contract + agent", not a gate; say so' and 'the justification of the limit written beside it' — the justification cell must carry the reason, not filler.

**A note counts as a find if it says:** The `d-graph-acyclic` row's justification is emptied to 'it is good to check', which states nothing; every gate's limit must carry its justification with origin label.

## Class 10: a factual error outside every class the rubric anticipates

Reported by the validator: no.

**Replaced text.**

```text
The brief answers what and for whom; the sources of truth answer where each kind of content comes from; the canon answers what the words and numbers are; the graph answers who owns what and in what order. Prepared well, those four make the rest — cards, gates, rubric, validator — the principle applied rather than invented.
```

**New text.**

```text
The brief answers what and for whom; the sources of truth answer where each kind of content comes from; the canon answers what the words and numbers are; the gates answer who owns what and in what order. Prepared well, those four make the rest — cards, graph, rubric, validator — the principle applied rather than invented.
```

**Where an input common to both arms shows it.** The guide itself: 'the artifact graph answers who owns what and in what order'; the role that owns ordering is the artifact graph, not the gates.

**A note counts as a find if it says:** The close says the gates answer who owns what and in what order; that role belongs to the artifact graph, as the guide states earlier.
