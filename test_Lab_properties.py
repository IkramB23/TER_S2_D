import requests

URL = "https://ter-s2-d.onrender.com/maze"

def test_labyrinth_has_corridors():
    response = requests.get(URL, params={"width": 15, "height": 15})
    assert response.status_code == 200

    data = response.json()
    maze = data["maze"]

    nb_couloirs = sum(
        1 for row in maze for cell in row if cell == 1
    )

    assert nb_couloirs > 0, "Le Labyrinthe ne contient aucun couloir"