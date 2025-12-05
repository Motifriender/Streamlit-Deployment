!pip install openai-agents -q
!pip install openai -q

pip install -U pydantic

import os
import openai
import asyncio
from datetime import datetime
from agents import Agent, Runner, function_tool, handoff, RunContextWrapper
from google.colab import userdata

# Get the OpenAI API key from Colab's user data
openai_api_key = userdata.get('OpenAI')

# Set the OpenAI API key as an environment variable with the correct name
os.environ["OPENAI_API_KEY"] = openai_api_key

from agents import Agent, Runner, handoff, RunContextWrapper

# Call Directing Agent
call_directing_agent = Agent(
    name="CallDirectingAgent",
    instructions="""
   You handle all incoming calls from customers, filter through clients and schedule appointments with professionals considering available dates and times from Google Calendar.

    Guidelines:
    1. Maintain a professional, consultative tone
    2. Focus on understanding customer challenges using key words
    3. Collect key information including:
       - Accident Details: Dates, locations, and details of the accident, including the nature and extent of injuries
       - Medical records: Doctor diagnoses, treatment plans, and hospital bills.
       - Insurance information: Details of all involved parties insurance and insurance claims
       - Witness information: Contact details or statements from witnesses
       - Photos or videos: Documentation of inflicted injuries, property damage, or accident scene.
    4. Emphasize lawyer's experience with similar cases, if relevant
    5. Suggest appropriate next steps (scheduling a consultation with lawyer if appropriate)

    Remember that enterprise clients value expertise, reliability, and strategic partnership.

    handoffs=[
        handoff(note_taking_agent, on_handoff=on_note_taking_agent_handoff),
        handoff(note_taking_assistant, on_handoff=on_note_taking_assistant_handoff),
        handoff(calendar_management_agent, on_handoff=on_calendar_management_agent_handoff),
        handoff(calendar_assistant, on_handoff=on_calendar_assistant_handoff),
        handoff(document_verifying_agent, on_handoff=on_document_verifying_agent_handoff),
        handoff(case_preparation_agent, on_handoff=on_case_preparation_agent_handoff)
    ],
    tools=[]
    """
)

# Callback functions for handoffs
def on_note_taking_agent_handoff(ctx: RunContextWrapper[None]):
    print("[SYSTEM] Relevant key words detected - transferring to Note Taking Agent")
    # In a real system, you could log this transfer, update systems, etc.

# Callback functions for handoffs
def on_note_taking_assistant_handoff(ctx: RunContextWrapper[None]):
    print("[SYSTEM] Relevant key words detected and written in Google sheet- transferring to Note Taking Assistant")
    # In a real system, you could log this transfer, update systems, etc.

def on_calendar_management_agent_handoff(ctx: RunContextWrapper[None]):
    print("[SYSTEM] Date and time detected - transferring to Calendar Management Agent")
    # In a real system, you could log this transfer, update systems, etc.

def on_calendar_assistant_handoff(ctx: RunContextWrapper[None]):
    print("[SYSTEM] Date and time detected - transferring to Calendar Assistant")
    # In a real system, you could log this transfer, update systems, etc.

def on_document_verifying_agent_handoff(ctx: RunContextWrapper[None]):
    print("[SYSTEM] Checking and confirming all outstanding documents are complete with being submitted with client signature - transferring to Document Verifying Agent")
    # In a real system, you could log this transfer, update systems, etc.

def on_case_preparation_agent_handoff(ctx: RunContextWrapper[None]):
    print("[SYSTEM] Appointment and relevant key words have been recorded and detected - transferring data to internal legal team")
    # In a real system, you could log this transfer, update systems, etc.

# Test the Call Directing Agent
async def test_call_directing_agent():
    result = await Runner.run(call_directing_agent, "Hello. Thank you for calling Law Offices of Melnik and Vasquez . How can I help you today?")
    print("Call Directing Agent Response:")
    print(result.final_output)
    print("\n" + "-"*50 + "\n")

await test_call_directing_agent()

!pip install openai-agents -q
from agents import Agent, Runner
import os
from google.colab import userdata

# Get the OpenAI API key from Colab's user data
openai_api_key = userdata.get('OpenAI')

# Set the OpenAI API key as an environment variable
os.environ["OPENAI_API_KEY"] = openai_api_key

# Note Taking Lead Agent
note_taking_agent = Agent(
    name="Note_Taking_Agent",
    instructions="""
    You are a Note Taking Agent who is taking notes from phone call with customer.
    Guidelines:
    1. Collect key information including:
       - Date and location of accident
       - Nature and extent of any injuries
       - Any medical treatment you’ve received (such as diagnoses, treatment plans, or hospital visits)
       - Information about any insurance claims, either yours or those of other involved parties
       - Contact information of witnesses
       - Any photos or videos of the accident
           Remember that goal of Note Taking Agent is to prepare lawyer with categorized information that is collected from Call Directing Agent for consultation appointment.
    """
)

# Test the Note Taking Agent
async def test_note_taking_agent():
    result = await Runner.run(note_taking_agent, "Thank you for taking the time to provide us with your accident details. Our trusted lawyers at Law Offices of Melnik and Vasquez. We will look into this and get you taken care. Please review the information collected to ensure accuracy with your case. Thank you.")
    print("Note Taking Agent Response:")
    print(result.final_output)
    print("\n" + "-"*50 + "\n")

await test_note_taking_agent()

from agents import Agent, Runner
from agents.mcp import MCPServerSse
import asyncio

# Define a function to chat with the agent
async def chat(question):
    # Connect to your MCP server
    mcp_server = MCPServerSse(
        params={
            "url": "https://vanessagomez.app.n8n.cloud/mcp/gsheet"
        },
        cache_tools_list=True
    )

    # Connect to the server
    await mcp_server.connect()

    try:
        # Define the conversational agent with vector store access
        chat_agent = Agent(
            name="Note Taking Assistant",
            instructions="""You are a helpful assistant that documents the following information from the client into a Google Sheet titled Accident & Injury Information Summary. The information below is to be collected from the client.

**1. Date and Location of Accident**
- Date of Accident: [Insert date]
- Location of Accident: [Insert precise location or intersection, city]

**2. Nature and Extent of Injuries**
- Reported Injuries: [List injuries sustained; e.g., neck pain, broken arm, bruises, etc.]
- Severity: [Mild, moderate, severe, if specified]
- Ongoing symptoms: [Describe if ongoing; e.g., headaches, dizziness, difficulty walking]

**3. Medical Treatment Received**
- Medical Visits: [e.g., ER visit, urgent care, consultation with specialist]
- Diagnoses: [e.g., concussion, fractured wrist]
- Treatment Plan: [e.g., prescribed medication, physical therapy]
- Dates of Treatment: [List if available]

**4. Insurance Information**
- Your Insurance Company: [Name, policy number if given]
- Claim Filed: [Yes/No; claim number if provided]
- Other Party’s Insurance: [Name, policy number if available; claim filed yes/no]
  
**5. Witness Information**
- Contact Details: [Names & phone numbers/emails of any witnesses if provided]
- Brief Account (if they provided a statement): [e.g., "Saw other vehicle run red light"]

**6. Photos or Videos**
- Photos/Videos Taken: [Yes/No]
- Type: [e.g., scene, vehicle damage, injuries]
- How to Access: [Provided copies, will email, etc.]""",
            mcp_servers=[mcp_server]
        )

        result = await Runner.run(chat_agent, question)
        return result.final_output
    finally:
        # Clean up the connection
        await mcp_server.cleanup()

  # Example usage
async def main():
    user_question = "What information did you collect from the client"
    response = await chat(user_question)
    print(response)

# Run the chat
await main()

from agents import Agent, Runner
import os
from google.colab import userdata

# Get the OpenAI API key from Colab's user data
openai_api_key = userdata.get('OpenAI')

# Set the OpenAI API key as an environment variable
os.environ["OPENAI_API_KEY"] = openai_api_key

# Document Verifying Agent
document_verifying_agent = Agent(
    name="DocumentVerifyingAgent",
    instructions="""
    You are a Document Verifying Agent who makes sure that all required documents are signed and uploaded three days before consultation appointment so that professional can review.

    Guidelines:
    1. Count and make sure that all required documents are signed
    2. If they are signed and completed, hand off to Case Preparation Agent
    3. If they are not signed, hand off to Email Agent to reach out to customer to fulfill outstanding requirements

    Remember that individual clients often value simplicity and clarity in their case files.
    """
)

# Test the Document Verifying Agent
async def test_document_verifying_agent(): # Renamed function
    result = await Runner.run(document_verifying_agent, "Your documents are being reviewed by our team, we will reach out before your consultation if there are any further requirements. Thank you.") # Changed agent to document_verifying_agent
    print("Document Verifying Agent Response:")
    print(result.final_output)
    print("\n" + "-"*50 + "\n")

await test_document_verifying_agent()

!pip install openai-agents -q
from agents import Agent, Runner
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import os
from google.colab import userdata

# Get the OpenAI API key from Colab's user data
openai_api_key = userdata.get('OpenAI')

# Set the OpenAI API key as an environment variable
os.environ["OPENAI_API_KEY"] = openai_api_key

# Calendar Management Agent
calendar_management_agent = Agent(
    name="CalendarManagementAgent",
    instructions="""
    You are a Calendar Management Agent. Your role is to schedule a consultation with chosen lawyer based on their availability.

    Guidelines:
    1. Only schedule appointments with customers who are able to answer majority of the questions the Note Taking Agent requests
    2. Do not schedule an appointment during an occupied time slot.
    3. Refer to Google Calendar to gain access to the calendar of all lawyers.
    4. Do not cancel any appointments.


    Remember that customers would prefer an appointment sooner rather than later so schedule for next available time slot.
    """
)

class CalendarManagementAgent:
    def __init__(self, lawyer_calendar_id, credentials: Credentials):
        """
        :param lawyer_calendar_id: the Google Calendar ID (email or calendarId) for the lawyer
        :param credentials: valid Google credentials for that calendar
        """
        self.calendar_id = lawyer_calendar_id
        self.creds = credentials
        self.service = build("calendar", "v3", credentials=self.creds)

    def is_slot_free(self, start_dt: datetime, end_dt: datetime) -> bool:
        """Check if the slot [start_dt, end_dt) is free on the lawyer's calendar."""
        req_body = {
            "timeMin": start_dt.isoformat(),
            "timeMax": end_dt.isoformat(),
            "timeZone": start_dt.tzinfo.zone if start_dt.tzinfo else "UTC",
            "items": [{"id": self.calendar_id}]
        }
        resp = self.service.freebusy().query(body=req_body).execute()
        busy = resp["calendars"][self.calendar_id]["busy"]
        return (len(busy) == 0)

    def find_next_available_slot(self, duration_minutes=30, look_ahead_days=7) -> datetime:
        """Find the next available slot from now onward for the lawyer."""
        now = datetime.now(timezone.utc)
        # Round up to next half hour
        minute = now.minute
        if minute % duration_minutes != 0:
            now = now + timedelta(minutes=(duration_minutes - (minute % duration_minutes)))
        end_search = now + timedelta(days=look_ahead_days)

        slot = now
        delta = timedelta(minutes=duration_minutes)

        while slot < end_search:
            slot_end = slot + delta
            if self.is_slot_free(slot, slot_end):
                return slot
            slot += delta

        return None  # no free slot found

    def schedule_appointment(self, customer_name: str, customer_email: str,
                              start_dt: datetime, duration_minutes=30, summary="Consultation"):
        """Schedule the event on the lawyer’s calendar."""
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        event = {
            "summary": summary,
            "description": f"Consultation with customer {customer_name}",
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": start_dt.tzinfo.zone if start_dt.tzinfo else "UTC",
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": end_dt.tzinfo.zone if end_dt.tzinfo else "UTC",
            },
            "attendees": [
                {"email": customer_email},
            ],
            # optional: send updates etc.
        }
        created = (self.service.events()
                   .insert(calendarId=self.calendar_id, body=event, sendUpdates="all")
                   .execute())
        return created

# Usage within your existing Agent logic

# Test the Calendar Management Agent
async def test_calendar_management_agent():
    result = await Runner.run(calendar_management_agent, "I scheduled your consultation at (time) on (date). We are looking forward to serving you then. Have a nice day.")
    print("Calendar Management Agent Response:")
    print(result.final_output)
    print("\n" + "-"*50 + "\n")

await test_calendar_management_agent()

from agents import Agent, Runner
from agents.mcp import MCPServerSse
import asyncio

# Define a function to chat with the agent
async def chat(question):
    # Connect to your MCP server
    mcp_server = MCPServerSse(
        params={
            "url": "https://vanessagomez.app.n8n.cloud/mcp/gcal"
        },
        cache_tools_list=True
    )

    # Connect to the server
    await mcp_server.connect()

    try:
        # Define the conversational agent with vector store access
        chat_agent = Agent(
            name="Calendar Assistant",
            instructions="""You are a helpful assistant that can search and retrieve information using MCP for my google calendar.
            When users ask questions, use the available tools to do CRUD operations for the calendar.
            Provide clear, helpful answers based on the information you find.""",
            mcp_servers=[mcp_server]
        )

        result = await Runner.run(chat_agent, question)
        return result.final_output
    finally:
        # Clean up the connection
        await mcp_server.cleanup()

  # Example usage
async def main():
    user_question = "Tell me about the events I have on my calendar specically on the day of Oct 13 2025"
    response = await chat(user_question)
    print(response)

# Run the chat
await main()

# Case Preparation Agent
case_preparation_agent = Agent(
    name="CasePreparationAgent",
    instructions="""
    You are a Case Preparation Agent who prepares the internal case file automatically based on the intake data

    Guidelines:
    1. Organize structured case file (PDF, CRM entry, or internal system)
    2. Provide customer of a summary for attorney review before consultation
    3. Inform customer of missing legal documents and its urgency as needed before scheduled consultation

    Remember that individual clients often value simplicity and clarity in their case files.
    """
)

# Test the Case Preparation Agent
async def test_case_preparation_agent():
    result = await Runner.run(case_preparation_agent, "Your case has been set up within our law firm. If there are any other documents needed by our lawyers, we will reach out before your consultation. Thank you.")
    print("Case Preparation Agent Response:")
    print(result.final_output)
    print("\n" + "-"*50 + "\n")

await test_case_preparation_agent()
