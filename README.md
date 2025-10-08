# KML_DXF – Pipeline KML → Elevação → XYZ → DXF (Escala Correta/UTM)

## Visão Geral
Ferramenta para ingestão de arquivos KML (incluindo `Point`, `LineString`, `MultiGeometry` aninhada), consulta de elevação via OpenTopoData (datasets como `aster30m`), projeção UTM obrigatória e exportação exclusiva para DXF 3D. Inclui caching, deduplicação automática de coordenadas e testes automatizados.

## Principais Recursos (Modo Simplificado)
- Suporte a KML real (pontos + linhas + multigeometrias aninhadas)
- Deduplicação automática de coordenadas (sempre ativa)
- Consulta de elevação em lotes com retry/backoff
- Cache JSON de elevações reutilizável entre execuções
- Projeção UTM obrigatória (X/Y/Z em metros, escala correta para CAD)
- Exportação DXF contendo apenas entidades de PONTO 3D (sem textos, polilinhas ou labels)
- Testes (pytest) e CI configurado

## Arquitetura
```
├── main.py
├── kml_processor/
│   ├── cli.py          # parser de argumentos
│   ├── io.py           # leitura KML + exportação DXF
│   ├── elev.py         # cliente OpenTopoData (batch, cache)
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
4. Converter para XYZ (sempre projetando para UTM)
5. Exportar DXF apenas com pontos 3D

## Instalação
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Uso Básico
```powershell
python main.py --input examples/sample.kml --output examples/out.dxf --dataset aster30m
```

## Uso Avançado (com cache)
```powershell
python main.py \
  --input examples/rionovo.kml \
  --output examples/rionovo_out.dxf \
  --dataset aster30m \
  --enable-cache --cache-file examples/elev_cache_rionovo.json \
  --progress
```


## Principais Flags
| Flag              | Descrição                                         |
|-------------------|--------------------------------------------------|
| `--input`         | Arquivo KML de entrada (obrigatório)              |
| `--output`        | Arquivo de saída DXF 3D (ex: `out.dxf`)           |
| `--dataset`       | Dataset OpenTopoData (`aster30m`, `etopo`, etc.) |
| `--batch-size`    | Tamanho do lote para API de elevação             |
| `--strict`        | Falha se alguma elevação não for obtida          |
| `--enable-cache`  | Ativa cache local de elevações                   |
| `--cache-file`    | Caminho do arquivo de cache JSON                 |
| `--progress`      | Exibe barra de progresso                         |
| `--log-json`      | Emite métricas de execução em JSON               |
| `--log-json-file` | Caminho para salvar métricas JSON                |

  --formats dxf
- Lotes até 100 pontos → `GET` na API OpenTopoData
- Retry exponencial em respostas 5xx ou exceções de rede
- Cache persistente (chave: "lat,lon") para evitar recomputar
- Cada ponto único é consultado ou recuperado do cache

### Métricas de Execução (Logging JSON)
 - Cada ponto único é consultado ou recuperado do cache
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
  "utm": true,
  "timestamp": "2025-10-08T12:34:56Z"
}
```

## Projeção UTM e Escala
Todos os valores X/Y/Z são exportados em metros (UTM), garantindo escala correta para CAD.

## Deduplicação de Coordenadas
Veja `requirements.txt` para versões fixas (requests, ezdxf, pyproj, etc.).

## Testes
```powershell
python -m pytest -q
| (removidos) scikit-learn / numpy / scipy / joblib / threadpoolctl | Não utilizados no modo simplificado |
- Interpolação interna quando API retornar `None`
- Validadores de geometria e estatísticas de elevação

## Dependências Principais
Veja `requirements.txt` para versões fixas (requests, ezdxf, pyproj, etc.).


### Tabela de Dependências
| Pacote    | Propósito técnico                        |
|-----------|------------------------------------------|
| requests  | Requisições à API OpenTopoData           |
| ezdxf     | Geração do DXF 3D                        |
| pyproj    | Projeção UTM e transformações espaciais  |
| xml.etree | Leitura de arquivos KML                  |
| tqdm      | Barra de progresso                       |
| pytest    | Execução de testes automatizados         |



## Contribuição
PRs e issues são bem-vindos. Abra uma issue descrevendo seu caso de uso ou melhoria desejada.

---
Gerado e mantido como parte de um fluxo iterativo orientado a testes e automações CI.
