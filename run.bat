@echo off
cd /d "%~dp0"
title 경영지원부 시스템 실행기

echo ========================================================
echo  [보안 환경] 로컬 가상환경(venv) 기반 시스템을 시작합니다.
echo ========================================================

:: 가상환경 활성화 후 Streamlit 실행
call venv\Scripts\activate
streamlit run app.py

pause