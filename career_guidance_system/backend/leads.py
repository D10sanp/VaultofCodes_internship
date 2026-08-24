"""
Lead qualification, classification, and storage (Sections 3 and 11 of the spec).

Storage strategy:
  - If Google Sheets credentials are configured (GOOGLE_SERVICE_ACCOUNT_JSON env var
    pointing to a service account key file, and GOOGLE_SHEET_ID env var), leads are
    appended to that Google Sheet via gspread.
  - Otherwise, leads are appended to a local `leads.csv` file so the system is fully
    runnable/testable without any Google credentials.

Duplicate/incomplete lead handling:
  - A lead is considered a duplicate if the same email OR phone number already exists
    in the store; duplicates are updated in place rather than creating a new row.
  - A lead is considered incomplete if it is missing name, a contact method
    (email or phone), or current_education; incomplete leads are not written to the
    sheet, and the API surfaces a clear reason back to the caller.
"""
from __future__ import annotations
import csv
import os
from pathlib import Path
from typing import Optional, Tuple

from models import LeadRecord, StudentProfile

CSV_PATH = Path(__file__).parent / "leads.csv"
CSV_FIELDS = list(LeadRecord.model_fields.keys())

QUALIFYING_DEGREE_MODES = {"Online Degree", "Distance Learning"}
QUALIFYING_COUNSELING_ANSWERS = {"Yes, I want counseling", "Yes, I want more information"}


# ---------------------------------------------------------------------------
# Qualification + classification (Sections 2, 3, 11)
# ---------------------------------------------------------------------------
def is_qualified_lead(profile: StudentProfile) -> bool:
    return (
        profile.degree_mode in QUALIFYING_DEGREE_MODES
        or profile.counseling_interest in QUALIFYING_COUNSELING_ANSWERS
    )


def classify_lead(profile: StudentProfile) -> str:
    """Section 11 - Lead Classification."""
    if profile.counseling_interest == "Yes, I want counseling":
        return "Counseling Interested"
    if profile.degree_mode == "Online Degree":
        return "Online Degree Lead"
    if profile.degree_mode == "Offline/Regular Degree":
        return "Offline Degree Lead"
    if profile.degree_mode == "Hybrid":
        return "Hybrid Degree Lead"
    if profile.degree_mode == "Distance Learning":
        return "Online Degree Lead"
    if profile.counseling_interest == "Yes, I want more information":
        return "Degree Explorer"
    if profile.degree_mode == "Not Sure Yet":
        return "Undecided"
    return "Career Guidance Only"


def is_complete(profile: StudentProfile) -> Tuple[bool, Optional[str]]:
    if not profile.name or not profile.name.strip():
        return False, "Missing name"
    if not profile.email and not profile.phone:
        return False, "Missing both email and phone"
    if not profile.current_education or not profile.current_education.strip():
        return False, "Missing current education"
    return True, None


# ---------------------------------------------------------------------------
# Storage backends
# ---------------------------------------------------------------------------
def _get_sheet():
    """Return a gspread worksheet if Google Sheets is configured, else None."""
    service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not service_account_path or not sheet_id:
        return None
    try:
        import gspread

        gc = gspread.service_account(filename=service_account_path)
        sh = gc.open_by_key(sheet_id)
        try:
            worksheet = sh.worksheet("Leads")
        except Exception:
            worksheet = sh.add_worksheet(title="Leads", rows=1000, cols=len(CSV_FIELDS))
            worksheet.append_row([f.replace("_", " ").title() for f in CSV_FIELDS])
        return worksheet
    except Exception as exc:  # pragma: no cover - network/credentials dependent
        print(f"[leads] Google Sheets unavailable, falling back to CSV: {exc}")
        return None


def _find_existing_row_csv(email: str, phone: str) -> Optional[int]:
    if not CSV_PATH.exists():
        return None
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    for idx, row in enumerate(reader):
        if (email and row.get("email") == email) or (phone and row.get("phone_number") == phone):
            return idx
    return None


def _write_csv(lead: LeadRecord) -> None:
    existing_idx = _find_existing_row_csv(lead.email, lead.phone_number)
    rows = []
    if CSV_PATH.exists():
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

    row_dict = lead.model_dump()
    if existing_idx is not None:
        rows[existing_idx] = row_dict  # update in place (dedup)
    else:
        rows.append(row_dict)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_sheet(lead: LeadRecord, worksheet) -> None:
    all_values = worksheet.get_all_records()
    row_dict = lead.model_dump()
    row_values = [row_dict.get(f, "") for f in CSV_FIELDS]

    for i, existing in enumerate(all_values, start=2):  # row 1 is header
        existing_email = existing.get("email") or existing.get("Email")
        existing_phone = existing.get("phone_number") or existing.get("Phone Number")
        if (lead.email and existing_email == lead.email) or (
            lead.phone_number and existing_phone == lead.phone_number
        ):
            worksheet.update(f"A{i}", [row_values])  # update in place (dedup)
            return
    worksheet.append_row(row_values)


def save_lead(lead: LeadRecord) -> str:
    """Persist a qualified lead. Returns the storage backend used ('google_sheet' or 'csv')."""
    worksheet = _get_sheet()
    if worksheet is not None:
        _write_sheet(lead, worksheet)
        return "google_sheet"
    _write_csv(lead)
    return "csv"
