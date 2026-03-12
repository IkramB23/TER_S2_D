from flask import Flask, jsonify, request, render_template
from Proto.maze_Prim_loops import generate_pacman_maze
import os

app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)

@app.route("/")
def home():
    """Serve the main interface"""
    return render_template('index.html')

@app.route("/maze")
def generate_maze_route():
    """Generate a maze with specified parameters"""
    try:
        width = int(request.args.get("width", 21))
        height = int(request.args.get("height", 21))
        loop_percent = int(request.args.get("loop_percent", 25))
        
        # Validate inputs
        if width < 5 or width > 101:
            return jsonify({"error": "Width must be between 5 and 101"}), 400
        if height < 5 or height > 101:
            return jsonify({"error": "Height must be between 5 and 101"}), 400
        if loop_percent < 0 or loop_percent > 100:
            return jsonify({"error": "Loop percent must be between 0 and 100"}), 400
        
        maze = generate_pacman_maze(width, height, loop_percent)

        return jsonify({
            "width": len(maze[0]),
            "height": len(maze),
            "loop_percent": loop_percent,
            "maze": maze
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Maze Generator API is running"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)