# Architecture & Prompt Engineering Notes

## Pipeline

```
User message
     │
     ▼
resolve_context()          <- conversation memory: rewrite pronouns ("its duration")
     │                         using session["last_topic"] from prior turns
     ▼
needs_escalation()         <- keyword-based check for payment, account-specific,
     │                         certificate/offer-letter corrections, disputes,
     │                         explicit "talk to a human" requests
     ▼
classify_intent()          <- assigns one of 14 intents (see SYSTEM_PROMPT.md)
     │
     ▼
build_response()           <- smart routing: looks up the knowledge base for
     │                         the matched intent (+ entity, e.g. course name)
     │                         and returns (reply, links, quick_replies, topic)
     ▼
session["last_topic"] updated (if a course/program/topic was discussed)
     │
     ▼
JSON response -> chat widget renders bubble + link pills + WhatsApp card
```

## Why rule-based instead of calling an LLM directly

The assignment's restrictions are absolute ("must NOT invent course details /
fees", "must NOT pretend to have account access"). A prompted LLM can still
hallucinate under those instructions. This implementation instead:

1. Classifies intent with transparent, auditable keyword rules
   (`intent_classifier.py`).
2. Looks up the answer **only** in the structured knowledge base
   (`knowledge_base.py`) — there is no code path that lets the bot generate
   a course name, fee, or duration that isn't in that file.
3. Falls back to the exact "I'm not able to find reliable information..."
   message, per spec, whenever nothing matches — never a best-guess answer.
4. Escalates to WhatsApp for anything account-specific, payment-related, or
   explicitly requesting a human, per spec section 7.

This also makes the system fast (no API latency/cost) and easy for a
non-engineer on the team to extend: adding a new course is editing a Python
dict, adding a new recognized phrasing is adding a keyword to a list.

`SYSTEM_PROMPT.md` documents the equivalent instructions as a traditional
LLM system prompt, for a future version that uses the Anthropic API for more
natural phrasing — the knowledge-base lookup and restrictions should stay
enforced in code even then, with the LLM only used to phrase the final
sentence, not to decide facts.

## Conversation memory

`SESSIONS` (in `main.py`) is an in-memory dict keyed by a `session_id` the
client generates once and stores in `sessionStorage`. Each session tracks
`last_topic` (e.g. "Python Programming") and a capped message history.
`resolve_context()` only rewrites a message when it contains a clear
referential phrase (`its`, `this course`, `that program`, etc.) — deliberately
narrow, because bare words like "it" appear too often in unrelated sentences
("wrong name on it") and would otherwise wrongly drag in the last topic.

**Production note:** this in-memory store resets on server restart and won't
work across multiple server instances behind a load balancer. Swap in Redis
or a database table keyed by `session_id` for production.

## Smart routing examples (spec section 11)

| Input | Intent | Action |
|---|---|---|
| "What ethical hacking courses do you have?" | `course_inquiry` | Answer from KB + course page link |
| "Where can I verify my certificate?" | `certificate_verification` | Link to verification page |
| "My certificate has the wrong name." | `certificate_query` (escalation trigger fires) | Escalation message + WhatsApp button |
| "I want to apply for an internship." | `internship_inquiry` | Link to internship application page |
| "I paid but haven't received access." | `payment_query` (always escalates) | Escalation message + WhatsApp button, no guessing |

## Frontend

Single-page widget (`static/index.html`, `style.css`, `script.js`) mounted by
FastAPI's `StaticFiles`. No build step — vanilla JS, `fetch()` to
`/api/chat`. Designed to be dropped into any page by including the same
`<div id="vault-chat-root">` markup + the two asset files, or embedded as an
iframe if preferred for the real VaultOfCodes site.
