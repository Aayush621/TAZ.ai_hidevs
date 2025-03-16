from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os

from typing import List, Optional
import uuid
# Load environment variables
load_dotenv()

# Set up the FastAPI app
app = FastAPI(title="Travel Agent API", description="API for interacting with a travel planning assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set environment variables
def set_env(name: str):
    env_value = os.getenv(name)
    if env_value is None:
        raise ValueError(f"Environment variable {name} is not set.")
    os.environ[name] = env_value

# Set required environment variables
set_env("GROQ_API_KEY")

# Initialize the LLM
llm = ChatGroq(
    model_name="llama3-70b-8192",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0,
    streaming=False,  # Set to False for API use
)

# Define system prompt
system_prompt = """
You are a travel agent that plans trips for users entirely.
You help users plan trips by providing detailed itineraries, flight options, accommodation recommendations,
and activities based on their preferences and budget.

Your process should be:
1. First, understand the basic travel request (destinations, dates if provided)
2. Ask the user about their specific activity interests and preferences
3. Only after receiving their preferences, create a complete itinerary including:
   - Flight options and travel time
   - Accommodation options
   - Must-see attractions and activities tailored to their interests
   - Estimated budget

Always ask for activity preferences before providing the final itinerary.
"""

# Create prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

def travel_planner(query):
    """Plan a trip based on user query."""
    formatted_prompt = prompt_template.format_messages(input=query)
    response = llm.invoke(formatted_prompt)
    return response.content

# Define tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "travel_planner",
            "description": "Plan a trip based on user's requirements. Always ask for activity preferences before providing the final itinerary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's travel query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Create the agent
agent = create_react_agent(llm, [travel_planner], checkpointer=MemorySaver())

# Store active conversations
active_conversations = {}

# Pydantic models for request and response
class Message(BaseModel):
    role: str
    content: str

class ConversationRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ConversationResponse(BaseModel):
    conversation_id: str
    response: str
    messages: List[Message]

@app.post("/travel/chat", response_model=ConversationResponse)
async def chat(request: ConversationRequest):
    """
    Chat with the travel agent.
    
    - If no conversation_id is provided, a new conversation will be started.
    - If a conversation_id is provided, the message will be added to that conversation.
    """
    # Get or create conversation ID
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Get or initialize conversation history
    if conversation_id not in active_conversations:
        active_conversations[conversation_id] = [("user", request.message)]
    else:
        active_conversations[conversation_id].append(("user", request.message))
    
    # Prepare input for the agent
    inputs = {"messages": active_conversations[conversation_id]}
    config = {"configurable": {"thread_id": conversation_id}}
    
    # Get response from agent
    result = None
    for s in agent.stream(inputs, config, stream_mode="values"):
        result = s
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to get response from agent")
    
    # Update conversation history with agent's response
    last_message = result["messages"][-1]
    if isinstance(last_message, tuple):
        role, content = last_message
    else:
        role, content = "assistant", last_message.content
    
    active_conversations[conversation_id] = result["messages"]
    
    # Format messages for response
    formatted_messages = []
    for msg in active_conversations[conversation_id]:
        if isinstance(msg, tuple):
            role, content = msg
        else:
            role, content = "assistant", msg.content
        formatted_messages.append(Message(role=role, content=content))
    
    # Return response
    return ConversationResponse(
        conversation_id=conversation_id,
        response=content,
        messages=formatted_messages
    )

@app.get("/travel/conversations/{conversation_id}", response_model=List[Message])
async def get_conversation(conversation_id: str):
    """Get the full conversation history for a given conversation ID."""
    if conversation_id not in active_conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    formatted_messages = []
    for msg in active_conversations[conversation_id]:
        if isinstance(msg, tuple):
            role, content = msg
        else:
            role, content = "assistant", msg.content
        formatted_messages.append(Message(role=role, content=content))
    
    return formatted_messages

@app.delete("/travel/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if conversation_id not in active_conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    del active_conversations[conversation_id]
    return {"status": "success", "message": "Conversation deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)