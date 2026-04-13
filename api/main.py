import os
import uuid
import time
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agent.gemini_agent import chat
from agent.ingest import ingest_data

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Persona API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Streamlit UI format ---
class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str

@app.on_event("startup")
async def startup_event():
    chroma_db_dir = "./chroma_db/"
    if not os.path.exists(chroma_db_dir):
        print("ChromaDB not found. Running ingestion...")
        try:
            ingest_data()
        except Exception as e:
            print(f"Warning: Ingestion failed, RAG context will be unavailable: {e}")
    else:
        print("ChromaDB found. Skipping ingestion.")

@app.get("/health")
async def health():
    return {"status": "ok"}

# --- Vapi-compatible OpenAI format endpoint ---
@app.post("/chat/completions")
async def vapi_chat_completions(request: Request):
    """
    Vapi Custom LLM endpoint — accepts OpenAI-compatible request,
    returns OpenAI-compatible response.
    """
    try:
        body = await request.json()
        logger.info(f"Vapi request received: model={body.get('model')}")

        messages = body.get("messages", [])

        # Extract the last user message
        user_message = ""
        history = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                continue  # We use our own system prompt
            if role in ("user", "assistant"):
                history.append({"role": role, "content": content or ""})

        # The last user message is what we respond to
        if history and history[-1]["role"] == "user":
            user_message = history.pop()["content"]
        else:
            user_message = "Hello"

        response_text = await chat(user_message, history)

        # Return OpenAI-compatible format
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": body.get("model", "gemini-2.5-flash"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        }
    except Exception as e:
        logger.error(f"Vapi chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# --- Streamlit UI endpoint (unchanged) ---
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response_text = await chat(request.message, request.history)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
