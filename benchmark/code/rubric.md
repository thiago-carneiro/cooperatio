# Rubric

## 1. Scoring dimensions

Each dimension is scored 1–5. Anchors are written for 1, 3 and 5; scores 2 and 4 are intermediate.

### D1. Correctness

- **1:** The code produces wrong results or crashes on ordinary inputs; logic errors are evident from reading; no evidence the author checked behaviour.
- **3:** The main path appears correct, but edge cases (empty input, boundaries, error returns, concurrency, integer overflow, encoding) are unhandled or demonstrably wrong.
- **5:** Behaviour is correct on ordinary and edge inputs; preconditions and failure modes are handled explicitly; the code does what its contract (name, doc, callers) says, and this is verifiable from the source.

### D2. Error handling and failure modes

- **1:** Errors are swallowed, ignored, or reported only by aborting/printing; resource leaks on failure; callers cannot distinguish success from failure.
- **3:** Errors are propagated, but inconsistently or with lost context; some failure paths leak or leave partial state.
- **5:** Every fallible operation's failure is handled at a deliberate level, with context preserved; resources are released on all paths; invariants held after failure are stated and preserved.

### D3. Design and structure

- **1:** Responsibilities are tangled; global state or hidden coupling; the subsystem cannot be understood without reading everything at once; abstraction boundaries are absent or wrong.
- **3:** A reasonable decomposition exists but has leaks: over-broad interfaces, duplicated logic, or layering violations that will impede change.
- **5:** Clear boundaries and single responsibilities; dependencies point one way; public surface is minimal and sufficient; the structure makes the intended use obvious and foreseeable changes local.

### D4. Readability and naming

- **1:** Names are misleading or meaningless; control flow is hard to follow; comments contradict the code or explain nothing.
- **3:** Generally readable, but with misleading names, dense or deeply nested passages, or comments that restate code instead of explaining intent.
- **5:** Names state intent; functions are short and control flow is linear; comments explain *why*, not *what*; a competent stranger can follow the code without external help.

### D5. Robustness and safety

- **1:** Crashes or corrupts state on plausible misuse; unchecked external input; no bounds/type/encoding discipline.
- **3:** Some defensive checks, but coverage is uneven; misuse fails late or confusingly rather than at the boundary.
- **5:** Inputs are validated at trust boundaries; invariants are enforced where they can be broken; misuse fails early with a clear diagnosis; no undefined or unspecified behaviour on realistic inputs.

### D6. Testability and evidence of verification

- **1:** Code is structured so it cannot be exercised in isolation (hidden dependencies, I/O in the middle of logic); no tests or checks accompany the subsystem.
- **3:** Core logic is testable but seams are awkward; some tests exist but miss the edge cases the code itself admits.
- **5:** Logic is separable from I/O and environment; tests or executable checks cover the main path, the edge cases and the failure paths identified in D1/D2.

### D7. Maintainability and change cost

- **1:** Magic values, copy-pasted blocks, hidden assumptions; any change requires touching many places or risks silent breakage.
- **3:** Tolerable, but with duplication, unclear ownership of constants, or coupling that makes targeted changes risky.
- **5:** Constants and policies are named in one place; duplication is absent or intentional; changes are local and their consequences are visible from the code.

### D8. Documentation (in-code and interface)

- **1:** Public interface is undocumented; preconditions, units, ownership and error semantics are guessable only.
- **3:** Public interface is documented, but key invariants, units or error semantics are missing or stale.
- **5:** Public surface documents contract, preconditions, units, ownership and failure behaviour; non-obvious decisions are justified; documentation matches the code.

## 2. Severity scale of findings

- **Low:** Cosmetic or stylistic defect: naming, formatting, redundant code, comment wording. No effect on behaviour or on the cost of change.
- **Medium:** Local defect with limited blast radius: a missed edge case in a narrow path, duplicated logic, a stale comment, an awkward but correct abstraction. Behaviour is currently correct on the main path.
- **High:** Defect that produces wrong behaviour, a resource leak, a crash, or a security/safety weakness on a realistic input or failure path; or a structural defect that makes a foreseeable change risky or forces wide edits.
- **Blocking:** The subsystem cannot be accepted as-is: wrong results on ordinary inputs, data corruption or loss, a security vulnerability reachable from untrusted input, undefined behaviour on a normal path, or a defect that makes the code unreviewable (e.g. the stated contract cannot be met by the implementation at all).

## 3. Verdict rule (mechanical)

- If any **blocking** finding exists, **or** any dimension has a score of **at most 2** → **rejected**.
- Else if there is **no high** finding **and** every dimension has a score of **at least 4** → **accepted**.
- Else → **accepted with conditions**.

## 4. Report format

1. **Summary** — one paragraph: what the subsystem does, overall impression, verdict.
2. **Dimension scores** — table: dimension, score (1–5), one-line justification per dimension.
3. **Findings** — numbered list; each finding states: severity (low/medium/high/blocking), location (file and line/function/symbol), the defect, and the evidence in the code (quoted snippet or precise reference). Ordered by severity, blocking first.
4. **Conditions** (only for "accepted with conditions") — the findings that must be fixed for acceptance, each mapped to its finding number and to the dimension it affects.
5. **Verdict** — exactly one of: `rejected`, `accepted with conditions`, `accepted`, with the rule instantiation (which clause fired).
6. **Out of scope / open questions** — anything the reviewer could not judge from the provided sources, and why.