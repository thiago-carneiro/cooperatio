# Errata of the adoption guide (instance 004)

This cell is the record of the second executed instance of the method,
produced under method version 0.2.2. Its guide (`guia-de-adocao.md`) was
accepted by the one review of that production and is frozen: it is never
edited to match a later version. This page, written in v0.6.0, lists what
the guide says that is false when read against the material as it stands,
with the sentence that is true now. The pin in `../registry.json` covers the
method document of the cell (`metodo-de-producao.md`), not this page, and
not the guide.

**Read the cell as a record, not as an example to copy.** It does not run
on the current validator without a migration (the migration note of the
`CHANGELOG.md`), and its own copy of the validator, `08-validator/validator.py`,
is the instrument of 0.2.2: since v0.6.0 it refuses to run unless it is
called with `--historical`, because its exit 0 does not mean what the
current validator's does (under 0.2.2 a gate that was not measured left the
run with exit 0). That flag is the only change made to the cell since it
was distributed; the reports under `08-validator/` and `review/` are the
reports of that execution. To start a production of your own, follow the
skill (`skills/cooperatio-teamwork/SKILL.md`) and the root `README.md`.

| Where in the guide | What it says (in Portuguese, as written) | What is true now |
| --- | --- | --- |
| The header paragraph | that every statement of fact about the method in the guide can be checked in the material | the three statements below no longer match the material; the rest was checked by the review of that production |
| "Rúbrica congelada" (line 27) | the rubric is frozen with its hash recorded before the first production | the rubric is written and frozen before the first review (step 8 of the recipe and the canon's definition of rubric), not before the production |
| "O que a evidência hoje sustenta" (line 50) | the instance registry holds one completed execution | the registry holds two executed instances: the first one, owner-held, and this one, `004-adoption-guide`, registered when its production closed; the three others are designed sketches, not executed |
| The distribution paragraph (line 56) | the skill folder works copied alone, with scripts and references of its own | copied alone, the skill still creates a cell, but without the validator, the sensitivity script and the contracts it copies from the material, and it says so; the cell has no validator until they are copied in |

The guide also writes the idea of the method with "toda revisão é
independente" (every review is independent). Since v0.6.0 the material
reads independence across families as a recommendation with a cost, not a
rule, and records each reviewer's relation to the producer; the one review
of this production came from the producer's own model through another
route, as `metodo-de-producao.md` states.
