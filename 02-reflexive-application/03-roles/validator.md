# Role card: validator

Reads all the documents against the canon and against their neighbors and
emits notes by itself. Terms follow the [canon](../01-canon.md).

**Mission.** That no term, number, or artifact or role name diverges between
documents, and that every form, size and anonymity gate is measured, not
eyeballed.

**Decides:** nothing beyond the rules it executes. It applies the canon's
lists and the limits of `04-gates-and-rubric.md` and returns the magnitude of
each gate.

**Does not decide:**

- whether a note of its own is a false positive: that belongs to the
  verifier;
- limits and lists: it reads them from the canon and from the gates, and has
  no copy of its own;
- the text: it only emits notes.

**Inputs:** all the `.md` files in the folder, `01-canon.md` (tables),
`04-gates-and-rubric.md` (size limits and the "Rubric" section), the case
method document (passed as a command-line argument, to check the
`[prior:...]` numbers), the instance registry (`../instances/registry.json`,
found by default) and a list of forbidden identifiers (passed as an argument,
kept out of the material so that it does not contain what it forbids; this
corpus has none, so that part of `p-anonymity` is pending and accepted by
name).

**Outputs:** `80-validator/report.md`, deterministic: no date, with
relative paths, sorted by document and by gate.

**Exit gate:** `m-determinism` (two runs, same report). The exit code is 0
when every gate was measured (or its pending accepted by name with
`--allow-pending`) and no note is high or blocking, 1 with such a note, 2
with invalid input (canon without the tables, missing document, truncated
table row, a gate it does not implement), 4 with a pending gate the call
did not accept.

**Notes it emits:**

- to the document, for a term to avoid, absolute path, date or forbidden
  identifier, HTML tag, block that is not `text`, size outside the range
  (`high`);
- to the instance, for a missing or empty row of the instantiation table, a
  missing mandatory section, a missing role card field, a gate without a
  limit, a justification without a tag, an artifact cited but not declared, an
  owner that is not a role, a cycle in the graph (`high`; a cycle is
  `blocking`);
- to the document, for a `[prior:...]` number absent from the prior's method
  document (`blocking`);
- to the `review`, if the "Rubric" section changed after being frozen
  (`blocking`).

**Code-conversion degree:** (a) converted. It is the script
`80-validator/validator.py`; the person or the model only
decides the contestations.

**Base prompt.**

```text
Run: python 80-validator/validator.py --folder . \
        --case PRIOR_000_DOCUMENT_PATH \
        --case ../instances/004-adoption-guide/metodo-de-producao.md \
        --rubric-hash 90-review/rubric.sha256 --notes 90-review/notes.json \
        --allow-pending p-anonymity
Read the report. Forward each note to the owner of the target artifact.
An exit 4 names a gate that was not measured: supply its input or accept
it by name, never read it as a pass.
```
