# VaultOfCodes Support Chatbot

An AI-style first-level support and inquiry assistant for the VaultOfCodes
website — courses, training programs, internships, workshops, certificates,
offer letters, certificate verification, and website navigation — with
WhatsApp escalation for anything it can't (or shouldn't) answer on its own.

Built with **FastAPI** (backend) and plain **HTML/CSS/JavaScript** (chat
widget, no build step).

## Project layout

```
.
├── main.py                  FastAPI app: /api/chat, /api/suggested-questions
├── router.py                Smart routing: builds replies from the KB
├── intent_classifier.py     Intent classification + escalation detection
├── knowledge_base.py        Structured knowledge base (SAMPLE DATA — see below)
├── static/
│   ├── index.html           Demo host page + chat widget markup
│   ├── style.css            "Vault" visual identity + widget styling
│   └── script.js            Widget behavior (fetch calls, rendering)
├── tests/
│   ├── test_queries.json    15 test cases covering all required categories
│   └── run_tests.py         Test runner -> TESTING_REPORT.md
├── SYSTEM_PROMPT.md          Structured system prompt (assignment section 9)
├── ARCHITECTURE.md          How the pieces fit together, and why
├── TESTING_REPORT.md        Generated evaluation report (run tests to refresh)
└── README.md                 This file
```

## ⚠️ Replace the sample data before going live

`knowledge_base.py` is filled with **placeholder** course names, fees,
durations, links, and a placeholder WhatsApp number so the bot has real data
to retrieve from and demonstrate correctly. Before deployment, replace every
value in that file with VaultOfCodes's actual current information. The bot
never invents facts beyond what's in this file — it will only ever be as
accurate as the data given to it.

## Setup

Requires Python 3.10+.

```bash
pip install fastapi "uvicorn[standard]"
```

Run the server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** — this serves a mock VaultOfCodes page with
the chat widget in the bottom-right corner (click the brass dial icon).

## Embedding the widget on the real site

Copy the `<div id="vault-chat-root">…</div>` block from `static/index.html`
onto any page, and include:

```html
<link rel="stylesheet" href="https://your-api-host/static/style.css">
<script src="https://your-api-host/static/script.js"></script>
```

If the API is hosted on a different domain than the website, set
`API_BASE` at the top of `script.js` to the full API origin (CORS is already
open in `main.py` — tighten `allow_origins` for production).

## API

### `POST /api/chat`

```json
// Request
{ "session_id": "optional-existing-session-id-or-null", "message": "Where can I verify my certificate?" }

// Response
{
  "session_id": "generated-or-echoed-session-id",
  "reply": "Anyone can verify a VaultOfCodes certificate using the certificate ID on our verification page — no login required.",
  "intent": "certificate_verification",
  "links": [{ "label": "Certificate verification page", "url": "https://www.vaultofcodes.com/verify-certificate" }],
  "escalate": false,
  "escalate_reason": null,
  "whatsapp_link": null,
  "quick_replies": []
}
```

### `GET /api/suggested-questions`
Returns the quick-action chips shown when the chat opens.

### `GET /api/session/{session_id}/history`
Debug helper — returns the stored conversation history for a session.

## Running the tests

With the server running on port 8000:

```bash
python3 tests/run_tests.py --base-url http://localhost:8000
```

This runs all 15 test cases (course/training/internship inquiries,
certificate issues, offer letter issues, verification, navigation, payment,
technical support, general/unclear questions, explicit human requests, and a
conversation-memory follow-up) and writes `TESTING_REPORT.md` with a
pass/fail table.

## How it decides what to say (short version)

1. **Conversation memory** rewrites clear follow-ups ("its duration") using
   the last course/program discussed in the session.
2. **Escalation check** runs first — payment issues, account-specific
   problems, certificate/offer-letter corrections, disputes, and explicit
   "talk to a human" requests always go straight to a WhatsApp handoff,
   never a guessed answer.
3. **Intent classification** assigns one of 14 intents using keyword rules.
4. **Smart routing** looks the answer up in the knowledge base and returns
   it with the relevant page link — or the "I don't have reliable
   information on that" fallback if nothing matches.

Full details in `ARCHITECTURE.md`; the intended chatbot "personality" and
hard restrictions are in `SYSTEM_PROMPT.md`.
