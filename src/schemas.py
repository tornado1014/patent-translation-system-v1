from pydantic import BaseModel, Field
from typing import Dict, TypedDict, Annotated, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Represents the state of our multi-agent system.
    """
    original_text: str
    document_type: str
    use_flash_review: bool
    analysis_result: dict
    draft_translation: str
    review_result: dict
    final_translation: str
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]


class AnalysisResult(BaseModel):
    """Pydantic model for the output of the Analyst node."""
    domain: str = Field(description="The main technical field of the patent.")
    term_mapping: Dict[str, str] = Field(description="A dictionary of key technical terms and their definitions.")

class ReviewResult(BaseModel):
    """Pydantic model for the output of the Reviewer node."""
    passed: bool = Field(description="True if the translation has no critical errors, False otherwise.")
    feedback: str = Field(description="Detailed feedback on any errors found, or a confirmation of success.")
