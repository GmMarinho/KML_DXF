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

def test_read_kml_dedup(tmp_path):
    # Monta KML com coordenadas repetidas (mesmo ponto em Point e LineString)
    kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2"><Document>
        <Placemark><name>P1</name><Point><coordinates>-46.0,-21.0,0</coordinates></Point>
            <LineString><coordinates>-46.0,-21.0,0 -46.0001,-21.0001,0</coordinates></LineString>
        </Placemark>
    </Document></kml>'''
    test_path = tmp_path / 'dup.kml'
    test_path.write_text(kml_content, encoding='utf-8')
    pts = io.read_kml(str(test_path))
    coords = [(p.lat, p.lon) for p in pts]
    print(f"\n[TEST] Dedup coords: {coords}")
    # Espera apenas dois pontos únicos (deduplicação sempre ativa)
    assert len(coords) == 2
