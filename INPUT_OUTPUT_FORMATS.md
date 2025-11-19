# 📥📤 입출력 파일 형식 가이드

## 🎯 지원 형식 요약

### 입력 (Input)
- ✅ `.txt` - 텍스트 파일
- ✅ `.docx` - Word 문서
- ✅ `.pdf` - PDF 파일

### 출력 (Output)
- ✅ `.txt` - 텍스트 파일
- ✅ `.docx` - Word 문서 ⭐ **실무 추천!**

## 💡 실무 권장 조합

### 🥇 최고 추천: Word → Word
```bash
uv run python main.py translate input.docx -o output.docx --type claim
```
**장점:**
- ✅ 실무에서 바로 사용 가능
- ✅ 서식 편집 용이
- ✅ 검토 과정에서 수정 편리
- ✅ 문단 구조 자동 유지

### 🥈 추천: Word → 텍스트
```bash
uv run python main.py translate input.docx -o output.txt --type claim
```
**장점:**
- ✅ 가벼운 파일
- ✅ 모든 편집기에서 열람
- ✅ 버전 관리 용이

### 🥉 추천: PDF → Word
```bash
uv run python main.py translate input.pdf -o output.docx --type specification
```
**장점:**
- ✅ PDF 자동 변환
- ✅ Word로 편집 가능

## 📋 사용 예시

### 청구항 번역 (Word → Word)
```bash
# 입력: claim.docx
# 출력: claim_ko.docx
uv run python main.py translate claim.docx -o claim_ko.docx --type claim
```

### 명세서 번역 (PDF → Word)
```bash
# 입력: specification.pdf
# 출력: spec_ko.docx
uv run python main.py translate specification.pdf -o spec_ko.docx --type specification
```

### 배치 처리 (여러 Word 파일)
```bash
# 폴더 내 모든 Word 파일을 Word로 번역
for file in input/*.docx; do
    filename=$(basename "$file" .docx)
    uv run python main.py translate "$file" -o "output/${filename}_ko.docx" --type claim
done
```

## 🔧 형식 자동 감지

시스템이 파일 확장자를 보고 자동으로 형식을 판단하므로, **별도 옵션 불필요**:

```bash
# .txt 파일 → 자동으로 텍스트로 읽기
uv run python main.py translate input.txt -o output.docx

# .docx 파일 → 자동으로 Word로 읽기
uv run python main.py translate input.docx -o output.docx

# .pdf 파일 → 자동으로 PDF로 읽기
uv run python main.py translate input.pdf -o output.docx
```

## 📊 형식별 특징 비교

| 형식 | 입력 속도 | 출력 품질 | 실무 활용도 | 비고 |
|------|-----------|-----------|------------|------|
| `.txt` | ⚡⚡⚡ | ⭐⭐ | 낮음 | 범용적이지만 서식 없음 |
| `.docx` | ⚡⚡ | ⭐⭐⭐ | **높음** | **실무 최적** 👍 |
| `.pdf` | ⚡ | ⭐⭐ | 중간 | 입력용으로만 권장 |

## 💡 팁

### Word 출력 사용 시 장점
1. **즉시 편집 가능**: 번역 후 바로 검토/수정
2. **서식 적용**: 글꼴, 크기, 스타일 쉽게 변경
3. **협업 용이**: Track Changes 기능 활용
4. **최종 제출**: 그대로 제출 가능

### 언제 텍스트 출력을 사용하나?
- 버전 관리 시스템 사용 시 (Git)
- 간단한 확인만 필요할 때
- 다른 도구로 추가 처리 시

## ❓ FAQ

**Q: Word 파일이 가장 추천되는 이유는?**
A: 실무에서 특허 문서는 주로 Word로 작성/편집되며, 번역 후 검토 과정에서 수정이 필요한 경우가 많아 Word 형식이 가장 실용적입니다.

**Q: PDF는 입력만 가능한가요?**
A: 네, 현재 PDF는 입력 형식으로만 지원됩니다. 출력은 `.txt` 또는 `.docx`로 하시면 됩니다.

**Q: 출력 파일명에 확장자를 안 쓰면?**
A: 확장자가 없으면 기본적으로 텍스트 파일(.txt)로 저장됩니다.

---

**💼 실무 워크플로우 예시:**

```
1. 고객으로부터 Word 파일 수령 (claim.docx)
   ↓
2. 자동 번역
   $ uv run python main.py translate claim.docx -o claim_ko.docx --type claim
   ↓
3. Word에서 번역 검토 및 수정 (claim_ko.docx)
   ↓
4. 최종 파일 제출 (claim_ko.docx)
```

**🎉 간단하고 효율적입니다!**
