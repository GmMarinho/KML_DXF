import PySimpleGUI as sg
import xml.etree.ElementTree as ET
import ezdxf
import os
import utm

# Função para extrair coordenadas do KML
def extrair_coordenadas_kml(arquivo_kml):
    tree = ET.parse(arquivo_kml)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    pontos = []
    linhas = []
    poligonos = []
    for placemark in root.findall('.//kml:Placemark', ns):
        # Point
        for pt in placemark.findall('.//kml:Point/kml:coordinates', ns):
            for linha in pt.text.strip().split():
                partes = linha.split(',')
                if len(partes) >= 2:
                    lon, lat = float(partes[0]), float(partes[1])
                    elev = float(partes[2]) if len(partes) > 2 else 0.0
                    if abs(elev) < 0.01:
                        elev = 0.0
                    pontos.append((lon, lat, elev))
        # LineString
        for ls in placemark.findall('.//kml:LineString/kml:coordinates', ns):
            linha_coords = []
            for linha in ls.text.strip().split():
                partes = linha.split(',')
                if len(partes) >= 2:
                    lon, lat = float(partes[0]), float(partes[1])
                    elev = float(partes[2]) if len(partes) > 2 else 0.0
                    if abs(elev) < 0.01:
                        elev = 0.0
                    linha_coords.append((lon, lat, elev))
            if linha_coords:
                linhas.append(linha_coords)
        # Polygon/LinearRing
        for poly in placemark.findall('.//kml:Polygon//kml:LinearRing/kml:coordinates', ns):
            poly_coords = []
            for linha in poly.text.strip().split():
                partes = linha.split(',')
                if len(partes) >= 2:
                    lon, lat = float(partes[0]), float(partes[1])
                    elev = float(partes[2]) if len(partes) > 2 else 0.0
                    if abs(elev) < 0.01:
                        elev = 0.0
                    poly_coords.append((lon, lat, elev))
            if poly_coords:
                poligonos.append(poly_coords)
    return pontos, linhas, poligonos

# Função para criar DXF
def criar_dxf(pontos, linhas, poligonos, arquivo_saida):
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()
    altitudes = []
    # Pontos
    for lon, lat, elev in pontos:
        e, n, zone, band = utm.from_latlon(lat, lon)
        msp.add_point((e, n, elev))
        altitudes.append(abs(elev))
    # Linhas
    for linha in linhas:
        pts = []
        for lon, lat, elev in linha:
            e, n, zone, band = utm.from_latlon(lat, lon)
            pts.append((e, n, elev))
            altitudes.append(abs(elev))
        if pts:
            msp.add_polyline3d(pts, dxfattribs={'closed': False})
    # Polígonos
    for poly in poligonos:
        pts = []
        for lon, lat, elev in poly:
            e, n, zone, band = utm.from_latlon(lat, lon)
            pts.append((e, n, elev))
            altitudes.append(abs(elev))
        if pts:
            msp.add_polyline3d(pts, dxfattribs={'closed': True})
    doc.saveas(arquivo_saida)
    # Aviso se todas as altitudes forem zero ou muito pequenas
    if altitudes and all(a < 1e-3 for a in altitudes):
        return 'Aviso: Todas as altitudes são zero ou muito pequenas.'
    return None

# Interface gráfica
layout = [
    [sg.Text('Selecione o arquivo KML:')],
    [sg.Input(key='-KML-'), sg.FileBrowse(file_types=(('KML Files', '*.kml'),))],
    [sg.Text('Salvar como DXF:')],
    [sg.Input(key='-DXF-'), sg.FileSaveAs(file_types=(('DXF Files', '*.dxf'),))],
    [sg.Button('Converter'), sg.Button('Sair')],
    [sg.Text('', key='-STATUS-', size=(40,1))]
]

window = sg.Window('Conversor KML para DXF', layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Sair'):
        break
    if event == 'Converter':
        kml = values['-KML-']
        dxf = values['-DXF-']
        if not kml or not dxf:
            window['-STATUS-'].update('Selecione os arquivos.')
            continue
        try:
            pontos, linhas, poligonos = extrair_coordenadas_kml(kml)
            if not (pontos or linhas or poligonos):
                window['-STATUS-'].update('Nenhuma coordenada encontrada.')
                continue
            aviso = criar_dxf(pontos, linhas, poligonos, dxf)
            msg = f'Arquivo DXF salvo em: {dxf}'
            if aviso:
                msg += f'\n{aviso}'
            window['-STATUS-'].update(msg)
        except Exception as e:
            window['-STATUS-'].update(f'Erro: {e}')

window.close()
