from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os

load_dotenv()

def set_env(name: str):
    env_value = os.getenv(name)
    if env_value is None:
        raise ValueError(f"Environment variable {name} is not set.")
    os.environ[name] = env_value


# Set required environment variables
set_env("GROQ_API_KEY")

llm = ChatGroq(
    model_name="llama3-70b-8192",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0,
    streaming=True,
)

# Define a proper system prompt
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

# Create a proper prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

def travel_planner(query):
    """Plan a trip based on user query."""
    # Create a proper prompt with the system message and user query
    formatted_prompt = prompt_template.format_messages(input=query)
    # Get response from LLM
    response = llm.invoke(formatted_prompt)
    return response.content

# Define tools properly
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

# Create the agent with the proper tools
agent = create_react_agent(llm, [travel_planner], checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "thread-1"}}

def print_stream(graph, inputs, config):
    collected_content = ""
    for s in graph.stream(inputs, config, stream_mode="values"):
        message = s["messages"][-1]
        if isinstance(message, tuple):
            # For user messages
            print(message)
        else:
            # For assistant messages, get the new content
            new_content = message.content
            
            # If we have collected content already, find what's new
            if collected_content:
                # Find the new part that was added
                if new_content.startswith(collected_content):
                    delta = new_content[len(collected_content):]
                    print(delta, end="", flush=True)
                else:
                    # Fallback if we can't determine the delta
                    print(new_content, end="", flush=True)
            else:
                # First chunk of content
                print(new_content, end="", flush=True)
            
            # Update our collected content
            collected_content = new_content
    
    # Print a newline at the end of the response
    if collected_content:
        print()

# Create a conversation loop to handle the multi-turn interaction
def run_conversation():
    print("Welcome to your Travel Planning Assistant!")
    user_message = input("How can I assist you with your travel plans: ")
    inputs = {"messages": [("user", user_message)]}
    
    # Optimize for faster initial response
    print("\nProcessing your request...", flush=True)
    
    while True:
        # Process the current message and stream the response
        result = None
        print("\nAssistant: ", end="", flush=True)  # Start the assistant message immediately
        
        for s in agent.stream(inputs, config, stream_mode="values"):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                continue  # Skip printing user messages during streaming
            
            # For assistant messages, stream the content
            current_content = message.content
            
            # If we have a previous result, find what's new
            if result and hasattr(result["messages"][-1], "content"):
                prev_content = result["messages"][-1].content
                if current_content.startswith(prev_content):
                    # Print only the new part
                    delta = current_content[len(prev_content):]
                    if delta:  # Only print if there's new content
                        print(delta, end="", flush=True)
                else:
                    # Fallback if we can't determine the delta
                    print(current_content, end="", flush=True)
            else:
                # First chunk of content
                print(current_content, end="", flush=True)
            
            result = s
        
        # Print a newline at the end of the response
        print()
        
        # Check if user wants to continue
        follow_up = input("\nDo you have more details to add? (Type your response or 'done' to finish): ")
        if follow_up.lower() == 'done':
            print("Thank you for using our Travel Planning Assistant!")
            break
        
        # Add the follow-up message to the conversation
        inputs = {"messages": result["messages"] + [("user", follow_up)]}

# Replace the single-turn interaction with the conversation loop
run_conversation()
