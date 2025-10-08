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

	# Opções de cache
	parser.add_argument('--enable-cache', action='store_true', help='Ativar cache local de elevações (JSON)')
	parser.add_argument('--cache-file', default='elev_cache.json', help='Arquivo de cache JSON para elevações')

	# Opções de clustering/interpolação
	parser.add_argument('--enable-clustering', action='store_true', help='Ativar clustering/interpolação para otimizar requisições')
	parser.add_argument('--cluster-eps', type=float, default=0.0, help='Distância máxima (em graus) para agrupar pontos próximos (0 desativa)')

	# Projeção de coordenadas
	parser.add_argument('--project-utm', action='store_true', help='Projetar lat/lon para UTM (metros) antes de exportar DXF')

	# Controle de labels no DXF
	parser.add_argument('--no-labels', action='store_true', help='Não exportar textos (nomes/ids) no DXF, apenas pontos')
	parser.add_argument('--keep-duplicates', action='store_true', help='Não remover coordenadas duplicadas ao ler KML')
	parser.add_argument('--progress', action='store_true', help='Exibir barra de progresso durante consulta de elevação')
	parser.add_argument('--log-json', action='store_true', help='Emitir métricas de execução em JSON (stdout ou arquivo)')
	parser.add_argument('--log-json-file', help='Arquivo para salvar métricas JSON (se omitido, imprime no stdout)')
	return parser

def parse_args(args=None):
	parser = build_parser()
	return parser.parse_args(args)