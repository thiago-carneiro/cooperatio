---
title: "Cooperatio Manual"
subtitle: "Architecture, capabilities and purpose of the method and of its instrument — method version 0.7.2"
lang: en-US
---

# Preface {-}

This manual describes **cooperatio**, a method for organizing a team of
people, language-model agents and code around a complex target, and the
material that distributes it: the principle, the reflexive application (the
method applied to itself), the validator and its sensitivity test, the
agent skill that scaffolds a production cell, and the registry of executed
instances. It is written for three readers:

- **the adopter**, a person or an orchestrator agent who wants to set up a
  production cell for a target of their own and run it to a verdict;
- **the maintainer**, who edits the material or the instrument and has to
  keep its provenance, ledgers and pins coherent;
- **the reviewer or auditor**, who wants to know what the material claims,
  what evidence stands behind each claim, and what a clone of the material
  can and cannot verify.

It is a manual, not a replacement for the material: every rule stated here
is stated with more precision in the file it comes from, and the manual
names that file. Where the manual and the material disagree, the material
wins; please report the disagreement as a note.

**Version.** The manual describes method version 0.7.2, as recorded in
`VERSION`. The counts it quotes (gates, perturbations, tests, files) were
measured on that version unless a sentence names another one; later
versions change them, and the "Migration note" of each entry in
`CHANGELOG.md` says what a cell has to change.

**What changed since the first edition (0.6.0).** Four things a reader of
the earlier manual needs to know:

- **One executed instance.** Version 0.7.0 removed from the living material
  the prior the owner held and did not distribute, and its registry entry.
  The evidence now rests on one execution, `004-adoption-guide`:
  documentary, by the owner, auditable from the material. A rule whose only
  support was the removed prior keeps its text with `[hypothesis]`, or says
  that no recorded execution supports it.
- **The value test ran, and withdrew a claim.** Experiment E4 measured the
  review apparatus against a careful checklist review on seeded defects,
  under thresholds the owner fixed before the runs. The claim that the
  apparatus adds to a careful review without it is **withdrawn**
  `[against:E4]` (chapter 10).
- **A benchmark.** The seeded material of E4 and its answer keys are kept in
  `benchmark/`, so that a later run compares with it.
- **An installer.** `skills/cooperatio-teamwork/scripts/install.py` links
  the skill into every agent harness it finds on the machine (chapter 17).

**Conventions.** File names and identifiers appear in `monospace`; paths
are relative to the root of the material, or to the folder of the
reflexive application (`02-reflexive-application/`) where the context says
so. A term in **bold** at its first use is a term of the canon
(`02-reflexive-application/01-canon.md`) and is defined in the glossary
(appendix A). Claims the material itself labels as hypotheses are quoted
with their label, `[hypothesis]`, because the material's own rule applies
to the manual: a claim that the method works carries its evidence or its
label.

**Diagrams.** Each diagram is written twice: as a Mermaid block in the
Markdown source, which Markdown viewers that support Mermaid render in
place, and as a Graphviz file under `diagrams/`, rendered to SVG and PDF.
The PDF edition uses the Graphviz renders; the two are drawn from the same
description and differ only in layout.

**Status of the method, in the material's own words.** A working
hypothesis, with a documentary validator; the gates of a target's domain
enter as results the cell's own code produces and the validator checks;
one executed instance, documentary, by the owner, auditable from the
material. The
manual repeats this on purpose wherever a reader could take a described
capability for a measured one.
