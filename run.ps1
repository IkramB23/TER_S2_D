# ========================================
# Générateur de Labyrinthes Pac-Man
# Launcher PowerShell - TER S2
# ========================================

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   Generateur de Labyrinthes Pac-Man v1.0" -ForegroundColor Cyan
Write-Host "   TER S2 - Groupe D" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Set script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if Python is installed
try {
    $PythonVersion = python --version 2>&1
    Write-Host "[OK] Python detecte: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python n'est pas installe ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Veuillez installer Python depuis https://www.python.org/" -ForegroundColor Yellow
    Write-Host "Assurez-vous de cocher 'Add Python to PATH' lors de l'installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Appuyez sur Entree pour terminer"
    exit 1
}

Write-Host ""

# Check if requirements are installed
Write-Host "[INFO] Verification des dependances..." -ForegroundColor Blue
$FlaskInstalled = pip show flask 2>$null
if (-not $FlaskInstalled) {
    Write-Host "[INFO] Installation des dependances..." -ForegroundColor Blue
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Impossible d'installer les dependances" -ForegroundColor Red
        Read-Host "Appuyez sur Entree pour terminer"
        exit 1
    }
}

Write-Host "[OK] Dependances verifiees" -ForegroundColor Green
Write-Host ""

# Start the application
Write-Host "[INFO] Demarrage de l'application..." -ForegroundColor Blue
Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "   L'application est accessible sur:" -ForegroundColor Green
Write-Host "   http://localhost:5000" -ForegroundColor Cyan
Write-Host "   " -ForegroundColor Green
Write-Host "   Appuyez sur Ctrl+C pour arreter" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

python app.py

Read-Host "Appuyez sur Entree pour terminer"
