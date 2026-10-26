@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo.
echo Phantom Access -^> http://localhost:5000
echo.
python app.py
