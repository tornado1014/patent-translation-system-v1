# 🤖 자동 섹션 분류 기능 추가

**전체 명세서를 한 번에 입력하여 자동으로 섹션별 번역**

---

## 🎯 기능 개요

기존에는 사용자가 청구항/명세서/요약서를 각각 나눠서 입력해야 했지만, 이제 **자동 섹션 분류** 기능으로 전체 명세서를 한 번에 입력하면 자동으로 섹션을 구분하여 번역합니다.

### 개선 전 (불편)
```
1. 명세서에서 청구항 부분만 복사 → 파일 저장
2. GUI에서 "청구항" 선택 → 번역 → 기다림
3. 명세서에서 요약서 부분만 복사 → 파일 저장
4. GUI에서 "요약서" 선택 → 번역 → 기다림
5. 명세서에서 상세설명 부분만 복사 → 파일 저장
6. GUI에서 "명세서" 선택 → 번역 → 기다림
```

### 개선 후 (편리)
```
1. 전체 명세서 파일 저장
2. GUI에서 "자동 섹션 분류" 체크
3. 번역 시작 → 자동으로 섹션 구분하여 일괄 번역!
```

---

## 📋 자동 인식 섹션

다음 섹션 헤더를 자동으로 인식합니다:

### 1. 제목 (Title)
- `TITLE OF THE INVENTION`
- `TITLE`
- `INVENTION TITLE`

### 2. 요약서 (Abstract)
- `ABSTRACT OF THE INVENTION`
- `ABSTRACT OF THE DISCLOSURE`
- `ABSTRACT`
- `TECHNICAL ABSTRACT`

### 3. 청구범위 (Claims)
- `CLAIMS`
- `CLAIM`
- `WHAT IS CLAIMED`
- `WE CLAIM`
- `I CLAIM`

각 청구항은 번호를 기준으로 자동 분리:
- `1. A method...`
- `Claim 1. A method...`
- `2. The method of claim 1...`

### 4. 명세서 (Specification)
다음 섹션들은 모두 "명세서"로 통합:
- `BACKGROUND OF THE INVENTION`
- `FIELD OF THE INVENTION`
- `SUMMARY OF THE INVENTION`
- `DETAILED DESCRIPTION`
- `DESCRIPTION OF THE EMBODIMENTS`
- `BRIEF DESCRIPTION OF THE DRAWINGS`

---

## 🚀 사용 방법

### GUI에서 사용

1. **전체 명세서 파일 준비**
   ```
   TITLE OF THE INVENTION
   Method for Processing Data

   ABSTRACT
   A method for processing data comprising...

   CLAIMS
   1. A method comprising:
       obtaining a substrate;
       processing the data.

   2. The method of claim 1, wherein...

   DETAILED DESCRIPTION
   This invention relates to...
   ```

2. **GUI 실행**
   ```bash
   ./run_gui.sh
   ```

3. **번역 탭에서:**
   - ✅ **"🤖 자동 섹션 분류 (전체 명세서 입력 시)" 체크**
   - 입력 파일 선택: 전체 명세서 파일
   - 출력 파일 지정
   - 번역 시작

4. **자동 처리:**
   ```
   📝 번역 중 (1/5): TITLE #1 - specification
   📝 번역 중 (2/5): ABSTRACT #1 - abstract
   📝 번역 중 (3/5): CLAIMS #1 - claim
   📝 번역 중 (4/5): CLAIMS #2 - claim
   📝 번역 중 (5/5): SPECIFICATION #1 - specification
   🔄 번역 문서 재구성 중...
   ✅ 번역 완료!
   ```

### CLI에서 사용 (향후 추가 예정)

```bash
# 현재는 GUI에서만 사용 가능
# CLI 옵션은 향후 추가 예정
```

---

## 🔧 기술적 세부사항

### 1. 섹션 파서 (`section_parser.py`)

새로 추가된 `PatentSectionParser` 클래스:

```python
from section_parser import PatentSectionParser

parser = PatentSectionParser()
sections = parser.parse_document(full_text)

# 결과:
# {
#     'title': [PatentSection(...)]
#     'abstract': [PatentSection(...)]
#     'claims': [PatentSection(...), PatentSection(...), ...]  # 각 청구항별로 분리
#     'specification': [PatentSection(...), PatentSection(...), ...]
# }
```

### 2. 자동 분류 알고리즘

#### 헤더 감지
- 각 라인을 정규식 패턴으로 검사
- 대소문자 무관 (case-insensitive)
- 여러 변형 지원 (ABSTRACT, ABSTRACT OF THE INVENTION 등)

#### 청구항 분리
- 청구항 번호 패턴 감지: `^\s*(?:Claim\s+)?(\d+)\.\s+`
- 각 청구항을 독립적인 섹션으로 분리
- 종속항도 정확하게 인식

#### 섹션 통합
- Background, Summary, Detailed Description → 모두 "Specification"으로 통합
- 원래 순서대로 보존하여 재구성

### 3. 번역 프로세스

```python
# 각 섹션별로:
for section in sections:
    # 섹션 타입에 따라 적절한 문서 타입 결정
    doc_type = parser.get_document_type_from_section(section.section_type)
    # title → specification
    # abstract → abstract
    # claim → claim
    # specification → specification

    # 해당 타입으로 번역
    result = pipeline.translate_document(
        source_text=section.content,
        document_type=doc_type,
        use_self_review=True,
        save_to_tm=True
    )

    # 번역 결과 저장
    translated_sections[section_type].append((section, result["translation"]))

# 원래 순서대로 재구성
final_translation = parser.reconstruct_document(translated_sections)
```

### 4. 헤더 번역

자동으로 섹션 헤더를 한국어로 번역:

| 영문 | 한국어 |
|------|--------|
| TITLE | 발명의 명칭 |
| ABSTRACT | 요약서 |
| CLAIMS | 청구범위 |
| CLAIM | 청구항 |
| BACKGROUND | 발명의 배경 |
| FIELD | 기술분야 |
| SUMMARY | 발명의 요약 |
| DETAILED DESCRIPTION | 발명의 상세한 설명 |
| BRIEF DESCRIPTION OF THE DRAWINGS | 도면의 간단한 설명 |

---

## 💡 사용 팁

### 언제 자동 섹션 분류를 사용할까?

**✅ 사용 권장:**
- 전체 명세서 파일이 있을 때
- 여러 섹션이 포함된 문서
- PCT 출원, 미국 특허 명세서 등 표준 형식

**❌ 사용 비권장:**
- 청구항만 있는 파일
- 요약서만 있는 파일
- 비표준 형식 (헤더 없음)

→ 단일 섹션만 있다면 일반 모드(문서 유형 선택)가 더 빠름!

### 파일 형식

지원하는 입력 파일:
- `.txt`: 텍스트 파일 (가장 빠름)
- `.docx`: Word 문서
- `.pdf`: PDF 파일 (docling 변환)

출력 파일:
- `.txt`: 텍스트
- `.docx`: Word 문서 (권장)

---

## 📊 성능

### 예시: 5개 섹션 명세서

| 모드 | 파일 수 | 작업 수 | 대기 시간 |
|------|---------|---------|-----------|
| **수동 (기존)** | 5개 | 5번 | 각 작업 후 대기 |
| **자동 (신규)** | 1개 | 1번 | 한 번만! |

### 번역 시간 비교

- **수동 모드**: 사용자 작업 시간 + 5회 번역 대기
- **자동 모드**: 5회 번역 대기만 (사용자 작업 시간 0)

→ **사용자 작업 시간이 크게 감소!**

---

## 🔍 예시 문서

### 입력 (전체 명세서)

```
TITLE OF THE INVENTION
Method for Processing Data

ABSTRACT
A method for processing data comprising obtaining a substrate,
processing the data, and analyzing results.

CLAIMS
1. A method for processing data comprising:
    obtaining a substrate;
    processing the data; and
    analyzing results.

2. The method of claim 1, wherein the substrate is adapted to
   receive signals.

DETAILED DESCRIPTION
This invention relates to data processing methods. The method
comprises several steps as described below...

BRIEF DESCRIPTION OF THE DRAWINGS
FIG. 1 shows a flowchart of the method.
FIG. 2 illustrates the substrate structure.
```

### 출력 (자동 번역 및 재구성)

```
발명의 명칭

데이터를 처리하는 방법

요약서

데이터를 처리하는 방법으로서, 기재를 획득하고, 데이터를 처리하고,
결과를 분석하는 것을 포함한다.

청구범위

1. 데이터를 처리하는 방법으로서:
   기재를 획득하는 단계;
   데이터를 처리하는 단계; 및
   결과를 분석하는 단계를 포함하는, 방법.

2. 제1항에 있어서, 상기 기재는 신호를 수신하도록 구성되는 것인, 방법.

발명의 상세한 설명

본 발명은 데이터 처리 방법에 관한 것이다. 상기 방법은 하기와 같이
기술되는 여러 단계를 포함한다...

도면의 간단한 설명

도 1은 상기 방법의 플로우차트를 도시한다.
도 2는 상기 기재 구조를 예시한다.
```

---

## 🛠️ 구현 파일

### 신규 파일
- `src/section_parser.py`: 섹션 자동 파싱 엔진

### 수정 파일
- `gui_app.py`: GUI에 자동 섹션 분류 옵션 추가
  - `auto_section_checkbox`: 체크박스 추가
  - `toggle_auto_section()`: 토글 함수
  - `TranslationThread`: 자동 분류 모드 추가
  - 섹션별 진행 상황 표시

---

## ⚠️ 주의사항

### 1. 섹션 헤더 필수
자동 분류는 **섹션 헤더**를 기준으로 작동합니다.

❌ **작동하지 않는 경우:**
```
A method for processing data comprising:
obtaining a substrate;
processing the data.

The method of claim 1, wherein...
```
→ 헤더 없음 = 섹션 구분 불가

✅ **작동하는 경우:**
```
CLAIMS
1. A method for processing data comprising:
obtaining a substrate;
processing the data.

2. The method of claim 1, wherein...
```
→ "CLAIMS" 헤더 = 자동 인식

### 2. 표준 형식 권장
- PCT 국제출원 형식
- 미국 특허 명세서 형식
- 유럽 특허 명세서 형식

비표준 형식은 수동 모드 사용 권장!

### 3. 청구항 번호
청구항은 **번호**로 구분됩니다:
- `1. A method...` ✅
- `First claim: A method...` ❌

---

## 📖 참고 자료

- `src/section_parser.py`: 파서 구현 코드
- `gui_app.py`: GUI 통합 코드
- `tests/test_samples/`: 테스트 샘플 파일

---

## ✨ 향후 개선 계획

### 1. CLI 지원
```bash
# 계획
uv run python main.py translate full_spec.txt -o output.txt --auto-section
```

### 2. 추가 섹션 인식
- Prior Art (선행기술)
- Examples (실시예)
- Comparative Examples (비교예)

### 3. 커스텀 헤더
사용자가 직접 헤더 패턴 추가 가능

### 4. 섹션 미리보기
번역 전 감지된 섹션 확인 기능

---

**🎉 이제 전체 명세서를 한 번에 번역할 수 있습니다!**

수동으로 섹션을 나누는 번거로움 없이, 한 번의 클릭으로 모든 섹션을 자동으로 번역하세요.
