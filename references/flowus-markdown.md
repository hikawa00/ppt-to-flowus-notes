# FlowUs-ready Markdown

## Delivery layout

Use this folder contract:

```text
<unit>/
├── notes.md
├── audit.md
├── materials.json
└── assets/
```

All image links in `notes.md` must be relative paths under `assets/`.

`assets/slides/` is a disposable rendering cache used while reading the source. Before delivery, copy each image actually used by the notes to a meaningful stable path under `assets/`, update its Markdown link, validate the unit, and remove the rendering cache. A completed unit must not contain `assets/slides/` unless the user explicitly requested full render retention.

## Portable subset

Prefer Markdown that survives import:

- ATX headings (`#`, `##`, `###`)
- unordered and ordered lists
- four-space nested list indentation
- bold and inline code
- fenced code blocks with a language when known
- pipe tables with one physical line per row
- blockquotes
- display math using `$$...$$` when the formula is reliable
- relative image links

Do not rely on raw HTML for colors, highlights, toggles, or layout. The user's FlowUs export retains content structure but drops much of this styling metadata.

## Folding and color intent

Portable Markdown cannot itself preserve FlowUs toggle metadata. Keep ordinary `##` and `###` ATX headings in `notes.md`. During FlowUs synchronization, map every H2 and H3 to a toggleable heading block and make the section body real descendants of that heading:

- H2 owns all following content through the block before the next H2.
- H3 is a child of the current H2 and owns all following content through the block before the next H3 or H2.
- Images, tables, equations, quotes, and nested lists follow the same ownership rule.
- Do not merely set `is_toggleable=true` while leaving section content as sibling blocks; collapsing the heading must hide the whole section.
- Verify the returned block state after synchronization. If FlowUs returns `is_toggleable=false` despite the request, retain the correct block tree and mark the page as requiring one final in-app conversion; do not misreport it as folded.

Use semantic markers that a future renderer can map:

- `> 💡 **补充解释**` → light-blue callout
- `> ⚠️ **易错点**` → light-red or yellow warning callout
- ordinary bold → standard bold rich text
- inline code → code-styled rich text

Keep ordinary notes mostly monochrome. Color is for meaning, not decoration.

## Images

Use descriptive, filesystem-safe names such as `ansi-sparc-architecture.png`, `selective-retransmission-timeline.png`, or `moore-vs-mealy-state-diagram.png`.

If the same image appears repeatedly, keep one copy and reuse its path. Rebuild text-only screenshots as native Markdown where reliable.

## Tables

- Keep every row on one physical line.
- Replace line breaks inside cells with `<br>` only when unavoidable; prefer shorter cell text.
- Escape literal pipe characters as `\|`.
- Use bold sparingly inside cells.
- If a table becomes too wide or contains code blocks, replace it with repeated labeled bullets.

Start from [../assets/note-template.md](../assets/note-template.md), removing unused optional sections. Use [../assets/audit-template.md](../assets/audit-template.md) for the separate coverage report. Do not include audit content in `notes.md`.
