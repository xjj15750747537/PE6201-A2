"""Read-only D0 fixture-data profiler for PE6201 Problem B.

It does not route cases, generate labels, call a model, or write booking records.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data_B"

def load_json(filename: str) -> Any:
    with (DATA_DIRECTORY / filename).open(encoding="utf-8") as source:
        return json.load(source)

def value(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        if key in row:
            return str(row[key])
    raise KeyError(f"Expected one of {keys} in {row!r}")

def main() -> None:
    referrals = load_json("referrals.json")
    specialties = load_json("specialties.json")
    patients = load_json("patients.json")
    contacts = load_json("contacts.json")
    slots = load_json("clinic_slots.json")
    bands = load_json("urgency_bands.json")
    as_of = load_json("as_of.json")

    specialty_ids = {value(row, "specialty", "specialty_code", "code") for row in specialties}
    patient_ids = {value(row, "patient_id") for row in patients}
    contact_ids = {value(row, "patient_id") for row in contacts}

    unresolved_specialties, unresolved_patients, missing_contacts = [], [], []
    for referral in referrals:
        case_id = value(referral, "referral_id", "case_id")
        if value(referral, "specialty", "specialty_code") not in specialty_ids:
            unresolved_specialties.append(case_id)
        patient_id = value(referral, "patient_id")
        if patient_id not in patient_ids:
            unresolved_patients.append(case_id)
        if patient_id not in contact_ids:
            missing_contacts.append(case_id)

    print("D0 fixture-data profile — Problem B")
    print(f"As-of date: {as_of.get('as_of', '<missing>')}")
    print(f"Referrals: {len(referrals)} | Specialties: {len(specialties)} | Patients: {len(patients)}")
    print(f"Contacts: {len(contacts)} | Clinic slots: {len(slots)} | Urgency bands: {len(bands)}")
    print(f"Unresolved specialty references: {unresolved_specialties or 'none'}")
    print(f"Unresolved patient references: {unresolved_patients or 'none'}")
    print(f"Referrals without contact records: {missing_contacts or 'none'}")
    print("Evidence map: referrals -> specialties -> patients -> urgency_bands -> clinic_slots.")
    print("Contacts are reached directly from referral.patient_id.")
    print("Routing, labels, booking, and model calls are intentionally out of scope.")

if __name__ == "__main__":
    main()
