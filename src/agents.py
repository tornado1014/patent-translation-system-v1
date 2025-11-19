from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from .schemas import AgentState, AnalysisResult, ReviewResult
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file at the earliest point
load_dotenv()

# Initialize the Gemini models
llm_pro = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

def load_prompt(filename: str) -> PromptTemplate:
    """Loads a prompt template from a file."""
    prompt_path = Path(__file__).parent.parent / "prompts" / filename
    return PromptTemplate.from_template(prompt_path.read_text(encoding="utf-8"))

def analyst_node(state: AgentState):
    """
    Analyzes the source text to extract domain and key terminology.
    """
    print("--- Running Analyst Node ---")
    parser = JsonOutputParser(pydantic_object=AnalysisResult)
    
    system_prompt_template = load_prompt("analyst.prompt")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_template.template),
        ("user", "{original_text}"),
    ])
    
    chain = prompt | llm_pro | parser
    result = chain.invoke({
        "original_text": state["original_text"],
        "format_instructions": parser.get_format_instructions(),
    })
    
    return {"analysis_result": result}


def translator_node(state: AgentState):
    """
    Translates the source text based on the analysis.
    """
    print("--- Running Translator Node ---")
    
    analysis = state["analysis_result"]
    domain = analysis.get("domain", "general technology")
    term_mapping = analysis.get("term_mapping", {})
    
    system_prompt_template = load_prompt("translator.prompt")
    
    prompt = ChatPromptTemplate.from_template(system_prompt_template.template)
    
    chain = prompt | llm_pro
    result = chain.invoke({
        "document_type": state.get("document_type", "claim"),
        "domain": domain,
        "term_mapping": json.dumps(term_mapping, ensure_ascii=False, indent=2),
        "original_text": state["original_text"],
    })
    
    return {"draft_translation": result.content}


def reviewer_node(state: AgentState):
    """
    Reviews the translated text for errors and consistency.
    """
    print("--- Running Reviewer Node ---")
    parser = JsonOutputParser(pydantic_object=ReviewResult)
    
    reviewer_llm = llm_flash if state.get("use_flash_review") else llm_pro
    
    system_prompt_template = load_prompt("reviewer.prompt")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_template.template),
        ("user", """**Original English:**
`{original_text}`

**Korean Translation:**
`{draft_translation}`

**Terminology Map Used:**
`{analysis_result}`"""),
    ])
    
    chain = prompt | reviewer_llm | parser
    result = chain.invoke({
        "original_text": state["original_text"],
        "draft_translation": state["draft_translation"],
        "analysis_result": json.dumps(state["analysis_result"], ensure_ascii=False, indent=2),
        "format_instructions": parser.get_format_instructions(),
    })
    
    return {"review_result": result}
