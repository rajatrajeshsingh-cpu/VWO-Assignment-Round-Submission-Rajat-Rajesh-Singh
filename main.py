## main.py
import os
import uuid
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session

from database import init_db, get_db, AnalysisJob
from worker import run_analysis_task

app = FastAPI(title="Financial Document Analyzer")


@app.on_event("startup")
def startup_event():
    """Initialize the SQLite database on startup."""
    init_db()


# ─── Health Check ────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Financial Document Analyzer API is running"}


# ─── Submit Analysis Job ──────────────────────────────────────────────────────

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db),
):
    """
    Upload a financial PDF and queue it for analysis.
    Returns a job_id — use GET /status/{job_id} to poll for results.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if not query or not query.strip():
        query = "Analyze this financial document for investment insights"

    # Save uploaded file
    job_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{job_id}.pdf"
    os.makedirs("data", exist_ok=True)

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create DB record
    job = AnalysisJob(
        id=job_id,
        query=query.strip(),
        filename=file.filename,
        status="pending",
    )
    db.add(job)
    db.commit()

    # Enqueue Celery task
    run_analysis_task.delay(job_id, query.strip(), file_path)

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Analysis queued. Poll /status/{job_id} for results.",
    }


# ─── Poll Job Status ──────────────────────────────────────────────────────────

@app.get("/status/{job_id}")
async def get_status(job_id: str, db: Session = Depends(get_db)):
    """
    Poll the status of a queued analysis job.
    Status values: pending | running | complete | failed
    """
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    response = {
        "job_id": job.id,
        "status": job.status,
        "query": job.query,
        "filename": job.filename,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }

    if job.status == "complete":
        response["analysis"] = job.result

    if job.status == "failed":
        response["error"] = job.error

    return response


# ─── List All Jobs ────────────────────────────────────────────────────────────

@app.get("/jobs")
async def list_jobs(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Return a paginated list of all analysis jobs with their status.
    """
    jobs = (
        db.query(AnalysisJob)
        .order_by(AnalysisJob.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    total = db.query(AnalysisJob).count()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "jobs": [
            {
                "job_id": j.id,
                "status": j.status,
                "query": j.query,
                "filename": j.filename,
                "created_at": j.created_at,
                "updated_at": j.updated_at,
            }
            for j in jobs
        ],
    }


# ─── Delete a Job ─────────────────────────────────────────────────────────────

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db)):
    """
    Delete a job record from the database.
    """
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    db.delete(job)
    db.commit()
    return {"message": f"Job {job_id} deleted."}


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
