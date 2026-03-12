# Générateur de Labyrinthes Pac-Man - Guide d'Utilisation

## 📋 Table des matières
1. [Installation](#installation)
2. [Démarrage](#démarrage)
3. [Utilisation de l'interface](#utilisation)
4. [Paramètres](#paramètres)
5. [Téléchargement des données](#téléchargement)
6. [Raccourcis clavier](#raccourcis)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Installation

### Prérequis
- **Python 3.6+** - [Télécharger Python](https://www.python.org/)
- **Connexion Internet** (pour la première installation)

### Installation des dépendances

**Option 1: Utiliser le launcher (Recommandé)**
```bash
# Windows
python launcher.py

# Linux/Mac
python3 launcher.py
```

**Option 2: Installation manuelle**
```bash
pip install -r requirements.txt
```

---

## 🎮 Démarrage

### Windows

**Méthode 1: Double-cliquez sur `run.bat`**
- Le script se charge tout seul
- L'application s'ouvre automatiquement dans votre navigateur

**Méthode 2: PowerShell**
```powershell
.\run.ps1
```

**Méthode 3: Ligne de commande**
```cmd
python launcher.py
```

### Linux / macOS

```bash
# Rendre le script exécutable
chmod +x run.sh

# Lancer l'application
python3 launcher.py
```

### Accéder à l'application

Une fois démarrée, ouvrez votre navigateur et allez sur:
```
http://localhost:5000
```

---

## 💡 Utilisation de l'interface

### Vue générale
L'interface est divisée en trois zones:

1. **Panneau de contrôle** (à gauche)
   - Paramètres de génération
   - Boutons d'action

2. **Panneau de visualisation** (à droite)
   - Affiche le labyrinthe généré
   - Statistiques en temps réel

3. **Informations générales**
   - En-tête: Titre et description du projet
   - Pied de page: Crédits et informations techniques

### Générer un labyrinthe

1. **Ajuster les paramètres** (voir section [Paramètres](#paramètres) ci-dessous)
2. **Cliquer sur "✨ Générer un Labyrinthe"**
3. **Attendre la génération** (quelques secondes selon la taille)
4. **Le labyrinthe s'affiche** dans le panneau de visualisation

---

## ⚙️ Paramètres

### Largeur du labyrinthe
- **Plage**: 5 à 101 pixels
- **Contrainte**: Doit être un nombre **impair**
- **Valeur par défaut**: 21
- **Incrément**: +2 ou -2
- ℹ️ Plus la largeur est grande, plus le labyrinthe est complexe

### Hauteur du labyrinthe
- **Plage**: 5 à 101 pixels
- **Contrainte**: Doit être un nombre **impair**
- **Valeur par défaut**: 21
- **Incrément**: +2 ou -2
- ℹ️ Plus la hauteur est grande, plus le labyrinthe est complexe

### Pourcentage de boucles
- **Plage**: 0% à 100%
- **Valeur par défaut**: 25%
- **Type**: Curseur (slider)
- **Description**: 
  - **0%**: Labyrinthe parfait (un seul chemin entre deux points)
  - **25%**: Labyrinthes équilibrés avec quelques boucles
  - **50%**: Labyrinthes complexes avec de nombreuses boucles
  - **100%**: Labyrinthes fortement connectés

---

## 💾 Téléchargement des données

### Format JSON

Le fichier JSON contient:
```json
{
  "width": 21,
  "height": 21,
  "loop_percent": 25,
  "maze": [
    [0, 1, 0, 1, ...],
    [1, 1, 1, 1, ...],
    ...
  ],
  "generated_at": "2024-03-06T10:30:00Z",
  "metadata": {
    "algorithm": "Prim with loops",
    "team": "Ikram Benchalal, Nada Zina, Aya Haddoun",
    "project": "TER S2 - Labyrinth Generator"
  }
}
```

### Valeurs de la matrice
- **0**: Mur (noir sur l'interface)
- **1**: Couloir/Passage (blanc sur l'interface)

### Télécharger un labyrinthe
1. Générez un labyrinthe
2. Cliquez sur "💾 Télécharger (JSON)"
3. Le fichier se télécharge automatiquement
4. Format du nom: `maze_WIDTHxHEIGHT_TIMESTAMP.json`

---

## ⌨️ Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| **Entrée** (dans les champs largeur/hauteur) | Générer un labyrinthe |
| **Ctrl + G** / **Cmd + G** | Générer un labyrinthe |
| **Ctrl + S** / **Cmd + S** | Télécharger en JSON |

---

## 📊 Panneau de visualisation

### Affichage du labyrinthe
- **Blanc**: Couloirs/Passages accessibles
- **Noir**: Murs
- **Grille optionnelle**: Montre les cellules individuelles

### Statistiques
En bas du panneau, vous verrez:
- **Dimensions**: Largeur × Hauteur (pixels)
- **Cellules couloirs**: Nombre total de passages
- **Cellules murs**: Nombre total de murs

---

## 🔍 API REST

Si vous voulez utiliser l'API directement:

### Endpoint: `/maze`

**Requête**:
```
GET /maze?width=21&height=21&loop_percent=25
```

**Paramètres**:
| Paramètre | Type | Plage | Défaut |
|-----------|------|-------|--------|
| `width` | Integer | 5-101 (impair) | 21 |
| `height` | Integer | 5-101 (impair) | 21 |
| `loop_percent` | Integer | 0-100 | 25 |

**Réponse** (200 OK):
```json
{
  "width": 21,
  "height": 21,
  "loop_percent": 25,
  "maze": [[0,1,0,...], ...]
}
```

**Exemple avec curl**:
```bash
curl "http://localhost:5000/maze?width=21&height=21&loop_percent=25"
```

---

## 🐛 Troubleshooting

### L'application ne démarre pas
**Problème**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Python n'est pas reconnu
**Problème**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Vérifiez que Python est installé: `python --version`
2. Si ce n'est pas reconnu, [téléchargez Python](https://www.python.org/)
3. Lors de l'installation, cochez "Add Python to PATH"

### Le port 5000 est déjà utilisé
**Problème**: `Address already in use`

**Solution**:
1. Fermez l'autre application qui utilise le port 5000
2. Ou modifiez `app.py` et changez `port=5000` par un autre port (ex: `port=5001`)

### L'interface n'apparaît pas correctement
**Problème**: Affichage mal formaté ou CSS non chargé

**Solution**:
1. Actualisez la page (F5 ou Ctrl+R)
2. Vérifiez que le dossier `static/` existe et contient `styles.css` et `script.js`
3. Videz le cache du navigateur (Ctrl+Shift+Delete)

### Génération très lente
**Problème**: La génération prend plus de quelques secondes

**Solution**:
- C'est normal pour les très grandes dimensions (>81×81)
- L'algorithme de Prim a une complexité O(n²)
- Réduisez la largeur/hauteur pour des résultats plus rapides

### Erreur lors du téléchargement
**Problème**: Le fichier JSON ne se télécharge pas

**Solution**:
1. Vérifiez que le labyrinthe a bien été généré
2. Essayez avec un autre navigateur
3. Vérifiez les paramètres du pare-feu

---

## 📚 Documentation supplémentaire

### Algorithme utilisé
- **Algorithme de base**: Prim avec backtracking
- **Complexité**: O(width × height)
- **Ajout de boucles**: Suppression aléatoire de murs

### Structure du code
```
TER_S2_D/
├── app.py                 # Application Flask principale
├── launcher.py           # Launcher Python portable
├── run.bat              # Launcher Windows (CMD)
├── run.ps1              # Launcher Windows (PowerShell)
├── requirements.txt     # Dépendances Python
├── Proto/
│   ├── maze_Prim_loops.py      # Générateur de labyrinthe
│   ├── maze_Prim.py            # Algorithme Prim seul
│   ├── maze_dfs.py             # Algorithme DFS (alternative)
│   └── ...
├── templates/
│   └── index.html       # Interface web
├── static/
│   ├── styles.css       # Styles CSS
│   └── script.js        # Logique JavaScript
└── tests/
    └── ...              # Tests unitaires
```

### Améliorations futures possibles
- [ ] Affichage en temps réel de la génération
- [ ] Export en PNG/SVG
- [ ] Algorithmes additionnels (Kruskal, Recursive Backtracking)
- [ ] Mode multijoueur
- [ ] Résolution de labyrinthes par IA
- [ ] Animations de parcours

---

## 📞 Support

### Équipe du projet
- **Ikram Benchalal**
- **Nada Zina**
- **Aya Haddoun**

### Encadrant
- **M. MENEZ** (GitHub: gmenez)

### Ressources
- [Documentation Flask](https://flask.palletsprojects.com/)
- [Algorithme de Prim](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [Génération de labyrinthes](https://en.wikipedia.org/wiki/Maze_generation_algorithm)

---

## 📄 Licence

Ce projet est un travail académique réalisé dans le cadre du TER S2.

---

**Bonne génération de labyrinthes! 🎮✨**
