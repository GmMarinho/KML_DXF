
# KML_DXF

Conversor de arquivos KML para DXF com interface gráfica (Tkinter).

## Funcionalidades
- Seleção de arquivo KML e destino DXF via interface
- Conversão de pontos, linhas e polígonos do KML para DXF
- Pontos e polilinhas categorizados em layers conforme o nome (NUMERO, ALFANUM, LETRA, OUTRO)
- Log detalhado do processo salvo em arquivo TXT junto ao DXF
- Compatível com Windows

## Como usar
1. Instale as dependências:
  ```bash
  pip install -r requirements.txt
  ```
2. Execute o programa:
  ```bash
  python kml_dxf.py
  ```
3. Selecione o arquivo KML e o destino do DXF na interface.
4. Clique em "Converter". O DXF e o log serão salvos no local escolhido.

## Como gerar o executável (.exe)
1. Instale o PyInstaller:
  ```bash
  pip install pyinstaller
  ```
2. Gere o executável:
  ```bash
  pyinstaller --onefile kml_dxf.py
  ```

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

### Exemplo de KML com ponto
```xml
<Placemark>
  <name>Ponto1</name>
  <Point>
    <coordinates>-35.20989232587857,-5.839852418981317,10</coordinates>
  </Point>
</Placemark>
```

### Exemplo de KML com polígono
```xml
<Placemark>
  <name>Poligono1</name>
  <Polygon>
    <outerBoundaryIs>
      <LinearRing>
        <coordinates>
          -43.2096,-22.9035,10 -43.2097,-22.9036,12 -43.2098,-22.9037,15 -43.2096,-22.9035,10
        </coordinates>
      </LinearRing>
    </outerBoundaryIs>
  </Polygon>
</Placemark>
```

## Exemplo de uso
1. Abra o programa com `python kml_dxf.py`
2. Selecione um arquivo KML de entrada e o destino do DXF
3. Clique em "Converter"
4. O log do processo será exibido na interface e salvo junto ao DXF


## Observações
- O DXF gerado utiliza o sistema de coordenadas UTM correspondente à latitude/longitude dos pontos.
- Se todas as altitudes forem zero ou muito pequenas, um aviso será exibido.
- O script suporta múltiplos Placemarks e múltiplas geometrias por arquivo.

## Dependências
- ezdxf
- utm
- Tkinter (nativo do Python)

## Licença
MIT

## Autor
[GmMarinho](https://github.com/GmMarinho)

## API para verficação
https://developers.google.com/maps/documentation/earth?hl=pt-BR
