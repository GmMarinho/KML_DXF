# OpenTopoData API — Documentação

OpenTopoData é uma API REST para consulta de elevação. Você pode usar a API pública gratuita ou hospedar seu próprio servidor.

---

## Introdução

- Compatível com Google Maps Elevation API.
- Suporta diversos formatos raster e esquemas de tiles.
- Pode ser auto-hospedada via Docker.

### Exemplo de uso rápido
```bash
curl https://api.opentopodata.org/v1/test-dataset?locations=56,123
```
Resposta:
```json
{
    "results": [{
        "elevation": 815.0,
        "location": {"lat": 56.0, "lng": 123.0},
        "dataset": "test-dataset"
    }],
    "status": "OK"
}
```

---

## Como hospedar

```bash
git clone https://github.com/ajnisbet/opentopodata.git
cd opentopodata
make build
make run
```
O servidor ficará disponível em http://localhost:5000/.

---

## API Pública

- Host: https://api.opentopodata.org
- Limites:
  - Máx. 100 localizações por requisição
  - Máx. 1 chamada por segundo
  - Máx. 1000 chamadas por dia

### Datasets disponíveis (exemplo)
| Nome        | Resolução | Extensão         | Fonte   | Exemplo (Denver, CO) |
|-------------|-----------|------------------|---------|----------------------|
| nzdem8m     | 8 m       | Nova Zelândia    | LINZ    | Fora dos limites     |
| ned10m      | ~10 m     | EUA, Havaí, AK   | USGS    | 1590 m               |
| eudem25m    | 25 m      | Europa           | EEA     | Fora dos limites     |
| mapzen      | ~30 m     | Global           | Mapzen  | 1590 m               |
| aster30m    | ~30 m     | Global           | NASA    | 1591 m               |
| srtm30m     | ~30 m     | -60 a 60 lat     | USGS    | 1604 m               |
| srtm90m     | ~90 m     | -60 a 60 lat     | USGS    | 1603 m               |
| bkg200m     | 200 m     | Alemanha         | BKG     | Fora dos limites     |
| etopo1      | ~1.8 km   | Global           | NOAA    | 1596 m               |
| gebco2020   | ~450 m    | Global           | GEBCO   | 1603 m               |
| emod2018    | ~100 m    | Europa (mar)     | EMODnet | Fora dos limites     |

---

## Endpoints principais

### GET /v1/<dataset_name>
Consulta elevação para um ou mais pontos em um dataset.

- **dataset_name**: nome do dataset (ex: srtm90m, etopo, etc)
- **locations** (obrigatório): pares latitude,longitude separados por pipe `|` (ex: `locations=12.5,160.2|-10.6,130`)
- **samples**: (opcional) número de amostras igualmente espaçadas ao longo do caminho
- **interpolation**: `nearest`, `bilinear`, `cubic` (padrão: bilinear)
- **nodata_value**: valor para NODATA (`null`, `nan`, ou inteiro, padrão: null)
- **format**: `json` (padrão) ou `geojson`

#### Exemplo de requisição
```http
GET /v1/srtm90m?locations=-43.5,172.5|27.6,1.98&interpolation=cubic
```

#### Exemplo de resposta (JSON)
```json
{
  "results": [
    {"dataset": "srtm90m", "elevation": 45, "location": {"lat": -43.5, "lng": 172.5}},
    {"dataset": "srtm90m", "elevation": 402, "location": {"lat": 27.6, "lng": 1.98}}
  ],
  "status": "OK"
}
```

#### Exemplo de resposta (GeoJSON)
```http
GET /v1/srtm90m?locations=-43.5,172.5|27.6,1.98&interpolation=cubic&format=geojson
```
```json
{
  "features": [
    {"geometry": {"coordinates": [172.5, -43.5, 45], "type": "Point"}, "properties": {"dataset": "srtm90m"}, "type": "Feature"},
    {"geometry": {"coordinates": [1.98, 27.6, 402], "type": "Point"}, "properties": {"dataset": "srtm90m"}, "type": "Feature"}
  ],
  "type": "FeatureCollection"
}
```

### POST /v1/<dataset_name>
Permite enviar muitos pontos sem limite de URL. Os argumentos são os mesmos do GET, mas enviados como JSON ou form-data.

#### Exemplo (Python requests)
```python
import requests
url = "https://api.opentopodata.org/v1/srtm90m"
data = {"locations": "-43.5,172.5|27.6,1.98", "interpolation": "cubic"}
response = requests.post(url, json=data)
```

### GET /health
Endpoint de healthcheck.
- Resposta: `{ "status": "OK" }` (200 se saudável, 500 se não)

### GET /datasets
Lista os datasets disponíveis no servidor.
- Resposta:
```json
{
  "results": [
    {"name": "test-dataset", "child_datasets": []}
  ],
  "status": "OK"
}
```

---

## Parâmetros detalhados
- **locations**: pares lat,lon separados por `|` ou polyline Google
- **samples**: número de amostras ao longo do caminho
- **interpolation**: `nearest`, `bilinear`, `cubic`
- **nodata_value**: valor para NODATA (`null`, `nan`, ou inteiro)
- **format**: `json` ou `geojson`

## Resposta
- **status**: `OK`, `INVALID_REQUEST` (4xx), `SERVER_ERROR` (5xx)
- **results**: lista de elevações (ou features, se geojson)
- **results[].elevation**: elevação (null se fora do dataset)
- **results[].location.lat/lng**: coordenadas retornadas
- **results[].dataset**: dataset usado

## Notas
- Se o raster for inteiro, a elevação é arredondada.
- Se a localização não for coberta, elevation será null.
- O parâmetro `nodata_value` só afeta o último dataset em multi-dataset.
- Para muitos pontos, prefira POST ou polyline encoding.

---

## Suporte
Dúvidas? Email: andrew@opentopodata.org

## Serviço pago (GPXZ)
- API com dados LIDAR de alta resolução (1m)
- Hospedagem gerenciada, redundância, suporte prioritário
- Endpoint compatível com Google Maps Elevation API
- Sem limites rígidos de uso
- Servidores na UE se necessário
- CORS habilitado para uso em frontend
- Contato: andrew@opentopodata.org

O serviço pago financia o desenvolvimento do OpenTopoData e mantém a API pública gratuita.