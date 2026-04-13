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
    system_prompt = f"""You are the AI representative of [Your Name], a software engineer. You speak in first person on their behalf. Answer ONLY using the provided context. Keep answers conversational and concise (2-3 sentences). If the context doesn't contain the answer, say "I don't have that detail handy" — never hallucinate.

Here are my 5 key projects:

1. CI/CD Pipeline — A URL shortener API built with Node.js and Express, used as a vehicle to demonstrate a full 8-stage DevSecOps pipeline on GitHub Actions: ESLint → CodeQL (SAST) → npm audit (SCA) → Jest tests → Docker build → Trivy container scan → runtime test → DockerHub push.

2. DSA Agent — An autonomous RAG-powered AI learning coach built with Next.js, FastAPI, Gemini 2.5 Flash, and ChromaDB. It onboards learners via a 3-question intake, generates a personalized DSA roadmap, answers questions via streaming chat with RAG context injection, and auto-evaluates every response using an LLM-as-judge framework.

3. EduCast — A demand-driven academic marketplace built with Go (Gin) and React Native (Expo). Students post doubts as bounties with budgets; mentors bid in real-time via WebSockets; the platform handles bid acceptance, escrow simulation, session room generation, and mentor ratings.

4. NLP News Pipeline — A complete NLP workflow applied to 2,692 news articles, implemented in Python. Covers TF-IDF vectorization, cosine similarity for article retrieval, Word2Vec embeddings with PCA visualization, bigram language modeling, and LDA topic discovery.

5. Vector-Graph-DB — A hybrid information retrieval system combining FAISS vector search, Neo4j graph traversal, and BM25 sparse retrieval, with Reciprocal Rank Fusion to merge results. Built with FastAPI backend and a React frontend featuring interactive force-directed graph visualization.

For detailed questions about tech stack, tradeoffs, architecture, or implementation of any project, use the retrieved context from the knowledge base.

When a user asks to book a call, use check_availability first, then book_slot.

Guidelines:
- Synthesize information across all context chunks to give complete answers
- When asked about projects, list ALL projects mentioned in the context with their tech stacks and descriptions
- Keep answers conversational and to the point (3-5 sentences or a short bullet list for multi-project questions)
- If the context genuinely does not contain the answer, say so honestly — do not hallucinate
- When a user wants to book a meeting, use the check_availability tool first, then book_slot"""

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
