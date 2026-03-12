#!/usr/bin/env python3
"""
Convertir RESUME_COMPLET.md en PDF avec un HTML intermédiaire
"""

import re

# Lire le markdown
with open('RESUME_COMPLET.md', 'r', encoding='utf-8') as f:
    markdown_content = f.read()

# Créer HTML
html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Résumé Complet - Projet TER S2 Groupe D</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: white;
            padding: 40px;
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: #2563eb;
            margin-top: 40px;
            margin-bottom: 20px;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 10px;
            font-size: 2.5em;
        }}
        
        h2 {{
            color: #1f2937;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.8em;
        }}
        
        h3 {{
            color: #4b5563;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.3em;
        }}
        
        h4 {{
            color: #6b7280;
            margin-top: 15px;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        
        p {{
            margin-bottom: 12px;
            text-align: justify;
        }}
        
        ul, ol {{
            margin-left: 30px;
            margin-bottom: 15px;
        }}
        
        li {{
            margin-bottom: 8px;
        }}
        
        code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        pre {{
            background: #1f2937;
            color: #f3f4f6;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin-bottom: 15px;
            line-height: 1.4;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}
        
        blockquote {{
            border-left: 4px solid #2563eb;
            padding-left: 15px;
            margin-left: 0;
            margin-bottom: 15px;
            color: #666;
            font-style: italic;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background: #2563eb;
            color: white;
        }}
        
        tr:nth-child(even) {{
            background: #f9fafb;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 5px;
        }}
        
        .badge-success {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .badge-info {{
            background: #dbeafe;
            color: #0c4a6e;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #e5e7eb;
            margin: 30px 0;
        }}
        
        @media print {{
            body {{
                padding: 0;
            }}
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
            pre {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    {markdown_content}
</body>
</html>
"""

# Sauvegarder HTML
with open('RESUME_COMPLET.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ HTML créé: RESUME_COMPLET.html")
print("")
print("📄 Pour convertir en PDF:")
print("   Option 1 (Windows): Ouvrir le HTML et faire Imprimer → Sauvegarder en PDF")
print("   Option 2 (Tous): Installer pandoc et faire:")
print("      pandoc RESUME_COMPLET.html -o RESUME_COMPLET.pdf")
print("   Option 3 (En ligne): https://cloudconvert.com/ (glisser-déposer)")
