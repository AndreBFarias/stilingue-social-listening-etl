#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/.venv/bin/activate"
pip install pyinstaller
pyinstaller --onefile --name whisper_pulse "${SCRIPT_DIR}/src/pipeline.py"
echo "Executavel gerado em dist/whisper_pulse"
echo "Copie dist/whisper_pulse.exe e o .env para o servidor Windows"
