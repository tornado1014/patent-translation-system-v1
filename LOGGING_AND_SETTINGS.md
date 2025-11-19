# 📊 로깅 시스템 및 설정 관리 가이드

**v1.1 - 상세 로그 추적 및 GUI 설정 편집 기능**

---

## 🎯 개선 사항 요약

### 1. **상세 로깅 시스템**
- 모든 번역 단계를 자동으로 파일에 기록
- 콘솔과 파일로 이중 로깅
- 타임스탬프 기반 로그 파일 생성
- 에러 추적 및 디버깅 용이

### 2. **GUI 설정 관리** (계획)
- API 키 GUI에서 직접 편집
- 용어집 실시간 수정
- QA 규칙 커스터마이징
- 로그 파일 뷰어 내장

---

## 📋 로깅 시스템

### 파일 구조

```
logs/
├── translation_20251115_041306.log  # 개별 번역 로그
├── translation_20251115_095432.log
└── translation_20251115_143021.log
```

### 로그 레벨

| 레벨 | 설명 | 콘솔 | 파일 |
|------|------|------|------|
| **DEBUG** | 상세 디버깅 정보 | ❌ | ✅ |
| **INFO** | 일반 정보 (단계 진행) | ✅ | ✅ |
| **WARNING** | 경고 (QA 실패 등) | ✅ | ✅ |
| **ERROR** | 오류 | ✅ | ✅ |
| **CRITICAL** | 치명적 오류 | ✅ | ✅ |

### 로그 내용

#### 1. 번역 시작
```
2025-11-15 04:13:06 | INFO     | PatentTranslation | ================================================================================
2025-11-15 04:13:06 | INFO     | PatentTranslation | 번역 작업 시작
2025-11-15 04:13:06 | INFO     | PatentTranslation |   입력 파일: input.txt
2025-11-15 04:13:06 | INFO     | PatentTranslation |   출력 파일: output.txt
2025-11-15 04:13:06 | INFO     | PatentTranslation |   문서 유형: claim
2025-11-15 04:13:06 | INFO     | PatentTranslation | ================================================================================
```

#### 2. 파일 읽기
```
2025-11-15 04:13:06 | INFO     | PatentTranslation | 파일 읽기 성공: input.txt (txt)
2025-11-15 04:13:06 | DEBUG    | PatentTranslation | 파일 크기: 1,234 bytes, 인코딩: utf-8
```

**오류 시:**
```
2025-11-15 04:13:06 | ERROR    | PatentTranslation | 파일 읽기 실패: input.txt (txt) - [Errno 2] No such file or directory
```

#### 3. 문서 분석
```
2025-11-15 04:13:07 | INFO     | PatentTranslation | STEP 1: 문서 분석 시작
2025-11-15 04:13:07 | INFO     | PatentTranslation |   도메인 식별: biotech
2025-11-15 04:13:07 | INFO     | PatentTranslation |   기술 용어 추출: 5개
2025-11-15 04:13:07 | INFO     | PatentTranslation |   반복 패턴: 2개
2025-11-15 04:13:07 | DEBUG    | PatentTranslation | 분석 완료 - 도메인: biotech, 용어: 5, 패턴: 2
```

#### 4. TM 검색
```
2025-11-15 04:13:08 | INFO     | PatentTranslation | STEP 2: Translation Memory 검색
2025-11-15 04:13:08 | DEBUG    | PatentTranslation |   검색어 길이: 234 문자
2025-11-15 04:13:08 | INFO     | PatentTranslation |   TM 매치 없음
```

**매치 발견 시:**
```
2025-11-15 04:13:08 | INFO     | PatentTranslation |   TM 매치 발견: 3개
2025-11-15 04:13:08 | DEBUG    | PatentTranslation |   최고 유사도: 0.92 (품질 점수: 9.5/10)
```

#### 5. 번역 수행
```
2025-11-15 04:13:10 | INFO     | PatentTranslation | STEP 3: 번역 수행 - 초벌 번역
2025-11-15 04:13:10 | DEBUG    | PatentTranslation |   Claude API 호출 중...
2025-11-15 04:13:15 | INFO     | PatentTranslation |   API 호출 성공: claude-sonnet-4-5 (토큰: 1500)
2025-11-15 04:13:15 | DEBUG    | PatentTranslation | Claude API 응답 성공 - 모델: claude-sonnet-4-5, 토큰: 1500
```

**자체 검수 시:**
```
2025-11-15 04:13:16 | INFO     | PatentTranslation | STEP 3: 번역 수행 - 자체 검수
2025-11-15 04:13:20 | INFO     | PatentTranslation |   API 호출 성공: claude-sonnet-4-5 (토큰: 2300)
2025-11-15 04:13:20 | DEBUG    | PatentTranslation |   검수 결과: REVISED (수정 사항 반영)
```

**API 오류 시:**
```
2025-11-15 04:13:15 | ERROR    | PatentTranslation |   API 호출 실패: claude-sonnet-4-5 - rate_limit_error: Rate limit exceeded
```

#### 6. QA 검증
```
2025-11-15 04:13:21 | INFO     | PatentTranslation | STEP 4: 품질 검증 (QA)
2025-11-15 04:13:21 | INFO     | PatentTranslation |   총 위반 사항: 2개
2025-11-15 04:13:21 | INFO     | PatentTranslation |   Critical: 0, Major: 1, Minor: 1
2025-11-15 04:13:21 | WARNING  | PatentTranslation |   QA 결과: ❌ FAIL
2025-11-15 04:13:21 | DEBUG    | PatentTranslation | QA 검증 완료 - 위반: 2, 통과: False
2025-11-15 04:13:21 | DEBUG    | PatentTranslation |   MAJOR: 1개
2025-11-15 04:13:21 | DEBUG    | PatentTranslation |   MINOR: 1개
```

#### 7. TM 저장
```
2025-11-15 04:13:22 | INFO     | PatentTranslation | STEP 5: Translation Memory 저장
2025-11-15 04:13:22 | DEBUG    | PatentTranslation |   원문 길이: 234 문자
2025-11-15 04:13:22 | DEBUG    | PatentTranslation |   번역문 길이: 198 문자
2025-11-15 04:13:22 | DEBUG    | PatentTranslation |   품질 점수: 8.5/10
```

#### 8. 파일 저장
```
2025-11-15 04:13:23 | INFO     | PatentTranslation | 파일 저장 성공: output.txt (txt)
```

**Word 파일:**
```
2025-11-15 04:13:25 | INFO     | PatentTranslation | 파일 저장 성공: output.docx (docx)
2025-11-15 04:13:25 | DEBUG    | PatentTranslation |   문단 수: 12, 총 글자 수: 1,523
```

#### 9. 번역 완료
```
2025-11-15 04:13:26 | INFO     | PatentTranslation | ================================================================================
2025-11-15 04:13:26 | INFO     | PatentTranslation | 번역 작업 완료 ✅
2025-11-15 04:13:26 | INFO     | PatentTranslation |   소요 시간: 20.15초
2025-11-15 04:13:26 | INFO     | PatentTranslation | ================================================================================
```

#### 10. 자동 섹션 분류
```
2025-11-15 04:20:10 | INFO     | PatentTranslation | 🤖 자동 섹션 분류 모드
2025-11-15 04:20:10 | INFO     | PatentTranslation |   총 섹션: 7개
2025-11-15 04:20:10 | INFO     | PatentTranslation |   TITLE: 1개
2025-11-15 04:20:10 | INFO     | PatentTranslation |   ABSTRACT: 1개
2025-11-15 04:20:10 | INFO     | PatentTranslation |   CLAIMS: 3개
2025-11-15 04:20:10 | INFO     | PatentTranslation |   SPECIFICATION: 2개
2025-11-15 04:20:11 | INFO     | PatentTranslation | 번역 중 (1/7): TITLE - specification
2025-11-15 04:20:15 | INFO     | PatentTranslation | 번역 중 (2/7): ABSTRACT - abstract
2025-11-15 04:20:20 | INFO     | PatentTranslation | 번역 중 (3/7): CLAIMS #1 - claim
...
```

---

## 🔧 로깅 시스템 사용법

### 1. 코드에서 사용

```python
from logger import get_logger

# 로거 가져오기
logger = get_logger()

# 번역 시작
logger.log_translation_start("input.txt", "output.txt", "claim")

# 파일 읽기
try:
    with open("input.txt", 'r') as f:
        content = f.read()
    logger.log_file_read("input.txt", "txt", True)
except Exception as e:
    logger.log_file_read("input.txt", "txt", False, str(e))

# 문서 분석
logger.log_analysis_start()
logger.log_analysis_result("biotech", 5, 2)

# TM 검색
logger.log_tm_search("query text", 0)

# 번역
logger.log_translation_phase("초벌 번역", "Claude API 호출")
logger.log_api_call("claude-sonnet-4-5", 1500, True)

# QA
logger.log_qa_start()
logger.log_qa_result(2, {'critical': 0, 'major': 1, 'minor': 1}, False)

# TM 저장
logger.log_tm_save("source", "translation", 8.5)

# 파일 저장
logger.log_file_save("output.txt", "txt", True)

# 완료
logger.log_translation_complete(True, 20.15)
```

### 2. 로그 파일 확인

```bash
# 최신 로그 보기
tail -f logs/translation_*.log | tail -1

# 특정 로그 전체 보기
cat logs/translation_20251115_041306.log

# 에러만 필터링
grep "ERROR" logs/translation_20251115_041306.log

# 특정 단계만 보기
grep "STEP" logs/translation_20251115_041306.log
```

### 3. 로그 레벨 조정

```python
from logger import TranslationLogger
import logging

# 콘솔에도 DEBUG 출력 (매우 상세)
logger = TranslationLogger(console_level=logging.DEBUG)

# 콘솔에 WARNING 이상만 (오류만)
logger = TranslationLogger(console_level=logging.WARNING)

# 콘솔 출력 없음 (파일만)
logger = TranslationLogger(console_level=logging.CRITICAL + 1)
```

---

## ⚙️ GUI 설정 관리 (향후 구현 예정)

### 계획된 기능

#### 1. API 설정 탭
- **API 키 편집**: 직접 입력 및 저장
- **모델 선택**: Sonnet 4.5 / Sonnet 4 / Haiku 4
- **파라미터 조정**: Temperature, Max Tokens
- **테스트 연결**: API 키 유효성 검증

#### 2. 용어집 탭
- **JSON 에디터**: 구문 강조 및 검증
- **도메인별 용어**: electronics, chemistry, mechanical, biotech
- **금지 용어**: detach, substrate 등
- **저장/다시 로드**: 즉시 반영

#### 3. QA 규칙 탭
- **규칙 편집**: style_guide.json 직접 수정
- **규칙 활성화/비활성화**: 체크박스로 on/off
- **심각도 조정**: critical / major / minor
- **커스텀 규칙 추가**

#### 4. 로그 뷰어 탭
- **로그 파일 목록**: logs/ 디렉토리 자동 스캔
- **로그 내용 표시**: 구문 강조
- **필터링**: 레벨별, 키워드별
- **검색**: 특정 문자열 찾기
- **내보내기**: 선택한 로그 복사/저장

---

## 📊 로그 분석 예시

### 성공적인 번역
```
2025-11-15 04:13:06 | INFO | 번역 작업 시작
2025-11-15 04:13:06 | INFO | 파일 읽기 성공: input.txt
2025-11-15 04:13:07 | INFO | STEP 1: 문서 분석 시작
2025-11-15 04:13:08 | INFO | STEP 2: Translation Memory 검색
2025-11-15 04:13:10 | INFO | STEP 3: 번역 수행 - 초벌 번역
2025-11-15 04:13:15 | INFO | API 호출 성공: claude-sonnet-4-5 (토큰: 1500)
2025-11-15 04:13:21 | INFO | STEP 4: 품질 검증 (QA)
2025-11-15 04:13:21 | INFO | QA 결과: ✅ PASS
2025-11-15 04:13:22 | INFO | STEP 5: Translation Memory 저장
2025-11-15 04:13:23 | INFO | 파일 저장 성공: output.txt
2025-11-15 04:13:26 | INFO | 번역 작업 완료 ✅
```

### 파일 읽기 오류
```
2025-11-15 04:15:10 | INFO | 번역 작업 시작
2025-11-15 04:15:10 | ERROR | 파일 읽기 실패: input.txt (txt) - [Errno 2] No such file or directory
2025-11-15 04:15:10 | ERROR | 번역 작업 실패 ❌
```

### API 오류
```
2025-11-15 04:20:30 | INFO | STEP 3: 번역 수행 - 초벌 번역
2025-11-15 04:20:35 | ERROR | API 호출 실패: claude-sonnet-4-5 - rate_limit_error: Rate limit exceeded
2025-11-15 04:20:35 | ERROR | 번역 작업 실패 ❌
```

### QA 실패
```
2025-11-15 04:25:50 | INFO | STEP 4: 품질 검증 (QA)
2025-11-15 04:25:50 | INFO | 총 위반 사항: 5개
2025-11-15 04:25:50 | INFO | Critical: 1, Major: 3, Minor: 1
2025-11-15 04:25:50 | WARNING | QA 결과: ❌ FAIL
2025-11-15 04:25:51 | INFO | 파일 저장 성공: output.txt (품질 저하 경고)
```

---

## 🔍 문제 해결

### Q: 로그 파일이 생성되지 않아요
A: `logs/` 디렉토리가 자동 생성됩니다. 권한 문제가 있다면:
```bash
mkdir -p logs
chmod 755 logs
```

### Q: 로그 파일이 너무 많아요
A: 오래된 로그 정리:
```bash
# 7일 이상 된 로그 삭제
find logs/ -name "translation_*.log" -mtime +7 -delete

# 또는 최신 10개만 유지
ls -t logs/translation_*.log | tail -n +11 | xargs rm -f
```

### Q: 로그에 한글이 깨져요
A: UTF-8 인코딩으로 열어야 합니다:
```bash
# macOS/Linux
cat logs/translation_*.log

# Windows (PowerShell)
Get-Content logs/translation_*.log -Encoding UTF8
```

### Q: 콘솔 출력을 줄이고 싶어요
A: 로거 초기화 시 레벨 조정:
```python
logger = TranslationLogger(console_level=logging.WARNING)  # 경고 이상만
```

---

## 📁 파일 구조

```
patent-translation-system/
├── src/
│   ├── logger.py                 # 로깅 시스템 (신규)
│   ├── pipeline.py               # 로거 통합 필요
│   ├── translator.py             # 로거 통합 필요
│   └── qa_checker.py             # 로거 통합 필요
│
├── logs/                          # 로그 디렉토리 (자동 생성)
│   ├── translation_*.log
│   └── ...
│
├── config/
│   ├── api_config.yaml           # API 설정
│   ├── terminology.json          # 용어집
│   └── style_guide.json          # QA 규칙
│
└── gui_app.py                     # GUI (설정 관리 추가 예정)
```

---

## ✅ 향후 작업

### 로깅 시스템
- [x] 로거 모듈 생성 (`logger.py`)
- [ ] pipeline.py 로거 통합
- [ ] translator.py 로거 통합
- [ ] qa_checker.py 로거 통합
- [ ] GUI 진행 상황에 로그 연동

### 설정 관리
- [ ] GUI 설정 탭 재설계
- [ ] API 키 편집 기능
- [ ] 용어집 에디터 (JSON)
- [ ] QA 규칙 에디터 (JSON)
- [ ] 로그 뷰어 내장
- [ ] 설정 유효성 검증

---

**📝 로깅 시스템이 준비되었습니다!**

이제 모든 번역 과정이 상세하게 기록되어 문제 해결이 훨씬 쉬워집니다.
