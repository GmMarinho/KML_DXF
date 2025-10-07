# kml (definição do projeto)

Visão geral
----------
O projeto `kml` é uma ferramenta em Python para processar arquivos KML, extrair coordenadas (latitude, longitude) de pontos, obter a elevação para cada coordenada usando a API OpenTopoData, compor coordenadas em um sistema XYZ (latitude -> X, longitude -> Y, elevação -> Z) e exportar os resultados como um arquivo DXF preservando as coordenadas geográficas (X = latitude, Y = longitude, Z = elevação).

Objetivos
---------
- Ler arquivos KML (pontos) e extrair informações relevantes (nome, lat, lon).
- Para cada ponto, consultar a API OpenTopoData para recuperar a elevação.
- Gerar uma representação XYZ dos pontos e permitir exportação em DXF (para uso em CAD) e CSV/GeoJSON para interoperabilidade.
- Ser testável, modular e fácil de integrar em pipelines.

Dependências (sugestão inicial)
-------------------------------
Recomendado usar um ambiente virtual (`.venv`). Dependências principais a incluir em `requirements.txt`:

- simplekml (ou pykml) — para parse de KML (ex.: `pykml` ou `simplekml`/`fastkml`)
- requests — para chamadas HTTP à API OpenTopoData
- shapely — para operações geométricas se necessário
- ezdxf — para gerar DXF
- pandas — para exportar CSV e manipular tabelas de pontos (opcional)
- pytest — para testes
- ruff ou flake8 — linting (opcional)

Exemplo de `requirements.txt` inicial
------------------------------------
```
requests==2.32.5
pykml==0.9.0
ezdxf==0.19.??  # use versão compatível; ajustar conforme disponibilidade
shapely==2.1.1
pandas==2.3.3
pytest==7.4.0
```

Arquitetura e arquivos a criar
------------------------------
Proposta de layout do projeto:

```
kml/
├── main.py                # CLI / runner (executa pipeline)
├── README.md              # este arquivo (definição do projeto)
├── requirements.txt
├── pyproject.toml         # opcional (configuração packaging, lint, ferramentas)
├── kml_processor/         # pacote principal
│   ├── __init__.py
│   ├── io.py              # leitura KML, escrita CSV/GeoJSON/DXF
│   ├── model.py           # modelos de dados (PointRecord, etc.)
│   ├── elev.py            # integração com OpenTopoData (API client)
│   ├── transform.py       # conversões de lat/lon->XYZ e utilitários
│   └── cli.py             # interface de linha de comando (argparse / typer)
├── tests/
│   ├── test_io.py
│   ├── test_elev.py
│   └── test_transform.py
└── examples/
		└── sample.kml
```

Componentes principais (contratos)
---------------------------------

1) Leitor KML (`kml_processor.io`) — contrato:

- função: read_kml(path: str) -> List[PointRecord]
- PointRecord: { id: str, name: Optional[str], lat: float, lon: float, properties: dict }
- comportamento: deve lançar uma exceção clara em caso de arquivo inválido ou sem pontos

2) Cliente de elevação (`kml_processor.elev`) — contrato em relação à API OpenTopoData:

- função: get_elevations(points: List[Tuple[float, float]], provider: str = 'etopo') -> List[Optional[float]]
- Input: lista de (lat, lon) ou objetos PointRecord
- Output: lista de alturas (float em metros) ou None quando falha/local não encontrado
- Erros/limites: o cliente deve respeitar limites de taxa e expor retry/backoff configurável

OpenTopoData API — definição resumida
-----------------------------------
Endpoint típico (exemplo):

GET https://api.opentopodata.org/v1/{dataset}?locations={lat1},{lon1}|{lat2},{lon2}

Parâmetros:
- dataset: p.ex. 'srtm90m', 'etopo', ou outro dataset suportado
- locations: pares lat,lon separados por |

Resposta (exemplo):

{
	"results": [
		{"latitude": 10.0, "longitude": 20.0, "elevation": 123.4},
		...
	],
	"status": "OK"
}

Contrato de uso no código:
- O cliente deve construir chamadas em lotes (ex.: 100 pontos por chamada) para reduzir chamadas e respeitar limites.
- Em caso de falha temporária (5xx ou timeout) re-tentar com backoff exponencial (até N tentativas configuráveis).
- Em caso de erro permanente (4xx) não re-tentar e propagar erro para o pipeline.

3) Transformação (`kml_processor.transform`)

- função: to_xyz(record: PointRecord, elevation: float) -> XYZRecord
- XYZRecord: { id, name, x: float, y: float, z: float, original: PointRecord }
- Observação: por definição do projeto, X=latitude, Y=longitude, Z=elevação. (Note que essa convenção é incomum; documentar para usuários finais.)

4) Escrita DXF (`kml_processor.io`) — contrato:

- função: write_dxf(path: str, points: List[XYZRecord], layer: Optional[str] = None) -> None
- Deve preservar X/Y/Z conforme definido e incluir metadados (nome, id) nos atributos ou como texto próximo ao ponto.

Exemplo de fluxo (CLI `main.py`)
--------------------------------
python main.py --input examples/sample.kml --output out.dxf --dataset srtm90m --batch-size 100

Passos executados:
1. Ler KML
2. Extrair pontos
3. Agrupar em lotes de `batch-size` e consultar OpenTopoData para cada lote
4. Mapear pontos para XYZ
5. Escrever DXF (e CSV/GeoJSON se solicitado)

Edge cases e validações
-----------------------
- KML sem pontos — logar e abortar com código de erro
- Coordenadas inválidas (lat/lon fora do intervalo) — filtrar e reportar
- Falha parcial na API de elevação — aceitar Nones para elevação ou abortar com flag `--strict`
- Requisições grandes — suportar batching e limite de tamanho de URL (usar POST se a API suportar)

Testes e qualidade
------------------
- Escrever testes unitários para:
	- Leitura de KML com pontos e atributos
	- Cliente de elevação: mock da API e simulação de respostas OK/5xx/4xx
	- Transformações lat/lon->XYZ
	- Escrita DXF (unitário checando as entidades criadas)
- Testes de integração mínimos com um `examples/sample.kml` e um script que roda o pipeline em modo offline (mockando a API)

Checklist de implantação / CI
---------------------------
- Configurar workflow GitHub Actions para:
	- rodar lint (ruff/flake8)
	- rodar testes (pytest)
	- construir pacote (opcional)

Roadmap inicial (próximos PRs)
----------------------------
1. Implementar o leitor KML e modelos de dados (skeleton + testes unitários)
2. Implementar cliente OpenTopoData com retry e batching (com testes)
3. Implementar transformações e exportador DXF (usar `ezdxf`) (com testes)
4. CLI e documentação de uso com exemplos
5. CI e lint

Observações finais
------------------
Se desejar, eu posso:
- Gerar a estrutura de arquivos/esqueleto do pacote (`kml_processor`), com arquivos Python vazios contendo docstrings.
- Preencher `requirements.txt` com versões exatas (posso inspecionar seu ambiente atual para sugerir versões).
- Implementar o leitor KML inicial e um teste unitário e rodar pytest aqui.

Escolha qual dessas ações você quer que eu execute a seguir e eu começo: gerar esqueleto, adicionar cliente OpenTopoData, adicionar exportador DXF, ou rodar os testes/CI.

## Exemplo de uso da CLI

Execute o pipeline completo (KML → XYZ → DXF) via PowerShell:

```powershell
# Ative o ambiente virtual
.\.venv\Scripts\Activate.ps1

# Execute o pipeline
python main.py --input examples/sample.kml --output examples/out.dxf --dataset etopo --batch-size 100 --formats dxf
```

Argumentos disponíveis:
- `--input` (obrigatório): caminho do arquivo KML de entrada
- `--output` (obrigatório): caminho do arquivo de saída (ex: out.dxf)
- `--dataset`: dataset OpenTopoData (padrão: etopo)
- `--batch-size`: tamanho do lote para API de elevação (padrão: 100)
- `--strict`: aborta se houver falha de elevação
- `--formats`: formatos de saída (ex: dxf, csv, geojson)

Exemplo para múltiplos formatos:
```powershell
python main.py --input examples/sample.kml --output examples/out.dxf --formats dxf csv
```

Veja também o script de exemplo em `examples/run.ps1`.
