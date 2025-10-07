import os
import pytest
from kml_processor import io

EXAMPLES = os.path.join(os.path.dirname(__file__), '..', 'examples')

def test_read_kml_linestring():
    kml_path = os.path.join(EXAMPLES, 'rionovo.kml')
    points = io.read_kml(kml_path)
    print(f"\n[TEST] rionovo.kml: {len(points)} pontos extraídos")
    # Deve extrair muitos pontos de LineString
    assert len(points) > 1000
    # Verifica se todos os pontos têm lat/lon válidos
    for p in points:
        assert -90 <= p.lat <= 90
        assert -180 <= p.lon <= 180
