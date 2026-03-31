import os
import uuid
from flask import Flask, jsonify, request
from pymongo import MongoClient
from Proto.maze_Prim_loops import generate_pacman_maze

app = Flask(__name__)
#test
# --- CONFIGURATION MONGODB ATLAS ---
MONGO_URI = os.getenv("MONGO_URI", "")
if MONGO_URI:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    db = client.pacman_db
    mazes_collection = db.mazes
else:
    mazes_collection = None

@app.route("/")
def home():
    return "Maze Generator API is running (loops version)"

@app.route("/maze")
def generate_maze_route():
    width = int(request.args.get("width", 21))
    height = int(request.args.get("height", 21))
    loop_percent = int(request.args.get("loop_percent", 25))
    maze = generate_pacman_maze(width, height, loop_percent)

    # 1. Création de l'ID Unique
    maze_id = str(uuid.uuid4())

    # 2. Enregistrement dans MongoDB Atlas (non bloquant en cas d'erreur)
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

if __name__ == "__main__":
    app.run(debug=True)