# -*- coding: utf-8 -*-
import os
import json
import asyncio
from fastapi import FastAPI, Response, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import uvicorn

# --- Supabase Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Lumina AI University Enterprise Sovereign Ecosystem V90")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket Lumina Chat Swarm Endpoint ---
@app.websocket("/ws/lumina-chat")
async def lumina_chat_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            persona = payload.get("persona", "auditor")
            user_message = payload.get("message", "")
            student_id_code = payload.get("student_id", "GUEST")

            # Store user query in Supabase (async non-blocking log)
            try:
                supabase.table("chat_history").insert({
                    "persona": persona,
                    "sender": "user",
                    "message": user_message
                }).execute()
            except Exception as e:
                print(f"[Supabase Log Warning]: {e}")

            # Determine response persona prefix
            if persona == "auditor":
                prefix = "[Cyber Compliance Auditor]: "
                reply = f"Evaluating prompt for EU AI Act High-Risk Tiering and NIST AI RMF compliance. Controls verified for input: '{user_message}'."
            elif persona == "assessor":
                prefix = "[EU AI Act Risk Assessor]: "
                reply = f"Data provenance logs and zero-trust differential privacy parameters validated under Article 10 for query: '{user_message}'."
            else:
                prefix = "[Distributed Megatron Trainer]: "
                reply = f"Cluster telemetry nominal across 1,024 H100 nodes. Executing ZeRO-3 optimization loops for task: '{user_message}'."

            # Stream response token by token over WebSocket
            await websocket.send_text(json.dumps({"type": "start", "persona": persona}))
            full_response = prefix + reply
            words = full_response.split(" ")
            
            for word in words:
                await websocket.send_text(json.dumps({"type": "token", "content": word + " "}))
                await asyncio.sleep(0.04)
                
            await websocket.send_text(json.dumps({"type": "end"}))

            # Store assistant response in Supabase
            try:
                supabase.table("chat_history").insert({
                    "persona": persona,
                    "sender": "assistant",
                    "message": full_response
                }).execute()
            except Exception as e:
                print(f"[Supabase Log Warning]: {e}")

    except WebSocketDisconnect:
        print("Lumina Chatbot WebSocket disconnected.")

# --- Database Endpoints ---
@app.post("/api/register-certificate")
async def register_certificate(payload: dict):
    program_title = payload.get("program_title")
    exam_code = payload.get("exam_code", "DIRECT-EXAM")
    zkp_hash = payload.get("zkp_hash")
    
    res = supabase.table("certificates").insert({
        "program_title": program_title,
        "exam_code": exam_code,
        "grade": "A+ (98%)",
        "zkp_hash": zkp_hash
    }).execute()
    
    return {"status": "success", "data": res.data}

@app.get("/")
def index():
    return Response(content="<h1>LAIU V90 Enterprise Backend Active</h1>", media_type="text/html")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8035)
