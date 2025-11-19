"""
문서 분석 모듈
- 기술 분야 자동 식별
- 핵심 용어 자동 추출
- 반복 패턴 감지
"""

import re
import json
import os
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class DocumentAnalyzer:
    """특허 문서 분석기"""

    def __init__(self, 
                 terminology_path: str = "config/terminology.json",
                 api_config_path: str = "config/api_config.yaml"):
        self.terminology_path = Path(terminology_path)
        self.terminology = self._load_terminology()

        # API 키 및 모델 설정
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY 환경 변수를 설정해야 합니다.")
        genai.configure(api_key=api_key)

        with open(api_config_path, 'r', encoding='utf-8') as f:
            api_config = yaml.safe_load(f)
        
        google_config = api_config.get("google", {})
        model_name = google_config.get("model", "gemini-2.5-flash")
        
        self.model = genai.GenerativeModel(model_name)
        self.generation_config = genai.types.GenerationConfig(
            max_output_tokens=google_config.get("max_output_tokens", 8192),
            temperature=google_config.get("temperature", 0.0)
        )

    def _load_terminology(self) -> Dict:
        """용어집 로드"""
        with open(self.terminology_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def identify_domain(self, text: str) -> str:
        """기술 분야 식별"""
        domain_keywords = {
            "electronics_semiconductor": ["substrate", "layer", "semiconductor", "wafer", "transistor", "chip", "circuit"],
            "chemistry_pharma": ["compound", "molecule", "pharmaceutical", "drug", "synthesis", "reaction", "chemical"],
            "mechanical": ["distal", "proximal", "apparatus", "device", "mechanical", "housing"],
            "biotech": ["protein", "cell", "antibody", "gene", "DNA", "RNA", "biological"]
        }
        text_lower = text.lower()
        scores = {domain: sum(1 for kw in keywords if kw in text_lower) for domain, keywords in domain_keywords.items()}
        return max(scores, key=scores.get) if max(scores.values()) > 0 else "general"

    def extract_technical_terms(self, text: str, top_n: int = 20) -> List[Tuple[str, int]]:
        """핵심 기술 용어 추출"""
        patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            r'\b(?:substrate|layer|compound|method|device|system|apparatus)\b',
        ]
        terms = [match for pattern in patterns for match in re.findall(pattern, text)]
        term_counts = Counter(terms)
        stopwords = {'The', 'A', 'An', 'In', 'Of', 'And', 'Or', 'To', 'For', 'With', 'By', 'At'}
        filtered_terms = [(term, count) for term, count in term_counts.most_common(top_n * 2) if term not in stopwords and len(term) > 2]
        return filtered_terms[:top_n]

    def identify_patterns(self, text: str) -> List[str]:
        """반복 패턴 식별"""
        patterns = {
            "comprising": r"comprising\s+[A-Za-z,\s]+", "wherein": r"wherein\s+[^.;]+",
            "selected from": r"selected\s+from\s+[^.;]+", "consisting of": r"consisting\s+of\s+[^.;]+"
        }
        found_patterns = [f"{name}: {len(matches)}회 출현" for name, pattern in patterns.items() if len(matches := re.findall(pattern, text, re.IGNORECASE)) >= 2]
        return found_patterns

    def analyze_with_gemini(self, text: str, domain: str) -> Dict:
        """Gemini API를 사용한 심층 분석"""
        prompt = f"""You are a patent translation expert analyzing an English patent document.

Domain identified: {domain}

Analyze the following text and provide:
1. Top 20 key technical terms that should be translated consistently.
2. The document type (claim, specification, or abstract).
3. Important phrases that repeat 3 or more times.
4. Suggested Korean terminology for domain-specific terms based on the identified domain: {domain}.

Text to analyze:
---
{text[:4000]}
---

Provide your analysis in a structured JSON format. The JSON output should be clean, without any surrounding text or markdown.

Example JSON structure:
{{
  "key_terms": ["term1", "term2", ...],
  "document_type": "claim",
  "repeated_phrases": ["phrase1", "phrase2", ...],
  "domain_specific_terms": {{
    "english_term_1": "korean_translation_1",
    "english_term_2": "korean_translation_2"
  }}
}}
"""
        try:
            response = self.model.generate_content(prompt, generation_config=self.generation_config)
            # Gemini 응답에서 JSON만 정리하여 추출
            clean_json_str = re.search(r'\{.*\}', response.text, re.DOTALL)
            if clean_json_str:
                return json.loads(clean_json_str.group())
            return {}
        except Exception as e:
            print(f"Gemini 분석 오류: {e}")
            return {}

    def analyze(self, text: str, use_ai: bool = True) -> Dict:
        """전체 문서 분석"""
        print("📊 문서 분석 중...")
        domain = self.identify_domain(text)
        print(f"   ✓ 도메인 식별: {domain}")
        technical_terms = self.extract_technical_terms(text)
        print(f"   ✓ 기술 용어 추출: {len(technical_terms)}개")
        patterns = self.identify_patterns(text)
        print(f"   ✓ 반복 패턴: {len(patterns)}개")

        ai_analysis = {}
        if use_ai:
            print("   ⏳ Gemini AI 심층 분석 중...")
            ai_analysis = self.analyze_with_gemini(text, domain)
            print("   ✓ Gemini 분석 완료")

        term_mapping = self._build_term_mapping(technical_terms, domain, ai_analysis)
        
        result = {
            "domain": domain, "technical_terms": technical_terms, "patterns": patterns,
            "ai_analysis": ai_analysis, "term_mapping": term_mapping
        }
        print("✅ 문서 분석 완료\n")
        return result

    def _build_term_mapping(self, technical_terms: List[Tuple[str, int]],
                           domain: str, ai_analysis: Dict) -> Dict[str, str]:
        """용어 매핑 구축"""
        mapping = {}
        domain_terms = self.terminology.get("domain_terms", {}).get(domain, {})
        mapping.update(domain_terms)
        
        general_terms = self.terminology.get("domain_terms", {}).get("general", {})
        for term, _ in technical_terms:
            term_lower = term.lower()
            if term_lower in general_terms:
                mapping[term] = general_terms[term_lower]

        if ai_analysis and "domain_specific_terms" in ai_analysis:
            ai_terms = ai_analysis["domain_specific_terms"]
            for eng, kor in ai_terms.items():
                if eng not in mapping:
                    mapping[eng] = kor
        return mapping

if __name__ == "__main__":
    analyzer = DocumentAnalyzer()
    sample_text = """
    A method for characterizing a protein, comprising:
    obtaining a protein sample; preparing said sample for spectroscopy;
    subjecting said sample to an experiment;
    eliminating noise from empty areas of a resulting spectrum;
    and analyzing the spectrum to characterize the protein.
    """
    result = analyzer.analyze(sample_text, use_ai=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
