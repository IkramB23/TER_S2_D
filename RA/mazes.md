# Réfs labyrinthes - Jour 1 (06/02/2026)

## Les key concepts
- **Labyrinthe parfait** : 1 seul chemin entre 2 points (arbre)
- **Labyrinthe imparfait** : avec boucles, plusieurs chemins : c'est ce qu'on veut pour Pac-Man
- **Connectivité** : permet d'échapper aux fantômes grâce aux chemins alternatifs

## Algorithmes explorés
- **DFS (Recursive Backtracker)** : O(n) - Parcours en profondeur (exploré par Ikram)
- **Prim** : O(n log n) - Arbre couvrant minimum (exploré par Nada)
- **Kruskal** : O(E log E) - Union-Find

**Pour ajouter des boucles :**
- Supprimer X% des murs après génération
- Kruskal modifié (continuer après l'arbre complet)
- Génération par pièces/salles

## Réfs où on devra creuser
- [Wikipedia - Maze Generation](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Think Labyrinth](http://www.astrolog.org/labyrnth/algrithm.htm)
- [Jamis Buck - Maze Generation](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
- Labyrinthe original Pac-Man (symétrie, tunnels, spawn)

## Pistes prioritaires
1. Prim (choix envisagé pour le projet)
2. DFS comme alternative
3. Kruskal modifié avec contrôle de la connectivité

## Petites questions:
- Comment mesurer le taux de connectivité ?
- Représentation : matrice 2D ou graphe ?
- Paramètres API : taille, difficulté, densité ?

## Stack technique envisagée (à voir avec les collègues membre de mon groupe)
- Backend : Python (Flask/FastAPI)
- Frontend : JS (Canvas) ou Pygame
- Hébergement : Render
- **Hébergement** : Render.com (qui est gratuit pour projets étudiants)
