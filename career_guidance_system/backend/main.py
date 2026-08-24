"""
AI Career Guidance & Counseling Lead Engine - FastAPI backend.

Flow (Section 12):
  Student submits questionnaire -> AI analyzes profile -> AI generates career,
  skill, degree & university recommendations -> Final report assembled ->
  System checks counseling intent -> If qualified, lead saved -> Report + lead
  status returned to the student.

Run with:
    uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import ai_service
import prompts
from leads import classify_lead, is_complete, is_qualified_lead, save_lead
from models import (
    ActionPlan,
    AnalyzeRequest,
    AnalyzeResponse,
    CareerPath,
    CareerReport,
    DegreeRecommendation,
    InstitutionSuggestion,
    LeadRecord,
    StudentProfile,
)

app = FastAPI(
    title="AI Career Guidance & Counseling Lead Engine",
    description="Assesses students, generates a personalized AI career report, and captures qualified counseling leads.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Core pipeline: chains the 6 prompts from prompts.py via ai_service.call_ai
# ---------------------------------------------------------------------------
def run_ai_pipeline(profile: StudentProfile) -> CareerReport:
    # 1. Student Profile Analysis
    p1 = prompts.student_profile_analysis_prompt(profile)
    profile_analysis = ai_service.call_ai(p1["system"], p1["user"])

    # 2. Career Path Recommendation
    p2 = prompts.career_path_prompt(profile, profile_analysis)
    career_paths_raw = ai_service.call_ai(p2["system"], p2["user"])

    # 3. Skill Recommendation
    p3 = prompts.skill_recommendation_prompt(profile, career_paths_raw)
    skills_raw = ai_service.call_ai(p3["system"], p3["user"])

    # 4. Degree Recommendation
    p4 = prompts.degree_recommendation_prompt(profile, career_paths_raw)
    degrees_raw = ai_service.call_ai(p4["system"], p4["user"])

    # 5. University/College Recommendation
    p5 = prompts.university_recommendation_prompt(profile, degrees_raw)
    institutions_raw = ai_service.call_ai(p5["system"], p5["user"])

    # 6. Final Career Report
    p6 = prompts.final_report_prompt(
        profile, profile_analysis, career_paths_raw, skills_raw, degrees_raw, institutions_raw
    )
    final_raw = ai_service.call_ai(p6["system"], p6["user"])

    # Assemble into the strongly-typed CareerReport model
    career_paths = [CareerPath(**cp) for cp in career_paths_raw.get("career_paths", [])]
    degree_recs = [DegreeRecommendation(**dr) for dr in degrees_raw.get("degree_recommendations", [])]
    institutions = [InstitutionSuggestion(**inst) for inst in institutions_raw.get("institutions", [])]

    report = CareerReport(
        student_name=profile.name,
        career_profile_summary=final_raw.get("career_profile_summary", profile_analysis.get("summary", "")),
        recommended_career_paths=career_paths,
        suitable_job_roles=final_raw.get("suitable_job_roles", []),
        skills_to_learn=skills_raw.get("priority_skills", []),
        recommended_degrees=degree_recs,
        recommended_institutions=institutions,
        action_plan=ActionPlan(
            short_term=final_raw.get("short_term_action_plan", []),
            long_term=final_raw.get("long_term_action_plan", []),
        ),
        overall_recommendation=final_raw.get("overall_recommendation", ""),
    )
    return report


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    profile = request.profile

    try:
        report = run_ai_pipeline(profile)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI pipeline failed: {exc}") from exc

    lead_type = classify_lead(profile)
    qualified = is_qualified_lead(profile)

    if qualified:
        complete, reason = is_complete(profile)
        if complete:
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
            save_lead(lead)
        # If incomplete, we still return the report to the student, we just skip lead capture.

    return AnalyzeResponse(report=report, is_lead=qualified, lead_type=lead_type)


# Serve the static frontend (index.html, style.css, script.js) at the root.
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
