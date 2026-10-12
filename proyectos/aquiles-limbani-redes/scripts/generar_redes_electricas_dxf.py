#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_redes_electricas_dxf.py
Genera el Plano Maestro de Ingeniería Electromecánica en formato DXF y DWG nativo:
- Cámara y vista inicial VPORT centrada directamente en Limbani (sin pantalla negra).
- Extents y Limits configurados en Model Space y Layout1 (A3) para encuadre automático.
- Compilación a DWG nativo de AutoCAD mediante AutoCAD Core Engine (accoreconsole.exe).
- Postería de Media Tensión (CAC 12m y 13m) y conductor AAAC 35 mm2 (10 kV) con anchos geométricos visibles.
- Subestaciones Aéreas Biposte (SED-01 50 kVA, SED-02 100 kVA, SED-03 100 kVA) con símbolos grandes de plataforma y transformador.
- Postería de Baja Tensión (CAC 8m y 9m) y cables autoportantes CAAI (380/220 V) con ancho de línea real.
- Retenidas en esquinas, terminales y vanos críticos con anclas visibles.
- Alumbrado público LED (165 luminarias de 50 W) con pastorales y luminarias visibles.
- Cuadro de Leyenda de Simbología y Membrete FIME-UNAP al costado del pueblo.
- Generación de 4 planos gráficos de alta resolución: Planta General y 3 Zooms Sectoriales.

Autor: Br. Aquiles Taylor Ramos Yapo (Cód. 227368)
Curso: Instalaciones Eléctricas II / Redes Eléctricas | FIME - UNA Puno
"""

import os
import math
import shutil
import subprocess
import ezdxf
from ezdxf import colors
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D

def distancia(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def interp_pt(p1, p2, f):
    return (p1[0] + f * (p2[0] - p1[0]), p1[1] + f * (p2[1] - p1[1]))

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dxf_orig = r"C:\Users\51949\Downloads\Catastro_Limbani\catastro_limbani.dxf"
    out_dxf = os.path.join(base_dir, "entregables", "planos", "catastro_limbani_redes_electricas.dxf")
    out_dwg = os.path.join(base_dir, "entregables", "planos", "catastro_limbani_redes_electricas.dwg")
    fig_dir = os.path.join(base_dir, "expediente", "figuras")
    
    out_img_gen = os.path.join(fig_dir, "07_redes_electricas_detalladas_catastro.png")
    out_img_norte = os.path.join(fig_dir, "08_zoom_norte_hidroelectrica_sed01.png")
    out_img_centro = os.path.join(fig_dir, "09_zoom_centro_plaza_sed02.png")
    out_img_sur = os.path.join(fig_dir, "10_zoom_sur_cruce_estadio_sed03.png")

    catastro_sync_dir = r"C:\Users\51949\Downloads\Catastro_Limbani\expediente_electrico"
    catastro_sync_dxf = os.path.join(catastro_sync_dir, "catastro_limbani_redes_electricas.dxf")
    catastro_sync_dwg = os.path.join(catastro_sync_dir, "catastro_limbani_redes_electricas.dwg")

    print("[*] Leyendo catastro base:", dxf_orig)
    doc = ezdxf.readfile(dxf_orig)
    msp = doc.modelspace()

    # -------------------------------------------------------------
    # CONFIGURAR CÁMARA Y ENCUADRE AUTOMÁTICO EN EL MODEL SPACE Y LAYOUT
    # -------------------------------------------------------------
    # Casco urbano de Limbani: Este: 425,100 a 426,150 | Norte: 8'434,350 a 8'436,850
    cx = 425600.0
    cy = 8435600.0
    view_h = 2650.0

    # Establecer los límites geométricos reales en el Model Space
    msp.dxf.extmin = (425100.0, 8434300.0, 0.0)
    msp.dxf.extmax = (426200.0, 8436900.0, 0.0)
    msp.dxf.limmin = (425100.0, 8434300.0)
    msp.dxf.limmax = (426200.0, 8436900.0)

    # Configurar el Viewport activo con la API oficial de ezdxf
    try:
        doc.set_modelspace_vport(height=view_h, center=(cx, cy))
    except Exception as e:
        print("[!] Nota sobre VPORT:", e)

    # Configurar Layout1 (Presentación A3) para que al dar clic a la pestaña Layout1 aparezca encuadrado
    try:
        l1 = doc.layout("Layout1")
        l1.page_setup(size=(420, 297), margins=(10, 10, 10, 10), units="mm")
        l1.add_viewport(
            center=(210.0, 148.5),
            size=(390.0, 267.0),
            view_center_point=(cx, cy),
            view_height=view_h
        )
    except Exception as e:
        print("[!] Nota sobre Layout1:", e)

    # -------------------------------------------------------------
    # 1. CREAR CAPAS ELECTROMECÁNICAS NORMALIZADAS DGE
    # -------------------------------------------------------------
    capas_def = [
        ("01_RED_MT_10KV_CONDUCTOR", colors.RED),      # Rojo brillante
        ("02_POSTES_MT_10KV", colors.RED),             # Rojo
        ("03_SUBESTACIONES_SED", colors.YELLOW),       # Amarillo
        ("04_RETENIDAS_MT_BT", colors.MAGENTA),        # Magenta
        ("05_RED_BT_TRONCAL_CAAI", colors.GREEN),      # Verde
        ("06_RED_BT_DERIVACION_CAAI", colors.CYAN),    # Cian
        ("07_POSTES_BT_CAC", colors.BLUE),             # Azul
        ("08_ALUMBRADO_PUBLICO_LED", 30),              # Naranja / Amarillo oscuro
        ("09_CUADRO_LEYENDA_ROTULO", colors.WHITE)     # Blanco
    ]
    for c_name, c_color in capas_def:
        if c_name not in doc.layers:
            doc.layers.new(name=c_name, dxfattribs={'color': c_color})

    # -------------------------------------------------------------
    # 2. EXTRAER VÍAS PARA EL TRAZADO
    # -------------------------------------------------------------
    vias_polys = []
    for e in msp:
        if e.dxf.layer == '02_CALLES_Y_VIAS' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            vias_polys.append(pts)

    print(f"[*] {len(vias_polys)} vías catastrales listas para electrificación.")

    # -------------------------------------------------------------
    # 3. LÍNEA PRIMARIA MEDIA TENSIÓN 10 kV (2.15 km)
    # -------------------------------------------------------------
    postes_mt_data = [
        ("E-01", 425715.0, 8436650.0, 3140.0, "C.A.C. 13/400", "PR-3", "Inclinada simple", "Pórtico Salida MCH Limbani (Cut-out + ZnO)"),
        ("E-02", 425660.0, 8436570.0, 3125.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Alineamiento bajada quebrada norte"),
        ("E-03", 425610.0, 8436490.0, 3110.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Alineamiento camino acceso norte"),
        ("E-04", 425570.0, 8436410.0, 3098.0, "C.A.C. 12/400", "PA-3", "Biselar simple", "Ángulo entrada a Jr. Villa Hermosa"),
        ("E-05", 425530.0, 8436330.0, 3088.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Paso por Jr. Villa Hermosa"),
        ("E-06", 425490.0, 8436250.0, 3080.0, "2xC.A.C. 13/400", "SAB-1", "Contraviento doble", "SED-01 Norte (50 kVA, 10/0.38-0.22 kV)"),
        ("E-07", 425470.0, 8436170.0, 3072.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Paso intermedio Jr. Progreso"),
        ("E-08", 425450.0, 8436090.0, 3065.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Alineamiento Pje. Jorge Chávez"),
        ("E-09", 425440.0, 8436010.0, 3060.0, "C.A.C. 12/400", "PA-3", "Biselar simple", "Ángulo desvío hacia margen río"),
        ("E-10", 425435.0, 8435925.0, 3055.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Paso por Pje. Cantutani"),
        ("E-11", 425430.0, 8435840.0, 3052.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Paso por Pje. Santa Elisa"),
        ("E-12", 425435.0, 8435760.0, 3050.0, "C.A.C. 12/400", "PA-3", "Biselar simple", "Ángulo aproximación Plaza de Armas"),
        ("E-13", 425445.0, 8435700.0, 3050.0, "2xC.A.C. 13/400", "SAB-2", "Contraviento doble", "SED-02 Centro Plaza de Armas (100 kVA)"),
        ("E-14", 425450.0, 8435615.0, 3048.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Alineamiento Calle Municipal"),
        ("E-15", 425455.0, 8435530.0, 3045.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Alineamiento sur centro urbano"),
        ("E-16", 425460.0, 8435445.0, 3040.0, "C.A.C. 12/400", "PA-3", "Biselar simple", "Ángulo entrada a confluencia"),
        ("E-17", 425465.0, 8435360.0, 3035.0, "C.A.C. 13/600", "PR-3", "Inclinada pesada", "Pórtico norte cruce aéreo Río Chinchalamani"),
        ("E-18", 425470.0, 8435250.0, 3030.0, "C.A.C. 13/600", "PR-3", "Inclinada pesada", "Pórtico sur cruce aéreo Río Chinchalamani (110m)"),
        ("E-19", 425460.0, 8435165.0, 3025.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Paso acceso Estadio Municipal"),
        ("E-20", 425445.0, 8435080.0, 3020.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Alineamiento sector estadio"),
        ("E-21", 425425.0, 8435000.0, 3015.0, "C.A.C. 12/400", "PA-3", "Biselar simple", "Ángulo hacia sector piscina"),
        ("E-22", 425410.0, 8434930.0, 3010.0, "2xC.A.C. 13/400", "SAB-3", "Contraviento doble", "SED-03 Sur Estadio-Piscina (100 kVA)"),
        ("E-23", 425390.0, 8434845.0, 3005.0, "C.A.C. 12/300", "PS-3", "Ninguna", "Paso Pasaje Piscina"),
        ("E-24", 425370.0, 8434760.0, 3000.0, "C.A.C. 12/400", "PR-3", "Inclinada terminal", "Terminal sur de línea primaria MT 10 kV")
    ]

    # Dibujar la línea de Media Tensión con ancho geométrico visible de 2.5m (const_width=2.5)
    pts_mt = [(p[1], p[2]) for p in postes_mt_data]
    for i in range(len(pts_mt) - 1):
        p_a, p_b = pts_mt[i], pts_mt[i+1]
        pl_mt = msp.add_lwpolyline([p_a, p_b], dxfattribs={'layer': '01_RED_MT_10KV_CONDUCTOR', 'color': colors.RED})
        pl_mt.dxf.const_width = 2.5

    # Dibujar los postes de MT y las 3 Subestaciones (SEDs)
    total_postes_mt_cac12_300 = 0
    total_postes_mt_cac12_400 = 0
    total_postes_mt_cac13_400 = 0
    total_postes_mt_cac13_600 = 0
    total_seds = 0
    total_ret_mt = 0

    for pid, px, py, cota, poste, armado, ret, desc in postes_mt_data:
        if "SAB" in armado:
            total_seds += 1
            # SÍMBOLO DESTACADO DE SUBESTACIÓN BIPOSTE (18x12 metros)
            msp.add_lwpolyline([
                (px - 9.0, py - 6.0), (px + 9.0, py - 6.0),
                (px + 9.0, py + 6.0), (px - 9.0, py + 6.0),
                (px - 9.0, py - 6.0)
            ], dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': colors.YELLOW})
            
            # Postes Biposte (2 círculos de r=2.5m)
            msp.add_circle((px - 4.5, py), radius=2.5, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': colors.YELLOW})
            msp.add_circle((px + 4.5, py), radius=2.5, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': colors.YELLOW})
            
            # Símbolo transformador (círculo central r=3.5m)
            msp.add_circle((px, py), radius=3.5, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': colors.YELLOW})
            
            # Rótulo de la Subestación (Texto grande de 5.5m de altura)
            sed_label = pid + " " + desc.split("(")[0].strip()
            sed_kva = "(" + desc.split("(")[1].replace(")", "") + ")"
            
            t_s1 = msp.add_text(sed_label, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'height': 5.5, 'color': colors.YELLOW})
            t_s1.dxf.insert = (px + 11.0, py + 3.0)
            t_s2 = msp.add_text(sed_kva, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'height': 4.2, 'color': colors.YELLOW})
            t_s2.dxf.insert = (px + 11.0, py - 4.0)
            
            total_postes_mt_cac13_400 += 2
        else:
            # POSTE MT NORMALIZADO (Círculo de radio 3.5m con cruz de 7m)
            msp.add_circle((px, py), radius=3.5, dxfattribs={'layer': '02_POSTES_MT_10KV', 'color': colors.RED})
            msp.add_line((px - 3.5, py), (px + 3.5, py), dxfattribs={'layer': '02_POSTES_MT_10KV', 'color': colors.RED})
            msp.add_line((px, py - 3.5), (px, py + 3.5), dxfattribs={'layer': '02_POSTES_MT_10KV', 'color': colors.RED})
            
            # Rótulo del poste MT (Texto de altura 4.0m)
            t_p = msp.add_text(f"{pid} ({poste.replace('C.A.C. ', '')})", dxfattribs={'layer': '02_POSTES_MT_10KV', 'height': 4.0, 'color': colors.RED})
            t_p.dxf.insert = (px + 4.5, py + 1.5)

            if "12/300" in poste: total_postes_mt_cac12_300 += 1
            elif "12/400" in poste: total_postes_mt_cac12_400 += 1
            elif "13/600" in poste: total_postes_mt_cac13_600 += 1

        # Retenidas MT (Línea de 10m con bloque de anclaje de 2m)
        if ret != "Ninguna":
            total_ret_mt += 1
            dx_ret, dy_ret = (8.0, 6.0) if px < 425500 else (-8.0, -6.0)
            p_ancla = (px + dx_ret, py + dy_ret)
            msp.add_line((px, py), p_ancla, dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'linetype': 'DASHED', 'color': colors.MAGENTA})
            msp.add_circle(p_ancla, radius=1.5, dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'color': colors.MAGENTA})

    # -------------------------------------------------------------
    # 4. REDES DE BAJA TENSIÓN 380/220 V Y POSTES CAC 8m/9m
    # -------------------------------------------------------------
    postes_bt_coords = []
    lineas_bt_segmentos = []
    p_idx = 1
    total_luminarias = 0
    total_ret_bt = 0
    total_cac_8_200 = 0
    total_cac_8_300 = 0
    total_cac_9_300 = 0

    vano_objetivo = 35.0  # metros

    for v_pts in vias_polys:
        if len(v_pts) < 2:
            continue
        v_segs = []
        v_len = 0
        for k in range(len(v_pts) - 1):
            d = distancia(v_pts[k], v_pts[k+1])
            v_segs.append((v_pts[k], v_pts[k+1], d, v_len))
            v_len += d

        if v_len < 25.0:
            continue

        num_tramos = max(1, round(v_len / vano_objetivo))
        step = v_len / num_tramos

        pts_via_red = []
        for s in range(num_tramos + 1):
            target_d = s * step
            for p_a, p_b, seg_d, seg_start in v_segs:
                if seg_start <= target_d <= seg_start + seg_d:
                    frac = (target_d - seg_start) / max(0.001, seg_d)
                    pt = interp_pt(p_a, p_b, frac)
                    pts_via_red.append(pt)
                    break

        is_troncal = (v_len > 800.0)
        c_layer = '05_RED_BT_TRONCAL_CAAI' if is_troncal else '06_RED_BT_DERIVACION_CAAI'
        c_color = colors.GREEN if is_troncal else colors.CYAN
        c_width = 1.2 if is_troncal else 0.8

        for k in range(len(pts_via_red) - 1):
            pl_bt = msp.add_lwpolyline([pts_via_red[k], pts_via_red[k+1]],
                                       dxfattribs={'layer': c_layer, 'color': c_color})
            pl_bt.dxf.const_width = c_width
            lineas_bt_segmentos.append((pts_via_red[k], pts_via_red[k+1], is_troncal))

        for k, pt in enumerate(pts_via_red):
            is_end = (k == 0 or k == len(pts_via_red) - 1)
            is_principal = is_troncal

            if is_principal:
                p_tipo = "CAC 9/300"
                total_cac_9_300 += 1
                has_ap = True
            elif is_end:
                p_tipo = "CAC 8/300"
                total_cac_8_300 += 1
                has_ap = False
            else:
                p_tipo = "CAC 8/200"
                total_cac_8_200 += 1
                has_ap = (k % 2 == 0 and total_luminarias < 165)

            # POSTE BT (Círculo de radio 2.0m con punto interior de 0.8m)
            msp.add_circle(pt, radius=2.0, dxfattribs={'layer': '07_POSTES_BT_CAC', 'color': colors.BLUE})
            msp.add_circle(pt, radius=0.8, dxfattribs={'layer': '07_POSTES_BT_CAC', 'color': colors.BLUE})
            postes_bt_coords.append((f"P-{p_idx:03d}", pt[0], pt[1], p_tipo, has_ap))

            # Rótulo de poste BT cada 2 postes para no saturar la vista
            if p_idx % 2 == 1:
                t_pbt = msp.add_text(f"P-{p_idx}", dxfattribs={'layer': '07_POSTES_BT_CAC', 'height': 2.5, 'color': colors.BLUE})
                t_pbt.dxf.insert = (pt[0] + 2.5, pt[1] + 1.0)

            # Alumbrado público (Pastoral de 4m y luminaria LED de radio 1.2m)
            if has_ap and total_luminarias < 165:
                total_luminarias += 1
                p_lum = (pt[0] + 3.0, pt[1] + 2.5)
                msp.add_line(pt, p_lum, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})
                msp.add_circle(p_lum, radius=1.2, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})

            # Retenida BT en terminales
            if is_end:
                total_ret_bt += 1
                p_ret = (pt[0] - 5.0, pt[1] - 4.0)
                msp.add_line(pt, p_ret, dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'linetype': 'DASHED', 'color': colors.MAGENTA})
                msp.add_circle(p_ret, radius=1.0, dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'color': colors.MAGENTA})

            p_idx += 1

    # Completar 165 luminarias LED exactas
    if total_luminarias < 165:
        faltan = 165 - total_luminarias
        for p_item in postes_bt_coords:
            if faltan <= 0: break
            if not p_item[4]:
                pt = (p_item[1], p_item[2])
                p_lum = (pt[0] + 3.0, pt[1] + 2.5)
                msp.add_line(pt, p_lum, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})
                msp.add_circle(p_lum, radius=1.2, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})
                total_luminarias += 1
                faltan -= 1

    # -------------------------------------------------------------
    # 5. CUADRO DE LEYENDA Y MEMBRETE EN EL MODEL SPACE
    # -------------------------------------------------------------
    lx = 425780.0
    ly = 8435800.0

    msp.add_lwpolyline([
        (lx, ly), (lx + 180.0, ly),
        (lx + 180.0, ly - 220.0), (lx, ly - 220.0),
        (lx, ly)
    ], dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'color': colors.WHITE})

    t_ltit = msp.add_text("CUADRO DE SIMBOLOGÍA ELECTROMECÁNICA", dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'height': 6.5, 'color': colors.WHITE})
    t_ltit.dxf.insert = (lx + 10.0, ly - 15.0)
    msp.add_line((lx + 5.0, ly - 20.0), (lx + 175.0, ly - 20.0), dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'color': colors.WHITE})

    items_leyenda = [
        ("Línea Primaria 10 kV (AAAC 35 mm2)", colors.RED, "linea"),
        ("Poste MT (C.A.C. 12m y 13m)", colors.RED, "poste_mt"),
        ("Subestación Aérea Biposte (SAB 50/100 kVA)", colors.YELLOW, "sed"),
        ("Red BT Troncal CAAI 3x35+1x16+NA25", colors.GREEN, "linea_bt"),
        ("Red BT Derivación CAAI 2x16+1x16+NA25", colors.CYAN, "linea_bt_der"),
        ("Poste BT (C.A.C. 8m y 9m)", colors.BLUE, "poste_bt"),
        ("Alumbrado Público LED 50W (165 und)", 30, "ap"),
        ("Retenida / Anclaje a tierra", colors.MAGENTA, "ret")
    ]

    curr_y = ly - 35.0
    for texto, color_val, tipo in items_leyenda:
        if tipo == "linea":
            pl = msp.add_lwpolyline([(lx + 15.0, curr_y), (lx + 40.0, curr_y)], dxfattribs={'layer': '01_RED_MT_10KV_CONDUCTOR', 'color': color_val})
            pl.dxf.const_width = 2.5
        elif tipo == "poste_mt":
            msp.add_circle((lx + 27.5, curr_y), radius=3.5, dxfattribs={'layer': '02_POSTES_MT_10KV', 'color': color_val})
            msp.add_line((lx + 24.0, curr_y), (lx + 31.0, curr_y), dxfattribs={'layer': '02_POSTES_MT_10KV', 'color': color_val})
        elif tipo == "sed":
            msp.add_circle((lx + 23.0, curr_y), radius=2.5, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': color_val})
            msp.add_circle((lx + 32.0, curr_y), radius=2.5, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': color_val})
            msp.add_circle((lx + 27.5, curr_y), radius=3.5, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': color_val})
        elif tipo == "linea_bt":
            pl = msp.add_lwpolyline([(lx + 15.0, curr_y), (lx + 40.0, curr_y)], dxfattribs={'layer': '05_RED_BT_TRONCAL_CAAI', 'color': color_val})
            pl.dxf.const_width = 1.2
        elif tipo == "linea_bt_der":
            pl = msp.add_lwpolyline([(lx + 15.0, curr_y), (lx + 40.0, curr_y)], dxfattribs={'layer': '06_RED_BT_DERIVACION_CAAI', 'color': color_val})
            pl.dxf.const_width = 0.8
        elif tipo == "poste_bt":
            msp.add_circle((lx + 27.5, curr_y), radius=2.0, dxfattribs={'layer': '07_POSTES_BT_CAC', 'color': color_val})
            msp.add_circle((lx + 27.5, curr_y), radius=0.8, dxfattribs={'layer': '07_POSTES_BT_CAC', 'color': color_val})
        elif tipo == "ap":
            msp.add_circle((lx + 27.5, curr_y), radius=1.8, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': color_val})
        elif tipo == "ret":
            msp.add_line((lx + 15.0, curr_y), (lx + 35.0, curr_y), dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'linetype': 'DASHED', 'color': color_val})
            msp.add_circle((lx + 35.0, curr_y), radius=1.5, dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'color': color_val})

        t_desc = msp.add_text(texto, dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'height': 4.5, 'color': colors.WHITE})
        t_desc.dxf.insert = (lx + 50.0, curr_y - 1.5)
        curr_y -= 18.0

    curr_y -= 5.0
    msp.add_line((lx + 5.0, curr_y), (lx + 175.0, curr_y), dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'color': colors.WHITE})
    curr_y -= 12.0
    
    membrete_lines = [
        "UNIVERSIDAD NACIONAL DEL ALTIPLANO - PUNO",
        "FACULTAD DE INGENIERIA MECANICA ELECTRICA (FIME)",
        "PROYECTO: REDES ELECTRICAS MCH LIMBANI (200 kW)",
        "AUTOR: BR. AQUILES TAYLOR RAMOS YAPO (COD. 227368)",
        "SEMESTRE: 2026-II  |  ESCALA: 1:2500  |  ZONA: 19S"
    ]
    for m_line in membrete_lines:
        t_m = msp.add_text(m_line, dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'height': 3.8, 'color': colors.YELLOW})
        t_m.dxf.insert = (lx + 10.0, curr_y)
        curr_y -= 8.0

    # -------------------------------------------------------------
    # GUARDAR DXF
    # -------------------------------------------------------------
    os.makedirs(os.path.dirname(out_dxf), exist_ok=True)
    doc.saveas(out_dxf)
    print(f"[OK] Plano DXF de Redes Electricas generado en: {out_dxf}")

    os.makedirs(catastro_sync_dir, exist_ok=True)
    doc.saveas(catastro_sync_dxf)
    print(f"[OK] Copia sincronizada DXF en: {catastro_sync_dxf}")

    # -------------------------------------------------------------
    # COMPILACIÓN A DWG NATIVO AUTOCAD MEDIANTE ACCORECONSOLE
    # -------------------------------------------------------------
    accore = r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"
    if os.path.exists(accore):
        print("[*] Ejecutando AutoCAD 2027 Core Engine para encuadre y compilación DWG nativa...")
        if os.path.exists(out_dwg):
            try: os.remove(out_dwg)
            except Exception: pass
        scr_content = f"ZOOM\nE\nFILEDIA 0\nSAVEAS\n2018\n{out_dwg}\nQUIT\nY\n"
        scr_path = os.path.abspath(os.path.join(base_dir, "scripts", "temp_zoom_save.scr"))
        with open(scr_path, "w", encoding="ascii") as sf:
            sf.write(scr_content)
        try:
            cmd = [accore, "/i", os.path.abspath(out_dxf), "/s", scr_path]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
            if os.path.exists(out_dwg):
                print(f"[OK] Archivo DWG nativo compilado con Zoom Extents: {out_dwg}")
                shutil.copy2(out_dwg, catastro_sync_dwg)
                print(f"[OK] Copia sincronizada DWG en: {catastro_sync_dwg}")
        except Exception as err:
            print("[!] Nota al compilar DWG con AutoCAD:", err)
        finally:
            if os.path.exists(scr_path):
                os.remove(scr_path)

    # -------------------------------------------------------------
    # 6. GENERAR RENDERIZADOS GRÁFICOS DE ALTA DEFINICIÓN (PNG)
    # -------------------------------------------------------------
    print("[*] Generando láminas de inspección gráfica (Planta General y Zooms Sectoriales)...")
    
    # Extraer capas base para graficación
    rios_pts = [e.get_points('xy') for e in msp if e.dxf.layer == '01_RIOS_Y_CUENCAS' and e.dxftype() == 'LWPOLYLINE']
    lotes_pts = [e.get_points('xy') for e in msp if e.dxf.layer == '04_LOTES_PREDIALES' and e.dxftype() == 'LWPOLYLINE']
    huellas_pts = [e.get_points('xy') for e in msp if 'HUELLAS' in e.dxf.layer and e.dxftype() == 'LWPOLYLINE']
    equip_pts = [e.get_points('xy') for e in msp if e.dxf.layer == '07_EQUIPAMIENTOS' and e.dxftype() == 'LWPOLYLINE']

    def dibujar_elementos_comunes(ax, detalle_textos=False):
        # Fondo oscuro técnico CAD
        ax.set_facecolor('#0B0F19')
        
        # Ríos
        for pts in rios_pts:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#0284C7', linewidth=2.5, alpha=0.9, zorder=2)
        
        # Lotes
        for pts in lotes_pts:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#334155', linewidth=0.6, alpha=0.7, zorder=3)
            
        # Huellas de viviendas
        for pts in huellas_pts:
            ax.fill([p[0] for p in pts], [p[1] for p in pts], color='#F59E0B', alpha=0.35, zorder=3)

        # Equipamientos (Plaza, estadio, salud)
        for pts in equip_pts:
            ax.fill([p[0] for p in pts], [p[1] for p in pts], color='#10B981', alpha=0.25, zorder=3)

        # Vías
        for v_pts in vias_polys:
            ax.plot([p[0] for p in v_pts], [p[1] for p in v_pts], color='#64748B', linewidth=1.0, alpha=0.6, zorder=4)

        # Redes BT
        for p_a, p_b, is_tr in lineas_bt_segmentos:
            c_line = '#10B981' if is_tr else '#38BDF8'
            lw = 1.6 if is_tr else 1.0
            ax.plot([p_a[0], p_b[0]], [p_a[1], p_b[1]], color=c_line, linewidth=lw, alpha=0.9, zorder=5)

        # Postes BT
        ax.scatter([p[1] for p in postes_bt_coords], [p[2] for p in postes_bt_coords],
                   s=24, color='#60A5FA', edgecolors='#1E3A8A', linewidths=0.6, zorder=6, label='Postes BT (CAC 8m/9m)')

        # Alumbrado AP
        ap_pts = [p for p in postes_bt_coords if p[4]]
        ax.scatter([p[1] for p in ap_pts], [p[2] for p in ap_pts],
                   s=40, color='#FBBF24', edgecolors='#B45309', linewidths=0.8, zorder=7, label='Alumbrado Público LED (165 und)')

        # Línea MT 10 kV (Roja)
        ax.plot([p[0] for p in pts_mt], [p[1] for p in pts_mt], color='#EF4444', linewidth=3.5, zorder=8, label='Línea Primaria 10 kV (AAAC 35 mm²)')

        # Postes MT
        mt_normal = [p for p in postes_mt_data if "SAB" not in p[5]]
        ax.scatter([p[1] for p in mt_normal], [p[2] for p in mt_normal],
                   s=85, color='#DC2626', edgecolors='#FFFFFF', linewidths=1.5, zorder=9, label='Postes MT (CAC 12m/13m)')

        # Subestaciones SED
        seds_pts = [p for p in postes_mt_data if "SAB" in p[5]]
        ax.scatter([p[1] for p in seds_pts], [p[2] for p in seds_pts],
                   s=240, color='#FACC15', edgecolors='#78350F', linewidths=2.5, marker='s', zorder=10, label='Subestaciones Aéreas Biposte (3 SAB)')

        if detalle_textos:
            # Anotaciones de postes MT
            for p in mt_normal:
                ax.annotate(f"{p[0]}\n{p[4].replace('C.A.C. ', '')}", (p[1], p[2]),
                            xytext=(p[1] + 8, p[2] + 4), color='#FCA5A5', fontsize=8, fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.2", fc="#450A0A", ec="#EF4444", lw=0.8, alpha=0.85),
                            zorder=11)
            # Anotaciones de SEDs
            for p in seds_pts:
                ax.annotate(f"{p[0]}: {p[7].split('(')[0].strip()}\n({p[7].split('(')[1].replace(')', '')})",
                            (p[1], p[2]), xytext=(p[1] + 15, p[2] + 12),
                            color='#FEF08A', fontsize=9, fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.3", fc="#1E293B", ec="#FACC15", lw=1.2),
                            arrowprops=dict(arrowstyle="->", color='#FACC15', lw=1.2),
                            zorder=12)

    # -------------------------------------------------------------
    # (A) PLANO DE PLANTA GENERAL COMPLETO
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(16, 24), dpi=150)
    dibujar_elementos_comunes(ax, detalle_textos=False)

    seds_pts = [p for p in postes_mt_data if "SAB" in p[5]]
    for p in seds_pts:
        ax.annotate(f"{p[0]}: {p[7].split('(')[0].strip()}\n({p[7].split('(')[1].replace(')', '')})",
                    (p[1], p[2]), xytext=(p[1] + 45, p[2] + 25),
                    color='#FACC15', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#1E293B", ec="#FACC15", lw=1.2),
                    arrowprops=dict(arrowstyle="->", color='#FACC15', lw=1.2),
                    zorder=12)

    p_inicio = postes_mt_data[0]
    ax.annotate("MCH LIMBANI (200 kW)\nPórtico Elevador 0.38/10 kV",
                (p_inicio[1], p_inicio[2]), xytext=(p_inicio[1] - 220, p_inicio[2] + 40),
                color='#38BDF8', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", fc="#0F172A", ec="#38BDF8", lw=1.2),
                arrowprops=dict(arrowstyle="->", color='#38BDF8', lw=1.2),
                zorder=12)

    p_fin = postes_mt_data[-1]
    ax.annotate("Terminal MT 10 kV\nSalida hacia Crucero/Ananea",
                (p_fin[1], p_fin[2]), xytext=(p_fin[1] - 180, p_fin[2] - 50),
                color='#EF4444', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", fc="#0F172A", ec="#EF4444", lw=1.0),
                arrowprops=dict(arrowstyle="->", color='#EF4444', lw=1.0),
                zorder=12)

    ax.set_title("PLANO DE REDES ELÉCTRICAS Y POSTERÍA GEORREFERENCIADA - LIMBANI (PUNO)\n"
                 "Línea Primaria 10 kV | 3 Subestaciones SAB (250 kVA) | Redes Secundarias CAAI 380/220 V | Catastro WGS 84 Z19S",
                 color='#F8FAFC', fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='lower right', facecolor='#1E293B', edgecolor='#475569', labelcolor='#F8FAFC', fontsize=9)
    ax.set_xlabel("Este UTM (WGS 84 Zona 19 Sur) [m]", color='#94A3B8', fontsize=10)
    ax.set_ylabel("Norte UTM (WGS 84 Zona 19 Sur) [m]", color='#94A3B8', fontsize=10)
    ax.set_xlim(425100, 426150)
    ax.set_ylim(8434350, 8436850)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(color='#1E293B', linestyle='--', linewidth=0.5, alpha=0.7)

    plt.tight_layout()
    fig.savefig(out_img_gen, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"[OK] Lámina General guardada en: {out_img_gen}")

    # -------------------------------------------------------------
    # (B) ZOOM SECTOR NORTE: MCH LIMBANI (200 kW), PÓRTICO Y SED-01
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 10), dpi=180)
    dibujar_elementos_comunes(ax, detalle_textos=True)
    ax.set_xlim(425350, 425850)
    ax.set_ylim(8436100, 8436750)
    ax.set_title("DETALLE SECTOR NORTE: CASA DE MÁQUINAS MCH LIMBANI (200 kW) Y SUBESTACIÓN SED-01 (50 kVA)\n"
                 "Pórtico 0.38/10 kV (E-01), Bajada de Quebrada (E-02 a E-05) y Redes CAAI Jr. Villa Hermosa",
                 color='#F8FAFC', fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Este UTM [m]", color='#94A3B8', fontsize=9)
    ax.set_ylabel("Norte UTM [m]", color='#94A3B8', fontsize=9)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(color='#1E293B', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    fig.savefig(out_img_norte, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"[OK] Zoom Sector Norte guardado en: {out_img_norte}")

    # -------------------------------------------------------------
    # (C) ZOOM SECTOR CENTRO: PLAZA DE ARMAS, MUNICIPALIDAD Y SED-02
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 10), dpi=180)
    dibujar_elementos_comunes(ax, detalle_textos=True)
    ax.set_xlim(425250, 425650)
    ax.set_ylim(8435450, 8436150)
    ax.set_title("DETALLE SECTOR CENTRO: PLAZA DE ARMAS DE LIMBANI Y SUBESTACIÓN SED-02 (100 kVA)\n"
                 "Troncales CAAI 3x35+1x16+NA25, Derivaciones, Alumbrado LED 50W y Lotes Urbanos de Alta Densidad",
                 color='#F8FAFC', fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Este UTM [m]", color='#94A3B8', fontsize=9)
    ax.set_ylabel("Norte UTM [m]", color='#94A3B8', fontsize=9)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(color='#1E293B', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    fig.savefig(out_img_centro, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"[OK] Zoom Sector Centro guardado en: {out_img_centro}")

    # -------------------------------------------------------------
    # (D) ZOOM SECTOR SUR: CRUCE FLUVIO-AÉREO, ESTADIO Y SED-03
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 10), dpi=180)
    dibujar_elementos_comunes(ax, detalle_textos=True)
    ax.set_xlim(425200, 425650)
    ax.set_ylim(8434650, 8435450)
    ax.set_title("DETALLE SECTOR SUR: CRUCE AÉREO RÍO CHINCHALAMANI, ESTADIO Y SUBESTACIÓN SED-03 (100 kVA)\n"
                 "Vano Especial 110m (CAC 13/600 daN, E-17 a E-18), SED-03 Estadio-Piscina y Terminal E-24",
                 color='#F8FAFC', fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Este UTM [m]", color='#94A3B8', fontsize=9)
    ax.set_ylabel("Norte UTM [m]", color='#94A3B8', fontsize=9)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(color='#1E293B', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    fig.savefig(out_img_sur, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"[OK] Zoom Sector Sur guardado en: {out_img_sur}")

    # Resumen metrados
    long_mt_total = sum(distancia(pts_mt[i], pts_mt[i+1]) for i in range(len(pts_mt)-1))
    long_bt_troncal = sum(distancia(p_a, p_b) for p_a, p_b, is_tr in lineas_bt_segmentos if is_tr)
    long_bt_deriv = sum(distancia(p_a, p_b) for p_a, p_b, is_tr in lineas_bt_segmentos if not is_tr)

    print("\n" + "="*70)
    print("METRADOS EXACTOS DEL MODELO CAD LIMBANI:")
    print("="*70)
    print(f"Línea Primaria 10.0 kV (AAAC 35 mm2):        {long_mt_total:.2f} m  ({long_mt_total/1000:.3f} km)")
    print(f"Postes MT CAC 12m/300 daN (Alineamiento):   {total_postes_mt_cac12_300} unidades")
    print(f"Postes MT CAC 12m/400 daN (Ángulos):        {total_postes_mt_cac12_400} unidades")
    print(f"Postes MT CAC 13m/400 daN (SAB Biposte):    {total_postes_mt_cac13_400} unidades (en {total_seds} subestaciones)")
    print(f"Postes MT CAC 13m/600 daN (Cruce río):      {total_postes_mt_cac13_600} unidades")
    print(f"Total Postes en Media Tensión:              {total_postes_mt_cac12_300 + total_postes_mt_cac12_400 + total_postes_mt_cac13_400 + total_postes_mt_cac13_600} unidades")
    print(f"Subestaciones Aéreas Biposte (SAB):         {total_seds} subestaciones (50, 100, 100 kVA)")
    print(f"Retenidas en Media Tensión:                 {total_ret_mt} unidades")
    print("-"*70)
    print(f"Red BT Troncal CAAI 3x35+1x16+NA25:         {long_bt_troncal:.2f} m")
    print(f"Red BT Ramales CAAI 2x16+1x16+NA25:         {long_bt_deriv:.2f} m")
    print(f"Total Conductor BT Autoportante:            {long_bt_troncal + long_bt_deriv:.2f} m")
    print(f"Postes BT CAC 8m/200 daN (Pasajes):         {total_cac_8_200} unidades")
    print(f"Postes BT CAC 8m/300 daN (Retenciones):     {total_cac_8_300} unidades")
    print(f"Postes BT CAC 9m/300 daN (Troncales/AP):    {total_cac_9_300} unidades")
    print(f"Total Postes en Baja Tensión:               {len(postes_bt_coords)} unidades")
    print(f"Luminarias Alumbrado Público LED 50W:       {total_luminarias} unidades")
    print(f"Retenidas en Baja Tensión:                  {total_ret_bt} unidades")
    print("="*70)

if __name__ == "__main__":
    main()
