"""Create editable D4-D6 templates for non-technical assignment owners."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
TEMPLATES.mkdir(exist_ok=True)

case_rows = []
for number in range(1, 41):
    negative = 33 <= number <= 40
    case_rows.append(
        {
            "case_id": f"TEAM-B-{number:02d}",
            "owner": "ASSIGN_OWNER",
            "is_negative": negative,
            "wrong_behaviour_to_catch": "REPLACE_WITH_A_SPECIFIC_UNSAFE_ACTION" if negative else "",
            "fixture_note": "Describe the referral or added fixture record.",
            "expected": {"decision": "REPLACE_WITH_book_request_information_OR_escalate", "trigger": "REPLACE_WITH_GROUND_TRUTH_TRIGGER"},
            "check_type": "code",
            "judgement_question": "Leave blank for code checks; otherwise state the human/judge question.",
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

print("Created templates/d4_cases_template.json (40 rows; 8 negative cases).")
print("Created templates/d5_models_template.json.")
print("Created templates/d6_inputs_template.json.")
print("Replace every REPLACE_ or MEASURED_ value before reporting a result.")
