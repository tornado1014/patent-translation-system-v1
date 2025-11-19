from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from .schemas import AgentState, AnalysisResult, ReviewResult
from .tm_manager import TranslationMemory
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

def tm_search_node(state: AgentState):
    """
    Searches the Translation Memory for existing translations.
    """
    print("--- Running TM Search Node ---")
    tm = TranslationMemory()
    analysis = state["analysis_result"]
    domain = analysis.get("domain", "general")
    
    matches = tm.search(state["original_text"], domain=domain, similarity_threshold=1.0)
    tm.close()
    
    if matches and matches[0]["similarity"] == 1.0:
        print(f"--- Found 100% match in TM. Skipping translation. ---")
        return {
            "final_translation": matches[0]["target"],
            "tm_match_found": True
        }
    else:
        print("--- No exact match found in TM. Proceeding to translation. ---")
        return {"tm_match_found": False}

def tm_save_node(state: AgentState):
    """
    Saves the final translation to the Translation Memory.
    """
    print("--- Running TM Save Node ---")
    tm = TranslationMemory()
    
    # Only save if the review passed and it was a new translation
    if state.get("review_result", {}).get("passed") and not state.get("tm_match_found"):
        analysis = state["analysis_result"]
        domain = analysis.get("domain", "general")
        
        tm.add(
            source=state["original_text"],
            target=state["draft_translation"],
            domain=domain,
            document_type=state.get("document_type", "claim"),
            quality_score=10 # Assuming perfect score after passing review
        )
        print("--- Saved new translation to TM. ---")
    
    tm.close()
    
    # This node doesn't modify the main state path, just performs an action.
    # We set final_translation here if it came from the translator path.
    return {"final_translation": state.get("draft_translation")}
