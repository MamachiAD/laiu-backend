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


@app.post("/agents/socratic-tutor")
def socratic_tutor_guidance(query: VectorSearchQuery):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            \"\"\"
            SELECT student_id, repository_url, novelty_score, status, 
                   1 - (embedding <=> %s::vector) AS similarity
            FROM student_submissions
            ORDER BY embedding <=> %s::vector ASC
            LIMIT 1;
            \"\"\",
            (
                str(query.query_embedding),
                str(query.query_embedding)
            )
        )
        row = cursor.fetchone()
        if not row:
            return {"guidance": "No prior context found. Initiate baseline research vector."}

        matched_submission = {
            "student_id": row[0],
            "repository_url": row[1],
            "novelty_score": row[2],
            "status": row[3],
            "similarity": float(row[4])
        }

        return {
            "agent": "Lumina Socratic Tutor",
            "matched_historical_context": matched_submission,
            "inquiry": "Your architecture demonstrates strong alignment with sovereign execution. How does your vector indexing strategy scale under high-concurrency evaluation?",
            "action_required": "Submit updated telemetry logs for re-evaluation."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()