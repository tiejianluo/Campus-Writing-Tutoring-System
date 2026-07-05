import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.responsive import (
    PHONE_MAX_WIDTH,
    RESPONSIVE_CSS,
    TABLET_MAX_WIDTH,
    TOUCH_TARGET_PX,
    records_table_html,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestResponsiveDesign(unittest.TestCase):
    def test_responsive_css_has_phone_tablet_and_touch_targets(self):
        self.assertIn(f"max-width: {PHONE_MAX_WIDTH}px", RESPONSIVE_CSS)
        self.assertIn(f"max-width: {TABLET_MAX_WIDTH}px", RESPONSIVE_CSS)
        self.assertIn(f"min-height: {TOUCH_TARGET_PX}px", RESPONSIVE_CSS)
        self.assertIn("grid-template-columns", RESPONSIVE_CSS)

    def test_records_table_html_escapes_user_content(self):
        html = records_table_html(
            [{"学生": "<script>alert(1)</script>", "作文": "今天很好。"}],
            columns=["学生", "作文"],
        )

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertIn('data-label="学生"', html)

    def test_ui_loads_responsive_styles(self):
        source = (PROJECT_ROOT / "app" / "ui.py").read_text(encoding="utf-8")

        self.assertIn("inject_responsive_styles", source)
        self.assertIn("render_records", source)
        self.assertIn("st.set_page_config", source)


if __name__ == "__main__":
    unittest.main()

