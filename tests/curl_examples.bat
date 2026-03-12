@echo off
REM ========================================
REM Exemples de commandes Curl (Windows)
REM Générateur de Labyrinthes Pac-Man - TER S2
REM ========================================

setlocal enabledelayedexpansion

set LOCAL_URL=http://localhost:5000
set RENDER_URL=https://pacman_S2_D.onrender.com
set BASE_URL=%LOCAL_URL%

echo.
echo 🎮 Exemples d'utilisation du Web Service Maze Pacman
echo ====================================================
echo.
echo ℹ️  BASE_URL: %BASE_URL%
echo.

REM ========================================
REM 1. Maze par défaut (21x21)
REM ========================================
echo 1️⃣  Générer un labyrinthe par défaut (21x21)
echo Commande:
echo   curl "%BASE_URL%/maze"
echo.
curl -s "%BASE_URL%/maze" | jq "."
echo.
echo.

REM ========================================
REM 2. Maze personnalisé - Petite taille
REM ========================================
echo 2️⃣  Générer un petit labyrinthe (11x11)
echo Commande:
echo   curl "%BASE_URL%/maze?width=11^&height=11"
echo.
curl -s "%BASE_URL%/maze?width=11&height=11" | jq ".width, .height"
echo.
echo.

REM ========================================
REM 3. Maze grande taille
REM ========================================
echo 3️⃣  Générer un grand labyrinthe (51x51)
echo Commande:
echo   curl "%BASE_URL%/maze?width=51^&height=51"
echo.
curl -s "%BASE_URL%/maze?width=51&height=51" | jq ".width, .height"
echo.
echo.

REM ========================================
REM 4. Maze avec boucles (25%%)
REM ========================================
echo 4️⃣  Générer un labyrinthe avec 25%% de boucles
echo Commande:
echo   curl "%BASE_URL%/maze?width=21^&height=21^&loop_percent=25"
echo.
curl -s "%BASE_URL%/maze?width=21&height=21&loop_percent=25" | jq ".loop_percent"
echo.
echo.

REM ========================================
REM 5. Maze avec beaucoup de boucles (75%%)
REM ========================================
echo 5️⃣  Générer un labyrinthe avec 75%% de boucles
echo Commande:
echo   curl "%BASE_URL%/maze?width=21^&height=21^&loop_percent=75"
echo.
curl -s "%BASE_URL%/maze?width=21&height=21&loop_percent=75" | jq ".loop_percent"
echo.
echo.

REM ========================================
REM 6. Enregistrer un maze en JSON
REM ========================================
echo 6️⃣  Télécharger un labyrinthe en JSON
echo Commande:
echo   curl "%BASE_URL%/maze?width=21^&height=21" -o maze.json
echo.
curl -s "%BASE_URL%/maze?width=21&height=21" -o "%TEMP%\maze.json"
echo ✅ Fichier créé: %TEMP%\maze.json
echo.
echo.

REM ========================================
REM 7. Vérifier la structure JSON
REM ========================================
echo 7️⃣  Structure JSON d'un labyrinthe
echo Commande:
echo   curl -s "%BASE_URL%/maze?width=5^&height=5" | jq "keys"
echo.
curl -s "%BASE_URL%/maze?width=5&height=5" | jq "keys"
echo.
echo.

REM ========================================
REM 8. Test de validation - Entrée invalide
REM ========================================
echo 8️⃣  Test d'erreur - Largeur invalide (0)
echo Commande:
echo   curl -w "Status: %%{http_code}" "%BASE_URL%/maze?width=0^&height=21"
echo.
curl -s -w "Status: %%{http_code}" "%BASE_URL%/maze?width=0&height=21"
echo.
echo.

REM ========================================
REM 9. Statistiques
REM ========================================
echo 9️⃣  Afficher les statistiques d'un labyrinthe
echo Commande:
echo   curl -s "%BASE_URL%/maze?width=21^&height=21" | jq "{width, height, loop_percent}"
echo.
curl -s "%BASE_URL%/maze?width=21&height=21" | jq "{width, height, loop_percent}"
echo.
echo.

REM ========================================
REM 10. Afficher JSON complet
REM ========================================
echo 1️⃣0️⃣ Afficher le contenu complet d'un petit labyrinthe
echo Commande:
echo   curl -s "%BASE_URL%/maze?width=5^&height=5" | jq "."
echo.
curl -s "%BASE_URL%/maze?width=5&height=5" | jq "."
echo.
echo.

echo ====================================================
echo ✅ Fin des exemples de test
echo.
echo Pour modifier la BASE_URL:
echo   - Local:  set BASE_URL=http://localhost:5000
echo   - Render: set BASE_URL=https://pacman_S2_D.onrender.com
echo.
echo Pour installer jq sur Windows:
echo   choco install jq
echo   ou télécharger depuis: https://stedolan.github.io/jq/
echo.

pause
