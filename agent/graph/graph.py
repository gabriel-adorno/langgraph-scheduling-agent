from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from agent.states.all_states import AgentState
from agent.tools.all_tools import all_tools
from agent.nodes.agent_node import agent
from agent.nodes.tool_executer_node import tool_executer
from agent.nodes.update_step_node import update_step
from agent.nodes.reset_state_node import reset_state
from agent.utils.functions import should_use_tool

memory = MemorySaver()

graph = StateGraph(AgentState)

graph.add_node("agent", agent)
graph.add_node("tool", ToolNode(all_tools))
graph.add_node("tool_executer", tool_executer)
graph.add_node("update_step", update_step)
graph.add_node("reset_state", reset_state)

graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_use_tool,
    {
        "tool_edge": "tool",
        "end_edge": END
    }
)
graph.add_edge("tool", "tool_executer")
graph.add_edge("tool_executer", "update_step")
graph.add_edge("update_step", "agent")
graph.add_edge("agent", "reset_state")
graph.add_edge("reset_state", END)

app = graph.compile()
