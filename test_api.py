import requests

URL = "https://ter-s2-d.onrender.com/maze"

params = {"width": 15, "height": 15}

response = requests.get(URL, params=params)

assert response.status_code == 200, "Erreur HTTP"

data = response.json()

assert data["width"] == 15, "Largeur incorrecte"
assert data["height"] == 15, "Hauteur incorrecte"
assert len(data["maze"]) == 15, "Mauvais nombre de lignes"
assert len(data["maze"][0]) == 15, "Mauvais nombre de colonnes"

print("Test API OK- Labytinthe généré avec succès!")