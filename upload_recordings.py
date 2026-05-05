"""Upload tous les enregistrements locaux vers MongoDB via l'API."""
import json
import requests
from pathlib import Path

API_URL = "https://ter-s2-d-85u5.onrender.com"
RECORDINGS_DIR = Path(__file__).parent / "recordings"

files = sorted(RECORDINGS_DIR.glob("game_*.json"))
print(f"{len(files)} fichier(s) a uploader...")

for f in files:
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    existing = data.get("cloud_id")
    if existing:
        print(f"  {f.name} : deja sur le cloud ({existing[:8]}...)")
        continue

    try:
        resp = requests.post(f"{API_URL}/recording", json=data, timeout=60)
        if resp.status_code == 200:
            cloud_id = resp.json().get("id")
            data["cloud_id"] = cloud_id
            with open(f, "w", encoding="utf-8") as fh:
                json.dump(data, fh)
            print(f"  {f.name} => {cloud_id[:8]}...")
        else:
            print(f"  {f.name} : erreur {resp.status_code} - {resp.text[:100]}")
    except Exception as e:
        print(f"  {f.name} : exception - {e}")

print("Termine.")
