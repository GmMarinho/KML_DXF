
"""Modelos de dados: PointRecord, XYZRecord, etc."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class PointRecord:
	"""Representa um ponto extraído do KML."""
	id: str
	name: Optional[str]
	lat: float
	lon: float
	properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class XYZRecord:
	"""Representa um ponto com coordenadas XYZ e metadados."""
	id: str
	name: Optional[str]
	x: float
	y: float
	z: float
	original: PointRecord