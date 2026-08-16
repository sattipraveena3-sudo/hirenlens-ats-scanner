import logging
import os
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from hirelens.parsing import extract_pdf_text
from hirelens.schemas import AnalyzeRequest, AnalysisResponse
from hirelens.service import run_analysis

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("hirelens")
STATIC = Path(__file__).parent / "static"

app = FastAPI(
    title="HireLens ATS Scanner",
    version="2.0.0",
    description="Explainable ATS resume matching with deterministic scoring and optional Groq insights.",
)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0", "groq_configured": bool(os.getenv("GROQ_API_KEY"))}


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze(request: AnalyzeRequest):
    try:
        return run_analysis(request.resume, request.job_description, request.use_ai)
    except Exception as exc:
        logger.exception("analysis failed")
        raise HTTPException(status_code=500, detail="Analysis failed") from exc


@app.post("/api/v1/analyze-file", response_model=AnalysisResponse)
async def analyze_file(
    resume: UploadFile = File(...),
    job_description: str = Form(..., min_length=20),
    use_ai: bool = Form(True),
):
    if resume.content_type not in {"application/pdf", "text/plain"}:
        raise HTTPException(status_code=415, detail="Upload a PDF or plain-text resume")
    data = await resume.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Resume must be 5 MB or smaller")
    try:
        text = extract_pdf_text(data) if resume.content_type == "application/pdf" else data.decode("utf-8")
        if len(text.strip()) < 20:
            raise ValueError("Resume text is too short")
        return run_analysis(text, job_description, use_ai)
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
