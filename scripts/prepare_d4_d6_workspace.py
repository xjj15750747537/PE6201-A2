"""Create editable D4-D6 templates for non-technical assignment owners."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
TEMPLATES.mkdir(exist_ok=True)

labels = json.loads((ROOT / "expected_outcomes_B.json").read_text(encoding="utf-8"))
referrals = {
    row["referral_id"]: row
    for row in json.loads((ROOT / "data_B" / "referrals.json").read_text(encoding="utf-8"))
}

case_rows = []
for number, label in enumerate(labels, start=1):
    case_id = label["case_id"]
    decision = label["expected_decision"]
    negative = decision != "book"
    expected = {"decision": decision}
    for field in ("trigger", "missing", "booked"):
        if field in label:
            expected[field] = label[field]
    # A small, named subset receives a human or independent-judge evidence check;
    # every case still has its outcome checked by code.
    judgement = number in {2, 5, 12, 18, 24, 31}
    case_rows.append(
        {
            "case_id": case_id,
            "owner": "ASSIGN_OWNER",
            "is_negative": negative,
            "wrong_behaviour_to_catch": (
                "Do not book or stage a booking when the correct outcome is "
                f"{decision}: {label.get('trigger') or label.get('missing')}."
                if negative else ""
            ),
            "fixture_note": referrals[case_id]["clinical_summary"],
            "expected": expected,
            "check_type": "judgement" if judgement else "code",
            "judgement_question": (
                "Does the stated reason and evidence trail support the labelled outcome?"
                if judgement else ""
            ),
        }
    )

d5_models = {
    "backend": "scripted",
    "final_prompt_version": "v2",
    "live_models": [
        {"owner": "MEMBER_1", "model": "REPLACE_WITH_CHEAP_MODEL", "family": "REPLACE", "price_tier": "cheap"},
        {"owner": "MEMBER_2", "model": "REPLACE_WITH_DIFFERENT_FAMILY", "family": "REPLACE", "price_tier": "mid"},
        {"owner": "MEMBER_3", "model": "REPLACE_WITH_THIRD_FAMILY", "family": "REPLACE", "price_tier": "frontier"},
    ],
    "v1_comparison": {"owner": "MEMBER_4", "same_model_as": "MEMBER_1", "prompt_version": "v1"},
}

d6_inputs = {
    "input_tokens": "MEASURED_FROM_D5",
    "output_tokens": "MEASURED_FROM_D5",
    "turns": "MEASURED_FROM_D4_D5",
    "input_price_per_million": "MODEL_LIST_PRICE",
    "output_price_per_million": "MODEL_LIST_PRICE",
    "retrieval_and_tool_fees": 0.0,
    "success_rate": "MEASURED_FROM_D4",
    "failure_cost": "PROBLEM_B_ESCALATION_LABOUR_COST",
    "fixed_monthly_cost": "TEAM_ASSUMPTION",
    "monthly_volume": "PROBLEM_B_MONTHLY_VOLUME",
}

for name, data in {
    "d4_cases_template.json": case_rows,
    "d5_models_template.json": d5_models,
    "d6_inputs_template.json": d6_inputs,
}.items():
    (TEMPLATES / name).write_text(json.dumps(data, indent=2), encoding="utf-8")

print(f"Created templates/d4_cases_template.json ({len(case_rows)} real labelled rows; {sum(row['is_negative'] for row in case_rows)} negative cases).")
print("Created templates/d5_models_template.json.")
print("Created templates/d6_inputs_template.json.")
print("Replace every REPLACE_ or MEASURED_ value before reporting a result.")
