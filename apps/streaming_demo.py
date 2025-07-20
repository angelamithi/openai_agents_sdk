import asyncio
import streamlit as st
import os
import sys
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner

# Load API Key
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set")

# Streamlit Config
st.set_page_config(
    page_title="OpenAI Agents Streaming Demo",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 OpenAI Agents Streaming Demo")

# Sidebar UI
with st.sidebar:
    agent_name = st.text_input("Agent Name", "StreamBot")
    agent_instructions = st.text_area("Agent Instructions", "You are a helpful assistant.")
    selected_model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "o3-mini"], index=1)
    demo_prompt = st.selectbox("Quick Prompts", [
        "Tell me 5 jokes",
        "Write a short story about a robot",
        "Explain how AI works to a 5-year-old",
        "Create a short poem about technology",
        "Give me 3 interesting facts about space"
    ])
    st.markdown("---")

# Main Input and Output
user_input = st.text_area("Your message:", value=demo_prompt, height=100)
send_button = st.button("Send", type="primary")

response_container = st.container()
message_placeholder = response_container.empty()

# This is the main function for streaming responses to the front end.

# Async stream function
async def stream_response(agent: Agent, user_input: str):
    response_parts = ""
    try:
        result = Runner.run_streamed(agent, input=user_input)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                response_parts += event.data.delta
                message_placeholder.markdown(response_parts + "▌")
        message_placeholder.markdown(response_parts)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Streamlit now supports async handlers
if send_button and user_input:
    agent = Agent(
        name=agent_name,
        instructions=agent_instructions,
        model=selected_model,
    )
    with st.spinner("Thinking..."):
        asyncio.run(stream_response(agent, user_input))  # only works if not already inside an event loop

    if st.button("Clear"):
        st.experimental_rerun()
else:
    with response_container:
        st.info("👆 Enter your message and click 'Send' to see a response.")


# Instructions when idle
if not send_button:
    with response_container:
        st.info("👆 Enter your message above and click 'Send' to see the streaming response.")
        st.markdown("""
        ### Tips:
        - Choose from the quick prompts or enter your own
        - Try complex prompts to see how the agent responds in real-time
        """)
