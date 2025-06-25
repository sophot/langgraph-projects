import os
import sys
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

class ChatBotAgent:
    def __init__(self):
        self.llm = init_chat_model(model="google_genai:gemini-2.0-flash")
        # self.llm = init_chat_model(model="google_genai:gemini-2.5-flash")
        
        self.graph_builder = StateGraph(State)        
        self.graph_builder.add_node("chatbot", self.chatbot)
        self.graph_builder.add_edge(START, "chatbot")
        
        self.graph = self.graph_builder.compile()
        
    def chatbot(self, state: State):
        return {"messages": [self.llm.invoke(state["messages"])]}

    def stream_graph_updates(self, user_input: str):
        for event in self.graph.stream({"messages": [{"role": "user", "content": user_input}]}):
            for value in event.values():
                print("Assistant:", value["messages"][-1].content)
                
    def run(self):
        while True:
            try:
                user_input = input("User: ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("goodbye!")
                    break
                self.stream_graph_updates(user_input=user_input)
        
            except KeyboardInterrupt:
                print("Received interrupt signal. Shutting down...")
                break
            except:
                user_input = "Tell me an interesting fact about Cambodia."
                print("User: ", user_input)
                self.stream_graph_updates(user_input=user_input)
                break
        

if __name__ == "__main__":
    cba = ChatBotAgent()
    cba.run()
    
