# Benchmark of seeded review defects

The inputs and the annotated answer keys of experiment E4, the seeded-escape
test of the review apparatus (`../02-reflexive-application/60-experiments.md`,
section E4, which holds the design, the results and what they do not show).
Two parts:

- `document/`: one guide of about 3,500 words written under a cell of the
  method, its clean copy and three seeded copies (`rep1`, `rep2`, `rep3`),
  ten defects each, one per class;
- `code/`: excerpts of three open-source programs with permissive licenses,
  one in Python (`asyncnet`, an asynchronous networking framework), one in C
  (`jsontool`, a JSON query tool) and one in C++ (`buildtool`, a build
  system), each anonymized, with a pristine copy and a seeded copy holding
  twelve defects, one per class.

## This folder holds the answers

Never give this folder, or any file of it as it stands, to a reviewer. A
reviewer receives only the files listed under "What a reviewer receives",
copied into a folder of its own under the names given there. The answer keys
name every defect; the notices, the licenses, `anonymization.json`,
`gates-detection.json` and the gates code name the programs or say which
defects the automatic checks report.

## What a reviewer receives

Document part, one run per copy (clean, `rep1`, `rep2` or `rep3`):

| File of this folder | Name the reviewer received | Arm A | Arm B | Arm C (auxiliary) |
| --- | --- | --- | --- | --- |
| `document/clean/guide.md` or `document/seeded/<rep>/guide.md` | `guide.md` | yes | yes | yes |
| `document/inputs/00-brief.md` | `00-brief.md` | yes | yes | yes |
| `document/inputs/02-canon.json` | `02-canon.json` | yes | yes | yes |
| `document/inputs/principle.md` | `principle.md` | yes | yes | yes |
| `document/inputs/prior-method-document.md` | `prior-method-document.md` | yes | yes | yes |
| `document/inputs/file-listing-of-the-cell.txt` | `file-listing-of-the-cell.txt` | yes | yes | yes |
| `document/arm-a/rubric.md` | `rubric.md` | yes | no | no |
| `document/arm-a/reviewer-card.md` | `reviewer-card.md` | yes | no | no |
| `document/automatic-checks/<copy>.md` | `automatic-checks-report.md` | yes | no | yes |
| `document/arm-b/checklist.md` | `checklist.md` | no | yes | yes |

The principle and the prior's method document are blind copies: the name of
the method replaced, and the principle without the passages about the
experiments, the seeded defects and the two arms, and without the table of
what would promote or withdraw a claim.

Code part, one run per tool:

| File of this folder | Name the reviewer received | Arm A | Arm B |
| --- | --- | --- | --- |
| every file under `code/<tool>/seeded/` (or `pristine/` for a clean run) | the same relative path | yes | yes |
| `code/rubric.md` | `rubric.md` | yes | no |
| `code/reviewer-card.md` | `reviewer-card.md` | yes | no |
| `code/<tool>/automatic-checks/seeded.md` (or `pristine.md`) | `automatic-checks-report.md` | yes | no |
| `code/checklist.md` | `checklist.md` | no | yes |

`code/brief.md` is the one-page brief the authors of the code rubric and
checklist wrote from; reviewers did not receive it.

The prompts are under `document/prompts/` and `code/prompts/`: the system
prompt, the same in every run, and one task prompt per arm, the same text but
for the sentence that names the apparatus. Each run was one chat completion,
with no tools, default sampling and every file attached as context, and had
to end with a line starting `VERDICT:` and one fenced JSON array of notes,
each with exactly the fields `location`, `problem` and `evidence`.

## How to reuse it unchanged

So that a new result compares with E4:

1. Check the files first: from inside this folder, `sha256sum -c
   MANIFEST.sha256` must report every file as OK. Edit nothing; a copy that
   differs is another benchmark.
2. Stage each run as the tables above say, with no other file, no diff and
   no hint of the number or the classes of the defects.
3. Use the reports under `automatic-checks/` as they are; do not regenerate
   them. The document reports came from the validator of method version
   0.7.0, the code reports from the gates code below on the analyzers of the
   run; a newer instrument is another arm.
4. A run that ends for length, or whose JSON does not parse, is a tool
   failure, re-run once; a run failing twice counts every defect as escaped,
   and is reported flagged, with a reading that leaves it out beside the one
   that counts it.
5. Score blind. Each adjudicator, who did not review, receives for each run
   only the notes, under an anonymous id and in a shuffled order, with the
   words that name the apparatus stripped, and the list of the seeded
   defects with the line that says what a note must state; and answers found
   or not found per defect. Primary count: found when two adjudicators say
   found; sensitivity: when either does. In the arms that receive the
   automatic checks, a defect the report names is counted as found: in the
   document part, the defects marked "Reported by the validator: yes" in the
   annotated key; in the code part, the rows of `gates-detection.json` whose
   list is not empty.
6. Count notes that match no seeded defect per run, on the clean and the
   seeded copies, without judging them true or false.

## The answer keys

- Document: `document/answer-key/<rep>.json`, as sealed before the first
  review (fields `class`, `old`, `new`, `shown_by`, `note_must_say`, and
  `orchestrator_fix` where the set was corrected before sealing), and
  `<rep>.md`, the same annotated: the class, the replaced and the new text,
  where an input common to both arms shows the defect, what a note must say,
  and whether the validator reported it. The classes: (1) an invented number
  about the registered prior, (2) a number that exists in the source but in
  another context, (3) a term used in a sense the canon does not give, (4) a
  sentence that contradicts the principle, (5) an absolute path, (6) a broken
  link to the canon, (7) a claim of efficacy without a label, (8) an omitted
  step of the list of steps, (9) a limit without a justification, (10) a
  factual error outside every class the rubric anticipates. The absolute
  paths of class 5 are invented and deliberate.
- Code: `code/<tool>/answer-key.json` and `answer-key.md`, anonymized like
  the code: per defect the id, the class, the file and lines of the seeded
  copy, the exact replacement, what is wrong and why, what a note must say,
  and how the seeder checked it. The classes: logic at a boundary (L1),
  semantic logic (L2), suboptimization (S), repetition (R), a clean-code
  break (C), unintelligible code (U), a layering violation (D), security (X),
  concurrency or shared state (K), a swallowed failure (E), a broken contract
  (A) and a resource lifecycle (M). S, R, C, U and D keep the observable
  behaviour. `gates-detection.json` says which gates' report names the lines
  of each defect.

## The gates code

`code/gates/gates.py` (static analyzers only, never a program's own tests),
`anonymize.py` and `build_reports.py` produced the code reports. They run on
the upstream source releases and on the excerpts before anonymization, which
are not part of this folder, so they are kept as the record of how the
reports were made, not as something a reuse needs. The copies differ from
the scripts as run only in the lines that held absolute paths of the run,
now read from the environment (`BENCHMARK_TOOLS_BIN`, `BENCHMARK_GCC_BIN`,
`BENCHMARK_SCRATCH`). The sha256 of the scripts as run:

| Script | sha256 as run |
| --- | --- |
| `gates.py` | `0b8a13646a938c73cd3b16164631cb2ab00a9b364d953f40410cfc46db487d9f` |
| `anonymize.py` | `d686178e35a39e9907e48b9fb67a61c25b317081881eabf85d9e7bda29608316` (unchanged here) |
| `build_reports.py` | `c22cd76fb64740e74eb15ff4ae39413e62edcc8e4c7bbd07b83e35f20f0624ce` |

## Known limits of the copies

- The code was anonymized by rules on whole names; in `jsontool` a few
  identifiers that carry the program's short name inside a longer one were
  left as they were, and reviewers received them so. A reviewer can also
  recognize any of the three programs from training.
- An excerpt is not a whole repository, and the programs' own tests are not
  part of it.
- The defects are one seeder's per part, of classes the designer chose.

## Licenses

The document part, the code brief, rubric, checklist, reviewer card and
prompts, and this README are under the license of the material, the Apache
License 2.0 (`../LICENSE`). Each code excerpt keeps the license of its
upstream program in its folder (`LICENSE` or `COPYING`): the Apache License
2.0 for `asyncnet` and `buildtool`, the MIT license for the code of
`jsontool`. Each folder's `NOTICE.md` states the modification (anonymized,
license headers emptied and reproduced there, deliberate defects in the
seeded copy) and that the copy must not be used in production or deployed in
any form. The gates code is under the license of the material.

`MANIFEST.sha256` lists the sha256 of every other file of this folder.
