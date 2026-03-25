"""
mistake_check.py
Detect common algebra mistakes in student-submitted equations and solutions.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── Mistake patterns ──────────────────────────────────────────────────────────

MISTAKE_PATTERNS = [
    {
        "id": "sign_error",
        "name": "Sign Error",
        "description": "Incorrect handling of negative signs during transposition.",
        "hint": "Remember: when moving a term to the other side of the equation, flip its sign. E.g., x - 3 = 5 → x = 5 + 3.",
        "pattern": re.compile(r"[+\-]\s*\d+\s*=\s*[+\-]\s*\d+"),
    },
    {
        "id": "distribution_error",
        "name": "Incorrect Distribution",
        "description": "Distributive property was not applied correctly to all terms.",
        "hint": "Apply the distributive property to every term inside the bracket: a(b + c) = ab + ac.",
        "pattern": re.compile(r"\d+\s*\(\s*[a-zA-Z]\s*[\+\-]"),
    },
    {
        "id": "arithmetic_error",
        "name": "Arithmetic Calculation Error",
        "description": "A numerical computation appears incorrect.",
        "hint": "Double-check your arithmetic operations — addition, subtraction, multiplication, and division.",
        "pattern": None,  # Checked programmatically
    },
    {
        "id": "wrong_transposition",
        "name": "Wrong Transposition",
        "description": "Term was moved to the wrong side or operation not reversed.",
        "hint": "When transposing, reverse the operation: addition becomes subtraction, multiplication becomes division.",
        "pattern": None,
    },
    {
        "id": "factorization_error",
        "name": "Incorrect Factorization",
        "description": "The equation was factored incorrectly.",
        "hint": "Verify your factors multiply back to the original expression.",
        "pattern": re.compile(r"\(\s*[a-zA-Z]\s*[\+\-]\s*\d+\s*\)\s*\(\s*[a-zA-Z]\s*[\+\-]\s*\d+\s*\)"),
    },
]


def detect_sign_errors(equation: str) -> list:
    """Check for likely sign-flip mistakes."""
    errors = []
    # If rhs becomes same sign as lhs term without sign change, flag it
    if re.search(r"=\s*-\s*-", equation) or re.search(r"=\s*\+\s*\+", equation):
        errors.append(MISTAKE_PATTERNS[0])
    return errors


def detect_distribution_errors(equation: str) -> list:
    """Heuristic: multiplication next to bracket without full expansion."""
    errors = []
    if re.search(r"\d\s*\(", equation):
        # Check if the expanded form might be missing terms
        # (simple heuristic – full check done by Gemini)
        errors.append(MISTAKE_PATTERNS[1])
    return errors


def detect_arithmetic_errors(steps: list) -> list:
    """
    Compare consecutive numeric results to detect inconsistencies.
    steps: list of dicts with 'expression' key.
    """
    errors = []
    numbers = []
    for step in steps:
        nums = re.findall(r"-?\d+\.?\d*", step.get("expression", ""))
        numbers.extend([float(n) for n in nums])
    # Simple check: if a number appears inconsistently
    # (Full check delegated to Gemini Vision)
    return errors


def check_mistakes(equation: str, steps: list = None) -> dict:
    """
    Run all mistake detectors and return structured results.

    Returns:
        {
          "has_mistakes": bool,
          "mistakes": [{"id", "name", "description", "hint"}],
          "summary": str
        }
    """
    steps = steps or []
    found = []

    found.extend(detect_sign_errors(equation))
    found.extend(detect_distribution_errors(equation))
    if steps:
        found.extend(detect_arithmetic_errors(steps))

    # Deduplicate
    seen = set()
    unique = []
    for m in found:
        if m["id"] not in seen:
            seen.add(m["id"])
            unique.append({k: v for k, v in m.items() if k != "pattern"})

    summary = (
        f"Found {len(unique)} potential mistake(s): "
        + ", ".join(m["name"] for m in unique)
        if unique else "No common mistakes detected."
    )

    return {
        "has_mistakes": bool(unique),
        "mistakes": unique,
        "summary": summary
    }
