from flask import Flask, jsonify, request
from Proto.maze_Prim_loops import generate_pacman_maze

app = Flask(__name__)

@app.route("/")
def home():
    return "Maze Generator API is running (loops version)"

@app.route("/maze")
def generate_maze_route():
    width = int(request.args.get("width", 21))
    height = int(request.args.get("height", 21))
    loop_percent=int(request.args.get("loop_percent",25))
    maze = generate_pacman_maze(width, height,loop_percent)

    return jsonify({
        "width": len(maze[0]),
        "height": len(maze),
        "loop_percent": loop_percent,
        "maze": maze
    })

if __name__ == "__main__":
    app.run(debug=True)