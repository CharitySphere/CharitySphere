@echo off

cd %~dp0

@echo off
setlocal

set VENV_DIR=venv

REM -------------------------
REM Setup / Activate venv
REM -------------------------
if not exist %VENV_DIR% (
    echo 📦 Installing requirements...
    python -m venv %VENV_DIR%

    call %VENV_DIR%\Scripts\activate.bat

    if exist requirements.txt (
        pip install -r requirements.txt
    ) else (
        echo 🚧 Warning: No requirements.txt found
    )
) else (
    if exist %VENV_DIR%\Scripts\activate.bat (
        call %VENV_DIR%\Scripts\activate.bat
    ) else (
        echo Virtual environment '%VENV_DIR%' directory not found.
        echo Using locally installed python instead
    )
)

REM -------------------------
REM Run migrations if pending
REM -------------------------
python manage.py showmigrations --plan | findstr "\[ \]" >nul
if %errorlevel%==0 (
    echo ✈️ Running migrations to database...
    python manage.py migrate
)

REM -------------------------
REM Open browser
REM -------------------------
start http://localhost:8000

REM -------------------------
REM Run server
REM -------------------------
python manage.py runserver
