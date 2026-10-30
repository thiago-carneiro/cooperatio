# Replies to the review notes

One line per note of the reviewer's report (`auditor-report.md`, round 1), in
the order of `auditor-notes.json`. Possible replies: done (where), partial
(what is missing), open (goes to `notes.json`). By the brief's stopping
criterion, only the `blocking` and `high` notes are applied; the others stay
open, except those that the fix of the blocking note resolved entirely.

| Note | Severity | Target | Reply |
| --- | --- | --- | --- |
| 0. claim about the case absent from the source (a role that compensated for the defect) | blocking | `recipe` | done. The gate first: `p-case-mark` (every paragraph, item or table row that speaks of the reference case carries the mark), which rejected the revised version in 10 units, among them the blocking one. Then the fix: the trap of step 5 was rewritten with what the case supports (declared value attenuated at the output, fix in the engine, "do not invent: note to the request owner"), and each of the 10 units was checked against the case method document and marked with the section. Permanent perturbation added to `80-validator/sensitivity.py` (13 of 13) |
| 1. "Verdict by the recipe's rule" with no rule in the recipe (text) | high | `instance-text-2027` | done: rule written in section 6 of the instance and "Verdict rule" template added to "Templates to copy" in the recipe, cited in step 8 |
| 2. same (HPC) | high | `instance-hpc` | done: same, in section 6 |
| 3. coverage of the sensitivity test | medium | `instrument-validator` | open (the perturbation of the new gate went in; those of `p-anchor`, `p-size`, `p-sections`, `p-frozen-rubric` and `p-notes` are still missing) |
| 4. qualitative claims about the case without a gate; `p-case` accepts a number out of context | medium | `gates-and-rubric` | partial: the first half became the gate `p-case-mark` (it was the cause of the blocking note); the check of the number in context and the requirement of the section stay open, rewritten in `notes.json` |
| 5. "Case numbers" table not read by an instrument; 0.15 s and 24 h outside it | medium | `instrument-validator` | open |
| 6. OpenMP fix that does not match the symptom | medium | `instance-hpc` | open |
| 7. gates that "are born" in the loop are already in the initial state (HPC) | medium | `instance-hpc` | open |
| 8. same, reading of numbers written out in words (text) | medium | `instance-text-2027` | open |
| 9. the arithmetic of `t-source-density` does not support "floor" | medium | `instance-text-2027` | open |
| 10. orchestrator as author of artifacts | medium | `recipe` | open |
| 11. rubric written by the writer, against step 8 | medium | `artifacts` | open; also recorded in `99-lessons.md` |
| 12. "reference-case rule" that is a quotation of the principle | medium | `instance-text-2027` | done, as part of the fix of the blocking note: the new gate flagged it; the sentence now attributes to the case what it says (the writer does not create claims, step 5 of the case) and to the principle the general formulation |
| 13. principle diverges from the case in two numbers | medium | `corpus` | open; the corpus does not belong to this work |
| 14. principle states about the case things that the case method document does not have | medium | `corpus` | open; same |
| 15. homonymous files: inference stated as fact | low | `recipe` | done, as part of the fix of the blocking note: when checking the unit in order to mark it, the inference came to be stated as an inference |
| 16 to 25 | low | several | open |

New note, found by the verifier during the work and not by the review: the
"Terms to avoid" table has no accepted variant by place and reason (open).

Change after the review, not a review finding: the count of method components
was reconciled to eleven across the principle, the bible, the gate
`p-components` and the instances, adding the gate sensitivity test that the
principle already counted. The review report and the notes in this folder are
a record of the version the reviewer read and still cite ten.
