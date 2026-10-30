# Templates

Copy a block, replace the angle-bracket placeholders, delete the guidance
lines. Keep pseudocode in fenced blocks marked `text`, plain Markdown only.

## 00-brief.md

```text
# Brief: <target name>

Target: <what is delivered, one sentence>
Audience: <who uses it>

## Non-negotiables
- <constraint that no role may trade away>

## Owner decisions
| Decision | Status | Blocks |
| --- | --- | --- |
| <decision only the owner can take> | open | <artifact that depends on it> |

## Budget and stopping criterion
- Maximum rounds per artifact: <n>
- Stop when: <condition declared before the last round; the review then becomes a list of open notes>
```

## 01-sources-of-truth.md

```text
# Sources of truth: <target name>

| Content type | Source that errs least | Who consults it | Forbidden as a source |
| --- | --- | --- | --- |
| fact | <primary source> | <role> | the writer; a generative tool |
| number | <instrument or canon> | <role> | the prose that cites it |
| exact text | <original or the engine> | <role> | a generative tool |
```

## 02-canon.json

The canon of the target as data. Numbers, variants, names and rules — no
method-vocabulary sections (those belong to the corpus of the method).

```text
{
  "target": "<target name>",
  "version": "v1",
  "sections": [
    { "name": "canonical numbers", "owner": "<role>", "version": "v1", "state": "pending" },
    { "name": "accepted variants", "owner": "<role>", "version": "v1", "state": "pending" },
    { "name": "names and terms", "owner": "<role>", "version": "v1", "state": "pending" },
    { "name": "rules", "owner": "<role>", "version": "v1", "state": "pending" }
  ],
  "canonical numbers": [
    { "value": null, "unit": null,
      "spelling": { "table": "", "prose": "", "code": "" },
      "nature": "fact or hypothesis", "source": "" }
  ],
  "accepted variants": [ { "variant": "", "holds where": "", "why": "" } ],
  "names and terms": [ { "name": "", "prefer": "", "gloss marker": "" } ],
  "rules": [],
  "recorded facts": [
    { "number": "<number as written>",
      "context": "<what it counts> [prior:<id>]",
      "section": "<section label(s) of that prior's method document>" }
  ]
}
```

The scaffold also writes the lists the validator consumes (terms to avoid,
fixed lists, triggers), empty. "recorded facts" holds one object per number
the cell states about a registered prior; a prior number without its row
fails `p-prior`.

## 03-artifacts.json

```text
[
  { "name": "<artifact>", "owner": "<role or owner>", "paths": ["<relative path>"],
    "depends_on": ["<names>"], "schema": null,
    "command": null, "gates": ["<gate ids>"],
    "resource": "code | agent | human | machine", "proposed": false }
]
```

Graph (must be acyclic):
  <artifact> -> <artifact>

## 04-roles/<role>.md

The fields are bold labels, the form the gate `p-card` reads (the scaffold
writes the same form); a field that still holds an angle-bracket
placeholder fails the gate.

```text
# Role card: <role>

Canon: [02-canon.json](../02-canon.json)

**Decides:**

- <what this role settles alone>

**Does not decide:**

- <what it must escalate or leave to another role>

**Inputs:**

- <artifacts it reads>

**Outputs:**

- <artifacts it writes>

**Exit gate:**

- <gate ids that its output must pass>

**Notes it emits:**

- <typical notes: target artifact and severity>

**Code-conversion degree:**

- <(a) converted, (b) partial under gate or (c) contract and gate only>; executor: <a person, code, or a model named by family and effort; the reviewer's executor differs from the producer's>
```

## 05-contracts/<artifact>.schema.json

```text
<JSON Schema of the artifact; rejects unknown fields and ambiguous values.
Write one valid example and one invalid example, and confirm the schema
rejects the invalid one.>
```

## 06-gates.md

```text
# Gates: <target name>

| Gate | Artifact | Magnitude | Limit | Justification |
| --- | --- | --- | --- | --- |
| <gate id the validator implements> | <artifact> | <measured value and unit> | <threshold> | [method|brief|hypothesis] <at least six words saying where the number comes from and why not another> |

### Size ranges

| Document | Minimum | Maximum |
| --- | --- | --- |
| <document> | <words> | <words> |
```

The Gates column of `03-artifacts.json` assigns the gates; this table
mirrors it, one row per gate, and the validator reports a gate assigned
there with no row here. A gate of the target's domain (a speedup, a mass)
is not one the validator implements: it is "contract + agent" or the
cell's own code. The validator reads the minimum words of `p-limit`
("fewer than N words" in its magnitude) and the minimum steps of
`p-recipe` ("≥ N steps" in its limit) from their rows.

## 07-rubric.md

```text
# Rubric: <target name>

Frozen before the first review; its sha256 is stored in 07-rubric.sha256.

## Dimensions
| Dimension | What is measured | 1 | 3 | 5 |
| --- | --- | --- | --- | --- |
| D1 <name> | <measurable statement> | <failing anchor> | <middling anchor> | <passing anchor> |

## Finding severity
| Severity | When |
| --- | --- |
| blocking | <defect that invalidates the target> |
| high | <gap that stops a role from executing a step> |
| medium | <imprecision without a hypothesis mark> |
| low | <style, local readability> |

## Verdict rule
Mechanical, applied to scores and findings:

if any blocking finding or any dimension scores <= 2: verdict = rejected
else if no high finding and every dimension >= 4: verdict = accepted
else: verdict = accepted with conditions

## Report format
1. Verdict with the rule applied. 2. Scores per dimension with evidence.
3. Findings by severity (target artifact, severity, text, evidence).
4. Verified and correct. 5. Not verified, and why. 6. Out of scope.
7. Notes as JSON.
```

## Note (JSON)

The only change request between roles. Six fields, all required.

```text
{
  "target_artifact": "<artifact name from 03-artifacts.json>",
  "severity": "low | medium | high | blocking",
  "text": "<what is wrong and what to do>",
  "origin": "<role or instrument that emitted it>",
  "evidence": "<file and excerpt or measured magnitude>",
  "round": "<round, e.g. v1>"
}
```

Optional fields carry its state: `status` (`open`, `fixed`, `disputed`,
`out of scope`) and `closed_in` (the version that closed it). The state of
a note in a ledger that is never edited goes to `state/notes-status.jsonl`,
one line per note: `{"ref": "notes:<n>", "status": "...", "closed_in":
"...", "summary": "..."}`.

Only `high` and `blocking` return the artifact to its owner. Aim at the
artifact where the defect was born, not where it was seen.

## 08-validator/perturbations.json

The cell's sensitivity test, as data: each object injects one known defect
into a copy of the cell, and the named gate has to fail on the named
document. The scaffold writes three generic ones; adapt their text to the
cell and add one per gate the cell assigns: a gate the artifact list
assigns without a perturbation leaves `p-sensitivity` pending, with the
gate named, never passing.

```text
[
  { "name": "<unique name>", "document": "<path in the cell>",
    "old": "<text that exists once>", "new": "<the defect>",
    "gate": "<gate id>" }
]
```

Optional keys: `expect` (`fail`, or `pending` for a defect that empties
what the gate reads), `delete` (remove the document instead), and
`needs_case`, `needs_rubric_hash`, `needs_notes`, `needs_registry` (the
input without which the row is not measured).

## priors.json

```text
{
  "instances": [
    { "id": "<id>", "status": "executed | designed",
      "document": "<method document path, relative to its own repository root>",
      "sha256": "<hash that pins the document>",
      "locator": "<path relative to this material, or owner-held, not distributable>",
      "number_format": "point-decimal | comma-decimal",
      "method_version": "<optional: the method version it ran under>" }
  ]
}
```

An executed entry carries all four of document, sha256, locator and
number_format; a designed entry keeps the four null or absent until it runs.
The validator checks this contract by status.

## Round-loop pseudocode

```text
compile(graph, brief, corpus):
    canon = extract(brief, corpus)
    repeat:
        for artifact in topological order:
            if inputs changed (hash) or a high/blocking note targets it:
                output = owner.produce(inputs, canon, open_notes)
                for gate in artifact.gates:
                    magnitude = gate(output)
                    if fails: emit note(artifact, severity, magnitude); return to owner
                validator.verify(output, canon)
        product = assemble(final artifacts)
        review = independent_reviewer(product, frozen_rubric)
        for finding in review:
            if instrument defect: fix the instrument at the root
            elif regression no gate caught: add the gate, then fix
            else: note to the artifact of origin
        if stopping criterion: record open notes and exit
```
