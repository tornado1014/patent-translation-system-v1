"""
전체 번역 파이프라인 통합
문서 분석 → 번역 → QA 검증 → TM 저장
"""

from typing import Dict, Optional
from pathlib import Path
import json

from analyzer import DocumentAnalyzer
from translator import PatentTranslator
from qa_checker import PatentQAChecker
from tm_manager import TranslationMemory


class TranslationPipeline:
    """통합 번역 파이프라인"""

    def __init__(self):
        print("🚀 번역 파이프라인 초기화 중...")
        self.analyzer = DocumentAnalyzer()
        self.translator = PatentTranslator()
        self.qa_checker = PatentQAChecker()
        self.tm = TranslationMemory()
        print("✅ 초기화 완료\n")

    def translate_document(self,
                          source_text: str,
                          document_type: str = "claim",
                          use_self_review: bool = True,
                          save_to_tm: bool = True) -> Dict:
        """문서 번역 전체 프로세스"""

        print("="*60)
        print("🌟 특허 번역 자동화 시작")
        print("="*60)
        print()

        # STEP 1: 문서 분석
        print("📋 STEP 1: 문서 분석")
        print("-" * 60)
        analysis = self.analyzer.analyze(source_text, use_claude=False)
        domain = analysis["domain"]
        term_mapping = analysis["term_mapping"]

        print(f"   도메인: {domain}")
        print(f"   핵심 용어: {len(term_mapping)}개")
        print()

        # STEP 2: TM 검색
        print("📚 STEP 2: Translation Memory 검색")
        print("-" * 60)
        tm_matches = self.tm.search(source_text, domain=domain, similarity_threshold=0.95)

        if tm_matches and tm_matches[0]["similarity"] == 1.0:
            print(f"   ✅ 완전 일치 발견! (품질 점수: {tm_matches[0]['quality_score']})")
            print()
            return {
                "success": True,
                "translation": tm_matches[0]["target"],
                "source": "TM",
                "analysis": analysis,
                "tm_match": tm_matches[0]
            }
        elif tm_matches:
            print(f"   ℹ️ 유사 번역 {len(tm_matches)}개 발견 (최고 유사도: {tm_matches[0]['similarity']:.1%})")
            print(f"   참고용으로 사용 가능")
        else:
            print("   ℹ️ TM 매치 없음")
        print()

        # STEP 3: 번역
        print("🔄 STEP 3: 번역 수행")
        print("-" * 60)

        if use_self_review:
            translation_result = self.translator.translate_with_self_review(
                source_text=source_text,
                domain=domain,
                term_mapping=term_mapping,
                document_type=document_type
            )
        else:
            translation_result = self.translator.translate(
                source_text=source_text,
                domain=domain,
                term_mapping=term_mapping,
                document_type=document_type
            )

        if not translation_result["success"]:
            print(f"   ❌ 번역 실패: {translation_result.get('error')}")
            return translation_result

        translation = translation_result["translation"]
        print()

        # STEP 4: QA 검증
        print("🔍 STEP 4: 품질 검증 (QA)")
        print("-" * 60)
        qa_result = self.qa_checker.check_all(
            source=source_text,
            translation=translation,
            term_mapping=term_mapping,
            document_type=document_type
        )
        print()

        # STEP 5: TM 저장
        if save_to_tm and qa_result["passed"]:
            print("💾 STEP 5: Translation Memory 저장")
            print("-" * 60)
            quality_score = 10 if qa_result["total_violations"] == 0 else 7
            self.tm.add(
                source=source_text,
                target=translation,
                domain=domain,
                document_type=document_type,
                quality_score=quality_score
            )
            print(f"   ✅ TM 저장 완료 (품질 점수: {quality_score})")
            print()

        # 최종 결과
        print("="*60)
        print("✅ 번역 완료!")
        print("="*60)
        print()

        return {
            "success": True,
            "translation": translation,
            "source": "Claude AI",
            "analysis": analysis,
            "qa_result": qa_result,
            "translation_result": translation_result
        }

    def close(self):
        """리소스 정리"""
        self.tm.close()


if __name__ == "__main__":
    # 테스트
    pipeline = TranslationPipeline()

    source = """A method for characterizing a protein, comprising:
obtaining a protein sample;
preparing said sample for spectroscopy;
subjecting said sample to an experiment;
eliminating noise from empty areas of a resulting spectrum;
and analyzing the spectrum to characterize the protein."""

    result = pipeline.translate_document(
        source_text=source,
        document_type="claim",
        use_self_review=True
    )

    if result["success"]:
        print("\n📄 번역 결과:")
        print("-" * 60)
        print(result["translation"])
        print()

        # QA 리포트
        if "qa_result" in result:
            qa_report = pipeline.qa_checker.generate_report(result["qa_result"])
            print(qa_report)

    pipeline.close()
