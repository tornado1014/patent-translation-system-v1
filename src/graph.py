from langgraph.graph import StateGraph, END
from .agents import analyst_node, translator_node, reviewer_node, tm_search_node, tm_save_node
from .schemas import AgentState

def decide_on_tm_match(state: AgentState):
    """Decision node to check if a TM match was found."""
    if state.get("tm_match_found"):
        return "end_with_tm"
    else:
        return "translate"

def decide_after_review(state: AgentState):
    """Decision node after the review step."""
    if state["review_result"] and state["review_result"].get("passed"):
        print("--- Review Passed. Proceeding to save to TM. ---")
        return "save_to_tm"
    else:
        print("--- Review Failed. Returning to Translator. ---")
        return "translate"

# Define the graph
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("analyze", analyst_node)
workflow.add_node("tm_search", tm_search_node)
workflow.add_node("translate", translator_node)
workflow.add_node("review", reviewer_node)
workflow.add_node("save_to_tm", tm_save_node)

# Set the entrypoint
workflow.set_entry_point("analyze")

# Add edges
workflow.add_edge("analyze", "tm_search")
workflow.add_edge("translate", "review")
workflow.add_edge("save_to_tm", END)

# Conditional edge after TM search
workflow.add_conditional_edges(
    "tm_search",
    decide_on_tm_match,
    {
        "end_with_tm": END,
        "translate": "translate",
    }
)

# Conditional edge after review
workflow.add_conditional_edges(
    "review",
    decide_after_review,
    {
        "save_to_tm": "save_to_tm",
        "translate": "translate",
    }
)

# Compile the graph
app = workflow.compile()
