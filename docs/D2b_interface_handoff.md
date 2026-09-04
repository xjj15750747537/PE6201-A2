# D2(b) interface handoff: four tool contracts

Interface version: 0.1  
Audience: D2(b) tool-descriptor owner  
Status: implementation-ready baseline. Keep names and field names unchanged unless the team records a versioned change.

This handoff freezes the four minimal tools selected in D2(a). All returned data is fixture-backed and non-identifying. No tool creates a real booking or sends a patient message.

## 1. get_referral_context

Purpose: retrieve the named referral with the specialty policy data needed to begin the case.

Input: `{"referral_id": "string"}`

Output:

    {
      "referral": {"referral_id": "string", "patient_id": "string", "specialty": "string", "date_received": "YYYY-MM-DD", "clinical_summary": "string", "tests_attached": ["string"]},
      "specialty": {"code": "string", "name": "string", "mandatory_tests": [{"code": "string", "name": "string"}], "red_flag_terms": ["string"], "treats": ["string"]},
      "as_of": "YYYY-MM-DD",
      "urgency_bands": ["urgent", "soon", "routine"]
    }

## 2. get_existing_appointments

Purpose: retrieve future appointments so deterministic code can detect a same-specialty duplicate.

Input: `{"patient_id": "string"}`

Output:

    {"patient_id": "string", "existing_appointments": [{"specialty": "string", "clinic": "string", "date": "YYYY-MM-DD", "time": "HH:MM"}]}

An empty list is valid. The tool reports facts only; it does not decide duplication.

## 3. find_eligible_slots

Purpose: return available candidate slots for one specialty and urgency band.

Input: `{"specialty": "string", "urgency_band": "urgent | soon | routine"}`

Output:

    {"specialty": "string", "urgency_band": "urgent | soon | routine", "slots": [{"clinic": "string", "specialty": "string", "band": "urgent | soon | routine", "date": "YYYY-MM-DD", "time": "HH:MM", "capacity_remaining": 1}]}

The implementation returns only slots with positive capacity that match the requested specialty and urgency window, ordered by date then time.

## 4. stage_booking_intent

Purpose: record a local staged intent after deterministic booking gates pass. It is the only write-like operation.

Input:

    {"referral_id": "string", "patient_id": "string", "specialty": "string", "slot": {"clinic": "string", "date": "YYYY-MM-DD", "time": "HH:MM"}, "evidence": ["string"]}

Output:

    {"status": "staged", "booking_intent_id": "string", "gate": "passed", "contact_method": "sms | phone | email"}

The tool must not create a real appointment, expose contact details, or send a notification. Call it only after policy, duplicate, capacity, and urgency gates pass.

## D2(c) dependency rule

get_existing_appointments and find_eligible_slots may run in parallel only after get_referral_context completes. stage_booking_intent always runs alone after its gates are evaluated.
