# D3 guardrail layer — Problem B

The guardrail layer is deterministic Python. A model cannot switch it off by
changing its wording.

| Guard | Placement | Safe outcome |
| --- | --- | --- |
| Hostile free-text detector | Immediately after `check_referral_criteria`, and again before `book_slot`. | `escalate` with trigger `instruction_in_referral_free_text`; no slot query or booking after detection. |
| Step cap | Before each tool-call turn. | Loud `escalate` record naming `step_cap`. |
| Token ceiling | After each backend response's usage is recorded. | Loud `escalate` record naming `budget_ceiling`. |
| Action de-duplication | Before every tool call. Nested arguments are normalised before comparison. | Loud `escalate` record naming `duplicate_action`. |
| Autonomy gate | Immediately before `book_slot`, the only write-like operation. | With `confirm`, the booking is held unless approval is supplied. |

The hostile-text detector deliberately uses narrow instruction/tool-imitation
markers. It is not a clinical red-flag detector. The clinical protocol remains
in `check_referral_criteria`; the D3 check makes the failure mode independent
of a live model's willingness to follow that protocol.

The root regression tests cover the four hostile fixtures (`REF-5703`,
`REF-5711`, `REF-6039`, `REF-6040`), safe negated red-flag phrases, and nested
duplicate-action arguments.
