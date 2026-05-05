import os
import uuid
import copy
from flask import Flask, jsonify, request
try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None
from Proto.maze_Prim_loops import generate_pacman_maze
from game.framework import compare_day6_strategies

app = Flask(__name__)

# --- configuration mongodb atlas ---
MONGO_URI = os.getenv("MONGO_URI", "")
if MONGO_URI and MongoClient is not None:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    db = client.pacman_db
    mazes_collection = db.mazes
    recordings_collection = db.recordings
else:
    mazes_collection = None
    recordings_collection = None

@app.route("/")
def home():
    return "Maze Generator API is running (loops version)"

@app.route("/maze")
def generate_maze_route():
    width = int(request.args.get("width", 21))
    height = int(request.args.get("height", 21))
    loop_percent = int(request.args.get("loop_percent", 25))
    maze = generate_pacman_maze(width, height, loop_percent)

    # 1. création de l'id unique
    maze_id = str(uuid.uuid4())

    # 2. enregistrement dans mongodb atlas (non bloquant en cas d'erreur)
    if mazes_collection is not None:
        try:
            mazes_collection.insert_one({
                "_id": maze_id,
                "width": width,
                "height": height,
                "loop_percent": loop_percent,
                "maze": maze,
                "rating": None
            })
        except Exception as e:
            print(f"Erreur DB : {e}")

    return jsonify({
        "id": maze_id,
        "width": len(maze[0]),
        "height": len(maze),
        "loop_percent": loop_percent,
        "maze": maze
    })

@app.route("/maze/<maze_id>/rate", methods=["POST"])
def rate_maze(maze_id):
    data = request.json
    
    if not data or "rating" not in data:
        return jsonify({"error": "Le champ 'rating' est requis"}), 400
        
    rating = data["rating"]
    if not isinstance(rating, int) or rating < 0 or rating > 5:
        return jsonify({"error": "Le rating doit être un entier entre 0 et 5"}), 400

    try:
        if mazes_collection is None:
            return jsonify({"error": "Base de données non configurée"}), 503
        result = mazes_collection.update_one(
            {"_id": maze_id},
            {"$set": {"rating": rating}}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Maze ID introuvable"}), 404
            
        return jsonify({"message": f"Labyrinthe {maze_id} noté {rating}/5 avec succès"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- microservice : liste des algorithmes disponibles ---

AVAILABLE_ALGORITHMS = ["bfs", "dfs", "ucs", "astar", "mcts"]

@app.route("/ai/algorithms")
def list_algorithms():
    # retourne la liste des pathfinders disponibles
    return jsonify({"algorithms": AVAILABLE_ALGORITHMS})


@app.route("/ai/benchmark", methods=["POST"])
def run_benchmark():
    # lance un benchmark de toutes les stratégies sur un labyrinthe
    data = request.json or {}
    width = int(data.get("width", 21))
    height = int(data.get("height", 21))
    loop_percent = int(data.get("loop_percent", 25))
    seeds = int(data.get("seeds", 1))
    steps = int(data.get("steps", 250))

    # limites de sécurité
    width = max(11, min(41, width))
    height = max(11, min(41, height))
    seeds = max(1, min(10, seeds))
    steps = max(50, min(500, steps))

    maze = generate_pacman_maze(width, height, loop_percent)

    if seeds == 1:
        seed = int(data.get("seed", 42))
        report = compare_day6_strategies(maze, route_steps=steps, seed=seed)
    else:
        from game.framework import compare_strategies_over_seeds
        seed_start = int(data.get("seed", 42))
        report = compare_strategies_over_seeds(
            maze=maze,
            seeds=range(seed_start, seed_start + seeds),
            route_steps=steps,
        )

    return jsonify(report)




# --- enregistrements de parties ---

@app.route("/recording", methods=["POST"])
def save_recording():
    """Sauvegarde un enregistrement de partie dans MongoDB."""
    data = request.json
    if not data:
        return jsonify({"error": "Corps JSON requis"}), 400
    if recordings_collection is None:
        return jsonify({"error": "Base de données non configurée"}), 503
    rec_id = str(uuid.uuid4())
    try:
        doc = {"_id": rec_id}
        meta = data.get("metadata", {})
        frames = data.get("frames", [])
        # enrichir score_final et nb_frames si absents (anciens enregistrements)
        if "score_final" not in meta and frames:
            meta["score_final"] = frames[-1].get("score", 0)
        if "nb_frames" not in meta:
            meta["nb_frames"] = len(frames)
        doc["metadata"] = meta
        doc["total_frames"] = data.get("total_frames", len(frames))
        doc["frames"] = frames
        recordings_collection.insert_one(doc)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"id": rec_id})


@app.route("/recordings")
def list_recordings():
    """Retourne la liste des enregistrements (sans les frames ni le labyrinthe)."""
    if recordings_collection is None:
        return jsonify({"error": "Base de données non configurée"}), 503
    try:
        cursor = recordings_collection.find(
            {}, {"frames": 0, "metadata.maze": 0}
        ).limit(200)
        results = []
        for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        return jsonify({"recordings": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/recordings/fix_scores", methods=["POST"])
def fix_scores():
    """Met à jour score_final et nb_frames pour les enregistrements qui n'en ont pas."""
    if recordings_collection is None:
        return jsonify({"error": "Base de données non configurée"}), 503
    updated = 0
    try:
        cursor = recordings_collection.find({"metadata.score_final": {"$exists": False}})
        for doc in cursor:
            frames = doc.get("frames", [])
            score_final = frames[-1].get("score", 0) if frames else 0
            nb_frames = len(frames)
            recordings_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"metadata.score_final": score_final, "metadata.nb_frames": nb_frames}}
            )
            updated += 1
        return jsonify({"updated": updated})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/recording/<rec_id>")
def get_recording(rec_id):
    """Retourne un enregistrement complet (avec frames et labyrinthe)."""
    if recordings_collection is None:
        return jsonify({"error": "Base de données non configurée"}), 503
    try:
        doc = recordings_collection.find_one({"_id": rec_id})
        if doc is None:
            return jsonify({"error": "Enregistrement introuvable"}), 404
        doc["id"] = str(doc.pop("_id"))
        return jsonify(doc)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)