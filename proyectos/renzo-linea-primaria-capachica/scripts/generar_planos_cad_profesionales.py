# -*- coding: utf-8 -*-
"""
generar_planos_cad_profesionales.py
Genera las láminas oficiales de ingeniería electromecánica en formato A3 Horizontal (420 x 297 mm)
con estética y simbología 100% normalizada AutoCAD / DGE-MEM / Electro Puno S.A.A.

Ajustes del proyecto:
1. ELIMINACIÓN DEL CIRCUITO 3: Ahora existen únicamente 2 CIRCUITOS DE BAJA TENSIÓN:
   - Circuito C-1: Troncal Norte hacia la Playa de Chifrón (Ruta 1 - 819.7 m, 24 viviendas censadas / 44 proyectadas).
   - Circuito C-2: Ramal Centro y Sur (Rutas 3, 4 y 2 - 469.2 m, 19 viviendas censadas / 34 proyectadas).
2. Simbología y bloques normalizados CAD oficiales:
   - Postes C.A.C. con bloque normalizado DGE (círculo con cuadrantes opuestos achurados).
   - Subestación Biposte SAB-1 (100 kVA, 22.9/0.38-0.22 kV) en Lat: -15.640067, Lon: -69.815400.
   - Retenidas R-1 con cable de acero y muerto de concreto armado normalizado.
   - Puestas a tierra PAT-1 y PAT-3 (3 trazos paralelos decrecientes).
   - Acometidas monofásicas concéntricas aéreas y caja portamedidor (M).
   - Diagrama unifilar oficial en formato CAD según normas IEEE/IEC/CNE.
   - Membrete formal de ingeniería UNA Puno - FIME.

Autor: Renzo Gabriel Mamani Galindo (Cód. 228447)
Curso: MEC330 - Instalaciones Eléctricas II | FIME - UNA Puno
"""

import os
import math
import csv
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Wedge, Rectangle, Polygon
from matplotlib.lines import Line2D

# -------------------------------------------------------------------------
# CONVERSIÓN DE COORDENADAS WGS-84 A UTM ZONA 19S
# -------------------------------------------------------------------------
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
    vias = []
    for pm in root.findall('.//kml:Placemark', ns):
        name = pm.find('kml:name', ns)
        name_str = name.text.strip() if name is not None and name.text else ''
        ls = pm.find('.//kml:LineString', ns)
        if ls is not None:
            coords = ls.find('kml:coordinates', ns).text.strip().split()
            pts = []
            for c in coords:
                parts = c.split(',')
                lon, lat = float(parts[0]), float(parts[1])
                e, n = latlon_to_utm(lat, lon)
                pts.append((e, n))
            if 'ruta electrica' in name_str:
                rutas[name_str] = pts
            elif 'carretera' in name_str:
                vias.append((name_str, pts))
    return rutas, vias

def cargar_abonados_csv(csv_path):
    abonados = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            lat = float(r['lat_centroide'])
            lon = float(r['lon_centroide'])
            e, n = latlon_to_utm(lat, lon)
            abonados.append({"cod": r['codigo_abonado'], "este": e, "norte": n, "lat": lat, "lon": lon})
    return abonados

# -------------------------------------------------------------------------
# BLOQUES GRÁFICOS CAD NORMALIZADOS
# -------------------------------------------------------------------------
def dibujar_bloque_poste_cad(ax, x, y, radio=1.4, etiqueta=""):
    """Dibuja un poste de concreto con simbología CAD normalizada DGE (círculo con cuadrantes)."""
    # Círculo base
    c = patches.Circle((x, y), radius=radio, facecolor='white', edgecolor='black', linewidth=0.8, zorder=10)
    ax.add_patch(c)
    # Cuadrantes achurados en diagonal
    w1 = Wedge((x, y), radio, 0, 90, facecolor='black', edgecolor='none', zorder=11)
    w2 = Wedge((x, y), radio, 180, 270, facecolor='black', edgecolor='none', zorder=11)
    ax.add_patch(w1)
    ax.add_patch(w2)
    if etiqueta:
        ax.text(x + radio + 0.8, y + radio + 0.5, etiqueta, fontsize=5.5, fontweight='bold', color='#111827', zorder=15)

def dibujar_bloque_sed_cad(ax, x, y):
    """Dibuja la Subestación Biposte SAB-1 en planta con simbología normalizada Electro Puno."""
    # Dos postes C.A.C. 13/400 separados 2.4 m
    dx = 1.4
    for px in [x - dx, x + dx]:
        c = patches.Circle((px, y), radius=1.6, facecolor='white', edgecolor='#B91C1C', linewidth=1.2, zorder=20)
        ax.add_patch(c)
        w1 = Wedge((px, y), 1.6, 0, 90, facecolor='#B91C1C', edgecolor='none', zorder=21)
        w2 = Wedge((px, y), 1.6, 180, 270, facecolor='#B91C1C', edgecolor='none', zorder=21)
        ax.add_patch(w1)
        ax.add_patch(w2)
    # Plataforma metálica de soporte
    rect_plat = patches.Rectangle((x - 2.8, y - 0.7), 5.6, 1.4, facecolor='#FEE2E2', edgecolor='#B91C1C', linewidth=1.0, zorder=19)
    ax.add_patch(rect_plat)
    # Cuba del transformador 100 kVA
    rect_trafo = patches.Rectangle((x - 1.2, y - 1.2), 2.4, 2.4, facecolor='#FEF3C7', edgecolor='#B45309', linewidth=1.2, zorder=22)
    ax.add_patch(rect_trafo)
    ax.text(x, y, "100\nkVA", ha='center', va='center', fontsize=5.0, fontweight='bold', color='#78350F', zorder=23)

def dibujar_bloque_pat_cad(ax, x, y, dx=0, dy=-3.5, label="PAT-1"):
    """Dibuja el símbolo normalizado DGE de puesta a tierra con tres barras decrecientes."""
    x_end, y_end = x + dx, y + dy
    # Conductor vertical de enlace
    ax.plot([x, x_end], [y, y_end], color='#15803D', linewidth=1.0, zorder=12)
    # Tres barras horizontales de tierra
    ax.plot([x_end - 2.2, x_end + 2.2], [y_end, y_end], color='#15803D', linewidth=1.5, zorder=13)
    ax.plot([x_end - 1.4, x_end + 1.4], [y_end - 0.9, y_end - 0.9], color='#15803D', linewidth=1.5, zorder=13)
    ax.plot([x_end - 0.6, x_end + 0.6], [y_end - 1.8, y_end - 1.8], color='#15803D', linewidth=1.5, zorder=13)
    ax.text(x_end + 2.6, y_end - 0.9, label, fontsize=4.8, fontweight='bold', color='#15803D', va='center', zorder=14)

def dibujar_bloque_retenida_cad(ax, x, y, dx=-6.0, dy=-6.0, tipo="RET-I"):
    """Dibuja la flecha de retenida con cable de acero y muerto de concreto normalizado."""
    x_ancla, y_ancla = x + dx, y + dy
    # Cable de retenida
    ax.plot([x, x_ancla], [y, y_ancla], color='#C2410C', linewidth=1.2, zorder=12)
    # Aislador de porcelana 54-1
    xm = (x + x_ancla) / 2.0
    ym = (y + y_ancla) / 2.0
    ax.plot(xm, ym, marker='s', color='#D97706', markersize=3.5, zorder=13)
    # Bloque de anclaje perpendicular al cable
    ang = math.atan2(dy, dx) + math.pi / 2.0
    bx = 2.2 * math.cos(ang)
    by = 2.2 * math.sin(ang)
    ax.plot([x_ancla - bx, x_ancla + bx], [y_ancla - by, y_ancla + by], color='#9A3412', linewidth=3.0, zorder=13)
    ax.text(x_ancla - 2.5, y_ancla - 2.0, tipo, fontsize=4.8, fontweight='bold', color='#9A3412', zorder=14)

def dibujar_bloque_medidor_cad(ax, x, y, cod=""):
    """Dibuja la caja portamedidor de abonado según simbología DGE."""
    # Caja de concreto/policarbonato
    rect = patches.Rectangle((x - 0.9, y - 0.9), 1.8, 1.8, facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=0.9, zorder=16)
    ax.add_patch(rect)
    # Mirilla circular con letra M
    c = patches.Circle((x, y), radius=0.6, facecolor='white', edgecolor='#DC2626', linewidth=0.6, zorder=17)
    ax.add_patch(c)
    ax.text(x, y, "M", ha='center', va='center', fontsize=4.5, fontweight='bold', color='#DC2626', zorder=18)
    if cod:
        ax.text(x + 1.2, y + 1.0, cod, fontsize=4.8, fontweight='bold', color='#1E293B', zorder=19)

# -------------------------------------------------------------------------
# RÓTULO FORMAL DE INGENIERÍA (MEMBRETE CAD ESTÁNDAR)
# -------------------------------------------------------------------------
def dibujar_rotulo_cad(ax, x0, y0, w, h, plano_cod, plano_nom, escala="1 : 2500"):
    # Marco exterior con línea gruesa
    rect_ext = patches.Rectangle((x0, y0), w, h, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.6, zorder=50)
    ax.add_patch(rect_ext)
    
    # Líneas divisorias horizontales
    h_filas = [0.18, 0.36, 0.52, 0.68, 0.84]
    for hf in h_filas:
        ax.plot([x0, x0 + w], [y0 + hf * h, y0 + hf * h], color='#334155', linewidth=0.8, zorder=51)
        
    # Divisiones verticales en fila inferior
    ax.plot([x0 + w * 0.35, x0 + w * 0.35], [y0, y0 + 0.18 * h], color='#334155', linewidth=0.8, zorder=51)
    ax.plot([x0 + w * 0.68, x0 + w * 0.68], [y0, y0 + 0.18 * h], color='#334155', linewidth=0.8, zorder=51)
    
    # Textos Institucionales
    ax.text(x0 + w/2.0, y0 + 0.92 * h, "UNIVERSIDAD NACIONAL DEL ALTIPLANO — PUNO\nFACULTAD DE INGENIERÍA MECÁNICA ELÉCTRICA, ELECTRÓNICA Y SISTEMAS",
            ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A', zorder=52)
            
    ax.text(x0 + w/2.0, y0 + 0.76 * h, "ESCUELA PROFESIONAL DE INGENIERÍA MECÁNICA ELÉCTRICA\nASIGNATURA: MEC330 — INSTALACIONES ELÉCTRICAS II (SEMESTRE 2026-II)",
            ha='center', va='center', fontsize=6.8, fontweight='bold', color='#0F766E', zorder=52)
            
    ax.text(x0 + w/2.0, y0 + 0.60 * h, "PROYECTO: INSTALACIÓN DEL SISTEMA DE ELECTRIFICACIÓN RURAL\nLP 22.9 kV Y REDES SECUNDARIAS SED 100 kVA SECTOR CHIFRÓN (CAPACHICA)",
            ha='center', va='center', fontsize=6.6, fontweight='bold', color='#0F172A', zorder=52)
            
    ax.text(x0 + w/2.0, y0 + 0.44 * h, f"PLANO: {plano_nom}",
            ha='center', va='center', fontsize=7.8, fontweight='bold', color='#B45309', zorder=52)
            
    ax.text(x0 + 0.02 * w, y0 + 0.27 * h, "PROYECTISTA:\nDOCENTES:",
            ha='left', va='center', fontsize=6.0, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.25 * w, y0 + 0.27 * h, "Br. Renzo Gabriel Mamani Galindo (Cód. 228447)\nIng. Leonidas Vilca Callata  /  Ing. Marcos José Villanueva Cornejo",
            ha='left', va='center', fontsize=6.0, color='#0F172A', zorder=52)
            
    # Casillas finales
    ax.text(x0 + 0.175 * w, y0 + 0.09 * h, f"FECHA:\nOctubre 2026",
            ha='center', va='center', fontsize=6.0, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.515 * w, y0 + 0.09 * h, f"ESCALA:\n{escala}",
            ha='center', va='center', fontsize=6.0, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.840 * w, y0 + 0.09 * h, f"LÁMINA:\n{plano_cod}",
            ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E3A8A', zorder=52)


# =========================================================================
# LÁMINA P-01: PLANO DE REDES EN PLANTA GENERAL (2 CIRCUITOS)
# =========================================================================
def generar_plano_p01_profesional(salida_pdf):
    kml_path = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\fuentes\kml\topografia_capachica_chifron.kml"
    csv_path = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\datos\cargas\censo_43_abonados.csv"
    
    rutas, vias = cargar_rutas_kml(kml_path)
    abonados = cargar_abonados_csv(csv_path)
    
    e_sed = 412606.01
    n_sed = 8270712.24
    
    # CONFIGURACIÓN ESTRICTA DE 2 CIRCUITOS:
    # Circuito C-1: Troncal Norte (Ruta 1)
    # Circuito C-2: Ramal Centro y Sur (Ruta 3 + Ruta 4 + Ruta 2)
    postes_c1 = []
    postes_c2 = []
    
    # Procesar Circuito C-1 (Ruta 1)
    if 'ruta electrica 1' in rutas:
        pts1 = rutas['ruta electrica 1']
        p_num = 1
        for i in range(len(pts1) - 1):
            p1 = pts1[i]
            p2 = pts1[i+1]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            n_seg = max(1, int(math.ceil(dist / 38.0)))
            for s in range(n_seg if i == len(pts1)-2 else n_seg):
                ts = s / float(n_seg)
                xe = p1[0] + ts * (p2[0] - p1[0])
                yn = p1[1] + ts * (p2[1] - p1[1])
                if math.hypot(xe - e_sed, yn - n_sed) < 6.0:
                    continue
                pid = f"P1-{p_num:02d}"
                es_fin = (s == 0 and i == 0) or (i == len(pts1)-2 and s == n_seg)
                pat = "PAT-1" if (p_num % 4 == 0 or es_fin) else None
                ret = "RET-I" if es_fin or (p_num in [6, 12]) else None
                postes_c1.append({"id": pid, "circuito": "C-1", "este": xe, "norte": yn, "pat": pat, "ret": ret})
                p_num += 1

    # Procesar Circuito C-2 (EXCLUSIVAMENTE Ruta 3 - Ramal Centro: 184.4 m)
    # Circuito 3 y Rutas 4 y 2 quedan COMPLETAMENTE ELIMINADAS
    p_num2 = 1
    if 'ruta electrica 3' in rutas:
        pts3 = rutas['ruta electrica 3']
        for i in range(len(pts3) - 1):
            p1 = pts3[i]
            p2 = pts3[i+1]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            n_seg = max(1, int(math.ceil(dist / 38.0)))
            for s in range(n_seg if i == len(pts3)-2 else n_seg):
                ts = s / float(n_seg)
                xe = p1[0] + ts * (p2[0] - p1[0])
                yn = p1[1] + ts * (p2[1] - p1[1])
                if math.hypot(xe - e_sed, yn - n_sed) < 6.0:
                    continue
                pid = f"P2-{p_num2:02d}"
                es_fin = (s == 0 and i == 0) or (i == len(pts3)-2 and s == n_seg)
                pat = "PAT-1" if (p_num2 % 4 == 0 or es_fin) else None
                ret = "RET-I" if es_fin else None
                postes_c2.append({"id": pid, "circuito": "C-2", "este": xe, "norte": yn, "pat": pat, "ret": ret})
                p_num2 += 1

    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    
    # Marco exterior del plano completo (Margen CAD 10mm)
    ax_box = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax_box.axis('off')
    rect_borde_ext = patches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='#0F172A', linewidth=2.0)
    rect_borde_int = patches.Rectangle((0.005, 0.005), 0.99, 0.99, facecolor='none', edgecolor='#0F172A', linewidth=0.8)
    ax_box.add_patch(rect_borde_ext)
    ax_box.add_patch(rect_borde_int)

    # Ventana cartográfica principal de redes
    ax_map = fig.add_axes([0.04, 0.05, 0.66, 0.90])
    
    # Dibujar Vías y Calles con doble línea de calzada estilo CAD
    for v_nom, pts in vias:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax_map.plot(xs, ys, color='#64748B', linewidth=2.5, linestyle='-', zorder=1)
        ax_map.plot(xs, ys, color='#E2E8F0', linewidth=0.8, linestyle='--', zorder=2)

    # Línea Primaria MT 22.9 kV (Alimentación Electro Puno)
    traza_mt = [(412380.00, 8270740.00), (412490.00, 8270725.00), (e_sed, n_sed)]
    x_mt = [p[0] for p in traza_mt]
    y_mt = [p[1] for p in traza_mt]
    ax_map.plot(x_mt, y_mt, color='#0284C7', linewidth=2.8, linestyle='-', zorder=4, label='Línea Primaria MT 22.9 kV (AAAC 35 mm²)')
    for p_mt in traza_mt[:-1]:
        ax_map.plot(p_mt[0], p_mt[1], marker='s', color='#0284C7', markersize=5.0, zorder=5)

    # TRAZADO DE LOS 2 CIRCUITOS DE BAJA TENSIÓN:
    # 1. Circuito C-1 (Troncal Norte - CAAI 3x35+25+16 mm²)
    if 'ruta electrica 1' in rutas:
        pts1 = rutas['ruta electrica 1']
        ax_map.plot([p[0] for p in pts1], [p[1] for p in pts1], color='#1D4ED8', linewidth=2.6, zorder=3,
                    label='Circuito C-1 BT (Troncal Norte Ruta 1: CAAI 3x35+25+16 mm²)')
    # 2. Circuito C-2 (Ramal Centro - CAAI 3x25+25+16 mm²)
    if 'ruta electrica 3' in rutas:
        pts3 = [(e_sed, n_sed)] + rutas['ruta electrica 3']
        ax_map.plot([p[0] for p in pts3], [p[1] for p in pts3], color='#B45309', linewidth=2.4, zorder=3,
                    label='Circuito C-2 BT (Ramal Centro Ruta 3: CAAI 3x25+25+16 mm²)')

    # Dibujar Postes de BT del Circuito C-1
    for p in postes_c1:
        dibujar_bloque_poste_cad(ax_map, p["este"], p["norte"], radio=1.2, etiqueta=p["id"])
        if p["pat"]:
            dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=-2.0, dy=-3.0, label="PAT-1")
        if p["ret"]:
            dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=-5.0, dy=-5.0, tipo="RET-I")

    # Dibujar Postes de BT del Circuito C-2
    for p in postes_c2:
        dibujar_bloque_poste_cad(ax_map, p["este"], p["norte"], radio=1.2, etiqueta=p["id"])
        if p["pat"]:
            dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=2.0, dy=-3.0, label="PAT-1")
        if p["ret"]:
            dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=5.0, dy=-5.0, tipo="RET-I")

    # Dibujar Subestación Biposte SAB-1 en Lat: -15.640067, Lon: -69.815400
    dibujar_bloque_sed_cad(ax_map, e_sed, n_sed)
    dibujar_bloque_pat_cad(ax_map, e_sed, n_sed, dx=-6.0, dy=-4.0, label="PAT-3 (R<=10Ω)")
    dibujar_bloque_retenida_cad(ax_map, e_sed, n_sed, dx=-8.0, dy=-8.0, tipo="RET-CV")
    
    # Rótulo de la Subestación
    ax_map.annotate("SED BIPOSTE SAB-1 (100 kVA)\n22.9 / 0.38 - 0.22 kV (Dyn5)\nLat: -15.640067°  Lon: -69.815400°\nE: 412606.01 m, N: 8270712.24 m\nOrigen C-1 (Norte) y C-2 (Sur)",
                    xy=(e_sed, n_sed), xytext=(e_sed - 95.0, n_sed + 45.0),
                    arrowprops=dict(facecolor='#B91C1C', shrink=0.08, width=1.4, headwidth=5.5),
                    bbox=dict(boxstyle="square,pad=0.3", fc="#FEF2F2", ec="#B91C1C", lw=1.0),
                    fontsize=6.0, fontweight='bold', color='#991B1B', zorder=25)

    # Conexión de las 43 Acometidas Domiciliarias a los Postes
    todos_postes = [(p["este"], p["norte"], p["id"]) for p in (postes_c1 + postes_c2)] + [(e_sed, n_sed, "SED-01")]
    for ab in abonados:
        xe_ab, yn_ab = ab["este"], ab["norte"]
        dist_min = 99999.0
        p_cercano = None
        for pe, pn, pid in todos_postes:
            d = math.hypot(xe_ab - pe, yn_ab - pn)
            if d < dist_min:
                dist_min = d
                p_cercano = (pe, pn, pid)
        if p_cercano:
            pe, pn, pid = p_cercano
            # Acometida aérea discontinua
            ax_map.plot([pe, xe_ab], [pn, yn_ab], color='#475569', linewidth=0.8, linestyle='--', zorder=4)
            # Medidor normalizado en lote
            dibujar_bloque_medidor_cad(ax_map, xe_ab, yn_ab, cod=f"{ab['cod']} ({dist_min:.0f}m)")

    # Formato de Grilla UTM WGS-84 y cotas perimetrales
    ax_map.set_xlim(412350, 412850)
    ax_map.set_ylim(8270650, 8271500)
    ax_map.set_aspect('equal')
    ax_map.grid(True, linestyle=':', color='#94A3B8', alpha=0.5)
    ax_map.set_title("PLANO DE REDES DE DISTRIBUCIÓN EN PLANTA GENERAL, ACOMETIDAS Y RETENIDAS — SECTOR CHIFRÓN (CAPACHICA)\nSISTEMA BIFILAR / TRIFÁSICO CON 2 CIRCUITOS DE DISTRIBUCIÓN (C-1 Y C-2) | SUBESTACIÓN BIPOSTE 100 kVA",
                     fontsize=9.0, fontweight='bold', color='#0F172A', pad=10)
    ax_map.set_xlabel("Coordenada Este UTM (m) — Datum WGS-84 Zona 19S", fontsize=7.5, fontweight='bold')
    ax_map.set_ylabel("Coordenada Norte UTM (m) — Datum WGS-84 Zona 19S", fontsize=7.5, fontweight='bold')
    ax_map.tick_params(axis='both', which='major', labelsize=6.8)

    # ---------------------------------------------------------------------
    # PANEL DERECHO: LEYENDA TÉCNICA DGE, CUADRO DE CARGAS Y RÓTULO
    # ---------------------------------------------------------------------
    # Leyenda Normalizada DGE
    ax_leg = fig.add_axes([0.72, 0.66, 0.25, 0.28])
    ax_leg.axis('off')
    rect_leg = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.2)
    ax_leg.add_patch(rect_leg)
    ax_leg.text(0.5, 0.94, "SIMBOLOGÍA TÉCNICA NORMALIZADA (DGE / CNE)", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')
    ax_leg.plot([0.04, 0.96], [0.88, 0.88], color='#334155', linewidth=0.8)
    
    simbolos_cad = [
        ("Red Primaria MT 22.9 kV (AAAC 35 mm²)", '#0284C7', '-', 'line'),
        ("Circuito C-1 BT Troncal Norte (CAAI 3x35+25+16 mm²)", '#1D4ED8', '-', 'line'),
        ("Circuito C-2 BT Ramal Centro (CAAI 3x25+25+16 mm²)", '#B45309', '-', 'line'),
        ("Acometida Concéntrica Aérea SET 2x4 mm²", '#475569', '--', 'line'),
        ("Subestación Distribución Biposte SAB-1 (100 kVA)", '#B91C1C', 'sed', 'sed'),
        ("Poste Concreto C.A.C. BT 8m/200daN (Bloque DGE)", '#0F172A', 'poste', 'poste'),
        ("Caja Portamedidor Monofásico de Abonado (M)", '#DC2626', 'med', 'med'),
        ("Puesta a Tierra Normalizada (PAT-3 / PAT-1)", '#15803D', 'pat', 'pat'),
        ("Retenida Inclinada / Contraviento (RET-I / RET-CV)", '#9A3412', 'ret', 'ret')
    ]
    y_l = 0.80
    for desc, col, st, t in simbolos_cad:
        if t == 'line':
            ax_leg.plot([0.06, 0.20], [y_l, y_l], color=col, linestyle=st, linewidth=2.0)
        elif t == 'sed':
            rect_s = patches.Rectangle((0.10, y_l - 0.025), 0.07, 0.05, facecolor='#FEF3C7', edgecolor='#B45309', linewidth=1.0)
            ax_leg.add_patch(rect_s)
        elif t == 'poste':
            c_p = patches.Circle((0.13, y_l), radius=0.025, facecolor='white', edgecolor='black', linewidth=0.8)
            ax_leg.add_patch(c_p)
            w_p = Wedge((0.13, y_l), 0.025, 0, 90, facecolor='black', edgecolor='none')
            ax_leg.add_patch(w_p)
        elif t == 'med':
            rect_m = patches.Rectangle((0.10, y_l - 0.025), 0.06, 0.05, facecolor='#FEE2E2', edgecolor='#DC2626', linewidth=0.8)
            ax_leg.add_patch(rect_m)
            ax_leg.text(0.13, y_l, "M", ha='center', va='center', fontsize=4.0, fontweight='bold', color='#DC2626')
        elif t == 'pat':
            ax_leg.plot([0.13, 0.13], [y_l - 0.02, y_l + 0.02], color='#15803D', linewidth=1.2)
            ax_leg.plot([0.09, 0.17], [y_l - 0.02, y_l - 0.02], color='#15803D', linewidth=1.5)
        elif t == 'ret':
            ax_leg.plot([0.08, 0.18], [y_l, y_l], color='#C2410C', linewidth=1.5)
            ax_leg.plot([0.18, 0.18], [y_l - 0.02, y_l + 0.02], color='#9A3412', linewidth=2.5)
        ax_leg.text(0.24, y_l, desc, va='center', fontsize=5.8, color='#0F172A')
        y_l -= 0.088

    # Cuadro de Cargas de los 2 Circuitos
    ax_car = fig.add_axes([0.72, 0.36, 0.25, 0.28])
    ax_car.axis('off')
    rect_car = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.2)
    ax_car.add_patch(rect_car)
    ax_car.text(0.5, 0.94, "CUADRO DE CARGAS — 2 CIRCUITOS DE BT", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')
    ax_car.plot([0.04, 0.96], [0.88, 0.88], color='#334155', linewidth=0.8)
    
    filas_2c = [
        ("Abonados Censados Actuales (NU₀)", "43 viviendas"),
        ("Tasa Crecimiento y Horizonte", "3.0 % anual | 20 años"),
        ("Usuarios Proyectados (NU_f)", "78 abonados"),
        ("Calificación Eléctrica Asignada", "0.90 kW / abonado"),
        ("Circuito C-1 (Norte Ruta 1: 51 hab / 10 lum)", "46.50 kW (51.67 kVA)"),
        ("Circuito C-2 (Centro Ruta 3: 27 hab / 5 lum)", "24.60 kW (27.33 kVA)"),
        ("MÁXIMA DEMANDA ACTIVA TOTAL", "71.10 kW"),
        ("Factor de Potencia de Diseño", "cos φ = 0.90"),
        ("POTENCIA APARENTE DEMANDADA", "79.00 kVA"),
        ("TRANSFORMADOR ESTANDARIZADO", "100 kVA (Dyn5)"),
        ("Margen de Reserva Técnica SED", "21.00 %")
    ]
    y_c = 0.82
    for param, val in filas_2c:
        f_w = 'bold' if 'MÁXIMA' in param or 'TRANSFORMADOR' in param or 'POTENCIA' in param or 'Circuito' in param else 'normal'
        c_t = '#B91C1C' if 'TRANSFORMADOR' in param else ('#1D4ED8' if 'C-1' in param else ('#B45309' if 'C-2' in param else '#0F172A'))
        ax_car.text(0.05, y_c, param, va='center', fontsize=5.6, fontweight=f_w, color=c_t)
        ax_car.text(0.95, y_c, val, ha='right', va='center', fontsize=5.6, fontweight='bold', color=c_t)
        y_c -= 0.072

    # Rótulo Oficial de Ingeniería Lámina P-01
    dibujar_rotulo_cad(fig.add_axes([0.72, 0.05, 0.25, 0.29]), 0, 0, 1, 1,
                       plano_cod="P-01",
                       plano_nom="REDES DE DISTRIBUCIÓN EN PLANTA GENERAL,\nACOMETIDAS Y RETENIDAS (2 CIRCUITOS)",
                       escala="1 : 2500")

    fig.savefig(salida_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"Lámina P-01 (2 Circuitos CAD) generada exitosamente en: {salida_pdf}")


# =========================================================================
# LÁMINA U-01: DIAGRAMA UNIFILAR GENERAL (2 CIRCUITOS DE BT)
# =========================================================================
def generar_plano_u01_profesional(salida_pdf):
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    
    # Marco exterior
    ax_box = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax_box.axis('off')
    rect_borde_ext = patches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='#0F172A', linewidth=2.0)
    rect_borde_int = patches.Rectangle((0.005, 0.005), 0.99, 0.99, facecolor='none', edgecolor='#0F172A', linewidth=0.8)
    ax_box.add_patch(rect_borde_ext)
    ax_box.add_patch(rect_borde_int)

    # ---------------------------------------------------------------------
    # PANEL PRINCIPAL: DIAGRAMA UNIFILAR (2 CIRCUITOS DE BT)
    # ---------------------------------------------------------------------
    ax_uni = fig.add_axes([0.05, 0.06, 0.52, 0.88])
    ax_uni.axis('off')
    rect_u = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.2)
    ax_uni.add_patch(rect_u)
    
    ax_uni.text(0.5, 0.965, "DIAGRAMA UNIFILAR GENERAL — SED BIPOSTE 100 kVA", ha='center', va='center', fontsize=9.2, fontweight='bold', color='#1E3A8A')
    ax_uni.text(0.5, 0.940, "Alimentación MT 22.9 kV | Salidas en BT 380/220 V con 2 Circuitos (C-1 y C-2) + Alumbrado Público", ha='center', va='center', fontsize=6.8, color='#64748B')
    ax_uni.plot([0.04, 0.96], [0.92, 0.92], color='#334155', linewidth=1.0)

    # Red Primaria MT 22.9 kV
    ax_uni.plot([0.5, 0.5], [0.91, 0.84], color='#0284C7', linewidth=2.5)
    ax_uni.text(0.52, 0.88, "LÍNEA PRIMARIA 22.9 kV (Red Electro Puno S.A.A.)\nTrifásico 3 Hilos — Conductor AAAC 35 mm²", fontsize=6.5, fontweight='bold', color='#0284C7')

    # Pararrayos de Distribución ZnO (Derivación)
    ax_uni.plot([0.5, 0.32], [0.84, 0.84], color='#0284C7', linewidth=1.8)
    ax_uni.plot([0.32, 0.32], [0.84, 0.79], color='#0284C7', linewidth=1.8)
    rect_par = patches.Rectangle((0.30, 0.76), 0.04, 0.03, facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=1.2)
    ax_uni.add_patch(rect_par)
    ax_uni.text(0.12, 0.775, "Pararrayos Óxido Metálico (ZnO)\n21 kV / 10 kA (Clase 1 Distribución)", fontsize=5.8, color='#B91C1C')
    # Puesta a tierra de pararrayos
    ax_uni.plot([0.32, 0.32], [0.76, 0.72], color='#15803D', linewidth=1.2)
    ax_uni.plot([0.29, 0.35], [0.72, 0.72], color='#15803D', linewidth=1.5)
    ax_uni.plot([0.30, 0.34], [0.71, 0.71], color='#15803D', linewidth=1.5)
    ax_uni.text(0.36, 0.715, "PAT-3", fontsize=5.5, fontweight='bold', color='#15803D')

    # Seccionadores Cut-Out en serie
    ax_uni.plot([0.5, 0.5], [0.84, 0.80], color='#0284C7', linewidth=1.8)
    rect_co = patches.Rectangle((0.47, 0.76), 0.06, 0.04, facecolor='#EFF6FF', edgecolor='#1D4ED8', linewidth=1.4)
    ax_uni.add_patch(rect_co)
    ax_uni.text(0.55, 0.78, "Seccionador Fusible Cut-Out\n27 kV / 100 A (Fusible Chicote K 4A)", fontsize=6.0, color='#1D4ED8')

    # Bajada a Bornes de Media Tensión del Transformador
    ax_uni.plot([0.5, 0.5], [0.76, 0.70], color='#0284C7', linewidth=1.8)

    # Símbolo Transformador Trifásico (2 círculos enlazados)
    c_mt = patches.Circle((0.5, 0.66), radius=0.035, facecolor='none', edgecolor='#DC2626', linewidth=2.0)
    c_bt = patches.Circle((0.5, 0.61), radius=0.035, facecolor='none', edgecolor='#1D4ED8', linewidth=2.0)
    ax_uni.add_patch(c_mt)
    ax_uni.add_patch(c_bt)
    ax_uni.text(0.56, 0.65, "TRANSFORMADOR DE DISTRIBUCIÓN 100 kVA\nRelación de Transformación: 22.9 / 0.38 - 0.22 kV\nGrupo Conexión: Dyn5 | Frecuencia: 60 Hz | ONAN\nDemanda Máxima: 79.0 kVA (Reserva Técnica: 21.0%)",
                fontsize=6.5, fontweight='bold', color='#991B1B')

    # Puesta a tierra de Neutro en BT
    ax_uni.plot([0.465, 0.38], [0.61, 0.61], color='#15803D', linewidth=1.2)
    ax_uni.plot([0.38, 0.38], [0.61, 0.57], color='#15803D', linewidth=1.2)
    ax_uni.plot([0.35, 0.41], [0.57, 0.57], color='#15803D', linewidth=1.5)
    ax_uni.plot([0.36, 0.40], [0.56, 0.56], color='#15803D', linewidth=1.5)
    ax_uni.text(0.20, 0.565, "Puesta a Tierra de Neutro\nR <= 10 Ω (PAT-3)", fontsize=5.5, color='#15803D')

    # Conductor de enlace a Tablero General BT
    ax_uni.plot([0.5, 0.5], [0.575, 0.52], color='#1D4ED8', linewidth=2.5)

    # Tablero de Distribución de Baja Tensión (Gabinete IP65)
    rect_tab = patches.Rectangle((0.10, 0.08), 0.80, 0.44, facecolor='#F8FAFC', edgecolor='#0F172A', linewidth=1.5)
    ax_uni.add_patch(rect_tab)
    ax_uni.text(0.5, 0.505, "TABLERO GENERAL DE DISTRIBUCIÓN BT (GABINETE FIBRA POLIÉSTER IP65)", ha='center', fontsize=7.2, fontweight='bold', color='#0F172A')

    # Interruptor General Totalizador 3x160A
    rect_gen = patches.Rectangle((0.44, 0.43), 0.12, 0.05, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.5)
    ax_uni.add_patch(rect_gen)
    ax_uni.text(0.5, 0.455, "TOTALIZADOR GENERAL 3x160 A\nTermomagnético Regulable (Icu = 25 kA)", ha='center', va='center', fontsize=5.8, fontweight='bold', color='#92400E')

    # Barra Trifásica de Cobre 380/220 V
    ax_uni.plot([0.5, 0.5], [0.43, 0.37], color='#1D4ED8', linewidth=2.0)
    ax_uni.plot([0.20, 0.80], [0.37, 0.37], color='#1E293B', linewidth=3.5)
    ax_uni.text(0.82, 0.37, "BARRA 380/220 V", va='center', fontsize=6.2, fontweight='bold', color='#1E293B')

    # EXACTAMENTE 2 CIRCUITOS DE DISTRIBUCIÓN + ALUMBRADO PÚBLICO:
    circuitos_2c = [
        (0.30, "C-1", "3x100 A", "Troncal Norte (Ruta 1 - Playa)\n51 usuarios proyectados\nDemanda: 46.50 kW (51.7 kVA)\nConductor: CAAI 3x35+25+16 mm²\nLongitud: 819.7 m | ΔV = 3.82%"),
        (0.52, "C-2", "3x63 A", "Ramal Centro (Ruta 3)\n27 usuarios proyectados\nDemanda: 24.60 kW (27.3 kVA)\nConductor: CAAI 3x25+25+16 mm²\nLongitud: 184.4 m | ΔV = 1.15%"),
        (0.72, "AP", "2x16 A", "Alumbrado Público Rural\n15 Luminarias LED 60W\nContactor 25A + Fotocelda\nConductor: CAAI 1x16 mm²\nDemanda: 0.90 kW")
    ]
    for xc, cid, itm, det in circuitos_2c:
        ax_uni.plot([xc, xc], [0.37, 0.31], color='#1D4ED8', linewidth=1.8)
        rect_it = patches.Rectangle((xc - 0.06, 0.25), 0.12, 0.06, facecolor='#FFFFFF', edgecolor='#1D4ED8', linewidth=1.2)
        ax_uni.add_patch(rect_it)
        ax_uni.text(xc, 0.28, f"ITM {cid}\n{itm}", ha='center', va='center', fontsize=5.8, fontweight='bold', color='#1E3A8A')
        ax_uni.plot([xc, xc], [0.25, 0.18], color='#1D4ED8', linewidth=1.8)
        ax_uni.plot(xc, 0.18, marker='v', color='#1D4ED8', markersize=6.0)
        ax_uni.text(xc, 0.14, det, ha='center', va='top', fontsize=5.2, color='#334155')

    # ---------------------------------------------------------------------
    # PANEL DERECHO: CUADRO DE ESPECIFICACIONES DE EQUIPOS Y RÓTULO
    # ---------------------------------------------------------------------
    ax_esp = fig.add_axes([0.60, 0.36, 0.37, 0.58])
    ax_esp.axis('off')
    rect_e = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.2)
    ax_esp.add_patch(rect_e)
    ax_esp.text(0.5, 0.96, "ESPECIFICACIONES TÉCNICAS DE EQUIPOS Y PROTECCIONES", ha='center', va='center', fontsize=7.8, fontweight='bold', color='#1E3A8A')
    ax_esp.plot([0.04, 0.96], [0.92, 0.92], color='#334155', linewidth=0.8)

    especs = [
        ("Transformador de Distribución", "100 kVA, 22.9 / 0.38-0.22 kV, trifásico, Dyn5, 60 Hz, ONAN, pérdidas garantizadas Po<=280W, Pk<=1450W."),
        ("Cortacircuitos Fusibles (Cut-Out)", "03 unidades tipo expulsión, 27 kV, 100 A, 150 kV BIL. Portafusible basculante para fusible chicote tipo K de 4 A."),
        ("Pararrayos de Distribución", "03 unidades de óxido de zinc (ZnO), 21 kV, corriente de descarga nominal 10 kA (Clase 1 de distribución)."),
        ("Interruptor Termomagnético General", "Caja moldeada 3x160 A, regulación térmica 0.8-1.0 In, poder de corte Icu = 25 kA a 380 V."),
        ("Interruptores de Circuitos C-1 y C-2", "Caja moldeada 3x80 A regulable, curva C, Icu = 18 kA a 380 V."),
        ("Circuito de Alumbrado Público", "ITM bipolar 2x16 A (6 kA), contactor modular 25 A AC-1, relé fotoeléctrico crepuscular de 1000 W."),
        ("Sistema de Puesta a Tierra PAT-3", "02 electrodos verticales de Cu 5/8\"x2.40m en paralelo a 4.8m, unidos con cable Cu 35 mm², bentonita sódica. R <= 10 Ω."),
        ("Gabinete de Distribución", "Poliéster reforzado con fibra de vidrio (PRFV), grado de protección IP65, cerradura tipo falleba, adosado a poste.")
    ]
    y_esp = 0.86
    for eq, desc in especs:
        ax_esp.text(0.05, y_esp, f"• {eq}:", fontsize=6.2, fontweight='bold', color='#B45309')
        ax_esp.text(0.08, y_esp - 0.045, desc, fontsize=5.5, color='#0F172A')
        y_esp -= 0.102

    # Rótulo Oficial de Ingeniería Lámina U-01
    dibujar_rotulo_cad(fig.add_axes([0.60, 0.05, 0.37, 0.29]), 0, 0, 1, 1,
                       plano_cod="U-01",
                       plano_nom="DIAGRAMA UNIFILAR GENERAL Y ESQUEMA DE\nPROTECCIONES BT (2 CIRCUITOS + AP)",
                       escala="INDICADA")

    fig.savefig(salida_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"Lámina U-01 (Diagrama Unifilar CAD) generada exitosamente en: {salida_pdf}")


if __name__ == "__main__":
    out_dir = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\entregables\planos"
    os.makedirs(out_dir, exist_ok=True)
    
    p01 = os.path.join(out_dir, "plano_P01_redes_planta.pdf")
    u01 = os.path.join(out_dir, "plano_U01_diagrama_unifilar_detalles.pdf")
    
    generar_plano_p01_profesional(p01)
    generar_plano_u01_profesional(u01)
