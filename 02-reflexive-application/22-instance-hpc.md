# Instance 3: an HPC library with measured gain and identical results

The recipe of `10-generic-recipe.md` applied to the development of a
high-performance computing library that has to be faster than the reference
implementation and give results identical to it. The method terms follow the
[canon](01-canon.md). What is an assumption about the domain is marked
`[hypothesis]`.

What sets this instance apart: here almost everything can be code, and the
danger moves. The risk is not the role that writes badly, it is the
**instrument that measures wrongly and passes**: the equivalence gate that
never rejects, the benchmark that records the threads requested and not the
threads obtained, the speedup measured at an extreme point and generalized.
The golden rule "measure what the system gave, not what was asked for" becomes
here the first gate of the loop.

## 0. Instantiation table

| Element | In this instance |
| --- | --- |
| Target | a C++ library with a C interface and shared-memory parallelism that replaces the reference implementation of a 3D finite-difference operator, with measured speedup and byte-for-byte identical outputs `[hypothesis: the concrete kernel; holds for any kernel with an oracle]` |
| Owner and owner decisions | the library's technical lead: what to optimize, the speedup target, the extra memory that is acceptable, the approval of new dependencies, the machine-time budget, the release |
| Sources of truth by content type | correctness → oracle (frozen reference implementation and hashed outputs); performance → measurement on a pinned node with the configuration obtained recorded; where the time goes → attribution instrument; API → specification; number in the documentation → CSV of measurements, through a generator |
| Main artifacts | `specification`, `interface`, `oracle`, `attribution-report`, `lever-decision`, `experiment-plan`, `implementation`, `tests`, `build`, `equivalence`, `measurements`, `performance-report`, `documentation` |
| Roles | API architect, oracle keeper, attribution engineer, experiment engineer, implementer, build engineer, documenter, validator, independent reviewer |
| Main gates | byte-for-byte equivalence, independence from order and from the number of threads, sensitivity of the gate itself to mutations, configuration obtained, noise, speedup with confidence interval, size sweep, prediction written beforehand, attribution, sanitizers, floating-point flags, numbers generated from the CSV, reproduction by a third party |
| Independent review rubric | code review and benchmark reproduction by someone who did not implement: correctness, reproduced performance, measurement quality, code, API and documentation, tests, build, honesty of the report |
| Validator verifies | API names across headers, documentation and examples; units and the definition of speedup; compiler, runtime and dependency versions; flags; numbers in the documentation against the CSV; node and threads cited against the CSV |
| Assembly engine | continuous integration that runs, in this order, build, sanitizers, tests, equivalence with sensitivity, configuration check, benchmark on a pinned node, report and documentation generated from the CSV; agents implement modules and write under gate |
| Quick first version | API, oracle, equivalence gate with mutations, benchmark harness, report generator and one trivial lever, end to end, reviewed immediately |
| Round loop | one lever (or one group) per round, with a numeric prediction written beforehand; regressions become gates; false positives fix the instrument; at the end, ablation of the levers |
| Stopping criterion | the owner declares: stop when the speedup passes with its confidence interval, equivalence is total and the review gives accepted, or at the end of the round budget; the ablation and the open notes are recorded |
| Case method document | `library-method.md`: graph, roles with degree, table of levers with gain and ablation, falsified predictions, false positives of the instrument, owner decisions |
| What stays with the human | what to optimize and the target, the acceptable memory, new dependencies, the machine budget, the release; "identical result" is not negotiated within a round |

## 1. Brief

- **Target:** a library that applies a high-order finite-difference operator to
  a 3D volume, replacing the reference implementation, in C++ with a C
  interface and OpenMP `[hypothesis]`.
- **For whom:** the programs that today call the reference; their contract is
  the specification.
- **Non-negotiables**, written as measurable things:
  - outputs byte-for-byte identical to those of the oracle across the whole
    input set, with any number of threads;
  - median speedup ≥ 1.5× at the target size, with the lower bound of the 95%
    confidence interval ≥ 1.3× `[hypothesis: owner's target]`;
  - no size on the measured axis slower than the reference beyond the noise
    floor;
  - no new dependency without approval.
- **Owner decisions:** which levers to try and in which order (after the
  attribution); acceptable extra memory; dependencies; machine-time budget;
  release.
- **Budget:** maximum rounds per artifact = 2 before escalation; one
  independent review per version; up to 4 versions `[hypothesis]`.
- **Non-goals:** porting to GPU; changing the result "for the better" (more
  accurate is also different).

## 2. Initial canon

| Section | Owner | Initial content |
| --- | --- | --- |
| Definitions | experiment engineer | speedup = median wall-clock time of the reference ÷ median of the new code, per size, on the same node; "identical" = equal sha256 of the output files in the declared canonical form; noise floor = coefficient of variation of the reference |
| API names | API architect | prefix, naming convention, public types, error codes |
| Units | experiment engineer | seconds with three significant digits; GB/s and GFLOP/s with the counting formula declared |
| Flags | build engineer | the set of optimization flags; floating-point flags pinned explicitly (FMA contraction and fast math forbidden), identical in the reference and in the new code |
| Environment | build engineer | versions of the compiler, the OpenMP runtime and the dependencies; the list of environment variables that enter each CSV row |
| Pinned node | experiment engineer | how the node is chosen and pinned; the node name enters the CSV as a variable, never a document |
| Input set | oracle keeper | the oracle's cases by class (size, edge, degenerate shape, special values) |
| Terms to avoid | documenter | "faster" without a number and a size; "equivalent" when "identical" is meant |

## 3. Artifacts and graph

| Artifact | Owner | Depends on | Schema | Gates |
| --- | --- | --- | --- | --- |
| `brief` | owner | — | fixed sections of the recipe | approved |
| `canon` | API architect | `brief` | JSON per section, with owner and version | schema |
| `specification` | API architect | `brief`, `canon` | semantics of each function, preconditions and postconditions, canonical output format | reviewed by the owner |
| `interface` | API architect | `specification` | public headers | `h-api` |
| `oracle` | oracle keeper | `specification` | reference implementation frozen by tag, input set, outputs and their sha256 | set covers the canon's classes |
| `attribution-report` | attribution engineer | `oracle`, `canon` | time per region on the target workload, with the unattributed remainder named | `h-attribution` |
| `lever-decision` | owner | `attribution-report` | ordered list of levers with the region each one attacks | recorded |
| `experiment-plan` | experiment engineer | `lever-decision`, `canon`, `specification` | per lever: numeric prediction, result that would refute it, control point, sizes, repetitions, rotated order | `h-prediction` |
| `implementation` | implementer | `interface`, `lever-decision`, `canon` | code per module | code review; `h-sanitizers` via `build` |
| `tests` | implementer | `interface`, `specification` | unit tests per public function | `h-coverage`, `h-sanitizers` |
| `build` | build engineer | `implementation`, `tests`, `canon` | build configuration; binaries by tag; sanitizer build | `h-flags`, `h-warnings`, `h-sanitizers` |
| `equivalence` | oracle keeper | `build`, `oracle` | per case and per number of threads: sha256 obtained and expected; result of the mutations | `h-equivalence`, `h-order-independence`, `h-gate-sensitivity` |
| `measurements` | experiment engineer | `build`, `experiment-plan`, `equivalence` | CSV: one row per run, with tag, size, repetition, order, time, threads requested and obtained, affinity, node, counters with running fraction, peak memory | `h-obtained-configuration`, `h-noise`, `h-counters`, `h-memory` |
| `performance-report` | experiment engineer | `measurements` | generated from the CSV: speedup per size with interval, prediction × result | `h-speedup`, `h-sweep`, `h-generated-numbers` |
| `documentation` | documenter | `interface`, `performance-report`, `canon` | usage guide, API reference; numbers inserted by a generator | `h-generated-numbers` |
| `validation-report` | validator | `canon`, `interface`, `documentation`, `performance-report`, `build` | deterministic report | `h-validation` |
| `independent-review` | independent reviewer | `implementation`, `tests`, `equivalence`, `measurements`, `performance-report`, `documentation`, `validation-report` | rubric report format, with the reproduction | `h-reproduction` |
| `release` | owner | `independent-review` | recorded decision, with the open notes accepted | signed |

The artifact graph:

```text
brief ─> canon ─> specification ─┬─> interface ──────────────┐
                                 └─> oracle ─> attribution-report
                                       │              │
                                       │              v
                                       │     lever-decision (owner)
                                       │          │            │
                                       │          v            v
                                       │  experiment-plan   implementation <─ interface
                                       │          │            │      tests <─ interface
                                       │          │            v        │
                                       │          │          build <────┘
                                       v          │            │
                                  equivalence <───┼────────────┘
                                       │          v
                                       └────> measurements ─> performance-report ─> documentation
                                                                    │
                             validation-report <────────────────────┘
                                       │
                                       v
                              independent-review ─> release
```

Two graph choices that matter:

- `measurements` **depends on** `equivalence`: the performance of a build that
  did not give an identical result is not measured. Fast and wrong does not
  enter the CSV.
- The owner of the `oracle` and of the `equivalence` is not the implementer.
  Whoever writes the code does not write the judge of the code.

## 4. Role cards

### API architect

- **Decides:** the specification, the public interface and the names.
- **Does not decide:** the internal algorithm (implementer); changing the
  output format (a non-negotiable of the brief; only the owner).
- **Inputs:** `brief`.
- **Outputs:** `canon` (his or her sections), `specification`, `interface`.
- **Exit gate:** `h-api`.
- **Notes it emits:** to the `implementation`, when a public symbol diverges
  from the specification (`high`).
- **Code-conversion degree:** (b) the symbol comparison is code; specifying is
  human or a reviewed agent.

### Oracle keeper

- **Decides:** the input set, the canonical form of comparison and the
  mutations the gate has to catch.
- **Does not decide:** relaxing the comparison to "approximately equal" (the
  brief forbids it); changing the library code.
- **Inputs:** `specification`, `build`.
- **Outputs:** `oracle`, `equivalence`.
- **Exit gate:** `h-equivalence`, `h-order-independence`,
  `h-gate-sensitivity`.
- **Notes it emits:** to the `implementation`, per case with a different hash,
  with the first divergent index and value as evidence (`blocking`).
- **Code-conversion degree:** (a) comparison, mutations and the thread sweep
  are code; the keeper decides the input classes.

### Attribution engineer

- **Decides:** how to instrument and what counts as a region.
- **Does not decide:** what to optimize (owner); the size of the acceptable
  remainder (gate).
- **Inputs:** `oracle`, `canon`.
- **Outputs:** `attribution-report`.
- **Exit gate:** `h-attribution`.
- **Notes it emits:** to the `lever-decision`, when a proposed lever attacks a
  region with a small fraction of the time (`medium`).
- **Code-conversion degree:** (b) collection and summation are code; choosing
  the regions is human.

### Experiment engineer

- **Decides:** the design of each measurement (points, repetitions, order,
  control) and the analysis.
- **Does not decide:** the speedup target (owner); running on a node that is
  not pinned.
- **Inputs:** `lever-decision`, `canon`, `specification`, `build`,
  `equivalence`.
- **Outputs:** `experiment-plan`, `measurements`, `performance-report`.
- **Exit gate:** `h-prediction`, `h-obtained-configuration`, `h-noise`,
  `h-counters`, `h-memory`, `h-speedup`, `h-sweep`.
- **Notes it emits:** to the `implementation`, when the lever did not deliver
  what was predicted (`medium`, with the prediction and the measured value); to
  `measurements`, when the configuration obtained diverges from the requested
  one (tool failure, redo).
- **Code-conversion degree:** (a) execution, CSV and report are code; writing
  the prediction is human or an agent under gate.

### Implementer

- **Decides:** how to implement each approved lever.
- **Does not decide:** which levers (owner); the interface (architect); the
  oracle (keeper).
- **Inputs:** `interface`, `lever-decision`, `canon`.
- **Outputs:** `implementation`, `tests`.
- **Exit gate:** `h-coverage`, `h-sanitizers`; and, downstream,
  `h-equivalence`.
- **Notes it emits:** to the `specification`, when an edge case is not
  specified (`high`).
- **Code-conversion degree:** (c) an agent or a person under gate; almost the
  whole gate is code.

### Build engineer

- **Decides:** the build configuration and the continuous integration.
- **Does not decide:** changing the canon's floating-point flags.
- **Inputs:** `implementation`, `tests`, `canon`.
- **Outputs:** `build`.
- **Exit gate:** `h-flags`, `h-warnings`, `h-sanitizers`.
- **Notes it emits:** to the `implementation`, per warning or sanitizer error
  (`high`).
- **Code-conversion degree:** (a).

### Documenter

- **Decides:** the structure and the text of the documentation.
- **Does not decide:** any number (it comes from the CSV through a generator).
- **Inputs:** `interface`, `performance-report`, `canon`.
- **Outputs:** `documentation`.
- **Exit gate:** `h-generated-numbers`.
- **Notes it emits:** to the `interface`, when a symbol has no contract
  comment (`low`).
- **Code-conversion degree:** (b) numbers and API reference generated; the
  guide is an agent under gate.

### Validator

- **Decides:** nothing outside the rules it executes.
- **Does not decide:** whether a note of its own is a false positive.
- **Inputs:** `canon`, `interface`, `documentation`, `performance-report`,
  `build`.
- **Outputs:** `validation-report`.
- **Exit gate:** identical report in two executions.
- **Notes it emits:** those of section 7.
- **Code-conversion degree:** (a).

### Independent reviewer

- **Decides:** the scores per dimension, the severity and, when reproducing,
  whether the published number holds up.
- **Does not decide:** the rubric; what gets fixed; the release.
- **Inputs:** the artifacts in the table, without access to the production
  conversations.
- **Outputs:** `independent-review`.
- **Exit gate:** `h-reproduction`; report in the rubric format.
- **Notes it emits:** to any artifact of the graph.
- **Code-conversion degree:** (c) an agent or a person who did not implement,
  with the benchmark harness to reproduce.

## 5. Gates

The order matters: the configuration obtained is checked **before** the
correctness and performance gates, because correct but serial work passes
every result test.

| Gate | Artifact | Magnitude | Limit | Justification |
| --- | --- | --- | --- | --- |
| `h-equivalence` | `equivalence` | cases whose sha256 of the canonical output differs from the oracle | 0 out of at least 60 cases | [brief] identical result is non-negotiable; 60 cases cover the canon's classes with room to spare [hypothesis] |
| `h-order-independence` | `equivalence` | distinct hashes across runs with 1, 2, 4 and the maximum number of threads and with different schedules | 1 hash per case | [method] parallelism may change how, never what; a reduction in non-fixed order changes the rounding |
| `h-gate-sensitivity` | `equivalence` | known mutations (a least significant bit flipped, an edge point omitted, one time step fewer) that the gate lets pass | 0 | [method] a gate that never rejects proves nothing; it is the signal gate in its most dangerous form |
| `h-obtained-configuration` | `measurements` | CSV rows with threads obtained different from those requested, affinity different from the declared one or a node different from the pinned one | 0; otherwise the measurement is invalid (tool failure, not rejection) | [method] publish what the system gave: the number of threads requested is a request, and in a nested region it can become one |
| `h-noise` | `measurements` | coefficient of variation of the reference time across repetitions, per size | ≤ 3% | [hypothesis] on a dedicated, pinned node it is attainable; with more noise, a speedup of 1.5 with a tight confidence interval becomes indistinguishable |
| `h-speedup` | `performance-report` | ratio of medians at the target size; lower bound of the 95% confidence interval by resampling | median ≥ 1.5; lower bound ≥ 1.3 | [brief] owner's target [hypothesis: illustrative value]; the interval keeps a lucky median from passing |
| `h-sweep` | `performance-report` | sizes measured on the problem axis; sizes slower than the reference beyond the noise floor | ≥ 5 sizes covering cache and memory; 0 slower | [method] measuring only the extreme point holds only for that point; the regression tends to live at the small size |
| `h-prediction` | `experiment-plan` | levers measured without a numeric prediction written beforehand and without the result that would refute it | 0 | [method] a prediction written afterwards is always right; without possible refutation the measurement decides nothing |
| `h-counters` | `measurements` | hardware counters published with a running-time fraction below 100% | 0 | [hypothesis] a multiplexed counter is an estimate scaled by the kernel, not a measurement; publish only what was fully counted |
| `h-attribution` | `attribution-report` | fraction of wall-clock time not attributed to any region | ≤ 10%, named as "unattributed" | [hypothesis] above that, choosing levers is guessing; naming the remainder keeps anyone from explaining it without measuring |
| `h-memory` | `measurements` | peak resident memory of the new code ÷ reference | ≤ 1.10 | [hypothesis] the owner accepts little extra spending; the magnitude forces declaring the cost of each lever that trades memory for time |
| `h-sanitizers` | `build`, `tests` | address and undefined-behavior errors in the suite; data races detected | 0 | [method] with undefined behavior, result identity is an accident and vanishes with the next compiler version |
| `h-warnings` | `build` | compiler warnings in the new code with the canon's warning set | 0 | [hypothesis] the warning set is a project choice; zero is cheap in new code and expensive to recover later |
| `h-flags` | `build` | differences between the effective floating-point flags (read from the binary or from the compile log) and those of the canon | 0 | [method] FMA contraction and reassociation change the rounding; identical result requires fixed flags, equal to the reference's |
| `h-coverage` | `tests` | line coverage of the new code; public functions without a test | ≥ 85%; 0 | [hypothesis] line coverage is a coarse floor; the public function without a test is the gap that matters |
| `h-api` | `interface` | public symbols different from the specification | 0 | [method] the contract of the calling programs is the specification; an undeclared new symbol is a silent change |
| `h-generated-numbers` | `performance-report`, `documentation` | performance numbers in the text that were not inserted by the generator from the CSV | 0 | [method] the number never comes from the writer; the generator is the only source of performance in the text |
| `h-reproduction` | `independent-review` | relative difference between the speedup reproduced by the reviewer and the published one, on the same type of pinned node | ≤ 10% | [hypothesis] nodes of the same model vary by a few percent; above that, the published number depends on something undeclared |
| `h-validation` | `validation-report` | open high and blocking notes from the validator | 0 to release | [method] a compiler version or flag that differs between document and CSV invalidates the comparison |

Every code gate goes through the gate sensitivity test before it counts, and
`h-gate-sensitivity` is that test turned into a permanent gate.

## 6. Independent review rubric

Code review and benchmark reproduction by someone who did not implement,
supported by the harness. Frozen by hash before the review of v1.

| Dimension | What is measured | 1 | 3 | 5 |
| --- | --- | --- | --- | --- |
| Correctness | total equivalence, thread independence, sensitivity of the gate | equivalence not proven | proven, without sensitivity | proven, with mutations caught |
| Reproduced performance | the reviewer reproduces the speedup | does not reproduce | reproduces outside 10% | reproduces within 10% |
| Measurement quality | prediction beforehand, control, noise, configuration obtained, sweep | measurement without a design | design with gaps | complete design |
| Code | readability, resource management, absence of hidden state | unreadable or fragile | acceptable | clear and robust |
| API and documentation | coherence with the specification, examples | divergent | coherent, documentation partial | coherent and documented |
| Tests | behavior, edges, regressions | absent | present, edges partial | complete |
| Build | flags, warnings, sanitizers, reproducibility | not reproducible | reproducible with manual steps | reproducible by one command |
| Report honesty | claims limited to the points measured; unattributed remainder named; falsified predictions recorded | generalizes beyond what was measured | limits partly declared | all limits declared |

Severity: `blocking` for any non-identical case and for a speedup that was not
reproduced; `high` for a measurement without the configuration obtained or
without a prediction; `medium` for divergent documentation; `low` for style.

Verdict by the mechanical rule (the same as the "Verdict rule" template of the
recipe): `rejected` if there is a blocking finding or any dimension scored
≤ 2; `accepted` if there is no high finding and all dimensions scored ≥ 4;
otherwise, `accepted with conditions`.

## 7. Validator

| Verifies | Against | Severity | Note to |
| --- | --- | --- | --- |
| function, type and error-code names | `interface` × documentation × examples | `high` | documenter or API architect |
| definition of speedup and units | the "definitions" and "units" sections | `high` | owner of the document |
| versions of compiler, runtime and dependencies | "environment" section × build log × CSV header × report | `blocking` if the report cites a version the CSV does not have | experiment engineer |
| flags | "flags" section × build log | `blocking` | build engineer |
| performance numbers in the text | CSV, by the generator's identifier | `blocking` if it did not come from the generator | documenter |
| node and threads cited in the report | CSV columns | `high` | experiment engineer |
| terms to avoid | "terms to avoid" section | `medium` | documenter |

## 8. Assembly engine

Here the engine is continuous integration, and the order is part of the
contract:

```text
for each candidate tag:
    normal build and sanitizer build                 # h-flags, h-warnings
    unit tests under sanitizers                      # h-sanitizers, h-coverage
    equivalence: all cases × {1, 2, 4, P} threads × schedules
    known mutations against the equivalence gate     # h-gate-sensitivity
    if any case is not identical: blocking note to the implementation; stop
    benchmark on the pinned node, rotated order (ABAB...), repetitions of the plan
        each CSV row: threads obtained, affinity, node, counters, memory
    h-obtained-configuration before any analysis     # invalid = tool failure
    report generated from the CSV; documentation with the generator's numbers
    validator
```

| Part | Code | Agent under gate | Human |
| --- | --- | --- | --- |
| Correctness | equivalence, mutations, thread sweep | — | chooses input classes |
| Performance | benchmark, CSV, confidence interval, report | — | writes predictions, decides levers |
| Implementation | build, sanitizers, coverage | implements modules | reviews |
| Documentation | numbers and API reference generated | writes the guide | approves |
| Notes | routes, deduplicates, escalates | — | replies |

## 9. Quick first version

In a few days `[hypothesis]`: the interface; the oracle with the input set; the
equivalence gate with the mutations; the benchmark harness with the complete
CSV; the report generator; and **one** trivial lever (for example, the loop
order). Immediate independent review.

The goal is to validate the instruments before optimizing: does the gate catch
the mutations? Does the CSV record the threads obtained? Does the noise allow
seeing 1.5×? Does the input set catch the edges? A v1 that only discovers that
the noise is 8% has already paid for what it cost.

## 10. Round loop

Each round applies one lever or a small group, each with the prediction
written in the `experiment-plan` before the measurement. Examples of what the
loop does here:

- **False positive, fixed at the root:** equivalence rejects because the
  output file carries the execution time in its header. The fix is neither to
  compare "almost equal" nor to ignore the whole header; it is to take the
  time out of the format (or to declare in the specification the canonical
  form that excludes only that field), with a test, and to redo the previous
  round. The reference case did the same when it took the timestamp field of
  its JSON files out of the hash (section 1.2 of the reference-case method
  document) [prior:000-av-production].
- **Regression that escaped:** the measurements with 8 and 16 threads give the
  same time. The cause is a nested parallel region that runs with one thread,
  and every result gate passes, because the serial work is correct. Before
  fixing it, `h-obtained-configuration` is born, which rejects the current
  version; only then is the region fixed (divide by the number of threads the
  runtime gave, or use a worksharing loop).
- **Instrument fixed:** a hardware counter published with a running fraction
  below 100% gives a cache-miss rate inconsistent with the time. The fix is to
  measure fewer counters per run, not to "adjust" the value; `h-counters` is
  born.
- **Ablation at the end:** accumulated gain is not current worth. At the end,
  each lever is removed one at a time and measured again; the one that no
  longer pays for what it costs in complexity goes out, by the owner's
  decision.

## 11. Stopping criterion

Declared by the owner before the last round: stop when `h-speedup` passes with
the confidence interval, equivalence is total and the independent review gives
`accepted`, or at the end of four versions `[hypothesis]`, whatever the
verdict. The ablation goes into the final report. `low` and `medium` notes
become open notes. A non-identical case never becomes an open note: it is a
target not delivered.

## 12. Case method document

`library-method.md`, with: the graph; per role, the pseudocode and the
code-conversion degree; the table of levers with prediction, result, gain and
ablation; the falsified predictions and what they taught; the false positives
of the instruments and the fix for each; the oracle's input set and why each
class exists; the owner decisions; the stopping criterion as applied.

## 13. What stays with the human

- What to optimize and the speedup target.
- The acceptable extra memory.
- The approval of new dependencies.
- The machine-time budget and where to measure.
- The decision to keep or remove a lever after the ablation.
- The release.

"Identical result" is non-negotiable in the brief: no round relaxes it, and if
it ever has to be relaxed, that is a new brief, decided by the owner.
