# Lessons of the round

What the single round of this work taught, about the documents and about the
method itself. The terms follow the [canon](01-canon.md); the notes are in
`90-review/notes.json` and the replies in `90-review/replies.md`.

## What happened, in numbers

| Moment | Magnitude |
| --- | --- |
| Gate rounds before the review | 3 documents came back once each (cards with an unclosed block; car instance without "artifact graph"; HPC instance with `iteration`); none reached a second return |
| Instrument fixes before the review | 3 (notes addressed to the document and not to the artifact; new note-target rule, with two false positives fixed at the root; `p-case` that read line by line) |
| Sensitivity test before the review | 11 of 12 on the first execution; 12 of 12 after the fix |
| Independent review | `rejected`: 1 blocking, 2 high, 12 medium, 11 low; D1 scored 2 |
| After the review | 1 new gate (`p-case-mark`), which rejected the revised version in 10 units; blocking and high notes fixed; sensitivity 13 of 13; validator with no high note |
| Open notes | 22 (12 medium, 10 low), 2 of them against the corpus |

## What the round taught about the documents

1. **The gate measured what was easy, not the property.** The non-negotiable
   was "nothing about the case that is not in the case method document"; the
   gate `p-case` checked only numbers. A qualitative claim about the case,
   with no number, passed everything and was the blocking note. It is the
   rule "measure what the system delivered, not what was requested" in
   documentary form: the gate measured an indicator (the number) instead of
   the thing (the claim).
2. **The error came from the corpus.** The blocking sentence was not invented
   by the writer: it was in the principle, which is the generalization of the
   case, and the writer treated it as a fact of the case. The reviewer found
   two more numeric divergences and seven claims of the principle about the
   case that the case method document does not record. When a method is
   generalized from a case, the generalization becomes corpus, and its errors
   enter the following documents with the authority of the original.
3. **Loop examples contradicted the initial state.** In the instances, the
   loop "gives birth" to gates that the gate table already declared. The
   writer first wrote the ideal state and then invented the story of how it
   would be reached. It stayed as an open note.

## What reflexivity showed about the method

1. **The independent review did what the principle promises.** The gates and
   the validator passed with no note; the review rejected. The
   pattern is the case's: the first review finds what no gate measured, and
   the finding becomes a gate.
2. **"A regression becomes a gate before the fix" works and pays off more
   than the note.** The new gate pointed to 10 units, not only the blocking
   one; two of them had imprecisions that the reviewer also saw, and the other
   seven were checked and kept the section of the case next to them.
3. **The principle lacks a component: proving that the gate rejects.** The
   sensitivity test (injecting a known defect and watching the gate reject)
   found a real defect in the instrument before any review. The principle
   speaks of a signal gate, but does not require the known perturbation as a
   condition for a gate to count. Proposal for the next version of the
   principle: include it in the component "gates with magnitude".
4. **With a single agent, the separation of roles is weak where it matters.**
   Here the same agent was writer, verifier and validator, and wrote
   the rubric. The cards separate responsibilities, but not blind spots: the
   gates written by the writer had the same blind spot as the text (numbers
   only). The only truly independent role was the reviewer, and it was the one
   that found the blocking note. A rubric written by the producer contradicts
   step 8 of the recipe itself; the deviation was not declared before the
   review and stayed as an open note.
5. **The workaround is the third exit that the principle does not name.**
   Faced with the false positive of `iteration`, there was the root-cause fix
   (accepted variant in the canon), the loosening (forbidden) and the
   workaround (changing the word). The workaround was chosen because the new
   term is more precise; the instrument defect stayed, recorded as an open
   note. It is worth naming the workaround in the principle, so that it is a
   declared decision and not a silent escape.
6. **Stopping after one round delivers one revised version and one that was
   not.** The verdict `rejected` holds for the version the reviewer read. The
   delivered version has the blocking and high notes fixed, checked only by
   gates (validator with no high note, sensitivity 13 of 13). That
   is the honest state of the delivery, not "acceptable".
7. **The cost was real.** Brief, canon, cards, gates, a validator of
   about eight hundred lines and a sensitivity test, for three instances and
   one recipe. The principle already warns that the method pays off when being
   wrong is expensive; here, being wrong about the case was non-negotiable,
   and the method found the error.

## What became a gate or a rule in this round

| Origin | Became |
| --- | --- |
| a note that a card addressed to a nonexistent artifact, found by reading | note-target rule in `p-references` |
| a case number in a sentence broken across two lines, found by the sensitivity test | `p-case` by text unit and comparison by whole number |
| a qualitative claim about the case, found by the review | gate `p-case-mark` and a permanent perturbation in the sensitivity test |
| "the recipe's rule" cited and nonexistent, found by the review | "Verdict rule" template in the recipe |

## The v0.2 round: correcting the corpus and settling the vocabulary

Appended in the v0.2 round of the method (version 0.2.0; see
`../CHANGELOG.md`). The review of round 1 had found, in `../01-principle.md`,
seven claims about the prior instance without support in its method document
and two numbers that did not match it (the audit's list, in
`90-review/auditor-report.md`). In this round each one was removed or aligned
with the recorded facts of the canon; the vocabulary was settled (production
cell, canon, position key, the verdicts `accepted` and `accepted with
conditions`; the old names are recorded as cited history); the prior instance
was registered (`../instances/registry.json`,
pinned by sha256) and the old quarantine mark became the `[prior:<id>]` mark.
The entries above keep the gate and artifact names of the round they describe;
the gates were renamed in this same round, and the frozen ledgers of
`90-review/` were not edited — the alias that maps the old note target to
the renamed artifact is part of the validator.

## The v0.2.3 round: a path that escaped the central resolution

Appended in the v0.2.3 round (see `../CHANGELOG.md`). The first real
execution of the v0.2 method (instance `004-adoption-guide`) found a defect
no corpus run could see: the validator's sensitivity gate read its report
from a path derived from the validator's own folder, not from the layout —
correct in the corpus by coincidence, pending in every scaffolded cell. The
replicable rule: a path that any gate reads or writes is a layout key, from
the day it is introduced; a directory convention that holds for the corpus
alone is an assumption waiting for the first cell to break it. New paths
join `DEFAULT_LAYOUT` (or the cell's `layout.json`) and nothing else; a
missing file is a pending that names the path and the key, never a silent
skip.

## The v0.3.0 round: a control that is not itself measured is decorative

Appended in the v0.3.0 round (see `../CHANGELOG.md`). The critical panel that
reviewed v0.2.3 found four criticals of one family: the instrument trusted
signals it never re-verified — a missing document silently unmeasured
(probe A), a rubric pin re-recordable by the freeze command that created it
(probe B), a sensitivity report accepted on the presence of one line
(probe D), and a freshly scaffolded cell green with zero documents measured
(probe E2). The replicable rule: every control the instrument relies on is
itself a measurement — a declared path has to be checked against the disk, a
frozen hash has to refuse its own re-recording, a report has to prove which
instrument produced it, and a run that measures nothing has to fail loudly.
A check that passes in the absence of its object is decoration, and the
report reads exactly like evidence.

## The v0.4.0 round: evidence about the method is subject to the method

Appended in the v0.4.0 round (see `../CHANGELOG.md`). The critical panel
that reviewed v0.2.3 found that the method exempted itself from its own
doctrine of evidence: a statement about a prior needed a mark and a
checkable source, a statement that the method works needed nothing. The
replicable rule: a claim about the method is a claim like any other — it
carries the label of where its evidence is registered (a prior, an
experiment, these lessons) or says that it is a hypothesis, and a gate
(`p-efficacy-mark`) reads the label. Where no evidence exists, the honest
move is to design the experiment that would produce it (E2, the arm without
the method) and to say that the claim waits for it, not to soften the
wording until no gate can read it.

Two instrument lessons of the same family closed in the round:

- **A number has one reading per document.** Read both ways, the English
  "1.2" matched a pt-BR "1.200" (one thousand two hundred): the two-way
  reading that made "0.546" equal "0,546" also turned a wrong claim green.
  The fix is a declared format per prior (`number_format` in the registry),
  not a smarter guess.
- **A control refuses what it does not understand.** A misspelled layout key
  (`sensitivty`) left the default in force, and the gate measured the wrong
  file in silence; an unknown key is now exit 2. A link counted by name
  passed while leading nowhere, until the gate checked that it resolves.

What experiment E1 showed about the reviewer (the record is in
`60-experiments.md`): given a known perturbation, the review did what the
rubric says — the producer's own model in another session and a model of
another family named both injected defects at the predicted severity and
accepted the clean product. What it did not show is as instructive: no arm
without the method, one run per cell, no difference between executors, and
nothing against a second session of the producer's model (it caught 2 of 2,
once). And two things no one had predicted:

- **The contract of a role stops where its executor's generation ends.**
  One report stopped at an output limit the dispatch had not declared (the
  budget it asked for was not applied) and still carried a verdict. A
  verdict a reader cannot verify against the full format is not a verdict;
  the dispatch now records the effective limit and the reason the
  generation ended, and an ending for length, or an incomplete report, is a
  tool failure.
- **The rule is stable; the scores and the findings are not.** The same
  executor, in the same condition, gave five findings in each of two runs,
  almost all different, and scores that moved, so the verdict changed; the
  mechanical rule was applied right both times. A verdict is exactly as
  stable as the dimension scores that decide it, and a single run cannot
  see how stable that is.

And one the experiment did not measure, found by the review of this round
when it checked a remark of the reviewers: the cell's prior gate passed the
invented number, because a number without a recorded fact was checked for
presence anywhere in the prior's document, and the invented one occurs
there once, by chance. The canon already said such a number does not enter
the documents; the gate did not enforce it. It does now.

## The v0.4.1 round: a verdict needs its rubric, and a family needs a check

Appended in the v0.4.1 round (see `../CHANGELOG.md`).

- **The rubric turns detection into a verdict.** Experiment E3 removed the
  review apparatus (the rubric and the reviewer card, together) from the
  review of E1 and kept the output contract [experiment:E3]. Both executors
  still named both injected defects, and neither rejected the perturbed
  product: without the severity table the invented fact about a prior was a
  correctable error, classed high, and without the mechanical rule two high
  findings did not bring the verdict down. The four verdicts, control and
  perturbed, came out the same. For two defects checkable against a source,
  one run per cell: what a rubric buys is not the reviewer's eye but a fixed
  price for each class of defect and a rule that turns the price into a
  verdict; a review without it can find everything and still not let what
  it found decide the verdict.
- **An alias is not a family.** The review of the second executed instance
  was recorded as coming from another family because its executor had
  another name; the name was an alias for the producer's own model, through
  another route and at another effort. It came out only when the table that
  maps aliases to models was read, rounds later. A claim of independence is
  checked on what a name maps to, never on the name. The rule that came out
  of it: the round record names each executor by family (a letter stable in
  the material) and effort, never by product identifier — an identifier
  changes, leaks the provider and, as here, hides whether two names are one
  model; the map from letter to identifier stays with the owner. The price
  is declared: the letters are as good as the owner-held map, and the
  material alone cannot detect a mislabeled letter. Read with the letters,
  the round record says what the identifiers hid: no recorded production
  round, nor the review of the second executed instance, had a reviewer of
  another family with a frozen rubric; the one exception without it is the
  reading review of family A in v0.4.1 (no frozen rubric, no verdict rule,
  no execution). The only reviews across families in the reviewer role,
  with a frozen rubric, are the runs of executor Y in E1 [experiment:E1]
  (E3 removed the rubric [experiment:E3]); the critical panels of v0.1.0,
  v0.2.0 and v0.2.3 had seats of several families, but no frozen rubric, no
  verdict rule and no line in the round record.

## The v0.4.2 round: a process flag does not cross into a child process

Appended in the v0.4.2 round (see `../CHANGELOG.md`). The instruction "run it
with `-B`" left bytecode caches beside the scripts anyway: the validator
starts child runs (the determinism check, and the sensitivity test starts
many), and a child inherits neither the caller's `-B` nor the switch it sets.
The first fix was written as instructions (an environment variable in the
runbook), which held only as long as every caller read them. The replicable
rule: a property the material has to keep is set where the code runs — the
module switches the cache off before it imports anything local, and the
argument list of each child carries the flag — and an instruction is only
the fallback for what the code cannot reach. Here that fallback is the test
suite: pytest imports the files before any of their code runs, so its
command keeps `-B`.

## The v0.5.0 round: exit 0 is not green

Appended in the v0.5.0 round (see `../CHANGELOG.md`). The critical panel
that reviewed v0.4.2 drove the instrument to exit 0 with the gate table
deleted, with an invented number under a mark written between backticks,
with scaffolded cards that still said "fill in" and with the lists of the
canon empty. Each of these is now a perturbation of the sensitivity test.
From this heading on, these lessons are under `p-efficacy-mark`; the
entries above are history, exempt by a line of the canon.

- **The control measured the easy part, again.** The first lesson of this
  record says the gate measured the number instead of the claim. Here the
  provenance of the sensitivity report pinned the validator's own sha, the
  easy input, and not the gate table and the canon, which decide what is
  measured; a mark gate read a code span that the number gate skipped; a
  card gate counted the names of the fields and not what they held. The
  replicable rule: a control is pinned to every input that defines what it
  measures, and two gates that read one object read it the same way.
- **Exit 0 is not green.** Exit 0 meant "no high note", whatever had not
  been measured: a pending row, an empty list read as 0 of 0, a placeholder
  read as a filled field. A run now exits 4 while a gate is pending that the
  caller did not accept by name, and an empty list or a placeholder is a
  pending or a fail, never a pass. A green that measured nothing reads
  exactly like evidence, which is why it has to look different.
- **The doctrine of evidence reached the founding claims through a closed
  list.** Five phrases of the principle claimed that the method works with
  no label (`observed in practice`, `the only way`, `err less`,
  `every rule below was born`, `none was`); they are triggers now, and
  their units carry a label. The gate is lexical: a paraphrase escapes it, and what a
  closed list cannot read is left to the independent review.

Two readings of the entries above are withdrawn here, not rewritten there.
The entry of v0.4.0 reads the one repetition of E1 as a change of verdict;
by the rule that same round adopted, the first run ended for length and is a
tool failure, so the stability of the verdict was not measured. The entry
of v0.4.1 says the rubric turned detection into a verdict; E3 removed the
whole review apparatus at once (rubric, card, gates file and the framing of
the dispatch), so the result belongs to the apparatus, and the share of the
severity table and the mechanical rule is a hypothesis [hypothesis]. Both
records are corrected in place in `60-experiments.md`.
