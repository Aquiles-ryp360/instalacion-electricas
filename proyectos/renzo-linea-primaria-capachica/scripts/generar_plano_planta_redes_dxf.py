# -*- coding: utf-8 -*-
"""
generar_plano_planta_redes_dxf.py
Genera el Plano General de Redes de Distribución en Planta (Georreferenciado UTM WGS-84 Zona 19S)
en formato AutoCAD DXF R2010 con simbología 100% oficial normalizada DGE / CNE / MEM / Electro Puno:
1. Traza de Línea Primaria MT (22.9 kV, AAAC 35 mm²) y Subestación Biposte SAB-1 (100 kVA, 22.9/0.38-0.22 kV).
2. Traza de Red Secundaria BT (380/220 V) con exactamente 2 CIRCUITOS DE DISTRIBUCIÓN:
   - Circuito C-1: Troncal Norte hacia la Playa de Chifrón (Ruta 1 - 820.0 m, 56 usuarios proyectados, incluye vivienda C31).
   - Circuito C-2: Troncal Carretera al Fondo continua (Rutas 3 y 4 - 456.0 m, 22 usuarios proyectados).
3. Postes de MT (C.A.C. 13/400) y BT (C.A.C. 8/200) con bloque oficial DGE (círculo y cuadrantes achurados).
4. Red de Alumbrado Público con brazos pastorales y luminarias LED 60W (10 en C-1 y 5 en C-2 = 15 luminarias = 0.90 kW).
5. Retenidas normalizadas (RET-I, RET-CV) con cable de acero Siemens-Martin, aislador 54-1 y bloque de concreto.
6. Puestas a tierra normalizadas (PAT-3 en SED con R <= 10 ohm; PAT-1 en red BT con R <= 25 ohm).
7. Acometidas domiciliarias concéntricas aéreas SET 2x4 mm² y cajas portamedidor monofásico "M" para 43 abonados.
8. Leyenda técnica normalizada DGE/CNE y cuadro resumen de cargas de los 2 circuitos.

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
    """Dibuja un poste C.A.C. con bloque normalizado DGE (círculo con cuadrantes) y pastoral AP opcional."""
    # Círculo base del poste
    msp.add_circle((x, y), radius=1.0, dxfattribs={"layer": "POSTES_BT", "color": colors.GREEN, "lineweight": 25})
    # Cruz divisoria de cuadrantes DGE
    msp.add_line((x - 1.0, y), (x + 1.0, y), dxfattribs={"layer": "POSTES_BT", "color": colors.GREEN, "lineweight": 15})
    msp.add_line((x, y - 1.0), (x, y + 1.0), dxfattribs={"layer": "POSTES_BT", "color": colors.GREEN, "lineweight": 15})
    # Achurado de cuadrantes opuestos (I y III)
    msp.add_line((x, y), (x + 0.707, y + 0.707), dxfattribs={"layer": "POSTES_BT", "color": colors.GREEN, "lineweight": 25})
    msp.add_line((x, y), (x - 0.707, y - 0.707), dxfattribs={"layer": "POSTES_BT", "color": colors.GREEN, "lineweight": 25})
    # Rótulo del poste
    msp.add_text(pid, dxfattribs={"layer": "TEXTOS_ROTULOS", "height": 1.3, "color": colors.GREEN}).set_placement((x + 1.4, y + 0.8))
    
    # Brazo Pastoral y Luminaria LED 60W de Alumbrado Público
    if ap:
        x_lum = x + dx_ap
        y_lum = y + dy_ap
        # Brazo pastoral de F° G°
        msp.add_line((x, y), (x_lum, y_lum), dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW, "lineweight": 20})
        # Luminaria LED
        msp.add_circle((x_lum, y_lum), radius=0.6, dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW, "lineweight": 25})
        msp.add_text("AP 60W LED", dxfattribs={"layer": "ALUMBRADO_PUBLICO", "height": 1.0, "color": colors.YELLOW}).set_placement((x_lum + 0.8, y_lum - 0.4))

def dibujar_simbolo_pat(msp, x, y):
    """Dibuja el símbolo normalizado DGE de Puesta a Tierra (3 barras horizontales decrecientes)."""
    # Conductor vertical de bajada
    msp.add_line((x, y), (x, y - 2.0), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3})
    # 3 barras de tierra decrecientes
    msp.add_line((x - 1.6, y - 2.0), (x + 1.6, y - 2.0), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3, "lineweight": 25})
    msp.add_line((x - 1.0, y - 2.6), (x + 1.0, y - 2.6), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3, "lineweight": 25})
    msp.add_line((x - 0.4, y - 3.2), (x + 0.4, y - 3.2), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3, "lineweight": 25})
    msp.add_text("PAT", dxfattribs={"layer": "PUESTAS_A_TIERRA", "height": 1.2, "color": 3}).set_placement((x + 1.0, y - 3.0))

def dibujar_simbolo_retenida(msp, x, y, az_grados, tipo="RET-I"):
    """Dibuja el tirante de retenida con su bloque de anclaje de concreto."""
    rad = math.radians(az_grados)
    long_cable = 8.0
    dx = long_cable * math.sin(rad)
    dy = long_cable * math.cos(rad)
    x_ancla = x + dx
    y_ancla = y + dy
    # Cable de retenida
    msp.add_line((x, y), (x_ancla, y_ancla), dxfattribs={"layer": "RETENIDAS", "color": 30, "lineweight": 20})
    # Bloque de concreto perpendicular
    rad_perp = rad + math.pi / 2.0
    dx_p = 1.6 * math.sin(rad_perp)
    dy_p = 1.6 * math.cos(rad_perp)
    msp.add_line((x_ancla - dx_p, y_ancla - dy_p), (x_ancla + dx_p, y_ancla + dy_p), dxfattribs={"layer": "RETENIDAS", "color": 30, "lineweight": 35})
    msp.add_text(tipo, dxfattribs={"layer": "RETENIDAS", "height": 1.4, "color": 30}).set_placement((x_ancla + 1.0, y_ancla + 0.5))

def dibujar_medidor_abonado(msp, x, y, cod):
    """Dibuja la caja portamedidor monofásica normalizada M y rótulo de abonado."""
    d = 0.9
    pts = [(x-d, y-d), (x+d, y-d), (x+d, y+d), (x-d, y+d), (x-d, y-d)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": "MEDIDORES_ACOMETIDAS", "color": 1})
    msp.add_circle((x, y), radius=0.6, dxfattribs={"layer": "MEDIDORES_ACOMETIDAS", "color": 1})
    msp.add_text("M", dxfattribs={"layer": "MEDIDORES_ACOMETIDAS", "height": 0.8, "color": 1}).set_placement((x - 0.25, y - 0.35))
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
        ("RETENIDAS", 30),
        ("PUESTAS_A_TIERRA", 3),
        ("VIAS_ACCESO", 8),
        ("TEXTOS_ROTULOS", colors.WHITE),
        ("MEMBRETE_LEYENDA", colors.WHITE)
    ]
    for c_name, c_color in capas:
        doc.layers.add(c_name, color=c_color)

    # 1. Cargar datos
    kml_path = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\fuentes\kml\topografia_capachica_chifron.kml"
    csv_path = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\datos\cargas\censo_43_abonados.csv"
    
    rutas, vias = cargar_rutas_kml(kml_path)
    abonados = cargar_abonados_csv(csv_path)
    postes_bt = generar_postes_bt(rutas)
    
    # 2. Vías y Calles
    for v_name, pts in vias:
        if len(pts) > 1:
            msp.add_lwpolyline(pts, dxfattribs={"layer": "VIAS_ACCESO", "color": 8, "lineweight": 13})

    # 3. Línea Primaria MT 22.9 kV
    msp.add_lwpolyline(TRAZA_MT, dxfattribs={"layer": "RED_PRIMARIA_MT", "color": colors.CYAN, "lineweight": 50})
    
    # Subestación Biposte SAB-1
    for p in POSTES_MT:
        xe, yn = p["este"], p["norte"]
        msp.add_circle((xe - 1.2, yn), radius=1.2, dxfattribs={"layer": "POSTES_MT", "color": colors.YELLOW, "lineweight": 35})
        msp.add_circle((xe + 1.2, yn), radius=1.2, dxfattribs={"layer": "POSTES_MT", "color": colors.YELLOW, "lineweight": 35})
        msp.add_line((xe - 1.2, yn), (xe + 1.2, yn), dxfattribs={"layer": "POSTES_MT", "color": colors.YELLOW, "lineweight": 35})
        
        msp.add_text(f"{p['id']} - SED BIPOSTE 100 kVA (22.9/0.38-0.22 kV)", dxfattribs={"layer": "TEXTOS_ROTULOS", "height": 2.4, "color": colors.YELLOW}).set_placement((xe + 3.0, yn + 2.0))
        msp.add_text("Lat: -15.640067, Lon: -69.815400 (Origen C-1 Norte y C-2 Sur)", dxfattribs={"layer": "TEXTOS_ROTULOS", "height": 1.6, "color": colors.WHITE}).set_placement((xe + 3.0, yn - 0.5))
        
        if p["pat"]:
            dibujar_simbolo_pat(msp, xe - 3.5, yn - 2.0)
        if p["ret"] and p["ret_az"] is not None:
            dibujar_simbolo_retenida(msp, xe, yn, p["ret_az"], p["ret"])

    # 4. Red Secundaria BT (2 Circuitos)
    # Circuito C-1 (Ruta 1)
    if 'ruta electrica 1' in rutas and len(rutas['ruta electrica 1']) > 1:
        msp.add_lwpolyline(rutas['ruta electrica 1'], dxfattribs={"layer": "RED_SECUNDARIA_BT", "color": colors.MAGENTA, "lineweight": 35})
    # Circuito C-2 (Rutas 3 y 4 continuas)
    pts_c2 = []
    if 'ruta electrica 3' in rutas:
        pts_c2 += rutas['ruta electrica 3']
    if 'ruta electrica 4' in rutas:
        pts_c2 += rutas['ruta electrica 4']
    if len(pts_c2) > 1:
        msp.add_lwpolyline([(412606.01, 8270712.24)] + pts_c2, dxfattribs={"layer": "RED_SECUNDARIA_BT", "color": colors.MAGENTA, "lineweight": 35})

    # Dibujar Postes de BT
    for p in postes_bt:
        xe, yn = p["este"], p["norte"]
        dibujar_bloque_poste_dxf(msp, xe, yn, p['id'], ap=p.get('ap', False), dx_ap=p.get('dx_ap', 3.5), dy_ap=p.get('dy_ap', 0.0))
        
        if p["pat"]:
            dibujar_simbolo_pat(msp, xe - 2.0, yn - 1.0)
        if p["ret"]:
            dibujar_simbolo_retenida(msp, xe, yn, 180.0, "RET-I")

    # 5. Acometidas Domiciliarias a los 43 Abonados
    todos_los_postes = [(p["este"], p["norte"], p["id"], p["circuito"]) for p in postes_bt] + [(p["este"], p["norte"], p["id"], "SED") for p in POSTES_MT]
    
    total_long_acometidas = 0.0
    for ab in abonados:
        xe_ab, yn_ab = ab["este"], ab["norte"]
        if ab["cod"] == "C31":
            cand = [p for p in todos_los_postes if p[3] == "C-1"]
        elif int(ab["cod"][1:]) <= 30:
            cand = [p for p in todos_los_postes if p[3] in ["C-1", "SED"]]
        else:
            cand = [p for p in todos_los_postes if p[3] in ["C-2", "SED"]]
            
        p_cercano = min(cand, key=lambda p: math.hypot(xe_ab - p[0], yn_ab - p[1]))
        dist_min = math.hypot(xe_ab - p_cercano[0], yn_ab - p_cercano[1])
        p_e, p_n, p_id, _ = p_cercano
        
        total_long_acometidas += dist_min
        msp.add_line((p_e, p_n), (xe_ab, yn_ab), dxfattribs={"layer": "ACOMETIDAS_DOMICILIARIAS", "color": colors.BLUE, "lineweight": 18})
        dibujar_medidor_abonado(msp, xe_ab, yn_ab, ab["cod"])
        
        xm = (p_e + xe_ab) / 2.0
        ym = (p_n + yn_ab) / 2.0
        msp.add_text(f"Acom. {dist_min:.1f}m", dxfattribs={"layer": "ACOMETIDAS_DOMICILIARIAS", "height": 0.9, "color": colors.BLUE}).set_placement((xm + 0.3, ym + 0.3))

    # 6. Cuadro de Simbología y Leyenda Normalizada DGE
    x_leg = 412500.0
    y_leg = 8270860.0
    w_leg = 100.0
    h_leg = 135.0
    
    pts_leg = [(x_leg, y_leg), (x_leg + w_leg, y_leg), (x_leg + w_leg, y_leg - h_leg), (x_leg, y_leg - h_leg), (x_leg, y_leg)]
    msp.add_lwpolyline(pts_leg, dxfattribs={"layer": "MEMBRETE_LEYENDA", "color": colors.WHITE, "lineweight": 30})
    msp.add_text("LEYENDA Y SIMBOLOGÍA TÉCNICA (DGE / CNE)", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 2.8, "color": colors.YELLOW}).set_placement((x_leg + 4.0, y_leg - 6.0))
    msp.add_line((x_leg, y_leg - 9.0), (x_leg + w_leg, y_leg - 9.0), dxfattribs={"layer": "MEMBRETE_LEYENDA"})

    items_leyenda = [
        ("RED PRIMARIA MT 22.9 kV (AAAC 35 mm2)", "RED_PRIMARIA_MT", colors.CYAN, "LINEA"),
        ("CIRCUITO C-1 BT TRONCAL NORTE + C31 (CAAI 3x35+25+16 mm2)", "RED_SECUNDARIA_BT", colors.MAGENTA, "LINEA"),
        ("CIRCUITO C-2 BT CARRETERA AL FONDO (CAAI 3x25+25+16 mm2)", "RED_SECUNDARIA_BT", colors.MAGENTA, "LINEA"),
        ("ACOMETIDA DOMICILIARIA CONCÉNTRICA (SET 2x4 mm2)", "ACOMETIDAS_DOMICILIARIAS", colors.BLUE, "LINEA"),
        ("POSTE C.A.C. MEDIA TENSIÓN (13m/400daN)", "POSTES_MT", colors.YELLOW, "CIRCULO_MT"),
        ("POSTE C.A.C. BAJA TENSIÓN 8m/200daN (BLOQUE DGE)", "POSTES_BT", colors.GREEN, "POSTE_DGE"),
        ("POSTE C.A.C. CON PASTORAL Y LUMINARIA AP 60W LED", "ALUMBRADO_PUBLICO", colors.YELLOW, "POSTE_AP"),
        ("SUBESTACIÓN DISTRIBUCIÓN BIPOSTE (SAB-1 100 kVA)", "POSTES_MT", colors.YELLOW, "SED"),
        ("PUESTA A TIERRA NORMALIZADA (PAT-3 / PAT-1)", "PUESTAS_A_TIERRA", 3, "PAT"),
        ("RETENIDA CON BLOQUE ANCLAJE CONCRETO (RET-I/RET-CV)", "RETENIDAS", 30, "RET"),
        ("CAJA PORTAMEDIDOR MONOFÁSICO DE ABONADO (M)", "MEDIDORES_ACOMETIDAS", colors.RED, "MEDIDOR"),
        ("VÍA DE ACCESO / CARRETERA AFIRMADA", "VIAS_ACCESO", 8, "LINEA")
    ]

    y_cur = y_leg - 15.0
    for texto, capa, col, tipo_simb in items_leyenda:
        xs = x_leg + 8.0
        if tipo_simb == "LINEA":
            msp.add_line((xs - 4.0, y_cur), (xs + 4.0, y_cur), dxfattribs={"layer": capa, "color": col, "lineweight": 30})
        elif tipo_simb == "CIRCULO_MT":
            msp.add_circle((xs, y_cur), radius=1.6, dxfattribs={"layer": capa, "color": col})
        elif tipo_simb == "POSTE_DGE":
            msp.add_circle((xs, y_cur), radius=1.0, dxfattribs={"layer": capa, "color": col})
            msp.add_line((xs - 1.0, y_cur), (xs + 1.0, y_cur), dxfattribs={"layer": capa, "color": col})
            msp.add_line((xs, y_cur - 1.0), (xs, y_cur + 1.0), dxfattribs={"layer": capa, "color": col})
        elif tipo_simb == "POSTE_AP":
            msp.add_circle((xs, y_cur), radius=0.9, dxfattribs={"layer": "POSTES_BT", "color": colors.GREEN})
            msp.add_line((xs, y_cur), (xs + 3.0, y_cur), dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW})
            msp.add_circle((xs + 3.0, y_cur), radius=0.5, dxfattribs={"layer": "ALUMBRADO_PUBLICO", "color": colors.YELLOW})
        elif tipo_simb == "SED":
            msp.add_circle((xs - 1.2, y_cur), radius=1.0, dxfattribs={"layer": capa, "color": col})
            msp.add_circle((xs + 1.2, y_cur), radius=1.0, dxfattribs={"layer": capa, "color": col})
            msp.add_line((xs - 1.2, y_cur), (xs + 1.2, y_cur), dxfattribs={"layer": capa, "color": col})
        elif tipo_simb == "PAT":
            dibujar_simbolo_pat(msp, xs, y_cur + 1.0)
        elif tipo_simb == "RET":
            dibujar_simbolo_retenida(msp, xs - 2.0, y_cur, 90.0, "")
        elif tipo_simb == "MEDIDOR":
            dibujar_medidor_abonado(msp, xs, y_cur, "")
            
        msp.add_text(texto, dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.5, "color": colors.WHITE}).set_placement((xs + 8.0, y_cur - 0.7))
        y_cur -= 8.5

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
