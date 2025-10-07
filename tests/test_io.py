import os
import pytest
from kml_processor import io

EXAMPLES = os.path.join(os.path.dirname(__file__), '..', 'examples')

def test_read_kml_points():
    kml_path = os.path.join(EXAMPLES, 'sample.kml')
    points = io.read_kml(kml_path)
    print("\n[TEST] Pontos lidos do sample.kml:")
    for p in points:
        print(f"  id={p.id} name={p.name} lat={p.lat} lon={p.lon} props={p.properties}")
    assert len(points) == 2
    assert points[0].name == 'Ponto A'
    assert points[0].lat < 0 and points[0].lon < 0
    assert points[1].name == 'Ponto B'

def test_read_kml_invalid():
    # KML sem pontos
    kml_path = os.path.join(EXAMPLES, 'empty.kml')
    with open(kml_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document></Document></kml>')
    with pytest.raises(ValueError) as excinfo:
        io.read_kml(kml_path)
    print(f"\n[TEST] Erro esperado para KML vazio: {excinfo.value}")
    os.remove(kml_path)
