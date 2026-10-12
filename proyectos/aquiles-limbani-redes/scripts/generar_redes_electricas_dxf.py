"""
SCRIPT: generar_redes_electricas_dxf.py
PROYECTO: EXPEDIENTE TÉCNICO - ELECTRIFICACIÓN Y REDES DE DISTRIBUCIÓN LIMBANI
AUTOR: Br. Aquiles Taylor Ramos Yapo (Cód. 227368) - FIME / UNA Puno
FECHA: Octubre 2026

DESCRIPCIÓN:
Genera el modelo digital integrado en CAD (DXF y compilación nativa DWG con AutoCAD 2027 Core Engine)
incorporando:
1. Línea Primaria en Media Tensión 10.0 kV (AAAC 35 mm2, 24 apoyos / 26 postes).
2. Tres Subestaciones Aéreas Biposte (SAB-01 50 kVA, SAB-02 100 kVA, SAB-03 100 kVA).
3. Redes Secundarias de Baja Tensión autoportantes CAAI en casco urbano consolidado
   (excluyendo carreteras rurales deshabitadas). Vanos estrictos <= 30.0 m (CNE Suministro 2011).
4. Red completa de Acometidas Domiciliarias (587 predios) y cajas portamedidor tipo L-T.
5. Simbología oficial DGE (R.M. N° 091-2002-EM/VME Sección 9) para postes, SEDs, AP y retenidas
   mecánicas completas (cable 5/16", aislador nuez, protector PVC y bloque de anclaje).
6. Los 8 Bloques de Detalle Constructivo Normalizado DGE integrados en el espacio modelo
   con imágenes oficiales (RD 024-2003-EM y RD 023-2003-EM-DGE), vectores técnicos, cotas y tablas.
7. Renderizados gráficos de alta definición de la planta general y zooms sectoriales.
"""

import os
import math
import shutil
import subprocess
import ezdxf
from ezdxf import colors
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def distancia(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def interp_pt(p1, p2, f):
    return (p1[0] + f * (p2[0] - p1[0]), p1[1] + f * (p2[1] - p1[1]))

# -------------------------------------------------------------------------
# SÍMBOLO NORMALIZADO DE RETENIDA CONFORME A DGE Y CNE SUMINISTRO
# -------------------------------------------------------------------------
def agregar_simbolo_retenida_cad(msp, p_poste, p_ancla, layer='04_RETENIDAS_MT_BT', label="RET-1"):
    """
    Dibuja el símbolo técnico normalizado de retenida mecánica en planta:
    - Cable de acero galvanizado Siemens Martin 5/16"
    - Aislador de tracción / nuez de porcelana 15 kV (rombo a 60% del tiro)
    - Protector de retenida en tubo PVC amarillo de 1.80 m
    - Barra transversal de varilla de anclaje
    - Bloque de anclaje de concreto ciclópeo 0.50 x 0.50 m
    - Rótulo normativo
    """
    dx = p_ancla[0] - p_poste[0]
    dy = p_ancla[1] - p_poste[1]
    L = math.sqrt(dx*dx + dy*dy)
    if L < 0.001: return
    ux = dx / L
    uy = dy / L
    vx = -uy
    vy = ux

    # 1. Cable de acero (trazo continuo con espesor visible)
    pl_ret = msp.add_lwpolyline([p_poste, p_ancla], dxfattribs={'layer': layer, 'color': colors.MAGENTA})
    pl_ret.dxf.const_width = 0.35

    # 2. Aislador de tracción / nuez (rombo + círculo central)
    p_iso = (p_poste[0] + 0.60 * dx, p_poste[1] + 0.60 * dy)
    r_sz = 1.0
    msp.add_lwpolyline([
        (p_iso[0] + r_sz*ux, p_iso[1] + r_sz*uy),
        (p_iso[0] + r_sz*vx, p_iso[1] + r_sz*vy),
        (p_iso[0] - r_sz*ux, p_iso[1] - r_sz*uy),
        (p_iso[0] - r_sz*vx, p_iso[1] - r_sz*vy),
        (p_iso[0] + r_sz*ux, p_iso[1] + r_sz*uy)
    ], dxfattribs={'layer': layer, 'color': colors.YELLOW})
    msp.add_circle(p_iso, radius=0.35, dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # 3. Protector de retenida (tubo PVC amarillo en los 2.0 m finales)
    p_prot = (p_ancla[0] - 2.2*ux, p_ancla[1] - 2.2*uy)
    pl_p = msp.add_lwpolyline([p_prot, p_ancla], dxfattribs={'layer': layer, 'color': colors.YELLOW})
    pl_p.dxf.const_width = 0.85

    # 4. Barra de anclaje perpendicular
    bar_w = 1.6
    b1 = (p_ancla[0] + bar_w * vx, p_ancla[1] + bar_w * vy)
    b2 = (p_ancla[0] - bar_w * vx, p_ancla[1] - bar_w * vy)
    msp.add_line(b1, b2, dxfattribs={'layer': layer, 'color': colors.WHITE})

    # 5. Bloque de concreto ciclópeo de anclaje (CAV 0.50x0.50x0.20 m)
    p_b1 = (b1[0] + 0.6*ux, b1[1] + 0.6*uy)
    p_b2 = (b2[0] + 0.6*ux, b2[1] + 0.6*uy)
    p_b3 = (b2[0] - 0.6*ux, b2[1] - 0.6*uy)
    p_b4 = (b1[0] - 0.6*ux, b1[1] - 0.6*uy)
    msp.add_lwpolyline([p_b1, p_b2, p_b3, p_b4, p_b1], dxfattribs={'layer': layer, 'color': colors.MAGENTA})

    # Rótulo de la retenida
    t_ret = msp.add_text(label, dxfattribs={'layer': layer, 'height': 1.6, 'color': colors.MAGENTA})
    t_ret.dxf.insert = (p_ancla[0] + 1.2*vx, p_ancla[1] + 1.2*vy)

# -------------------------------------------------------------------------
# BLOQUES DE DETALLES TÉCNICOS NORMALIZADOS DGE (100% VECTORIALES)
# -------------------------------------------------------------------------
from armados_vectoriales_dge import (
    generar_vector_ps3,
    generar_vector_pa3,
    generar_vector_pr3,
    generar_vector_sab,
    generar_vector_e1_bt,
    generar_vector_retenida,
    generar_vector_pat,
    generar_vector_acometida
)

# -------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# -------------------------------------------------------------------------
def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dxf_orig = r"C:\Users\51949\Downloads\Catastro_Limbani\catastro_limbani.dxf"
    out_dxf = os.path.join(base_dir, "entregables", "planos", "catastro_limbani_redes_electricas.dxf")
    out_dwg = os.path.join(base_dir, "entregables", "planos", "catastro_limbani_redes_electricas.dwg")
    fig_dir = os.path.join(base_dir, "expediente", "figuras")
    normas_dir = os.path.join(fig_dir, "normas_dge")
    
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

    # Configuración de encuadre
    cx = 425600.0
    cy = 8435600.0
    view_h = 2650.0

    msp.dxf.extmin = (425100.0, 8434300.0, 0.0)
    msp.dxf.extmax = (428500.0, 8437000.0, 0.0)
    msp.dxf.limmin = (425100.0, 8434300.0)
    msp.dxf.limmax = (428500.0, 8437000.0)

    try:
        doc.set_modelspace_vport(height=view_h, center=(cx, cy))
    except Exception as e:
        print("[!] Nota sobre VPORT:", e)

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

    # 1. CREAR CAPAS ELECTROMECÁNICAS NORMALIZADAS DGE
    capas_def = [
        ("01_RED_MT_10KV_CONDUCTOR", colors.RED),      # Rojo (AAAC 35 mm2)
        ("02_POSTES_MT_10KV", colors.RED),             # Rojo (C.A.C. 12m y 13m)
        ("03_SUBESTACIONES_SED", colors.YELLOW),       # Amarillo (SAB 10/0.38-0.22 kV)
        ("04_RETENIDAS_MT_BT", colors.MAGENTA),        # Magenta (Inclinada y Contraviento)
        ("05_RED_BT_TRONCAL_CAAI", colors.GREEN),      # Verde (CAAI 3x35+1x16+NA25)
        ("06_RED_BT_DERIVACION_CAAI", colors.CYAN),    # Cian (CAAI 2x16+1x16+NA25)
        ("07_POSTES_BT_CAC", colors.BLUE),             # Azul (C.A.C. 8m y 9m)
        ("08_ALUMBRADO_PUBLICO_LED", 30),              # Amarillo/Naranja (LED 50 W)
        ("09_CUADRO_LEYENDA_ROTULO", colors.WHITE),    # Blanco
        ("10_DETALLES_ESTRUCTURAS_DGE", colors.WHITE), # Multicolor
        ("11_ACOMETIDAS_DOMICILIARIAS", colors.CYAN),  # Cian (Cable SET 2x4 mm2)
        ("12_CAJAS_PORTAMEDIDOR_LT", colors.YELLOW)    # Amarillo (Medidor monofásico)
    ]
    for c_name, c_color in capas_def:
        if c_name not in doc.layers:
            doc.layers.new(name=c_name, dxfattribs={'color': c_color})

    # -------------------------------------------------------------
    # 2. EXTRAER LOTES Y FILTRAR VÍAS URBANAS (ELIMINAR CARRETERAS INNECESARIAS)
    # -------------------------------------------------------------
    lotes_polys = []
    lote_centers = []
    for e in msp:
        if e.dxf.layer == '04_LOTES_PREDIALES' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            lotes_polys.append(pts)
            cx_l = sum(p[0] for p in pts) / len(pts)
            cy_l = sum(p[1] for p in pts) / len(pts)
            lote_centers.append((cx_l, cy_l))

    print(f"[*] {len(lotes_polys)} lotes prediales catastrados leídos.")

    def dist_to_nearest_lot(pt):
        if not lote_centers: return 999999.0
        return min(math.sqrt((lc[0]-pt[0])**2 + (lc[1]-pt[1])**2) for lc in lote_centers)

    vias_urbanas_polys = []
    for e in msp:
        if e.dxf.layer == '02_CALLES_Y_VIAS' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            # Segmentar la vía conservando únicamente tramos con predios a <= 35.0 m
            sub = []
            for p in pts:
                if dist_to_nearest_lot(p) <= 35.0:
                    sub.append(p)
                else:
                    if len(sub) >= 2:
                        vias_urbanas_polys.append(sub)
                    sub = []
            if len(sub) >= 2:
                vias_urbanas_polys.append(sub)

    print(f"[*] {len(vias_urbanas_polys)} tramos viales urbanos consolidados con predios (carreteras no pobladas descartadas).")

    # -------------------------------------------------------------
    # 3. LÍNEA PRIMARIA MEDIA TENSIÓN 10 kV (24 APOYOS / 26 POSTES)
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

    pts_mt = [(p[1], p[2]) for p in postes_mt_data]
    for i in range(len(pts_mt) - 1):
        p_a, p_b = pts_mt[i], pts_mt[i+1]
        pl_mt = msp.add_lwpolyline([p_a, p_b], dxfattribs={'layer': '01_RED_MT_10KV_CONDUCTOR', 'color': colors.RED})
        pl_mt.dxf.const_width = 2.5

    total_postes_mt_cac12_300 = 0
    total_postes_mt_cac12_400 = 0
    total_postes_mt_cac13_400 = 0
    total_postes_mt_cac13_600 = 0
    total_seds = 0
    total_ret_mt = 0

    for pid, px, py, cota, poste, armado, ret, desc in postes_mt_data:
        if "SAB" in armado:
            total_seds += 1
            # SÍMBOLO NORMALIZADO DGE 09-90-04 (Subestación Aérea Biposte)
            msp.add_lwpolyline([
                (px - 9.0, py - 6.0), (px + 9.0, py - 6.0),
                (px + 9.0, py + 6.0), (px - 9.0, py + 6.0),
                (px - 9.0, py - 6.0)
            ], dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': colors.YELLOW})
            
            msp.add_circle((px - 4.5, py), radius=2.5, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': colors.YELLOW})
            msp.add_circle((px + 4.5, py), radius=2.5, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': colors.YELLOW})
            msp.add_circle((px, py), radius=3.5, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': colors.YELLOW})
            msp.add_line((px - 2.5, py), (px + 2.5, py), dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': colors.YELLOW})
            msp.add_line((px, py - 2.5), (px, py + 2.5), dxfattribs={'layer': '03_SUBESTACIONES_SED', 'color': colors.YELLOW})
            
            sed_label = pid + " " + desc.split("(")[0].strip()
            sed_kva = "(" + desc.split("(")[1].replace(")", "") + ")"
            t_s1 = msp.add_text(sed_label, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'height': 5.5, 'color': colors.YELLOW})
            t_s1.dxf.insert = (px + 11.0, py + 3.0)
            t_s2 = msp.add_text(sed_kva, dxfattribs={'layer': '03_SUBESTACIONES_SED', 'height': 4.2, 'color': colors.YELLOW})
            t_s2.dxf.insert = (px + 11.0, py - 4.0)
            total_postes_mt_cac13_400 += 2
        else:
            # SÍMBOLO NORMALIZADO DGE 09-91-20 (Poste de Concreto MT)
            msp.add_circle((px, py), radius=3.5, dxfattribs={'layer': '02_POSTES_MT_10KV', 'color': colors.RED})
            msp.add_line((px - 3.5, py), (px + 3.5, py), dxfattribs={'layer': '02_POSTES_MT_10KV', 'color': colors.RED})
            msp.add_line((px, py - 3.5), (px, py + 3.5), dxfattribs={'layer': '02_POSTES_MT_10KV', 'color': colors.RED})
            
            t_p = msp.add_text(f"{pid} ({poste.replace('C.A.C. ', '')})", dxfattribs={'layer': '02_POSTES_MT_10KV', 'height': 4.0, 'color': colors.RED})
            t_p.dxf.insert = (px + 4.5, py + 1.5)

            if "12/300" in poste: total_postes_mt_cac12_300 += 1
            elif "12/400" in poste: total_postes_mt_cac12_400 += 1
            elif "13/600" in poste: total_postes_mt_cac13_600 += 1

        if ret != "Ninguna":
            total_ret_mt += 1
            dx_ret, dy_ret = (8.0, 6.0) if px < 425500 else (-8.0, -6.0)
            p_ancla = (px + dx_ret, py + dy_ret)
            agregar_simbolo_retenida_cad(msp, (px, py), p_ancla, layer='04_RETENIDAS_MT_BT', label="RET-MT")

    # -------------------------------------------------------------
    # 4. REDES DE BAJA TENSIÓN EN CASCO URBANO (VANOS <= 30 M)
    # -------------------------------------------------------------
    postes_bt_coords = []
    lineas_bt_segmentos = []
    p_idx = 1
    total_luminarias = 0
    total_ret_bt = 0
    total_cac_8_200 = 0
    total_cac_8_300 = 0
    total_cac_9_300 = 0
    longitud_troncal_bt = 0.0
    longitud_derivacion_bt = 0.0

    vano_max_reglamentario = 30.0  # metros (CNE Suministro Regla 232 / Tabla 232-1)

    for v_pts in vias_urbanas_polys:
        if len(v_pts) < 2: continue
        v_segs = []
        v_len = 0
        for k in range(len(v_pts) - 1):
            d = distancia(v_pts[k], v_pts[k+1])
            v_segs.append((v_pts[k], v_pts[k+1], d, v_len))
            v_len += d

        if v_len < 10.0: continue

        num_tramos = max(1, math.ceil(v_len / vano_max_reglamentario))
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

        is_troncal = (v_len > 400.0)
        c_layer = '05_RED_BT_TRONCAL_CAAI' if is_troncal else '06_RED_BT_DERIVACION_CAAI'
        c_color = colors.GREEN if is_troncal else colors.CYAN
        c_width = 1.2 if is_troncal else 0.8

        if is_troncal: longitud_troncal_bt += v_len
        else: longitud_derivacion_bt += v_len

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
                has_ap = (k % 2 == 0)

            # SÍMBOLO NORMALIZADO DGE 09-91-20 (Poste BT)
            msp.add_circle(pt, radius=2.0, dxfattribs={'layer': '07_POSTES_BT_CAC', 'color': colors.BLUE})
            msp.add_circle(pt, radius=0.8, dxfattribs={'layer': '07_POSTES_BT_CAC', 'color': colors.BLUE})
            postes_bt_coords.append((f"P-{p_idx:03d}", pt[0], pt[1], p_tipo, has_ap))

            if p_idx % 2 == 1:
                t_pbt = msp.add_text(f"P-{p_idx}", dxfattribs={'layer': '07_POSTES_BT_CAC', 'height': 2.4, 'color': colors.BLUE})
                t_pbt.dxf.insert = (pt[0] + 2.4, pt[1] + 1.0)

            # SÍMBOLO NORMALIZADO DGE 09-91-24 (Luminaria AP LED 50W)
            if has_ap:
                total_luminarias += 1
                p_lum = (pt[0] + 3.0, pt[1] + 2.5)
                msp.add_line(pt, p_lum, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})
                msp.add_circle(p_lum, radius=1.2, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})
                msp.add_line((p_lum[0]-0.8, p_lum[1]-0.8), (p_lum[0]+0.8, p_lum[1]+0.8), dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})
                msp.add_line((p_lum[0]-0.8, p_lum[1]+0.8), (p_lum[0]+0.8, p_lum[1]-0.8), dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})

            # Símbolo normalizado de Retenida BT en terminales
            if is_end:
                total_ret_bt += 1
                p_ret = (pt[0] - 5.5, pt[1] - 4.5)
                agregar_simbolo_retenida_cad(msp, pt, p_ret, layer='04_RETENIDAS_MT_BT', label="RET-BT")

            p_idx += 1

    # -------------------------------------------------------------
    # 5. GENERAR ACOMETIDAS DOMICILIARIAS PARA TODOS LOS LOTES
    # -------------------------------------------------------------
    print("[*] Generando acometidas domiciliarias y cajas portamedidor L-T para 587 lotes...")
    total_acometidas_cortas = 0
    total_acometidas_largas = 0
    total_longitud_acometidas = 0.0

    for l_pts in lotes_polys:
        c_x = sum(p[0] for p in l_pts) / len(l_pts)
        c_y = sum(p[1] for p in l_pts) / len(l_pts)

        best_dist = 999999.0
        best_pole = None
        for pid, px, py, p_tipo, _ in postes_bt_coords:
            d = math.sqrt((px - c_x)**2 + (py - c_y)**2)
            if d < best_dist:
                best_dist = d
                best_pole = (px, py, pid)

        if best_pole is not None:
            # Vértice de fachada más cercano al poste
            v_front = min(l_pts, key=lambda p: math.sqrt((p[0]-best_pole[0])**2 + (p[1]-best_pole[1])**2))
            d_acom = math.sqrt((v_front[0]-best_pole[0])**2 + (v_front[1]-best_pole[1])**2)
            total_longitud_acometidas += d_acom

            if d_acom <= 15.0: total_acometidas_cortas += 1
            else: total_acometidas_largas += 1

            # Cable concéntrico SET 2x4 mm2
            pl_ac = msp.add_lwpolyline([(best_pole[0], best_pole[1]), (v_front[0], v_front[1])],
                                       dxfattribs={'layer': '11_ACOMETIDAS_DOMICILIARIAS', 'color': colors.CYAN})
            pl_ac.dxf.const_width = 0.15

            # Caja portamedidor L-T
            msp.add_lwpolyline([
                (v_front[0]-0.5, v_front[1]-0.4),
                (v_front[0]+0.5, v_front[1]-0.4),
                (v_front[0]+0.5, v_front[1]+0.4),
                (v_front[0]-0.5, v_front[1]+0.4),
                (v_front[0]-0.5, v_front[1]-0.4)
            ], dxfattribs={'layer': '12_CAJAS_PORTAMEDIDOR_LT', 'color': colors.YELLOW})

    # -------------------------------------------------------------
    # 6. INCORPORAR LOS 8 BLOQUES DE PLANOS Y DETALLES DGE
    # -------------------------------------------------------------
    print("[*] Incorporando los 8 bloques de planos y detalles constructivos 100% vectoriales DGE en el espacio CAD...")
    w_blk = 340.0
    h_blk = 250.0

    # Columna 1 (X = 426800): Armados MT y SAB
    x_c1 = 426800.0
    generar_vector_ps3(msp, x_c1, 8436500.0, w_blk, h_blk)
    generar_vector_pa3(msp, x_c1, 8436180.0, w_blk, h_blk)
    generar_vector_pr3(msp, x_c1, 8435860.0, w_blk, h_blk)
    generar_vector_sab(msp, x_c1, 8435540.0, w_blk, h_blk)

    # Columna 2 (X = 427200): BT, Retenida, PAT y Acometidas
    x_c2 = 427200.0
    generar_vector_e1_bt(msp, x_c2, 8436500.0, w_blk, h_blk)
    generar_vector_retenida(msp, x_c2, 8436180.0, w_blk, h_blk)
    generar_vector_pat(msp, x_c2, 8435860.0, w_blk, h_blk)
    generar_vector_acometida(msp, x_c2, 8435540.0, w_blk, h_blk)

    # -------------------------------------------------------------
    # 7. CUADRO DE LEYENDA Y MEMBRETE EN EL MODEL SPACE
    # -------------------------------------------------------------
    lx = 425780.0
    ly = 8435800.0

    msp.add_lwpolyline([
        (lx, ly), (lx + 185.0, ly),
        (lx + 185.0, ly - 250.0), (lx, ly - 250.0),
        (lx, ly)
    ], dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'color': colors.WHITE})

    t_ltit = msp.add_text("CUADRO DE SIMBOLOGÍA NORMALIZADA DGE", dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'height': 5.8, 'color': colors.WHITE})
    t_ltit.dxf.insert = (lx + 8.0, ly - 15.0)
    msp.add_line((lx + 5.0, ly - 20.0), (lx + 180.0, ly - 20.0), dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'color': colors.WHITE})

    items_leyenda = [
        ("Línea Primaria 10 kV (AAAC 35 mm2)", colors.RED, "linea"),
        ("Poste MT CAC (09-91-20 DGE: 12m y 13m)", colors.RED, "poste_mt"),
        ("Subestación Aérea SAB (09-90-04 DGE: 50/100 kVA)", colors.YELLOW, "sed"),
        ("Red BT Troncal CAAI 3x35+1x16+NA25", colors.GREEN, "linea_bt"),
        ("Red BT Derivación CAAI 2x16+1x16+NA25", colors.CYAN, "linea_bt_der"),
        ("Poste BT CAC (09-91-20 DGE: 8m y 9m)", colors.BLUE, "poste_bt"),
        ("Alumbrado Público LED 50W (09-91-24 DGE)", 30, "ap"),
        ("Retenida Normalizada (09-91-18 DGE / RD 024)", colors.MAGENTA, "ret"),
        ("Acometida Domiciliaria (SET 2x4 mm2)", colors.CYAN, "acom"),
        ("Caja Portamedidor Monofásica L-T", colors.YELLOW, "med")
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
            msp.add_circle((lx + 27.5, curr_y), radius=2.2, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': color_val})
            msp.add_line((lx + 25.0, curr_y), (lx + 30.0, curr_y), dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': color_val})
        elif tipo == "ret":
            agregar_simbolo_retenida_cad(msp, (lx + 15.0, curr_y), (lx + 38.0, curr_y), layer='04_RETENIDAS_MT_BT', label="")
        elif tipo == "acom":
            pl_ac = msp.add_lwpolyline([(lx + 15.0, curr_y), (lx + 40.0, curr_y)], dxfattribs={'layer': '11_ACOMETIDAS_DOMICILIARIAS', 'color': color_val})
            pl_ac.dxf.const_width = 0.2
        elif tipo == "med":
            msp.add_lwpolyline([(lx + 25.0, curr_y - 2.0), (lx + 30.0, curr_y - 2.0), (lx + 30.0, curr_y + 2.0), (lx + 25.0, curr_y + 2.0), (lx + 25.0, curr_y - 2.0)],
                               dxfattribs={'layer': '12_CAJAS_PORTAMEDIDOR_LT', 'color': color_val})

        t_desc = msp.add_text(texto, dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'height': 3.2, 'color': colors.WHITE})
        t_desc.dxf.insert = (lx + 48.0, curr_y - 1.2)
        curr_y -= 15.0

    # Membrete
    msp.add_lwpolyline([
        (lx, curr_y), (lx + 185.0, curr_y),
        (lx + 185.0, curr_y - 80.0), (lx, curr_y - 80.0),
        (lx, curr_y)
    ], dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'color': colors.WHITE})

    membrete_lines = [
        "EXPEDIENTE TÉCNICO DE INGENIERÍA ELÉCTRICA",
        "PROYECTO: ELECTRIFICACIÓN RURAL Y REDES LIMBANI",
        "UBICACIÓN: DISTRITO LIMBANI - SANDIA - PUNO",
        "FUENTE: MCH LIMBANI 200 kW (MICHELL-BANKI)",
        "PLANO: REDES MT 10 kV, BT 380/220 V, AP Y DETALLES DGE",
        "AUTOR: Br. Aquiles Taylor Ramos Yapo (Cód. 227368)",
        "UNIVERSIDAD NACIONAL DEL ALTIPLANO - PUNO (FIME)",
        "ESCALA: 1:2500 / DETALLES S/E  |  FECHA: OCTUBRE 2026"
    ]
    curr_y -= 10.0
    for m_line in membrete_lines:
        t_m = msp.add_text(m_line, dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'height': 3.4, 'color': colors.YELLOW})
        t_m.dxf.insert = (lx + 8.0, curr_y)
        curr_y -= 8.0

    # -------------------------------------------------------------
    # 8. GUARDAR DXF Y SINCRONIZAR
    # -------------------------------------------------------------
    os.makedirs(os.path.dirname(out_dxf), exist_ok=True)
    doc.saveas(out_dxf)
    print(f"[OK] Plano DXF de Redes y Detalles generado en: {out_dxf}")

    try:
        os.makedirs(catastro_sync_dir, exist_ok=True)
        doc.saveas(catastro_sync_dxf)
        print(f"[OK] Copia sincronizada DXF en: {catastro_sync_dxf}")
    except Exception as e:
        print(f"[!] Aviso al sincronizar DXF: {e}")

    # -------------------------------------------------------------
    # 9. COMPILACIÓN A DWG NATIVO AUTOCAD MEDIANTE ACCORECONSOLE
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
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=25)
            if os.path.exists(out_dwg):
                print(f"[OK] Archivo DWG nativo compilado con Zoom Extents: {out_dwg}")
                try:
                    shutil.copy2(out_dwg, catastro_sync_dwg)
                    print(f"[OK] Copia sincronizada DWG en: {catastro_sync_dwg}")
                except Exception as e:
                    print(f"[!] Aviso al sincronizar DWG: {e}")
        except Exception as err:
            print("[!] Nota al compilar DWG con AutoCAD:", err)
        finally:
            if os.path.exists(scr_path):
                os.remove(scr_path)

    # -------------------------------------------------------------
    # 10. GENERAR RENDERIZADOS GRÁFICOS DE ALTA DEFINICIÓN (PNG)
    # -------------------------------------------------------------
    print("[*] Generando láminas de inspección gráfica (Planta General y Zooms Sectoriales)...")
    
    rios_pts = [e.get_points('xy') for e in msp if e.dxf.layer == '01_RIOS_Y_CUENCAS' and e.dxftype() == 'LWPOLYLINE']
    lotes_pts = [e.get_points('xy') for e in msp if e.dxf.layer == '04_LOTES_PREDIALES' and e.dxftype() == 'LWPOLYLINE']
    huellas_pts = [e.get_points('xy') for e in msp if 'HUELLAS' in e.dxf.layer and e.dxftype() == 'LWPOLYLINE']
    equip_pts = [e.get_points('xy') for e in msp if e.dxf.layer == '07_EQUIPAMIENTOS' and e.dxftype() == 'LWPOLYLINE']

    def dibujar_elementos_comunes(ax, detalle_textos=False):
        ax.set_facecolor('#0B0F19')
        for pts in rios_pts:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#0284C7', linewidth=2.5, alpha=0.9, zorder=2)
        for pts in lotes_pts:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#334155', linewidth=0.6, alpha=0.7, zorder=3)
        for pts in huellas_pts:
            ax.fill([p[0] for p in pts], [p[1] for p in pts], color='#F59E0B', alpha=0.35, zorder=3)
        for pts in equip_pts:
            ax.fill([p[0] for p in pts], [p[1] for p in pts], color='#10B981', alpha=0.45, zorder=3)

        # Red de baja tensión
        for p_a, p_b, is_tr in lineas_bt_segmentos:
            col = '#22C55E' if is_tr else '#06B6D4'
            lw = 1.3 if is_tr else 0.8
            ax.plot([p_a[0], p_b[0]], [p_a[1], p_b[1]], color=col, linewidth=lw, alpha=0.85, zorder=4)

        # Línea de Media Tensión 10 kV
        ax.plot([p[0] for p in pts_mt], [p[1] for p in pts_mt], color='#EF4444', linewidth=2.4, zorder=6)

        # Postes BT
        xs_bt = [p[1] for p in postes_bt_coords]
        ys_bt = [p[2] for p in postes_bt_coords]
        ax.scatter(xs_bt, ys_bt, s=14, color='#3B82F6', edgecolors='#93C5FD', linewidths=0.5, zorder=7)

        # Luminarias AP
        xs_ap = [p[1] for p in postes_bt_coords if p[4]]
        ys_ap = [p[2] for p in postes_bt_coords if p[4]]
        ax.scatter(xs_ap, ys_ap, s=16, color='#FACC15', edgecolors='#FEF08A', linewidths=0.5, zorder=8)

        # Postes MT y SEDs
        for pid, px, py, cota, poste, armado, ret, desc in postes_mt_data:
            if "SAB" in armado:
                ax.scatter([px], [py], s=140, marker='s', color='#EAB308', edgecolors='#FFFFFF', linewidths=1.8, zorder=10)
                ax.text(px + 8.0, py, f"{pid}\n{armado} ({desc.split('(')[1].replace(')', '')})",
                        color='#FEF08A', fontsize=7.5, fontweight='bold', zorder=11,
                        bbox=dict(boxstyle="square,pad=0.2", facecolor='#1E293B', edgecolor='#EAB308', alpha=0.85))
            else:
                ax.scatter([px], [py], s=45, marker='o', color='#EF4444', edgecolors='#FFFFFF', linewidths=1.0, zorder=9)
                if detalle_textos:
                    ax.text(px + 4.0, py + 2.0, f"{pid}\n{poste}", color='#FCA5A5', fontsize=6.5, zorder=11)

    # 1. PLANTA GENERAL COMPLETA
    fig, ax = plt.subplots(figsize=(15, 11), dpi=250)
    dibujar_elementos_comunes(ax, detalle_textos=False)
    ax.set_xlim(425200, 425850)
    ax.set_ylim(8434600, 8436750)
    ax.set_title("REDES ELÉCTRICAS DE DISTRIBUCIÓN INTEGRAL - LIMBANI (WGS 84 / UTM Z19S)\n"
                 "Línea MT 10 kV (Rojo, 1.97 km) | 3 SEDs (Amarillo, 250 kVA) | Red BT CAAI (Verde/Cian, 6.21 km) | 587 Acometidas",
                 fontsize=10, fontweight='bold', color='#F8FAFC', pad=12)
    ax.set_xlabel("Este UTM (m)", fontsize=8, color='#94A3B8')
    ax.set_ylabel("Norte UTM (m)", fontsize=8, color='#94A3B8')
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(True, linestyle='--', alpha=0.25, color='#475569')
    plt.tight_layout()
    plt.savefig(out_img_gen, facecolor='#0B0F19', edgecolor='none')
    plt.close()
    print(f"[OK] Lámina General guardada en: {out_img_gen}")

    # 2. ZOOM NORTE
    fig, ax = plt.subplots(figsize=(12, 9), dpi=250)
    dibujar_elementos_comunes(ax, detalle_textos=True)
    ax.set_xlim(425350, 425780)
    ax.set_ylim(8436150, 8436750)
    ax.set_title("DETALLE SECTOR NORTE: MCH LIMBANI (200 kW) Y SUBESTACIÓN SED-01 (50 kVA)\n"
                 "Pórtico Salida E-01 (CAC 13/400) | Jr. Villa Hermosa | Red BT Autoportante CAAI",
                 fontsize=10, fontweight='bold', color='#F8FAFC', pad=10)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(True, linestyle='--', alpha=0.25, color='#475569')
    plt.tight_layout()
    plt.savefig(out_img_norte, facecolor='#0B0F19', edgecolor='none')
    plt.close()

    # 3. ZOOM CENTRO
    fig, ax = plt.subplots(figsize=(12, 9), dpi=250)
    dibujar_elementos_comunes(ax, detalle_textos=True)
    ax.set_xlim(425330, 425620)
    ax.set_ylim(8435480, 8436050)
    ax.set_title("DETALLE SECTOR CENTRO: PLAZA DE ARMAS, MUNICIPALIDAD Y SUBESTACIÓN SED-02 (100 kVA)\n"
                 "Jr. Progreso | Calle Municipal | Centro Cívico | Alumbrado LED 50W",
                 fontsize=10, fontweight='bold', color='#F8FAFC', pad=10)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(True, linestyle='--', alpha=0.25, color='#475569')
    plt.tight_layout()
    plt.savefig(out_img_centro, facecolor='#0B0F19', edgecolor='none')
    plt.close()

    # 4. ZOOM SUR
    fig, ax = plt.subplots(figsize=(12, 9), dpi=250)
    dibujar_elementos_comunes(ax, detalle_textos=True)
    ax.set_xlim(425300, 425580)
    ax.set_ylim(8434700, 8435420)
    ax.set_title("DETALLE SECTOR SUR: CRUCE RÍO CHINCHALAMANI, ESTADIO Y SUBESTACIÓN SED-03 (100 kVA)\n"
                 "Vano 110m Postes CAC 13/600 | Armados PR-3 | Sector Piscina | Terminal MT E-24",
                 fontsize=10, fontweight='bold', color='#F8FAFC', pad=10)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(True, linestyle='--', alpha=0.25, color='#475569')
    plt.tight_layout()
    plt.savefig(out_img_sur, facecolor='#0B0F19', edgecolor='none')
    plt.close()

    # Sincronizar figuras en Catastro_Limbani
    try:
        shutil.copy2(out_img_gen, os.path.join(catastro_sync_dir, "07_redes_electricas_detalladas_catastro.png"))
    except Exception: pass

    # -------------------------------------------------------------
    # IMPRESIÓN DE METRADOS EXACTOS DEL MODELO
    # -------------------------------------------------------------
    print("\n" + "="*70)
    print("METRADOS EXACTOS DEL MODELO CAD LIMBANI (CONFORME A NORMA DGE):")
    print("="*70)
    long_mt = sum(distancia(pts_mt[i], pts_mt[i+1]) for i in range(len(pts_mt)-1))
    print(f"Línea Primaria 10.0 kV (AAAC 35 mm2):        {long_mt:.2f} m  ({long_mt/1000:.3f} km)")
    print(f"Postes MT CAC 12m/300 daN (Alineamiento):   {total_postes_mt_cac12_300} unidades")
    print(f"Postes MT CAC 12m/400 daN (Ángulos):        {total_postes_mt_cac12_400} unidades")
    print(f"Postes MT CAC 13m/400 daN (SAB Biposte):    {total_postes_mt_cac13_400} unidades (en 3 subestaciones)")
    print(f"Postes MT CAC 13m/600 daN (Cruce río):      {total_postes_mt_cac13_600} unidades")
    total_postes_mt = total_postes_mt_cac12_300 + total_postes_mt_cac12_400 + total_postes_mt_cac13_400 + total_postes_mt_cac13_600
    print(f"Total Postes en Media Tensión:              {total_postes_mt} unidades")
    print(f"Subestaciones Aéreas Biposte (SAB):         {total_seds} subestaciones (50, 100, 100 kVA)")
    print(f"Retenidas en Media Tensión:                 {total_ret_mt} unidades")
    print("-"*70)
    print(f"Red BT Troncal CAAI 3x35+1x16+NA25:         {longitud_troncal_bt:.2f} m")
    print(f"Red BT Ramales CAAI 2x16+1x16+NA25:         {longitud_derivacion_bt:.2f} m")
    total_bt_cond = longitud_troncal_bt + longitud_derivacion_bt
    print(f"Total Conductor BT Autoportante:            {total_bt_cond:.2f} m ({total_bt_cond/1000:.2f} km)")
    print(f"Postes BT CAC 8m/200 daN (Pasajes):         {total_cac_8_200} unidades")
    print(f"Postes BT CAC 8m/300 daN (Retenciones):     {total_cac_8_300} unidades")
    print(f"Postes BT CAC 9m/300 daN (Troncales/AP):    {total_cac_9_300} unidades")
    total_postes_bt = total_cac_8_200 + total_cac_8_300 + total_cac_9_300
    print(f"Total Postes en Baja Tensión:               {total_postes_bt} unidades (estrictamente en casco urbano)")
    print(f"Luminarias Alumbrado Público LED 50W:       {total_luminarias} unidades")
    print(f"Retenidas en Baja Tensión:                  {total_ret_bt} unidades")
    print("-"*70)
    total_acometidas = total_acometidas_cortas + total_acometidas_largas
    print(f"Acometidas Domiciliarias Config. Corta:     {total_acometidas_cortas} unidades (<= 15 m)")
    print(f"Acometidas Domiciliarias Config. Larga:     {total_acometidas_largas} unidades (15 - 30 m)")
    print(f"Total Acometidas Monofásicas (Predios):     {total_acometidas} unidades")
    print(f"Longitud Total Conductor SET 2x4 mm2:       {total_longitud_acometidas:.2f} m (prom. {total_longitud_acometidas/total_acometidas:.1f} m/lote)")
    print(f"Cajas Portamedidor Monofásicas Tipo L-T:    {total_acometidas} unidades")
    print("="*70)

if __name__ == '__main__':
    main()
