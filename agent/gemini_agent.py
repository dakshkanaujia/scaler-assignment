import os
import google.generativeai as genai
from dotenv import load_dotenv
from agent.retriever import get_retriever
from agent.calendar_tools import check_availability, book_slot, TOOLS

load_dotenv()

# Configure GenAI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Mapping tool names to functions for execution
AVAILABLE_TOOLS = {
    "check_availability": check_availability,
    "book_slot": book_slot
}

async def chat(user_message: str, history: list) -> str:
    owner_name = os.getenv("OWNER_NAME", "Daksh")
    
    # 1. Get RAG context
    retriever = get_retriever()
    if retriever:
        docs = retriever.get_relevant_documents(user_message)
        context = "\n".join([doc.page_content for doc in docs])
    else:
        context = "No additional context available."

    # 2. Build system prompt
    system_prompt = f"""You are the AI representative of {owner_name}. Answer ONLY using the provided context. Keep answers brief (2-3 sentences max), conversational, and honest. If the context does not contain the answer, say so — do not hallucinate. When a user wants to book a meeting, use the check_availability tool first, then book_slot."""

    # 3. Configure Model with Tools
    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        system_instruction=system_prompt,
        tools=TOOLS
    )

    # 4. Prepare Message with context
    full_message = f"Context:\n{context}\n\nUser Message: {user_message}"
    
    # 5. Start Chat/Process
    # Note: We manage history manually or via SDK. The requirements ask for 'history: list' as input.
    # Converting history to GenAI format if needed, but for now we process the current message.
    
    chat_session = model.start_chat(history=[]) # Could populate from history input
    
    response = chat_session.send_message(full_message)
    
    # 6. Handle Function Calls
    while response.candidates[0].content.parts[0].function_call:
        fc = response.candidates[0].content.parts[0].function_call
        tool_name = fc.name
        tool_args = fc.args
        
        if tool_name in AVAILABLE_TOOLS:
            # Execute tool
            if tool_name == "book_slot":
                result = await book_slot(email=tool_args['email'], iso_time=tool_args['iso_time'])
            else:
                result = await check_availability()
            
            # Send result back to model
            response = chat_session.send_message(
                genai.types.Content(
                    parts=[genai.types.Part.from_function_response(
                        name=tool_name,
                        response={'result': result}
                    )]
                )
            )
        else:
            break

    return response.text

if __name__ == "__main__":
    # Test script (requires API key)
    import asyncio
    async def test():
        res = await chat("What is Daksh's experience?", [])
        print(f"AI: {res}")
    # asyncio.run(test())
