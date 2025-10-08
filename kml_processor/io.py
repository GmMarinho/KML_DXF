

from typing import List, Set, Tuple
from .model import PointRecord, XYZRecord

def write_dxf(path: str, points: List[XYZRecord], layer: str = "Pontos") -> None:
	"""Exporta pontos 3D para DXF (somente entidades POINT no modo simplificado)."""
	import ezdxf
	doc = ezdxf.new(dxfversion="R2010")
	msp = doc.modelspace()
	for pt in points:
		msp.add_point((pt.x, pt.y, pt.z), dxfattribs={"layer": layer})
	doc.saveas(path)

def read_kml(path: str) -> List[PointRecord]:
	"""
	Lê um arquivo KML e retorna uma lista de PointRecord.
	Lança ValueError se não encontrar pontos válidos.
	"""
	import simplekml
	import os
	if not os.path.exists(path):
		raise FileNotFoundError(f"Arquivo não encontrado: {path}")
	kml = simplekml.Kml()
	# simplekml só lê arquivos via from_file
	kml = simplekml.Kml()
	kml = simplekml.Kml()
	kml = simplekml.Kml()
	# Usar o método from_file para ler o arquivo
	kml = simplekml.Kml()
	kml = simplekml.Kml()
	# simplekml não tem parsing de arquivo pronto, então parse manual
	# Vamos fazer parsing manual do XML para extrair os pontos
	import xml.etree.ElementTree as ET
	tree = ET.parse(path)
	root = tree.getroot()
	ns = {'kml': 'http://www.opengis.net/kml/2.2'}
	points: List[PointRecord] = []
	seen: Set[Tuple[float, float]] = set()
	for placemark in root.findall('.//kml:Placemark', ns):
		name_el = placemark.find('kml:name', ns)
		name = name_el.text if name_el is not None else None
		desc_el = placemark.find('kml:description', ns)
		desc = desc_el.text if desc_el is not None else None
		props = {}
		if desc:
			props['description'] = desc

		# Extrai pontos simples
		point = placemark.find('kml:Point', ns)
		if point is not None:
			coords = point.find('kml:coordinates', ns)
			if coords is not None and coords.text:
				try:
					lon, lat, *_ = [float(x) for x in coords.text.strip().split(',')]
				except Exception:
					continue
				if not (-90 <= lat <= 90 and -180 <= lon <= 180):
					continue
				if (lat, lon) in seen:
					continue
				seen.add((lat, lon))
				pid = name or f"pt{len(points)+1}"
				points.append(PointRecord(id=str(pid), name=name, lat=lat, lon=lon, properties=props))

		# Extrai pontos de LineString (apenas diretamente sob Placemark)
		for linestring in placemark.findall('kml:LineString', ns):
			coords = linestring.find('kml:coordinates', ns)
			if coords is not None and coords.text:
				coord_list = coords.text.strip().split()
				for idx, coord in enumerate(coord_list):
					try:
						lon, lat, *_ = [float(x) for x in coord.split(',')]
					except Exception:
						continue
					if not (-90 <= lat <= 90 and -180 <= lon <= 180):
						continue
					if (lat, lon) in seen:
						continue
					seen.add((lat, lon))
					pid = f"{name or 'Line'}_{idx+1}"
					points.append(PointRecord(id=str(pid), name=name, lat=lat, lon=lon, properties=props))

		# Extrai pontos de MultiGeometry (LineString dentro de MultiGeometry)
		for multigeom in placemark.findall('kml:MultiGeometry', ns):
			for linestring in multigeom.findall('kml:LineString', ns):
				coords = linestring.find('kml:coordinates', ns)
				if coords is not None and coords.text:
					coord_list = coords.text.strip().split()
					for idx, coord in enumerate(coord_list):
						try:
							lon, lat, *_ = [float(x) for x in coord.split(',')]
						except Exception:
							continue
						if not (-90 <= lat <= 90 and -180 <= lon <= 180):
							continue
						if (lat, lon) in seen:
							continue
						seen.add((lat, lon))
						pid = f"{name or 'MultiGeom'}_{idx+1}"
						points.append(PointRecord(id=str(pid), name=name, lat=lat, lon=lon, properties=props))
	if not points:
		raise ValueError("Nenhum ponto válido encontrado no KML.")
	return points