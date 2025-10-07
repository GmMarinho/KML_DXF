
from kml_processor import cli, io, elev, transform

def main():
    args = cli.parse_args()
    print(f"[CLI] Argumentos: {args}")
    # 1. Ler KML
    points = io.read_kml(args.input)
    print(f"[CLI] {len(points)} pontos lidos do KML")
    # 2. Consultar elevação
    coords = [(p.lat, p.lon) for p in points]
    elevations = elev.get_elevations(coords, provider=args.dataset, batch_size=args.batch_size)
    if args.strict and any(e is None for e in elevations):
        raise RuntimeError("Falha ao obter elevação para todos os pontos (modo --strict)")
    # 3. Transformar para XYZ
    xyzs = [transform.to_xyz(p, z if z is not None else 0.0) for p, z in zip(points, elevations)]
    # 4. Exportar formatos
    if 'dxf' in args.formats:
        io.write_dxf(args.output, xyzs)
        print(f"[CLI] DXF exportado para {args.output}")
    # (csv/geojson podem ser implementados depois)

if __name__ == "__main__":
    main()
