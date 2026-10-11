# -*- coding: utf-8 -*-
"""
generar_plano_planta_redes_dxf.py
Genera el Plano General de Redes de Distribución en Planta (Georreferenciado UTM WGS-84)
mostrando:
1. Traza de Línea Primaria MT (22.9 kV) y Subestación Biposte E-04 (100 kVA).
2. Traza de Red Secundaria BT (380/220 V) en los 3 circuitos (C-1, C-2, C-3).
3. Postes de MT y BT con sus números correlativos y armados.
4. Simbología y vectores de RETENIDAS (RET-I, RET-B, RET-T) con sus anclajes de concreto.
5. Simbología de PUESTAS A TIERRA (PAT-3, PAT-1) en postes normados.
6. ACOMETIDAS DOMICILIARIAS desde el poste más cercano hasta cada una de las 43 viviendas (C1 a C43),
   con cajas portamedidor monofásico normalizadas (M).
7. Leyenda de simbología DGE y membrete oficial UNA Puno - FIME.

Autor: Renzo Gabriel Mamani Galindo (Cód. 228447)
Curso: MEC330 - Instalaciones Eléctricas II | UNA Puno
"""

import os
import math
import csv
import xml.etree.ElementTree as ET
import ezdxf
from ezdxf import colors

# Conversor de WGS84 Lat/Lon a UTM Zona 19S
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

# Subestación de Distribución Proyectada (SED Biposte 100 kVA)
# Ubicación fijada por usuario: Lat: -15.640067, Lon: -69.815400 (Origen de Circuitos BT 1, 2, 3)
POSTES_MT = [
    {"id": "SED-01", "este": 412606.01, "norte": 8270712.24, "tipo": "2xC.A.C. 13/400 (Biposte)", "armado": "SAB-1", "pat": "PAT-3", "ret": "RET-CV", "ret_az": 210.0, "desc": "Subestación Biposte 100 kVA (22.9/0.38-0.22 kV)"},
]

# Línea Primaria MT 22.9 kV de alimentación desde red Electro Puno hasta la SED
TRAZA_MT = [
    (412380.00, 8270740.00), # Punto de derivación red Electro Puno en carretera
    (412490.00, 8270725.00), # Poste intermedio MT
    (412606.01, 8270712.24)  # Llegada a SED-01
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
    Genera la distribución de postes de Baja Tensión (C.A.C. 8/200 o 9/300)
    a lo largo de las rutas secundarias C-1, C-2, C-3 con vanos máximos de 35 a 40 metros.
    """
    postes_bt = []
    p_idx = 1
    
    for r_name in ['ruta electrica 1', 'ruta electrica 3', 'ruta electrica 4', 'ruta electrica 2']:
        if r_name not in rutas:
            continue
        pts = rutas[r_name]
        if '1' in r_name:
            circuito = "C-1"
        elif '3' in r_name:
            circuito = "C-2"
        else:
            circuito = "C-3"
        
        # Subdividir tramos largos en vanos <= 38 m
        for i in range(len(pts) - 1):
            p1 = pts[i]
            p2 = pts[i+1]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            n_seg = max(1, int(math.ceil(dist / 38.0)))
            
            for s in range(n_seg if i == len(pts)-2 else n_seg):
                ts = s / float(n_seg)
                xe = p1[0] + ts * (p2[0] - p1[0])
                yn = p1[1] + ts * (p2[1] - p1[1])
                
                # Evitar duplicar exactamente la SED-01
                if math.hypot(xe - 412606.01, yn - 8270712.24) < 5.0 and len(postes_bt) > 0:
                    continue
                    
                pid = f"P-BT-{p_idx:02d}"
                # Puestas a tierra en extremos y retenidas en vértices
                es_extremo = (s == 0 and i == 0) or (i == len(pts)-2 and s == n_seg)
                pat = "PAT-1" if (p_idx % 5 == 0 or es_extremo) else None
                ret = "RET-BT" if es_extremo else None
                
                postes_bt.append({
                    "id": pid,
                    "circuito": circuito,
                    "este": xe,
                    "norte": yn,
                    "pat": pat,
                    "ret": ret
                })
                p_idx += 1
                
    return postes_bt

def dibujar_simbolo_pat(msp, x, y, rot=0.0):
    """Dibuja el símbolo normalizado DGE de Puesta a Tierra (3 rayitas paralelas decrecientes)."""
    # Conductor vertical de bajada
    msp.add_line((x, y), (x, y - 2.0), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3}) # Verde
    # 3 rayitas de tierra
    msp.add_line((x - 1.6, y - 2.0), (x + 1.6, y - 2.0), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3})
    msp.add_line((x - 1.0, y - 2.6), (x + 1.0, y - 2.6), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3})
    msp.add_line((x - 0.4, y - 3.2), (x + 0.4, y - 3.2), dxfattribs={"layer": "PUESTAS_A_TIERRA", "color": 3})
    # Texto identificador PAT
    msp.add_text("PAT", dxfattribs={"layer": "PUESTAS_A_TIERRA", "height": 1.2, "color": 3}).set_placement((x + 1.0, y - 3.0))

def dibujar_simbolo_retenida(msp, x, y, az_grados, tipo="RET-I"):
    """Dibuja la flecha de retenida con su bloque de anclaje de concreto."""
    rad = math.radians(az_grados)
    # Longitud de representación del cable en planta: 8 metros
    long_cable = 8.0
    dx = long_cable * math.sin(rad)
    dy = long_cable * math.cos(rad)
    x_ancla = x + dx
    y_ancla = y + dy
    
    # Cable de retenida
    msp.add_line((x, y), (x_ancla, y_ancla), dxfattribs={"layer": "RETENIDAS", "color": 30, "lineweight": 20})
    
    # Bloque de anclaje (perpendicular al cable de retenida)
    rad_perp = rad + math.pi / 2.0
    dx_p = 1.6 * math.sin(rad_perp)
    dy_p = 1.6 * math.cos(rad_perp)
    msp.add_line((x_ancla - dx_p, y_ancla - dy_p), (x_ancla + dx_p, y_ancla + dy_p), dxfattribs={"layer": "RETENIDAS", "color": 30, "lineweight": 35})
    
    # Texto de retenida
    msp.add_text(tipo, dxfattribs={"layer": "RETENIDAS", "height": 1.4, "color": 30}).set_placement((x_ancla + 1.0, y_ancla + 0.5))

def dibujar_medidor_abonado(msp, x, y, cod):
    """Dibuja el símbolo de caja portamedidor monofásico M y rótulo del abonado."""
    # Caja portamedidor (cuadrado de 1.8m x 1.8m)
    d = 0.9
    pts = [(x-d, y-d), (x+d, y-d), (x+d, y+d), (x-d, y+d), (x-d, y-d)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": "MEDIDORES_ACOMETIDAS", "color": 1}) # Rojo
    # Círculo con letra 'M' adentro
    msp.add_circle((x, y), radius=0.6, dxfattribs={"layer": "MEDIDORES_ACOMETIDAS", "color": 1})
    msp.add_text("M", dxfattribs={"layer": "MEDIDORES_ACOMETIDAS", "height": 0.8, "color": 1}).set_placement((x - 0.25, y - 0.35))
    # Rótulo del abonado
    msp.add_text(cod, dxfattribs={"layer": "TEXTOS_ROTULOS", "height": 1.3, "color": 7}).set_placement((x + 1.2, y + 0.5))


def generar_plano_completo_planta(dxf_out):
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()
    
    # Capas Normalizadas
    capas = [
        ("RED_PRIMARIA_MT", colors.CYAN),
        ("RED_SECUNDARIA_BT", colors.MAGENTA),
        ("POSTES_MT", colors.YELLOW),
        ("POSTES_BT", colors.GREEN),
        ("ACOMETIDAS_DOMICILIARIAS", colors.BLUE),
        ("MEDIDORES_ACOMETIDAS", colors.RED),
        ("RETENIDAS", 30), # Naranja
        ("PUESTAS_A_TIERRA", 3), # Verde claro
        ("VIAS_ACCESO", 8), # Gris
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
    
    # 2. Dibujar Vías y Calles de Acceso
    for v_name, pts in vias:
        if len(pts) > 1:
            msp.add_lwpolyline(pts, dxfattribs={"layer": "VIAS_ACCESO", "color": 8, "lineweight": 13})

    # 3. Dibujar Línea Primaria MT (22.9 kV)
    msp.add_lwpolyline(TRAZA_MT, dxfattribs={"layer": "RED_PRIMARIA_MT", "color": colors.CYAN, "lineweight": 50})
    
    # Dibujar Subestación de Distribución Biposte SED-01 (100 kVA)
    for p in POSTES_MT:
        xe, yn = p["este"], p["norte"]
        # Estructura biposte: dos círculos
        msp.add_circle((xe - 1.2, yn), radius=1.2, dxfattribs={"layer": "POSTES_MT", "color": colors.YELLOW, "lineweight": 35})
        msp.add_circle((xe + 1.2, yn), radius=1.2, dxfattribs={"layer": "POSTES_MT", "color": colors.YELLOW, "lineweight": 35})
        msp.add_line((xe - 1.2, yn), (xe + 1.2, yn), dxfattribs={"layer": "POSTES_MT", "color": colors.YELLOW, "lineweight": 35})
        
        # Rótulo de la SED
        msp.add_text(f"{p['id']} - SED BIPOSTE 100 kVA (22.9/0.38-0.22 kV)", dxfattribs={"layer": "TEXTOS_ROTULOS", "height": 2.4, "color": colors.YELLOW}).set_placement((xe + 3.0, yn + 2.0))
        msp.add_text("Lat: -15.640067, Lon: -69.815400 (Origen C-1, C-2, C-3)", dxfattribs={"layer": "TEXTOS_ROTULOS", "height": 1.6, "color": colors.WHITE}).set_placement((xe + 3.0, yn - 0.5))
        
        # Puesta a tierra normada PAT-3
        if p["pat"]:
            dibujar_simbolo_pat(msp, xe - 3.5, yn - 2.0)
            
        # Retenida contraviento
        if p["ret"] and p["ret_az"] is not None:
            dibujar_simbolo_retenida(msp, xe, yn, p["ret_az"], p["ret"])

    # 4. Dibujar Red Secundaria BT (380/220 V)
    for r_name in ['ruta electrica 1', 'ruta electrica 2', 'ruta electrica 3', 'ruta electrica 4']:
        if r_name in rutas and len(rutas[r_name]) > 1:
            msp.add_lwpolyline(rutas[r_name], dxfattribs={"layer": "RED_SECUNDARIA_BT", "color": colors.MAGENTA, "lineweight": 35})

    # Dibujar Postes de BT
    for p in postes_bt:
        xe, yn = p["este"], p["norte"]
        msp.add_circle((xe, yn), radius=1.0, dxfattribs={"layer": "POSTES_BT", "color": colors.GREEN, "lineweight": 25})
        msp.add_text(p['id'], dxfattribs={"layer": "TEXTOS_ROTULOS", "height": 1.3, "color": colors.GREEN}).set_placement((xe + 1.5, yn + 0.8))
        
        if p["pat"]:
            dibujar_simbolo_pat(msp, xe - 2.0, yn - 1.0)
        if p["ret"]:
            dibujar_simbolo_retenida(msp, xe, yn, 180.0, "RET-BT")

    # 5. Dibujar Acometidas Domiciliarias a los 43 Abonados (C1 a C43)
    todos_los_postes = [(p["este"], p["norte"], p["id"]) for p in postes_bt] + [(p["este"], p["norte"], p["id"]) for p in POSTES_MT]
    
    total_long_acometidas = 0.0
    for ab in abonados:
        xe_ab, yn_ab = ab["este"], ab["norte"]
        # Encontrar poste más cercano
        dist_min = float('inf')
        poste_cercano = None
        for p_e, p_n, p_id in todos_los_postes:
            d = math.hypot(xe_ab - p_e, yn_ab - p_n)
            if d < dist_min:
                dist_min = d
                poste_cercano = (p_e, p_n, p_id)
                
        # Dibujar línea de acometida discontinua
        if poste_cercano:
            p_e, p_n, p_id = poste_cercano
            total_long_acometidas += dist_min
            msp.add_line((p_e, p_n), (xe_ab, yn_ab), dxfattribs={"layer": "ACOMETIDAS_DOMICILIARIAS", "color": colors.BLUE, "lineweight": 18})
            
            # Dibujar medidor en la vivienda
            dibujar_medidor_abonado(msp, xe_ab, yn_ab, ab["cod"])
            
            # Texto de longitud de acometida en el punto medio
            xm = (p_e + xe_ab) / 2.0
            ym = (p_n + yn_ab) / 2.0
            msp.add_text(f"Acom. {dist_min:.1f}m", dxfattribs={"layer": "ACOMETIDAS_DOMICILIARIAS", "height": 0.9, "color": colors.BLUE}).set_placement((xm + 0.3, ym + 0.3))

    # 6. Cuadro de Simbología y Leyenda Técnica Normalizada DGE
    x_leg = 412500.0
    y_leg = 8270850.0
    w_leg = 95.0
    h_leg = 120.0
    
    # Marco de Leyenda
    pts_leg = [(x_leg, y_leg), (x_leg + w_leg, y_leg), (x_leg + w_leg, y_leg - h_leg), (x_leg, y_leg - h_leg), (x_leg, y_leg)]
    msp.add_lwpolyline(pts_leg, dxfattribs={"layer": "MEMBRETE_LEYENDA", "color": colors.WHITE, "lineweight": 30})
    msp.add_text("LEYENDA Y SIMBOLOGÍA TÉCNICA (DGE / CNE)", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 2.8, "color": colors.YELLOW}).set_placement((x_leg + 4.0, y_leg - 6.0))
    msp.add_line((x_leg, y_leg - 9.0), (x_leg + w_leg, y_leg - 9.0), dxfattribs={"layer": "MEMBRETE_LEYENDA"})

    items_leyenda = [
        ("RED PRIMARIA MT 22.9 kV (AAAC 35 mm2)", "RED_PRIMARIA_MT", colors.CYAN, "LINEA"),
        ("RED SECUNDARIA BT 380/220 V (CAAI 3x25+16 mm2)", "RED_SECUNDARIA_BT", colors.MAGENTA, "LINEA"),
        ("ACOMETIDA DOMICILIARIA CONCÉNTRICA (2x4 mm2)", "ACOMETIDAS_DOMICILIARIAS", colors.BLUE, "LINEA"),
        ("POSTE C.A.C. MEDIA TENSIÓN (12m/13m)", "POSTES_MT", colors.YELLOW, "CIRCULO_MT"),
        ("POSTE C.A.C. BAJA TENSIÓN (8m/9m)", "POSTES_BT", colors.GREEN, "CIRCULO_BT"),
        ("SUBESTACIÓN DISTRIBUCIÓN BIPOSTE (SAB-1 100 kVA)", "POSTES_MT", colors.YELLOW, "SED"),
        ("PUESTA A TIERRA NORMALIZADA (PAT-3 / PAT-1)", "PUESTAS_A_TIERRA", 3, "PAT"),
        ("RETENIDA CON BLOQUE ANCLAJE CONCRETO (RET-I/RET-B)", "RETENIDAS", 30, "RET"),
        ("CAJA PORTAMEDIDOR MONOFÁSICO DE ABONADO (M)", "MEDIDORES_ACOMETIDAS", colors.RED, "MEDIDOR"),
        ("VÍA DE ACCESO / CARRETERA AFIRMADA", "VIAS_ACCESO", 8, "LINEA")
    ]

    y_cur = y_leg - 16.0
    for texto, capa, col, tipo_simb in items_leyenda:
        xs = x_leg + 8.0
        # Dibujar muestra
        if tipo_simb == "LINEA":
            msp.add_line((xs - 4.0, y_cur), (xs + 4.0, y_cur), dxfattribs={"layer": capa, "color": col, "lineweight": 30})
        elif tipo_simb == "CIRCULO_MT":
            msp.add_circle((xs, y_cur), radius=1.6, dxfattribs={"layer": capa, "color": col})
        elif tipo_simb == "CIRCULO_BT":
            msp.add_circle((xs, y_cur), radius=1.0, dxfattribs={"layer": capa, "color": col})
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
            
        msp.add_text(texto, dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.7, "color": colors.WHITE}).set_placement((xs + 8.0, y_cur - 0.7))
        y_cur -= 10.0

    # 7. Resumen de Cargas en el Plano
    msp.add_line((x_leg, y_cur + 2.0), (x_leg + w_leg, y_cur + 2.0), dxfattribs={"layer": "MEMBRETE_LEYENDA"})
    msp.add_text("DATOS TÉCNICOS RESUMEN:", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 2.0, "color": colors.YELLOW}).set_placement((x_leg + 4.0, y_cur - 2.0))
    msp.add_text(f"• Total Abonados Censados: 43 viviendas", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.5, "color": colors.WHITE}).set_placement((x_leg + 6.0, y_cur - 6.0))
    msp.add_text(f"• Población Proyectada (n=20, 3%): 78 abonados", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.5, "color": colors.WHITE}).set_placement((x_leg + 6.0, y_cur - 10.0))
    msp.add_text(f"• Máxima Demanda Total: 71.10 kW  |  79.00 kVA", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.5, "color": colors.WHITE}).set_placement((x_leg + 6.0, y_cur - 14.0))
    msp.add_text(f"• Transformador SED E-04: 100 kVA (22.9/0.38-0.22 kV)", dxfattribs={"layer": "MEMBRETE_LEYENDA", "height": 1.5, "color": colors.WHITE}).set_placement((x_leg + 6.0, y_cur - 18.0))

    doc.saveas(dxf_out)
    print(f"Plano de Redes en Planta generado exitosamente en: {dxf_out}")

if __name__ == "__main__":
    out_dir = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\entregables\planos"
    target = os.path.join(out_dir, "PLANO_PLANTA_REDES_Y_ACOMETIDAS_CAPACHICA.dxf")
    generar_plano_completo_planta(target)
