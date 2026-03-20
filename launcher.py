#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de Labyrinthes Pac-Man - Launcher local
TER S2 - Groupe D (Ikram, Nada, Aya)

Ce script démarre l'interface locale type Pac-Man (pygame).
"""

import sys
import os
import subprocess
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
    
    required_packages = ['pygame']
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
    
    # Launch local game
    print("[INFO] Démarrage de l'interface locale...\n")
    print("=" * 50)
    print("   Interface locale Pac-Man")
    print("   Contrôles: flèches/WASD pour bouger")
    print("   N: nouveau labyrinthe, [ ]: changer")
    print("=" * 50 + "\n")
    
    # Import and run local game
    try:
        from local_pacman import main as run_local_game
        run_local_game()
    except KeyboardInterrupt:
        print("\n[INFO] Application arrêtée par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Une erreur s'est produite: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
