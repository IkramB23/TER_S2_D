# test_api.py
import requests

url = "https://ter-s2-d.onrender.com/maze"
params = {"width": 15, "height": 15}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print("Maze reçu :")
    print("Largeur:", data["width"])
    print("Hauteur:", data["height"])
else:
    print("Erreur :", response.status_code)