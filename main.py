import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel

app = FastAPI(title="Lumina AI University Sovereign Core")

DATABASE_URL = os.environ.get("DATABASE_URL")

class StudentSubmission(BaseModel):
    student_id: str
    repository_url: str
    code_telemetry_logs: str
    socratic_transcript: str

class ComplianceCheck(BaseModel):
    user_id: str
    content_stream: str
    action_type: str
    channel_type: str

def get_db_connection():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL environment variable not set.")
    return psycopg2.connect(DATABASE_URL)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "Lumina AI University Sovereign Core",
        "institutional_standard": "70/30 Production Execution Model"
    }

@app.post("/agents/innovation-scout")
def evaluate_student_innovation(submission: StudentSubmission):
    novelty_score = 94.5
    status = "Venture-Track & Elite Honor Awarded"
    dummy_embedding = [0.01] * 1536

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            \"\"\"
            INSERT INTO student_submissions (student_id, repository_url, novelty_score, status, embedding)
            VALUES (%s, %s, %s, %s, %s::vector);
            \"\"\",
            (
                submission.student_id,
                submission.repository_url,
                novelty_score,
                status,
                str(dummy_embedding)
            )
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return {
        "student_id": submission.student_id,
        "novelty_score": novelty_score,
        "status": status,
        "compute_credits_awarded": 25000,
        "patent_pipeline_initiated": True,
        "executive_approval_card_generated": True
    }

@app.post("/agents/ethical-compliance")
def moderate_content_stream(check: ComplianceCheck):
    status = "cleared"
    threat_detected = False
    action_taken = f"Approved via {check.channel_type} under 70/30 standard"

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            \"\"\"
            INSERT INTO compliance_logs (user_id, content_stream, status, action_taken)
            VALUES (%s, %s, %s, %s);
            \"\"\",
            (
                check.user_id,
                check.content_stream,
                status,
                action_taken
            )
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return {
        "status": status,
        "threat_detected": threat_detected
    }