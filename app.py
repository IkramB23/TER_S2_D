from flask import Flask, jsonify, request
from Proto.maze_Prim import Maze


app = Flask(__name__)

@app.route("/")
def home():
    return "Maze Generator API is running"

@app.route("/maze")
def generate_maze():
    width = int(request.args.get("width", 21))
    height = int(request.args.get("height", 21))

    maze = Maze(width, height)
    maze.generate_prim()

    return jsonify({
        "width": width,
        "height": height,
        "maze": maze.maze
    })

if __name__ == "__main__":
    app.run(debug=True)

