import requests

URL = "https://ter-s2-d.onrender.com/maze"

def test_labyrinth_dimensions():
    response = requests.get(URL, params={"width": 15, "height": 15})
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["maze"]) == 15
    assert len(data["maze"][0]) == 15

def test_labyrinth_has_corridors():
    response = requests.get(URL, params={"width": 15, "height": 15})
    data = response.json()
    maze = data["maze"]

    nb_couloirs = sum(cell == 1 for row in maze for cell in row)
    assert nb_couloirs > 0