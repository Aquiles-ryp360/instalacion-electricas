# -*- coding: utf-8 -*-
"""
generar_plano_planta_redes_dxf.py
Genera el Plano General de Redes de Distribución en Planta (Georreferenciado UTM WGS-84 Zona 19S)
en formato AutoCAD DXF R2010 con simbología estrictamente normalizada UNE-EN 60617 y Norma DGE Perú:
1. Traza de Línea Primaria MT (22.9 kV, AAAC 35 mm²) y Subestación Biposte SAB-1 (100 kVA, 22.9/0.38-0.22 kV).
2. Traza de Red Secundaria BT (380/220 V) con exactamente 2 CIRCUITOS DE DISTRIBUCIÓN:
   - Circuito C-1: Troncal Norte hacia la Playa de Chifrón (Ruta 1 - 820.0 m, 56 usuarios proyectados, incluye C31).
   - Circuito C-2: Troncal Carretera al Fondo continua (Rutas 3 y 4 - 456.0 m, 22 usuarios proyectados).
3. Postes C.A.C. limpios (DGE 09-91-20 / UNE 11-11-01) con identificación limpia.
4. Alumbrado Público UNE-EN 60617-11 nº 11-15-03 (círculo con 'X' inscrita en pastoral, sin textos flotantes).
5. Puestas a tierra UNE-EN 60617-2 nº 02-15-01 (3 barras paralelas decrecientes, sin textos flotantes en planta).
6. Retenidas DGE 09-91-18 / UNE 11-11-01 (tirante, aislador 54-1 y ancla, sin textos flotantes en planta).
7. Acometidas domiciliarias concéntricas aéreas SET 2x4 mm² y cajas portamedidor monofásico "M" para 43 abonados.
8. Leyenda oficial técnica UNE/DGE, planilla de estructuras y cuadro resumen de cargas de los 2 circuitos.

Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
Curso: MEC330 - Instalaciones Eléctricas II | FIME - UNA Puno
"""

import os
import math
import csv
import xml.etree.ElementTree as ET
import ezdxf
from ezdxf import colors

def latlon_to_utm(lat, lon):
    """Conversión de coordenadas geográficas WGS-84 a UTM Zona 19S."""
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

# Subestación de Distribución Biposte SAB-1 (100 kVA, 22.9/0.38-0.22 kV)
POSTES_MT = [
    {
        "id": "SAB-1",
        "este": 412606.01,
        "norte": 8270712.24,
        "tipo": "2xC.A.C. 13/400 (Biposte)",
        "armado": "SAB-1",
        "pat": "PAT-3",
        "ret": "RET-CV",
        "ret_az": 210.0,
        "desc": "Subestación Biposte 100 kVA (22.9/0.38-0.22 kV Dyn5)"
    }
]

# Línea Primaria MT 22.9 kV (Alimentación Electro Puno)
TRAZA_MT = [
    (412380.00, 8270740.00),
    (412490.00, 8270725.00),
    (412606.01, 8270712.24)
]

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
            coords_text = ls.find('kml:coordinates', ns).text.strip()
            pts = []
            for c in coords_text.split():
                if c.strip():
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
        for row in reader:
            cod = row['codigo_abonado']
            lat = float(row['lat_centroide'])
            lon = float(row['lon_centroide'])
            e, n = latlon_to_utm(lat, lon)
            abonados.append({"cod": cod, "este": e, "norte": n})
    return abonados

def generar_postes_bt(rutas):
    """
    Genera la distribución de postes de Baja Tensión (C.A.C. 8/200)
    para exactamente los 2 CIRCUITOS DE DISTRIBUCIÓN:
    - Circuito C-1: Troncal Norte hacia la Playa de Chifrón (Ruta 1 - 820.0 m, 56 hab, incluye C31).
    - Circuito C-2: Troncal Carretera al Fondo continua (Rutas 3 y 4 - 456.0 m, 22 hab).
    """
    postes_bt = []
    
    # 1. Circuito C-1 (Ruta 1)
    if 'ruta electrica 1' in rutas:
        pts1 = rutas['ruta electrica 1']
        p_idx = 1
        for i in range(len(pts1) - 1):
            p1 = pts1[i]
            p2 = pts1[i+1]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            n_seg = max(1, int(math.ceil(dist / 38.0)))
            for s in range(n_seg if i == len(pts1)-2 else n_seg):
                ts = s / float(n_seg)
                xe = p1[0] + ts * (p2[0] - p1[0])
                yn = p1[1] + ts * (p2[1] - p1[1])
                if math.hypot(xe - 412606.01, yn - 8270712.24) < 5.0 and len(postes_bt) > 0:
                    continue
                pid = f"P1-{p_idx:02d}"
                es_extremo = (s == 0 and i == 0) or (i == len(pts1)-2 and s == n_seg)
                pat = "PAT-1" if (p_idx % 4 == 0 or es_extremo) else None
                ret = "RET-I" if (es_extremo or p_idx in [6, 12, 18]) else None
                # Exactamente 10 luminarias de AP en C-1
                ap = True if p_idx in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19] else False
                postes_bt.append({
                    "id": pid, "circuito": "C-1", "este": xe, "norte": yn,
                    "pat": pat, "ret": ret, "ap": ap, "dx_ap": -3.5, "dy_ap": 1.5
                })
                p_idx += 1
                
    # 2. Circuito C-2 (Rutas 3 y 4 continuas)
    pts_c2 = []
    if 'ruta electrica 3' in rutas:
        pts_c2 += rutas['ruta electrica 3']
    if 'ruta electrica 4' in rutas:
        pts_c2 += rutas['ruta electrica 4']
    p_idx2 = 1
    for i in range(len(pts_c2) - 1):
        p1 = pts_c2[i]
        p2 = pts_c2[i+1]
        dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        n_seg = max(1, int(math.ceil(dist / 38.0)))
        for s in range(n_seg if i == len(pts_c2)-2 else n_seg):
            ts = s / float(n_seg)
            xe = p1[0] + ts * (p2[0] - p1[0])
            yn = p1[1] + ts * (p2[1] - p1[1])
            if math.hypot(xe - 412606.01, yn - 8270712.24) < 5.0 and len(postes_bt) > 0:
                continue
            pid = f"P2-{p_idx2:02d}"
            es_extremo = (s == 0 and i == 0) or (i == len(pts_c2)-2 and s == n_seg)
            pat = "PAT-1" if (p_idx2 % 4 == 0 or es_extremo) else None
            ret = "RET-I" if (es_extremo or p_idx2 in [4, 8]) else None
            # Exactamente 5 luminarias de AP en C-2
            ap = True if p_idx2 in [1, 3, 6, 9, 12] else False
            postes_bt.append({
                "id": pid, "circuito": "C-2", "este": xe, "norte": yn,
                "pat": pat, "ret": ret, "ap": ap, "dx_ap": 3.5, "dy_ap": -1.5
            })
            p_idx2 += 1
            
    return postes_bt

def dibujar_bloque_poste_dxf(msp, x, y, pid, ap=False, dx_ap=3.5, dy_ap=0.0):
    """
    Dibuja un poste C.A.C. normalizado DGE 09-91-20 / UNE 11-11-01:
    - Círculo limpio con centro definido.
    - Símbolo oficial de luminaria AP (UNE 11-15-03: círculo con 'X' inscrita).
    - SIN textos flotantes innecesarios para evitar solapes.
    """
    # Círculo base del poste (limpio DGE)
    msp.add_circle((x, y), radius=1.0, dxfattribs={"layer": "POSTES_BT", "color": colors.GREEN, "lineweight": 25})
    # Punto central geodésico
    msp.add_line((x - 0.25, y), (x + 0.25, y), dxfattribs={"layer": "POSTES_BT", "color": colors.GREEN, "lineweight": 15})
    msp.add_line((x, y - 0.25), (x, y + 0.25), dxfattribs={"layer": "POSTES_BT", "color": colors.GREEN, "lineweight": 15})
    # Rótulo del poste
    msp.add_text(pid, dxfattribs={"layer": "TEXTOS_ROTULOS", "height": 1.3, "color": colors.GREEN}).set_placement((x + 1.4, y + 0.8))
    
    # Brazo Pastoral y Luminaria UNE-EN 60617-11 nº 11-15-03
    if ap:
        x_lum = x + dx_ap
        y_lum = y + dy_ap
        # Brazo pastoral de F° G°
        msp.add_line((x, y), (x_lum, y_lum), dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW, "lineweight": 20})
        # Círculo de luminaria
        r_l = 0.6
        msp.add_circle((x_lum, y_lum), radius=r_l, dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW, "lineweight": 25})
        # Aspa 'X' normalizada inscrita (UNE 11-15-03)
        d = r_l * 0.707
        msp.add_line((x_lum - d, y_lum - d), (x_lum + d, y_lum + d), dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW, "lineweight": 15})
        msp.add_line((x_lum - d, y_lum + d), (x_lum + d, y_lum - d), dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW, "lineweight": 15})

def dibujar_simbolo_pat(msp, x, y):
    """Dibuja el símbolo oficial UNE-EN 60617-2 nº 02-15-01 de Puesta a Tierra (3 barras horizontales decrecientes)."""
    # Conductor vertical de bajada
    msp.add_line((x, y), (x, y - 2.0), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3})
    # 3 barras de tierra decrecientes
    msp.add_line((x - 1.6, y - 2.0), (x + 1.6, y - 2.0), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3, "lineweight": 25})
    msp.add_line((x - 1.0, y - 2.6), (x + 1.0, y - 2.6), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3, "lineweight": 25})
    msp.add_line((x - 0.4, y - 3.2), (x + 0.4, y - 3.2), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3, "lineweight": 25})

def dibujar_simbolo_retenida(msp, x, y, az_grados):
    """Dibuja el tirante de retenida normalizado DGE 09-91-18 con aislador y bloque de anclaje."""
    rad = math.radians(az_grados)
    long_cable = 8.0
    dx = long_cable * math.sin(rad)
    dy = long_cable * math.cos(rad)
    x_ancla = x + dx
    y_ancla = y + dy
    # Cable de retenida
    msp.add_line((x, y), (x_ancla, y_ancla), dxfattribs={"layer": "RETENIDAS", "color": 30, "lineweight": 20})
    # Aislador de porcelana 54-1 a media altura
    xm = (x + x_ancla) / 2.0
    ym = (y + y_ancla) / 2.0
    d_ais = 0.4
    msp.add_lwpolyline([(xm-d_ais, ym-d_ais), (xm+d_ais, ym-d_ais), (xm+d_ais, ym+d_ais), (xm-d_ais, ym+d_ais), (xm-d_ais, ym-d_ais)],
                       dxfattribs={"layer": "RETENIDAS", "color": 30, "lineweight": 25})
    # Bloque de concreto perpendicular
    rad_perp = rad + math.pi / 2.0
    dx_p = 1.6 * math.sin(rad_perp)
    dy_p = 1.6 * math.cos(rad_perp)
    msp.add_line((x_ancla - dx_p, y_ancla - dy_p), (x_ancla + dx_p, y_ancla + dy_p), dxfattribs={"layer": "RETENIDAS", "color": 30, "lineweight": 35})

def dibujar_medidor_abonado(msp, x, y, cod):
    """Dibuja la caja portamedidor monofásica normalizada M y rótulo de abonado."""
    d = 0.9
    pts = [(x-d, y-d), (x+d, y-d), (x+d, y+d), (x-d, y+d), (x-d, y-d)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": "MEDIDORES_ACOMETIDAS", "color": 1})
    msp.add_circle((x, y), radius=0.6, dxfattribs={"layer": "MEDIDORES_ACOMETIDAS", "color": 1})
    msp.add_text("M", dxfattribs={"layer": "MEDIDORES_ACOMETIDAS", "height": 0.8, "color": 1}).set_placement((x - 0.25, y - 0.35))
    if cod:
        msp.add_text(cod, dxfattribs={"layer": "TEXTOS_ROTULOS", "height": 1.3, "color": 7}).set_placement((x + 1.2, y + 0.5))

def generar_plano_completo_planta(dxf_out):
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()
    
    # Capas Normalizadas CAD
    capas = [
        ("RED_PRIMARIA_MT", colors.CYAN),
        ("RED_SECUNDARIA_BT", colors.MAGENTA),
        ("ALUMBRADO_PUBLICO", colors.YELLOW),
        ("POSTES_MT", colors.YELLOW),
        ("POSTES_BT", colors.GREEN),
        ("ACOMETIDAS_DOMICILIARIAS", colors.BLUE),
        ("MEDIDORES_ACOMETIDAS", colors.RED),
        ("PUESTAS_A_TIERRA", 3),
        ("RETENIDAS", 30),
        ("VIAS_ACCESO", 8),
        ("TEXTOS_ROTULOS", colors.WHITE),
        ("MEMBRETE_LEYENDA", colors.WHITE)
    ]
    for c_nom, c_col in capas:
        if c_nom not in doc.layers:
            doc.layers.add(c_nom, color=c_col)

    # 1. Rutas y Vías KML
    kml_path = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\fuentes\kml\topografia_capachica_chifron.kml"
    csv_path = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\datos\cargas\censo_43_abonados.csv"
    
    rutas, vias = cargar_rutas_kml(kml_path)
    abonados = cargar_abonados_csv(csv_path)
    
    # Dibujar Vías
    for v_nom, pts in vias:
        for i in range(len(pts) - 1):
            msp.add_line(pts[i], pts[i+1], dxfattribs={"layer": "VIAS_ACCESO", "color": 8, "lineweight": 13})

    # 2. Línea Primaria MT 22.9 kV
    for i in range(len(TRAZA_MT) - 1):
        msp.add_line(TRAZA_MT[i], TRAZA_MT[i+1], dxfattribs={"layer": "RED_PRIMARIA_MT", "color": colors.CYAN, "lineweight": 40})
        # Textos de tramo MT
        p1, p2 = TRAZA_MT[i], TRAZA_MT[i+1]
        dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
        xm = (p1[0] + p2[0]) / 2.0
        ym = (p1[1] + p2[1]) / 2.0
        msp.add_text(f"LP 22.9 kV AAAC 35mm2 (L={dist:.1f}m)", dxfattribs={"layer": "RED_PRIMARIA_MT", "height": 1.6, "color": colors.CYAN}).set_placement((xm - 15.0, ym + 2.5))

    # Subestación Biposte SAB-1
    for p_mt in POSTES_MT:
        x, y = p_mt["este"], p_mt["norte"]
        # Dos postes de la SED (C.A.C. 13/400)
        msp.add_circle((x - 1.5, y), radius=1.2, dxfattribs={"layer": "POSTES_MT", "color": colors.YELLOW, "lineweight": 35})
        msp.add_circle((x + 1.5, y), radius=1.2, dxfattribs={"layer": "POSTES_MT", "color": colors.YELLOW, "lineweight": 35})
        # Plataforma estructural portatransformador
        msp.add_line((x - 3.0, y - 0.7), (x + 3.0, y - 0.7), dxfattribs={"layer": "POSTES_MT", "color": colors.YELLOW, "lineweight": 25})
        msp.add_line((x - 3.0, y + 0.7), (x + 3.0, y + 0.7), dxfattribs={"layer": "POSTES_MT", "color": colors.YELLOW, "lineweight": 25})
        # Símbolo oficial de transformador UNE 06-09-01 (dos círculos entrelazados)
        msp.add_circle((x, y + 0.5), radius=1.0, dxfattribs={"layer": "POSTES_MT", "color": colors.RED, "lineweight": 25})
        msp.add_circle((x, y - 0.5), radius=1.0, dxfattribs={"layer": "POSTES_MT", "color": colors.BLUE, "lineweight": 25})
        msp.add_text("SED BIPOSTE SAB-1 (100 kVA - 22.9/0.38-0.22 kV)", dxfattribs={"layer": "TEXTOS_ROTULOS", "height": 1.8, "color": colors.YELLOW}).set_placement((x + 4.0, y + 2.0))
        # Puesta a tierra y retenida SED
        dibujar_simbolo_pat(msp, x - 3.5, y)
        dibujar_simbolo_retenida(msp, x + 3.5, y, p_mt["ret_az"])

    # 3. Red Secundaria BT (2 Circuitos)
    postes_bt = generar_postes_bt(rutas)
    
    # Líneas BT C-1
    if 'ruta electrica 1' in rutas:
        pts1 = rutas['ruta electrica 1']
        for i in range(len(pts1) - 1):
            msp.add_line(pts1[i], pts1[i+1], dxfattribs={"layer": "RED_SECUNDARIA_BT", "color": colors.MAGENTA, "lineweight": 35})
        # Rótulo C-1
        p_mid = pts1[len(pts1)//2]
        msp.add_text("CIRCUITO C-1 (Troncal Norte CAAI 3x35+25+16 mm2 - L=820m)", dxfattribs={"layer": "RED_SECUNDARIA_BT", "height": 1.6, "color": colors.MAGENTA}).set_placement((p_mid[0] + 3.0, p_mid[1] + 2.0))

    # Líneas BT C-2
    pts_c2 = []
    if 'ruta electrica 3' in rutas:
        pts_c2 += rutas['ruta electrica 3']
    if 'ruta electrica 4' in rutas:
        pts_c2 += rutas['ruta electrica 4']
    if pts_c2:
        msp.add_line((412606.01, 8270712.24), pts_c2[0], dxfattribs={"layer": "RED_SECUNDARIA_BT", "color": colors.MAGENTA, "lineweight": 35})
        for i in range(len(pts_c2) - 1):
            msp.add_line(pts_c2[i], pts_c2[i+1], dxfattribs={"layer": "RED_SECUNDARIA_BT", "color": colors.MAGENTA, "lineweight": 35})
        # Rótulo C-2
        p_mid2 = pts_c2[len(pts_c2)//2]
        msp.add_text("CIRCUITO C-2 (Carretera Fondo CAAI 3x25+25+16 mm2 - L=456m)", dxfattribs={"layer": "RED_SECUNDARIA_BT", "height": 1.6, "color": colors.MAGENTA}).set_placement((p_mid2[0] + 3.0, p_mid2[1] + 2.0))

    # 4. Postes BT y Equipamiento Asociado
    for p in postes_bt:
        x, y = p["este"], p["norte"]
        dibujar_bloque_poste_dxf(msp, x, y, p["id"], ap=p["ap"], dx_ap=p["dx_ap"], dy_ap=p["dy_ap"])
        if p["pat"]:
            dibujar_simbolo_pat(msp, x, y - 1.5)
        if p["ret"]:
            az_ret = 45.0 if p["circuito"] == "C-1" else 225.0
            dibujar_simbolo_retenida(msp, x, y, az_ret)

    # 5. Acometidas Domiciliarias a los 43 Abonados
    total_long_acometidas = 0.0
    for ab in abonados:
        xe_ab, yn_ab = ab["este"], ab["norte"]
        if ab["cod"] == "C31":
            cand = [p for p in postes_bt if p["circuito"] == "C-1"]
        elif int(ab["cod"][1:]) <= 30:
            cand = [p for p in postes_bt if p["circuito"] == "C-1"]
        else:
            cand = [p for p in postes_bt if p["circuito"] == "C-2"]
            
        p_cercano = min(cand, key=lambda p: math.hypot(xe_ab - p["este"], yn_ab - p["norte"]))
        p_e, p_n = p_cercano["este"], p_cercano["norte"]
        dist_min = math.hypot(xe_ab - p_e, yn_ab - p_n)
        
        total_long_acometidas += dist_min
        msp.add_line((p_e, p_n), (xe_ab, yn_ab), dxfattribs={"layer": "ACOMETIDAS_DOMICILIARIAS", "color": colors.BLUE, "lineweight": 18})
        dibujar_medidor_abonado(msp, xe_ab, yn_ab, ab["cod"])
        
        xm = (p_e + xe_ab) / 2.0
        ym = (p_n + yn_ab) / 2.0
        msp.add_text(f"Acom. {dist_min:.1f}m", dxfattribs={"layer": "ACOMETIDAS_DOMICILIARIAS", "height": 0.9, "color": colors.BLUE}).set_placement((xm + 0.3, ym + 0.3))

    # 6. Cuadro de Simbología y Leyenda Normalizada DGE
    x_leg = 412500.0
    y_leg = 8270860.0
    w_leg = 105.0
    h_leg = 145.0
    
    pts_leg = [(x_leg, y_leg), (x_leg + w_leg, y_leg), (x_leg + w_leg, y_leg - h_leg), (x_leg, y_leg - h_leg), (x_leg, y_leg)]
    msp.add_lwpolyline(pts_leg, dxfattribs={"layer": "MEMBRETE_LEYENDA", "color": colors.WHITE, "lineweight": 30})
    msp.add_text("SIMBOLOGÍA NORMALIZADA UNE-EN 60617 / DGE-MEM", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 2.6, "color": colors.YELLOW}).set_placement((x_leg + 4.0, y_leg - 6.0))
    msp.add_line((x_leg, y_leg - 9.0), (x_leg + w_leg, y_leg - 9.0), dxfattribs={"layer": "MEMBRETE_LEYENDA"})

    items_leyenda = [
        ("RED PRIMARIA MT 22.9 kV (AAAC 35 mm2)", "RED_PRIMARIA_MT", colors.CYAN, "LINEA"),
        ("CIRCUITO C-1 BT TRONCAL NORTE + C31 (CAAI 3x35+25+16 mm2)", "RED_SECUNDARIA_BT", colors.MAGENTA, "LINEA"),
        ("CIRCUITO C-2 BT CARRETERA AL FONDO (CAAI 3x25+25+16 mm2)", "RED_SECUNDARIA_BT", colors.MAGENTA, "LINEA"),
        ("ACOMETIDA DOMICILIARIA CONCÉNTRICA (SET 2x4 mm2)", "ACOMETIDAS_DOMICILIARIAS", colors.BLUE, "LINEA"),
        ("POSTE C.A.C. MEDIA TENSIÓN 13m/400daN (DGE 09-91-20)", "POSTES_MT", colors.YELLOW, "CIRCULO_MT"),
        ("POSTE C.A.C. BAJA TENSIÓN 8m/200daN (DGE 09-91-20)", "POSTES_BT", colors.GREEN, "POSTE_DGE"),
        ("PASTORAL CON LUMINARIA LED 60W AP (UNE 11-15-03)", "ALUMBRADO_PUBLICO", colors.YELLOW, "POSTE_AP"),
        ("SUBESTACIÓN DISTRIBUCIÓN BIPOSTE 100 kVA (UNE 06-09-01)", "POSTES_MT", colors.YELLOW, "SED"),
        ("PUESTA A TIERRA NORMALIZADA PAT-1 / PAT-3 (UNE 02-15-01)", "PUESTAS_A_TIERRA", 3, "PAT"),
        ("RETENIDA DE ACERO SM 3/8\" CON ANCLA (DGE 09-91-18)", "RETENIDAS", 30, "RET"),
        ("CAJA PORTAMEDIDOR MONOFÁSICO DE ABONADO (DGE 09-91-30)", "MEDIDORES_ACOMETIDAS", colors.RED, "MEDIDOR"),
        ("VÍA DE ACCESO / CARRETERA AFIRMADA", "VIAS_ACCESO", 8, "LINEA")
    ]

    y_cur = y_leg - 15.0
    for texto, capa, col, tipo_simb in items_leyenda:
        xs = x_leg + 8.0
        if tipo_simb == "LINEA":
            msp.add_line((xs - 4.0, y_cur), (xs + 4.0, y_cur), dxfattribs={"layer": capa, "color": col, "lineweight": 30})
        elif tipo_simb == "CIRCULO_MT":
            msp.add_circle((xs, y_cur), radius=1.4, dxfattribs={"layer": capa, "color": col})
        elif tipo_simb == "POSTE_DGE":
            msp.add_circle((xs, y_cur), radius=1.0, dxfattribs={"layer": capa, "color": col})
            msp.add_line((xs - 0.25, y_cur), (xs + 0.25, y_cur), dxfattribs={"layer": capa, "color": col})
            msp.add_line((xs, y_cur - 0.25), (xs, y_cur + 0.25), dxfattribs={"layer": capa, "color": col})
        elif tipo_simb == "POSTE_AP":
            msp.add_circle((xs, y_cur), radius=0.9, dxfattribs={"layer": "POSTES_BT", "color": colors.GREEN})
            msp.add_line((xs, y_cur), (xs + 3.0, y_cur), dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW})
            msp.add_circle((xs + 3.0, y_cur), radius=0.6, dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW})
            msp.add_line((xs + 2.6, y_cur - 0.4), (xs + 3.4, y_cur + 0.4), dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW})
            msp.add_line((xs + 2.6, y_cur + 0.4), (xs + 3.4, y_cur - 0.4), dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW})
        elif tipo_simb == "SED":
            msp.add_circle((xs - 0.8, y_cur), radius=0.9, dxfattribs={"layer": capa, "color": colors.RED})
            msp.add_circle((xs + 0.8, y_cur), radius=0.9, dxfattribs={"layer": capa, "color": colors.BLUE})
        elif tipo_simb == "PAT":
            dibujar_simbolo_pat(msp, xs, y_cur + 1.0)
        elif tipo_simb == "RET":
            dibujar_simbolo_retenida(msp, xs - 2.0, y_cur, 90.0)
        elif tipo_simb == "MEDIDOR":
            dibujar_medidor_abonado(msp, xs, y_cur, "")
            
        msp.add_text(texto, dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.4, "color": colors.WHITE}).set_placement((xs + 8.0, y_cur - 0.6))
        y_cur -= 8.2

    # 7. Resumen de Cargas en el Plano
    msp.add_line((x_leg, y_cur + 2.0), (x_leg + w_leg, y_cur + 2.0), dxfattribs={"layer": "MEMBRETE_LEYENDA"})
    msp.add_text("DATOS TÉCNICOS RESUMEN (2 CIRCUITOS BT):", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.8, "color": colors.YELLOW}).set_placement((x_leg + 4.0, y_cur - 1.5))
    msp.add_text(f"• Total Abonados Censados: 43 viviendas", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.3, "color": colors.WHITE}).set_placement((x_leg + 6.0, y_cur - 4.5))
    msp.add_text(f"• Población Proyectada (n=20, 3%): 78 abonados", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.3, "color": colors.WHITE}).set_placement((x_leg + 6.0, y_cur - 7.5))
    msp.add_text(f"• C-1 (Norte + C31): 56 hab / 10 lum AP / 51.00 kW (56.7 kVA) / CAAI 3x35+25+16 mm2 / 820m", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.2, "color": colors.WHITE}).set_placement((x_leg + 6.0, y_cur - 10.5))
    msp.add_text(f"• C-2 (Carretera Fondo): 22 hab / 5 lum AP / 20.10 kW (22.3 kVA) / CAAI 3x25+25+16 mm2 / 456m", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.2, "color": colors.WHITE}).set_placement((x_leg + 6.0, y_cur - 13.5))
    msp.add_text(f"• Máxima Demanda Total: 71.10 kW  |  79.00 kVA (cos phi = 0.90)", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.3, "color": colors.YELLOW}).set_placement((x_leg + 6.0, y_cur - 17.0))
    msp.add_text(f"• Transformador SED SAB-1: 100 kVA (22.9/0.38-0.22 kV Dyn5 - Reserva: 21.0%)", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.3, "color": colors.YELLOW}).set_placement((x_leg + 6.0, y_cur - 20.0))

    doc.saveas(dxf_out)
    print(f"Plano DXF de Redes en Planta generado exitosamente en: {dxf_out}")

if __name__ == "__main__":
    out_dir = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\entregables\planos"
    target = os.path.join(out_dir, "PLANO_PLANTA_REDES_Y_ACOMETIDAS_CAPACHICA.dxf")
    generar_plano_completo_planta(target)
