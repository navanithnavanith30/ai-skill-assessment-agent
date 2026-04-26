"""
AI-powered Skill Assessment Agent - FastAPI Backend
===================================================
A robust, official API backend using FastAPI.
Serves a custom HTML/CSS/JS frontend located in the 'static' folder.
"""

import os
import uuid
import logging
from dataclasses import dataclass
from typing import Optional, Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from google import genai
from google.genai import types

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ==============================================================================
# CONFIGURATION & PROMPTS
# ==============================================================================

@dataclass
class AgentConfig:
    # 👉 PASTE YOUR API KEY HERE: Replace the os.environ.get(...) with your actual key like "AIzaSy..."
    api_key: Optional[str] = os.environ.get("GEMINI_API_KEY") or "ADD API KEY HERE"
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.7


SYSTEM_PROMPT = """
You are an AI-powered Skill Assessment and Personalized Learning Agent.

### 1. Resume & JD Parser
Extract required skills from exactly what the user inputs (JD and Resume). 
Identify expected proficiency levels.

### 2. Skill Matching Engine
Compare the extracted skills to output:
- Matched Skills
- Missing Skills
- Partial/Weak Skills

### 3. AI Interview Agent (Core Phase)
- Ask dynamic questions (Start Beginner -> Move to Intermediate -> Move to Advanced).
- RULES: Ask ONE question at a time. Wait for user response. Adapt questioning based on answers.

### 4. Scoring System
Evaluate each answer on:
- Correctness (0–10)
- Depth (0–10)
- Confidence / Practical example (0–10)

Compute: Score = (Correctness + Depth + Confidence) / 3
Levels: 0–40 (Beginner), 40–70 (Intermediate), 70–100 (Advanced).

### 5. Gap Analyzer
Compare the JD required level to the actual assessed level.

### 6. Final Learning Plan Generator
When the assessment concludes, you MUST output the final result exactly like this:

📊 Skill Report
- [Skill Name] -> [Score]% ([Level])

📉 Gaps
- [List Missing or Weak concepts]

📚 Learning Plan
- [Topics to learn] ([Time estimate])
- [Resources]
"""

# ==============================================================================
# CORE BUSINESS LOGIC (Unchanged, wrapped in a class)
# ==============================================================================

class AssessmentAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self._chat_session: Any = None
        self._client: Any = None
        self._generation_config: Any = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        if not self.config.api_key:
            raise ValueError("Missing Gemini API Key.")
        self._client = genai.Client(api_key=self.config.api_key)
        self._generation_config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=self.config.temperature,
        )

    def start_assessment(self, job_description: str, resume: str) -> str:
        self._chat_session = self._client.chats.create(
            model=self.config.model_name,
            config=self._generation_config
        )
        initial_payload = (
            f"Here is the Job Description:\n{job_description}\n\n"
            f"Here is my Resume:\n{resume}\n\n"
            "Please begin mapped evaluation. Ask your very first question."
        )
        return self.send_message(initial_payload)

    def send_message(self, message: str) -> str:
        if not self._chat_session:
            raise RuntimeError("Chat session is not initialized.")
        try:
            response = self._chat_session.send_message(message)
            return response.text
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error communicating with AI: {str(e)}"

# ==============================================================================
# FASTAPI APPLICATION ARCHITECTURE
# ==============================================================================

app = FastAPI(title="Skill Assessment AI Core")

# In-Memory Session Store (for Hackathon simplicity)
# Maps a unique session_id to an AssessmentAgent instance
sessions: Dict[str, AssessmentAgent] = {}
base_config = AgentConfig()

# Request Models
class StartRequest(BaseModel):
    job_description: str
    resume: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

# API ENDPOINTS
@app.post("/api/start")
def start_session(req: StartRequest):
    """Initializes the AI and returns the first question."""
    session_id = str(uuid.uuid4())
    
    # Initialize a fresh agent for this session
    agent = AssessmentAgent(base_config)
    sessions[session_id] = agent
    
    # Start assessment
    first_question = agent.start_assessment(req.job_description, req.resume)
    
    return {"session_id": session_id, "reply": first_question}

@app.post("/api/chat")
def chat(req: ChatRequest):
    """Sends a user message to the AI and gets the next question."""
    agent = sessions.get(req.session_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Session not found. Please restart.")
    
    reply = agent.send_message(req.message)
    return {"reply": reply}

# Mount static files to serve the frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_frontend():
    """Serves the main HTML application."""
    html_path = os.path.join(static_dir, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"error": "Frontend files not built yet! Expected at /static/index.html"}

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time

    def open_browser():
        # Wait a moment for the server to spin up, then open the browser
        time.sleep(1.5)
        webbrowser.open("http://localhost:8000")

    # Start the browser thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start the FastAPI server directly from Python
    uvicorn.run(app, host="127.0.0.1", port=8000)
