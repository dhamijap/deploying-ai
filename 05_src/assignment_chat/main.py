import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from assignment_chat.tools_science_facts import get_science_fact

from langgraph.graph import StateGraph, MessagesState, START
from langchain.chat_models import init_chat_model
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langchain_core.messages import AIMessage, SystemMessage,  HumanMessage

from dotenv import load_dotenv
import json
import requests
import os

from assignment_chat import tools_game_deals
from assignment_chat.prompts import return_instructions
from assignment_chat.tools_advice import get_advice
from assignment_chat.tools_music import recommend_albums
from assignment_chat.tools_game_deals import recommend_game
from utils.logger import get_logger
from langchain_openai import ChatOpenAI


_logs = get_logger(__name__)
load_dotenv(".env")
load_dotenv(".secrets")

# from langchain_google_genai import ChatGoogleGenerativeAI
# import google.generativeai as genai


# USE_GEMINI = True

# if USE_GEMINI:
#     from langchain_google_genai import ChatGoogleGenerativeAI
#     print("Open AI not working - using Google Gemini")
#     chat_agent = ChatGoogleGenerativeAI(
#         model="gemini-1.5-flash-latest",
#         version="v1",
#         google_api_key=os.getenv("GOOGLE_API_KEY")
#     )
# else:
#     print("Using OpenAI")
#     chat_agent = ChatOpenAI(
#         model="gpt-4o-mini",
#         openai_api_key="dummy",
#         openai_api_base="https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
#         default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')}
#     )

from assignment_chat.load_science_data import load_science_facts
import chromadb

# Auto-initialize ChromaDB collections if empty
def initialize_chromadb():
    """Check and load ChromaDB collections if needed"""
    try:
        chroma = chromadb.HttpClient(host="http://localhost:8000")
        
        # Check science_facts collection
        try:
            collection = chroma.get_collection("science_facts")
            count = collection.count()
            
            if count == 0:
                print("Science facts collection is empty. Loading data...")
                load_science_facts()
            else:
                print(f"Science facts loaded: {count} items")
        except:
            print("Science facts collection not found. Creating and loading...")
            load_science_facts()
            
    except Exception as e:
        print(f"ChromaDB initialization warning: {e}")

# Call at startup
initialize_chromadb()



from langchain_openai import ChatOpenAI
chat_agent = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key="dummy",
    openai_api_base="https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
    default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')}
)


tools = [get_advice, recommend_albums,recommend_game, get_science_fact]  # adding tools here 

instructions = return_instructions()

# @traceable(run_type="llm")
def call_model(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    
    # DEBUG: Print what's happening
    print(f"\n{'='*60}")
    print(f"🔄 call_model invoked")
    print(f"📊 Total messages in state: {len(state['messages'])}")
    print(f"📝 Last message: {state['messages'][-1].content[:80]}...")
    print(f"{'='*60}\n")
    ### end of debug code   

    
    response = chat_agent.bind_tools(tools).invoke( [SystemMessage(content=instructions)] + state["messages"])    
    return {
        "messages": [response]
    }

def get_graph():
    
    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_node(ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        tools_condition,
    )
    builder.add_edge("tools", "call_model")
    graph = builder.compile()
    return graph

import gradio as gr

def chat_interface(message, history):
    """Gradio chat function"""
    graph = get_graph()
    
    # Convert Gradio history to LangGraph messages
    messages = []
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    
    # Add current message
    messages.append(HumanMessage(content=message))
    
    # Invoke the graph
    result = graph.invoke({"messages": messages})
    
    # Return the assistant's response
    return result["messages"][-1].content

if __name__ == "__main__":
    demo = gr.ChatInterface(
        fn=chat_interface,
        title="Assigmment Chat Agent",
        type="messages",
        description="Chat with an AI assistant that can give you advice, can inform you about science misconceptions and science facts, and search and provide information about discounted games",
        examples=[
            "Tell me some advice",
            "Tell me an interesting science misconception",
            "What is the top game deal you can find for me right now?",
            "What are adventure games you can recommend that are on sale right now?",
        ],
        theme=gr.themes.Soft(),
    )
    
    demo.launch()
    
    
    