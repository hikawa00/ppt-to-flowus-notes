# Personal note style

## Core character

Write an exam-oriented bilingual reconstruction. English supplies exact terminology and assessment-ready definitions. Chinese supplies navigation, distinctions, intuition, and memory cues.

Use the restrained structure seen in the DB, OO, communication-network, and digital-logic notes. Apply colored callouts sparingly and adapt the information form to the subject.

## Hierarchy

Prefer a shallow heading structure and deep list structure:

```text
# TB / Week / Part
## Major topic
### Subtopic when genuinely needed
- Knowledge unit
    - explanation, condition, or example
```

Do not create a heading for every slide. Merge consecutive slides that answer the same conceptual question.

## Bilingual phrasing

Preferred pattern:

```text
- 中文功能标签：English definition or technical statement（简短中文理解）
```

Useful labels include `定义`、`本质`、`作用`、`机制`、`条件`、`为什么`、`区别`、`结论`、`注意`、`物理事实` and `例子`. Use labels only when they improve retrieval; do not force every concept into the same template.

- Preserve canonical English terms, code identifiers, and wording that may be required in an English exam.
- Translate for understanding rather than sentence-by-sentence duplication.
- Keep Chinese concise and direct. Parenthetical explanations may be conversational and memorable.
- Use `→`, `/`, `+`, and `=` when they express a real dependency, contrast, composition, or transformation.
- Avoid polishing the prose into a formal textbook voice.

## Emphasis

- Bold decisive terms, conditions, outputs, and distinctions.
- Use inline code for identifiers, syntax, variables, commands, and API names.
- Reserve warning styling for common confusions or failure conditions.
- Do not highlight whole paragraphs or bold every technical noun.
- In portable Markdown, represent external supplements with the required `💡 **补充解释**` blockquote. FlowUs synchronization may later map this to a light-blue callout.

## Choosing a representation

| Content | Preferred form |
|---|---|
| One definition | Bullet with exact English and a Chinese cue |
| Several comparable concepts | Native table with consistent dimensions |
| Ordered operation | Numbered list |
| Protocol or mechanism | Labeled bullets such as Mechanism, Loss, Receiver, Sender, Condition |
| Formula | Meaning, symbols, conditions, then a representative use |
| API or method family | Method / purpose / example table |
| Code execution | Code block followed by short step explanation |
| Spatial relationship | Selected source diagram followed by interpretation |

Tables are information compression tools, not decoration. Avoid tables when a short list reads more naturally.

## Subject adaptation

- Concept-heavy courses: emphasize definitions, categories, comparisons, integrity conditions, advantages, and limitations.
- Programming courses: emphasize object models, syntax, APIs, code behavior, common errors, and language comparisons.
- Mathematical, network, and digital-logic courses: emphasize symbol definitions, conditions, mechanisms, derivations, diagrams, and reusable solving procedures.

Keep the same bilingual voice across modes. Adapt structure and visual density rather than adopting unrelated writing personalities.

## Improvements over historical exports

- Normalize spacing around Chinese, English, formulas, and punctuation where it improves readability.
- Generate valid Markdown tables; do not reproduce broken multiline table cells.
- Remove scratch phrases and unfinished fragments.
- Give images meaningful names.
- Preserve uncertainty instead of silently guessing unreadable content.
