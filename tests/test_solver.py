"""
tests/test_solver.py
Unit tests for the SymPy equation solver module.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from modules.solver import solve_equation, simplify_expression


class TestSolveEquation:
    def test_simple_linear(self):
        result = solve_equation("2*x + 3 = 7")
        assert result["error"] is None
        assert "2" in str(result["solution"])

    def test_quadratic(self):
        result = solve_equation("x**2 - 5*x + 6 = 0")
        assert result["error"] is None
        assert len(result["solution"]) == 2

    def test_steps_present(self):
        result = solve_equation("x + 1 = 5")
        assert len(result["steps"]) > 0

    def test_invalid_equation(self):
        result = solve_equation("not_an_equation!!!")
        assert result["error"] is not None

    def test_no_solution(self):
        result = solve_equation("0 = 1")
        assert isinstance(result["solution"], list)


class TestSimplifyExpression:
    def test_simplify_zero(self):
        result = simplify_expression("x**2 - x**2")
        assert result["error"] is None
        assert result["simplified"] == "0"

    def test_expand(self):
        result = simplify_expression("(x+1)**2")
        assert result["error"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
