@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Build - Stilingue Social Listening ETL
echo ============================================
echo.

REM --- Diretorio do projeto (onde este .bat esta) ---
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

REM --- Verificar Python ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado no PATH.
    echo Instale Python 3.10+ e adicione ao PATH do sistema.
    pause
    exit /b 1
)
echo Python encontrado.

REM --- Criar venv se nao existir ---
if not exist ".venv\Scripts\activate.bat" (
    echo Criando ambiente virtual...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
)

REM --- Ativar venv ---
call .venv\Scripts\activate.bat
echo Ambiente virtual ativado.

REM --- Instalar dependencias ---
echo.
echo Instalando dependencias...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias.
    pause
    exit /b 1
)

REM --- Instalar PyInstaller ---
pip install pyinstaller >nul 2>&1

REM --- Limpar build anterior ---
echo.
echo Limpando build anterior...
if exist "build" rmdir /s /q "build"
if exist "dist\stilingue_etl.exe" del /f /q "dist\stilingue_etl.exe"

REM --- Gerar executavel ---
echo.
echo Gerando executavel com PyInstaller...
pyinstaller stilingue_etl.spec --noconfirm
if %errorlevel% neq 0 (
    echo ERRO: Falha ao gerar executavel.
    pause
    exit /b 1
)

REM --- Montar pasta distribuivel ---
set "DIST_DIR=%PROJECT_DIR%dist\stilingue-etl"
echo.
echo Montando pasta distribuivel em: %DIST_DIR%

if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

REM Mover exe
if exist "dist\stilingue_etl.exe" (
    move /Y "dist\stilingue_etl.exe" "%DIST_DIR%\stilingue_etl.exe" >nul
    echo   [OK] stilingue_etl.exe
) else (
    echo ERRO: stilingue_etl.exe nao foi gerado.
    pause
    exit /b 1
)

REM Copiar .env.example
copy /Y ".env.example" "%DIST_DIR%\.env.example" >nul
echo   [OK] .env.example

REM Copiar run.bat
copy /Y "run.bat" "%DIST_DIR%\run.bat" >nul 2>&1
echo   [OK] run.bat

REM Copiar scripts
if exist "scripts\configurar.bat" (
    copy /Y "scripts\configurar.bat" "%DIST_DIR%\configurar.bat" >nul
    echo   [OK] configurar.bat
)
if exist "scripts\instalar_agendamento.bat" (
    copy /Y "scripts\instalar_agendamento.bat" "%DIST_DIR%\instalar_agendamento.bat" >nul
    echo   [OK] instalar_agendamento.bat
)

REM Criar pasta logs
if not exist "%DIST_DIR%\logs" mkdir "%DIST_DIR%\logs"
echo   [OK] logs\

REM Copiar dados historicos (CSVs) se existirem
if exist "data\csv" (
    echo.
    echo Copiando dados historicos (CSVs)...
    xcopy /E /I /Y "data\csv" "%DIST_DIR%\data\csv" >nul
    echo   [OK] data\csv\ copiado com dados historicos
) else (
    if not exist "%DIST_DIR%\data\csv" mkdir "%DIST_DIR%\data\csv"
    echo   [OK] data\csv\ (vazio - backfill sera executado na primeira execucao)
)

REM --- Resumo ---
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
echo Proximo passo:
echo   1. Copie a pasta stilingue-etl para o servidor Windows
echo   2. Copie o .env.example para .env e configure o token
echo   3. Execute o stilingue_etl.exe
echo.

pause
