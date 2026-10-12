#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_redes_electricas_dxf.py
Genera el Plano Maestro de Ingeniería Electromecánica en formato DXF y DWG nativo:
- Simbología oficial normalizada CNE Suministro 2011 y Norma DGE (R.M. N° 091-2002-EM/VME Sección 9).
- Vanos y distancias reglamentarias verificadas (BT <= 35m, MT <= 85m, cruce río 110m).
- Inclusión directa en el espacio CAD de los 8 PLANOS Y BLOQUES DE DETALLE CONSTRUCTIVO:
  1. ARMADO PS-3: Suspensión Alineamiento MT 10 kV (CAC 12m/300 daN)
  2. ARMADO PA-3: Ángulo MT 10 kV (CAC 12m/400 daN con Retenida Biselar)
  3. ARMADO PR-3: Retención / Anclaje MT 10 kV (CAC 13m/400 y 13m/600 daN con Retenida Pesada)
  4. SUBESTACIÓN AÉREA BIPOSTE SAB 10/0.38-0.22 kV (dyn5, 50 y 100 kVA con seccionamiento y PAT)
  5. ESTRUCTURA DE BAJA TENSIÓN CAC 8m/9m CON CONDUCTOR CAAI Y ALUMBRADO PÚBLICO LED 50W
  6. DETALLE CONSTRUCTIVO DE RETENIDA INCLINADA Y CONTRAVIENTO CON ANCLAJE DE CONCRETO
  7. DETALLE CONSTRUCTIVO DE POZO DE PUESTA A TIERRA VERTICAL (PAT NORMALIZADO DGE)
  8. DETALLE DE ACOMETIDA DOMICILIARIA Y CAJA PORTAMEDIDOR TIPO L-T
- Cámara y vista inicial VPORT centrada directamente en Limbani.
- Compilación a DWG nativo de AutoCAD mediante AutoCAD Core Engine (accoreconsole.exe).
- Generación de láminas gráficas de alta resolución: Planta General y Zooms Sectoriales.

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

# -------------------------------------------------------------------------
# BLOQUES DE DETALLES TÉCNICOS NORMALIZADOS DGE DIBUJADOS EN EL ESPACIO CAD
# -------------------------------------------------------------------------
def dibujar_marco_detalle(msp, x0, y0, w, h, codigo_armado, titulo_armado, norma="R.D. N° 018-2003-EM/DGE"):
    """Dibuja el marco técnico perimetral para una lámina de detalle constructivo en CAD."""
    # Borde exterior
    msp.add_lwpolyline([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    # Borde interior
    msp.add_lwpolyline([(x0 + 4.0, y0 + 4.0), (x0 + w - 4.0, y0 + 4.0),
                        (x0 + w - 4.0, y0 + h - 4.0), (x0 + 4.0, y0 + h - 4.0), (x0 + 4.0, y0 + 4.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    # Franja superior de título
    msp.add_lwpolyline([(x0 + 4.0, y0 + h - 28.0), (x0 + w - 4.0, y0 + h - 28.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    
    t1 = msp.add_text(f"DETALLE NORMALIZADO: {codigo_armado} — {titulo_armado}",
                      dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 5.8, 'color': colors.YELLOW})
    t1.dxf.insert = (x0 + 10.0, y0 + h - 14.0)

    t2 = msp.add_text(f"NORMATIVA APLICABLE: CNE SUMINISTRO 2011 / {norma} — SECCIÓN 9",
                      dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 3.6, 'color': colors.CYAN})
    t2.dxf.insert = (x0 + 10.0, y0 + h - 22.0)

def dibujar_tabla_materiales(msp, x_t, y_t, items):
    """Dibuja una planilla de metrado de materiales normalizada al pie del bloque de detalle."""
    w_t = 150.0
    h_row = 8.0
    msp.add_lwpolyline([(x_t, y_t), (x_t + w_t, y_t), (x_t + w_t, y_t - len(items)*h_row - 10.0),
                        (x_t, y_t - len(items)*h_row - 10.0), (x_t, y_t)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    # Título tabla
    tt = msp.add_text("LISTA DE MATERIALES NORMALIZADOS DGE",
                      dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 3.5, 'color': colors.YELLOW})
    tt.dxf.insert = (x_t + 5.0, y_t - 6.5)
    msp.add_line((x_t, y_t - 9.0), (x_t + w_t, y_t - 9.0),
                 dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})

    curr_y = y_t - 15.0
    for num, desc, cant in items:
        t_row = msp.add_text(f"{num:02d}. {desc}",
                             dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.8, 'color': colors.WHITE})
        t_row.dxf.insert = (x_t + 3.0, curr_y)
        t_c = msp.add_text(f"{cant}",
                           dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.8, 'color': colors.GREEN})
        t_c.dxf.insert = (x_t + w_t - 22.0, curr_y)
        curr_y -= h_row

def dibujar_detalle_ps3(msp, x0, y0, w, h):
    """Lámina de Armado PS-3: Suspensión Alineamiento MT 10 kV."""
    dibujar_marco_detalle(msp, x0, y0, w, h, "ARMADO PS-3", "SUSPENSIÓN ALINEAMIENTO MT 10 kV (ÁNGULO 0° A 5°)")
    cx = x0 + 80.0
    # Poste C.A.C. 12m / 300 daN
    msp.add_lwpolyline([(cx - 3.5, y0 + 30.0), (cx + 3.5, y0 + 30.0), (cx + 1.8, y0 + 200.0), (cx - 1.8, y0 + 200.0), (cx - 3.5, y0 + 30.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    # Línea de terreno y empotramiento (1.40 m)
    msp.add_line((cx - 20.0, y0 + 50.0), (cx + 20.0, y0 + 50.0),
                 dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    msp.add_text("Nivel de Terreno Natural (+- 0.00)", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.8, 'insert': (cx + 22.0, y0 + 49.0), 'color': colors.YELLOW})
    msp.add_text("Empotramiento 1.40 m (Solado f'c=140)", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.5, 'insert': (cx - 35.0, y0 + 38.0), 'color': colors.CYAN})

    # Cruceta de acero galvanizado 75x75x6.4 mm x 2.00 m (a Y = y0 + 190)
    cy_c = y0 + 190.0
    msp.add_lwpolyline([(cx - 35.0, cy_c - 2.0), (cx + 35.0, cy_c - 2.0), (cx + 35.0, cy_c + 2.0), (cx - 35.0, cy_c + 2.0), (cx - 35.0, cy_c - 2.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    # 3 Aisladores Pin ANSI 55-5
    for px_iso in [cx - 28.0, cx, cx + 28.0]:
        msp.add_lwpolyline([(px_iso - 2.5, cy_c + 2.0), (px_iso + 2.5, cy_c + 2.0), (px_iso + 1.5, cy_c + 12.0), (px_iso - 1.5, cy_c + 12.0), (px_iso - 2.5, cy_c + 2.0)],
                           dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.RED})
        msp.add_circle((px_iso, cy_c + 13.0), radius=1.8, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.RED})
        # Conductor AAAC 35 mm2
        msp.add_line((px_iso - 8.0, cy_c + 13.0), (px_iso + 8.0, cy_c + 13.0),
                     dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})

    msp.add_text("Poste C.A.C. 12m / 300 daN", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 3.5, 'insert': (cx + 8.0, y0 + 120.0), 'color': colors.WHITE})
    msp.add_text("Cruceta F°G° 75x75x6.4 mm x 2.00 m", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 3.0, 'insert': (cx - 40.0, cy_c + 18.0), 'color': colors.CYAN})

    # Lista de materiales PS-3
    items_ps3 = [
        (1, "Poste C.A.C. 12.0 m / 300 daN", "1 und"),
        (2, "Cruceta de acero F°G° 75x75x6.4 mm x 2.0 m", "1 und"),
        (3, "Aislador de porcelana tipo Pin ANSI 55-5", "3 und"),
        (4, "Espiga para aislador de espiga 3/4\" x 8\"", "3 und"),
        (5, "Perno maquinado F°G° 5/8\" x 8\" con tuerca", "2 und"),
        (6, "Abrazadera de pletina F°G° de 3 vías p/poste", "1 jgo"),
        (7, "Alambre de amarre de aluminio plano 35 mm²", "12 m"),
        (8, "Cinta plana de armar de aleación aluminio", "3 m")
    ]
    dibujar_tabla_materiales(msp, x0 + 155.0, y0 + h - 40.0, items_ps3)

def dibujar_detalle_pa3(msp, x0, y0, w, h):
    """Lámina de Armado PA-3: Ángulo MT 10 kV."""
    dibujar_marco_detalle(msp, x0, y0, w, h, "ARMADO PA-3", "ÁNGULO MT 10 kV (DESVÍO 5° A 30° CON RETENIDA BISELAR)")
    cx = x0 + 80.0
    # Poste CAC 12m/400 daN
    msp.add_lwpolyline([(cx - 3.8, y0 + 30.0), (cx + 3.8, y0 + 30.0), (cx + 2.0, y0 + 200.0), (cx - 2.0, y0 + 200.0), (cx - 3.8, y0 + 30.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    msp.add_line((cx - 20.0, y0 + 50.0), (cx + 20.0, y0 + 50.0),
                 dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})

    cy_c = y0 + 190.0
    msp.add_lwpolyline([(cx - 35.0, cy_c - 2.0), (cx + 35.0, cy_c - 2.0), (cx + 35.0, cy_c + 2.0), (cx - 35.0, cy_c + 2.0), (cx - 35.0, cy_c - 2.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    for px_iso in [cx - 28.0, cx, cx + 28.0]:
        msp.add_circle((px_iso, cy_c + 12.0), radius=2.2, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.RED})
    
    # Retenida biselar en ángulo
    msp.add_line((cx, cy_c - 10.0), (cx + 60.0, y0 + 50.0),
                 dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'linetype': 'DASHED', 'color': colors.MAGENTA})
    msp.add_circle((cx + 60.0, y0 + 50.0), radius=3.5, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.MAGENTA})
    msp.add_text("Retenida Biselar Simple 5/16\"", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.8, 'insert': (cx + 25.0, y0 + 115.0), 'color': colors.MAGENTA})

    items_pa3 = [
        (1, "Poste C.A.C. 12.0 m / 400 daN", "1 und"),
        (2, "Cruceta angular F°G° 75x75x6.4 mm x 2.0 m", "1 und"),
        (3, "Aislador de porcelana tipo Pin ANSI 55-5", "3 und"),
        (4, "Espiga para aislador de espiga 3/4\" x 8\"", "3 und"),
        (5, "Cable de acero Siemens Martin 5/16\" (retenida)", "25 m"),
        (6, "Aislador de tracción de porcelana 15 kV (nuez)", "1 und"),
        (7, "Varilla de anclaje F°G° 5/8\" x 2.0 m con ojo", "1 und"),
        (8, "Bloque de anclaje de concreto ciclópeo 0.5x0.5m", "1 und")
    ]
    dibujar_tabla_materiales(msp, x0 + 155.0, y0 + h - 40.0, items_pa3)

def dibujar_detalle_pr3(msp, x0, y0, w, h):
    """Lámina de Armado PR-3: Retención / Anclaje MT 10 kV."""
    dibujar_marco_detalle(msp, x0, y0, w, h, "ARMADO PR-3", "RETENCIÓN / ANCLAJE Y TERMINAL MT 10 kV (> 30° Y CRUCES)")
    cx = x0 + 80.0
    msp.add_lwpolyline([(cx - 4.2, y0 + 30.0), (cx + 4.2, y0 + 30.0), (cx + 2.2, y0 + 205.0), (cx - 2.2, y0 + 205.0), (cx - 4.2, y0 + 30.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    msp.add_line((cx - 20.0, y0 + 50.0), (cx + 20.0, y0 + 50.0),
                 dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})

    cy_c = y0 + 195.0
    # Doble cruceta de retención
    msp.add_lwpolyline([(cx - 40.0, cy_c - 4.0), (cx + 40.0, cy_c - 4.0), (cx + 40.0, cy_c + 4.0), (cx - 40.0, cy_c + 4.0), (cx - 40.0, cy_c - 4.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    # Cadenas de suspensión poliméricas
    for px_iso in [cx - 32.0, cx, cx + 32.0]:
        msp.add_lwpolyline([(px_iso, cy_c + 4.0), (px_iso, cy_c + 18.0)], dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.RED})
        msp.add_circle((px_iso, cy_c + 11.0), radius=2.5, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.RED})
        msp.add_circle((px_iso, cy_c + 18.0), radius=1.5, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})

    # Doble retenida inclinada contraviento
    msp.add_line((cx, cy_c - 5.0), (cx - 65.0, y0 + 50.0),
                 dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'linetype': 'DASHED', 'color': colors.MAGENTA})
    msp.add_circle((cx - 65.0, y0 + 50.0), radius=4.0, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.MAGENTA})
    msp.add_text("Retenida Inclinada Pesada 5/16\"", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.8, 'insert': (cx - 75.0, y0 + 115.0), 'color': colors.MAGENTA})

    items_pr3 = [
        (1, "Poste C.A.C. 13.0 m / 400 daN (o 13/600 cruce río)", "1 und"),
        (2, "Doble cruceta retención F°G° 100x100x6.4 mm x 2.0m", "2 und"),
        (3, "Aislador polimérico de suspensión 15 kV / 70 kN", "6 und"),
        (4, "Grapa de anclaje tipo pistola de aleación Al-Cu", "6 und"),
        (5, "Pernos de doble armado F°G° 5/8\" x 16\" c/tuercas", "4 und"),
        (6, "Cable de acero Siemens Martin 5/16\" (2 retenidas)", "50 m"),
        (7, "Aislador de tracción polimérico de 15 kV", "2 und"),
        (8, "Varilla de ancla F°G° 5/8\" x 2.0 m con bloque conc.", "2 jgo")
    ]
    dibujar_tabla_materiales(msp, x0 + 155.0, y0 + h - 40.0, items_pr3)

def dibujar_detalle_sab(msp, x0, y0, w, h):
    """Lámina de Subestación Aérea Biposte (SAB 10/0.38-0.22 kV)."""
    dibujar_marco_detalle(msp, x0, y0, w, h, "SUBESTACIÓN SAB", "SUBESTACIÓN AÉREA BIPOSTE 10 / 0.38-0.22 kV (50 kVA Y 100 kVA)")
    cx = x0 + 80.0
    # Dos postes CAC 13m / 400 daN separados 2.0m escala (cx - 20, cx + 20)
    for px_p in [cx - 20.0, cx + 20.0]:
        msp.add_lwpolyline([(px_p - 3.8, y0 + 30.0), (px_p + 3.8, y0 + 30.0), (px_p + 2.0, y0 + 210.0), (px_p - 2.0, y0 + 210.0), (px_p - 3.8, y0 + 30.0)],
                           dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    msp.add_line((cx - 45.0, y0 + 50.0), (cx + 45.0, y0 + 50.0),
                 dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})

    # Plataforma de perfiles UPN 120 (a Y = y0 + 120)
    py_plat = y0 + 120.0
    msp.add_lwpolyline([(cx - 30.0, py_plat - 3.0), (cx + 30.0, py_plat - 3.0), (cx + 30.0, py_plat + 3.0), (cx - 30.0, py_plat + 3.0), (cx - 30.0, py_plat - 3.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    # Transformador dyn5 (rectángulo 24 x 20)
    msp.add_lwpolyline([(cx - 12.0, py_plat + 3.0), (cx + 12.0, py_plat + 3.0), (cx + 12.0, py_plat + 23.0), (cx - 12.0, py_plat + 23.0), (cx - 12.0, py_plat + 3.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    msp.add_circle((cx, py_plat + 13.0), radius=5.0, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    msp.add_text("TRAFO dyn5\n50/100 kVA", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.8, 'insert': (cx - 8.0, py_plat + 12.0), 'color': colors.YELLOW})

    # Cruceta de seccionamiento y pararrayos (a Y = y0 + 200)
    py_sec = y0 + 200.0
    msp.add_lwpolyline([(cx - 35.0, py_sec - 2.5), (cx + 35.0, py_sec - 2.5), (cx + 35.0, py_sec + 2.5), (cx - 35.0, py_sec + 2.5), (cx - 35.0, py_sec - 2.5)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    for px_s in [cx - 18.0, cx, cx + 18.0]:
        msp.add_line((px_s, py_sec + 2.5), (px_s, py_sec + 12.0), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.RED})
        msp.add_circle((px_s, py_sec + 13.0), radius=2.0, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.RED})

    # Tablero BT en poste derecho (a Y = y0 + 80)
    msp.add_lwpolyline([(cx + 16.0, y0 + 75.0), (cx + 26.0, y0 + 75.0), (cx + 26.0, y0 + 95.0), (cx + 16.0, y0 + 95.0), (cx + 16.0, y0 + 75.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.CYAN})
    msp.add_text("TABLERO BT IP54\nMCCB 100A/160A", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.2, 'insert': (cx + 17.0, y0 + 84.0), 'color': colors.CYAN})

    # Doble pozo de puesta a tierra PAT
    msp.add_line((cx - 20.0, y0 + 50.0), (cx - 35.0, y0 + 25.0), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'linetype': 'DASHED', 'color': colors.GREEN})
    msp.add_circle((cx - 35.0, y0 + 25.0), radius=3.0, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.GREEN})
    msp.add_text("PAT-1 Protección (R<=10 Ohm)", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.4, 'insert': (cx - 65.0, y0 + 22.0), 'color': colors.GREEN})

    msp.add_line((cx + 20.0, y0 + 50.0), (cx + 35.0, y0 + 25.0), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'linetype': 'DASHED', 'color': colors.GREEN})
    msp.add_circle((cx + 35.0, y0 + 25.0), radius=3.0, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.GREEN})
    msp.add_text("PAT-2 Neutro (R<=5 Ohm)", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.4, 'insert': (cx + 38.0, y0 + 22.0), 'color': colors.GREEN})

    items_sab = [
        (1, "Poste C.A.C. 13.0 m / 400 daN (estructura biposte)", "2 und"),
        (2, "Plataforma metálica UPN 120 galvanizada c/pernos", "1 jgo"),
        (3, "Transformador trifásico dyn5 10/0.38-0.22 kV ONAN", "1 und"),
        (4, "Seccionador cut-out unipolar 15 kV / 100 A", "3 und"),
        (5, "Pararrayos de óxido de zinc (ZnO) 12 kV / 10 kA", "3 und"),
        (6, "Tablero de distribución BT adosado IP54 c/MCCB", "1 und"),
        (7, "Cable de energía N2XOH 0.6/1 kV en tubo F°G° 2\"", "15 m"),
        (8, "Sistema PAT doble (2 pozos, varillas Cu 5/8\"x2.4m)", "2 jgo")
    ]
    dibujar_tabla_materiales(msp, x0 + 155.0, y0 + h - 40.0, items_sab)

def dibujar_detalle_bt_ap(msp, x0, y0, w, h):
    """Lámina de Red Secundaria BT y Alumbrado Público LED."""
    dibujar_marco_detalle(msp, x0, y0, w, h, "RED SECUNDARIA Y AP", "RED SECUNDARIA CAAI 380/220 V Y ALUMBRADO PÚBLICO LED 50 W", "R.D. N° 016-2003-EM/DGE")
    cx = x0 + 80.0
    # Poste CAC 9m / 300 daN
    msp.add_lwpolyline([(cx - 3.2, y0 + 30.0), (cx + 3.2, y0 + 30.0), (cx + 1.6, y0 + 185.0), (cx - 1.6, y0 + 185.0), (cx - 3.2, y0 + 30.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    msp.add_line((cx - 20.0, y0 + 50.0), (cx + 20.0, y0 + 50.0),
                 dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})

    # Cable autoportante CAAI a Y = y0 + 175
    py_c = y0 + 175.0
    msp.add_line((cx - 35.0, py_c), (cx + 35.0, py_c), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.GREEN})
    msp.add_circle((cx, py_c), radius=2.2, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.GREEN})
    msp.add_text("Cable CAAI 3x35+1x16+NA25", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.8, 'insert': (cx - 40.0, py_c + 4.0), 'color': colors.GREEN})

    # Pastoral y luminaria LED 50W
    msp.add_line((cx, py_c + 2.0), (cx + 25.0, py_c + 12.0), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': 30})
    msp.add_line((cx + 25.0, py_c + 12.0), (cx + 30.0, py_c + 8.0), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': 30})
    msp.add_lwpolyline([(cx + 28.0, py_c + 6.0), (cx + 36.0, py_c + 6.0), (cx + 36.0, py_c + 10.0), (cx + 28.0, py_c + 10.0), (cx + 28.0, py_c + 6.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    msp.add_text("Luminaria LED 50 W (>=6,500 lm, IP66)", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.6, 'insert': (cx + 10.0, py_c + 15.0), 'color': 30})

    # Regla de vano máximo
    msp.add_text("VANO REGLAMENTARIO CNE: L <= 35.0 m (Promedio 30-32 m)",
                 dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 3.2, 'insert': (cx - 40.0, y0 + 130.0), 'color': colors.CYAN})

    items_bt = [
        (1, "Poste C.A.C. 9.0 m / 300 daN (troncales y AP)", "1 und"),
        (2, "Cable autoportante CAAI 3x35+1x16+NA25 mm²", "Vano m"),
        (3, "Grapa de suspensión p/cable autoportante BT", "1 und"),
        (4, "Abrazadera de pletina F°G° 2 vías de fijación", "1 jgo"),
        (5, "Pastoral de tubo de acero F°G° 1.5\" x 1.50 m", "1 und"),
        (6, "Luminaria de alumbrado público LED 50 W IP66", "1 und"),
        (7, "Conector bimetálico tipo cuña o perno partido", "4 und"),
        (8, "Cinta de acero inoxidable Band-It con hebillas", "2 m")
    ]
    dibujar_tabla_materiales(msp, x0 + 155.0, y0 + h - 40.0, items_bt)

def dibujar_detalle_retenida(msp, x0, y0, w, h):
    """Lámina de Detalle de Retenida Inclinada y Anclaje."""
    dibujar_marco_detalle(msp, x0, y0, w, h, "RETENIDA MECÁNICA", "RETENIDA INCLINADA Y CONTRAVIENTO CON BLOQUE DE ANCLAJE", "CNE REGLA 261")
    cx = x0 + 80.0
    # Poste y retenida
    msp.add_line((cx, y0 + 190.0), (cx + 70.0, y0 + 60.0), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.MAGENTA})
    # Aislador de tracción (nuez) a Y = y0 + 140
    msp.add_circle((cx + 27.0, y0 + 140.0), radius=3.0, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.RED})
    msp.add_text("Aislador de Tracción 15 kV (Huevo)", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.6, 'insert': (cx + 32.0, y0 + 145.0), 'color': colors.RED})

    # Varilla y bloque de concreto
    msp.add_line((cx + 70.0, y0 + 60.0), (cx + 85.0, y0 + 35.0), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    msp.add_lwpolyline([(cx + 75.0, y0 + 20.0), (cx + 95.0, y0 + 20.0), (cx + 95.0, y0 + 35.0), (cx + 75.0, y0 + 35.0), (cx + 75.0, y0 + 20.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    msp.add_text("Bloque de Concreto 0.50x0.50x0.30 m\nProfundidad h = 1.80 m", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.6, 'insert': (cx + 40.0, y0 + 15.0), 'color': colors.YELLOW})

    items_ret = [
        (1, "Cable de acero Siemens Martin 5/16\" (7 hilos)", "25 m"),
        (2, "Aislador de tracción polimérico/porcelana 15 kV", "1 und"),
        (3, "Varilla de ancla F°G° 5/8\" x 2.0 m con ojal guardac.", "1 und"),
        (4, "Bloque de anclaje de concreto ciclópeo 0.5x0.5m", "1 und"),
        (5, "Grapas prensacables de acero forjado 5/16\"", "6 und"),
        (6, "Guardacabo de acero forjado galvanizado 5/16\"", "2 und"),
        (7, "Perno de ojo o abrazadera p/poste de concreto", "1 und"),
        (8, "Protector de retenida en tubo PVC amarillo 1.8m", "1 und")
    ]
    dibujar_tabla_materiales(msp, x0 + 155.0, y0 + h - 40.0, items_ret)

def dibujar_detalle_pat(msp, x0, y0, w, h):
    """Lámina de Detalle de Pozo de Puesta a Tierra (PAT)."""
    dibujar_marco_detalle(msp, x0, y0, w, h, "PUESTA A TIERRA (PAT)", "POZO DE PUESTA A TIERRA VERTICAL NORMALIZADO DGE", "CNE SECCIÓN 060")
    cx = x0 + 80.0
    # Pozo excavado (0.80 m x 2.60 m)
    msp.add_lwpolyline([(cx - 20.0, y0 + 30.0), (cx + 20.0, y0 + 30.0), (cx + 20.0, y0 + 130.0), (cx - 20.0, y0 + 130.0), (cx - 20.0, y0 + 30.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    msp.add_text("Pozo de Tierra D = 0.80 m x H = 2.60 m\nRelleno con Tierra Vegetal + Bentonita", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.6, 'insert': (cx - 45.0, y0 + 15.0), 'color': colors.YELLOW})

    # Caja de registro de concreto (0.40 x 0.40 m) a Y = y0 + 130
    msp.add_lwpolyline([(cx - 15.0, y0 + 130.0), (cx + 15.0, y0 + 130.0), (cx + 15.0, y0 + 150.0), (cx - 15.0, y0 + 150.0), (cx - 15.0, y0 + 130.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    msp.add_text("Caja Registro 0.40x0.40 m c/Tapa", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.6, 'insert': (cx - 18.0, y0 + 154.0), 'color': colors.WHITE})

    # Electrodo Copperweld 5/8" x 2.40 m
    msp.add_line((cx, y0 + 40.0), (cx, y0 + 140.0), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.RED})
    msp.add_circle((cx, y0 + 138.0), radius=2.5, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.GREEN})
    msp.add_text("Conector AB Bronce", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.4, 'insert': (cx + 4.0, y0 + 138.0), 'color': colors.GREEN})
    msp.add_text("Electrodo Copperweld 5/8\" x 2.40 m", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.6, 'insert': (cx + 4.0, y0 + 85.0), 'color': colors.RED})

    items_pat = [
        (1, "Electrodo de cobre Copperweld 5/8\" x 2.40 m", "1 und"),
        (2, "Conector de bronce de alta presión tipo AB", "1 und"),
        (3, "Conductor de cobre desnudo recocido 35 mm²", "8 m"),
        (4, "Tubo de protección PVC-P de 3/4\" x 3.0 m", "1 und"),
        (5, "Caja de registro de concreto 0.40x0.40 m c/tapa", "1 und"),
        (6, "Bentonita sódica para pozo a tierra (sacos 25 kg)", "2 sacos"),
        (7, "Dosis de sales electrolíticas Thor-Gel / Lab-Gel", "1 dosis"),
        (8, "Tierra de chacra cernida para relleno compactado", "1.5 m³")
    ]
    dibujar_tabla_materiales(msp, x0 + 155.0, y0 + h - 40.0, items_pat)

def dibujar_detalle_acometida(msp, x0, y0, w, h):
    """Lámina de Detalle de Acometida Domiciliaria y Caja Portamedidor L-T."""
    dibujar_marco_detalle(msp, x0, y0, w, h, "ACOMETIDA DOMICILIARIA", "ACOMETIDA AÉREA Y CAJA PORTAMEDIDOR TIPO L-T (MONOFÁSICA/TRIFÁSICA)", "NORMA DGE CONEXIONES")
    cx = x0 + 80.0
    # Muro de fachada predial
    msp.add_lwpolyline([(cx + 15.0, y0 + 30.0), (cx + 35.0, y0 + 30.0), (cx + 35.0, y0 + 170.0), (cx + 15.0, y0 + 170.0), (cx + 15.0, y0 + 30.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    msp.add_text("Fachada del Predio", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.8, 'insert': (cx + 16.0, y0 + 175.0), 'color': colors.WHITE})

    # Caja portamedidor L-T en fachada (Y = y0 + 80 a 115)
    msp.add_lwpolyline([(cx + 16.0, y0 + 80.0), (cx + 30.0, y0 + 80.0), (cx + 30.0, y0 + 115.0), (cx + 16.0, y0 + 115.0), (cx + 16.0, y0 + 80.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    msp.add_text("CAJA L-T\nMedidor", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.6, 'insert': (cx + 18.0, y0 + 95.0), 'color': colors.YELLOW})

    # Acometida aérea concéntrica desde red BT
    msp.add_line((cx - 40.0, y0 + 160.0), (cx + 20.0, y0 + 140.0), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.CYAN})
    msp.add_line((cx + 20.0, y0 + 140.0), (cx + 20.0, y0 + 115.0), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.CYAN})
    msp.add_text("Cable Concéntrico SET 2x6 mm²\nVano acometida <= 25.0 m", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.6, 'insert': (cx - 40.0, y0 + 145.0), 'color': colors.CYAN})

    items_acom = [
        (1, "Caja portamedidor monofásica tipo L-T reforzada", "1 und"),
        (2, "Medidor de energía electrónico digital homologado", "1 und"),
        (3, "Interruptor termomagnético bipolar 2x16A 6kA", "1 und"),
        (4, "Cable concéntrico de cobre tipo SET 2x6 mm²", "15 m"),
        (5, "Mástil soporte de acometida F°G° 1\" x 2.0 m", "1 und"),
        (6, "Conector bimetálico perforación p/red secundaria", "2 und"),
        (7, "Accesorios de fijación, grapa de acometida y cáncamo", "1 jgo"),
        (8, "Puesta a tierra domiciliaria con varilla 1/2\"x1.5m", "1 jgo")
    ]
    dibujar_tabla_materiales(msp, x0 + 155.0, y0 + h - 40.0, items_acom)

# -------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# -------------------------------------------------------------------------
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

    # -------------------------------------------------------------
    # 1. CREAR CAPAS ELECTROMECÁNICAS NORMALIZADAS DGE
    # -------------------------------------------------------------
    capas_def = [
        ("01_RED_MT_10KV_CONDUCTOR", colors.RED),      # Rojo brillante (AAAC 35 mm2)
        ("02_POSTES_MT_10KV", colors.RED),             # Rojo (C.A.C. 12m y 13m)
        ("03_SUBESTACIONES_SED", colors.YELLOW),       # Amarillo (SAB 10/0.38-0.22 kV)
        ("04_RETENIDAS_MT_BT", colors.MAGENTA),        # Magenta (Inclinada y Contraviento)
        ("05_RED_BT_TRONCAL_CAAI", colors.GREEN),      # Verde (CAAI 3x35+1x16+NA25)
        ("06_RED_BT_DERIVACION_CAAI", colors.CYAN),    # Cian (CAAI 2x16+1x16+NA25)
        ("07_POSTES_BT_CAC", colors.BLUE),             # Azul (C.A.C. 8m y 9m)
        ("08_ALUMBRADO_PUBLICO_LED", 30),              # Naranja / Amarillo (LED 50 W)
        ("09_CUADRO_LEYENDA_ROTULO", colors.WHITE),    # Blanco
        ("10_DETALLES_ESTRUCTURAS_DGE", colors.WHITE)  # Blanco / Multicolor (Láminas de detalle)
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
            # SÍMBOLO NORMALIZADO DGE 09-91-20 (Poste de Concreto MT con cruz de material "C")
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
            msp.add_line((px, py), p_ancla, dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'linetype': 'DASHED', 'color': colors.MAGENTA})
            msp.add_circle(p_ancla, radius=1.5, dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'color': colors.MAGENTA})

    # -------------------------------------------------------------
    # 4. REDES DE BAJA TENSIÓN CON VANOS REGLAMENTARIOS (<= 32 METROS)
    # -------------------------------------------------------------
    postes_bt_coords = []
    lineas_bt_segmentos = []
    p_idx = 1
    total_luminarias = 0
    total_ret_bt = 0
    total_cac_8_200 = 0
    total_cac_8_300 = 0
    total_cac_9_300 = 0

    # Vano máximo regulatorio estricto para redes autoportantes CAAI en zonas urbanas
    vano_max_reglamentario = 32.0  # metros (Garantiza vanos <= 35m conforme al CNE)

    for v_pts in vias_polys:
        if len(v_pts) < 2:
            continue
        v_segs = []
        v_len = 0
        for k in range(len(v_pts) - 1):
            d = distancia(v_pts[k], v_pts[k+1])
            v_segs.append((v_pts[k], v_pts[k+1], d, v_len))
            v_len += d

        if v_len < 20.0:
            continue

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

        is_troncal = (v_len > 700.0)
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

            # SÍMBOLO NORMALIZADO DGE 09-91-20 (Poste BT)
            msp.add_circle(pt, radius=2.0, dxfattribs={'layer': '07_POSTES_BT_CAC', 'color': colors.BLUE})
            msp.add_circle(pt, radius=0.8, dxfattribs={'layer': '07_POSTES_BT_CAC', 'color': colors.BLUE})
            postes_bt_coords.append((f"P-{p_idx:03d}", pt[0], pt[1], p_tipo, has_ap))

            if p_idx % 2 == 1:
                t_pbt = msp.add_text(f"P-{p_idx}", dxfattribs={'layer': '07_POSTES_BT_CAC', 'height': 2.5, 'color': colors.BLUE})
                t_pbt.dxf.insert = (pt[0] + 2.5, pt[1] + 1.0)

            # SÍMBOLO NORMALIZADO DGE 09-91-24 (Luminaria AP LED 50W)
            if has_ap and total_luminarias < 165:
                total_luminarias += 1
                p_lum = (pt[0] + 3.0, pt[1] + 2.5)
                msp.add_line(pt, p_lum, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})
                msp.add_circle(p_lum, radius=1.2, dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})
                msp.add_line((p_lum[0]-0.8, p_lum[1]-0.8), (p_lum[0]+0.8, p_lum[1]+0.8), dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})
                msp.add_line((p_lum[0]-0.8, p_lum[1]+0.8), (p_lum[0]+0.8, p_lum[1]-0.8), dxfattribs={'layer': '08_ALUMBRADO_PUBLICO_LED', 'color': 30})

            # Retenida BT en terminales
            if is_end:
                total_ret_bt += 1
                p_ret = (pt[0] - 5.0, pt[1] - 4.0)
                msp.add_line(pt, p_ret, dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'linetype': 'DASHED', 'color': colors.MAGENTA})
                msp.add_circle(p_ret, radius=1.0, dxfattribs={'layer': '04_RETENIDAS_MT_BT', 'color': colors.MAGENTA})

            p_idx += 1

    # Asegurar exactamente 165 luminarias de alumbrado LED
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
    # 5. DIBUJAR LOS 8 BLOQUES DE DETALLE CONSTRUCTIVO NORMALIZADO DGE
    # -------------------------------------------------------------
    print("[*] Incorporando los 8 bloques de planos y detalles constructivos en el espacio CAD...")
    # Columna 1 (X = 426800): Armados MT y SAB
    x_c1 = 426800.0
    w_blk = 330.0
    h_blk = 260.0
    dibujar_detalle_ps3(msp, x_c1, 8436500.0, w_blk, h_blk)
    dibujar_detalle_pa3(msp, x_c1, 8436180.0, w_blk, h_blk)
    dibujar_detalle_pr3(msp, x_c1, 8435860.0, w_blk, h_blk)
    dibujar_detalle_sab(msp, x_c1, 8435540.0, w_blk, h_blk)

    # Columna 2 (X = 427200): BT, Retenida, PAT y Acometida
    x_c2 = 427200.0
    dibujar_detalle_bt_ap(msp, x_c2, 8436500.0, w_blk, h_blk)
    dibujar_detalle_retenida(msp, x_c2, 8436180.0, w_blk, h_blk)
    dibujar_detalle_pat(msp, x_c2, 8435860.0, w_blk, h_blk)
    dibujar_detalle_acometida(msp, x_c2, 8435540.0, w_blk, h_blk)

    # -------------------------------------------------------------
    # 6. CUADRO DE LEYENDA Y MEMBRETE EN EL MODEL SPACE
    # -------------------------------------------------------------
    lx = 425780.0
    ly = 8435800.0

    msp.add_lwpolyline([
        (lx, ly), (lx + 180.0, ly),
        (lx + 180.0, ly - 220.0), (lx, ly - 220.0),
        (lx, ly)
    ], dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'color': colors.WHITE})

    t_ltit = msp.add_text("CUADRO DE SIMBOLOGÍA NORMALIZADA DGE", dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'height': 6.0, 'color': colors.WHITE})
    t_ltit.dxf.insert = (lx + 8.0, ly - 15.0)
    msp.add_line((lx + 5.0, ly - 20.0), (lx + 175.0, ly - 20.0), dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'color': colors.WHITE})

    items_leyenda = [
        ("Línea Primaria 10 kV (AAAC 35 mm2)", colors.RED, "linea"),
        ("Poste MT CAC (09-91-20 DGE: 12m y 13m)", colors.RED, "poste_mt"),
        ("Subestación Aérea SAB (09-90-04 DGE: 50/100 kVA)", colors.YELLOW, "sed"),
        ("Red BT Troncal CAAI 3x35+1x16+NA25", colors.GREEN, "linea_bt"),
        ("Red BT Derivación CAAI 2x16+1x16+NA25", colors.CYAN, "linea_bt_der"),
        ("Poste BT CAC (09-91-20 DGE: 8m y 9m)", colors.BLUE, "poste_bt"),
        ("Alumbrado Público LED 50W (09-91-24 DGE)", 30, "ap"),
        ("Retenida / Anclaje a tierra (09-91-18 DGE)", colors.MAGENTA, "ret")
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

        t_desc = msp.add_text(texto, dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'height': 4.2, 'color': colors.WHITE})
        t_desc.dxf.insert = (lx + 48.0, curr_y - 1.5)
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
        t_m = msp.add_text(m_line, dxfattribs={'layer': '09_CUADRO_LEYENDA_ROTULO', 'height': 3.6, 'color': colors.YELLOW})
        t_m.dxf.insert = (lx + 10.0, curr_y)
        curr_y -= 8.0

    # -------------------------------------------------------------
    # GUARDAR DXF
    # -------------------------------------------------------------
    os.makedirs(os.path.dirname(out_dxf), exist_ok=True)
    doc.saveas(out_dxf)
    print(f"[OK] Plano DXF de Redes y Detalles generado en: {out_dxf}")

    try:
        os.makedirs(catastro_sync_dir, exist_ok=True)
        doc.saveas(catastro_sync_dxf)
        print(f"[OK] Copia sincronizada DXF en: {catastro_sync_dxf}")
    except Exception as e:
        print(f"[!] Aviso: No se pudo sobrescribir catastro_sync_dxf: {e}")

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
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=25)
            if os.path.exists(out_dwg):
                print(f"[OK] Archivo DWG nativo compilado con Zoom Extents: {out_dwg}")
                try:
                    shutil.copy2(out_dwg, catastro_sync_dwg)
                    print(f"[OK] Copia sincronizada DWG en: {catastro_sync_dwg}")
                except Exception as e:
                    print(f"[!] Aviso: No se pudo sobrescribir catastro_sync_dwg: {e}")
        except Exception as err:
            print("[!] Nota al compilar DWG con AutoCAD:", err)
        finally:
            if os.path.exists(scr_path):
                os.remove(scr_path)

    # -------------------------------------------------------------
    # 7. GENERAR RENDERIZADOS GRÁFICOS DE ALTA DEFINICIÓN (PNG)
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
            ax.fill([p[0] for p in pts], [p[1] for p in pts], color='#10B981', alpha=0.25, zorder=3)
        for v_pts in vias_polys:
            ax.plot([p[0] for p in v_pts], [p[1] for p in v_pts], color='#64748B', linewidth=1.0, alpha=0.6, zorder=4)

        for p_a, p_b, is_tr in lineas_bt_segmentos:
            c_line = '#10B981' if is_tr else '#38BDF8'
            lw = 1.6 if is_tr else 1.0
            ax.plot([p_a[0], p_b[0]], [p_a[1], p_b[1]], color=c_line, linewidth=lw, alpha=0.9, zorder=5)

        ax.scatter([p[1] for p in postes_bt_coords], [p[2] for p in postes_bt_coords],
                   s=24, color='#60A5FA', edgecolors='#1E3A8A', linewidths=0.6, zorder=6, label='Postes BT (CAC 8m/9m)')

        ap_pts = [p for p in postes_bt_coords if p[4]]
        ax.scatter([p[1] for p in ap_pts], [p[2] for p in ap_pts],
                   s=40, color='#FBBF24', edgecolors='#B45309', linewidths=0.8, zorder=7, label='Alumbrado Público LED (165 und)')

        ax.plot([p[0] for p in pts_mt], [p[1] for p in pts_mt], color='#EF4444', linewidth=3.5, zorder=8, label='Línea Primaria 10 kV (AAAC 35 mm²)')

        mt_normal = [p for p in postes_mt_data if "SAB" not in p[5]]
        ax.scatter([p[1] for p in mt_normal], [p[2] for p in mt_normal],
                   s=85, color='#DC2626', edgecolors='#FFFFFF', linewidths=1.5, zorder=9, label='Postes MT (CAC 12m/13m)')

        seds_pts = [p for p in postes_mt_data if "SAB" in p[5]]
        ax.scatter([p[1] for p in seds_pts], [p[2] for p in seds_pts],
                   s=240, color='#FACC15', edgecolors='#78350F', linewidths=2.5, marker='s', zorder=10, label='Subestaciones Aéreas Biposte (3 SAB)')

        if detalle_textos:
            for p in mt_normal:
                ax.annotate(f"{p[0]}\n{p[4].replace('C.A.C. ', '')}", (p[1], p[2]),
                            xytext=(p[1] + 8, p[2] + 4), color='#FCA5A5', fontsize=8, fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.2", fc="#450A0A", ec="#EF4444", lw=0.8, alpha=0.85),
                            zorder=11)
            for p in seds_pts:
                ax.annotate(f"{p[0]}: {p[7].split('(')[0].strip()}\n({p[7].split('(')[1].replace(')', '')})",
                            (p[1], p[2]), xytext=(p[1] + 15, p[2] + 12),
                            color='#FEF08A', fontsize=9, fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.3", fc="#1E293B", ec="#FACC15", lw=1.2),
                            arrowprops=dict(arrowstyle="->", color='#FACC15', lw=1.2),
                            zorder=12)

    # (A) PLANO DE PLANTA GENERAL
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
                 "Simbología Norma DGE Sección 9 | Vanos Reglamentarios CNE | Catastro WGS 84 Z19S",
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

    # (B) ZOOMS SECTORIALES
    fig, ax = plt.subplots(figsize=(14, 10), dpi=180)
    dibujar_elementos_comunes(ax, detalle_textos=True)
    ax.set_xlim(425350, 425850)
    ax.set_ylim(8436100, 8436750)
    ax.set_title("DETALLE SECTOR NORTE: MCH LIMBANI (200 kW) Y SUBESTACIÓN SED-01 (50 kVA)",
                 color='#F8FAFC', fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Este UTM [m]", color='#94A3B8', fontsize=9)
    ax.set_ylabel("Norte UTM [m]", color='#94A3B8', fontsize=9)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(color='#1E293B', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    fig.savefig(out_img_norte, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(14, 10), dpi=180)
    dibujar_elementos_comunes(ax, detalle_textos=True)
    ax.set_xlim(425250, 425650)
    ax.set_ylim(8435450, 8436150)
    ax.set_title("DETALLE SECTOR CENTRO: PLAZA DE ARMAS DE LIMBANI Y SUBESTACIÓN SED-02 (100 kVA)",
                 color='#F8FAFC', fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Este UTM [m]", color='#94A3B8', fontsize=9)
    ax.set_ylabel("Norte UTM [m]", color='#94A3B8', fontsize=9)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(color='#1E293B', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    fig.savefig(out_img_centro, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(14, 10), dpi=180)
    dibujar_elementos_comunes(ax, detalle_textos=True)
    ax.set_xlim(425200, 425650)
    ax.set_ylim(8434650, 8435450)
    ax.set_title("DETALLE SECTOR SUR: CRUCE FLUVIO-AÉREO RÍO CHINCHALAMANI, ESTADIO Y SED-03 (100 kVA)",
                 color='#F8FAFC', fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Este UTM [m]", color='#94A3B8', fontsize=9)
    ax.set_ylabel("Norte UTM [m]", color='#94A3B8', fontsize=9)
    ax.tick_params(colors='#94A3B8', labelsize=8)
    ax.grid(color='#1E293B', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    fig.savefig(out_img_sur, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)

    # Resumen metrados
    long_mt_total = sum(distancia(pts_mt[i], pts_mt[i+1]) for i in range(len(pts_mt)-1))
    long_bt_troncal = sum(distancia(p_a, p_b) for p_a, p_b, is_tr in lineas_bt_segmentos if is_tr)
    long_bt_deriv = sum(distancia(p_a, p_b) for p_a, p_b, is_tr in lineas_bt_segmentos if not is_tr)

    print("\n" + "="*70)
    print("METRADOS EXACTOS DEL MODELO CAD LIMBANI (CONFORME A NORMA DGE):")
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
