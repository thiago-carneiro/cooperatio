# Role card: reviewer

**Decides:** the score of each dimension, the severity of each finding, and the verdict by the rubric's mechanical rule.

**Does not decide:** the rubric, or what gets fixed: it only points, with location and evidence.

**Inputs:** the source files and the rubric, and the report of the automatic checks; never the reasoning of whoever wrote the code.

**Outputs:** a report in the rubric's format, and the findings.

**Exit gate:** the report has every section of the format and the verdict matches the rule.
