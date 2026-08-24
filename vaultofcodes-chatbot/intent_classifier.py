"""
intent_classifier.py

Lightweight, dependency-free intent classification for the VaultOfCodes
chatbot, plus escalation detection.

Design notes:
- This uses transparent keyword/phrase scoring rather than a black-box model.
  That's a deliberate choice for a support bot: it's auditable, fast, needs no
  external API, and it's easy for the team to add new phrases as they see
  real user queries come in.
- To swap in an LLM-based classifier later (e.g. calling the Anthropic API
  with a structured-JSON prompt), replace `classify_intent()`'s body while
  keeping the same function signature — the rest of the app doesn't care how
  the intent is produced.
"""

import re

INTENTS = [
    "course_inquiry",
    "training_inquiry",
    "internship_inquiry",
    "workshop_inquiry",
    "certificate_query",
    "certificate_verification",
    "offer_letter_query",
    "enrollment_query",
    "payment_query",
    "website_navigation",
    "technical_support",
    "human_support",
    "general_query",
    "unknown",
]

# Ordered roughly from most specific to least specific; specific matches
# should win over generic ones (e.g. "certificate_verification" should beat
# the more generic "certificate_query" when "verify" is present).
INTENT_KEYWORDS = {
    "human_support": [
        "talk to a human", "talk to someone", "speak to a human", "speak to an agent",
        "real person", "human agent", "connect me to support", "customer care agent",
    ],
    "payment_query": [
        "payment", "paid but", "transaction failed", "money deducted", "refund",
        "charged twice", "double charged", "payment failed", "upi", "invoice",
    ],
    "certificate_verification": [
        "verify certificate", "certificate verification", "verify my certificate",
        "verify someone", "how does verification work", "check certificate",
        "validate certificate",
    ],
    "certificate_query": [
        "certificate", "cert not showing", "download certificate", "certificate details",
        "certificate incorrect", "wrong name on certificate",
    ],
    "offer_letter_query": [
        "offer letter", "appointment letter", "offer not received", "download offer",
    ],
    "internship_inquiry": [
        "internship", "intern", "stipend", "internship certificate", "internship assignment",
        "apply for internship", "internship eligibility",
    ],
    "training_inquiry": [
        "training program", "training", "bootcamp", "corporate readiness", "placement training",
    ],
    "workshop_inquiry": [
        "workshop", "webinar", "live session", "one day session",
    ],
    "enrollment_query": [
        "enroll", "enrolment", "enrollment", "register for course", "sign up for course",
        "join the course",
    ],
    "course_inquiry": [
        "course", "courses", "syllabus", "curriculum", "fees", "fee", "duration of",
        "duration", "how long", "is it recorded", "is it live", "which course",
        "suitable for me", "what's included", "what is included",
    ],
    "website_navigation": [
        "where can i find", "where is the page", "which page", "navigate to", "link to",
        "where do i go", "show me the page", "take me to",
    ],
    "technical_support": [
        "not working", "error", "bug", "site is down", "page not loading", "broken link",
        "can't log in", "cannot log in", "login issue", "app crashed",
    ],
    "general_query": [
        "hi", "hello", "hey", "help", "who are you", "what can you do", "about vaultofcodes",
    ],
}

# Escalation keywords: if any of these appear, we escalate regardless of the
# matched intent (per spec section 7 & the "Restrictions" in the system prompt:
# never promise refunds, never claim account-specific access, never guess).
ESCALATION_TRIGGERS = {
    "payment_query": [
        "payment", "refund", "money deducted", "transaction failed", "charged twice",
        "double charged", "paid but",
    ],
    "account_specific": [
        "my account", "my order", "my enrollment", "haven't received access",
        "not received access", "my dashboard",
    ],
    "certificate_correction": [
        "wrong name", "incorrect name", "certificate is wrong", "certificate has the wrong",
        "details are incorrect", "spelling mistake", "name is misspelled",
    ],
    "offer_letter_issue": [
        "offer letter is not available", "haven't received my offer", "not received my offer",
        "name is incorrect on my offer", "offer letter not available",
    ],
    "internship_dispute": [
        "internship dispute", "did not get my stipend", "stipend not received",
        "internship certificate not issued", "not received internship certificate",
    ],
    "explicit_human_request": [
        "talk to a human", "speak to a human", "real person", "human agent",
        "talk to someone", "customer care",
    ],
    "technical_unresolved": [
        "still not working", "not fixed", "same issue again",
    ],
}


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def classify_intent(message: str) -> str:
    """Return the single best-matching intent for a user message."""
    norm = _normalize(message)
    if not norm:
        return "unknown"

    scores = {}
    for intent, phrases in INTENT_KEYWORDS.items():
        score = 0
        for phrase in phrases:
            if phrase in norm:
                # Longer / multi-word phrases are more specific -> weight more.
                score += 1 + phrase.count(" ")
        if score:
            scores[intent] = score

    if not scores:
        return "unknown"

    # Pick the highest-scoring intent; ties broken by INTENT_KEYWORDS order
    # (which is already ordered specific -> generic).
    best_intent = max(scores, key=lambda k: (scores[k], -list(INTENT_KEYWORDS).index(k)))
    return best_intent


def needs_escalation(message: str):
    """
    Returns (should_escalate: bool, reason: str|None).
    This is checked independently of intent classification because an
    escalation-worthy phrase can appear inside what otherwise looks like a
    normal informational question (e.g. a certificate_query that turns out
    to be a correction request).
    """
    norm = _normalize(message)
    for reason, phrases in ESCALATION_TRIGGERS.items():
        for phrase in phrases:
            if phrase in norm:
                return True, reason
    return False, None
