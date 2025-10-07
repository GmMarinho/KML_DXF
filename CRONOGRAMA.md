# Cronograma e checklist — projeto `kml`

Este documento converte o cronograma em uma checklist acionável. Marque as subtarefas conforme for avançando.

Premissas
---------
- Windows + PowerShell; Python 3.10+ instalado.

Instruções de uso
-----------------
Abra PowerShell, vá para o diretório `kml` e ative o ambiente virtual antes de rodar qualquer comando listado abaixo.

```powershell
cd kml
.\.venv\Scripts\Activate.ps1
```

Milestone 0 — Preparação do ambiente (0.5 dia)
----------------------------------------------
- [x] Criar virtualenv e ativar
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
- [x] Atualizar pip/setuptools/wheel
   ```powershell
   python -m pip install --upgrade pip setuptools wheel
   ```
- [x] Criar/atualizar `requirements.txt` completo com todas as dependências do projeto
- [x] Instalar todas as dependências do projeto
   ```powershell
   python -m pip install -r requirements.txt
   ```
- [x] Critério de aceitação: `.venv` criado e ativável; `python --version` e `pip` atualizados; todas as dependências instaladas sem erro.

Milestone 1 — Estrutura do projeto e esqueleto (1 dia)
------------------------------------------------------
- [x] Criar diretórios e arquivos do esqueleto:
   - [x] `kml_processor/__init__.py`
   - [x] `kml_processor/io.py` (docstrings)
   - [x] `kml_processor/model.py` (dataclasses)
   - [x] `kml_processor/elev.py` (cliente da API — esqueleto)
   - [x] `kml_processor/transform.py` (funções de conversão)
   - [x] `kml_processor/cli.py` (argparse/typer stub)
   - [x] `tests/test_io.py`, `tests/test_elev.py`, `tests/test_transform.py`
- [x] Rodar pytest para garantir importação dos módulos (tests stub)
   ```powershell
   python -m pytest -q
   ```
- [x] Critério de aceitação: estrutura criada; testes stub passam ou falham com mensagens claras.

Milestone 2 — Implementar leitor KML e modelos (1.5–2 dias)
----------------------------------------------------------
- [x] Escolher biblioteca KML (`simplekml`/parsing manual) e adicionar a `requirements.txt`.
- [x] Implementar `read_kml(path: str) -> List[PointRecord]` em `kml_processor/io.py`.
- [x] Normalizar atributos: `id`, `name`, `description`, validar `lat`/`lon`.
- [x] Testes unitários com `examples/sample.kml` cobrindo:
   - [x] pontos simples
   - [x] pontos com nomes/descrições
   - [x] KML inválido (teste de erro)
- [x] Comando: instalar dependências e rodar testes
   ```powershell
   python -m pip install -r requirements.txt
   python -m pytest tests/test_io.py -q
   ```
- [x] Critério de aceitação: `read_kml` retorna lista de `PointRecord` corretos; testes passam.

Milestone 3 — Cliente OpenTopoData (2 dias)
------------------------------------------
- [x] Implementar cliente em `kml_processor/elev.py` com:
   - [x] `batch_size` configurável (ex.: 100)
   - [x] `timeout` configurável
   - [x] retry exponencial até N tentativas
- [x] Testes (mock) cobrindo:
   - [x] resposta OK
   - [x] timeout/5xx -> retry
   - [x] 4xx -> erro propagado
- [x] Comando de teste:
   ```powershell
   python -m pytest tests/test_elev.py -q
   ```
- [x] Critério de aceitação: retorno mantém a ordem; retry/backoff testados.

Milestone 4 — Transformação e exportador DXF (2 dias)
--------------------------------------------------
- [x] Implementar `to_xyz(record, elevation) -> XYZRecord` em `kml_processor/transform.py`.
- [x] Implementar `write_dxf(path, xyz_records)` em `kml_processor/io.py` usando `ezdxf`.
- [x] Incluir metadados (nome, id) como atributos ou textos próximos aos pontos.
- [x] Testes unitários que inspecionam o DXF gerado (usar `ezdxf` para verificar entidades).
- [x] Comando de teste:
   ```powershell
   python -m pytest tests/test_transform.py -q
   ```
- [x] Critério de aceitação: DXF contém pontos com X/Y/Z corretos e metadados acessíveis.

Milestone 5 — CLI, documentação e exemplos (1 dia)
-----------------------------------------------
- [x] Implementar `main.py` e `kml_processor/cli.py` com argumentos:
   - `--input`, `--output`, `--dataset`, `--batch-size`, `--strict`, `--formats` (dxf/csv/geojson)
- [x] Criar `examples/sample.kml` e scripts de exemplo (`examples/run.ps1`).
- [x] Atualizar `README.md` com exemplos de uso e flags.
- [x] Critério de aceitação: `python main.py --input examples/sample.kml --output out.dxf` executa pipeline (mock API em testes).

Milestone 6 — Testes de integração e CI (1–2 dias)
-----------------------------------------------
- [ ] Adicionar workflow CI (`.github/workflows/ci.yml`) com etapas:
   - [ ] Setup Python
   - [ ] Install dependencies
   - [ ] Lint (ruff/flake8)
   - [ ] Run pytest
- [ ] Rodar pipeline localmente e ajustar falhas.
- [ ] Critério de aceitação: workflow CI passa em PR.

Milestone 7 — Extras e entrega (opcional, 1–2 dias)
-------------------------------------------------
- [ ] Considerar extras:
   - [ ] Caching local de elevações (SQLite)
   - [ ] Suporte a formatos adicionais (GeoJSON, LAS)
   - [ ] GUI leve (streamlit)
- [ ] Critério de aceitação: funcionalidades extras implementadas e testadas.

Tempo total estimado
--------------------
- Estimativa: 8–11 dias úteis (dependendo dos KMLs e edge-cases).

Comandos úteis (PowerShell)
--------------------------
- Ativar venv:
   ```powershell
   cd kml
   .\.venv\Scripts\Activate.ps1
   ```
- Instalar dependências:
   ```powershell
   python -m pip install -r requirements.txt
   ```
- Rodar testes:
   ```powershell
   python -m pytest -q
   ```

Próximo passo imediato (escolha uma ação)
-----------------------------------------
- [ ] Gerar esqueleto do pacote `kml_processor/` (arquivos e docstrings) — ~15–30 minutos
- [ ] Implementar leitor KML mínimo + teste unitário — ~2 horas
- [ ] Implementar cliente OpenTopoData esqueleto (com testes stub) — ~2 horas
- [ ] Preencher `requirements.txt` com versões exatas do ambiente atual — ~5 minutos

Marque a ação desejada e eu começo (marcarei a tarefa correspondente como `in-progress` e farei as alterações).

