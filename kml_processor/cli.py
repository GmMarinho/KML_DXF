"""Interface de linha de comando (CLI) do projeto."""

import argparse

def build_parser():
	parser = argparse.ArgumentParser(description="Pipeline KML → XYZ → DXF/CSV/GeoJSON")
	parser.add_argument('--input', '-i', required=True, help='Arquivo KML de entrada')
	parser.add_argument('--output', '-o', required=True, help='Arquivo de saída (ex: out.dxf)')
	parser.add_argument('--dataset', default='etopo', help='Dataset OpenTopoData (ex: srtm90m, etopo)')
	parser.add_argument('--batch-size', type=int, default=100, help='Tamanho do lote para API de elevação')
	parser.add_argument('--strict', action='store_true', help='Abortar se houver falha de elevação')
	parser.add_argument('--formats', nargs='+', default=['dxf'], help='Formatos de saída: dxf, csv, geojson')
	return parser

def parse_args(args=None):
	parser = build_parser()
	return parser.parse_args(args)