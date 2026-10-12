#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_redes_electricas_dxf.py
Genera el Plano de Ingeniería Electromecánica en formato DXF incorporando:
- Postería de Media Tensión (CAC 12m y 13m) y conductor AAAC 35 mm2 (10 kV)
- Subestaciones Aéreas Biposte (SED-01 50 kVA, SED-02 100 kVA, SED-03 100 kVA)
- Postería de Baja Tensión (CAC 8m y 9m) y cables autoportantes CAAI (380/220 V)
- Retenidas en esquinas y terminales
- Alumbrado público LED (165 luminarias de 50 W)
- Preservación de capas del catastro oficial de Limbani (lotes, vías, ríos, equipamientos)

Autor: Br. Aquiles Taylor Ramos Yapo (Cód. 227368)
Curso: Instalaciones Eléctricas II / Redes Eléctricas | FIME - UNA Puno
"""

import os
import math
import ezdxf
from ezdxf import colors
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D

def distancia(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def interp_pt(p1, p2, f):
    return (p1[0] + f * (p2[0] - p1[0]), p1[1] + f * (p2[1] - p1[1]))

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dxf_orig = r"C:\Users\51949\Downloads\Catastro_Limbani\catastro_limbani.dxf"
    out_dxf = os.path.join(base_dir, "entregables", "planos", "catastro_limbani_redes_electricas.dxf")
    out_img = os.path.join(base_dir, "expediente", "figuras", "07_redes_electricas_detalladas_catastro.png")
    catastro_sync_dxf = r"C:\Users\51949\Downloads\Catastro_Limbani\expediente_electrico\catastro_limbani_redes_electricas.dxf"

    print("[*] Leyendo catastro base:", dxf_orig)
    doc = ezdxf.readfile(dxf_orig)
    msp = doc.modelspace()

    # 1. Crear nuevas capas electromecánicas normalizadas
    capas_def = [
        ("01_RED_MT_10KV_CONDUCTOR", colors.CYAN),
        ("02_POSTES_MT_10KV", colors.RED),
        ("03_SUBESTACIONES_SED", colors.YELLOW),
        ("04_RETENIDAS_MT_BT", colors.MAGENTA),
        ("05_RED_BT_TRONCAL_CAAI", colors.GREEN),
        ("06_RED_BT_DERIVACION_CAAI", 140), # Verde azulado
        ("07_POSTES_BT_CAC", colors.BLUE),
        ("08_ALUMBRADO_PUBLICO_LED", 30), # Naranja
        ("09_ACOMETIDAS_DOMICILIARIAS", colors.WHITE)
    ]
    for c_name, c_color in capas_def:
        if c_name not in doc.layers:
            doc.layers.new(name=c_name, dxfattribs={'color': c_color})

    # 2. Extraer polilíneas de vías para trazar las redes
    vias_polys = []
    for e in msp:
        if e.dxf.layer == '02_CALLES_Y_VIAS' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            vias_polys.append(pts)

    print(f"[*] {len(vias_polys)} vías catastrales extraídas.")

    # 3. Definición de la Línea Primaria en Media Tensión 10 kV (2.15 km)
    # Troncal de interconexión desde MCH Limbani (Norte) hasta SED-03 (Sur)
    postes_mt_data = [
        # (ID, X, Y, Cota, Tipo_Poste, Armado, Retenida, Descripcion)
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

    # Dibujar la línea de Media Tensión (conductor AAAC 35 mm2)
    pts_mt = [(p[1], p[2]) for p in postes_mt_data]
    for i in range(len(pts_mt) - 1):
        msp.add_line(pts_mt[i], pts_mt[i+1], dxfattribs={'layer': '01_RED_MT_10KV_CONDUCTOR', 'lineweight': 50})

    # Dibujar los postes de MT y SEDs
    total_postes_mt_cac12_300 = 0
    total_postes_mt_cac12_400 = 0
    total_postes_mt_cac13_400 = 0
    total_postes_mt_cac13_600 = 0
    total_seds = 0
    total_ret_mt = 0

    for pid, px, py, cota, poste, armado, ret, desc in postes_mt_data:
        if "SAB" in armado:
            total_seds += 1
            # Dibujar subestación biposte (dos círculos y plataforma)
            msp.add_circle((px - 1.0, py), radius=0.9, dxfattribs={'layer': '03_SUBESTACIONES_SED'})
            msp.add_circle((px + 1.0, py), radius=0.9, dxfattribs={'layer': '03_SUBESTACIONES_SED'})
            msp.add_lwpolyline([(px - 1.8, py - 0.7), (px + 1.8, py - 0.7), (px + 1.8, py + 0.7), (px - 1.8, py + 0.7), (px - 1.8, py - 0.7)],
                               dxfattribs={'layer': '03_SUBESTACIONES_SED'})
            # Texto SED
            t_sed = msp.add_text(f"{pid} ({desc.split()[0]})", dxfattribs={'layer': '03_SUBESTACIONES_SED', 'height': 2.2})
            t_sed.dxf.insert = (px + 2.5, py + 1.0)
            total_postes_mt_cac13_400 += 2
        else:
            # Poste común MT
            msp.add_circle((px, py), radius=1.0, dxfattribs={'layer': '02_POSTES_MT_10KV'})
            msp.add_line((px - 1.0, py), (px + 1.0, py), dxfattribs={'layer': '02_POSTES_MT_10KV'})
            msp.add_line((px, py - 1.0), (px, py + 1.0), dxfattribs={'layer': '02_POSTES_MT_10KV'})
            t_p = msp.add_text(f"{pid} {poste.replace('C.A.C. ', '')}", dxfattribs={'layer': '02_POSTES_MT_10KV', 'height': 1.6})
            t_p.dxf.insert = (px + 1.5, py + 0.5)
            
            if "12/300" in poste: total_postes_mt_cac12_300 += 1
            elif "12/400" in poste: total_postes_mt_cac12_400 += 1
            elif "13/600" in poste: total_postes_mt_cac13_600 += 1

        # Retenidas MT
        if ret != "Ninguna":
            total_ret_mt += 1
            # Dibujar vector de retenida
            dx_ret, dy_ret = (4.0, 3.0) if px < 425500 else (-4.0, -3.0)
            msp.add_line((px, py), (px + dx_ret, py + dy_ret), dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'linetype': 'DASHED'})
            msp.add_circle((px + dx_ret, py + dy_ret), radius=0.4, dxfattribs={'layer': '04_RETENIDAS_MT_BT'})

    # 4. Trazado de Redes de Baja Tensión y Postería CAC (8m y 9m)
    # Generar postes a lo largo de las 19 vías a intervalos regulares de 35 m
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
        # Calcular longitud total de la vía
        v_segs = []
        v_len = 0
        for k in range(len(v_pts) - 1):
            d = distancia(v_pts[k], v_pts[k+1])
            v_segs.append((v_pts[k], v_pts[k+1], d, v_len))
            v_len += d

        if v_len < 25.0:
            continue

        num_tramos = max(1, round(v_len / vano_objetivo))
        ds_actual = 0.0
        step = v_len / num_tramos

        pts_via_red = []
        for s in range(num_tramos + 1):
            target_d = s * step
            # Encontrar punto exacto en la polilínea
            for p_a, p_b, seg_d, seg_start in v_segs:
                if seg_start <= target_d <= seg_start + seg_d:
                    frac = (target_d - seg_start) / max(0.001, seg_d)
                    pt = interp_pt(p_a, p_b, frac)
                    pts_via_red.append(pt)
                    break

        # Añadir conductores de baja tensión entre postes
        is_troncal = (v_len > 800.0)
        c_layer = '05_RED_BT_TRONCAL_CAAI' if is_troncal else '06_RED_BT_DERIVACION_CAAI'

        for k in range(len(pts_via_red) - 1):
            msp.add_line(pts_via_red[k], pts_via_red[k+1], dxfattribs={'layer': c_layer, 'lineweight': 30})
            lineas_bt_segmentos.append((pts_via_red[k], pts_via_red[k+1], is_troncal))

        # Añadir postes
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

            # Dibujar poste BT
            msp.add_circle(pt, radius=0.6, dxfattribs={'layer': '07_POSTES_BT_CAC'})
            postes_bt_coords.append((f"P-{p_idx:03d}", pt[0], pt[1], p_tipo, has_ap))

            # Alumbrado público
            if has_ap and total_luminarias < 165:
                total_luminarias += 1
                # Dibujar brazo/pastoral y luminaria
                msp.add_line(pt, (pt[0] + 1.5, pt[1] + 1.2), dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED'})
                msp.add_circle((pt[0] + 1.5, pt[1] + 1.2), radius=0.3, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED'})

            # Retenida BT en terminales
            if is_end:
                total_ret_bt += 1
                msp.add_line(pt, (pt[0] - 2.5, pt[1] - 2.0), dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'linetype': 'DASHED'})
                msp.add_circle((pt[0] - 2.5, pt[1] - 2.0), radius=0.25, dxfattribs={'layer': '04_RETENIDAS_MT_BT'})

            p_idx += 1

    # Asegurar que completemos exactamente las 165 luminarias LED normadas
    if total_luminarias < 165:
        faltan = 165 - total_luminarias
        for p_item in postes_bt_coords:
            if faltan <= 0: break
            if not p_item[4]:
                pt = (p_item[1], p_item[2])
                msp.add_line(pt, (pt[0] + 1.5, pt[1] + 1.2), dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED'})
                msp.add_circle((pt[0] + 1.5, pt[1] + 1.2), radius=0.3, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED'})
                total_luminarias += 1
                faltan -= 1

    # Guardar DXF enriquecido
    os.makedirs(os.path.dirname(out_dxf), exist_ok=True)
    doc.saveas(out_dxf)
    print(f"[OK] Plano DXF de Redes Electricas generado en: {out_dxf}")

    # Sincronizar copia al repositorio Catastro_Limbani
    if os.path.exists(os.path.dirname(catastro_sync_dxf)):
        doc.saveas(catastro_sync_dxf)
        print(f"[OK] Copia sincronizada en: {catastro_sync_dxf}")

    # 5. Generar Renderizado Gráfico de Alta Definición para Inspección (PNG)
    print("[*] Generando lámina de inspección gráfica en alta definición...")
    fig, ax = plt.subplots(figsize=(16, 24), dpi=150)
    ax.set_facecolor('#0B0F19') # Fondo oscuro tipo AutoCAD Dark

    # Dibujar ríos (azul cian)
    for e in msp:
        if e.dxf.layer == '01_RIOS_Y_CUENCAS' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#0284C7', linewidth=1.8, alpha=0.8)

    # Dibujar lotes (gris tenue)
    for e in msp:
        if e.dxf.layer == '04_LOTES_PREDIALES' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#334155', linewidth=0.5, alpha=0.6)

    # Dibujar huellas de viviendas (amarillo sutil)
    for e in msp:
        if 'HUELLAS' in e.dxf.layer and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            ax.fill([p[0] for p in pts], [p[1] for p in pts], color='#F59E0B', alpha=0.3)

    # Dibujar vías (gris medio)
    for v_pts in vias_polys:
        ax.plot([p[0] for p in v_pts], [p[1] for p in v_pts], color='#475569', linewidth=0.8, alpha=0.5)

    # Dibujar Red BT (Verde troncales, verde claro derivaciones)
    for p_a, p_b, is_tr in lineas_bt_segmentos:
        c_line = '#10B981' if is_tr else '#34D399'
        lw = 1.2 if is_tr else 0.8
        ax.plot([p_a[0], p_b[0]], [p_a[1], p_b[1]], color=c_line, linewidth=lw, alpha=0.85)

    # Dibujar Postes BT (Azul cian)
    ax.scatter([p[1] for p in postes_bt_coords], [p[2] for p in postes_bt_coords],
               s=10, color='#38BDF8', zorder=5, label='Postes BT (CAC 8m/9m)')

    # Dibujar Luminarias AP (Puntos amarillos brillantes)
    ap_pts = [p for p in postes_bt_coords if p[4]]
    ax.scatter([p[1] for p in ap_pts], [p[2] for p in ap_pts],
               s=18, color='#FBBF24', edgecolors='#D97706', linewidths=0.5, zorder=6, label='Alumbrado Público LED (165 und)')

    # Dibujar Línea MT 10 kV (Línea roja gruesa destacada)
    ax.plot([p[0] for p in pts_mt], [p[1] for p in pts_mt], color='#EF4444', linewidth=2.5, zorder=7, label='Línea Primaria 10 kV (AAAC 35 mm²)')

    # Dibujar Postes MT (Rojos con borde blanco)
    ax.scatter([p[1] for p in postes_mt_data if "SAB" not in p[5]],
               [p[2] for p in postes_mt_data if "SAB" not in p[5]],
               s=45, color='#DC2626', edgecolors='#FFFFFF', linewidths=1.0, zorder=8, label='Postes MT (CAC 12m/13m)')

    # Dibujar Subestaciones Aéreas Biposte (Grandes marcadores dorados/amarillos)
    seds_pts = [p for p in postes_mt_data if "SAB" in p[5]]
    ax.scatter([p[1] for p in seds_pts], [p[2] for p in seds_pts],
               s=180, color='#FACC15', edgecolors='#B45309', linewidths=2.0, marker='s', zorder=9, label='Subestaciones Aéreas Biposte (3 SAB - 250 kVA)')

    # Etiquetas para las SEDs
    for p in seds_pts:
        ax.annotate(f"{p[0]}: {p[7].split('(')[0].strip()}\n({p[7].split('(')[1].replace(')', '')})",
                    (p[1], p[2]), xytext=(p[1] + 35, p[2] + 25),
                    color='#FACC15', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#1E293B", ec="#FACC15", lw=1.2),
                    arrowprops=dict(arrowstyle="->", color='#FACC15', lw=1.2),
                    zorder=10)

    # Etiquetas clave de inicio y fin de línea MT
    p_inicio = postes_mt_data[0]
    ax.annotate("MCH LIMBANI (200 kW)\nPórtico Elevador 0.38/10 kV",
                (p_inicio[1], p_inicio[2]), xytext=(p_inicio[1] - 180, p_inicio[2] + 40),
                color='#38BDF8', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", fc="#0F172A", ec="#38BDF8", lw=1.2),
                arrowprops=dict(arrowstyle="->", color='#38BDF8', lw=1.2),
                zorder=10)

    p_fin = postes_mt_data[-1]
    ax.annotate("Terminal MT 10 kV\nSalida hacia Crucero/Ananea",
                (p_fin[1], p_fin[2]), xytext=(p_fin[1] - 160, p_fin[2] - 50),
                color='#EF4444', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", fc="#0F172A", ec="#EF4444", lw=1.0),
                arrowprops=dict(arrowstyle="->", color='#EF4444', lw=1.0),
                zorder=10)

    # Carátula y Membrete en el gráfico
    ax.set_title("PLANO DE REDES ELÉCTRICAS Y POSTERÍA GEORREFERENCIADA - LIMBANI (PUNO)\n"
                 "Línea Primaria 10 kV | 3 Subestaciones SAB (250 kVA) | Redes Secundarias CAAI 380/220 V | Catastro WGS 84 Z19S",
                 color='#F8FAFC', fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='lower right', facecolor='#1E293B', edgecolor='#475569', labelcolor='#F8FAFC', fontsize=9)
    ax.set_xlabel("Este UTM (WGS 84 Zona 19 Sur) [m]", color='#94A3B8', fontsize=10)
    ax.set_ylabel("Norte UTM (WGS 84 Zona 19 Sur) [m]", color='#94A3B8', fontsize=10)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(color='#1E293B', linestyle='--', linewidth=0.5, alpha=0.7)

    plt.tight_layout()
    fig.savefig(out_img, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"[OK] Lámina gráfica guardada exitosamente en: {out_img}")

    # Resumen de metrados precisos derivados del modelo
    long_mt_total = sum(distancia(pts_mt[i], pts_mt[i+1]) for i in range(len(pts_mt)-1))
    long_bt_troncal = sum(distancia(p_a, p_b) for p_a, p_b, is_tr in lineas_bt_segmentos if is_tr)
    long_bt_deriv = sum(distancia(p_a, p_b) for p_a, p_b, is_tr in lineas_bt_segmentos if not is_tr)

    print("\n" + "="*70)
    print("METRADOS EXACTOS EXTRACTADOS DEL MODELO FÍSICO CAD:")
    print("="*70)
    print(f"Línea Primaria 10.0 kV (AAAC 35 mm2):        {long_mt_total:.2f} m  ({long_mt_total/1000:.3f} km)")
    print(f"Postes MT CAC 12m/300 daN (Alineamiento):   {total_postes_mt_cac12_300} unidades")
    print(f"Postes MT CAC 12m/400 daN (Ángulos):        {total_postes_mt_cac12_400} unidades")
    print(f"Postes MT CAC 13m/400 daN (SAB Biposte):    {total_postes_mt_cac13_400} unidades (en {total_seds} subestaciones)")
    print(f"Postes MT CAC 13m/600 daN (Cruce río):      {total_postes_mt_cac13_600} unidades")
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
