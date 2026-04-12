import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from agent.gemini_agent import chat

load_dotenv()

# Page configuration
st.set_page_config(page_title=f"{os.getenv('OWNER_NAME', 'Daksh')} — AI Persona", layout="wide")

# Styling
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; }
    .stSidebar { background-color: #f0f2f6; }
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

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is your experience?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Call the agent directly
        try:
            # Since chat is async, we use asyncio.run or manage the loop
            # Streamlit runs in a script-like fashion, so we use a helper
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response_text = loop.run_until_complete(chat(prompt, st.session_state.messages[:-1]))
            
            # Simulate streaming for character-by-character effect if SDK doesn't stream directly
            import time
            for chunk in response_text.split():
                full_response += chunk + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            full_response = "Sorry, I encountered an error processing your request."
            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
