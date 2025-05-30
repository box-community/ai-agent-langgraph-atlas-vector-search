import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage
from langgraph.graph.state import CompiledStateGraph
from typing import Dict, List
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient

from c_agent_demo import get_llm_with_tools, get_tools

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")


# Define the graph state
class GraphState(TypedDict):
    messages: Annotated[list, add_messages]


# Define the agent node function
def agent(state: GraphState) -> Dict[str, List]:
    """
    Agent node
    Args:
        state (GraphState): Graph state
    Returns:
        Dict[str, List]: Updates to messages
    """
    llm_with_tools = get_llm_with_tools()
    # Get the messages from the graph `state`
    messages = state["messages"]
    # Invoke `llm_with_tools` with `messages`
    result = llm_with_tools.invoke(messages)
    # Write `result` to the `messages` attribute of the graph state
    return {"messages": [result]}


# Define the tools node function
def tools_node(state: GraphState) -> Dict[str, List]:
    tools = get_tools()
    # Create a map of tool name to tool call
    tools_by_name = {tool.name: tool for tool in tools}

    result = []
    # Get the list of tool calls from messages
    tool_calls = state["messages"][-1].tool_calls
    # Iterate through `tool_calls`
    for tool_call in tool_calls:
        # Get the tool from `tools_by_name` using the `name` attribute of the `tool_call`
        tool = tools_by_name[tool_call["name"]]
        # Invoke the `tool` using the `args` attribute of the `tool_call`
        observation = tool.invoke(tool_call["args"])
        # Append the result of executing the tool to the `result` list as a ToolMessage
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    # Write `result` to the `messages` attribute of the graph state
    return {"messages": result}


def execute_graph(thread_id: str, user_input: str, app: CompiledStateGraph) -> None:
    config = {"configurable": {"thread_id": thread_id}}
    input = {
        "messages": [
            (
                "user",
                user_input,
            )
        ]
    }
    for output in app.stream(input, config):
        for key, value in output.items():
            print(f"Node {key}:")
            print(value)

    print("\n---FINAL ANSWER---")
    print(value["messages"][-1].content)


# Define a conditional edge
def route_tools(state: GraphState):
    """
    Uses a conditional_edge to route to the tools node if the last message
    has tool calls. Otherwise, route to the end.
    """
    # Get messages from graph state
    messages = state.get("messages", [])
    if len(messages) > 0:
        # Get the last AI message from messages
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")

    # Check if the last message has tool calls
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


def get_compiled_graph() -> CompiledStateGraph:
    """
    Main function to execute the graph.
    """

    # Instantiate the graph
    graph = StateGraph(GraphState)

    # Add "agent" node using the `add_node` function
    graph.add_node("agent", agent)

    # Add "tools" node using the `add_node` function
    graph.add_node("tools", tools_node)

    # Add an edge from the START node to the `agent` node
    graph.add_edge(START, "agent")

    # Add a conditional edge from the `agent` node to the `tools` node
    graph.add_conditional_edges(
        "agent",
        route_tools,
        {"tools": "tools", END: END},
    )

    # Add an edge from the `tools` node to the `agent` node
    graph.add_edge("tools", "agent")

    # Initialize a MongoDB check_pointer
    client = MongoClient(MONGODB_URI)
    check_pointer = MongoDBSaver(client)
    # Instantiate the graph with the checkpointer
    return graph.compile(checkpointer=check_pointer)


def main() -> None:
    app = get_compiled_graph()
    execute_graph("001", "What are the biggest challenges facing tech companies?", app)
    execute_graph("001", "What earnings reports has a comment from Brett Iversen?", app)


if __name__ == "__main__":
    main()
