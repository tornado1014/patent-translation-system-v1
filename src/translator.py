"""
Gemini API 번역 엔진
- 구조화된 프롬프트 기반 번역
- 용어 일관성 강제
- 3단계 번역 프로세스 (분석 → 번역 → 검증)
"""

import os
import json
import re
import yaml
from typing import Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class PatentTranslator:
    """특허 번역 엔진"""

    def __init__(self, config_path: str = "config/api_config.yaml"):
        # API 키 설정
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY 환경 변수를 설정해야 합니다.")
        genai.configure(api_key=api_key)

        # API 설정 로드
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self.google_config = config.get("google", {})
        self.model_name = self.google_config.get("model", "gemini-2.5-flash")
        
        # GenerationConfig 설정
        self.generation_config = genai.types.GenerationConfig(
            max_output_tokens=self.google_config.get("max_output_tokens", 8192),
            temperature=self.google_config.get("temperature", 0.0),
            top_p=self.google_config.get("top_p", 1.0)
        )

        # GenerativeModel 인스턴스 생성
        self.model = genai.GenerativeModel(self.model_name)
        
    def set_model(self, model_name: str):
        """번역에 사용할 모델을 설정합니다."""
        print(f"모델을 {model_name}(으)로 변경합니다.")
        self.model_name = model_name
        self.model = genai.GenerativeModel(self.model_name)

    def build_translation_prompt(self,
                                 source_text: str,
                                 domain: str,
                                 term_mapping: Dict[str, str],
                                 document_type: str = "claim",
                                 previous_translation: Optional[str] = None) -> str:
        """번역 프롬프트 구축"""

        # 기본 프롬프트 (Gemini에 맞게 약간 수정)
        base_prompt = """당신은 12년 경력의 영한 특허 번역 전문가입니다.

**중요 지시사항**:
이 작업은 법률 문서 번역이므로, 자연스러움보다 **정확성과 일관성**이 최우선입니다.
창의적 표현 대신 기계적이더라도 완벽한 일관성을 유지해야 합니다.
동일한 영어 표현은 문맥과 무관하게 반드시 동일한 한국어로 번역되어야 합니다.

## 문서 정보
- **기술 분야**: {domain}
- **문서 유형**: {document_type}

## 필수 준수 용어집
아래 용어집을 **절대적으로** 준수하십시오. 이 세션 동안 절대 변경해서는 안 됩니다.

| 영어 | 한국어 | 비고 |
|---|---|---|
{term_table}

## 번역 원칙 (우선순위 순)
1.  **용어 일관성**: 동일 영어 = 동일 한국어 (예외 없음)
2.  **스타일 가이드 준수**: 특허 언어 규칙 준수
3.  **문법 정확성**: 한국어 문법 준수
4.  **자연스러움**: 위 3가지 원칙을 모두 지키는 범위 내에서만 허용

## 청구항 번역 시 필수 규칙
- 완전한 명사구로 종결해야 합니다. (예: "~를 포함하는 방법.", "~인 장치.")
- 반드시 마침표로 종결해야 합니다.
- 선행사가 있는 명사(예: the compound)는 반드시 "상기"를 붙여 번역해야 합니다. (예: 상기 화합물)
- `comprising`은 "포함하는"으로 번역합니다. ("구비하는" 사용 금지)
- `wherein`은 "여기서" 또는 화학식 뒤에서는 "상기 식에서"로 번역합니다.

{previous_context}

---
**번역 대상 텍스트:**

{source_text}
---

**요구사항:**
1.  위 텍스트를 한국어로 번역하십시오.
2.  제시된 용어집을 100% 완벽하게 준수하십시오.
3.  문서 유형이 'claim'인 경우, 반드시 명사구 구조로 종결하십시오.
4.  번역문 외에 다른 설명이나 주석은 절대 추가하지 마십시오.
"""

        # 용어 테이블 생성
        term_table = "\n".join([f"| {eng} | {kor} | 절대 준수 |" for eng, kor in term_mapping.items()])

        # 이전 번역 컨텍스트
        previous_context = ""
        if previous_translation:
            previous_context = f"""
## 이전 세그먼트 번역 (용어 일관성 참고)
{previous_translation}

**지시**: 위 번역에서 사용된 용어와 표현을 **반드시 일관되게** 유지하십시오.
"""

        return base_prompt.format(
            domain=domain,
            document_type=document_type,
            term_table=term_table,
            previous_context=previous_context,
            source_text=source_text
        )

    def translate(self,
                 source_text: str,
                 domain: str,
                 term_mapping: Dict[str, str],
                 document_type: str = "claim",
                 previous_translation: Optional[str] = None) -> Dict:
        """텍스트 번역"""

        print(f"🔄 번역 중... (모델: {self.model_name}, 도메인: {domain}, 유형: {document_type})")

        prompt = self.build_translation_prompt(
            source_text, domain, term_mapping, document_type, previous_translation
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Gemini API의 응답 구조에 따라 텍스트 추출
            translation = response.text.strip()

            return {"success": True, "translation": translation}

        except Exception as e:
            return {"success": False, "error": str(e), "translation": None}

    def translate_with_self_review(self,
                                   source_text: str,
                                   domain: str,
                                   term_mapping: Dict[str, str],
                                   document_type: str = "claim") -> Dict:
        """자체 검수 포함 번역"""

        print("📝 1단계: 초벌 번역")
        first_result = self.translate(source_text, domain, term_mapping, document_type)

        if not first_result["success"]:
            return first_result
        first_translation = first_result["translation"]

        print("🔍 2단계: 자체 검수")
        review_prompt = f"""당신은 특허 번역 품질 검수 전문가입니다.

아래 번역을 검토하고 문제가 있으면 수정하십시오.

## 원문
{source_text}

## 번역문
{first_translation}

## 필수 용어집 (절대 준수)
{json.dumps(term_mapping, ensure_ascii=False, indent=2)}

## 검수 체크리스트
- **용어 일관성**: 모든 기술 용어가 용어집대로 번역되었는가?
- **형식 규칙 (청구항)**: 명사구 종결, 마침표, "상기" 사용이 적절한가?
- **금지 용어**: "탈착하다", "말단" 등 금지된 표현이 사용되지 않았는가?

## 출력 형식
**수정 사항이 있으면 수정된 번역을, 없으면 원 번역을 그대로 출력하십시오.**
번역문 외에 다른 설명은 절대 추가하지 마십시오.
"""
        
        try:
            response = self.model.generate_content(
                review_prompt,
                generation_config=self.generation_config
            )
            final_translation = response.text.strip()
            
            status = "REVISED" if final_translation != first_translation else "APPROVED"
            print(f"   ✓ 검수 결과: {status}")

            return {
                "success": True,
                "translation": final_translation,
                "review_status": status,
                "first_translation": first_translation if status == "REVISED" else None,
            }

        except Exception as e:
            print(f"   ⚠️ 검수 실패, 초벌 번역 사용: {e}")
            return first_result

if __name__ == "__main__":
    translator = PatentTranslator()

    source = """A method for characterizing a protein, comprising:
obtaining a protein sample;
preparing said sample for spectroscopy;
subjecting said sample to an experiment;
eliminating noise from empty areas of a resulting spectrum;
and analyzing the spectrum to characterize the protein."""

    term_mapping = {
        "protein": "단백질", "sample": "샘플", "spectroscopy": "분광 검사",
        "experiment": "실험", "spectrum": "스펙트럼", "noise": "소음"
    }

    result = translator.translate_with_self_review(
        source_text=source, domain="biotech",
        term_mapping=term_mapping, document_type="claim"
    )

    if result["success"]:
        print("\n✅ 번역 완료:")
        print(result["translation"])
        print(f"\n상태: {result.get('review_status', 'N/A')}")
    else:
        print(f"\n❌ 번역 실패: {result.get('error', 'Unknown error')}")
