#!/usr/bin/env python3
"""
Script de validation rapide du Web Service Maze Pacman
Vérifie que tout est prêt pour la présentation
"""

import subprocess
import sys
import json
from pathlib import Path

def colored(text, color):
    """Colore le texte en terminal."""
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'end': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"

def check(name, condition, details=""):
    """Affiche un check ou une croix."""
    status = colored("✅ PASS", "green") if condition else colored("❌ FAIL", "red")
    print(f"{status} | {name}")
    if details and not condition:
        print(f"       {details}")
    return condition

def run_command(cmd, silent=True):
    """Exécute une commande et retourne le résultat."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def main():
    print(colored("\n🎮 Validation Web Service Maze Pacman", "blue"))
    print(colored("=" * 50, "blue"))
    
    all_passed = True
    
    # 1. Vérifier la structure des fichiers
    print(colored("\n1️⃣  Structure des fichiers", "yellow"))
    print("-" * 50)
    
    files_to_check = {
        'app.py': 'Flask app',
        'requirements.txt': 'Dépendances',
        'Procfile': 'Config Render',
        'templates/index.html': 'Interface HTML',
        'static/styles.css': 'Styles CSS',
        'static/script.js': 'Logique JS',
        '.github/workflows/tests.yml': 'CI/CD config',
        'DEPLOYMENT.md': 'Documentation déploiement',
        'GUIDE_UTILISATION.md': 'Guide utilisateur',
    }
    
    for file, desc in files_to_check.items():
        exists = Path(file).exists()
        all_passed &= check(f"Fichier: {file:40} ({desc})", exists, f"Fichier manquant!")
    
    # 2. Vérifier Python et dépendances
    print(colored("\n2️⃣  Environnement Python", "yellow"))
    print("-" * 50)
    
    # Python version
    success, stdout, _ = run_command("python --version")
    all_passed &= check("Python disponible", success)
    if success:
        print(f"    → {stdout.strip()}")
    
    # Pip
    success, _, _ = run_command("pip --version")
    all_passed &= check("Pip disponible", success)
    
    # Flask
    success, _, _ = run_command("python -c \"import flask; print(flask.__version__)\"")
    all_passed &= check("Flask installé", success, "pip install flask")
    
    # Pytest
    success, _, _ = run_command("python -c \"import pytest\"")
    all_passed &= check("Pytest installé", success, "pip install pytest")
    
    # 3. Exécuter les tests
    print(colored("\n3️⃣  Tests", "yellow"))
    print("-" * 50)
    
    success, stdout, stderr = run_command("python -m pytest tests/ -q")
    
    # Parser le résumé des tests
    if "passed" in stdout:
        all_passed &= check("Tous les tests passent", success)
        # Extraire le nombre de tests
        for line in stdout.split('\n'):
            if 'passed' in line:
                print(f"    → {line.strip()}")
    else:
        all_passed &= check("Tous les tests passent", success, stderr)
    
    # 4. Vérifier l'API
    print(colored("\n4️⃣  API REST", "yellow"))
    print("-" * 50)
    
    # Tester que l'app peut démarrer
    success, _, _ = run_command("python -c \"from app import app; app.test_client()\"")
    all_passed &= check("App Flask loadable", success, "Erreur import app.py")
    
    # Vérifier les routes
    success, stdout, _ = run_command("python -c \"from app import app; print(list(app.url_map.iter_rules()))\"")
    all_passed &= check("Routes disponibles", success)
    
    # 5. Vérifier la structure Git
    print(colored("\n5️⃣  Git & GitHub", "yellow"))
    print("-" * 50)
    
    # Git initialized
    git_exists = Path('.git').exists()
    all_passed &= check("Repository Git", git_exists, "git init ou clone needed")
    
    if git_exists:
        # Check remotes
        success, stdout, _ = run_command("git remote -v")
        all_passed &= check("Git remote configuré", success and "github" in stdout.lower())
        if success:
            for line in stdout.strip().split('\n')[:2]:
                print(f"    → {line}")
    
    # 6. Vérifier le contenu crucial
    print(colored("\n6️⃣  Contenu crucial", "yellow"))
    print("-" * 50)
    
    # Procfile
    procfile_ok = Path('Procfile').exists()
    if procfile_ok:
        with open('Procfile', encoding='utf-8') as f:
            content = f.read()
            procfile_ok = 'gunicorn' in content
    all_passed &= check("Procfile avec gunicorn", procfile_ok, "Doit contenir: gunicorn app:app")
    
    # HTML
    html_ok = Path('templates/index.html').exists()
    if html_ok:
        try:
            with open('templates/index.html', encoding='utf-8') as f:
                content = f.read()
                html_ok = 'mazeCanvas' in content and 'fetch' in Path('static/script.js').read_text(encoding='utf-8')
        except:
            html_ok = False
    all_passed &= check("Interface HTML complète", html_ok)
    
    # API endpoint
    api_ok = Path('app.py').exists()
    if api_ok:
        with open('app.py', encoding='utf-8') as f:
            content = f.read()
            api_ok = '/maze' in content
    all_passed &= check("Endpoint /maze implémenté", api_ok)
    
    # 7. Checklist déploiement
    print(colored("\n7️⃣  Prêt pour déploiement Render", "yellow"))
    print("-" * 50)
    
    check("✓ requirements.txt à jour", Path('requirements.txt').exists())
    check("✓ Procfile configuré", Path('Procfile').exists())
    check("✓ app.py prêt", Path('app.py').exists())
    check("✓ GitHub Actions setup", Path('.github/workflows/tests.yml').exists())
    check("✓ Documentation DEPLOYMENT.md", Path('DEPLOYMENT.md').exists())
    
    # Résumé final
    print(colored("\n" + "=" * 50, "blue"))
    if all_passed:
        print(colored("✅ TOUS LES CONTRÔLES PASSENT!", "green"))
        print(colored("✨ Prêt pour la présentation et le déploiement!", "green"))
    else:
        print(colored("⚠️  QUELQUES PROBLÈMES À RÉSOUDRE", "red"))
        print("Vérifiez les détails ci-dessus")
    
    print(colored("\n📞 Prochaines étapes:", "blue"))
    print("  1. git add . && git commit && git push")
    print("  2. Créer un compte Render (render.com)")
    print("  3. Déployer: New Web Service → Select repo")
    print("  4. URL: https://pacman_S2_D.onrender.com/")
    print(colored("\n" + "=" * 50, "blue"))
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
