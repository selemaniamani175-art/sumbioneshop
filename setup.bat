@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo        MAUZO PRO - FIRST TIME SETUP
echo ========================================
if not exist venv (py -m venv venv)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py setup_roles
if not exist db.sqlite3 echo Database setup complete.
echo.
echo ========================================
echo Setup complete.
echo Login: admin / admin12345
echo Run: run.bat
echo ========================================
pause
