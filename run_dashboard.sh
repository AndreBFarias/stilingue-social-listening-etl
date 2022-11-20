#!/bin/bash
source .venv/bin/activate 2>/dev/null || true
streamlit run dashboard/app.py
