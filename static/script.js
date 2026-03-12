// ========================================
// STATE MANAGEMENT
// ========================================
let currentMaze = null;
let isLoading = false;

// ========================================
// DOM ELEMENTS
// ========================================
const widthInput = document.getElementById('widthInput');
const heightInput = document.getElementById('heightInput');
const loopPercentInput = document.getElementById('loopPercentInput');
const generateBtn = document.getElementById('generateBtn');
const downloadBtn = document.getElementById('downloadBtn');
const canvas = document.getElementById('mazeCanvas');
const ctx = canvas.getContext('2d');
const statusMessage = document.getElementById('statusMessage');

const widthValue = document.getElementById('widthValue');
const heightValue = document.getElementById('heightValue');
const loopPercentValue = document.getElementById('loopPercentValue');
const dimensions = document.getElementById('dimensions');
const corridorCount = document.getElementById('corridorCount');
const wallCount = document.getElementById('wallCount');

// ========================================
// EVENT LISTENERS
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    // Input value displays
    widthInput.addEventListener('input', function() {
        widthValue.textContent = this.value;
    });

    heightInput.addEventListener('input', function() {
        heightValue.textContent = this.value;
    });

    loopPercentInput.addEventListener('input', function() {
        loopPercentValue.textContent = this.value;
    });

    // Generate button
    generateBtn.addEventListener('click', generateMaze);

    // Download button - show menu
    downloadBtn.addEventListener('click', showDownloadMenu);

    // Enter key to generate
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && e.target === widthInput || e.target === heightInput) {
            generateMaze();
        }
    });

    // Initial canvas setup
    setupCanvas();
});

// ========================================
// MAZE GENERATION
// ========================================
async function generateMaze() {
    if (isLoading) return;

    const width = parseInt(widthInput.value);
    const height = parseInt(heightInput.value);
    const loopPercent = parseInt(loopPercentInput.value);

    // Validation
    if (!validateInputs(width, height)) {
        return;
    }

    isLoading = true;
    generateBtn.disabled = true;
    showStatus('⏳ Génération en cours...', 'loading');

    try {
        const response = await fetch(`/maze?width=${width}&height=${height}&loop_percent=${loopPercent}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentMaze = data.maze;

        // Display success
        showStatus(`✅ Labyrinthe généré avec succès!`, 'success');
        
        // Update UI
        drawMaze(data.maze);
        updateMazeStats(data.maze);
        downloadBtn.disabled = false;

    } catch (error) {
        console.error('Error:', error);
        showStatus(`❌ Erreur: ${error.message}`, 'error');
    } finally {
        isLoading = false;
        generateBtn.disabled = false;
    }
}

// ========================================
// INPUT VALIDATION
// ========================================
function validateInputs(width, height) {
    if (width < 5 || width > 101) {
        showStatus('⚠️ Largeur doit être entre 5 et 101', 'error');
        return false;
    }

    if (height < 5 || height > 101) {
        showStatus('⚠️ Hauteur doit être entre 5 et 101', 'error');
        return false;
    }

    if (width % 2 === 0) {
        showStatus('⚠️ Largeur doit être impaire', 'error');
        return false;
    }

    if (height % 2 === 0) {
        showStatus('⚠️ Hauteur doit être impaire', 'error');
        return false;
    }

    return true;
}

// ========================================
// MAZE VISUALIZATION
// ========================================
function setupCanvas() {
    // Fill canvas with light background
    ctx.fillStyle = '#f3f4f6';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw initial message
    ctx.fillStyle = '#9ca3af';
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('Génère un labyrinthe pour le visualiser ici', canvas.width / 2, canvas.height / 2);
}

function drawMaze(maze) {
    const height = maze.length;
    const width = maze[0].length;

    // Calculate cell size to fit canvas
    const cellWidth = canvas.width / width;
    const cellHeight = canvas.height / height;

    // Clear canvas
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw maze
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const cell = maze[y][x];
            
            // 0 = wall (black), 1 = corridor (white)
            ctx.fillStyle = cell === 1 ? '#ffffff' : '#1f2937';
            ctx.fillRect(
                x * cellWidth,
                y * cellHeight,
                cellWidth,
                cellHeight
            );

            // Optional: Draw grid
            ctx.strokeStyle = cell === 1 ? '#e5e7eb' : '#111827';
            ctx.lineWidth = 0.5;
            ctx.strokeRect(
                x * cellWidth,
                y * cellHeight,
                cellWidth,
                cellHeight
            );
        }
    }
}

// ========================================
// MAZE STATISTICS
// ========================================
function updateMazeStats(maze) {
    const height = maze.length;
    const width = maze[0].length;

    let corridors = 0;
    let walls = 0;

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            if (maze[y][x] === 1) {
                corridors++;
            } else {
                walls++;
            }
        }
    }

    dimensions.textContent = `${width} × ${height}`;
    corridorCount.textContent = corridors;
    wallCount.textContent = walls;
}

// ========================================
// DOWNLOAD FUNCTIONALITY
// ========================================
function showDownloadMenu() {
    if (!currentMaze) {
        showStatus('❌ Aucun labyrinthe à télécharger', 'error');
        return;
    }

    // Create menu
    const menu = document.createElement('div');
    menu.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        border: 2px solid #2563eb;
        border-radius: 8px;
        padding: 20px;
        z-index: 9999;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    `;

    menu.innerHTML = `
        <h3 style="margin-top: 0; color: #2563eb;">Télécharger le labyrinthe</h3>
        <button id="downloadImage" style="
            display: block;
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        ">📸 Télécharger en PNG</button>
        <button id="downloadJSON" style="
            display: block;
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            background: #7c3aed;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        ">📄 Télécharger en JSON</button>
        <button id="cancelMenu" style="
            display: block;
            width: 100%;
            padding: 10px;
            background: #6b7280;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        ">Annuler</button>
    `;

    document.body.appendChild(menu);

    document.getElementById('downloadImage').addEventListener('click', downloadMazeImage);
    document.getElementById('downloadJSON').addEventListener('click', downloadMazeJSON);
    document.getElementById('cancelMenu').addEventListener('click', function() {
        menu.remove();
    });
}

function downloadMazeImage() {
    if (!currentMaze) {
        showStatus('❌ Aucun labyrinthe à télécharger', 'error');
        return;
    }

    const width = parseInt(widthInput.value);
    const height = parseInt(heightInput.value);

    // Get PNG data
    canvas.toBlob(function(blob) {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `maze_${width}x${height}_${new Date().getTime()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        showStatus('🖼️ Image PNG téléchargée avec succès!', 'success');
        
        // Close menu if exists
        const menu = document.querySelector('div[style*="position: fixed"]');
        if (menu) menu.remove();
    });
}

function downloadMazeJSON() {
    if (!currentMaze) {
        showStatus('❌ Aucun labyrinthe à télécharger', 'error');
        return;
    }

    const width = parseInt(widthInput.value);
    const height = parseInt(heightInput.value);
    const loopPercent = parseInt(loopPercentInput.value);

    const data = {
        width: width,
        height: height,
        loop_percent: loopPercent,
        maze: currentMaze,
        generated_at: new Date().toISOString(),
        metadata: {
            algorithm: 'Prim with loops',
            team: 'Ikram Benchalal, Nada Zina, Aya Haddoun',
            project: 'TER S2 - Labyrinth Generator'
        }
    };

    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `maze_${width}x${height}_${new Date().getTime()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    showStatus('💾 Labyrinthe JSON téléchargé avec succès!', 'success');
    
    // Close menu if exists
    const menu = document.querySelector('div[style*="position: fixed"]');
    if (menu) menu.remove();
}

// ========================================
// UI HELPERS
// ========================================
function showStatus(message, type = 'success') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message show ${type}`;

    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            statusMessage.classList.remove('show');
        }, 5000);
    }
}

// ========================================
// KEYBOARD SHORTCUTS
// ========================================
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + G to generate
    if ((e.ctrlKey || e.metaKey) && e.key === 'g') {
        e.preventDefault();
        generateMaze();
    }

    // Ctrl/Cmd + S to download (show menu)
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        showDownloadMenu();
    }
});

// ========================================
// HELPER FUNCTIONS
// ========================================
function getRandomColor() {
    const colors = ['#2563eb', '#7c3aed', '#dc2626', '#ea580c', '#16a34a'];
    return colors[Math.floor(Math.random() * colors.length)];
}

// Log app info
console.log('%c🎮 Générateur de Labyrinthes Pac-Man', 'color: #2563eb; font-size: 16px; font-weight: bold;');
console.log('%cTER S2 - Équipe D', 'color: #7c3aed; font-size: 12px;');
console.log('%cKeyboard Shortcuts: Ctrl+G (Generate), Ctrl+S (Download)', 'color: #6b7280; font-size: 11px;');
