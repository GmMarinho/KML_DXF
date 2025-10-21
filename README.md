# Conversor KML para DXF

Este projeto converte arquivos KML (com geometrias Point, LineString e Polygon/LinearRing, incluindo latitude, longitude e elevação) em arquivos DXF 3D, utilizando uma interface gráfica simples para Windows.

## Funcionalidades
- Suporte a arquivos KML contendo:
  - Pontos (Point)
  - Linhas (LineString)
  - Polígonos (Polygon/LinearRing)
- Conversão automática de coordenadas geográficas (lat/lon) para UTM.
- Preserva a elevação (Z) de cada ponto.
- Gera entidades 3D no DXF (POINT, POLYLINE 3D).
- Interface gráfica amigável (PySimpleGUI).
- Aviso ao usuário se todas as altitudes forem zero ou muito pequenas.

## Como usar
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o script:
   ```bash
   python kml_para_dxf.py
   ```
3. Na interface, selecione o arquivo KML de entrada e o local para salvar o DXF de saída.
4. Clique em "Converter". O status será exibido na tela.

## Empacotando como .exe (opcional)
Para criar um executável Windows:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed kml_para_dxf.py
```
O executável estará em `dist/kml_para_dxf.exe`.

## Exemplo de KML suportado
```xml
<Placemark>
  <LineString>
    <coordinates>
      -43.2096,-22.9035,10 -43.2097,-22.9036,12
    </coordinates>
  </LineString>
</Placemark>
```

## Observações
- O DXF gerado utiliza o sistema de coordenadas UTM correspondente à latitude/longitude dos pontos.
- Se todas as altitudes forem zero ou muito pequenas, um aviso será exibido.
- O script suporta múltiplos Placemarks e múltiplas geometrias por arquivo.

## Bibliotecas utilizadas
- PySimpleGUI
- ezdxf
- utm
- xml.etree.ElementTree (padrão Python)

## Licença
MIT
