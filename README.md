# 🧠 AI Skill Assessment & Learning Path Generator

An intelligent, full-stack application designed to evaluate a candidate's true proficiency by comparing their Resume against a target Job Description. It conducts a dynamic, interview-style assessment and generates a personalized learning roadmap to bridge any skill gaps.

---

## 🏗️ Architecture

- **Frontend**: Custom Glassmorphic Web UI (Vanilla JS + Custom CSS) mimicking a premium ChatGPT-style interface.
- **Backend**: Python `FastAPI` providing high-performance asynchronous endpoints.
- **AI Core**: Google Gemini (`google-genai`), utilized strictly for intelligent parsing and dynamic adaptive questioning.

---

## 🔹 Core Modules

### 1. Resume + JD Parser
Securely ingests the textual Job Description and the Candidate's Resume. The AI extracts claimed skills, toolsets, and infers raw experience level.

### 2. Skill Matching Engine
Performs an automatic gap analysis right out of the gate:
- **Matched** (Skills in both JD & Resume)
- **Missing** (Required by JD, absent in Resume)
- **Partial** (Claimed basic knowledge, but JD requires advanced)

### 3. AI Interview Agent (🔥 Core Function)
The system acts as an expert interviewer:
- Sequences questions progressively: **Beginner → Intermediate → Advanced**.
- Operates on an *Adaptive Questioning Algorithm*: if a user struggles on a concept, it simplifies; if they excel, it drills deeper.
- *Strict Rule: Only ever asks one question at a time to maintain conversational parity.*

### 4. 🧩 Rigid Scoring System
Calculated implicitly during the interview loop. Each response is graded on three vectors:
- **Correctness** (0–10)
- **Depth of Knowledge** (0–10)
- **Confidence & Practical Example** (0–10)

`Final Skill Score = Average of all vectors`

**Ranking Classifications:**
- **0–40** → Beginner
- **40–70** → Intermediate
- **70–100** → Advanced

### 5. Gap Analyzer
After concluding the questionnaire across all matching topics, the AI explicitly measures the required job level against the candidate's actual output level.

### 6. Learning Plan Generator
Spits out an ultra-realistic, highly structured personalized learning roadmap targeting weak proficiency areas.

**Example Output:**
```text
📊 Skill Report
Python → 45% (Intermediate)
SQL → 70% (Advanced)
ML → Missing

📉 Gaps
No Machine Learning
Weak Python concepts

📚 Learning Plan
Python advanced concepts (5 days)
ML basics (2 weeks)
```

---

## ⚙️ Running Locally

1. Install requirements:
`pip install fastapi uvicorn google-genai`

2. Set your Gemini API Configuration in `Hackathon.py`.

3. Start the application:
`python Hackathon.py`

This will automatically boot the server and open your default web browser to the premium assessment dashboard!
