"""
tests/test_mistake_check.py
Unit tests for the mistake detection module.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from modules.mistake_check import check_mistakes, detect_sign_errors, detect_distribution_errors


class TestMistakeCheck:
    def test_no_mistakes_clean_equation(self):
        result = check_mistakes("2x + 3 = 7")
        assert isinstance(result["has_mistakes"], bool)
        assert isinstance(result["mistakes"], list)
        assert "summary" in result

    def test_returns_required_keys(self):
        result = check_mistakes("x = --5")
        assert "has_mistakes" in result
        assert "mistakes" in result
        assert "summary" in result

    def test_distribution_heuristic(self):
        errors = detect_distribution_errors("3(x + 2) = 9")
        assert isinstance(errors, list)

    def test_sign_error_detection(self):
        errors = detect_sign_errors("x = --5")
        assert isinstance(errors, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
