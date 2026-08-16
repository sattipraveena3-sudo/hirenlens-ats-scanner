from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    resume: str = Field(min_length=20, max_length=100_000)
    job_description: str = Field(min_length=20, max_length=50_000)
    use_ai: bool = True


class ScoreBreakdown(BaseModel):
    keyword_match: float
    skill_match: float
    section_quality: float
    impact_quality: float
    readability: float


class AnalysisResponse(BaseModel):
    match_score: int
    verdict: str
    summary: str
    matched_keywords: list[str]
    missing_keywords: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    improvements: list[str]
    ats_tips: list[str]
    breakdown: ScoreBreakdown
    mode: str
