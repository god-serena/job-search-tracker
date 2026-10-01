from typing import Optional


from typing import Optional


def build_tailor_prompt(
    resume_text: str, role: str, company: str, description: str
) -> str:
    return f"""Here is my current resume:
---
{resume_text}
---
Here is a job description for a {role} role at {company}:
---
{description}
---
Rewrite my resume to be tailored to this job. Keep it truthful — only re-emphasize, reorder, and rephrase existing experience, don't invent anything new. Return the full tailored resume."""


def build_cover_letter_prompt(
    resume_text: str, role: str, company: str, description: str
) -> str:
    return f"""Here is my current resume:
---
{resume_text}
---
Here is a job description for a {role} role at {company}:
---
{description}
---
Write a compelling, professional cover letter (3-4 short paragraphs) for this application. Connect my real experience to the specific requirements in the job description — highlight the most relevant skills and achievements. Keep it truthful: only reference experience that appears in my resume, don't invent anything new. Use a confident, warm but not pushy tone. Return only the cover letter text (greeting, body, sign-off), no explanations."""


OUTREACH_TEMPLATE_TYPES = ("cold_outreach", "thank_you", "follow_up")


def build_outreach_prompt(
    role: str,
    company: str,
    contact_name: Optional[str],
    template_type: str,
    notes: Optional[str],
) -> str:
    recipient = contact_name.strip() if contact_name and contact_name.strip() else "the hiring team"
    notes_block = (
        f"Additional context from the candidate:\n---\n{notes.strip()}\n---\n\n"
        if notes and notes.strip()
        else ""
    )

    if template_type == "thank_you":
        task = (
            f"Write a warm thank-you email to {recipient} after an interview "
            f"for the {role} role at {company}. Express appreciation, briefly "
            "recap one or two specific points discussed to reinforce fit, and "
            "restate enthusiasm for the role. Keep it to 3-5 sentences, "
            "professional and concise."
        )
    elif template_type == "follow_up":
        task = (
            f"Write a polite follow-up email to {recipient} checking the status "
            f"of the application for the {role} role at {company}. Keep it to "
            "3-4 sentences, friendly and professional, without sounding "
            "demanding."
        )
    else:  # cold_outreach
        task = (
            f"Write a concise cold outreach email to {recipient} at {company} "
            f"expressing interest in the {role} role. Pitch why I'm a strong "
            "fit in 2-3 sentences and propose a brief conversation. Keep it to "
            "4-6 sentences, professional and direct."
        )

    return f"""{notes_block}Write a professional outreach email.

{task}

Keep it truthful — do not invent achievements, details, or conversations. Return only the email text (greeting, body, sign-off), no explanations."""


def build_cover_letter_prompt(
    resume_text: str, role: str, company: str, description: str
) -> str:
    return f"""Here is my current resume:
---
{resume_text}
---
Here is a job description for a {role} role at {company}:
---
{description}
---
Write a professional, compelling, and tailored cover letter for this position. Connect specific experiences and skills from my resume to the requirements of the job. Keep it truthful to my resume and write 3-4 structured paragraphs ready to send."""


def build_outreach_prompt(
    role: str,
    company: str,
    contact_name: Optional[str] = None,
    template_type: str = "cold_outreach",
    notes: Optional[str] = None,
) -> str:
    greeting = f"to {contact_name}" if contact_name else "to a recruiter or hiring manager"
    context = f"\nAdditional application context/notes:\n{notes}\n" if notes else ""

    if template_type == "thank_you":
        instructions = f"Write a warm, professional post-interview thank you email {greeting} for the {role} position at {company}. Express genuine enthusiasm, briefly reference a strong alignment with the role, and offer to provide any additional information."
    elif template_type == "follow_up":
        instructions = f"Write a polite, concise follow-up email {greeting} regarding my application for the {role} position at {company}. Reiterate continued interest and inquire about the current timeline or next steps in the review process."
    else:  # cold_outreach
        instructions = f"Write a concise, compelling networking outreach email or LinkedIn message {greeting} regarding the {role} position at {company}. Briefly highlight why I am excited about {company} and ask if they would be open to a brief conversation."

    return f"""Context:
Role: {role}
Company: {company}
Target: {contact_name or "Hiring Team"}
{context}
Task:
{instructions}
Keep the email concise, professional, and ready to customize and send."""
