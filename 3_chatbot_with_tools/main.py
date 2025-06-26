import os
import sys
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END      # **`UPDATE`**
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt.tool_node import ToolNode
from langchain_tavily import TavilySearch       # **`NEW`**

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
        
        ### Create an in-memory checkpointer ###
        ## (For Production, recommend using 'SqlliteSaver' or 'PostgresSaver' and connect to database.) ##
        self.memory = MemorySaver()
        
        ### Pick a thread to use a the key for the conversation ###
        self.config = {"configurable": {"thread_id": "1"}}
        
        ### Define the web search tool ###
        search_tool = TavilySearch(max_results=2)      # **`NEW`**
        self.available_tools = [search_tool]
        
        ### Tell the LLM which tools it can call ###
        self.llm = self.llm.bind_tools(tools=self.available_tools)  # **`NEW`**
        
        ### Define a ToolNode that runs the tools in the last AIMessage ###
        ## (The Node checks the most recent message in the state and calls tools if the message contains tool_calls.)
        ## (It relies on the LLM's tool_calling support, which is available in Anthropic, OpenAI, Google Gemini, and a number of other LLM providers.)
        self.tool_node = ToolNode(tools=self.available_tools)       # **`NEW`**
        
        self.graph_builder = StateGraph(State)        
        self.graph_builder.add_node("chatbot", self.chatbot)
        self.graph_builder.add_node("tools", self.tool_node)        # **`NEW`**
        
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("tools", "chatbot")     # **`NEW`**
        self.graph_builder.add_conditional_edges(           # **`NEW`**
            "chatbot",
            self.route_tools,
            # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
            {"tools": "tools", END: END}
        )
        
        ### Compile the graph with the provided checkpointer, which will checkpoint the 'State' as the graph works through each node ###
        self.graph = self.graph_builder.compile(checkpointer=self.memory)
        
    def chatbot(self, state: State):
        return {"messages": [self.llm.invoke(state["messages"])]}
    
    # **`NEW FUNCTION`**
    ### The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
    ### it is fine directly responding. This conditional routing defines the main agent loop.
    def route_tools(self, state:State):
        """
            Use in the conditional_edge to route to the ToolNode if the last message
            has tool calls. Otherwise, route to the end.
        """
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages:= state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError("No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END

    def stream_graph_updates(self, user_input: str):
        for event in self.graph.stream({"messages": [{"role": "user", "content": user_input}]}, self.config):
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
    
