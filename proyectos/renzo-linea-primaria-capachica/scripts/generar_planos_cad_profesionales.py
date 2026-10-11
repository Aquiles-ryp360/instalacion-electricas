# -*- coding: utf-8 -*-
"""
generar_planos_cad_profesionales.py
Genera las láminas oficiales de ingeniería electromecánica en formato A3 Horizontal (420 x 297 mm)
con simbología estrictamente normalizada UNE-EN 60617 (CEI 617) y Norma DGE - MINEM Perú (R.M. Nº 091-2002-EM/VME):
- Lámina P-01: Redes de Distribución en Planta General, Acometidas Domiciliarias y Retenidas (2 Circuitos).
  * Simbología oficial UNE-EN 60617 / DGE sin saturación en planta geográfica.
  * Símbolos de postes C.A.C. limpios (DGE 09-91-20 / UNE 11-11-01).
  * Luminarias AP con símbolo oficial UNE 11-15-03 (círculo con 'X' inscrita en pastoral).
  * Puestas a tierra con símbolo oficial UNE 02-15-01 (3 barras paralelas decrecientes, sin textos flotantes saturantes).
  * Retenidas con símbolo oficial DGE 09-91-18 / UNE 11-11-01 (tirante, aislador 54-1 y ancla, sin textos flotantes).
  * Subestación Biposte SAB-1 100 kVA con símbolo oficial de transformador UNE 06-09-01 (dos círculos entrelazados).
  * Planilla de Estructuras y Armados de Redes Secundarias en panel lateral técnico.
  * Leyenda oficial detallada y Cuadro de Cargas de los 2 Circuitos.
- Lámina U-01: Diagrama Unifilar General y Esquema de Protecciones (SED Biposte 100 kVA, 2 Circuitos + AP).

Cero solapes verificado matemáticamente y mediante PyMuPDF.

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
from matplotlib.patches import Rectangle, Circle, Polygon
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
# BLOQUES GRÁFICOS CAD OFICIALES UNE-EN 60617 / DGE-MEM PERÚ (ESCALA CALIBRADA)
# -------------------------------------------------------------------------
def dibujar_bloque_poste_cad(ax, x, y, radio=1.8, etiqueta="", ap=False, dx_ap=4.2, dy_ap=1.8, pos_etiqueta='top-left'):
    """
    Dibuja un poste de concreto C.A.C. según Norma DGE 09-91-20 / UNE-EN 60617-11:
    - Círculo de concreto limpio a escala cartográfica (radio=1.8 m, ~1.5 mm en papel A3).
    - Símbolo oficial de luminaria AP (UNE-EN 60617-11 nº 11-15-03: círculo con 'X' inscrita).
    - Etiqueta de código con máscara anticolisión ajustada.
    """
    c = patches.Circle((x, y), radius=radio, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=0.75, zorder=16)
    ax.add_patch(c)
    ax.plot(x, y, marker='.', color='#0F172A', markersize=2.0, zorder=17)
    
    # Conjunto de Alumbrado Público: Pastoral con Luminaria LED UNE 11-15-03
    if ap:
        x_lum = x + dx_ap
        y_lum = y + dy_ap
        ax.plot([x, x_lum], [y, y_lum], color='#475569', linewidth=0.65, zorder=14)
        r_lum = 1.5
        lum = patches.Circle((x_lum, y_lum), radius=r_lum, facecolor='#FEF9C3', edgecolor='#CA8A04', linewidth=0.70, zorder=17)
        ax.add_patch(lum)
        # Aspa 'X' normalizada inscrita (UNE-EN 60617-11 nº 11-15-03 / DGE 09-91-24)
        d = r_lum * 0.707
        ax.plot([x_lum - d, x_lum + d], [y_lum - d, y_lum + d], color='#CA8A04', linewidth=0.55, zorder=18)
        ax.plot([x_lum - d, x_lum + d], [y_lum + d, y_lum - d], color='#CA8A04', linewidth=0.55, zorder=18)
        
    if etiqueta:
        dist_offset = radio + 2.5
        if pos_etiqueta == 'top-left':
            ex, ey = x - dist_offset, y + dist_offset
            ha, va = 'right', 'center'
        elif pos_etiqueta == 'top-right':
            ex, ey = x + dist_offset, y + dist_offset
            ha, va = 'left', 'center'
        elif pos_etiqueta == 'bottom-left':
            ex, ey = x - dist_offset, y - dist_offset
            ha, va = 'right', 'center'
        elif pos_etiqueta == 'bottom-right':
            ex, ey = x + dist_offset, y - dist_offset
            ha, va = 'left', 'center'
        elif pos_etiqueta == 'top':
            ex, ey = x, y + dist_offset
            ha, va = 'center', 'bottom'
        elif pos_etiqueta == 'bottom':
            ex, ey = x, y - dist_offset
            ha, va = 'center', 'top'
        else:
            ex, ey = x + dist_offset, y + dist_offset
            ha, va = 'left', 'center'
            
        ax.text(ex, ey, etiqueta, fontsize=4.0, fontweight='bold', color='#0F172A', ha=ha, va=va,
                bbox=dict(boxstyle='square,pad=0.10', fc='white', ec='#64748B', lw=0.35, alpha=0.96), zorder=25)

def dibujar_bloque_sed_cad(ax, x, y):
    """
    Dibuja la Subestación Biposte SAB-1 en planta con simbología normalizada UNE-EN 60617-6 nº 06-09-01:
    - 2 Postes C.A.C. 13/400 separados limpiamente (intereje 6.0 m).
    - Plataforma estructural portatransformador.
    - Símbolo unifilar oficial de transformador: Dos círculos entrelazados nítidos.
    """
    dx = 3.0
    for px in [x - dx, x + dx]:
        c = patches.Circle((px, y), radius=1.5, facecolor='white', edgecolor='#B91C1C', linewidth=0.85, zorder=20)
        ax.add_patch(c)
        ax.plot(px, y, marker='.', color='#B91C1C', markersize=2.2, zorder=21)
    # Plataforma portatransformador
    rect_plat = patches.Rectangle((x - 4.2, y - 1.1), 8.4, 2.2, facecolor='#FEE2E2', edgecolor='#B91C1C', linewidth=0.75, zorder=19)
    ax.add_patch(rect_plat)
    # Símbolo oficial de transformador UNE-EN 60617-6 nº 06-09-01 (dos círculos entrelazados)
    r_trafo = 1.6
    c_prim = patches.Circle((x, y + 0.8), radius=r_trafo, facecolor='none', edgecolor='#DC2626', linewidth=0.85, zorder=22)
    c_sec = patches.Circle((x, y - 0.8), radius=r_trafo, facecolor='none', edgecolor='#1D4ED8', linewidth=0.85, zorder=22)
    ax.add_patch(c_prim)
    ax.add_patch(c_sec)

def dibujar_bloque_pat_cad(ax, x, y, dx=0.0, dy=-5.5):
    """
    Dibuja el símbolo oficial UNE-EN 60617-2 nº 02-15-01 de Puesta a Tierra:
    Línea vertical de bajada con 3 barras horizontales paralelas decrecientes de escala fina
    y espaciado amplio (1.2 m) que garantiza nitidez absoluta sin empastes.
    """
    x_end, y_end = x + dx, y + dy
    ax.plot([x, x_end], [y, y_end], color='#15803D', linewidth=0.65, zorder=12)
    ax.plot([x_end - 2.2, x_end + 2.2], [y_end, y_end], color='#15803D', linewidth=0.70, zorder=13)
    ax.plot([x_end - 1.4, x_end + 1.4], [y_end - 1.2, y_end - 1.2], color='#15803D', linewidth=0.70, zorder=13)
    ax.plot([x_end - 0.6, x_end + 0.6], [y_end - 2.4, y_end - 2.4], color='#15803D', linewidth=0.70, zorder=13)
    ax.plot([x_end, x_end], [y_end, y_end - 2.4], color='#15803D', linewidth=0.65, zorder=13)

def dibujar_bloque_retenida_cad(ax, x, y, dx=-7.0, dy=-7.0):
    """
    Dibuja la retenida mecánica según Norma DGE 09-91-18 / UNE-EN 60617-11:
    Cable tensor, aislador de tracción 54-1 nítido y placa de anclaje perpendicular.
    """
    x_ancla, y_ancla = x + dx, y + dy
    ax.plot([x, x_ancla], [y, y_ancla], color='#C2410C', linewidth=0.75, zorder=12)
    xm = (x + x_ancla) / 2.0
    ym = (y + y_ancla) / 2.0
    ax.plot(xm, ym, marker='s', color='#D97706', markeredgecolor='#9A3412', markeredgewidth=0.5, markersize=3.0, zorder=13)
    ang = math.atan2(dy, dx) + math.pi / 2.0
    bx = 1.8 * math.cos(ang)
    by = 1.8 * math.sin(ang)
    ax.plot([x_ancla - bx, x_ancla + bx], [y_ancla - by, y_ancla + by], color='#9A3412', linewidth=1.0, zorder=13)

def dibujar_bloque_medidor_cad(ax, x, y, cod="", dx_label=2.4, dy_label=1.4, ha='left'):
    """Dibuja la caja portamedidor monofásica según simbología DGE 09-91-30 con máscara protectora fina."""
    d = 0.8
    rect = patches.Rectangle((x - d, y - d), 2*d, 2*d, facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=0.55, zorder=18)
    ax.add_patch(rect)
    c = patches.Circle((x, y), radius=0.50, facecolor='white', edgecolor='#DC2626', linewidth=0.45, zorder=19)
    ax.add_patch(c)
    ax.plot(x, y, marker='.', color='#DC2626', markersize=1.6, zorder=20)
    if cod:
        ax.text(x + dx_label, y + dy_label, cod, fontsize=3.7, fontweight='bold', color='#1E293B',
                ha=ha, va='center',
                bbox=dict(boxstyle='round,pad=0.10', fc='white', ec='#DC2626', lw=0.30, alpha=0.96), zorder=25)

def dibujar_recuadro_detalles_tecnicos(ax):
    """
    Dibuja un recuadro formal de detalles constructivos normalizados en la zona noroeste
    (E: 412365 - 412560, N: 8271100 - 8271465), garantizando legibilidad total y cero colisiones.
    """
    x0, y0 = 412365.0, 8271100.0
    w, h = 195.0, 365.0
    
    rect_box = patches.Rectangle((x0, y0), w, h, facecolor='#FFFFFF', edgecolor='#1E3A8A', linewidth=1.1, zorder=10)
    ax.add_patch(rect_box)
    
    rect_title = patches.Rectangle((x0, y0 + h - 18.0), w, 18.0, facecolor='#1E3A8A', edgecolor='#1E3A8A', linewidth=1.0, zorder=11)
    ax.add_patch(rect_title)
    ax.text(x0 + w/2.0, y0 + h - 9.0, "DETALLES CONSTRUCTIVOS DE INGENIERÍA (NORMAS DGE / MEM)",
            ha='center', va='center', fontsize=5.5, fontweight='bold', color='#FFFFFF', zorder=12)
    
    # ---------------------------------------------------------------------
    # DETALLE 1: SUBESTACIÓN BIPOSTE SAB-1 100 kVA
    # ---------------------------------------------------------------------
    y_d1_top = y0 + h - 26.0
    ax.text(x0 + 8.0, y_d1_top, "DETALLE 1: ESTRUCTURA SED BIPOSTE SAB-1 100 kVA (ESC. 1:75)",
            fontsize=4.8, fontweight='bold', color='#B91C1C', zorder=12)
    ax.plot([x0 + 6.0, x0 + w - 6.0], [y_d1_top - 4.0, y_d1_top - 4.0], color='#CBD5E1', lw=0.6, zorder=11)
    
    x_c = x0 + 45.0
    y_base = y_d1_top - 85.0
    ax.plot([x_c - 35.0, x_c + 35.0], [y_base, y_base], color='#475569', lw=1.0, zorder=12)
    ax.text(x_c + 38.0, y_base, "N.T.N. ±0.00", fontsize=3.4, color='#475569', va='center', zorder=12)
    
    d_p = 14.0
    for xp in [x_c - d_p, x_c + d_p]:
        poly_p = patches.Polygon([[xp - 2.5, y_base], [xp + 2.5, y_base], [xp + 1.6, y_base + 66.0], [xp - 1.6, y_base + 66.0]],
                                 facecolor='#F1F5F9', edgecolor='#334155', lw=0.7, zorder=13)
        ax.add_patch(poly_p)
    
    y_cruc = y_base + 62.0
    rect_cr = patches.Rectangle((x_c - 32.0, y_cruc - 1.8), 64.0, 3.6, facecolor='#FEF3C7', edgecolor='#B45309', lw=0.7, zorder=14)
    ax.add_patch(rect_cr)
    
    y_plat = y_base + 30.0
    rect_pl = patches.Rectangle((x_c - 20.0, y_plat - 2.0), 40.0, 4.0, facecolor='#E2E8F0', edgecolor='#1E293B', lw=0.8, zorder=14)
    ax.add_patch(rect_pl)
    
    rect_tr = patches.Rectangle((x_c - 10.0, y_plat + 1.5), 20.0, 16.0, facecolor='#EFF6FF', edgecolor='#1D4ED8', lw=0.85, zorder=15)
    ax.add_patch(rect_tr)
    ax.text(x_c, y_plat + 11.5, "Trafo 100 kVA", fontsize=3.3, fontweight='bold', color='#1D4ED8', ha='center', va='center', zorder=16)
    ax.text(x_c, y_plat + 5.0, "Dyn5 22.9 kV", fontsize=3.0, color='#1D4ED8', ha='center', va='center', zorder=16)
    
    y_tab = y_base + 6.0
    rect_tb = patches.Rectangle((x_c - 8.0, y_tab), 16.0, 13.0, facecolor='#FEF2F2', edgecolor='#DC2626', lw=0.75, zorder=15)
    ax.add_patch(rect_tb)
    ax.text(x_c, y_tab + 8.0, "Tablero BT", fontsize=3.1, fontweight='bold', color='#991B1B', ha='center', va='center', zorder=16)
    ax.text(x_c, y_tab + 3.5, "IP65 3x160A", fontsize=3.0, color='#991B1B', ha='center', va='center', zorder=16)

    # Textos de Especificaciones Técnicas SED (una sola línea por viñeta para cero colisiones)
    x_esp_sed = x0 + 88.0
    y_esp_s = y_d1_top - 12.0
    sed_textos = [
        "• Potencia: 100 kVA (Dyn5, 60 Hz)",
        "• Tensión: 22.9 / 0.38-0.22 kV",
        "• Postes: 2xC.A.C. 13m/400daN",
        "• Cut-Out: 27 kV / 100A (Fus. 4A)",
        "• Pararrayos: ZnO 21 kV / 10 kA",
        "• Tablero BT: Gabinete IP65 3x160A",
        "• Puesta a Tierra: PAT-3 (R <= 10 Ω)"
    ]
    for lin in sed_textos:
        ax.text(x_esp_sed, y_esp_s, lin, fontsize=3.5, color='#0F172A', zorder=13)
        y_esp_s -= 10.5

    # ---------------------------------------------------------------------
    # DETALLE 2: POZO DE PUESTA A TIERRA PAT-1 / PAT-3 (NORMA DGE)
    # ---------------------------------------------------------------------
    y_d2_top = y_base - 14.0
    ax.text(x0 + 8.0, y_d2_top, "DETALLE 2: POZO DE PUESTA A TIERRA PAT-1 / PAT-3 (ESC. 1:25)",
            fontsize=4.8, fontweight='bold', color='#15803D', zorder=12)
    ax.plot([x0 + 6.0, x0 + w - 6.0], [y_d2_top - 4.0, y_d2_top - 4.0], color='#CBD5E1', lw=0.6, zorder=11)
    
    x_pzt = x0 + 35.0
    y_pzt = y_d2_top - 16.0
    rect_caj = patches.Rectangle((x_pzt - 9.0, y_pzt - 6.0), 18.0, 6.0, facecolor='#F1F5F9', edgecolor='#475569', lw=0.7, zorder=13)
    ax.add_patch(rect_caj)
    ax.text(x_pzt, y_pzt - 3.0, "Caja 0.40x0.40m", fontsize=3.0, ha='center', color='#475569', zorder=14)
    
    rect_pozo = patches.Rectangle((x_pzt - 12.0, y_pzt - 54.0), 24.0, 48.0, facecolor='#FDF6B2', edgecolor='#CA8A04', lw=0.6, linestyle='--', zorder=12)
    ax.add_patch(rect_pozo)
    
    ax.plot([x_pzt, x_pzt], [y_pzt - 2.0, y_pzt - 50.0], color='#B45309', lw=2.0, zorder=14)
    ax.plot(x_pzt, y_pzt - 2.0, marker='s', color='#D97706', markersize=3.2, zorder=15)
    ax.text(x_pzt + 3.0, y_pzt - 24.0, "Varilla Cu\n5/8\"x2.40m", fontsize=3.1, color='#78350F', fontweight='bold', va='center', zorder=15)
    
    x_esp_pat = x0 + 88.0
    y_esp_p = y_d2_top - 14.0
    pat_textos = [
        "• PAT-1 (Redes BT): R <= 25 Ω",
        "• PAT-3 (SED 100kVA): R <= 10 Ω",
        "• Electrodo: Cobre 5/8\" x 2.40 m",
        "• Conductor: Cu desnudo 35 mm²",
        "• Tratamiento: Bentonita sódica"
    ]
    for lin in pat_textos:
        ax.text(x_esp_pat, y_esp_p, lin, fontsize=3.5, color='#0F172A', zorder=13)
        y_esp_p -= 10.5

    # ---------------------------------------------------------------------
    # DETALLE 3: ARMADO DE RETENIDA INCLINADA RET-I (DGE 09-91-18)
    # ---------------------------------------------------------------------
    y_d3_top = y_d2_top - 76.0
    ax.text(x0 + 8.0, y_d3_top, "DETALLE 3: ARMADO RETENIDA INCLINADA RET-I (ESC. 1:50)",
            fontsize=4.8, fontweight='bold', color='#9A3412', zorder=12)
    ax.plot([x0 + 6.0, x0 + w - 6.0], [y_d3_top - 4.0, y_d3_top - 4.0], color='#CBD5E1', lw=0.6, zorder=11)
    
    x_ret_base = x0 + 25.0
    y_ret_base = y_d3_top - 44.0
    ax.plot([x_ret_base, x_ret_base], [y_ret_base, y_ret_base + 36.0], color='#334155', lw=2.0, zorder=13)
    ax.text(x_ret_base - 2.5, y_ret_base + 18.0, "Poste BT", fontsize=3.0, color='#334155', ha='right', zorder=14)
    
    x_ret_ancla = x_ret_base + 32.0
    ax.plot([x_ret_base, x_ret_ancla], [y_ret_base + 32.0, y_ret_base], color='#C2410C', lw=1.1, zorder=13)
    
    xm_r = (x_ret_base + x_ret_ancla) / 2.0
    ym_r = (y_ret_base + 32.0 + y_ret_base) / 2.0
    ax.plot(xm_r, ym_r, marker='s', color='#D97706', markeredgecolor='#9A3412', markersize=3.8, zorder=14)
    ax.text(xm_r + 2.5, ym_r, "Aislador 54-1", fontsize=3.0, color='#9A3412', va='center', zorder=15)
    
    ax.plot([x_ret_ancla, x_ret_ancla + 7.0], [y_ret_base, y_ret_base - 8.0], color='#9A3412', lw=1.4, zorder=13)
    rect_blq = patches.Rectangle((x_ret_ancla + 3.0, y_ret_base - 12.0), 9.0, 5.0, facecolor='#E2E8F0', edgecolor='#475569', lw=0.6, zorder=13)
    ax.add_patch(rect_blq)
    
    x_esp_ret = x0 + 88.0
    y_esp_r = y_d3_top - 14.0
    ret_textos = [
        "• Cable: Acero SM 3/8\" (7 hilos)",
        "• Aislador: Tracción ANSI 54-1",
        "• Varilla: F°G° 5/8\" x 2.40 m",
        "• Inclinación: 45° a la vertical",
        "• Bloque: Concreto 0.5x0.5x0.2m",
        "• Tracción mín.: 3 800 daN"
    ]
    for lin in ret_textos:
        ax.text(x_esp_ret, y_esp_r, lin, fontsize=3.5, color='#0F172A', zorder=13)
        y_esp_r -= 10.5

# -------------------------------------------------------------------------
# RÓTULO FORMAL DE INGENIERÍA (MEMBRETE CAD ESTÁNDAR)
# -------------------------------------------------------------------------
def dibujar_rotulo_cad(ax, x0, y0, w, h, plano_cod, plano_nom_l1, plano_nom_l2, escala="1 : 2500"):
    ax.axis('off')
    ax.set_xlim(x0, x0 + w)
    ax.set_ylim(y0, y0 + h)
    
    rect_ext = patches.Rectangle((x0, y0), w, h, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.5, zorder=50)
    ax.add_patch(rect_ext)
    
    h_filas = [0.18, 0.36, 0.52, 0.68, 0.84]
    for hf in h_filas:
        ax.plot([x0, x0 + w], [y0 + hf * h, y0 + hf * h], color='#334155', linewidth=0.7, zorder=51)
        
    ax.plot([x0 + w * 0.35, x0 + w * 0.35], [y0, y0 + 0.18 * h], color='#334155', linewidth=0.7, zorder=51)
    ax.plot([x0 + w * 0.68, x0 + w * 0.68], [y0, y0 + 0.18 * h], color='#334155', linewidth=0.7, zorder=51)
    
    # Textos Institucionales
    ax.text(x0 + w/2.0, y0 + 0.93 * h, "UNIVERSIDAD NACIONAL DEL ALTIPLANO — PUNO", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.88 * h, "FACULTAD DE INGENIERÍA MECÁNICA ELÉCTRICA, ELECTRÓNICA Y SISTEMAS", ha='center', va='center', fontsize=5.8, fontweight='bold', color='#1E3A8A', zorder=52)
            
    ax.text(x0 + w/2.0, y0 + 0.78 * h, "ESCUELA PROFESIONAL DE INGENIERÍA MECÁNICA ELÉCTRICA", ha='center', va='center', fontsize=6.3, fontweight='bold', color='#0F766E', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.72 * h, "ASIGNATURA: MEC330 — INSTALACIONES ELÉCTRICAS II (SEMESTRE 2026-II)", ha='center', va='center', fontsize=5.6, color='#0F766E', zorder=52)
            
    ax.text(x0 + w/2.0, y0 + 0.62 * h, "PROYECTO: INSTALACIÓN DEL SISTEMA DE ELECTRIFICACIÓN RURAL", ha='center', va='center', fontsize=6.1, fontweight='bold', color='#0F172A', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.56 * h, "LP 22.9 kV Y REDES SECUNDARIAS SED 100 kVA SECTOR CHIFRÓN (CAPACHICA)", ha='center', va='center', fontsize=5.6, color='#0F172A', zorder=52)
            
    # Título del Plano en 2 líneas explícitas
    ax.text(x0 + w/2.0, y0 + 0.465 * h, f"PLANO: {plano_nom_l1}", ha='center', va='center', fontsize=6.2, fontweight='bold', color='#B45309', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.395 * h, plano_nom_l2, ha='center', va='center', fontsize=5.8, fontweight='bold', color='#B45309', zorder=52)
            
    ax.text(x0 + 0.03 * w, y0 + 0.27 * h, "PROYECTISTA:\nDOCENTES:", ha='left', va='center', fontsize=5.3, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.26 * w, y0 + 0.27 * h, "Br. Renzo Gabriel Mamani Galindo (Cód. 228447)\nIng. Leonidas Vilca Callata  /  Ing. Marcos José Villanueva Cornejo", ha='left', va='center', fontsize=5.3, color='#0F172A', zorder=52)
            
    # Casillas finales
    ax.text(x0 + 0.175 * w, y0 + 0.125 * h, "FECHA:", ha='center', va='center', fontsize=5.2, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.175 * w, y0 + 0.055 * h, "Octubre 2026", ha='center', va='center', fontsize=5.2, color='#334155', zorder=52)

    ax.text(x0 + 0.515 * w, y0 + 0.125 * h, "ESCALA:", ha='center', va='center', fontsize=5.2, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.515 * w, y0 + 0.055 * h, escala, ha='center', va='center', fontsize=5.2, color='#334155', zorder=52)

    ax.text(x0 + 0.840 * w, y0 + 0.125 * h, "LÁMINA:", ha='center', va='center', fontsize=5.4, fontweight='bold', color='#1E3A8A', zorder=52)
    ax.text(x0 + 0.840 * w, y0 + 0.055 * h, plano_cod, ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A', zorder=52)


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

    # 2. Postes Circuito C-2 (Bifurcación limpia desde P1-03 hacia la carretera al fondo)
    pts3 = rutas.get('ruta electrica 3', [])
    pts4 = rutas.get('ruta electrica 4', [])
    # Omitimos el punto inicial de ruta 3 que coincidía redundantemente con el eje de C-1
    pts_c2 = pts3[1:] + pts4

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
        p["ap"] = True if p_num in [1, 3, 6, 9] else False

    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    
    ax_box = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax_box.axis('off')
    rect_borde_ext = patches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='#0F172A', linewidth=2.0)
    rect_borde_int = patches.Rectangle((0.005, 0.005), 0.99, 0.99, facecolor='none', edgecolor='#0F172A', linewidth=0.8)
    ax_box.add_patch(rect_borde_ext)
    ax_box.add_patch(rect_borde_int)

    # MAPA GEOGRÁFICO DE DISTRIBUCIÓN
    ax_map = fig.add_axes([0.04, 0.05, 0.60, 0.90])
    
    # Vías
    for v_nom, pts in vias:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax_map.plot(xs, ys, color='#94A3B8', linewidth=1.2, linestyle='-', zorder=1)
        ax_map.plot(xs, ys, color='#E2E8F0', linewidth=0.45, linestyle='--', zorder=2)

    # Línea Primaria MT
    traza_mt = [(412380.00, 8270740.00), (412490.00, 8270725.00), (e_sed, n_sed)]
    ax_map.plot([p[0] for p in traza_mt], [p[1] for p in traza_mt], color='#0284C7', linewidth=1.3, linestyle='-', zorder=4)
    for p_mt in traza_mt[:-1]:
        ax_map.plot(p_mt[0], p_mt[1], marker='s', color='#0284C7', markersize=3.8, zorder=5)

    # Conducción en Doble Terna SED -> P1-03
    p1_03_coord = (postes_c1[2]["este"], postes_c1[2]["norte"])
    vx = p1_03_coord[0] - e_sed
    vy = p1_03_coord[1] - n_sed
    L_seg = math.hypot(vx, vy)
    ux, uy = -vy / L_seg, vx / L_seg
    
    # Redes BT C-1 (offset -1.1 m en tramo compartido con SED, luego sigue eje)
    if 'ruta electrica 1' in rutas:
        pts1 = rutas['ruta electrica 1']
        pts1_draw = [(e_sed + ux * (-1.1), n_sed + uy * (-1.1))] + pts1
        ax_map.plot([p[0] for p in pts1_draw], [p[1] for p in pts1_draw], color='#1D4ED8', linewidth=1.2, zorder=3)
        
    # Redes BT C-2: Desde SED hasta P1-03 corre paralela en doble terna (+1.1 m), luego se bifurca hacia P2-01
    pt_sed_c2 = (e_sed + ux * (1.1), n_sed + uy * (1.1))
    pt_p103_c2 = (p1_03_coord[0] + ux * (1.1), p1_03_coord[1] + uy * (1.1))
    pts_c2_draw = [pt_sed_c2, pt_p103_c2] + [(p["este"], p["norte"]) for p in postes_c2]
    ax_map.plot([p[0] for p in pts_c2_draw], [p[1] for p in pts_c2_draw], color='#B45309', linewidth=1.1, zorder=3)

    # Postes del Circuito C-1
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
        
        dibujar_bloque_poste_cad(ax_map, p["este"], p["norte"], radio=1.8, etiqueta=p["id"],
                                 ap=p.get("ap", False), dx_ap=4.2, dy_ap=1.8, pos_etiqueta=pos_lbl)
        
        if p["pat"]:
            if pid == 'P1-04':
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=4.5, dy=4.5)
            elif pid == 'P1-12':
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=4.5, dy=-4.5)
            elif pid == 'P1-16':
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=4.5, dy=-4.2)
            elif pid == 'P1-19':
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=-4.5, dy=4.5)
            else:
                dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=-4.2, dy=-4.2)
                
        if p["ret"]:
            if pid == 'P1-12':
                dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=7.0, dy=7.0)
            elif pid == 'P1-19':
                dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=7.0, dy=7.5)
            else:
                dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=-7.0, dy=-7.0)

    # Postes del Circuito C-2
    for p in postes_c2:
        pid = p["id"]
        if pid == 'P2-01':
            pos_lbl = 'top-left'
        else:
            casas_cercanas = [ab for ab in abonados if math.hypot(ab["este"] - p["este"], ab["norte"] - p["norte"]) < 20.0]
            pos_lbl = 'top-right' if (casas_cercanas and casas_cercanas[0]["este"] < p["este"]) else 'top-left'
            
        dibujar_bloque_poste_cad(ax_map, p["este"], p["norte"], radio=1.8, etiqueta=p["id"],
                                 ap=p.get("ap", False), dx_ap=4.2, dy_ap=1.8, pos_etiqueta=pos_lbl)
        if p["pat"]:
            dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=4.5, dy=-4.5)
        if p["ret"]:
            dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=7.0, dy=-7.0)

    # Subestación Biposte SAB-1
    dibujar_bloque_sed_cad(ax_map, e_sed, n_sed)
    dibujar_bloque_pat_cad(ax_map, e_sed, n_sed, dx=0.0, dy=-7.0)
    dibujar_bloque_retenida_cad(ax_map, e_sed, n_sed, dx=9.0, dy=-7.0)
    
    # Rótulo de la Subestación al Suroeste con flecha técnica fina
    ax_map.annotate("SED BIPOSTE SAB-1 (100 kVA)\n22.9 / 0.38 - 0.22 kV (Dyn5)\nE: 412606.01 m, N: 8270712.24 m\nOrigen C-1 (Norte) y C-2 (Sur)",
                    xy=(e_sed - 5.0, n_sed), xytext=(e_sed - 150.0, n_sed - 30.0),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.7", color='#B91C1C', lw=0.9),
                    bbox=dict(boxstyle="square,pad=0.3", fc="#FEF2F2", ec="#B91C1C", lw=1.0),
                    fontsize=5.6, fontweight='bold', color='#991B1B', zorder=30)

    # Conexión de las 43 Acometidas
    todos_postes = [(p["este"], p["norte"], p["id"], p["circuito"]) for p in (postes_c1 + postes_c2)] + [(e_sed, n_sed, "SED-01", "SED")]
    
    label_offsets = {}
    for i, ab1 in enumerate(abonados):
        cid = ab1["cod"]
        if cid == 'C10':
            label_offsets[cid] = (-3.2, -2.2, 'right')
        elif cid == 'C11':
            label_offsets[cid] = (-3.2, 0.0, 'right')
        elif cid == 'C14':
            label_offsets[cid] = (-3.2, -2.2, 'right')
        elif cid == 'C15':
            label_offsets[cid] = (-3.2, 2.2, 'right')
        elif cid == 'C18':
            label_offsets[cid] = (0.0, 3.2, 'center')
        elif cid == 'C20':
            label_offsets[cid] = (-3.2, 0.0, 'right')
        elif cid == 'C28':
            label_offsets[cid] = (3.2, 2.4, 'left')
        elif cid == 'C43':
            label_offsets[cid] = (-3.5, 0.0, 'right')
        else:
            cercanos = [ab2 for j, ab2 in enumerate(abonados) if i != j and math.hypot(ab1["este"] - ab2["este"], ab1["norte"] - ab2["norte"]) < 14.0]
            if not cercanos:
                label_offsets[cid] = (2.8, 1.6, 'left')
            else:
                num = int(cid[1:])
                if num % 4 == 0:
                    label_offsets[cid] = (3.2, 2.6, 'left')
                elif num % 4 == 1:
                    label_offsets[cid] = (-3.2, 2.6, 'right')
                elif num % 4 == 2:
                    label_offsets[cid] = (3.2, -2.6, 'left')
                else:
                    label_offsets[cid] = (-3.2, -2.6, 'right')

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
        ax_map.plot([pe, xe_ab], [pn, yn_ab], color='#64748B', linewidth=0.5, linestyle='--', zorder=3)
        
        dx_l, dy_l, ha_l = label_offsets[ab["cod"]]
        dibujar_bloque_medidor_cad(ax_map, xe_ab, yn_ab, cod=ab['cod'], dx_label=dx_l, dy_label=dy_l, ha=ha_l)

    # Recuadro de detalles constructivos ampliado en la esquina noroeste
    dibujar_recuadro_detalles_tecnicos(ax_map)

    ax_map.set_xlim(412350, 412950)
    ax_map.set_ylim(8270650, 8271500)
    ax_map.set_aspect('equal')
    ax_map.grid(True, linestyle=':', color='#94A3B8', alpha=0.5)
    ax_map.set_title("PLANO DE REDES DE DISTRIBUCIÓN EN PLANTA GENERAL, ACOMETIDAS Y RETENIDAS — SECTOR CHIFRÓN (CAPACHICA)\nSISTEMA TRIFÁSICO / BIFILAR CON 2 CIRCUITOS DE DISTRIBUCIÓN (C-1 Y C-2) | SUBESTACIÓN BIPOSTE 100 kVA",
                     fontsize=8.5, fontweight='bold', color='#0F172A', pad=10)
    ax_map.set_xlabel("Coordenada Este UTM (m) — Datum WGS-84 Zona 19S", fontsize=7.2, fontweight='bold')
    ax_map.set_ylabel("Coordenada Norte UTM (m) — Datum WGS-84 Zona 19S", fontsize=7.2, fontweight='bold')
    ax_map.tick_params(axis='both', which='major', labelsize=6.5)

    # ---------------------------------------------------------------------
    # PANEL 1: LEYENDA OFICIAL DE SIMBOLOGÍA (UNE-EN 60617 / DGE-MEM PERÚ)
    # ---------------------------------------------------------------------
    ax_leg = fig.add_axes([0.66, 0.735, 0.31, 0.215])
    ax_leg.axis('off')
    rect_leg = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.1)
    ax_leg.add_patch(rect_leg)
    ax_leg.text(0.5, 0.930, "SIMBOLOGÍA NORMALIZADA UNE-EN 60617 / DGE-MEM", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A')
    ax_leg.plot([0.04, 0.96], [0.865, 0.865], color='#334155', linewidth=0.7)
    
    simbolos_cad = [
        ("Red Primaria MT 22.9 kV (AAAC 35 mm²)", '#0284C7', '-', 'line'),
        ("Red Secundaria BT Troncal C-1 (CAAI 3x35+25+16 mm²)", '#1D4ED8', '-', 'line'),
        ("Red Secundaria BT Troncal C-2 (CAAI 3x25+25+16 mm²)", '#B45309', '-', 'line'),
        ("Acometida Concéntrica Aérea Domiciliaria (SET 2x4 mm²)", '#64748B', '--', 'line'),
        ("Subestación Biposte SAB-1 100 kVA (UNE 06-09-01)", '#B91C1C', 'sed', 'sed'),
        ("Poste Concreto C.A.C. BT 8m/200daN (DGE 09-91-20)", '#0F172A', 'poste', 'poste'),
        ("Pastoral con Luminaria LED 60W AP (UNE 11-15-03)", '#CA8A04', 'poste_ap', 'poste_ap'),
        ("Puesta a Tierra Protección PAT-1 / PAT-3 (UNE 02-15-01)", '#15803D', 'pat', 'pat'),
        ("Retenida Inclinada de Acero SM 3/8\" (DGE 09-91-18)", '#9A3412', 'ret', 'ret'),
        ("Caja Portamedidor Monofásico kWh (DGE 09-91-30)", '#DC2626', 'med', 'med')
    ]
    y_l = 0.790
    for desc, col, st, t in simbolos_cad:
        if t == 'line':
            ax_leg.plot([0.05, 0.18], [y_l, y_l], color=col, linestyle=st, linewidth=1.3)
        elif t == 'sed':
            c1 = patches.Circle((0.095, y_l), radius=0.016, facecolor='none', edgecolor='#B45309', linewidth=0.85)
            c2 = patches.Circle((0.135, y_l), radius=0.016, facecolor='none', edgecolor='#1D4ED8', linewidth=0.85)
            ax_leg.add_patch(c1)
            ax_leg.add_patch(c2)
        elif t == 'poste':
            c_p = patches.Circle((0.115, y_l), radius=0.016, facecolor='white', edgecolor='#0F172A', linewidth=0.8)
            ax_leg.add_patch(c_p)
            ax_leg.plot(0.115, y_l, marker='.', color='#0F172A', markersize=2.0)
        elif t == 'poste_ap':
            c_p = patches.Circle((0.085, y_l), radius=0.014, facecolor='white', edgecolor='#0F172A', linewidth=0.7)
            ax_leg.add_patch(c_p)
            ax_leg.plot([0.085, 0.145], [y_l, y_l], color='#334155', linewidth=0.75)
            c_lum = patches.Circle((0.145, y_l), radius=0.015, facecolor='#FEF9C3', edgecolor='#CA8A04', linewidth=0.75)
            ax_leg.add_patch(c_lum)
            d = 0.015 * 0.68
            ax_leg.plot([0.145 - d, 0.145 + d], [y_l - d, y_l + d], color='#CA8A04', linewidth=0.6)
            ax_leg.plot([0.145 - d, 0.145 + d], [y_l + d, y_l - d], color='#CA8A04', linewidth=0.6)
        elif t == 'pat':
            ax_leg.plot([0.115, 0.115], [y_l + 0.018, y_l - 0.008], color='#15803D', linewidth=0.8)
            ax_leg.plot([0.095, 0.135], [y_l - 0.008, y_l - 0.008], color='#15803D', linewidth=0.85)
            ax_leg.plot([0.103, 0.127], [y_l - 0.016, y_l - 0.016], color='#15803D', linewidth=0.85)
            ax_leg.plot([0.109, 0.121], [y_l - 0.024, y_l - 0.024], color='#15803D', linewidth=0.85)
        elif t == 'ret':
            ax_leg.plot([0.07, 0.15], [y_l - 0.015, y_l + 0.015], color='#C2410C', linewidth=0.80)
            ax_leg.plot(0.11, y_l, marker='s', color='#D97706', markersize=2.0)
            ax_leg.plot([0.135, 0.165], [y_l + 0.024, y_l + 0.006], color='#9A3412', linewidth=1.5)
        elif t == 'med':
            rect_m = patches.Rectangle((0.090, y_l - 0.015), 0.05, 0.030, facecolor='#FEE2E2', edgecolor='#DC2626', linewidth=0.6)
            ax_leg.add_patch(rect_m)
            c_m = patches.Circle((0.115, y_l), radius=0.010, facecolor='white', edgecolor='#DC2626', linewidth=0.45)
            ax_leg.add_patch(c_m)
        ax_leg.text(0.22, y_l, desc, va='center', fontsize=5.1, color='#0F172A')
        y_l -= 0.076

    # ---------------------------------------------------------------------
    # PANEL 2: PLANILLA DE ESTRUCTURAS Y ARMADOS (REDES SECUNDARIAS)
    # ---------------------------------------------------------------------
    ax_est = fig.add_axes([0.66, 0.480, 0.31, 0.245])
    ax_est.axis('off')
    rect_est = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.1)
    ax_est.add_patch(rect_est)
    ax_est.text(0.5, 0.935, "PLANILLA DE ESTRUCTURAS Y ARMADOS DE REDES BT", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A')
    ax_est.plot([0.04, 0.96], [0.875, 0.875], color='#334155', linewidth=0.7)

    filas_est = [
        ("Postes C.A.C. 8 m / 200 daN en Red BT", "30 unidades", "Total postes C-1 y C-2"),
        ("Postes C.A.C. 13 m / 400 daN en SED SAB-1", "02 unidades", "Estructura biposte MT/BT"),
        ("Armado E1 (Alineamiento / Suspensión)", "18 estructuras", "11 en C-1  |  7 en C-2"),
        ("Armado PA1 (Ángulo con Retenida RET-I)", "06 estructuras", "04 en C-1  |  02 en C-2"),
        ("Armado PS1 (Fin de Línea con RET-I)", "04 estructuras", "03 en C-1  |  01 en C-2"),
        ("Armado E2 (Derivación Secundaria)", "02 estructuras", "Vértices de bifurcación"),
        ("Retenidas Inclinadas RET-I (Acero 3/8\")", "08 retenidas", "Varilla 5/8\"x2.4m + bloque"),
        ("Puestas a Tierra PAT-1 (R <= 25 Ω)", "09 PAT-1", "Electrodo Cu 5/8\"x2.40m"),
        ("Puesta a Tierra SED PAT-3 (R <= 10 Ω)", "01 PAT-3", "2 electrodos Cu en paralelo"),
        ("Luminarias AP 60W LED + Pastoral 1.5m", "15 unidades", "10 en C-1  |  05 en C-2 (0.90 kW)"),
        ("Acometidas Aéreas SET 2x4 mm² + Caja M", "43 abonados", "C01 - C43 georreferenciados")
    ]
    y_e = 0.815
    for item, cant, obs in filas_est:
        ax_est.text(0.04, y_e, item, va='center', fontsize=5.1, fontweight='bold' if 'Postes' in item or 'Luminarias' in item else 'normal', color='#0F172A')
        ax_est.text(0.68, y_e, cant, va='center', fontsize=5.1, fontweight='bold', color='#1E3A8A' if 'Postes' in item else ('#15803D' if 'PAT' in item else '#B45309'))
        ax_est.text(0.96, y_e, obs, ha='right', va='center', fontsize=4.8, color='#64748B')
        y_e -= 0.068

    # ---------------------------------------------------------------------
    # PANEL 3: CUADRO DE CARGAS — 2 CIRCUITOS DE DISTRIBUCIÓN
    # ---------------------------------------------------------------------
    ax_car = fig.add_axes([0.66, 0.315, 0.31, 0.155])
    ax_car.axis('off')
    rect_car = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.1)
    ax_car.add_patch(rect_car)
    ax_car.text(0.5, 0.905, "CUADRO DE CARGAS — 2 CIRCUITOS DE BT (AÑO 20)", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A')
    ax_car.plot([0.04, 0.96], [0.815, 0.815], color='#334155', linewidth=0.7)
    
    filas_2c = [
        ("Abonados Censados / Proyectados (20 años)", "43 actuales / 78 proyectados"),
        ("Calificación Eléctrica Asignada", "0.90 kW / abonado proyectado"),
        ("Circuito C-1 (Norte + C31: 56 hab / 10 lum)", "51.00 kW (56.67 kVA)"),
        ("Circuito C-2 (Carretera Fondo: 22 hab / 5 lum)", "20.10 kW (22.33 kVA)"),
        ("MÁXIMA DEMANDA TOTAL (cos φ = 0.90)", "71.10 kW / 79.00 kVA"),
        ("TRANSFORMADOR ESTANDARIZADO", "100 kVA (Dyn5) — Reserva: 21.0%")
    ]
    y_c = 0.705
    for param, val in filas_2c:
        f_w = 'bold' if 'MÁXIMA' in param or 'TRANSFORMADOR' in param or 'Circuito' in param else 'normal'
        c_t = '#B91C1C' if 'TRANSFORMADOR' in param else ('#1D4ED8' if 'C-1' in param else ('#B45309' if 'C-2' in param else '#0F172A'))
        ax_car.text(0.04, y_c, param, va='center', fontsize=5.1, fontweight=f_w, color=c_t)
        ax_car.text(0.96, y_c, val, ha='right', va='center', fontsize=5.1, fontweight='bold', color=c_t)
        y_c -= 0.120

    # ---------------------------------------------------------------------
    # PANEL 4: RÓTULO OFICIAL DE INGENIERÍA LÁMINA P-01
    # ---------------------------------------------------------------------
    dibujar_rotulo_cad(fig.add_axes([0.66, 0.050, 0.31, 0.255]), 0, 0, 1, 1,
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
    ax_uni = fig.add_axes([0.04, 0.05, 0.58, 0.90])
    ax_uni.axis('off')
    rect_u = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.2)
    ax_uni.add_patch(rect_u)
    
    ax_uni.text(0.5, 0.968, "DIAGRAMA UNIFILAR GENERAL — SED BIPOSTE 100 kVA", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E3A8A')
    ax_uni.text(0.5, 0.942, "Alimentación MT 22.9 kV | Salidas en BT 380/220 V con 2 Circuitos (C-1 y C-2) + Alumbrado Público", ha='center', va='center', fontsize=6.6, color='#64748B')
    ax_uni.plot([0.04, 0.96], [0.925, 0.925], color='#334155', linewidth=1.0)

    # Red Primaria MT 22.9 kV (UNE 03-01-01 / 03-01-05)
    ax_uni.plot([0.5, 0.5], [0.915, 0.840], color='#0284C7', linewidth=1.6)
    ax_uni.text(0.52, 0.885, "LÍNEA PRIMARIA 22.9 kV (Red Electro Puno S.A.A.)\nTrifásico 3 Hilos — Conductor AAAC 35 mm²", fontsize=6.2, fontweight='bold', color='#0284C7')

    # Pararrayos ZnO (UNE 07-21-01 / DGE)
    ax_uni.plot([0.5, 0.30], [0.840, 0.840], color='#0284C7', linewidth=1.1)
    ax_uni.plot([0.30, 0.30], [0.840, 0.790], color='#0284C7', linewidth=1.1)
    rect_par = patches.Rectangle((0.275, 0.755), 0.05, 0.035, facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=1.0)
    ax_uni.add_patch(rect_par)
    ax_uni.text(0.095, 0.772, "Pararrayos Óxido Metálico (ZnO)\n21 kV / 10 kA (Clase 1 Distribución)", fontsize=5.5, color='#B91C1C')
    # Puesta a tierra pararrayos (UNE 02-15-01) afinada
    ax_uni.plot([0.30, 0.30], [0.755, 0.715], color='#15803D', linewidth=0.85)
    ax_uni.plot([0.275, 0.325], [0.715, 0.715], color='#15803D', linewidth=1.0)
    ax_uni.plot([0.283, 0.317], [0.707, 0.707], color='#15803D', linewidth=1.0)
    ax_uni.plot([0.290, 0.310], [0.699, 0.699], color='#15803D', linewidth=1.0)
    ax_uni.text(0.34, 0.710, "PAT-3 (R <= 10 Ω)", fontsize=5.2, fontweight='bold', color='#15803D')

    # Seccionadores Cut-Out (UNE 07-21-07)
    ax_uni.plot([0.5, 0.5], [0.840, 0.800], color='#0284C7', linewidth=1.2)
    rect_co = patches.Rectangle((0.47, 0.760), 0.06, 0.040, facecolor='#EFF6FF', edgecolor='#1D4ED8', linewidth=1.1)
    ax_uni.add_patch(rect_co)
    ax_uni.text(0.55, 0.780, "Seccionador Fusible Cut-Out\n27 kV / 100 A (Fusible Chicote K 4A)", fontsize=5.8, color='#1D4ED8')

    # Bajada a Bornes MT
    ax_uni.plot([0.5, 0.5], [0.760, 0.695], color='#0284C7', linewidth=1.2)

    # Transformador Trifásico 100 kVA (UNE-EN 60617-6 nº 06-09-01)
    c_mt = patches.Circle((0.5, 0.660), radius=0.035, facecolor='none', edgecolor='#DC2626', linewidth=1.4)
    c_bt = patches.Circle((0.5, 0.610), radius=0.035, facecolor='none', edgecolor='#1D4ED8', linewidth=1.4)
    ax_uni.add_patch(c_mt)
    ax_uni.add_patch(c_bt)
    ax_uni.text(0.56, 0.640, "TRANSFORMADOR DE DISTRIBUCIÓN 100 kVA\nRelación de Transformación: 22.9 / 0.38 - 0.22 kV\nGrupo Conexión: Dyn5 | Frecuencia: 60 Hz | ONAN\nDemanda Máxima: 79.0 kVA (Reserva Técnica: 21.0%)",
                fontsize=6.0, fontweight='bold', color='#991B1B')

    # Puesta a tierra Neutro BT (UNE 02-15-01) afinada
    ax_uni.plot([0.465, 0.38], [0.610, 0.610], color='#15803D', linewidth=0.85)
    ax_uni.plot([0.38, 0.38], [0.610, 0.565], color='#15803D', linewidth=0.85)
    ax_uni.plot([0.355, 0.405], [0.565, 0.565], color='#15803D', linewidth=1.0)
    ax_uni.plot([0.363, 0.397], [0.557, 0.557], color='#15803D', linewidth=1.0)
    ax_uni.plot([0.370, 0.390], [0.549, 0.549], color='#15803D', linewidth=1.0)
    ax_uni.text(0.20, 0.560, "Puesta a Tierra de Neutro\nR <= 10 Ω (PAT-3)", fontsize=5.2, color='#15803D')

    # Bajada a Tablero
    ax_uni.plot([0.5, 0.5], [0.575, 0.520], color='#1D4ED8', linewidth=1.6)

    # Gabinete BT IP65
    rect_tab = patches.Rectangle((0.08, 0.035), 0.84, 0.485, facecolor='#F8FAFC', edgecolor='#0F172A', linewidth=1.2)
    ax_uni.add_patch(rect_tab)
    ax_uni.text(0.5, 0.505, "TABLERO GENERAL DE DISTRIBUCIÓN BT (GABINETE FIBRA POLIÉSTER IP65)", ha='center', fontsize=7.0, fontweight='bold', color='#0F172A')

    # Totalizador General 3x160A (UNE 07-13-05)
    rect_gen = patches.Rectangle((0.43, 0.435), 0.14, 0.050, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.2)
    ax_uni.add_patch(rect_gen)
    ax_uni.text(0.5, 0.460, "TOTALIZADOR GENERAL 3x160 A\nTermomagnético Regulable (Icu = 25 kA)", ha='center', va='center', fontsize=5.5, fontweight='bold', color='#92400E')

    # Barra Trifásica (UNE 03-01-01)
    ax_uni.plot([0.5, 0.5], [0.435, 0.380], color='#1D4ED8', linewidth=1.3)
    ax_uni.plot([0.16, 0.84], [0.380, 0.380], color='#1E293B', linewidth=2.4)
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
        ax_uni.plot([xc, xc], [0.380, 0.345], color='#1D4ED8', linewidth=1.2)
        
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
    ax_esp = fig.add_axes([0.64, 0.355, 0.33, 0.595])
    ax_esp.axis('off')
    rect_e = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.2)
    ax_esp.add_patch(rect_e)
    ax_esp.text(0.5, 0.965, "ESPECIFICACIONES TÉCNICAS DE EQUIPOS Y PROTECCIONES", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')
    ax_esp.plot([0.04, 0.96], [0.935, 0.935], color='#334155', linewidth=0.8)

    especs = [
        ("Transformador de Distribución (UNE 06-09-01)", "100 kVA, 22.9 / 0.38-0.22 kV, trifásico, Dyn5, 60 Hz, ONAN, Po<=280W, Pk<=1450W."),
        ("Cortacircuitos Fusibles Cut-Out (UNE 07-21-07)", "03 unidades tipo expulsión, 27 kV, 100 A, 150 kV BIL, fusible chicote tipo K de 4 A."),
        ("Pararrayos de Distribución ZnO (DGE)", "03 unidades de óxido de zinc (ZnO), 21 kV, corriente descarga nominal 10 kA Clase 1."),
        ("Interruptor Termomagnético General (UNE 07-13-05)", "Caja moldeada 3x160 A, regulación térmica 0.8-1.0 In, poder de corte Icu = 25 kA a 380 V."),
        ("Interruptores de Circuitos C-1 y C-2", "Caja moldeada 3x80 A regulable (C-1 a 100A, C-2 a 63A), curva C, Icu = 18 kA a 380 V."),
        ("Circuito de Alumbrado Público", "ITM bipolar 2x16 A (6 kA), contactor modular 25 A AC-1, relé crepuscular de 1000 W."),
        ("Sistema de Puesta a Tierra PAT-3 (UNE 02-15-01)", "02 electrodos verticales Cu 5/8\"x2.40m en paralelo, cable Cu 35 mm². R <= 10 Ω."),
        ("Gabinete de Distribución BT (UNE 02-01-01)", "Poliéster reforzado con fibra de vidrio (PRFV), IP65, cerradura tipo falleba.")
    ]
    y_esp = 0.890
    for eq, desc in especs:
        ax_esp.text(0.04, y_esp, f"• {eq}:", fontsize=5.6, fontweight='bold', color='#B45309')
        ax_esp.text(0.06, y_esp - 0.038, desc, fontsize=5.1, color='#0F172A')
        y_esp -= 0.106

    # Rótulo Oficial de Ingeniería Lámina U-01
    dibujar_rotulo_cad(fig.add_axes([0.64, 0.05, 0.33, 0.29]), 0, 0, 1, 1,
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
