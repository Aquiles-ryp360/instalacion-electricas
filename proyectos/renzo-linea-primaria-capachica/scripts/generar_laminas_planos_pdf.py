# -*- coding: utf-8 -*-
"""
generar_laminas_planos_pdf.py
Genera las láminas oficiales de ingeniería electromecánica en formato A3 Horizontal (420 x 297 mm)
en alta definición vectorial / PDF para su compilación directa dentro del Expediente Técnico:

Lámina P-01:  Plano de Redes de Distribución en Planta General, Acometidas, Retenidas y Puesta a Tierra (Escala 1:2500)
Lámina U-01:  Diagrama Unifilar General y Detalles Constructivos de Montaje (SED 100 kVA, PAT, Retenidas, Acometida)
Lámina PL-01: Perfil Longitudinal Topográfico y Catenarias de la Línea Primaria 22.9 kV

Autor: Renzo Gabriel Mamani Galindo (Cód. 228447)
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
from matplotlib.lines import Line2D

# -------------------------------------------------------------------------
# CONSTANTES Y CONVERSIÓN DE COORDENADAS
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
# DIBUJO DE MEMBRETE OFICIAL NORMALIZADO (RÓTULO DE INGENIERÍA)
# -------------------------------------------------------------------------
def dibujar_rotulo_oficial(ax, x0, y0, w, h, plano_cod, plano_nom, escala="1 : 2500"):
    """
    Dibuja un rótulo formal normalizado de ingeniería en coordenadas normalizadas de la figura.
    """
    # Marco exterior del rótulo
    rect = patches.Rectangle((x0, y0), w, h, facecolor='#F8FAFC', edgecolor='#0F172A', linewidth=1.5, zorder=50)
    ax.add_patch(rect)
    
    # Líneas divisorias horizontales
    h_sub = h / 6.0
    for i in range(1, 6):
        ax.plot([x0, x0 + w], [y0 + i * h_sub, y0 + i * h_sub], color='#334155', linewidth=0.8, zorder=51)
        
    # División vertical en fila inferior
    ax.plot([x0 + w * 0.5, x0 + w * 0.5], [y0, y0 + h_sub], color='#334155', linewidth=0.8, zorder=51)
    ax.plot([x0 + w * 0.75, x0 + w * 0.75], [y0, y0 + h_sub], color='#334155', linewidth=0.8, zorder=51)
    
    # Textos institucionales
    # Fila 5: Universidad y Facultad
    ax.text(x0 + w/2.0, y0 + 5.5 * h_sub, "UNIVERSIDAD NACIONAL DEL ALTIPLANO — PUNO\nFACULTAD DE INGENIERÍA MECÁNICA ELÉCTRICA, ELECTRÓNICA Y SISTEMAS",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1E3A8A', zorder=52)
            
    # Fila 4: Curso y Especialidad
    ax.text(x0 + w/2.0, y0 + 4.5 * h_sub, "ESCUELA PROFESIONAL DE INGENIERÍA MECÁNICA ELÉCTRICA\nCURSO: MEC330 — INSTALACIONES ELÉCTRICAS II (SEMESTRE 2026-II)",
            ha='center', va='center', fontsize=7.0, fontweight='bold', color='#0F766E', zorder=52)
            
    # Fila 3: Proyecto
    ax.text(x0 + w/2.0, y0 + 3.5 * h_sub, "PROYECTO: LP 22.9 kV Y RED SECUNDARIA SED 100 kVA SECTOR CHIFRÓN\nDISTRITO DE CAPACHICA — PROVINCIA Y DEPARTAMENTO DE PUNO",
            ha='center', va='center', fontsize=7.0, fontweight='bold', color='#1E293B', zorder=52)
            
    # Fila 2: Nombre del Plano
    ax.text(x0 + w/2.0, y0 + 2.5 * h_sub, f"PLANO: {plano_nom}",
            ha='center', va='center', fontsize=8.0, fontweight='bold', color='#B45309', zorder=52)
            
    # Fila 1: Diseñador y Docentes
    ax.text(x0 + 0.01 * w, y0 + 1.5 * h_sub, "RESPONSABLE:\nDOCENTES:",
            ha='left', va='center', fontsize=6.2, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.22 * w, y0 + 1.5 * h_sub, "Br. Renzo Gabriel Mamani Galindo (Cód. 228447)\nIng. Leonidas Vilca Callata / Ing. Marcos José Villanueva Cornejo",
            ha='left', va='center', fontsize=6.2, color='#0F172A', zorder=52)
            
    # Fila 0: Fecha, Escala, N° de Lámina
    ax.text(x0 + 0.25 * w, y0 + 0.5 * h_sub, f"FECHA:\nOctubre 2026",
            ha='center', va='center', fontsize=6.0, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.625 * w, y0 + 0.5 * h_sub, f"ESCALA:\n{escala}",
            ha='center', va='center', fontsize=6.0, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.875 * w, y0 + 0.5 * h_sub, f"LÁMINA:\n{plano_cod}",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1E3A8A', zorder=52)


# =========================================================================
# LÁMINA P-01: PLANO DE REDES EN PLANTA GENERAL (A3 HORIZONTAL)
# =========================================================================
def generar_lamina_p01(salida_pdf):
    kml_path = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\fuentes\kml\topografia_capachica_chifron.kml"
    csv_path = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\datos\cargas\censo_43_abonados.csv"
    
    rutas, vias = cargar_rutas_kml(kml_path)
    abonados = cargar_abonados_csv(csv_path)
    
    # Coordenadas exactas SED 100 kVA (origen C1, C2, C3)
    e_sed = 412606.01
    n_sed = 8270712.24
    
    # Postes de BT con vanos <= 38m
    postes_bt = []
    p_idx = 1
    for r_name in ['ruta electrica 1', 'ruta electrica 3', 'ruta electrica 4', 'ruta electrica 2']:
        if r_name not in rutas:
            continue
        pts = rutas[r_name]
        circuito = "C-1" if '1' in r_name else ("C-2" if '3' in r_name else "C-3")
        for i in range(len(pts) - 1):
            p1 = pts[i]
            p2 = pts[i+1]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            n_seg = max(1, int(math.ceil(dist / 38.0)))
            for s in range(n_seg if i == len(pts)-2 else n_seg):
                ts = s / float(n_seg)
                xe = p1[0] + ts * (p2[0] - p1[0])
                yn = p1[1] + ts * (p2[1] - p1[1])
                if math.hypot(xe - e_sed, yn - n_sed) < 6.0 and len(postes_bt) > 0:
                    continue
                pid = f"P-BT-{p_idx:02d}"
                es_fin = (s == 0 and i == 0) or (i == len(pts)-2 and s == n_seg)
                pat = "PAT-1" if (p_idx % 5 == 0 or es_fin) else None
                ret = "RET-BT" if es_fin else None
                postes_bt.append({"id": pid, "circuito": circuito, "este": xe, "norte": yn, "pat": pat, "ret": ret})
                p_idx += 1

    # Figura A3 Landscape: 16.54 x 11.69 pulgadas (420 x 297 mm)
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    ax_map = fig.add_axes([0.05, 0.06, 0.65, 0.88])  # Ventana gráfica principal
    
    # 1. Dibujar Vías y Calles
    for v_nom, pts in vias:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax_map.plot(xs, ys, color='#94A3B8', linewidth=3.5, linestyle='-', zorder=1)
        ax_map.plot(xs, ys, color='#CBD5E1', linewidth=1.2, linestyle='--', zorder=2)
        
    # 2. Línea Primaria MT 22.9 kV (Llegada desde Electro Puno)
    traza_mt = [(412380.00, 8270740.00), (412490.00, 8270725.00), (e_sed, n_sed)]
    x_mt = [p[0] for p in traza_mt]
    y_mt = [p[1] for p in traza_mt]
    ax_map.plot(x_mt, y_mt, color='#0284C7', linewidth=3.0, linestyle='-', zorder=4, label='Línea Primaria MT 22.9 kV (AAAC 35 mm²)')
    ax_map.plot(x_mt[:-1], y_mt[:-1], marker='s', color='#0284C7', markersize=6, zorder=5)
    
    # 3. Redes de Baja Tensión 380/220 V
    # Circuito C-1
    if 'ruta electrica 1' in rutas:
        pts = rutas['ruta electrica 1']
        ax_map.plot([p[0] for p in pts], [p[1] for p in pts], color='#2563EB', linewidth=2.8, zorder=3, label='Circuito C-1 BT (Troncal Norte 38 hab - CAAI 3x35+1x25+1x16 mm²)')
    # Circuito C-2
    if 'ruta electrica 3' in rutas:
        pts = [(e_sed, n_sed)] + rutas['ruta electrica 3']
        ax_map.plot([p[0] for p in pts], [p[1] for p in pts], color='#D97706', linewidth=2.5, zorder=3, label='Circuito C-2 BT (Sector Centro 20 hab - CAAI 3x25+1x25+1x16 mm²)')
    # Circuito C-3
    if 'ruta electrica 4' in rutas:
        pts = [(e_sed, n_sed)] + rutas['ruta electrica 4']
        ax_map.plot([p[0] for p in pts], [p[1] for p in pts], color='#7C3AED', linewidth=2.5, zorder=3, label='Circuito C-3 BT (Sector Sur 20 hab - CAAI 3x25+1x25+1x16 mm²)')
    if 'ruta electrica 2' in rutas:
        pts = rutas['ruta electrica 2']
        ax_map.plot([p[0] for p in pts], [p[1] for p in pts], color='#7C3AED', linewidth=2.5, linestyle=':', zorder=3)

    # 4. Dibujar Postes de BT
    for p in postes_bt:
        xe, yn = p["este"], p["norte"]
        # Círculo del poste C.A.C. 8/200
        ax_map.plot(xe, yn, marker='o', markerfacecolor='#22C55E', markeredgecolor='#0F172A', markersize=5.5, markeredgewidth=1.0, zorder=6)
        ax_map.text(xe + 2.0, yn + 1.5, p["id"], fontsize=5.5, fontweight='bold', color='#166534', zorder=7)
        
        # Puesta a tierra normada PAT-1 (3 rayitas decrecientes)
        if p["pat"]:
            ax_map.plot([xe, xe], [yn, yn - 4.5], color='#15803D', linewidth=1.2, zorder=8)
            ax_map.plot([xe - 3.0, xe + 3.0], [yn - 4.5, yn - 4.5], color='#15803D', linewidth=1.5, zorder=8)
            ax_map.plot([xe - 2.0, xe + 2.0], [yn - 5.7, yn - 5.7], color='#15803D', linewidth=1.5, zorder=8)
            ax_map.plot([xe - 1.0, xe + 1.0], [yn - 6.9, yn - 6.9], color='#15803D', linewidth=1.5, zorder=8)
            ax_map.text(xe + 1.8, yn - 6.5, "PAT-1", fontsize=5.0, fontweight='bold', color='#15803D', zorder=8)
            
        # Retenida con bloque de anclaje
        if p["ret"]:
            dx_ret, dy_ret = -6.0, -6.0
            ax_map.plot([xe, xe + dx_ret], [yn, yn + dy_ret], color='#EA580C', linewidth=1.5, zorder=8)
            # Bloque perpendicular
            ax_map.plot([xe + dx_ret - 2.0, xe + dx_ret + 2.0], [yn + dy_ret + 2.0, yn + dy_ret - 2.0], color='#EA580C', linewidth=3.0, zorder=8)
            ax_map.text(xe + dx_ret - 3.5, yn + dy_ret, "RET-BT", fontsize=5.0, fontweight='bold', color='#EA580C', zorder=8)

    # 5. Dibujar SED Biposte 100 kVA (SED-01) en Lat: -15.640067, Lon: -69.815400
    ax_map.plot([e_sed - 2.0, e_sed + 2.0], [n_sed, n_sed], color='#DC2626', linewidth=2.5, zorder=9)
    ax_map.plot(e_sed - 2.0, n_sed, marker='o', markerfacecolor='#FACC15', markeredgecolor='#DC2626', markersize=7.0, zorder=10)
    ax_map.plot(e_sed + 2.0, n_sed, marker='o', markerfacecolor='#FACC15', markeredgecolor='#DC2626', markersize=7.0, zorder=10)
    
    # Simbología PAT-3 en la SED
    ax_map.plot([e_sed - 5.0, e_sed - 5.0], [n_sed, n_sed - 6.0], color='#15803D', linewidth=1.5, zorder=10)
    ax_map.plot([e_sed - 9.0, e_sed - 1.0], [n_sed - 6.0, n_sed - 6.0], color='#15803D', linewidth=2.0, zorder=10)
    ax_map.plot([e_sed - 7.5, e_sed - 2.5], [n_sed - 7.5, n_sed - 7.5], color='#15803D', linewidth=2.0, zorder=10)
    ax_map.plot([e_sed - 6.0, e_sed - 4.0], [n_sed - 9.0, n_sed - 9.0], color='#15803D', linewidth=2.0, zorder=10)
    ax_map.text(e_sed - 14.0, n_sed - 8.0, "PAT-3\nR<=10Ω", fontsize=5.5, fontweight='bold', color='#15803D', zorder=11)
    
    # Retenida Contraviento en la SED
    ax_map.plot([e_sed, e_sed - 10.0], [n_sed, n_sed - 10.0], color='#EA580C', linewidth=2.0, zorder=10)
    ax_map.plot([e_sed - 12.0, e_sed - 8.0], [n_sed - 8.0, n_sed - 12.0], color='#EA580C', linewidth=3.5, zorder=10)
    ax_map.text(e_sed - 16.0, n_sed - 13.0, "RET-CV", fontsize=5.5, fontweight='bold', color='#EA580C', zorder=11)
    
    # Rótulo destacado de la SED
    ax_map.annotate("SED BIPOSTE SAB-1 (100 kVA)\n22.9 / 0.38 - 0.22 kV\nLat: -15.640067°  Lon: -69.815400°\nUTM: 412606.01 E, 8270712.24 N",
                    xy=(e_sed, n_sed), xytext=(e_sed - 85.0, n_sed + 45.0),
                    arrowprops=dict(facecolor='#DC2626', shrink=0.08, width=1.5, headwidth=6.0),
                    bbox=dict(boxstyle="round,pad=0.4", fc="#FEF2F2", ec="#DC2626", lw=1.2),
                    fontsize=6.5, fontweight='bold', color='#991B1B', zorder=15)

    # 6. Dibujar las 43 Acometidas Domiciliarias a las Viviendas
    todos_postes = [(p["este"], p["norte"], p["id"]) for p in postes_bt] + [(e_sed, n_sed, "SED-01")]
    for ab in abonados:
        xe_ab, yn_ab = ab["este"], ab["norte"]
        # Encontrar poste más cercano
        dist_min = 99999.0
        p_cercano = None
        for pe, pn, pid in todos_postes:
            d = math.hypot(xe_ab - pe, yn_ab - pn)
            if d < dist_min:
                dist_min = d
                p_cercano = (pe, pn, pid)
        if p_cercano:
            pe, pn, pid = p_cercano
            # Línea discontinua de acometida concéntrica
            ax_map.plot([pe, xe_ab], [pn, yn_ab], color='#475569', linewidth=0.9, linestyle='--', zorder=4)
            # Medidor M en vivienda
            ax_map.plot(xe_ab, yn_ab, marker='s', markerfacecolor='#EF4444', markeredgecolor='#0F172A', markersize=4.5, zorder=6)
            ax_map.text(xe_ab + 1.2, yn_ab + 1.2, f"{ab['cod']} ({dist_min:.0f}m)", fontsize=5.0, fontweight='bold', color='#1E293B', zorder=7)

    # Ajustes cartográficos
    ax_map.set_xlim(412350, 412850)
    ax_map.set_ylim(8270650, 8271500)
    ax_map.set_aspect('equal')
    ax_map.grid(True, linestyle=':', color='#94A3B8', alpha=0.6)
    ax_map.set_title("PLANO DE REDES DE DISTRIBUCIÓN EN PLANTA GENERAL, ACOMETIDAS Y RETENIDAS — SECTOR CHIFRÓN (CAPACHICA)\nGEORREFERENCIACIÓN WGS-84 ZONA 19S | ORIGEN EN SED 100 kVA (Lat: -15.640067, Lon: -69.815400)",
                     fontsize=9.5, fontweight='bold', color='#0F172A', pad=10)
    ax_map.set_xlabel("Coordenada Este UTM (m)", fontsize=8.0, fontweight='bold')
    ax_map.set_ylabel("Coordenada Norte UTM (m)", fontsize=8.0, fontweight='bold')
    ax_map.tick_params(axis='both', which='major', labelsize=7.0)

    # ---------------------------------------------------------------------
    # COLUMNA DERECHA: LEYENDA, CUADRO DE CARGAS, CUADRO DE POSTES Y RÓTULO
    # ---------------------------------------------------------------------
    # Panel de Leyenda de Simbología Normalizada CNE / DGE
    ax_leg = fig.add_axes([0.72, 0.65, 0.25, 0.29])
    ax_leg.axis('off')
    rect_leg = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.2)
    ax_leg.add_patch(rect_leg)
    ax_leg.text(0.5, 0.94, "SIMBOLOGÍA TÉCNICA NORMALIZADA (CNE / DGE)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1E3A8A')
    ax_leg.plot([0.05, 0.95], [0.89, 0.89], color='#334155', linewidth=0.8)
    
    simbolos = [
        ("Red Primaria MT 22.9 kV (AAAC 35 mm²)", '#0284C7', '-', 'line'),
        ("Red Secundaria BT Circuito C-1 (CAAI 3x35+25+16 mm²)", '#2563EB', '-', 'line'),
        ("Red Secundaria BT Circuito C-2/C-3 (CAAI 3x25+25+16 mm²)", '#D97706', '-', 'line'),
        ("Acometida Concéntrica Aérea SET 2x4 mm²", '#475569', '--', 'line'),
        ("Subestación Distribución Biposte SAB-1 (100 kVA)", '#DC2626', 's', 'point'),
        ("Poste C.A.C. Baja Tensión 8m/200daN", '#22C55E', 'o', 'point'),
        ("Caja Portamedidor Monofásico Abonado (M)", '#EF4444', 's', 'point'),
        ("Puesta a Tierra Normalizada (PAT-3 / PAT-1)", '#15803D', '|', 'pat'),
        ("Retenida Mecánica con Bloque Concreto (RET-CV/RET-BT)", '#EA580C', '>', 'ret'),
        ("Luminaria Alumbrado Público LED 60W en Pastoral", '#F59E0B', '*', 'point')
    ]
    y_pos = 0.82
    for desc, col, st, t in simbolos:
        if t == 'line':
            ax_leg.plot([0.08, 0.22], [y_pos, y_pos], color=col, linestyle=st, linewidth=2.0)
        elif t == 'point':
            ax_leg.plot(0.15, y_pos, marker=st, color=col, markersize=5.0)
        elif t == 'pat':
            ax_leg.plot([0.15, 0.15], [y_pos - 0.02, y_pos + 0.02], color=col, linewidth=1.5)
            ax_leg.plot([0.11, 0.19], [y_pos - 0.02, y_pos - 0.02], color=col, linewidth=1.8)
        elif t == 'ret':
            ax_leg.plot([0.10, 0.20], [y_pos, y_pos], color=col, linewidth=1.8)
            ax_leg.plot([0.20, 0.20], [y_pos - 0.02, y_pos + 0.02], color=col, linewidth=3.0)
        ax_leg.text(0.25, y_pos, desc, va='center', fontsize=6.0, color='#1E293B')
        y_pos -= 0.08

    # Cuadro de Cargas y Resumen Eléctrico
    ax_car = fig.add_axes([0.72, 0.36, 0.25, 0.27])
    ax_car.axis('off')
    rect_car = patches.Rectangle((0, 0), 1, 1, facecolor='#F8FAFC', edgecolor='#334155', linewidth=1.2)
    ax_car.add_patch(rect_car)
    ax_car.text(0.5, 0.93, "CUADRO DE CARGAS Y PARÁMETROS DEL SISTEMA", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1E3A8A')
    ax_car.plot([0.05, 0.95], [0.87, 0.87], color='#334155', linewidth=0.8)
    
    filas_carga = [
        ("Abonados Censados Actuales (NU₀)", "43 viviendas"),
        ("Tasa Crecimiento y Horizonte", "3.0 % anual | 20 años"),
        ("Usuarios Proyectados (NU_f)", "78 abonados"),
        ("Calificación Eléctrica Asignada", "0.90 kW / lote"),
        ("Demanda Servicio Particular", "70.20 kW"),
        ("Alumbrado Público (15 lum. x 60W)", "0.90 kW"),
        ("MÁXIMA DEMANDA TOTAL", "71.10 kW"),
        ("Factor de Potencia de Diseño", "cos φ = 0.90"),
        ("POTENCIA APARENTE DEMANDADA", "79.00 kVA"),
        ("TRANSFORMADOR ESTANDARIZADO", "100 kVA (Dyn5)"),
        ("Margen de Reserva Técnica SED", "21.00 %")
    ]
    y_c = 0.80
    for param, val in filas_carga:
        f_weight = 'bold' if 'MÁXIMA' in param or 'TRANSFORMADOR' in param or 'POTENCIA' in param else 'normal'
        c_text = '#B91C1C' if 'TRANSFORMADOR' in param else '#0F172A'
        ax_car.text(0.06, y_c, param, va='center', fontsize=5.8, fontweight=f_weight, color=c_text)
        ax_car.text(0.94, y_c, val, ha='right', va='center', fontsize=5.8, fontweight='bold', color=c_text)
        y_c -= 0.068

    # Rótulo Oficial de Ingeniería en esquina inferior derecha
    dibujar_rotulo_oficial(fig.add_axes([0.72, 0.06, 0.25, 0.28]), 0, 0, 1, 1,
                          plano_cod="P-01",
                          plano_nom="REDES DE DISTRIBUCIÓN EN PLANTA,\nACOMETIDAS, RETENIDAS Y PUESTA A TIERRA",
                          escala="1 : 2500")

    fig.savefig(salida_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"Lámina P-01 generada exitosamente en: {salida_pdf}")


# =========================================================================
# LÁMINA U-01: DIAGRAMA UNIFILAR Y DETALLES CONSTRUCTIVOS (A3 HORIZONTAL)
# =========================================================================
def generar_lamina_u01(salida_pdf):
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    
    # ---------------------------------------------------------------------
    # CUADRANTE IZQUIERDO: DIAGRAMA UNIFILAR GENERAL (MT -> TRAFO -> TABLERO BT)
    # ---------------------------------------------------------------------
    ax_uni = fig.add_axes([0.05, 0.06, 0.45, 0.88])
    ax_uni.axis('off')
    rect_uni = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.5)
    ax_uni.add_patch(rect_uni)
    
    ax_uni.text(0.5, 0.97, "DIAGRAMA UNIFILAR GENERAL — SUBESTACIÓN BIPOSTE 100 kVA", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1E3A8A')
    ax_uni.text(0.5, 0.945, "Alimentación MT 22.9 kV | Salidas BT 380/220 V (Circuitos C-1, C-2, C-3 y AP)", ha='center', va='center', fontsize=7.0, color='#64748B')
    ax_uni.plot([0.04, 0.96], [0.93, 0.93], color='#334155', linewidth=1.0)
    
    # Línea Primaria 22.9 kV
    ax_uni.plot([0.5, 0.5], [0.92, 0.85], color='#0284C7', linewidth=2.5)
    ax_uni.text(0.52, 0.89, "RED PRIMARIA 22.9 kV (Electro Puno)\nTrifásico 3 Hilos — Conductor AAAC 35 mm²", fontsize=6.5, fontweight='bold', color='#0284C7')
    
    # Seccionador Cut-Out y Pararrayos
    # Pararrayos derivado a tierra
    ax_uni.plot([0.5, 0.35], [0.85, 0.85], color='#0284C7', linewidth=1.8)
    ax_uni.plot([0.35, 0.35], [0.85, 0.80], color='#0284C7', linewidth=1.8)
    ax_uni.plot([0.33, 0.37], [0.80, 0.80], color='#DC2626', linewidth=2.5)
    ax_uni.plot([0.32, 0.38], [0.78, 0.78], color='#DC2626', linewidth=2.5)
    ax_uni.text(0.18, 0.79, "Pararrayos Óxido Metálico\n21 kV / 10 kA (Clase 1)", fontsize=5.8, color='#B91C1C')
    # Tierra de pararrayos
    ax_uni.plot([0.35, 0.35], [0.78, 0.74], color='#15803D', linewidth=1.5)
    ax_uni.plot([0.32, 0.38], [0.74, 0.74], color='#15803D', linewidth=1.8)
    ax_uni.plot([0.33, 0.37], [0.73, 0.73], color='#15803D', linewidth=1.5)
    ax_uni.text(0.39, 0.735, "PAT-3", fontsize=5.5, fontweight='bold', color='#15803D')
    
    # Cut-Out
    ax_uni.plot([0.5, 0.5], [0.85, 0.81], color='#0284C7', linewidth=1.8)
    rect_co = patches.Rectangle((0.47, 0.77), 0.06, 0.04, facecolor='#EFF6FF', edgecolor='#1D4ED8', linewidth=1.5)
    ax_uni.add_patch(rect_co)
    ax_uni.text(0.55, 0.79, "Seccionador Fusible Cut-Out\n27 kV / 100 A (Fusible Chicote K 4A)", fontsize=6.0, color='#1D4ED8')
    
    # Bajada al Transformador
    ax_uni.plot([0.5, 0.5], [0.77, 0.71], color='#0284C7', linewidth=1.8)
    
    # Símbolo Transformador (2 círculos intersecados)
    circle_mt = patches.Circle((0.5, 0.67), radius=0.035, facecolor='none', edgecolor='#DC2626', linewidth=2.0)
    circle_bt = patches.Circle((0.5, 0.62), radius=0.035, facecolor='none', edgecolor='#2563EB', linewidth=2.0)
    ax_uni.add_patch(circle_mt)
    ax_uni.add_patch(circle_bt)
    ax_uni.text(0.56, 0.66, "TRANSFORMADOR DE DISTRIBUCIÓN 100 kVA\nRelación: 22.9 / 0.38 - 0.22 kV\nGrupo: Dyn5 | Frecuencia: 60 Hz | ONAN\nCarga Máxima: 79.0 kVA (Reserva 21.0%)",
                fontsize=6.5, fontweight='bold', color='#991B1B')
    
    # Neutro de BT puesto a tierra
    ax_uni.plot([0.465, 0.40], [0.62, 0.62], color='#15803D', linewidth=1.5)
    ax_uni.plot([0.40, 0.40], [0.62, 0.58], color='#15803D', linewidth=1.5)
    ax_uni.plot([0.37, 0.43], [0.58, 0.58], color='#15803D', linewidth=1.8)
    ax_uni.plot([0.38, 0.42], [0.57, 0.57], color='#15803D', linewidth=1.5)
    ax_uni.text(0.24, 0.575, "Puesta a Tierra Neutro\nR <= 10 Ω (PAT-3)", fontsize=5.5, color='#15803D')

    # Bajada a Tablero de Distribución BT
    ax_uni.plot([0.5, 0.5], [0.585, 0.53], color='#2563EB', linewidth=2.5)
    
    # Caja Tablero General BT
    rect_tab = patches.Rectangle((0.10, 0.08), 0.80, 0.44, facecolor='#F8FAFC', edgecolor='#0F172A', linewidth=1.5)
    ax_uni.add_patch(rect_tab)
    ax_uni.text(0.5, 0.505, "TABLERO DE DISTRIBUCIÓN BT (Montaje Adosado a Poste — Grado IP65)", ha='center', fontsize=7.2, fontweight='bold', color='#0F172A')
    
    # Interruptor General Totalizador
    rect_gen = patches.Rectangle((0.44, 0.43), 0.12, 0.05, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.5)
    ax_uni.add_patch(rect_gen)
    ax_uni.text(0.5, 0.455, "INTERRUPTOR GENERAL 3x160 A\nTermomagnético Regulable (Icu = 25 kA)", ha='center', va='center', fontsize=5.8, fontweight='bold', color='#92400E')
    
    # Barra de distribución BT
    ax_uni.plot([0.5, 0.5], [0.43, 0.38], color='#2563EB', linewidth=2.0)
    ax_uni.plot([0.18, 0.82], [0.38, 0.38], color='#1E293B', linewidth=3.5)
    ax_uni.text(0.84, 0.38, "BARRA 380/220 V", va='center', fontsize=6.0, fontweight='bold', color='#1E293B')
    
    # Derivaciones a 4 circuitos: C-1, C-2, C-3 y AP
    circuitos_info = [
        (0.24, "C-1", "3x80 A", "Troncal Norte (Playa)\n38 usuarios | 34.6 kW\nCAAI 3x35+25+16 mm²\nL = 819.7 m | ΔV = 3.82%"),
        (0.42, "C-2", "3x50 A", "Sector Centro\n20 usuarios | 18.2 kW\nCAAI 3x25+25+16 mm²\nL = 184.4 m | ΔV = 1.15%"),
        (0.60, "C-3", "3x50 A", "Sector Sur (Playa Sur)\n20 usuarios | 18.2 kW\nCAAI 3x25+25+16 mm²\nL = 284.8 m | ΔV = 1.76%"),
        (0.76, "AP", "2x16 A", "Alumbrado Público\n15 Luminarias LED 60W\nContactor 25A + Fotocelda\nCAAI 1x16 mm²")
    ]
    for x_c, c_id, itm, detalle in circuitos_info:
        # Bajante desde barra
        ax_uni.plot([x_c, x_c], [0.38, 0.33], color='#2563EB', linewidth=1.8)
        # Termomagnético
        rect_it = patches.Rectangle((x_c - 0.05, 0.27), 0.10, 0.06, facecolor='#FFFFFF', edgecolor='#2563EB', linewidth=1.2)
        ax_uni.add_patch(rect_it)
        ax_uni.text(x_c, 0.30, f"ITM {c_id}\n{itm}", ha='center', va='center', fontsize=5.5, fontweight='bold', color='#1E3A8A')
        # Salida hacia la red
        ax_uni.plot([x_c, x_c], [0.27, 0.20], color='#2563EB', linewidth=1.8)
        ax_uni.plot(x_c, 0.20, marker='v', color='#2563EB', markersize=6.0)
        ax_uni.text(x_c, 0.14, detalle, ha='center', va='top', fontsize=5.0, color='#334155')

    # ---------------------------------------------------------------------
    # CUADRANTE DERECHO SUPERIOR: DETALLES DE MONTAJE DE RETENIDAS Y PAT
    # ---------------------------------------------------------------------
    ax_det1 = fig.add_axes([0.53, 0.52, 0.44, 0.42])
    ax_det1.axis('off')
    rect_det1 = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.2)
    ax_det1.add_patch(rect_det1)
    
    ax_det1.text(0.5, 0.95, "DETALLES TÍPICOS DE MONTAJE ELECTROMECÁNICO", ha='center', fontsize=8.5, fontweight='bold', color='#1E3A8A')
    ax_det1.plot([0.05, 0.95], [0.90, 0.90], color='#334155', linewidth=0.8)
    
    # Subpanel Detalle 1: Retenida Mecánica R-1
    ax_det1.text(0.25, 0.85, "DETALLE DE RETENIDA INCLINADA (R-1)", ha='center', fontsize=7.0, fontweight='bold', color='#EA580C')
    # Poste
    ax_det1.plot([0.08, 0.08], [0.15, 0.80], color='#64748B', linewidth=4.0)
    ax_det1.text(0.04, 0.50, "Poste C.A.C.\n8m / 12m", rotation=90, fontsize=5.5, color='#475569')
    # Cable de retenida
    ax_det1.plot([0.08, 0.40], [0.72, 0.15], color='#EA580C', linewidth=2.0)
    # Aislador de tracción 54-1
    rect_ais = patches.Rectangle((0.21, 0.47), 0.04, 0.04, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.0)
    ax_det1.add_patch(rect_ais)
    ax_det1.text(0.26, 0.52, "Aislador Tracción\nPorcelana 54-1", fontsize=5.0, color='#92400E')
    # Varilla y bloque de concreto
    ax_det1.plot([0.40, 0.43], [0.15, 0.08], color='#334155', linewidth=2.5)
    rect_blq = patches.Rectangle((0.38, 0.04), 0.10, 0.05, facecolor='#94A3B8', edgecolor='#1E293B', linewidth=1.0)
    ax_det1.add_patch(rect_blq)
    ax_det1.text(0.44, 0.18, "Varilla Anclaje Ø5/8\"x2.4m\nBloque Concreto 0.5x0.5x0.2m", fontsize=5.0, color='#0F172A')

    # Subpanel Detalle 2: Pozo de Puesta a Tierra (PAT-3 / PAT-1)
    ax_det1.text(0.75, 0.85, "POZO DE PUESTA A TIERRA (PAT-3)", ha='center', fontsize=7.0, fontweight='bold', color='#15803D')
    # Caja de registro
    rect_caj = patches.Rectangle((0.68, 0.65), 0.16, 0.12, facecolor='#F1F5F9', edgecolor='#334155', linewidth=1.2)
    ax_det1.add_patch(rect_caj)
    ax_det1.text(0.76, 0.73, "Caja de Registro\n0.30 x 0.30 m", ha='center', fontsize=5.2, color='#334155')
    # Jabalina de cobre
    ax_det1.plot([0.76, 0.76], [0.70, 0.12], color='#B45309', linewidth=3.5)
    ax_det1.text(0.78, 0.38, "Electrodo Cobre\nØ5/8\" x 2.40 m", fontsize=5.2, fontweight='bold', color='#B45309')
    # Tratamiento con bentonita
    rect_bent = patches.Rectangle((0.65, 0.10), 0.22, 0.55, facecolor='#DCFCE7', edgecolor='#15803D', linestyle='--', linewidth=1.0, alpha=0.5)
    ax_det1.add_patch(rect_bent)
    ax_det1.text(0.65, 0.05, "Tratamiento: Bentonita Sódica (30 kg) + Thor-Gel\nResistencia Garantizada: R <= 10 Ω (SED) | R <= 25 Ω (BT)", fontsize=5.2, color='#15803D')

    # ---------------------------------------------------------------------
    # CUADRANTE DERECHO INFERIOR: DETALLE DE ACOMETIDA MONOFÁSICA Y RÓTULO
    # ---------------------------------------------------------------------
    ax_det2 = fig.add_axes([0.53, 0.06, 0.20, 0.43])
    ax_det2.axis('off')
    rect_det2 = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.2)
    ax_det2.add_patch(rect_det2)
    ax_det2.text(0.5, 0.94, "ACOMETIDA DOMICILIARIA TÍPICA", ha='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')
    ax_det2.plot([0.05, 0.95], [0.88, 0.88], color='#334155', linewidth=0.8)
    
    # Poste BT
    ax_det2.plot([0.15, 0.15], [0.10, 0.85], color='#22C55E', linewidth=3.5)
    ax_det2.text(0.15, 0.88, "Poste BT", ha='center', fontsize=5.0, color='#15803D')
    # Cable concéntrico
    ax_det2.plot([0.15, 0.70], [0.75, 0.60], color='#475569', linewidth=1.5, linestyle='--')
    ax_det2.text(0.42, 0.72, "Cable Concéntrico\nSET 2x4 mm²", fontsize=5.0, color='#334155')
    # Mureta / Vivienda
    rect_mur = patches.Rectangle((0.68, 0.10), 0.24, 0.65, facecolor='#F8FAFC', edgecolor='#64748B', linewidth=1.2)
    ax_det2.add_patch(rect_mur)
    # Caja portamedidor
    rect_med = patches.Rectangle((0.72, 0.40), 0.16, 0.18, facecolor='#FEE2E2', edgecolor='#DC2626', linewidth=1.2)
    ax_det2.add_patch(rect_med)
    ax_det2.text(0.80, 0.51, "CAJA L-M\nMedidor Monof.\nITM 2x16 A", ha='center', va='center', fontsize=4.8, fontweight='bold', color='#991B1B')
    ax_det2.text(0.80, 0.25, "Mureta de\nConcreto\n(H = 1.80 m)", ha='center', fontsize=4.8, color='#475569')

    # Rótulo Oficial de Ingeniería Lámina U-01
    dibujar_rotulo_oficial(fig.add_axes([0.74, 0.06, 0.23, 0.43]), 0, 0, 1, 1,
                          plano_cod="U-01",
                          plano_nom="DIAGRAMA UNIFILAR GENERAL Y DETALLES\nDE MONTAJE ELECTROMECÁNICO",
                          escala="INDICADA")

    fig.savefig(salida_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"Lámina U-01 generada exitosamente en: {salida_pdf}")


# =========================================================================
# LÁMINA PL-01: PERFIL LONGITUDINAL LÍNEA PRIMARIA (A3 HORIZONTAL)
# =========================================================================
def generar_lamina_pl01(salida_pdf):
    # Datos de los 9 postes de MT
    postes_mt_data = [
        ("E-01", 0.00, 3924.17, "PR-1 (12/400)", "Derivación Electro Puno - Ret. Inclinada / PAT-3"),
        ("E-02", 105.00, 3895.00, "PS-1 (12/300)", "Suspensión Alineamiento"),
        ("E-03", 210.00, 3865.00, "PS-1 (12/300)", "Suspensión Alineamiento"),
        ("E-04", 305.21, 3839.56, "SAB-1 (2x13/400)", "SED Biposte 100 kVA - Ret. Contraviento / PAT-3"),
        ("E-05", 402.43, 3817.04, "PA-1 (12/400)", "Ángulo 36° - Ret. Biselar"),
        ("E-06", 518.02, 3827.27, "PA-1 (12/400)", "Ángulo 31° - Ret. Biselar"),
        ("E-07", 628.53, 3824.61, "PS-1 (12/300)", "Suspensión"),
        ("E-08", 708.34, 3824.61, "PA-1 (12/300)", "Ángulo 33° - Ret. Biselar"),
        ("E-09", 816.60, 3824.61, "PR-1 (12/400)", "Terminal Fin de Línea - Ret. Inclinada / PAT-3")
    ]
    
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    ax_prof = fig.add_axes([0.06, 0.38, 0.90, 0.55])
    
    progs = [p[1] for p in postes_mt_data]
    cotas = [p[2] for p in postes_mt_data]
    
    # Terreno
    ax_prof.plot(progs, cotas, color='#78350F', linewidth=2.5, label='Perfil del Terreno Natural (msnm)')
    ax_prof.fill_between(progs, cotas, 3780, color='#FEF3C7', alpha=0.35)
    
    # Postes y Catenarias
    h_poste = 11.0  # Altura libre sobre terreno
    for name, prog, cota, armado, desc in postes_mt_data:
        # Dibujar poste vertical
        ax_prof.plot([prog, prog], [cota, cota + h_poste], color='#1E293B', linewidth=3.0)
        ax_prof.plot(prog, cota + h_poste, marker='^', color='#DC2626', markersize=8.0)
        ax_prof.text(prog, cota + h_poste + 2.5, f"{name}\n{armado}", ha='center', fontsize=6.0, fontweight='bold', color='#1E3A8A')
        
    # Catenarias parabólicas entre postes
    for i in range(len(postes_mt_data) - 1):
        x1, y1 = progs[i], cotas[i] + h_poste
        x2, y2 = progs[i+1], cotas[i+1] + h_poste
        vano = x2 - x1
        xs = [x1 + vano * k / 30.0 for k in range(31)]
        # Ecuación de flecha máxima a +35°C
        flecha = 0.00035 * (vano**2)
        ys = [y1 + (y2 - y1)*(x - x1)/vano - 4.0 * flecha * ((x - x1)/vano) * (1.0 - (x - x1)/vano) for x in xs]
        ax_prof.plot(xs, ys, color='#2563EB', linewidth=1.8)
        # Línea de gálibo CNE (6.5m sobre terreno)
        ys_gal = [cotas[i] + (cotas[i+1] - cotas[i])*(x - x1)/vano + 6.5 for x in xs]
        ax_prof.plot(xs, ys_gal, color='#16A34A', linestyle=':', linewidth=1.0)

    ax_prof.set_xlim(-20, 850)
    ax_prof.set_ylim(3800, 3950)
    ax_prof.set_ylabel("Cota (msnm)", fontsize=8.5, fontweight='bold')
    ax_prof.grid(True, linestyle='--', color='#94A3B8', alpha=0.5)
    ax_prof.set_title("PERFIL TOPOGRÁFICO LONGITUDINAL, DISTRIBUCIÓN DE ESTRUCTURAS Y CATENARIAS — LÍNEA PRIMARIA 22.9 kV\nCONDUCCIÓN: CONDUCTOR AAAC 35 mm² | LÍNEA VERDE: DISTANCIA MÍNIMA DE SEGURIDAD CNE (6.50 m SOBRE SUELO)",
                      fontsize=9.5, fontweight='bold', color='#0F172A', pad=10)

    # ---------------------------------------------------------------------
    # GUITARRA DE DATOS TOPOGRÁFICOS EN PARTE INFERIOR
    # ---------------------------------------------------------------------
    ax_guit = fig.add_axes([0.06, 0.06, 0.62, 0.28])
    ax_guit.axis('off')
    rect_guit = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.2)
    ax_guit.add_patch(rect_guit)
    
    filas_guit = [
        "ESTRUCTURA",
        "ARMADO DGE",
        "POSTE C.A.C.",
        "COTA TERRENO (m)",
        "VANO PARCIAL (m)",
        "PROGRESIVA (m)",
        "RETENIDA / PAT"
    ]
    n_f = len(filas_guit)
    for i in range(1, n_f):
        ax_guit.plot([0, 1], [i / float(n_f), i / float(n_f)], color='#64748B', linewidth=0.6)
    ax_guit.plot([0.18, 0.18], [0, 1], color='#0F172A', linewidth=1.2)
    
    for idx, f_nom in enumerate(filas_guit):
        y_f = (n_f - 1 - idx + 0.5) / float(n_f)
        ax_guit.text(0.01, y_f, f_nom, va='center', fontsize=6.0, fontweight='bold', color='#1E293B')
        
    # Llenar datos de cada poste
    dx_col = 0.80 / float(len(postes_mt_data))
    for p_i, (p_id, prog, cota, arm, desc) in enumerate(postes_mt_data):
        x_c = 0.19 + p_i * dx_col + dx_col / 2.0
        vano_p = f"{prog - postes_mt_data[p_i-1][1]:.1f}" if p_i > 0 else "0.0"
        ret_pat = "RET / PAT" if "PAT" in desc else ("RET" if "Ret" in desc else "---")
        
        datos_col = [p_id, arm.split()[0], arm.split('(')[1].replace(')', '') if '(' in arm else "12m", f"{cota:.1f}", vano_p, f"{prog:.1f}", ret_pat]
        for f_idx, d_val in enumerate(datos_col):
            y_f = (n_f - 1 - f_idx + 0.5) / float(n_f)
            ax_guit.text(x_c, y_f, d_val, ha='center', va='center', fontsize=5.5, color='#0F172A')

    # Rótulo Oficial de Ingeniería Lámina PL-01
    dibujar_rotulo_oficial(fig.add_axes([0.70, 0.06, 0.26, 0.28]), 0, 0, 1, 1,
                          plano_cod="PL-01",
                          plano_nom="PERFIL LONGITUDINAL TOPOGRÁFICO Y\nDISTRIBUCIÓN DE ESTRUCTURAS LP 22.9 kV",
                          escala="H: 1/2000 | V: 1/500")

    fig.savefig(salida_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"Lámina PL-01 generada exitosamente en: {salida_pdf}")


if __name__ == "__main__":
    out_dir = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\entregables\planos"
    os.makedirs(out_dir, exist_ok=True)
    
    pdf_p01 = os.path.join(out_dir, "plano_P01_redes_planta.pdf")
    pdf_u01 = os.path.join(out_dir, "plano_U01_diagrama_unifilar_detalles.pdf")
    pdf_pl01 = os.path.join(out_dir, "plano_PL01_perfil_longitudinal.pdf")
    
    generar_lamina_p01(pdf_p01)
    generar_lamina_u01(pdf_u01)
    generar_lamina_pl01(pdf_pl01)
