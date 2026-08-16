import math
import re
from collections import Counter

from hirelens.schemas import AnalysisResponse, ScoreBreakdown

STOP = {"the","and","for","with","that","this","from","your","you","are","our","will","have","has","into","using","use","job","role","work","team","years","year","experience","skills","required","preferred"}
SKILLS = {
    "python","java","javascript","typescript","sql","aws","azure","gcp","docker","kubernetes","terraform","linux","git","fastapi","flask","django","streamlit","react","node","spark","airflow","dbt","snowflake","postgresql","mysql","mongodb","redis","pytorch","tensorflow","scikit-learn","sklearn","pandas","numpy","mlflow","langchain","rag","bert","transformers","nlp","machine learning","deep learning","data engineering","etl","rest api","microservices","ci/cd","github actions"
}
SECTIONS = {"summary", "experience", "education", "skills", "projects"}


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]{1,}", text.lower())


def _phrases(text: str) -> set[str]:
    low = text.lower()
    found = {s for s in SKILLS if s in low}
    found.update(t for t in _tokens(text) if t in SKILLS)
    return found


def _job_keywords(text: str, limit: int = 24) -> list[str]:
    counts = Counter(t for t in _tokens(text) if t not in STOP and len(t) > 2)
    return [k for k, _ in counts.most_common(limit)]


def _pct(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 1)


def analyze_resume(resume: str, job_description: str) -> AnalysisResponse:
    rlow, jlow = resume.lower(), job_description.lower()
    keywords = _job_keywords(job_description)
    matched_keywords = [k for k in keywords if k in rlow]
    missing_keywords = [k for k in keywords if k not in rlow]
    keyword_score = 100 * len(matched_keywords) / max(1, len(keywords))

    job_skills = sorted(_phrases(job_description))
    resume_skills = _phrases(resume)
    matched_skills = [s for s in job_skills if s in resume_skills]
    missing_skills = [s for s in job_skills if s not in resume_skills]
    skill_score = 100 if not job_skills else 100 * len(matched_skills) / len(job_skills)

    sections_found = {s for s in SECTIONS if re.search(rf"(?im)^\s*{re.escape(s)}\b", resume)}
    section_score = 100 * len(sections_found) / len(SECTIONS)

    bullets = len(re.findall(r"(?m)^\s*(?:[-*•]|\d+[.)])\s+", resume))
    quantified = len(re.findall(r"\b(?:\d+(?:\.\d+)?%|\$\s?\d+[\d,.]*|\d+[xX]\b|\d+[\d,]*\+?)", resume))
    impact_score = min(100.0, bullets * 5 + quantified * 12)

    words = _tokens(resume)
    avg_word = sum(map(len, words)) / max(1, len(words))
    sentence_count = max(1, len(re.findall(r"[.!?](?:\s|$)", resume)))
    avg_sentence = len(words) / sentence_count
    readability = 100 - max(0, avg_sentence - 24) * 2 - max(0, avg_word - 7) * 8
    readability = _pct(readability)

    score = round(
        keyword_score * .35 + skill_score * .30 + section_score * .15 + impact_score * .15 + readability * .05
    )
    score = max(0, min(100, score))
    verdict = "Strong match" if score >= 80 else "Competitive match" if score >= 65 else "Partial match" if score >= 45 else "Needs tailoring"

    strengths = []
    if keyword_score >= 70: strengths.append("Strong overlap with role-specific language.")
    if skill_score >= 70: strengths.append("Most explicitly requested technical skills are represented.")
    if impact_score >= 60: strengths.append("Experience includes measurable outcomes and achievement signals.")
    if section_score >= 80: strengths.append("Resume contains the major ATS-friendly sections.")
    if not strengths: strengths.append("The resume provides a usable baseline that can be tailored to the role.")

    improvements = []
    if missing_skills: improvements.append("Add relevant missing skills only where you can support them with real experience: " + ", ".join(missing_skills[:8]) + ".")
    if missing_keywords: improvements.append("Mirror important job terminology naturally: " + ", ".join(missing_keywords[:8]) + ".")
    if impact_score < 60: improvements.append("Rewrite experience bullets around actions, scope, metrics, and outcomes.")
    missing_sections = sorted(SECTIONS - sections_found)
    if missing_sections: improvements.append("Add or clearly label ATS-standard sections: " + ", ".join(missing_sections) + ".")

    tips = [
        "Use a single-column layout and conventional section headings for parser reliability.",
        "Place the most relevant role keywords inside achievement bullets rather than a keyword dump.",
        "Keep dates, employers, job titles, and education entries consistently formatted.",
    ]
    summary = f"Deterministic ATS analysis found {len(matched_keywords)}/{len(keywords)} priority keywords and {len(matched_skills)}/{len(job_skills)} requested skills."
    return AnalysisResponse(
        match_score=score, verdict=verdict, summary=summary,
        matched_keywords=matched_keywords, missing_keywords=missing_keywords,
        matched_skills=matched_skills, missing_skills=missing_skills,
        strengths=strengths, improvements=improvements, ats_tips=tips,
        breakdown=ScoreBreakdown(keyword_match=_pct(keyword_score), skill_match=_pct(skill_score), section_quality=_pct(section_score), impact_quality=_pct(impact_score), readability=readability),
        mode="deterministic",
    )
