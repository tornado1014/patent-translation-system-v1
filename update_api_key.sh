#!/bin/bash
# 설치된 프로젝트의 API 키 업데이트 스크립트
# 사용법: ./update_api_key.sh [대상_디렉토리1] [대상_디렉토리2] ...

set -e

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}API 키 업데이트 스크립트${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 소스 디렉토리
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# .env 파일 확인
if [ ! -f "$SOURCE_DIR/.env" ]; then
    echo -e "${RED}오류: 소스 디렉토리에 .env 파일이 없습니다.${NC}"
    echo "먼저 원본 프로젝트에서 API 키를 설정하세요."
    exit 1
fi

echo -e "${GREEN}✓ 소스 .env 파일 확인됨${NC}"
echo ""

# 대상 디렉토리가 없으면 기본값 사용
if [ $# -eq 0 ]; then
    echo "대상 디렉토리를 지정하지 않았습니다."
    echo ""
    echo "사용법:"
    echo "  ./update_api_key.sh [대상1] [대상2] ..."
    echo ""
    echo "예시:"
    echo "  ./update_api_key.sh \"/path/to/SuccessGlo\" \"/path/to/베링랩\""
    exit 1
fi

# 각 대상 디렉토리 업데이트
for TARGET_DIR in "$@"; do
    echo -e "${BLUE}처리 중: ${TARGET_DIR}${NC}"

    if [ ! -d "$TARGET_DIR" ]; then
        echo -e "${YELLOW}  ⚠ 디렉토리가 존재하지 않습니다. 건너뜁니다.${NC}"
        echo ""
        continue
    fi

    if [ ! -f "$TARGET_DIR/.env" ]; then
        echo -e "${YELLOW}  ⚠ .env 파일이 없습니다. 생성합니다.${NC}"
    fi

    # .env 파일 복사
    cp "$SOURCE_DIR/.env" "$TARGET_DIR/.env"
    echo -e "${GREEN}  ✓ API 키 업데이트 완료${NC}"
    echo ""
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 모든 프로젝트 업데이트 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
