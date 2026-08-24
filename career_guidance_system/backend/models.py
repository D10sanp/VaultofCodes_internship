"""
Data models for the AI Career Guidance & Counseling Lead Engine.
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class StudentProfile(BaseModel):
    """Raw questionnaire input collected from the student."""

    # Basic contact info
    name: str
    email: EmailStr
    phone: str = Field(..., description="Phone / WhatsApp number")

    # Education
    current_education: str = Field(..., description="e.g. High School, Undergraduate, Graduate")
    degree_course: Optional[str] = Field(None, description="Current degree/course, if any")
    college: Optional[str] = Field(None, description="Current college/university, if any")
    current_year: Optional[str] = Field(None, description="Current year/semester, if applicable")

    # Interests & goals
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    career_goals: str = Field(..., description="Free text: what the student wants to become / achieve")
    preferred_career_field: Optional[str] = None
    current_experience: Optional[str] = Field(None, description="Internships, jobs, projects, or 'None'")

    # Higher-education / lead qualification signals
    preferred_location: Optional[str] = None
    budget_preference: Optional[str] = None
    degree_mode: str = Field(
        ..., description="Online Degree | Offline/Regular Degree | Hybrid | Distance Learning | Not Sure Yet"
    )
    counseling_interest: str = Field(
        ...,
        description="Yes, I want counseling | Yes, I want more information | Maybe, I'm exploring options | No, I just want career guidance",
    )
    preferred_specialization: Optional[str] = None

    @field_validator("skills", "interests", mode="before")
    @classmethod
    def _split_csv(cls, v):
        # Allow the frontend to send either a list or a comma-separated string
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v or []


class CareerPath(BaseModel):
    title: str
    why_it_suits: str
    relevant_roles: List[str]
    skills_required: List[str]
    skill_gaps: List[str]


class DegreeRecommendation(BaseModel):
    career_goal: str
    suitable_degrees: List[str]
    specializations: List[str]
    notes: Optional[str] = None


class InstitutionSuggestion(BaseModel):
    name: str
    type: str = Field(..., description="e.g. 'AI-generated guidance' or 'Verified institutional information'")
    reason: str


class ActionPlan(BaseModel):
    short_term: List[str]
    long_term: List[str]


class CareerReport(BaseModel):
    """The final, student-facing AI Career Report (Section 9)."""

    student_name: str
    career_profile_summary: str
    recommended_career_paths: List[CareerPath]
    suitable_job_roles: List[str]
    skills_to_learn: List[str]
    recommended_degrees: List[DegreeRecommendation]
    recommended_institutions: List[InstitutionSuggestion]
    action_plan: ActionPlan
    overall_recommendation: str


class LeadRecord(BaseModel):
    """Row schema for the Google Sheet / CSV lead store (Section 3)."""

    name: str
    phone_number: str
    email: str
    current_education: str
    current_course_degree: Optional[str] = None
    college: Optional[str] = None
    career_interest: Optional[str] = None
    preferred_degree_mode: str
    counseling_required: str
    preferred_specialization: Optional[str] = None
    ai_recommended_career: Optional[str] = None
    ai_recommended_degree: Optional[str] = None
    lead_type: Optional[str] = None
    date_time: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    lead_source: str = "Website - AI Career Guidance System"


class AnalyzeRequest(BaseModel):
    profile: StudentProfile


class AnalyzeResponse(BaseModel):
    report: CareerReport
    is_lead: bool
    lead_type: str
