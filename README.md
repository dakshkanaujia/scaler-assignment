# 🤖 Daksh Kanaujia — AI Persona Agent

An AI representative that can be called, chatted with, and used to book interviews. Built for the Scaler Screening Assignment.

**Live Links:**
- 🎙️ **Voice Agent:** Call via Twilio number (connected to Vapi)
- 💬 **Chat Interface:** [Streamlit App](https://scaler-assignment-htbrf274vyrmnydkgbmz4q.streamlit.app)
- 🔌 **API:** [https://scaler-assignment-36qz.onrender.com](https://scaler-assignment-36qz.onrender.com)

---

## Architecture

```
Caller
  │
  ▼
Twilio (Phone Number)
  │  Voice call
  ▼
Vapi.ai (Voice Agent)
  │  POST /chat/completions (OpenAI-compatible, streaming)
  ▼
FastAPI (Render)
  │  ┌─────────────────────────────────┐
  │  │  1. Extract user message        │
  │  │  2. Retrieve RAG context        │──► ChromaDB (local)
  │  │  3. Call Gemini 2.5 Flash       │──► Google AI Studio
  │  │  4. Handle function calls       │──► Cal.com API
  │  │  5. Stream response back        │
  │  └─────────────────────────────────┘
  │  SSE stream
  ▼
Vapi.ai (TTS via Deepgram/ElevenLabs)
  │
  ▼
Caller hears response

─────────────────────────────────────────

Browser
  │
  ▼
Streamlit Chat UI (Streamlit Cloud)
  │  Direct Python import
  ▼
gemini_agent.chat()
  │
  ├──► ChromaDB (RAG retrieval)
  ├──► Gemini 2.5 Flash (LLM)
  └──► Cal.com API (calendar tools)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Voice platform | Vapi.ai |
| Telephony | Twilio |
| Transcription | Deepgram (flux-general-en) |
| TTS | Vapi (Elliot voice) |
| LLM | Gemini 2.5 Flash |
| Vector store | ChromaDB (local, persisted) |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Backend API | FastAPI + Uvicorn |
| Chat UI | Streamlit |
| API hosting | Render (free tier) |
| UI hosting | Streamlit Community Cloud |
| Calendar | Cal.com API |

---

## Project Structure

```
scaler-assignment/
├── agent/
│   ├── gemini_agent.py      # Core LLM + RAG + function calling logic
│   ├── calendar_tools.py    # Cal.com check_availability + book_slot
│   ├── retriever.py         # ChromaDB retriever loader
│   └── ingest.py            # RAG ingestion pipeline
├── api/
│   └── main.py              # FastAPI server (unified /chat + /chat/completions)
├── chat_ui/
│   └── app.py               # Streamlit chat interface
├── data/
│   ├── Daksh_Kanaujia_Resume.pdf
│   ├── README.md            # DSA Agent
│   ├── README (1).md        # CI/CD Pipeline
│   ├── README (2).md        # NLP News Pipeline
│   ├── README (3).md        # EduCast
│   └── README (4).md        # Vector-Graph-DB
├── chroma_db/               # Persisted vector store (auto-generated)
├── .env.example             # Environment variable template
├── requirements.txt
├── Procfile                 # Render deployment config
├── render.yaml
└── README.md
```

---

## Setup

### Prerequisites
- Python 3.10+
- Git

### 1. Clone and install

```bash
git clone https://github.com/dakshkanaujia/scaler-assignment.git
cd scaler-assignment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your keys:

| Variable | Description | Where to get it |
|----------|-------------|-----------------|
| `GEMINI_API_KEY` | Google Gemini API key | [aistudio.google.com](https://aistudio.google.com) |
| `CALCOM_API_KEY` | Cal.com API key | Cal.com dashboard → Settings → API keys |
| `CALCOM_EVENT_TYPE_ID` | Numeric ID of your interview event | Cal.com dashboard → Event Types |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | [console.twilio.com](https://console.twilio.com) |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | Twilio console |
| `TWILIO_PHONE_NUMBER` | Your Twilio phone number | Twilio console → Phone Numbers |
| `VAPI_API_KEY` | Vapi private API key | Vapi dashboard → API Keys |
| `OWNER_NAME` | Your name | e.g. `Daksh` |

### 3. Add your data

Drop your resume and project READMEs into `/data/`:
```
data/
├── your_resume.pdf         # or .txt
├── README.md               # project 1
├── README (1).md           # project 2
└── ...
```

### 4. Run ingestion

```bash
python agent/ingest.py
```

This embeds your resume + READMEs into ChromaDB. Run once; re-run if you update data.

### 5. Start the API server

```bash
uvicorn api.main:app --reload --port 8000
```

### 6. Start the chat UI

```bash
streamlit run chat_ui/app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Deployment

### FastAPI → Render

1. Push repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service → connect repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables in Render dashboard → Environment
6. Deploy

### Streamlit UI → Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub repo
3. Set main file path: `chat_ui/app.py`
4. Add environment variables in Advanced Settings
5. Deploy

### Vapi Voice Agent Setup

1. Go to [dashboard.vapi.ai](https://dashboard.vapi.ai) → Assistants → Create
2. Provider: `Custom LLM`
3. Custom LLM URL: `https://your-render-url.onrender.com` (no trailing slash)
4. First Message: `Hello, I'm Daksh's AI representative. How can I help you?`
5. Voice: Elliot (Vapi) or any ElevenLabs voice
6. Transcriber: Deepgram
7. Set timeout via API:
```bash
curl -X PATCH https://api.vapi.ai/assistant/YOUR_ASSISTANT_ID \
  -H "Authorization: Bearer YOUR_VAPI_PRIVATE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": {"provider": "custom-llm", "url": "https://your-render-url.onrender.com", "model": "gpt-4.1", "maxTokens": 1000, "timeoutSeconds": 30}}'
```
8. In Twilio: buy a phone number → connect to Vapi

---

## API Reference

### `GET /health`
Returns server status.
```json
{"status": "ok"}
```

### `GET /ping`
Keepalive endpoint (used by cron-job.org to prevent Render spin-down).
```json
{"status": "pong"}
```

### `POST /chat`
Streamlit UI format.
```json
// Request
{"message": "Tell me about your projects", "history": []}

// Response
{"response": "I've built 5 key projects..."}
```

### `POST /chat/completions`
OpenAI-compatible format (used by Vapi). Supports streaming (`"stream": true`).
```json
// Request
{
  "model": "gpt-4.1",
  "messages": [{"role": "user", "content": "Tell me about yourself"}],
  "stream": false
}

// Response
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "model": "gpt-4.1",
  "choices": [{"index": 0, "message": {"role": "assistant", "content": "..."}, "finish_reason": "stop"}]
}
```

---

## How RAG Works

1. On startup, `ingest.py` reads all files from `/data/`
2. Text is split into 512-token chunks with 64-token overlap
3. Chunks are embedded using `all-MiniLM-L6-v2` (HuggingFace, runs locally)
4. Embeddings are stored in ChromaDB at `./chroma_db/`
5. On each user query, top-4 most relevant chunks are retrieved
6. Chunks are injected into the Gemini system prompt as context
7. Gemini answers strictly from this context — no hallucination

---

## Calendar Booking Flow

1. User asks about availability (voice or chat)
2. Gemini triggers `check_availability()` function call
3. API fetches open slots from Cal.com for next 7 days
4. Gemini presents slots to user
5. User confirms a time + provides email
6. Gemini triggers `book_slot(email, iso_time)`
7. Cal.com creates the booking and sends confirmation email
8. Meeting appears in real Google Calendar

---

## Key Projects in Knowledge Base

| Project | Stack | Description |
|---------|-------|-------------|
| DSA Agent | Next.js, FastAPI, Gemini, ChromaDB | RAG-powered AI learning coach with LLM-as-judge evals |
| CI/CD Pipeline | Node.js, GitHub Actions, Docker, Trivy | 8-stage DevSecOps pipeline with SAST, SCA, container scanning |
| EduCast | Go (Gin), React Native, WebSockets, MySQL | Demand-driven academic marketplace with real-time bidding |
| NLP News Pipeline | Python, NLTK, Word2Vec, LDA | Complete NLP workflow on 2,692 news articles |
| Vector-Graph-DB | FastAPI, Neo4j, FAISS, React | Hybrid retrieval combining vector search + graph traversal + BM25 |

---

## Keep Render Awake

Render free tier spins down after inactivity. Set up a cron job to ping every 5 minutes:

1. Go to [cron-job.org](https://cron-job.org) → Create Cronjob
2. URL: `https://your-render-url.onrender.com/ping`
3. Schedule: every 5 minutes

---

## Evaluation Report

See `eval_report.pdf` in the repo root. Covers:
- Voice latency measurement (target < 2s first response)
- Chat hallucination rate over 20 test questions
- 3 failure modes found and fixed
- Improvements for 2 more weeks

---

## License

MIT
