"""
특허 명세서 섹션 자동 파싱
- 제목(Title), 요약서(Abstract), 청구항(Claims), 명세서(Specification) 자동 구분
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PatentSection:
    """특허 섹션 데이터"""
    section_type: str  # title, abstract, claim, specification
    content: str
    start_line: int
    end_line: int
    heading: str = ""


class PatentSectionParser:
    """특허 명세서 섹션 파서"""

    def __init__(self):
        # 영문 섹션 헤더 패턴
        self.section_patterns = {
            'title': [
                r'^TITLE\s*(?:OF\s*(?:THE\s*)?INVENTION)?',
                r'^(?:INVENTION\s+)?TITLE',
            ],
            'abstract': [
                r'^ABSTRACT\s*(?:OF\s*(?:THE\s*)?(?:DISCLOSURE|INVENTION))?',
                r'^TECHNICAL\s+ABSTRACT',
            ],
            'claims': [
                r'^CLAIMS?',
                r'^WHAT\s+IS\s+CLAIMED',
                r'^WE\s+CLAIM',
                r'^I\s+CLAIM',
            ],
            'background': [
                r'^BACKGROUND\s*(?:OF\s*(?:THE\s*)?INVENTION)?',
                r'^FIELD\s*(?:OF\s*(?:THE\s*)?INVENTION)?',
            ],
            'summary': [
                r'^SUMMARY\s*(?:OF\s*(?:THE\s*)?INVENTION)?',
                r'^BRIEF\s+SUMMARY',
            ],
            'description': [
                r'^DETAILED\s+DESCRIPTION',
                r'^DESCRIPTION\s*(?:OF\s*(?:THE\s*)?(?:PREFERRED\s+)?EMBODIMENTS?)?',
                r'^DESCRIPTION\s*(?:OF\s*(?:THE\s*)?INVENTION)?',
            ],
            'drawings': [
                r'^BRIEF\s+DESCRIPTION\s+OF\s+(?:THE\s+)?DRAWINGS?',
                r'^DESCRIPTION\s+OF\s+(?:THE\s+)?DRAWINGS?',
            ]
        }

        # 청구항 번호 패턴 (1., Claim 1, 등)
        self.claim_number_pattern = r'^\s*(?:Claim\s+)?(\d+)\.\s+'

    def parse_document(self, text: str) -> Dict[str, List[PatentSection]]:
        """
        특허 문서를 섹션별로 파싱

        Returns:
            {
                'title': [PatentSection],
                'abstract': [PatentSection],
                'claims': [PatentSection],  # 각 청구항별로 분리
                'specification': [PatentSection],  # Background, Summary, Description 통합
            }
        """
        lines = text.split('\n')
        sections = {
            'title': [],
            'abstract': [],
            'claims': [],
            'specification': []
        }

        current_section = None
        section_start = 0
        section_content = []

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # 빈 줄 스킵
            if not line_stripped:
                if current_section:
                    section_content.append(line)
                continue

            # 섹션 헤더 감지
            detected_section = self._detect_section_header(line_stripped)

            if detected_section:
                # 이전 섹션 저장
                if current_section and section_content:
                    self._save_section(
                        sections,
                        current_section,
                        '\n'.join(section_content).strip(),
                        section_start,
                        i - 1,
                        line_stripped
                    )

                # 새 섹션 시작
                current_section = detected_section
                section_start = i
                section_content = []

            # 청구항 섹션 내에서 개별 청구항 감지
            elif current_section == 'claims':
                claim_match = re.match(self.claim_number_pattern, line_stripped)
                if claim_match:
                    # 이전 청구항 저장
                    if section_content:
                        self._save_claim(
                            sections,
                            '\n'.join(section_content).strip(),
                            section_start,
                            i - 1
                        )

                    # 새 청구항 시작
                    section_start = i
                    section_content = [line]
                else:
                    section_content.append(line)

            # 일반 내용 누적
            else:
                section_content.append(line)

        # 마지막 섹션 저장
        if current_section and section_content:
            if current_section == 'claims':
                self._save_claim(
                    sections,
                    '\n'.join(section_content).strip(),
                    section_start,
                    len(lines) - 1
                )
            else:
                self._save_section(
                    sections,
                    current_section,
                    '\n'.join(section_content).strip(),
                    section_start,
                    len(lines) - 1,
                    ""
                )

        return sections

    def _detect_section_header(self, line: str) -> str:
        """라인에서 섹션 헤더 감지"""
        line_upper = line.upper()

        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.match(pattern, line_upper):
                    # Background, Summary, Description은 specification으로 통합
                    if section_type in ['background', 'summary', 'description', 'drawings']:
                        return 'specification'
                    return section_type

        return None

    def _save_section(self, sections: Dict, section_type: str, content: str,
                     start_line: int, end_line: int, heading: str):
        """섹션 저장"""
        if not content:
            return

        # title, abstract, claims는 그대로 저장
        if section_type in ['title', 'abstract', 'claims']:
            sections[section_type].append(PatentSection(
                section_type=section_type,
                content=content,
                start_line=start_line,
                end_line=end_line,
                heading=heading
            ))
        # specification은 누적
        else:
            sections['specification'].append(PatentSection(
                section_type='specification',
                content=content,
                start_line=start_line,
                end_line=end_line,
                heading=heading
            ))

    def _save_claim(self, sections: Dict, content: str, start_line: int, end_line: int):
        """청구항 저장"""
        if not content:
            return

        sections['claims'].append(PatentSection(
            section_type='claim',
            content=content,
            start_line=start_line,
            end_line=end_line
        ))

    def get_document_type_from_section(self, section_type: str) -> str:
        """섹션 타입을 문서 타입으로 변환"""
        type_mapping = {
            'title': 'specification',
            'abstract': 'abstract',
            'claim': 'claim',
            'claims': 'claim',
            'specification': 'specification'
        }
        return type_mapping.get(section_type, 'specification')

    def reconstruct_document(self, translated_sections: Dict[str, List[Tuple[PatentSection, str]]]) -> str:
        """번역된 섹션들을 원래 순서대로 재구성"""
        all_sections = []

        # 모든 섹션을 시작 라인 기준으로 정렬
        for section_type, items in translated_sections.items():
            for original_section, translated_text in items:
                all_sections.append((original_section, translated_text))

        # 시작 라인 기준 정렬
        all_sections.sort(key=lambda x: x[0].start_line)

        # 재구성
        result = []
        for original_section, translated_text in all_sections:
            if original_section.heading:
                # 헤더를 한국어로 변환
                result.append(self._translate_header(original_section.heading))
                result.append("")

            result.append(translated_text)
            result.append("")

        return '\n'.join(result)

    def _translate_header(self, header: str) -> str:
        """섹션 헤더를 한국어로 번역"""
        header_upper = header.upper()

        translations = {
            'TITLE': '발명의 명칭',
            'ABSTRACT': '요약서',
            'CLAIMS': '청구범위',
            'CLAIM': '청구항',
            'BACKGROUND': '발명의 배경',
            'FIELD': '기술분야',
            'SUMMARY': '발명의 요약',
            'DETAILED DESCRIPTION': '발명의 상세한 설명',
            'DESCRIPTION': '설명',
            'BRIEF DESCRIPTION OF THE DRAWINGS': '도면의 간단한 설명'
        }

        for eng, kor in translations.items():
            if eng in header_upper:
                return kor

        return header


if __name__ == "__main__":
    # 테스트
    parser = PatentSectionParser()

    test_doc = """
TITLE OF THE INVENTION
Method for Processing Data

ABSTRACT
A method for processing data comprising various steps.

CLAIMS
1. A method for processing data comprising:
obtaining a substrate; and
processing the data.

2. The method of claim 1, wherein the substrate is adapted to receive signals.

DETAILED DESCRIPTION
This invention relates to data processing...
"""

    sections = parser.parse_document(test_doc)

    print("📋 파싱 결과:")
    for section_type, items in sections.items():
        print(f"\n{section_type.upper()}: {len(items)}개")
        for i, section in enumerate(items, 1):
            print(f"  [{i}] Lines {section.start_line}-{section.end_line}")
            print(f"      {section.content[:50]}...")
