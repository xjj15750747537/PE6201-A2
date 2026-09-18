"""Measure the concrete D2(b) return-shape rewrite without a paid model call."""

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import tools
from harness import load_cases, run_set


OUTPUT = ROOT / "results" / "d2b_return_shape_measurement.json"
HOSTILE_CASES = ["REF-5703", "REF-5711", "REF-6039", "REF-6040"]
REPRESENTATIVE_ARGS = {
    "specialty": "OPH",
    "band": "routine",
    "from": "2026-09-01",
    "to": "2026-12-31",
}


def serialized_payload_token_proxy(value):
    """Return a deterministic lexical proxy for a JSON tool observation.

    This is intentionally not provider token usage: the project records that
    only for complete model responses in D5(b).  It simply makes the concrete
    v1/v2 returned payloads comparable and reproducible.
    """
    text = json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))
    return len(re.findall(r"[A-Za-z0-9_]+|[^\sA-Za-z0-9_]", text))


def summary(rows):
    return {"trials": len(rows), "passed": sum(bool(row["passed"])
                                                for row in rows)}


def main():
    report = {
        "measurement_kind": "deterministic serialized-JSON lexical token proxy",
        "warning": (
            "This is not provider-reported token usage, a live-model result, "
            "or D5/D6 cost evidence."
        ),
        "representative_call_args": REPRESENTATIVE_ARGS,
        "versions": {},
    }
    for version in ("v1", "v2"):
        payload = tools.call("B", "get_clinic_slots", REPRESENTATIVE_ARGS,
                             return_shape_version=version)
        full_rows, _ = run_set(load_cases(), prompt_version=version)
        hostile_rows, _ = run_set(HOSTILE_CASES, prompt_version=version)
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                separators=(",", ":"))
        report["versions"][version] = {
            "return_type": type(payload).__name__,
            "payload_bytes": len(serialized.encode("utf-8")),
            "payload_token_proxy": serialized_payload_token_proxy(payload),
            "scripted_full_set": summary(full_rows),
            "scripted_hostile_guardrails": summary(hostile_rows),
        }
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("Wrote", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
