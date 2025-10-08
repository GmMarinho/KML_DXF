
"""Funções de conversão e transformação de coordenadas."""
from .model import PointRecord, XYZRecord
from typing import Tuple


def latlon_to_utm(lat: float, lon: float) -> Tuple[float, float]:
	"""Converte coordenadas geográficas (lat, lon) para coordenadas UTM (x, y) em metros.

	Usa pyproj para inferir zona UTM automaticamente com base na longitude.
	"""
	try:
		from pyproj import Transformer
	except Exception:
		raise RuntimeError("pyproj é necessário para projeção UTM. Instale via requirements.txt")

	# Determina zona UTM a partir da longitude
	zone_number = int((lon + 180) / 6) + 1
	is_northern = lat >= 0
	utm_epsg = 32600 + zone_number if is_northern else 32700 + zone_number
	utm_crs = f"EPSG:{utm_epsg}"
	transformer = Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)
	x, y = transformer.transform(lon, lat)
	return x, y


def to_xyz(record: PointRecord, elevation: float) -> XYZRecord:
	"""Converte PointRecord + elevação em XYZRecord (sempre UTM metros)."""
	x, y = latlon_to_utm(record.lat, record.lon)
	return XYZRecord(
		id=record.id,
		name=record.name,
		x=x,
		y=y,
		z=elevation,
		original=record
	)