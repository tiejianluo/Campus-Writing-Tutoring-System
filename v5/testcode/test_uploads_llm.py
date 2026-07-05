import io
import os
import sys
import unittest

from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import Settings
from app.llm import LLMService, build_prompt, fallback_feedback, fallback_image_prompts
from app.rate_limit import FixedWindowRateLimiter
from app.uploads import UploadValidationError, image_to_model_data_url, load_uploaded_image, read_uploaded_text


class TestUploadsAndLLM(unittest.TestCase):
    def test_text_upload_size_limit(self):
        settings = Settings(max_text_upload_bytes=8)

        self.assertEqual(read_uploaded_text(io.BytesIO("作文".encode("utf-8")), settings), "作文")
        with self.assertRaises(UploadValidationError):
            read_uploaded_text(io.BytesIO(b"a" * 9), settings)

    def test_image_upload_pixel_limit_and_compression(self):
        settings = Settings(max_image_pixels=200, max_model_image_side=8)
        image_bytes = io.BytesIO()
        Image.new("RGB", (10, 10), "white").save(image_bytes, format="PNG")
        image_bytes.seek(0)

        image = load_uploaded_image(image_bytes, settings)
        data_url = image_to_model_data_url(image, settings)

        self.assertEqual(image.size, (10, 10))
        self.assertTrue(data_url.startswith("data:image/jpeg;base64,"))

        too_large = io.BytesIO()
        Image.new("RGB", (20, 20), "white").save(too_large, format="PNG")
        too_large.seek(0)
        with self.assertRaises(UploadValidationError):
            load_uploaded_image(too_large, settings)

    def test_llm_fallback_without_key_and_prompt_content(self):
        settings = Settings(openai_api_key=None)
        service = LLMService(settings)

        feedback = service.essay_feedback("三年级", "写事", "一次活动", "今天我很高兴。", user_key="student")
        prompt = build_prompt("三年级", "写事", "一次活动", "今天我很高兴。")

        self.assertIn("teacher_feedback", feedback)
        self.assertIn("三年级", prompt)
        self.assertIn("一次活动", prompt)
        self.assertEqual(fallback_image_prompts("三年级")["suggested_title"], "看图作文")
        self.assertIn("student_feedback", fallback_feedback("三年级", "写事", "题目", "作文"))

    def test_rate_limiter_blocks_after_limit(self):
        limiter = FixedWindowRateLimiter(limit=2, window_seconds=60)

        self.assertTrue(limiter.allow("u", now=1.0))
        self.assertTrue(limiter.allow("u", now=2.0))
        self.assertFalse(limiter.allow("u", now=3.0))
        self.assertTrue(limiter.allow("u", now=63.0))


if __name__ == "__main__":
    unittest.main()

