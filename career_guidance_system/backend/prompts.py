"""
Prompt architecture for the AI Career Guidance System.

Per the project spec (Section 10), we do NOT use a single generic prompt.
Instead we define six separate, purpose-built prompts, each with:
  - a fixed SYSTEM prompt that sets rules/tone/output-format constraints
  - a USER prompt template that is filled with the *actual* student data

Every prompt enforces:
  - use of the student's real information (no generic filler)
  - an explanation of *why* each recommendation was made
  - avoidance of unrealistic promises ("guaranteed job", "100% placement", etc.)
  - strict, parseable JSON output (no prose outside the JSON object)
"""
from __future__ import annotations
import json
from typing import Any, Dict
from models import StudentProfile

# ---------------------------------------------------------------------------
# Shared guardrails appended to every system prompt
# ---------------------------------------------------------------------------
_COMMON_RULES = """
Rules you must always follow:
1. Base every recommendation strictly on the student data provided. Never invent facts about the student.
2. Personalize your language - refer to the student's actual skills, interests, and goals.
3. Briefly justify each recommendation (the "why"), don't just list things.
4. Never make unrealistic promises (e.g. "guaranteed job", "100% placement", "become an expert in a week").
5. Be encouraging but honest about skill gaps.
6. Output ONLY valid JSON matching the requested schema. No markdown fences, no commentary, no extra keys.
"""


def _profile_to_json(profile: StudentProfile) -> str:
    return json.dumps(profile.model_dump(), indent=2, default=str)


# ---------------------------------------------------------------------------
# 1. Student Profile Analysis
# ---------------------------------------------------------------------------
def student_profile_analysis_prompt(profile: StudentProfile) -> Dict[str, str]:
    system = f"""You are a career-counseling analyst. Your job is to read a student's raw
questionnaire answers and produce a clean, structured interpretation of who they are,
what stage of education/career they are at, and what signals matter most for guidance.
{_COMMON_RULES}

Return JSON with this exact schema:
{{
  "summary": "2-3 sentence plain-language summary of the student's current situation",
  "education_stage": "string, e.g. 'Undergraduate - 2nd year'",
  "strengths": ["list of 3-5 strengths inferred from skills/experience"],
  "gaps_or_risks": ["list of gaps, e.g. missing foundational skills, unclear goals"],
  "primary_interest_signal": "the single clearest interest/goal signal from the data",
  "higher_education_intent": "low | medium | high - based on degree_mode and counseling_interest fields"
}}"""
    user = f"Student questionnaire data:\n{_profile_to_json(profile)}\n\nAnalyze this student's profile."
    return {"system": system, "user": user}


# ---------------------------------------------------------------------------
# 2. Career Path Recommendation
# ---------------------------------------------------------------------------
def career_path_prompt(profile: StudentProfile, profile_analysis: Dict[str, Any]) -> Dict[str, str]:
    system = f"""You are a career-path recommendation engine. Using the student's data and a prior
profile analysis, recommend the TOP 3 to 5 career paths that genuinely fit this specific student.
{_COMMON_RULES}

Return JSON with this exact schema:
{{
  "career_paths": [
    {{
      "title": "Career path name",
      "why_it_suits": "1-2 sentences tying it to this student's actual skills/interests/goals",
      "relevant_roles": ["job role 1", "job role 2", "job role 3"],
      "skills_required": ["skill 1", "skill 2", "skill 3"],
      "skill_gaps": ["skills this specific student is currently missing"]
    }}
  ]
}}
Order career_paths from best-fit to least-fit."""
    user = (
        f"Student questionnaire data:\n{_profile_to_json(profile)}\n\n"
        f"Prior profile analysis:\n{json.dumps(profile_analysis, indent=2)}\n\n"
        "Recommend 3-5 career paths."
    )
    return {"system": system, "user": user}


# ---------------------------------------------------------------------------
# 3. Skill Recommendation
# ---------------------------------------------------------------------------
def skill_recommendation_prompt(profile: StudentProfile, career_paths: Dict[str, Any]) -> Dict[str, str]:
    system = f"""You are a skills advisor. Given a student's chosen/recommended career paths, identify
the MOST IMPORTANT skills to develop. Prioritize - do not produce a huge generic list.
{_COMMON_RULES}

Return JSON with this exact schema:
{{
  "priority_skills": ["ranked list of 5-8 highest-priority skills, most important first"],
  "rationale": {{"skill name": "one short sentence on why it matters for this student's target career(s)"}}
}}"""
    user = (
        f"Student data:\n{_profile_to_json(profile)}\n\n"
        f"Recommended career paths:\n{json.dumps(career_paths, indent=2)}\n\n"
        "Produce a prioritized skill list."
    )
    return {"system": system, "user": user}


# ---------------------------------------------------------------------------
# 4. Degree Recommendation
# ---------------------------------------------------------------------------
def degree_recommendation_prompt(profile: StudentProfile, career_paths: Dict[str, Any]) -> Dict[str, str]:
    system = f"""You are a higher-education advisor. Based on the student's current education and
recommended career paths, suggest suitable degree programs, specializations, and fields of study.
{_COMMON_RULES}

Return JSON with this exact schema:
{{
  "degree_recommendations": [
    {{
      "career_goal": "career path this maps to",
      "suitable_degrees": ["degree 1", "degree 2", "degree 3"],
      "specializations": ["specialization 1", "specialization 2"],
      "notes": "short note on how this fits the student's current education level"
    }}
  ]
}}"""
    user = (
        f"Student data:\n{_profile_to_json(profile)}\n\n"
        f"Recommended career paths:\n{json.dumps(career_paths, indent=2)}\n\n"
        "Recommend degree programs and specializations."
    )
    return {"system": system, "user": user}


# ---------------------------------------------------------------------------
# 5. University / College Recommendation
# ---------------------------------------------------------------------------
def university_recommendation_prompt(profile: StudentProfile, degree_recs: Dict[str, Any]) -> Dict[str, str]:
    system = f"""You are a university-guidance assistant. Suggest TYPES of universities/colleges (not
fabricated specific institution names claimed as verified fact) that fit the student's budget, preferred
study mode, and location preference. You must clearly label every suggestion as "AI-generated guidance"
unless it is a very well-known, widely-verifiable institution category.
{_COMMON_RULES}
Additional rule: Do not present unverified institution names as confirmed facts. Always set "type" to
"AI-generated guidance" unless referring to a well-known public institution category (e.g. "IITs", "State
public universities"), in which case you may set "type" to "Verified institutional information".

Return JSON with this exact schema:
{{
  "institutions": [
    {{
      "name": "institution or institution-category name",
      "type": "AI-generated guidance | Verified institutional information",
      "reason": "why this fits the student's budget/location/mode preference"
    }}
  ]
}}
Return 3-6 suggestions."""
    user = (
        f"Student data:\n{_profile_to_json(profile)}\n\n"
        f"Degree recommendations:\n{json.dumps(degree_recs, indent=2)}\n\n"
        "Suggest suitable universities/colleges or institution types."
    )
    return {"system": system, "user": user}


# ---------------------------------------------------------------------------
# 6. Final Career Report
# ---------------------------------------------------------------------------
def final_report_prompt(
    profile: StudentProfile,
    profile_analysis: Dict[str, Any],
    career_paths: Dict[str, Any],
    skills: Dict[str, Any],
    degrees: Dict[str, Any],
    institutions: Dict[str, Any],
) -> Dict[str, str]:
    system = f"""You are assembling the FINAL, student-facing Career Report. Combine all prior analysis
into one concise, encouraging, easy-to-read report. Do NOT overwhelm the student with unnecessary
courses, certifications, or excessive information - keep it focused and actionable.
{_COMMON_RULES}

Return JSON with this exact schema:
{{
  "career_profile_summary": "2-3 sentence friendly summary of who this student is right now",
  "suitable_job_roles": ["deduplicated flat list of the best-fit job roles across all recommended paths"],
  "short_term_action_plan": ["3-5 concrete actions for the next 3-6 months"],
  "long_term_action_plan": ["3-5 concrete actions for the next 1-3 years"],
  "overall_recommendation": "3-4 sentence closing recommendation tying career + degree + skills together, in an encouraging but realistic tone"
}}"""
    user = (
        f"Student data:\n{_profile_to_json(profile)}\n\n"
        f"Profile analysis:\n{json.dumps(profile_analysis, indent=2)}\n\n"
        f"Career paths:\n{json.dumps(career_paths, indent=2)}\n\n"
        f"Skills:\n{json.dumps(skills, indent=2)}\n\n"
        f"Degrees:\n{json.dumps(degrees, indent=2)}\n\n"
        f"Institutions:\n{json.dumps(institutions, indent=2)}\n\n"
        "Assemble the final student-facing report."
    )
    return {"system": system, "user": user}
