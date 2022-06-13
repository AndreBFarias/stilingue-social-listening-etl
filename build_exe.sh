#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo "  Build - Stilingue Social Listening ETL"
echo "============================================"
echo

if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 nao encontrado."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "Ambiente virtual ativado."

echo
echo "Instalando dependencias..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo
echo "Gerando executavel com PyInstaller..."
pip install pyinstaller > /dev/null 2>&1
pyinstaller stilingue_etl.spec --noconfirm

DIST_DIR="$SCRIPT_DIR/dist/stilingue-etl"
mkdir -p "$DIST_DIR"

mv -f dist/stilingue_etl "$DIST_DIR/stilingue_etl" 2>/dev/null || true
cp -f .env.example "$DIST_DIR/.env.example"
mkdir -p "$DIST_DIR/logs"

if [ -d "data/csv" ]; then
    echo "Copiando dados historicos..."
    cp -r data/csv "$DIST_DIR/data/"
else
    mkdir -p "$DIST_DIR/data/csv"
fi

echo
echo "============================================"
echo "  Build concluido!"
echo "============================================"
echo "Pasta distribuivel: $DIST_DIR"
