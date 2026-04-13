import os
import logging

logger = logging.getLogger(__name__)
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from dotenv import load_dotenv
from agent.retriever import get_retriever
from agent.calendar_tools import check_availability, book_slot

load_dotenv()

# Configure GenAI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define tools using the proper Gemini SDK format
check_availability_fn = FunctionDeclaration(
    name="check_availability",
    description="Check for available meeting slots in the next 7 days.",
    parameters={"type": "object", "properties": {}}
)

book_slot_fn = FunctionDeclaration(
    name="book_slot",
    description="Book a meeting slot at a specific ISO 8601 time.",
    parameters={
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of the person booking the meeting."},
            "iso_time": {"type": "string", "description": "The ISO 8601 formatted start time (e.g. 2024-04-12T10:00:00Z)."}
        },
        "required": ["email", "iso_time"]
    }
)

TOOLS = [Tool(function_declarations=[check_availability_fn, book_slot_fn])]

async def chat(user_message: str, history: list) -> str:
    owner_name = os.getenv("OWNER_NAME", "Daksh")

    # Short-circuit for greetings — save Gemini quota
    if user_message.lower().strip().rstrip("?.!") in ["hello", "hi", "hey", "hello"]:
        return f"Hi! I'm {owner_name}'s AI representative. Feel free to ask me about his background, projects, or book a call!"

    # 1. Get RAG context
    try:
        retriever = get_retriever()
        if retriever:
            # Skip RAG for very short messages
            if len(user_message.split()) < 4:
                context = ""
            else:
                docs = retriever.invoke(user_message)
                context = "\n".join([doc.page_content for doc in docs])
                logger.info(f"RAG retrieved {len(docs)} docs, context length: {len(context)} chars")
        else:
            context = "No additional context available."
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}", exc_info=True)
        context = "No additional context available."


    # 2. Build system prompt
    system_prompt = f"""You are the AI representative of Daksh, a software engineer. You speak in first person as Daksh.

CORE BEHAVIOR:
- Be natural, conversational, and adaptive (not robotic or scripted)
- Answer in 3–5 sentences max unless explicitly asked for detail
- Handle follow-ups intelligently and maintain context across turns
- NEVER hallucinate — if unsure, say: "I don't have that detail handy"
- Sound like a real person in a conversation, not a FAQ bot

GROUNDING (CRITICAL):
- You MUST answer strictly using retrieved context from Daksh's resume, GitHub, and knowledge base
- Do NOT invent projects, metrics, or experiences
- If context is insufficient, admit it honestly

PROJECT KNOWLEDGE:
You have access to 5 key projects. When asked:
- Always explain WHAT it does + WHY it was built + HOW it works + key TRADEOFFS
- Mention tech stack explicitly
- Be ready for deep dives (architecture, scaling, design decisions)

Projects:
1. CI/CD Pipeline — Node.js, Express, GitHub Actions, Docker, Trivy, CodeQL  
2. DSA Agent — Next.js, FastAPI, Gemini 2.5 Flash, ChromaDB (RAG + LLM judge)  
3. EduCast — Go (Gin), React Native, WebSockets (real-time bidding system)  
4. NLP News Pipeline — Python, TF-IDF, Word2Vec, LDA  
5. Vector-Graph-DB — FastAPI, React, FAISS, Neo4j, BM25, RRF  

INTERVIEW-FOCUSED RESPONSES:
- When asked "Why are you a good fit?" → connect projects to:
  - AI systems (RAG, LLM evals)
  - backend + infra (FastAPI, Go, pipelines)
  - real-world problem solving
- Highlight impact, not just implementation

FOLLOW-UP HANDLING:
- Expect probing questions (edge cases, tradeoffs, failures)
- Answer thoughtfully, not defensively
- If something failed → explain what went wrong + how you fixed it

BOOKING FLOW (CRITICAL REQUIREMENT):
- If user shows intent to schedule:
  1. Ask for their preferred time
  2. Call check_availability
  3. Suggest available slots
  4. Confirm and call book_slot
- Keep it smooth and human-like, not tool-like

VOICE + CHAT ALIGNMENT:
- Keep responses short enough for voice (<= 20–25 sec speaking)
- Avoid long paragraphs
- Use natural pauses and phrasing

EDGE CASE HANDLING:
- If user asks something outside resume/GitHub → say you don’t have that detail
- If user tests hallucination → stay grounded
- If user asks vague questions → ask a clarifying question

STYLE:
- Confident but not arrogant
- Specific, not generic
- Practical, not theoretical

GOAL:
Convince the user (recruiter) that Daksh can:
- Build production-grade AI systems
- Handle real-world ambiguity
- Communicate clearly and honestly
- Deliver an end-to-end working product (voice + chat + booking)"""

    # 3. Configure Model with Tools
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=system_prompt,
        tools=TOOLS
    )

    # 4. Prepare message with context
    full_message = f"Context:\n{context}\n\nUser Message: {user_message}"

    # 5. Transform history for Gemini SDK
    # Gemini expects: [{'role': 'user', 'parts': ['...']}, {'role': 'model', 'parts': ['...']}]
    transformed_history = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        content = msg["content"]
        transformed_history.append({"role": role, "parts": [content]})

    chat_session = model.start_chat(history=transformed_history)
    response = chat_session.send_message(full_message)

    # 6. Handle Function Calls in a loop
    for _ in range(5):  # Max 5 tool rounds
        # Safely check if this response contains a function call
        parts = response.candidates[0].content.parts
        if not parts or not hasattr(parts[0], 'function_call') or not parts[0].function_call.name:
            break

        fc = parts[0].function_call
        tool_name = fc.name
        tool_args = dict(fc.args)

        if tool_name == "book_slot":
            result = await book_slot(email=tool_args.get('email'), iso_time=tool_args.get('iso_time'))
        elif tool_name == "check_availability":
            result = await check_availability()
        else:
            break

        response = chat_session.send_message(
            genai.protos.Content(
                parts=[genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=tool_name,
                        response={"result": result}
                    )
                )]
            )
        )

    # Safely extract text — avoid crash if last part is still a function_call
    try:
        return response.text
    except Exception:
        # Extract text from parts manually
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                return part.text
        return "I encountered an issue processing your request. Please try again."
