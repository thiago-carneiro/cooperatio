# Review checklist for a set of teamwork files

Use before handing the files over, and as a reviewer's starting list. Each item
is checkable; "looks fine" is not a result.

## Structure
- [ ] Every file in the set points to the canon (the canon itself excepted).
- [ ] The artifact graph is acyclic; every dependency names a declared artifact.
- [ ] Every artifact has exactly one owner, and the owner is a role or the owner of the target.
- [ ] Every owner decision is a named artifact and the artifacts that depend on it say so.
- [ ] Every role card has all seven fields filled in; none is empty or generic.
- [ ] A role with neither an exit gate nor a note it emits was demoted to a step.

## Gates
- [ ] Every gate returns a magnitude, not only pass/fail.
- [ ] Every limit has a justification of at least six words and an origin label.
- [ ] No signal-only gate ("exists", "greater than zero") remains without a magnitude limit.
- [ ] A tool that does not run is reported as a tool failure, never as pass or fail.
- [ ] Each gate has a sensitivity case: a known defect injected on purpose that it must reject.
- [ ] The sensitivity report was regenerated after the last change to the validator, the gates file or the canon.
- [ ] The gate table has one row per gate the artifact list assigns, naming the same artifacts.
- [ ] No field, gate row or artifact record still holds a placeholder (`<...>`, TBD, TODO).
- [ ] The validator exits 0; any pending gate it reports is accepted by name, with the reason, never read as a pass.
- [ ] No limit was loosened to make a finding go away.

## Contracts
- [ ] Every artifact consumed by another role has a schema or is marked "free text" with what is missing.
- [ ] Each schema has one valid and one invalid example, and rejects the invalid one.
- [ ] Every position key is unique at the moment of assembly.

## Rubric and review
- [ ] The rubric was written and hashed before the first review; the hash is stored.
- [ ] Each dimension has anchors for 1, 3 and 5 that two reviewers would read the same way.
- [ ] The verdict rule is mechanical and has three values (rejected, accepted with conditions, accepted).
- [ ] The reviewer cannot see the producers' reasoning.
- [ ] With a single agent behind all roles, the rubric and the review come from outside.
- [ ] Every role has a named executor; the independent reviewer's executor differs from the producers', checked on what each alias or route maps to, not on its name.
- [ ] The round record names each executor by family (a stable letter) and effort, never by model identifier; the letter-to-identifier map stays with the owner, outside the files.

## Language and honesty
- [ ] One term per concept; the synonyms to avoid are listed and absent from the files.
- [ ] Every assumption about the domain carries `[hypothesis]`; every claim about a prior instance carries `[prior:<id>]` and a checkable source.
- [ ] No absolute paths, machine names, user names or authoring dates.
- [ ] Open notes are written down with target, severity, evidence and round.
- [ ] The files do not claim the method has been validated on this target.

## Loop
- [ ] Maximum rounds per artifact is stated; an artifact over it is escalated to the owner.
- [ ] The stopping criterion was declared by the owner before the last round.
- [ ] Each false positive led to a root-cause fix with a reproducing test and a redone previous round.
