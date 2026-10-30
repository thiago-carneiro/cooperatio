# Independent reviewer's report (round 1)

Independent review of the production that applies the method to itself. The
reviewer did not take part in the production and read only the files in the
folder, the corpus (the principle and the reference-case method document) and
the rubric in the "Rubric" section of `04-gates-and-rubric.md`, used unchanged.
The sha256 of that section was recomputed and is equal to the one stored in
`90-review/rubric.sha256`. The terms follow the [bible](../01-bible.md).

## 1. Verdict

**Rejected.**

The rubric's mechanical rule, applied:

- There is one `blocking` finding: the recipe states about the case something
  that the reference-case method document does not record (step 5: the
  designer role that "raised the requested value" instead of notifying the
  engine). That alone closes the
  verdict as `rejected`.
- Dimension D1 (Fidelity to the principle) scores 2, which under the same rule
  also rejects.
- The two `high` findings (the instance rubrics of the text and HPC instances
  have no verdict rule) and dimensions D5 and D6 scoring 3 would prevent
  `acceptable` even without the blocking one.

The defect that decides is small and localized: a sentence inherited from the
principle, fixed by rewriting one trap. The cause, however, is structural and
deserves more attention than the sentence. No gate checks a qualitative claim
about the case, because rule 5 of the bible only requires `[case]` on a numeric
claim. That is also why the claim went through the validator without a
note.

## 2. Scores by dimension

| Dimension | Score | Evidence |
| --- | --- | --- |
| D1 Fidelity to the principle | 2 | The ten components and the golden rules are applied, including in the production itself (gates with magnitude, a validator in code with a sensitivity test, a rubric frozen by hash). But `10-generic-recipe.md`, lines 229-231, attributes to the reference case a fact that the reference-case method document does not have, and `21-instance-text-2027.md`, line 109, cites as a "rule of the reference case" a sentence from the principle. Anchor 1 of the rubric ("invents a fact of the case") applies to the first. The score stays at 2, and not 1, because the sentence was copied from the corpus and not made up, and the rest checks out. |
| D2 Recipe executability | 4 | The fifteen steps have "Reads", "Creates", "Does" and "Done when", and almost every done criterion is a count or an equality (for example, step 9: "two runs over the same input give an identical report"). What requires interpretation: the orchestrator, which is a step and not a role, appears as the author of the cards and of the artifact list (steps 4, 5 and 14), and the recipe gives no template for a verdict rule, which two instances ended up citing as if it existed. |
| D3 Concreteness of instances | 5 | A specialist recognizes the artifacts, roles and gates of each domain. In the car: 800 V platform, 10% to 80% recharge, WLTP, MC/DC coverage, correlation between simulation and test, regulatory matrix. In the text: claims register separate from the chapters, projection with a resolution criterion, a single edition per series. In HPC: oracle with a hash, mutations against the equivalence gate, threads obtained and not requested, multiplexed counters, ablation. No row of the instantiation table would serve another target. |
| D4 Gates and numbers | 4 | Almost every limit has a magnitude, an origin label and a why (for example, `g-mass-budget`, with a reserve that shrinks with fidelity, and `h-sweep`). Some justifications are weak: the arithmetic of `t-source-density` does not support "floor" and that of `h-noise` is truncated. There are gates declared only in the artifact table, without justification (`budgets`, `theme-map`, `domain-dossier`, `oracle`). In the production, `p-sensitivity` does not cover three document gates, and `p-case` only sees numbers. |
| D5 Internal coherence | 3 | Coherent overall, with local slips that an attentive reader finds. Examples in the loop contradict the instance's own initial state (`22-instance-hpc.md`, lines 358-367; `21-instance-text-2027.md`, lines 323 and 366-370). The drawing of the car's graph diverges from its table. The bible says the validator reads all of its tables, but "Case numbers" is not read, and two case numbers in use (0.15 s and 24 h) are not in it. The `bible` artifact has two owners, against the definition of artifact. |
| D6 Reflexivity | 3 | The production followed its own method: brief, bible, acyclic graph, cards, gates measured by code, deterministic report, frozen rubric, one independent review and a declared stop. There are undeclared gaps: the rubric was written by the writer, against step 8 of the recipe ("never whoever is going to produce alone"); `p-sensitivity` promises one defect per gate and tests ten of thirteen; the "Case numbers" table is read by no instrument. The declared gap (owner decisions without a file of their own, in `02-artifacts.md`) counts in its favor. |
| D7 Form | 5 | American English, plain Markdown, every fenced block marked `text`, no HTML tag, no absolute path or authoring date, all sizes within the declared ranges. The validator's report, run again by the reviewer, gave the same measurements byte for byte. |
| D8 Epistemic honesty | 4 | Almost every domain assumption is marked `[hypothesis]`, including limits that come from the owner (`[brief] owner target [hypothesis: illustrative value]`), and the documents separate method, case and domain. There are claims larger than the evidence: the recipe states as fact the case's inference about same-named files; the self-test docstring promises one case per rule; `p-sensitivity` describes itself as "one per document gate". |

## 3. Findings by severity

### Blocking

1. **`recipe`**. Step 5 states: "In the reference case, the designer role
   'raised the requested value' instead of notifying the engine, which
   delivered less than was asked". The reference-case method document does not
   record this. It says that a declared input arrived attenuated at the output
   and that the engine was changed to apply it correctly (section 1.10 and
   step 9), with no role compensating for the defect. The role, there, has a
   different name. The sentence comes from the principle (section 4, row
   "Roles with a card"). The brief forbids stating about the case anything that
   is not in the reference-case method document, and the justification of
   `p-case` treats a claim absent from the source as an invented fact until
   proven otherwise. Evidence: `10-generic-recipe.md`, lines 229-231; searches
   for "compens", "raised", "raising", "notif" and "designer" in the
   reference-case method document, with no occurrence in the claimed sense.
   Suggested fix: use what the case supports. The pseudocode of the designer
   role (section 4.14 of the reference-case method document) has "the engine
   lacks the requested component -> do not invent: note to the owner of the
   request", which serves the same trap.

### High

1. **`instance-text-2027`**. The instance's rubric ends with "Verdict by the
   recipe's rule", but the recipe has no concrete rule: step 8, item 4, only
   says to write one. Evidence: `21-instance-text-2027.md`, line 314;
   `10-generic-recipe.md`, lines 300-302. The car instance writes the rule
   (lines 370-373).
2. **`instance-hpc`**. The same defect: "Verdict by the recipe's rule".
   Evidence: `22-instance-hpc.md`, lines 293-294.

### Medium

1. **`instrument-validator`**. `p-sensitivity` promises one injected
   defect per document gate, but covers 10 of the 13. `p-anchor`, `p-size` and
   `p-sections` were never perturbed, nor were `p-frozen-rubric` and `p-notes`.
   The validator only reads "Caught X of Y" from a stored file, without
   checking the coverage or whether the file corresponds to the current
   documents. A probe by the reviewer on a copy showed that these gates do
   reject the known defect; what is missing is the proof, not the behavior.
   Evidence: `sensitivity.py`, lines 31-59; `validator.py`,
   `check_global`.
2. **`gates-and-rubric`**. `p-case` only checks numbers in units marked
   `[case]`, and rule 5 of the bible only requires the mark on a numeric claim.
   Qualitative claims about the case stay without a mark and without a gate:
   there are nine, from `10-generic-recipe.md` line 160 to
   `22-instance-hpc.md` line 356. Besides that, `p-case` accepts the number if
   it is anywhere in the reference-case method document, and small numbers
   always pass. It was through this hole that the blocking finding escaped.
3. **`instrument-validator`**. The bible says the validator
   reads its tables and that a case number only enters if it is in "Case
   numbers". The script does not read that table, and two numbers in use are not
   in it: 0.15 s (`10-generic-recipe.md`, line 283) and 24 h
   (`21-instance-text-2027.md`, line 278). Both check against the
   reference-case method document.
4. **`instance-hpc`**. In the example "Regression that escaped", the symptom is
   correct and serial work, but the fix indicated ("divide by the number of
   threads the runtime gave, or use a worksharing loop") is the fix for another
   defect: the manual division by the requested number, which in a nested
   region with one thread processes 1/k of the data and would fail equivalence.
   For a correct and serial region, parallelism comes back by removing the
   nesting or enabling nested levels. It also lacks saying where the obtained
   threads are measured: read outside the region that does the work, they do not
   catch the case. Evidence: `22-instance-hpc.md`, lines 358-363.
5. **`instance-hpc`**. By the loop, `h-obtained-configuration` and `h-counters`
   "are born" during the rounds, but both are already in sections 3, 5 and 8
   since v1. Besides that, section 5 calls the thread divergence a "tool
   failure, not a rejection", and the loop says it "rejects the current
   version", with the cause in the product. Evidence: lines 87, 255, 260,
   320-321 and 358-367.
6. **`instance-text-2027`**. The loop says "the validator only read
   digits", but section 7 already checks numbers in words from the start.
   Evidence: lines 323 and 366-370.
7. **`instance-text-2027`**. In `t-source-density`, one note every 200 to 300
   words gives 3.3 to 5 per thousand, and the limit of 4 per thousand, called
   "the floor, not the target", falls inside that range, not below it.
   Evidence: line 273.
8. **`recipe`**. The orchestrator is defined as a step, which "does not decide
   anything that a card assigns to a role". Even so, it is the author of the
   artifact list, of the cards and of the case method document (steps 4, 5 and
   14), which are left without an owner role, against the "Done when" of step
   4. Evidence: lines 74-76, 188, 213 and 451; term "orchestrator" in the bible.
9. **`artifacts`**. The rubric of this production is owned by the writer, the
   role that wrote everything it measures, against step 8 of the recipe. The
   deviation is not declared. Evidence: `02-artifacts.md`, row of
   `gates-and-rubric`; `10-generic-recipe.md`, line 291.
10. **`instance-text-2027`**. "It is the rule of the reference case ('the fact
    never comes from the writer')": the sentence is golden rule 2 of the
    principle. The reference-case method document does not have the word
    "writer", although the substance checks out (sections 1.7 and 2.1).
    Evidence: line 109.
11. **`corpus`**. The principle diverges from the case on two numbers: "13 notes
    from the automatic reviewer, 10 of them false", against 12 and 10 in the
    case (step 15, section 5.3); "3 blocking notes that the team had looked at
    and approved", against "Two of the blocking notes were pending items that
    had been noted and let go" (section 1.1).
12. **`corpus`**. The principle states about the case seven things absent from
    the reference-case method document: a role that compensated for a defect
    of the engine; "54 high notes" attributed to an outdated setup; "in three
    years" on a card; an item left with stale text; an unknown field that
    halted the assembly; a model "doing everything" that mixed several kinds of
    decision; the "six rules". The first one has already made its way into the
    recipe.

### Low

1. **`recipe`**. "Three files with the same name [...] confused the
   review" states as fact what the case records as an inference of the v2
   review ("probably read the same-named file"). Evidence: lines 366-368.
2. **`bible`**. The definition of artifact requires a single owner, but `bible`
   has two owners: the writer and the verifier, owner of "Case numbers". The
   case (section 1.2) shows the way out: a bible section as an artifact of its
   own.
3. **`cards`**. The outputs of the verifier and of the validator omit
   `sensitivity.py` and `sensitivity.md`, which are in their artifacts, and no
   card says who runs the sensitivity test.
4. **`bible`**. The list of components shortens the principle's names
   ("instrument" instead of "instrument with a root-cause fix"), and
   `p-components` passes only because the word appears. The instances have the
   practices; the gate does not prove them.
5. **`instance-car`**. The graph drawing has an arrow from `budgets` to
   `safety-analysis` that the table does not declare, and several edges of the
   table are missing.
6. **`instance-car`**. The limit "sum of allocated ≤ target", of `budgets`, has
   no row in the gates table and no justification.
7. **`instance-text-2027`**. The gates of `theme-map` and `domain-dossier` are
   only in the artifact table, with no name and no justification.
8. **`instance-hpc`**. The gates of `oracle`, `specification` and
   `implementation` have no magnitude and no row in the gates table; the last
   two are judgment and should be marked "contract + agent".
9. **`instance-hpc`**. The justification of `h-noise` is truncated: the risk is
   the lower limit of the interval and detection near the noise floor, not the
   1.5 itself.
10. **`instance-hpc`**. The brief lacks the "Provisional stopping criterion"
    row, which the recipe requires and the other two instances have.
11. **`instrument-validator`**. The self-test docstring promises "one
    positive and one negative case per rule", but nine rules have no test case.

## 4. Verified and correct

- The twelve numbers of the "Case numbers" table of the bible are in the
  reference-case method document, in the context and section cited: 18 roles
  (1.1, 2.1), 49 artifacts (2.1), 2 maximum rounds, 50 notes per gate and code 3
  (1.4), 3, 4, 12 and 12 of v1 and 12 and 10 of v2 (step 15), 0.546
  s, 0.10 s and 15 s (1.10), 38 and 2 (step 14), 31, 18 and 73 (step 16), 26
  (step 17).
- The units with `[case]` in the recipe (lines 253, 282, 287, 334, 387, 422 and
  445) and in the text instance (lines 278 and 365) check in context against the
  reference-case method document.
- The `[case]` justification of `p-determinism` (a report without a date
  and with relative paths, section 1.6 of the reference-case method document)
  and that of `p-notes` (the router refuses an unknown target, section 1.3)
  check out.
- The names of the case's three verdicts ("rejected", "acceptable with minor
  corrections", "acceptable") and the note contract (six fields, four
  severities, only `high` and `blocking` go back) check against sections 1.3 and
  3 of the reference-case method document.
- `p-frozen-rubric`: the sha256 of the "Rubric" section, recomputed separately,
  is equal to the stored one.
- The validator's self-test passes (exit 0). Run again, the validator
  gave a report identical byte for byte to the one stored in
  `80-validator/report.md`, with `p-determinism` passing and exit 0.
- The sensitivity test, run again in a scratch folder, gave a result identical
  to the stored one: 12 of 12 caught.
- Reviewer probe on a copy of the folder: link to the bible deleted, card
  inflated to 2,334 words, "Validator" section renamed in the HPC
  instance and text added to the rubric. `p-anchor`, `p-size`, `p-sections` and
  `p-frozen-rubric` rejected, the latter with a `blocking` note to `review`.
- The notes in this report validate against the contract: the
  validator, with `--notes`, measured 26 notes and 0 invalid.
- The graph of `02-artifacts.md` is acyclic and every owner is a role or
  `owner` (`p-references` passed, and reading the table confirms it).
- The recipe has fifteen steps, each with the four fields, and the map to the
  twelve steps of the principle closes.
- The three instances have the fourteen sections and the fourteen rows of the
  instantiation table, all filled with domain content, checked by reading.
- No absolute path, authoring date, machine name or user name appeared, neither
  in reading nor in the search for typical marks.

## 5. Not verified

- **The external list of forbidden identifiers.** It sits outside the folder and
  was not handed to the reviewer; the validator ran with an empty list.
  The report came out equal to the stored one, but that does not prove that the
  real list would flag nothing.
- **Domain numbers checked only for plausibility**, with the reviewer's
  knowledge and no primary source opened. They are: MC/DC strongly recommended
  for the highest integrity level in the functional safety standard; 10% to 80%
  recharge in about 20 min on 800 V platforms; interior noise of 68 dB(A) at 120
  km/h; scale of the readability index adapted to Portuguese; typical density of
  notes in nonfiction; scaling of counters multiplexed by the kernel.
- **`g-thermal-propagation`** ("≥ 5 min, with warning"). According to the
  reviewer's knowledge, the most recent revision of the Chinese traction-battery
  safety standard came to require no fire and no explosion, and not a warning
  interval. If so, "recent regulations" describes the previous generation. The
  limit is marked `[hypothesis]` and says that the market's standard confirms or
  replaces it; what is missing is opening the text of the standard to decide.
- **Default behavior of nesting in OpenMP** (how many active levels by default,
  per runtime version). The instance says "may become one", which is cautious;
  the reviewer did not check it against the specification.
- **The principle's claims about the case** may be in other files of the
  reference case (cards, flow, review reports), which the reviewer did not open.
  The check was made only against the reference-case method document, as the
  brief orders.

## 6. Out of scope

- Fixing the principle. The divergences between the principle and the case are
  in the notes to the `corpus`, and the decision to fix them is the owner's
  (open in the brief).
- Checking whether the parent folder's index (the README of the general method)
  describes this folder correctly: it is not in this production's graph.
- The regulatory update on thermal propagation matters for a real instance of
  the car, not for this production.

## 7. Notes in JSON

```text
[
  {
    "target_artifact": "recipe",
    "severity": "blocking",
    "text": "Claim about the case that is not in the reference-case method document: 'In the reference case, the designer role \"raised the requested value\" instead of notifying the engine, which delivered less than was asked'. The reference-case method document says only that a declared input arrived attenuated at the output and that the engine was fixed (section 1.10 and step 9); it records no role compensating for the defect, and the role there has a different name. The sentence comes from the principle (corpus), not from the case. By the brief's non-negotiable and by the rule of p-case itself, a claim absent from the source is an invented fact until proven otherwise. Fix: rewrite the trap with what the case supports (the engine delivered less than requested, and the fix was in the engine; the designer role's pseudocode in section 4.14 says 'the engine lacks the requested component -> do not invent: note to the owner of the request') or remove the attribution to the reference case.",
    "origin": "reviewer",
    "evidence": "10-generic-recipe.md, step 5, lines 229-231; search for 'compens', 'raised', 'raising', 'notif' and 'designer' in the reference-case method document with no occurrence in the claimed sense; sections 1.10 and 4.14 and step 9 of the reference-case method document",
    "round": 1
  },
  {
    "target_artifact": "instance-text-2027",
    "severity": "high",
    "text": "The instance's rubric ends with 'Verdict by the recipe's rule', but the recipe has no concrete verdict rule: step 8, item 4, only says to write one. An agent running the review of this instance cannot apply the verdict mechanically without inventing the rule. Fix: write the rule, as the car instance does in section 6 (rejected if there is a blocking finding or a dimension ≤ 2; acceptable if there is no high finding and all dimensions ≥ 4; otherwise acceptable with minor corrections), or put a rule template in 'Templates to copy' of the recipe and cite it.",
    "origin": "reviewer",
    "evidence": "21-instance-text-2027.md, section 6, line 314; 10-generic-recipe.md, step 8, lines 300-302 and section 'Templates to copy' (no rule); compare 20-instance-car.md, lines 370-373",
    "round": 1
  },
  {
    "target_artifact": "instance-hpc",
    "severity": "high",
    "text": "The instance's rubric ends with 'Verdict by the recipe's rule', a rule that the recipe does not contain (step 8 only says to write one). The element is filled with a reference to nonexistent content, and the verdict cannot be applied without inventing the rule. Fix: write the rule in section 6, as the car instance does.",
    "origin": "reviewer",
    "evidence": "22-instance-hpc.md, section 6, lines 293-294; 10-generic-recipe.md, step 8, lines 300-302",
    "round": 1
  },
  {
    "target_artifact": "instrument-validator",
    "severity": "medium",
    "text": "p-sensitivity promises 'one injected defect per document gate', but sensitivity.py has 12 perturbations that cover 10 of the 13 document gates: p-anchor, p-size and p-sections were never perturbed, and neither were p-frozen-rubric (blocking) and p-notes. The validator only reads the line 'Caught X of Y' from sensitivity.md: it checks neither the coverage against the list of gates nor whether the file belongs to the current version of the documents, so the gate passes while its own definition is not fulfilled. A reviewer probe on a copy showed that the untested gates do reject the known defect; the gap is one of proof, not of behavior. Fix: add the missing perturbations and make the gate compare the set of perturbed gates with the gates table.",
    "origin": "reviewer",
    "evidence": "04-gates-and-rubric.md, row of p-sensitivity; 80-validator/sensitivity.py, PERTURBATIONS (lines 31-59); 80-validator/validator.py, check_global (reading of 'Caught X of Y'); reviewer probe on a copy: p-anchor 0, p-size 2,334 words, p-sections 13/14 and p-frozen-rubric 'different' rejected",
    "round": 1
  },
  {
    "target_artifact": "gates-and-rubric",
    "severity": "medium",
    "text": "p-case only checks numbers in units marked [case], and rule 5 of the bible only requires [case] on a numeric claim. Qualitative claims about the case ('In the reference case, ...') stay without a mark and without a gate; that is how the recipe's blocking claim about the designer went through every gate. Besides that, p-case accepts the number if it appears anywhere in the reference-case method document, not in the claimed context, and small numbers (2, 3, 4, 12) always pass. By golden rule 4, a regression that escaped every gate gets a gate. Fix: require [case] on every claim about the case, with the section of the reference-case method document alongside, and put the check of those lines in the verifier's exit gate.",
    "origin": "reviewer",
    "evidence": "04-gates-and-rubric.md, row of p-case; 01-bible.md, 'Form rules', rule 5; unmarked claims: 10-generic-recipe.md lines 160, 206, 229, 312 and 366; 21-instance-text-2027.md lines 10, 109 and 268; 22-instance-hpc.md line 356; validator.py, case_number_hits and number_in",
    "round": 1
  },
  {
    "target_artifact": "instrument-validator",
    "severity": "medium",
    "text": "The bible says the validator reads its tables ('changing a table changes what it checks') and that no case number enters a document without being in the 'Case numbers' table. The script does not read that table (load_bible loads terms to avoid and fixed lists), and p-case checks against the reference-case method document. Result: two case numbers already in use are not in the table, 0.15 s (drift limit, in the recipe) and 24 h (recheck of volatile items, in the text instance). Both check against the reference-case method document; the defect is that the bible stops being the source of truth without any gate noticing. Fix: add the two numbers to the table and make p-case require that every [case] number be in it.",
    "origin": "reviewer",
    "evidence": "01-bible.md, lines 4-5 and 172-174; validator.py, load_bible; 10-generic-recipe.md, lines 281-283; 21-instance-text-2027.md, line 278; reference-case method document, section 1.10 and table of section 2.4 (G1)",
    "round": 1
  },
  {
    "target_artifact": "instance-hpc",
    "severity": "medium",
    "text": "In the example 'Regression that escaped', the symptom is correct and serial work (8 and 16 threads give the same time, every result gate passes), but the fix indicated, 'divide by the number of threads the runtime gave, or use a worksharing loop', fixes another defect: the manual division by the requested number, which in a nested region with one thread processes only 1/k of the data and would fail equivalence. With a correct and serial region, what brings parallelism back is removing the nesting (parallelizing at the outer level, collapsing loops) or enabling nested active levels. It also lacks saying where the obtained threads are measured: if they are read outside the region that does the work, h-obtained-configuration does not catch the case. Fix: align the fix with the symptom and declare the measurement point.",
    "origin": "reviewer",
    "evidence": "22-instance-hpc.md, section 10, lines 358-363; section 3, 'measures' schema (line 87); section 5, row of h-obtained-configuration",
    "round": 1
  },
  {
    "target_artifact": "instance-hpc",
    "severity": "medium",
    "text": "The loop's examples contradict the instance's own initial state. According to the loop, h-obtained-configuration and h-counters 'are born' from a regression and from an instrument fix, but both are already in the gates table of section 5, in the CSV schema of section 3 and in the engine of section 8 since the first version, so the regression as told could not have escaped. Besides that, section 5 classifies the thread divergence as 'tool failure, not rejection', while the loop says the gate 'rejects the current version' and the cause is a product defect (note to the implementation). Fix: take the two gates out of the initial state and say they enter through the loop, or swap the examples; and separate the divergence caused by the environment (tool failure) from the one caused by the library (rejection with a note to the implementation).",
    "origin": "reviewer",
    "evidence": "22-instance-hpc.md, lines 87, 255, 260, 320-321, 358-367; experiment engineer card, lines 179-180",
    "round": 1
  },
  {
    "target_artifact": "instance-text-2027",
    "severity": "medium",
    "text": "The example 'Regression that escaped' says 'the validator only read digits' and that is why it gains the reading of numbers in words, but the validator table of section 7 already checks 'numbers in words (\"a quarter\", \"two thirds\")' from the start. The example cannot happen in the instance as written. Fix: take the line out of section 7 and say it enters through the loop, or choose another regression.",
    "origin": "reviewer",
    "evidence": "21-instance-text-2027.md, section 7, line 323; section 10, lines 366-370",
    "round": 1
  },
  {
    "target_artifact": "instance-text-2027",
    "severity": "medium",
    "text": "The justification of t-source-density does not support the limit: it says books usually carry one note every 200 to 300 words in factual passages, that is, 3.3 to 5 per thousand, and calls 4 per thousand 'the floor, not the target'. Four is inside the typical range, above its lower end, and not below it. Fix: lower the floor to something below the cited range (for example, 3 per thousand) or justify why the floor sits in the middle of it.",
    "origin": "reviewer",
    "evidence": "21-instance-text-2027.md, section 5, line 273",
    "round": 1
  },
  {
    "target_artifact": "recipe",
    "severity": "medium",
    "text": "The bible and the recipe itself define the orchestrator as a step that passes paths, runs the engine and imports notes, and say that it 'does not decide anything that a card assigns to a role'. Even so, the recipe makes it the author of the artifact list (step 4, with the brief's owner), of the role cards with decides and does not decide (step 5) and of the case method document (step 14). Those artifacts are left without an owner role, which contradicts the 'Done when' of step 4 (every artifact with exactly one owner) and the practice of this production, in which the writer owns them. Fix: name an owner role (writer, process architect) for those steps and leave the orchestrator only the execution.",
    "origin": "reviewer",
    "evidence": "01-bible.md, term 'orchestrator'; 10-generic-recipe.md, lines 74-76, 188, 213, 451; 02-artifacts.md, owners of artifacts and cards",
    "round": 1
  },
  {
    "target_artifact": "artifacts",
    "severity": "medium",
    "text": "Undeclared reflexivity gap. Step 8 of the recipe says the rubric is written by the 'owner, with whoever is going to review; never whoever is going to produce alone'. In this production, gates-and-rubric, which contains the rubric, is owned by the writer, the same role that wrote everything the rubric measures, and no document records the participation of the owner or of the reviewer or declares the deviation. Fix: declare the deviation in the brief, as was done with the owner decisions without a file of their own, or record who approved the rubric before the freeze.",
    "origin": "reviewer",
    "evidence": "10-generic-recipe.md, step 8, line 291; 02-artifacts.md, row of gates-and-rubric (owner: writer); 00-brief.md, 'Owner decisions' table (without the rubric)",
    "round": 1
  },
  {
    "target_artifact": "instance-text-2027",
    "severity": "medium",
    "text": "'It is the rule of the reference case (\"the fact never comes from the writer\")' attributes to the case a sentence from the principle (golden rule 2). The reference-case method document does not have the word 'writer' and does not carry this rule with this text. The substance checks out: every claim has an identifier and a mark from the corpus, and the fact verifier answers for it. But the quotation marked as a rule of the reference case is not in the source. Fix: attribute the sentence to the principle, or paraphrase what the case says, with [case] and the section.",
    "origin": "reviewer",
    "evidence": "21-instance-text-2027.md, line 109; 01-principle.md of the corpus, section 5, rule 2; reference-case method document, sections 1.7 and 2.1 (search for 'writer' with no occurrence)",
    "round": 1
  },
  {
    "target_artifact": "corpus",
    "severity": "medium",
    "text": "The principle diverges from the reference-case method document on two numbers. (1) Section 4, row 'Instrument with a root-cause fix': 'Automatic reviewer with 13 notes, 10 of them false'; the case says 12 notes, 10 false (step 15 and section 5.3), and the principle's own '2 notes, both real' only closes with 12. (2) Section 2, reason 1: '3 blocking notes that the team that produced it had looked at and approved'; the case says 'Two of the blocking notes were pending items that had been noted and let go' (section 1.1).",
    "origin": "reviewer",
    "evidence": "01-principle.md of the corpus, section 2 (reason 1) and table of section 4; reference-case method document, section 1.1, step 15 and table of section 5.3",
    "round": 1
  },
  {
    "target_artifact": "corpus",
    "severity": "medium",
    "text": "The principle states about the case things that the reference-case method document does not record: a role that compensated for a defect of the engine by 'raising the requested value' (section 4, Roles with a card); '54 high notes at once' attributed to an outdated setup and cited by the bible (section 4, Validator; in the case, '54' only appears as a count of sampled items); '\"in three years\" on a card' (section 4, Bible; the case only records the error of 'four years'); 'an item was left with stale text' (section 4, Graph); 'unknown field in a layer (assembly halted)' (section 4, Contracts); 'the same model \"doing everything\" mixed several kinds of decision' (section 2); 'by six rules' (section 4). They may be in other files of the reference case, which the reviewer did not open; in the reference-case method document, they are not. The first of these sentences has already made its way into the recipe.",
    "origin": "reviewer",
    "evidence": "01-principle.md of the corpus, sections 2 and 4; searches in the reference-case method document for 'compens', 'setup', 'three years', 'stale', 'unknown', 'mixed' and 'six rules' with no occurrence in the claimed sense",
    "round": 1
  },
  {
    "target_artifact": "recipe",
    "severity": "low",
    "text": "'In the reference case, three files with the same name, one of an old version, confused the review' states as fact what the case records as an inference: the same-named files were the process-level high finding of the v2 review, and the automatic reviewer 'probably read the same-named file of v1' according to the v2 review ('its inference'). Fix: say that the same-named files were a process finding and that reading the wrong file is likely.",
    "origin": "reviewer",
    "evidence": "10-generic-recipe.md, step 10, lines 366-368; reference-case method document, step 15 and table of section 5.3 ('Automatic reviewer: wrong input')",
    "round": 1
  },
  {
    "target_artifact": "bible",
    "severity": "low",
    "text": "The bible defines artifact with a 'single owner', but the bible artifact has two owners: the writer and the verifier, owner of the 'Case numbers' section. The case shows the way out (section 1.2): a section of the bible can be an artifact of its own, with a hash of the section only. Fix: declare the 'Case numbers' section as an artifact of its own owned by the verifier in 02-artifacts.md, or write the exception into the definition.",
    "origin": "reviewer",
    "evidence": "01-bible.md, term 'artifact' and sections table (line 14); 02-artifacts.md, row of bible (owner: writer); 03-roles/writer.md, 'Outputs'",
    "round": 1
  },
  {
    "target_artifact": "cards",
    "severity": "low",
    "text": "The outputs of the cards do not close with the artifact table: the verifier lists only validator.py, but instrument-validator includes sensitivity.py; the validator lists only report.md, but validation-report includes sensitivity.md; and no card says who runs sensitivity.py or with what command.",
    "origin": "reviewer",
    "evidence": "03-roles/verifier.md, 'Outputs'; 03-roles/validator.md, 'Outputs' and 'Base prompt'; 02-artifacts.md, rows of instrument-validator and validation-report",
    "round": 1
  },
  {
    "target_artifact": "bible",
    "severity": "low",
    "text": "The 'Method components' list shortens the principle's names: 'instrument' instead of 'instrument with a root-cause fix', 'gate' instead of 'gates with magnitude', 'note' instead of 'routed notes', 'independent review' without 'with a fixed rubric'. With that, p-components passes only because the word appears. The three instances have the practices (the root-cause fix examples are in sections 10), so today there is no consequence; the gate, however, does not prove them.",
    "origin": "reviewer",
    "evidence": "01-bible.md, 'Method components'; 01-principle.md of the corpus, table of section 4; validator.py, component_pattern",
    "round": 1
  },
  {
    "target_artifact": "instance-car",
    "severity": "low",
    "text": "The graph drawing does not match the table: there is an arrow from budgets to safety-analysis, but the table says safety-analysis depends only on requirements and architecture; and edges that the table declares are missing (owner-decisions and bible to requirements, regulatory-matrix to validation-plan and homologation-dossier, vehicle-software to simulations, the inputs of validation-report).",
    "origin": "reviewer",
    "evidence": "20-instance-car.md, section 3, table (lines 79-100) and drawing (lines 104-126)",
    "round": 1
  },
  {
    "target_artifact": "instance-car",
    "severity": "low",
    "text": "The budgets artifact has as its gate 'sum of allocated ≤ target', a limit with a magnitude but without a row in the gates table and therefore without a justification or origin label. Step 7 of the recipe requires a justification for every limit, and p-limit does not see a gate declared only in the artifact table. Fix: give the gate a name and a row in section 5.",
    "origin": "reviewer",
    "evidence": "20-instance-car.md, line 85; 10-generic-recipe.md, step 7, 'Done when'",
    "round": 1
  },
  {
    "target_artifact": "instance-text-2027",
    "severity": "low",
    "text": "The gates of theme-map ('each sub-thesis covered by a domain') and of domain-dossier ('every candidate with source and excerpt') are only in the artifact table, without a name, without a row in the gates table and without a justification.",
    "origin": "reviewer",
    "evidence": "21-instance-text-2027.md, lines 73-74; 10-generic-recipe.md, step 7, 'Done when'",
    "round": 1
  },
  {
    "target_artifact": "instance-hpc",
    "severity": "low",
    "text": "Three artifacts have a 'gate' without a magnitude and without a row in the gates table: oracle ('set covers the bible's classes', which is measurable and deserves a named gate), specification ('reviewed by the owner') and implementation ('code review'). The last two are judgment; step 7 says to mark them 'contract + agent', with the agent named.",
    "origin": "reviewer",
    "evidence": "22-instance-hpc.md, lines 77, 79 and 83; 10-generic-recipe.md, step 7, 'Done when'",
    "round": 1
  },
  {
    "target_artifact": "instance-hpc",
    "severity": "low",
    "text": "The justification of h-noise is truncated: 'with larger noise, a speedup of 1.5 with a tight confidence interval becomes indistinguishable'. With a coefficient of variation a little above 3%, a speedup of 1.5 is still visible. What is at risk is the lower limit of the interval (≥ 1.3) and the detection of slower sizes near the noise floor (h-sweep). Fix: say that.",
    "origin": "reviewer",
    "evidence": "22-instance-hpc.md, section 5, line 256",
    "round": 1
  },
  {
    "target_artifact": "instance-hpc",
    "severity": "low",
    "text": "The instance's brief lacks the 'Provisional stopping criterion' row, which step 1 of the recipe requires and which the car and text instances have. The criterion exists in section 11, but the brief does not point to it.",
    "origin": "reviewer",
    "evidence": "22-instance-hpc.md, section 1, lines 37-56; 10-generic-recipe.md, step 1, 'Creates'; 20-instance-car.md, line 58",
    "round": 1
  },
  {
    "target_artifact": "instrument-validator",
    "severity": "low",
    "text": "The self-test docstring says 'One positive and one negative case per rule', but several rules have no case at all: p-size, p-anchor, p-sections, p-table, p-card, p-limit, p-recipe, the rubric hash and the note contract. What the verifier requires, one test per root-cause-fixed rule, is fulfilled; the docstring promises more than it delivers.",
    "origin": "reviewer",
    "evidence": "80-validator/validator.py, self_test (docstring and asserts)",
    "round": 1
  }
]
```
