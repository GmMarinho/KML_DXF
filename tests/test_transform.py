import os
import tempfile
from kml_processor.model import PointRecord
from kml_processor import transform, io

def test_to_xyz_and_write_dxf():
    # Cria pontos fictícios
    pts = [
        PointRecord(id="1", name="A", lat=1.0, lon=2.0, properties={}),
        PointRecord(id="2", name="B", lat=3.0, lon=4.0, properties={}),
    ]
    elevs = [10.0, 20.0]
    xyzs = [transform.to_xyz(p, z) for p, z in zip(pts, elevs)]
    print("\n[TEST] XYZ gerados:")
    for x in xyzs:
        print(f"  id={x.id} name={x.name} x={x.x} y={x.y} z={x.z}")
    # Exporta para DXF temporário
    with tempfile.TemporaryDirectory() as tmp:
        dxf_path = os.path.join(tmp, "out.dxf")
        io.write_dxf(dxf_path, xyzs)
        # Lê DXF e valida entidades
        import ezdxf
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        points = [e for e in msp if e.dxftype() == "POINT"]
    texts = [e for e in msp if e.dxftype() == "TEXT"]
    print(f"[TEST] DXF: {len(points)} pontos (sem textos esperados)")
    assert len(points) == 2
    # Modo simplificado: não gera textos
    assert len(texts) == 0
