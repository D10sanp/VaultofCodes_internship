"""
knowledge_base.py

Structured knowledge base for the VaultOfCodes support chatbot.

IMPORTANT (for the intern/team maintaining this project):
The values below (course details, fees, durations, links, phone numbers) are
SAMPLE / PLACEHOLDER data so the chatbot has something real to retrieve from
and demonstrate "answer from knowledge base, not invented facts". Replace the
contents of this file with VaultOfCodes's real, current information before
going live. The chatbot code never invents facts beyond what's in here.
"""

BASE_URL = "https://www.vaultofcodes.com"

KB = {
    # ------------------------------------------------------------------
    # Website pages used for navigation / redirection
    # ------------------------------------------------------------------
    "pages": {
        "courses": f"{BASE_URL}/courses",
        "free_courses": f"{BASE_URL}/courses/free",
        "training_programs": f"{BASE_URL}/training-programs",
        "internships": f"{BASE_URL}/internships",
        "internship_apply": f"{BASE_URL}/internships/apply",
        "workshops": f"{BASE_URL}/workshops",
        "certificates": f"{BASE_URL}/certificates",
        "certificate_verification": f"{BASE_URL}/verify-certificate",
        "offer_letter": f"{BASE_URL}/offer-letter",
        "offer_letter_verification": f"{BASE_URL}/verify-offer-letter",
        "enrollment": f"{BASE_URL}/enroll",
        "student_dashboard": f"{BASE_URL}/dashboard",
        "faq": f"{BASE_URL}/faq",
        "contact_support": f"{BASE_URL}/contact",
    },

    # ------------------------------------------------------------------
    # Contact / escalation channels
    # ------------------------------------------------------------------
    "support": {
        "whatsapp_number_display": "+91 00000 00000",
        "whatsapp_link": "https://wa.me/910000000000",
        "email": "support@vaultofcodes.com",
        "hours": "Monday–Saturday, 10:00 AM – 7:00 PM IST",
    },

    # ------------------------------------------------------------------
    # Courses (sample data)
    # ------------------------------------------------------------------
    "courses": [
        {
            "name": "Python Programming",
            "aliases": ["python", "python course", "python programming"],
            "duration": "6 weeks",
            "mode": "Recorded + Live doubt-clearing sessions",
            "fees": "₹4,999",
            "certificate": True,
            "description": "Covers Python fundamentals, OOP, file handling, and mini projects.",
            "link": f"{BASE_URL}/courses/python-programming",
        },
        {
            "name": "Ethical Hacking",
            "aliases": ["ethical hacking", "hacking", "cybersecurity basics"],
            "duration": "8 weeks",
            "mode": "Live sessions with recordings provided",
            "fees": "₹7,999",
            "certificate": True,
            "description": "Introduces penetration testing basics, network security, and common vulnerabilities in a legal, ethical lab environment.",
            "link": f"{BASE_URL}/courses/ethical-hacking",
        },
        {
            "name": "Data Science & Analytics",
            "aliases": ["data science", "data analytics", "data analyst"],
            "duration": "10 weeks",
            "mode": "Recorded",
            "fees": "₹9,999",
            "certificate": True,
            "description": "Covers Python for data analysis, statistics, visualization, and an introduction to machine learning.",
            "link": f"{BASE_URL}/courses/data-science",
        },
        {
            "name": "Web Development (Full Stack)",
            "aliases": ["web development", "full stack", "web dev", "mern"],
            "duration": "12 weeks",
            "mode": "Live + Recorded",
            "fees": "₹11,999",
            "certificate": True,
            "description": "HTML, CSS, JavaScript, React, Node.js, and databases, ending with a capstone project.",
            "link": f"{BASE_URL}/courses/web-development",
        },
        {
            "name": "Digital Marketing",
            "aliases": ["digital marketing", "marketing course", "seo course"],
            "duration": "4 weeks",
            "mode": "Recorded",
            "fees": "₹2,999",
            "certificate": True,
            "description": "SEO, social media marketing, Google Ads, and content marketing basics.",
            "link": f"{BASE_URL}/courses/digital-marketing",
        },
    ],

    # ------------------------------------------------------------------
    # Training programs (broader / cohort-based, sample data)
    # ------------------------------------------------------------------
    "training_programs": [
        {
            "name": "Corporate Readiness Training",
            "aliases": ["corporate training", "placement training", "readiness program"],
            "duration": "4 weeks",
            "description": "Resume building, mock interviews, and soft-skills training for job readiness.",
            "link": f"{BASE_URL}/training-programs/corporate-readiness",
        },
        {
            "name": "Advanced Data Science Bootcamp",
            "aliases": ["bootcamp", "advanced data science", "ds bootcamp"],
            "duration": "16 weeks",
            "description": "An intensive, project-heavy extension of the Data Science course for advanced learners.",
            "link": f"{BASE_URL}/training-programs/data-science-bootcamp",
        },
    ],

    # ------------------------------------------------------------------
    # Internship program details (sample data)
    # ------------------------------------------------------------------
    "internship": {
        "tracks": ["Web Development", "Data Science", "Digital Marketing", "Content Writing", "Ethical Hacking"],
        "duration": "4 to 12 weeks (track dependent)",
        "paid_status": "Most internships are unpaid/learning-based; select tracks offer stipends based on performance — check the internship page for the current list.",
        "eligibility": "Open to students and recent graduates who have completed (or are currently enrolled in) a related VaultOfCodes course, or who meet the criteria listed on the internship page.",
        "how_to_apply": "Apply directly from the internship page by filling out the application form and submitting the requested details.",
        "offer_letter_process": "Offer letters are generated automatically after your application is approved and are made available in your student dashboard.",
        "certificate_process": "Internship completion certificates are issued after all assignments are submitted and reviewed, and appear in your dashboard.",
        "assignment_submission": "Assignments are submitted through the internship section of your student dashboard.",
        "link": f"{BASE_URL}/internships",
    },

    # ------------------------------------------------------------------
    # Workshops (sample data)
    # ------------------------------------------------------------------
    "workshops": {
        "description": "Short, focused live sessions (1-3 days) on trending tools and skills, open to all students.",
        "examples": ["Resume & LinkedIn Optimization", "Intro to Generative AI", "Git & GitHub Essentials"],
        "link": f"{BASE_URL}/workshops",
    },

    # ------------------------------------------------------------------
    # Certificates
    # ------------------------------------------------------------------
    "certificates": {
        "download_info": "Certificates can be downloaded from the student dashboard once a course or internship is marked complete.",
        "verification_info": "Anyone can verify a VaultOfCodes certificate using the certificate ID on our verification page — no login required.",
        "download_link": f"{BASE_URL}/certificates",
        "verification_link": f"{BASE_URL}/verify-certificate",
    },

    # ------------------------------------------------------------------
    # Offer letters
    # ------------------------------------------------------------------
    "offer_letters": {
        "download_info": "Offer letters for approved internships are available for download from the student dashboard under the 'Internship' tab.",
        "download_link": f"{BASE_URL}/offer-letter",
        "verification_link": f"{BASE_URL}/verify-offer-letter",
    },

    # ------------------------------------------------------------------
    # General FAQs
    # ------------------------------------------------------------------
    "faqs": [
        {
            "q": ["how do i enroll", "how can i enroll", "how to join a course"],
            "a": "You can enroll directly from any course page by clicking 'Enroll Now' and completing the payment/registration steps.",
        },
        {
            "q": ["do you provide certificates", "will i get a certificate"],
            "a": "Yes, all courses and internships include a certificate of completion once you finish the required work.",
        },
        {
            "q": ["how do i access my course", "where is my course"],
            "a": "Enrolled courses appear in your student dashboard under 'My Courses'.",
        },
    ],

    # ------------------------------------------------------------------
    # Suggested quick-action questions shown when the chat opens
    # ------------------------------------------------------------------
    "suggested_questions": [
        "🎓 Explore Courses",
        "💼 Internship Information",
        "📜 Certificate Verification",
        "📄 Offer Letter",
        "🏫 Training Programs",
        "❓ General Help",
        "💬 Contact Support",
    ],
}
