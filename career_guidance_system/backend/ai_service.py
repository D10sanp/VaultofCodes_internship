"""
AI service layer - chains the six prompts from prompts.py against the Anthropic API.

If no ANTHROPIC_API_KEY is set, falls back to a deterministic, rule-based generator
so the whole pipeline (and the required 5-10 sample profile tests) still runs
end-to-end without any external calls or API keys.
"""
from __future__ import annotations
import json
import os
import re
from typing import Any, Dict

from models import StudentProfile

ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

_client = None
if API_KEY:
    try:
        import anthropic

        _client = anthropic.Anthropic(api_key=API_KEY)
    except Exception:
        _client = None


def _extract_json(text: str) -> Dict[str, Any]:
    """Best-effort extraction of a JSON object from a model response."""
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def call_ai(system: str, user: str) -> Dict[str, Any]:
    """Call Claude with a system/user prompt pair and parse structured JSON output."""
    if _client is not None:
        response = _client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1500,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        return _extract_json(text)

    # ---- Offline fallback (no API key configured) ----
    return _offline_fallback(system, user)


# ---------------------------------------------------------------------------
# Offline, rule-based fallback generator
# ---------------------------------------------------------------------------
def _offline_fallback(system: str, user: str) -> Dict[str, Any]:
    """
    A lightweight, deterministic stand-in for the AI model so the pipeline can be
    demoed/tested without network access or an API key. It inspects which prompt
    stage is being called (via distinctive text in the system prompt) and returns
    a plausible structured response built from the student data embedded in `user`.
    """
    data_match = re.search(r"Student (?:questionnaire )?data:\s*(\{.*?\n\})", user, re.DOTALL)
    profile = {}
    if data_match:
        try:
            profile = json.loads(data_match.group(1))
        except Exception:
            profile = {}

    skills = profile.get("skills", []) or []
    interests = profile.get("interests", []) or []
    goal = profile.get("career_goals", "a fulfilling career")
    field = profile.get("preferred_career_field") or (interests[0] if interests else "Technology")

    if "Student Profile Analysis" in system or "career-counseling analyst" in system:
        intent = "high" if profile.get("degree_mode") in ("Online Degree", "Distance Learning") or \
            "counseling" in (profile.get("counseling_interest", "").lower()) else "medium"
        return {
            "summary": f"{profile.get('name', 'The student')} is currently in {profile.get('current_education', 'their studies')} "
                        f"and is interested in {field}, aiming toward: {goal}.",
            "education_stage": profile.get("current_education", "Unknown"),
            "strengths": skills[:5] or ["Motivated to explore career options"],
            "gaps_or_risks": ["Needs clearer roadmap"] if not skills else ["Some foundational skills still developing"],
            "primary_interest_signal": field,
            "higher_education_intent": intent,
        }

    if "career-path recommendation engine" in system:
        base_titles = [field, f"{field} Specialist", f"{field} Analyst"]
        paths = []
        for i, title in enumerate(base_titles):
            paths.append({
                "title": title,
                "why_it_suits": f"Matches interest in {field} and existing skills such as {', '.join(skills[:2]) or 'foundational coursework'}.",
                "relevant_roles": [f"Junior {title}", f"{title}", f"Senior {title}"],
                "skills_required": (skills[:2] or ["Core fundamentals"]) + ["Communication", "Problem solving"],
                "skill_gaps": ["Advanced tools/frameworks", "Practical project experience"],
            })
        return {"career_paths": paths}

    if "skills advisor" in system:
        priority = list(dict.fromkeys((skills[:3] or []) + ["Communication", "Portfolio building", "Time management"]))[:6]
        return {
            "priority_skills": priority,
            "rationale": {s: f"Strengthens readiness for a career in {field}." for s in priority},
        }

    if "higher-education advisor" in system:
        return {
            "degree_recommendations": [
                {
                    "career_goal": field,
                    "suitable_degrees": [f"B.Sc/B.Tech related to {field}", f"Specialized diploma in {field}"],
                    "specializations": [field, f"{field} (Advanced)"],
                    "notes": f"Aligned with current education: {profile.get('current_education', 'N/A')}.",
                }
            ]
        }

    if "university-guidance assistant" in system:
        mode = profile.get("degree_mode", "Not Sure Yet")
        return {
            "institutions": [
                {"name": f"Public universities offering {field} programs", "type": "AI-generated guidance",
                 "reason": f"Good fit for {mode} study mode and moderate budget."},
                {"name": f"Reputed private colleges with {field} tracks", "type": "AI-generated guidance",
                 "reason": "Stronger industry connections, may suit higher budget preference."},
                {"name": "Accredited online degree platforms", "type": "AI-generated guidance",
                 "reason": "Fits flexible/online study preference."},
            ]
        }

    if "FINAL" in system or "assembling" in system.lower():
        return {
            "career_profile_summary": f"{profile.get('name', 'This student')} shows strong potential in {field} "
                                        f"and is working toward: {goal}.",
            "suitable_job_roles": [f"Junior {field} Associate", f"{field} Analyst"],
            "short_term_action_plan": [
                f"Build 1-2 small projects related to {field}",
                "Strengthen core skills through free/low-cost courses",
                "Update resume/portfolio",
            ],
            "long_term_action_plan": [
                f"Pursue a relevant degree/specialization in {field}",
                "Seek internships or entry-level roles",
                "Build a professional network in the field",
            ],
            "overall_recommendation": f"Focus on building practical {field} skills now, and consider a "
                                        f"degree path that complements your goal of {goal}. Progress steadily - "
                                        f"consistency matters more than speed.",
        }

    return {}
