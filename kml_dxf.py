
import tkinter as tk
from tkinter import filedialog, messagebox
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
    pontos_por_nome = {}
    for placemark in root.findall('.//kml:Placemark', ns):
        nome_elem = placemark.find('kml:name', ns)
        nome = nome_elem.text.strip() if nome_elem is not None and nome_elem.text else None
        # Point
        for pt in placemark.findall('.//kml:Point/kml:coordinates', ns):
            for linha in pt.text.strip().split():
                partes = linha.split(',')
                if len(partes) >= 2:
                    lon, lat = float(partes[0]), float(partes[1])
                    elev = float(partes[2]) if len(partes) > 2 else 0.0
                    if abs(elev) < 0.01:
                        elev = 0.0
                    pontos.append((lon, lat, elev, nome))
                    if nome:
                        if nome not in pontos_por_nome:
                            pontos_por_nome[nome] = []
                        pontos_por_nome[nome].append((lon, lat, elev))
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
    return pontos, linhas, poligonos, pontos_por_nome

# Função para criar DXF

def categorizar_nome(nome):
    if nome is None:
        return 'SEM_NOME'
    nome = nome.strip()
    if nome.isdigit():
        return 'NUMERO'
    elif nome.isalnum() and any(c.isalpha() for c in nome) and any(c.isdigit() for c in nome):
        return 'ALFANUM'
    elif nome.isalpha():
        return 'LETRA'
    else:
        return 'OUTRO'

def criar_dxf(pontos, linhas, poligonos, pontos_por_nome, arquivo_saida):
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()
    altitudes = []
    # Criar layers para categorias
    categorias = set()
    for lon, lat, elev, nome in pontos:
        cat = categorizar_nome(nome)
        categorias.add(cat)
    for cat in categorias:
        if cat not in doc.layers:
            doc.layers.add(cat)
    # Pontos
    for lon, lat, elev, nome in pontos:
        e, n, zone, band = utm.from_latlon(lat, lon)
        cat = categorizar_nome(nome)
        msp.add_point((e, n, elev), dxfattribs={'layer': cat})
        altitudes.append(abs(elev))
    # Linhas
    for linha in linhas:
        pts = []
        for lon, lat, elev in linha:
            e, n, zone, band = utm.from_latlon(lat, lon)
            pts.append((e, n, elev))
            altitudes.append(abs(elev))
        if pts:
            msp.add_polyline3d(pts, dxfattribs={'closed': False, 'layer': 'LINHA'})
    # Polígonos
    for poly in poligonos:
        pts = []
        for lon, lat, elev in poly:
            e, n, zone, band = utm.from_latlon(lat, lon)
            pts.append((e, n, elev))
            altitudes.append(abs(elev))
        if pts:
            msp.add_polyline3d(pts, dxfattribs={'closed': True, 'layer': 'POLIGONO'})
    # Polylines by point name (categorize by layer)
    for nome, pts_list in pontos_por_nome.items():
        if len(pts_list) > 1:
            poly_pts = []
            for lon, lat, elev in pts_list:
                e, n, zone, band = utm.from_latlon(lat, lon)
                poly_pts.append((e, n, elev))
            cat = categorizar_nome(nome)
            msp.add_polyline3d(poly_pts, dxfattribs={'closed': False, 'layer': cat})
    doc.saveas(arquivo_saida)
    # Aviso se todas as altitudes forem zero ou muito pequenas
    if altitudes and all(a < 1e-3 for a in altitudes):
        return 'Aviso: Todas as altitudes são zero ou muito pequenas.'
    return None


# Nova interface Tkinter
class KML2DXFApp:

    def __init__(self, master):
        self.master = master
        master.title('Conversor KML para DXF')
        master.geometry('600x400')

        tk.Label(master, text='Selecione o arquivo KML:').pack(anchor='w', padx=10, pady=(10,0))
        self.kml_entry = tk.Entry(master, width=60)
        self.kml_entry.pack(padx=10)
        tk.Button(master, text='Browse', command=self.browse_kml).pack(padx=10, anchor='e')

        tk.Label(master, text='Salvar como DXF:').pack(anchor='w', padx=10, pady=(10,0))
        self.dxf_entry = tk.Entry(master, width=60)
        self.dxf_entry.pack(padx=10)
        tk.Button(master, text='Salvar como...', command=self.save_dxf).pack(padx=10, anchor='e')

        self.status = tk.Label(master, text='', fg='blue')
        self.status.pack(padx=10, pady=(10,0))

        # Caixa de log
        tk.Label(master, text='Log do processo:').pack(anchor='w', padx=10, pady=(10,0))
        self.log_text = tk.Text(master, height=8, width=80, state='disabled', bg='#f0f0f0')
        self.log_text.pack(padx=10, pady=(0,10), fill='both', expand=False)

        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text='Converter', command=self.converter).pack(side='left', padx=5)
        tk.Button(btn_frame, text='Sair', command=master.quit).pack(side='left', padx=5)

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, msg + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def browse_kml(self):
        filename = filedialog.askopenfilename(filetypes=[('KML Files', '*.kml')])
        if filename:
            self.kml_entry.delete(0, tk.END)
            self.kml_entry.insert(0, filename)

    def save_dxf(self):
        filename = filedialog.asksaveasfilename(defaultextension='.dxf', filetypes=[('DXF Files', '*.dxf')])
        if filename:
            self.dxf_entry.delete(0, tk.END)
            self.dxf_entry.insert(0, filename)

    def converter(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        kml = self.kml_entry.get()
        dxf = self.dxf_entry.get()
        if not kml or not dxf:
            self.status.config(text='Selecione os arquivos.', fg='red')
            self.log('Erro: Selecione os arquivos de entrada e saída.')
            return
        try:
            self.log(f'Iniciando extração do KML: {kml}')
            pontos, linhas, poligonos, pontos_por_nome = extrair_coordenadas_kml(kml)
            self.log(f'Pontos extraídos: {len(pontos)}')
            self.log(f'Linhas extraídas: {len(linhas)}')
            self.log(f'Polígonos extraídos: {len(poligonos)}')
            self.log(f'Grupos de pontos para polilinhas: {len([k for k in pontos_por_nome if len(pontos_por_nome[k]) > 1])}')
            if not (pontos or linhas or poligonos):
                self.status.config(text='Nenhuma coordenada encontrada.', fg='red')
                self.log('Nenhuma coordenada encontrada no arquivo KML.')
                return
            self.log(f'Convertendo para DXF: {dxf}')
            aviso = criar_dxf(pontos, linhas, poligonos, pontos_por_nome, dxf)
            msg = f'Arquivo DXF salvo em: {dxf}'
            if aviso:
                msg += f'\n{aviso}'
                self.log(aviso)
            self.status.config(text=msg, fg='blue')
            self.log('Conversão concluída com sucesso.')

            # Salvar log em arquivo txt no mesmo local do DXF
            log_content = self.log_text.get(1.0, tk.END)
            log_path = os.path.splitext(dxf)[0] + '_log.txt'
            try:
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                self.log(f'Log salvo em: {log_path}')
            except Exception as e:
                self.log(f'Erro ao salvar log: {e}')
        except Exception as e:
            self.status.config(text=f'Erro: {e}', fg='red')
            self.log(f'Erro: {e}')


if __name__ == '__main__':
    root = tk.Tk()
    app = KML2DXFApp(root)
    root.mainloop()
