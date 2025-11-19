# ⚡ 빠른 시작 가이드

특허 번역 자동화 시스템을 5분 안에 시작하기

## 1️⃣ 환경 준비 (2분)

### Python 설치 확인
```bash
python --version  # Python 3.8 이상 필요
```

### 패키지 설치
```bash
# 현재 디렉토리로 이동
cd patent-translation-system

# 의존성 설치
pip install -r requirements.txt
```

## 2️⃣ API 키 설정 (1분)

### .env 파일 생성
```bash
cp .env.example .env
```

### API 키 입력
`.env` 파일을 열어 다음 내용 수정:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...  # 여기에 실제 API 키 입력
```

💡 **API 키 받기**: https://console.anthropic.com/

## 3️⃣ 첫 번역 실행 (2분)

### 테스트 샘플 번역
```bash
python main.py translate tests/test_samples/sample_claim.txt \
  -o output/test_result.txt \
  --type claim
```

### 결과 확인
```bash
# 번역 결과
cat output/test_result.txt

# QA 리포트
cat output/test_result.qa.txt
```

## 🎉 완료!

이제 특허 번역 자동화 시스템을 사용할 준비가 되었습니다!

## 📚 다음 단계

### 실제 문서 번역
```bash
# 청구항 번역
python main.py translate your_claim.txt -o output/claim_ko.txt --type claim

# 명세서 번역
python main.py translate your_spec.txt -o output/spec_ko.txt --type specification
```

### TM 활용
번역을 반복하면 Translation Memory가 자동으로 쌓입니다:
```bash
# TM 통계 확인
python main.py tm-stats
```

### 자체 검수 비활성화 (더 빠른 번역)
```bash
python main.py translate input.txt -o output.txt --no-review
```

## 💡 팁

1. **배치 처리**: 여러 파일을 폴더에 넣고 반복문으로 처리
2. **용어집 커스터마이징**: `config/terminology.json` 수정
3. **QA 규칙 조정**: `config/style_guide.json` 편집

## ❓ 문제 해결

### "ModuleNotFoundError" 오류
```bash
pip install -r requirements.txt
```

### "API key not found" 오류
```bash
# .env 파일 확인
cat .env

# API 키가 제대로 설정되었는지 확인
```

### 기타 문제
[README.md](README.md) 의 "문제 해결" 섹션 참고

---

**더 자세한 사용법은 [README.md](README.md) 참고**
