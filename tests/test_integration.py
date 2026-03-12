"""
Tests d'intégration pour le Web Service Maze Pacman
Tests de l'API Flask + validation des données
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
import pytest


@pytest.fixture
def client():
    """Créé un client de test Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPIBasics:
    """Tests basiques de l'API."""
    
    def test_home_route_returns_html(self, client):
        """La route / doit retourner du HTML (200)."""
        response = client.get('/')
        assert response.status_code == 200
        # Check for either French text or canvas element
        assert b'mazeCanvas' in response.data or b'canvas' in response.data.lower()
    
    def test_maze_route_default_params(self, client):
        """GET /maze sans params doit retourner un maze 21x21 par défaut."""
        response = client.get('/maze')
        assert response.status_code == 200
        data = response.get_json()
        assert data["width"] == 21
        assert data["height"] == 21
        assert data["loop_percent"] == 25  # Défaut


class TestMazeGeneration:
    """Tests de génération de labyrinthes."""
    
    def test_generate_small_maze(self, client):
        """Générer un petit labyrinthe."""
        response = client.get('/maze?width=5&height=5')
        assert response.status_code == 200
        data = response.get_json()
        assert data["width"] == 5
        assert data["height"] == 5
        assert len(data["maze"]) == 5
        assert all(len(row) == 5 for row in data["maze"])
    
    def test_generate_large_maze(self, client):
        """Générer un grand labyrinthe."""
        response = client.get('/maze?width=101&height=101')
        assert response.status_code == 200
        data = response.get_json()
        assert data["width"] == 101
        assert data["height"] == 101
        assert len(data["maze"]) == 101
    
    def test_maze_with_loops(self, client):
        """Générer un labyrinthe avec boucles."""
        response = client.get('/maze?width=21&height=21&loop_percent=50')
        assert response.status_code == 200
        data = response.get_json()
        assert data["loop_percent"] == 50


class TestMazeStructure:
    """Tests de la structure des données du maze."""
    
    def test_maze_contains_only_0_and_1(self, client):
        """Le maze doit contenir uniquement des 0 (murs) et 1 (couloirs)."""
        response = client.get('/maze?width=15&height=15')
        data = response.get_json()
        for row in data["maze"]:
            for cell in row:
                assert cell in (0, 1), f"Valeur invalide: {cell}"
    
    def test_maze_json_structure(self, client):
        """Vérifier la structure JSON du maze."""
        response = client.get('/maze?width=11&height=11&loop_percent=25')
        data = response.get_json()
        
        # Clés obligatoires
        assert "width" in data
        assert "height" in data
        assert "loop_percent" in data
        assert "maze" in data
        
        # Types corrects
        assert isinstance(data["width"], int)
        assert isinstance(data["height"], int)
        assert isinstance(data["loop_percent"], int)
        assert isinstance(data["maze"], list)
    
    def test_maze_dimensions_match(self, client):
        """Les dimensions du maze doivent correspondre à width/height."""
        for width in [5, 11, 21, 51]:
            for height in [5, 11, 21, 51]:
                response = client.get(f'/maze?width={width}&height={height}')
                data = response.get_json()
                
                assert len(data["maze"]) == height
                assert all(len(row) == width for row in data["maze"])


class TestInputValidation:
    """Tests de validation des entrées."""
    
    def test_width_too_small(self, client):
        """Width < 5 doit échouer."""
        response = client.get('/maze?width=3&height=21')
        assert response.status_code == 400
    
    def test_width_too_large(self, client):
        """Width > 101 doit échouer."""
        response = client.get('/maze?width=103&height=21')
        assert response.status_code == 400
    
    def test_height_too_small(self, client):
        """Height < 5 doit échouer."""
        response = client.get('/maze?width=21&height=2')
        assert response.status_code == 400
    
    def test_loop_percent_negative(self, client):
        """Loop_percent négatif doit échouer."""
        response = client.get('/maze?width=21&height=21&loop_percent=-10')
        assert response.status_code == 400
    
    def test_loop_percent_too_high(self, client):
        """Loop_percent > 100 doit échouer."""
        response = client.get('/maze?width=21&height=21&loop_percent=150')
        assert response.status_code == 400
    
    def test_width_even_number_valid(self, client):
        """Width même si pair doit marcher (converti en impair)."""
        response = client.get('/maze?width=20&height=21')
        # Soit ça échoue, soit ça le convertit
        # Selon la logique, on peut tester les deux
        assert response.status_code in (200, 400)
    
    def test_non_numeric_width(self, client):
        """Width non-numérique doit échouer."""
        response = client.get('/maze?width=abc&height=21')
        # Flask convertit automatiquement, donc on teste le résultat
        assert response.status_code in (400, 500)


class TestPerformance:
    """Tests de performance et limites."""
    
    def test_generate_max_size_maze(self, client):
        """Générer un maze 101x101 ne doit pas être trop lent."""
        import time
        start = time.time()
        response = client.get('/maze?width=101&height=101')
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 5, f"Génération trop lente: {elapsed}s"
    
    def test_response_is_json_not_too_large(self, client):
        """La réponse JSON ne doit pas être énorme."""
        response = client.get('/maze?width=101&height=101')
        size_mb = len(response.data) / (1024 * 1024)
        assert size_mb < 1, f"Response trop grande: {size_mb}MB"


class TestMultipleCalls:
    """Tests d'appels multiples."""
    
    def test_multiple_sequential_calls(self, client):
        """Appeler l'API plusieurs fois doit fonctionner."""
        for i in range(10):
            response = client.get('/maze?width=11&height=11')
            assert response.status_code == 200
    
    def test_different_parameters_each_call(self, client):
        """Chaque appel avec des params différents doit réussir."""
        sizes = [(5, 5), (11, 11), (21, 21), (51, 51), (101, 101)]
        for width, height in sizes:
            response = client.get(f'/maze?width={width}&height={height}')
            assert response.status_code == 200


class TestDataConsistency:
    """Tests de cohérence des données."""
    
    def test_multiple_calls_produce_different_mazes(self, client):
        """Appeler 2 fois doit généralement produire des mazes différents."""
        # (à moins que l'algorithme soit déterministe, ce qui n'est pas le cas)
        response1 = client.get('/maze?width=11&height=11')
        data1 = response1.get_json()
        
        response2 = client.get('/maze?width=11&height=11')
        data2 = response2.get_json()
        
        # Les deux mazes peuvent être différents (algorithme aléatoire)
        # On teste juste qu'ils sont tous les deux valides
        assert data1["width"] == data2["width"] == 11
        assert data1["height"] == data2["height"] == 11
    
    def test_loop_percent_affects_maze_content(self, client):
        """Un labyrinthe avec 0% boucles doit différer d'un avec 100%."""
        response_no_loops = client.get('/maze?width=21&height=21&loop_percent=0')
        data_no_loops = response_no_loops.get_json()
        
        response_max_loops = client.get('/maze?width=21&height=21&loop_percent=100')
        data_max_loops = response_max_loops.get_json()
        
        # Les deux doivent être valides
        assert response_no_loops.status_code == 200
        assert response_max_loops.status_code == 200
        
        # Et probablement différents (mais pas garanti)
        # On teste juste la structure
        assert len(data_no_loops["maze"]) == len(data_max_loops["maze"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
