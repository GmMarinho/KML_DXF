
"""Funções de conversão e transformação de coordenadas."""
from .model import PointRecord, XYZRecord

def to_xyz(record: PointRecord, elevation: float) -> XYZRecord:
	"""
	Converte PointRecord + elevação em XYZRecord.
	Por padrão: X=lat, Y=lon, Z=elevation.
	"""
	return XYZRecord(
		id=record.id,
		name=record.name,
		x=record.lat,
		y=record.lon,
		z=elevation,
		original=record
	)