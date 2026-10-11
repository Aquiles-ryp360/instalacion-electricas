# -*- coding: utf-8 -*-
"""
generar_figuras_expediente.py
Genera figuras técnicas y mapas con imágenes satelitales reales (Esri/ArcGIS)
para ser insertadas en el Expediente Técnico en LaTeX.
Ubicación del Transformador fijada por usuario: Lat: -15.640067, Lon: -69.815400
Distribución hacia Rutas Eléctricas 1, 2, 3, 4.
"""

import os
import math
import csv
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

def latlon_to_utm(lat, lon):
    a = 6378137.0
    f = 1 / 298.257223563
    b = a * (1 - f)
    e2 = (a**2 - b**2) / (a**2)
    e_prime2 = (a**2 - b**2) / (b**2)
    k0 = 0.9996
    lon0 = -69.0
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    lon0_rad = math.radians(lon0)
    N = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2)
    T = math.tan(lat_rad)**2
    C = e_prime2 * math.cos(lat_rad)**2
    A = (lon_rad - lon0_rad) * math.cos(lat_rad)
    M = a * ((1 - e2/4 - 3*e2**2/64 - 5*e2**3/256)*lat_rad
            - (3*e2/8 + 3*e2**2/32 + 45*e2**3/1024)*math.sin(2*lat_rad)
            + (15*e2**2/256 + 45*e2**3/1024)*math.sin(4*lat_rad)
            - (35*e2**3/3072)*math.sin(6*lat_rad))
    easting = k0 * N * (A + (1 - T + C)*A**3/6 + (5 - 18*T + T**2 + 72*C - 58*e_prime2)*A**5/120) + 500000.0
    northing = k0 * (M + N*math.tan(lat_rad)*(A**2/2 + (5 - T + 9*C + 4*C**2)*A**4/24 + (61 - 58*T + T**2 + 600*C - 330*e_prime2)*A**6/720)) + 10000000.0
    return easting, northing

def cargar_rutas_kml(kml_path):
    tree = ET.parse(kml_path)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    rutas = {}
    for pm in root.findall('.//kml:Placemark', ns):
        name = pm.find('kml:name', ns)
        name_str = name.text.strip() if name is not None and name.text else ''
        ls = pm.find('.//kml:LineString', ns)
        if ls is not None:
            coords = ls.find('kml:coordinates', ns).text.strip().split()
            pts = []
            for c in coords:
                parts = c.split(',')
                pts.append((float(parts[0]), float(parts[1])))
            rutas[name_str] = pts
    return rutas

def generar_mapa_macro(out_dir):
    img_path = os.path.join(out_dir, "satelite_macro_capachica.jpg")
    if not os.path.exists(img_path):
        return
    img = Image.open(img_path)
    
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)
    extent = [-70.20, -69.60, -15.85, -15.45]
    ax.imshow(img, extent=extent, aspect='auto')
    
    # Puntos de referencia
    puntos = [
        ("PUNO (Capital Dep.)", -70.0219, -15.8422, 'yellow', 's'),
        ("CAPACHICA (Capital Dist.)", -69.8322, -15.6425, 'cyan', 'o'),
        ("CHIFRÓN (SED 100 kVA)", -69.8154, -15.6401, 'red', '^'),
        ("LAGO TITICACA", -69.7200, -15.7000, 'white', None),
        ("ISLA TAQUILE", -69.6840, -15.7760, 'lightgreen', 'o'),
        ("ISLA AMANTANÍ", -69.7100, -15.6640, 'lightgreen', 'o')
    ]
    for nom, lon, lat, col, mk in puntos:
        if mk:
            ax.plot(lon, lat, marker=mk, color=col, markersize=8, markeredgecolor='black', markeredgewidth=1.2)
        ax.text(lon + 0.008, lat + 0.005, nom, color=col, fontsize=9, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.2", fc="black", ec=col, alpha=0.7))
        
    ax.set_title("MAPA REGIONAL DE UBICACIÓN — PENÍNSULA DE CAPACHICA (PUNO)\nFuente: Esri World Imagery / Maxar Technologies (Satelital Real)", fontsize=11, fontweight='bold', color='navy')
    ax.set_xlabel("Longitud Oeste (WGS-84)", fontsize=9)
    ax.set_ylabel("Latitud Sur (WGS-84)", fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.4, color='white')
    
    out_file = os.path.join(out_dir, "fig_ubicacion_macro.png")
    fig.tight_layout()
    fig.savefig(out_file, dpi=300)
    plt.close(fig)
    print("Mapa macro generado:", out_file)

def generar_mapa_chifron_satelital(out_dir):
    img_path = os.path.join(out_dir, "satelite_chifron_real.jpg")
    if not os.path.exists(img_path):
        return
    img = Image.open(img_path)
    
    # Cargar rutas KML
    kml_path = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\fuentes\kml\topografia_capachica_chifron.kml"
    rutas = cargar_rutas_kml(kml_path)
    
    # Cargar abonados
    csv_path = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\datos\cargas\censo_43_abonados.csv"
    abonados = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            abonados.append((r['codigo_abonado'], float(r['lon_centroide']), float(r['lat_centroide'])))
            
    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=300)
    extent = [-69.825, -69.805, -15.645, -15.630]
    ax.imshow(img, extent=extent, aspect='auto')
    
    # Coordenadas exactas del Transformador (SED) indicadas por el usuario
    lon_sed = -69.815400
    lat_sed = -15.640067

    # Línea Primaria de Alimentación en Media Tensión 22.9 kV llegando a la SED
    # (Procedente del alimentador de Electro Puno por la vía de acceso suroeste)
    lon_mt_inicio = -69.817659
    lat_mt_inicio = -15.639793
    ax.plot([lon_mt_inicio, lon_sed], [lat_mt_inicio, lat_sed], color='yellow', linewidth=3.0, linestyle='--',
            label='Línea Primaria MT 22.9 kV (Llegada a SED)', zorder=4)
    
    # Rutas Eléctricas en Baja Tensión partiendo desde la SED:
    # 1. Ruta Eléctrica 1 (Circuito C-1 Troncal Norte hacia C1 a C30)
    if 'ruta electrica 1' in rutas:
        pts = rutas['ruta electrica 1']
        lons = [p[0] for p in pts]
        lats = [p[1] for p in pts]
        ax.plot(lons, lats, color='cyan', linewidth=2.8, label='Circuito C-1 BT (Ruta 1 Troncal Norte: 819.7 m)', zorder=3)
        # Postes intermedios representativos a lo largo de la ruta 1
        ax.plot(lons[::2], lats[::2], 'o', color='cyan', markersize=4, zorder=5)

    # 2. Ruta Eléctrica 3 (Circuito C-2 Sector Centro hacia C31, C33-C37)
    if 'ruta electrica 3' in rutas:
        pts3 = rutas['ruta electrica 3']
        lons3 = [lon_sed] + [p[0] for p in pts3]
        lats3 = [lat_sed] + [p[1] for p in pts3]
        ax.plot(lons3, lats3, color='#F97316', linewidth=2.4, label='Circuito C-2 BT (Ruta 3 Sector Centro: 184.4 m)', zorder=3)
        ax.plot(lons3, lats3, 'o', color='#F97316', markersize=4, zorder=5)

    # 3. Ruta Eléctrica 4 & 2 (Circuito C-3 Sector Sur hacia C32, C43, C38-C42)
    if 'ruta electrica 4' in rutas:
        pts4 = rutas['ruta electrica 4']
        lons4 = [lon_sed] + [p[0] for p in pts4]
        lats4 = [lat_sed] + [p[1] for p in pts4]
        ax.plot(lons4, lats4, color='#A855F7', linewidth=2.4, label='Circuito C-3 BT (Rutas 4 y 2 Sector Sur: 284.8 m)', zorder=3)
        ax.plot(lons4, lats4, 'o', color='#A855F7', markersize=4, zorder=5)
        
    if 'ruta electrica 2' in rutas:
        pts2 = rutas['ruta electrica 2']
        lons2 = [p[0] for p in pts2]
        lats2 = [p[1] for p in pts2]
        ax.plot(lons2, lats2, color='#A855F7', linewidth=2.4, linestyle=':', zorder=3)

    # Dibujar las 43 Viviendas Censadas
    lons_ab = [a[1] for a in abonados]
    lats_ab = [a[2] for a in abonados]
    ax.scatter(lons_ab, lats_ab, color='red', s=22, edgecolors='white', linewidths=0.7, label='43 Viviendas Censadas (C1 a C43)', zorder=6)

    # DIBUJAR EL TRANSFORMADOR / SED BIPOSTE 100 kVA (UBICACIÓN EXACTA DEL USUARIO)
    ax.plot(lon_sed, lat_sed, marker='s', color='#EC4899', markersize=12, markeredgecolor='white', markeredgewidth=1.8, zorder=8)
    ax.annotate("TRANSFORMADOR PROYECTADO 100 kVA\nSED BIPOSTE (Armado SAB-1)\nLat: -15.640067°  Lon: -69.815400°\n(Origen de Circuitos BT 1, 2 y 3)",
                xy=(lon_sed, lat_sed), xytext=(lon_sed - 0.0068, lat_sed + 0.0018),
                arrowprops=dict(facecolor='#EC4899', shrink=0.08, width=2.0, headwidth=8),
                bbox=dict(boxstyle="round,pad=0.4", fc="black", ec="#EC4899", alpha=0.9),
                fontsize=8.5, fontweight='bold', color='white', zorder=9)

    # Límites del encuadre
    ax.set_xlim(-69.822, -69.810)
    ax.set_ylim(-15.642, -15.632)
    
    ax.set_title("VISTA SATELITAL REAL Y TRAZADO ELECTROMECÁNICO DEFINITIVO — SECTOR CHIFRÓN\nUbicación de SED 100 kVA en Lat: -15.640067, Lon: -69.815400 y Redes de BT (Rutas 1, 2, 3)",
                 fontsize=10.5, fontweight='bold', color='navy')
    ax.set_xlabel("Longitud Oeste (WGS-84)", fontsize=8.5)
    ax.set_ylabel("Latitud Sur (WGS-84)", fontsize=8.5)
    ax.legend(loc='lower left', fontsize=7.5, facecolor='black', edgecolor='white', labelcolor='white')
    ax.grid(True, linestyle='--', alpha=0.35, color='white')
    
    out_file = os.path.join(out_dir, "fig_traza_satelital_chifron.png")
    fig.tight_layout()
    fig.savefig(out_file, dpi=300)
    plt.close(fig)
    print("Mapa satelital Chifrón generado:", out_file)

def generar_grafico_cargas(out_dir):
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    circuitos = ['Circuito C-1 (Ruta 1)\n(Troncal Norte: 38 hab)', 'Circuito C-2 (Ruta 3)\n(Sector Centro: 20 hab)', 'Circuito C-3 (Rutas 4 y 2)\n(Sector Sur: 20 hab)']
    pot_part = [34.20, 18.00, 18.00]
    pot_ap = [0.42, 0.24, 0.24]
    
    bars1 = ax.bar(circuitos, pot_part, label='Servicio Particular (kW)', color='#1E3A8A', width=0.45)
    bars2 = ax.bar(circuitos, pot_ap, bottom=pot_part, label='Alumbrado Público (kW)', color='#D97706', width=0.45)
    
    ax.axhline(y=71.10, color='red', linestyle='--', linewidth=1.5, label='Demanda Máxima Total = 71.10 kW (79.00 kVA)')
    ax.axhline(y=100.0, color='green', linestyle=':', linewidth=1.5, label='Capacidad SED en Origen = 100 kVA (Reserva 21%)')
    
    for b1, b2 in zip(bars1, bars2):
        tot = b1.get_height() + b2.get_height()
        ax.text(b1.get_x() + b1.get_width()/2., tot + 1.2, f"{tot:.2f} kW", ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    ax.set_ylabel("Potencia Activa Demandada (kW)", fontsize=9, fontweight='bold')
    ax.set_title("DISTRIBUCIÓN DE MÁXIMA DEMANDA POR CIRCUITOS DESDE EL TRANSFORMADOR\nSED Biposte 100 kVA (Lat: -15.640067, Lon: -69.815400)", fontsize=10, fontweight='bold', color='navy')
    ax.set_ylim(0, 115)
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    out_file = os.path.join(out_dir, "fig_diagrama_cargas_circuitos.png")
    fig.tight_layout()
    fig.savefig(out_file, dpi=300)
    plt.close(fig)
    print("Gráfico de cargas generado:", out_file)

if __name__ == "__main__":
    out_dir = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\entregables\imagenes"
    os.makedirs(out_dir, exist_ok=True)
    generar_mapa_macro(out_dir)
    generar_mapa_chifron_satelital(out_dir)
    generar_grafico_cargas(out_dir)
