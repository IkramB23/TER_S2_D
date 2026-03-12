@echo off
REM ========================================
REM Générateur de Labyrinthes Pac-Man
REM Launcher Windows - TER S2
REM ========================================

setlocal enabledelayedexpansion

cls

echo.
echo ===============================================
echo   Generateur de Labyrinthes Pac-Man v1.0
echo   TER S2 - Groupe D
echo ===============================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Python depuis https://www.python.org/
    echo Assurez-vous de cocher "Add Python to PATH" lors de l'installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python detecte
echo.

REM Check if requirements are installed
echo [INFO] Verification des dependances...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation des dependances...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Impossible d'installer les dependances
        pause
        exit /b 1
    )
)

echo [OK] Dependances verifiees
echo.

REM Start the application
echo [INFO] Demarrage de l'application...
echo.
echo ===============================================
echo   L'application est accessible sur:
echo   http://localhost:5000
echo   
echo   Appuyez sur Ctrl+C pour arreter
echo ===============================================
echo.

python app.py

pause
