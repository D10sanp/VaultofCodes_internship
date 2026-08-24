# Wayfind — AI Career Guidance & Counseling Lead Engine

An AI-powered career guidance system that assesses a student's education, skills,
interests, and goals, generates a personalized career report, and simultaneously
identifies and captures qualified higher-education/counseling leads.

Built for the "AI Career Guidance & Counseling Lead Engine" project brief.

## Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Plain HTML + CSS + vanilla JS (no build step)
- **AI:** Anthropic Claude API, with a deterministic offline fallback so the whole
  system runs and is testable even without an API key
- **Lead storage:** Google Sheets (via `gspread`), with an automatic CSV fallback

## Project structure

```
career_guidance_system/
├── backend/
│   ├── main.py              # FastAPI app, wires questionnaire → AI pipeline → lead engine
│   ├── models.py             # Pydantic schemas (StudentProfile, CareerReport, LeadRecord, ...)
│   ├── prompts.py            # 6 separate, purpose-built prompts (Section 10 of the brief)
│   ├── ai_service.py         # Calls Claude; falls back to a rule-based generator with no API key
│   ├── leads.py               # Lead qualification, classification, dedup, Google Sheets/CSV storage
│   └── requirements.txt
├── frontend/
│   ├── index.html             # Multi-step questionnaire with conditional questions + results view
│   ├── style.css
│   └── script.js
├── sample_profiles.json       # 8 sample student profiles for testing
├── test_samples.py            # Runs the full pipeline against all sample profiles
└── README.md
```

## Setup

```bash
cd career_guidance_system
pip install -r backend/requirements.txt
```

(If you're on a system that requires it: `pip install -r backend/requirements.txt --break-system-packages`)

## Running it

```bash
cd career_guidance_system/backend
uvicorn main:app --reload --port 8000
```

Then open **http://localhost:8000** in a browser — FastAPI serves the frontend
directly, so no separate web server is needed. The questionnaire, AI analysis, and
lead capture all run against this one server.

## Testing with sample profiles

The brief requires testing with 5-10 sample student profiles. `sample_profiles.json`
contains 8 varied profiles (high schoolers, undergrads, postgrads, a working
professional; a mix of degree-mode and counseling answers). Run:

```bash
cd career_guidance_system
python test_samples.py
```

This runs the complete 6-prompt AI pipeline for every sample profile, prints the
generated report + lead classification for each, and saves any qualifying leads to
`backend/leads.csv`.

## Configuring the AI (optional)

By default, if no `ANTHROPIC_API_KEY` is set, the backend uses a deterministic,
rule-based generator (see `ai_service.py`) so you can run and demo the entire system
with zero external dependencies. To use real Claude-generated recommendations:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export ANTHROPIC_MODEL="claude-sonnet-5"   # optional, this is the default
```

## Configuring Google Sheets (optional)

By default, leads are appended to `backend/leads.csv`. To send leads to a real
Google Sheet instead:

1. Create a Google Cloud service account and download its JSON key file.
2. Share your target Google Sheet with the service account's email address (Editor access).
3. Set environment variables before starting the server:

```bash
export GOOGLE_SERVICE_ACCOUNT_JSON="/path/to/service-account.json"
export GOOGLE_SHEET_ID="the-google-sheet-id-from-its-url"
```

The backend will automatically create a "Leads" worksheet with the correct headers
if one doesn't already exist, and will update existing rows (matched by email or
phone) instead of duplicating them.

## How the pieces fit together (Section 12 flow)

1. Student completes the questionnaire in the browser (`frontend/`), including
   conditional questions (e.g. degree/college fields only appear if currently
   enrolled).
2. The frontend POSTs the full profile to `POST /api/analyze`.
3. The backend runs **six separate, chained AI prompts** (`prompts.py` →
   `ai_service.py`, orchestrated in `main.run_ai_pipeline`):
   1. Student Profile Analysis
   2. Career Path Recommendation
   3. Skill Recommendation
   4. Degree Recommendation
   5. University/College Recommendation
   6. Final Career Report
4. `leads.py` checks the student's degree-mode and counseling answers to decide
   if this is a qualified lead, classifies the lead type, checks for duplicates
   and completeness, and — if qualified and complete — saves it.
5. The student sees a full, structured career report in the browser; qualified
   students additionally see a note that a counselor may follow up.

## Design notes on the prompt architecture

Each prompt in `prompts.py` has a fixed system prompt (rules: use real student data,
explain the "why," avoid unrealistic promises, output strict JSON) and a user prompt
built from the actual student answers plus the outputs of any earlier stage in the
chain. This keeps each stage focused and auditable, rather than asking one generic
prompt to do everything at once.

## Known limitations / next steps

- The offline fallback generator is intentionally simple (rule-based) — it exists so
  the system is fully runnable without an API key; real usage should set
  `ANTHROPIC_API_KEY` for genuinely personalized AI output.
- University/college suggestions are explicitly framed as "AI-generated guidance"
  rather than verified fact, per the brief's requirement to distinguish AI guidance
  from verified institutional information — for production use, pair this with a
  verified institution database.
- Authentication, rate limiting, and a persistent database (vs. CSV) would be the
  next additions for a production deployment.
