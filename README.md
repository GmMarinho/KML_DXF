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
  python kml_2_dxf.py
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
  pyinstaller --onefile kml_2_dxf.py
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
