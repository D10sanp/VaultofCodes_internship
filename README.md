# 🚀 VaultOfCodes AI & Prompt Engineering Internship

<p align="center">
  <b>AI & Prompt Engineering Internship Projects</b><br>
  <i>Hands-on implementation of AI-powered applications, prompt engineering, intelligent routing, and career guidance systems.</i>
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![AI](https://img.shields.io/badge/AI-Prompt%20Engineering-8A2BE2?style=for-the-badge)
![Internship](https://img.shields.io/badge/VaultOfCodes-Internship-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow?style=for-the-badge)
</p>

---

## 👨‍💻 Intern

**Sandip Dusadh**

**Role:** AI & Prompt Engineering Intern <br>
**Organization:** VaultOfCodes <br>
**Internship Mode:** Online / Remote<br>
**Duration:** 2 Months<br>
**Start Date:** 01/08/2026

---

## 📌 About the Internship

This repository contains the projects and practical work completed as part of the **VaultOfCodes Training & Internship Program** for the role of **AI & Prompt Engineering Intern**.

The internship focuses on applying Artificial Intelligence and Prompt Engineering concepts to real-world software projects. The work emphasizes:

* 🤖 Artificial Intelligence
* 🧠 Prompt Engineering
* 💬 AI-powered conversational systems
* 🎯 Career guidance and recommendation systems
* ⚙️ Backend API development
* 🔀 Intelligent routing and intent classification
* 🧪 Testing and evaluation
* 📊 Structured knowledge management
* 🔗 API integration and deployment-ready architecture

The projects in this repository demonstrate the practical application of these concepts through functional AI-oriented systems.

---

# 📂 Repository Projects

The repository currently contains two major projects:

```text
VaultofCodes_internship/
│
├── career_guidance_system/
│   ├── backend/
│   ├── frontend/
│   ├── sample_profiles.json
│   ├── test_samples.py
│   └── README.md
│
└── vaultofcodes-chatbot/
    ├── static/
    ├── tests/
    ├── main.py
    ├── router.py
    ├── intent_classifier.py
    ├── knowledge_base.py
    ├── SYSTEM_PROMPT.md
    ├── ARCHITECTURE.md
    ├── TESTING_REPORT.md
    └── README.md
```

---

# 🧭 Project 1 — Wayfind AI Career Guidance System

📁 **Directory:** `career_guidance_system/`

Wayfind is an **AI-powered career guidance and counseling lead engine** designed to analyze a student's education, skills, interests, and goals and generate a personalized career report.

The system also includes a lead qualification pipeline for identifying students who may require additional counseling or higher-education assistance.

### ✨ Key Features

* 📝 Multi-step student questionnaire
* 🎓 Education and academic profile analysis
* 💡 Career path recommendations
* 🛠️ Skill recommendations
* 🎓 Degree recommendations
* 🏫 University/college recommendations
* 📄 Personalized career report
* 🎯 Lead qualification and classification
* 🔍 Duplicate lead detection
* 💾 CSV lead storage
* 📊 Optional Google Sheets integration
* 🤖 Claude API integration
* 🔄 Deterministic offline AI fallback
* 🧪 Automated sample-profile testing

### 🧠 Prompt Engineering Pipeline

The system uses a chained multi-prompt architecture consisting of six stages:

```text
Student Profile
      │
      ▼
┌─────────────────────────┐
│ 1. Profile Analysis     │
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 2. Career Recommendation│
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 3. Skill Recommendation │
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 4. Degree Recommendation│
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 5. University Guidance  │
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 6. Final Career Report  │
└─────────────────────────┘
             │
             ▼
      Lead Qualification
```

Each stage has a dedicated prompt instead of relying on one generic AI prompt. This makes the system easier to understand, test, and improve.

### 🛠️ Technology Stack

| Component       | Technology            |
| --------------- | --------------------- |
| Backend         | FastAPI               |
| Language        | Python                |
| Frontend        | HTML, CSS, JavaScript |
| AI              | Anthropic Claude API  |
| Data Validation | Pydantic              |
| Lead Storage    | CSV / Google Sheets   |
| Testing         | Python                |
| API Server      | Uvicorn               |

### ▶️ Running the Career Guidance System

```bash
cd career_guidance_system

pip install -r backend/requirements.txt
```

Start the backend:

```bash
cd backend

uvicorn main:app --reload --port 8000
```

Then open:

```text
http://localhost:8000
```

The FastAPI backend serves the frontend and handles the complete questionnaire → AI analysis → career report → lead qualification pipeline.

### 🧪 Testing

The project includes eight sample student profiles.

Run:

```bash
cd career_guidance_system

python test_samples.py
```

The test pipeline evaluates the sample profiles through the AI workflow and generates qualified leads where applicable.

---

# 🤖 Project 2 — VaultOfCodes Support Chatbot

📁 **Directory:** `vaultofcodes-chatbot/`

The VaultOfCodes Support Chatbot is an **AI-style first-level support and inquiry assistant** designed to help users with questions related to courses, training programs, internships, workshops, certificates, offer letters, certificate verification, payments, and website navigation.

It also includes an escalation mechanism for issues that should be handled by a human support representative.

### ✨ Key Features

* 💬 Interactive chatbot interface
* 🧠 Intent classification
* 📚 Structured knowledge base
* 🔀 Smart response routing
* 🗂️ Conversation/session memory
* ⚠️ Automatic escalation detection
* 📱 WhatsApp escalation support
* 🔗 Relevant page/link responses
* 💡 Suggested questions
* 🧪 Automated test suite
* 🛡️ Restricted-answer behavior to avoid inventing unsupported information

### 🧩 Chatbot Architecture

```text
                 User
                   │
                   ▼
          ┌─────────────────┐
          │  Chat Interface │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Conversation    │
          │ Memory          │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Intent          │
          │ Classifier      │
          └────────┬────────┘
                   │
          ┌────────┴─────────┐
          │                  │
          ▼                  ▼
     Escalation?          Normal Query
          │                  │
          ▼                  ▼
     WhatsApp          Knowledge Base
     Handoff                │
                             ▼
                       Smart Router
                             │
                             ▼
                         Response
```

The chatbot checks escalation conditions before attempting to answer. Issues such as payment problems, account-specific issues, certificate/offer-letter corrections, disputes, and explicit human-support requests are routed toward escalation rather than answered with potentially unreliable information.

### 🛠️ Technology Stack

| Component             | Technology                       |
| --------------------- | -------------------------------- |
| Backend               | FastAPI                          |
| Language              | Python                           |
| Frontend              | HTML, CSS, JavaScript            |
| Intent Classification | Rule-based classifier            |
| Knowledge Management  | Structured Python knowledge base |
| API                   | REST                             |
| Testing               | Python                           |
| Support Escalation    | WhatsApp                         |

### ▶️ Running the Chatbot

Python 3.10+ is recommended.

Install dependencies:

```bash
cd vaultofcodes-chatbot

pip install fastapi "uvicorn[standard]"
```

Start the application:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000
```

The application serves a demo VaultOfCodes page with the chatbot widget.

### 🧪 Running Tests

The chatbot contains a test suite covering multiple categories including:

* Course inquiries
* Training inquiries
* Internship inquiries
* Certificate issues
* Offer-letter issues
* Certificate verification
* Website navigation
* Payment-related questions
* Technical support
* General/unclear questions
* Human-support requests
* Conversation-memory follow-ups

Run:

```bash
python3 tests/run_tests.py --base-url http://localhost:8000
```

The test runner generates `TESTING_REPORT.md`.

---

# 🧠 Prompt Engineering Concepts Demonstrated

This internship repository demonstrates several practical prompt-engineering concepts.

### 1. Structured Prompts

Prompts are designed with clear instructions, context, constraints, and expected output formats.

### 2. Prompt Chaining

The career guidance system separates a complex task into multiple AI stages instead of asking one prompt to perform every task.

### 3. Context Passing

Outputs from earlier AI stages can be provided as context to subsequent stages.

### 4. Controlled AI Output

The systems use structured outputs and predefined rules to make AI responses more predictable and auditable.

### 5. Grounded Responses

The support chatbot retrieves information from a predefined knowledge base rather than freely generating unsupported facts.

### 6. Escalation Handling

When a query requires human intervention, the chatbot can identify the situation and escalate instead of guessing.

### 7. Fallback Design

The career guidance system includes a deterministic fallback mode so that the application can still be demonstrated without an external AI API key.

---

# 🔐 Configuration

## Anthropic API

The career guidance system can optionally use the Anthropic Claude API.

Set:

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

An optional model can also be configured:

```bash
export ANTHROPIC_MODEL="your-model-name"
```

Without an API key, the project uses its deterministic rule-based fallback.

> **Security:** Never commit API keys, passwords, service-account credentials, or other secrets to GitHub.

---

# 📊 Project Comparison

| Feature                | Career Guidance System | Support Chatbot |
| ---------------------- | :--------------------: | :-------------: |
| AI/Prompt Engineering  |            ✅           |        ✅        |
| FastAPI                |            ✅           |        ✅        |
| Frontend               |            ✅           |        ✅        |
| Intent Classification  |            —           |        ✅        |
| Prompt Chaining        |            ✅           |        —        |
| Career Recommendations |            ✅           |        —        |
| Knowledge Base         |            —           |        ✅        |
| Lead Qualification     |            ✅           |        —        |
| Conversation Memory    |            —           |        ✅        |
| Human Escalation       |            —           |        ✅        |
| Automated Testing      |            ✅           |        ✅        |
| External AI API        |        Optional        |        —        |
| CSV Storage            |            ✅           |        —        |
| Google Sheets          |        Optional        |        —        |

---

# 🎯 Internship Learning Outcomes

Through these projects, the internship provided practical experience in:

* Artificial Intelligence application development
* Prompt engineering
* AI workflow design
* Prompt chaining
* Conversational AI
* Intent classification
* API development
* FastAPI
* Python development
* Frontend integration
* Structured data handling
* Automated testing
* AI fallback strategies
* Knowledge-base-driven systems
* Lead qualification
* System architecture
* Human escalation workflows

---

# 📁 Repository Structure

```text
VaultofCodes_internship/
│
├── career_guidance_system/
│   │
│   ├── backend/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── prompts.py
│   │   ├── ai_service.py
│   │   ├── leads.py
│   │   └── requirements.txt
│   │
│   ├── frontend/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   │
│   ├── sample_profiles.json
│   ├── test_samples.py
│   └── README.md
│
├── vaultofcodes-chatbot/
│   │
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   │
│   ├── tests/
│   │   ├── test_queries.json
│   │   └── run_tests.py
│   │
│   ├── main.py
│   ├── router.py
│   ├── intent_classifier.py
│   ├── knowledge_base.py
│   ├── SYSTEM_PROMPT.md
│   ├── ARCHITECTURE.md
│   ├── TESTING_REPORT.md
│   └── README.md
│
└── README.md
```

---

# ⚠️ Important Note

The chatbot's `knowledge_base.py` currently contains sample/placeholder information intended for development and demonstration. Before production deployment, the knowledge base should be replaced with verified and current VaultOfCodes information.

Similarly, AI-generated career and university recommendations should be treated as guidance rather than authoritative institutional information. A production system should connect recommendations to verified institutional data.

---

# 🚀 Future Improvements

Potential improvements for production deployment include:

* [ ] Add authentication and authorization
* [ ] Add persistent database storage
* [ ] Add rate limiting
* [ ] Improve AI evaluation and monitoring
* [ ] Add verified university/course databases
* [ ] Add richer analytics dashboards
* [ ] Add multilingual chatbot support
* [ ] Add conversation analytics
* [ ] Improve lead-management workflows
* [ ] Add CI/CD pipelines
* [ ] Deploy applications to a cloud platform
* [ ] Add comprehensive API documentation
* [ ] Add stronger security and input validation

---

# 🏆 Internship Summary

This repository represents practical work completed during the **VaultOfCodes AI & Prompt Engineering Internship**.

The projects focus on building useful AI-powered applications while applying software engineering principles such as modular architecture, API development, testing, structured prompts, controlled AI behavior, and fallback mechanisms.

The internship provided an opportunity to move beyond theoretical AI concepts and implement them in practical, real-world-oriented applications.

---

## 👤 Author

**Sandip Dusadh**

AI & Prompt Engineering Intern
VaultOfCodes

GitHub: [D10sanp](https://github.com/D10sanp)

---

## ⭐ Acknowledgement

I would like to thank **VaultOfCodes** for providing the opportunity to participate in the **AI & Prompt Engineering Training & Internship Program** and for providing hands-on exposure to real-world AI application development.

---

<p align="center">
  <b>Built with Python, FastAPI, AI & Prompt Engineering 🤖</b>
</p>
