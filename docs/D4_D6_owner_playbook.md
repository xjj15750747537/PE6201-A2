# D4-D6 owner playbook

This playbook is designed for team members who do not need to edit Python. Run the commands in the D4-D6 Colab workbook from top to bottom, then fill only the template files named in each step.

## D4: evaluation set

1. Run the template cell. It creates the 55 real, labelled Problem B rows: the 15 shipped cases plus 40 team-authored cases.
2. Keep the generator, generated `data_B/`, and `expected_outcomes_B.json` together. Do not edit or delete a shipped row.
3. Every negative case states the unsafe booking behaviour it prevents. Keep ordinary cases at one trial and negative cases at three trials.
4. Use `code` for fixed fields such as decision, trigger, clinic, date, time, and whether the staged action happened once. Use `judgement` only when a person or independent judge must assess a reason or evidence trail.
5. Do not report a final pass rate until D3 is integrated. Re-run the full set from clean state after D3 changes the guardrail outcome or gate.

## D5: model battery

1. Run the scripted backend first; it is the default and must remain reproducible without a key.
2. Fill `templates/d5_models_template.json` with at least three different model families across at least two price tiers.
3. All owners use the same final prompt version (v2), same evaluation cases, and same commit. Only the model string changes.
4. One owner runs v1 on one model already in the battery. Do not run v1 across every model.
5. Do not spend live-model credits before D3 is integrated and D4 labels are final.

## D6: cost model

1. Fill `templates/d6_inputs_template.json` only with measured D4 success rates and measured D5 token counts.
2. Use the three-layer baseline: variable token/tool cost, expected human fallback, and fixed monthly cost.
3. Report sensitivity at success rate minus 10 points, baseline, and plus 10 points.
4. Calculate the cheap-model break-even success rate after at least two live models have measured results.

## D3 dependency

D3 does not block drafting D4 cases, D5 assignments, or the D6 calculator. It **does** block final reported D4 pass rates, final D5 live battery results, and D6 cost conclusions because its step cap, budget ceiling, action de-duplication, and autonomy gate can change an outcome or a staged action. After D3 is merged, run the entire D4-D6 sequence again from clean state.
