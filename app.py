import streamlit as st
import dotenv
import os
import asyncio
import nest_asyncio
from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    StorageContext, 
    load_index_from_storage, 
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Context
from llama_index.core.agent import FunctionAgent
from llama_index.llms.ollama import Ollama
from holocron import get_agent

# --- 1. CONFIGURATION & SETUP ---
# Fixes "RuntimeError: This event loop is already running" in Streamlit
nest_asyncio.apply()

st.set_page_config(
    page_title="Sith Holocron",
    page_icon="⚡",
    layout="centered"
)

# Load the agent (cached)
agent = get_agent()

# --- 3. SESSION STATE (Chat Memory) ---
if "context" not in st.session_state:
    # Create a new memory context for this user session
    st.session_state.context = Context(agent)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "I am the Sith Holocron. Ask, if you are strong enough to hear the truth."}
    ]

# --- 4. UI: SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/6/6c/Star_Wars_Logo.svg", width=200)
    st.title("Sith Archives")
    st.markdown("---")
    st.write("**System Status:** Online")
    st.write("**Model:** Llama 3.2 (Local)")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.context = Context(agent)
        st.rerun()

# --- 5. UI: CHAT INTERFACE ---
st.title("⚡ The Sith Holocron")

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input Handler
def run_async_fix(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# Chat Input Handler
if prompt := st.chat_input("Seek your knowledge..."):
    # 1. Add User Message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Accessing Dark Side Archives..."):
            # --- THE FIX IS HERE ---
            # We use our custom helper instead of asyncio.run()
            response = run_async_fix(agent.run(prompt, context=st.session_state.context))
            
            # Display response
            st.markdown(str(response))
            
    # 3. Add Assistant Message to History
    st.session_state.messages.append({"role": "assistant", "content": str(response)})