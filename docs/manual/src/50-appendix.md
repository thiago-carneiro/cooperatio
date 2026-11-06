
# Appendices {- .part}

# Appendix A — Glossary {-}
Condensed from the "Method terms" table of
`02-reflexive-application/01-canon.md`, which is the authoritative
definition of each term.

| Term | Definition |
| --- | --- |
| accepted variant | another spelling of a number or term that the canon admits in a declared place and for a declared reason |
| artifact | an intermediate or final output, typed, with a name, a single owner, paths, a schema, dependencies, gates and content identified by hash; an owner decision is also an artifact |
| artifact graph | the set of artifacts with the dependencies between them; it has to be acyclic |
| assembly engine | the code that composes the artifacts into the target, rejects ambiguity, rebuilds by hash, routes notes and names the outputs by version label |
| brief | the owner's document: what the target is, for whom, what is non-negotiable, what is an owner decision, the round budget |
| canon | the single source of numbers, names, terms to prefer and to avoid, accepted variants and rules, with an owner and a version per section |
| case method document | the document that records, at the end, the ideas, graph, step by step, pseudocode per role with its degree, the owner's pending items and the known false positives of an instance |
| code-conversion degree | how much of a role's work the code does: (a) converted, (b) partial under gate, (c) contract and gate only |
| contract | the schema an artifact has to validate before it is accepted |
| corpus | the facts, materials, standards and references available before the production; read, never edited |
| dispatch | one call of an executor with its inputs, recorded with what the endpoint returned (tokens, the reason the generation ended) |
| domain gate | a gate of the target's domain, named `d-<name>`, measured by the cell's own code and read by the validator from a result file |
| escalated | the state of an artifact that exceeded its maximum rounds: nothing that depends on it runs until the owner decides |
| executor | whoever or whatever exercises a role: a person, code, or a language model of a declared kind |
| experiment | a measurement about the method itself, registered with its question, protocol and predictions written before measuring; `executed`, `pending` or `designed` |
| false negative | a real defect that no instrument reported |
| false positive | a note the instrument emits when there is no defect; an instrument defect until proven otherwise |
| family | the provider and line of models an executor belongs to, named by a stable letter |
| first version | the v1: the whole target, end to end, made quickly to be reviewed, not to be good |
| gate | a measurable function over an artifact that returns pass or fail together with the measured magnitude; with a limit and a written justification |
| gate sensitivity test | injecting a known defect and checking that the gate rejects it, before trusting the gate |
| hand-off sheet | the artifact one role writes for another role to consume |
| independent review | a reading of the product by someone who did not produce it and has no access to the producer's reasoning, with the fixed rubric |
| instance registry | the record of the known instances, each with an id, a status, the path of its method document and the sha256 that pins it |
| instantiation table | the table of fourteen fixed rows that summarizes an instance |
| instrument | anything that measures: gate, validator, reviewer, simulation, benchmark |
| limit | the value that separates pass from fail, with the justification and the origin label next to it |
| magnitude | the measured value the gate returns, never just a sign |
| maintenance round | a round that corrects the material of the method itself after its stopping criterion, outside the reflexive production, with no verdict of the canon |
| maximum rounds | how many returns an artifact accepts before it is escalated to the owner |
| note | the only change request between roles: target artifact, severity, text, origin, evidence, round |
| open note | a note recorded and not resolved when the production stops |
| orchestrator | whoever executes the recipe: passes paths to the roles, runs the engine and imports notes; a step, not a role |
| owner | the person who commissions the target, approves the brief, makes the decisions no role can make and declares the stop |
| position key | the value that fixes where a part of the target lands during assembly; an ambiguous one is a contract error |
| prior instance | an instance of the method that ran before the current one and is registered in the registry |
| production cell | the organization assembled for one target: roles, artifacts, gates, canon, validator, review and assembly engine |
| regression | a defect that comes back or appears in a new version; if it escaped every gate, it gains a gate before it is fixed |
| retired gate | a gate removed deliberately, with its perturbation, because its object is gone or its rule moved into a contract |
| role | a narrow responsibility exercised by an agent, a person or code, which communicates only through artifacts and notes |
| role card | the sheet of a role with seven fixed fields |
| root-cause fix | handling a false positive by fixing the instrument's rule, with a test that reproduces the case, and redoing the previous round |
| round | one pass of the loop: produce, pass the gates, assemble, review, notes |
| rubric | the fixed grid of dimensions, anchors and verdict rule that every independent review uses in every round |
| rubric anchor | the written description of what a score of 1, 3 or 5 means in one rubric dimension |
| runner | the role that runs the validator and routes its notes; it decides nothing beyond the rules the validator executes |
| severity | `low`, `medium`, `high`, `blocking`; only the last two send the artifact back |
| signal gate | a gate that only tests existence or "greater than zero"; it has to gain a magnitude limit |
| source of truth | for each content type, the only source accepted as origin; the writer is never a source of fact |
| stale | the state of an artifact whose input changed since it passed its gates |
| stopping criterion | the condition, declared by the owner before the last round, under which the review becomes a list of open notes |
| target | the final product that the production cell hands over |
| teamwork | the files that set up a production cell for a target; the name of the skill that creates them |
| unit | what a gate reads as one statement: a paragraph, a list item, a table row or a heading |
| validator | a checking instrument, preferably in code, that reads all artifacts against the canon and emits notes on its own |
| verdict | `rejected`, `accepted with conditions`, `accepted` |
| wave | a batch of dispatches run in parallel, whose outputs are read together before the next step |

# Appendix B — The contracts {-}
Six JSON Schemas under `02-reflexive-application/05-contracts/`, each
declaring `contract_version` `1` and rejecting unknown fields. The
validator applies a closed subset of JSON Schema keywords and reports a
contract that uses others.

| Contract | File | Required fields | Optional fields |
| --- | --- | --- | --- |
| Note | `notes.schema.json` | `target_artifact`, `severity` (the four values), `text`, `origin`, `evidence`, `round` (string, or the legacy integer) | `status` (`open`, `fixed`, `disputed`, `out of scope`), `closed_in` |
| State of a note | `notes-status.schema.json` | `ref` (`notes:<n>` or `panel:<version>:<id>`), `status`, `summary` | `closed_in`, `prev`, `escaped`, `gate`, `no_gate`, `decision`, `opened_in`, `due`, `severity`, `affects` |
| Instance registry | `registry.schema.json` | `instances`: a list of entries with `id`, `status` (`executed`, `designed`) | per entry: `document`, `sha256`, `locator`, `number_format` (`point-decimal`, `comma-decimal`), `heading_style` (`section`, `subsection`, `step`), `method_version`; an executed entry carries the first four non-null, a designed one keeps them null |
| Round record | `round-record.schema.json` | `method_version`, `round`, `models` (a list of `role`, `model`, with optional `tokens` of `input`, `output`, `reasoning`, `cached`; `calls`; `finish`), `summary` | `verdict`, `rubric_hash`, `rubric_author`, `family_map_commitment`, `prev`, `kind` (`production`, `maintenance`), `reviewer_relation` (`another family`, `same family, separate session`, `same model, separate route`, `none`), `rubric_applied`, `rounds_to_stop`, `wall_seconds`, `notes_count`, `crew` |
| Domain result | `domain-result.schema.json` | `contract_version`, `gate`, `magnitude`, `limit`, `result` (`pass`, `fail`, `tool-failure`), `inputs` (a list of `path`, `sha256`) | — |
| Owner decisions | `owner-decisions.schema.json` | `name`, `status` (`open`, `decided`), `blocks`, `version`, `summary` | `covers`, `prev` |

The scaffold writes a seventh, `02-canon.schema.json`, the contract of a
cell's JSON canon, and copies the first five except the registry's (a
cell's `priors.json` follows the same contract, enforced by the validator).

# Appendix C — Command-line reference {-}
## `validator.py`

| Option | Meaning |
| --- | --- |
| `--folder FOLDER` | the production folder (default `.`) |
| `--layout LAYOUT` | a `layout.json` that remaps artifacts to paths and gates to parsers; default is the Markdown layout of the corpus |
| `--registry REGISTRY` | the instance registry; default `../instances/registry.json` relative to the folder, when present; without a registry `p-prior` is pending |
| `--case CASE` | a prior method document, repeatable; each is identified by its sha256 against the registry |
| `--forbidden FORBIDDEN` | the list of forbidden identifiers, one per line (names or `sha256:<hex>`); without it that half of `p-anonymity` is pending |
| `--rubric-hash FILE` | the file with the frozen sha256 of the rubric |
| `--freeze-rubric FILE` | write the current sha256 of the rubric to the file and exit; refuses an existing pin (the scaffold's `not-frozen` placeholder excepted) |
| `--re-freeze-rubric FILE` | replace an existing frozen rubric deliberately; mutually exclusive with the previous |
| `--notes NOTES` | the note ledger to validate against the contract, with its state ledger |
| `--output FILE` | write the report to the file; one summary line goes to the error stream |
| `--determinism` | run twice more with different hash seeds (and the C locale) and compare the reports |
| `--allow-pending LIST` | the gates whose pending rows the caller accepts, comma-separated, from the closed list `p-anonymity`, `p-prior`, `p-prior-pin`, `p-sensitivity-synthetic` |
| `--self-test` | run the embedded checks and exit |

Exit codes: 0, 1, 2, 4 (chapter 12).

## `sensitivity.py`

| Option | Meaning |
| --- | --- |
| `--folder FOLDER` | the production folder to copy and perturb |
| `--case CASE` | as in the validator, repeatable; without any, the rows that need a prior are not measured |
| `--forbidden FORBIDDEN` | the list of forbidden identifiers |
| `--registry REGISTRY` | the instance registry |
| `--rubric-hash FILE` | forwarded to the validator; without it the `p-frozen-rubric` row is not measured |
| `--notes NOTES` | forwarded; without it the `p-notes` row is not measured |
| `--work WORK` | the scratch folder for the copies (default: a temporary folder) |
| `--output FILE` | where the report is written (default: the layout key `artifacts.sensitivity`) |
| `--synthetic-prior ID` | an executed prior whose method document you do not have: a synthetic document is generated from the canon's recorded facts and pinned in the copies only |
| `--layout LAYOUT` | the cell's `layout.json`, which also names the cell's perturbation file |

An empty perturbation set exits 4; a gate the validator does not implement
in the set is a tool failure (exit 2).

## `scaffold.py`

| Option | Meaning |
| --- | --- |
| `--target TARGET` | the name of the target (required) |
| `--roles ROLE [ROLE ...]` | role ids, lowercase letters, digits and hyphens (required) |
| `--out OUT` | the destination folder (required); the scaffold refuses to overwrite |

Run from inside the material, so that it finds the validator, the
sensitivity script, the perturbation module and the contracts to copy.

## The historical validator of instance 004

`instances/004-adoption-guide/08-validator/validator.py` is the instrument
of 0.2.2 and refuses to run without `--historical`, since its exit 0 does
not mean what the current validator's does.

# Appendix D — The false greens of the gates {-}
From the table of `06-gate-semantics.md`, "The false greens of the gates":
for each gate, the cause of a false green found so far, what detects it
today, and the perturbation that covers it. The causes are the ones found,
not an exhaustive list.

| Gate | Cause of a false green | Current detection | Perturbation that covers it |
| --- | --- | --- | --- |
| `p-terms` | a synonym written in a way the lexical match does not see | the canon's list and whole-word matching; the review reads the prose | avoid-word in the changelog |
| `p-canon-link` | a link that names the canon from the wrong folder | the target resolved relative to the document's folder | link to the canon does not resolve |
| `p-anonymity` | a path, a date or an identifier in a form the patterns do not know, or hidden by the valve | the patterns, the months of six languages and the canon's own, the forbidden list by name or sha256; an accepted path dropped only by equality | date written with the month's name |
| `p-form` | an HTML tag or comment hidden in a block the reader skips | one reader of fences, comments read | HTML comment |
| `p-size` | a document pushed past its range, or words counted wrong | the declared ranges; table pipes are no words | canon pushed above its size range |
| `p-table` | an instantiation table missing a row | the canon's fixed list of rows | instantiation table row deleted |
| `p-sections` | an instance missing a mandatory section | the canon's fixed list of sections | mandatory section heading removed |
| `p-card` | a card with a field empty, deleted or a placeholder | the seven fields, the placeholder detector | placeholder in a card field |
| `p-limit` | a justification of six words of any kind, or a limit raised in the table | the origin label and the word count; the Limit column compared | limit raised in the gate table |
| `p-references` | a reference to a role, an artifact or a gate that does not exist | the artifact table, the graph without cycles, the commands resolved | limit cell diverges from the applied limit |
| `p-prior` | an invented number about a prior: in a code span, under a malformed mark, in a section the reader does not find | each number checked in the sections its recorded fact cites; section commitments; the synthetic prior in the registry's heading style | prior number in a code span |
| `p-prior-mark` | a statement about a prior with no mark, or the mark in a code span | the canon's triggers, read outside code spans | prior mark inside a code span |
| `p-prior-pin` | a prior document swapped or edited, or a pin no run compares | the registry's sha256 compared with each document passed, prior by prior | prior pin altered in the registry |
| `p-contract-shape` | a ledger line rewritten, a contract of another version, a registry entry that breaks its status | the schemas line by line, the hash chain (an edit that recomputes it is not detected) | old line of the round record edited |
| `p-recipe` | a step of the recipe without one of its fields | the canon's step fields | step field deleted |
| `p-components` | a component the principle names and an instance omits | the canon's list | method component omitted |
| `p-efficacy-mark` | a claim that the method works without a label, or with a label citing nothing executed | the canon's triggers (lexical), the provenance table of an experiment, a lessons title that resolves | claim backed by a designed experiment |
| `p-notes` | a note without a state, a regression closed with a gate that does not exist, a protection undone by a later line | the state ledger, golden rule 4 against the gate table, the highest severity and the union of `affects` | note without a status line |
| `p-frozen-rubric` | a rubric or a frozen record rewritten after the fact | the sha256 of the rubric and of each frozen record; the attestation in the owner's run | frozen review report rewritten |
| `p-sensitivity` | a report the instrument did not produce, a stale one, or one made without the owner's document read as made with it | the provenance header, the case lines against the pins, the attestation, a synthetic prior never a pass | none: the baseline reads the report; its defects are regression tests |
| `p-declared` | a declared path that matches nothing, a repointed file, a document no artifact declares | each literal path and each glob, the resolved map pinned in the sensitivity's provenance | file of an artifact repointed |

# Appendix E — File index of the material {-}
The 79 files the material tracks at 0.6.0, grouped.

| Path | Contents |
| --- | --- |
| `README.md`, `VERSION`, `CHANGELOG.md`, `LICENSE`, `.gitattributes`, `.gitignore` | the entry page, the version, the history, the license, the LF rule, the ignore list |
| `01-principle.md` | the method |
| `02-reflexive-application/README.md` | the index and the runbook of the reflexive application |
| `02-reflexive-application/00-brief.md` … `06-gate-semantics.md` | brief, canon, artifacts, four role cards, gates and rubric, gate semantics |
| `02-reflexive-application/05-contracts/*.schema.json` | the six contracts |
| `02-reflexive-application/10-generic-recipe.md` | the fifteen steps |
| `02-reflexive-application/20-instance-car.md`, `21-instance-text-2027.md`, `22-instance-hpc.md` | the three designed instances |
| `02-reflexive-application/60-experiments.md` | E1 to E5 |
| `02-reflexive-application/80-validator/validator.py`, `sensitivity.py`, `perturbation_set.py`, `test_validator.py` | the instrument and its suite |
| `02-reflexive-application/80-validator/report.md`, `sensitivity.md` | the published reports |
| `02-reflexive-application/90-review/rubric.sha256`, `auditor-report.md`, `auditor-notes.json`, `notes.json`, `replies.md` | the frozen records of round 1 |
| `02-reflexive-application/99-lessons.md` | the lessons, one entry per round |
| `02-reflexive-application/state/round-record.jsonl`, `notes-status.jsonl`, `owner-decisions.jsonl` | the three chained ledgers |
| `skills/cooperatio-teamwork/SKILL.md`, `references/templates.md`, `references/review-checklist.md`, `scripts/scaffold.py`, `scripts/test_scaffold.py` | the skill |
| `instances/registry.json` | the instance registry |
| `instances/004-adoption-guide/` | the cell of the second executed instance: brief, sources of truth, JSON canon, artifacts, four cards, two contracts, gates, rubric and pin, the validator of 0.2.2 with its rules and reports, the engine's README, the two wave reports and the round-1 notes, the state ledgers, lessons, open notes, priors, layout, the guide (`guia-de-adocao.md`), the method document (`metodo-de-producao.md`) and `ERRATA.md` |
| `docs/manual/` | this manual: `src/`, `diagrams/`, `filters/`, `Makefile`, the built `manual.md`, `manual.pdf` and `build/manual.tex` |

# Appendix F — Open owner decisions {-}
The lines of `02-reflexive-application/state/owner-decisions.jsonl` at
0.6.0, all `open`; each names what it blocks. Only the owner can close
one, with a new chained line.

| Decision | What it blocks |
| --- | --- |
| sign the tag of the version (create a signing key and sign `v0.6.0`) | the anchor of integrity outside the tree |
| publish an extract of the first prior, or not | a clone's check of the numbers about `000-av-production` |
| accept or adjust the thresholds to promote or withdraw a claim | experiment E4 |
| approve the budget and run E4 | the measure of value of the material |
| find the third party for E5 | the measure of portability |
| promote independence across families to a rule | the rule of independence |
| open the next production of the material as a production, with its own brief, a rubric of the reviewing side and a stop | a new verdict of the canon on the material |
| replace the cell of 004 as the example (a new cell under 0.6.0 would be the third execution) | an executable example of a cell |

# Appendix G — Building this manual {-}
The manual lives in `docs/manual/`:

| Path | What it is |
| --- | --- |
| `src/*.md` | the source, one file per part, concatenated in order |
| `diagrams/*.dot` | the Graphviz twin of each Mermaid diagram; rendered to `.svg` and `.pdf` |
| `filters/mermaid.lua` | the pandoc filter that swaps a Mermaid block for its twin's PDF in the PDF build |
| `filters/header.tex` | the LaTeX preamble additions (fonts, shaded code blocks, table spacing) |
| `Makefile` | the build |
| `manual.md` | the concatenated Markdown, for viewers that render Mermaid |
| `build/manual.tex`, `manual.pdf` | the LaTeX and the PDF editions |

Each Mermaid block opens with two Mermaid comments, `%% name:` (the twin
under `diagrams/`) and `%% caption:`, which the filter reads; a Markdown
viewer ignores them. The build needs pandoc 3 or later, Graphviz and
LuaLaTeX with the TeX Gyre fonts (TeX Live 2025 was used); no Mermaid
renderer is needed:

```bash
cd docs/manual
make            # manual.md, the diagrams, build/manual.tex, manual.pdf
make check      # margin overflow check of the PDF, where the local tool exists
```

The manual follows the form rules of the material where it can: no
absolute path, machine name, user name, model identifier or authoring
date; executors by family letter; claims of efficacy with their label.
