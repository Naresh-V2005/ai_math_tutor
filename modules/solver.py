"""
solver.py
Parse LaTeX/text equations and solve them using SymPy.
Returns structured step-by-step solutions.
"""

import re
import logging
from sympy import (
    symbols, Eq, solve, simplify, expand, factor,
    latex, sympify, SympifyError, sqrt, Rational
)
from sympy.parsing.latex import parse_latex

logger = logging.getLogger(__name__)

x, y, z = symbols("x y z")


def _clean_latex(equation: str) -> str:
    """Strip display math delimiters."""
    return equation.strip().lstrip("$").rstrip("$").strip()


def _parse_equation(equation: str):
    """
    Try to parse as LaTeX, fall back to sympify.
    Returns a SymPy Eq object or expression.
    """
    cleaned = _clean_latex(equation)
    try:
        if "=" in cleaned:
            lhs_str, rhs_str = cleaned.split("=", 1)
            lhs = parse_latex(lhs_str.strip())
            rhs = parse_latex(rhs_str.strip())
            return Eq(lhs, rhs)
        return parse_latex(cleaned)
    except Exception:
        pass
    # Fallback: sympify
    try:
        if "=" in cleaned:
            lhs_str, rhs_str = cleaned.split("=", 1)
            lhs = sympify(lhs_str.strip())
            rhs = sympify(rhs_str.strip())
            return Eq(lhs, rhs)
        return sympify(cleaned)
    except SympifyError as e:
        raise ValueError(f"Cannot parse equation: {equation}") from e


def solve_equation(equation: str) -> dict:
    """
    Solve an equation and return steps + final answer.

    Returns:
        {
          "equation": str,
          "latex_equation": str,
          "steps": [{"step": int, "description": str, "expression": str}],
          "solution": list | str,
          "error": str | None
        }
    """
    steps = []
    try:
        eq = _parse_equation(equation)
        steps.append({
            "step": 1,
            "description": "Parsed equation",
            "expression": f"${latex(eq)}$"
        })

        # Expand
        if hasattr(eq, "lhs"):
            expanded = Eq(expand(eq.lhs), expand(eq.rhs))
            steps.append({
                "step": 2,
                "description": "Expand both sides",
                "expression": f"${latex(expanded)}$"
            })
            lhs_simplified = simplify(eq.lhs - eq.rhs)
            steps.append({
                "step": 3,
                "description": "Move all terms to one side",
                "expression": f"${latex(lhs_simplified)} = 0$"
            })
            solution = solve(eq, x)
        else:
            simplified = simplify(eq)
            steps.append({
                "step": 2,
                "description": "Simplified expression",
                "expression": f"${latex(simplified)}$"
            })
            solution = [simplified]

        steps.append({
            "step": len(steps) + 1,
            "description": "Apply algebraic operations to isolate x",
            "expression": f"Solving for x..."
        })
        steps.append({
            "step": len(steps) + 1,
            "description": "Final solution",
            "expression": ", ".join(f"$x = {latex(s)}$" for s in solution)
                          if solution else "No real solution"
        })

        return {
            "equation": equation,
            "latex_equation": f"${latex(eq)}$",
            "steps": steps,
            "solution": [str(s) for s in solution],
            "error": None
        }

    except Exception as exc:
        logger.error("Solver error: %s", exc)
        return {
            "equation": equation,
            "latex_equation": equation,
            "steps": steps,
            "solution": [],
            "error": str(exc)
        }


def simplify_expression(expression: str) -> dict:
    """Simplify a mathematical expression."""
    try:
        expr = sympify(_clean_latex(expression))
        result = simplify(expr)
        return {"original": expression, "simplified": str(result), "latex": f"${latex(result)}$", "error": None}
    except Exception as e:
        return {"original": expression, "simplified": "", "latex": "", "error": str(e)}
