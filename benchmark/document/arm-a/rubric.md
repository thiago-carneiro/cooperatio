# Rubric

Target: a guide for newcomers on preparing a production cell (brief `00-brief.md`, canon `02-canon.json`, principle `01-principle.md`).
Round: every reviewer uses this grid in every round. Verdicts across rounds are comparable only if this grid was frozen before the first review.

## 1. Dimensions

### D1. Source discipline

Every statement about the method can be checked in the principle; every statement about a registered prior carries its mark (`[prior:<id>]`) and can be checked in its method document; nothing about a prior is stated outside the method document that registers it.

- **1**: statements about the method contradict the principle; statements about a prior carry no mark, or a mark whose method document does not support them.
- **3**: statements about the method are traceable, but at least one statement about a prior is unmarked or its mark is wrong, or a fact about a prior is stated outside its method document.
- **5**: every method statement traceable to the principle, every prior statement marked and checkable, no prior fact borrowed from outside its method document.

### D2. Canon conformance

Numbers, names, terms and accepted variants follow the canon: recorded facts match their recorded values and context; the terms of the canon are used in the canon's sense; the terms to avoid do not appear as working vocabulary.

- **1**: a recorded fact is stated with a different number, or a term to avoid is used as working vocabulary, or a canon term is used with a different sense without a gloss.
- **3**: numbers and names match, but at least one canon term is used loosely or a term to avoid slips in once without being the term of art.
- **5**: every number, name and term matches the canon; the terms to avoid are absent as vocabulary; accepted variants are used only where the canon says they hold.

### D3. Instruction fit

The guide tells a newcomer what to do: the brief, the sources of truth, the canon and the artifact graph, in an order a reader who has read the principle once and never prepared a cell can follow; the audience declared in the brief is the audience addressed.

- **1**: the guide assumes knowledge the declared audience does not have, or omits one of the four subjects the brief names, or addresses a different audience.
- **3**: the four subjects are there and the audience is roughly right, but a step assumes an unstated prerequisite, or the order forces the reader to go back.
- **5**: a reader of the declared audience can prepare a cell from the guide alone, in one pass; each of the four subjects is present and placed where it is needed; nothing assumes a reading the brief does not grant.

### D4. Coverage and completeness

The guide covers the brief's scope without silent gaps: every non-negotiable of the brief is addressed, every section promised by the guide's own structure is present and does its job, and the owner decisions the brief records are respected.

- **1**: a non-negotiable of the brief is unaddressed, or a promised section is empty or a stub, or the guide overrides an owner decision.
- **3**: all non-negotiables are touched, but at least one is treated so thinly that a reader would not act on it, or one promised section does work assigned elsewhere.
- **5**: every non-negotiable is addressed at the depth its weight in the brief deserves; every promised section is present and does its own work; owner decisions are respected and marked as such.

### D5. Precision and unambiguity

Terms, numbers, orderings and hand-offs are stated so that only one reading is possible: a term is glossed where it first appears, a number carries its unit and its source, a step's input and output are named.

- **1**: a newcomer would have to guess what a term means, which number is meant, or what a step takes in and gives out.
- **3**: readable in one pass, but at least one term is used before its gloss, or one hand-off is named in two ways, or one number lacks its source.
- **5**: every term glossed at first use, every number with unit and source, every step with named input and output; no sentence admits two readings a newcomer would resolve differently.

### D6. Internal coherence

The guide does not contradict itself: the same fact is stated the same way across sections, the vocabulary is stable, and a rule stated in one place is not denied in another.

- **1**: two sections state different values or different rules for the same thing, or the vocabulary shifts so that a reader cannot tell whether two names are one thing.
- **3**: one contradiction a careful reader would resolve in favor of one of the two statements, without a stated reason for the choice.
- **5**: no contradiction; where a nuance differs between sections, the guide says so explicitly and says why.

### D7. Enforceable form

Plain Markdown, no HTML, no absolute path, no authoring date, no machine name; the length falls inside the brief's range; headings are used as structure and not as decoration.

- **1**: contains HTML, an absolute path, an authoring date, or a machine name; or the length falls outside the brief's stated range; or the Markdown does not render as intended.
- **3**: form is clean, but the length is inside the range only at its edge, or a heading level is used inconsistently, or a link or code span is malformed.
- **5**: form is clean on every point above; the length sits inside the range with room on both sides; the structure reads as sections doing work.

### D8. Actionability for the next round

Findings against the guide can be routed to an origin: a section names its source, a term names its canon entry, a step names its role and artifact. A reviewer can say where a defect was born.

- **1**: findings can only be phrased as "the guide is wrong"; no section, term or step can be traced to a named origin.
- **3**: most findings route to a section, but at least one class of defect (a number, a term, a step) cannot be routed to the origin the method expects.
- **5**: every finding a reviewer can raise routes to a named section, canon entry, role or artifact; the guide's own structure tells the reviewer where to send the note.

## 2. Severity scale of findings

- **low** — a reading defect that does not change what a newcomer would do: a stylistic inconsistency, a term used loosely where the canon allows it, a heading that could be sharper. The guide is usable as it stands.
- **medium** — a defect a newcomer would notice and would have to resolve by going back to the principle or the canon: a term used before its gloss, a step whose input is unnamed, a section that is thin against the brief's weight. The guide is usable, at a cost to the reader.
- **high** — a defect that changes what the newcomer would do: a step that, followed as written, produces a wrong artifact; a non-negotiable of the brief addressed only nominally; a statement about a prior that is wrong but marked. The guide cannot be followed safely without a correction.
- **blocking** — a defect that makes the guide unfit for the declared audience or violates a non-negotiable of the brief outright: an unmarked or misattributed statement about a registered prior; a recorded fact stated with a different number; the use of a term to avoid as working vocabulary; the omission of one of the four subjects the brief names; an owner decision overridden.

## 3. Verdict rule

Applied mechanically over the dimension scores and the findings, in this order:

1. If any **blocking** finding exists, or any dimension has a score **at most 2** → **rejected**.
2. Else if there is **no high finding** and **every** dimension has a score **at least 4** → **accepted**.
3. Else → **accepted with conditions**.

No reviewer adds a fourth value, and no reviewer adjusts the rule for a round. A finding whose severity the reviewer is unsure of is recorded at the higher severity and the disagreement is written into the report, not resolved silently.

## 4. Report format

Every review is reported in exactly these numbered sections, in this order:

1. **Header** — target, round, reviewer relation to the producer (`reviewer_relation`: same session / different session / different family), the hash of this rubric, and the hash of the reviewed artifact. No model identifier, no date of making, no machine name.
2. **Dimension scores** — one line per dimension D1 to D8, each with its integer score and one sentence of justification that names the evidence.
3. **Findings** — one numbered block per finding, each with: severity (low / medium / high / blocking), the dimension it bears on, the section or line of the guide it targets, the evidence, the origin the note is routed to (section, canon entry, role or artifact), and one sentence on what a fix would change.
4. **Verdict** — the three-valued verdict from section 3, with the rule clause that produced it stated verbatim ("blocking present", "some dimension at most 2", "no high and all at least 4", or "otherwise").
5. **Open questions to the owner** — questions this review could not resolve against the brief or the canon, each named as an open item, none answered by the reviewer. Empty if none.
6. **Instrument note** — any point where this rubric itself read wrongly (a dimension whose anchors did not fit the target, a severity the reviewer had to stretch), recorded so the rubric can be fixed at the root and not loosened in the next round. Empty if none.