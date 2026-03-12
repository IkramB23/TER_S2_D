#!/bin/bash

# ========================================
# Exemples de commandes Curl
# Générateur de Labyrinthes Pac-Man - TER S2
# ========================================

echo "🎮 Exemples d'utilisation du Web Service Maze Pacman"
echo "=================================================="
echo ""

# URLs de base
LOCAL_URL="http://localhost:5000"
RENDER_URL="https://pacman_S2_D.onrender.com"

# Utilisez LOCAL_URL pour tester en local
# Utilisez RENDER_URL pour tester en production
BASE_URL=$LOCAL_URL

echo "ℹ️  BASE_URL: $BASE_URL"
echo ""

# ========================================
# 1. Maze par défaut (21x21, 0% boucles)
# ========================================
echo "1️⃣  Générer un labyrinthe par défaut (21x21)"
echo "Commande:"
echo "  curl \"$BASE_URL/maze\""
echo ""
curl -s "$BASE_URL/maze" | jq '.' | head -20
echo ""
echo ""

# ========================================
# 2. Maze personnalisé - Petite taille
# ========================================
echo "2️⃣  Générer un petit labyrinthe (11x11)"
echo "Commande:"
echo "  curl \"$BASE_URL/maze?width=11&height=11\""
echo ""
curl -s "$BASE_URL/maze?width=11&height=11" | jq '.width, .height'
echo ""
echo ""

# ========================================
# 3. Maze grande taille
# ========================================
echo "3️⃣  Générer un grand labyrinthe (51x51)"
echo "Commande:"
echo "  curl \"$BASE_URL/maze?width=51&height=51\""
echo ""
curl -s "$BASE_URL/maze?width=51&height=51" | jq '.width, .height'
echo ""
echo ""

# ========================================
# 4. Maze avec boucles (25%)
# ========================================
echo "4️⃣  Générer un labyrinthe avec 25% de boucles"
echo "Commande:"
echo "  curl \"$BASE_URL/maze?width=21&height=21&loop_percent=25\""
echo ""
curl -s "$BASE_URL/maze?width=21&height=21&loop_percent=25" | jq '.loop_percent'
echo ""
echo ""

# ========================================
# 5. Maze avec beaucoup de boucles (75%)
# ========================================
echo "5️⃣  Générer un labyrinthe avec 75% de boucles (plus complexe)"
echo "Commande:"
echo "  curl \"$BASE_URL/maze?width=21&height=21&loop_percent=75\""
echo ""
curl -s "$BASE_URL/maze?width=21&height=21&loop_percent=75" | jq '.loop_percent'
echo ""
echo ""

# ========================================
# 6. Enregistrer un maze en JSON
# ========================================
echo "6️⃣  Télécharger un labyrinthe en JSON"
echo "Commande:"
echo "  curl \"$BASE_URL/maze?width=21&height=21\" > maze.json"
echo ""
curl -s "$BASE_URL/maze?width=21&height=21" > /tmp/maze.json
echo "✅ Fichier créé: /tmp/maze.json"
echo ""
echo ""

# ========================================
# 7. Vérifier la structure JSON
# ========================================
echo "7️⃣  Structure JSON d'un labyrinthe"
echo "Commande:"
echo "  curl -s \"$BASE_URL/maze?width=5&height=5\" | jq 'keys'"
echo ""
curl -s "$BASE_URL/maze?width=5&height=5" | jq 'keys'
echo ""
echo ""

# ========================================
# 8. Test de validation - Entrée invalide
# ========================================
echo "8️⃣  Test d'erreur - Largeur invalide (0)"
echo "Commande:"
echo "  curl -w \"Status: %{http_code}\n\" \"$BASE_URL/maze?width=0&height=21\""
echo ""
curl -s -w "Status: %{http_code}\n" "$BASE_URL/maze?width=0&height=21"
echo ""
echo ""

# ========================================
# 9. Statistiques d'un maze
# ========================================
echo "9️⃣  Afficher les statistiques d'un labyrinthe"
echo "Commande:"
echo "  curl -s \"$BASE_URL/maze?width=21&height=21\" | jq '{width: .width, height: .height, loop_percent: .loop_percent}'"
echo ""
curl -s "$BASE_URL/maze?width=21&height=21" | jq '{width: .width, height: .height, loop_percent: .loop_percent}'
echo ""
echo ""

# ========================================
# 10. Boucle - Générer 5 labyrinthes aléatoires
# ========================================
echo "🔟 Générer 5 labyrinthes aléatoires"
echo "Commande:"
echo "  for i in {1..5}; do curl -s \"$BASE_URL/maze?width=11&height=11\" | jq '.width, .height'; done"
echo ""
for i in {1..5}; do
    SIZE=$((5 + RANDOM % 20))
    SIZE=$((SIZE * 2 + 1))  # Force nombre impair
    echo "  Labyrinthe $i: ${SIZE}x${SIZE}"
    curl -s "$BASE_URL/maze?width=$SIZE&height=$SIZE" | jq '.width, .height'
done
echo ""
echo ""

# ========================================
# 11. Health check
# ========================================
echo "1️⃣1️⃣ Vérifier que l'API est accessible (health check)"
echo "Commande:"
echo "  curl -w \"Status: %{http_code}\n\" \"$BASE_URL/health\""
echo ""
if curl -s "$BASE_URL/health" > /dev/null 2>&1; then
    echo "✅ API en ligne!"
else
    echo "❌ API indisponible"
fi
echo ""
echo ""

# ========================================
# 12. Afficher toutes les données d'un maze
# ========================================
echo "1️⃣2️⃣ Afficher le contenu complet d'un petit labyrinthe"
echo "Commande:"
echo "  curl -s \"$BASE_URL/maze?width=5&height=5\" | jq '.'"
echo ""
curl -s "$BASE_URL/maze?width=5&height=5" | jq '.'
echo ""
echo ""

echo "=================================================="
echo "✅ Fin des exemples de test"
echo ""
echo "Pour modifier la BASE_URL:"
echo "  - Local:  BASE_URL=\"http://localhost:5000\""
echo "  - Render: BASE_URL=\"https://pacman_S2_D.onrender.com\""
echo ""
echo "Pour installer jq (formatage JSON):"
echo "  Ubuntu/Debian: sudo apt-get install jq"
echo "  macOS: brew install jq"
echo "  Windows: choco install jq"
