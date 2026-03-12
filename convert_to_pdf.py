#!/usr/bin/env python3
"""Convertir RESUME_COMPLET.md en PDF"""

import subprocess
import sys

# Essayer avec pandoc d'abord
try:
    subprocess.run([
        'pandoc',
        'RESUME_COMPLET.md',
        '-o', 'RESUME_COMPLET.pdf',
        '--pdf-engine=pdflatex'
    ], check=True)
    print("✅ PDF créé avec pandoc: RESUME_COMPLET.pdf")
    sys.exit(0)
except FileNotFoundError:
    print("pandoc non trouvé, essai avec weasyprint...")

# Essayer avec weasyprint
try:
    from weasyprint import HTML
    HTML('RESUME_COMPLET.md').write_pdf('RESUME_COMPLET.pdf')
    print("✅ PDF créé avec weasyprint: RESUME_COMPLET.pdf")
    sys.exit(0)
except ImportError:
    print("weasyprint non trouvé, essai avec reportlab...")

# Essayer avec reportlab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    # Lire le markdown
    with open('RESUME_COMPLET.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Créer PDF simple
    c = canvas.Canvas('RESUME_COMPLET.pdf', pagesize=letter)
    y = 800
    
    for line in content.split('\n')[:200]:  # Premiers 200 lignes
        if y < 50:
            c.showPage()
            y = 800
        if line.strip():
            c.drawString(20, y, line[:100])
            y -= 12
    
    c.save()
    print("✅ PDF créé avec reportlab: RESUME_COMPLET.pdf")
    sys.exit(0)
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("\nPour créer un PDF, installez pandoc:")
    print("  Windows: choco install pandoc")
    print("  ou téléchargez: https://pandoc.org/installing.html")
    sys.exit(1)
