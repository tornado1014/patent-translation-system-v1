#!/bin/bash
# 특허 번역 시스템 설치 스크립트
# 사용법: ./install.sh [대상_디렉토리]

set -e  # 오류 발생 시 중단

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}특허 번역 시스템 설치 스크립트${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 현재 스크립트 위치 (소스 디렉토리)
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 대상 디렉토리 확인
if [ -z "$1" ]; then
    echo -e "${RED}오류: 대상 디렉토리를 지정해주세요.${NC}"
    echo ""
    echo "사용법:"
    echo "  ./install.sh [대상_디렉토리]"
    echo ""
    echo "예시:"
    echo "  ./install.sh ~/Documents/NewProject"
    echo "  ./install.sh /Users/earendel/Library/CloudStorage/OneDrive-개인/경력관리/SJ/Translation/SuccessGlo"
    exit 1
fi

TARGET_DIR="$1"

# 대상 디렉토리 생성 (없으면)
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}대상 디렉토리가 없습니다. 생성합니다: ${TARGET_DIR}${NC}"
    mkdir -p "$TARGET_DIR"
fi

echo -e "${GREEN}✓ 소스 디렉토리: ${SOURCE_DIR}${NC}"
echo -e "${GREEN}✓ 대상 디렉토리: ${TARGET_DIR}${NC}"
echo ""

# 설치 확인
read -p "계속 진행하시겠습니까? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}설치가 취소되었습니다.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}설치를 시작합니다...${NC}"
echo ""

# 1. 핵심 파일 복사
echo -e "${BLUE}[1/6] 핵심 파일 복사 중...${NC}"

# 소스 코드
cp -r "$SOURCE_DIR/src" "$TARGET_DIR/"
echo "  ✓ src/ 디렉토리 복사 완료"

# 설정 파일
cp -r "$SOURCE_DIR/config" "$TARGET_DIR/"
echo "  ✓ config/ 디렉토리 복사 완료"

# GUI 앱
cp "$SOURCE_DIR/gui_app.py" "$TARGET_DIR/"
echo "  ✓ gui_app.py 복사 완료"

# 실행 스크립트
cp "$SOURCE_DIR/run_gui.sh" "$TARGET_DIR/"
chmod +x "$TARGET_DIR/run_gui.sh"
echo "  ✓ run_gui.sh 복사 완료"

# pyproject.toml
cp "$SOURCE_DIR/pyproject.toml" "$TARGET_DIR/"
echo "  ✓ pyproject.toml 복사 완료"

# README 및 문서
cp "$SOURCE_DIR/README.md" "$TARGET_DIR/" 2>/dev/null || echo "  ⚠ README.md 없음 (선택 사항)"
cp "$SOURCE_DIR/QUICKSTART.md" "$TARGET_DIR/" 2>/dev/null || echo "  ⚠ QUICKSTART.md 없음 (선택 사항)"
cp "$SOURCE_DIR/AUTO_SECTION_FEATURE.md" "$TARGET_DIR/" 2>/dev/null || echo "  ⚠ AUTO_SECTION_FEATURE.md 없음 (선택 사항)"
cp "$SOURCE_DIR/LOGGING_AND_SETTINGS.md" "$TARGET_DIR/" 2>/dev/null || echo "  ⚠ LOGGING_AND_SETTINGS.md 없음 (선택 사항)"

echo ""

# 2. 필요한 디렉토리 생성
echo -e "${BLUE}[2/6] 작업 디렉토리 생성 중...${NC}"
mkdir -p "$TARGET_DIR/input"
mkdir -p "$TARGET_DIR/output"
mkdir -p "$TARGET_DIR/logs"
mkdir -p "$TARGET_DIR/tm_database"
echo "  ✓ input/, output/, logs/, tm_database/ 생성 완료"
echo ""

# 3. .env 파일 복사 (API 키 포함)
echo -e "${BLUE}[3/6] 환경 설정 파일 복사 중...${NC}"
if [ -f "$TARGET_DIR/.env" ]; then
    echo -e "${YELLOW}  ⚠ .env 파일이 이미 존재합니다. 건너뜁니다.${NC}"
else
    if [ -f "$SOURCE_DIR/.env" ]; then
        # 소스 디렉토리의 .env 파일 복사 (API 키 포함)
        cp "$SOURCE_DIR/.env" "$TARGET_DIR/.env"
        echo "  ✓ .env 파일 복사 완료 (API 키 포함)"
    else
        # .env 파일이 없으면 템플릿 생성
        cat > "$TARGET_DIR/.env" << 'EOF'
# Claude API 키 (필수)
# GUI의 설정 탭에서 입력하거나 직접 편집하세요
ANTHROPIC_API_KEY=your-api-key-here

# 선택 사항
# LOG_LEVEL=INFO
EOF
        echo -e "${YELLOW}  ⚠ 소스 디렉토리에 .env 파일이 없습니다. 템플릿을 생성했습니다.${NC}"
        echo -e "${YELLOW}  → GUI 설정 탭에서 API 키를 입력하세요.${NC}"
    fi
fi
echo ""

# 4. .gitignore 파일 생성
echo -e "${BLUE}[4/6] .gitignore 파일 생성 중...${NC}"
cat > "$TARGET_DIR/.gitignore" << 'EOF'
# API 키 및 환경 변수
.env
*.env

# 데이터베이스
tm_database/*.db
*.db

# 로그 파일
logs/*.log

# 출력 파일
output/*.docx
output/*.txt
output/*.pdf

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store

# uv
.venv/
EOF
echo "  ✓ .gitignore 생성 완료"
echo ""

# 5. Python 가상환경 및 의존성 설치
echo -e "${BLUE}[5/6] Python 의존성 설치 중...${NC}"
cd "$TARGET_DIR"

# uv 설치 확인
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}  ⚠ uv가 설치되어 있지 않습니다. 설치 중...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# 의존성 직접 설치 (editable 모드 대신)
echo "  uv를 사용하여 의존성을 설치합니다..."
uv venv
uv pip install anthropic python-docx PyQt6 python-dotenv
echo "  ✓ 의존성 설치 완료"
echo ""

# 6. 설치 완료 메시지
echo -e "${BLUE}[6/6] 설치 정보 파일 생성 중...${NC}"
cat > "$TARGET_DIR/INSTALLATION_INFO.txt" << EOF
========================================
특허 번역 시스템 설치 정보
========================================

설치 일시: $(date)
설치 경로: $TARGET_DIR
소스 경로: $SOURCE_DIR

========================================
다음 단계
========================================

1. GUI 실행:
   ./run_gui.sh

   또는

   uv run python gui_app.py

2. 테스트:
   - 샘플 파일을 input/ 폴더에 넣으세요
   - GUI에서 번역 탭을 열고 파일을 선택하세요
   - 번역 시작 버튼을 클릭하세요

========================================
주요 기능
========================================

✓ 자동 섹션 분류 (제목/요약/청구항/명세서)
✓ 10개 카테고리 QA 검사
✓ Translation Memory (TM) 시스템
✓ Self-review 기능
✓ 상세 로깅
✓ GUI 설정 관리

========================================
문서
========================================

- README.md - 전체 가이드
- QUICKSTART.md - 빠른 시작
- AUTO_SECTION_FEATURE.md - 자동 섹션 분류
- LOGGING_AND_SETTINGS.md - 로깅 및 설정

========================================
EOF
echo "  ✓ INSTALLATION_INFO.txt 생성 완료"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 설치 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}다음 단계:${NC}"
echo ""
echo "1. 대상 디렉토리로 이동:"
echo -e "   ${YELLOW}cd \"$TARGET_DIR\"${NC}"
echo ""
echo "2. GUI 실행:"
echo -e "   ${YELLOW}./run_gui.sh${NC}"
echo ""
if [ -f "$SOURCE_DIR/.env" ]; then
    echo -e "${GREEN}✓ API 키가 자동으로 설정되었습니다!${NC}"
    echo ""
else
    echo "3. 설정 탭에서 API 키 입력"
    echo ""
fi
echo -e "${BLUE}자세한 내용은 다음 파일을 참조하세요:${NC}"
echo -e "   ${YELLOW}$TARGET_DIR/INSTALLATION_INFO.txt${NC}"
echo ""
