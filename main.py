
from kml_processor import cli, io, elev, transform
import json, time

def main():
    args = cli.parse_args()
    print(f"[CLI] Argumentos: {args}")
    # 1. Ler KML
    points = io.read_kml(args.input)
    print(f"[CLI] {len(points)} pontos lidos do KML")
    # 2. Consultar elevação
    coords = [(p.lat, p.lon) for p in points]
    stats = {}
    elevations = elev.get_elevations(
        coords,
        provider=args.dataset,
        batch_size=args.batch_size,
        enable_cache=getattr(args, 'enable_cache', False),
        cache_file=getattr(args, 'cache_file', 'elev_cache.json'),
        show_progress=getattr(args, 'progress', False),
        _stats=stats if getattr(args, 'log_json', False) else None
    )
    if args.strict and any(e is None for e in elevations):
        raise RuntimeError("Falha ao obter elevação para todos os pontos (modo --strict)")
    # 3. Transformar para XYZ (sempre projetando para UTM)
    xyzs = [transform.to_xyz(p, z if z is not None else 0.0) for p, z in zip(points, elevations)]
    # Depuração: imprimir estatísticas dos valores de Z
    zs = [pt.z for pt in xyzs]
    print(f"[DEBUG] Z min: {min(zs):.2f}, max: {max(zs):.2f}, únicos: {sorted(set(zs))[:10]} ... total únicos: {len(set(zs))}")
    # 4. Exportar DXF
    io.write_dxf(args.output, xyzs)
    print(f"[CLI] DXF exportado para {args.output}")

    if getattr(args, 'log_json', False):
        stats.update({
            "dataset": args.dataset,
            "output": args.output,
            "utm": True,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })
        payload = json.dumps(stats, ensure_ascii=False, indent=2)
        out_file = getattr(args, 'log_json_file', None)
        if out_file:
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(payload)
            print(f"[CLI] Métricas JSON salvas em {out_file}")
        else:
            print("[CLI][METRICS]" )
            print(payload)
    # ...existing code...

if __name__ == "__main__":
    main()
