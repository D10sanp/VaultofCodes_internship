"""
router.py

Smart routing: given a classified intent + message, decide what the bot
says, which links it offers, and whether the "last topic" (for conversation
memory / pronoun resolution) should be updated.

Also holds resolve_context(), which does simple pronoun resolution ("its
duration" -> "Python course duration") using the session's last_topic.
"""

import re

from knowledge_base import KB

# Deliberately narrow: bare "it"/"this"/"that" are too common in unrelated
# sentences ("wrong name on it") and would wrongly pull in the last topic.
# Only trigger on possessive/referential phrases that clearly point back to
# a previously discussed course or program.
PRONOUN_PATTERN = re.compile(
    r"\b(its|it's|this course|that course|the course|this program|that program|the program)\b",
    re.IGNORECASE,
)

FALLBACK_MESSAGE = (
    "I'm not able to find reliable information about that. "
    "Please contact our support team on WhatsApp for assistance."
)

ESCALATION_MESSAGE = (
    "This issue requires our support team to check your details. "
    "Please contact us on WhatsApp and our team will assist you."
)


def _find_course(text: str):
    norm = text.lower()
    for course in KB["courses"]:
        if course["name"].lower() in norm:
            return course
        for alias in course["aliases"]:
            if alias in norm:
                return course
    return None


def _find_training_program(text: str):
    norm = text.lower()
    for program in KB["training_programs"]:
        if program["name"].lower() in norm:
            return program
        for alias in program["aliases"]:
            if alias in norm:
                return program
    return None


def resolve_context(message: str, session: dict) -> str:
    """
    If the message uses a pronoun ("its duration") and we have a
    remembered last_topic (e.g. a course name), splice the topic name into
    the message so downstream matching/lookup works without the user having
    to repeat themselves.
    """
    last_topic = session.get("last_topic")
    if not last_topic:
        return message

    # Only rewrite if the message doesn't already name a course/program
    # explicitly (avoid clobbering an explicit new subject).
    if _find_course(message) or _find_training_program(message):
        return message

    if PRONOUN_PATTERN.search(message):
        return f"{message} (regarding {last_topic})"

    return message


def build_response(intent: str, message: str, escalate: bool, escalate_reason: str | None):
    """
    Returns (reply: str, links: list[dict], quick_replies: list[str], topic: str|None)
    `topic` is what should be remembered as session['last_topic'], or None to
    leave it unchanged.
    """
    links = []
    quick_replies = []
    topic = None

    # Escalation takes priority over everything else, per spec section 7 &
    # the system prompt restrictions (never guess, never promise refunds,
    # never claim account access).
    if escalate:
        return ESCALATION_MESSAGE, links, quick_replies, topic

    if intent == "course_inquiry":
        course = _find_course(message)
        if course:
            reply = (
                f"**{course['name']}**\n"
                f"{course['description']}\n\n"
                f"• Duration: {course['duration']}\n"
                f"• Mode: {course['mode']}\n"
                f"• Fees: {course['fees']}\n"
                f"• Certificate: {'Yes' if course['certificate'] else 'No'}"
            )
            links = [{"label": f"View {course['name']} page", "url": course["link"]}]
            topic = course["name"]
        else:
            names = ", ".join(c["name"] for c in KB["courses"])
            reply = f"We currently offer: {names}. Tell me which one you'd like details on, or browse them all here."
            links = [{"label": "Browse all courses", "url": KB["pages"]["courses"]}]
        return reply, links, quick_replies, topic

    if intent == "training_inquiry":
        program = _find_training_program(message)
        if program:
            reply = f"**{program['name']}**\n{program['description']}\n\n• Duration: {program['duration']}"
            links = [{"label": f"View {program['name']} page", "url": program["link"]}]
            topic = program["name"]
        else:
            names = ", ".join(p["name"] for p in KB["training_programs"])
            reply = f"Our training programs include: {names}. Want details on one of these?"
            links = [{"label": "View all training programs", "url": KB["pages"]["training_programs"]}]
        return reply, links, quick_replies, topic

    if intent == "internship_inquiry":
        internship = KB["internship"]
        norm = message.lower()
        if "apply" in norm or "how can i apply" in norm:
            reply = internship["how_to_apply"]
            links = [{"label": "Go to internship application", "url": KB["pages"]["internship_apply"]}]
        elif "paid" in norm or "stipend" in norm or "unpaid" in norm:
            reply = internship["paid_status"]
            links = [{"label": "View internship page", "url": internship["link"]}]
        elif "eligib" in norm or "who is eligible" in norm:
            reply = internship["eligibility"]
        elif "offer letter" in norm:
            reply = internship["offer_letter_process"]
            links = [{"label": "Offer letter page", "url": KB["pages"]["offer_letter"]}]
        elif "assignment" in norm:
            reply = internship["assignment_submission"]
            links = [{"label": "Go to dashboard", "url": KB["pages"]["student_dashboard"]}]
        elif "certificate" in norm:
            reply = internship["certificate_process"]
            links = [{"label": "Go to dashboard", "url": KB["pages"]["student_dashboard"]}]
        elif "duration" in norm or "how long" in norm:
            reply = f"Internship duration is {internship['duration']}."
        else:
            tracks = ", ".join(internship["tracks"])
            reply = f"We offer internships in: {tracks}. What would you like to know — eligibility, duration, how to apply, or stipend details?"
            links = [{"label": "View internship page", "url": internship["link"]}]
        topic = "the internship program"
        return reply, links, quick_replies, topic

    if intent == "workshop_inquiry":
        w = KB["workshops"]
        examples = ", ".join(w["examples"])
        reply = f"{w['description']} Recent examples: {examples}."
        links = [{"label": "View workshops", "url": w["link"]}]
        topic = "workshops"
        return reply, links, quick_replies, topic

    if intent == "certificate_verification":
        reply = KB["certificates"]["verification_info"]
        links = [{"label": "Certificate verification page", "url": KB["certificates"]["verification_link"]}]
        topic = "certificate verification"
        return reply, links, quick_replies, topic

    if intent == "certificate_query":
        reply = KB["certificates"]["download_info"]
        links = [{"label": "Certificates page", "url": KB["certificates"]["download_link"]}]
        topic = "certificates"
        return reply, links, quick_replies, topic

    if intent == "offer_letter_query":
        reply = KB["offer_letters"]["download_info"]
        links = [{"label": "Offer letter page", "url": KB["offer_letters"]["download_link"]}]
        topic = "your offer letter"
        return reply, links, quick_replies, topic

    if intent == "enrollment_query":
        reply = "You can enroll directly from any course page — click 'Enroll Now' and follow the registration steps."
        links = [{"label": "Browse courses to enroll", "url": KB["pages"]["courses"]}]
        return reply, links, quick_replies, topic

    if intent == "website_navigation":
        norm = message.lower()
        page_map = [
            (["free course"], "free_courses", "Free courses page"),
            (["course"], "courses", "Courses page"),
            (["internship"], "internships", "Internships page"),
            (["certificate verif", "verify certificate"], "certificate_verification", "Certificate verification page"),
            (["certificate"], "certificates", "Certificates page"),
            (["offer letter"], "offer_letter", "Offer letter page"),
            (["training"], "training_programs", "Training programs page"),
            (["workshop"], "workshops", "Workshops page"),
            (["dashboard"], "student_dashboard", "Student dashboard"),
            (["contact", "support"], "contact_support", "Contact support page"),
        ]
        for keywords, page_key, label in page_map:
            if any(k in norm for k in keywords):
                reply = f"Here's the {label.lower()} you're looking for:"
                links = [{"label": label, "url": KB["pages"][page_key]}]
                return reply, links, quick_replies, topic
        reply = "Here are our main pages — let me know which one you need:"
        links = [{"label": name.replace("_", " ").title(), "url": url} for name, url in list(KB["pages"].items())[:5]]
        return reply, links, quick_replies, topic

    if intent == "technical_support":
        reply = ESCALATION_MESSAGE
        return reply, links, quick_replies, topic

    if intent == "general_query":
        norm = message.lower()
        for faq in KB["faqs"]:
            if any(q in norm for q in faq["q"]):
                return faq["a"], links, quick_replies, topic
        if any(g in norm for g in ["hi", "hello", "hey"]):
            reply = "Hi! 👋 I'm the VaultOfCourse support assistant. I can help with courses, internships, certificates, offer letters, and website navigation. What do you need help with?"
        else:
            reply = "I can help with courses, training programs, internships, certificates, offer letters, and finding pages on our website. What would you like to know?"
        quick_replies = KB["suggested_questions"]
        return reply, links, quick_replies, topic

    # unknown
    return FALLBACK_MESSAGE, links, quick_replies, topic
