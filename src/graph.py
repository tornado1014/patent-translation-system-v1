from langgraph.graph import StateGraph, END
from .agents import analyst_node, translator_node, reviewer_node
from .schemas import AgentState

def decide_to_end(state: AgentState):
    """
    Decision node to determine if the review passed.
    """
    if state["review_result"] and state["review_result"].get("passed"):
        print("--- Review Passed. Finalizing Translation. ---")
        return "end"
    else:
        print("--- Review Failed. Returning to Translator. ---")
        return "translate"

# Define the graph
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("analyze", analyst_node)
workflow.add_node("translate", translator_node)
workflow.add_node("review", reviewer_node)

# Set the entrypoint
workflow.set_entry_point("analyze")

# Add edges
workflow.add_edge("analyze", "translate")
workflow.add_edge("translate", "review")

# Add conditional edge from review
workflow.add_conditional_edges(
    "review",
    decide_to_end,
    {
        "end": END,
        "translate": "translate",
    }
)

# Compile the graph
app = workflow.compile()
