import os
import uuid
import time
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
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

# --- Unified Chat Endpoint (Handles both formats) ---
@app.post("/chat")
@app.post("/chat/completions")
async def unified_chat_endpoint(request: Request):
    """
    Unified endpoint that detects whether the request is:
    1. Simple format: {"message": "...", "history": [...]}
    2. OpenAI format: {"messages": [...], "model": "..."}
    """
    try:
        body = await request.json()
        
        # Check if it's OpenAI format
        if "messages" in body:
            logger.info(f"OpenAI format request detected. Model: {body.get('model')}")
            messages = body.get("messages", [])
            
            # Extract last user message and history
            user_message = ""
            history = []
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "system":
                    continue
                if role in ("user", "assistant"):
                    history.append({"role": role, "content": content or ""})
            
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
        
        # Simple format (for Streamlit UI)
        elif "message" in body:
            logger.info("Simple format request detected.")
            message = body.get("message")
            history = body.get("history", [])
            response_text = await chat(message, history)
            return {"response": response_text}
            
        else:
            logger.warning(f"Unknown request format: {body}")
            raise HTTPException(status_code=400, detail="Unknown request format. Expected 'messages' or 'message' field.")

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        # Return OpenAI-compatible error if possible
        error_response = {
            "error": {
                "message": str(e),
                "type": "server_error",
                "param": None,
                "code": None
            }
        }
        return JSONResponse(status_code=500, content=error_response)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
