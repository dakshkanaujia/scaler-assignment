# 🧠 DSA Agent — Autonomous AI Learning Coach

An **autonomous, RAG-powered AI agent** that onboards learners, generates personalized DSA roadmaps, teaches through streaming conversation, and self-evaluates response quality using an LLM-as-judge framework — built with **Next.js**, **FastAPI**, **Gemini 2.5 Flash**, and **ChromaDB**.


---

## 🎯 What It Does

| Feature | Description |
|---------|-------------|
| **Autonomous Onboarding** | 3-question intake → Gemini generates a full learning profile (level, 5-topic roadmap, first task, timeline) with zero human intervention |
| **RAG-Powered Chat** | Every user query triggers top-3 semantic retrieval from a chunked DSA knowledge base, injected as context before generation |
| **Streaming Responses** | Real-time token-by-token output via Server-Sent Events (SSE), with conversation history threading up to 10 turns |
| **LLM-as-Judge Eval** | Every agent response is scored (0.0–1.0) on relevance, accuracy, and helpfulness — logged to `eval.jsonl` for analysis |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Next.js Frontend (Vercel)                              │
│  ┌──────────────┐  ┌────────────────────────────────┐   │
│  │  /onboard     │  │  / (Chat UI)                   │   │
│  │  3-question   │  │  Streaming SSE · Sidebar with  │   │
│  │  intake form  │  │  profile, roadmap, eval scores │   │
│  └──────┬───────┘  └──────────────┬─────────────────┘   │
│         │                         │                      │
└─────────┼─────────────────────────┼──────────────────────┘
          │ POST /onboard           │ POST /chat (SSE)
          │                         │ POST /progress
          ▼                         ▼
┌─────────────────────────────────────────────────────────┐
│  FastAPI Backend (Railway)                              │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │ Onboard     │  │ Chat Agent  │  │ Eval Agent     │  │
│  │ Agent       │  │             │  │ (LLM-as-Judge) │  │
│  │             │  │  ┌────────┐ │  │                │  │
│  │ Structured  │  │  │  RAG   │ │  │ Scores 0–1    │  │
│  │ JSON output │  │  │ Context│ │  │ Logs to JSONL  │  │
│  └─────────────┘  │  └───┬────┘ │  └────────────────┘  │
│                   │      │      │                       │
│                   └──────┼──────┘                       │
│                          │                              │
│                   ┌──────▼──────┐                       │
│                   │  ChromaDB   │                       │
│                   │ (in-memory) │                       │
│                   │ 10 DSA      │                       │
│                   │ topic chunks│                       │
│                   └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
agent-mvp/
├── frontend/                      # Next.js 16 + TypeScript + Tailwind
│   └── src/app/
│       ├── layout.tsx             # Root layout, Inter + JetBrains Mono fonts
│       ├── globals.css            # Dark theme design system, glassmorphism
│       ├── page.tsx               # Chat UI — streaming, sidebar, suggestions
│       └── onboard/page.tsx       # 3-question onboarding form
│
├── backend/                       # FastAPI + Python 3.10
│   ├── main.py                    # App entrypoint — 3 endpoints + CORS
│   ├── agents/
│   │   ├── onboard.py             # Profile generation agent
│   │   ├── chat.py                # Streaming conversational agent + RAG
│   │   └── eval.py                # LLM-as-judge scoring agent
│   ├── rag/
│   │   ├── loader.py              # Chunk & load DSA notes into Chroma
│   │   └── retriever.py           # Top-k semantic retrieval
│   ├── data/
│   │   └── dsa_notes.txt          # 200+ line DSA knowledge base (10 topics)
│   ├── requirements.txt
│   └── .env                       # GEMINI_API_KEY
│
└── README.md
```

---

## 🔌 API Endpoints

### `POST /onboard`
Autonomous profile generation — no human in the loop.

```json
// Request
{ "answers": ["beginner", "SDE-1 at product company", "3 months"] }

// Response
{
  "level": "beginner",
  "roadmap": ["Arrays & Hashing", "Two Pointers", "Stacks", "Binary Trees", "Graphs"],
  "first_task": "Solve 3 easy array problems: Two Sum, Contains Duplicate, Valid Anagram",
  "estimated_weeks": 12,
  "daily_hours": 2,
  "focus_areas": ["Pattern recognition", "Time complexity analysis", "Problem decomposition"]
}
```

### `POST /chat`
Streaming conversational agent with RAG context injection. Returns `text/event-stream`.

```json
// Request
{
  "message": "Explain Dijkstra's algorithm",
  "history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}],
  "profile": { "level": "beginner", "roadmap": [...] }
}
```

**Pipeline per request:**
1. Retrieve top-3 relevant chunks from ChromaDB
2. Inject chunks + learner profile into system prompt
3. Stream Gemini response token-by-token via SSE

### `POST /progress`
LLM-as-judge evaluation — fires after every chat response.

```json
// Request
{ "message": "Explain BFS", "response": "BFS explores level by level..." }

// Response
{
  "quality_score": 0.92,
  "reason": "Accurate explanation with clear examples, well-adapted to beginner level",
  "logged": true
}
```

---

## 🧪 Evaluation Framework

Every agent response is automatically scored by a separate Gemini call acting as an impartial judge:

| Metric | What it measures |
|--------|-----------------|
| **Relevance** (0–1) | Does the response address the user's actual question? |
| **Accuracy** (0–1) | Is the technical/DSA content correct? |
| **Helpfulness** (0–1) | Would a learner at this level find it genuinely useful? |

Results are appended to `backend/eval.jsonl` with timestamps — enabling trend analysis, regression detection, and quality dashboards.

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **LLM** | Gemini 2.5 Flash | Fast, high-quality, generous free tier |
| **Backend** | FastAPI (async) | Native streaming, async-first, production-grade |
| **Vector Store** | ChromaDB (in-memory) | Zero-config, built-in embeddings (all-MiniLM-L6-v2) |
| **Frontend** | Next.js 16 + TypeScript | SSR, App Router, fast iteration |
| **Styling** | Tailwind CSS | Dark theme, glassmorphism, micro-animations |
| **Eval** | LLM-as-Judge | Automated quality assurance without labeled data |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Gemini API key](https://aistudio.google.com/apikey) (free)

### Backend

```bash
cd agent-mvp/backend
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add your API key
echo "GEMINI_API_KEY=your-key-here" > .env

# Run
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd agent-mvp/frontend
npm install
npm run dev
```

Open **http://localhost:3000/onboard** → complete onboarding → start chatting.

---

## ☁️ Deployment

### Backend → Railway (free tier)
```bash
cd backend
railway init && railway up
# Set GEMINI_API_KEY in Railway dashboard → Variables
```

### Frontend → Vercel (free tier)
```bash
cd frontend
vercel --prod
# Set NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app
```

---

## 📊 What This Demonstrates

| Capability | Implementation |
|-----------|---------------|
| **Autonomous agent design** | `/onboard` runs end-to-end with zero human intervention |
| **Conversational AI** | Stateful multi-turn chat with history threading |
| **RAG pipeline** | ChromaDB vector store → semantic retrieval → context injection |
| **Streaming architecture** | FastAPI SSE → frontend EventSource consumer |
| **Production API design** | Async endpoints, CORS, structured error handling |
| **Eval/observability** | LLM-as-judge scoring every response, JSONL logging |
| **Full-stack delivery** | Next.js + FastAPI, deployed to Vercel + Railway |

---

## ✅ Testing & Verification

You can verify each component independently using `curl` against the running backend.

### 1. Health Check
```bash
curl http://localhost:8000/health
```
```json
{"status": "ok"}
```

### 2. Onboarding Agent
```bash
curl -X POST http://localhost:8000/onboard \
  -H "Content-Type: application/json" \
  -d '{"answers": ["beginner", "SDE-1 at product company", "3 months"]}'
```
**Expected:** JSON with `level`, `roadmap` (5 items), `first_task`, `estimated_weeks`, `daily_hours`, `focus_areas`.

### 3. Chat Agent (Streaming)
```bash
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain two pointer technique", "history": [], "profile": {"level": "beginner"}}'
```
**Expected:** `text/event-stream` with `data: {"text": "..."}` chunks arriving in real-time, ending with `data: [DONE]`.

### 4. Eval Agent (LLM-as-Judge)
```bash
curl -X POST http://localhost:8000/progress \
  -H "Content-Type: application/json" \
  -d '{"message": "What is BFS?", "response": "BFS is a graph traversal algorithm that explores all neighbors at the current depth before moving to the next level."}'
```
**Expected:** `{"quality_score": 0.85, "reason": "...", "logged": true}`. Check `backend/eval.jsonl` for the logged entry.

### 5. RAG Retrieval (Indirect)
Ask a specific DSA topic in the chat — the response should reference content from `dsa_notes.txt`:
```bash
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Kadane\"s algorithm?", "history": [], "profile": {"level": "beginner"}}'
```
**Expected:** The response should mention maximum subarray, running sum, and O(n) complexity — content that comes from the RAG knowledge base.

### 6. Frontend Flow
1. Open `http://localhost:3000/onboard`
2. Fill in: level → goal → timeframe
3. Click "Generate My Roadmap →" — should redirect to chat with profile in sidebar
4. Send a message — response streams in real-time
5. Check sidebar for quality score after each response

### What's Working

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI server | ✅ | Starts with Chroma loaded, CORS enabled |
| Onboarding agent | ✅ | Returns structured JSON profile via Gemini |
| Chat agent (streaming) | ✅ | SSE stream with RAG context injection |
| RAG pipeline | ✅ | 10 DSA topics chunked and embedded in Chroma |
| Eval agent | ✅ | Scores responses, logs to `eval.jsonl` |
| Next.js onboarding page | ✅ | Dark theme, form validation, API integration |
| Next.js chat page | ✅ | Streaming consumer, sidebar, suggestion chips |
| Profile persistence | ✅ | Stored in `localStorage`, survives refresh |
| History threading | ✅ | Last 10 turns sent as conversation context |

---

## 📄 License

MIT
