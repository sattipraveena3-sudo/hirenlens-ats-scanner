from hirelens.scoring import analyze_resume

RESUME = '''
Summary
Data engineer building Python and SQL services.
Skills
Python, SQL, Docker, AWS, FastAPI
Experience
- Built ETL pipelines in Python and SQL, reducing processing time by 35%.
Projects
- Deployed FastAPI services with Docker on AWS.
Education
B.Tech Computer Science
'''
JOB = '''We need a data engineer with Python, SQL, Docker, AWS, FastAPI, ETL and Kubernetes experience. The role builds scalable data pipelines and REST API services.'''


def test_analysis_is_explainable():
    result = analyze_resume(RESUME, JOB)
    assert 0 <= result.match_score <= 100
    assert "python" in result.matched_skills
    assert "kubernetes" in result.missing_skills
    assert result.breakdown.skill_match > 0
    assert result.mode == "deterministic"


def test_missing_sections_reduce_quality():
    full = analyze_resume(RESUME, JOB)
    thin = analyze_resume("Python SQL Docker AWS developer with measurable 20% improvement.", JOB)
    assert full.breakdown.section_quality > thin.breakdown.section_quality
