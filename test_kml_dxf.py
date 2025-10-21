import pytest
import os
from kml_dxf import extrair_coordenadas_kml, criar_dxf

def test_extrair_coordenadas_kml():
    # KML de exemplo com um ponto
    kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
      <Document>
        <Placemark>
          <name>teste</name>
          <Point>
            <coordinates>-35.20989232587857,-5.839852418981317,10</coordinates>
          </Point>
        </Placemark>
      </Document>
    </kml>'''
    with open("temp_test.kml", "w", encoding="utf-8") as f:
        f.write(kml_content)
    pontos, linhas, poligonos, pontos_por_nome = extrair_coordenadas_kml("temp_test.kml")
    os.remove("temp_test.kml")
    assert len(pontos) == 1
    assert pontos[0][0] == -35.20989232587857
    assert pontos[0][1] == -5.839852418981317
    assert pontos[0][2] == 10
    assert pontos[0][3] == "teste"
    assert len(linhas) == 0
    assert len(poligonos) == 0
    assert "teste" in pontos_por_nome


def test_criar_dxf(tmp_path):
    pontos = [(-35.20989232587857, -5.839852418981317, 10, "teste")]
    linhas = []
    poligonos = []
    pontos_por_nome = {"teste": [(-35.20989232587857, -5.839852418981317, 10)]}
    dxf_path = tmp_path / "test.dxf"
    aviso = criar_dxf(pontos, linhas, poligonos, pontos_por_nome, str(dxf_path))
    assert os.path.exists(dxf_path)
    assert aviso is None or isinstance(aviso, str)
