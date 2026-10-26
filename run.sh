#!/usr/bin/env bash
set -e
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo ""
echo "Phantom Access -> http://localhost:5000"
echo ""
python app.py
