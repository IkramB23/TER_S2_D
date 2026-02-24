from flask import Flask, jsonify, request
from Proto.maze_Prim_loops import generate_maze as generate_maze_loops

app = Flask(__name__)

@app.route("/")
def home():
    return "Maze Generator API is running (loops version)"

@app.route("/maze")
def generate_maze_route():
    width = int(request.args.get("width", 21))
    height = int(request.args.get("height", 21))

    maze = generate_maze_loops(width, height)

    return jsonify({
        "width": width,
        "height": height,
        "maze": maze
    })

if __name__ == "__main__":
    app.run(debug=True)