import os
import uuid
import time
import logging
import json
import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
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

@app.get("/ping")
async def ping():
    return {"status": "pong"}

def extract_content(content):
    """Handle both string and list content formats from Vapi"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            part.get("text", "") for part in content
            if isinstance(part, dict)
        )
    return str(content) if content else ""

async def stream_openai_response(text: str, model: str):
    """Stream response word by word in OpenAI chunk format"""
    words = text.split(" ")
    for word in words:
        chunk = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"content": word + " "},
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        # Small delay so Vapi can process chunks
        await asyncio.sleep(0.01)

    # Final chunk
    final_chunk = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"

# --- Unified Chat Endpoint (Handles both formats) ---
@app.post("/chat")
@app.post("/chat/completions")
async def unified_chat_endpoint(request: Request):
    try:
        body = await request.json()
        logger.info(f"RAW VAPI BODY: {body}")

        # OpenAI format (Vapi)
        if "messages" in body:
            logger.info(f"OpenAI format request detected. Model: {body.get('model')}")
            messages = body.get("messages", [])
            user_message = ""
            history = []

            for msg in messages:
                role = msg.get("role", "")
                content = extract_content(msg.get("content", ""))
                if role == "system":
                    continue
                if role in ("user", "assistant"):
                    history.append({"role": role, "content": content or ""})

            if history and history[-1]["role"] == "user":
                user_message = history.pop()["content"]
            else:
                user_message = "Hello"

            response_text = await chat(user_message, history)
            model_name = body.get("model", "gemini-1.5-flash")

            # Check if client wants streaming
            if body.get("stream", False):
                return StreamingResponse(
                    stream_openai_response(response_text, model_name),
                    media_type="text/event-stream"
                )

            # Non-streaming response
            return {
                "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_name,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text,
                    },
                    "finish_reason": "stop",
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
            }

        # Simple format (Streamlit UI)
        elif "message" in body:
            logger.info("Simple format request detected.")
            message = body.get("message")
            history = body.get("history", [])
            response_text = await chat(message, history)
            return {"response": response_text}

        else:
            logger.warning(f"Unknown request format: {body}")
            raise HTTPException(status_code=400, detail="Unknown request format.")

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={
            "error": {
                "message": str(e),
                "type": "server_error",
                "param": None,
                "code": None
            }
        })

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)