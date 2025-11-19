# 🚀 특허 번역 자동화 시스템

Claude AI 및 Python 기반의 영한 특허 번역 자동화 솔루션

## ✨ 주요 기능

### 1. 자동 문서 분석
- 기술 분야 자동 식별 (전자/반도체, 화학/제약, 기계, 바이오 등)
- 핵심 기술 용어 자동 추출
- 반복 패턴 감지

### 2. 구조화 번역 시스템
- **3단계 프롬프트 엔지니어링**
  - Phase 0: 문서 분석 및 용어 확정
  - Phase 1: 용어집 기반 번역
  - Phase 2: 자체 검수 및 재번역
- Claude API 기반 고품질 번역
- 용어 일관성 강제 적용
- 이전 세그먼트 컨텍스트 활용

### 3. 자동 QA 검증 (40+ 규칙)
- **형식 규칙**: 온도/퍼센트 공백, 서열번호 형식 등
- **용어 일관성**: 금지 용어 탐지, 도메인별 용어 검증
- **법률 언어**: 선행사 '상기' 검사, transitional phrases
- **청구항 구조**: 명사구 종결, 마침표 확인

### 4. Translation Memory (TM)
- SQLite 기반 경량 TM 시스템
- 유사 문장 자동 검색 (유사도 기반)
- 품질 점수 관리
- 도메인/문서 유형별 필터링

### 5. RAG 기반 스타일 가이드 시스템
- 스타일 가이드를 벡터 DB에 저장
- 번역 시 관련 규칙 자동 검색
- 실시간 규칙 주입

## 📦 설치

### 1. 프로젝트 클론 또는 다운로드
```bash
cd patent-translation-system
```

### 2. Python 가상환경 생성 (권장)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
cp .env.example .env
```

`.env` 파일을 열어 Anthropic API 키 입력:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

## 🚀 빠른 시작

### 지원 파일 형식
- ✅ **입력**: 텍스트(.txt), Word(.docx), PDF(.pdf)
- ✅ **출력**: 텍스트(.txt), Word(.docx)

### 기본 사용법

```bash
# 텍스트 → 텍스트
python main.py translate input.txt -o output.txt --type claim

# Word → 텍스트
python main.py translate input.docx -o output.txt --type claim

# Word → Word (실무 추천! 👍)
python main.py translate input.docx -o output.docx --type claim

# PDF → Word
python main.py translate input.pdf -o output.docx --type specification
```

### 주요 옵션

```bash
# 자체 검수 없이 번역 (더 빠름)
python main.py translate input.txt -o output.txt --no-review

# TM 저장하지 않고 번역
python main.py translate input.txt -o output.txt --no-tm

# 문서 유형 지정
python main.py translate input.txt -o output.txt --type [claim|specification|abstract]
```

### TM 통계 확인

```bash
python main.py tm-stats
```

### 스타일 가이드 RAG 인덱싱 (선택사항)

```bash
python main.py init-rag "Style_Guide_for_En-Ko_Patent_Localization_v1.0.md"
```

## 📁 프로젝트 구조

```
patent-translation-system/
├── config/
│   ├── terminology.json        # 도메인별 용어집
│   ├── style_guide.json        # QA 규칙
│   └── api_config.yaml         # API 설정
├── src/
│   ├── analyzer.py             # 문서 분석 모듈
│   ├── translator.py           # Claude API 번역 엔진
│   ├── qa_checker.py           # 자동 QA 검증
│   ├── tm_manager.py           # Translation Memory
│   ├── rag_guide.py            # RAG 시스템
│   └── pipeline.py             # 통합 파이프라인
├── data/
│   ├── translation_memory.db   # TM 데이터베이스
│   └── style_guide_vectors/    # RAG 벡터 DB
├── tests/
│   └── test_samples/           # 테스트 샘플
├── output/                     # 번역 결과 출력
├── main.py                     # CLI 진입점
├── requirements.txt            # 의존성
└── README.md
```

## 🎯 번역 워크플로우

```
1. 📄 입력 텍스트
   ↓
2. 📊 문서 분석
   - 도메인 식별
   - 용어 추출
   ↓
3. 📚 TM 검색
   - 완전 일치 → 즉시 반환
   - 유사 매치 → 참고용
   ↓
4. 🔄 Claude 번역
   - 용어집 강제 적용
   - 자체 검수 (선택)
   ↓
5. 🔍 QA 검증
   - 형식/용어/구조 검사
   - 위반 사항 리포트
   ↓
6. 💾 TM 저장
   - 품질 점수 부여
   ↓
7. ✅ 번역 완료
```

## 💡 사용 예시

### Python 스크립트에서 사용

```python
from src.pipeline import TranslationPipeline

# 파이프라인 초기화
pipeline = TranslationPipeline()

# 번역 실행
source_text = """A method comprising obtaining a sample..."""

result = pipeline.translate_document(
    source_text=source_text,
    document_type="claim",
    use_self_review=True,
    save_to_tm=True
)

if result["success"]:
    print(result["translation"])
    print(f"QA 통과: {result['qa_result']['passed']}")

pipeline.close()
```

## 🔧 설정 커스터마이징

### 용어집 추가 (`config/terminology.json`)

```json
{
  "domain_terms": {
    "your_domain": {
      "english_term": "한국어_번역"
    }
  }
}
```

### QA 규칙 수정 (`config/style_guide.json`)

JSON 파일을 편집하여 검증 규칙 추가/수정 가능

### API 설정 변경 (`config/api_config.yaml`)

모델, temperature, chunk_size 등 조정 가능

## 📊 예상 효과

| 항목 | 개선 효과 |
|------|-----------|
| **용어 일관성** | 60% → 85-95% (+35%) |
| **QA 자동화** | 수동 → 100% 자동 |
| **번역 속도** | 10배 향상 |
| **재작업률** | 30% → 5% (-83%) |

## 🛠 문제 해결

### API 키 오류
```bash
# .env 파일에 올바른 API 키가 설정되어 있는지 확인
cat .env
```

### 모듈 import 오류
```bash
# Python 경로 확인
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### ChromaDB 오류 (선택 기능)
```bash
# ChromaDB는 선택 사항. RAG 기능 없이도 사용 가능
# 설치하려면:
pip install chromadb sentence-transformers
```

## 📝 주의사항

1. **API 비용**: Claude API 사용량에 따라 비용 발생
2. **온라인 필수**: 번역 시 인터넷 연결 필요
3. **품질 검토**: 자동 QA를 통과해도 최종 인간 검토 권장
4. **법적 책임**: 본 도구는 보조 수단이며, 최종 번역 품질은 사용자 책임

## 🔮 향후 개선 계획

- [ ] 배치 처리 기능
- [ ] 웹 UI 추가
- [ ] 다국어 지원 (한중, 한일)
- [ ] Fine-tuning 옵션
- [ ] CAT Tool 연동 (MemoQ, Trados)

## 📄 라이선스

이 프로젝트는 개인 사용 목적으로 개발되었습니다.

## 🙏 참고 자료

- [Anthropic Claude API Documentation](https://docs.anthropic.com/)
- [특허청 (KIPO)](https://www.kipo.go.kr/)
- Style Guide for En-Ko Patent Localization v1.0

---

**Made with ❤️ using Claude Code**
