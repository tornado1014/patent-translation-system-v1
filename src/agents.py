from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from .schemas import AgentState, AnalysisResult, ReviewResult
import json
from dotenv import load_dotenv

# Load environment variables from .env file at the earliest point
load_dotenv()

# Initialize the Gemini models
llm_pro = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

def analyst_node(state: AgentState):
    """
    Analyzes the source text to extract domain and key terminology.
    """
    print("--- Running Analyst Node ---")
    parser = JsonOutputParser(pydantic_object=AnalysisResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a specialized patent analyst. Your task is to analyze the patent text and extract its technical domain and key terms. Respond with a JSON object that strictly follows this format:\n{format_instructions}"),
        ("user", "Please analyze the following text:\n\n{original_text}"),
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
    term_mapping_str = json.dumps(term_mapping, ensure_ascii=False, indent=2)

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert translator specializing in English-to-Korean patent translations for the '{{domain}}' domain.
You MUST adhere to the following terminology map. Do not deviate from it.
{{term_mapping}}
Translate the following patent document text into Korean, ensuring accuracy and maintaining the formal tone and structure of a patent document."""),
        ("user", "{original_text}"),
    ]).partial(domain=domain, term_mapping=term_mapping_str)
    
    chain = prompt | llm_pro
    result = chain.invoke({"original_text": state["original_text"]})
    
    return {"draft_translation": result.content}


def reviewer_node(state: AgentState):
    """
    Reviews the translated text for errors and consistency.
    """
    print("--- Running Reviewer Node ---")
    parser = JsonOutputParser(pydantic_object=ReviewResult)
    
    reviewer_llm = llm_flash if state.get("use_flash_review") else llm_pro

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a meticulous QA reviewer for patent translations. Compare the original text with the translation and identify critical errors. Respond with a JSON object that strictly follows this format:\n{format_instructions}"),
        ("user", """**Original English Text:**
{original_text}

**Korean Translation Draft:**
{draft_translation}

**Key Terminology Map to Verify:**
{analysis_result}

Please provide your review."""),
    ])
    
    chain = prompt | reviewer_llm | parser
    result = chain.invoke({
        "original_text": state["original_text"],
        "draft_translation": state["draft_translation"],
        "analysis_result": json.dumps(state["analysis_result"], ensure_ascii=False, indent=2),
        "format_instructions": parser.get_format_instructions(),
    })
    
    return {"review_result": result}
