# VaultOfCodes Chatbot — Testing / Evaluation Report

**Result: 15 / 15 test cases passed**

| ID | Category | Message | Expected Intent | Actual Intent | Escalate (exp/act) | Links (exp/act) | Status |
|----|----------|---------|------------------|----------------|----------------------|-------------------|--------|
| TC01 | Course inquiry | What ethical hacking courses do you have? | `course_inquiry` | `course_inquiry` | False/False | yes/1 | ✅ PASS |
| TC02 | Training inquiry | Tell me about your corporate readiness training program | `training_inquiry` | `training_inquiry` | False/False | yes/1 | ✅ PASS |
| TC03 | Internship inquiry | I want to apply for an internship | `internship_inquiry` | `internship_inquiry` | False/False | yes/1 | ✅ PASS |
| TC04 | Certificate issue | My certificate is not showing in my dashboard | `certificate_query` | `certificate_query` | True/True | no/0 | ✅ PASS |
| TC05 | Certificate correction (should escalate) | My certificate has the wrong name on it | `certificate_query` | `certificate_query` | True/True | no/0 | ✅ PASS |
| TC06 | Offer letter issue | I have not received my offer letter | `offer_letter_query` | `offer_letter_query` | True/True | no/0 | ✅ PASS |
| TC07 | Certificate verification | Where can I verify my certificate? | `certificate_verification` | `certificate_verification` | False/False | yes/1 | ✅ PASS |
| TC08 | Website navigation | Where can I find free courses? | `website_navigation` | `website_navigation` | False/False | yes/1 | ✅ PASS |
| TC09 | Payment question (should escalate) | I paid but haven't received access to my course | `payment_query` | `payment_query` | True/True | no/0 | ✅ PASS |
| TC10 | Technical issue | The website is not working and giving me an error | `technical_support` | `technical_support` | True/True | no/0 | ✅ PASS |
| TC11 | Random / general question | Hi there, what can you help me with? | `general_query` | `general_query` | False/False | no/0 | ✅ PASS |
| TC12 | Unclear / out-of-scope question | What's the weather like today? | `unknown` | `unknown` | False/False | no/0 | ✅ PASS |
| TC13 | Human support (explicit) | I want to talk to a human agent | `human_support` | `human_support` | True/True | no/0 | ✅ PASS |
| TC14 | Course inquiry (specific course) | Tell me about your Python course | `course_inquiry` | `course_inquiry` | False/False | yes/1 | ✅ PASS |
| TC15 | Conversation memory (context follow-up) | What's its duration? | `course_inquiry` | `course_inquiry` | False/False | yes/1 | ✅ PASS |

## Reply previews

**TC01** (Course inquiry)
> Q: What ethical hacking courses do you have?
> A: **Ethical Hacking**
Introduces penetration testing basics, network security, and common vulnerabilities in a legal, ethi

**TC02** (Training inquiry)
> Q: Tell me about your corporate readiness training program
> A: **Corporate Readiness Training**
Resume building, mock interviews, and soft-skills training for job readiness.

• Durati

**TC03** (Internship inquiry)
> Q: I want to apply for an internship
> A: Apply directly from the internship page by filling out the application form and submitting the requested details.

**TC04** (Certificate issue)
> Q: My certificate is not showing in my dashboard
> A: This issue requires our support team to check your details. Please contact us on WhatsApp and our team will assist you.

**TC05** (Certificate correction (should escalate))
> Q: My certificate has the wrong name on it
> A: This issue requires our support team to check your details. Please contact us on WhatsApp and our team will assist you.

**TC06** (Offer letter issue)
> Q: I have not received my offer letter
> A: This issue requires our support team to check your details. Please contact us on WhatsApp and our team will assist you.

**TC07** (Certificate verification)
> Q: Where can I verify my certificate?
> A: Anyone can verify a VaultOfCodes certificate using the certificate ID on our verification page — no login required.

**TC08** (Website navigation)
> Q: Where can I find free courses?
> A: Here's the free courses page you're looking for:

**TC09** (Payment question (should escalate))
> Q: I paid but haven't received access to my course
> A: This issue requires our support team to check your details. Please contact us on WhatsApp and our team will assist you.

**TC10** (Technical issue)
> Q: The website is not working and giving me an error
> A: This issue requires our support team to check your details. Please contact us on WhatsApp and our team will assist you.

**TC11** (Random / general question)
> Q: Hi there, what can you help me with?
> A: Hi! 👋 I'm the VaultOfCodes support assistant. I can help with courses, internships, certificates, offer letters, and we

**TC12** (Unclear / out-of-scope question)
> Q: What's the weather like today?
> A: I'm not able to find reliable information about that. Please contact our support team on WhatsApp for assistance.

**TC13** (Human support (explicit))
> Q: I want to talk to a human agent
> A: This issue requires our support team to check your details. Please contact us on WhatsApp and our team will assist you.

**TC14** (Course inquiry (specific course))
> Q: Tell me about your Python course
> A: **Python Programming**
Covers Python fundamentals, OOP, file handling, and mini projects.

• Duration: 6 weeks
• Mode: R

**TC15** (Conversation memory (context follow-up))
> Q: What's its duration?
> A: **Python Programming**
Covers Python fundamentals, OOP, file handling, and mini projects.

• Duration: 6 weeks
• Mode: R

## Coverage checklist (per assignment spec, section 15)

- [x] Course inquiries
- [x] Training inquiries
- [x] Internship inquiries
- [x] Certificate issues
- [x] Offer letter issues
- [x] Verification queries
- [x] Website navigation
- [x] Payment questions
- [x] Technical issues
- [x] Random/general questions
- [x] Unclear questions
- [x] Human support
- [x] Conversation memory (context retention)