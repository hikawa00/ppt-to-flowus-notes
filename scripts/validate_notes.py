#!/usr/bin/env python3
"""Validate FlowUs-ready Markdown notes and their separate audit."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote


REQUIRED_AUDIT_HEADINGS = ("参考清单覆盖", "来源范围", "补充解释", "不确定项", "格式检查")


def unescaped_pipe_count(line: str) -> int:
    return len(re.findall(r"(?<!\\)\|", line))


def validate_tables(lines: list[str]) -> list[str]:
    errors: list[str] = []
    index = 0
    while index < len(lines):
        if lines[index].lstrip().startswith("|"):
            start = index
            block = []
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                block.append(lines[index])
                index += 1
            if len(block) >= 2:
                counts = [unescaped_pipe_count(line) for line in block]
                if len(set(counts)) != 1:
                    errors.append(f"Malformed table near line {start + 1}: row column counts differ ({counts}).")
            continue
        index += 1
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notes", help="Path to notes.md")
    parser.add_argument("--materials", required=True, help="Path to materials.json")
    parser.add_argument("--audit", required=True, help="Path to audit.md")
    parser.add_argument("--output", help="Optional validation JSON path")
    args = parser.parse_args()

    notes_path = Path(args.notes).resolve()
    materials_path = Path(args.materials).resolve()
    audit_path = Path(args.audit).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for path in (notes_path, materials_path, audit_path):
        if not path.exists():
            errors.append(f"Missing required file: {path}")
    if errors:
        payload = {"ok": False, "errors": errors, "warnings": warnings}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    notes = notes_path.read_text(encoding="utf-8")
    audit = audit_path.read_text(encoding="utf-8")
    lines = notes.splitlines()

    if not re.search(r"^#\s+\S", notes, flags=re.MULTILINE):
        errors.append("notes.md needs a level-1 title.")
    if not re.search(r"^##\s+\S", notes, flags=re.MULTILINE):
        warnings.append("notes.md has no level-2 topic heading.")
    if notes.count("```") % 2:
        errors.append("Unbalanced fenced code block markers in notes.md.")
    if re.search(r"\{\{[^}]+\}\}|\bTODO\b", notes):
        errors.append("notes.md still contains template placeholders or TODO text.")
    errors.extend(validate_tables(lines))

    images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", notes)
    for raw_target in images:
        target = unquote(raw_target.strip().split(" ", 1)[0].strip("<>"))
        if re.match(r"^[a-z]+://", target, flags=re.IGNORECASE) or target.startswith("data:"):
            continue
        image_path = (notes_path.parent / target).resolve()
        if not image_path.exists():
            errors.append(f"Broken local image link: {raw_target}")

    for number, line in enumerate(lines, start=1):
        if "补充解释" in line and not re.match(r"^>\s*💡\s*\*\*补充解释\*\*", line.strip()):
            warnings.append(f"Possible unmarked supplement near line {number}: {line.strip()}")

    for heading in REQUIRED_AUDIT_HEADINGS:
        if not re.search(rf"^##\s+.*{re.escape(heading)}", audit, flags=re.MULTILINE):
            errors.append(f"audit.md is missing section: {heading}")
    if re.search(r"\{\{[^}]+\}|\bTODO\b", audit):
        errors.append("audit.md still contains template placeholders or TODO text.")

    try:
        materials = json.loads(materials_path.read_text(encoding="utf-8"))
        if materials.get("schema_version") != 1:
            warnings.append("materials.json has an unexpected schema_version.")
        if not materials.get("sources"):
            errors.append("materials.json contains no sources.")
        if "coverage_reference_candidates" not in materials:
            errors.append("materials.json lacks coverage_reference_candidates.")
    except json.JSONDecodeError as exc:
        errors.append(f"materials.json is invalid JSON: {exc}")

    payload = {
        "ok": not errors,
        "notes": str(notes_path),
        "materials": str(materials_path),
        "audit": str(audit_path),
        "image_count": len(images),
        "supplement_count": len(re.findall(r"^>\s*💡\s*\*\*补充解释\*\*", notes, flags=re.MULTILINE)),
        "errors": errors,
        "warnings": warnings,
    }
    output_path = Path(args.output).resolve() if args.output else notes_path.parent / "validation.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
