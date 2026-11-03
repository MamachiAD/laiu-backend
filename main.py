import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel

app = FastAPI(title="Lumina AI University Sovereign Core")

DATABASE_URL = os.environ.get("DATABASE_URL")

class SubmissionCreate(BaseModel):
    student_id: str
    repository_url: str
    novelty_score: float
    status: str
    embedding: List[float]

class VectorSearchQuery(BaseModel):
    query_embedding: List[float]
    match_threshold: Optional[float] = 0.7
    match_count: Optional[int] = 5

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

@app.post("/api/v1/submissions")
def create_submission(submission: SubmissionCreate):
    if len(submission.embedding) != 1536:
        raise HTTPException(
            status_code=400,
            detail="Embedding vector must have exactly 1536 dimensions."
        )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            \"\"\"
            INSERT INTO student_submissions (student_id, repository_url, novelty_score, status, embedding)
            VALUES (%s, %s, %s, %s, %s::vector)
            RETURNING id, created_at;
            \"\"\",
            (
                submission.student_id,
                submission.repository_url,
                submission.novelty_score,
                submission.status,
                str(submission.embedding)
            )
        )
        row = cursor.fetchone()
        conn.commit()
        return {
            "status": "success",
            "submission_id": row[0],
            "created_at": row[1]
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/v1/submissions/search")
def search_submissions(query: VectorSearchQuery):
    if len(query.query_embedding) != 1536:
        raise HTTPException(
            status_code=400,
            detail="Query embedding vector must have exactly 1536 dimensions."
        )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            \"\"\"
            SELECT id, student_id, repository_url, novelty_score, status, 
                   1 - (embedding <=> %s::vector) AS similarity
            FROM student_submissions
            ORDER BY embedding <=> %s::vector ASC
            LIMIT %s;
            \"\"\",
            (
                str(query.query_embedding),
                str(query.query_embedding),
                query.match_count
            )
        )
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "student_id": row[1],
                "repository_url": row[2],
                "novelty_score": row[3],
                "status": row[4],
                "similarity_score": float(row[5])
            })
        return {"matches": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()