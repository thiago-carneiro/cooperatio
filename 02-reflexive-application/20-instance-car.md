# Instance 1: a new car

The recipe of `10-generic-recipe.md` applied to the development of a new car
with the most advanced technologies available. The method terms follow the
[canon](01-canon.md). Everything that is an assumption about the automotive
domain is marked `[hypothesis]`: the numbers are plausible and justified, not
normative, and a real instance replaces them with those of its own program and
its own market.

The production cell's target here is not the factory or the series car: it is
the **design released for tooling**, with validation prototypes that passed the
test plan and the homologation dossier ready. What happens afterwards
(industrialization, series production) would be another production cell.

## 0. Instantiation table

| Element | In this instance |
| --- | --- |
| Target | design of a new battery-electric passenger vehicle released for tooling, with approved validation prototypes and a homologation dossier `[hypothesis: typical scope of a program up to design freeze]` |
| Owner and owner decisions | the program director: cost, mass, range and price targets, target market, styling, acceptance of residual risk, release of each phase |
| Sources of truth by content type | requirement → brief and regulatory matrix; geometry → released CAD with tag; mass → weighing or CAD mass properties; cost → supplier quotation; physics → simulation correlated with testing; standard → official text of the regulation; prototype performance → test with a calibrated instrument |
| Main artifacts | `requirements`, `architecture`, `budgets`, `subsystem-cad`, `virtual-vehicle`, `bom`, `simulations`, `safety-analysis`, `vehicle-software`, `validation-plan`, `test-reports`, `sim-test-correlation`, `homologation-dossier` |
| Roles | systems engineer, subsystem designer, virtual vehicle integrator, embedded software engineer, simulation analyst, safety engineer, cost engineer, manufacturing engineer, validation engineer, homologation specialist, validator, independent reviewer |
| Main gates | mass measured against target with reserve, range simulated with the real mass, charging from 10% to 80%, interferences and clearances, crash margin, battery thermal propagation, traceability, MC/DC coverage, quoted cost, simulation × test correlation |
| Independent review rubric | design review by a panel from outside the program: requirements met, safety, compliance, integration, cost and manufacturing, quality of evidence, occupant experience, documentary coherence |
| Validator verifies | part numbers across CAD, BOM, wiring harness and software; units; masses and costs across BOM, budgets and reports; cited CAD, software and standard versions; requirement identifiers |
| Assembly engine | code that assembles the virtual vehicle by tag, sums masses and costs, detects interferences, regenerates simulations by hash and checks traceability; agents draft requirements, failure analyses and the regulatory matrix under gate |
| Quick first version | the "paper vehicle": parametric package, budgets, 1D energy model, simplified crash model, initial hazard analysis, parametric BOM, reviewed by the panel within a few weeks |
| Round loop | each version raises the fidelity (paper, virtual, engineering prototype, validation prototype); within each one, rounds of notes, new gates and instrument correction by correlation with testing |
| Stopping criterion | release for tooling when the review gives accepted and all safety and regulatory gates pass; low notes become open notes for pre-series |
| Case method document | `program-method.md`: graph, roles with degree, gates with limit history, corrected simulation false positives, owner decisions |
| What stays with the human | targets and positioning, styling, final supplier choice, acceptance of residual risk, functional safety sign-off, relationship with the homologation authority, decision to launch |

## 1. Brief

The brief (the production cell's `00-brief.md`) has the fixed sections of the
recipe. Here is the content of each one:

- **Target:** battery-electric passenger vehicle, five seats, mid-size segment,
  with an 800 V platform, a structural battery (cell-to-pack), a zonal
  electrical and electronic architecture with a central computer, over-the-air
  software updates and Level 2 driver assistance `[hypothesis: a set that
  represents "the most advanced available" without depending on technology
  that cannot yet be homologated]`.
- **For whom:** the market defined by the owner; here, markets that adopt the
  UN regulations for vehicles `[hypothesis]`.
- **Non-negotiables**, written as measurable things:
  - curb mass ≤ 1,900 kg `[hypothesis]`;
  - range on the WLTP cycle ≥ 500 km `[hypothesis]`;
  - charging from 10% to 80% in ≤ 20 min `[hypothesis]`;
  - material cost ≤ the owner's target (value in the brief, not in this
    document);
  - no safety or regulatory gate open at release.
- **Owner decisions:** the targets above; styling (exterior shape and
  interior); final supplier of the cell and of the central computer; accepted
  residual risk; release of each phase; launch market.
- **Budget:** maximum rounds per artifact = 2 before escalating to the program
  director; one independent review per version.
- **Provisional stopping criterion:** the one in section 11.
- **What is not a goal:** industrialization, service network, selling price.

## 2. Initial canon

| Section | Owner | Initial content |
| --- | --- | --- |
| Goals | systems engineer | the brief's non-negotiables with canonical spelling, unit and rounding (mass in kg with no decimal places; range in km; Cd to three decimal places) |
| Units and spellings | systems engineer | SI; space as thousands separator in documents and none in data files, as accepted variant "in data"; temperature in °C in documents and K in simulation decks |
| Nomenclature | systems engineer | subsystem tree with fixed code (body, chassis, propulsion, battery, thermal, electrical and electronic, interior, software); part number rule |
| Tags | virtual vehicle integrator | format of the CAD and software release tag; which tag is valid in each version |
| Standards | homologation specialist | list of the regulations and revisions the program follows, one revision per regulation |
| Terms to avoid | systems engineer | "approximately" in a requirement, "adequate", "robust", "sufficient" without a value; synonyms for a subsystem outside the tree |
| Declared fits | subsystem designer | intentional interferences (interference fit, press fit) with value and tolerance, so the interference detector does not flag them |
| Accepted risks | owner | residual risk accepted, with who accepted it and with what evidence; starts as `pending` |

## 3. Artifacts and graph

| Artifact | Owner | Depends on | Schema | Gates |
| --- | --- | --- | --- | --- |
| `brief` | owner | — | fixed sections of the recipe | exists; approved by the owner |
| `owner-decisions` | owner | `brief` | record per decision: what, when in the round, with what evidence | exists |
| `canon` | systems engineer | `brief`, `owner-decisions` | JSON per section, with owner and version | schema |
| `regulatory-matrix` | homologation specialist | `brief` | table regulation × requirement × verification method | `g-matrix` |
| `requirements` | systems engineer | `brief`, `owner-decisions`, `regulatory-matrix`, `canon` | tree vehicle → system → component; each requirement with value, unit, owner and verification method | `g-traceability`, `g-measurable-requirement` |
| `architecture` | systems engineer | `requirements` | functional, physical and electrical/electronic, with numbered interfaces | interface schema |
| `budgets` | systems engineer | `requirements`, `architecture` | mass, energy, cost and space allocated per subsystem | sum of allocations ≤ target |
| `safety-analysis` | safety engineer | `requirements`, `architecture` | hazard and risk analysis with integrity classification, failure mode analysis, cybersecurity threat analysis | `g-functional-safety`, `g-cybersecurity` |
| `subsystem-cad` | subsystem designer | `architecture`, `budgets`, `requirements`, `safety-analysis` | CAD model released with tag, per subsystem, with mass properties | metadata schema |
| `vehicle-software` | embedded software engineer | `architecture`, `requirements`, `safety-analysis` | code, configuration and tests per function, with tag | `g-software-coverage`, `g-software-defects`, `g-compute-load`, `g-cybersecurity` |
| `virtual-vehicle` | virtual vehicle integrator | `subsystem-cad` | integrated assembly by tag, with mass, center of gravity and interference list | `g-interference`, `g-mass-budget` |
| `bom` | cost engineer | `subsystem-cad` | bill of materials with part number, mass, supplier, quotation or marked estimate | `g-bom-cad`, `g-cost`, `g-mass-budget` |
| `dfm-analysis` | manufacturing engineer | `subsystem-cad` | manufacturability and assembly assessment per part | `g-dfm` |
| `simulations` | simulation analyst | `virtual-vehicle`, `vehicle-software`, `requirements` | one deck per quantity (energy, crash, aerodynamics, noise, thermal), generated from the current tag | `g-range`, `g-charging`, `g-crash` |
| `validation-plan` | validation engineer | `requirements`, `safety-analysis`, `regulatory-matrix` | requirement × test or analysis × criterion × sample | `g-plan-coverage` |
| `prototypes` | manufacturing engineer | `virtual-vehicle`, `bom`, `dfm-analysis`, `vehicle-software` | build record per prototype: CAD and software tags, deviations, weighed mass | `g-mass-budget` |
| `test-reports` | validation engineer | `prototypes`, `validation-plan` | one report per test: instrument, calibration, uncertainty, prototype tag, result | `g-test-instrument`, `g-thermal-propagation`, `g-noise`, `g-charging` |
| `sim-test-correlation` | simulation analyst | `simulations`, `test-reports` | per quantity: simulated, measured, error, cause of the difference | `g-correlation` |
| `validation-report` | validator | `canon`, `requirements`, `subsystem-cad`, `bom`, `vehicle-software`, `simulations`, `test-reports` | deterministic report per rule | `g-validation` |
| `homologation-dossier` | homologation specialist | `regulatory-matrix`, `test-reports`, `safety-analysis` | per matrix item: evidence and status | `g-dossier` |
| `design-review` | independent reviewer | `virtual-vehicle`, `simulations`, `safety-analysis`, `bom`, `test-reports`, `validation-report`, `homologation-dossier` | report format of the rubric | frozen rubric |
| `phase-release` | owner | `design-review`, `homologation-dossier` | recorded decision with verdict, accepted open notes and accepted risks | exists; signed |

The artifact graph, from top to bottom (each arrow means "is read by"):

```text
brief ─> owner-decisions ─> canon
  └─> regulatory-matrix ─┐
                         v
                    requirements ─> architecture ─> budgets
                         │               │             │
                         └──> safety-analysis <────────┘ (reads architecture)
                                    │
            ┌───────────────────────┼──────────────────────────┐
            v                       v                          v
      subsystem-cad          vehicle-software            validation-plan
    ┌──────┼───────────┐            │                          │
    v      v           v            │                          │
virtual-  bom    dfm-analysis       │                          │
vehicle    │           │            │                          │
   │  └────┴────> prototypes <──────┘                          │
   v                   │                                       │
simulations            └──────> test-reports <─────────────────┘
   └──────────> sim-test-correlation <──┘      │
                                               v
                                    homologation-dossier
validation-report ─> design-review ─> phase-release
```

A loop that looks like a cycle and is not: the correlation between simulation
and testing corrects the simulation models, but by **note** to the
`simulations` artifact (instrument fixed at the root), not by dependency. If it
were an edge, the graph would have a cycle and nothing would know in what order
to rebuild.

## 4. Role cards

### Systems engineer

- **Decides:** the requirements tree, the architecture and the allocation of
  the mass, energy, cost and space budgets among subsystems.
- **Does not decide:** the vehicle targets (owner); the solution inside a
  subsystem (designer); the safety integrity classification (safety engineer).
- **Inputs:** `brief`, `owner-decisions`, `regulatory-matrix`, notes.
- **Outputs:** `canon` (his or her sections), `requirements`, `architecture`,
  `budgets`.
- **Exit gate:** `g-traceability` and `g-measurable-requirement`; sum of the
  allocated budgets ≤ target.
- **Notes it emits:** to the designer, when a subsystem exceeds its budget
  (`high`); to the owner, when two targets contradict each other (`blocking`,
  with the calculation that shows the contradiction).
- **Code-conversion degree:** (b) traceability and the budget sums are code;
  writing requirements is an agent under gate, reviewed by the engineer.

### Subsystem designer

One card per subsystem (body, chassis, propulsion, battery, thermal,
electrical and electronic, interior), all with the same format.

- **Decides:** the solution of the subsystem within the budget and the
  interfaces.
- **Does not decide:** changing an interface or a budget (note to the systems
  engineer); accepting an interference (only if it is in the "declared fits"
  section of the canon).
- **Inputs:** `architecture`, `budgets`, `requirements`, `safety-analysis`.
- **Outputs:** `subsystem-cad` with tag and mass properties.
- **Exit gate:** valid metadata; subsystem mass ≤ allocated; no new
  interference in the `virtual-vehicle`.
- **Notes it emits:** to the `architecture`, when the interface does not close
  (`high`); to the `canon`, to declare an interference fit (`medium`).
- **Code-conversion degree:** (c) designing is human work with CAD tools; the
  code validates metadata and measures mass and interference.

### Virtual vehicle integrator

- **Decides:** no design decisions; assembles the vehicle from the tags that
  the canon says are valid in the version.
- **Does not decide:** which tag is valid (canon); how to resolve an
  interference (designer).
- **Inputs:** `subsystem-cad`, the "tags" section of the canon.
- **Outputs:** `virtual-vehicle`.
- **Exit gate:** `g-interference` and `g-mass-budget`.
- **Notes it emits:** to the designer who owns each part in interference
  (`high`); to the `canon`, when a cited tag does not exist (`blocking`).
- **Code-conversion degree:** (a) assembly, mass properties and interference
  detection are code; the integrator only decides exceptions.

### Embedded software engineer

- **Decides:** the implementation of each software function within the
  architecture and the requirements.
- **Does not decide:** the integrity classification (safety engineer); the
  allocation of a function to a computer (systems engineer).
- **Inputs:** `architecture`, `requirements`, `safety-analysis`.
- **Outputs:** `vehicle-software` with tag.
- **Exit gate:** `g-software-coverage`, `g-software-defects`,
  `g-compute-load`.
- **Notes it emits:** to the `architecture`, when the measured compute load does
  not fit in the allocated computer (`high`).
- **Code-conversion degree:** (b) tests, coverage and load measurement are
  code; implementing is an agent or a person under gate.

### Simulation analyst

- **Decides:** the simulation method for each quantity and the correction of
  the model when the correlation with testing fails.
- **Does not decide:** changing the design to pass the simulation (note to the
  designer); changing the limit (owner or systems engineer, with
  justification).
- **Inputs:** `virtual-vehicle`, `vehicle-software`, `requirements`,
  `test-reports`.
- **Outputs:** `simulations`, `sim-test-correlation`.
- **Exit gate:** `g-range`, `g-charging`, `g-crash` on the current tag;
  `g-correlation`.
- **Notes it emits:** to the designer, when a quantity is rejected (`high`); to
  `simulations` (to oneself, as an instrument), when the correlation shows an
  error above the limit (`high`).
- **Code-conversion degree:** (b) generating the decks from the tag and
  extracting the quantities are code; building and validating the model is
  human work.

### Safety engineer

- **Decides:** the integrity classification of each hazard, the safety goals
  and the cybersecurity threats to be treated.
- **Does not decide:** the technical solution (designer, software); accepting
  residual risk (owner).
- **Inputs:** `requirements`, `architecture`.
- **Outputs:** `safety-analysis`.
- **Exit gate:** `g-functional-safety`, `g-cybersecurity`.
- **Notes it emits:** to `requirements`, when a safety goal has no technical
  requirement (`blocking`).
- **Code-conversion degree:** (b) the completeness check is code; the analysis
  is human, with an agent drafting under gate.

### Cost engineer

- **Decides:** the source of each cost (quotation or marked estimate).
- **Does not decide:** the cost target (owner); swapping a part (designer).
- **Inputs:** `subsystem-cad`, quotations.
- **Outputs:** `bom`.
- **Exit gate:** `g-bom-cad`, `g-cost`.
- **Notes it emits:** to the designer, when a subsystem exceeds its allocated
  cost (`high`).
- **Code-conversion degree:** (a) the sum and the BOM × CAD check are code;
  quoting is human work.

### Manufacturing engineer

- **Decides:** the manufacturability assessment of each part and the build
  record of the prototypes.
- **Does not decide:** the geometry (designer).
- **Inputs:** `subsystem-cad`, `virtual-vehicle`, `bom`, `vehicle-software`.
- **Outputs:** `dfm-analysis`, `prototypes`.
- **Exit gate:** `g-dfm`; prototype mass weighed and recorded.
- **Notes it emits:** to the designer, when a part cannot be made with the
  planned process (`high`).
- **Code-conversion degree:** (c) the assessment is human; the code only
  checks that every part has one.

### Validation engineer

- **Decides:** the test plan and the validity of each test.
- **Does not decide:** the pass limit (requirement); repeating a test until it
  passes (a repeated test requires a recorded cause).
- **Inputs:** `requirements`, `safety-analysis`, `regulatory-matrix`,
  `prototypes`.
- **Outputs:** `validation-plan`, `test-reports`.
- **Exit gate:** `g-plan-coverage`, `g-test-instrument`.
- **Notes it emits:** to the artifact where the defect originated (design,
  software, simulation), never to the prototype (`high` or `blocking`).
- **Code-conversion degree:** (b) data acquisition and quantity extraction are
  code; the test itself is human work on the bench.

### Homologation specialist

- **Decides:** which regulations apply to the brief's market and what evidence
  each one requires.
- **Does not decide:** negotiating with the authority (owner); changing the
  design (note).
- **Inputs:** `brief`, `test-reports`, `safety-analysis`.
- **Outputs:** `regulatory-matrix`, `homologation-dossier`.
- **Exit gate:** `g-matrix`, `g-dossier`.
- **Notes it emits:** to `validation-plan`, when a matrix item has no test
  (`blocking`).
- **Code-conversion degree:** (c) reading a standard is human work, with an
  agent extracting requirements for review; the code checks completeness.

### Validator

- **Decides:** nothing beyond the rules it executes.
- **Does not decide:** whether a note of its own is a false positive (the
  analyst or designer contests it; the systems engineer decides).
- **Inputs:** `canon` and all the artifacts in the list of section 7.
- **Outputs:** `validation-report`.
- **Exit gate:** report identical in two runs.
- **Notes it emits:** those of section 7.
- **Code-conversion degree:** (a).

### Independent reviewer

- **Decides:** the scores per dimension and the severity of the findings; the
  verdict comes out of the rule.
- **Does not decide:** the rubric (frozen); what gets corrected; the release
  (owner).
- **Inputs:** the artifacts listed in the table, with no access to the
  program's discussions.
- **Outputs:** `design-review`.
- **Exit gate:** report in the format of the rubric.
- **Notes it emits:** to any artifact of the graph.
- **Code-conversion degree:** (c) a human panel from outside the program, with
  agents preparing the reading (quantity extraction, comparison between
  versions).

## 5. Gates

The magnitude is always what the system delivered: mass weighed or summed from
the CAD, not the allocated one; range simulated with the mass and drag of the
current version, not with the targets; compute load measured on the computer,
not estimated.

| Gate | Artifact | Magnitude | Limit | Justification |
| --- | --- | --- | --- | --- |
| `g-traceability` | `requirements` | vehicle requirements with no child requirement, no verification method or no owner | 0 | [method] a requirement without verification is a promise without a gate, and without an owner it is a note without a destination |
| `g-measurable-requirement` | `requirements` | requirements containing a term from the canon's "terms to avoid" list with no value and unit | 0 | [method] a requirement without a value cannot become a gate; the vague term is the typical drift of drafted requirements |
| `g-mass-budget` | `virtual-vehicle`, `bom`, `prototypes` | curb mass computed from the CAD and BOM masses, or weighed on the prototype, compared with the target | ≤ target − 3% on the virtual vehicle; ≤ target − 1% on the validation prototype | [hypothesis] mass tends to grow during development; a reserve that shrinks as fidelity rises absorbs the growth without hiding an overrun |
| `g-range` | `simulations` | range on the WLTP cycle simulated with the mass, drag and powertrain efficiency of the current tag | ≥ 500 km, with the model within the limit of `g-correlation` | [hypothesis] competitive target for the segment; without the correlated model, the number measures the model and not the car |
| `g-charging` | `simulations`, `test-reports` | time from 10% to 80% state of charge, at 25 °C, on a 350 kW charger, simulated and then measured | ≤ 20 min | [hypothesis] production 800 V platforms announce times of this order; the limit comes from the brief and needs the battery thermal design to be met |
| `g-interference` | `virtual-vehicle` | undeclared static interferences; smallest clearance between a moving part and its neighbor along its travel | 0 interferences; clearance ≥ 10 mm | [hypothesis] accumulated assembly tolerances and deformation in use consume a few millimeters; 10 mm is a usual order of magnitude for moving parts |
| `g-crash` | `simulations` | smallest margin between the simulated quantity (intrusion, acceleration, injury criterion) and the limit of the target protocol, across all load cases | ≥ 15% | [hypothesis] the scatter between simulation and crash test is of the order of ten percent; the margin covers the scatter before the physical test |
| `g-thermal-propagation` | `test-reports` | time between a thermal runaway triggered in one cell and fire or explosion outside the pack | ≥ 5 min, with a warning to the occupant | [hypothesis] value of the kind required by recent traction-battery regulations; the standard applicable to the brief's market confirms or replaces it |
| `g-functional-safety` | `safety-analysis` | hazards without integrity classification and goal; goals without technical requirement; high-priority failure modes without action | 0 | [method] completeness of the analysis is a condition for safety to be verifiable; the criteria follow the adopted functional safety standard [hypothesis] |
| `g-cybersecurity` | `safety-analysis`, `vehicle-software` | high-risk threats with no implemented and tested treatment | 0 | [hypothesis] requirement of vehicle cybersecurity regulations in the markets that adopt them; an open high threat blocks homologation |
| `g-software-coverage` | `vehicle-software` | structural modified condition/decision coverage in the functions of highest integrity | 100% | [hypothesis] the functional safety standard strongly recommends this criterion for the highest integrity level |
| `g-software-defects` | `vehicle-software` | open defects of high severity on the candidate tag | 0 at release | [method] an open high defect is an open high note, and a high note does not become an open note at release |
| `g-compute-load` | `vehicle-software` | processor load measured on the central computer in the worst usage scenario | ≤ 70% | [hypothesis] reserve for functions delivered by over-the-air update over the life of the car |
| `g-bom-cad` | `bom` | part numbers present in the CAD and absent from the BOM, and the reverse | 0 | [method] a part with no BOM line has neither cost nor mass; a line with no part is a phantom cost |
| `g-cost` | `bom` | material cost summed against the target; fraction of the cost backed by quotation | ≤ target; ≥ 80% quoted at release | [hypothesis] a parametric estimate errs more than a quotation; requiring most of it to be quoted measures what the supplier delivers, not what was estimated |
| `g-dfm` | `dfm-analysis` | parts without a manufacturability assessment before the tooling order | 0 | [method] tooling is the expensive work; the contract refuses ambiguity before it |
| `g-plan-coverage` | `validation-plan` | requirements with no test or analysis assigned | 0 | [method] a requirement without planned verification is a gate that never runs |
| `g-test-instrument` | `test-reports` | tests with an instrument without current calibration or without declared uncertainty | 0 | [method] measuring what the system delivered requires knowing how much the instrument errs |
| `g-noise` | `test-reports` | interior noise level at 120 km/h, at the driver's position | ≤ 68 dB(A) | [hypothesis] without a combustion engine, wind and rolling noise dominate; reference value for comfort in the segment |
| `g-correlation` | `sim-test-correlation` | error between simulated and measured per quantity | range ≤ 3%; drag coefficient ≤ 0.005 absolute; intrusion ≤ 10%; noise ≤ 1.5 dB(A) | [hypothesis] usual ranges of acceptable correlation; above them, the simulation is a broken instrument and the gates that depend on it are not valid |
| `g-matrix` | `regulatory-matrix` | regulations of the target market with no mapped requirement | 0 | [method] a regulation without a requirement is a non-negotiable without a gate |
| `g-dossier` | `homologation-dossier` | matrix items with no test or analysis evidence | 0 | [method] the dossier is the proof that each regulatory gate passed |
| `g-validation` | `validation-report` | open high and blocking notes from the validator | 0 to release the phase | [method] a divergence of part number or tag between documents is the cheapest way to build the wrong prototype |

Every code gate goes through the gate sensitivity test, with a known
perturbation, before it counts: a part
shifted 20 mm into its neighbor must be rejected by `g-interference`; a deleted
BOM line must be rejected by `g-bom-cad`.

## 6. Independent review rubric

A design review panel of engineers who do not work on the program, supported
by agents that extract quantities and compare versions. The rubric is written
before the review of the paper vehicle and frozen by hash.

| Dimension | What is measured | 1 | 3 | 5 |
| --- | --- | --- | --- | --- |
| Requirements met | each non-negotiable measured on the current version, not allocated | targets not measured or measured on the allocated value | measured, with margins at the limit | measured, with a reserve consistent with the phase |
| Safety | functional, passive and battery safety | hazard without treatment | complete analyses, partial evidence | complete analyses and correlated evidence |
| Compliance | matrix and dossier | regulation without requirement | complete matrix, partial dossier | complete matrix and dossier for the phase |
| Integration | interfaces, interferences, electrical/electronic and software with hardware | open interfaces | closed interfaces with recorded exceptions | no open exception |
| Cost and manufacturing | quoted cost, manufacturing assessments | parametric cost, no assessment | mostly quoted, partial assessments | quoted and with assessment |
| Quality of evidence | correlation, calibration, coverage | simulation without correlation | partial correlation | every quantity with correlation within the limit |
| Occupant experience | ergonomics, noise, interface | not evaluated | evaluated on a model | evaluated on a prototype with users |
| Documentary coherence | traceability and consistency | divergences between documents | low divergences | no divergence |

Severity: `blocking` for any safety or regulatory gate rejected and for any
safety quantity without evidence; `high` for a non-negotiable without a
measurement or an open integration; `medium` for cost without quotation and
weak evidence; `low` for documentation.

Verdict: `rejected` if there is a blocking finding or any dimension ≤ 2;
`accepted` if there is no high finding and all dimensions are ≥ 4; otherwise
`accepted with conditions`. At release for tooling, the owner accepts
only `accepted`.

## 7. Validator

| Checks | Against | Severity | Note to |
| --- | --- | --- | --- |
| part number | CAD × BOM × wiring harness list × software configuration | `high` | owner of the artifact that diverges from the released tag |
| unit and spelling of numbers | canon, "goals" and "units" sections | `medium` | document owner |
| cited mass and cost | BOM × budgets × reports | `high` | owner of the document that cites a stale value |
| cited CAD and software tag | "tags" section of the canon | `blocking` in a test report; `high` in the others | validation engineer or document owner |
| cited regulation revision | "standards" section of the canon | `high` | document owner |
| cited requirement identifier | `requirements` | `high` | document owner |
| declared interference | "declared fits" section | `medium` | designer |
| terms to avoid in requirements | "terms to avoid" section | `medium` | systems engineer |

## 8. Assembly engine

| Part | Code | Agent under gate | Human |
| --- | --- | --- | --- |
| Virtual vehicle | assembles by tag, computes mass and center of gravity, detects interference | — | resolves interference |
| Budgets and cost | sums and compares with the target; BOM × CAD | — | quotes |
| Simulations | regenerates decks when the tag changes (hash), extracts quantities, compares versions | — | builds and validates models |
| Requirements and traceability | checks the tree, vague terms, verification methods | drafts component requirements from the system ones | approves |
| Safety | checks completeness | drafts failure mode analysis | analyzes and signs |
| Regulatory matrix | checks completeness | extracts requirements from regulations | confirms applicability |
| Tests | acquires data and extracts quantities | — | runs the test |
| Notes | routes, deduplicates, counts rounds, escalates | summarizes work orders per wave | replies |

The engine rebuilds only what is stale: changing the battery CAD makes the
virtual vehicle, the BOM, the crash, energy and thermal simulations, and the
prototypes stale; it does not make the regulatory matrix or the threat
analysis stale.

## 9. Quick first version

The "paper vehicle", within a few weeks `[hypothesis]`:

1. parametric package (hard points, basic ergonomics, battery volume);
2. mass, energy and cost budgets from reference vehicles, marked as
   estimates;
3. one-dimensional energy model for the range;
4. simplified crash model (beams) for the margin;
5. hazard analysis at vehicle level;
6. parametric BOM and a skeleton regulatory matrix;
7. immediate independent review, with the rubric.

What it is expected to reveal: budgets without an owner (the thermal design of
800 V charging usually falls between battery and thermal `[hypothesis]`),
requirements without a verification method, forgotten regulations. The goal is
to be reviewed, not to be good.

## 10. Round loop

Each version raises the fidelity: v1 paper, v2 virtual with subsystem CAD, v3
engineering prototype, v4 validation prototype `[hypothesis: usual phases]`.
Within each version, rounds of notes, as in the recipe.

Examples of what the loop does here:

- **False positive, fixed at the root:** the detector flags as an interference
  the bearing press-fitted into the steering knuckle. The fix is not to
  increase the detector's tolerance; it is to declare the fit in the "declared
  fits" section of the canon, with value and tolerance, and to make the
  detector accept only what is declared; a test reproduces the case, and the
  previous round is redone to prove that no real interference disappeared.
- **Regression that escaped:** the change to the battery mount shortens the
  lateral load path and the side-impact margin drops, but the side simulation
  did not run because the deck depended only on the body. Before fixing it, the
  deck now also depends on the battery (the hash catches the change) and the
  side margin enters `g-crash`.
- **Instrument corrected:** the chassis dynamometer test gives 6% less range
  than the simulation; `g-correlation` rejects; the note goes to
  `simulations`, which finds the inverter loss at part load underestimated;
  once the model is corrected, the simulations of the previous round are
  redone.

## 11. Stopping criterion

Declared by the owner before the last round of v4: release for tooling when
the review gives `accepted` and all safety and regulatory gates pass. `low`
and `medium` notes become open notes for pre-series. A rule specific to the
domain: a safety or regulatory note never becomes an open note, because a
violated non-negotiable is not debt, it is a target not met.

## 12. Case method document

`program-method.md`, with: the ideas and the defect each one prevented in the
program; the graph with the real dependencies; the step-by-step with the
engine's commands; per role, the pseudocode of the work and the
code-conversion degree, with what is missing to raise it; the history of each
limit (who changed it, why, with what evidence); the simulation and detector
false positives that were corrected; the owner decisions; the stopping
criterion as applied.

## 13. What stays with the human

- Targets, positioning and market.
- Styling: the shape of the car is the owner's decision, with a consumer
  clinic.
- Final choice of suppliers.
- Acceptance of residual risk, with signature.
- Functional safety sign-off by the designated responsible person.
- Relationship with the homologation authority.
- Execution of the physical tests and the decision to launch.

The code prepares each of these decisions (the calculation, the evidence, the
list of open items); it does not make them.
