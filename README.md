# KML_DXF – Pipeline KML → Elevação → XYZ → DXF (Escala Correta/UTM)

## Visão Geral
Ferramenta completa para ingestão de arquivos KML (incluindo `Point`, `LineString`, `MultiGeometry` aninhada), consulta de elevação via OpenTopoData (datasets como `aster30m`), conversão opcional para coordenadas métricas (UTM) e exportação para DXF (e base pronta para CSV/GeoJSON). Inclui caching, redução de requisições via clustering, deduplicação de coordenadas e testes automatizados.

## Principais Recursos (Modo Simplificado)
- Suporte a KML real (pontos + linhas + multigeometrias aninhadas)
- Deduplicação automática de coordenadas (sempre ativa)
- Consulta de elevação em lotes com retry/backoff
- Cache JSON de elevações reutilizável entre execuções
- Projeção automática opcional Lat/Lon → UTM (X/Y em metros; Z já em metros)
- Exportação DXF contendo apenas entidades de PONTO (sem textos) com (X,Y,Z)
- Testes (pytest) e CI configurado

## Arquitetura
```
├── main.py
├── kml_processor/
│   ├── cli.py          # parser de argumentos
│   ├── io.py           # leitura KML + exportação DXF
│   ├── elev.py         # cliente OpenTopoData (batch, cache, clustering)
│   ├── transform.py    # conversões + projeção UTM
│   ├── model.py        # dataclasses PointRecord / XYZRecord
│   └── __init__.py
├── tests/              # testes unitários e de integração
└── examples/           # KMLs reais + caches
```

## Fluxo do Pipeline
1. Ler e parsear o KML (extraindo todas as coordenadas de latitude e longitude)
2. Deduplicar coordenadas automaticamente
3. Consultar elevação (usando cache quando disponível)
4. Converter para XYZ (opcionalmente projetando para UTM)
5. Exportar DXF apenas com pontos 3D (sem labels)

## Instalação
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Uso Básico
```powershell
python main.py --input examples/sample.kml --output examples/out.dxf --dataset aster30m --formats dxf
```

## Uso Avançado (cache + UTM)
```powershell
python main.py \
  --input examples/rionovo.kml \
  --output examples/rionovo_out.dxf \
  --dataset aster30m \
  --enable-cache --cache-file examples/elev_cache_rionovo.json \
  --project-utm \
  --no-labels \
  --formats dxf
```

## Principais Flags (Modo Atual)
| Flag | Descrição |
|------|-----------|
| `--input` | Arquivo KML de entrada (obrigatório) |
| `--output` | Arquivo de saída (ex: `out.dxf`) |
| `--dataset` | Dataset OpenTopoData (`aster30m`, `etopo`, etc.) |
| `--batch-size` | Tamanho de lote por chamada (padrão 100) |
| `--strict` | Falha se alguma elevação não for obtida |
| `--enable-cache` | Ativa cache local de elevações |
| `--cache-file` | Caminho do arquivo de cache JSON |
| `--project-utm` | Converte X/Y para UTM (metros) |
| `--formats` | Formatos de saída (atual: dxf; CSV/GeoJSON futuro) |
| `--progress` | Exibe barra de progresso durante a consulta de elevação |
| `--log-json` | Emite métricas de execução em JSON (inclui points_per_second) |
| `--log-json-file` | Caminho para salvar métricas JSON (senão imprime em stdout) |

## Estratégia de Elevação
- Lotes até 100 pontos → `GET` na API OpenTopoData
- Retry exponencial em respostas 5xx ou exceções de rede
- Cache persistente (chave: "lat,lon") para evitar recomputar
- (Modo simplificado) Sem clustering: cada ponto único é consultado ou recuperado do cache

### Métricas de Execução (Logging JSON)
Exemplo de saída com `--log-json`:
```json
{
  "points_total": 5001,
  "cache_hits": 4800,
  "cache_miss_points": 201,
  "api_batches": 3,
  "elapsed_seconds": 12.53,
  "points_per_second": 399.28,
  "dataset": "aster30m",
  "output": "examples/rionovo_out.dxf",
  "project_utm": true,
  "timestamp": "2025-10-08T12:34:56Z"
}
```

## Projeção UTM e Escala
Sem `--project-utm` os valores X/Y estão em graus e Z em metros (escala distorcida em CAD). Com a flag, todos os eixos ficam em metros (EPSG calculado conforme zona).

## Deduplicação de Coordenadas
Sempre ativa para evitar pontos repetidos provenientes de múltiplas geometrias (LineString / MultiGeometry). Não há opção de desativação no modo atual.

## Testes
```powershell
python -m pytest -q
```

## Próximos Passos (Potenciais)
- Exportações CSV e GeoJSON
- Suporte a malha TIN ou GRID
- Interpolação interna quando API retornar `None`
- Validadores de geometria e estatísticas de elevação

## Dependências Principais
Veja `requirements.txt` para versões fixas (requests, ezdxf, pyproj, scikit-learn, etc.).

### Tabela de Dependências (Resumo)
| Pacote | Uso |
|--------|-----|
| requests | Chamadas HTTP à API OpenTopoData |
| simplekml | Compatibilidade futura com manipulação KML (parse atual é XML manual) |
| ezdxf | Criação de entidades DXF (pontos + texto) |
| shapely | Possíveis operações geométricas futuras (validação, buffers) |
| pandas | Base para futuros exports CSV/GeoJSON estruturados |
| scikit-learn | (Opcional / legado) clustering – não utilizado no modo simplificado atual |
| pyproj | Conversão Lat/Lon → UTM (escala correta no CAD) |
| numpy | Base numérica (suporte a sklearn / pyproj) |
| scipy | Cálculos científicos exigidos por sklearn |
| joblib | Paralelização e cache interno do sklearn |
| threadpoolctl | Gerenciamento de threads para libs nativas |
| tqdm | Barra de progresso de batches de elevação |
| pytest | Testes automatizados |

Remoção segura potencial: `simplekml`, `shapely` (se nenhuma transformação extra for usada). Avaliar antes de produção minimalista.

## Contribuição
PRs e issues são bem-vindos. Abra uma issue descrevendo seu caso de uso ou melhoria desejada.

---
Gerado e mantido como parte de um fluxo iterativo orientado a testes e automações CI.
