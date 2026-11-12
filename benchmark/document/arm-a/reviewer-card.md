# Role card: reviewer

Canon: [02-canon.json](../02-canon.json)

**Decides:**

- the score of each dimension, the severity of each finding and the verdict by the mechanical rule

**Does not decide:**

- the rubric, and what gets fixed

**Inputs:**

- the guide, the brief, the canon, the sources, the rubric and the report of the validator; never the reasoning of the writer

**Outputs:**

- a report in the format of the rubric, and the notes

**Exit gate:**

- the report has every section of the format and the verdict matches the rule

**Notes it emits:**

- to the guide, of the four severities, each with its location and its evidence

**Code-conversion degree:**

- (c) contract and gate only; executor: a language model that did not write the guide
