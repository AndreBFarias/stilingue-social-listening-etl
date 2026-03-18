#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/.venv/bin/activate"
pip install pyinstaller
pyinstaller --onefile --name stilingue_etl "${SCRIPT_DIR}/src/pipeline.py"
echo "Executavel gerado em dist/stilingue_etl"
echo "Copie dist/stilingue_etl.exe e o .env para o servidor Windows"
