# 🎮 Générateur de Labyrinthes Pac-Man - TER S2

> **Un outil professionnel pour générer des labyrinthes paramétrables avec interface graphique complète**

[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)](#)

## 👥 Équipe

| Membre | Rôle |
|--------|------|
| **Ikram Benchalal** | Développement algorithme + API |
| **Nada Zina** | Développement algorithme + Optimisations |
| **Aya Haddoun** | Interface graphique + UX/UI |

**Encadrant**: M. MENEZ (GitHub: [gmenez](https://github.com/gmenez))

## 🎯 Objectif du projet

Créer une application web complète permettant de:
- ✅ Générer des labyrinthes avec l'algorithme de Prim
- ✅ Ajouter des boucles de complexité variable
- ✅ Paramétrer la taille et la connectivité
- ✅ Visualiser en temps réel
- ✅ Télécharger en format JSON
- ✅ Utiliser via une API REST

## 🚀 Quick Start

### Installation rapide

```bash
# Cloner le projet
git clone https://github.com/votre-username/TER_S2_D.git
cd TER_S2_D

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python launcher.py
```

L'application s'ouvre automatiquement sur **http://localhost:5000**

### Alternatives de démarrage

**Windows**:
```cmd
run.bat
```

**PowerShell**:
```powershell
.\run.ps1
```

**Linux/macOS**:
```bash
python3 launcher.py
```

## 📖 Documentation

- **[Guide d'utilisation complet](GUIDE_UTILISATION.md)** - Instructions détaillées et aide
- **[RA/](RA/)** - Rapports d'activité de chaque membre
- **[Proto/](Proto/)** - Fichiers prototypes et algorithmes

## ✨ Fonctionnalités principales

### 🎨 Interface utilisateur
- Design moderne et réactif (Gradient, animations)
- Contrôles intuitifs et fluides
- Visualisation en temps réel sur canvas HTML5
- Statistiques des labyrinthes générés
- Responsive design (mobile, tablet, desktop)

### ⚙️ Paramètres personnalisables
- **Largeur**: 5 à 101 pixels (nombres impairs)
- **Hauteur**: 5 à 101 pixels (nombres impairs)
- **Boucles**: 0% à 100% (curseur interactif)

### 🔧 Fonctionnalités techniques
- API REST pour accès programmatique
- Export JSON avec métadonnées
- Algorithme Prim optimisé O(n²)
- Validation complète des entrées
- Gestion d'erreurs robuste

## 📁 Structure du projet

```
TER_S2_D/
├── 📄 app.py                    # Application Flask
├── 🚀 launcher.py              # Launcher Python
├── 🪟 run.bat                  # Launcher Windows (CMD)
├── 🔵 run.ps1                  # Launcher PowerShell
├── 📋 requirements.txt
├── 📘 README.md
├── 📖 GUIDE_UTILISATION.md
│
├── 📁 templates/
│   └── index.html              # Interface complète
│
├── 📁 static/
│   ├── styles.css              # Styles modernes
│   └── script.js               # Logique JS
│
├── 📁 Proto/
│   ├── maze_Prim_loops.py      # Générateur ⭐
│   ├── maze_Prim.py
│   ├── maze_dfs.py
│   └── ...
│
├── 📁 tests/
│   ├── test_app_local.py
│   ├── test_maze_generator.py
│   └── ...
│
└── 📁 RA/
    ├── ra_ikram.md
    ├── ra_nada.md
    └── mazes.md
```

## 🔗 API REST

### Endpoint: `/maze`

```http
GET /maze?width=21&height=21&loop_percent=25
```

**Paramètres**:
| Param | Type | Min | Max | Défaut |
|-------|------|-----|-----|--------|
| `width` | int | 5 | 101 | 21 |
| `height` | int | 5 | 101 | 21 |
| `loop_percent` | int | 0 | 100 | 25 |

**Réponse**:
```json
{
  "width": 21,
  "height": 21,
  "loop_percent": 25,
  "maze": [[0,1,0,...], ...]
}
```

## 🧮 Algorithme

**Prim avec génération de boucles**

1. **Prim**: Génère labyrinthe parfait (O(n²))
2. **Boucles**: Supprime murs aléatoires pour complexité

Représentation: `0` = mur, `1` = couloir

## 🔨 Technologies

- **Backend**: Python 3.6+, Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Gunicorn, Render

## ⌨️ Raccourcis

| Touche | Action |
|--------|--------|
| **Ctrl+G** | Générer |
| **Ctrl+S** | Télécharger |
| **Enter** | Générer (en largeur/hauteur) |

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🧪 Tests

```bash
python -m pytest tests/
```

## 🌐 Déploiement

Local:
```bash
python launcher.py
```

Production (Render): Voir `Procfile`

## ❓ FAQ

**Erreur Flask?**  
→ `pip install -r requirements.txt`

**Port déjà utilisé?**  
→ Modifiez `app.py`: changez `port=5000`

**API?**  
→ [Voir documentation complète](GUIDE_UTILISATION.md)

## 📄 Licence

Travail académique TER S2

---

**Version**: 1.0.0 | **Status**: ✅ Complet

**[📖 Guide complet →](GUIDE_UTILISATION.md)**
