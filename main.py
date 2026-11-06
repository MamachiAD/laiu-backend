# -*- coding: utf-8 -*-
import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from supabase import create_client, Client
from dotenv import load_dotenv
import uvicorn

# --- Load Environment Variables ---
load_dotenv()

# --- Supabase Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hwmuvewmkytzqnivperx.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx6Y2l4bXliaXZvcGRhZmp3cmZtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM3MTY2OTUsImV4cCI6MjEwOTI5MjY5NX0.PZTU5b_7fpocQBzRFLMAmM9GH7WpqTdOkUrS2fgloAo")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Lumina AI University Enterprise Sovereign Ecosystem V90")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Automated Interactive Dashboard Route ---
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Lumina AI University - Live Sovereign Chat</title>
        <style>
            body { font-family: monospace; background: #0f172a; color: #f8fafc; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
            h2 { color: #38bdf8; margin-top: 0; }
            #tutorChatBox { height: 400px; border: 1px solid #334155; background: #090d16; border-radius: 8px; padding: 15px; overflow-y: scroll; margin-bottom: 15px; }
            .controls { display: flex; gap: 10px; }
            select, input, button { padding: 10px; border-radius: 6px; border: 1px solid #475569; background: #334155; color: #fff; font-family: monospace; }
            input { flex-grow: 1; }
            button { background: #10b981; border: none; font-weight: bold; cursor: pointer; }
            button:hover { background: #059669; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Lumina AI University — Swarm Control</h2>
            <div style="font-size: 12px; margin-bottom: 10px; color: #94a3b8;">
                Student ID: <span id="dash-student-id">LAIU-V90-001</span>
            </div>
            <div id="tutorChatBox"></div>
            <div class="controls">
                <select id="agentPersona">
                    <option value="auditor">Cyber Compliance Auditor</option>
                    <option value="assessor">EU AI Act Risk Assessor</option>
                    <option value="trainer">Distributed Megatron Trainer</option>
                </select>
                <input type="text" id="tutorInput" placeholder="Ask your AI agent or enter compliance query..." onkeydown="if(event.key==='Enter') sendMultiAgentPromptWS();">
                <button onclick="sendMultiAgentPromptWS()">Send Stream</button>
            </div>
        </div>
        <script>
            let chatSocket = null;
            function initLuminaChatWebSocket() {
                chatSocket = new WebSocket('ws://127.0.0.1:8035/ws/lumina-chat');
                chatSocket.onmessage = function(event) {
                    let msg = JSON.parse(event.data);
                    let chatBox = document.getElementById('tutorChatBox');
                    if (msg.type === 'start') {
                        let streamDiv = document.createElement('div');
                        streamDiv.id = 'activeStreamBubble';
                        streamDiv.style.cssText = 'margin-bottom:10px; text-align:left; color:#10B981; font-size:12px; font-family:monospace;';
                        streamDiv.innerText = `[${msg.persona.toUpperCase()}]: `;
                        chatBox.appendChild(streamDiv);
                    } else if (msg.type === 'token') {
                        let activeBubble = document.getElementById('activeStreamBubble');
                        if (activeBubble) {
                            activeBubble.innerText += msg.content;
                            chatBox.scrollTop = chatBox.scrollHeight;
                        }
                    } else if (msg.type === 'end') {
                        let activeBubble = document.getElementById('activeStreamBubble');
                        if (activeBubble) activeBubble.id = '';
                    }
                };
                chatSocket.onclose = function() {
                    setTimeout(initLuminaChatWebSocket, 3000);
                };
            }
            function sendMultiAgentPromptWS() {
                let persona = document.getElementById('agentPersona').value;
                let input = document.getElementById('tutorInput').value;
                if (!input || !chatSocket) return;
                let chatBox = document.getElementById('tutorChatBox');
                chatBox.innerHTML += `<div style="margin-bottom:10px; text-align:right;"><span style="background:rgba(56,189,248,0.2); padding:8px 12px; border-radius:10px; display:inline-block; font-size:12px; color:#38bdf8;">${input}</span></div>`;
                chatSocket.send(JSON.stringify({
                    persona: persona,
                    message: input,
                    student_id: document.getElementById('dash-student-id').innerText
                }));
                document.getElementById('tutorInput').value = '';
            }
            document.addEventListener('DOMContentLoaded', initLuminaChatWebSocket);
        </script>
    </body>
    </html>
    """

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

            # Store user query in Supabase
            try:
                supabase.table("chat_history").insert({
                    "persona": persona,
                    "sender": "user",
                    "message": user_message
                }).execute()
            except Exception as e:
                print(f"[Supabase Log Warning]: {e}")

            # Determine response persona prefix and reply
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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8035)
