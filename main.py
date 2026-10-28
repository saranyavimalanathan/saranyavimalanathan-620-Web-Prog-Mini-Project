"""FastAPI application for the AI Resume Builder."""
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from services.export import OUTPUT, convert_to_pdf, render_cover_letter_docx, render_resume_docx
from services.local_generator import ats_report as build_ats_report
from services.local_generator import cover_letter as build_cover_letter
from services.local_generator import generate_resume as build_resume
from services.local_generator import improvement_plan as build_improvement_plan

app = FastAPI(title="AI Resume Builder API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
OUTPUT.mkdir(exist_ok=True)
app.mount("/output", StaticFiles(directory=str(OUTPUT)), name="output")

class ResumeRequest(BaseModel):
    """Request body for resume generation."""
    student_profile: str = Field(min_length=10)
    job_description: str = Field(min_length=10)
    target_words: int = Field(default=400, ge=300, le=500)

class ResumeAnalysisRequest(BaseModel):
    """Request body for resume-based analysis calls."""
    resume: dict[str, Any]
    job_description: str = Field(min_length=10)
    recipient_name: str = ""
    recipient_company: str = ""
    recipient_location: str = ""

class GenerateResumeResponse(BaseModel):
    """Response body for resume generation."""
    resume: dict[str, Any]
    docx_url: str
    pdf_url: str | None

class ATSResponse(BaseModel):
    """Response body for ATS results."""
    score: int
    matched_keywords: list[str]
    missing_keywords: list[str]
    strengths: list[str]
    weaknesses: list[str]

class ImprovementResponse(BaseModel):
    """Response body for the improvement plan."""
    missing_skills: list[str]
    certifications: list[str]
    roadmap: list[str]

class CoverLetterResponse(BaseModel):
    """Response body for a generated cover letter."""
    cover_letter: str
    docx_url: str
    pdf_url: str | None

@app.post("/generate-resume", response_model=GenerateResumeResponse)
async def generate_resume(request: ResumeRequest) -> GenerateResumeResponse:
    """Generate a tailored resume and downloadable document versions."""
    resume = build_resume(request.student_profile, request.job_description)
    docx_name = render_resume_docx(resume)
    pdf_name = convert_to_pdf(docx_name)
    return GenerateResumeResponse(resume=resume, docx_url=f"/download/{docx_name}", pdf_url=f"/download/{pdf_name}" if pdf_name else None)

@app.post("/ats-report", response_model=ATSResponse)
async def ats_report(request: ResumeAnalysisRequest) -> ATSResponse:
    """Return ATS match findings for a resume and target job."""
    return ATSResponse(**build_ats_report(request.resume, request.job_description))

@app.post("/improvement-plan", response_model=ImprovementResponse)
async def improvement_plan(request: ResumeAnalysisRequest) -> ImprovementResponse:
    """Return an actionable skills and certification plan."""
    return ImprovementResponse(**build_improvement_plan(request.resume, request.job_description))

@app.post("/cover-letter", response_model=CoverLetterResponse)
async def cover_letter(request: ResumeAnalysisRequest) -> CoverLetterResponse:
    """Return a tailored cover letter."""
    letter = build_cover_letter(
        request.resume,
        request.job_description,
        request.recipient_name,
        request.recipient_company,
        request.recipient_location,
    )
    docx_name = render_cover_letter_docx(letter)
    pdf_name = convert_to_pdf(docx_name)
    return CoverLetterResponse(cover_letter=letter, docx_url=f"/download/{docx_name}", pdf_url=f"/download/{pdf_name}" if pdf_name else None)

@app.get("/download/{filename}")
async def download_file(filename: str) -> FileResponse:
    """Serve a generated output file as an attachment."""
    path = (OUTPUT / filename).resolve()
    if path.parent != OUTPUT.resolve() or not path.is_file(): raise HTTPException(status_code=404, detail="Requested file was not found.")
    return FileResponse(path, filename=path.name, media_type="application/octet-stream")
