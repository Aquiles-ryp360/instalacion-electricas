#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exportar_armados_vectoriales_figuras.py
Genera 8 láminas de detalle técnico electromecánico vectorial de alta resolución (300 DPI)
en formato PNG para su incorporación en el Expediente Técnico en LaTeX y Word,
reemplazando cualquier captura raster escaneada por dibujos de ingeniería 100% vectoriales:

1. vector_ps3.png: Armado de Suspensión PS-3 (10 kV, 0°-5°) - R.D. N° 024-2003-EM/DGE Lám. 004
2. vector_pa3.png: Armado de Ángulo PA-3 (10 kV, 5°-30°) - R.D. N° 024-2003-EM/DGE Lám. 008
3. vector_pr3.png: Armado de Retención / Anclaje PR-3 (10 kV, >30°) - R.D. N° 024-2003-EM/DGE Lám. 020
4. vector_sab.png: Subestación Aérea Biposte SAB (50/100 kVA) - R.D. N° 024-2003-EM/DGE Lám. 064
5. vector_e1.png: Estructura E-1 CAAI y Alumbrado LED 50W - R.D. N° 023-2003-EM-DGE Lám. 001
6. vector_retenida.png: Retenida Inclinada CNE Regla 261 / R.D. 024 Lám. 074
7. vector_pat.png: Pozo de Puesta a Tierra PAT con Electrodo Vertical - R.D. 024 Lám. 077
8. vector_acometida.png: Acometida Monofásica Aérea y Caja L-T - R.D. 023 Lám. 007

Autor: Br. Aquiles Taylor Ramos Yapo (Cód. 227368) | FIME - UNA Puno
"""

import os
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon

# -------------------------------------------------------------------------
# ESTILOS GRÁFICOS Y CONSTANTES
# -------------------------------------------------------------------------
COLOR_POLE = '#334155'         # Gris oscuro concreto centrifugado
COLOR_STEEL = '#1E3A8A'        # Azul marino perfiles y acero galvanizado
COLOR_INSULATOR = '#DC2626'    # Rojo óxido / marrón aisladores porcelana/polímero
COLOR_CONDUCTOR = '#0284C7'    # Azul cielo conductores AAAC / fase
COLOR_GUY = '#BE185D'          # Fucsia/rosa cable de retenida
COLOR_GROUND = '#78350F'       # Tierra y cimentación
COLOR_FOUNDATION = '#94A3B8'   # Concreto ciclópeo
COLOR_COPPER = '#B45309'       # Cobre electrodo PAT
COLOR_TEXT = '#0F172A'         # Texto principal
COLOR_NOTE = '#475569'         # Texto secundario
COLOR_DIM = '#0369A1'          # Cotas azul ingeniería
COLOR_TABLE_HDR = '#0F766E'    # Verde azulado cabecera

def dibujar_marco_base(ax, codigo, titulo, norma):
    """Configura el fondo técnico, recuadros y encabezado institucional."""
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Marco perimetral
    rect_ext = patches.Rectangle((1.0, 1.0), 98.0, 98.0, fill=False, edgecolor='#0F172A', linewidth=1.8)
    rect_int = patches.Rectangle((1.8, 1.8), 96.4, 96.4, fill=False, edgecolor='#64748B', linewidth=0.8)
    ax.add_patch(rect_ext)
    ax.add_patch(rect_int)

    # Franja superior encabezado
    rect_hdr = patches.Rectangle((1.8, 90.5), 96.4, 7.7, facecolor='#F1F5F9', edgecolor='#334155', linewidth=1.0)
    ax.add_patch(rect_hdr)
    ax.plot([25.0, 25.0], [90.5, 98.2], color='#334155', linewidth=1.0)

    # Institución
    ax.text(13.4, 95.8, "UNA PUNO — FIME", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1E3A8A')
    ax.text(13.4, 92.6, "ING. MECÁNICA ELÉCTRICA\nREDES DE DISTRIBUCIÓN", ha='center', va='center', fontsize=6.8, color='#334155')

    # Título principal y norma
    ax.text(28.0, 95.8, f"DETALLE ELECTROMECÁNICO NORMALIZADO: {codigo} — {titulo}",
            ha='left', va='center', fontsize=10.0, fontweight='bold', color='#0F172A')
    ax.text(28.0, 92.6, f"NORMA TÉCNICA APLICABLE: {norma}  |  PROYECTO: ELECTRIFICACIÓN LIMBANI 200 kW",
            ha='left', va='center', fontsize=7.2, fontweight='bold', color='#B45309')

    # Línea divisoria central: Izquierda Dibujo Técnico (0 a 64), Derecha Metrado y Notas (64 a 98.2)
    ax.plot([64.0, 64.0], [1.8, 90.5], color='#CBD5E1', linewidth=1.0)

def dibujar_cota_h(ax, x1, x2, y, texto, offset_t=1.5):
    """Dibuja una cota técnica horizontal."""
    ax.plot([x1, x1], [y - offset_t, y + 1.0], color=COLOR_DIM, linewidth=0.7)
    ax.plot([x2, x2], [y - offset_t, y + 1.0], color=COLOR_DIM, linewidth=0.7)
    ax.plot([x1, x2], [y, y], color=COLOR_DIM, linewidth=0.8)
    # Ticks a 45 grados
    ax.plot([x1 - 0.4, x1 + 0.4], [y - 0.4, y + 0.4], color=COLOR_DIM, linewidth=1.0)
    ax.plot([x2 - 0.4, x2 + 0.4], [y - 0.4, y + 0.4], color=COLOR_DIM, linewidth=1.0)
    ax.text((x1 + x2)/2.0, y + 0.6, texto, ha='center', va='bottom', fontsize=6.2, fontweight='bold', color=COLOR_DIM)

def dibujar_cota_v(ax, y1, y2, x, texto, offset_t=1.5):
    """Dibuja una cota técnica vertical."""
    ax.plot([x - offset_t, x + 1.0], [y1, y1], color=COLOR_DIM, linewidth=0.7)
    ax.plot([x - offset_t, x + 1.0], [y2, y2], color=COLOR_DIM, linewidth=0.7)
    ax.plot([x, x], [y1, y2], color=COLOR_DIM, linewidth=0.8)
    # Ticks a 45 grados
    ax.plot([x - 0.4, x + 0.4], [y1 - 0.4, y1 + 0.4], color=COLOR_DIM, linewidth=1.0)
    ax.plot([x - 0.4, x + 0.4], [y2 - 0.4, y2 + 0.4], color=COLOR_DIM, linewidth=1.0)
    ax.text(x + 0.8, (y1 + y2)/2.0, texto, ha='left', va='center', fontsize=6.2, fontweight='bold', color=COLOR_DIM, rotation=90)

def dibujar_llamada(ax, p_obj, p_txt, texto, num_item=None):
    """Dibuja un globo de directriz técnica apuntando al objeto."""
    xo, yo = p_obj
    xt, yt = p_txt
    ax.plot(xo, yo, marker='o', markersize=3.0, color='#B91C1C')
    dx = xt - xo
    x_codo = xt - (2.0 if dx > 0 else -2.0)
    ax.plot([xo, x_codo, xt], [yo, yt, yt], color='#64748B', linewidth=0.7)

    if num_item is not None:
        c_x = xt + (1.6 if dx > 0 else -1.6)
        circ = patches.Circle((c_x, yt), radius=1.3, facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=1.0)
        ax.add_patch(circ)
        ax.text(c_x, yt, str(num_item), ha='center', va='center', fontsize=5.8, fontweight='bold', color='#DC2626')
        ax.text(xt + (3.6 if dx > 0 else -3.6), yt, texto, ha='left' if dx > 0 else 'right', va='center', fontsize=5.8, color=COLOR_TEXT)
    else:
        ax.text(xt + (0.8 if dx > 0 else -0.8), yt, texto, ha='left' if dx > 0 else 'right', va='center', fontsize=5.8, color=COLOR_TEXT)

def dibujar_tabla_materiales(ax, x0, y0, w, items, titulo="PLANILLA DE MATERIALES NORMALIZADOS DGE"):
    """Dibuja la tabla formal de especificaciones y materiales."""
    h_row = 3.6
    n = len(items)
    h_tot = 5.5 + (n + 1) * h_row

    # Fondo encabezado
    rect_th = patches.Rectangle((x0, y0 - 5.5), w, 5.5, facecolor=COLOR_TABLE_HDR, edgecolor='#0F172A', linewidth=1.0)
    ax.add_patch(rect_th)
    ax.text(x0 + w/2.0, y0 - 2.8, titulo, ha='center', va='center', fontsize=7.2, fontweight='bold', color='#FFFFFF')

    # Encabezados de columna: Ítem (8%), Cant (10%), Und (10%), Descripción (72%)
    y_hdr = y0 - 5.5
    rect_ch = patches.Rectangle((x0, y_hdr - h_row), w, h_row, facecolor='#E2E8F0', edgecolor='#64748B', linewidth=0.8)
    ax.add_patch(rect_ch)
    
    col_w = [0.08 * w, 0.10 * w, 0.10 * w, 0.72 * w]
    x_c = [x0, x0 + col_w[0], x0 + col_w[0] + col_w[1], x0 + col_w[0] + col_w[1] + col_w[2], x0 + w]

    ax.text(x0 + col_w[0]/2.0, y_hdr - h_row/2.0, "ÍTEM", ha='center', va='center', fontsize=5.8, fontweight='bold')
    ax.text(x_c[1] + col_w[1]/2.0, y_hdr - h_row/2.0, "CANT", ha='center', va='center', fontsize=5.8, fontweight='bold')
    ax.text(x_c[2] + col_w[2]/2.0, y_hdr - h_row/2.0, "UND", ha='center', va='center', fontsize=5.8, fontweight='bold')
    ax.text(x_c[3] + 1.0, y_hdr - h_row/2.0, "DESCRIPCIÓN NORMALIZADA DE MATERIAL", ha='left', va='center', fontsize=5.8, fontweight='bold')

    # Filas
    curr_y = y_hdr - h_row
    for idx, (it, cant, und, desc) in enumerate(items):
        curr_y -= h_row
        bg_col = '#F8FAFC' if idx % 2 == 1 else '#FFFFFF'
        r_row = patches.Rectangle((x0, curr_y), w, h_row, facecolor=bg_col, edgecolor='#CBD5E1', linewidth=0.6)
        ax.add_patch(r_row)

        ax.text(x0 + col_w[0]/2.0, curr_y + h_row/2.0, str(it), ha='center', va='center', fontsize=5.5, fontweight='bold', color='#1E3A8A')
        ax.text(x_c[1] + col_w[1]/2.0, curr_y + h_row/2.0, str(cant), ha='center', va='center', fontsize=5.5)
        ax.text(x_c[2] + col_w[2]/2.0, curr_y + h_row/2.0, str(und), ha='center', va='center', fontsize=5.5)
        ax.text(x_c[3] + 1.0, curr_y + h_row/2.0, desc, ha='left', va='center', fontsize=5.3, color='#0F172A')

    # Borde exterior de tabla
    rect_box = patches.Rectangle((x0, curr_y), w, y0 - curr_y, fill=False, edgecolor='#0F172A', linewidth=1.0)
    ax.add_patch(rect_box)

    return curr_y

def dibujar_bloque_notas(ax, x0, y_top, w, notas):
    """Dibuja un cuadro de notas técnicas y condiciones de diseño."""
    h_tot = y_top - 3.5
    rect_n = patches.Rectangle((x0, 3.5), w, h_tot, facecolor='#FEF9C3', edgecolor='#CA8A04', linewidth=1.0)
    ax.add_patch(rect_n)

    ax.text(x0 + w/2.0, y_top - 2.8, "NOTAS TÉCNICAS Y REGLAMENTARIAS", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#854D0E')
    ax.plot([x0 + 1.5, x0 + w - 1.5], [y_top - 5.0, y_top - 5.0], color='#CA8A04', linewidth=0.8)

    y_t = y_top - 7.5
    for num, nota in enumerate(notas, 1):
        ax.text(x0 + 1.5, y_t, f"{num}. {nota}", ha='left', va='top', fontsize=5.2, color='#713F12', wrap=True)
        y_t -= 3.6

# =========================================================================
# 1. ARMADO PS-3: SUSPENSIÓN 10 kV (0° - 5°)
# =========================================================================
def generar_vector_ps3(out_file):
    fig, ax = plt.subplots(figsize=(11.69, 8.27), dpi=300)
    dibujar_marco_base(ax, "PS-3", "ESTRUCTURA DE SUSPENSIÓN 10 kV (0° a 5°)", "R.D. N° 024-2003-EM/DGE — LÁMINA 004")

    # Coordenadas eje del poste: X=32, Terreno Y=18, Cúspide Y=82 (H_total=64 unds equiv. a 12m)
    # Empotramiento Y=6 a Y=18 (1.70 m)
    # Bloque de cimentación
    fnd = patches.Rectangle((27, 4), 10, 14, facecolor='#CBD5E1', edgecolor='#475569', linewidth=1.0, hatch='//')
    ax.add_patch(fnd)
    ax.text(32, 2.5, "Solera de concreto 0.80 x 0.80 x 1.70 m", ha='center', fontsize=5.5, color=COLOR_NOTE)

    # Línea de terreno natural
    ax.plot([14, 52], [18, 18], color=COLOR_GROUND, linewidth=2.0)
    ax.text(16, 19, "N.T. ±0.00 (Terreno Natural)", fontsize=5.8, fontweight='bold', color=COLOR_GROUND)

    # Poste cónico CAC 12/300
    poly_poste = Polygon([(30.2, 18), (30.8, 82), (33.2, 82), (33.8, 18)], facecolor='#94A3B8', edgecolor=COLOR_POLE, linewidth=1.5)
    ax.add_patch(poly_poste)
    poly_emp = Polygon([(29.8, 4), (30.2, 18), (33.8, 18), (34.2, 4)], facecolor='#64748B', edgecolor=COLOR_POLE, linewidth=1.2, linestyle='--')
    ax.add_patch(poly_emp)

    # Cruceta simétrica de acero galvanizado L 75x75x6.4 mm x 2000 mm a Y=79
    cruz = patches.Rectangle((20, 78.2), 24, 1.6, facecolor=COLOR_STEEL, edgecolor='#0F172A', linewidth=1.2)
    ax.add_patch(cruz)

    # Riostras / Diagonales angulares
    ax.plot([25, 32], [78.2, 72], color=COLOR_STEEL, linewidth=2.0)
    ax.plot([39, 32], [78.2, 72], color=COLOR_STEEL, linewidth=2.0)
    ax.plot(32, 72, marker='o', markersize=3.5, color='#0F172A') # Abrazadera

    # Espigas y Aisladores Pin ANSI 55-5 (Fases L1, L2, L3)
    pos_fases = [22.0, 32.0, 42.0]
    for xf in pos_fases:
        # Espiga F°G°
        ax.plot([xf, xf], [79.8, 82.5], color=COLOR_STEEL, linewidth=2.2)
        # Falda de aislador porcelana pin
        aisl = patches.Polygon([(xf - 1.2, 82.5), (xf + 1.2, 82.5), (xf + 0.8, 85.0), (xf - 0.8, 85.0)],
                               facecolor=COLOR_INSULATOR, edgecolor='#7F1D1D', linewidth=1.0)
        ax.add_patch(aisl)
        camp = patches.Circle((xf, 85.5), radius=0.9, facecolor=COLOR_INSULATOR, edgecolor='#7F1D1D', linewidth=1.0)
        ax.add_patch(camp)
        # Garganta y Conductor AAAC 35 mm²
        ax.plot([xf - 2.5, xf + 2.5], [86.0, 86.0], color=COLOR_CONDUCTOR, linewidth=2.0)
        ax.plot(xf, 86.0, marker='x', markersize=4, color='#F59E0B') # Atadura

    # Fases labels
    ax.text(22, 88.0, "Fase L1\n(Extremo)", ha='center', fontsize=5.2, fontweight='bold', color=COLOR_CONDUCTOR)
    ax.text(32, 88.0, "Fase L2\n(Central)", ha='center', fontsize=5.2, fontweight='bold', color=COLOR_CONDUCTOR)
    ax.text(42, 88.0, "Fase L3\n(Extremo)", ha='center', fontsize=5.2, fontweight='bold', color=COLOR_CONDUCTOR)

    # Cotas
    dibujar_cota_h(ax, 20, 44, 75.5, "Cruceta L 75x75x6.4 mm x 2.00 m")
    dibujar_cota_h(ax, 22, 32, 89.5, "1.00 m")
    dibujar_cota_h(ax, 32, 42, 89.5, "1.00 m")
    dibujar_cota_v(ax, 4, 18, 18.0, "Empotramiento = 1.70 m")
    dibujar_cota_v(ax, 18, 82, 18.0, "Altura Libre = 10.30 m")
    dibujar_cota_v(ax, 4, 82, 13.0, "Longitud Total CAC = 12.00 m")

    # Llamadas
    dibujar_llamada(ax, (32, 85.5), (48, 83), "Aislador Tipo Pin ANSI 55-5", num_item=1)
    dibujar_llamada(ax, (20, 79.0), (12, 79), "Cruceta F°G° 75x75x6.4x2000mm", num_item=2)
    dibujar_llamada(ax, (32, 72.0), (46, 72), "Diagonales F°G° 38x6.4x750mm", num_item=3)
    dibujar_llamada(ax, (32, 50.0), (46, 50), "Poste C.A.C. 12m / 300 daN", num_item=4)
    dibujar_llamada(ax, (32, 10.0), (46, 10), "Cimentación Ciclópea 1:10+30%PG", num_item=5)

    # Planilla de Materiales
    items = [
        (1, 1, "und", "Poste de concreto armado centrifugado CAC 12m / 300 daN"),
        (2, 1, "und", "Cruceta simétrica de perfil angular L F°G° 75x75x6.4 x 2000 mm"),
        (3, 2, "und", "Pletina arriostre angular F°G° 38x6.4 x 750 mm c/pernos 1/2\"x1 1/2\""),
        (4, 3, "und", "Aislador de porcelana tipo Pin clase ANSI 55-5"),
        (5, 3, "und", "Espiga para cruceta de F°G° de 3/4\" x 7\" con arandela y tuerca"),
        (6, 1, "jgo", "Abrazadera partida platina F°G° de 3\" x 1/4\" para cabeza de poste"),
        (7, 3, "jgo", "Varilla de armar preformada de aleación de Al para AAAC 35 mm²"),
        (8, 1, "est", "Cimentación ciclópea concreto 1:10 + 30% PG solera 0.8x0.8x1.7 m")
    ]
    y_table_bot = dibujar_tabla_materiales(ax, 65.5, 89.0, 31.5, items, "PLANILLA DE MATERIALES NORMALIZADOS PS-3")

    # Bloque de notas
    notas = [
        "Estructura aplicable exclusivamente a tramos rectos o con ángulo de desvío 0° <= alpha <= 5°.",
        "Vano horizontal máximo admisible: Vh = 95 metros para zona de viento y altitud 3,050 m.s.n.m.",
        "Cruceta y pernos galvanizados en caliente según norma ASTM A153 / NTP 370.050.",
        "Profundidad de enterramiento del poste: h = H/10 + 0.50 m = 12/10 + 0.50 = 1.70 m.",
        "Conforme a Norma R.D. N° 024-2003-EM/DGE - Lámina 004."
    ]
    dibujar_bloque_notas(ax, 65.5, y_table_bot - 2.0, 31.5, notas)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    fig.savefig(out_file, format='png', dpi=300)
    plt.close(fig)
    print(f"[OK] Generado vector_ps3.png en: {out_file}")

# =========================================================================
# 2. ARMADO PA-3: ÁNGULO 10 kV (5° - 30°)
# =========================================================================
def generar_vector_pa3(out_file):
    fig, ax = plt.subplots(figsize=(11.69, 8.27), dpi=300)
    dibujar_marco_base(ax, "PA-3", "ESTRUCTURA DE ÁNGULO 10 kV (5° a 30°)", "R.D. N° 024-2003-EM/DGE — LÁMINA 008")

    # Poste CAC 12/400 en X=28
    fnd = patches.Rectangle((23, 4), 10, 14, facecolor='#CBD5E1', edgecolor='#475569', linewidth=1.0, hatch='//')
    ax.add_patch(fnd)

    ax.plot([10, 58], [18, 18], color=COLOR_GROUND, linewidth=2.0)
    ax.text(12, 19, "N.T. ±0.00", fontsize=5.8, fontweight='bold', color=COLOR_GROUND)

    poly_poste = Polygon([(26.2, 18), (26.8, 82), (29.2, 82), (29.8, 18)], facecolor='#94A3B8', edgecolor=COLOR_POLE, linewidth=1.5)
    ax.add_patch(poly_poste)
    poly_emp = Polygon([(25.8, 4), (26.2, 18), (29.8, 18), (30.2, 4)], facecolor='#64748B', edgecolor=COLOR_POLE, linewidth=1.2, linestyle='--')
    ax.add_patch(poly_emp)

    # Cruceta angular reforzada a Y=79
    cruz = patches.Rectangle((16, 78.2), 24, 1.8, facecolor=COLOR_STEEL, edgecolor='#0F172A', linewidth=1.2)
    ax.add_patch(cruz)
    ax.plot([21, 28], [78.2, 72], color=COLOR_STEEL, linewidth=2.2)
    ax.plot([35, 28], [78.2, 72], color=COLOR_STEEL, linewidth=2.2)

    # Aisladores Pin con doble cuello para retención angular
    for xf in [18.0, 28.0, 38.0]:
        ax.plot([xf, xf], [80.0, 82.5], color=COLOR_STEEL, linewidth=2.2)
        aisl = patches.Polygon([(xf - 1.3, 82.5), (xf + 1.3, 82.5), (xf + 0.9, 85.0), (xf - 0.9, 85.0)],
                               facecolor=COLOR_INSULATOR, edgecolor='#7F1D1D', linewidth=1.0)
        ax.add_patch(aisl)
        camp = patches.Circle((xf, 85.5), radius=1.0, facecolor=COLOR_INSULATOR, edgecolor='#7F1D1D', linewidth=1.0)
        ax.add_patch(camp)
        # Línea de conductor con ángulo
        ax.plot([xf - 2.5, xf, xf + 2.5], [85.5, 86.2, 85.7], color=COLOR_CONDUCTOR, linewidth=2.0)
        ax.plot(xf, 86.2, marker='D', markersize=4, color='#F59E0B') # Doble atadura

    # Retenida Biselar de Contratiro (sale de Y=77 en X=28 hacia X=52, Y=18)
    ax.plot(28, 77, marker='s', markersize=4, color='#0F172A')
    ax.plot([28, 52], [77, 18], color=COLOR_GUY, linewidth=2.0)
    # Aislador nuez 54-1 a Y=46 (altura libre > 3.0m)
    ax.plot(40, 47.5, marker='o', markersize=5.0, color='#F59E0B', markeredgecolor='#78350F')
    ax.text(42, 48.0, "Aislador nuez 54-1\n(H >= 3.0 m)", fontsize=5.0, color='#B45309', fontweight='bold')
    # Tubo protector PVC amarillo
    ax.plot([47, 52], [30, 18], color='#EAB308', linewidth=3.5)
    ax.text(50, 24, "Protector PVC 1.80m", fontsize=4.8, color='#A16207')
    # Varilla y bloque de concreto subterráneo
    ax.plot([52, 55], [18, 9], color=COLOR_STEEL, linewidth=2.0)
    blk = patches.Rectangle((53, 5), 5, 4, facecolor='#64748B', edgecolor='#0F172A', linewidth=1.0)
    ax.add_patch(blk)
    ax.text(55.5, 3.2, "Bloque CAV 0.5x0.5x0.2m (h=1.8m)", ha='center', fontsize=5.0, color=COLOR_NOTE)

    # Cotas
    dibujar_cota_h(ax, 16, 40, 75.0, "Cruceta F°G° 75x75x6.4 x 2.00 m")
    dibujar_cota_v(ax, 4, 18, 14.0, "1.70 m")
    dibujar_cota_v(ax, 18, 82, 14.0, "10.30 m")
    dibujar_cota_v(ax, 4, 82, 9.0, "Total = 12.00 m")

    # Llamadas
    dibujar_llamada(ax, (28, 85.5), (42, 85), "Pin ANSI 55-5 c/Doble Amarre", num_item=1)
    dibujar_llamada(ax, (28, 77.0), (12, 77), "Retenida Biselar en Vértice", num_item=2)
    dibujar_llamada(ax, (28, 50.0), (38, 62), "Poste C.A.C. 12m / 400 daN", num_item=3)

    # Tabla de materiales
    items = [
        (1, 1, "und", "Poste de concreto armado centrifugado CAC 12m / 400 daN"),
        (2, 1, "und", "Cruceta angular reforzada L F°G° 75x75x6.4 x 2000 mm"),
        (3, 2, "und", "Pletina arriostre F°G° 38x6.4 x 750 mm con pernos 1/2\""),
        (4, 3, "und", "Aislador de porcelana tipo Pin clase ANSI 55-5 para ángulo"),
        (5, 3, "und", "Espiga para cruceta F°G° 3/4\" x 7\" de alta resistencia"),
        (6, 1, "est", "Retenida simple inclinada cable SM 5/16\" (rotura >= 35 kN)"),
        (7, 1, "und", "Aislador de tracción tipo nuez de porcelana ANSI 54-1"),
        (8, 1, "und", "Varilla de anclaje F°G° 5/8\"x2.0m c/guardacabo y bloque CAV 0.5m"),
        (9, 1, "und", "Protector de retenida PVC amarillo 1.80m bandas reflectivas"),
        (10, 1, "est", "Cimentación ciclópea solera 0.8x0.8x1.7 m (f'c=100 kg/cm²)")
    ]
    y_table_bot = dibujar_tabla_materiales(ax, 65.5, 89.0, 31.5, items, "PLANILLA DE MATERIALES NORMALIZADOS PA-3")

    notas = [
        "Estructura aplicable a vértices con ángulo de deflexión 5° < alpha <= 30°.",
        "La retenida mecánica debe orientarse en la bisectriz exterior del ángulo topográfico.",
        "Los conductores se sujetan mediante doble atadura lateral normalizada con alambre de aleación.",
        "Tensión de rotura mínima del cable de retenida: 35.0 kN (Siemens Martin 5/16\").",
        "Conforme a Norma R.D. N° 024-2003-EM/DGE - Lámina 008."
    ]
    dibujar_bloque_notas(ax, 65.5, y_table_bot - 2.0, 31.5, notas)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    fig.savefig(out_file, format='png', dpi=300)
    plt.close(fig)
    print(f"[OK] Generado vector_pa3.png en: {out_file}")

# =========================================================================
# 3. ARMADO PR-3: RETENCIÓN / ANCLAJE 10 kV (>30° O TERMINAL)
# =========================================================================
def generar_vector_pr3(out_file):
    fig, ax = plt.subplots(figsize=(11.69, 8.27), dpi=300)
    dibujar_marco_base(ax, "PR-3", "ESTRUCTURA DE RETENCIÓN / ANCLAJE 10 kV (> 30°)", "R.D. N° 024-2003-EM/DGE — LÁMINA 020")

    # Poste CAC 13/400 o 13/600 en X=28, Cúspide Y=83, Terreno Y=18
    fnd = patches.Rectangle((22, 3), 12, 15, facecolor='#CBD5E1', edgecolor='#475569', linewidth=1.0, hatch='//')
    ax.add_patch(fnd)

    ax.plot([8, 60], [18, 18], color=COLOR_GROUND, linewidth=2.0)
    ax.text(10, 19, "N.T. ±0.00", fontsize=5.8, fontweight='bold', color=COLOR_GROUND)

    poly_poste = Polygon([(26.0, 18), (26.7, 83), (29.3, 83), (30.0, 18)], facecolor='#94A3B8', edgecolor=COLOR_POLE, linewidth=1.5)
    ax.add_patch(poly_poste)
    poly_emp = Polygon([(25.6, 3), (26.0, 18), (30.0, 18), (30.4, 3)], facecolor='#64748B', edgecolor=COLOR_POLE, linewidth=1.2, linestyle='--')
    ax.add_patch(poly_emp)

    # Doble Cruceta reforzada UPN o L 100x100x6.4 mm a Y=80
    cruz1 = patches.Rectangle((16, 79.5), 24, 2.0, facecolor=COLOR_STEEL, edgecolor='#0F172A', linewidth=1.2)
    cruz2 = patches.Rectangle((16, 76.5), 24, 2.0, facecolor=COLOR_STEEL, edgecolor='#0F172A', linewidth=1.2)
    ax.add_patch(cruz1)
    ax.add_patch(cruz2)
    # Pernos separadores
    for xp in [17, 28, 39]:
        ax.plot([xp, xp], [76.5, 81.5], color='#F59E0B', linewidth=1.8)

    # Cadenas de suspensión poliméricas 15 kV / 70 kN horizontales (anclaje de tiro)
    fases_x = [19.0, 28.0, 37.0]
    for xf in fases_x:
        # Cadena izquierda (vano de entrada)
        ax.plot([xf - 5.0, xf - 0.5], [80.5, 80.5], color=COLOR_INSULATOR, linewidth=3.5)
        ax.plot(xf - 5.0, 80.5, marker='<', markersize=5, color=COLOR_STEEL) # Grapa pistola
        ax.plot([xf - 8.0, xf - 5.0], [80.5, 80.5], color=COLOR_CONDUCTOR, linewidth=2.0)

        # Cadena derecha (vano de salida)
        ax.plot([xf + 0.5, xf + 5.0], [80.5, 80.5], color=COLOR_INSULATOR, linewidth=3.5)
        ax.plot(xf + 5.0, 80.5, marker='>', markersize=5, color=COLOR_STEEL)
        ax.plot([xf + 5.0, xf + 8.0], [80.5, 80.5], color=COLOR_CONDUCTOR, linewidth=2.0)

        # Puente de derivación / Bypass (catenaria colgante)
        arc_x = [xf - 5.0, xf, xf + 5.0]
        arc_y = [80.5, 74.0, 80.5]
        ax.plot(arc_x, arc_y, color=COLOR_CONDUCTOR, linewidth=1.8, linestyle='--')

    ax.text(28, 72.8, "Puente de Paso (Bypass)", ha='center', fontsize=5.0, color=COLOR_CONDUCTOR, fontweight='bold')

    # Doble Retenida Pesada (anclaje bidireccional)
    # Retenida Izquierda
    ax.plot([28, 11], [78, 18], color=COLOR_GUY, linewidth=2.0)
    ax.plot(19.5, 48.0, marker='o', markersize=5, color='#F59E0B')
    # Retenida Derecha
    ax.plot([28, 51], [78, 18], color=COLOR_GUY, linewidth=2.0)
    ax.plot(39.5, 48.0, marker='o', markersize=5, color='#F59E0B')
    ax.plot([47, 51], [27, 18], color='#EAB308', linewidth=3.5)

    # Cotas
    dibujar_cota_h(ax, 16, 40, 83.5, "Doble Cruceta 2.00 m")
    dibujar_cota_v(ax, 3, 18, 6.0, "1.80 m")
    dibujar_cota_v(ax, 18, 83, 6.0, "11.20 m")
    dibujar_cota_v(ax, 3, 83, 2.5, "Total = 13.00 m")

    # Llamadas
    dibujar_llamada(ax, (33.0, 80.5), (46, 83), "Cadena Polimérica 15 kV / 70 kN", num_item=1)
    dibujar_llamada(ax, (16.0, 79.5), (9, 79), "Doble Cruceta L 100x100x6.4 mm", num_item=2)
    dibujar_llamada(ax, (28.0, 50.0), (38, 62), "Poste C.A.C. 13m / 400 daN (ó 600)", num_item=3)
    dibujar_llamada(ax, (28.0, 74.0), (12, 70), "Grapa de Anclaje Tipo Pistola", num_item=4)

    # Tabla de materiales
    items = [
        (1, 1, "und", "Poste de concreto armado centrifugado CAC 13m / 400 daN (ó 13m/600)"),
        (2, 2, "und", "Cruceta simétrica de perfil angular L F°G° 100x100x6.4 x 2000 mm"),
        (3, 4, "und", "Pletina arriostre F°G° 50x6.4 x 900 mm con pernos 5/8\""),
        (4, 6, "und", "Aislador de suspensión / retención polimérico 15 kV / 70 kN"),
        (5, 6, "und", "Grapa de retención tipo pistola de Al para conductor AAAC 35 mm²"),
        (6, 6, "und", "Grillete de anclaje de acero forjado galvanizado 5/8\""),
        (7, 4, "und", "Perno espaciador de F°G° 5/8\" x 12\" con tuercas y contratuercas"),
        (8, 2, "est", "Retenida mecánica pesada cable Siemens Martin 5/16\""),
        (9, 2, "und", "Aislador de tracción tipo nuez ANSI 54-1 a H >= 3.0 m"),
        (10, 2, "und", "Varilla de anclaje F°G° 3/4\"x2.4m c/guardacabo y bloque CAV 0.6m"),
        (11, 1, "est", "Cimentación ciclópea solera 0.9x0.9x1.8 m (f'c=140 kg/cm²)")
    ]
    y_table_bot = dibujar_tabla_materiales(ax, 65.5, 89.0, 31.5, items, "PLANILLA DE MATERIALES NORMALIZADOS PR-3")

    notas = [
        "Estructura aplicable a anclajes, cruces de ríos, fin de línea y ángulos alpha > 30°.",
        "En el cruce fluvial del Río Chinchalamani (110 m de vano) se emplea poste CAC 13m/600 daN.",
        "Los aisladores poliméricos garantizan línea de fuga >= 31 mm/kV para alta precipitación.",
        "La retenida pesada soporta una carga de tiro unilateral de hasta 2,200 daN.",
        "Conforme a Norma R.D. N° 024-2003-EM/DGE - Lámina 020."
    ]
    dibujar_bloque_notas(ax, 65.5, y_table_bot - 2.0, 31.5, notas)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    fig.savefig(out_file, format='png', dpi=300)
    plt.close(fig)
    print(f"[OK] Generado vector_pr3.png en: {out_file}")

# =========================================================================
# 4. SUBESTACIÓN AÉREA BIPOSTE SAB (50 kVA / 100 kVA)
# =========================================================================
def generar_vector_sab(out_file):
    fig, ax = plt.subplots(figsize=(11.69, 8.27), dpi=300)
    dibujar_marco_base(ax, "SAB", "SUBESTACIÓN AÉREA BIPOSTE SAB (50 / 100 kVA, 10/0.38-0.22 kV)", "R.D. N° 024-2003-EM/DGE — LÁMINA 064")

    # Biposte: Poste 1 en X=22, Poste 2 en X=38 (distancia entre ejes 2.0 m a escala)
    ax.plot([6, 54], [16, 16], color=COLOR_GROUND, linewidth=2.0)
    ax.text(8, 17, "N.T. ±0.00", fontsize=5.8, fontweight='bold', color=COLOR_GROUND)

    for xp in [22.0, 38.0]:
        fnd = patches.Rectangle((xp - 4, 2), 8, 14, facecolor='#CBD5E1', edgecolor='#475569', linewidth=1.0, hatch='//')
        ax.add_patch(fnd)
        poly_p = Polygon([(xp - 1.8, 16), (xp - 1.2, 83), (xp + 1.2, 83), (xp + 1.8, 16)],
                         facecolor='#94A3B8', edgecolor=COLOR_POLE, linewidth=1.4)
        ax.add_patch(poly_p)

    # Nivel Superior: Cruceta de Seccionadores Cut-Out y Pararrayos a Y=79
    cruz_sup = patches.Rectangle((16, 78.5), 28, 1.8, facecolor=COLOR_STEEL, edgecolor='#0F172A', linewidth=1.2)
    ax.add_patch(cruz_sup)

    # Cortacircuitos fusibles Cut-Out (15 kV, 100 A) en X=25, 30, 35
    for xf in [25.0, 30.0, 35.0]:
        # Aislador soporte
        ax.plot([xf, xf], [78.5, 75.5], color=COLOR_INSULATOR, linewidth=3.0)
        # Tubo portafusible inclinado
        ax.plot([xf, xf + 1.5], [75.5, 72.5], color='#F59E0B', linewidth=2.0)
        # Pararrayo ZnO adyacente
        ax.plot([xf - 1.5, xf - 1.5], [78.5, 75.0], color='#10B981', linewidth=2.5)

    ax.text(18, 76.0, "Pararrayos ZnO\n12 kV / 10 kA", ha='right', fontsize=4.8, color='#047857', fontweight='bold')
    ax.text(42, 74.0, "Cut-Out Fusible\n15 kV / 100 A", ha='left', fontsize=4.8, color='#B45309', fontweight='bold')

    # Plataforma de Transformador a H=3.50 m (Y=38 en escala dibujo)
    plat = patches.Rectangle((18, 37.0), 24, 2.0, facecolor=COLOR_STEEL, edgecolor='#0F172A', linewidth=1.4)
    ax.add_patch(plat)
    ax.plot([18, 18], [37, 34], color=COLOR_STEEL, linewidth=2.0)
    ax.plot([42, 42], [37, 34], color=COLOR_STEEL, linewidth=2.0)

    # Cuba del Transformador Trifásico (50 kVA / 100 kVA)
    trafo = patches.Rectangle((25, 39.0), 10, 12, facecolor='#475569', edgecolor='#0F172A', linewidth=1.4)
    ax.add_patch(trafo)
    # Aletas de refrigeración
    for ya in range(41, 49, 2):
        ax.plot([23.5, 25.0], [ya, ya], color='#64748B', linewidth=1.5)
        ax.plot([35.0, 36.5], [ya, ya], color='#64748B', linewidth=1.5)
    # Pasatapas MT superiores
    for xp in [27.0, 30.0, 33.0]:
        ax.plot([xp, xp], [51.0, 54.0], color=COLOR_INSULATOR, linewidth=2.8)
        ax.plot(xp, 54.0, marker='^', markersize=4, color='#DC2626')
        # Conexión flexible desde seccionadores
        ax.plot([xp, xp], [54.0, 72.5], color=COLOR_CONDUCTOR, linewidth=1.0, linestyle=':')

    ax.text(30, 44.5, "TRANSFORMADOR\n50 / 100 kVA\n10 / 0.38-0.22 kV", ha='center', va='center',
            fontsize=5.2, fontweight='bold', color='#FFFFFF')

    # Tablero de Distribución BT adosado a poste derecho a H=1.80 m (Y=26)
    tablero = patches.Rectangle((39.5, 24.0), 5.5, 8.0, facecolor='#334155', edgecolor='#F59E0B', linewidth=1.2)
    ax.add_patch(tablero)
    ax.text(42.25, 28.0, "TABLERO\nBT IP54", ha='center', va='center', fontsize=4.8, fontweight='bold', color='#F59E0B')

    # Sistema de Puesta a Tierra PAT (Doble pozo: MT pararrayos y BT neutro)
    ax.plot([22, 12], [37, 16], color=COLOR_COPPER, linewidth=1.5)
    ax.plot([12, 12], [16, 5], color=COLOR_COPPER, linewidth=2.0)
    p_pat1 = patches.Circle((12, 5), radius=1.5, facecolor='#FEF08A', edgecolor=COLOR_COPPER, linewidth=1.0)
    ax.add_patch(p_pat1)
    ax.text(12, 2.5, "PAT MT <= 10 Ohm", ha='center', fontsize=5.0, fontweight='bold', color=COLOR_COPPER)

    ax.plot([42, 48], [24, 16], color=COLOR_COPPER, linewidth=1.5)
    ax.plot([48, 48], [16, 5], color=COLOR_COPPER, linewidth=2.0)
    p_pat2 = patches.Circle((48, 5), radius=1.5, facecolor='#FEF08A', edgecolor=COLOR_COPPER, linewidth=1.0)
    ax.add_patch(p_pat2)
    ax.text(48, 2.5, "PAT BT <= 5 Ohm", ha='center', fontsize=5.0, fontweight='bold', color=COLOR_COPPER)

    # Cotas
    dibujar_cota_h(ax, 22, 38, 14.0, "Distancia entre ejes = 2.00 m")
    dibujar_cota_v(ax, 16, 37, 16.0, "Plataforma H = 3.50 m")
    dibujar_cota_v(ax, 16, 83, 16.0, "H_libre = 11.20 m")

    # Llamadas
    dibujar_llamada(ax, (30, 52.0), (12, 58), "Transformador Trifásico Dyn5", num_item=1)
    dibujar_llamada(ax, (30, 75.0), (12, 72), "Seccionador Cut-Out 15 kV", num_item=2)
    dibujar_llamada(ax, (42, 28.0), (52, 30), "Tablero BT Distribución", num_item=3)
    dibujar_llamada(ax, (30, 38.0), (52, 42), "Plataforma Soporte UPN 120", num_item=4)

    # Tabla de materiales
    items = [
        (1, 2, "und", "Poste de concreto armado centrifugado CAC 13m / 400 daN"),
        (2, 1, "und", "Transformador trifásico 50 kVA / 100 kVA, 10/0.38-0.22 kV Dyn5"),
        (3, 1, "jgo", "Plataforma de soporte de transformador vigas perfil UPN 120 x 2.4 m"),
        (4, 3, "und", "Cortacircuito fusible tipo Cut-Out 15 kV / 100 A, BIL 110 kV"),
        (5, 3, "und", "Pararrayo polimérico de óxido de zinc (ZnO) 12 kV / 10 kA"),
        (6, 1, "und", "Tablero de distribución BT adosado IP54 con totalizador e interruptores"),
        (7, 1, "jgo", "Cruceta simétrica para equipos MT de L F°G° 75x75x6.4 x 2.4 m"),
        (8, 2, "pozo", "Pozo de puesta a tierra PAT (cobre 35 mm², Copperweld 5/8\"x2.4m)"),
        (9, 1, "jgo", "Conductor de cobre para bajada y puentes MT y BT"),
        (10, 2, "est", "Cimentación ciclópea soleras de concreto 0.9x0.9x1.8 m")
    ]
    y_table_bot = dibujar_tabla_materiales(ax, 65.5, 89.0, 31.5, items, "PLANILLA DE MATERIALES SUBESTACIÓN SAB")

    notas = [
        "Aplica a SED-01 (50 kVA), SED-02 (100 kVA) y SED-03 (100 kVA).",
        "Distancia vertical mínima entre plataforma y suelo: 3.50 m según CNE Suministro.",
        "Resistencia de PAT MT (pararrayos/cuba): R <= 10 Ohmios obligatoria.",
        "Resistencia de PAT BT (neutro secundario): R <= 5 Ohmios según Regla 060 CNE.",
        "Conforme a Norma R.D. N° 024-2003-EM/DGE - Lámina 064."
    ]
    dibujar_bloque_notas(ax, 65.5, y_table_bot - 2.0, 31.5, notas)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    fig.savefig(out_file, format='png', dpi=300)
    plt.close(fig)
    print(f"[OK] Generado vector_sab.png en: {out_file}")

# =========================================================================
# 5. ESTRUCTURA E-1: RED SECUNDARIA CAAI Y ALUMBRADO PÚBLICO
# =========================================================================
def generar_vector_e1(out_file):
    fig, ax = plt.subplots(figsize=(11.69, 8.27), dpi=300)
    dibujar_marco_base(ax, "E-1", "ESTRUCTURA DE BAJA TENSIÓN CAAI Y ALUMBRADO PÚBLICO", "R.D. N° 023-2003-EM-DGE — LÁMINA 001")

    # Poste CAC 8m/9m en X=30
    ax.plot([12, 56], [18, 18], color=COLOR_GROUND, linewidth=2.0)
    ax.text(14, 19, "N.T. ±0.00", fontsize=5.8, fontweight='bold', color=COLOR_GROUND)

    fnd = patches.Rectangle((26, 6), 8, 12, facecolor='#CBD5E1', edgecolor='#475569', linewidth=1.0, hatch='//')
    ax.add_patch(fnd)

    poly_p = Polygon([(28.5, 18), (29.1, 78), (30.9, 78), (31.5, 18)],
                     facecolor='#94A3B8', edgecolor=COLOR_POLE, linewidth=1.4)
    ax.add_patch(poly_p)

    # Brazo Pastoral de Alumbrado Público a H=7.0 m (Y=72)
    # Tubo curvado de acero F°G° 1 1/2" x 1.50 m
    pts_pastoral = [(30.0, 72.0), (33.0, 75.0), (39.0, 75.5), (42.0, 74.0)]
    ax.plot([p[0] for p in pts_pastoral], [p[1] for p in pts_pastoral], color=COLOR_STEEL, linewidth=2.5)
    # Abrazadera en poste
    ax.plot([28.5, 31.5], [72.0, 72.0], color='#0F172A', linewidth=3.0)

    # Luminaria LED 50 W IP66 con fotocélula
    lum = patches.Polygon([(41.0, 74.0), (44.5, 74.5), (44.0, 72.5), (40.5, 72.5)],
                          facecolor='#0284C7', edgecolor='#0369A1', linewidth=1.0)
    ax.add_patch(lum)
    # Fotocélula superior
    ax.plot(42.5, 74.8, marker='o', markersize=3.5, color='#F59E0B')
    # Haz de luz divergente punteado
    ax.plot([40.5, 35.0], [72.5, 45.0], color='#FBBF24', linewidth=1.0, linestyle=':')
    ax.plot([44.0, 52.0], [72.5, 45.0], color='#FBBF24', linewidth=1.0, linestyle=':')
    ax.text(43.5, 76.5, "Luminaria LED 50 W\nIP66 c/Fotocélula", fontsize=5.0, color='#0284C7', fontweight='bold')

    # Soporte de Red Autoportante CAAI a H=6.0 m (Y=64)
    # Abrazadera partida y grapa de suspensión termoplástica
    ax.plot([28.5, 31.5], [64.0, 64.0], color='#0F172A', linewidth=3.0)
    ax.plot([30.0, 33.0], [64.0, 64.0], color=COLOR_STEEL, linewidth=2.0)
    # Haz de conductores trenzados CAAI
    ax.plot([22.0, 38.0], [64.0, 64.0], color='#10B981', linewidth=4.0)
    # Detalle de fases y neutro portante
    ax.text(22.0, 66.0, "Red Troncal CAAI\n3x35 + 1x16 + NA25 mm²", ha='center', fontsize=5.0, color='#047857', fontweight='bold')

    # Derivación a caja de acometida
    ax.plot([33.0, 22.0], [64.0, 48.0], color='#0284C7', linewidth=1.5, linestyle='--')
    ax.text(20.0, 50.0, "Acometida Domiciliaria\nSET 2x4 mm²", ha='right', fontsize=4.8, color='#0284C7')

    # Cotas
    dibujar_cota_v(ax, 6, 18, 22.0, "1.40 m")
    dibujar_cota_v(ax, 18, 64, 22.0, "H_red = 6.00 m")
    dibujar_cota_v(ax, 18, 74, 18.0, "H_lum = 7.00 m")
    dibujar_cota_v(ax, 6, 78, 14.0, "Total CAC = 9.00 m")

    # Llamadas
    dibujar_llamada(ax, (42.5, 73.5), (50, 73), "Luminaria LED 50 W IP66", num_item=1)
    dibujar_llamada(ax, (35.0, 75.0), (22, 75), "Pastoral F°G° 1 1/2\" x 1.5 m", num_item=2)
    dibujar_llamada(ax, (33.0, 64.0), (46, 62), "Grapa de Suspensión CAAI", num_item=3)
    dibujar_llamada(ax, (30.0, 40.0), (42, 40), "Poste C.A.C. 9m / 300 daN", num_item=4)

    # Tabla de materiales
    items = [
        (1, 1, "und", "Poste de concreto armado centrifugado CAC 9m / 300 daN (ó 8m/200 daN)"),
        (2, 1, "und", "Pastoral de tubo de acero galvanizado F°G° 1 1/2\" x 1.50 m"),
        (3, 1, "jgo", "Abrazadera platina F°G° de 2 pernos para fijación de pastoral"),
        (4, 1, "und", "Luminaria LED integrada 50 W, 220 V, IP66, flujo >= 6,500 lm"),
        (5, 1, "und", "Fotocélula electrónica omnidireccional para encendido crepuscular"),
        (6, 1, "jgo", "Grapa de suspensión termoplástica para neutro portante NA 25 mm²"),
        (7, 1, "jgo", "Abrazadera partida F°G° de 1 perno para soporte de red BT"),
        (8, 1, "est", "Cimentación de concreto ciclópea solera 0.60 x 0.60 x 1.40 m")
    ]
    y_table_bot = dibujar_tabla_materiales(ax, 65.5, 89.0, 31.5, items, "PLANILLA DE MATERIALES E-1 / AP")

    notas = [
        "Aplica a los 243 apoyos de distribución secundaria y 166 luminarias LED urbanas.",
        "Altura de montaje de luminaria de alumbrado público: 7.00 m sobre nivel de calzada.",
        "Altura libre del haz autoportante CAAI en cruce de calzada: >= 5.50 m (CNE Suministro).",
        "Conforme a Normas R.D. N° 023-2003-EM-DGE y R.D. N° 017-2003-EM/DGE."
    ]
    dibujar_bloque_notas(ax, 65.5, y_table_bot - 2.0, 31.5, notas)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    fig.savefig(out_file, format='png', dpi=300)
    plt.close(fig)
    print(f"[OK] Generado vector_e1.png en: {out_file}")

# =========================================================================
# 6. RETENIDA INCLINADA NORMALIZADA CNE REGLA 261
# =========================================================================
def generar_vector_retenida(out_file):
    fig, ax = plt.subplots(figsize=(11.69, 8.27), dpi=300)
    dibujar_marco_base(ax, "RET-INC", "RETENIDA MECÁNICA INCLINADA NORMALIZADA (CNE REGLA 261)", "R.D. N° 024-2003-EM/DGE LÁM. 074 / R.D. N° 023-2003-EM-DGE LÁM. 014")

    # Terreno natural
    ax.plot([6, 62], [22, 22], color=COLOR_GROUND, linewidth=2.0)
    ax.text(8, 23, "N.T. ±0.00 (Nivel de Suelo)", fontsize=5.8, fontweight='bold', color=COLOR_GROUND)

    # Poste en X=16
    poly_p = Polygon([(14.8, 22), (15.2, 85), (16.8, 85), (17.2, 22)],
                     facecolor='#94A3B8', edgecolor=COLOR_POLE, linewidth=1.4)
    ax.add_patch(poly_p)
    # Empotramiento
    poly_emp = Polygon([(14.5, 8), (14.8, 22), (17.2, 22), (17.5, 8)],
                       facecolor='#64748B', edgecolor=COLOR_POLE, linewidth=1.0, linestyle='--')
    ax.add_patch(poly_emp)

    # Abrazadera de retenida en poste a H=9.5m (Y=78)
    ax.plot([14.5, 17.5], [78, 78], color='#0F172A', linewidth=3.5)
    # Perno de ojo y guardacabo
    ax.plot(17.5, 78, marker='o', markersize=4, color='#F59E0B')

    # Cable de acero galvanizado Siemens Martin 5/16" inclinado a 45°
    # Punto en poste: (17.5, 78), Punto en suelo: (48, 22) -> Longitud aprox 43 unds
    ax.plot([17.5, 48.0], [78.0, 22.0], color=COLOR_GUY, linewidth=2.5)

    # 3 Grapas prensacables Crosby superiores
    for ug in [0.92, 0.88, 0.84]:
        xg = 17.5 + (48.0 - 17.5) * (1 - ug)
        yg = 78.0 + (22.0 - 78.0) * (1 - ug)
        ax.plot(xg, yg, marker='s', markersize=3.5, color='#0F172A')

    # Aislador de porcelana de tracción tipo nuez ANSI 54-1 a H >= 3.0 m de suelo (Y=42)
    # 42 = 22 + 20 -> aprox 3.2 m sobre suelo
    x_nuez = 17.5 + (48.0 - 17.5) * (78.0 - 42.0) / (78.0 - 22.0)
    aisl_nuez = patches.Ellipse((x_nuez, 42.0), width=3.5, height=2.2, angle=-45,
                                facecolor='#F59E0B', edgecolor='#78350F', linewidth=1.2)
    ax.add_patch(aisl_nuez)
    ax.text(x_nuez + 2.5, 43.5, "Aislador Tipo Nuez ANSI 54-1\n(H >= 3.00 m obligatorio)",
            fontsize=5.5, fontweight='bold', color='#B45309')

    # Tubo protector de PVC amarillo de 1 1/2" x 1.80 m (desde suelo hasta Y=34)
    x_tubo = 17.5 + (48.0 - 17.5) * (78.0 - 34.0) / (78.0 - 22.0)
    ax.plot([x_tubo, 48.0], [34.0, 22.0], color='#EAB308', linewidth=4.5)
    # Bandas reflectivas
    for ub in [0.25, 0.50, 0.75]:
        xb = 48.0 - (48.0 - x_tubo) * ub
        yb = 22.0 + (34.0 - 22.0) * ub
        ax.plot(xb, yb, marker='|', markersize=6, color='#DC2626')
    ax.text(49.0, 28.0, "Protector PVC 1.80 m\ncon franjas reflectivas", fontsize=5.0, color='#A16207', fontweight='bold')

    # Varilla de anclaje F°G° 5/8" x 2.0 m y bloque enterrado a h=1.80 m (Y=8)
    ax.plot([48.0, 54.0], [22.0, 10.0], color=COLOR_STEEL, linewidth=2.5)
    # Guardacabo inferior y 3 grapas
    ax.plot(48.0, 22.0, marker='o', markersize=4, color='#F59E0B')

    # Bloque de concreto ciclópeo CAV 0.50 x 0.50 x 0.20 m
    blk = patches.Rectangle((51.0, 5.0), 7.0, 4.5, facecolor='#64748B', edgecolor='#0F172A', linewidth=1.2, hatch='//')
    ax.add_patch(blk)
    ax.text(54.5, 2.5, "Bloque CAV 0.50x0.50x0.20 m\n(Empotramiento h = 1.80 m)", ha='center', fontsize=5.2, color=COLOR_NOTE)

    # Cotas
    dibujar_cota_h(ax, 16.0, 48.0, 16.0, "Separación horizontal d = 5.00 a 7.00 m (Ángulo 45°)")
    dibujar_cota_v(ax, 22.0, 42.0, 31.0, "H >= 3.00 m")
    dibujar_cota_v(ax, 8.0, 22.0, 60.0, "Profundidad h = 1.80 m")

    # Llamadas
    dibujar_llamada(ax, (17.5, 78.0), (8, 78), "Abrazadera de Retenida F°G°", num_item=1)
    dibujar_llamada(ax, (26.0, 62.0), (38, 68), "Cable Siemens Martin 5/16\"", num_item=2)
    dibujar_llamada(ax, (x_nuez, 42.0), (18, 42), "Aislador de Tracción Nuez", num_item=3)
    dibujar_llamada(ax, (46.0, 26.0), (32, 26), "Guarda Protectora PVC", num_item=4)
    dibujar_llamada(ax, (54.5, 7.5), (38, 10), "Bloque Anclaje CAV", num_item=5)

    # Tabla de materiales
    items = [
        (1, 1, "und", "Abrazadera platina F°G° 3\"x1/4\" c/perno de ojo 5/8\""),
        (2, 18, "m", "Cable de acero grado Siemens Martin 5/16\" (rotura >= 35 kN)"),
        (3, 1, "und", "Aislador de porcelana de tracción tipo nuez ANSI 54-1"),
        (4, 6, "und", "Grapas prensacables tipo Crosby forjadas galvanizadas 5/16\""),
        (5, 2, "und", "Guardacabo de acero forjado galvanizado de 5/16\""),
        (6, 1, "und", "Varilla de anclaje F°G° 5/8\" x 2.00 m con ojal guardacabo"),
        (7, 1, "und", "Tubo protector de PVC rígido amarillo 1 1/2\" x 1.80 m reflectivo"),
        (8, 1, "und", "Bloque de concreto armado prefabricado CAV 0.50x0.50x0.20 m")
    ]
    y_table_bot = dibujar_tabla_materiales(ax, 65.5, 89.0, 31.5, items, "PLANILLA DE MATERIALES RETENIDA NORMALIZADA")

    notas = [
        "Diseñado en cumplimiento estricto de la Regla 261 del CNE Suministro 2011.",
        "El aislador nuez debe situarse a una altura no menor a 3.0 m respecto al suelo.",
        "Se prohíbe el uso de retenidas sin guarda protectora en vías de tránsito peatonal o vehicular.",
        "El relleno de la fosa de anclaje se realiza con tierra compactada mecánicamente en capas de 20 cm.",
        "Conforme a Normas R.D. N° 024-2003-EM/DGE Lám. 074 y R.D. N° 023-2003-EM-DGE Lám. 014."
    ]
    dibujar_bloque_notas(ax, 65.5, y_table_bot - 2.0, 31.5, notas)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    fig.savefig(out_file, format='png', dpi=300)
    plt.close(fig)
    print(f"[OK] Generado vector_retenida.png en: {out_file}")

# =========================================================================
# 7. POZO DE PUESTA A TIERRA PAT VERTICAL NORMALIZADO
# =========================================================================
def generar_vector_pat(out_file):
    fig, ax = plt.subplots(figsize=(11.69, 8.27), dpi=300)
    dibujar_marco_base(ax, "PAT-VERT", "POZO DE PUESTA A TIERRA CON ELECTRODO VERTICAL", "R.D. N° 024-2003-EM/DGE LÁM. 077 — CNE SECCIÓN 060")

    # Terreno natural Y=75
    ax.plot([6, 62], [75, 75], color=COLOR_GROUND, linewidth=2.0)
    ax.text(8, 76.5, "N.T. ±0.00 (Nivel de Suelo Natural)", fontsize=5.8, fontweight='bold', color=COLOR_GROUND)

    # Caja de registro de concreto 0.40 x 0.40 x 0.30 m
    caja = patches.Rectangle((26, 70), 16, 8, facecolor='#E2E8F0', edgecolor='#334155', linewidth=1.5)
    ax.add_patch(caja)
    # Tapa con asa
    tapa = patches.Rectangle((25.5, 76.5), 17, 2.5, facecolor='#CBD5E1', edgecolor='#0F172A', linewidth=1.2)
    ax.add_patch(tapa)
    ax.plot([32, 36], [78.2, 78.2], color='#0F172A', linewidth=2.0) # Asa
    ax.text(34, 73.0, "Caja de Concreto 0.40 x 0.40 m\nRegistro y Borne Telurómetro", ha='center', fontsize=5.0, color='#0F172A', fontweight='bold')

    # Pozo cilíndrico excavado D=0.80 m x H=2.60 m (de Y=75 a Y=10)
    pozo = patches.Rectangle((28, 10), 12, 60, facecolor='#FEF3C7', edgecolor='#D97706', linewidth=1.4, hatch='..')
    ax.add_patch(pozo)

    # Capas de relleno: Bentonita y Tierra vegetal cernida tratada con Thor-Gel
    ax.text(34, 35, "Tierra de chacra cernida\ntratada con Bentonita Sódica\ny dosis química Thor-Gel",
            ha='center', va='center', fontsize=5.5, color='#92400E', fontweight='bold')

    # Electrodo de cobre Copperweld 5/8" x 2.40 m (de Y=72 a Y=15)
    ax.plot([34, 34], [15, 72], color=COLOR_COPPER, linewidth=4.5)
    # Conector de bronce de alta presión tipo AB
    ax.plot(34, 72, marker='s', markersize=6.0, color='#F59E0B', markeredgecolor='#78350F')

    # Conductor de bajada Cu 25/35 mm² dentro de tubo PVC-P 3/4"
    ax.plot([34, 18], [72, 85], color=COLOR_COPPER, linewidth=2.0)
    ax.text(18, 86, "Hacia Transformador / Neutro / Pararrayos\n(Cable Cobre Desnudo 35 mm²)",
            ha='center', fontsize=5.0, color=COLOR_COPPER, fontweight='bold')

    # Cotas
    dibujar_cota_h(ax, 28, 40, 7.0, "Diámetro pozo D = 0.80 m")
    dibujar_cota_v(ax, 10, 75, 43.0, "Profundidad total H = 2.60 m")
    dibujar_cota_v(ax, 15, 72, 23.0, "Electrodo Copperweld L = 2.40 m")

    # Llamadas
    dibujar_llamada(ax, (34, 72), (48, 72), "Conector de Bronce Tipo AB", num_item=1)
    dibujar_llamada(ax, (34, 50), (48, 55), "Electrodo Copperweld 5/8\"x2.4m", num_item=2)
    dibujar_llamada(ax, (34, 25), (48, 30), "Relleno Tratado con Bentonita", num_item=3)
    dibujar_llamada(ax, (34, 77), (16, 75), "Caja Registro y Tapa", num_item=4)

    # Tabla de materiales
    items = [
        (1, 1, "und", "Varilla de puesta a tierra Copperweld 5/8\" x 2.40 m de alta conductividad"),
        (2, 1, "und", "Conector mecánico de bronce fundido tipo AB de 5/8\" para cable 35 mm²"),
        (3, 2, "bol", "Bentonita sódica de alta expansión bolsa de 25 kg"),
        (4, 1, "dosis", "Dosis química electrolítica de sales minerales tipo Thor-Gel / Lab-Gel"),
        (5, 1, "und", "Caja de registro de concreto prefabricado 0.40 x 0.40 m con tapa y asa"),
        (6, 12, "m", "Conductor de cobre electrolítico desnudo recocido de 35 mm² (bajante)"),
        (7, 3, "m", "Tubo de PVC pesado SAP de 3/4\" para protección mecánica del bajante")
    ]
    y_table_bot = dibujar_tabla_materiales(ax, 65.5, 89.0, 31.5, items, "PLANILLA DE MATERIALES POZO PAT")

    notas = [
        "Resistencia de PAT MT (pararrayos y cuba de transformador): R <= 10 Ohmios obligatoria.",
        "Resistencia de PAT BT (neutro de transformador y redes secundarias): R <= 5 Ohmios.",
        "Se prohíbe el uso de tierra con piedras, cascajo o residuos orgánicos en el relleno.",
        "La mezcla de bentonita con agua se realiza en relación 1:5 antes de verter al pozo.",
        "Conforme a Normas R.D. N° 024-2003-EM/DGE Lám. 077 y CNE Suministro Sección 060."
    ]
    dibujar_bloque_notas(ax, 65.5, y_table_bot - 2.0, 31.5, notas)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    fig.savefig(out_file, format='png', dpi=300)
    plt.close(fig)
    print(f"[OK] Generado vector_pat.png en: {out_file}")

# =========================================================================
# 8. ACOMETIDA MONOFÁSICA AÉREA Y CAJA TIPO L-T
# =========================================================================
def generar_vector_acometida(out_file):
    fig, ax = plt.subplots(figsize=(11.69, 8.27), dpi=300)
    dibujar_marco_base(ax, "ACOM-LT", "ACOMETIDA DOMICILIARIA MONOFÁSICA Y CAJA TIPO L-T", "R.D. N° 023-2003-EM-DGE — LÁMINA 007")

    # Terreno natural Y=16
    ax.plot([6, 62], [16, 16], color=COLOR_GROUND, linewidth=2.0)
    ax.text(8, 17, "N.T. ±0.00 (Nivel de Suelo / Vereda)", fontsize=5.8, fontweight='bold', color=COLOR_GROUND)

    # Poste CAC en X=14
    poly_p = Polygon([(12.8, 16), (13.2, 85), (14.8, 85), (15.2, 16)],
                     facecolor='#94A3B8', edgecolor=COLOR_POLE, linewidth=1.4)
    ax.add_patch(poly_p)

    # Red CAAI en poste a H=6.0 m (Y=62)
    ax.plot(14.0, 62.0, marker='o', markersize=6.0, color='#10B981')
    ax.text(14.0, 64.5, "Red CAAI BT", ha='center', fontsize=5.0, color='#047857', fontweight='bold')

    # Fachada de la vivienda en X=50
    muro = patches.Rectangle((50, 16), 10, 70, facecolor='#E2E8F0', edgecolor='#475569', linewidth=1.2)
    ax.add_patch(muro)
    ax.text(55, 78, "FACHADA\nPREDIO", ha='center', fontsize=6.5, fontweight='bold', color='#475569')

    # Mástil de acometida F°G° 1" x 2.50 m en fachada (de Y=55 a Y=75)
    ax.plot([50, 50], [55, 75], color=COLOR_STEEL, linewidth=3.0)
    # Pipeta de entrada hermética
    ax.plot([50, 48.5], [75, 76], color=COLOR_STEEL, linewidth=2.5)

    # Cable de acometida concéntrico SET 2x4 mm² (catenaria aérea desde X=14, Y=62 hasta X=48.5, Y=76)
    caten_x = [14.0, 22.0, 32.0, 42.0, 48.5]
    caten_y = [62.0, 58.5, 61.0, 68.0, 76.0]
    ax.plot(caten_x, caten_y, color=COLOR_CONDUCTOR, linewidth=2.0)
    ax.text(28.0, 56.5, "Vano Aéreo de Acometida\nCable SET 2x4 mm² (L <= 30 m)", ha='center', fontsize=5.2, color='#0284C7', fontweight='bold')

    # Tubo de bajada en fachada desde mástil a caja (de Y=55 a Y=36)
    ax.plot([50, 50], [36, 55], color=COLOR_STEEL, linewidth=2.0)

    # Caja de policarbonato reforzado tipo L-T a H=1.40 m de suelo (Y=32 a Y=40)
    caja_lt = patches.Rectangle((47.5, 30), 5.0, 8.0, facecolor='#0284C7', edgecolor='#0F172A', linewidth=1.2)
    ax.add_patch(caja_lt)
    # Visor transparente policarbonato
    visor = patches.Rectangle((48.5, 33.5), 3.0, 3.5, facecolor='#E0F2FE', edgecolor='#0369A1', linewidth=0.8)
    ax.add_patch(visor)
    ax.text(50.0, 35.2, "kWh", ha='center', va='center', fontsize=5.0, fontweight='bold', color='#0369A1')
    ax.text(45.0, 34.0, "Caja L-T\nH = 1.40 m", ha='right', fontsize=5.0, color='#0284C7', fontweight='bold')

    # Cotas
    dibujar_cota_h(ax, 14.0, 50.0, 20.0, "Longitud del Vano L = 8.0 a 25.0 m")
    dibujar_cota_v(ax, 16.0, 34.0, 44.0, "H = 1.40 m")
    dibujar_cota_v(ax, 16.0, 75.0, 58.0, "H = 5.50 m (Cruce)")

    # Llamadas
    dibujar_llamada(ax, (14.0, 62.0), (6, 62), "Conector Perforación IPC", num_item=1)
    dibujar_llamada(ax, (48.5, 76.0), (38, 78), "Pipeta de Entrada F°G°", num_item=2)
    dibujar_llamada(ax, (50.0, 65.0), (38, 65), "Mástil F°G° 1\" x 2.50 m", num_item=3)
    dibujar_llamada(ax, (47.5, 34.0), (36, 34), "Caja Portamedidor L-T", num_item=4)

    # Tabla de materiales
    items = [
        (1, 2, "und", "Conector de perforación de aislamiento (IPC) bimetálico BT"),
        (2, 1, "und", "Templador termoplástico de acometida c/gancho de anclaje F°G°"),
        (3, 15, "m", "Cable concéntrico bipolar de cobre SET 2x4 mm² 0.6/1 kV"),
        (4, 1, "und", "Mástil de tubo de F°G° de 1\" x 2.50 m con cabeza de servicio"),
        (5, 2, "und", "Abrazadera platina F°G° de 1\" para adosar mástil a muro"),
        (6, 3, "m", "Tubo de PVC pesado SAP 3/4\" para bajada a caja portamedidor"),
        (7, 1, "und", "Caja portamedidor monofásica de policarbonato reforzado tipo L-T"),
        (8, 1, "und", "Medidor estático de energía activa monofásico 220 V homologado"),
        (9, 1, "und", "Interruptor termomagnético bipolar 2 x 16 A curva C, Icu=6 kA")
    ]
    y_table_bot = dibujar_tabla_materiales(ax, 65.5, 89.0, 31.5, items, "PLANILLA DE MATERIALES ACOMETIDA L-T")

    notas = [
        "Aplica a los 587 predios catastrados de Limbani (534 cortas y 53 largas).",
        "Altura normalizada de la base de la caja portamedidor: 1.40 m sobre nivel de vereda.",
        "Caída de tensión máxima admisible en la acometida particular: delta_V <= 1.50%.",
        "Conforme a Normas R.D. N° 023-2003-EM-DGE Lám. 007 y Código Nacional de Electricidad."
    ]
    dibujar_bloque_notas(ax, 65.5, y_table_bot - 2.0, 31.5, notas)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    fig.savefig(out_file, format='png', dpi=300)
    plt.close(fig)
    print(f"[OK] Generado vector_acometida.png en: {out_file}")

# =========================================================================
# FUNCIÓN PRINCIPAL
# =========================================================================
def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "expediente", "figuras", "armados_vector")
    os.makedirs(out_dir, exist_ok=True)

    print("\n" + "="*75)
    print("GENERANDO 8 DIBUJOS TÉCNICOS VECTORIALES DE ALTA RESOLUCIÓN (300 DPI)")
    print("="*75)

    generar_vector_ps3(os.path.join(out_dir, "vector_ps3.png"))
    generar_vector_pa3(os.path.join(out_dir, "vector_pa3.png"))
    generar_vector_pr3(os.path.join(out_dir, "vector_pr3.png"))
    generar_vector_sab(os.path.join(out_dir, "vector_sab.png"))
    generar_vector_e1(os.path.join(out_dir, "vector_e1.png"))
    generar_vector_retenida(os.path.join(out_dir, "vector_retenida.png"))
    generar_vector_pat(os.path.join(out_dir, "vector_pat.png"))
    generar_vector_acometida(os.path.join(out_dir, "vector_acometida.png"))

    # Sincronizar en Catastro_Limbani
    sync_dir = r"C:\Users\51949\Downloads\Catastro_Limbani\expediente_electrico\armados_vector"
    try:
        import shutil
        os.makedirs(sync_dir, exist_ok=True)
        for f in os.listdir(out_dir):
            if f.endswith('.png'):
                shutil.copy2(os.path.join(out_dir, f), os.path.join(sync_dir, f))
        print(f"[OK] Sincronizados 8 diagramas vectoriales en: {sync_dir}")
    except Exception as e:
        print(f"[!] Advertencia al sincronizar: {e}")

    print("="*75)
    print("[OK] TODOS LOS DIBUJOS VECTORIALES GENERADOS Y SINCRONIZADOS EXITOSAMENTE")
    print("="*75 + "\n")

if __name__ == "__main__":
    main()
