"""
Streamlit web interface for Multi-Agent Legal System with conversation memory.
Replace placeholder agent builders with your real implementations.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import asyncio
import json

import streamlit as st

# Add parent directory to path to import from main project (adjust as needed)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Attempt to import your project modules; fall back to placeholders for local testing
try:
    from config.settings import get_config, ConfigurationError
except Exception:
    def get_config():
        # Minimal config fallback
        return {"max_turns": 3}
    ConfigurationError = Exception

try:
    # Replace these with your real builder functions if available
    from legal_agents.build_portfolio_manager import build_portfolio_manager
    from legal_agents.build_receptionist_agent import build_receptionist_agent
    from legal_agents.email_agent import build_email_agent
    from legal_agents.calendar_agent import build_calendar_agent
except Exception:
    # Placeholder builders for testing — replace with your real functions.
    def build_receptionist_agent():
        async def run(input_text):
            return type("R", (), {"final_output": f"[Receptionist] Echo: {input_text}"})
        return {"name": "receptionist_agent", "run": run}

    def build_portfolio_manager(*args, **kwargs):
        async def run(input_text):
            return type("R", (), {"final_output": f"[PortfolioManager] Echo: {input_text}"})
        return {"name": "portfolio_manager_agent", "run": run}

    def build_calendar_agent():
        async def run(input_text):
            return type("R", (), {"final_output": f"[CalendarAgent] Echo: {input_text}"})
        return {"name": "calendar_agent", "run": run}

    def build_email_agent():
        async def run(input_text):
            return type("R", (), {"final_output": f"[EmailAgent] Echo: {input_text}"})
        return {"name": "email_agent", "run": run}

# Runner: prefer your project's Runner; fallback to a simple runner that calls agent['run']
try:
    from agents import Runner
except Exception:
    class Runner:
        @staticmethod
        async def run(agent, message, **kwargs):
            # If agent is a callable/coroutine function
            if callable(agent):
                res = agent(message)
                if asyncio.iscoroutine(res):
                    res = await res
                return res
            # If agent is an object/dict with async run method
            run_method = None
            if isinstance(agent, dict) and "run" in agent:
                run_method = agent["run"]
            elif hasattr(agent, "run"):
                run_method = getattr(agent, "run")
            if run_method is None:
                # simple echo fallback
                return type("R", (), {"final_output": f"[Fallback Runner] Echo: {message}"})
            res = run_method(message)
            if asyncio.iscoroutine(res):
                res = await res
            return res

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Legal System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: bold; color: #1f77b4; text-align: center; margin-bottom: 1rem; }
    .sub-header { font-size: 1.0rem; color: #666; text-align: center; margin-bottom: 1.2rem; }
    .chat-message { padding: 0.8rem; border-radius: 8px; margin-bottom: 0.6rem; }
    .user-message { background-color: #e3f2fd; border-left: 4px solid #2196f3; }
    .assistant-message { background-color: #f5f5f5; border-left: 4px solid #4caf50; }
</style>
""", unsafe_allow_html=True)


# ----------------------------
# Session state init
# ----------------------------
def initialize_session_state():
    if "agents_built" not in st.session_state:
        st.session_state.agents_built = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    if "agents" not in st.session_state:
        st.session_state.agents = {}


# ----------------------------
# Build agents (cache in session)
# ----------------------------
def build_agents():
    if st.session_state.agents_built:
        return st.session_state.agents

    with st.spinner("🔧 Building AI agents..."):
        try:
            # Use your real builders here; placeholders exist above if imports failed
            receptionist = build_receptionist_agent()
            portfolio_manager = build_portfolio_manager()
            calendar = build_calendar_agent()
            email = build_email_agent()

            # Map to names expected by the UI
            agents_map = {
                "Receptionist Agent": receptionist,
                "Portfolio Manager Agent": portfolio_manager,
                "Calendar Agent": calendar,
                "Email Agent": email,
            }

            st.session_state.agents = agents_map
            st.session_state.agents_built = True
            st.success("✅ AI agents ready!")
            return agents_map

        except Exception as e:
            st.error(f"❌ Error building agents: {e}")
            # ensure we still have at least an empty dict
            st.session_state.agents = {}
            return st.session_state.agents


# ----------------------------
# Async analysis runner
# ----------------------------
async def run_agent_async(agent_obj, query: str):
    """
    Run an agent object. The agent_obj can be:
      - an async function taking (query)
      - an object or dict with an async run(query) method
      - anything Runner.run expects
    """
    try:
        # Prefer project's Runner if available (we defined fallback earlier)
        result = await Runner.run(agent_obj, query, max_turns=get_config().get("max_turns", 3))
        return result.final_output if hasattr(result, "final_output") else str(result)
    except Exception as e:
        return f"❌ Error while running agent: {e}"


# ----------------------------
# Retell integration (optional)
# ----------------------------
import aiohttp

RETELL_API_KEY = st.secrets.get("RETELL_API_KEY") if hasattr(st, "secrets") else os.getenv("RETELL_API_KEY")

async def call_retell_conversation(published_id: str, user_message: str, api_key: str):
    """
    Call Retell (replace endpoint/payload with actual Retell docs if different).
    Returns reply string or raises.
    """
    if not api_key:
        raise ValueError("RETELL_API_KEY not configured")

    url = f"https://api.retell.ai/v1/published_conversations/{published_id}/reply"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"message": user_message}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
            # Map according to Retell response structure — adapt as needed
            # Try common fields
            reply = data.get("reply") or data.get("message") or data.get("response") or json.dumps(data)
            return reply


# ----------------------------
# UI helpers
# ----------------------------
def display_chat_history():
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(
                f'<div class="chat-message user-message"><strong>🧑 You:</strong><br>{message["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-message assistant-message"><strong>🤖 Agent:</strong><br>{message["content"]}</div>',
                unsafe_allow_html=True,
            )


def add_to_chat(role: str, content: str):
    st.session_state.chat_history.append({"role": role, "content": content})


# ----------------------------
# Main app
# ----------------------------
def main():
    initialize_session_state()
    agents = build_agents()

    st.markdown('<div class="main-header">📊 Multi-Agent Legal System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automating and Optimizing Workflow with Memory</div>', unsafe_allow_html=True)

    # Layout
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.header("Conversation")
        display_chat_history()

        user_message = st.text_area("Enter a client message or query:", height=140, key="user_message")

        cols = st.columns([1, 1, 1])
        if cols[0].button("Send to Selected Agent"):
            selected_agent_key = st.session_state.get("selected_agent", None)
            if not user_message or not user_message.strip():
                st.warning("Please enter a message first!")
            elif not selected_agent_key:
                st.warning("Select an agent from the sidebar first.")
            else:
                selected_agent_obj = agents.get(selected_agent_key)
                add_to_chat("user", user_message)

                # Run agent asynchronously using a fresh loop (safe in Streamlit)
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    reply = loop.run_until_complete(run_agent_async(selected_agent_obj, user_message))
                finally:
                    loop.close()
                add_to_chat("assistant", reply)
                st.experimental_rerun()  # refresh UI to show new messages

        if cols[1].button("Send to Retell (published)"):
            if not user_message or not user_message.strip():
                st.warning("Enter a message first.")
            else:
                if not RETELL_API_KEY or not RETELL_PUBLISHED_ID:
                    st.error("Retell keys not configured. Add RETELL_API_KEY and RETELL_PUBLISHED_ID to Streamlit secrets.")
                else:
                    add_to_chat("user", user_message)
                    loop = asyncio.new_event_loop()
                    try:
                        asyncio.set_event_loop(loop)
                        reply = loop.run_until_complete(call_retell_conversation(RETELL_PUBLISHED_ID, user_message, RETELL_API_KEY))
                    finally:
                        loop.close()
                    add_to_chat("assistant", reply)
                    st.experimental_rerun()

        if cols[2].button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    with col_right:
        st.sidebar.header("🎯 Test Any Agent")
        agent_names = list(agents.keys()) if agents else []
        selected_agent = st.sidebar.selectbox("Choose an agent to test:", agent_names, key="selected_agent")
        st.sidebar.markdown("---")
        st.sidebar.header("Session")
        st.sidebar.write(f"Agents built: {st.session_state.agents_built}")
        st.sidebar.write(f"Chat turns: {len(st.session_state.chat_history)}")
        st.sidebar.markdown("---")
        st.sidebar.header("Config")
        cfg = get_config()
        st.sidebar.write(cfg)

    st.markdown("---")
    st.info("✅ Agents ready (or running fallback stubs). Replace placeholders with your real builders for production.")


if __name__ == "__main__":
    main()
