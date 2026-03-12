# 🚀 Guide de Déploiement - Render

> Déploiement du Web Service "Maze Pacman" sur Render

## Prérequis

- Compte GitHub (avec accès au repo IkramB23/TER_S2_D)
- Compte Render (https://render.com)
- Variables d'environnement configurées

## 📋 Étapes de déploiement

### 1️⃣ Créer une application Web sur Render

1. Aller sur https://dashboard.render.com
2. Cliquer **"New +"** → **"Web Service"**
3. Connecter le compte GitHub
4. Sélectionner le repo **IkramB23/TER_S2_D**
5. Configurer:

| Champ | Valeur |
|-------|--------|
| **Name** | `pacman_S2_D` |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Region** | Frankfurt (Europe) |
| **Plan** | Free tier (gratuit) |

### 2️⃣ Configurer les variables d'environnement

Sur la page Web Service:
1. Aller dans **"Environment"**
2. Ajouter les variables:

```
FLASK_ENV=production
FLASK_APP=app.py
```

### 3️⃣ Déployer

1. Cliquer sur **"Create Web Service"**
2. Render va automatiquement:
   - Cloner le repo
   - Installer les dépendances
   - Déployer l'app

⏳ Attendre 5-10 minutes pour le premier déploiement.

### 4️⃣ Vérifier le déploiement

Une fois en ligne, accéder à:
```
https://pacman_S2_D.onrender.com/
```

### 5️⃣ Tests post-déploiement

```bash
# Health check
curl https://pacman_S2_D.onrender.com/health

# Générer un maze
curl "https://pacman_S2_D.onrender.com/maze?width=21&height=21&loop_percent=25"

# Afficher l'interface web
open https://pacman_S2_D.onrender.com/
```

## 🔄 Déploiement continu (Auto-Deploy)

Render peut déployer **automatiquement** à chaque push sur `main`:

1. Sur la page Web Service
2. Aller dans **"Settings"**
3. Cocher: **"Auto-Deploy from Git"**

Désormais, chaque `git push` va déclencher un nouveau déploiement!

## 🧪 CI/CD avec GitHub Actions

Les tests s'exécutent automatiquement:

1. A chaque **push** sur `main`
2. A chaque **pull request**
3. Résultats visibles dans l'onglet **"Actions"** du repo

Voir `.github/workflows/tests.yml` pour la configuration.

## 📊 Logs et Monitoring

Sur Render dashboard:
- **Live tail** → Voir les logs en temps réel
- **Metrics** → CPU, Mémoire, Requêtes
- **Deployments** → Historique des déploiements

## 🔧 Troubleshooting

### ❌ Build fails
```
Vérifier:
- requirements.txt existe et est à jour
- app.py est valide
- Pas de imports manquants
```

### ❌ App crashes au démarrage
```
Vérifier logs:
1. Aller dans "Logs" on Render
2. Chercher les erreurs
3. Corriger le code localement
4. git push pour redéployer
```

### ❌ API répond lentement
```
Render Free tier peut mettre 30s à démarrer.
Pour des perf meilleures:
1. Upgrade vers Starter ($7/mois)
2. Utiliser un autre service (Heroku, Railway, etc.)
```

## 📚 Liens utiles

- Render Docs: https://render.com/docs
- Flask Deployment: https://flask.palletsprojects.com/deployment/
- Gunicorn: https://gunicorn.org/
- GitHub Actions: https://docs.github.com/en/actions

## 🎯 Résumé

```bash
# Local development
python launcher.py

# Tests
pytest tests/

# Voir les logs de déploiement
# → https://dashboard.render.com/

# Accéder à l'app en production
# → https://pacman_S2_D.onrender.com/
```

---

**Status**: ✅ Prêt pour déploiement
**URL de production**: https://pacman_S2_D.onrender.com/
