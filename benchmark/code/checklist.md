# Review checklist

## Scope and inventory

- Confirm the subsystem boundary matches the files actually delivered: list every file, map each to a responsibility, and flag files that are dead, duplicated, vendored, or generated without a note saying so.
- Identify the public surface (exported symbols, entry points, command-line flags, configuration keys) and check that everything intended to be private is actually unreachable from outside.
- Note the language(s), build system, and dependency manifest versions; verify the code compiles or parses as delivered, and that no source file is truncated or stale relative to its siblings.
- Check that every file has a clear ownership/purpose signal: header comment, module docstring, or naming that matches its directory.

## Correctness: control flow and data

- Trace each public entry point end to end; confirm every return path yields a value of the documented type, including early returns, exceptions, and fall-through branches.
- Look for off-by-one errors in every loop bound, slice, index, and range: check `<` vs `<=`, inclusive vs exclusive intervals, and whether the boundary element is handled.
- Verify null/None/nil/empty handling at each boundary: function arguments, parsed input, query results, environment variables, and optional fields.
- Check comparison and equality logic for type coercion, case sensitivity, locale, and floating-point equality; flag `==` on floats or on objects without defined equality.
- Inspect integer arithmetic for overflow, underflow, division by zero, truncation, and negative-modulo behavior; inspect float arithmetic for NaN propagation and precision loss in money or counts.
- Confirm resource lifetimes: files, sockets, locks, transactions, and iterators are closed/released on every path, including exceptions; look for missing `finally`/`defer`/context-manager equivalents.
- Check concurrency: shared mutable state, missing synchronization, lock ordering, and whether callbacks or signals can re-enter the same object.
- Verify error handling does not swallow failures silently: every caught exception is either handled, wrapped with context, or re-raised; flag bare or broad catches with empty bodies.
- Check that errors carry enough context to diagnose (operation, input, cause) and that success/failure is distinguishable by the caller, not just by log output.

## Input, parsing, and boundaries

- Audit every place external data enters: files, network, argv, env, deserialization. Confirm validation happens before use, and that malformed input produces a defined error rather than a crash or silent default.
- Check deserialization for untrusted input: type confusion, oversized payloads, deeply nested structures, and unsafe defaults (e.g., eval-like loaders, permissive YAML).
- Verify path handling: joins, traversal (`..`), absolute vs relative, symlinks, and encoding; confirm user-supplied paths cannot escape an intended root.
- Check string handling for encoding assumptions, normalization, splitting on ambiguous delimiters, and Unicode length vs byte length mismatches.
- Confirm any shell/command/SQL/template construction uses parameterization or escaping rather than concatenation.

## Design and structure

- Assess cohesion: does each module do one thing, and is that thing named accurately? Flag functions that mix I/O, validation, business logic, and formatting.
- Check coupling: count cross-module imports and flag cycles, hidden global state, and modules reaching into each other's internals.
- Verify abstraction levels are consistent: a high-level function should not drop into byte manipulation without a named helper; a low-level helper should not call back into application policy.
- Look for duplicated logic that will drift (validation rules, retry policies, magic constants) and confirm shared constants live in one place.
- Check that extension points (hooks, interfaces, subclass seams) are minimal and documented; flag speculative generality with a single caller.
- Confirm error and logging strategy is uniform across the subsystem rather than per-file improvisation.

## Maintainability and readability

- Check naming: booleans read as predicates, functions as verbs, units encoded in names (`_ms`, `_bytes`), and no misleading names (a `get_` that mutates).
- Flag magic numbers and strings; confirm each has a named constant or a comment explaining the value.
- Look for commented-out code, TODOs without owners, and debug prints left in production paths.
- Verify comments explain *why*, not *what*; flag comments that contradict the code.
- Check function length and nesting depth against team norms; flag deeply nested conditionals that invert into guard clauses.
- Confirm the subsystem's tests exist and cover the risky paths identified above: boundaries, errors, empty input, concurrency. Note untested public functions by name.

## Performance and resources

- Identify hot paths and check for accidental quadratic behavior (nested scans, repeated `in` on lists, string concatenation in loops, N+1 queries).
- Check that expensive work is not repeated per iteration when it could be hoisted, and that caches have bounds and invalidation.
- Verify batch sizes, buffer sizes, and timeouts are configurable and have sane defaults.
- Flag unbounded growth: caches, queues, log buffers, and collections that accumulate per request.

## Security and safety

- Check trust boundaries: anything from outside the process is untrusted, including config files, plugin names, and environment variables.
- Verify secrets are not logged, embedded in error messages, or committed; check for hardcoded credentials and permissive file modes.
- Review deserialization, subprocess invocation, and dynamic import for injection.
- Confirm fail-closed behavior: an authentication, permission, or validation error must deny, not proceed with defaults.

## Reporting

- For each defect, record file, line or symbol, the triggering condition, and the evidence in the code; distinguish confirmed defects from suspicions and style preferences.
- Rank by severity (correctness/security first, then design, then style) and state the smallest fix that resolves each.