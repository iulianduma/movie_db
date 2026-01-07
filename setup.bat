@echo off
title CineTracker Setup
echo ====================================================
echo   CineTracker 2026 - Instalare Automata
echo ====================================================

:: 1. Verificare Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [EROARE] Python nu este instalat sau nu este in PATH.
    pause
    exit
)

:: 2. Creare Mediu Virtual (pentru a pastra curatenia)
echo [1/4] Se creeaza mediul virtual (venv)...
python -m venv venv

:: 3. Activare si Instalare Librarii
echo [2/4] Se instaleaza librariile (streamlit, requests, python-dotenv)...
call venv\Scripts\activate
pip install --upgrade pip
pip install streamlit requests python-dotenv

:: 4. Verificare fisier .env
if not exist .env (
    echo [3/4] ATENTIE: Fisierul .env nu a fost gasit!
    echo Se creeaza un fisier .env gol...
    echo TMDB_API_KEY=ta_cheia_aici > .env
    echo [!] Mergi in .env si pune cheia ta API de la TMDb.
) else (
    echo [3/4] Fisierul .env exista deja.
)

echo [4/4] Finalizat! 
echo.
echo ====================================================
echo Poti rula aplicatia scriind in terminal:
echo call venv\Scripts\activate
echo streamlit run app.py
echo ====================================================
echo.
pause