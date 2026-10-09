#!/usr/bin/env python3
"""Safely remove temporary slide renders from a completed note unit."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote


IMAGE_LINK = re.compile(r"!\[[^\]]*\]\((?P<target><[^>]+>|[^)\s]+)")
REQUIRED_OUTPUTS = ("notes.md", "audit.md", "materials.json")


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def referenced_slide_renders(markdown_path: Path, slides_dir: Path) -> list[str]:
    text = markdown_path.read_text(encoding="utf-8")
    references: list[str] = []
    for match in IMAGE_LINK.finditer(text):
        raw = match.group("target").strip("<>")
        if re.match(r"^[a-z][a-z0-9+.-]*:", raw, flags=re.IGNORECASE):
            continue
        raw = unquote(raw.split("#", 1)[0].split("?", 1)[0]).replace("\\", "/")
        resolved = (markdown_path.parent / raw).resolve()
        if is_within(resolved, slides_dir):
            references.append(match.group("target").strip("<>"))
    return references


def discard_render_paths(materials_path: Path, slides_dir: Path, unit_dir: Path) -> int:
    payload = json.loads(materials_path.read_text(encoding="utf-8"))
    changed = 0
    for source in payload.get("sources", []):
        for slide in source.get("slides", []):
            render = slide.get("render")
            if not render:
                continue
            resolved = (unit_dir / str(render)).resolve()
            if is_within(resolved, slides_dir):
                slide["render"] = None
                slide["render_discarded"] = True
                changed += 1
    if changed:
        materials_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return changed


def directory_stats(path: Path) -> tuple[int, int]:
    files = [item for item in path.rglob("*") if item.is_file()]
    return len(files), sum(item.stat().st_size for item in files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unit", help="Completed note-unit directory")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform deletion; without this flag the command is a dry run",
    )
    args = parser.parse_args()

    unit_dir = Path(args.unit).expanduser().resolve()
    if not unit_dir.is_dir():
        raise SystemExit(f"Unit directory does not exist: {unit_dir}")

    missing = [name for name in REQUIRED_OUTPUTS if not (unit_dir / name).is_file()]
    if missing:
        raise SystemExit(f"Refusing cleanup; incomplete unit is missing: {', '.join(missing)}")

    slides_path = unit_dir / "assets" / "slides"
    if slides_path.is_symlink():
        raise SystemExit(f"Refusing cleanup of symlinked render directory: {slides_path}")
    slides_dir = slides_path.resolve()
    expected = (unit_dir / "assets" / "slides").resolve()
    if slides_dir != expected or not is_within(slides_dir, unit_dir):
        raise SystemExit(f"Refusing cleanup of unexpected path: {slides_dir}")
    if not slides_dir.exists():
        print(f"No slide-render cache found: {slides_dir}")
        return 0
    if not slides_dir.is_dir():
        raise SystemExit(f"Expected a directory at: {slides_dir}")

    blockers: dict[str, list[str]] = {}
    for name in ("notes.md", "audit.md"):
        references = referenced_slide_renders(unit_dir / name, slides_dir)
        if references:
            blockers[name] = references
    if blockers:
        print("Refusing cleanup because final Markdown still references temporary renders:", file=sys.stderr)
        for name, references in blockers.items():
            for reference in references:
                print(f"  {name}: {reference}", file=sys.stderr)
        print("Copy required images to stable paths under assets/ and update the links first.", file=sys.stderr)
        return 2

    file_count, byte_count = directory_stats(slides_dir)
    if not args.apply:
        print(f"Dry run: would remove {file_count} files ({byte_count} bytes) from {slides_dir}")
        print("Run again with --apply after note validation succeeds.")
        return 0

    discarded = discard_render_paths(unit_dir / "materials.json", slides_dir, unit_dir)
    shutil.rmtree(slides_dir)
    print(f"Removed {file_count} temporary slide renders ({byte_count} bytes): {slides_dir}")
    print(f"Marked {discarded} render paths as discarded in materials.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
