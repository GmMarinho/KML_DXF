
"""Cliente da API OpenTopoData."""
import time
import requests
import json
import os
from typing import List, Tuple, Optional, Dict

try:
    from tqdm import tqdm  # type: ignore
except Exception:  # fallback silencioso
    tqdm = None  # type: ignore

def get_elevations(
	points: List[Tuple[float, float]],
	provider: str = 'etopo',
	batch_size: int = 100,
	timeout: float = 10.0,
	max_retries: int = 3,
	enable_cache: bool = False,
	cache_file: str = 'elev_cache.json',
	show_progress: bool = False,
	_stats: Optional[Dict[str, float]] = None
) -> List[Optional[float]]:
	"""
	Consulta a API OpenTopoData para obter elevações de uma lista de (lat, lon).
	Retorna lista de elevações (float) ou None para falha.
	"""
	endpoint = f"https://api.opentopodata.org/v1/{provider}"
	results: List[Optional[float]] = [None] * len(points)

	# Carregar cache se ativado
	cache: Dict[str, float] = {}
	if enable_cache and os.path.exists(cache_file):
		try:
			with open(cache_file, 'r', encoding='utf-8') as f:
				cache = json.load(f)
		except Exception:
			cache = {}

	#

	# Mapear pontos para índices originais
	point_to_indices = {}
	for idx, pt in enumerate(points):
		key = f"{pt[0]:.7f},{pt[1]:.7f}"
		point_to_indices.setdefault(key, []).append(idx)

	# Consultar elevação para pontos únicos (considerando cache)
	to_query = []
	query_indices = []
	cache_hits = 0
	cache_miss_points = 0
	for i, pt in enumerate(points):
		key = f"{pt[0]:.7f},{pt[1]:.7f}"
		if enable_cache and key in cache:
			cache_hits += 1
			continue
		to_query.append(pt)
		query_indices.append(i)
		cache_miss_points += 1

	# Fazer requisições em lote
	elevations: List[Optional[float]] = [None] * len(points)
	iterator = range(0, len(to_query), batch_size)
	api_batches = 0
	start_time = time.time()
	if show_progress and tqdm is not None:
		iterator = tqdm(iterator, total=max(1, (len(to_query) + batch_size - 1)//batch_size), desc="Elevations", unit="batch")  # type: ignore
	for i in iterator:  # type: ignore
		api_batches += 1
		batch = to_query[i:i+batch_size]
		locations = "|".join(f"{lat},{lon}" for lat, lon in batch)
		params = {"locations": locations}
		attempt = 0
		while attempt <= max_retries:
			try:
				resp = requests.get(endpoint, params=params, timeout=timeout)
				if resp.status_code == 200:
					data = resp.json()
					if data.get("status") == "OK":
						for j, res in enumerate(data["results"]):
							elev = res.get("elevation")
							idx = i + j
							if idx < len(query_indices):
								elevations[query_indices[idx]] = elev
								# Atualizar cache
								if enable_cache:
									key = f"{batch[j][0]:.7f},{batch[j][1]:.7f}"
									cache[key] = elev
						break
					else:
						# Falha lógica da API
						for j in range(len(batch)):
							idx = i + j
							if idx < len(query_indices):
								elevations[query_indices[idx]] = None
						break
				elif 500 <= resp.status_code < 600:
					attempt += 1
					time.sleep(2 ** attempt)
				else:
					for j in range(len(batch)):
						idx = i + j
						if idx < len(query_indices):
							elevations[query_indices[idx]] = None
					break
			except requests.RequestException:
				attempt += 1
				time.sleep(2 ** attempt)
		else:
			for j in range(len(batch)):
				idx = i + j
				if idx < len(query_indices):
					elevations[query_indices[idx]] = None

	# Salvar cache se ativado
	if enable_cache:
		try:
			with open(cache_file, 'w', encoding='utf-8') as f:
				json.dump(cache, f)
		except Exception:
			pass

	# Mapear elevações de volta para todos os pontos originais
	# Cada ponto pega sua elevação (do cache ou da consulta)
	for idx, pt in enumerate(points):
		key = f"{pt[0]:.7f},{pt[1]:.7f}"
		elev = cache.get(key) if enable_cache else None
		if elev is not None:
			results[idx] = elev
		else:
			if pt in points:
				elev_idx = points.index(pt)
				results[idx] = elevations[elev_idx]
			else:
				results[idx] = None

	end_time = time.time()
	if _stats is not None:
		elapsed = max(1e-9, end_time - start_time)
		_stats.update({
			"points_total": float(len(points)),
			"cache_hits": float(cache_hits),
			"cache_miss_points": float(cache_miss_points),
			"api_batches": float(api_batches),
			"elapsed_seconds": elapsed,
			"points_per_second": float(len(points))/elapsed,
		})
	return results