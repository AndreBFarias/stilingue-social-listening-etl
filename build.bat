@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Build - Stilingue ETL (Windows .exe)
echo ============================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado no PATH.
    echo Instale Python 3.10+ e adicione ao PATH do sistema.
    pause
    exit /b 1
)
echo Python encontrado.

if not exist ".venv\Scripts\activate.bat" (
    echo Criando ambiente virtual...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat
echo Ambiente virtual ativado.

echo.
echo Instalando dependencias...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias.
    pause
    exit /b 1
)

pip install pyinstaller >nul 2>&1

echo.
echo Limpando build anterior...
if exist "build" rmdir /s /q "build"
if exist "dist\stilingue_etl.exe" del /f /q "dist\stilingue_etl.exe"

echo.
echo Gerando executavel com PyInstaller...
pyinstaller stilingue_etl.spec --noconfirm
if %errorlevel% neq 0 (
    echo ERRO: Falha ao gerar executavel.
    pause
    exit /b 1
)

set "DIST_DIR=%PROJECT_DIR%dist\stilingue-etl"
echo.
echo Montando pasta distribuivel em: %DIST_DIR%

if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

if exist "dist\stilingue_etl.exe" (
    move /Y "dist\stilingue_etl.exe" "%DIST_DIR%\stilingue_etl.exe" >nul
    echo   [OK] stilingue_etl.exe
) else (
    echo ERRO: stilingue_etl.exe nao foi gerado.
    pause
    exit /b 1
)

copy /Y ".env.example" "%DIST_DIR%\.env.example" >nul
echo   [OK] .env.example

if not exist "%DIST_DIR%\logs" mkdir "%DIST_DIR%\logs"
echo   [OK] logs\

if exist "data\csv" (
    echo.
    echo Copiando dados historicos (CSVs)...
    xcopy /E /I /Y "data\csv" "%DIST_DIR%\data\csv" >nul
    echo   [OK] data\csv\ copiado com dados historicos
) else (
    if not exist "%DIST_DIR%\data\csv" mkdir "%DIST_DIR%\data\csv"
    echo   [OK] data\csv\ (vazio - backfill na primeira execucao)
)

echo.
echo ============================================
echo   Build concluido com sucesso!
echo ============================================
echo.
echo Pasta distribuivel: %DIST_DIR%
echo.
echo Conteudo:
echo   stilingue_etl.exe      - Executavel principal
echo   .env.example           - Template de configuracao
echo   data\csv\              - Dados historicos
echo   logs\                  - Logs de execucao
echo.

pause
