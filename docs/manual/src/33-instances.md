
# The instances

## Instance 000: the audiovisual production method

The first executed instance, from which the method was generalized: an
audiovisual production method, written in Brazilian Portuguese, held by
the owner and not distributable. The registry pins its method document by
sha256 and declares its number format (`comma-decimal`) and its heading
style (a section `## 6.`, a subsection `### 1.1`, a step `### Passo 15.`),
and the canon commits, section by section, to the text of the twelve
sections the recorded facts cite. The facts the material states about it
are the rows of the canon's "Recorded facts" table — among them 18 roles
with a card, 49 artifacts in the graph of its first pilot, 2 maximum rounds
per artifact, the review of v1 with 3 blocking, 4 high, 12 medium and 12
low findings, 26 low notes open at v5, a drift gate whose wrong instrument
read a p95 of 0.546 s at v1 and 0.10 s once fixed, and an automatic
reviewer of which 10 of 12 notes were false `[prior:000-av-production]`.
Several rules of the recipe carry the error of this instance that the step
prevents, as a measured size of the error.

Its historical vocabulary is recorded in the canon so that the frozen
records of round 1 can be read: the validator was its "continuity
checker"; the verdicts were "publishable", "publishable with minor
corrections" and "rejected"; the production cell carried a media term;
the quarantine mark of a bracketed word became `[prior:<id>]`.

## Instance 004: the adoption guide

The second executed instance: the adoption guide of the method itself, in
Brazilian Portuguese, of 900 to 1,400 words by its brief, produced under
method version 0.2.2 with a writer of one family and a review in a
separate dispatch without the producer's reasoning, which gave `accepted`
with no dimension below 4 and a guide of 1,054 words
`[prior:004-adoption-guide]`. That review was first recorded as coming
from another family; it came from the producer's own model through
another route, so it separated the session and the reasoning, not the
family.

Its cell is distributed under `instances/004-adoption-guide/` since
v0.5.0, as a **record, not an example to copy**:

- it does not run under the current validator without a migration (the
  migration notes of `CHANGELOG.md`);
- its own copy of the validator, `08-validator/validator.py`, is the
  instrument of 0.2.2 and since v0.6.0 refuses to run unless called with
  `--historical`, because its exit 0 does not mean what the current
  validator's does (under 0.2.2 a gate that was not measured left the run
  with exit 0); that flag is the only change made to the cell since it was
  distributed;
- its `ERRATA.md` lists what the guide says that is no longer true when
  read against the material as it stands (the rubric is frozen before the
  first review, not before the production; the registry holds two executed
  instances; the skill copied alone creates a cell without the validator;
  independence across families is a recommendation, not a rule);
- its list of forbidden identifiers stayed with the owner, outside the
  material, since it contains what it forbids.

The cell shows the shape of a JSON-layout cell at 0.2.2: `00-brief.md`,
`01-sources-of-truth.md`, `02-canon.json`, `03-artifacts.json`,
`04-roles/` (four cards), `05-contracts/`, `06-gates.md`, `07-rubric.md`
with its pin, `08-validator/` with its reports, `09-engine/`, `review/`
(two wave reports and the round-1 notes), `state/`, `lessons.md`,
`open-notes.json`, `priors.json`, `layout.json`, the guide, the method
document and the errata.

Whether a new cell under 0.6.0 replaces it as the example is an open owner
decision (appendix F).

## The three designed instances

Three instances were chosen because they differ from each other, and each
fills the fourteen rows of the instantiation table and the fourteen
mandatory sections with domain content marked `[hypothesis]` where it is
an assumption. They are designed sketches, not executions, and carry the
design, not a result.

| Element | Car (`20-instance-car.md`) | Text about 2027 (`21-instance-text-2027.md`) | HPC library (`22-instance-hpc.md`) |
| --- | --- | --- | --- |
| Target | the design of a battery-electric passenger vehicle released for tooling, with approved validation prototypes and a homologation dossier | a publishable nonfiction manuscript of about 90 thousand words in 12 chapters on the world in 2027, saying on every page which statement is fact, projection or opinion | a C++ library with a C interface that replaces the reference implementation of a 3D finite-difference operator, with measured speedup and byte-for-byte identical outputs |
| Owner | the program director | the author | the library's technical lead |
| Sources of truth | requirement → brief and regulatory matrix; geometry → released CAD; mass → weighing; cost → supplier quotation; physics → correlated simulation; standard → the regulation's text | fact → primary source; projection → declared model; number → claims register; quotation → original; figure → data plus script | correctness → oracle (frozen reference and hashed outputs); performance → measurement on a pinned node with the configuration obtained recorded; where the time goes → attribution instrument |
| Main artifacts | requirements, architecture, budgets, subsystem CAD, virtual vehicle, BOM, simulations, safety analysis, validation plan, test reports, homologation dossier | thesis, theme map, domain dossier, claims register, projections, outline, scenarios, chapters, figures, fact-check, manuscript | specification, interface, oracle, attribution report, lever decision, experiment plan, implementation, tests, build, equivalence, measurements, performance report, documentation |
| Main gates | mass against target with reserve, range with the real mass, charging time, clearances, crash margin, thermal propagation, traceability, coverage, quoted cost, simulation × test correlation | every claim with a register identifier, every projection marked, primary source, source density, readability, size per chapter, overlap, recheck of volatile claims | byte-for-byte equivalence, independence from order and thread count, sensitivity of the gate to mutations, configuration obtained, noise, speedup with confidence interval, size sweep, prediction written beforehand, sanitizers, third-party reproduction |
| Review rubric | a design review by a panel from outside the program | blind reading by readers from the target audience | code review and benchmark reproduction by someone who did not implement |
| What stays with the human | targets, styling, supplier choice, residual risk, safety sign-off, the decision to launch | thesis, tone, opinion, the label of projection or opinion, legal risk, release | what to optimize, the target, acceptable memory, new dependencies, the budget, the release |

What each sketch adds to the method's vocabulary: the car shows the gates
of a physical product and the fidelity ladder of its versions (paper,
virtual, engineering prototype, validation prototype); the text shows the
separation of fact, projection and opinion as a contract of the claims
register and a gate on the chapters; the HPC library shows the danger
moving from the role that writes badly to the instrument that measures
wrongly and passes — the equivalence gate that never rejects, the benchmark
that records the threads requested and not the threads obtained, the
speedup measured at an extreme point and generalized — and makes "measure
what the system gave, not what was asked for" the first gate of the loop.

## The registry as a contract

`instances/registry.json` is one list; the status of an entry decides its
fields, and `p-contract-shape` enforces that contract on every run. A cell
keeps its own registry, `priors.json`, in the same contract, and registers
itself in it at the close of its production (step 14 of the recipe), which
is also what makes the token of its own id read as a name rather than as a
number.
