import os
import uuid
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, prompts, schemas
from ..database import get_db
from ..llm import clean_thinking_tags

router = APIRouter(prefix="/api/applications", tags=["documents"])


def call_llm(prompt: str, model_name: str) -> str:
    local_llm_url = os.getenv(
        "LOCAL_LLM_URL", "http://host.docker.internal:8080"
    ).rstrip("/")

    generated_text: Optional[str] = None
    last_error: Optional[Exception] = None

    # Primary: OpenAI format (/v1/chat/completions)
    try:
        res = httpx.post(
            f"{local_llm_url}/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=180.0,
        )
        res.raise_for_status()
        data = res.json()
        choices = data.get("choices")
        if choices and isinstance(choices, list) and len(choices) > 0:
            msg = choices[0].get("message", {})
            content = msg.get("content")
            if content and str(content).strip():
                sanitized = clean_thinking_tags(str(content).strip())
                if sanitized:
                    generated_text = sanitized
    except Exception as exc:
        last_error = exc

    # Fallback 1: llama.cpp native completion endpoint (/completion)
    if not generated_text:
        try:
            res = httpx.post(
                f"{local_llm_url}/completion",
                json={
                    "prompt": prompt,
                    "temperature": 0.2,
                },
                timeout=180.0,
            )
            res.raise_for_status()
            data = res.json()
            content = data.get("content")
            if content and str(content).strip():
                sanitized = clean_thinking_tags(str(content).strip())
                if sanitized:
                    generated_text = sanitized
        except Exception as exc:
            last_error = exc

    # Fallback 2: Ollama format (/api/generate)
    if not generated_text:
        try:
            res = httpx.post(
                f"{local_llm_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=180.0,
            )
            res.raise_for_status()
            data = res.json()
            response_val = data.get("response")
            if response_val and str(response_val).strip():
                sanitized = clean_thinking_tags(str(response_val).strip())
                if sanitized:
                    generated_text = sanitized
        except Exception as exc:
            last_error = exc

    if not generated_text:
        detail = (
            f"Local LLM service error: {str(last_error)}"
            if last_error
            else "Local LLM service returned empty response"
        )
        raise HTTPException(
            status_code=502,
            detail=detail,
        )

    return clean_thinking_tags(generated_text)


@router.get(
    "/{application_id}/cover-letter/prompt",
    response_model=schemas.TailorPromptOut,
)
def get_cover_letter_prompt(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    application = crud.get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if not application.description or not application.description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description is required to generate cover letter prompt",
        )
    master_resume = crud.get_or_create_resume(db)
    if not master_resume.content or not master_resume.content.strip():
        raise HTTPException(
            status_code=400,
            detail="Base resume is required. Please set your master resume first.",
        )
    prompt = prompts.build_cover_letter_prompt(
        resume_text=master_resume.content,
        role=application.role,
        company=application.company,
        description=application.description,
    )
    return schemas.TailorPromptOut(prompt=prompt)


@router.post(
    "/{application_id}/cover-letter/generate-local",
    response_model=schemas.DocumentOut,
)
def generate_local_cover_letter(
    application_id: uuid.UUID,
    payload: Optional[schemas.GenerateDocumentRequest] = None,
    db: Session = Depends(get_db),
):
    application = crud.get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if not application.description or not application.description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description is required to generate cover letter",
        )
    master_resume = crud.get_or_create_resume(db)
    if not master_resume.content or not master_resume.content.strip():
        raise HTTPException(
            status_code=400,
            detail="Base resume is required. Please set your master resume first.",
        )

    model = (
        payload.model.strip()
        if payload and payload.model and payload.model.strip()
        else None
    ) or os.getenv("LOCAL_LLM_MODEL", "Swift-1.5-Qwen3.8-27B-GSQ-RCO")

    prompt = prompts.build_cover_letter_prompt(
        resume_text=master_resume.content,
        role=application.role,
        company=application.company,
        description=application.description,
    )

    generated_text = call_llm(prompt=prompt, model_name=model)
    return schemas.DocumentOut(content=clean_thinking_tags(generated_text), document_type="cover_letter")


@router.get(
    "/{application_id}/outreach/prompt",
    response_model=schemas.TailorPromptOut,
)
def get_outreach_prompt(
    application_id: uuid.UUID,
    template_type: str = Query("cold_outreach"),
    db: Session = Depends(get_db),
):
    application = crud.get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    prompt = prompts.build_outreach_prompt(
        role=application.role,
        company=application.company,
        contact_name=application.contact_name,
        template_type=template_type,
        notes=application.notes,
    )
    return schemas.TailorPromptOut(prompt=prompt)


@router.post(
    "/{application_id}/outreach/generate-local",
    response_model=schemas.DocumentOut,
)
def generate_local_outreach(
    application_id: uuid.UUID,
    payload: Optional[schemas.GenerateDocumentRequest] = None,
    db: Session = Depends(get_db),
):
    application = crud.get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    template_type = (
        payload.template_type if payload and payload.template_type else "cold_outreach"
    )
    model = (
        payload.model.strip()
        if payload and payload.model and payload.model.strip()
        else None
    ) or os.getenv("LOCAL_LLM_MODEL", "Swift-1.5-Qwen3.8-27B-GSQ-RCO")

    prompt = prompts.build_outreach_prompt(
        role=application.role,
        company=application.company,
        contact_name=application.contact_name,
        template_type=template_type,
        notes=application.notes,
    )

    generated_text = call_llm(prompt=prompt, model_name=model)
    return schemas.DocumentOut(content=clean_thinking_tags(generated_text), document_type=template_type)
