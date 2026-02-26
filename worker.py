## worker.py
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from celery import Celery
from crewai import Crew, Process

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import verification, analyze_financial_document, investment_analysis, risk_assessment
from database import SessionLocal, AnalysisJob

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "financial_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(bind=True)
def run_analysis_task(self, job_id: str, query: str, file_path: str):
    """
    Celery task — runs the full CrewAI pipeline for a given job.
    Updates the DB record with status, result, or error.
    """
    db = SessionLocal()
    try:
        # Mark job as running
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            return

        job.status = "running"
        job.updated_at = datetime.utcnow()
        db.commit()

        # Run CrewAI pipeline
        financial_crew = Crew(
            agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
            tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment],
            process=Process.sequential,
        )
        result = financial_crew.kickoff({"query": query, "file_path": file_path})

        # Save result
        job.status = "complete"
        job.result = str(result)
        job.updated_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        # Save error
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error = str(e)
            job.updated_at = datetime.utcnow()
            db.commit()
        raise

    finally:
        # Clean up uploaded file after processing
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        db.close()
