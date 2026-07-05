import base64
import io
import os

from PIL import Image

from .config import Settings


class UploadValidationError(ValueError):
    pass


def uploaded_size(uploaded_file) -> int:
    if hasattr(uploaded_file, "size"):
        return int(uploaded_file.size)
    if hasattr(uploaded_file, "getbuffer"):
        return len(uploaded_file.getbuffer())
    if hasattr(uploaded_file, "tell") and hasattr(uploaded_file, "seek"):
        pos = uploaded_file.tell()
        uploaded_file.seek(0, os.SEEK_END)
        size = uploaded_file.tell()
        uploaded_file.seek(pos)
        return size
    return 0


def read_uploaded_text(uploaded_file, settings: Settings) -> str:
    size = uploaded_size(uploaded_file)
    if size > settings.max_text_upload_bytes:
        raise UploadValidationError(f"文本文件过大，最大允许 {settings.max_text_upload_bytes} 字节。")
    data = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    if isinstance(data, str):
        return data
    return data.decode("utf-8", errors="replace")


def load_uploaded_image(uploaded_file, settings: Settings) -> Image.Image:
    size = uploaded_size(uploaded_file)
    if size > settings.max_image_upload_bytes:
        raise UploadValidationError(f"图片文件过大，最大允许 {settings.max_image_upload_bytes} 字节。")
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    try:
        image = Image.open(uploaded_file)
        image.load()
    except Exception as exc:
        raise UploadValidationError("无法读取图片文件。") from exc

    width, height = image.size
    if width * height > settings.max_image_pixels:
        raise UploadValidationError(f"图片像素过高，最大允许 {settings.max_image_pixels} 像素。")
    return image.convert("RGB")


def image_to_model_data_url(image: Image.Image, settings: Settings) -> str:
    model_img = image.copy().convert("RGB")
    model_img.thumbnail((settings.max_model_image_side, settings.max_model_image_side))
    buf = io.BytesIO()
    model_img.save(buf, format="JPEG", quality=85, optimize=True)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

