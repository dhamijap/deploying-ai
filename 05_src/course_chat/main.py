from langgraph.graph import StateGraph, MessagesState, START
from langchain.chat_models import init_chat_model
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langchain_core.messages import SystemMessage,  HumanMessage

from dotenv import load_dotenv
import json
import requests
import os

from course_chat.prompts import return_instructions
from course_chat.tools_animals import get_cat_facts, get_dog_facts
from course_chat.tools_horoscope import get_horoscope
from course_chat.tools_music import recommend_albums
from utils.logger import get_logger


_logs = get_logger(__name__)
load_dotenv(".env")
load_dotenv(".secrets")


# chat_agent = init_chat_model(
#     "openai:gpt-4o-mini",
#     api_key=os.getenv("OPENAI_API_KEY"),  # Your tunneled key
#     base_url=os.getenv('https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1'),  # Your AWS tunnel endpoint
# )

from langchain_openai import ChatOpenAI

chat_agent = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key="dummy",
    openai_api_base="https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
    default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')}
)


tools = [get_cat_facts, get_dog_facts, recommend_albums, get_horoscope]

instructions = return_instructions()



# @traceable(run_type="llm")
def call_model(state: MessagesState):
    """LLM decides whether to call a tool or not"""
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
    for human, assistant in history:
        messages.append(HumanMessage(content=human))
        if assistant:
            messages.append({"role": "assistant", "content": assistant})
    
    # Add current message
    messages.append(HumanMessage(content=message))
    
    # Invoke the graph
    result = graph.invoke({"messages": messages})
    
    # Return the assistant's response
    return result["messages"][-1].content

if __name__ == "__main__":
    demo = gr.ChatInterface(
        fn=chat_interface,
        title="Course Chat Agent",
        description="Chat with an AI assistant that can tell you cat/dog facts, recommend music, and share horoscopes!",
        examples=[
            "Tell me a cat fact",
            "What's my horoscope for Aries?",
            "Recommend some albums",
            "Give me a dog fact"
        ],
        theme=gr.themes.Soft(),
    )
    
    demo.launch()