import streamlit as st
import asyncio
import os
import sys

# Ensure root directory is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from agent.gemini_agent import chat

load_dotenv()

# Page configuration
st.set_page_config(page_title=f"{os.getenv('OWNER_NAME', 'Daksh')} — AI Persona", layout="wide")

# Styling
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; }
    .stSidebar { 
        background-color: #1E1E1E; 
        color: #FFFFFF;
    }
    .stSidebar [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("👨‍💻 AI Persona")
    st.write(f"**Name**: {os.getenv('OWNER_NAME', 'Daksh')}")
    st.write(f"**Role**: {os.getenv('ROLE', 'AI Developer')}")
    st.divider()
    
    st.write("### 📅 Book a Call")
    st.info("Want to chat? Ask me to check my availability or book a slot!")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.write("### ℹ️ About")
    st.write("This is an AI representation designed to answer questions about projects, experience, and handle scheduling.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Suggested Questions
if not st.session_state.messages:
    st.write("### 👋 Welcome! How can I help you today?")
    st.write("Here are some things you can ask me:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("What is your experience?"):
            st.session_state.suggested_query = "What is your experience?"
        if st.button("Tell me about your projects"):
            st.session_state.suggested_query = "Tell me about your projects"
    with col2:
        if st.button("How can I book a meeting?"):
            st.session_state.suggested_query = "How can I book a meeting?"
        if st.button("Check availability for tomorrow"):
            st.session_state.suggested_query = "Check availability for tomorrow"

# React to user input
prompt = st.chat_input("Ask me something...")
if "suggested_query" in st.session_state:
    prompt = st.session_state.pop("suggested_query")

if prompt:
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Store previous messages for context
    context_msgs = list(st.session_state.messages)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Create a localized event loop for the async call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response_text = loop.run_until_complete(chat(prompt, context_msgs))
            
            # Simulate streaming
            import time
            words = response_text.split()
            for i in range(len(words)):
                full_response = " ".join(words[:i+1])
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.02) # Faster streaming
            
            message_placeholder.markdown(response_text)
            full_response = response_text # Use the original text for history
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.error(error_msg)
            full_response = error_msg
            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun() # Ensure UI refreshes with the new message
