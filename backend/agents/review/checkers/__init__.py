"""Checkers — pluggable review checkers.

Each checker is a callable that takes (context, diagnosis, prescription) and returns
a list of findings. New checkers can be added by creating a module in this package
and registering it in the CHECKERS dict.
"""

from typing import Any, Callable

# Checker type: function(context, diagnosis, prescription) -> list[dict]
CheckerFn = Callable[..., list[dict[str, Any]]]

# Registry of all available checkers
CHECKERS: dict[str, CheckerFn] = {}


def register_checker(name: str):
    """Decorator to register a checker."""
    def decorator(fn: CheckerFn) -> CheckerFn:
        CHECKERS[name] = fn
        return fn
    return decorator


def run_all_checkers(context: dict, diagnosis: dict, prescription: dict) -> list[dict]:
    """Run all registered checkers and aggregate findings."""
    all_findings: list[dict] = []
    for name, checker in CHECKERS.items():
        try:
            findings = checker(context, diagnosis, prescription)
            all_findings.extend(findings)
        except Exception as e:
            all_findings.append({
                "checker": name,
                "error": str(e),
                "severity": "error",
            })
    return all_findings
