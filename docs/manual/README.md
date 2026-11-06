# Cooperatio manual

An extensive manual of the method and of its instrument, for method
version 0.6.0: purpose and scope, the concepts, the architecture of the
material and of the validator, the gate catalogue, the sensitivity test,
the ledgers and the integrity structure, the instances, and the how-to
chapters (quick start, setting up a cell, running the instrument, running
a round, domain gates, maintaining the material), with appendices
(glossary, contracts, command-line reference, false greens, file index,
open owner decisions).

- Read it as Markdown: [`manual.md`](manual.md) (the Mermaid diagrams render
  in viewers that support them).
- Read it as PDF: `manual.pdf` (built from the same source, with the
  Graphviz twins of the diagrams).

The source is under `src/` (one file per part), the diagrams under
`diagrams/` (one `.dot` per diagram, rendered to `.svg` and `.pdf`), and
the build is `make` (pandoc, Graphviz, LuaLaTeX). Appendix G of the manual
describes the build.
