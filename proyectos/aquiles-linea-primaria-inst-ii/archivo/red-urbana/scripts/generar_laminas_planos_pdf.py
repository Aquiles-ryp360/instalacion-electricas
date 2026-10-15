#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_laminas_planos_pdf.py
Genera las 5 láminas oficiales de ingeniería electromecánica en formato A3 Horizontal (420 x 297 mm)
en alta definición vectorial / PDF para su compilación e inclusión en el Expediente Técnico:

Lámina PL-01: Plano Clave General: Redes MT, SEDs, BT y Catastro Urbano (Escala 1:2500)
Lámina PL-02: Trazo y Perfil Longitudinal Topográfico con Catenarias de la Línea Primaria 10 kV
Lámina PL-03: Detalle Electromecánico de Subestaciones Aéreas Biposte (SAB 50 y 100 kVA)
Lámina PL-04: Red de Distribución Secundaria CAAI 380/220 V y Alumbrado Público LED 50W
Lámina PL-05: Armados Normalizados DGE (PS-3, PA-3, PR-3, SAB) y Puesta a Tierra (PAT)

Autor: Br. Aquiles Taylor Ramos Yapo (Cód. 227368)
Curso: Instalaciones Eléctricas II / Redes Eléctricas | FIME - UNA Puno
"""

import os
import math
import shutil
import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D

# -------------------------------------------------------------------------
# FUNCIÓN DE DIBUJO DE RÓTULO NORMALIZADO INSTITUCIONAL (FIME - UNAP)
# -------------------------------------------------------------------------
def dibujar_rotulo_oficial(ax, x0, y0, w, h, plano_cod, plano_nom, escala="1 : 2500"):
    """
    Dibuja un rótulo formal normalizado de ingeniería en coordenadas de figura (0 a 1).
    """
    rect = patches.Rectangle((x0, y0), w, h, facecolor='#F8FAFC', edgecolor='#0F172A', linewidth=1.4, zorder=50)
    ax.add_patch(rect)
    
    h_sub = h / 6.0
    for i in range(1, 6):
        ax.plot([x0, x0 + w], [y0 + i * h_sub, y0 + i * h_sub], color='#334155', linewidth=0.8, zorder=51)
        
    ax.plot([x0 + w * 0.45, x0 + w * 0.45], [y0, y0 + h_sub], color='#334155', linewidth=0.8, zorder=51)
    ax.plot([x0 + w * 0.72, x0 + w * 0.72], [y0, y0 + h_sub], color='#334155', linewidth=0.8, zorder=51)
    
    # Textos institucionales
    ax.text(x0 + w/2.0, y0 + 5.5 * h_sub, "UNIVERSIDAD NACIONAL DEL ALTIPLANO — PUNO\nFACULTAD DE INGENIERÍA MECÁNICA ELÉCTRICA (FIME)",
            ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A', zorder=52)
            
    ax.text(x0 + w/2.0, y0 + 4.5 * h_sub, "ESCUELA PROFESIONAL DE INGENIERÍA MECÁNICA ELÉCTRICA\nCURSO: INSTALACIONES ELÉCTRICAS II / REDES ELÉCTRICAS",
            ha='center', va='center', fontsize=6.8, fontweight='bold', color='#0F766E', zorder=52)
            
    ax.text(x0 + w/2.0, y0 + 3.5 * h_sub, "EXPEDIENTE TÉCNICO: REDES ELÉCTRICAS MCH LIMBANI (200 kW)\nDISTRITO DE LIMBANI — SANDIA — PUNO (3,050 m.s.n.m.)",
            ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E293B', zorder=52)
            
    ax.text(x0 + w/2.0, y0 + 2.5 * h_sub, f"PLANO: {plano_nom}",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#B45309', zorder=52)
            
    ax.text(x0 + 0.02 * w, y0 + 1.5 * h_sub, "PROYECTISTA:\nDOCENTE:",
            ha='left', va='center', fontsize=6.0, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.28 * w, y0 + 1.5 * h_sub, "Br. Aquiles Taylor Ramos Yapo (Cód. 227368)\nDocente FIME - UNA Puno",
            ha='left', va='center', fontsize=6.0, color='#0F172A', zorder=52)
            
    ax.text(x0 + 0.225 * w, y0 + 0.5 * h_sub, f"FECHA:\nOctubre 2026",
            ha='center', va='center', fontsize=5.8, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.585 * w, y0 + 0.5 * h_sub, f"ESCALA:\n{escala}",
            ha='center', va='center', fontsize=5.8, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.86 * w, y0 + 0.5 * h_sub, f"LÁMINA:\n{plano_cod}",
            ha='center', va='center', fontsize=8.0, fontweight='bold', color='#1E3A8A', zorder=52)

def dibujar_marco_general(fig, ax_bg):
    """Dibuja el marco exterior y la grilla perimetral de lámina A3."""
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')
    # Marco exterior
    rect_ext = patches.Rectangle((0.015, 0.015), 0.97, 0.97, fill=False, edgecolor='#0F172A', linewidth=2.0, zorder=1)
    rect_int = patches.Rectangle((0.020, 0.020), 0.96, 0.96, fill=False, edgecolor='#64748B', linewidth=0.8, zorder=1)
    ax_bg.add_patch(rect_ext)
    ax_bg.add_patch(rect_int)

# =========================================================================
# LÁMINA PL-01: PLANO CLAVE GENERAL REDES ELÉCTRICAS Y CATASTRO URBANO
# =========================================================================
def generar_lamina_pl01(dxf_redes_path, out_pdf):
    print("[*] Generando Lámina PL-01: Plano Clave General...")
    doc = ezdxf.readfile(dxf_redes_path)
    msp = doc.modelspace()

    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    ax_bg = fig.add_axes([0, 0, 1, 1])
    dibujar_marco_general(fig, ax_bg)

    # Ventana gráfica del mapa (66% del ancho)
    ax = fig.add_axes([0.035, 0.04, 0.65, 0.92])
    ax.set_facecolor('#0B0F19')

    # Ríos
    for e in msp:
        if e.dxf.layer == '01_RIOS_Y_CUENCAS' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#0284C7', linewidth=2.2, alpha=0.9, zorder=2)

    # Lotes
    for e in msp:
        if e.dxf.layer == '04_LOTES_PREDIALES' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#334155', linewidth=0.5, alpha=0.7, zorder=3)

    # Huellas
    for e in msp:
        if 'HUELLAS' in e.dxf.layer and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            ax.fill([p[0] for p in pts], [p[1] for p in pts], color='#F59E0B', alpha=0.35, zorder=3)

    # Equipamientos
    for e in msp:
        if e.dxf.layer == '07_EQUIPAMIENTOS' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            ax.fill([p[0] for p in pts], [p[1] for p in pts], color='#10B981', alpha=0.25, zorder=3)

    # Vías
    for e in msp:
        if e.dxf.layer == '02_CALLES_Y_VIAS' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#475569', linewidth=0.7, alpha=0.5, zorder=3)

    # Acometidas Domiciliarias a los 587 predios
    for e in msp:
        if e.dxf.layer == '11_ACOMETIDAS_DOMICILIARIAS' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#38BDF8', linewidth=0.35, alpha=0.6, zorder=4)

    # Retenidas normalizadas MT y BT
    for e in msp:
        if e.dxf.layer == '04_RETENIDAS_MT_BT' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#EC4899', linewidth=1.2, zorder=5)

    # Redes BT CAAI
    for e in msp:
        if 'RED_BT' in e.dxf.layer and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            c_line = '#10B981' if 'TRONCAL' in e.dxf.layer else '#06B6D4'
            lw = 1.3 if 'TRONCAL' in e.dxf.layer else 0.8
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color=c_line, linewidth=lw, alpha=0.9, zorder=6)

    # Postes BT
    pts_pbt = [e.dxf.center for e in msp if e.dxf.layer == '07_POSTES_BT_CAC' and e.dxftype() == 'CIRCLE' and e.dxf.radius > 1.0]
    ax.scatter([p[0] for p in pts_pbt], [p[1] for p in pts_pbt], s=14, color='#60A5FA', edgecolors='#1E3A8A', linewidths=0.5, zorder=7)

    # Alumbrado AP
    pts_ap = [e.dxf.center for e in msp if e.dxf.layer == '08_ALUMBRADO_PUBLICO_LED' and e.dxftype() == 'CIRCLE']
    ax.scatter([p[0] for p in pts_ap], [p[1] for p in pts_ap], s=22, color='#FBBF24', edgecolors='#B45309', linewidths=0.6, zorder=8)

    # Línea MT 10 kV
    for e in msp:
        if e.dxf.layer == '01_RED_MT_10KV_CONDUCTOR' and e.dxftype() == 'LWPOLYLINE':
            pts = e.get_points('xy')
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#EF4444', linewidth=3.0, zorder=8)

    # Postes MT
    pts_pmt = [e.dxf.center for e in msp if e.dxf.layer == '02_POSTES_MT_10KV' and e.dxftype() == 'CIRCLE' and e.dxf.radius > 3.0]
    ax.scatter([p[0] for p in pts_pmt], [p[1] for p in pts_pmt], s=75, color='#DC2626', edgecolors='#FFFFFF', linewidths=1.2, zorder=9)

    # SEDs
    seds = [
        (425490.0, 8436250.0, "SED-01 (50 kVA)\nJr. Villa Hermosa"),
        (425445.0, 8435700.0, "SED-02 (100 kVA)\nPlaza de Armas"),
        (425410.0, 8434930.0, "SED-03 (100 kVA)\nEstadio - Piscina")
    ]
    for sx, sy, slbl in seds:
        ax.scatter([sx], [sy], s=200, color='#FACC15', edgecolors='#78350F', linewidths=2.0, marker='s', zorder=10)
        ax.annotate(slbl, (sx, sy), xytext=(sx + 40, sy + 25),
                    color='#FEF08A', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#1E293B", ec="#FACC15", lw=1.0),
                    arrowprops=dict(arrowstyle="->", color='#FACC15', lw=1.0), zorder=11)

    ax.set_xlim(425100, 426150)
    ax.set_ylim(8434350, 8436850)
    ax.set_xlabel("Este UTM (WGS 84 Zona 19S) [m]", color='#94A3B8', fontsize=8)
    ax.set_ylabel("Norte UTM (WGS 84 Zona 19S) [m]", color='#94A3B8', fontsize=8)
    ax.tick_params(colors='#94A3B8', labelsize=7)
    ax.grid(color='#1E293B', linestyle='--', linewidth=0.5, alpha=0.7)

    # Panel lateral derecho con Leyenda, Cuadro de Cargas y Rótulo
    ax_side = fig.add_axes([0.70, 0.04, 0.28, 0.92])
    ax_side.set_facecolor('#F8FAFC')
    ax_side.set_xlim(0, 1)
    ax_side.set_ylim(0, 1)
    ax_side.axis('off')

    # Marco del panel lateral
    rect_side = patches.Rectangle((0, 0), 1, 1, facecolor='#F8FAFC', edgecolor='#334155', linewidth=1.2)
    ax_side.add_patch(rect_side)

    # 1. TÍTULO LEYENDA
    ax_side.text(0.5, 0.97, "SIMBOLOGÍA ELECTROMECÁNICA", ha='center', va='center', fontsize=9, fontweight='bold', color='#1E293B')
    ax_side.plot([0.05, 0.95], [0.95, 0.95], color='#334155', linewidth=1.0)

    simbolos = [
        ("Línea MT 10 kV (AAAC 35 mm²)", '#EF4444', 'linea', 3.0),
        ("Poste MT (C.A.C. 12m y 13m)", '#DC2626', 'circulo', 7),
        ("Subestación SAB (50 / 100 kVA)", '#FACC15', 'cuadrado', 8),
        ("Red BT Troncal CAAI 3x35+1x16+NA25", '#10B981', 'linea', 2.2),
        ("Red BT Derivación CAAI 2x16+1x16+NA25", '#06B6D4', 'linea', 1.8),
        ("Poste BT (C.A.C. 8m y 9m)", '#60A5FA', 'circulo', 5),
        ("Alumbrado Público LED 50W (166 und)", '#FBBF24', 'circulo', 6),
        ("Retenida Normalizada (RD 024/023)", '#EC4899', 'linea', 2.0),
        ("Acometida Domiciliaria (587 lotes)", '#38BDF8', 'linea_d', 1.2),
        ("Río Limbani / Quebradas", '#0284C7', 'linea', 2.0)
    ]
    sy = 0.92
    for desc, col, tipo, sz in simbolos:
        if tipo == 'linea':
            ax_side.plot([0.08, 0.22], [sy, sy], color=col, linewidth=sz)
        elif tipo == 'linea_d':
            ax_side.plot([0.08, 0.22], [sy, sy], color=col, linewidth=sz, linestyle='--')
        elif tipo == 'circulo':
            ax_side.plot(0.15, sy, marker='o', markersize=sz, color=col, markeredgecolor='#0F172A')
        elif tipo == 'cuadrado':
            ax_side.plot(0.15, sy, marker='s', markersize=sz, color=col, markeredgecolor='#78350F')
        ax_side.text(0.26, sy, desc, va='center', fontsize=6.5, color='#0F172A')
        sy -= 0.034

    # 2. CUADRO RESUMEN DE PARÁMETROS TÉCNICOS
    ax_side.plot([0.05, 0.95], [sy, sy], color='#334155', linewidth=1.0)
    sy -= 0.02
    ax_side.text(0.5, sy, "RESUMEN TÉCNICO DE REDES", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1E293B')
    sy -= 0.02
    ax_side.plot([0.05, 0.95], [sy, sy], color='#334155', linewidth=1.0)
    sy -= 0.023

    datos_tecnicos = [
        ("Generación MCH Limbani:", "200.0 kW (Michell-Banki, 380 V)"),
        ("Tensión de Transmisión MT:", "10.0 kV (Trifásica, 60 Hz)"),
        ("Longitud Línea Primaria:", "1,967.87 m (1.97 km)"),
        ("Conductor de Línea MT:", "AAAC 35 mm² (Desnudo)"),
        ("Subestaciones Aéreas SAB:", "3 SEDs (Total 250 kVA)"),
        ("• SED-01 Norte (Jr. V. Hermosa):", "50 kVA (142 viviendas)"),
        ("• SED-02 Centro (Plaza Armas):", "100 kVA (348 viviendas)"),
        ("• SED-03 Sur (Estadio-Piscina):", "100 kVA (274 viviendas)"),
        ("Redes Secundarias BT CAAI:", "6,206.73 m (6.21 km casco urbano)"),
        ("Total Postería CAC MT / BT:", "26 MT / 243 BT (269 postes)"),
        ("Alumbrado Público LED:", "166 luminarias LED 50 W"),
        ("Acometidas Monofásicas:", "587 predios (534 C / 53 L)"),
        ("Retenidas Normalizadas:", "12 MT / 48 BT (60 und)"),
        ("Demanda Coincidente Total:", "181.80 kW (F.C. = 90.9%)"),
        ("Caída de Tensión Máx. BT:", "3.82% (Admisible <= 5.0%)")
    ]
    for k, v in datos_tecnicos:
        ax_side.text(0.06, sy, k, va='center', fontsize=6.0, fontweight='bold', color='#334155')
        ax_side.text(0.94, sy, v, ha='right', va='center', fontsize=6.0, color='#0F172A')
        sy -= 0.021

    # 3. RÓTULO NORMALIZADO INSTITUCIONAL
    rot_h = 0.22
    dibujar_rotulo_oficial(ax_side, 0.02, 0.015, 0.96, rot_h, "PL-01", "REDES ELÉCTRICAS Y CATASTRO URBANO", "1 : 2500")

    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
    fig.savefig(out_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"[OK] Lámina PL-01 generada en: {out_pdf}")

# =========================================================================
# LÁMINA PL-02: TRAZO Y PERFIL LONGITUDINAL LÍNEA PRIMARIA 10 kV
# =========================================================================
def generar_lamina_pl02(out_pdf):
    print("[*] Generando Lámina PL-02: Perfil Longitudinal MT 10 kV...")
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    ax_bg = fig.add_axes([0, 0, 1, 1])
    dibujar_marco_general(fig, ax_bg)

    # Ventana gráfica principal del perfil
    ax = fig.add_axes([0.05, 0.28, 0.90, 0.68])
    ax.set_facecolor('#F8FAFC')

    postes_perfil = [
        ("E-01", 0.0, 3140.0, "13/400", "PR-3", "Pórtico Salida MCH 200 kW"),
        ("E-02", 95.0, 3125.0, "12/300", "PS-3", "Bajada quebrada norte"),
        ("E-03", 185.0, 3110.0, "12/300", "PS-3", "Acceso quebrada"),
        ("E-04", 270.0, 3098.0, "12/400", "PA-3", "Ángulo entrada a Jr. V. Hermosa"),
        ("E-05", 355.0, 3088.0, "12/300", "PS-3", "Jr. Villa Hermosa"),
        ("E-06", 440.0, 3080.0, "13/400", "SAB-1", "SED-01 Norte (50 kVA)"),
        ("E-07", 522.0, 3072.0, "12/300", "PS-3", "Jr. Progreso"),
        ("E-08", 605.0, 3065.0, "12/300", "PS-3", "Pje. Jorge Chávez"),
        ("E-09", 686.0, 3060.0, "12/400", "PA-3", "Ángulo margen río"),
        ("E-10", 771.0, 3055.0, "12/300", "PS-3", "Pje. Cantutani"),
        ("E-11", 856.0, 3052.0, "12/300", "PS-3", "Pje. Santa Elisa"),
        ("E-12", 936.0, 3050.0, "12/400", "PA-3", "Aprox. Plaza de Armas"),
        ("E-13", 997.0, 3050.0, "13/400", "SAB-2", "SED-02 Centro (100 kVA)"),
        ("E-14", 1082.0, 3048.0, "12/300", "PS-3", "Calle Municipal"),
        ("E-15", 1167.0, 3045.0, "12/300", "PS-3", "Sur centro urbano"),
        ("E-16", 1252.0, 3040.0, "12/400", "PA-3", "Ángulo confluencia"),
        ("E-17", 1337.0, 3035.0, "13/600", "PR-3", "Pórtico Norte Cruce Río"),
        ("E-18", 1447.0, 3030.0, "13/600", "PR-3", "Pórtico Sur Cruce Río (110m)"),
        ("E-19", 1532.0, 3025.0, "12/300", "PS-3", "Acceso Estadio"),
        ("E-20", 1618.0, 3020.0, "12/300", "PS-3", "Estadio Municipal"),
        ("E-21", 1700.0, 3015.0, "12/400", "PA-3", "Ángulo Piscina"),
        ("E-22", 1772.0, 3010.0, "13/400", "SAB-3", "SED-03 Estadio-Piscina (100 kVA)"),
        ("E-23", 1859.0, 3005.0, "12/300", "PS-3", "Pasaje Piscina"),
        ("E-24", 1968.0, 3000.0, "12/400", "PR-3", "Terminal Línea MT 10 kV")
    ]

    dist_x = [p[1] for p in postes_perfil]
    cota_y = [p[2] for p in postes_perfil]

    # Terreno
    ax.plot(dist_x, cota_y, color='#78350F', linewidth=2.2, label='Perfil del Terreno Natural')
    ax.fill_between(dist_x, cota_y, 2980.0, color='#D97706', alpha=0.15)

    # Postes y Catenarias
    h_poste_val = {'12/300': 10.2, '12/400': 10.2, '13/400': 11.0, '13/600': 11.0}
    cables_x = []
    cables_y = []

    for pid, px, py, p_tipo, armado, desc in postes_perfil:
        hp = h_poste_val.get(p_tipo, 10.2)
        # Dibujar poste vertical
        ax.plot([px, px], [py, py + hp], color='#0F172A', linewidth=2.0)
        cables_x.append(px)
        cables_y.append(py + hp)

        # Destacar subestaciones
        if 'SAB' in armado:
            ax.plot(px, py + hp, marker='s', markersize=9, color='#FACC15', markeredgecolor='#78350F', markeredgewidth=1.5, zorder=10)
            ax.text(px, py + hp + 4.0, f"{pid}\n{armado}\n{desc.split('(')[1].replace(')', '')}", ha='center', va='bottom', fontsize=6.2, fontweight='bold', color='#B45309', bbox=dict(boxstyle="round,pad=0.2", fc="#FEF3C7", ec="#F59E0B", lw=0.8))
        else:
            ax.plot(px, py + hp, marker='o', markersize=5, color='#DC2626', markeredgecolor='#FFFFFF', zorder=9)
            ax.text(px, py + hp + 2.0, f"{pid}", ha='center', va='bottom', fontsize=5.8, fontweight='bold', color='#1E293B')

    # Catenarias parabólicas aproximadas
    for i in range(len(cables_x) - 1):
        x1, y1 = cables_x[i], cables_y[i]
        x2, y2 = cables_x[i+1], cables_y[i+1]
        dx = x2 - x1
        flecha = 0.8 if dx < 100 else 1.6  # Flecha en metros según Truxa
        xs_c = [x1 + t * dx for t in [0.0, 0.25, 0.5, 0.75, 1.0]]
        ys_c = [y1 + t * (y2 - y1) - 4 * flecha * t * (1 - t) for t in [0.0, 0.25, 0.5, 0.75, 1.0]]
        ax.plot(xs_c, ys_c, color='#EF4444', linewidth=1.5, linestyle='-', zorder=8)

    # Indicar vano crítico del cruce del río
    ax.annotate("VANO ESPECIAL CRUCE RÍO (110 m)\nPostes Reforzados C.A.C. 13m / 600 daN",
                xy=(1392, 3042), xytext=(1392, 3090),
                ha='center', fontsize=7.5, fontweight='bold', color='#0284C7',
                arrowprops=dict(arrowstyle="->", color='#0284C7', lw=1.2),
                bbox=dict(boxstyle="round,pad=0.3", fc="#E0F2FE", ec="#0284C7", lw=1.0))

    ax.set_xlim(-50, 2020)
    ax.set_ylim(2985, 3175)
    ax.set_ylabel("Cota Altimétrica (m.s.n.m.)", fontsize=8.5, fontweight='bold', color='#1E293B')
    ax.set_title("PERFIL LONGITUDINAL TOPOGRÁFICO DE LA LÍNEA PRIMARIA 10 kV — MCH LIMBANI A TERMINAL SUR\n"
                 "Conductor AAAC 35 mm² | Tensión 10 kV | Conductor Catenaria Truxa Flecha Máxima a 35 °C",
                 fontsize=10.5, fontweight='bold', color='#0F172A', pad=12)
    ax.grid(color='#CBD5E1', linestyle='--', linewidth=0.6)

    # Tabla de datos técnicos al pie del perfil (Guitarras de cotas)
    ax_tab = fig.add_axes([0.05, 0.04, 0.62, 0.22])
    ax_tab.set_facecolor('#F8FAFC')
    ax_tab.set_xlim(-50, 2020)
    ax_tab.set_ylim(0, 4)
    ax_tab.axis('off')

    # Filas de la guitarra
    labels_filas = ["DISTANCIA PARCIAL (m)", "DISTANCIA ACUM. (m)", "COTA TERRENO (m)", "ESTRUCTURA / ARMADO"]
    for idx, lab in enumerate(labels_filas):
        ax_tab.plot([-50, 2020], [idx, idx], color='#334155', linewidth=0.8)
        ax_tab.text(-40, idx + 0.5, lab, ha='left', va='center', fontsize=6.2, fontweight='bold', color='#1E3A8A')
    ax_tab.plot([-50, 2020], [4, 4], color='#334155', linewidth=0.8)

    for i, p in enumerate(postes_perfil):
        px = p[1]
        cota = p[2]
        dp = p[1] if i == 0 else (p[1] - postes_perfil[i-1][1])
        ax_tab.plot([px, px], [0, 4], color='#94A3B8', linewidth=0.5, linestyle=':')
        ax_tab.text(px, 0.5, f"{dp:.0f}", ha='center', va='center', fontsize=5.5, color='#0F172A', rotation=90)
        ax_tab.text(px, 1.5, f"{px:.0f}", ha='center', va='center', fontsize=5.5, color='#0F172A', rotation=90)
        ax_tab.text(px, 2.5, f"{cota:.1f}", ha='center', va='center', fontsize=5.5, color='#0F172A', rotation=90)
        ax_tab.text(px, 3.5, f"{p[0]}-{p[4]}", ha='center', va='center', fontsize=5.2, fontweight='bold', color='#B45309', rotation=90)

    # Rótulo de la lámina
    dibujar_rotulo_oficial(ax_bg, 0.70, 0.04, 0.28, 0.22, "PL-02", "TRAZO Y PERFIL LONGITUDINAL MT 10 kV", "H: 1:2000 | V: 1:200")

    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
    fig.savefig(out_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"[OK] Lámina PL-02 generada en: {out_pdf}")

# =========================================================================
# LÁMINA PL-03: DETALLE ELECTROMECÁNICO SUBESTACIÓN AÉREA BIPOSTE (SAB)
# =========================================================================
def generar_lamina_pl03(out_pdf):
    print("[*] Generando Lámina PL-03: Detalle Constructivo Subestación SAB...")
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    ax_bg = fig.add_axes([0, 0, 1, 1])
    dibujar_marco_general(fig, ax_bg)

    # Ventana gráfica: Esquema de elevación frontal y de perfil
    ax = fig.add_axes([0.05, 0.04, 0.63, 0.92])
    ax.set_facecolor('#F8FAFC')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Marco
    rect_m = patches.Rectangle((0, 0), 100, 100, facecolor='#F8FAFC', edgecolor='#334155', linewidth=1.2)
    ax.add_patch(rect_m)

    ax.text(50, 96, "SUBESTACIÓN AÉREA BIPOSTE (SAB) 10 / 0.38 - 0.22 kV (50 kVA y 100 kVA)\n"
                   "MONTAJE ELECTROMECÁNICO NORMALIZADO SEGÚN NORMA DGE / MEM",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0F172A')

    # Terreno
    ax.plot([5, 95], [15, 15], color='#78350F', linewidth=2.5)
    ax.text(8, 13, "NIVEL DE TERRENO NATURAL (± 0.00 m)", fontsize=6.5, color='#78350F', fontweight='bold')

    # Postes Biposte CAC 13m/400 daN (Elevación Frontal)
    # Poste Izquierdo (X=25), Poste Derecho (X=45) -> Distancia 2.0 m a escala
    ax.fill_between([23.5, 26.5], [0, 0], [85, 85], color='#64748B', alpha=0.3)
    ax.plot([23.5, 23.5], [0, 85], color='#334155', linewidth=1.5)
    ax.plot([26.5, 26.5], [0, 85], color='#334155', linewidth=1.5)

    ax.fill_between([43.5, 46.5], [0, 0], [85, 85], color='#64748B', alpha=0.3)
    ax.plot([43.5, 43.5], [0, 85], color='#334155', linewidth=1.5)
    ax.plot([46.5, 46.5], [0, 85], color='#334155', linewidth=1.5)

    ax.text(25, 4, "C.A.C. 13m / 400 daN\nEmpotramiento 1.50 m", ha='center', fontsize=5.8, color='#0F172A')
    ax.text(45, 4, "C.A.C. 13m / 400 daN\nEmpotramiento 1.50 m", ha='center', fontsize=5.8, color='#0F172A')

    # Cruceta superior de seccionamiento (Y=82)
    ax.fill_between([20, 50], [81, 81], [83, 83], color='#D97706', alpha=0.8)
    ax.text(35, 84.5, "Cruceta F°G° 100x100x6.4 mm x 2.50 m (Seccionadores Cut-out 15 kV + Pararrayos ZnO 12 kV)",
            ha='center', fontsize=6.2, fontweight='bold', color='#B45309')

    # Cortacircuitos fusibles (3 unidades)
    for cx in [27, 35, 43]:
        ax.plot([cx, cx], [83, 88], color='#DC2626', linewidth=2.0)
        ax.plot([cx - 1.5, cx + 1.5], [88, 88], color='#DC2626', linewidth=1.5)
        ax.plot(cx, 85.5, marker='o', markersize=4, color='#EF4444')

    # Plataforma de Transformador (Y=52)
    ax.fill_between([20, 50], [51, 51], [53, 53], color='#334155', alpha=0.9)
    ax.text(35, 49, "Plataforma de Perfiles UPN 120 / Madera Tratada (H = 5.50 m sobre nivel de piso)",
            ha='center', fontsize=6.0, fontweight='bold', color='#1E293B')

    # Transformador Trifásico dyn5 (Y=53 a 67)
    rect_trafo = patches.Rectangle((27, 53), 16, 14, facecolor='#FEF08A', edgecolor='#78350F', linewidth=1.5)
    ax.add_patch(rect_trafo)
    ax.text(35, 60, "TRANSFORMADOR TRIFÁSICO\n10 / 0.38 - 0.22 kV\n50 kVA / 100 kVA (dyn5)\nEnfriamiento ONAN",
            ha='center', va='center', fontsize=6.2, fontweight='bold', color='#78350F')

    # Tablero de Distribución BT (Y=26 a 36 en poste derecho)
    rect_td = patches.Rectangle((42, 26), 9, 11, facecolor='#93C5FD', edgecolor='#1E3A8A', linewidth=1.2)
    ax.add_patch(rect_td)
    ax.text(46.5, 31.5, "TABLERO BT\nGabinete IP54\nITM 125A/160A\nTotalizador",
            ha='center', va='center', fontsize=5.5, fontweight='bold', color='#1E3A8A')

    # Puesta a Tierra (PAT)
    # Bajada con fleje y electrodo vertical
    ax.plot([25, 25], [51, 8], color='#16A34A', linewidth=2.0, linestyle='--')
    ax.plot([25, 18], [8, 8], color='#16A34A', linewidth=2.0, linestyle='--')
    ax.plot([18, 18], [8, -5], color='#16A34A', linewidth=2.5)  # Varilla Copperweld
    ax.plot(18, 8, marker='o', markersize=5, color='#16A34A')
    ax.text(18, 10, "PAT Protección\nR <= 10 Ohm", ha='center', fontsize=5.5, fontweight='bold', color='#16A34A')

    ax.plot([45, 45], [26, 8], color='#16A34A', linewidth=2.0, linestyle='--')
    ax.plot([45, 52], [8, 8], color='#16A34A', linewidth=2.0, linestyle='--')
    ax.plot([52, 52], [8, -5], color='#16A34A', linewidth=2.5)  # Varilla Neutro
    ax.plot(52, 8, marker='o', markersize=5, color='#16A34A')
    ax.text(52, 10, "PAT Neutro\nR <= 5 Ohm", ha='center', fontsize=5.5, fontweight='bold', color='#16A34A')

    # VISTA DE PERFIL (X=65 a 90)
    ax.text(77, 90, "VISTA LATERAL DE PERFIL", ha='center', fontsize=7.5, fontweight='bold', color='#1E3A8A')
    ax.fill_between([75.5, 78.5], [0, 0], [85, 85], color='#64748B', alpha=0.3)
    ax.plot([75.5, 75.5], [0, 85], color='#334155', linewidth=1.5)
    ax.plot([78.5, 78.5], [0, 85], color='#334155', linewidth=1.5)
    # Ménsula y transformador
    rect_tr_lat = patches.Rectangle((70, 53), 14, 14, facecolor='#FEF08A', edgecolor='#78350F', linewidth=1.2)
    ax.add_patch(rect_tr_lat)
    ax.text(77, 60, "Trafo\nPerfil", ha='center', va='center', fontsize=5.8, color='#78350F')
    # Retenida contraviento en perfil
    ax.plot([77, 92], [80, 15], color='#EC4899', linewidth=1.5, linestyle='--')
    ax.plot(92, 15, marker='^', markersize=7, color='#EC4899')
    ax.text(88, 30, "Retenida\nContraviento", fontsize=5.5, color='#EC4899', fontweight='bold')

    # Panel lateral derecho con especificaciones técnicas y Rótulo
    ax_side = fig.add_axes([0.70, 0.04, 0.28, 0.92])
    ax_side.set_facecolor('#F8FAFC')
    ax_side.set_xlim(0, 1)
    ax_side.set_ylim(0, 1)
    ax_side.axis('off')

    rect_side = patches.Rectangle((0, 0), 1, 1, facecolor='#F8FAFC', edgecolor='#334155', linewidth=1.2)
    ax_side.add_patch(rect_side)

    ax_side.text(0.5, 0.97, "ESPECIFICACIONES DE MONTAJE SAB", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1E293B')
    ax_side.plot([0.05, 0.95], [0.95, 0.95], color='#334155', linewidth=1.0)

    specs = [
        ("Postes Principales:", "2 x CAC 13m / 400 daN (Norma DGE)"),
        ("Separación entre Postes:", "2.00 m entre ejes"),
        ("Profundidad Empotramiento:", "1.50 m con solado de concreto f'c=140"),
        ("Plataforma Soporte:", "Perfiles de acero galvanizado UPN 120"),
        ("Transformador Trifásico:", "Dyn5, 10 / 0.38-0.22 kV, ONAN"),
        ("• SED-01 (Jr. Villa Hermosa):", "50 kVA / Corriente In = 76.0 A"),
        ("• SED-02 (Plaza de Armas):", "100 kVA / Corriente In = 151.9 A"),
        ("• SED-03 (Estadio-Piscina):", "100 kVA / Corriente In = 151.9 A"),
        ("Seccionamiento MT:", "3 Cut-out 15 kV, 100 A, BIL 110 kV"),
        ("Protección Sobretensiones:", "3 Pararrayos ZnO 12 kV, 10 kA"),
        ("Fusibles Chicote:", "Tipo K (3A para 50kVA, 6A para 100kVA)"),
        ("Tablero de Distribución BT:", "Gabinete intemperie poliéster IP54"),
        ("Interruptor General Termomagnético:", "Regulable (100A para SED-01, 160A para SED-02/03)"),
        ("Sistema de Puesta a Tierra PAT:", "2 pozos verticales independientes:"),
        ("• PAT-1 Protección (Masas MT):", "Varilla Cu 5/8\"x2.4m, R <= 10 Ohm"),
        ("• PAT-2 Servicio (Neutro BT):", "Varilla Cu 5/8\"x2.4m, R <= 5 Ohm"),
        ("Distancia entre Pozos PAT:", "Minimo 6.0 m de separación")
    ]
    sy = 0.92
    for k, v in specs:
        ax_side.text(0.06, sy, k, va='center', fontsize=6.0, fontweight='bold', color='#334155')
        ax_side.text(0.94, sy, v, ha='right', va='center', fontsize=5.8, color='#0F172A')
        sy -= 0.024

    dibujar_rotulo_oficial(ax_side, 0.02, 0.015, 0.96, 0.22, "PL-03", "DETALLE SUBESTACIÓN AÉREA BIPOSTE (SAB)", "1 : 50 / 1 : 25")

    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
    fig.savefig(out_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"[OK] Lámina PL-03 generada en: {out_pdf}")

# =========================================================================
# LÁMINA PL-04: RED DE DISTRIBUCIÓN SECUNDARIA Y ALUMBRADO PÚBLICO
# =========================================================================
def generar_lamina_pl04(out_pdf):
    print("[*] Generando Lámina PL-04: Red Secundaria BT y Alumbrado Público...")
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    ax_bg = fig.add_axes([0, 0, 1, 1])
    dibujar_marco_general(fig, ax_bg)

    # Ventana gráfica izquierda: Detalles de armado de poste BT, AP y Acometida
    ax = fig.add_axes([0.05, 0.04, 0.63, 0.92])
    ax.set_facecolor('#F8FAFC')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    rect_m = patches.Rectangle((0, 0), 100, 100, facecolor='#F8FAFC', edgecolor='#334155', linewidth=1.2)
    ax.add_patch(rect_m)

    ax.text(50, 96, "REDES SECUNDARIAS 380/220 V, ALUMBRADO PÚBLICO Y ACOMETIDAS DOMICILIARIAS\n"
                   "SISTEMA TRIFÁSICO TETRAFILAR CON CONDUCTOR AUTOPORTANTE CAAI",
            ha='center', va='center', fontsize=9.2, fontweight='bold', color='#0F172A')

    # Detalle 1: Poste CAC 9m con Alumbrado Público y Conductor CAAI (X=10 a 45)
    ax.text(25, 90, "DETALLE DE POSTE C.A.C. 9m/300 daN\nCON LUMINARIA LED 50 W Y CAAI", ha='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')
    # Poste
    ax.fill_between([23.5, 26.5], [10, 10], [82, 82], color='#64748B', alpha=0.3)
    ax.plot([23.5, 23.5], [10, 82], color='#334155', linewidth=1.5)
    ax.plot([26.5, 26.5], [10, 82], color='#334155', linewidth=1.5)
    ax.plot([15, 35], [10, 10], color='#78350F', linewidth=2.0)  # Nivel terreno
    ax.text(25, 7, "C.A.C. 9m / 300 daN (H = 7.70 m libre)", ha='center', fontsize=5.8, color='#0F172A')

    # Conductor CAAI Troncal (Y=78)
    ax.plot([10, 40], [78, 78], color='#10B981', linewidth=3.0)
    ax.text(32, 80, "Cable CAAI 3x35+1x16+NA25 mm²\nSujeción con grapa de suspensión", fontsize=5.5, color='#047857', fontweight='bold')

    # Pastoral y luminaria AP (Y=79 hacia la derecha)
    ax.plot([25, 38], [79, 83], color='#B45309', linewidth=2.0)
    ax.plot([38, 41], [83, 81], color='#B45309', linewidth=2.0)
    # Luminaria LED
    rect_led = patches.Rectangle((39, 79), 5, 2.5, facecolor='#FBBF24', edgecolor='#B45309', linewidth=1.2)
    ax.add_patch(rect_led)
    ax.text(41.5, 77, "Luminaria LED 50 W\nFlujo: >= 6,500 lm\nVida útil: >= 50,000 h", ha='center', fontsize=5.5, fontweight='bold', color='#B45309')

    # Detalle 2: Acometida domiciliaria monofásica / trifásica (X=55 a 95)
    ax.text(75, 90, "DETALLE DE ACOMETIDA DOMICILIARIA\nY CAJA PORTAMEDIDOR CON PUESTA A TIERRA", ha='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')

    # Muro predial
    rect_muro = patches.Rectangle((80, 10), 12, 60, facecolor='#E2E8F0', edgecolor='#475569', linewidth=1.2)
    ax.add_patch(rect_muro)
    ax.plot([70, 98], [10, 10], color='#78350F', linewidth=2.0)
    ax.text(86, 6, "LÍNEA DE FACHADA PREDIAL", ha='center', fontsize=5.8, color='#78350F')

    # Cable concéntrico SET 2x6 mm² desde red BT (X=25 a poste o muro)
    ax.plot([25, 80], [75, 45], color='#2563EB', linewidth=1.5, linestyle=':')
    ax.text(50, 62, "Cable Concéntrico SET 2x6 mm² (Vano acometida <= 25 m)", ha='center', fontsize=5.5, color='#1D4ED8', fontweight='bold', rotation=-22)

    # Caja portamedidor (Y=30 a 42 en fachada predial)
    rect_caja = patches.Rectangle((82, 30), 8, 12, facecolor='#FEF08A', edgecolor='#78350F', linewidth=1.2)
    ax.add_patch(rect_caja)
    ax.text(86, 36, "CAJA L-T\nMedidor Electrónico\nMonofásico / Trifásico\nInterruptor Termomagnético",
            ha='center', va='center', fontsize=5.2, fontweight='bold', color='#78350F')

    # Pozo a tierra domiciliario
    ax.plot([86, 86], [30, 10], color='#16A34A', linewidth=1.5, linestyle='--')
    ax.plot([86, 86], [10, -3], color='#16A34A', linewidth=2.0)
    ax.plot(86, 10, marker='o', markersize=4, color='#16A34A')
    ax.text(86, 12, "PAT Domiciliario (R <= 15 Ohm)", ha='center', fontsize=5.2, color='#16A34A', fontweight='bold')

    # Panel lateral derecho con especificaciones técnicas de BT y Alumbrado
    ax_side = fig.add_axes([0.70, 0.04, 0.28, 0.92])
    ax_side.set_facecolor('#F8FAFC')
    ax_side.set_xlim(0, 1)
    ax_side.set_ylim(0, 1)
    ax_side.axis('off')

    rect_side = patches.Rectangle((0, 0), 1, 1, facecolor='#F8FAFC', edgecolor='#334155', linewidth=1.2)
    ax_side.add_patch(rect_side)

    ax_side.text(0.5, 0.97, "ESPECIFICACIONES TÉCNICAS BT Y AP", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1E293B')
    ax_side.plot([0.05, 0.95], [0.95, 0.95], color='#334155', linewidth=1.0)

    specs_bt = [
        ("Sistema de Distribución:", "380 / 220 V Trifásico tetrafilar"),
        ("Conductor Troncal CAAI:", "3x35 + 1x16 + NA25 mm² (3.98 km)"),
        ("Conductor Ramales CAAI:", "2x16 + 1x16 + NA25 mm² (2.23 km)"),
        ("Total Red Autoportante BT:", "6,206.73 m (6.21 km casco urbano)"),
        ("Portante Neutro Alfol:", "Aleación de Aluminio NA 25 mm²"),
        ("Aislamiento Conductor:", "Polietileno Reticulado XLPE 90°C"),
        ("Postes de BT Principales/AP:", "CAC 9m / 300 daN (139 unidades)"),
        ("Postes de BT Terminales:", "CAC 8m / 300 daN (38 unidades)"),
        ("Postes de BT en Pasajes:", "CAC 8m / 200 daN (66 unidades)"),
        ("Total Postes Baja Tensión:", "243 unidades (sin postes en carretera)"),
        ("Luminarias Alumbrado LED:", "166 unidades de 50 W / 220 V IP66"),
        ("Eficacia Luminosa LED:", ">= 130 lm/W (Flujo >= 6,500 lm)"),
        ("Pastoral de Alumbrado:", "Tubo de acero F°G° 1.5\" x 1.50 m"),
        ("Acometidas Domiciliarias:", "587 predios (534 C / 53 L)"),
        ("Conductor de Acometida:", "Concéntrico SET 2x4 mm² (4,604 m)"),
        ("Cajas Portamedidor:", "587 und policarbonato tipo L-T"),
        ("Medidores de Energía:", "Electrónicos digitales homologados"),
        ("Caída de Tensión Máxima:", "3.82% en extremo sur (Norma <= 5%)")
    ]
    sy = 0.92
    for k, v in specs_bt:
        ax_side.text(0.06, sy, k, va='center', fontsize=6.0, fontweight='bold', color='#334155')
        ax_side.text(0.94, sy, v, ha='right', va='center', fontsize=5.8, color='#0F172A')
        sy -= 0.024

    dibujar_rotulo_oficial(ax_side, 0.02, 0.015, 0.96, 0.22, "PL-04", "REDES SECUNDARIAS Y ALUMBRADO PÚBLICO", "Indicadas")

    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
    fig.savefig(out_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"[OK] Lámina PL-04 generada en: {out_pdf}")

# =========================================================================
# LÁMINA PL-05: ARMADOS NORMALIZADOS DGE Y PUESTA A TIERRA (PAT)
# =========================================================================
def generar_lamina_pl05(out_pdf):
    print("[*] Generando Lámina PL-05: Armados Normalizados DGE y PAT (Vectores Técnicos de Alta Resolución)...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vec_dir = os.path.join(base_dir, "expediente", "figuras", "armados_vector")

    # Si no existen los vectores, generarlos
    if not os.path.exists(os.path.join(vec_dir, "vector_ps3.png")):
        print("[*] Generando previamente diagramas vectoriales con exportar_armados_vectoriales_figuras.py...")
        import scripts.exportar_armados_vectoriales_figuras as evf
        evf.main()

    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    ax_bg = fig.add_axes([0, 0, 1, 1])
    dibujar_marco_general(fig, ax_bg)

    # Disposición en cuadrícula 4 filas x 2 columnas en la zona izquierda (X: 0.035 a 0.685)
    # Columna 0: Red Primaria MT y SEDs (PS-3, PA-3, PR-3, SAB)
    # Columna 1: Red Secundaria BT, Retenida, PAT y Acometida (E-1, Retenida, PAT, Acometida)
    col_x = [0.035, 0.355]
    w_cell = 0.312
    h_cell = 0.220
    row_y = [0.736, 0.508, 0.280, 0.052]

    cuadricula = [
        # (fila, col, archivo_png, cod_armado, titulo)
        (0, 0, "vector_ps3.png", "PS-3", "Suspensión MT 10 kV (0°-5°)"),
        (1, 0, "vector_pa3.png", "PA-3", "Ángulo MT 10 kV (5°-30°)"),
        (2, 0, "vector_pr3.png", "PR-3", "Retención / Anclaje MT 10 kV"),
        (3, 0, "vector_sab.png", "SAB", "Subestación Biposte 50/100 kVA"),
        (0, 1, "vector_e1.png", "E-1", "Distribución BT CAAI y AP LED"),
        (1, 1, "vector_retenida.png", "RET-INC", "Retenida Normalizada CNE 261"),
        (2, 1, "vector_pat.png", "PAT-VERT", "Pozo Puesta a Tierra Vertical"),
        (3, 1, "vector_acometida.png", "ACOM-LT", "Acometida Monofásica Tipo L-T"),
    ]

    for f_idx, c_idx, img_name, cod, tit in cuadricula:
        img_path = os.path.join(vec_dir, img_name)
        px = col_x[c_idx]
        py = row_y[f_idx]

        ax_cell = fig.add_axes([px, py, w_cell, h_cell])
        ax_cell.set_facecolor('#FFFFFF')
        ax_cell.axis('off')

        if os.path.exists(img_path):
            img = plt.imread(img_path)
            ax_cell.imshow(img, aspect='equal')
        else:
            ax_cell.text(0.5, 0.5, f"Diagrama Vectorial\n{cod} — {tit}", ha='center', va='center', fontsize=7, color='#DC2626')

        # Borde sutil del recuadro de celda
        rect_b = patches.Rectangle((0, 0), 1, 1, transform=ax_cell.transAxes, fill=False, edgecolor='#64748B', linewidth=0.8)
        ax_cell.add_patch(rect_b)

    # Panel lateral derecho y Rótulo oficial FIME - UNAP
    ax_side = fig.add_axes([0.685, 0.04, 0.295, 0.92])
    ax_side.set_facecolor('#F8FAFC')
    ax_side.set_xlim(0, 1)
    ax_side.set_ylim(0, 1)
    ax_side.axis('off')

    rect_side = patches.Rectangle((0, 0), 1, 1, facecolor='#F8FAFC', edgecolor='#334155', linewidth=1.2)
    ax_side.add_patch(rect_side)

    ax_side.text(0.5, 0.975, "ESTÁNDARES DGE Y ESPECIFICACIONES TÉCNICAS", ha='center', va='center', fontsize=7.8, fontweight='bold', color='#1E293B')
    ax_side.plot([0.05, 0.95], [0.96, 0.96], color='#334155', linewidth=1.0)

    normas = [
        ("Base Legal Principal:", "Código Nacional de Electricidad (CNE-Suministro 2011)"),
        ("Soportes MT Normalizados:", "R.D. N° 024-2003-EM/DGE (Láminas 004, 008, 020, 064, 074, 077)"),
        ("Soportes BT Normalizados:", "R.D. N° 023-2003-EM-DGE (Láminas 001, 007, 012, 014)"),
        ("Alumbrado de Vías Rurales:", "R.D. N° 017-2003-EM/DGE y R.M. N° 013-2003-EM"),
        ("Símbolos Gráficos DGE:", "R.M. N° 091-2002-EM/VME (Sección 9 Símbolos Eléctricos)"),
        ("Aisladores MT:", "Poliméricos y Pin porcelana clase ANSI 55-5 (BIL 110 kV)"),
        ("Tensión de Aislamiento:", "15 kV / Tensión de Servicio 10.0 kV Trifásico"),
        ("Distancia de Fuga Mínima:", ">= 31 mm/kV (Zona de alta pluviosidad 3,050 msnm)"),
        ("Retenidas Mecánicas:", "Cable de acero Siemens Martin 5/16\" (Carga rotura >= 35 kN)"),
        ("Aislador de Tracción Nuez:", "Porcelana vitrificada ANSI 54-1 a altura H >= 3.00 m del suelo"),
        ("Protector de Retenida:", "Tubo de PVC rígido amarillo 1 1/2\" x 1.80 m con franjas reflectivas"),
        ("Varilla de Anclaje:", "F°G° 5/8\" x 2.0 m con ojal guardacabo y bloque CAV 0.5x0.5x0.2 m"),
        ("Profundidad Anclaje Retenida:", "h = 1.80 m en fosa excavada y compactada en capas"),
        ("Pozos de Puesta a Tierra MT:", "Resistencia R <= 10 Ohmios (Subestaciones y Pararrayos ZnO)"),
        ("Pozos de Puesta a Tierra BT:", "Resistencia R <= 5 Ohmios (Neutro de servicio según CNE 060)"),
        ("Electrodo de Tierra PAT:", "Varilla de Copperweld 5/8\" x 2.40 m y bentonita sódica activa"),
        ("Red Secundaria Autoportante:", "Cable CAAI 3x35+1x16+NA25 mm² con neutro portador alfol"),
        ("Acometidas Particulares:", "Cable concéntrico SET 2x4 mm², caja L-T a H=1.40 m y medidor kWh"),
        ("Galvanizado en Caliente:", "Crucetas, pernos y herrajes según norma ASTM A153 / NTP 370.050")
    ]
    sy = 0.94
    for k, v in normas:
        ax_side.text(0.05, sy, k, va='center', fontsize=5.4, fontweight='bold', color='#334155')
        ax_side.text(0.95, sy, v, ha='right', va='center', fontsize=5.1, color='#0F172A')
        sy -= 0.023

    dibujar_rotulo_oficial(ax_side, 0.02, 0.015, 0.96, 0.22, "PL-05", "ARMADOS NORMALIZADOS DGE Y PAT", "Indicadas")

    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
    fig.savefig(out_pdf, format='pdf', dpi=300)
    plt.close(fig)
    print(f"[OK] Lámina PL-05 generada con 8 diagramas vectoriales en: {out_pdf}")

# =========================================================================
# FUNCIÓN PRINCIPAL
# =========================================================================
def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dxf_redes = os.path.join(base_dir, "entregables", "planos", "catastro_limbani_redes_electricas.dxf")
    out_dir = os.path.join(base_dir, "entregables", "planos")
    sync_dir = r"C:\Users\51949\Downloads\Catastro_Limbani\expediente_electrico"

    pl01_pdf = os.path.join(out_dir, "PL-01_plano_clave_general.pdf")
    pl02_pdf = os.path.join(out_dir, "PL-02_perfil_longitudinal_mt.pdf")
    pl03_pdf = os.path.join(out_dir, "PL-03_subestacion_sab_detalles.pdf")
    pl04_pdf = os.path.join(out_dir, "PL-04_redes_bt_alumbrado_publico.pdf")
    pl05_pdf = os.path.join(out_dir, "PL-05_armados_normalizados_dge_pat.pdf")

    generar_lamina_pl01(dxf_redes, pl01_pdf)
    generar_lamina_pl02(pl02_pdf)
    generar_lamina_pl03(pl03_pdf)
    generar_lamina_pl04(pl04_pdf)
    generar_lamina_pl05(pl05_pdf)

    # Sincronizar copias a Catastro_Limbani
    if os.path.exists(sync_dir):
        for p_pdf in [pl01_pdf, pl02_pdf, pl03_pdf, pl04_pdf, pl05_pdf]:
            shutil.copy2(p_pdf, os.path.join(sync_dir, os.path.basename(p_pdf)))
        print(f"[OK] 5 Láminas PDF sincronizadas en: {sync_dir}")

    print("\n" + "="*70)
    print("[OK] TODAS LAS LÁMINAS OFICIALES DE PLANOS PDF GENERADAS CON ÉXITO")
    print("="*70)

if __name__ == "__main__":
    main()
