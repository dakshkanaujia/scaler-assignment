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

    # 1. Get RAG context
    try:
        retriever = get_retriever()
        if retriever:
            docs = retriever.invoke(user_message)
            context = "\n".join([doc.page_content for doc in docs])
            logger.info(f"RAG retrieved {len(docs)} docs, context length: {len(context)} chars")
        else:
            logger.warning("RAG retriever returned None — chroma_db may be missing or failed to load")
            context = "No additional context available."
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}", exc_info=True)
        context = "No additional context available."

    # 2. Build system prompt
    system_prompt = f"""You are the AI representative of {owner_name}. Use the provided context to answer questions about {owner_name}'s background, skills, experience, and projects.

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
