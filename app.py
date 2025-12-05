import os
import asyncio
from datetime import datetime
import streamlit as st

# Ensure agents module exists and imports are correct
try:
    from agents import Agent, Runner, handoff, RunContextWrapper
except ImportError as e:
    st.error(f"Error importing agents module: {e}")

# ============================================================
# 🔧 Environment Setup
# ============================================================

# Load your API Key (from Streamlit secrets or environment)
openai_api_key = st.secrets.get("OPENAI_API_KEY", None)
if not openai_api_key:
    st.warning("⚠️ OpenAI API key not found in Streamlit secrets. Please add it under Settings.")
else:
    os.environ["OPENAI_API_KEY"] = openai_api_key

# ============================================================
# 🔁 Async Example (demo)
# ============================================================

async def fetch_data():
    await asyncio.sleep(1)
    return "Async task completed successfully."

st.title("📞 Law Firm Agent Framework")
st.write(asyncio.run(fetch_data()))

# ============================================================
# 🤖 Agent Callbacks (handoffs)
# ============================================================

def on_note_taking_agent_handoff(ctx: RunContextWrapper[None]):
    st.info("[SYSTEM] Keywords detected → transferring to Note Taking Agent")

def on_note_taking_assistant_handoff(ctx: RunContextWrapper[None]):
    st.info("[SYSTEM] Data saved to Sheet → transferring to Note Taking Assistant")

def on_calendar_management_agent_handoff(ctx: RunContextWrapper[None]):
    st.info("[SYSTEM] Date/time detected → transferring to Calendar Management Agent")

def on_calendar_assistant_handoff(ctx: RunContextWrapper[None]):
    st.info("[SYSTEM] Calendar data requested → transferring to Calendar Assistant")

def on_document_verifying_agent_handoff(ctx: RunContextWrapper[None]):
    st.info("[SYSTEM] Checking document completion → transferring to Document Verifying Agent")

def on_case_preparation_agent_handoff(ctx: RunContextWrapper[None]):
    st.info("[SYSTEM] Appointment info recorded → transferring to Case Preparation Agent")

# ============================================================
# 🧩 Define Agents
# ============================================================

call_directing_agent = Agent(
    name="CallDirectingAgent",
    instructions="..."  # complete with relevant instructions
)

note_taking_agent = Agent(
    name="NoteTakingAgent",
    instructions="..."  # complete with relevant instructions
)

document_verifying_agent = Agent(
    name="DocumentVerifyingAgent",
    instructions="..."  # complete with relevant instructions
)

calendar_management_agent = Agent(
    name="CalendarManagementAgent",
    instructions="..."  # complete with relevant instructions
)

case_preparation_agent = Agent(
    name="CasePreparationAgent",
    instructions="..."  # complete with relevant instructions
)

# Map agent names for dropdown use
AGENTS = {
    "Call Directing Agent": call_directing_agent,
    "Note Taking Agent": note_taking_agent,
    "Document Verifying Agent": document_verifying_agent,
    "Calendar Management Agent": calendar_management_agent,
    "Case Preparation Agent": case_preparation_agent,
}

# ============================================================
# 💬 Streamlit Interface
# ============================================================

st.header("🎯 Test Any Agent")

selected_agent_name = st.selectbox("Choose an agent to test:", list(AGENTS.keys()))
selected_agent = AGENTS[selected_agent_name]

user_message = st.text_area("Enter a client message or query:", height=120)

if st.button("🚀 Run Selected Agent"):
    if not user_message.strip():
        st.warning("Please enter a message first!")
    else:
        with st.spinner("Running agent asynchronously..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(Runner.run(selected_agent, user_message))
                st.success("✅ Agent Response:")
                st.write(result.final_output)
            except Exception as e:
                st.error(f"Error running agent: {e}")

st.markdown("---")
st.info("✅ All agents are initialized and ready.")
