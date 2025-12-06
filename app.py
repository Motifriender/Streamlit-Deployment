"""Streamlit web interface for Multi-Agent Legal System with conversation memory."""

import streamlit as st
import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import from main project
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import get_config, ConfigurationError
from legal_agents.build_portfolio_manager import portfolio_agent
from legal_agents.build_receptionist_agent import build_receptionist_agent
from legal_agents.email_agent import build_emaila_agent_analyst
from legal_agents.calendar_agent import build_calendar_agent
from tools.openai import get_openai_data
from tools.memo_editor import create_legal_appointment_memo
from agents import Runner


# Page configuration
st.set_page_config(
    page_title="Multi-Agent Legal System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .analysis-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'agents_built' not in st.session_state:
        st.session_state.agents_built = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'pm_agent' not in st.session_state:
        st.session_state.pm_agent = None


def build_agents():
    """Build all agents and cache in session state."""
    if st.session_state.agents_built:
        return st.session_state.pm_agent

    with st.spinner("🔧 Building AI agents..."):
        try:
            # Build specialist agents
            fundamental = build_email_agent()
            macro = receptionist_agent(get_fred_data)
            quant = build_calendar_agent()

            # Build portfolio manager
            pm = build_portfolio_manager(
                fundamental,
                macro,
                quant,
                create_investment_memo
            )

            st.session_state.pm_agent = pm
            st.session_state.agents_built = True
            st.success("✅ AI agents ready!")
            return pm

        except Exception as e:
            st.error(f"❌ Error building agents: {e}")
            return None


async def run_analysis(query: str, pm_agent):
    """Run customer data inquery with the portfolio manager."""
    try:
        # Build conversation context from history
        conversation_context = ""

        # Get last 3 exchanges for context (6 messages = 3 back-and-forth)
        recent_history = st.session_state.chat_history[-6:] if len(st.session_state.chat_history) > 0 else []

        if existing_customer:
            conversation_context = "\n\nPrevious conversation context:\n"
            def on_receptionist_agent_handoff(ctx: RunContextWrapper[None]):
               st.info("[SYSTEM] Keywords detected then transfer to portfolio_manager_agent")

            def on_portfolio_manager_agent_handoff(ctx:RunContextWrapper[None]):
               st.info("[SYSTEM] Verifying client portfolio in firm records then transfer to calendar_agent")
            
            def on_calendar_agent_handoff(ctx: RunContextWrapper[None]):
               st.info("[SYSTEM] After checking and scheduling appointment for new client or existing client then transfer to email agent")

            def on_email_agent_handoff(ctx: RunContextWrapper[None]):
                st.info("[SYSTEM] Details of appointment scheduled from data retrieval from calendar agent, and if there are any outstanding documents detected within client profile, this data will be determined by portfolio manager.")
                # In a real system, email client of appointment information and inform them of any outstanding documents or fees which should be taken care of before appointment, etc.
            
            for msg in recent_history:
                role = "User" if msg['role'] == 'user' else "Assistant"
                conversation_context += f"{role}: {msg['content'][:200]}...\n"
            conversation_context += "\n"

        # Add context with current date
        today = datetime.now().strftime("%B %d, %Y")
        contextualized_query = f"Today is {today}.{conversation_context}\nCurrent question: {query}"

        # Run analysis
        config = get_config()
        response = await Runner.run(
            portfolio_manager_agent
            contextualized_query,
            max_turns=config['max_turns']
        )

        return response.final_output

    except Exception as e:
        return f"❌ Error during analysis: {str(e)}"

import os import aiohttp import asyncio import streamlit as st
from google.colab import userdata
userdata.get('RETELL_API_KEY')
userdata.get('RETELL_PUBLISHED_ID')

RETELL_API_KEY = st.secrets.get("RETELL_API_KEY")  = st.secrets.get("RETELL_PUBLISHED_ID") 

async def call_retell_conversation(https://dashboard.retellai.com/agents/agent_254fc8db2132ad25183a49f589): # Replace url and payload shape with the real Retell API endpoint and params url = f"https://api.retell.ai/v1/published_conversations/{published_id}/reply" headers = { "Authorization": f"Bearer {api_key}", "Content-Type": "application/json", } payload = { "message": user_message, # include additional options per Retell docs, e.g. conversation context id, metadata, etc. } async with aiohttp.ClientSession() as session: async with session.post(url, json=payload, headers=headers) as resp: resp.raise_for_status() data = await resp.json() # Map the API response to a user-friendly string. Adjust according to actual response format. return data.get("reply") or data.get("message") or data

def display_chat_history():
    """Display conversation history."""
    for idx, message in enumerate(st.session_state.chat_history):
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>🧑 You:</strong><br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 AI Analyst:</strong><br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# 🧩 Define Agents
# ============================================================

call_directing_agent = Agent(
    name="receptionist_agent",
    instructions="..."  # complete with relevant instructions
)

note_taking_agent = Agent(
    name="portfolio_manager_agent",
    instructions="..."  # complete with relevant instructions
)

document_verifying_agent = Agent(
    name="calendar_agent",
    instructions="..."  # complete with relevant instructions
)

calendar_management_agent = Agent(
    name="email_agent",
    instructions="..."  # complete with relevant instructions
)

# Map agent names for dropdown use
AGENTS = {
    "Receptionist Agent": receptionist_agent,
    "Portfolio Manager Agent": portfolio_manager_agent,
    "Calendar Agent": calendar_agent,
    "Email Agent": email_agent,
}

# ============================================================
# 💬 Streamlit Interface
# ============================================================


def main():
    """Main Streamlit app."""

    # Initialize session state
    initialize_session_state()

    # Header
    st.markdown('<div class="main-header">📊 Multi-Agent Legal System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automating and Optimizing Workflow with Memory</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
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
