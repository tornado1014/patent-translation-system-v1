# 🎁 독립 실행 파일 만들기

PyInstaller를 사용하여 Python 설치 없이 실행 가능한 앱 만들기

## 📦 PyInstaller 설치

```bash
uv add pyinstaller
```

## 🔨 실행 파일 생성

### macOS용 앱 빌드
```bash
uv run pyinstaller --name="특허번역기" \
    --windowed \
    --onefile \
    --icon=icon.icns \
    --add-data="config:config" \
    --add-data="src:src" \
    gui_app.py
```

### Windows용 실행 파일 빌드
```bash
uv run pyinstaller --name="특허번역기" ^
    --windowed ^
    --onefile ^
    --icon=icon.ico ^
    --add-data="config;config" ^
    --add-data="src;src" ^
    gui_app.py
```

### Linux용 실행 파일 빌드
```bash
uv run pyinstaller --name="특허번역기" \
    --windowed \
    --onefile \
    --add-data="config:config" \
    --add-data="src:src" \
    gui_app.py
```

## 📂 결과물

빌드 완료 후:
- `dist/` 폴더에 실행 파일 생성
- macOS: `특허번역기.app`
- Windows: `특허번역기.exe`
- Linux: `특허번역기`

## 🚀 배포

### macOS
```bash
# DMG 파일 생성 (선택사항)
hdiutil create -volname "특허번역기" -srcfolder dist/특허번역기.app -ov -format UDZO 특허번역기.dmg
```

### Windows
```bash
# Inno Setup 등으로 설치 프로그램 생성 가능
```

## ⚠️ 주의사항

### 1. API 키 포함 여부
- `.env` 파일은 포함되지 않음
- 사용자가 직접 설정 필요
- 또는 첫 실행 시 API 키 입력 창 추가

### 2. 의존성 문제
- PyQt5, docling 등 대용량 패키지 포함
- 실행 파일 크기가 클 수 있음 (100MB 이상)

### 3. 권한 문제
- macOS: 서명/공증 필요 (배포 시)
- Windows: SmartScreen 경고 가능

## 💡 대안: 간소화 버전

크기를 줄이려면:

```bash
# 핵심 기능만 포함
uv run pyinstaller --name="특허번역기_Lite" \
    --windowed \
    --onefile \
    --exclude-module matplotlib \
    --exclude-module scipy \
    gui_app.py
```

## 🎯 권장 배포 방법

### 개인 사용
- Python + UV 설치 후 스크립트 실행 (현재 방식)
- 가장 간단하고 업데이트 용이

### 팀 배포
- Git 저장소 공유
- 설치 스크립트 제공

### 일반 사용자 배포
- PyInstaller로 실행 파일 생성
- 설치 가이드 포함

## 📝 spec 파일 커스터마이징

```python
# patent_translator.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'anthropic',
        'docx',
        'docling',
        'chromadb',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='특허번역기',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='특허번역기.app',
    icon='icon.icns',
    bundle_identifier='com.patent.translator',
)
```

사용:
```bash
uv run pyinstaller patent_translator.spec
```

## 🔧 문제 해결

### "모듈을 찾을 수 없습니다" 오류
```bash
# hiddenimports에 추가
--hidden-import=모듈명
```

### GUI가 표시되지 않음
```bash
# --windowed 옵션 확인
# 또는 --noconsole 사용
```

### 실행 파일이 너무 큼
```bash
# UPX 압축 사용
--upx-dir=/path/to/upx
```

---

**현재로서는 Python + UV 환경에서 실행하는 것을 권장합니다.**
**필요시 위 가이드를 참고하여 독립 실행 파일을 만들 수 있습니다.** ✨
