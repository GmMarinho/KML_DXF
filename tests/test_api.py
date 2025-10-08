# Teste de integração da API OpenTopoData com cache e clustering
import os
import pytest
from kml_processor import io, elev

SAMPLE_KML = os.path.join(os.path.dirname(__file__), '../examples/sample.kml')

def test_elevation_api_cache_and_clustering(tmp_path):
	# Lê pontos do sample.kml
	points = io.read_kml(SAMPLE_KML)
	coords = [(p.lat, p.lon) for p in points]
	cache_file = tmp_path / 'elev_cache.json'

	# 1. Testa consulta sem cache nem clustering
	elevs = elev.get_elevations(coords, provider='aster30m', batch_size=100, enable_cache=False, enable_clustering=False)
	print(f"[TEST] Elevations (no cache, no clustering): {elevs}")
	assert len(elevs) == len(coords)
	assert all(e is None or isinstance(e, (float, int)) for e in elevs)

	# 2. Testa consulta com cache
	elevs2 = elev.get_elevations(coords, provider='aster30m', batch_size=100, enable_cache=True, cache_file=str(cache_file), enable_clustering=False)
	print(f"[TEST] Elevations (with cache): {elevs2}")
	assert elevs2 == elevs  # Deve bater pois cache foi preenchido

	# 3. Testa consulta com clustering (eps pequeno para não agrupar)
	elevs3 = elev.get_elevations(coords, provider='aster30m', batch_size=100, enable_cache=True, cache_file=str(cache_file), enable_clustering=True, cluster_eps=0.00001)
	print(f"[TEST] Elevations (with clustering, eps=0.00001): {elevs3}")
	assert elevs3 == elevs

	# 4. Testa consulta com clustering (eps grande para agrupar tudo)
	elevs4 = elev.get_elevations(coords, provider='aster30m', batch_size=100, enable_cache=True, cache_file=str(cache_file), enable_clustering=True, cluster_eps=1.0)
	print(f"[TEST] Elevations (with clustering, eps=1.0): {elevs4}")
	assert len(elevs4) == len(coords)
	assert all(e is None or isinstance(e, (float, int)) for e in elevs4)
