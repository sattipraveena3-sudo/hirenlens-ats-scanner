from hirelens.ai import enrich
from hirelens.scoring import analyze_resume
from hirelens.schemas import AnalysisResponse


def run_analysis(resume: str, job_description: str, use_ai: bool = True) -> AnalysisResponse:
    result = analyze_resume(resume, job_description)
    if not use_ai:
        return result
    ai = enrich(resume, job_description, result.model_dump())
    if not ai:
        return result
    if isinstance(ai.get("summary"), str) and ai["summary"].strip():
        result.summary = ai["summary"].strip()
    for field in ("strengths", "improvements", "ats_tips"):
        value = ai.get(field)
        if isinstance(value, list) and all(isinstance(x, str) for x in value):
            setattr(result, field, value[:8])
    result.mode = "deterministic+groq"
    return result
