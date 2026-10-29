"""
ATS Resume Optimizer - Backend API
Main FastAPI application entry point
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from pdf_processor import extract_text_from_pdf
from resume_parser import parse_resume
from ats_scorer import calculate_ats_score
from ai_optimizer import optimize_resume
from pdf_generator import generate_ats_friendly_pdf

# Create temp directory for processing
TEMP_DIR = Path(tempfile.gettempdir()) / "ats_resume_optimizer"
TEMP_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="ATS Resume Optimizer API",
    description="AI-powered resume optimization for ATS systems",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OptimizeRequest(BaseModel):
    """Request model for resume optimization"""
    job_description: str
    resume_text: str
    auto_iterate: bool = True
    target_score: float = 85.0
    max_iterations: int = 5


class OptimizationResult(BaseModel):
    """Result model for optimization"""
    original_score: float
    optimized_score: float
    optimized_resume: str
    improvements: List[str]
    iterations: int
    pdf_path: Optional[str] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ATS Resume Optimizer",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "ok",
        "temp_dir": str(TEMP_DIR),
        "temp_dir_exists": TEMP_DIR.exists()
    }


@app.post("/api/extract-text")
async def extract_text(
    file: UploadFile = File(None),
    text: str = Form("")
):
    """
    Extract text from uploaded PDF or use provided text
    """
    try:
        resume_text = ""

        if file and file.filename:
            # Check if it's a PDF
            if file.filename.lower().endswith('.pdf'):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    content = await file.read()
                    tmp.write(content)
                    tmp_path = tmp.name

                try:
                    resume_text = extract_text_from_pdf(tmp_path)
                finally:
                    os.unlink(tmp_path)
            else:
                # For non-PDF files, try to read as text
                content = await file.read()
                resume_text = content.decode('utf-8', errors='ignore')
        elif text:
            resume_text = text
        else:
            raise HTTPException(
                status_code=400,
                detail="Either provide a file or text content"
            )

        # Parse the resume to get structured data
        parsed = parse_resume(resume_text)

        return {
            "success": True,
            "text": resume_text,
            "parsed": parsed
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/score")
async def score_resume(
    job_description: str = Form(...),
    file: UploadFile = File(None),
    text: str = Form("")
):
    """
    Calculate ATS score for a resume against job description
    """
    try:
        # Get resume text
        resume_text = text

        if file and file.filename:
            if file.filename.lower().endswith('.pdf'):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    content = await file.read()
                    tmp.write(content)
                    tmp_path = tmp.name

                try:
                    resume_text = extract_text_from_pdf(tmp_path)
                finally:
                    os.unlink(tmp_path)
            else:
                content = await file.read()
                resume_text = content.decode('utf-8', errors='ignore')

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Please provide resume text or upload a PDF"
            )

        # Calculate ATS score
        score_data = calculate_ats_score(resume_text, job_description)

        return {
            "success": True,
            "score": score_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize", response_model=OptimizationResult)
async def optimize_resume_endpoint(
    job_description: str = Form(...),
    file: UploadFile = File(None),
    text: str = Form(""),
    auto_iterate: bool = Form(True),
    target_score: float = Form(85.0),
    max_iterations: int = Form(5)
):
    """
    Optimize resume for ATS - main endpoint
    """
    try:
        # Get resume text
        resume_text = text

        if file and file.filename:
            if file.filename.lower().endswith('.pdf'):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    content = await file.read()
                    tmp.write(content)
                    tmp_path = tmp.name

                try:
                    resume_text = extract_text_from_pdf(tmp_path)
                finally:
                    os.unlink(tmp_path)
            else:
                content = await file.read()
                resume_text = content.decode('utf-8', errors='ignore')

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Please provide resume text or upload a PDF"
            )

        # Calculate initial score
        initial_score = calculate_ats_score(resume_text, job_description)

        # Optimize resume using AI
        result = optimize_resume(
            resume_text=resume_text,
            job_description=job_description,
            auto_iterate=auto_iterate,
            target_score=target_score,
            max_iterations=max_iterations
        )

        # Calculate final score
        final_score = calculate_ats_score(result["optimized_resume"], job_description)

        # Generate PDF
        pdf_path = generate_ats_friendly_pdf(
            result["optimized_resume"],
            str(TEMP_DIR / "optimized_resume.pdf")
        )

        return OptimizationResult(
            original_score=initial_score["total_score"],
            optimized_score=final_score["total_score"],
            optimized_resume=result["optimized_resume"],
            improvements=result["improvements"],
            iterations=result["iterations"],
            pdf_path=pdf_path
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize/feedback")
async def optimize_with_feedback(
    job_description: str = Form(...),
    resume_text: str = Form(...),
    feedback: str = Form(...),
    current_version: int = Form(1)
):
    """
    Refine resume based on user feedback
    """
    try:
        # Parse current resume
        parsed = parse_resume(resume_text)

        # Generate improved version based on feedback
        improved = optimize_resume(
            resume_text=resume_text,
            job_description=job_description,
            user_feedback=feedback,
            version_number=current_version + 1
        )

        # Calculate new score
        new_score = calculate_ats_score(
            improved["optimized_resume"],
            job_description
        )

        return {
            "success": True,
            "optimized_resume": improved["optimized_resume"],
            "improvements": improved["improvements"],
            "new_score": new_score["total_score"],
            "score_breakdown": new_score
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{filename}")
async def download_pdf(filename: str):
    """
    Download generated PDF
    """
    file_path = TEMP_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/pdf"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)