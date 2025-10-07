
"""Cliente da API OpenTopoData."""
import time
import requests
from typing import List, Tuple, Optional

def get_elevations(
	points: List[Tuple[float, float]],
	provider: str = 'etopo',
	batch_size: int = 100,
	timeout: float = 10.0,
	max_retries: int = 3
) -> List[Optional[float]]:
	"""
	Consulta a API OpenTopoData para obter elevações de uma lista de (lat, lon).
	Retorna lista de elevações (float) ou None para falha.
	"""
	endpoint = f"https://api.opentopodata.org/v1/{provider}"
	results = []
	for i in range(0, len(points), batch_size):
		batch = points[i:i+batch_size]
		locations = "|".join(f"{lat},{lon}" for lat, lon in batch)
		params = {"locations": locations}
		attempt = 0
		while attempt <= max_retries:
			try:
				resp = requests.get(endpoint, params=params, timeout=timeout)
				if resp.status_code == 200:
					data = resp.json()
					if data.get("status") == "OK":
						for res in data["results"]:
							results.append(res.get("elevation"))
						break
					else:
						# Falha lógica da API
						results.extend([None] * len(batch))
						break
				elif 500 <= resp.status_code < 600:
					# Retry em erro 5xx
					attempt += 1
					time.sleep(2 ** attempt)
				else:
					# Erro 4xx: não retry
					results.extend([None] * len(batch))
					break
			except requests.RequestException:
				attempt += 1
				time.sleep(2 ** attempt)
		else:
			# Se esgotou tentativas
			results.extend([None] * len(batch))
	return results