# -*- coding: utf-8 -*-
"""
generar_planos_cad_profesionales.py
Genera las láminas oficiales de ingeniería electromecánica en formato A3 Horizontal (420 x 297 mm)
con simbología normalizada DGE-MEM / Electro Puno S.A.A. y diseño CAD profesional con cero solapes:
- Lámina P-01: Redes de Distribución en Planta General, Acometidas Domiciliarias y Retenidas (2 Circuitos).
- Lámina U-01: Diagrama Unifilar General y Esquema de Protecciones (SED Biposte 100 kVA).

Optimizado con algoritmos de evasión de colisiones (staggering) y máscaras anticolisión (wipeout)
para garantizar 100% de legibilidad sin cruces entre textos y líneas.

Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
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
# BLOQUES GRÁFICOS CAD NORMALIZADOS CON MÁSCARA ANTICOLISIÓN
# -------------------------------------------------------------------------
def dibujar_bloque_poste_cad(ax, x, y, radio=1.2, etiqueta="", ap=False, dx_ap=3.5, dy_ap=1.0, pos_etiqueta='top-left'):
    """Dibuja un poste de concreto C.A.C. con bloque normalizado DGE y máscara anticolisión."""
    c = patches.Circle((x, y), radius=radio, facecolor='white', edgecolor='#0F172A', linewidth=0.9, zorder=15)
    ax.add_patch(c)
    w1 = Wedge((x, y), radio, 0, 90, facecolor='#0F172A', edgecolor='none', zorder=16)
    w2 = Wedge((x, y), radio, 180, 270, facecolor='#0F172A', edgecolor='none', zorder=16)
    ax.add_patch(w1)
    ax.add_patch(w2)
    
    if ap:
        x_lum = x + dx_ap
        y_lum = y + dy_ap
        ax.plot([x, x_lum], [y, y_lum], color='#334155', linewidth=1.2, zorder=14)
        lum = patches.Circle((x_lum, y_lum), radius=1.0, facecolor='#FEF08A', edgecolor='#CA8A04', linewidth=1.0, zorder=17)
        ax.add_patch(lum)
        ax.plot(x_lum, y_lum, marker='o', color='#CA8A04', markersize=2.2, zorder=18)
        
    if etiqueta:
        if pos_etiqueta == 'top-left':
            ex, ey = x - radio - 1.2, y + radio + 1.2
            ha, va = 'right', 'center'
        elif pos_etiqueta == 'top-right':
            ex, ey = x + radio + 1.2, y + radio + 1.2
            ha, va = 'left', 'center'
        elif pos_etiqueta == 'bottom-left':
            ex, ey = x - radio - 1.2, y - radio - 1.2
            ha, va = 'right', 'center'
        elif pos_etiqueta == 'bottom-right':
            ex, ey = x + radio + 1.2, y - radio - 1.2
            ha, va = 'left', 'center'
        elif pos_etiqueta == 'top':
            ex, ey = x, y + radio + 1.5
            ha, va = 'center', 'bottom'
        elif pos_etiqueta == 'bottom':
            ex, ey = x, y - radio - 1.5
            ha, va = 'center', 'top'
        else:
            ex, ey = x + radio + 1.2, y + radio + 1.2
            ha, va = 'left', 'center'
            
        ax.text(ex, ey, etiqueta, fontsize=4.6, fontweight='bold', color='#0F172A', ha=ha, va=va,
                bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='#64748B', lw=0.4, alpha=0.95), zorder=22)

def dibujar_bloque_sed_cad(ax, x, y):
    """Dibuja la Subestación Biposte SAB-1 en planta con simbología normalizada Electro Puno."""
    dx = 1.4
    for px in [x - dx, x + dx]:
        c = patches.Circle((px, y), radius=1.6, facecolor='white', edgecolor='#B91C1C', linewidth=1.2, zorder=20)
        ax.add_patch(c)
        w1 = Wedge((px, y), 1.6, 0, 90, facecolor='#B91C1C', edgecolor='none', zorder=21)
        w2 = Wedge((px, y), 1.6, 180, 270, facecolor='#B91C1C', edgecolor='none', zorder=21)
        ax.add_patch(w1)
        ax.add_patch(w2)
    rect_plat = patches.Rectangle((x - 2.8, y - 0.7), 5.6, 1.4, facecolor='#FEE2E2', edgecolor='#B91C1C', linewidth=1.0, zorder=19)
    ax.add_patch(rect_plat)
    rect_trafo = patches.Rectangle((x - 1.2, y - 1.2), 2.4, 2.4, facecolor='#FEF3C7', edgecolor='#B45309', linewidth=1.2, zorder=22)
    ax.add_patch(rect_trafo)
    ax.text(x, y, "100 kVA", ha='center', va='center', fontsize=4.4, fontweight='bold', color='#78350F', zorder=23)

def dibujar_bloque_pat_cad(ax, x, y, dx=0, dy=-4.0, label="PAT-1"):
    """Dibuja el símbolo normalizado DGE de puesta a tierra con fondo protector."""
    x_end, y_end = x + dx, y + dy
    ax.plot([x, x_end], [y, y_end], color='#15803D', linewidth=1.0, zorder=12)
    ax.plot([x_end - 2.0, x_end + 2.0], [y_end, y_end], color='#15803D', linewidth=1.4, zorder=13)
    ax.plot([x_end - 1.3, x_end + 1.3], [y_end - 0.8, y_end - 0.8], color='#15803D', linewidth=1.4, zorder=13)
    ax.plot([x_end - 0.6, x_end + 0.6], [y_end - 1.6, y_end - 1.6], color='#15803D', linewidth=1.4, zorder=13)
    ax.text(x_end, y_end - 2.8, label, fontsize=4.0, fontweight='bold', color='#15803D', ha='center', va='top',
            bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='#15803D', lw=0.3, alpha=0.92), zorder=20)

def dibujar_bloque_retenida_cad(ax, x, y, dx=-5.5, dy=-5.5, tipo="RET-I"):
    """Dibuja la retenida mecánica con aislador y bloque de anclaje."""
    x_ancla, y_ancla = x + dx, y + dy
    ax.plot([x, x_ancla], [y, y_ancla], color='#C2410C', linewidth=1.2, zorder=12)
    xm = (x + x_ancla) / 2.0
    ym = (y + y_ancla) / 2.0
    ax.plot(xm, ym, marker='s', color='#D97706', markersize=3.2, zorder=13)
    ang = math.atan2(dy, dx) + math.pi / 2.0
    bx = 2.0 * math.cos(ang)
    by = 2.0 * math.sin(ang)
    ax.plot([x_ancla - bx, x_ancla + bx], [y_ancla - by, y_ancla + by], color='#9A3412', linewidth=2.8, zorder=13)
    r_dist = math.hypot(dx, dy)
    ux = dx / r_dist if r_dist > 0 else 0
    uy = dy / r_dist if r_dist > 0 else -1
    ax.text(x_ancla + ux * 2.8, y_ancla + uy * 2.8, tipo, fontsize=4.0, fontweight='bold', color='#9A3412',
            ha='center', va='center',
            bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='#9A3412', lw=0.3, alpha=0.92), zorder=20)

def dibujar_bloque_medidor_cad(ax, x, y, cod="", dx_label=1.6, dy_label=1.0, ha='left'):
    """Dibuja la caja portamedidor de abonado según simbología DGE con etiqueta protegida (sin colisión de letra M)."""
    rect = patches.Rectangle((x - 0.7, y - 0.7), 1.4, 1.4, facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=0.8, zorder=18)
    ax.add_patch(rect)
    c = patches.Circle((x, y), radius=0.45, facecolor='white', edgecolor='#DC2626', linewidth=0.5, zorder=19)
    ax.add_patch(c)
    ax.plot(x, y, marker='.', color='#DC2626', markersize=2.0, zorder=20)
    if cod:
        ax.text(x + dx_label, y + dy_label, cod, fontsize=4.2, fontweight='bold', color='#1E293B',
                ha=ha, va='center',
                bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='#DC2626', lw=0.35, alpha=0.95), zorder=25)

# -------------------------------------------------------------------------
# RÓTULO FORMAL DE INGENIERÍA (MEMBRETE CAD ESTÁNDAR)
# -------------------------------------------------------------------------
def dibujar_rotulo_cad(ax, x0, y0, w, h, plano_cod, plano_nom_l1, plano_nom_l2, escala="1 : 2500"):
    ax.axis('off')
    ax.set_xlim(x0, x0 + w)
    ax.set_ylim(y0, y0 + h)
    
    rect_ext = patches.Rectangle((x0, y0), w, h, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.6, zorder=50)
    ax.add_patch(rect_ext)
    
    h_filas = [0.18, 0.36, 0.52, 0.68, 0.84]
    for hf in h_filas:
        ax.plot([x0, x0 + w], [y0 + hf * h, y0 + hf * h], color='#334155', linewidth=0.8, zorder=51)
        
    ax.plot([x0 + w * 0.35, x0 + w * 0.35], [y0, y0 + 0.18 * h], color='#334155', linewidth=0.8, zorder=51)
    ax.plot([x0 + w * 0.68, x0 + w * 0.68], [y0, y0 + 0.18 * h], color='#334155', linewidth=0.8, zorder=51)
    
    # Textos Institucionales
    ax.text(x0 + w/2.0, y0 + 0.93 * h, "UNIVERSIDAD NACIONAL DEL ALTIPLANO — PUNO", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.88 * h, "FACULTAD DE INGENIERÍA MECÁNICA ELÉCTRICA, ELECTRÓNICA Y SISTEMAS", ha='center', va='center', fontsize=6.0, fontweight='bold', color='#1E3A8A', zorder=52)
            
    ax.text(x0 + w/2.0, y0 + 0.78 * h, "ESCUELA PROFESIONAL DE INGENIERÍA MECÁNICA ELÉCTRICA", ha='center', va='center', fontsize=6.4, fontweight='bold', color='#0F766E', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.72 * h, "ASIGNATURA: MEC330 — INSTALACIONES ELÉCTRICAS II (SEMESTRE 2026-II)", ha='center', va='center', fontsize=5.8, color='#0F766E', zorder=52)
            
    ax.text(x0 + w/2.0, y0 + 0.62 * h, "PROYECTO: INSTALACIÓN DEL SISTEMA DE ELECTRIFICACIÓN RURAL", ha='center', va='center', fontsize=6.2, fontweight='bold', color='#0F172A', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.56 * h, "LP 22.9 kV Y REDES SECUNDARIAS SED 100 kVA SECTOR CHIFRÓN (CAPACHICA)", ha='center', va='center', fontsize=5.8, color='#0F172A', zorder=52)
            
    # Título del Plano en 2 líneas explícitas (cero solape)
    ax.text(x0 + w/2.0, y0 + 0.46 * h, f"PLANO: {plano_nom_l1}", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#B45309', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.40 * h, plano_nom_l2, ha='center', va='center', fontsize=6.2, fontweight='bold', color='#B45309', zorder=52)
            
    ax.text(x0 + 0.03 * w, y0 + 0.27 * h, "PROYECTISTA:\nDOCENTES:", ha='left', va='center', fontsize=5.6, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.26 * w, y0 + 0.27 * h, "Br. Renzo Gabriel Mamani Galindo (Cód. 228447)\nIng. Leonidas Vilca Callata  /  Ing. Marcos José Villanueva Cornejo", ha='left', va='center', fontsize=5.6, color='#0F172A', zorder=52)
            
    # Casillas finales
    ax.text(x0 + 0.175 * w, y0 + 0.12 * h, "FECHA:", ha='center', va='center', fontsize=5.5, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.175 * w, y0 + 0.06 * h, "Octubre 2026", ha='center', va='center', fontsize=5.5, color='#334155', zorder=52)

    ax.text(x0 + 0.515 * w, y0 + 0.12 * h, "ESCALA:", ha='center', va='center', fontsize=5.5, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.515 * w, y0 + 0.06 * h, escala, ha='center', va='center', fontsize=5.5, color='#334155', zorder=52)

    ax.text(x0 + 0.840 * w, y0 + 0.12 * h, "LÁMINA:", ha='center', va='center', fontsize=5.8, fontweight='bold', color='#1E3A8A', zorder=52)
    ax.text(x0 + 0.840 * w, y0 + 0.06 * h, plano_cod, ha='center', va='center', fontsize=8.0, fontweight='bold', color='#1E3A8A', zorder=52)


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
    
    # 1. Postes Circuito C-1 (Filtrados para asegurar vanos >= 24 m)
    postes_c1_raw = []
    if 'ruta electrica 1' in rutas:
        pts1 = rutas['ruta electrica 1']
        for i in range(len(pts1) - 1):
            p1 = pts1[i]
            p2 = pts1[i+1]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            n_seg = max(1, int(math.ceil(dist / 38.0)))
            for s in range(n_seg if i == len(pts1)-2 else n_seg):
                ts = s / float(n_seg)
                xe = p1[0] + ts * (p2[0] - p1[0])
                yn = p1[1] + ts * (p2[1] - p1[1])
                if math.hypot(xe - e_sed, yn - n_sed) < 8.0:
                    continue
                postes_c1_raw.append({"este": xe, "norte": yn})

    postes_c1 = []
    for p in postes_c1_raw:
        if not postes_c1:
            postes_c1.append(p)
        else:
            if math.hypot(p["este"] - postes_c1[-1]["este"], p["norte"] - postes_c1[-1]["norte"]) >= 24.0:
                postes_c1.append(p)

    for idx, p in enumerate(postes_c1):
        p_num = idx + 1
        p["id"] = f"P1-{p_num:02d}"
        p["circuito"] = "C-1"
        es_fin = (idx == 0 or idx == len(postes_c1) - 1)
        p["pat"] = "PAT-1" if (p_num % 4 == 0 or es_fin) else None
        p["ret"] = "RET-I" if (es_fin or p_num in [6, 12, 18]) else None
        p["ap"] = True if p_num in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19] else False

    # 2. Postes Circuito C-2 (Filtrados para asegurar vanos >= 24 m)
    pts_c2 = []
    if 'ruta electrica 3' in rutas:
        pts_c2 += rutas['ruta electrica 3']
    if 'ruta electrica 4' in rutas:
        pts_c2 += rutas['ruta electrica 4']

    postes_c2_raw = []
    for i in range(len(pts_c2) - 1):
        p1 = pts_c2[i]
        p2 = pts_c2[i+1]
        dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        n_seg = max(1, int(math.ceil(dist / 38.0)))
        for s in range(n_seg if i == len(pts_c2)-2 else n_seg):
            ts = s / float(n_seg)
            xe = p1[0] + ts * (p2[0] - p1[0])
            yn = p1[1] + ts * (p2[1] - p1[1])
            if math.hypot(xe - e_sed, yn - n_sed) < 8.0:
                continue
            postes_c2_raw.append({"este": xe, "norte": yn})

    postes_c2 = []
    for p in postes_c2_raw:
        if not postes_c2:
            postes_c2.append(p)
        else:
            if math.hypot(p["este"] - postes_c2[-1]["este"], p["norte"] - postes_c2[-1]["norte"]) >= 24.0:
                postes_c2.append(p)

    for idx, p in enumerate(postes_c2):
        p_num = idx + 1
        p["id"] = f"P2-{p_num:02d}"
        p["circuito"] = "C-2"
        es_fin = (idx == 0 or idx == len(postes_c2) - 1)
        p["pat"] = "PAT-1" if (p_num % 4 == 0 or es_fin) else None
        p["ret"] = "RET-I" if (es_fin or p_num in [4, 8]) else None
        p["ap"] = True if p_num in [1, 3, 6, 9, 11] else False

    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    
    ax_box = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax_box.axis('off')
    rect_borde_ext = patches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='#0F172A', linewidth=2.0)
    rect_borde_int = patches.Rectangle((0.005, 0.005), 0.99, 0.99, facecolor='none', edgecolor='#0F172A', linewidth=0.8)
    ax_box.add_patch(rect_borde_ext)
    ax_box.add_patch(rect_borde_int)

    ax_map = fig.add_axes([0.04, 0.05, 0.66, 0.90])
    
    # Vías
    for v_nom, pts in vias:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax_map.plot(xs, ys, color='#64748B', linewidth=2.5, linestyle='-', zorder=1)
        ax_map.plot(xs, ys, color='#E2E8F0', linewidth=0.8, linestyle='--', zorder=2)

    # Línea Primaria MT
    traza_mt = [(412380.00, 8270740.00), (412490.00, 8270725.00), (e_sed, n_sed)]
    ax_map.plot([p[0] for p in traza_mt], [p[1] for p in traza_mt], color='#0284C7', linewidth=2.8, linestyle='-', zorder=4)
    for p_mt in traza_mt[:-1]:
        ax_map.plot(p_mt[0], p_mt[1], marker='s', color='#0284C7', markersize=5.0, zorder=5)

    # Redes BT
    if 'ruta electrica 1' in rutas:
        pts1 = rutas['ruta electrica 1']
        ax_map.plot([p[0] for p in pts1], [p[1] for p in pts1], color='#1D4ED8', linewidth=2.6, zorder=3)
    if pts_c2:
        pts_c2_draw = [(e_sed, n_sed)] + pts_c2
        ax_map.plot([p[0] for p in pts_c2_draw], [p[1] for p in pts_c2_draw], color='#B45309', linewidth=2.4, zorder=3)

    # Configuración de postes del Circuito C-1
    for p in postes_c1:
        pid = p["id"]
        if pid in ['P1-17']:
            pos_lbl = 'bottom-right'
        elif pid == 'P1-03':
            pos_lbl = 'bottom-left'
        elif pid in ['P1-14', 'P1-19']:
            pos_lbl = 'top-right'
        elif pid in ['P1-09', 'P1-11', 'P1-12', 'P1-13']:
            pos_lbl = 'top-left'
        else:
            casas_cercanas = [ab for ab in abonados if math.hypot(ab["este"] - p["este"], ab["norte"] - p["norte"]) < 20.0]
            pos_lbl = 'top-right' if (casas_cercanas and casas_cercanas[0]["este"] < p["este"]) else 'top-left'
        
        dibujar_bloque_poste_cad(ax_map, p["este"], p["norte"], radio=1.2, etiqueta=p["id"],
                                 ap=p.get("ap", False), dx_ap=3.5, dy_ap=1.0, pos_etiqueta=pos_lbl)
        
        if p["pat"]:
            if pid == 'P1-04':
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=4.5, dy=4.5, label="PAT-1")
            elif pid == 'P1-12':
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=4.5, dy=-4.5, label="PAT-1")
            elif pid == 'P1-16':
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=4.0, dy=-3.5, label="PAT-1")
            elif pid == 'P1-23':
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=-4.5, dy=5.0, label="PAT-1")
            else:
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=-3.5, dy=-3.5, label="PAT-1")
                
        if p["ret"]:
            if pid == 'P1-12':
                dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=6.5, dy=6.5, tipo="RET-I")
            elif pid == 'P1-23':
                dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=5.5, dy=7.5, tipo="RET-I")
            else:
                dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=-6.0, dy=-6.0, tipo="RET-I")

    for p in postes_c2:
        pid = p["id"]
        if pid == 'P2-01':
            pos_lbl = 'top-right'
        else:
            casas_cercanas = [ab for ab in abonados if math.hypot(ab["este"] - p["este"], ab["norte"] - p["norte"]) < 20.0]
            pos_lbl = 'top-right' if (casas_cercanas and casas_cercanas[0]["este"] < p["este"]) else 'top-left'
            
        dibujar_bloque_poste_cad(ax_map, p["este"], p["norte"], radio=1.2, etiqueta=p["id"],
                                 ap=p.get("ap", False), dx_ap=3.5, dy_ap=1.0, pos_etiqueta=pos_lbl)
        if p["pat"]:
            if pid == 'P2-01':
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=4.5, dy=-5.0, label="PAT-1")
            else:
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=3.5, dy=-3.5, label="PAT-1")
        if p["ret"]:
            if pid == 'P2-01':
                dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=-5.5, dy=5.5, tipo="RET-I")
            else:
                dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=5.5, dy=-5.5, tipo="RET-I")

    # Subestación Biposte SAB-1
    dibujar_bloque_sed_cad(ax_map, e_sed, n_sed)
    dibujar_bloque_pat_cad(ax_map, e_sed, n_sed, dx=0.0, dy=-12.0, label="PAT-3")
    dibujar_bloque_retenida_cad(ax_map, e_sed, n_sed, dx=14.0, dy=-12.0, tipo="RET-CV")
    
    # Rótulo de la Subestación al Suroeste (despejado de la SED y PAT-3)
    ax_map.annotate("SED BIPOSTE SAB-1 (100 kVA)\n22.9 / 0.38 - 0.22 kV (Dyn5)\nE: 412606.01 m, N: 8270712.24 m\nOrigen C-1 (Norte) y C-2 (Sur)",
                    xy=(e_sed, n_sed), xytext=(e_sed - 150.0, n_sed - 30.0),
                    arrowprops=dict(facecolor='#B91C1C', shrink=0.08, width=1.4, headwidth=5.5),
                    bbox=dict(boxstyle="square,pad=0.3", fc="#FEF2F2", ec="#B91C1C", lw=1.0),
                    fontsize=5.6, fontweight='bold', color='#991B1B', zorder=30)

    # Conexión de las 43 Acometidas con Offsets Inteligentes Anticolisión
    todos_postes = [(p["este"], p["norte"], p["id"], p["circuito"]) for p in (postes_c1 + postes_c2)] + [(e_sed, n_sed, "SED-01", "SED")]
    
    label_offsets = {}
    for i, ab1 in enumerate(abonados):
        cid = ab1["cod"]
        if cid == 'C10':
            label_offsets[cid] = (-2.5, -1.8, 'right')
        elif cid == 'C11':
            label_offsets[cid] = (-2.5, 0.0, 'right')
        elif cid == 'C14':
            label_offsets[cid] = (-2.5, -1.8, 'right')
        elif cid == 'C15':
            label_offsets[cid] = (-2.5, 1.8, 'right')
        elif cid == 'C18':
            label_offsets[cid] = (0.0, 2.5, 'center')
        elif cid == 'C20':
            label_offsets[cid] = (-2.5, 0.0, 'right')
        elif cid == 'C28':
            label_offsets[cid] = (2.5, 2.0, 'left')
        elif cid == 'C43':
            label_offsets[cid] = (-2.8, 0.0, 'right')
        else:
            cercanos = [ab2 for j, ab2 in enumerate(abonados) if i != j and math.hypot(ab1["este"] - ab2["este"], ab1["norte"] - ab2["norte"]) < 14.0]
            if not cercanos:
                label_offsets[cid] = (2.2, 1.2, 'left')
            else:
                num = int(cid[1:])
                if num % 4 == 0:
                    label_offsets[cid] = (2.6, 2.2, 'left')
                elif num % 4 == 1:
                    label_offsets[cid] = (-2.6, 2.2, 'right')
                elif num % 4 == 2:
                    label_offsets[cid] = (2.6, -2.2, 'left')
                else:
                    label_offsets[cid] = (-2.6, -2.2, 'right')

    for ab in abonados:
        xe_ab, yn_ab = ab["este"], ab["norte"]
        if ab["cod"] == "C31":
            cand = [p for p in todos_postes if p[3] == "C-1"]
        elif int(ab["cod"][1:]) <= 30:
            cand = [p for p in todos_postes if p[3] in ["C-1", "SED"]]
        else:
            cand = [p for p in todos_postes if p[3] in ["C-2", "SED"]]
        p_cercano = min(cand, key=lambda p: math.hypot(xe_ab - p[0], yn_ab - p[1]))
        pe, pn, pid, pcirc = p_cercano
        ax_map.plot([pe, xe_ab], [pn, yn_ab], color='#64748B', linewidth=0.75, linestyle='--', zorder=3)
        
        dx_l, dy_l, ha_l = label_offsets[ab["cod"]]
        dibujar_bloque_medidor_cad(ax_map, xe_ab, yn_ab, cod=ab['cod'], dx_label=dx_l, dy_label=dy_l, ha=ha_l)

    ax_map.set_xlim(412350, 412950)
    ax_map.set_ylim(8270650, 8271500)
    ax_map.set_aspect('equal')
    ax_map.grid(True, linestyle=':', color='#94A3B8', alpha=0.5)
    ax_map.set_title("PLANO DE REDES DE DISTRIBUCIÓN EN PLANTA GENERAL, ACOMETIDAS Y RETENIDAS — SECTOR CHIFRÓN (CAPACHICA)\nSISTEMA BIFILAR / TRIFÁSICO CON 2 CIRCUITOS DE DISTRIBUCIÓN (C-1 Y C-2) | SUBESTACIÓN BIPOSTE 100 kVA",
                     fontsize=8.5, fontweight='bold', color='#0F172A', pad=10)
    ax_map.set_xlabel("Coordenada Este UTM (m) — Datum WGS-84 Zona 19S", fontsize=7.2, fontweight='bold')
    ax_map.set_ylabel("Coordenada Norte UTM (m) — Datum WGS-84 Zona 19S", fontsize=7.2, fontweight='bold')
    ax_map.tick_params(axis='both', which='major', labelsize=6.5)

    # 1. Leyenda Normalizada DGE
    ax_leg = fig.add_axes([0.72, 0.655, 0.25, 0.295])
    ax_leg.axis('off')
    rect_leg = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.2)
    ax_leg.add_patch(rect_leg)
    ax_leg.text(0.5, 0.94, "SIMBOLOGÍA TÉCNICA NORMALIZADA (DGE / CNE)", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#1E3A8A')
    ax_leg.plot([0.04, 0.96], [0.89, 0.89], color='#334155', linewidth=0.8)
    
    simbolos_cad = [
        ("Red Primaria MT 22.9 kV (AAAC 35 mm²)", '#0284C7', '-', 'line'),
        ("Circuito C-1 BT Troncal Norte + C31 (CAAI 3x35+25+16 mm²)", '#1D4ED8', '-', 'line'),
        ("Circuito C-2 BT Carretera al Fondo (CAAI 3x25+25+16 mm²)", '#B45309', '-', 'line'),
        ("Acometida Concéntrica Aérea SET 2x4 mm²", '#64748B', '--', 'line'),
        ("Subestación Distribución Biposte SAB-1 (100 kVA)", '#B91C1C', 'sed', 'sed'),
        ("Poste Concreto C.A.C. BT 8m/200daN (Bloque DGE)", '#0F172A', 'poste', 'poste'),
        ("Poste C.A.C. con Pastoral y Luminaria AP 60W LED", '#CA8A04', 'poste_ap', 'poste_ap'),
        ("Caja Portamedidor Monofásico de Abonado", '#DC2626', 'med', 'med'),
        ("Puesta a Tierra Normalizada (PAT-3 / PAT-1)", '#15803D', 'pat', 'pat'),
        ("Retenida Inclinada / Contraviento (RET-I / RET-CV)", '#9A3412', 'ret', 'ret')
    ]
    y_l = 0.82
    for desc, col, st, t in simbolos_cad:
        if t == 'line':
            ax_leg.plot([0.06, 0.20], [y_l, y_l], color=col, linestyle=st, linewidth=2.0)
        elif t == 'sed':
            rect_s = patches.Rectangle((0.10, y_l - 0.020), 0.07, 0.040, facecolor='#FEF3C7', edgecolor='#B45309', linewidth=1.0)
            ax_leg.add_patch(rect_s)
        elif t == 'poste':
            c_p = patches.Circle((0.13, y_l), radius=0.020, facecolor='white', edgecolor='black', linewidth=0.8)
            ax_leg.add_patch(c_p)
            w_p = Wedge((0.13, y_l), 0.020, 0, 90, facecolor='black', edgecolor='none')
            ax_leg.add_patch(w_p)
        elif t == 'poste_ap':
            c_p = patches.Circle((0.10, y_l), radius=0.016, facecolor='white', edgecolor='black', linewidth=0.7)
            ax_leg.add_patch(c_p)
            w_p = Wedge((0.10, y_l), 0.016, 0, 90, facecolor='black', edgecolor='none')
            ax_leg.add_patch(w_p)
            ax_leg.plot([0.10, 0.17], [y_l, y_l], color='#334155', linewidth=1.1)
            c_lum = patches.Circle((0.17, y_l), radius=0.014, facecolor='#FEF08A', edgecolor='#CA8A04', linewidth=0.8)
            ax_leg.add_patch(c_lum)
        elif t == 'med':
            rect_m = patches.Rectangle((0.10, y_l - 0.018), 0.06, 0.036, facecolor='#FEE2E2', edgecolor='#DC2626', linewidth=0.8)
            ax_leg.add_patch(rect_m)
            c_m = patches.Circle((0.13, y_l), radius=0.012, facecolor='white', edgecolor='#DC2626', linewidth=0.5)
            ax_leg.add_patch(c_m)
        elif t == 'pat':
            ax_leg.plot([0.13, 0.13], [y_l - 0.018, y_l + 0.018], color='#15803D', linewidth=1.2)
            ax_leg.plot([0.09, 0.17], [y_l - 0.018, y_l - 0.018], color='#15803D', linewidth=1.4)
        elif t == 'ret':
            ax_leg.plot([0.08, 0.18], [y_l, y_l], color='#C2410C', linewidth=1.4)
            ax_leg.plot([0.18, 0.18], [y_l - 0.018, y_l + 0.018], color='#9A3412', linewidth=2.2)
        ax_leg.text(0.24, y_l, desc, va='center', fontsize=5.4, color='#0F172A')
        y_l -= 0.076

    # 2. Cuadro de Cargas de los 2 Circuitos
    ax_car = fig.add_axes([0.72, 0.355, 0.25, 0.285])
    ax_car.axis('off')
    rect_car = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.2)
    ax_car.add_patch(rect_car)
    ax_car.text(0.5, 0.94, "CUADRO DE CARGAS — 2 CIRCUITOS DE BT", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#1E3A8A')
    ax_car.plot([0.04, 0.96], [0.88, 0.88], color='#334155', linewidth=0.8)
    
    filas_2c = [
        ("Abonados Censados Actuales (NU₀)", "43 viviendas"),
        ("Tasa Crecimiento y Horizonte", "3.0 % anual | 20 años"),
        ("Usuarios Proyectados (NU_f)", "78 abonados"),
        ("Calificación Eléctrica Asignada", "0.90 kW / abonado"),
        ("Circuito C-1 (Norte + C31: 56 hab / 10 lum)", "51.00 kW (56.67 kVA)"),
        ("Circuito C-2 (Carretera Fondo: 22 hab / 5 lum)", "20.10 kW (22.33 kVA)"),
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
        ax_car.text(0.05, y_c, param, va='center', fontsize=5.4, fontweight=f_w, color=c_t)
        ax_car.text(0.95, y_c, val, ha='right', va='center', fontsize=5.4, fontweight='bold', color=c_t)
        y_c -= 0.072

    # 3. Rótulo Oficial de Ingeniería Lámina P-01
    dibujar_rotulo_cad(fig.add_axes([0.72, 0.05, 0.25, 0.29]), 0, 0, 1, 1,
                       plano_cod="P-01",
                       plano_nom_l1="REDES DE DISTRIBUCIÓN EN PLANTA GENERAL,",
                       plano_nom_l2="ACOMETIDAS Y RETENIDAS (2 CIRCUITOS)",
                       escala="1 : 2500")

    fig.savefig(salida_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"Lámina P-01 generada exitosamente en: {salida_pdf}")


# =========================================================================
# LÁMINA U-01: DIAGRAMA UNIFILAR GENERAL (2 CIRCUITOS DE BT)
# =========================================================================
def generar_plano_u01_profesional(salida_pdf):
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    
    ax_box = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax_box.axis('off')
    rect_borde_ext = patches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='#0F172A', linewidth=2.0)
    rect_borde_int = patches.Rectangle((0.005, 0.005), 0.99, 0.99, facecolor='none', edgecolor='#0F172A', linewidth=0.8)
    ax_box.add_patch(rect_borde_ext)
    ax_box.add_patch(rect_borde_int)

    # PANEL PRINCIPAL: DIAGRAMA UNIFILAR (2 CIRCUITOS DE BT)
    ax_uni = fig.add_axes([0.05, 0.05, 0.53, 0.90])
    ax_uni.axis('off')
    rect_u = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.2)
    ax_uni.add_patch(rect_u)
    
    ax_uni.text(0.5, 0.968, "DIAGRAMA UNIFILAR GENERAL — SED BIPOSTE 100 kVA", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E3A8A')
    ax_uni.text(0.5, 0.942, "Alimentación MT 22.9 kV | Salidas en BT 380/220 V con 2 Circuitos (C-1 y C-2) + Alumbrado Público", ha='center', va='center', fontsize=6.6, color='#64748B')
    ax_uni.plot([0.04, 0.96], [0.925, 0.925], color='#334155', linewidth=1.0)

    # Red Primaria MT 22.9 kV
    ax_uni.plot([0.5, 0.5], [0.915, 0.840], color='#0284C7', linewidth=2.5)
    ax_uni.text(0.52, 0.885, "LÍNEA PRIMARIA 22.9 kV (Red Electro Puno S.A.A.)\nTrifásico 3 Hilos — Conductor AAAC 35 mm²", fontsize=6.2, fontweight='bold', color='#0284C7')

    # Pararrayos ZnO
    ax_uni.plot([0.5, 0.30], [0.840, 0.840], color='#0284C7', linewidth=1.8)
    ax_uni.plot([0.30, 0.30], [0.840, 0.790], color='#0284C7', linewidth=1.8)
    rect_par = patches.Rectangle((0.275, 0.755), 0.05, 0.035, facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=1.2)
    ax_uni.add_patch(rect_par)
    ax_uni.text(0.095, 0.772, "Pararrayos Óxido Metálico (ZnO)\n21 kV / 10 kA (Clase 1 Distribución)", fontsize=5.5, color='#B91C1C')
    # Puesta a tierra pararrayos
    ax_uni.plot([0.30, 0.30], [0.755, 0.715], color='#15803D', linewidth=1.2)
    ax_uni.plot([0.27, 0.33], [0.715, 0.715], color='#15803D', linewidth=1.5)
    ax_uni.plot([0.28, 0.32], [0.705, 0.705], color='#15803D', linewidth=1.5)
    ax_uni.text(0.34, 0.710, "PAT-3", fontsize=5.2, fontweight='bold', color='#15803D')

    # Seccionadores Cut-Out
    ax_uni.plot([0.5, 0.5], [0.840, 0.800], color='#0284C7', linewidth=1.8)
    rect_co = patches.Rectangle((0.47, 0.760), 0.06, 0.040, facecolor='#EFF6FF', edgecolor='#1D4ED8', linewidth=1.4)
    ax_uni.add_patch(rect_co)
    ax_uni.text(0.55, 0.780, "Seccionador Fusible Cut-Out\n27 kV / 100 A (Fusible Chicote K 4A)", fontsize=5.8, color='#1D4ED8')

    # Bajada a Bornes MT
    ax_uni.plot([0.5, 0.5], [0.760, 0.695], color='#0284C7', linewidth=1.8)

    # Transformador Trifásico 100 kVA
    c_mt = patches.Circle((0.5, 0.660), radius=0.035, facecolor='none', edgecolor='#DC2626', linewidth=2.0)
    c_bt = patches.Circle((0.5, 0.610), radius=0.035, facecolor='none', edgecolor='#1D4ED8', linewidth=2.0)
    ax_uni.add_patch(c_mt)
    ax_uni.add_patch(c_bt)
    ax_uni.text(0.56, 0.640, "TRANSFORMADOR DE DISTRIBUCIÓN 100 kVA\nRelación de Transformación: 22.9 / 0.38 - 0.22 kV\nGrupo Conexión: Dyn5 | Frecuencia: 60 Hz | ONAN\nDemanda Máxima: 79.0 kVA (Reserva Técnica: 21.0%)",
                fontsize=6.0, fontweight='bold', color='#991B1B')

    # Puesta a tierra Neutro BT
    ax_uni.plot([0.465, 0.38], [0.610, 0.610], color='#15803D', linewidth=1.2)
    ax_uni.plot([0.38, 0.38], [0.610, 0.565], color='#15803D', linewidth=1.2)
    ax_uni.plot([0.35, 0.41], [0.565, 0.565], color='#15803D', linewidth=1.5)
    ax_uni.plot([0.36, 0.40], [0.555, 0.555], color='#15803D', linewidth=1.5)
    ax_uni.text(0.21, 0.560, "Puesta a Tierra de Neutro\nR <= 10 Ω (PAT-3)", fontsize=5.2, color='#15803D')

    # Bajada a Tablero
    ax_uni.plot([0.5, 0.5], [0.575, 0.520], color='#1D4ED8', linewidth=2.5)

    # Gabinete BT IP65
    rect_tab = patches.Rectangle((0.08, 0.035), 0.84, 0.485, facecolor='#F8FAFC', edgecolor='#0F172A', linewidth=1.5)
    ax_uni.add_patch(rect_tab)
    ax_uni.text(0.5, 0.505, "TABLERO GENERAL DE DISTRIBUCIÓN BT (GABINETE FIBRA POLIÉSTER IP65)", ha='center', fontsize=7.0, fontweight='bold', color='#0F172A')

    # Totalizador General 3x160A
    rect_gen = patches.Rectangle((0.43, 0.435), 0.14, 0.050, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.5)
    ax_uni.add_patch(rect_gen)
    ax_uni.text(0.5, 0.460, "TOTALIZADOR GENERAL 3x160 A\nTermomagnético Regulable (Icu = 25 kA)", ha='center', va='center', fontsize=5.5, fontweight='bold', color='#92400E')

    # Barra Trifásica
    ax_uni.plot([0.5, 0.5], [0.435, 0.380], color='#1D4ED8', linewidth=2.0)
    ax_uni.plot([0.16, 0.84], [0.380, 0.380], color='#1E293B', linewidth=3.5)
    ax_uni.text(0.85, 0.380, "BARRA 380/220 V", va='center', fontsize=5.8, fontweight='bold', color='#1E293B')

    circuitos_data = [
        (0.28, "C-1", "3x100 A", [
            ("Troncal Norte + C31 (Ruta 1)", '#1E3A8A', True),
            ("56 usuarios proyectados", '#0F172A', False),
            ("Demanda: 51.00 kW (56.7 kVA)", '#B91C1C', True),
            ("CAAI 3x35+25+16 mm²", '#0F172A', False),
            ("L = 820.0 m | ΔV = 3.82%", '#15803D', True)
        ]),
        (0.50, "C-2", "3x63 A", [
            ("Carretera Fondo (Rutas 3 y 4)", '#B45309', True),
            ("22 usuarios proyectados", '#0F172A', False),
            ("Demanda: 20.10 kW (22.3 kVA)", '#B91C1C', True),
            ("CAAI 3x25+25+16 mm²", '#0F172A', False),
            ("L = 456.0 m | ΔV = 2.14%", '#15803D', True)
        ]),
        (0.72, "AP", "2x16 A", [
            ("Alumbrado Público Rural", '#CA8A04', True),
            ("15 Luminarias LED 60W", '#0F172A', False),
            ("Contactor 25A + Fotocelda", '#0F172A', False),
            ("CAAI 1x16 mm²", '#0F172A', False),
            ("Demanda AP: 0.90 kW", '#15803D', True)
        ])
    ]
    
    for xc, cid, itm_val, lineas_det in circuitos_data:
        ax_uni.plot([xc, xc], [0.380, 0.345], color='#1D4ED8', linewidth=1.8)
        
        rect_it = patches.Rectangle((xc - 0.065, 0.275), 0.13, 0.070, facecolor='#FFFFFF', edgecolor='#1D4ED8', linewidth=1.2)
        ax_uni.add_patch(rect_it)
        ax_uni.text(xc, 0.320, f"ITM {cid}", ha='center', va='center', fontsize=5.5, fontweight='bold', color='#1E3A8A')
        ax_uni.text(xc, 0.295, itm_val, ha='center', va='center', fontsize=5.0, color='#1E3A8A')
        
        ax_uni.plot([xc, xc], [0.275, 0.215], color='#1D4ED8', linewidth=1.8)
        ax_uni.plot(xc, 0.215, marker='v', color='#1D4ED8', markersize=5.5)
        
        rect_card = patches.Rectangle((xc - 0.095, 0.050), 0.190, 0.150, facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=0.7, zorder=10)
        ax_uni.add_patch(rect_card)
        
        y_pos = 0.180
        for txt, col, es_b in lineas_det:
            ax_uni.text(xc, y_pos, txt, ha='center', va='center',
                        fontsize=4.6, fontweight='bold' if es_b else 'normal', color=col, zorder=12)
            y_pos -= 0.028

    # PANEL DERECHO: ESPECIFICACIONES TÉCNICAS
    ax_esp = fig.add_axes([0.60, 0.355, 0.37, 0.595])
    ax_esp.axis('off')
    rect_e = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.2)
    ax_esp.add_patch(rect_e)
    ax_esp.text(0.5, 0.965, "ESPECIFICACIONES TÉCNICAS DE EQUIPOS Y PROTECCIONES", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')
    ax_esp.plot([0.04, 0.96], [0.935, 0.935], color='#334155', linewidth=0.8)

    especs = [
        ("Transformador de Distribución", "100 kVA, 22.9 / 0.38-0.22 kV, trifásico, Dyn5, 60 Hz, ONAN, Po<=280W, Pk<=1450W."),
        ("Cortacircuitos Fusibles (Cut-Out)", "03 unidades tipo expulsión, 27 kV, 100 A, 150 kV BIL, fusible chicote tipo K de 4 A."),
        ("Pararrayos de Distribución ZnO", "03 unidades de óxido de zinc (ZnO), 21 kV, corriente descarga nominal 10 kA Clase 1."),
        ("Interruptor Termomagnético General", "Caja moldeada 3x160 A, regulación térmica 0.8-1.0 In, poder de corte Icu = 25 kA a 380 V."),
        ("Interruptores de Circuitos C-1 y C-2", "Caja moldeada 3x80 A regulable (C-1 a 100A, C-2 a 63A), curva C, Icu = 18 kA a 380 V."),
        ("Circuito de Alumbrado Público", "ITM bipolar 2x16 A (6 kA), contactor modular 25 A AC-1, relé crepuscular de 1000 W."),
        ("Sistema de Puesta a Tierra PAT-3", "02 electrodos verticales Cu 5/8\"x2.40m en paralelo, cable Cu 35 mm². R <= 10 Ω."),
        ("Gabinete de Distribución BT", "Poliéster reforzado con fibra de vidrio (PRFV), IP65, cerradura tipo falleba.")
    ]
    y_esp = 0.890
    for eq, desc in especs:
        ax_esp.text(0.04, y_esp, f"• {eq}:", fontsize=5.8, fontweight='bold', color='#B45309')
        ax_esp.text(0.06, y_esp - 0.038, desc, fontsize=5.2, color='#0F172A')
        y_esp -= 0.106

    # Rótulo Oficial de Ingeniería Lámina U-01
    dibujar_rotulo_cad(fig.add_axes([0.60, 0.05, 0.37, 0.29]), 0, 0, 1, 1,
                       plano_cod="U-01",
                       plano_nom_l1="DIAGRAMA UNIFILAR GENERAL Y ESQUEMA DE",
                       plano_nom_l2="PROTECCIONES BT (2 CIRCUITOS + AP)",
                       escala="INDICADA")

    fig.savefig(salida_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"Lámina U-01 generada exitosamente en: {salida_pdf}")


if __name__ == "__main__":
    out_dir = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\entregables\planos"
    os.makedirs(out_dir, exist_ok=True)
    
    p01 = os.path.join(out_dir, "plano_P01_redes_planta.pdf")
    u01 = os.path.join(out_dir, "plano_U01_diagrama_unifilar_detalles.pdf")
    
    generar_plano_p01_profesional(p01)
    generar_plano_u01_profesional(u01)
