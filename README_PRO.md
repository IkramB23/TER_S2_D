# Maze Pacman Generator - Web Service

Generateur de labyrinthes parametrables avec interface graphique web et API REST.

## Project Overview

This project implements a complete web-based maze generator using Prim's algorithm with customizable loop insertion. The application consists of a Python Flask backend API and a modern HTML5/CSS3/JavaScript frontend, allowing users to generate, visualize, and export labyrinth data in real-time.

### Team

- Ikram Benchalal - Algorithm Development
- Nada Zina - Algorithm Optimization
- Aya Haddoun - Interface Design and Frontend Development

**Supervisor:** M. MENEZ

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

```bash
# Clone the repository
git clone https://github.com/IkramB23/TER_S2_D.git
cd TER_S2_D

# Install dependencies
pip install -r requirements.txt

# Run the application
python launcher.py
```

The application will start on `http://localhost:5000`

### Alternative Launch Methods

**Windows Command Prompt:**
```cmd
run.bat
```

**Windows PowerShell:**
```powershell
.\run.ps1
```

## Features

### Core Functionality

- Maze generation using Prim's algorithm
- Customizable maze dimensions (5x5 to 101x101 pixels)
- Adjustable loop percentage (0% to 100%)
- Real-time visualization on HTML5 Canvas
- Live statistics (corridor and wall counts)

### User Interface

- Responsive design (desktop, tablet, mobile)
- Modern gradient-based styling
- Smooth animations and transitions
- Keyboard shortcuts (Ctrl+G to generate, Ctrl+S to download)
- Real-time input validation

### Export Options

- PNG format (visual representation)
- JSON format (structured data with metadata)
- Download with automatic timestamp

## API Documentation

### Endpoint: GET /maze

Generates a maze with specified parameters.

**Parameters:**
```
width      (integer) - Maze width in pixels. Range: 5-101 (must be odd). Default: 21
height     (integer) - Maze height in pixels. Range: 5-101 (must be odd). Default: 21
loop_percent (integer) - Percentage of loops to add. Range: 0-100. Default: 25
```

**Request Examples:**

```bash
# Default maze (21x21, 25% loops)
curl "http://localhost:5000/maze"

# Custom size
curl "http://localhost:5000/maze?width=31&height=31"

# With loop adjustment
curl "http://localhost:5000/maze?width=21&height=21&loop_percent=50"

# Save to file
curl "http://localhost:5000/maze?width=21&height=21" > maze.json
```

**Response Format:**
```json
{
  "width": 21,
  "height": 21,
  "loop_percent": 25,
  "maze": [
    [0, 1, 0, 1, 0, ...],
    [1, 0, 1, 0, 1, ...],
    [0, 1, 0, 1, 0, ...],
    ...
  ]
}
```

**Data Representation:**
- 0 = wall (black)
- 1 = corridor (white)

**Error Responses:**
- 400 Bad Request - Invalid parameters
- 500 Internal Server Error - Generation failure

## Project Structure

```
TER_S2_D/
├── app.py                    # Flask application
├── launcher.py               # Cross-platform launcher
├── run.bat                   # Windows batch launcher
├── run.ps1                   # PowerShell launcher
├── requirements.txt          # Python dependencies
├── Procfile                  # Render deployment config
│
├── templates/
│   └── index.html           # Web interface
│
├── static/
│   ├── styles.css           # Styling and animations
│   └── script.js            # Client-side logic
│
├── Proto/
│   ├── maze_Prim_loops.py   # Maze generation algorithm
│   ├── maze_Prim.py
│   └── ...
│
├── tests/
│   ├── test_app_local.py    # API unit tests
│   ├── test_integration.py  # Integration tests
│   ├── test_maze_generator.py
│   ├── curl_examples.sh     # Curl command examples (Linux/macOS)
│   └── curl_examples.bat    # Curl command examples (Windows)
│
├── .github/
│   └── workflows/
│       └── tests.yml        # CI/CD configuration
│
└── README.md                # This file
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Suite

```bash
# API tests
pytest tests/test_app_local.py -v

# Integration tests
pytest tests/test_integration.py -v

# Generator tests
pytest tests/test_maze_generator.py -v
```

### Test Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

### Test Results

All 36 tests pass successfully, covering:
- API route functionality
- Input validation
- Maze generation correctness
- Data structure integrity
- Performance benchmarks
- Error handling

## Algorithm Details

### Prim's Algorithm

The maze generation uses Prim's algorithm (minimum spanning tree approach):

1. Start with a grid of walls
2. Choose a random cell and mark it as visited
3. Repeatedly add neighboring walls to a list
4. Pick a random wall from the list
5. If it separates visited and unvisited cells, carve a passage
6. Continue until all cells are visited

**Complexity:** O(n²) where n is the maze dimension

### Loop Generation

After creating a perfect maze, loops are added by:
1. Identifying wall cells that can be removed
2. Randomly selecting walls based on the loop_percent parameter
3. Removing selected walls to create alternate paths

## Technology Stack

**Backend:**
- Python 3.8+
- Flask 3.1
- Gunicorn (production server)

**Frontend:**
- HTML5 (semantic markup)
- CSS3 (Grid, Flexbox, animations)
- Vanilla JavaScript (ES6+, fetch API)

**Testing:**
- pytest 9.0
- GitHub Actions (CI/CD)

**Deployment:**
- Render.com (cloud platform)
- Docker-ready

## Deployment

### Local Development

```bash
python launcher.py
```

### Production (Render)

1. Create account at https://render.com
2. Connect GitHub repository
3. New Web Service configuration:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Name: `pacman_S2_D`
4. Deploy and access at `https://pacman_S2_D.onrender.com`

See DEPLOYMENT.md for detailed instructions.

## Documentation

- GUIDE_UTILISATION.md - User guide with detailed instructions
- DEPLOYMENT.md - Cloud deployment guidelines
- RESUME_COMPLET.md - Complete project summary
- tests/README.md - Testing documentation

## Performance

- Generation time for 101x101 maze: < 5 seconds
- API response time: < 100ms
- Memory usage: < 50MB
- JSON response size: < 1MB

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+G | Generate new maze |
| Ctrl+S | Download maze |
| Enter | Generate (when in input field) |

## Troubleshooting

**Port 5000 already in use**
```bash
# Use different port by modifying app.py
app.run(port=5001)
```

**Missing dependencies**
```bash
pip install -r requirements.txt
```

**Permission denied on launcher**
```bash
chmod +x launcher.py  # Linux/macOS
```

## Future Enhancements

- MongoDB integration for maze storage and rating system
- User authentication and leaderboards
- Multiple maze generation algorithms
- Pacman game implementation
- AI opponent (bot) players
- Game replay functionality
- Difficulty levels and power-ups

## License

Academic project - TER S2

## Contact

For questions or issues, please open an issue on GitHub or contact the development team.

---

**Status:** Production Ready  
**Last Updated:** March 12, 2026  
**Version:** 1.0.0
