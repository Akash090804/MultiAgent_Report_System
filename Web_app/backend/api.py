# backend/api.py
"""
FastAPI backend for AI Report Generator
Handles report generation requests and serves files
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid
import os
from typing import Optional
from datetime import datetime
import json
from pathlib import Path

app = FastAPI(
    title="AI Report Generator API",
    description="Multi-Agent Academic Report Generation System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (use Redis in production)
jobs = {}

# Set up absolute paths for outputs
project_root = Path(__file__).resolve().parent.parent.parent
outputs_dir = project_root / "Web_app" / "outputs"
outputs_dir.mkdir(parents=True, exist_ok=True)


class ReportRequest(BaseModel):
    """Request model for report generation"""
    api_key: str
    topic: str
    description: Optional[str] = None
    author: Optional[str] = None
    generate_pdf: bool = True


class JobStatus(BaseModel):
    """Response model for job status"""
    job_id: str
    status: str
    progress: int
    current_stage: str
    error: Optional[str] = None
    markdown_url: Optional[str] = None
    pdf_url: Optional[str] = None
    created_at: str


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend HTML"""
    html_path = os.path.join("frontend", "index.html")
    
    if not os.path.exists(html_path):
        return HTMLResponse(
            content="<h1>Frontend not found</h1><p>Please create frontend/index.html</p>",
            status_code=404
        )
    
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/app.js")
async def serve_js():
    """Serve JavaScript file"""
    js_path = os.path.join("frontend", "app.js")
    
    if not os.path.exists(js_path):
        raise HTTPException(status_code=404, detail="app.js not found")
    
    return FileResponse(js_path, media_type="application/javascript")


@app.post("/api/generate")
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """
    Start report generation
    Returns job_id to track progress
    """
    # Validate API key format
    if not request.api_key or len(request.api_key) < 30:
        raise HTTPException(status_code=400, detail="Invalid API key format")
    
    # Validate topic
    if not request.topic or len(request.topic) < 10:
        raise HTTPException(status_code=400, detail="Topic must be at least 10 characters")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())[:8]
    
    # Initialize job status
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "current_stage": "Initializing...",
        "error": None,
        "markdown_url": None,
        "pdf_url": None,
        "created_at": datetime.now().isoformat(),
        "topic": request.topic
    }
    
    # Import generator
    from backend.generator import run_report_generation
    
    # Start generation in background
    background_tasks.add_task(
        run_report_generation,
        job_id,
        request.api_key,
        request.topic,
        request.description,
        request.author,
        request.generate_pdf,
        jobs
    )
    
    return {
        "job_id": job_id,
        "message": "Report generation started",
        "status_url": f"/api/status/{job_id}"
    }


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get current status of report generation"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]


@app.get("/api/download/{job_id}/{file_type}")
async def download_file(job_id: str, file_type: str):
    """
    Download generated report
    file_type: 'pdf' or 'markdown'
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Report not ready yet")
    
    if file_type == "pdf":
        file_path = outputs_dir / f"report_{job_id}.pdf"
        media_type = "application/pdf"
        filename = f"report_{job_id}.pdf"
    elif file_type == "markdown":
        file_path = outputs_dir / f"report_{job_id}.md"
        media_type = "text/markdown"
        filename = f"report_{job_id}.md"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Use 'pdf' or 'markdown'")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    return FileResponse(
        str(file_path),
        media_type=media_type,
        filename=filename
    )


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs (for debugging)"""
    return {
        "total": len(jobs),
        "active": sum(1 for j in jobs.values() if j["status"] == "processing"),
        "completed": sum(1 for j in jobs.values() if j["status"] == "completed"),
        "failed": sum(1 for j in jobs.values() if j["status"] == "failed"),
        "jobs": list(jobs.values())
    }


@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its files"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete files
    pdf_path = f"outputs/report_{job_id}.pdf"
    md_path = f"outputs/report_{job_id}.md"
    
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    if os.path.exists(md_path):
        os.remove(md_path)
    
    # Remove from jobs dict
    del jobs[job_id]
    
    return {"message": "Job deleted successfully"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_jobs": sum(1 for j in jobs.values() if j["status"] == "processing"),
        "total_jobs": len(jobs),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting AI Report Generator Web Server...")
    print("Access at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")