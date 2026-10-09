from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cleanup_renders.py"


class CleanupRendersTest(unittest.TestCase):
    def make_unit(self, root: Path, note_image: str) -> Path:
        unit = root / "unit"
        slides = unit / "assets" / "slides"
        slides.mkdir(parents=True)
        (slides / "slide-001.png").write_bytes(b"temporary-render")
        (unit / "assets" / "selected.png").write_bytes(b"selected-image")
        (unit / "notes.md").write_text(f"# Unit\n\n![figure]({note_image})\n", encoding="utf-8")
        (unit / "audit.md").write_text("# Audit\n", encoding="utf-8")
        payload = {
            "sources": [
                {
                    "slides": [
                        {"number": 1, "render": "assets/slides/slide-001.png"}
                    ]
                }
            ]
        }
        (unit / "materials.json").write_text(json.dumps(payload), encoding="utf-8")
        return unit

    def run_cleanup(self, unit: Path, apply: bool = True) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(SCRIPT), str(unit)]
        if apply:
            command.append("--apply")
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_refuses_when_notes_reference_temporary_render(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            unit = self.make_unit(Path(temporary), "assets/slides/slide-001.png")
            result = self.run_cleanup(unit)
            self.assertEqual(result.returncode, 2)
            self.assertTrue((unit / "assets" / "slides").exists())
            self.assertIn("still references temporary renders", result.stderr)

    def test_removes_cache_and_updates_manifest_after_image_is_copied(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            unit = self.make_unit(Path(temporary), "assets/selected.png")
            result = self.run_cleanup(unit)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((unit / "assets" / "slides").exists())
            self.assertTrue((unit / "assets" / "selected.png").exists())
            payload = json.loads((unit / "materials.json").read_text(encoding="utf-8"))
            slide = payload["sources"][0]["slides"][0]
            self.assertIsNone(slide["render"])
            self.assertTrue(slide["render_discarded"])


if __name__ == "__main__":
    unittest.main()
