import ast
import os
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestArchitecture(unittest.TestCase):
    def test_streamlit_entrypoint_is_thin(self):
        source = (PROJECT_ROOT / "campus_essay_system.py").read_text(encoding="utf-8")
        tree = ast.parse(source)

        self.assertLessEqual(len(source.splitlines()), 10)
        self.assertTrue(any(isinstance(node, ast.ImportFrom) and node.module == "app.ui" for node in tree.body))

    def test_ui_module_does_not_import_sqlite(self):
        source = (PROJECT_ROOT / "app" / "ui.py").read_text(encoding="utf-8")

        self.assertNotIn("import sqlite3", source)

    def test_requirements_are_runtime_minimal(self):
        lines = [
            line.strip()
            for line in (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        names = {re.split(r"[<>=!~;\\[]", line, maxsplit=1)[0].strip().lower() for line in lines}

        self.assertEqual(names, {"streamlit", "pandas", "pillow", "openai", "bcrypt"})
        self.assertTrue(all("<" in line and (">=" in line or "==" in line or "~=" in line) for line in lines))


if __name__ == "__main__":
    unittest.main()

