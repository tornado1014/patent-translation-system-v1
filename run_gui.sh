#!/bin/bash
# 특허 번역 GUI 앱 실행 스크립트

cd "$(dirname "$0")"

echo "🚀 특허 번역 자동화 시스템 GUI 시작..."
uv run python gui_app.py
