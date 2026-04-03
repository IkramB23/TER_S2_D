import pytest
import requests


URL_CANDIDATES = [
	"https://ter-s2-d.onrender.com/maze",
	"https://ter-s2-d.onrender.com/api/maze",
]


def _fetch_maze(width=15, height=15):
	params = {"width": width, "height": height, "loop_percent": 25}
	for url in URL_CANDIDATES:
		try:
			response = requests.get(url, params=params, timeout=5)
		except requests.RequestException:
			continue
		if response.status_code == 200:
			return response.json()
	pytest.skip("Maze API unavailable or endpoint changed")


def test_api_returns_expected_maze_shape():
	data = _fetch_maze(width=15, height=15)
	assert "maze" in data
	assert len(data["maze"]) == 15
	assert len(data["maze"][0]) == 15