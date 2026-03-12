#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de Labyrinthes Pac-Man - Launcher
TER S2 - Groupe D (Ikram, Nada, Aya)

Ce script démarre l'application web du générateur de labyrinthes.
Il vérifie les dépendances et lance Flask sur http://localhost:5000
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print application header"""
    print("\n" + "=" * 50)
    print("   Générateur de Labyrinthes Pac-Man v1.0")
    print("   TER S2 - Groupe D")
    print("=" * 50 + "\n")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print("[ERROR] Python 3.6+ est requis")
        print(f"Vous avez: Python {sys.version}")
        sys.exit(1)
    print(f"[OK] Python {sys.version.split()[0]} détecté")

def check_dependencies():
    """Check and install required packages"""
    print("[INFO] Vérification des dépendances...")
    
    required_packages = ['flask']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"[INFO] Installation des paquets manquants: {', '.join(missing_packages)}")
        requirements_file = Path(__file__).parent / 'requirements.txt'
        
        if requirements_file.exists():
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)])
        else:
            for package in missing_packages:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    
    print("[OK] Dépendances vérifiées\n")

def main():
    """Main launcher function"""
    print_header()
    
    # Check Python version
    check_python_version()
    print()
    
    # Check dependencies
    check_dependencies()
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Launch Flask app
    print("[INFO] Démarrage de l'application...\n")
    print("=" * 50)
    print("   L'application est accessible sur:")
    print("   http://localhost:5000")
    print()
    print("   Appuyez sur Ctrl+C pour arrêter")
    print("=" * 50 + "\n")
    
    # Import and run Flask app
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n[INFO] Application arrêtée par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Une erreur s'est produite: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
