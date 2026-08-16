import json
import os
import re
from typing import Any

from groq import Groq

SYSTEM = """You are an ATS resume reviewer. Return ONLY valid JSON with keys summary, strengths, improvements, ats_tips. Each list must contain concise factual suggestions grounded only in the supplied resume and job description. Never invent experience or credentials."""


def enrich(resume: str, job_description: str, baseline: dict[str, Any]) -> dict[str, Any] | None:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    try:
        response = Groq(api_key=api_key).chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"BASELINE SCORE:\n{json.dumps(baseline)}\n\nRESUME:\n{resume}\n\nJOB DESCRIPTION:\n{job_description}"},
            ],
            temperature=0.15,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or "{}"
        return json.loads(re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.I))
    except Exception:
        return None
