import re
from typing import List


class PromptTokenizerCleaner:
    """Lightweight tokenizer, boilerplate cleaner, and token-budget compressor."""

    # Section headers to completely exclude from prompt context
    EXCLUDED_SECTION_PATTERNS = [
        r"(?:equal\s+opportunity|eeo\s+statement|diversity\s*(?:&|and)\s*inclusion|affirmative\s+action)",
        r"(?:benefits\s*(?:&|and)\s*perks|what\s+we\s+offer|our\s+benefits|compensation\s*(?:&|and)\s*benefits|perks)",
        r"(?:notice\s+to\s+(?:recruitment|staffing|agencies)|agency\s+disclaimer|third\s+party\s+recruiters)",
        r"(?:privacy\s+notice|privacy\s+policy|ccpa\s+notice|data\s+protection)",
        r"(?:covid-19|vaccination\s+policy|drug-free\s+workplace|background\s+check\s+notice)",
        r"(?:about\s+(?:us|the\s+company|our\s+client|our\s+team|outsource\s+teams)|company\s+overview|who\s+we\s+are)",
        r"(?:how\s+we\s+hire|recruitment\s+process|interview\s+process|hiring\s+stages|selection\s+process)",
        r"(?:employer\s+questions|application\s+questions|screening\s+questions|questions\s+from\s+the\s+employer|your\s+application\s+will\s+include)",
        r"(?:schedule|working\s+hours|shift\s+details)",
    ]

    # Section headers to prioritize (breaks skip mode if encountered)
    PRIORITY_SECTION_PATTERNS = [
        r"(?:^|\b)(?:requirements|qualifications|minimum\s+qualifications|basic\s+qualifications|preferred\s+qualifications)\b",
        r"(?:^|\b)(?:responsibilities|duties|what\s+you(?:'ll|\s+will)\s+do|key\s+responsibilities|day-to-day)\b",
        r"(?:^|\b)(?:technical\s+skills|tech\s+stack|core\s+competencies|^skills(?:\s*:|$)|what\s+you\s+bring|who\s+you\s+are)\b",
    ]

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count based on standard ~4 characters per token heuristic."""
        if not text:
            return 0
        return max(1, len(text.strip()) // 4)

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Strip raw HTML, unescape common entities, and normalize whitespace."""
        if not text:
            return ""
        # Strip HTML tags
        cleaned = re.sub(r"<[^>]+>", " ", text)
        cleaned = (
            cleaned.replace("&nbsp;", " ")
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )
        # Normalize carriage returns and tabs
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse multiple blank lines
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    @classmethod
    def clean_job_description(cls, description: str, max_tokens: int = 800) -> str:
        """
        Tokenize and clean a job description:
        1. Strips HTML & boilerplate disclaimers (EEO, benefits, legal notices).
        2. Segments into structural paragraphs/sections.
        3. Prioritizes requirements, qualifications, and core duties.
        4. Enforces max_tokens budget (default 800 tokens = ~3,200 chars).
        """
        raw = cls.clean_text(description)
        if not raw:
            return ""

        lines = [line.strip() for line in raw.splitlines()]
        filtered_lines: List[str] = []
        skip_block = False

        for line in lines:
            if not line:
                if filtered_lines and filtered_lines[-1] != "":
                    filtered_lines.append("")
                continue

            lower_line = line.lower()

            # Check if this line starts a boilerplate/excluded section
            if any(re.search(pat, lower_line) for pat in cls.EXCLUDED_SECTION_PATTERNS):
                skip_block = True
                continue

            # Check if this line starts a priority section (breaks skip mode)
            if skip_block and any(re.search(pat, lower_line) for pat in cls.PRIORITY_SECTION_PATTERNS):
                skip_block = False

            if not skip_block:
                filtered_lines.append(line)

        cleaned_text = "\n".join(filtered_lines).strip()
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

        # Enforce token budget
        max_chars = max_tokens * 4
        if len(cleaned_text) > max_chars:
            truncated = cleaned_text[:max_chars]
            last_break = max(truncated.rfind("\n\n"), truncated.rfind("\n"), truncated.rfind(". "))
            if last_break > max_chars // 2:
                truncated = truncated[:last_break]
            cleaned_text = truncated.strip() + "\n\n[...job requirements summarized for brevity...]"

        return cleaned_text

    @classmethod
    def clean_resume(cls, resume_text: str, max_tokens: int = 1500) -> str:
        """Normalize master resume whitespace and enforce token limit."""
        cleaned = cls.clean_text(resume_text)
        max_chars = max_tokens * 4
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars].rsplit("\n", 1)[0]
        return cleaned
