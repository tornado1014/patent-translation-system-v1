# 특허 번역 시스템 - 다른 프로젝트에 설치하기

## 📦 설치 방법

### 자동 설치 (권장)

설치 스크립트를 사용하면 모든 파일과 설정이 자동으로 복사되고 의존성이 설치됩니다.

```bash
# 기본 사용법
./install.sh [대상_디렉토리]

# 예시: SuccessGlo 프로젝트에 설치
./install.sh "/Users/earendel/Library/CloudStorage/OneDrive-개인/경력관리/SJ/Translation/SuccessGlo"

# 예시: 베링랩 프로젝트에 설치
./install.sh "/Users/earendel/Library/CloudStorage/OneDrive-개인/경력관리/SJ/Translation/베링랩"
```

### 설치 스크립트가 수행하는 작업

1. **핵심 파일 복사**
   - `src/` - 소스 코드
   - `config/` - 설정 파일 (스타일 가이드, 용어집, QA 체크리스트)
   - `gui_app.py` - GUI 애플리케이션
   - `run_gui.sh` - 실행 스크립트
   - 문서 파일들 (README, QUICKSTART 등)

2. **작업 디렉토리 생성**
   - `input/` - 번역할 파일
   - `output/` - 번역된 파일
   - `logs/` - 로그 파일
   - `tm_database/` - Translation Memory 데이터베이스

3. **환경 설정**
   - `.env` 파일 생성 (API 키 설정용)
   - `.gitignore` 생성 (민감한 파일 보호)

4. **Python 의존성 설치**
   - uv를 사용하여 가상환경 생성
   - 필요한 패키지 자동 설치:
     - anthropic (Claude API)
     - python-docx (Word 문서)
     - PyQt6 (GUI)
     - python-dotenv (환경 변수)

5. **설치 정보 파일 생성**
   - `INSTALLATION_INFO.txt` - 설치 정보 및 다음 단계 안내

---

## ✅ 설치 완료 후 할 일

### 1. 첫 번째 번역 테스트 (API 키 설정 불필요!)

```bash
# GUI 실행
./run_gui.sh

# 또는 직접 실행
uv run python gui_app.py
```

1. "번역" 탭 선택
2. 입력 파일 선택 (txt, docx, pdf)
3. 출력 파일 지정
4. 문서 유형 선택 또는 자동 섹션 분류 체크
5. "번역 시작" 클릭

---

## 📁 설치된 디렉토리 구조

```
SuccessGlo/  (또는 베링랩/)
├── src/                    # 소스 코드
│   ├── pipeline.py        # 번역 파이프라인
│   ├── translator.py      # Claude API 번역기
│   ├── qa_checker.py      # QA 검증 시스템
│   ├── tm_manager.py      # Translation Memory
│   ├── section_parser.py  # 섹션 자동 분류
│   └── logger.py          # 로깅 시스템
├── config/                 # 설정 파일
│   ├── style_guide.json   # 스타일 가이드
│   ├── terminology.json   # 용어집
│   └── QA_CHECKLIST.md    # QA 체크리스트
├── input/                  # 입력 파일 (번역할 파일)
├── output/                 # 출력 파일 (번역된 파일)
├── logs/                   # 로그 파일
├── tm_database/            # TM 데이터베이스
├── .venv/                  # Python 가상환경
├── gui_app.py             # GUI 애플리케이션
├── run_gui.sh             # 실행 스크립트
├── .env                   # API 키 및 환경 변수
└── INSTALLATION_INFO.txt  # 설치 정보
```

---

## 🎯 주요 기능

### 1. 자동 섹션 분류
전체 명세서를 한 번에 입력하면 자동으로 구분:
- 제목 (Title)
- 요약서 (Abstract)
- 청구항 (Claims) - 각 청구항별로 분리
- 명세서 (Specification)

### 2. 10개 카테고리 QA 검사
- 형식 검사 (온도, 퍼센트, 서열번호)
- 용어 일관성 검사
- 선행사 '상기' 검사
- 청구항 구조 검사
- 구두점 검사
- 도메인별 오역 검사
- 표준 용어 검사
- 수치 표현 검사
- 전환구 검사
- 청구항 명사구 구조 검사

### 3. Translation Memory (TM)
- 자동 저장 및 재사용
- 유사도 기반 매칭
- GUI에서 검색 가능

### 4. 상세 로깅
- 모든 번역 단계 기록
- 오류 추적
- GUI에서 로그 뷰어 제공

### 5. GUI 설정 관리
- API 키 설정
- 용어집 편집
- 로그 뷰어

---

## 🔧 설치 문제 해결

### uv가 설치되지 않은 경우

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 권한 오류

```bash
chmod +x install.sh
chmod +x run_gui.sh
```

### Python 버전 확인

```bash
python3 --version  # 3.10 이상 필요
```

---

## 📝 사용 예시

### 예시 1: 청구항만 번역

```bash
./run_gui.sh
```
1. 입력 파일: `claim.txt`
2. 문서 유형: "청구항 (claim)"
3. Self-review 활성화
4. 번역 시작

### 예시 2: 전체 명세서 자동 번역

```bash
./run_gui.sh
```
1. 입력 파일: `full_specification.txt` (전체 명세서)
2. ✅ "자동 섹션 분류" 체크
3. Self-review 활성화
4. 번역 시작

→ 자동으로 제목/요약/청구항/명세서 구분하여 번역

### 예시 3: TM 검색

```bash
./run_gui.sh
```
1. "Translation Memory" 탭 선택
2. 검색어 입력 (예: "substrate")
3. 유사도 임계값 조정 (70%)
4. 검색 버튼 클릭

---

## 🌟 각 프로젝트별 독립 운영 + API 키 공유

각 설치된 디렉토리는 **독립적**으로 동작하지만 **API 키는 자동으로 공유**됩니다:

- ✅ **API 키 자동 복사**: 설치 시 원본 프로젝트의 API 키가 자동으로 복사됨
- ✅ **독립적인 TM 데이터베이스**: 각 프로젝트의 번역 데이터는 별도 저장
- ✅ **독립적인 로그**: 각 프로젝트의 로그는 해당 디렉토리에만 저장
- ✅ **독립적인 용어집**: 용어집은 각 프로젝트별로 커스터마이징 가능
- ✅ **독립적인 가상환경**: Python 패키지 충돌 없음

### API 키 업데이트

원본 프로젝트에서 API 키를 변경한 후 다른 프로젝트들에도 적용하려면:

```bash
cd "/Users/earendel/Library/CloudStorage/OneDrive-개인/경력관리/SJ/Translation/JLT/patent-translation-system"

./update_api_key.sh \
  "/path/to/SuccessGlo" \
  "/path/to/베링랩"
```

---

## 📚 추가 문서

각 설치된 디렉토리에 다음 문서가 포함됩니다:

- `README.md` - 전체 사용 가이드
- `QUICKSTART.md` - 빠른 시작 가이드
- `AUTO_SECTION_FEATURE.md` - 자동 섹션 분류 상세 설명
- `LOGGING_AND_SETTINGS.md` - 로깅 및 설정 가이드
- `INSTALLATION_INFO.txt` - 설치 정보

---

## ✅ 설치 확인 체크리스트

- [ ] 설치 스크립트 실행 성공
- [ ] ✨ API 키 자동 복사 확인 (설정 필요 없음!)
- [ ] GUI 정상 실행 (`./run_gui.sh`)
- [ ] 테스트 파일로 번역 성공
- [ ] TM 검색 기능 작동 확인
- [ ] 로그 파일 생성 확인

---

## 🎉 완료!

이제 각 프로젝트 폴더에서 독립적으로 특허 번역 시스템을 사용할 수 있습니다.

문제가 발생하면 각 디렉토리의 `logs/` 폴더에서 오류 로그를 확인하세요.
