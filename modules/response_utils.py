"""
response_utils.py
JSON response formatting and filename generation utilities.
"""

import json
import re
import os
from datetime import datetime


def clean_json_response(raw: str) -> dict:
    """
    Strip markdown code fences and parse JSON from a Gemini API response.
    Returns parsed dict or {"error": ..., "raw": raw} on failure.
    """
    # Remove ```json ... ``` or ``` ... ```
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}", "raw": raw}


def success_response(data: dict, message: str = "Success") -> dict:
    """Standard success response wrapper."""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def error_response(message: str, details: str = "") -> dict:
    """Standard error response wrapper."""
    return {
        "status": "error",
        "message": message,
        "details": details,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def generate_filename(prefix: str, extension: str) -> str:
    """
    Generate a unique filename using timestamp.
    Example: math_solution_20250601_153045.pdf
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prefix = re.sub(r"[^a-zA-Z0-9_\-]", "_", prefix)
    return f"{safe_prefix}_{ts}.{extension.lstrip('.')}"


def confidence_label(score: float) -> str:
    """Convert a 0-1 confidence score to a human-readable label."""
    if score >= 0.9:
        return "Very High"
    elif score >= 0.75:
        return "High"
    elif score >= 0.5:
        return "Medium"
    elif score >= 0.25:
        return "Low"
    return "Very Low"
