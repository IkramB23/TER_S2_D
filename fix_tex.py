import re

def process_presentation():
    with open('presentation.tex', 'r', encoding='utf-8') as f:
        text = f.read()

    text = text.replace('Web Service \& API', 'Interface Graphique Pygame').replace('Déploiement Continue (Render)', 'Aperçu Local (Pygame)').replace('Serveur Web', 'Interface Locale')

    text = re.sub(r'\\\\node\[box, fill=ucalight\] \(flask\).*?app\.py};', r'\\\\node[box, fill=ucalight] (pygame) at (11, 0) {\\\\faGamepad\\\\\\\\[0.1cm]\\\\textbf{Pygame}\\\\\\\\local\\\\_pacman.py};', text)
    text = re.sub(r'\\\\node\[box, fill=ucamiddle, text=white\] \(render\).*?Render.*?};', r'\\\\node[box, fill=ucamiddle, text=white] (sqlite) at (11, -3) {\\\\faDatabase\\\\\\\\[0.1cm]\\\\textbf{SQLite}\\\\\\\\mazes.db};', text)
    text = text.replace('(render) -- (flask)', '(sqlite) -- (pygame)')
    text = text.replace('(flask) -- (gen)', '(pygame) -- (gen)')
    text = text.replace('Gunicorn / Render', 'Pygame / LocalPacman')
    text = text.replace('app.py ', 'local_pacman.py ')
    text = text.replace('API Flask +', 'Aperçu Pygame +')
    text = text.replace('Flask (pas Django)', 'Pygame')
    text = text.replace('léger et simple', 'bibliothèque 2D légère')
    text = re.sub(r'Flask -- Documentation officielle.*?https://flask.palletsprojects.com/[^}]*}', r'Pygame -- Documentation officielle ~~\\\\url{https://www.pygame.org/docs/}', text)
    text = text.replace('API REST développée avec Flask', 'Interface interactive développée avec Pygame')
    text = text.replace('Déploiement sur Render', 'Sauvegarde via base de données SQLite en local')
    text = text.replace('API Web / Cloud', 'Interface Visuelle Locale')

    with open('presentation.tex', 'w', encoding='utf-8') as f:
        f.write(text)

def process_guide():
    with open('guide_presentation.tex', 'r', encoding='utf-8') as f:
        guide = f.read()

    guide = guide.replace('API Flask (serveur web)', 'Interface Locale Pygame (Aperçu du jeu)')
    guide = guide.replace('app.py', 'local_pacman.py')
    guide = guide.replace('API Flask, déploiement Render, tests cloud', 'Interface Pygame, Tests locaux, SQLite')
    guide = guide.replace('Flask & Mini-framework Python', 'Pygame & Bibliothèque Python')
    guide = guide.replace('Render & Plateforme cloud pour héberger notre API web (Paas)', 'SQLite & Base de données locale pour l\'historique')
    guide = guide.replace('Gunicorn', 'Pygame')
    guide = guide.replace('Ligne 1} : on importe Flask (le framework web)', 'Ligne 1} : on importe Pygame')

    with open('guide_presentation.tex', 'w', encoding='utf-8') as f:
        f.write(guide)

process_presentation()
process_guide()
