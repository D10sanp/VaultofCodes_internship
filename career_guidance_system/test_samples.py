"""
Runs the full AI Career Guidance pipeline against sample_profiles.json (Section 13:
"Testing with at least 5-10 different sample student profiles") and prints a
summary of the generated report + lead classification for each one.

Works with or without ANTHROPIC_API_KEY set (falls back to the offline rule-based
generator in backend/ai_service.py when no key is configured).

Usage:
    cd career_guidance_system
    pip install -r backend/requirements.txt --break-system-packages
    python test_samples.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from models import StudentProfile, LeadRecord  # noqa: E402
from main import run_ai_pipeline  # noqa: E402
from leads import classify_lead, is_qualified_lead, is_complete, save_lead  # noqa: E402


def main():
    profiles_path = Path(__file__).parent / "sample_profiles.json"
    raw_profiles = json.loads(profiles_path.read_text())

    print(f"Loaded {len(raw_profiles)} sample profiles.\n")

    for i, raw in enumerate(raw_profiles, start=1):
        profile = StudentProfile(**raw)
        print("=" * 78)
        print(f"[{i}] {profile.name}  ({profile.current_education})")
        print("-" * 78)

        report = run_ai_pipeline(profile)
        qualified = is_qualified_lead(profile)
        lead_type = classify_lead(profile)
        complete, reason = is_complete(profile)

        print(f"Summary: {report.career_profile_summary}")
        print("Top career paths:")
        for cp in report.recommended_career_paths:
            print(f"  - {cp.title}: {cp.why_it_suits}")
        print(f"Skills to learn: {', '.join(report.skills_to_learn)}")
        print(f"Short-term plan: {report.action_plan.short_term}")
        print(f"Long-term plan: {report.action_plan.long_term}")
        print(f"Overall recommendation: {report.overall_recommendation}")
        print(f"\nLead qualified: {qualified} | Lead type: {lead_type} | Complete: {complete}"
              + (f" ({reason})" if not complete else ""))

        if qualified and complete:
            top_career = report.recommended_career_paths[0].title if report.recommended_career_paths else None
            top_degree = (
                report.recommended_degrees[0].suitable_degrees[0]
                if report.recommended_degrees and report.recommended_degrees[0].suitable_degrees
                else None
            )
            lead = LeadRecord(
                name=profile.name,
                phone_number=profile.phone,
                email=profile.email,
                current_education=profile.current_education,
                current_course_degree=profile.degree_course,
                college=profile.college,
                career_interest=profile.preferred_career_field,
                preferred_degree_mode=profile.degree_mode,
                counseling_required=profile.counseling_interest,
                preferred_specialization=profile.preferred_specialization,
                ai_recommended_career=top_career,
                ai_recommended_degree=top_degree,
                lead_type=lead_type,
            )
            backend_used = save_lead(lead)
            print(f"Lead saved via: {backend_used}")
        print()

    print("=" * 78)
    print("Done. If a lead was captured, check backend/leads.csv "
          "(or your configured Google Sheet).")


if __name__ == "__main__":
    main()
