"""
ocr_utils.py
Image preprocessing and OCR-based symbol extraction using EasyOCR / OpenCV.
"""

import cv2
import numpy as np
from PIL import Image
import easyocr
import logging
import os

logger = logging.getLogger(__name__)

_reader = None

SYMBOL_MAP = {
    chr(215): r"\times",
    chr(247): r"\div",
    chr(177): r"\pm",
    chr(8804): r"\leq",
    chr(8805): r"\geq",
    chr(8800): r"\neq",
    chr(8730): r"\sqrt",
    chr(8734): r"\infty",
    chr(960): r"\pi",
    chr(178): "^{2}",
    chr(179): "^{3}",
}


def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def preprocess_image(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    kernel = np.ones((1, 1), np.uint8)
    return cv2.dilate(thresh, kernel, iterations=1)


def extract_text_from_image(image_path: str) -> str:
    try:
        processed = preprocess_image(image_path)
        results = get_reader().readtext(processed, detail=0, paragraph=True)
        return " ".join(results).strip()
    except Exception as e:
        logger.error("OCR failed: %s", e)
        return ""


def map_symbols_to_latex(text: str) -> str:
    for char, latex in SYMBOL_MAP.items():
        text = text.replace(char, latex)
    return text


def validate_image(image_path: str, max_mb: float = 5.0) -> bool:
    if not os.path.exists(image_path):
        return False
    if os.path.getsize(image_path) / (1024 * 1024) > max_mb:
        return False
    try:
        with Image.open(image_path) as im:
            im.verify()
        return True
    except Exception:
        return False


def resize_image(image_path: str, max_dim: int = 1024) -> str:
    with Image.open(image_path) as im:
        w, h = im.size
        if max(w, h) <= max_dim:
            return image_path
        scale = max_dim / max(w, h)
        resized = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        base, ext = os.path.splitext(image_path)
        out = f"{base}_resized{ext}"
        resized.save(out)
        return out
