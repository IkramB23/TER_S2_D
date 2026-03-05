# Tests de l'API Flask en local (sans Render)
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app


def get_client():
    """Cree un client de test Flask."""
    app.config['TESTING'] = True
    return app.test_client()


# ============ Tests de l'API ============

def test_home_route():
    """La route / doit repondre 200."""
    client = get_client()
    response = client.get('/')
    assert response.status_code == 200


def test_maze_route_default():
    """GET /maze sans params doit retourner un maze 21x21."""
    client = get_client()
    response = client.get('/maze')
    assert response.status_code == 200
    data = response.get_json()
    assert data["width"] == 21
    assert data["height"] == 21
    assert len(data["maze"]) == 21
    assert len(data["maze"][0]) == 21


def test_maze_route_custom_size():
    """GET /maze?width=15&height=15 doit retourner 15x15."""
    client = get_client()
    response = client.get('/maze?width=15&height=15')
    assert response.status_code == 200
    data = response.get_json()
    assert data["width"] == 15
    assert data["height"] == 15
    assert len(data["maze"]) == 15
    assert len(data["maze"][0]) == 15


def test_maze_route_returns_json():
    """La reponse doit etre du JSON valide avec width, height, maze."""
    client = get_client()
    response = client.get('/maze?width=11&height=11')
    data = response.get_json()
    assert "width" in data
    assert "height" in data
    assert "maze" in data
    assert isinstance(data["maze"], list)


def test_maze_contains_0_and_1():
    """Le maze retourne doit contenir que des 0 et 1."""
    client = get_client()
    response = client.get('/maze?width=15&height=15')
    data = response.get_json()
    for row in data["maze"]:
        for cell in row:
            assert cell in (0, 1)
