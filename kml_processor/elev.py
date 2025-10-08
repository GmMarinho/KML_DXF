
"""Cliente da API OpenTopoData."""
import time
import requests
import json
import os
from typing import List, Tuple, Optional, Dict

from sklearn.cluster import DBSCAN

def get_elevations(
	points: List[Tuple[float, float]],
	provider: str = 'etopo',
	batch_size: int = 100,
	timeout: float = 10.0,
	max_retries: int = 3,
	enable_cache: bool = False,
	cache_file: str = 'elev_cache.json',
	enable_clustering: bool = False,
	cluster_eps: float = 0.0
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

	# Estratégia de clustering/interpolação
	clustered_points = points
	cluster_map = None
	if enable_clustering and cluster_eps > 0.0 and len(points) > 1:
		# DBSCAN para agrupar pontos próximos
		import numpy as np
		arr = np.array(points)
		db = DBSCAN(eps=cluster_eps, min_samples=1, metric='euclidean').fit(arr)
		labels = db.labels_
		# Para cada cluster, usar o primeiro ponto como representante
		cluster_map = {}
		rep_points = []
		for idx, label in enumerate(labels):
			if label not in cluster_map:
				cluster_map[label] = idx
				rep_points.append(points[idx])
		clustered_points = rep_points

	# Mapear pontos para índices originais
	point_to_indices = {}
	for idx, pt in enumerate(points):
		key = f"{pt[0]:.7f},{pt[1]:.7f}"
		point_to_indices.setdefault(key, []).append(idx)

	# Consultar elevação para pontos únicos (considerando cache)
	to_query = []
	query_indices = []
	for i, pt in enumerate(clustered_points):
		key = f"{pt[0]:.7f},{pt[1]:.7f}"
		if enable_cache and key in cache:
			continue
		to_query.append(pt)
		query_indices.append(i)

	# Fazer requisições em lote
	elevations: List[Optional[float]] = [None] * len(clustered_points)
	for i in range(0, len(to_query), batch_size):
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
	if enable_clustering and cluster_eps > 0.0 and cluster_map is not None:
		# Cada ponto original pega a elevação do representante do seu cluster
		import numpy as np
		arr = np.array(points)
		db = DBSCAN(eps=cluster_eps, min_samples=1, metric='euclidean').fit(arr)
		labels = db.labels_
		# Para cada ponto original, encontre o representante do cluster
		for idx, label in enumerate(labels):
			rep_idx = cluster_map[label]
			elev = None
			# Tenta pegar do cache primeiro
			key = f"{points[rep_idx][0]:.7f},{points[rep_idx][1]:.7f}"
			if enable_cache and key in cache:
				elev = cache[key]
			else:
				elev = elevations[list(cluster_map.values()).index(rep_idx)]
			results[idx] = elev
	else:
		# Sem clustering: cada ponto pega sua elevação (do cache ou consulta)
		for idx, pt in enumerate(points):
			key = f"{pt[0]:.7f},{pt[1]:.7f}"
			elev = cache.get(key) if enable_cache else None
			if elev is not None:
				results[idx] = elev
			else:
				# Se não estava no cache, buscar na lista de elevs
				if pt in clustered_points:
					elev_idx = clustered_points.index(pt)
					results[idx] = elevations[elev_idx]
				else:
					results[idx] = None

	return results