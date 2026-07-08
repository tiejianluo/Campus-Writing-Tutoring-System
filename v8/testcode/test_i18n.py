"""v8 双语 UI 测试：中英文案齐全、占位符一致、tr 回退语义、UI 引用的 key 全部存在。"""

import os
import string
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.i18n import DEFAULT_LANG, LANG_EN, LANG_LABELS, LANG_ZH, LANGS, TEXTS, tr


def placeholders(text: str) -> set:
    """提取 format 占位符名集合。"""
    return {field for _, field, _, _ in string.Formatter().parse(text) if field}


class TestCatalogCompleteness(unittest.TestCase):
    def test_every_key_has_zh_and_en(self):
        """双语 UI 核心要求：每条界面文案必须同时有中文和英文。"""
        for key, entry in TEXTS.items():
            for lang in (LANG_ZH, LANG_EN):
                self.assertIn(lang, entry, f"{key} 缺少 {lang} 文案")
                self.assertIsInstance(entry[lang], str, f"{key}/{lang} 不是字符串")
                self.assertTrue(entry[lang].strip(), f"{key}/{lang} 为空")

    def test_placeholders_match_between_languages(self):
        """中英文案的 {占位符} 必须一致，否则某一语言运行时会格式化失败。"""
        for key, entry in TEXTS.items():
            self.assertEqual(
                placeholders(entry[LANG_ZH]),
                placeholders(entry[LANG_EN]),
                f"{key} 的中英文占位符不一致",
            )

    def test_langs_and_labels(self):
        self.assertEqual(set(LANGS), {LANG_ZH, LANG_EN})
        self.assertEqual(DEFAULT_LANG, LANG_ZH)
        for lang in LANGS:
            self.assertTrue(LANG_LABELS.get(lang))


class TestTrFunction(unittest.TestCase):
    def test_returns_requested_language(self):
        self.assertEqual(tr("logout", LANG_ZH), "退出登录")
        self.assertEqual(tr("logout", LANG_EN), "Log out")

    def test_default_language_is_chinese(self):
        self.assertEqual(tr("logout"), "退出登录")

    def test_unknown_language_falls_back_to_chinese(self):
        self.assertEqual(tr("logout", "fr"), "退出登录")

    def test_unknown_key_returns_key(self):
        self.assertEqual(tr("no_such_key_xyz", LANG_EN), "no_such_key_xyz")

    def test_formatting_kwargs(self):
        self.assertIn("3", tr("quota_left", LANG_ZH, n=3))
        self.assertIn("3", tr("quota_left", LANG_EN, n=3))

    def test_bad_format_kwargs_do_not_crash(self):
        # 传错的关键字参数不应抛异常，返回未格式化文本即可
        text = tr("quota_left", LANG_ZH, wrong_name=1)
        self.assertIsInstance(text, str)
        self.assertTrue(text)


class TestUiUsesCatalog(unittest.TestCase):
    """app.ui 中引用的文案 key 必须都在 TEXTS 中（两种语言可用）。"""

    def test_student_menu_keys_exist(self):
        from app.ui import STUDENT_MENU_KEYS

        for key in STUDENT_MENU_KEYS:
            self.assertIn(key, TEXTS, f"学生菜单 key {key} 缺文案")

    def test_fallback_and_ocr_message_keys_exist(self):
        from app.ui import FALLBACK_TEXT_KEYS, OCR_TEXT_KEYS

        for key in list(FALLBACK_TEXT_KEYS.values()) + list(OCR_TEXT_KEYS.values()):
            self.assertIn(key, TEXTS, f"提示文案 key {key} 缺失")

    def test_handwriting_page_keys_exist(self):
        for key in (
            "handwriting_title",
            "handwriting_intro",
            "handwriting_upload",
            "handwriting_extract_btn",
            "handwriting_extracted",
            "handwriting_ok",
            "handwriting_empty",
            "handwriting_manual_hint",
        ):
            self.assertIn(key, TEXTS)


if __name__ == "__main__":
    unittest.main()
