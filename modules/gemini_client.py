"""
gemini_client.py
Wrapper around Google Generative AI (Gemini 2.5 Flash) for image-to-LaTeX
conversion, equation solving prompts, and mistake detection.
"""

import os
import base64
import logging
import json
import re
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyCwXeCrcgP6VPLVLE9slu0thvfSf7a9NXE"))

MODEL_NAME = "gemini-2.5-flash"


def _get_model():
    return genai.GenerativeModel(MODEL_NAME)


def _encode_image(image_path: str) -> dict:
    """Encode image as base64 inline_data for Gemini."""
    suffix = Path(image_path).suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".webp": "image/webp"}
    mime = mime_map.get(suffix, "image/jpeg")
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return {"inline_data": {"mime_type": mime, "data": data}}


# ── Prompts ───────────────────────────────────────────────────────────────────

IMAGE_TO_LATEX_PROMPT = """
You are an expert mathematics OCR system. Analyze the provided image of an algebra problem.
Your task:
1. Identify ALL mathematical symbols, operators, variables, and numbers.
2. Convert the complete equation into valid LaTeX notation.
3. Return ONLY a JSON object with these keys:
   - "latex": the LaTeX string (e.g. "2x + 3 = 7")
   - "confidence": a float between 0 and 1
   - "notes": any observations about image quality or ambiguity

Return ONLY valid JSON. No preamble. No markdown fences.
"""

STEP_BY_STEP_PROMPT = """
You are an expert algebra tutor. Given the equation: {equation}

Provide a complete step-by-step solution. Return ONLY a JSON object:
{{
  "steps": [
    {{"step": 1, "description": "...", "expression": "..."}},
    ...
  ],
  "solution": ["x = ..."],
  "explanation": "brief summary"
}}

Be clear, educational, and suitable for high school students. Return ONLY valid JSON.
"""

MISTAKE_DETECTION_PROMPT = """
You are an algebra tutor reviewing a student's work. Given the equation: {equation}
And steps: {steps}

Identify common algebra mistakes. Return ONLY a JSON object:
{{
  "has_mistakes": true/false,
  "mistakes": [
    {{"name": "...", "description": "...", "hint": "..."}}
  ],
  "summary": "..."
}}

Return ONLY valid JSON. No preamble.
"""


def _clean_json(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return {"error": "JSON parse error", "raw": raw}


# ── Public API ────────────────────────────────────────────────────────────────

def image_to_latex(image_path: str, ocr_text: str = "") -> dict:
    """
    Send image + OCR text to Gemini and get LaTeX equation back.
    """
    try:
        model = _get_model()
        img_part = _encode_image(image_path)
        prompt = IMAGE_TO_LATEX_PROMPT
        if ocr_text:
            prompt += f"\n\nOCR pre-extracted text for reference: {ocr_text}"
        response = model.generate_content([prompt, img_part])
        return _clean_json(response.text)
    except Exception as e:
        logger.error("image_to_latex failed: %s", e)
        return {"latex": "", "confidence": 0.0, "notes": str(e), "error": str(e)}


def get_step_by_step_solution(equation: str) -> dict:
    """
    Ask Gemini for a step-by-step solution to the given equation.
    """
    try:
        model = _get_model()
        prompt = STEP_BY_STEP_PROMPT.format(equation=equation)
        response = model.generate_content(prompt)
        return _clean_json(response.text)
    except Exception as e:
        logger.error("get_step_by_step_solution failed: %s", e)
        return {"steps": [], "solution": [], "explanation": "", "error": str(e)}


def detect_mistakes_with_ai(equation: str, steps: list) -> dict:
    """
    Use Gemini to identify algebraic mistakes in student steps.
    """
    try:
        model = _get_model()
        steps_text = json.dumps(steps)
        prompt = MISTAKE_DETECTION_PROMPT.format(
            equation=equation, steps=steps_text)
        response = model.generate_content(prompt)
        return _clean_json(response.text)
    except Exception as e:
        logger.error("detect_mistakes_with_ai failed: %s", e)
        return {"has_mistakes": False, "mistakes": [], "summary": str(e), "error": str(e)}
