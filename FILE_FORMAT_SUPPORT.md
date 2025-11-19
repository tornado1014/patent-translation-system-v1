# 📄 지원 파일 형식

특허 번역 자동화 시스템은 다양한 파일 형식을 지원합니다.

## ✅ 지원되는 파일 형식

### 1. 텍스트 파일 (.txt)
- **설명**: 가장 기본적인 형식
- **장점**: 빠르고 간단, 호환성 최고
- **사용 예시**:
  ```bash
  uv run python main.py translate input.txt -o output.txt --type claim
  ```

### 2. Word 문서 (.docx)
- **설명**: Microsoft Word 문서
- **장점**: 실무에서 가장 많이 사용
- **자동 처리**: 문단별로 텍스트 추출
- **사용 예시**:
  ```bash
  uv run python main.py translate input.docx -o output.txt --type claim
  ```
- **패키지**: `python-docx` (이미 설치됨 ✅)

### 3. PDF 파일 (.pdf)
- **설명**: PDF 문서
- **장점**: 레이아웃 보존된 문서
- **자동 처리**: Docling으로 마크다운 변환 후 번역
- **사용 예시**:
  ```bash
  uv run python main.py translate input.pdf -o output.txt --type specification
  ```
- **패키지**: `docling` (이미 설치됨 ✅)

## 🎯 실전 사용 예시

### 시나리오 1: Word 파일로 받은 청구항
```bash
# Word 파일 직접 번역
uv run python main.py translate claim.docx -o claim_ko.txt --type claim

# 자체 검수 없이 빠르게
uv run python main.py translate claim.docx -o claim_ko.txt --type claim --no-review
```

### 시나리오 2: PDF 특허 명세서
```bash
# PDF 파일 번역
uv run python main.py translate patent.pdf -o patent_ko.txt --type specification
```

### 시나리오 3: 배치 처리
```bash
# 폴더 내 모든 Word 파일 번역
for file in input/*.docx; do
    filename=$(basename "$file" .docx)
    uv run python main.py translate "$file" -o "output/${filename}_ko.txt" --type claim
done
```

## 📊 파일 형식별 처리 방식

| 형식 | 처리 방법 | 속도 | 정확도 |
|------|-----------|------|--------|
| .txt | 직접 읽기 | ⚡⚡⚡ | ✅✅✅ |
| .docx | 문단 추출 | ⚡⚡ | ✅✅✅ |
| .pdf | Docling 변환 | ⚡ | ✅✅ |

## 💡 팁

### Word 파일 사용 시
- **장점**: 실무에서 가장 많이 사용하는 형식
- **주의**: 표, 이미지는 텍스트만 추출됨
- **권장**: 청구항, 요약서 번역에 적합

### PDF 파일 사용 시
- **장점**: 레이아웃이 복잡한 문서도 처리 가능
- **주의**: 변환 시간이 더 소요됨
- **권장**: 전체 명세서 번역에 적합

### 텍스트 파일 사용 시
- **장점**: 가장 빠르고 정확
- **권장**: 이미 텍스트로 추출된 내용 번역

## 🔧 추가 파일 형식 지원

현재 시스템은 확장 가능하도록 설계되어 있습니다. 필요시 다음 형식도 추가 가능:

- `.rtf` (Rich Text Format)
- `.odt` (OpenDocument Text)
- `.html` (HTML 문서)

추가를 원하시면 `main.py`의 `translate` 함수를 수정하시면 됩니다.

## ❓ FAQ

**Q: Word 파일에 표가 있으면?**
A: 표 안의 텍스트도 추출되지만, 표 구조는 유지되지 않습니다. 필요시 텍스트로 미리 정리하는 것을 권장합니다.

**Q: PDF 파일이 이미지로 된 스캔본이면?**
A: Docling의 OCR 기능이 작동하지만, 정확도가 떨어질 수 있습니다. 가능하면 텍스트 레이어가 있는 PDF를 사용하세요.

**Q: 가장 권장하는 형식은?**
A: **Word (.docx) 파일**을 권장합니다. 실무에서 가장 많이 사용하며, 처리 속도와 정확도의 균형이 좋습니다.

---

**모든 파일 형식이 자동으로 감지되므로, 확장자만 맞다면 별도 옵션 없이 바로 사용 가능합니다!** ✨
