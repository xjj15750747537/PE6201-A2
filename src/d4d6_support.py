"""Small, deterministic helpers for the D4-D6 owner workbooks.

The module intentionally does not call a model.  D4 supplies the observed
outcomes, D5 supplies measured token counts, and D6 derives the cost table.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


REQUIRED_CASE_FIELDS = {
    "case_id",
    "is_negative",
    "wrong_behaviour_to_catch",
    "expected",
    "check_type",
}


def validate_cases(cases: list[dict[str, object]]) -> list[str]:
    """Return plain-English validation issues; an empty list means ready."""
    issues: list[str] = []
    if len(cases) < 51:
        issues.append("D4 needs at least 51 cases under the lecturer's current instruction.")
    negative_count = sum(bool(case.get("is_negative")) for case in cases)
    if negative_count < 2:
        issues.append("D4 needs at least two negative cases; six to ten is recommended.")
    seen: set[str] = set()
    for row, case in enumerate(cases, start=1):
        missing = REQUIRED_CASE_FIELDS - set(case)
        if missing:
            issues.append(f"Row {row} is missing: {', '.join(sorted(missing))}.")
        case_id = str(case.get("case_id", ""))
        if not case_id:
            issues.append(f"Row {row} needs a case_id.")
        elif case_id in seen:
            issues.append(f"case_id {case_id} appears more than once.")
        seen.add(case_id)
        if case.get("check_type") not in {"code", "judgement"}:
            issues.append(f"{case_id or f'Row {row}'} needs check_type code or judgement.")
        if case.get("is_negative") and not str(case.get("wrong_behaviour_to_catch", "")).strip():
            issues.append(f"{case_id or f'Row {row}'} must name the wrong behaviour it catches.")
    return issues


def trial_count(case: dict[str, object]) -> int:
    """Use the brief's one ordinary / three negative trial rule."""
    return 3 if bool(case.get("is_negative")) else 1


def code_check(expected: dict[str, object], observed: dict[str, object]) -> bool:
    """Compare only explicitly labelled expected values, never reason strings."""
    return all(observed.get(key) == value for key, value in expected.items())


def pass_rate(results: Iterable[dict[str, object]]) -> dict[str, float | int]:
    rows = list(results)
    total = len(rows)
    passed = sum(bool(row.get("passed")) for row in rows)
    return {"passed": passed, "trials": total, "pass_rate": passed / total if total else 0.0}


@dataclass(frozen=True)
class CostInputs:
    input_tokens: float
    output_tokens: float
    turns: float
    input_price_per_million: float
    output_price_per_million: float
    retrieval_and_tool_fees: float
    success_rate: float
    failure_cost: float
    fixed_monthly_cost: float
    monthly_volume: int


def cost_summary(inputs: CostInputs) -> dict[str, float]:
    """Implement the three-layer D6 baseline with no model-specific discounts."""
    variable = (
        inputs.input_tokens / 1_000_000 * inputs.input_price_per_million
        + inputs.output_tokens / 1_000_000 * inputs.output_price_per_million
        + inputs.retrieval_and_tool_fees
    )
    expected_fallback = (1 - inputs.success_rate) * inputs.failure_cost
    per_successful_task = variable + expected_fallback
    return {
        "turns": inputs.turns,
        "layer_1_variable": variable,
        "layer_2_expected_fallback": expected_fallback,
        "layer_3_fixed_monthly": inputs.fixed_monthly_cost,
        "cost_per_successful_task": per_successful_task,
        "monthly_cost": per_successful_task * inputs.monthly_volume + inputs.fixed_monthly_cost,
    }


def sensitivity(inputs: CostInputs) -> list[dict[str, float]]:
    """Return the required success-rate minus/plus ten-point sensitivity table."""
    rows: list[dict[str, float]] = []
    for rate in (max(0.0, inputs.success_rate - 0.10), inputs.success_rate, min(1.0, inputs.success_rate + 0.10)):
        varied = CostInputs(**{**inputs.__dict__, "success_rate": rate})
        row = cost_summary(varied)
        row["success_rate"] = rate
        rows.append(row)
    return rows


def break_even_success_rate(cheap_run_cost: float, expensive_all_in_cost: float, failure_cost: float) -> float:
    """Return the D6 cheap-model success threshold; inputs must be positive."""
    if failure_cost <= 0:
        raise ValueError("failure_cost must be positive.")
    return 1 - (expensive_all_in_cost - cheap_run_cost) / failure_cost
