@echo off
setlocal enabledelayedexpansion

set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

if not exist "data\csv\visao_geral" mkdir "data\csv\visao_geral"
if not exist "data\csv\sentimento_grupos" mkdir "data\csv\sentimento_grupos"
if not exist "data\csv\sentimento_temas" mkdir "data\csv\sentimento_temas"
if not exist "data\csv\linechart" mkdir "data\csv\linechart"
if not exist "data\csv\publicacoes" mkdir "data\csv\publicacoes"
if not exist "data\csv\ranking_evolutivo" mkdir "data\csv\ranking_evolutivo"
if not exist "consolidado" mkdir "consolidado"
if not exist "logs" mkdir "logs"

if not exist ".env" (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >nul
        echo Arquivo .env criado. Edite com seu token antes de continuar.
        notepad ".env"
        pause
        exit /b 0
    ) else (
        echo ERRO: .env.example nao encontrado.
        pause
        exit /b 1
    )
)

if exist "whisper_pulse.exe" (
    whisper_pulse.exe
) else (
    python -m src
)
