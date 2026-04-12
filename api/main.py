import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agent.gemini_agent import chat
from agent.ingest import ingest_data

app = FastAPI(title="AI Persona API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
