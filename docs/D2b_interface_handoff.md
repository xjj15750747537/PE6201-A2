# D2(b) descriptor handoff — canonical root runner

The submit-and-run path for Problem B is the repository root:

```text
run_eval.py -> agent.py -> tools.py
```

`src/` remains a D4/D6 workbook-support module. It is not the agent invoked
by `run_eval.py` and must not be treated as a second submission runner.

## Callable Problem B tools

The full six-field contracts are the dictionaries in `tools.py`. The live
prompt is built from exactly these six callable tools:

| Tool | Role | Write-like? |
| --- | --- | --- |
| `get_referral` | Read the referral record. | No |
| `check_referral_criteria` | Report hostile instruction text, red flags, specialty fit, missing tests, and urgency. | No |
| `lookup_patient` | Read existing appointments for the duplicate check. | No |
| `as_of` | Read the fixed date used for urgency windows. | No |
| `get_clinic_slots` | Read legal available slots in a named band/window. | No |
| `book_slot` | Record the simulated booking. It is the only gated action. | Yes |

`check_referral_criteria` reports facts; it does not make a clinical
decision. The routing order is: hostile instruction, red flag, wrong
department, missing mandatory test, duplicate appointment, then slot search.
The code layer also blocks a booking if hostile free text is detected, even if
a live model tries to skip the normal criteria call.

## v1 -> v2 experiment

Both versions use the same function names and argument names.

- **v1** provides deliberately generic six-field descriptions. It is the
  baseline: callable, but it does not explain domain failures or routing.
- **v2** provides the detailed descriptions in `tools.py`: exact input and
  output shapes, empty/None meaning, urgency-band constraint, and gate
  placement.

The version is selected by `config.PROMPT_VERSION` or at the command line:

```bash
python run_eval.py --prompt --prompt-version v1
python run_eval.py --prompt --prompt-version v2
```

The command prints the exact system prompt and its rough token size. A live
D5(b) comparison must record the version, model, real provider token counts,
trial count, pass rate, and price source. The scripted D5(a) run is not valid
evidence that either descriptor version improves a live model.

## Return-shape completion

`get_clinic_slots` now changes its real Python payload as well as its
descriptor: v1 returns a `{query, matching_slots, match_count}` dictionary
with all matching rows (including full slots), while v2 returns only free
slot rows in a list. `agent.run_case(..., prompt_version=...)` passes the
selected version to the tool dispatcher, so this is not descriptor-only.

Run `python scripts/measure_d2b_return_shape.py` to produce
`results/d2b_return_shape_measurement.json`. It records each concrete return
type, byte size, deterministic JSON token proxy, scripted 93-trial pass rate,
and hostile-case guardrail result for both versions.

The runner records provider usage per model response, not per individual tool
payload. Do not invent provider-measured per-tool token counts or use a
payload-size estimate as D5(b) or D6 cost evidence. A live v1/v2 claim needs
two same-model, same-93-trial batteries after this change, saved as separate
immutable fragments with provider-reported aggregate tokens.
