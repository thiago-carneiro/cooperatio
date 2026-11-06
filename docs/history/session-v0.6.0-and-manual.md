# Session record: from v0.4.0 to v0.6.0, and the manual

A curated record of one working session of the owner with an orchestrator
agent and the agents it delegated to, on this material. It is evidence
about the material and about how it was maintained, not about the method:
every round it describes is a maintenance round in the sense of the brief
of the reflexive application. It follows the form rules of the canon
(`02-reflexive-application/01-canon.md`): executors are named by family
letter and role, never by model identifier; no machine name, user name,
absolute path or authoring date appears; a claim that the method works
carries its label. The raw transcript of the session is not in the
material, by design: it holds what these rules forbid, and the extracts
below are what the material can carry.

## Starting point and end point

- Start: the material at version 0.4.0 in the working tree, the remote at
  version 0.5.0 by the end of the session's first half (commit `6321d1c`,
  "Add the cooperatio material at version 0.5.0"), continuing a session
  of critical review of the material by a panel.
- End: `main` at the merge commit `ee257c3`, holding `9ab05e5` (the
  material at version 0.6.0) and `a794640` (the manual under
  `docs/manual/`), pushed to the remote.

## The sequence of requests and what each one produced

| Request of the owner | What was done | Where it is recorded |
| --- | --- | --- |
| continue the critical-panel analysis | closure of v0.3.1; the epistemological round v0.4.0 (perturbations covering every gate, the rules of evidence, the experiment record under a gate) | `CHANGELOG.md` 0.4.0; the lessons entry of that round |
| "take the decisions you think best" | v0.4.1: closures of what v0.4.0 left open, plus experiment E3 (the reviewer without the rubric) | `CHANGELOG.md` 0.4.1; `60-experiments.md`, E3 |
| remove model identifiers from the whole corpus, with minimal impact | a sweep by hand, recorded outside the material; executors renamed by family letter; the map from letter to family kept by the owner | `01-canon.md`, form rule 4; `06-gate-semantics.md`, "The commitment to the map of families" |
| "fix what was left" | v0.4.2: no bytecode cache, the anonymity gate on the round record and the principle, the other residues | `CHANGELOG.md` 0.4.2 |
| "make a complete critical re-evaluation" | a nine-seat critical panel on v0.4.2, of several disciplines and kinds of access | the panel's findings, outside the material; its findings as `panel:0.4.2:*` lines of `state/notes-status.jsonl` |
| "fix, push" | v0.5.0: the corrections of that panel the owner does not decide, the cell of instance 004 moved into the material; pushed | `CHANGELOG.md` 0.5.0; commit `6321d1c` |
| "a complete, very rigorous critical evaluation by a multidisciplinary team of your own" | an eight-seat panel on v0.5.0, every seat of family B by the owner's choice after the family first chosen became unavailable; 7 critical, 16 important and 22 suggested findings; the panel drove the instrument to exit 0 with a repointed file, a malformed mark, a number in a code span, a deleted sensitivity report accepted by name, and a domain regression the validator never read | `CHANGELOG.md` 0.6.0, opening; `panel:0.5.0:*` lines of the state ledger |
| "write your recommendations on the open questions; execute every correction and adjustment" | eight recommendations (below), then the v0.6.0 round: a specification, a coder in three passes (the specification, a second pass, a rework after the independent review) and a closing pass, with an independent reviewer of family B in a separate session whose verdicts went NEEDS_WORK, NEEDS_WORK after rework, READY after closing | `CHANGELOG.md` 0.6.0; the round line of 0.6.0 in `state/round-record.jsonl`; `state/owner-decisions.jsonl` |
| "review the architecture, capabilities and purpose of the product and generate an extensive manual" | `docs/manual/`: 22 chapters and 7 appendices, 14 diagrams written as Mermaid with a Graphviz twin each, a Markdown edition and a PDF edition built with pandoc and LuaLaTeX | `docs/manual/README.md`; appendix G of the manual |
| "commit merge push" | the branch `release/0.6.0` with two commits, merged into `main` with a merge commit, pushed; `.gitattributes` gained `*.pdf binary` so the LF rule does not rewrite the PDFs | commits `9ab05e5`, `a794640`, `ee257c3` |
| "save the history of this session in the repository" | this record, curated; the raw transcript stays outside the material | this file |

## The eight recommendations on the open questions

Written by the orchestrator at the owner's request, before the v0.6.0
round, and executed in it except where only the owner can act:

1. **Scope of the validator.** Declare it documentary and open a minimal
   interface for the gates of a target's domain: the cell's own code
   writes results, the validator reads them and checks the sha256 of
   their inputs (`d-*` gates, `domain-result.schema.json`). Done.
2. **Independence of the reviewer.** A recommendation with a declared
   cost, not a rule; the demonstrated part is the frozen rubric with a
   mechanical verdict rule (`[experiment:E3]`). Done; promoting it to a
   rule stays an owner decision, with the thresholds of the principle's
   table.
3. **Maintenance rounds.** Declared as outside the method, with a minimal
   record: `kind`, the reviewer's relation, the hash chain. Done; opening
   the next production of the material as a production stays with the
   owner.
4. **Instance 000.** "One auditable instance, one held by the owner", plus
   a sha256 commitment per cited section in the canon. Done; publishing
   an extract stays with the owner.
5. **Integrity.** The README says what a clone verifies and what rests on
   the owner; the three ledgers are chained; a signed tag per version is
   recommended. Done except the tag, which is the owner's.
6. **The next budget.** Freeze the instrument; spend on measuring value
   (experiment E4, designed) and portability (E5, designed). Designs
   written; the budget and the third party are the owner's.
7. **Cell 004.** Not migrated; kept as the record of an execution, with
   `ERRATA.md` beside its guide and its own validator refusing to run
   without `--historical`. Done; replacing it as the example stays with
   the owner.
8. **Exit from the hypothesis.** A table, written before the data, of what
   would promote or withdraw each claim, with thresholds. Done; accepting
   the thresholds stays with the owner.

## What the v0.6.0 round changed, in short

- every critical and important finding of the panel on v0.5.0 closed, and
  the suggestions done or declared; three high, nine medium and thirteen
  low findings of the independent review closed in the rework and the
  closing pass;
- the validator split into one family of gates per kind over a shared
  core (byte-identical report before and after); 65 perturbations (35
  before), 280 tests (171 before), 185 self-test checks;
- `--allow-pending` closed to four names; a missing sensitivity report
  blocking; the sensitivity test copying the whole material, with
  specificity (noisy perturbations) and coverage by pair (50 of 182);
- a synthetic prior for a clone, and a `case attestation` per document
  that the owner's run recomputes, after the review showed a forged
  `case sha256` line passing;
- the frozen records of round 1 pinned in the canon; the three ledgers
  chained; the owner's decisions a ledger; golden rule 4 mechanical
  (`escaped` closes with a gate or a reason); non-negotiables with ids and
  notes with `affects`;
- the role that runs the validator renamed `runner`; instance 004 kept as
  a record with errata; `.gitattributes` and one hash policy for every
  object.

## Verification at the close of v0.6.0

| Check | Result |
| --- | --- |
| the full command of the runbook (owner's run, both prior documents) | exit 0, 0 notes, report byte-identical across runs |
| the same without `--allow-pending` | exit 4 |
| the clone run (document of 004 only) | exit 0 |
| `--allow-pending p-sensitivity` or `p-anonymity-language` | exit 2 |
| the owner's run against a forged attestation | exit 1 |
| the sensitivity report | 65 of 65 caught, 0 noisy, 50 of 182 pairs, byte-identical across runs |
| pytest and the self-test | 280 passed; 185 checks |
| the frozen records, the old ledger lines, the 004 method document and guide | untouched |
| the inventory | 79 files, no bytecode cache; the sweep for model, machine and user identifiers found none |

The residual risks declared in the material: in a clone without the
owner's document a forged `case sha256` line passes; the eight distinct
words of a `no_gate` reason measure form, not content; the attestation
does not prove the perturbations ran; the anchor outside the tree (a
signed tag) is not yet made.

## The manual

- An architecture review first: the principle, the recipe, the canon, the
  gates and their declared semantics, the role cards, the validator, the
  sensitivity test, the perturbation set, the scaffold, the contracts, the
  ledgers, the experiments, the instances and the skill.
- Then the text (about 28,900 words; 93 pages in the PDF edition) and the
  14 diagrams, each written twice: Mermaid in the Markdown, Graphviz for
  the PDF, swapped by a pandoc Lua filter that reads `%% name:` and
  `%% caption:` comments.
- Executive verification: the quick-start chapter's path from a freshly
  scaffolded cell (24 files, exit 1 with three blocking and eight high
  notes) to a green run was executed, not described: six minimal edits
  took it to exit 0, with the sensitivity report at "6 of 6 gates
  covered, 6 of 22 pairs (27 %)". The material's own validator run was
  repeated after the manual folder was added and gave the same report.
- PDF verification: the margin check found no overflow after two fixes (a
  break opportunity in inline code, two wrapped code lines); figures carry
  captions and are capped at 86 % of the text height; pages were inspected
  as images. Two dense diagrams (the artifact graph and the integrity
  structure) are small in the PDF and better read in the Markdown or SVG.

## Executors, by family and role

| Role | Family and relation |
| --- | --- |
| orchestrator | family B |
| coder of v0.6.0 (three passes), coder of the earlier rounds | family B |
| independent reviewer of v0.6.0 | family B, same family as the producer, separate session |
| the panel on v0.4.2 | nine seats of several families, by discipline and access |
| the panel on v0.5.0 | eight seats of family B, by the owner's choice; the diversity was of discipline and access |
| author of the manual | the orchestrator, family B |
| the owner | a person: every decision the brief reserves, the choice of executors, the go-ahead for each push |

The map from a family letter to a family, and the salt of the commitment
the round record carries, stay with the owner outside the material.

## What stays outside the material, on purpose

- the raw transcript of the session, with the subagents' transcripts;
- the orchestrator's working records of each round (specification,
  coder's notes, review with its addenda, the panels' seats and findings,
  the recommendations in full), kept in the owner's workspace;
- the family map and its salt;
- the method document of instance 000 and the list of forbidden
  identifiers;
- the scratch copies the sensitivity test and the manual's build left.

## Open for the owner

The eight lines of `state/owner-decisions.jsonl`, all `open`: sign the tag
of the version; publish an extract of the first prior or not; accept or
adjust the thresholds; approve the budget and run E4; find the third party
for E5; promote independence across families to a rule; open the next
production of the material as a production; replace the cell of 004 as the
example.
