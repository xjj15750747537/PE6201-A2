# D2(b) and D3 integration handoff

## Files changed

- `tools.py`: added v1/v2 descriptor sets, hostile free-text detection, and
  negation-aware red-flag matching for the existing 55 fixtures.
- `prompt.py`, `config.py`, `agent.py`: select and record prompt version; pass
  the selected descriptor set to live calls; stop safely after hostile text.
- `guardrails.py`: normalise nested arguments before duplicate detection.
- `problem_b_scripts.py`, `backends.py`, `run_eval.py`: provide a complete
  fixture-derived reproducible D5(a) battery and capture provider-reported
  token usage for live calls.
- `harness.py`: grade exact missing-test names as well as decision, trigger,
  and booking.
- `tests/test_submission_runner.py`: root-runner regression coverage.

## Verified checkpoint

```text
fixture check: 55 labelled referrals, PASS
unit tests: 16 passed
scripted battery: 93 / 93 trials passed
```

The scripted result is not a live-model accuracy, token, or cost claim. Use
the D5(b) procedure for real models and preserve the provider's measured usage
metadata.
