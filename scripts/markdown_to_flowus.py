#!/usr/bin/env python3
"""Convert FlowUs-ready Markdown into ordered FlowUs block/image segments."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_ANNOTATIONS = {
    "bold": False,
    "italic": False,
    "strikethrough": False,
    "underline": False,
    "code": False,
    "text_color": "default",
    "background_color": "default",
}
IMAGE_RE = re.compile(r"^\s*(?:[-+*]\s+)?!\[(?P<alt>[^\]]*)\]\((?P<target>[^)]+)\)\s*$")
LIST_RE = re.compile(r"^(?P<indent>\s*)(?P<marker>[-+*]|\d+[.)])\s+(?P<text>.+)$")
FENCE_RE = re.compile(r"^```(?P<language>[A-Za-z0-9_+.-]*)\s*$")
SPECIAL_RE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\$[^$\n]+\$|\[[^\]]+\]\([^)]+\))")


def rich_text(content: str, *, bold: bool = False, code: bool = False, link: str | None = None, equation: bool = False) -> dict:
    annotations = dict(DEFAULT_ANNOTATIONS)
    annotations["bold"] = bold
    annotations["code"] = code
    if equation:
        return {
            "type": "equation",
            "equation": {"expression": content},
            "annotations": annotations,
            "plain_text": content,
            "href": None,
        }
    return {
        "type": "text",
        "text": {"content": content, "link": {"url": link} if link else None},
        "annotations": annotations,
        "plain_text": content,
        "href": link,
    }


def parse_rich_text(value: str) -> list[dict]:
    parts: list[dict] = []
    cursor = 0
    for match in SPECIAL_RE.finditer(value):
        if match.start() > cursor:
            parts.append(rich_text(value[cursor : match.start()]))
        token = match.group(0)
        if token.startswith("**"):
            parts.append(rich_text(token[2:-2], bold=True))
        elif token.startswith("`"):
            parts.append(rich_text(token[1:-1], code=True))
        elif token.startswith("$"):
            parts.append(rich_text(token[1:-1], equation=True))
        else:
            link_match = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", token)
            if link_match:
                parts.append(rich_text(link_match.group(1), link=link_match.group(2)))
        cursor = match.end()
    if cursor < len(value):
        parts.append(rich_text(value[cursor:]))
    return [part for part in parts if part.get("plain_text")]


def text_block(block_type: str, value: str, **extra: object) -> dict:
    content = {"rich_text": parse_rich_text(value)}
    content.update(extra)
    return {"object": "block", "type": block_type, block_type: content}


def split_table_row(line: str) -> list[str]:
    value = line.strip().strip("|")
    cells = re.split(r"(?<!\\)\|", value)
    return [cell.strip().replace("\\|", "|") for cell in cells]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def convert(markdown: str, source_dir: Path) -> dict:
    lines = markdown.splitlines()
    title = "Untitled notes"
    segments: list[dict] = []
    current_blocks: list[dict] = []
    list_stack: list[tuple[int, dict]] = []
    heading_stack: list[tuple[int, str]] = []
    heading_counts = {2: 0, 3: 0}
    current_parent_path: list[str] = []

    def flush_blocks() -> None:
        nonlocal current_blocks, list_stack
        if current_blocks:
            segments.append({
                "kind": "blocks",
                "parent_path": list(current_parent_path),
                "blocks": current_blocks,
            })
            current_blocks = []
        list_stack = []

    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped:
            index += 1
            continue

        fence_match = FENCE_RE.match(stripped)
        if fence_match:
            language = fence_match.group("language") or "plain text"
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and lines[index].strip() != "```":
                code_lines.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            code_value = "\n".join(code_lines)
            current_blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [rich_text(code_value)] if code_value else [],
                    "language": language,
                    "display_mode": "source",
                },
            })
            list_stack = []
            continue

        image_match = IMAGE_RE.match(raw)
        if image_match:
            flush_blocks()
            target = image_match.group("target").strip().strip("<>")
            is_remote = bool(re.match(r"^https?://", target, flags=re.IGNORECASE))
            resolved = target if is_remote else str((source_dir / target).resolve())
            segments.append({
                "kind": "image",
                "parent_path": list(current_parent_path),
                "alt": image_match.group("alt"),
                "target": resolved,
                "remote": is_remote,
            })
            index += 1
            continue

        if stripped.startswith("$$"):
            expression_lines: list[str] = []
            if stripped != "$$":
                expression_lines.append(stripped[2:])
            index += 1
            while index < len(lines) and lines[index].strip() != "$$":
                expression_lines.append(lines[index].strip())
                index += 1
            if index < len(lines):
                index += 1
            current_blocks.append({"object": "block", "type": "equation", "equation": {"expression": "\n".join(expression_lines)}})
            list_stack = []
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            level = len(heading.group(1))
            if level == 1 and title == "Untitled notes":
                title = heading.group(2).strip()
            else:
                flush_blocks()
                block_type = f"heading_{min(level, 3)}"
                level = min(level, 3)
                heading_counts[level] += 1
                heading_key = f"h{level}-{heading_counts[level]}"
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                parent_path = [key for _, key in heading_stack]
                segments.append({
                    "kind": "blocks",
                    "parent_path": parent_path,
                    "heading_key": heading_key,
                    "blocks": [text_block(block_type, heading.group(2).strip(), is_toggleable=level >= 2)],
                })
                heading_stack.append((level, heading_key))
                current_parent_path = [key for _, key in heading_stack]
            list_stack = []
            index += 1
            continue

        if stripped.startswith("|") and index + 1 < len(lines) and is_table_separator(lines[index + 1]):
            rows = [split_table_row(raw)]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(split_table_row(lines[index]))
                index += 1
            width = max(len(row) for row in rows)
            children = []
            for row in rows:
                padded = row + [""] * (width - len(row))
                children.append({
                    "object": "block",
                    "type": "table_row",
                    "table_row": {"cells": [parse_rich_text(cell) for cell in padded]},
                })
            current_blocks.append({
                "object": "block",
                "type": "table",
                "table": {"table_width": width, "has_column_header": True, "has_row_header": False, "width_mode": "adaptive"},
                "children": children,
            })
            list_stack = []
            continue

        if stripped.startswith(">"):
            quote_lines = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(re.sub(r"^\s*>\s?", "", lines[index]).strip())
                index += 1
            value = "\n".join(line for line in quote_lines if line)
            background = "light_blue" if "补充解释" in value else "light_yellow" if "易错点" in value else "default"
            current_blocks.append(text_block("quote", value, background_color=background))
            list_stack = []
            continue

        list_match = LIST_RE.match(raw)
        if list_match:
            indent = len(list_match.group("indent").expandtabs(4))
            block_type = "numbered_list_item" if list_match.group("marker")[0].isdigit() else "bulleted_list_item"
            block = text_block(block_type, list_match.group("text").strip())
            # FlowUs Markdown commonly uses two spaces per nesting level, while
            # hand-authored Markdown often uses four. Compare relative
            # indentation instead of dividing by a fixed width so either style
            # preserves the same parent-child list tree. Blank lines do not
            # clear list_stack, because FlowUs exports loose lists with blank
            # lines between a parent item and its children.
            while list_stack and list_stack[-1][0] >= indent:
                list_stack.pop()
            if list_stack:
                list_stack[-1][1].setdefault("children", []).append(block)
            else:
                current_blocks.append(block)
            list_stack.append((indent, block))
            index += 1
            continue

        paragraph_lines = [stripped]
        index += 1
        while index < len(lines):
            candidate = lines[index]
            candidate_stripped = candidate.strip()
            if not candidate_stripped or IMAGE_RE.match(candidate) or LIST_RE.match(candidate):
                break
            if re.match(r"^(#{1,3})\s+", candidate_stripped) or candidate_stripped.startswith(("|", ">", "$$")):
                break
            paragraph_lines.append(candidate_stripped)
            index += 1
        current_blocks.append(text_block("paragraph", " ".join(paragraph_lines)))
        list_stack = []

    flush_blocks()
    return {"title": title, "segments": segments}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", help="FlowUs-ready Markdown file")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()
    source = Path(args.markdown).resolve()
    payload = convert(source.read_text(encoding="utf-8"), source.parent)
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    block_count = sum(len(segment.get("blocks", [])) for segment in payload["segments"])
    top_level_blocks = sum(
        len(segment.get("blocks", []))
        for segment in payload["segments"]
        if segment.get("kind") == "blocks" and not segment.get("parent_path")
    )
    image_count = sum(segment["kind"] == "image" for segment in payload["segments"])
    print(json.dumps({
        "title": payload["title"],
        "segments": len(payload["segments"]),
        "blocks": block_count,
        "top_level_blocks": top_level_blocks,
        "images": image_count,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
