# D4 case catalogue - Problem B

The D4 set contains 55 labelled referrals: 15 shipped cases and 40 team-authored cases (`REF-6001` through `REF-6040`). This follows the lecturer's current instruction to use more than 50 cases.

## Reproduction assets

Run `python3 scripts/make_fixtures_B.py`, then `python3 scripts/check_my_data.py`. The generator writes `data_B/`; the checker verifies fixture links, shipped-row fingerprints, duplicate IDs, and one answer-key label per referral.

`expected_outcomes_B.json` is the ground truth. Labels were written from the Problem B routing table before any agent run. The generator does not derive outcomes.

## Coverage

The team cases include routine, soon, and urgent bookings; specialties with zero, one, and two mandatory tests; named-missing-test requests; future same-specialty duplicates; no-slot-in-window escalation; and two hostile free-text escalations. The 55-row workbook has six designated judgement checks for evidence-trail quality; all rows retain code checks for their fixed outcome fields.

## Trial rule

Run ordinary cases once and negative cases three times, each from clean state. Report each model's pass rate with its trial count. Do not report a final pass rate until D3 is integrated and the full set is rerun.
