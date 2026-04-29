from langgraph.graph import StateGraph

from graph.state import GraphState
from graph.agent_node import agent_node


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("agent", agent_node)
    builder.set_entry_point("agent")

    return builder.compile()


app = build_graph()
