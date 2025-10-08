# Teste de integração da API OpenTopoData (modo simplificado, sem clustering)
import os
import pytest
from kml_processor import io, elev

SAMPLE_KML = os.path.join(os.path.dirname(__file__), '../examples/sample.kml')

def test_elevation_api_cache(tmp_path):
	# Lê pontos do sample.kml
	points = io.read_kml(SAMPLE_KML)
	coords = [(p.lat, p.lon) for p in points]
	cache_file = tmp_path / 'elev_cache.json'

	# 1. Testa consulta sem cache
	elevs = elev.get_elevations(coords, provider='aster30m', batch_size=100, enable_cache=False)
	print(f"[TEST] Elevations (no cache): {elevs}")
	assert len(elevs) == len(coords)
	assert all(e is None or isinstance(e, (float, int)) for e in elevs)

	# 2. Testa consulta com cache
	elevs2 = elev.get_elevations(coords, provider='aster30m', batch_size=100, enable_cache=True, cache_file=str(cache_file))
	print(f"[TEST] Elevations (with cache): {elevs2}")
	assert elevs2 == elevs  # Deve bater pois cache foi preenchido
