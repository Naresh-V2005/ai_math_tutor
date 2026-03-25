"""
tests/test_response_utils.py
Unit tests for response utility functions.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from modules.response_utils import clean_json_response, success_response, error_response, generate_filename, confidence_label


class TestCleanJsonResponse:
    def test_clean_json(self):
        raw = '{"key": "value"}'
        result = clean_json_response(raw)
        assert result["key"] == "value"

    def test_strips_markdown_fences(self):
        raw = '```json\n{"key": "value"}\n```'
        result = clean_json_response(raw)
        assert result.get("key") == "value"

    def test_invalid_json_returns_error(self):
        result = clean_json_response("not json at all!!")
        assert "error" in result


class TestSuccessResponse:
    def test_structure(self):
        r = success_response({"x": 1})
        assert r["status"] == "success"
        assert r["data"]["x"] == 1
        assert "timestamp" in r


class TestErrorResponse:
    def test_structure(self):
        r = error_response("Something went wrong", "details here")
        assert r["status"] == "error"
        assert r["message"] == "Something went wrong"


class TestGenerateFilename:
    def test_has_extension(self):
        name = generate_filename("solution", "pdf")
        assert name.endswith(".pdf")

    def test_contains_prefix(self):
        name = generate_filename("math_result", "docx")
        assert "math_result" in name


class TestConfidenceLabel:
    def test_very_high(self):
        assert confidence_label(0.95) == "Very High"

    def test_low(self):
        assert confidence_label(0.3) == "Low"

    def test_very_low(self):
        assert confidence_label(0.1) == "Very Low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
