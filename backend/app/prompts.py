from typing import Optional
from .preprocessor import PromptTokenizerCleaner

OUTREACH_TEMPLATE_TYPES = ("cold_outreach", "thank_you", "follow_up")


def build_tailor_prompt(
    resume_text: str, role: str, company: str, description: str
) -> str:
    cleaned_resume = PromptTokenizerCleaner.clean_resume(resume_text)
    cleaned_desc = PromptTokenizerCleaner.clean_job_description(description)
    return f"""Here is my current resume:
---
{cleaned_resume}
---
Here is a job description for a {role} role at {company}:
---
{cleaned_desc}
---
Rewrite my resume to be tailored to this job. Keep it truthful — only re-emphasize, reorder, and rephrase existing experience, don't invent anything new. Return the full tailored resume in clean markdown. Do NOT output <think> tags or your internal thinking process."""


def build_cover_letter_prompt(
    resume_text: str, role: str, company: str, description: str
) -> str:
    cleaned_resume = PromptTokenizerCleaner.clean_resume(resume_text)
    cleaned_desc = PromptTokenizerCleaner.clean_job_description(description)
    return f"""Here is my current resume:
---
{cleaned_resume}
---
Here is a job description for a {role} role at {company}:
---
{cleaned_desc}
---
Write a compelling, professional cover letter (3-4 short paragraphs) for this position. Connect my real experience to the specific requirements in the job description — highlight the most relevant skills and achievements. Keep it truthful: only reference experience that appears in my resume, don't invent anything new. Return only the cover letter text (greeting, body, sign-off). Do NOT output <think> tags or your internal thinking process."""


def build_outreach_prompt(
    role: str,
    company: str,
    contact_name: Optional[str] = None,
    template_type: str = "cold_outreach",
    notes: Optional[str] = None,
) -> str:
    greeting = f"to {contact_name.strip()}" if contact_name and contact_name.strip() else "to a recruiter or hiring manager"
    cleaned_notes = PromptTokenizerCleaner.clean_text(notes) if notes else ""
    context = f"\nAdditional application context/notes:\n{cleaned_notes}\n" if cleaned_notes else ""

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
Keep the email concise, professional, and ready to customize and send. Do NOT output <think> tags or your internal thinking process."""
