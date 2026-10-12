# -*- coding: utf-8 -*-
"""
generar_planos_cad_profesionales.py
Generador Maestro de Láminas Oficiales de Ingeniería Electromecánica en Formato A3 Horizontal (420 x 297 mm):
- Lámina P-01:  Plano de Redes de Distribución en Planta General, Acometidas, Retenidas y Detalles DGE (Escala 1:2500)
- Lámina PL-01: Perfil Longitudinal Topográfico y Catenarias de la Línea Primaria 22.9 kV (H: 1/2000, V: 1/500)
- Lámina U-01:  Diagrama Unifilar General y Esquema de Protecciones (SED 100 kVA, 2 Circuitos + Alumbrado Público)

Simbología estrictamente normalizada UNE-EN 60617 y Norma DGE - MINEM Perú (R.M. Nº 091-2002-EM/VME).
Cero solapes, textos legibles en formato A3 ploteado, y alineación total con la Matriz Maestra de Datos de Ingeniería.

Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
Curso: MEC330 - Instalaciones Eléctricas II | FIME - UNA Puno
Docentes: Ing. Leonidas Vilca Callata / Ing. Marcos José Villanueva Cornejo
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
import ezdxf
from ezdxf import colors

# -------------------------------------------------------------------------
# CONSTANTES Y CONVERSIÓN DE COORDENADAS WGS-84 A UTM ZONA 19S
# -------------------------------------------------------------------------
def latlon_to_utm(lat, lon):
    a = 6378137.0
    f = 1 / 298.257223563
    b = a * (1 - f)
    e2 = (a**2 - b**2) / (a**2)
    e_prime2 = (a**2 - b**2) / (b**2)
    k0 = 0.9996
    lon0 = -69.0  # Meridiano central Zona 19S
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
# MATRIZ DE ESTRUCTURAS CANÓNICAS DE LA LÍNEA PRIMARIA MT (E-01 A E-09)
# -------------------------------------------------------------------------
POSTES_MT_CANONICOS = [
    {
        "id": "E-01", "prog": 0.00, "cota": 3924.17, "este": 412606.01, "norte": 8270712.24,
        "poste": "C.A.C. 12/400", "armado": "PR-1", "tipo": "Derivación MT (TAP)",
        "ang": 0.00, "ret": "Inclinada simple", "pat": "PAT-3",
        "desc": "Derivación Electro Puno (Cut-Out 27 kV + ZnO)"
    },
    {
        "id": "E-02", "prog": 105.00, "cota": 3895.00, "este": 412658.71, "norte": 8270803.07,
        "poste": "C.A.C. 12/300", "armado": "PS-1", "tipo": "Suspensión alineamiento",
        "ang": 0.00, "ret": "Ninguna", "pat": None,
        "desc": "Suspensión en ladera pronunciada"
    },
    {
        "id": "E-03", "prog": 210.00, "cota": 3865.00, "este": 412711.42, "norte": 8270893.91,
        "poste": "C.A.C. 12/300", "armado": "PS-1", "tipo": "Suspensión paso",
        "ang": 0.00, "ret": "Ninguna", "pat": None,
        "desc": "Suspensión paso hacia caserío"
    },
    {
        "id": "E-04", "prog": 305.21, "cota": 3839.56, "este": 412759.20, "norte": 8270976.22,
        "poste": "2xC.A.C. 13/400 (Biposte)", "armado": "SAB-1", "tipo": "SED Biposte 100 kVA",
        "ang": -35.20, "ret": "Contraviento doble", "pat": "PAT-3",
        "desc": "SED Biposte 100 kVA (22.9/0.38-0.22 kV Dyn5)"
    },
    {
        "id": "E-05", "prog": 402.43, "cota": 3817.04, "este": 412750.60, "norte": 8271073.06,
        "poste": "C.A.C. 12/400", "armado": "PA-1", "tipo": "Ángulo con retenida",
        "ang": -36.06, "ret": "Biselar simple", "pat": None,
        "desc": "Ángulo hacia camino secundario"
    },
    {
        "id": "E-06", "prog": 518.02, "cota": 3827.27, "este": 412684.34, "norte": 8271166.70,
        "poste": "C.A.C. 12/400", "armado": "PA-1", "tipo": "Ángulo vano crítico",
        "ang": 31.35, "ret": "Biselar simple", "pat": None,
        "desc": "Ángulo vano crítico 115.59m cruce camino"
    },
    {
        "id": "E-07", "prog": 628.53, "cota": 3824.61, "este": 412677.31, "norte": 8271272.50,
        "poste": "C.A.C. 12/300", "armado": "PS-1", "tipo": "Suspensión alineamiento",
        "ang": -6.05, "ret": "Ninguna", "pat": None,
        "desc": "Suspensión alineamiento tramo llano"
    },
    {
        "id": "E-08", "prog": 708.34, "cota": 3824.61, "este": 412646.16, "norte": 8271345.24,
        "poste": "C.A.C. 12/400", "armado": "PA-1", "tipo": "Ángulo reforzado",
        "ang": 32.95, "ret": "Biselar simple", "pat": None,
        "desc": "Ángulo reforzado acceso a playa"
    },
    {
        "id": "E-09", "prog": 816.60, "cota": 3824.61, "este": 412659.90, "norte": 8271446.51,
        "poste": "C.A.C. 12/400", "armado": "PR-1", "tipo": "Terminal de línea",
        "ang": 0.00, "ret": "Inclinada simple", "pat": "PAT-3",
        "desc": "Terminal de línea primaria fin de red"
    }
]

# -------------------------------------------------------------------------
# BLOQUES GRÁFICOS CAD OFICIALES UNE-EN 60617 / DGE-MEM PERÚ
# -------------------------------------------------------------------------
def dibujar_marco_a3_con_encabezado(fig, titulo_l1, titulo_l2):
    """
    Crea el marco exterior e interior normalizado A3 y una caja de título superior
    separada limpiamente del borde superior (mínimo 18 mm al borde).
    """
    ax_box = fig.add_axes([0.015, 0.015, 0.970, 0.970])
    ax_box.axis('off')
    
    # Bordes institucional FIME
    rect_ext = patches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='#0F172A', linewidth=2.0)
    rect_int = patches.Rectangle((0.005, 0.005), 0.990, 0.990, facecolor='none', edgecolor='#0F172A', linewidth=0.8)
    ax_box.add_patch(rect_ext)
    ax_box.add_patch(rect_int)

    # Franja superior de título (separada del borde superior)
    ax_head = fig.add_axes([0.025, 0.938, 0.950, 0.040])
    ax_head.axis('off')
    rect_head = patches.Rectangle((0, 0), 1, 1, facecolor='#F8FAFC', edgecolor='#1E3A8A', linewidth=1.1)
    ax_head.add_patch(rect_head)
    ax_head.text(0.5, 0.68, titulo_l1, ha='center', va='center', fontsize=9.2, fontweight='bold', color='#1E3A8A')
    ax_head.text(0.5, 0.28, titulo_l2, ha='center', va='center', fontsize=6.8, fontweight='bold', color='#334155')


def dibujar_rotulo_oficial_cad(ax, x0, y0, w, h, plano_cod, plano_nom_l1, plano_nom_l2, escala="1 : 2500"):
    """
    Dibuja el rótulo oficial de ingeniería conforme a normas DGE / UNA Puno.
    """
    ax.axis('off')
    ax.set_xlim(x0, x0 + w)
    ax.set_ylim(y0, y0 + h)
    
    rect_ext = patches.Rectangle((x0, y0), w, h, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.4, zorder=50)
    ax.add_patch(rect_ext)
    
    # Líneas divisorias horizontales
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
            
    # Título del Plano
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


def dibujar_bloque_poste_cad(ax, x, y, radio=1.8, etiqueta="", ap=False, dx_ap=4.2, dy_ap=1.8, pos_etiqueta='top-left', es_mt=False):
    """Dibuja un poste de concreto C.A.C. según Norma DGE 09-91-20 / UNE-EN 60617-11."""
    fc = '#E0F2FE' if es_mt else '#FFFFFF'
    ec = '#0284C7' if es_mt else '#0F172A'
    lw = 1.0 if es_mt else 0.75
    c = patches.Circle((x, y), radius=radio, facecolor=fc, edgecolor=ec, linewidth=lw, zorder=16)
    ax.add_patch(c)
    ax.plot(x, y, marker='.', color=ec, markersize=2.2, zorder=17)
    
    # Conjunto Pastoral + Luminaria LED UNE 11-15-03
    if ap:
        x_lum = x + dx_ap
        y_lum = y + dy_ap
        ax.plot([x, x_lum], [y, y_lum], color='#475569', linewidth=0.65, zorder=14)
        r_lum = 1.5
        lum = patches.Circle((x_lum, y_lum), radius=r_lum, facecolor='#FEF9C3', edgecolor='#CA8A04', linewidth=0.70, zorder=17)
        ax.add_patch(lum)
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
            
        color_lbl = '#0369A1' if es_mt else '#0F172A'
        border_lbl = '#0284C7' if es_mt else '#64748B'
        ax.text(ex, ey, etiqueta, fontsize=4.2, fontweight='bold', color=color_lbl, ha=ha, va=va,
                bbox=dict(boxstyle='square,pad=0.10', fc='white', ec=border_lbl, lw=0.40, alpha=0.96), zorder=25)


def dibujar_bloque_sed_cad(ax, x, y):
    """Dibuja la Subestación Biposte SAB-1 en planta según UNE-EN 60617-6 nº 06-09-01."""
    dx = 3.2
    for px in [x - dx, x + dx]:
        c = patches.Circle((px, y), radius=1.6, facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=0.95, zorder=20)
        ax.add_patch(c)
        ax.plot(px, y, marker='.', color='#DC2626', markersize=2.4, zorder=21)
    rect_plat = patches.Rectangle((x - 4.6, y - 1.2), 9.2, 2.4, facecolor='#FEE2E2', edgecolor='#B91C1C', linewidth=0.85, zorder=19)
    ax.add_patch(rect_plat)
    r_trafo = 1.8
    c_prim = patches.Circle((x, y + 0.9), radius=r_trafo, facecolor='none', edgecolor='#DC2626', linewidth=0.95, zorder=22)
    c_sec = patches.Circle((x, y - 0.9), radius=r_trafo, facecolor='none', edgecolor='#1D4ED8', linewidth=0.95, zorder=22)
    ax.add_patch(c_prim)
    ax.add_patch(c_sec)


def dibujar_bloque_pat_cad(ax, x, y, dx=0.0, dy=-5.5):
    """Dibuja el símbolo oficial UNE-EN 60617-2 nº 02-15-01 de Puesta a Tierra."""
    x_end, y_end = x + dx, y + dy
    ax.plot([x, x_end], [y, y_end], color='#15803D', linewidth=0.70, zorder=12)
    ax.plot([x_end - 2.2, x_end + 2.2], [y_end, y_end], color='#15803D', linewidth=0.75, zorder=13)
    ax.plot([x_end - 1.4, x_end + 1.4], [y_end - 1.2, y_end - 1.2], color='#15803D', linewidth=0.75, zorder=13)
    ax.plot([x_end - 0.6, x_end + 0.6], [y_end - 2.4, y_end - 2.4], color='#15803D', linewidth=0.75, zorder=13)
    ax.plot([x_end, x_end], [y_end, y_end - 2.4], color='#15803D', linewidth=0.70, zorder=13)


def dibujar_bloque_retenida_cad(ax, x, y, dx=-7.0, dy=-7.0):
    """Dibuja retenida mecánica según Norma DGE 09-91-18 / UNE-EN 60617-11."""
    x_ancla, y_ancla = x + dx, y + dy
    ax.plot([x, x_ancla], [y, y_ancla], color='#C2410C', linewidth=0.80, zorder=12)
    xm = (x + x_ancla) / 2.0
    ym = (y + y_ancla) / 2.0
    ax.plot(xm, ym, marker='s', color='#D97706', markeredgecolor='#9A3412', markeredgewidth=0.5, markersize=3.2, zorder=13)
    ang = math.atan2(dy, dx) + math.pi / 2.0
    bx = 1.8 * math.cos(ang)
    by = 1.8 * math.sin(ang)
    ax.plot([x_ancla - bx, x_ancla + bx], [y_ancla - by, y_ancla + by], color='#9A3412', linewidth=1.1, zorder=13)


def dibujar_bloque_medidor_cad(ax, x, y, cod="", dx_label=2.4, dy_label=1.4, ha='left'):
    """Dibuja caja portamedidor monofásica según simbología DGE 09-91-30."""
    d = 0.8
    rect = patches.Rectangle((x - d, y - d), 2*d, 2*d, facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=0.55, zorder=18)
    ax.add_patch(rect)
    c = patches.Circle((x, y), radius=0.50, facecolor='white', edgecolor='#DC2626', linewidth=0.45, zorder=19)
    ax.add_patch(c)
    ax.plot(x, y, marker='.', color='#DC2626', markersize=1.6, zorder=20)
    if cod:
        ax.text(x + dx_label, y + dy_label, cod, fontsize=3.8, fontweight='bold', color='#1E293B',
                ha=ha, va='center',
                bbox=dict(boxstyle='round,pad=0.10', fc='white', ec='#DC2626', lw=0.30, alpha=0.96), zorder=25)


# -------------------------------------------------------------------------
# RECUADRO DE DETALLES CONSTRUCTIVOS DGE (LÁMINA P-01)
# -------------------------------------------------------------------------
def dibujar_recuadro_detalles_tecnicos_p01(ax):
    """
    Dibuja un recuadro formal de detalles constructivos normalizados DGE/MEM en la zona
    noroeste libre (E: 412360 - 412595, N: 8271100 - 8271465).
    """
    x0, y0 = 412362.0, 8271100.0
    w, h = 232.0, 365.0
    
    rect_box = patches.Rectangle((x0, y0), w, h, facecolor='#FFFFFF', edgecolor='#1E3A8A', linewidth=1.2, zorder=10)
    ax.add_patch(rect_box)
    
    rect_title = patches.Rectangle((x0, y0 + h - 18.0), w, 18.0, facecolor='#1E3A8A', edgecolor='#1E3A8A', linewidth=1.0, zorder=11)
    ax.add_patch(rect_title)
    ax.text(x0 + w/2.0, y0 + h - 9.0, "DETALLES CONSTRUCTIVOS DE INGENIERÍA (NORMAS DGE / MEM)",
            ha='center', va='center', fontsize=5.3, fontweight='bold', color='#FFFFFF', zorder=12)
    
    # DETALLE 1: SUBESTACIÓN BIPOSTE SAB-1 100 kVA (ESC. 1:75)
    y_d1_top = y0 + h - 25.0
    ax.text(x0 + 8.0, y_d1_top, "DETALLE 1: ESTRUCTURA SED BIPOSTE SAB-1 100 kVA (ESC. 1:75)",
            fontsize=4.9, fontweight='bold', color='#B91C1C', zorder=12)
    ax.plot([x0 + 6.0, x0 + w - 6.0], [y_d1_top - 3.8, y_d1_top - 3.8], color='#CBD5E1', lw=0.6, zorder=11)
    
    x_c = x0 + 52.0
    y_base = y_d1_top - 84.0
    ax.plot([x_c - 42.0, x_c + 42.0], [y_base, y_base], color='#475569', lw=1.0, zorder=12)
    ax.text(x_c + 45.0, y_base, "N.T.N. ±0.00", fontsize=3.4, color='#475569', va='center', zorder=12)
    
    d_p = 16.0
    for xp in [x_c - d_p, x_c + d_p]:
        poly_p = patches.Polygon([[xp - 2.8, y_base], [xp + 2.8, y_base], [xp + 1.8, y_base + 66.0], [xp - 1.8, y_base + 66.0]],
                                 facecolor='#F1F5F9', edgecolor='#334155', lw=0.7, zorder=13)
        ax.add_patch(poly_p)
    ax.text(x_c - d_p - 4.5, y_base + 14.0, "C.A.C. 13/400", fontsize=3.2, color='#334155', ha='right', zorder=14)
    ax.text(x_c + d_p + 4.5, y_base + 14.0, "C.A.C. 13/400", fontsize=3.2, color='#334155', ha='left', zorder=14)
    
    y_cruc = y_base + 62.0
    rect_cr = patches.Rectangle((x_c - 36.0, y_cruc - 1.8), 72.0, 3.6, facecolor='#FEF3C7', edgecolor='#B45309', lw=0.7, zorder=14)
    ax.add_patch(rect_cr)
    ax.text(x_c, y_cruc + 4.2, "Cruceta F°G° 2.50 m\n(Cut-Out 27 kV + Pararrayos ZnO)",
            fontsize=3.1, fontweight='bold', color='#B45309', ha='center', va='bottom', linespacing=1.1, zorder=14)
    
    y_plat = y_base + 30.0
    rect_pl = patches.Rectangle((x_c - 24.0, y_plat - 2.0), 48.0, 4.0, facecolor='#E2E8F0', edgecolor='#1E293B', lw=0.8, zorder=14)
    ax.add_patch(rect_pl)
    
    rect_tr = patches.Rectangle((x_c - 13.0, y_plat + 2.0), 26.0, 18.0, facecolor='#EFF6FF', edgecolor='#1D4ED8', lw=0.85, zorder=15)
    ax.add_patch(rect_tr)
    ax.text(x_c, y_plat + 9.5, "Trafo 100 kVA\nDyn5  22.9/0.38 kV", fontsize=3.3, fontweight='bold', color='#1D4ED8', ha='center', va='center', linespacing=1.2, zorder=16)
    
    y_tab = y_base + 6.0
    rect_tb = patches.Rectangle((x_c - 11.0, y_tab), 22.0, 14.0, facecolor='#FEF2F2', edgecolor='#DC2626', lw=0.75, zorder=15)
    ax.add_patch(rect_tb)
    ax.text(x_c, y_tab + 7.0, "Tablero BT IP65\nITM Gen. 3x160A", fontsize=3.1, fontweight='bold', color='#991B1B', ha='center', va='center', linespacing=1.2, zorder=16)

    x_esp_sed = x0 + 108.0
    y_esp_s = y_d1_top - 12.0
    sed_textos = [
        "• Potencia: 100 kVA (Dyn5, 60 Hz)",
        "• Tensión: 22.9 / 0.38 - 0.22 kV",
        "• Estructura: 2 x C.A.C. 13m / 400 daN",
        "• Protección MT: Cut-Out 27 kV 100A (4A)",
        "• Pararrayos MT: ZnO 21 kV / 10 kA",
        "• Tablero BT: PRFV IP65 con ITM 3x160A",
        "• Puesta a Tierra: PAT-3 (R <= 10 Ω)"
    ]
    for lin in sed_textos:
        ax.text(x_esp_sed, y_esp_s, lin, fontsize=3.6, color='#0F172A', zorder=13)
        y_esp_s -= 10.5

    # DETALLE 2: POZO DE PUESTA A TIERRA PAT-1 / PAT-3 (ESC. 1:25)
    y_d2_top = y_base - 14.0
    ax.text(x0 + 8.0, y_d2_top, "DETALLE 2: POZO DE PUESTA A TIERRA PAT-1 / PAT-3 (ESC. 1:25)",
            fontsize=4.9, fontweight='bold', color='#15803D', zorder=12)
    ax.plot([x0 + 6.0, x0 + w - 6.0], [y_d2_top - 3.8, y_d2_top - 3.8], color='#CBD5E1', lw=0.6, zorder=11)
    
    x_pzt = x0 + 38.0
    y_pzt = y_d2_top - 16.0
    rect_caj = patches.Rectangle((x_pzt - 15.0, y_pzt - 3.0), 30.0, 7.5, facecolor='#F1F5F9', edgecolor='#475569', lw=0.7, zorder=13)
    ax.add_patch(rect_caj)
    ax.text(x_pzt, y_pzt + 0.8, "Caja Registro 0.40x0.40 m", fontsize=3.0, ha='center', va='center', color='#334155', fontweight='bold', zorder=14)
    
    rect_pozo = patches.Rectangle((x_pzt - 15.0, y_pzt - 54.0), 30.0, 48.0, facecolor='#FDF6B2', edgecolor='#CA8A04', lw=0.6, linestyle='--', zorder=12)
    ax.add_patch(rect_pozo)
    
    ax.plot([x_pzt, x_pzt], [y_pzt - 4.5, y_pzt - 50.0], color='#B45309', lw=2.2, zorder=14)
    ax.plot(x_pzt, y_pzt - 7.5, marker='s', color='#D97706', markersize=3.4, zorder=15)
    ax.text(x_pzt + 4.5, y_pzt - 7.5, "Conector Bronce", fontsize=3.0, color='#B45309', va='center', zorder=15)
    ax.text(x_pzt + 4.5, y_pzt - 26.0, "Varilla Cu\n5/8\" x 2.40 m", fontsize=3.1, color='#78350F', fontweight='bold', va='center', linespacing=1.1, zorder=15)
    ax.text(x_pzt, y_pzt - 47.0, "Bentonita Sódica", fontsize=3.0, ha='center', color='#854D0E', zorder=15)
    
    x_esp_pat = x0 + 108.0
    y_esp_p = y_d2_top - 14.0
    pat_textos = [
        "• PAT-1 (Redes Secundarias): R <= 25 Ω",
        "• PAT-3 (Neutro y Masa SED): R <= 10 Ω",
        "• Electrodo: Cobre Puro 5/8\" x 2.40 m",
        "• Conductor Enlace: Cu Desnudo 35 mm²",
        "• Tratamiento: Bentonita / Gel Electrolítico"
    ]
    for lin in pat_textos:
        ax.text(x_esp_pat, y_esp_p, lin, fontsize=3.6, color='#0F172A', zorder=13)
        y_esp_p -= 10.5

    # DETALLE 3: ARMADO DE RETENIDA INCLINADA Y BISELAR (ESC. 1:50)
    y_d3_top = y_d2_top - 76.0
    ax.text(x0 + 8.0, y_d3_top, "DETALLE 3: ARMADO RETENIDA INCLINADA Y BISELAR (ESC. 1:50)",
            fontsize=4.9, fontweight='bold', color='#9A3412', zorder=12)
    ax.plot([x0 + 6.0, x0 + w - 6.0], [y_d3_top - 3.8, y_d3_top - 3.8], color='#CBD5E1', lw=0.6, zorder=11)
    
    x_ret_base = x0 + 22.0
    y_ret_base = y_d3_top - 44.0
    ax.plot([x_ret_base, x_ret_base], [y_ret_base, y_ret_base + 36.0], color='#334155', lw=2.2, zorder=13)
    ax.text(x_ret_base - 3.0, y_ret_base + 18.0, "Poste C.A.C.", fontsize=3.2, color='#334155', ha='right', zorder=14)
    
    x_ret_ancla = x_ret_base + 26.0
    ax.plot([x_ret_base, x_ret_ancla], [y_ret_base + 32.0, y_ret_base], color='#C2410C', lw=1.2, zorder=13)
    
    xm_r = (x_ret_base + x_ret_ancla) / 2.0
    ym_r = (y_ret_base + 32.0 + y_ret_base) / 2.0
    ax.plot(xm_r, ym_r, marker='s', color='#D97706', markeredgecolor='#9A3412', markersize=3.8, zorder=14)
    ax.text(xm_r + 3.0, ym_r, "Aislador 54-1\n(H > 3.0 m)", fontsize=3.1, color='#9A3412', va='center', linespacing=1.1, zorder=15)
    
    ax.plot([x_ret_ancla, x_ret_ancla + 6.0], [y_ret_base, y_ret_base - 7.0], color='#9A3412', lw=1.5, zorder=13)
    rect_blq = patches.Rectangle((x_ret_ancla + 1.0, y_ret_base - 13.0), 14.0, 6.0, facecolor='#E2E8F0', edgecolor='#475569', lw=0.6, zorder=13)
    ax.add_patch(rect_blq)
    ax.text(x_ret_ancla + 8.0, y_ret_base - 17.0, "Bloque Concreto\n0.50x0.50x0.20 m", fontsize=3.0, color='#475569', ha='center', va='top', linespacing=1.1, zorder=14)
    
    x_esp_ret = x0 + 108.0
    y_esp_r = y_d3_top - 14.0
    ret_textos = [
        "• Cable Tirante: Acero SM 3/8\" (7 hilos)",
        "• Aislador Tracción: Porcelana ANSI 54-1",
        "• Varilla Anclaje: F°G° 5/8\" x 2.40 m",
        "• Inclinación Normal: 45° a la vertical",
        "• Carga Rotura Mínima: 3 800 daN"
    ]
    for lin in ret_textos:
        ax.text(x_esp_ret, y_esp_r, lin, fontsize=3.6, color='#0F172A', zorder=13)
        y_esp_r -= 10.5


# =========================================================================
# 1. LÁMINA P-01: REDES DE DISTRIBUCIÓN EN PLANTA GENERAL
# =========================================================================
def generar_plano_p01_profesional(salida_pdf, salida_png=None):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    kml_path = os.path.join(script_dir, "..", "fuentes", "kml", "topografia_capachica_chifron.kml")
    csv_path = os.path.join(script_dir, "..", "datos", "cargas", "censo_43_abonados.csv")
    
    rutas, vias = cargar_rutas_kml(kml_path)
    abonados = cargar_abonados_csv(csv_path)
    
    # Coordenadas Canónicas de E-04 (SED)
    e_sed = 412759.20
    n_sed = 8270976.22
    
    # ---------------------------------------------------------------------
    # CÁLCULO DE REDES SECUNDARIAS BT (C-1 Y C-2) DESDE E-04
    # ---------------------------------------------------------------------
    # Circuito C-1 (Hacia el Norte / Playa y Muelle)
    pts1_raw = rutas.get('ruta electrica 1', [])
    # Filtrar puntos que estén al norte de la SED (norte >= n_sed - 10.0)
    pts1_norte = [p for p in pts1_raw if p[1] >= n_sed - 10.0]
    if not pts1_norte:
        pts1_norte = [(e_sed, n_sed), (412684.34, 8271166.70), (412659.90, 8271446.51)]
    
    postes_c1_raw = []
    for i in range(len(pts1_norte) - 1):
        p1, p2 = pts1_norte[i], pts1_norte[i+1]
        dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        n_seg = max(1, int(math.ceil(dist / 38.0)))
        for s in range(n_seg if i == len(pts1_norte)-2 else n_seg):
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

    # Circuito C-2 (Hacia el Sur / Carretera al Fondo)
    pts3 = rutas.get('ruta electrica 3', [])
    pts4 = rutas.get('ruta electrica 4', [])
    pts_c2 = pts3[1:] + pts4

    postes_c2_raw = []
    for i in range(len(pts_c2) - 1):
        p1, p2 = pts_c2[i], pts_c2[i+1]
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
    
    # Marco y encabezado
    dibujar_marco_a3_con_encabezado(
        fig,
        "PLANO DE REDES DE DISTRIBUCIÓN EN PLANTA GENERAL, ACOMETIDAS Y RETENIDAS — SECTOR CHIFRÓN (CAPACHICA)",
        "SISTEMA MT 22.9 kV (AAAC 35 mm²) | SED BIPOSTE 100 kVA (Dyn5) | REDES BT 380/220 V (2 CIRCUITOS C-1 Y C-2)"
    )

    # MAPA GEOGRÁFICO DE DISTRIBUCIÓN
    ax_map = fig.add_axes([0.035, 0.050, 0.615, 0.875])
    
    # 1. Trazado de Vías de Comunicación
    for v_nom, pts in vias:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax_map.plot(xs, ys, color='#94A3B8', linewidth=1.4, linestyle='-', zorder=1)
        ax_map.plot(xs, ys, color='#F1F5F9', linewidth=0.6, linestyle='--', zorder=2)

    # 2. LÍNEA PRIMARIA MT 22.9 kV (DOMINANTE, CONTINUA, AZUL ELÉCTRICO)
    traza_mt = [(p["este"], p["norte"]) for p in POSTES_MT_CANONICOS]
    ax_map.plot([p[0] for p in traza_mt], [p[1] for p in traza_mt], color='#0284C7', linewidth=2.6, linestyle='-', zorder=6)
    
    # Dibujar las 9 Estructuras MT E-01 a E-09
    for p_mt in POSTES_MT_CANONICOS:
        pe, pn, pid = p_mt["este"], p_mt["norte"], p_mt["id"]
        if pid == "E-04":
            dibujar_bloque_sed_cad(ax_map, pe, pn)
            dibujar_bloque_pat_cad(ax_map, pe, pn, dx=0.0, dy=-7.0)
            dibujar_bloque_retenida_cad(ax_map, pe, pn, dx=9.0, dy=-7.0)
        else:
            dibujar_bloque_poste_cad(ax_map, pe, pn, radio=2.2, etiqueta=pid, pos_etiqueta='top-right', es_mt=True)
            if p_mt["ret"] != "Ninguna":
                dibujar_bloque_retenida_cad(ax_map, pe, pn, dx=-8.0, dy=-8.0)
            if p_mt["pat"]:
                dibujar_bloque_pat_cad(ax_map, pe, pn, dx=5.0, dy=-5.0)

    # CALLOUTS TÉCNICOS DESTACADOS EN PLANTA:
    # A. Punto de Derivación E-01 (Electro Puno)
    e01 = POSTES_MT_CANONICOS[0]
    ax_map.annotate("E-01: PUNTO DE DERIVACIÓN MT (ELECTRO PUNO)\nPoste C.A.C. 12/400 | Armado PR-1 | PAT-3\nCut-Out 27 kV 100A + Pararrayos ZnO 21 kV\nE: 412606.01 m, N: 8270712.24 m (3,924.17 msnm)",
                    xy=(e01["este"], e01["norte"]), xytext=(e01["este"] - 180.0, e01["norte"] + 30.0),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.7", color='#0369A1', lw=1.2),
                    bbox=dict(boxstyle="square,pad=0.35", fc="#F0F9FF", ec="#0284C7", lw=1.1),
                    fontsize=5.4, fontweight='bold', color='#0369A1', zorder=35)

    # B. Subestación Biposte E-04 (SED 100 kVA)
    e04 = POSTES_MT_CANONICOS[3]
    ax_map.annotate("E-04: SED BIPOSTE SAB-1 (100 kVA, Dyn5)\n2 x C.A.C. 13/400 | 22.9 / 0.38 - 0.22 kV | PAT-3\nE: 412759.20 m, N: 8270976.22 m (3,839.56 msnm)\nORIGEN DE REDES BT: C-1 (Norte) y C-2 (Sur)",
                    xy=(e04["este"], e04["norte"]), xytext=(e04["este"] + 45.0, e04["norte"] - 45.0),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.7", color='#B91C1C', lw=1.2),
                    bbox=dict(boxstyle="square,pad=0.35", fc="#FEF2F2", ec="#B91C1C", lw=1.1),
                    fontsize=5.4, fontweight='bold', color='#991B1B', zorder=35)

    # C. Vano Crítico E-05 - E-06 (115.59 m)
    e05 = POSTES_MT_CANONICOS[4]
    e06 = POSTES_MT_CANONICOS[5]
    xm_vc = (e05["este"] + e06["este"]) / 2.0
    ym_vc = (e05["norte"] + e06["norte"]) / 2.0
    ax_map.annotate("VANO CRÍTICO: 115.59 m (E-05 — E-06)\nFlecha Máx (+35°C): 1.244 m\nGálibo Mín: 9.356 m (CNE Regla 232 >= 6.50 m)\nCRUCE DE CAMINO PRINCIPAL A CHIFRÓN",
                    xy=(xm_vc, ym_vc), xytext=(xm_vc + 35.0, ym_vc + 15.0),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.7", color='#D97706', lw=1.2),
                    bbox=dict(boxstyle="square,pad=0.35", fc="#FFFBEB", ec="#D97706", lw=1.1),
                    fontsize=5.4, fontweight='bold', color='#92400E', zorder=35)

    # D. Terminal de Línea MT E-09
    e09 = POSTES_MT_CANONICOS[8]
    ax_map.annotate("E-09: TERMINAL LÍNEA PRIMARIA\nPoste C.A.C. 12/400 | Armado PR-1 | PAT-3\nE: 412659.90 m, N: 8271446.51 m",
                    xy=(e09["este"], e09["norte"]), xytext=(e09["este"] + 25.0, e09["norte"] - 15.0),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.7", color='#0369A1', lw=1.0),
                    bbox=dict(boxstyle="square,pad=0.30", fc="#F0F9FF", ec="#0284C7", lw=0.9),
                    fontsize=5.0, fontweight='bold', color='#0369A1', zorder=35)

    # 3. REDES SECUNDARIAS BT (380/220 V)
    # Circuito C-1 (Azul Real): Desde E-04 corre hacia el norte
    pts_c1_draw = [(e_sed, n_sed)] + [(p["este"], p["norte"]) for p in postes_c1]
    ax_map.plot([p[0] for p in pts_c1_draw], [p[1] for p in pts_c1_draw], color='#1D4ED8', linewidth=1.5, zorder=4)
    for p in postes_c1:
        pid = p["id"]
        if pid in ['P1-02', 'P1-16']:
            pos_p = 'bottom-left'
        elif pid in ['P1-05', 'P1-07', 'P1-14', 'P1-19']:
            pos_p = 'bottom-right'
        elif pid in ['P1-04', 'P1-09', 'P1-11', 'P1-12']:
            pos_p = 'top-right'
        else:
            pos_p = 'top-left'
            
        dibujar_bloque_poste_cad(ax_map, p["este"], p["norte"], radio=1.7, etiqueta=p["id"],
                                 ap=p.get("ap", False), dx_ap=4.0, dy_ap=1.8, pos_etiqueta=pos_p, es_mt=False)
        if p["pat"]:
            dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=4.0, dy=-4.0)
        if p["ret"]:
            dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=6.5, dy=-6.5)

    # Circuito C-2 (Ámbar / Naranja): Desde E-04 corre hacia el sur
    pts_c2_draw = [(e_sed, n_sed)] + [(p["este"], p["norte"]) for p in postes_c2]
    ax_map.plot([p[0] for p in pts_c2_draw], [p[1] for p in pts_c2_draw], color='#D97706', linewidth=1.5, zorder=4)
    for p in postes_c2:
        pid = p["id"]
        pos_p = 'bottom-right' if pid in ['P2-03', 'P2-07'] else 'top-left'
        dibujar_bloque_poste_cad(ax_map, p["este"], p["norte"], radio=1.7, etiqueta=p["id"],
                                 ap=p.get("ap", False), dx_ap=4.0, dy_ap=1.8, pos_etiqueta=pos_p, es_mt=False)
        if p["pat"]:
            dibujar_bloque_pat_cad(ax_map, p["este"], p["norte"], dx=4.0, dy=-4.0)
        if p["ret"]:
            dibujar_bloque_retenida_cad(ax_map, p["este"], p["norte"], dx=6.5, dy=-6.5)

    # 4. ACOMETIDAS DOMICILIARIAS (43 ABONADOS CENSADOS)
    todos_postes = [(p["este"], p["norte"], p["id"], p["circuito"]) for p in (postes_c1 + postes_c2)] + [(e_sed, n_sed, "SED-01", "SED")]
    for ab in abonados:
        xe_ab, yn_ab = ab["este"], ab["norte"]
        cid = ab["cod"]
        if cid == "C31":
            cand = [p for p in todos_postes if p[3] == "C-1"]
        elif int(cid[1:]) <= 30:
            cand = [p for p in todos_postes if p[3] in ["C-1", "SED"]]
        else:
            cand = [p for p in todos_postes if p[3] in ["C-2", "SED"]]
        p_cercano = min(cand, key=lambda p: math.hypot(xe_ab - p[0], yn_ab - p[1]))
        pe, pn, pid, pcirc = p_cercano
        ax_map.plot([pe, xe_ab], [pn, yn_ab], color='#94A3B8', linewidth=0.55, linestyle='--', zorder=3)
        
        # Orientación fina anticolisión para cajas portamedidor
        if cid in ['C10', 'C14', 'C22', 'C27', 'C34', 'C41']:
            dx_m, dy_m, ha_m = -2.8, 1.4, 'right'
        elif cid in ['C15', 'C23', 'C28', 'C35', 'C42']:
            dx_m, dy_m, ha_m = 2.8, -1.6, 'left'
        else:
            dx_m, dy_m, ha_m = 2.4, 1.4, 'left'
            
        dibujar_bloque_medidor_cad(ax_map, xe_ab, yn_ab, cod=cid, dx_label=dx_m, dy_label=dy_m, ha=ha_m)

    # Recuadro de detalles constructivos normalizados en la esquina noroeste
    dibujar_recuadro_detalles_tecnicos_p01(ax_map)

    # Ajustes y grilla del mapa
    ax_map.set_xlim(412350, 413000)
    ax_map.set_ylim(8270650, 8271500)
    ax_map.set_aspect('equal')
    ax_map.grid(True, linestyle=':', color='#94A3B8', alpha=0.5)
    ax_map.set_xlabel("Coordenada Este UTM (m) — Datum WGS-84 Zona 19S", fontsize=7.2, fontweight='bold', labelpad=4)
    ax_map.set_ylabel("Coordenada Norte UTM (m) — Datum WGS-84 Zona 19S", fontsize=7.2, fontweight='bold', labelpad=4)
    ax_map.tick_params(axis='both', which='major', labelsize=6.5)

    # ---------------------------------------------------------------------
    # PANELES LATERALES DERECHOS
    # ---------------------------------------------------------------------
    # PANEL 1: LEYENDA OFICIAL DE SIMBOLOGÍA
    ax_leg = fig.add_axes([0.665, 0.725, 0.305, 0.200])
    ax_leg.axis('off')
    rect_leg = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.1)
    ax_leg.add_patch(rect_leg)
    ax_leg.text(0.5, 0.925, "SIMBOLOGÍA NORMALIZADA UNE-EN 60617 / DGE-MEM", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A')
    ax_leg.plot([0.04, 0.96], [0.855, 0.855], color='#334155', linewidth=0.7)
    
    simbolos_cad = [
        ("Red Primaria MT 22.9 kV (AAAC 35 mm²)", '#0284C7', '-', 'line'),
        ("Red Secundaria BT Troncal C-1 (CAAI 3x35+25+16 mm²)", '#1D4ED8', '-', 'line'),
        ("Red Secundaria BT Troncal C-2 (CAAI 3x25+25+16 mm²)", '#D97706', '-', 'line'),
        ("Acometida Concéntrica Aérea Domiciliaria (SET 2x4 mm²)", '#94A3B8', '--', 'line'),
        ("Subestación Biposte SAB-1 100 kVA (UNE 06-09-01)", '#B91C1C', 'sed', 'sed'),
        ("Poste Concreto MT C.A.C. 12m y 13m (DGE 09-91-20)", '#0284C7', 'poste_mt', 'poste_mt'),
        ("Poste Concreto BT C.A.C. 8m/200daN (DGE 09-91-20)", '#0F172A', 'poste', 'poste'),
        ("Pastoral con Luminaria LED 60W AP (UNE 11-15-03)", '#CA8A04', 'poste_ap', 'poste_ap'),
        ("Puesta a Tierra Protección PAT-1 / PAT-3 (UNE 02-15-01)", '#15803D', 'pat', 'pat'),
        ("Retenida Inclinada / Biselar (DGE 09-91-18)", '#C2410C', 'ret', 'ret')
    ]
    y_l = 0.775
    for desc, col, st, t in simbolos_cad:
        if t == 'line':
            ax_leg.plot([0.05, 0.18], [y_l, y_l], color=col, linestyle=st, linewidth=1.4)
        elif t == 'sed':
            c1 = patches.Circle((0.095, y_l), radius=0.016, facecolor='none', edgecolor='#DC2626', linewidth=0.85)
            c2 = patches.Circle((0.135, y_l), radius=0.016, facecolor='none', edgecolor='#1D4ED8', linewidth=0.85)
            ax_leg.add_patch(c1)
            ax_leg.add_patch(c2)
        elif t == 'poste_mt':
            c_p = patches.Circle((0.115, y_l), radius=0.016, facecolor='#E0F2FE', edgecolor='#0284C7', linewidth=0.9)
            ax_leg.add_patch(c_p)
            ax_leg.plot(0.115, y_l, marker='.', color='#0284C7', markersize=2.0)
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
        ax_leg.text(0.22, y_l, desc, va='center', fontsize=5.1, color='#0F172A')
        y_l -= 0.076

    # PANEL 2: PLANILLA DE ESTRUCTURAS CANÓNICAS MT (E-01 A E-09)
    ax_est = fig.add_axes([0.665, 0.465, 0.305, 0.245])
    ax_est.axis('off')
    rect_est = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.1)
    ax_est.add_patch(rect_est)
    ax_est.text(0.5, 0.935, "PLANILLA CANÓNICA DE ESTRUCTURAS MT (E-01 A E-09)", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A')
    ax_est.plot([0.04, 0.96], [0.875, 0.875], color='#334155', linewidth=0.7)

    filas_est_mt = [
        ("E-01 (0+000): 12/400 PR-1", "Derivación MT", "Ret. Incl. / PAT-3"),
        ("E-02 (0+105): 12/300 PS-1", "Suspensión", "Ladera Pronunciada"),
        ("E-03 (0+210): 12/300 PS-1", "Suspensión", "Ladera Caserío"),
        ("E-04 (0+305): 2x13/400 SAB-1", "SED 100 kVA", "Ret. CV / PAT-3"),
        ("E-05 (0+402): 12/400 PA-1", "Ángulo -36°", "Ret. Biselar"),
        ("E-06 (0+518): 12/400 PA-1", "Ángulo +31°", "Vano Crítico (115.6m)"),
        ("E-07 (0+628): 12/300 PS-1", "Suspensión", "Alineamiento Llano"),
        ("E-08 (0+708): 12/400 PA-1", "Ángulo +33°", "Ret. Biselar"),
        ("E-09 (0+816): 12/400 PR-1", "Terminal MT", "Ret. Incl. / PAT-3")
    ]
    y_e = 0.815
    for item, funcion, obs in filas_est_mt:
        es_crit = ("E-04" in item or "E-06" in item or "E-01" in item)
        c_i = '#B91C1C' if "E-04" in item else ('#D97706' if "E-06" in item else ('#0369A1' if "E-01" in item else '#0F172A'))
        ax_est.text(0.04, y_e, item, va='center', fontsize=5.1, fontweight='bold' if es_crit else 'normal', color=c_i)
        ax_est.text(0.58, y_e, funcion, va='center', fontsize=5.0, color='#1E3A8A' if es_crit else '#334155')
        ax_est.text(0.96, y_e, obs, ha='right', va='center', fontsize=4.8, color='#64748B')
        y_e -= 0.082

    # PANEL 3: CUADRO DE CARGAS — 2 CIRCUITOS DE DISTRIBUCIÓN
    ax_car = fig.add_axes([0.665, 0.300, 0.305, 0.150])
    ax_car.axis('off')
    rect_car = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.1)
    ax_car.add_patch(rect_car)
    ax_car.text(0.5, 0.905, "CUADRO DE CARGAS Y MÁXIMA DEMANDA (AÑO 20)", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A')
    ax_car.plot([0.04, 0.96], [0.815, 0.815], color='#334155', linewidth=0.7)
    
    filas_2c = [
        ("Abonados Censados / Proyectados", "43 actuales / 78 año 20"),
        ("Circuito C-1 (Norte / Playa: 56 hab, 10 lum)", "51.00 kW (56.67 kVA)"),
        ("Circuito C-2 (Carretera Sur: 22 hab, 5 lum)", "20.10 kW (22.33 kVA)"),
        ("MÁXIMA DEMANDA TOTAL (cos φ = 0.90)", "71.10 kW / 79.00 kVA"),
        ("TRANSFORMADOR ESTANDARIZADO", "100 kVA (Dyn5) — Reserva: 21.0%")
    ]
    y_c = 0.690
    for param, val in filas_2c:
        f_w = 'bold' if ('MÁXIMA' in param or 'TRANSFORMADOR' in param) else 'normal'
        c_t = '#B91C1C' if 'TRANSFORMADOR' in param else ('#1D4ED8' if 'C-1' in param else ('#D97706' if 'C-2' in param else '#0F172A'))
        ax_car.text(0.04, y_c, param, va='center', fontsize=5.1, fontweight=f_w, color=c_t)
        ax_car.text(0.96, y_c, val, ha='right', va='center', fontsize=5.1, fontweight='bold', color=c_t)
        y_c -= 0.132

    # PANEL 4: RÓTULO OFICIAL DE INGENIERÍA LÁMINA P-01
    dibujar_rotulo_oficial_cad(fig.add_axes([0.665, 0.050, 0.305, 0.235]), 0, 0, 1, 1,
                               plano_cod="P-01",
                               plano_nom_l1="REDES DE DISTRIBUCIÓN EN PLANTA GENERAL,",
                               plano_nom_l2="ACOMETIDAS Y RETENIDAS (2 CIRCUITOS)",
                               escala="1 : 2500")

    fig.savefig(salida_pdf, format='pdf', dpi=300)
    if salida_png:
        fig.savefig(salida_png, format='png', dpi=300)
    plt.close(fig)
    print(f"Lámina P-01 generada exitosamente en: {salida_pdf}")


# =========================================================================
# 2. LÁMINA PL-01: PERFIL LONGITUDINAL TOPOGRÁFICO DE LÍNEA PRIMARIA
# =========================================================================
def generar_plano_pl01_profesional(salida_pdf, salida_png=None):
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    
    dibujar_marco_a3_con_encabezado(
        fig,
        "PERFIL LONGITUDINAL TOPOGRÁFICO Y DISTRIBUCIÓN DE ESTRUCTURAS — LÍNEA PRIMARIA 22.9 kV",
        "SECTOR CHIFRÓN, CAPACHICA (PUNO) | CONDUCTOR AAAC 35 mm² | ESCALAS: HORIZONTAL 1:2000, VERTICAL 1:500"
    )

    # ÁREA PRINCIPAL DEL PERFIL TOPOGRÁFICO Y CATENARIAS
    ax_prof = fig.add_axes([0.050, 0.380, 0.915, 0.540])
    
    progs = [p["prog"] for p in POSTES_MT_CANONICOS]
    cotas = [p["cota"] for p in POSTES_MT_CANONICOS]
    
    # Perfil del Terreno Natural
    ax_prof.plot(progs, cotas, color='#78350F', linewidth=2.4, label='Perfil del Terreno Natural (msnm)')
    ax_prof.fill_between(progs, cotas, 3800, color='#FEF3C7', alpha=0.35)
    
    # Dibujo de Postes Verticales y Catenarias
    for p in POSTES_MT_CANONICOS:
        prog, cota, pid, arm = p["prog"], p["cota"], p["id"], p["armado"]
        h_libre = 11.5 if pid == "E-04" else 10.6  # 13m o 12m menos empotramiento
        
        # Poste vertical de concreto
        color_poste = '#DC2626' if pid == "E-04" else '#1E293B'
        lw_poste = 3.6 if pid == "E-04" else 2.6
        ax_prof.plot([prog, prog], [cota, cota + h_libre], color=color_poste, linewidth=lw_poste, zorder=5)
        
        # Símbolo en cabeza de poste
        marker_sop = 's' if pid == "E-04" else '^'
        color_sop = '#DC2626' if pid == "E-04" else '#0284C7'
        ax_prof.plot(prog, cota + h_libre, marker=marker_sop, color=color_sop, markersize=7.0, zorder=6)
        
        # Etiqueta de la estructura sobre el poste
        y_txt = cota + h_libre + 2.8
        lbl_arm = arm.split()[0]
        ax_prof.text(prog, y_txt, f"{pid}\n{lbl_arm}", ha='center', va='bottom', fontsize=5.8, fontweight='bold',
                     color='#991B1B' if pid == "E-04" else ('#D97706' if pid == "E-06" else '#1E3A8A'),
                     bbox=dict(boxstyle='square,pad=0.15', fc='white', ec='#CBD5E1', lw=0.4, alpha=0.92), zorder=10)

    # Catenarias parabólicas exactas y Línea de Gálibo CNE (Regla 232)
    flechas_canónicas = {
        0: 1.054,  # E-01 a E-02 (105.00 m)
        1: 1.054,  # E-02 a E-03 (105.00 m)
        2: 0.889,  # E-03 a E-04 (95.21 m)
        3: 0.922,  # E-04 a E-05 (97.22 m)
        4: 1.244,  # E-05 a E-06 (115.59 m) -> VANO CRÍTICO
        5: 1.151,  # E-06 a E-07 (110.51 m)
        6: 0.653,  # E-07 a E-08 (79.81 m)
        7: 1.111   # E-08 a E-09 (108.26 m)
    }

    for i in range(len(POSTES_MT_CANONICOS) - 1):
        x1, y1 = progs[i], cotas[i] + (11.5 if POSTES_MT_CANONICOS[i]["id"] == "E-04" else 10.6)
        x2, y2 = progs[i+1], cotas[i+1] + (11.5 if POSTES_MT_CANONICOS[i+1]["id"] == "E-04" else 10.6)
        vano = x2 - x1
        xs = [x1 + vano * k / 30.0 for k in range(31)]
        f_max = flechas_canónicas[i]
        
        # Ecuación parabólica de la catenaria
        ys = [y1 + (y2 - y1)*(x - x1)/vano - 4.0 * f_max * ((x - x1)/vano) * (1.0 - (x - x1)/vano) for x in xs]
        color_cat = '#DC2626' if i == 4 else '#0284C7'
        lw_cat = 2.2 if i == 4 else 1.6
        ax_prof.plot(xs, ys, color=color_cat, linewidth=lw_cat, zorder=4)
        
        # Línea de gálibo normativo CNE (6.50 m sobre suelo)
        ys_gal = [cotas[i] + (cotas[i+1] - cotas[i])*(x - x1)/vano + 6.50 for x in xs]
        ax_prof.plot(xs, ys_gal, color='#16A34A', linestyle=':', linewidth=1.1, zorder=3)

    # CALLOUTS TÉCNICOS EN EL PERFIL
    # A. Vano Crítico E-05 - E-06 (Cruce Camino)
    x_crit = (progs[4] + progs[5]) / 2.0
    y_crit_cat = (cotas[4] + cotas[5])/2.0 + 10.6 - 1.244
    ax_prof.annotate("VANO CRÍTICO: 115.59 m (E-05 a E-06)\nFlecha Máx (+35°C): 1.244 m\nGálibo Vertical: 9.356 m (CNE >= 6.50 m)\nMargen de Seguridad: +2.856 m (CRUCE CAMINO)",
                     xy=(x_crit, y_crit_cat), xytext=(x_crit + 25.0, y_crit_cat + 22.0),
                     arrowprops=dict(arrowstyle="-|>,head_width=0.4,head_length=0.7", color='#DC2626', lw=1.2),
                     bbox=dict(boxstyle="square,pad=0.35", fc="#FEF2F2", ec="#DC2626", lw=1.1),
                     fontsize=5.6, fontweight='bold', color='#991B1B', zorder=20)

    # B. Estructura E-04 (SED Biposte)
    ax_prof.annotate("E-04: SED BIPOSTE 100 kVA (SAB-1, 13m)\nTransformador 22.9/0.38-0.22 kV Dyn5\nPAT-3 (R <= 10 Ω)",
                     xy=(progs[3], cotas[3] + 11.5), xytext=(progs[3] - 120.0, cotas[3] + 28.0),
                     arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.7", color='#DC2626', lw=1.0),
                     bbox=dict(boxstyle="square,pad=0.30", fc="#FEF2F2", ec="#DC2626", lw=0.9),
                     fontsize=5.2, fontweight='bold', color='#991B1B', zorder=20)

    # C. Derivación E-01 (Electro Puno)
    ax_prof.annotate("E-01: DERIVACIÓN ELECTRO PUNO (12/400 PR-1)\nCut-Out 27 kV + ZnO 21 kV | Cota: 3,924.17 msnm",
                     xy=(progs[0], cotas[0] + 10.6), xytext=(progs[0] + 35.0, cotas[0] + 8.0),
                     arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.7", color='#0369A1', lw=1.0),
                     bbox=dict(boxstyle="square,pad=0.30", fc="#F0F9FF", ec="#0284C7", lw=0.9),
                     fontsize=5.2, fontweight='bold', color='#0369A1', zorder=20)

    ax_prof.set_xlim(-25, 845)
    ax_prof.set_ylim(3805, 3945)
    ax_prof.set_ylabel("Cota (msnm)", fontsize=7.5, fontweight='bold')
    ax_prof.grid(True, linestyle='--', color='#94A3B8', alpha=0.45)
    ax_prof.tick_params(axis='both', which='major', labelsize=6.5)

    # ---------------------------------------------------------------------
    # GUITARRA DE DATOS TOPOGRÁFICOS (BANDS)
    # ---------------------------------------------------------------------
    ax_guit = fig.add_axes([0.050, 0.045, 0.635, 0.300])
    ax_guit.axis('off')
    rect_guit = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.2)
    ax_guit.add_patch(rect_guit)
    
    filas_guit = [
        "ESTRUCTURA",
        "ARMADO DGE",
        "POSTE C.A.C.",
        "COTA TERRENO (m)",
        "COTA CABEZA POSTE (m)",
        "VANO PARCIAL (m)",
        "PROGRESIVA (m)",
        "ÁNGULO DESVÍO (°)",
        "RETENIDA / PAT"
    ]
    n_f = len(filas_guit)
    for i in range(1, n_f):
        ax_guit.plot([0, 1], [i / float(n_f), i / float(n_f)], color='#64748B', linewidth=0.6)
    ax_guit.plot([0.18, 0.18], [0, 1], color='#0F172A', linewidth=1.2)
    
    for idx, f_nom in enumerate(filas_guit):
        y_f = (n_f - 1 - idx + 0.5) / float(n_f)
        ax_guit.text(0.015, y_f, f_nom, va='center', fontsize=5.4, fontweight='bold', color='#1E293B')
        
    dx_col = 0.81 / float(len(POSTES_MT_CANONICOS))
    for p_i, p in enumerate(POSTES_MT_CANONICOS):
        x_c = 0.185 + p_i * dx_col + dx_col / 2.0
        vano_p = f"{p['prog'] - POSTES_MT_CANONICOS[p_i-1]['prog']:.1f}" if p_i > 0 else "---"
        ret_pat = f"{p['ret'][:7]} / {p['pat']}" if p['pat'] else (p['ret'][:10] if p['ret'] != "Ninguna" else "---")
        h_l = 11.5 if p["id"] == "E-04" else 10.6
        cota_sop = f"{p['cota'] + h_l:.2f}"
        
        datos_col = [
            p["id"],
            p["armado"].split()[0],
            p["poste"].replace(" (Biposte)", ""),
            f"{p['cota']:.2f}",
            cota_sop,
            vano_p,
            f"{p['prog']:.2f}",
            f"{p['ang']:+.1f}°",
            ret_pat
        ]
        es_crit_col = (p["id"] in ["E-04", "E-05", "E-06"])
        for f_idx, d_val in enumerate(datos_col):
            y_f = (n_f - 1 - f_idx + 0.5) / float(n_f)
            col_txt = '#B91C1C' if (es_crit_col and f_idx in [0, 5]) else '#0F172A'
            f_weight = 'bold' if (f_idx in [0, 5]) else 'normal'
            ax_guit.text(x_c, y_f, d_val, ha='center', va='center', fontsize=4.8, fontweight=f_weight, color=col_txt)

    # Rótulo Oficial de Ingeniería Lámina PL-01
    dibujar_rotulo_oficial_cad(fig.add_axes([0.695, 0.045, 0.270, 0.300]), 0, 0, 1, 1,
                               plano_cod="PL-01",
                               plano_nom_l1="PERFIL LONGITUDINAL TOPOGRÁFICO Y",
                               plano_nom_l2="DISTRIBUCIÓN DE ESTRUCTURAS LP 22.9 kV",
                               escala="H: 1/2000 | V: 1/500")

    fig.savefig(salida_pdf, format='pdf', dpi=300)
    if salida_png:
        fig.savefig(salida_png, format='png', dpi=300)
    plt.close(fig)
    print(f"Lámina PL-01 generada exitosamente en: {salida_pdf}")


# =========================================================================
# 3. LÁMINA U-01: DIAGRAMA UNIFILAR GENERAL Y PROTECCIONES
# =========================================================================
def generar_plano_u01_profesional(salida_pdf, salida_png=None):
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    
    dibujar_marco_a3_con_encabezado(
        fig,
        "DIAGRAMA UNIFILAR GENERAL Y ESQUEMA DE PROTECCIONES ELECTROMECÁNICAS",
        "SED BIPOSTE 100 kVA (22.9 / 0.38 - 0.22 kV Dyn5) | 2 CIRCUITOS DE DISTRIBUCIÓN + ALUMBRADO PÚBLICO"
    )

    # PANEL PRINCIPAL: DIAGRAMA UNIFILAR GENERAL
    ax_uni = fig.add_axes([0.040, 0.045, 0.585, 0.880])
    ax_uni.axis('off')
    rect_u = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.2)
    ax_uni.add_patch(rect_u)
    
    ax_uni.text(0.5, 0.968, "DIAGRAMA UNIFILAR GENERAL — SUBESTACIÓN BIPOSTE 100 kVA", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E3A8A')
    ax_uni.text(0.5, 0.942, "Alimentación MT 22.9 kV | Salidas en BT 380/220 V con 2 Circuitos (C-1 y C-2) + Alumbrado Público", ha='center', va='center', fontsize=6.6, color='#64748B')
    ax_uni.plot([0.04, 0.96], [0.925, 0.925], color='#334155', linewidth=1.0)

    # Red Primaria MT 22.9 kV
    ax_uni.plot([0.5, 0.5], [0.915, 0.840], color='#0284C7', linewidth=1.8)
    ax_uni.text(0.52, 0.885, "LÍNEA PRIMARIA 22.9 kV (Red Electro Puno S.A.A.)\nTrifásico 3 Hilos — Conductor AAAC 35 mm²", fontsize=6.2, fontweight='bold', color='#0284C7')

    # Pararrayos ZnO
    ax_uni.plot([0.5, 0.30], [0.840, 0.840], color='#0284C7', linewidth=1.2)
    ax_uni.plot([0.30, 0.30], [0.840, 0.790], color='#0284C7', linewidth=1.2)
    rect_par = patches.Rectangle((0.275, 0.755), 0.05, 0.035, facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=1.0)
    ax_uni.add_patch(rect_par)
    ax_uni.text(0.095, 0.772, "Pararrayos Óxido Metálico (ZnO)\n21 kV / 10 kA (Clase 1 Distribución)", fontsize=5.6, color='#B91C1C')
    # Puesta a tierra pararrayos
    ax_uni.plot([0.30, 0.30], [0.755, 0.715], color='#15803D', linewidth=0.85)
    ax_uni.plot([0.275, 0.325], [0.715, 0.715], color='#15803D', linewidth=1.0)
    ax_uni.plot([0.283, 0.317], [0.707, 0.707], color='#15803D', linewidth=1.0)
    ax_uni.plot([0.290, 0.310], [0.699, 0.699], color='#15803D', linewidth=1.0)
    ax_uni.text(0.34, 0.710, "PAT-3 (R <= 10 Ω)", fontsize=5.3, fontweight='bold', color='#15803D')

    # Seccionadores Cut-Out 27 kV
    ax_uni.plot([0.5, 0.5], [0.840, 0.800], color='#0284C7', linewidth=1.3)
    rect_co = patches.Rectangle((0.47, 0.760), 0.06, 0.040, facecolor='#EFF6FF', edgecolor='#1D4ED8', linewidth=1.1)
    ax_uni.add_patch(rect_co)
    ax_uni.text(0.55, 0.780, "Seccionador Fusible Cut-Out\n27 kV / 100 A (Fusible Chicote K 4A)", fontsize=5.8, color='#1D4ED8')

    # Bajada a Bornes MT
    ax_uni.plot([0.5, 0.5], [0.760, 0.695], color='#0284C7', linewidth=1.3)

    # Transformador Trifásico 100 kVA
    c_mt = patches.Circle((0.5, 0.660), radius=0.035, facecolor='none', edgecolor='#DC2626', linewidth=1.4)
    c_bt = patches.Circle((0.5, 0.610), radius=0.035, facecolor='none', edgecolor='#1D4ED8', linewidth=1.4)
    ax_uni.add_patch(c_mt)
    ax_uni.add_patch(c_bt)
    ax_uni.text(0.56, 0.640, "TRANSFORMADOR DE DISTRIBUCIÓN 100 kVA\nRelación de Transformación: 22.9 / 0.38 - 0.22 kV\nGrupo Conexión: Dyn5 | Frecuencia: 60 Hz | ONAN\nDemanda Máxima: 79.0 kVA (Reserva Técnica: 21.0%)",
                fontsize=6.0, fontweight='bold', color='#991B1B')

    # Puesta a tierra Neutro BT
    ax_uni.plot([0.465, 0.38], [0.610, 0.610], color='#15803D', linewidth=0.85)
    ax_uni.plot([0.38, 0.38], [0.610, 0.565], color='#15803D', linewidth=0.85)
    ax_uni.plot([0.355, 0.405], [0.565, 0.565], color='#15803D', linewidth=1.0)
    ax_uni.plot([0.363, 0.397], [0.557, 0.557], color='#15803D', linewidth=1.0)
    ax_uni.plot([0.370, 0.390], [0.549, 0.549], color='#15803D', linewidth=1.0)
    ax_uni.text(0.20, 0.560, "Puesta a Tierra de Neutro\nR <= 10 Ω (PAT-3)", fontsize=5.3, color='#15803D')

    # Bajada a Tablero
    ax_uni.plot([0.5, 0.5], [0.575, 0.520], color='#1D4ED8', linewidth=1.6)

    # Gabinete BT IP65
    rect_tab = patches.Rectangle((0.08, 0.035), 0.84, 0.485, facecolor='#F8FAFC', edgecolor='#0F172A', linewidth=1.2)
    ax_uni.add_patch(rect_tab)
    ax_uni.text(0.5, 0.505, "TABLERO GENERAL DE DISTRIBUCIÓN BT (GABINETE FIBRA POLIÉSTER IP65)", ha='center', fontsize=7.0, fontweight='bold', color='#0F172A')

    # Totalizador General 3x160A
    rect_gen = patches.Rectangle((0.43, 0.435), 0.14, 0.050, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.2)
    ax_uni.add_patch(rect_gen)
    ax_uni.text(0.5, 0.460, "TOTALIZADOR GENERAL 3x160 A\nTermomagnético Regulable (Icu = 25 kA)", ha='center', va='center', fontsize=5.5, fontweight='bold', color='#92400E')

    # Barra Trifásica 380/220 V
    ax_uni.plot([0.5, 0.5], [0.435, 0.380], color='#1D4ED8', linewidth=1.3)
    ax_uni.plot([0.16, 0.84], [0.380, 0.380], color='#1E293B', linewidth=2.4)
    ax_uni.text(0.85, 0.380, "BARRA 380/220 V", va='center', fontsize=5.8, fontweight='bold', color='#1E293B')

    circuitos_data = [
        (0.28, "C-1", "3x100 A", [
            ("Troncal Norte + C31 (Ruta 1)", '#1E3A8A', True),
            ("56 usuarios proyectados", '#0F172A', False),
            ("Demanda: 51.00 kW (56.7 kVA)", '#B91C1C', True),
            ("CAAI 3x35+25+16 mm²", '#0F172A', False),
            ("L = 820.0 m | ΔV = 2.14%", '#15803D', True)
        ]),
        (0.50, "C-2", "3x63 A", [
            ("Carretera Fondo (Rutas 3 y 4)", '#B45309', True),
            ("22 usuarios proyectados", '#0F172A', False),
            ("Demanda: 20.10 kW (22.3 kVA)", '#B91C1C', True),
            ("CAAI 3x25+25+16 mm²", '#0F172A', False),
            ("L = 456.0 m | ΔV = 1.15%", '#15803D', True)
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
        ax_uni.text(xc, 0.320, f"ITM {cid}", ha='center', va='center', fontsize=5.6, fontweight='bold', color='#1E3A8A')
        ax_uni.text(xc, 0.295, itm_val, ha='center', va='center', fontsize=5.1, color='#1E3A8A')
        
        ax_uni.plot([xc, xc], [0.275, 0.215], color='#1D4ED8', linewidth=1.8)
        ax_uni.plot(xc, 0.215, marker='v', color='#1D4ED8', markersize=5.5)
        
        rect_card = patches.Rectangle((xc - 0.095, 0.050), 0.190, 0.150, facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=0.7, zorder=10)
        ax_uni.add_patch(rect_card)
        
        y_pos = 0.180
        for txt, col, es_b in lineas_det:
            ax_uni.text(xc, y_pos, txt, ha='center', va='center',
                        fontsize=4.8, fontweight='bold' if es_b else 'normal', color=col, zorder=12)
            y_pos -= 0.028

    # PANEL DERECHO: ESPECIFICACIONES TÉCNICAS
    ax_esp = fig.add_axes([0.640, 0.340, 0.330, 0.585])
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
        ("Interruptores de Circuitos C-1 y C-2", "Caja moldeada regulable (C-1 a 3x100A, C-2 a 3x63A), curva C, Icu = 18 kA a 380 V."),
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
    dibujar_rotulo_oficial_cad(fig.add_axes([0.640, 0.045, 0.330, 0.275]), 0, 0, 1, 1,
                               plano_cod="U-01",
                               plano_nom_l1="DIAGRAMA UNIFILAR GENERAL Y ESQUEMA DE",
                               plano_nom_l2="PROTECCIONES BT (2 CIRCUITOS + AP)",
                               escala="INDICADA")

    fig.savefig(salida_pdf, format='pdf', dpi=300)
    if salida_png:
        fig.savefig(salida_png, format='png', dpi=300)
    plt.close(fig)
    print(f"Lámina U-01 generada exitosamente en: {salida_pdf}")


# =========================================================================
# 4. REGENERACIÓN DE PLANOS DXF PARA AUTOCAD
# =========================================================================
def generar_dxfs_oficiales(out_dir):
    """
    Regenera los archivos DXF en R2010 para asegurar consistencia total con los PDFs.
    """
    dxf_planta = os.path.join(out_dir, "PLANO_PLANTA_REDES_Y_ACOMETIDAS_CAPACHICA.dxf")
    dxf_perfil = os.path.join(out_dir, "PLANO_PERFIL_LONGITUDINAL_LP_CAPACHICA.dxf")
    
    # 1. DXF Planta
    doc_pl = ezdxf.new("R2010")
    msp_pl = doc_pl.modelspace()
    doc_pl.layers.new("RED_MT_22KV", dxfattribs={"color": 5})      # Azul
    doc_pl.layers.new("RED_BT_C1", dxfattribs={"color": 1})        # Rojo / azul
    doc_pl.layers.new("RED_BT_C2", dxfattribs={"color": 30})       # Ámbar
    doc_pl.layers.new("POSTES_MT", dxfattribs={"color": 4})        # Cyan
    doc_pl.layers.new("POSTES_BT", dxfattribs={"color": 7})        # Blanco
    doc_pl.layers.new("SED_100KVA", dxfattribs={"color": 1})       # Rojo
    doc_pl.layers.new("TEXTOS_INFO", dxfattribs={"color": 2})      # Amarillo
    
    pts_mt = [(p["este"], p["norte"]) for p in POSTES_MT_CANONICOS]
    msp_pl.add_lwpolyline(pts_mt, dxfattribs={"layer": "RED_MT_22KV"})
    
    for p in POSTES_MT_CANONICOS:
        msp_pl.add_circle((p["este"], p["norte"]), radius=2.5, dxfattribs={"layer": "POSTES_MT"})
        msp_pl.add_text(f"{p['id']} ({p['armado']})", dxfattribs={"layer": "TEXTOS_INFO", "height": 2.0}).set_placement((p["este"] + 3.0, p["norte"] + 3.0))
        
    doc_pl.saveas(dxf_planta)
    
    # 2. DXF Perfil
    doc_pr = ezdxf.new("R2010")
    msp_pr = doc_pr.modelspace()
    doc_pr.layers.new("TERRENO", dxfattribs={"color": 34})        # Marrón
    doc_pr.layers.new("POSTES_MT", dxfattribs={"color": 4})        # Cyan
    doc_pr.layers.new("CATENARIA_MT", dxfattribs={"color": 5})     # Azul
    doc_pr.layers.new("GALIBO_CNE", dxfattribs={"color": 3})       # Verde
    doc_pr.layers.new("TEXTOS_COTAS", dxfattribs={"color": 7})     # Blanco
    
    progs = [p["prog"] for p in POSTES_MT_CANONICOS]
    cotas = [p["cota"] for p in POSTES_MT_CANONICOS]
    
    pts_terr = list(zip(progs, cotas))
    msp_pr.add_lwpolyline(pts_terr, dxfattribs={"layer": "TERRENO"})
    
    for p in POSTES_MT_CANONICOS:
        prg, cta, pid = p["prog"], p["cota"], p["id"]
        hl = 11.5 if pid == "E-04" else 10.6
        msp_pr.add_line((prg, cta), (prg, cta + hl), dxfattribs={"layer": "POSTES_MT"})
        msp_pr.add_text(f"{pid} {cta:.1f}m", dxfattribs={"layer": "TEXTOS_COTAS", "height": 1.8}).set_placement((prg, cta + hl + 1.5))
        
    doc_pr.saveas(dxf_perfil)
    print("Archivos DXF regenerados exitosamente.")


# =========================================================================
# EJECUCIÓN PRINCIPAL
# =========================================================================
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "..", "entregables", "planos")
    prev_dir = os.path.join(out_dir, "preview_png")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(prev_dir, exist_ok=True)
    
    pdf_p01 = os.path.join(out_dir, "plano_P01_redes_planta.pdf")
    png_p01 = os.path.join(prev_dir, "plano_P01_redes_planta.png")
    png_p01_oficial = os.path.join(out_dir, "vista_oficial_p01.png")
    
    pdf_pl01 = os.path.join(out_dir, "plano_PL01_perfil_longitudinal.pdf")
    png_pl01 = os.path.join(prev_dir, "plano_PL01_perfil_longitudinal.png")
    
    pdf_u01 = os.path.join(out_dir, "plano_U01_diagrama_unifilar_detalles.pdf")
    png_u01 = os.path.join(prev_dir, "plano_U01_diagrama_unifilar_detalles.png")
    
    print("\n--- GENERANDO LÁMINAS OFICIALES EN FORMATO A3 (PDF + PNG) ---")
    generar_plano_p01_profesional(pdf_p01, png_p01)
    # Copia de vista oficial para expediente
    if os.path.exists(png_p01):
        import shutil
        shutil.copyfile(png_p01, png_p01_oficial)
        
    generar_plano_pl01_profesional(pdf_pl01, png_pl01)
    generar_plano_u01_profesional(pdf_u01, png_u01)
    
    print("\n--- REGENERANDO ARCHIVOS DXF PARA AUTOCAD ---")
    generar_dxfs_oficiales(out_dir)
    print("\n¡PROCESO COMPLETADO EXITOSAMENTE!")
