"""
자동 QA 검증 시스템
- 형식 규칙 검사
- 용어 일관성 검사
- 금지 용어 검사
- 스타일 가이드 준수 확인
- QA_CHECKLIST.md 기반 포괄적 검사
"""

import re
import json
from typing import Dict, List
from pathlib import Path


class QAViolation:
    """QA 위반 사항"""

    def __init__(self, rule_id: str, severity: str, description: str,
                 location: str, found: str, correct: str = ""):
        self.rule_id = rule_id
        self.severity = severity  # critical, major, minor, neutral
        self.description = description
        self.location = location
        self.found = found
        self.correct = correct

    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "description": self.description,
            "location": self.location,
            "found": self.found,
            "correct": self.correct
        }


class PatentQAChecker:
    """특허 번역 QA 체커"""

    def __init__(self, style_guide_path: str = "config/style_guide.json",
                 terminology_path: str = "config/terminology.json",
                 qa_checklist_path: str = "config/QA_CHECKLIST.md"):
        self.style_guide = self._load_json(style_guide_path)
        self.terminology = self._load_json(terminology_path)
        self.qa_checklist_path = qa_checklist_path
        self.violations: List[QAViolation] = []

        # QA 체크리스트 기반 규칙 초기화
        self._init_checklist_rules()

    def _load_json(self, path: str) -> Dict:
        """JSON 파일 로드"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _init_checklist_rules(self):
        """QA 체크리스트 기반 규칙 초기화"""
        # 체크리스트에서 추출한 주요 검사 항목들

        # 1. 금지 용어 (도메인별)
        self.domain_mistranslations = {
            'substrate': {'wrong': '기판', 'context': '화학', 'correct': '기재'},
            'detach': {'wrong': '탈착하다', 'correct': '탈리하다'},
            'fault': {'wrong': '오류', 'context': '기계/전기', 'correct': '고장'},
            'source': {'wrong': '공급원', 'context': '방사선', 'correct': '선원'},
            'communication': {'wrong': '통신', 'context': '유체', 'correct': '연통'},
            'distal end': {'wrong': '말단', 'correct': '원위 단부'},
            'proximal end': {'wrong': '말단', 'correct': '근위 단부'},
            'intake': {'wrong': '흡기구', 'context': '액체', 'correct': '흡입구'},
            'ground': {'wrong': '지면', 'context': '전기', 'correct': '접지'},
            'recite': {'wrong': ['암송', '열거'], 'correct': '기술하다'},
            'incubate': {'wrong': '배양', 'correct': '정치'},
            'adapted to': {'wrong': '적합화된', 'correct': '~하도록 구성된'}
        }

        # 2. 표준 용어
        self.standard_terms = {
            'embodiment': {'preferred': '실시형태', 'forbidden': ['실시태양', '실시예', '구현예']},
            'aspect': {'preferred': '양태', 'avoid': ['양상', '측면']},
            'subject matter': {'correct': ['대상물', '대상'], 'forbidden': '주제'}
        }

        # 3. 수치 비교 오역
        self.numerical_comparisons = {
            'more than one': {'wrong': '하나(1개) 이상', 'correct': ['둘(2개) 이상', '하나(1개) 초과']},
            'less than two': {'wrong': '둘(2개) 이하', 'correct': ['하나(1개) 이하', '둘(2개) 미만']}
        }

        # 4. 전환구
        self.transitional_phrases = {
            'comprising': '포함하는',
            'consisting of': ['이루어지는', '구성되는'],
            'consisting essentially of': '필수적으로 구성되는',
            'characterized by': '~을 특징으로 하는',
            'adapted to': '~하도록 구성된'
        }

    def check_formatting(self, text: str, document_type: str = "claim") -> List[QAViolation]:
        """형식 규칙 검사"""
        violations = []
        formatting_rules = self.style_guide.get("formatting_rules", {})

        # 온도 표기 검사
        temp_pattern = r'(\d+)\s*℃'
        matches = re.finditer(temp_pattern, text)
        for match in matches:
            if not re.match(r'\d+\s℃', match.group()):
                violations.append(QAViolation(
                    rule_id="format_temperature",
                    severity="minor",
                    description="온도 표기 시 숫자와 단위 사이에 공백 필요",
                    location=f"위치: {match.start()}",
                    found=match.group(),
                    correct=f"{match.group(1)} ℃"
                ))

        # 퍼센트 표기 검사
        percent_pattern = r'(\d+)\s*%'
        matches = re.finditer(percent_pattern, text)
        for match in matches:
            if not re.match(r'\d+\s%', match.group()):
                violations.append(QAViolation(
                    rule_id="format_percentage",
                    severity="minor",
                    description="퍼센트 표기 시 숫자와 기호 사이에 공백 필요",
                    location=f"위치: {match.start()}",
                    found=match.group(),
                    correct=f"{match.group(1)} %"
                ))

        # 청구항 마침표 검사
        if document_type == "claim":
            if not text.strip().endswith('.'):
                violations.append(QAViolation(
                    rule_id="claim_ending",
                    severity="major",
                    description="청구항은 마침표로 종결되어야 함",
                    location="문장 끝",
                    found=text.strip()[-20:],
                    correct="... (마침표 추가)"
                ))

        # 서열번호 형식 검사
        seq_pattern = r'서열\s?번호\s?:?\s?(\d+)'
        matches = re.finditer(seq_pattern, text)
        for match in matches:
            if match.group() != f"서열번호 {match.group(1)}":
                violations.append(QAViolation(
                    rule_id="seq_id_format",
                    severity="minor",
                    description="서열번호 형식: '서열번호 숫자'",
                    location=f"위치: {match.start()}",
                    found=match.group(),
                    correct=f"서열번호 {match.group(1)}"
                ))

        return violations

    def check_terminology(self, text: str, term_mapping: Dict[str, str]) -> List[QAViolation]:
        """용어 일관성 검사"""
        violations = []

        # 금지 용어 검사
        forbidden = self.terminology.get("forbidden_translations", {})
        for eng_term, forbidden_list in forbidden.items():
            for forbidden_kr in forbidden_list:
                if forbidden_kr in text:
                    correct_term = term_mapping.get(eng_term, "확인 필요")
                    violations.append(QAViolation(
                        rule_id=f"forbidden_term_{eng_term}",
                        severity="major",
                        description=f"금지 용어 사용: {forbidden_kr}",
                        location=f"'{forbidden_kr}' 발견",
                        found=forbidden_kr,
                        correct=correct_term
                    ))

        return violations

    def check_antecedent_basis(self, source: str, translation: str) -> List[QAViolation]:
        """선행사 '상기' 검사"""
        violations = []

        # "the compound/device/method" 패턴 찾기
        the_pattern = r'the\s+(compound|device|method|system|apparatus|composition)'
        matches = re.finditer(the_pattern, source, re.IGNORECASE)

        for match in matches:
            noun = match.group(1)
            # 한국어 번역에서 해당 명사 찾기
            noun_kr_map = {
                'compound': '화합물',
                'device': '장치',
                'method': '방법',
                'system': '시스템',
                'apparatus': '장치',
                'composition': '조성물'
            }

            noun_kr = noun_kr_map.get(noun.lower())
            if noun_kr:
                # "상기"가 붙어 있는지 확인
                sanggi_pattern = f'상기\\s+{noun_kr}'
                if noun_kr in translation and not re.search(sanggi_pattern, translation):
                    violations.append(QAViolation(
                        rule_id="antecedent_basis",
                        severity="major",
                        description="선행사 있는 명사에 '상기' 누락",
                        location=f"'{noun_kr}' 발견",
                        found=noun_kr,
                        correct=f"상기 {noun_kr}"
                    ))

        return violations

    def check_claim_structure(self, text: str, document_type: str = "claim") -> List[QAViolation]:
        """청구항 구조 검사"""
        violations = []

        if document_type != "claim":
            return violations

        # 명사구 종결 확인
        claim_endings = ['방법.', '장치.', '시스템.', '화합물.', '조성물.', '키트.', '용도.']
        has_proper_ending = any(text.strip().endswith(ending) for ending in claim_endings)

        if not has_proper_ending:
            violations.append(QAViolation(
                rule_id="claim_noun_phrase_ending",
                severity="major",
                description="청구항이 완전한 명사구로 종결되지 않음",
                location="문장 끝",
                found=text.strip()[-30:],
                correct="... 방법. / ... 장치. 등"
            ))

        return violations

    def check_punctuation(self, text: str, document_type: str = "claim") -> List[QAViolation]:
        """구두점 검사 (체크리스트 기반)"""
        violations = []

        # 1. 콜론 오용 검사 (청구항에서 "~로서:" 금지)
        if document_type == "claim":
            colon_after_verb = re.finditer(r'(로서|에서|에|를|을|이|가)\s*:', text)
            for match in colon_after_verb:
                violations.append(QAViolation(
                    rule_id="colon_after_particle",
                    severity="major",
                    description="청구항에서 조사 뒤 콜론 사용 금지",
                    location=f"위치: {match.start()}",
                    found=match.group(),
                    correct=match.group(1) + ","
                ))

        # 2. 세미콜론 오용 검사 (목록 끝 세미콜론)
        semicolon_at_end = re.search(r';\s*$', text.strip())
        if semicolon_at_end:
            violations.append(QAViolation(
                rule_id="semicolon_at_list_end",
                severity="minor",
                description="목록 마지막 항목 뒤 세미콜론 금지",
                location="문장 끝",
                found="... ;",
                correct="... (세미콜론 제거)"
            ))

        return violations

    def check_domain_terms(self, source: str, translation: str) -> List[QAViolation]:
        """도메인별 오역 검사 (체크리스트 기반)"""
        violations = []

        for eng_term, rule in self.domain_mistranslations.items():
            # 원문에 해당 영어 용어가 있는지 확인
            if eng_term.lower() in source.lower():
                wrong_terms = rule['wrong'] if isinstance(rule['wrong'], list) else [rule['wrong']]

                for wrong_kr in wrong_terms:
                    if wrong_kr in translation:
                        violations.append(QAViolation(
                            rule_id=f"domain_mistranslation_{eng_term.replace(' ', '_')}",
                            severity="major",
                            description=f"'{eng_term}' 오역: {rule.get('context', '')} 문맥",
                            location=f"'{wrong_kr}' 발견",
                            found=wrong_kr,
                            correct=rule['correct']
                        ))

        return violations

    def check_standard_terminology(self, translation: str) -> List[QAViolation]:
        """표준 용어 검사 (체크리스트 기반)"""
        violations = []

        # embodiment 번역 검사
        forbidden_embodiments = ['실시태양', '실시예', '구현예']
        for forbidden in forbidden_embodiments:
            if forbidden in translation:
                violations.append(QAViolation(
                    rule_id="embodiment_forbidden_term",
                    severity="minor",
                    description=f"'embodiment' 번역 시 '{forbidden}' 사용 지양",
                    location=f"'{forbidden}' 발견",
                    found=forbidden,
                    correct="실시형태 (권장)"
                ))

        # subject matter 오역 검사
        if '주제' in translation:
            # "subject matter"가 원문에 있을 가능성 체크 (간접적)
            violations.append(QAViolation(
                rule_id="subject_matter_mistranslation",
                severity="minor",
                description="'subject matter'를 '주제'로 번역 지양",
                location="'주제' 발견",
                found="주제",
                correct="대상물 또는 대상"
            ))

        return violations

    def check_numerical_expressions(self, source: str, translation: str) -> List[QAViolation]:
        """수치 표현 검사 (체크리스트 기반)"""
        violations = []

        # "more than one" 검사
        if 'more than one' in source.lower():
            if '하나(1개) 이상' in translation or '하나 이상' in translation:
                violations.append(QAViolation(
                    rule_id="more_than_one_mistranslation",
                    severity="major",
                    description="'more than one' 오역",
                    location="'하나 이상' 발견",
                    found="하나(1개) 이상",
                    correct="둘(2개) 이상 또는 하나(1개) 초과"
                ))

        # "less than two" 검사
        if 'less than two' in source.lower():
            if '둘(2개) 이하' in translation or '둘 이하' in translation:
                violations.append(QAViolation(
                    rule_id="less_than_two_mistranslation",
                    severity="major",
                    description="'less than two' 오역",
                    location="'둘 이하' 발견",
                    found="둘(2개) 이하",
                    correct="하나(1개) 이하 또는 둘(2개) 미만"
                ))

        return violations

    def check_transitional_phrases(self, source: str, translation: str) -> List[QAViolation]:
        """전환구 검사 (체크리스트 기반)"""
        violations = []

        # "adapted to" 특별 검사
        if 'adapted to' in source.lower():
            if '적합화된' in translation or '적응된' in translation:
                violations.append(QAViolation(
                    rule_id="adapted_to_mistranslation",
                    severity="critical",
                    description="'adapted to' 오역 - 권리범위 영향",
                    location="'적합화된' 또는 '적응된' 발견",
                    found="적합화된/적응된",
                    correct="~하도록 구성된"
                ))

        return violations

    def check_claim_noun_phrase_structure(self, text: str, document_type: str = "claim") -> List[QAViolation]:
        """청구항 명사구 구조 상세 검사"""
        violations = []

        if document_type != "claim":
            return violations

        # 방법 청구항 구조 검사
        if '방법' in text:
            # "방법으로서," 또는 "방법에 있어서,"로 시작하는지
            if not (re.search(r'방법으로서,', text) or re.search(r'방법에\s*있어서,', text)):
                violations.append(QAViolation(
                    rule_id="method_claim_preamble",
                    severity="major",
                    description="방법 청구항은 '~방법으로서,' 또는 '~방법에 있어서,'로 시작 권장",
                    location="청구항 시작 부분",
                    found=text[:50] + "...",
                    correct="~방법으로서, ... 또는 ~방법에 있어서, ..."
                ))

            # "~를 포함하는 방법." 또는 "~방법." 형식으로 끝나는지
            proper_endings = [
                r'포함하는\s*방법\.$',
                r'특성화되는,?\s*방법\.$',
                r'이루어지는\s*방법\.$',
                r'구성되는\s*방법\.$'
            ]
            has_proper_ending = any(re.search(pattern, text) for pattern in proper_endings)

            if not has_proper_ending and text.strip().endswith('방법.'):
                # 방법으로 끝나긴 하는데 적절한 형식이 아닐 수 있음
                violations.append(QAViolation(
                    rule_id="method_claim_ending_structure",
                    severity="minor",
                    description="방법 청구항 종결 구조 확인 필요",
                    location="청구항 끝",
                    found=text[-50:],
                    correct="~를 포함하는 방법. 또는 ~특성화되는, 방법."
                ))

        return violations

    def check_all(self, source: str, translation: str,
                  term_mapping: Dict[str, str],
                  document_type: str = "claim") -> Dict:
        """전체 QA 검사 (QA_CHECKLIST.md 기반 포괄적 검사)"""

        print("🔍 QA 검증 중 (QA_CHECKLIST.md 기반)...")

        self.violations = []

        # 1. 형식 검사
        self.violations.extend(self.check_formatting(translation, document_type))
        print(f"   ✓ 형식 검사 완료")

        # 2. 용어 검사 (기존)
        self.violations.extend(self.check_terminology(translation, term_mapping))
        print(f"   ✓ 용어 검사 완료")

        # 3. 선행사 검사
        self.violations.extend(self.check_antecedent_basis(source, translation))
        print(f"   ✓ 선행사 검사 완료")

        # 4. 청구항 구조 검사
        if document_type == "claim":
            self.violations.extend(self.check_claim_structure(translation, document_type))
            print(f"   ✓ 청구항 구조 검사 완료")

        # === QA_CHECKLIST.md 기반 추가 검사 ===

        # 5. 구두점 검사
        self.violations.extend(self.check_punctuation(translation, document_type))
        print(f"   ✓ 구두점 검사 완료")

        # 6. 도메인별 오역 검사
        self.violations.extend(self.check_domain_terms(source, translation))
        print(f"   ✓ 도메인별 용어 검사 완료")

        # 7. 표준 용어 검사
        self.violations.extend(self.check_standard_terminology(translation))
        print(f"   ✓ 표준 용어 검사 완료")

        # 8. 수치 표현 검사
        self.violations.extend(self.check_numerical_expressions(source, translation))
        print(f"   ✓ 수치 표현 검사 완료")

        # 9. 전환구 검사
        self.violations.extend(self.check_transitional_phrases(source, translation))
        print(f"   ✓ 전환구 검사 완료")

        # 10. 청구항 명사구 구조 상세 검사
        if document_type == "claim":
            self.violations.extend(self.check_claim_noun_phrase_structure(translation, document_type))
            print(f"   ✓ 청구항 명사구 구조 상세 검사 완료")

        # 결과 집계
        severity_counts = {
            "critical": 0,
            "major": 0,
            "minor": 0,
            "neutral": 0
        }

        for v in self.violations:
            severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1

        print(f"\n📊 QA 결과:")
        print(f"   Critical: {severity_counts['critical']}")
        print(f"   Major: {severity_counts['major']}")
        print(f"   Minor: {severity_counts['minor']}")
        print(f"   Neutral: {severity_counts['neutral']}")

        return {
            "total_violations": len(self.violations),
            "severity_counts": severity_counts,
            "violations": [v.to_dict() for v in self.violations],
            "passed": severity_counts['critical'] == 0 and severity_counts['major'] == 0
        }

    def generate_report(self, qa_result: Dict) -> str:
        """QA 리포트 생성 (QA_CHECKLIST.md 기반)"""
        report = ["=" * 60]
        report.append("📋 특허 번역 QA 리포트 (QA_CHECKLIST.md 기반)")
        report.append("=" * 60)
        report.append("")

        # 요약
        report.append("## 요약")
        report.append(f"총 위반 사항: {qa_result['total_violations']}개")
        report.append(f"통과 여부: {'✅ PASS' if qa_result['passed'] else '❌ FAIL'}")
        report.append("")

        # 심각도별 집계
        report.append("## 심각도별 집계")
        report.append(f"  CRITICAL (치명적): {qa_result['severity_counts']['critical']}개 - 자동 실패")
        report.append(f"  MAJOR (중대): {qa_result['severity_counts']['major']}개 - 품질 저하")
        report.append(f"  MINOR (경미): {qa_result['severity_counts']['minor']}개 - 개선 권장")
        report.append(f"  NEUTRAL (중립): {qa_result['severity_counts']['neutral']}개 - 참고용")
        report.append("")

        # QA 검사 항목
        report.append("## 실행된 QA 검사 항목 (10개)")
        report.append("  1. ✓ 형식 검사 (온도, 퍼센트, 서열번호, 청구항 마침표)")
        report.append("  2. ✓ 용어 일관성 검사 (금지 용어)")
        report.append("  3. ✓ 선행사 '상기' 검사")
        report.append("  4. ✓ 청구항 구조 검사 (명사구 종결)")
        report.append("  5. ✓ 구두점 검사 (콜론, 세미콜론 오용)")
        report.append("  6. ✓ 도메인별 오역 검사 (substrate, detach, distal/proximal end 등)")
        report.append("  7. ✓ 표준 용어 검사 (embodiment, aspect, subject matter)")
        report.append("  8. ✓ 수치 표현 검사 (more than one, less than two)")
        report.append("  9. ✓ 전환구 검사 (adapted to 등)")
        report.append(" 10. ✓ 청구항 명사구 구조 상세 검사")
        report.append("")
        report.append("📖 전체 가이드라인: config/QA_CHECKLIST.md 참조")
        report.append("")

        # 상세 위반 사항
        if qa_result['violations']:
            report.append("## 상세 위반 사항")
            report.append("")

            for i, v in enumerate(qa_result['violations'], 1):
                report.append(f"### [{i}] {v['rule_id']} ({v['severity'].upper()})")
                report.append(f"설명: {v['description']}")
                report.append(f"위치: {v['location']}")
                report.append(f"발견: {v['found']}")
                if v['correct']:
                    report.append(f"수정: {v['correct']}")
                report.append("")

        report.append("=" * 60)

        return "\n".join(report)


if __name__ == "__main__":
    # 테스트
    checker = PatentQAChecker()

    source = "A method comprising the compound"
    translation = "화합물을 포함하는 방법"  # "상기" 누락
    term_mapping = {"compound": "화합물", "method": "방법"}

    result = checker.check_all(source, translation, term_mapping, document_type="claim")
    report = checker.generate_report(result)

    print(report)
