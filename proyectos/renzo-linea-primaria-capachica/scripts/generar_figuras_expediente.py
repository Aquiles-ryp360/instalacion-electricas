# -*- coding: utf-8 -*-
"""
generar_figuras_expediente.py
Genera figuras técnicas y mapas con imágenes satelitales reales (Esri/ArcGIS)
para ser insertadas en el Expediente Técnico en LaTeX.
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

def utm_to_latlon(easting, northing):
    a = 6378137.0
    f = 1 / 298.257223563
    b = a * (1 - f)
    e2 = (a**2 - b**2) / (a**2)
    e_prime2 = (a**2 - b**2) / (b**2)
    k0 = 0.9996
    lon0 = -69.0
    x = easting - 500000.0
    y = northing - 10000000.0
    M = y / k0
    mu = M / (a * (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    phi1 = mu + (3*e1/2 - 27*e1**3/32)*math.sin(2*mu) + (21*e1**2/16 - 55*e1**4/32)*math.sin(4*mu) + (151*e1**3/96)*math.sin(6*mu)
    N1 = a / math.sqrt(1 - e2 * math.sin(phi1)**2)
    T1 = math.tan(phi1)**2
    C1 = e_prime2 * math.cos(phi1)**2
    R1 = a * (1 - e2) / ((1 - e2 * math.sin(phi1)**2)**1.5)
    D = x / (N1 * k0)
    lat = phi1 - (N1 * math.tan(phi1) / R1) * (D**2/2 - (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*e_prime2)*D**4/24 + (61 + 90*T1 + 298*C1 + 45*T1**2 - 252*e_prime2 - 3*C1**2)*D**6/720)
    lon = math.radians(lon0) + (D - (1 + 2*T1 + C1)*D**3/6 + (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*e_prime2 + 24*T1**2)*D**5/120) / math.cos(phi1)
    return math.degrees(lat), math.degrees(lon)

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
        ("CHIFRÓN (Área Proyecto)", -69.8144, -15.6360, 'red', '^'),
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
    
    # Postes MT
    postes = [
        ("E-01", 412606.01, 8270712.24, "Derivación MT"),
        ("E-02", 412658.20, 8270802.10, "Suspensión"),
        ("E-03", 412710.40, 8270891.90, "Suspensión"),
        ("E-04", 412759.20, 8270976.22, "SED 100 kVA"),
        ("E-05", 412750.60, 8271073.06, "Ángulo"),
        ("E-06", 412688.54, 8271218.86, "Ángulo"),
        ("E-07", 412656.92, 8271306.91, "Suspensión"),
        ("E-08", 412660.46, 8271391.24, "Ángulo"),
        ("E-09", 412659.90, 8271446.51, "Terminal MT")
    ]
    postes_geo = []
    for pid, e, n, f in postes:
        lat, lon = utm_to_latlon(e, n)
        postes_geo.append((pid, lon, lat, f))
        
    # Cargar abonados
    csv_path = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\datos\cargas\censo_43_abonados.csv"
    abonados = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            abonados.append((r['codigo_abonado'], float(r['lon_centroide']), float(r['lat_centroide'])))
            
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    extent = [-69.825, -69.805, -15.645, -15.630]
    ax.imshow(img, extent=extent, aspect='auto')
    
    # Dibujar traza de Línea Primaria MT
    lons_mt = [p[1] for p in postes_geo]
    lats_mt = [p[2] for p in postes_geo]
    ax.plot(lons_mt, lats_mt, color='cyan', linewidth=2.5, label='Línea Primaria 22.9 kV (AAAC 35 mm²)', zorder=3)
    
    # Dibujar Postes MT
    for pid, lon, lat, func in postes_geo:
        col = 'yellow' if pid != 'E-04' else 'magenta'
        mk = 'o' if pid != 'E-04' else 's'
        ms = 7 if pid != 'E-04' else 10
        ax.plot(lon, lat, marker=mk, color=col, markersize=ms, markeredgecolor='black', markeredgewidth=1.2, zorder=5)
        ax.text(lon + 0.0003, lat + 0.0002, f"{pid}", color=col, fontsize=7.5, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.15", fc="black", ec=col, alpha=0.7), zorder=6)
                
    # Dibujar Viviendas Censadas
    lons_ab = [a[1] for a in abonados]
    lats_ab = [a[2] for a in abonados]
    ax.scatter(lons_ab, lats_ab, color='red', s=16, edgecolors='white', linewidths=0.5, label='43 Viviendas Censadas (C1 a C43)', zorder=4)
    
    # Rótulo de la SED E-04
    e04 = postes_geo[3]
    ax.annotate("SED BIPOSTE 100 kVA\n(E-04 / SAB-1)", xy=(e04[1], e04[2]), xytext=(e04[1] + 0.003, e04[2] + 0.0015),
                arrowprops=dict(facecolor='magenta', shrink=0.08, width=1.5, headwidth=6),
                bbox=dict(boxstyle="square,pad=0.3", fc="black", ec="magenta", alpha=0.85),
                fontsize=8, fontweight='bold', color='magenta', zorder=7)

    # Rótulo Punto de Derivación E-01
    e01 = postes_geo[0]
    ax.annotate("DERIVACIÓN ELECTRO PUNO\n(E-01 / TMT000012389)", xy=(e01[1], e01[2]), xytext=(e01[1] - 0.0065, e01[2] - 0.002),
                arrowprops=dict(facecolor='yellow', shrink=0.08, width=1.5, headwidth=6),
                bbox=dict(boxstyle="square,pad=0.3", fc="black", ec="yellow", alpha=0.85),
                fontsize=8, fontweight='bold', color='yellow', zorder=7)

    # Zoom a la zona del proyecto
    ax.set_xlim(-69.822, -69.810)
    ax.set_ylim(-15.642, -15.632)
    
    ax.set_title("VISTA SATELITAL REAL Y TRAZADO ELECTROMECÁNICO — SECTOR CHIFRÓN\nOrtomosaico Satelital Esri World Imagery (Resolución Submétrica)", fontsize=10.5, fontweight='bold', color='navy')
    ax.set_xlabel("Longitud Oeste (WGS-84)", fontsize=8.5)
    ax.set_ylabel("Latitud Sur (WGS-84)", fontsize=8.5)
    ax.legend(loc='lower left', fontsize=8, facecolor='black', edgecolor='white', labelcolor='white')
    ax.grid(True, linestyle='--', alpha=0.35, color='white')
    
    out_file = os.path.join(out_dir, "fig_traza_satelital_chifron.png")
    fig.tight_layout()
    fig.savefig(out_file, dpi=300)
    plt.close(fig)
    print("Mapa satelital Chifrón generado:", out_file)

def generar_grafico_cargas(out_dir):
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    circuitos = ['Circuito C-1\n(Sector Sur)', 'Circuito C-2\n(Sector Centro)', 'Circuito C-3\n(Sector Norte)']
    pot_part = [34.20, 18.00, 18.00]
    pot_ap = [0.42, 0.24, 0.24]
    
    bars1 = ax.bar(circuitos, pot_part, label='Servicio Particular (kW)', color='#1E3A8A', width=0.45)
    bars2 = ax.bar(circuitos, pot_ap, bottom=pot_part, label='Alumbrado Público (kW)', color='#D97706', width=0.45)
    
    ax.axhline(y=71.10, color='red', linestyle='--', linewidth=1.5, label='Demanda Máxima Total = 71.10 kW')
    ax.axhline(y=100.0, color='green', linestyle=':', linewidth=1.5, label='Capacidad Trafo SED = 100 kVA')
    
    for b1, b2 in zip(bars1, bars2):
        tot = b1.get_height() + b2.get_height()
        ax.text(b1.get_x() + b1.get_width()/2., tot + 1.2, f"{tot:.2f} kW", ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    ax.set_ylabel("Potencia Activa Demandada (kW)", fontsize=9, fontweight='bold')
    ax.set_title("DISTRIBUCIÓN DE MÁXIMA DEMANDA POR CIRCUITOS DE DISTRIBUCIÓN\nMetodología Oficial FIME UNA Puno (Horizonte 20 años, TC=3%, cos φ=0.9)", fontsize=10, fontweight='bold', color='navy')
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
