# Content selection and provenance

## Primary objective

Produce an exam-oriented knowledge reconstruction, not a slide transcript. Group information by conceptual dependency and retrieval value.

## Source roles

Classify each slide or page as one or more of:

- `content`: definitions, mechanisms, rules, properties, classifications, formulas, syntax, or procedures.
- `example`: a worked or illustrative case.
- `diagram`: a figure whose spatial structure carries meaning.
- `exercise`: a question, prompt, or practice task.
- `administration`: schedules, assessment logistics, contacts, book covers, module representation, or generic course advice.
- `coverage_reference`: Learning Outcomes, objectives, review pages, recaps, and final knowledge lists.

Discard administration unless the user asks for it. Exercises belong in the main notes only when they teach a reusable solving pattern; otherwise list them in the audit or a separately requested question page.

## Learning Outcomes and summaries

Treat Learning Outcomes, objectives, recaps, and final knowledge lists as:

1. coverage checks;
2. importance signals;
3. optional architecture hints when the main deck structure is unclear.

Do not reproduce them by default. Include one only when it is independently useful as a concise review artifact or the user asks for it.

When a goal appears in a coverage reference but not in substantive slides, report the discrepancy in `audit.md`; do not manufacture the missing explanation.

## What to keep

- Exact technical terms and definitions likely to be assessed in English.
- Conditions, boundaries, exceptions, and failure cases.
- Comparisons with at least two useful dimensions.
- Ordered methods, algorithms, derivations, and design procedures.
- Formula meanings, variable meanings, and applicability conditions.
- Representative code/API syntax and one example that generalizes.
- Diagrams needed to understand architecture, signal flow, topology, state, circuitry, or a question.
- Teacher emphasis that changes what the learner should remember or distinguish.

## What to compress or omit

- Repeated restatements and recap text already covered well.
- Multiple examples that exercise the same pattern without adding a new edge case.
- Presenter transitions, branding, decorative imagery, and page furniture.
- Long histories or biographies unless the course treats them as assessed content.
- Text that only narrates what a nearby diagram already makes clear.

## Added knowledge

Use these provenance classes while drafting:

- `source`: explicitly present in supplied material.
- `derived`: direct translation, reorganization, calculation, or conservative explanation of supplied material.
- `supplement`: useful domain knowledge not established by supplied material.

Render `source` and `derived` naturally. Render every `supplement` in a separate block beginning:

```markdown
> 💡 **补充解释**
>
> Supplementary content here.
```

Do not mix a supplement into an English source definition. Consolidate related supplements so the page is not covered in labels.

## Traceability

Keep slide provenance in `materials.json` and summarize it in `audit.md`. The study notes should remain clean; add visible slide citations only when the user requests them.
