@echo off
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (echo Virtual environment not found. Run setup.bat first.&pause&exit /b 1)
call venv\Scripts\activate.bat
python manage.py check
python manage.py runserver 127.0.0.1:8000
