import streamlit as st
import dotenv
import asyncio
import nest_asyncio
import threading
from holocron import get_agent


nest_asyncio.apply()

dotenv.load_dotenv()

st.set_page_config(
    page_title="Sith Holocron",
    page_icon="⚡",
    layout="centered"
)

# Create a new agent instance per session so each user has their own memory
# Each call to get_agent() creates a new agent with a new ChatMemoryBuffer
if "agent" not in st.session_state:
    st.session_state.agent = get_agent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "I am the Sith Holocron. Ask, if you are strong enough to hear the truth."}
    ]

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/6/6c/Star_Wars_Logo.svg", width=200)
    st.title("Sith Archives")
    st.markdown("---")
    st.write("**System Status:** Online")
    st.write("**Model:** Llama 3.2 (Local)")
    if st.button("Clear Chat History"):
        # Reset messages and create a new agent instance to clear memory
        st.session_state.messages = [
            {"role": "assistant", "content": "I am the Sith Holocron. Ask, if you are strong enough to hear the truth."}
        ]
        # Create a new agent instance to clear its memory
        st.session_state.agent = get_agent()
        st.rerun()

st.title("⚡ The Sith Holocron")

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input Handler  
def run_agent_async(agent_instance, prompt_text):
    """Helper to run async agent.run() in Streamlit - runs in separate thread with own event loop
    The agent's memory should maintain conversation history internally"""
    result = None
    exception = None
    
    def run_in_thread():
        nonlocal result, exception
        try:
            # Apply nest_asyncio in this thread as well
            nest_asyncio.apply()
            # Create the coroutine inside the thread and run it
            # The agent's memory (ChatMemoryBuffer) should maintain conversation history
            async def run_agent():
                return await agent_instance.run(prompt_text)
            # Use asyncio.run() which creates and manages the event loop
            result = asyncio.run(run_agent())
        except Exception as e:
            exception = e
    
    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join()
    
    if exception:
        raise exception
    return result

# Chat Input Handler
if prompt := st.chat_input("Seek your knowledge..."):
    # 1. Add User Message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Accessing Dark Side Archives..."):
            try:
                # Agent.run() is async and handles memory internally via ChatMemoryBuffer
                # Each session has its own agent instance with its own memory
                response = run_agent_async(st.session_state.agent, prompt)
                
                # Display response
                st.markdown(str(response))
                
                # 3. Add Assistant Message to History
                st.session_state.messages.append({"role": "assistant", "content": str(response)})
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})