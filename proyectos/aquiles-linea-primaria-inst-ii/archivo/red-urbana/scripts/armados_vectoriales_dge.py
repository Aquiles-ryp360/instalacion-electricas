#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
armados_vectoriales_dge.py
Módulo de generación de láminas de detalle electromecánico y armados normalizados DGE
mediante geometría vectorial 100% CAD nativa (líneas, polilíneas, arcos, cotas, llamadas,
bloques, tablas de materiales y rótulos de ingeniería).

CUMPLE ESTRICTAMENTE:
- R.D. N° 024-2003-EM/DGE: Redes Primarias (PS-3, PA-3, PR-3, SAB, Retenida MT, PAT MT).
- R.D. N° 023-2003-EM-DGE: Redes Secundarias (E-1, Retenida BT, PAT BT, Acometida L-T).
- Código Nacional de Electricidad - Suministro 2011 (Regla 261: Retenidas y Puestas a Tierra).
- R.M. N° 091-2002-EM/VME: Símbolos Gráficos en Electricidad (Sección 9).

CERO CAPTURAS RASTER / 100% VECTORES TÉCNICOS.
"""

import math
import ezdxf
from ezdxf import colors

# -------------------------------------------------------------------------
# UTILIDADES VECTORIALES DE DIBUJO CAD
# -------------------------------------------------------------------------

def add_cota_h(msp, x1, x2, y, texto, offset_testigo=2.5, layer='09_COTAS_Y_TEXTOS', color=colors.CYAN):
    """Dibuja una cota lineal horizontal técnica con líneas testigo y flechas/ticks."""
    # Líneas testigo desde el objeto
    msp.add_line((x1, y - offset_testigo), (x1, y + 2.5), dxfattribs={'layer': layer, 'color': color})
    msp.add_line((x2, y - offset_testigo), (x2, y + 2.5), dxfattribs={'layer': layer, 'color': color})
    # Línea de cota principal
    msp.add_line((x1, y), (x2, y), dxfattribs={'layer': layer, 'color': color})
    # Ticks a 45° en los extremos
    t_sz = 1.6
    msp.add_line((x1 - t_sz, y - t_sz), (x1 + t_sz, y + t_sz), dxfattribs={'layer': layer, 'color': color})
    msp.add_line((x2 - t_sz, y - t_sz), (x2 + t_sz, y + t_sz), dxfattribs={'layer': layer, 'color': color})
    # Texto centrado sobre la línea
    xm = (x1 + x2) / 2.0
    t = msp.add_text(texto, dxfattribs={'layer': layer, 'height': 2.2, 'color': colors.WHITE})
    t.dxf.insert = (xm - len(texto)*0.65, y + 0.8)

def add_cota_v(msp, y1, y2, x, texto, offset_testigo=2.5, layer='09_COTAS_Y_TEXTOS', color=colors.CYAN):
    """Dibuja una cota lineal vertical técnica con líneas testigo y flechas/ticks."""
    msp.add_line((x - offset_testigo, y1), (x + 2.5, y1), dxfattribs={'layer': layer, 'color': color})
    msp.add_line((x - offset_testigo, y2), (x + 2.5, y2), dxfattribs={'layer': layer, 'color': color})
    msp.add_line((x, y1), (x, y2), dxfattribs={'layer': layer, 'color': color})
    t_sz = 1.6
    msp.add_line((x - t_sz, y1 - t_sz), (x + t_sz, y1 + t_sz), dxfattribs={'layer': layer, 'color': color})
    msp.add_line((x - t_sz, y2 - t_sz), (x + t_sz, y2 + t_sz), dxfattribs={'layer': layer, 'color': color})
    ym = (y1 + y2) / 2.0
    t = msp.add_text(texto, dxfattribs={'layer': layer, 'height': 2.2, 'color': colors.WHITE})
    t.dxf.insert = (x + 1.2, ym - 1.0)

def add_llamada(msp, px_obj, py_obj, px_txt, py_txt, texto, num_item=None, layer='10_DETALLES_ESTRUCTURAS_DGE'):
    """Dibuja una línea de directriz / llamada con punto en el objeto y texto alineado."""
    # Punto o círculo en el objeto
    msp.add_circle((px_obj, py_obj), radius=0.6, dxfattribs={'layer': layer, 'color': colors.YELLOW})
    # Tramo de directriz
    dx = px_txt - px_obj
    x_codo = px_txt - (8.0 if dx > 0 else -8.0)
    msp.add_lwpolyline([(px_obj, py_obj), (x_codo, py_txt), (px_txt, py_txt)],
                       dxfattribs={'layer': layer, 'color': colors.YELLOW})
    
    # Si tiene número de ítem, encerrar en globito
    if num_item is not None:
        c_x = px_txt + (3.5 if dx > 0 else -3.5)
        msp.add_circle((c_x, py_txt + 3.0), radius=2.5, dxfattribs={'layer': layer, 'color': colors.RED})
        ti = msp.add_text(f"{num_item}", dxfattribs={'layer': layer, 'height': 2.2, 'color': colors.WHITE})
        ti.dxf.insert = (c_x - 1.0, py_txt + 2.0)
        t = msp.add_text(texto, dxfattribs={'layer': layer, 'height': 1.9, 'color': colors.WHITE})
        t.dxf.insert = (px_txt + (7.0 if dx > 0 else -len(texto)*1.4), py_txt + 1.5)
    else:
        t = msp.add_text(texto, dxfattribs={'layer': layer, 'height': 1.9, 'color': colors.WHITE})
        t.dxf.insert = (px_txt + (2.0 if dx > 0 else -len(texto)*1.4), py_txt + 0.8)

def dibujar_marco_lamina_detalle(msp, x0, y0, w, h, cod_armado, titulo, norma):
    """Dibuja el marco de plano formal con recuadro institucional y franjas de título."""
    # Borde exterior grueso
    pl_ext = msp.add_lwpolyline([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0)],
                                dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    pl_ext.dxf.const_width = 0.6
    # Borde interior fino
    msp.add_lwpolyline([(x0 + 3.0, y0 + 3.0), (x0 + w - 3.0, y0 + 3.0),
                        (x0 + w - 3.0, y0 + h - 3.0), (x0 + 3.0, y0 + h - 3.0), (x0 + 3.0, y0 + 3.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    # Franja superior de encabezado
    msp.add_lwpolyline([(x0 + 3.0, y0 + h - 22.0), (x0 + w - 3.0, y0 + h - 22.0)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    msp.add_line((x0 + 75.0, y0 + h - 22.0), (x0 + 75.0, y0 + h - 3.0),
                 dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    
    t_fime = msp.add_text("UNA PUNO — FIME", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 3.2, 'color': colors.YELLOW})
    t_fime.dxf.insert = (x0 + 8.0, y0 + h - 12.0)
    t_ing = msp.add_text("INGENIERÍA MECÁNICA ELÉCTRICA", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.0, 'color': colors.WHITE})
    t_ing.dxf.insert = (x0 + 8.0, y0 + h - 18.0)

    t_tit = msp.add_text(f"ESTRUCTURA NORMALIZADA: {cod_armado} — {titulo}",
                         dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 4.2, 'color': colors.YELLOW})
    t_tit.dxf.insert = (x0 + 82.0, y0 + h - 11.5)

    t_sub = msp.add_text(f"NORMATIVA TÉCNICA: {norma}  |  PROYECTO: ELECTRIFICACIÓN RURAL LIMBANI 200 kW",
                         dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.4, 'color': colors.CYAN})
    t_sub.dxf.insert = (x0 + 82.0, y0 + h - 18.0)

    # Divisoria vertical: Izquierda (Zona de Dibujos Vectoriales) / Derecha (Planilla y Notas)
    msp.add_line((x0 + 195.0, y0 + 3.0), (x0 + 195.0, y0 + h - 22.0),
                 dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})

def dibujar_tabla_materiales_vectorial(msp, x_t, y_t, w_t, items, titulo="PLANILLA DE MATERIALES NORMALIZADOS DGE"):
    """Dibuja una planilla cuadriculada de especificaciones y metrado en formato vectorial formal."""
    h_row = 7.2
    n_items = len(items)
    h_tot = 12.0 + (n_items + 1) * h_row

    # Recuadro perimetral
    msp.add_lwpolyline([(x_t, y_t), (x_t + w_t, y_t), (x_t + w_t, y_t - h_tot),
                        (x_t, y_t - h_tot), (x_t, y_t)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})
    # Título tabla
    t_h = msp.add_text(titulo, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.8, 'color': colors.YELLOW})
    t_h.dxf.insert = (x_t + 5.0, y_t - 7.5)
    msp.add_line((x_t, y_t - 11.0), (x_t + w_t, y_t - 11.0), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})

    # Encabezados de columna
    y_enc = y_t - 17.0
    msp.add_text("ÍTEM", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.1, 'insert': (x_t + 2.0, y_enc), 'color': colors.CYAN})
    msp.add_text("DESCRIPCIÓN DEL MATERIAL", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.1, 'insert': (x_t + 16.0, y_enc), 'color': colors.CYAN})
    msp.add_text("NORMA", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.1, 'insert': (x_t + w_t - 38.0, y_enc), 'color': colors.CYAN})
    msp.add_text("CANT.", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.1, 'insert': (x_t + w_t - 16.0, y_enc), 'color': colors.CYAN})
    msp.add_line((x_t, y_t - 19.5), (x_t + w_t, y_t - 19.5), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})

    # Líneas verticales de columnas
    c1 = x_t + 13.0
    c2 = x_t + w_t - 42.0
    c3 = x_t + w_t - 20.0
    for cx in [c1, c2, c3]:
        msp.add_line((cx, y_t - 11.0), (cx, y_t - h_tot), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.WHITE})

    # Filas de datos
    curr_y = y_t - 25.5
    for item in items:
        # item: (num, desc, norma, cant)
        num, desc, nrm, cant = item
        msp.add_text(f"{num:02d}", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.0, 'insert': (x_t + 3.0, curr_y), 'color': colors.WHITE})
        msp.add_text(desc[:34], dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 1.9, 'insert': (x_t + 15.0, curr_y), 'color': colors.WHITE})
        msp.add_text(nrm[:10], dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 1.8, 'insert': (c2 + 2.0, curr_y), 'color': colors.GREEN})
        msp.add_text(str(cant), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.0, 'insert': (c3 + 2.0, curr_y), 'color': colors.YELLOW})
        msp.add_line((x_t, curr_y - 2.5), (x_t + w_t, curr_y - 2.5), dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': 250})
        curr_y -= h_row

    return y_t - h_tot

def dibujar_notas_tecnicas(msp, x_n, y_n, w_n, notas):
    """Dibuja recuadro de notas técnicas y prescripciones de montaje al pie de la planilla."""
    h_box = len(notas) * 5.8 + 10.0
    msp.add_lwpolyline([(x_n, y_n), (x_n + w_n, y_n), (x_n + w_n, y_n - h_box),
                        (x_n, y_n - h_box), (x_n, y_n)],
                       dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'color': colors.YELLOW})
    msp.add_text("NOTAS TÉCNICAS DE MONTAJE:", dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 2.2, 'insert': (x_n + 4.0, y_n - 6.0), 'color': colors.YELLOW})
    curr_y = y_n - 11.5
    for nota in notas:
        msp.add_text(nota, dxfattribs={'layer': '10_DETALLES_ESTRUCTURAS_DGE', 'height': 1.8, 'insert': (x_n + 4.0, curr_y), 'color': colors.WHITE})
        curr_y -= 5.8

def dibujar_cimentacion_ciclopea(msp, cx, y_base, y_terreno, w_cim=22.0):
    """Dibuja en corte la cimentación de concreto ciclópeo y achurado técnico."""
    layer = '10_DETALLES_ESTRUCTURAS_DGE'
    # Línea de terreno natural
    msp.add_line((cx - 45.0, y_terreno), (cx + 45.0, y_terreno), dxfattribs={'layer': layer, 'color': colors.YELLOW})
    msp.add_text("N.T.N. ±0.00", dxfattribs={'layer': layer, 'height': 2.1, 'insert': (cx + 30.0, y_terreno + 1.2), 'color': colors.YELLOW})
    # Pozo excavado
    x_c1, x_c2 = cx - w_cim/2.0, cx + w_cim/2.0
    msp.add_lwpolyline([(x_c1, y_terreno), (x_c1, y_base - 3.0), (x_c2, y_base - 3.0), (x_c2, y_terreno)],
                       dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Solado inferior de 10 cm
    msp.add_lwpolyline([(x_c1, y_base - 3.0), (x_c2, y_base - 3.0), (x_c2, y_base), (x_c1, y_base), (x_c1, y_base - 3.0)],
                       dxfattribs={'layer': layer, 'color': colors.CYAN})
    msp.add_text("Solado e=0.10m", dxfattribs={'layer': layer, 'height': 1.6, 'insert': (x_c1 + 1.5, y_base - 2.2), 'color': colors.CYAN})
    # Símbolos de piedra ciclópea (triángulos y polígonos dentro del macizo)
    for px_s, py_s in [(cx - 7.0, y_base + 6.0), (cx + 6.0, y_base + 9.0),
                       (cx - 6.0, y_base + 16.0), (cx + 7.0, y_base + 18.0)]:
        msp.add_lwpolyline([(px_s - 2.0, py_s - 1.5), (px_s + 2.0, py_s - 1.0),
                            (px_s + 0.5, py_s + 2.0), (px_s - 2.0, py_s - 1.5)],
                           dxfattribs={'layer': layer, 'color': 252})
    msp.add_text("Concreto Ciclópeo f'c=140 kg/cm² + 30% P.M.",
                 dxfattribs={'layer': layer, 'height': 1.8, 'insert': (cx - 22.0, y_base + 12.0), 'color': colors.WHITE})

def dibujar_aislador_pin_vector(msp, x_iso, y_espiga, h_iso=11.0, w_iso=6.5, layer='10_DETALLES_ESTRUCTURAS_DGE'):
    """Dibuja con precisión vectorial un aislador tipo Pin ANSI 55-5 con espiga y campanas concéntricas."""
    # Espiga de acero galvanizado
    msp.add_lwpolyline([(x_iso - 1.0, y_espiga), (x_iso + 1.0, y_espiga),
                        (x_iso + 0.8, y_espiga + 5.0), (x_iso - 0.8, y_espiga + 5.0),
                        (x_iso - 1.0, y_espiga)], dxfattribs={'layer': layer, 'color': colors.WHITE})
    y_base_iso = y_espiga + 4.5
    # Campana inferior
    msp.add_lwpolyline([
        (x_iso - w_iso*0.55, y_base_iso), (x_iso + w_iso*0.55, y_base_iso),
        (x_iso + w_iso*0.45, y_base_iso + 2.2), (x_iso - w_iso*0.45, y_base_iso + 2.2),
        (x_iso - w_iso*0.55, y_base_iso)
    ], dxfattribs={'layer': layer, 'color': colors.RED})
    # Campana intermedia
    y_m = y_base_iso + 2.2
    msp.add_lwpolyline([
        (x_iso - w_iso*0.48, y_m), (x_iso + w_iso*0.48, y_m),
        (x_iso + w_iso*0.35, y_m + 2.2), (x_iso - w_iso*0.35, y_m + 2.2),
        (x_iso - w_iso*0.48, y_m)
    ], dxfattribs={'layer': layer, 'color': colors.RED})
    # Campana superior (sombrerete y ranura)
    y_s = y_m + 2.2
    msp.add_lwpolyline([
        (x_iso - w_iso*0.40, y_s), (x_iso + w_iso*0.40, y_s),
        (x_iso + w_iso*0.25, y_s + 3.0), (x_iso + 0.8, y_s + 3.0),
        (x_iso + 0.8, y_s + 1.8), (x_iso - 0.8, y_s + 1.8),
        (x_iso - 0.8, y_s + 3.0), (x_iso - w_iso*0.25, y_s + 3.0),
        (x_iso - w_iso*0.40, y_s)
    ], dxfattribs={'layer': layer, 'color': colors.RED})
    # Conductor pasando por la garganta
    y_cond = y_s + 2.2
    msp.add_line((x_iso - 6.0, y_cond), (x_iso + 6.0, y_cond), dxfattribs={'layer': layer, 'color': colors.RED})
    msp.add_circle((x_iso, y_cond), radius=0.9, dxfattribs={'layer': layer, 'color': colors.YELLOW})
    # Amarre con alambre
    msp.add_line((x_iso - 2.5, y_cond + 0.9), (x_iso + 2.5, y_cond - 0.9), dxfattribs={'layer': layer, 'color': colors.WHITE})

def dibujar_cadena_polimerica_vector(msp, x_p, y_p, l_cad=26.0, layer='10_DETALLES_ESTRUCTURAS_DGE'):
    """Dibuja una cadena de aislador polimérico de suspensión / retención de 15 kV."""
    # Terminal de horquilla
    msp.add_lwpolyline([(x_p, y_p - 1.2), (x_p + 3.0, y_p - 1.2), (x_p + 3.0, y_p + 1.2), (x_p, y_p + 1.2), (x_p, y_p - 1.2)],
                       dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Vástago de fibra de vidrio
    msp.add_line((x_p + 3.0, y_p), (x_p + l_cad - 4.0, y_p), dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Aletas de silicona (6 faldas)
    n_aletas = 6
    step = (l_cad - 8.0) / n_aletas
    for i in range(n_aletas):
        xa = x_p + 4.5 + i * step
        msp.add_line((xa, y_p - 3.2), (xa, y_p + 3.2), dxfattribs={'layer': layer, 'color': colors.RED})
        msp.add_lwpolyline([(xa - 0.8, y_p - 3.2), (xa + 0.8, y_p - 3.2),
                            (xa, y_p), (xa - 0.8, y_p - 3.2)], dxfattribs={'layer': layer, 'color': colors.RED})
        msp.add_lwpolyline([(xa - 0.8, y_p + 3.2), (xa + 0.8, y_p + 3.2),
                            (xa, y_p), (xa - 0.8, y_p + 3.2)], dxfattribs={'layer': layer, 'color': colors.RED})
    # Grapa terminal tipo pistola
    xg = x_p + l_cad - 4.0
    msp.add_lwpolyline([(xg, y_p - 1.5), (xg + 4.0, y_p - 1.5), (xg + 6.0, y_p + 2.5), (xg + 2.0, y_p + 2.5), (xg, y_p - 1.5)],
                       dxfattribs={'layer': layer, 'color': colors.YELLOW})
    # Pernos en U de la grapa
    msp.add_circle((xg + 2.5, y_p - 0.5), radius=0.5, dxfattribs={'layer': layer, 'color': colors.WHITE})
    msp.add_circle((xg + 4.2, y_p - 0.5), radius=0.5, dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Conductor saliendo
    msp.add_line((xg + 5.0, y_p + 1.5), (xg + 16.0, y_p + 1.5), dxfattribs={'layer': layer, 'color': colors.RED})


# -------------------------------------------------------------------------
# BLOQUE 1: ARMADO PS-3 (SUSPENSIÓN ALINEAMIENTO MT 10 kV)
# -------------------------------------------------------------------------
def generar_vector_ps3(msp, x0, y0, w=340.0, h=250.0):
    dibujar_marco_lamina_detalle(msp, x0, y0, w, h, "ARMADO PS-3", "SUSPENSIÓN ALINEAMIENTO TRIFÁSICA MT 10 kV (0° A 5°)", "R.D. N° 024-2003-EM/DGE LÁMINA 004")
    layer = '10_DETALLES_ESTRUCTURAS_DGE'

    # Eje del poste en la mitad izquierda
    cx = x0 + 85.0
    y_base = y0 + 35.0
    y_ntn = y0 + 58.0
    y_cima = y0 + 215.0

    # Cimentación
    dibujar_cimentacion_ciclopea(msp, cx, y_base, y_ntn, w_cim=22.0)

    # Poste troncocónico CAC 12/300
    r_base, r_cima = 3.6, 1.6
    msp.add_lwpolyline([
        (cx - r_base, y_base), (cx + r_base, y_base),
        (cx + r_cima, y_cima), (cx - r_cima, y_cima),
        (cx - r_base, y_base)
    ], dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Cúpula de perilla
    msp.add_arc((cx, y_cima), radius=r_cima, start_angle=0, end_angle=180, dxfattribs={'layer': layer, 'color': colors.WHITE})

    # Cruceta simétrica F°G° 75x75x6.4 mm x 2.0 m
    y_cruc = y_cima - 12.0
    w_cr = 64.0  # 2.0 m a escala
    h_cr = 3.0
    msp.add_lwpolyline([
        (cx - w_cr/2.0, y_cruc - h_cr/2.0), (cx + w_cr/2.0, y_cruc - h_cr/2.0),
        (cx + w_cr/2.0, y_cruc + h_cr/2.0), (cx - w_cr/2.0, y_cruc + h_cr/2.0),
        (cx - w_cr/2.0, y_cruc - h_cr/2.0)
    ], dxfattribs={'layer': layer, 'color': colors.WHITE})

    # Abrazadera partida platina 50x6 mm fijando cruceta
    msp.add_lwpolyline([(cx - 3.2, y_cruc - 2.5), (cx + 3.2, y_cruc - 2.5),
                        (cx + 3.2, y_cruc + 2.5), (cx - 3.2, y_cruc + 2.5), (cx - 3.2, y_cruc - 2.5)],
                       dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # Riostras en V de perfil angular 50x50x4.8 mm
    y_abraz_inf = y_cruc - 30.0
    msp.add_lwpolyline([(cx - 2.6, y_abraz_inf - 1.5), (cx + 2.6, y_abraz_inf - 1.5),
                        (cx + 2.6, y_abraz_inf + 1.5), (cx - 2.6, y_abraz_inf + 1.5), (cx - 2.6, y_abraz_inf - 1.5)],
                       dxfattribs={'layer': layer, 'color': colors.YELLOW})
    msp.add_line((cx, y_abraz_inf), (cx - 22.0, y_cruc - h_cr/2.0), dxfattribs={'layer': layer, 'color': colors.WHITE})
    msp.add_line((cx, y_abraz_inf), (cx + 22.0, y_cruc - h_cr/2.0), dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Pernos de riostra
    for px_b in [cx - 22.0, cx + 22.0]:
        msp.add_circle((px_b, y_cruc - h_cr/2.0 - 0.8), radius=0.7, dxfattribs={'layer': layer, 'color': colors.WHITE})

    # 3 Aisladores Pin ANSI 55-5 (fases R, S, T)
    for px_iso in [cx - 26.0, cx, cx + 26.0]:
        dibujar_aislador_pin_vector(msp, px_iso, y_cruc + h_cr/2.0, h_iso=10.0, w_iso=6.0, layer=layer)

    # Conductor de bajada PAT
    msp.add_line((cx + 1.0, y_cima - 5.0), (cx + 1.0, y_ntn), dxfattribs={'layer': layer, 'color': colors.GREEN})

    # Cotas Técnicas
    add_cota_v(msp, y_base, y_cima, cx + 52.0, "12.00 m (Ht)", layer=layer)
    add_cota_v(msp, y_base, y_ntn, cx + 38.0, "1.70 m (He)", layer=layer)
    add_cota_v(msp, y_ntn, y_cima, cx + 38.0, "10.30 m (Hu)", layer=layer)
    add_cota_h(msp, cx - w_cr/2.0, cx + w_cr/2.0, y_cima + 15.0, "2 000 mm", layer=layer)
    add_cota_h(msp, cx - 26.0, cx, y_cima + 8.0, "950 mm", layer=layer)
    add_cota_h(msp, cx, cx + 26.0, y_cima + 8.0, "950 mm", layer=layer)

    # Líneas de llamada con números de ítem
    add_llamada(msp, cx + r_cima, y_cima - 5.0, cx - 45.0, y_cima + 2.0, "Poste CAC 12/300 daN", num_item=1, layer=layer)
    add_llamada(msp, cx - 28.0, y_cruc, cx - 55.0, y_cruc + 6.0, "Cruceta F°G° 75x75x6.4x2000 mm", num_item=2, layer=layer)
    add_llamada(msp, cx + 26.0, y_cruc + 8.0, cx + 45.0, y_cruc + 10.0, "Aislador Pin ANSI 55-5", num_item=3, layer=layer)
    add_llamada(msp, cx + 26.0, y_cruc + 2.0, cx + 45.0, y_cruc - 4.0, "Espiga F°G° 3/4\"x8\"", num_item=4, layer=layer)
    add_llamada(msp, cx - 11.0, y_cruc - 15.0, cx - 55.0, y_cruc - 18.0, "Riostra angular L 50x50x4.8 mm", num_item=5, layer=layer)
    add_llamada(msp, cx, y_cruc, cx - 55.0, y_cruc - 8.0, "Abrazadera partida platina 50x6 mm", num_item=6, layer=layer)
    add_llamada(msp, cx - 26.0, y_cruc + 10.5, cx - 55.0, y_cruc + 20.0, "Conductor AAAC 35 mm² c/cinta", num_item=7, layer=layer)
    add_llamada(msp, cx + 8.0, y_base + 10.0, cx + 32.0, y_base + 2.0, "Cimentación f'c=140 kg/cm²", num_item=8, layer=layer)

    # Planilla de Materiales en el lado derecho
    items_ps3 = [
        (1, "Poste Concreto Centrifugado 12/300", "NTP 339.027", "1 und"),
        (2, "Cruceta simétrica F°G° 75x75x6.4x2000", "ASTM A123", "1 und"),
        (3, "Aislador porcelana Pin ANSI 55-5", "ANSI C29.5", "3 und"),
        (4, "Espiga recta aislador Pin F°G° 3/4\"x8\"", "ASTM A153", "3 und"),
        (5, "Riostras angulares V 50x50x4.8x800", "ASTM A36", "2 und"),
        (6, "Abrazadera platina partida 50x6 mm", "ASTM A36", "2 jgo"),
        (7, "Perno maquinado F°G° 5/8\"x8\" c/tca", "ASTM A307", "4 und"),
        (8, "Cinta plana armar aleación aluminio", "NTP 370.258", "3 jgo"),
        (9, "Alambre amarre Al recocido #4", "NTP 370.258", "6 m"),
        (10, "Conductor bajada PAT Cu desnudo 25", "NTP 370.043", "14 m")
    ]
    y_fin_t = dibujar_tabla_materiales_vectorial(msp, x0 + 198.0, y0 + h - 28.0, 138.0, items_ps3, "PLANILLA DE MATERIALES DGE — ARMADO PS-3")

    # Notas Técnicas
    notas = [
        "1. Armado para alineamientos rectos y ángulos menores de 0° a 5°.",
        "2. Conductor AAAC 35 mm² tensado según tabla de templado a 15°C.",
        "3. Profundidad de excavación reglamentaria: He = H/10 + 0.50 = 1.70 m.",
        "4. Todos los herrajes y pernos deben ser galvanizados en caliente (ASTM A153).",
        "5. Conexión de PAT con grapa de bronce en la base del poste (R <= 25 Ω)."
    ]
    dibujar_notas_tecnicas(msp, x0 + 198.0, y_fin_t - 4.0, 138.0, notas)


# -------------------------------------------------------------------------
# BLOQUE 2: ARMADO PA-3 (ÁNGULO MT 10 kV, 5° - 30°)
# -------------------------------------------------------------------------
def generar_vector_pa3(msp, x0, y0, w=340.0, h=250.0):
    dibujar_marco_lamina_detalle(msp, x0, y0, w, h, "ARMADO PA-3", "ÁNGULO PEQUEÑO Y MEDIANO TRIFÁSICA MT 10 kV (5° A 30°)", "R.D. N° 024-2003-EM/DGE LÁMINA 008")
    layer = '10_DETALLES_ESTRUCTURAS_DGE'

    cx = x0 + 85.0
    y_base = y0 + 35.0
    y_ntn = y0 + 58.0
    y_cima = y0 + 215.0

    dibujar_cimentacion_ciclopea(msp, cx, y_base, y_ntn, w_cim=24.0)

    # Poste CAC 12/400
    r_base, r_cima = 3.9, 1.8
    msp.add_lwpolyline([
        (cx - r_base, y_base), (cx + r_base, y_base),
        (cx + r_cima, y_cima), (cx - r_cima, y_cima),
        (cx - r_base, y_base)
    ], dxfattribs={'layer': layer, 'color': colors.WHITE})
    msp.add_arc((cx, y_cima), radius=r_cima, start_angle=0, end_angle=180, dxfattribs={'layer': layer, 'color': colors.WHITE})

    # Cruceta angular reforzada F°G° 75x75x6.4 mm
    y_cruc = y_cima - 12.0
    w_cr = 64.0
    h_cr = 3.2
    msp.add_lwpolyline([
        (cx - w_cr/2.0, y_cruc - h_cr/2.0), (cx + w_cr/2.0, y_cruc - h_cr/2.0),
        (cx + w_cr/2.0, y_cruc + h_cr/2.0), (cx - w_cr/2.0, y_cruc + h_cr/2.0),
        (cx - w_cr/2.0, y_cruc - h_cr/2.0)
    ], dxfattribs={'layer': layer, 'color': colors.WHITE})

    # Doble riostra en V
    y_abraz_inf = y_cruc - 30.0
    msp.add_lwpolyline([(cx - 2.8, y_abraz_inf - 1.5), (cx + 2.8, y_abraz_inf - 1.5),
                        (cx + 2.8, y_abraz_inf + 1.5), (cx - 2.8, y_abraz_inf + 1.5), (cx - 2.8, y_abraz_inf - 1.5)],
                       dxfattribs={'layer': layer, 'color': colors.YELLOW})
    msp.add_line((cx, y_abraz_inf), (cx - 22.0, y_cruc - h_cr/2.0), dxfattribs={'layer': layer, 'color': colors.WHITE})
    msp.add_line((cx, y_abraz_inf), (cx + 22.0, y_cruc - h_cr/2.0), dxfattribs={'layer': layer, 'color': colors.WHITE})

    # 3 Aisladores Pin con doble amarre lateral para soportar tiro angular
    for px_iso in [cx - 26.0, cx, cx + 26.0]:
        dibujar_aislador_pin_vector(msp, px_iso, y_cruc + h_cr/2.0, h_iso=10.0, w_iso=6.0, layer=layer)
        # Doble amarre angular en el cuello
        msp.add_line((px_iso - 3.0, y_cruc + 6.5), (px_iso + 3.0, y_cruc + 7.5), dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # RETENIDA BISELAR DE CONTRA-TIRO (en el lado opuesto al ángulo)
    y_ret = y_cruc - 2.0
    px_ancla = cx - 55.0
    py_ancla = y_ntn
    # Cable SM 5/16"
    msp.add_line((cx, y_ret), (px_ancla, py_ancla), dxfattribs={'layer': layer, 'color': colors.MAGENTA})
    # Aislador nuez 54-1 a 60%
    px_nuez = cx - 33.0
    py_nuez = y_ret - (y_ret - py_ancla)*0.60
    msp.add_circle((px_nuez, py_nuez), radius=2.2, dxfattribs={'layer': layer, 'color': colors.YELLOW})
    # Tubo PVC amarillo 1.80 m
    pl_pv = msp.add_lwpolyline([(px_ancla + 14.0, py_ancla + 14.0), (px_ancla, py_ancla)], dxfattribs={'layer': layer, 'color': colors.YELLOW})
    pl_pv.dxf.const_width = 1.2
    # Varilla y bloque CAV
    px_cav = px_ancla - 12.0
    py_cav = py_ancla - 16.0
    msp.add_line((px_ancla, py_ancla), (px_cav, py_cav), dxfattribs={'layer': layer, 'color': colors.WHITE})
    msp.add_lwpolyline([(px_cav - 5.0, py_cav - 3.0), (px_cav + 5.0, py_cav - 3.0),
                        (px_cav + 5.0, py_cav + 3.0), (px_cav - 5.0, py_cav + 3.0), (px_cav - 5.0, py_cav - 3.0)],
                       dxfattribs={'layer': layer, 'color': colors.MAGENTA})

    # Cotas
    add_cota_v(msp, y_base, y_cima, cx + 52.0, "12.00 m (Ht)", layer=layer)
    add_cota_v(msp, y_base, y_ntn, cx + 38.0, "1.70 m (He)", layer=layer)
    add_cota_h(msp, cx - w_cr/2.0, cx + w_cr/2.0, y_cima + 15.0, "2 000 mm", layer=layer)
    add_cota_h(msp, px_ancla, cx, y_ntn - 8.0, "d = 8.50 m (45°)", layer=layer)

    # Llamadas
    add_llamada(msp, cx + r_cima, y_cima - 5.0, cx + 45.0, y_cima + 5.0, "Poste CAC 12/400 daN", num_item=1, layer=layer)
    add_llamada(msp, cx, y_cruc, cx + 45.0, y_cruc - 4.0, "Cruceta angular reforzada", num_item=2, layer=layer)
    add_llamada(msp, cx - 26.0, y_cruc + 7.0, cx - 55.0, y_cruc + 20.0, "Aislador Pin c/amarre lateral", num_item=3, layer=layer)
    add_llamada(msp, px_nuez, py_nuez, cx - 60.0, py_nuez + 8.0, "Aislador tracción ANSI 54-1", num_item=4, layer=layer)
    add_llamada(msp, px_ancla + 7.0, py_ancla + 7.0, cx - 60.0, py_ancla + 18.0, "Protector PVC amarillo 1.80m", num_item=5, layer=layer)
    add_llamada(msp, px_cav, py_cav, cx - 60.0, py_cav - 2.0, "Bloque anclaje CAV 0.50x0.50", num_item=6, layer=layer)

    items_pa3 = [
        (1, "Poste Concreto Centrifugado 12/400", "NTP 339.027", "1 und"),
        (2, "Cruceta angular reforzada F°G° 75x75x6.4", "ASTM A123", "1 und"),
        (3, "Aislador porcelana Pin ANSI 55-5", "ANSI C29.5", "3 und"),
        (4, "Espiga para pin reforzada 3/4\"x10\"", "ASTM A153", "3 und"),
        (5, "Retenida acero Siemens Martin 5/16\"", "ASTM A363", "1 jgo"),
        (6, "Aislador tracción nuez ANSI 54-1", "ANSI C29.4", "1 und"),
        (7, "Varilla ancla F°G° 5/8\"x2.0m c/guard.", "ASTM A153", "1 und"),
        (8, "Bloque anclaje concreto CAV 0.50x0.50", "DGE Lám.074", "1 und"),
        (9, "Protector PVC amarillo D=1.5\"x1.8m", "NTP 399.002", "1 und"),
        (10, "Grapas prensacables Crosby 5/16\"", "Fed.Spec.", "6 und")
    ]
    y_fin_t = dibujar_tabla_materiales_vectorial(msp, x0 + 198.0, y0 + h - 28.0, 138.0, items_pa3, "PLANILLA DE MATERIALES DGE — ARMADO PA-3")

    notas_pa = [
        "1. Para vértices con ángulo horizontal de deflexión entre 5° y 30°.",
        "2. La retenida biselar se instala en la bisectriz del ángulo suplementario.",
        "3. Emplear doble amarre de conductor con alambre de aluminio recocido.",
        "4. Profundidad del bloque de anclaje: 1.80 m mínimo con tierra compactada."
    ]
    dibujar_notas_tecnicas(msp, x0 + 198.0, y_fin_t - 4.0, 138.0, notas_pa)


# -------------------------------------------------------------------------
# BLOQUE 3: ARMADO PR-3 (RETENCIÓN / ANCLAJE / CRUCE FLUVIAL)
# -------------------------------------------------------------------------
def generar_vector_pr3(msp, x0, y0, w=340.0, h=250.0):
    dibujar_marco_lamina_detalle(msp, x0, y0, w, h, "ARMADO PR-3", "RETENCIÓN / ANCLAJE Y CRUCE FLUVIAL TRIFÁSICA 10 kV", "R.D. N° 024-2003-EM/DGE LÁMINA 020")
    layer = '10_DETALLES_ESTRUCTURAS_DGE'

    cx = x0 + 85.0
    y_base = y0 + 32.0
    y_ntn = y0 + 58.0
    y_cima = y0 + 220.0

    dibujar_cimentacion_ciclopea(msp, cx, y_base, y_ntn, w_cim=26.0)

    # Poste CAC 13/400 (o 13/600 cruce río)
    r_base, r_cima = 4.2, 1.9
    msp.add_lwpolyline([
        (cx - r_base, y_base), (cx + r_base, y_base),
        (cx + r_cima, y_cima), (cx - r_cima, y_cima),
        (cx - r_base, y_base)
    ], dxfattribs={'layer': layer, 'color': colors.WHITE})
    msp.add_arc((cx, y_cima), radius=r_cima, start_angle=0, end_angle=180, dxfattribs={'layer': layer, 'color': colors.WHITE})

    # Doble cruceta de retención 100x100x6.4 mm x 2.0 m
    y_cruc = y_cima - 14.0
    w_cr = 64.0
    h_cr = 4.2
    # Cruceta frontal y trasera (dibujada con doble línea)
    msp.add_lwpolyline([
        (cx - w_cr/2.0, y_cruc - h_cr/2.0), (cx + w_cr/2.0, y_cruc - h_cr/2.0),
        (cx + w_cr/2.0, y_cruc + h_cr/2.0), (cx - w_cr/2.0, y_cruc + h_cr/2.0),
        (cx - w_cr/2.0, y_cruc - h_cr/2.0)
    ], dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Pernos de doble armado (4 unidades)
    for px_da in [cx - 28.0, cx - 12.0, cx + 12.0, cx + 28.0]:
        msp.add_circle((px_da, y_cruc), radius=0.9, dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # 3 Cadenas de retención con aisladores poliméricos horizontales
    for px_cad, dx_tiro in [(cx - 26.0, 24.0), (cx, 24.0), (cx + 26.0, 24.0)]:
        dibujar_cadena_polimerica_vector(msp, px_cad, y_cruc, l_cad=dx_tiro, layer=layer)
        # Cuello muerto / puente de derivación en catenaria
        msp.add_arc((px_cad + 12.0, y_cruc + 6.0), radius=7.0, start_angle=180, end_angle=360, dxfattribs={'layer': layer, 'color': colors.RED})

    # Doble retenida pesada de anclaje a contra-tiro
    px_ancla = cx - 55.0
    py_ancla = y_ntn
    msp.add_line((cx, y_cruc), (px_ancla, py_ancla), dxfattribs={'layer': layer, 'color': colors.MAGENTA})
    msp.add_line((cx, y_cruc - 6.0), (px_ancla - 5.0, py_ancla), dxfattribs={'layer': layer, 'color': colors.MAGENTA})
    # Nuez doble
    msp.add_circle((cx - 33.0, y_cruc - 28.0), radius=2.4, dxfattribs={'layer': layer, 'color': colors.YELLOW})
    msp.add_circle((cx - 37.0, y_cruc - 32.0), radius=2.4, dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # Cotas
    add_cota_v(msp, y_base, y_cima, cx + 62.0, "13.00 m (Ht)", layer=layer)
    add_cota_v(msp, y_base, y_ntn, cx + 48.0, "1.80 m (He)", layer=layer)
    add_cota_h(msp, cx - w_cr/2.0, cx + w_cr/2.0, y_cima + 16.0, "2 000 mm", layer=layer)

    # Llamadas
    add_llamada(msp, cx + r_cima, y_cima - 5.0, cx + 45.0, y_cima + 6.0, "Poste CAC 13/400 o 13/600", num_item=1, layer=layer)
    add_llamada(msp, cx - 28.0, y_cruc, cx - 60.0, y_cruc + 12.0, "Doble cruceta 100x100x6.4 mm", num_item=2, layer=layer)
    add_llamada(msp, cx + 16.0, y_cruc, cx + 55.0, y_cruc + 10.0, "Aislador polimérico 15kV/70kN", num_item=3, layer=layer)
    add_llamada(msp, cx + 22.0, y_cruc - 1.5, cx + 55.0, y_cruc - 6.0, "Grapa pistola 3 pernos Al-Cu", num_item=4, layer=layer)
    add_llamada(msp, cx - 12.0, y_cruc, cx - 60.0, y_cruc - 5.0, "Pernos doble armado 5/8\"x16\"", num_item=5, layer=layer)
    add_llamada(msp, cx - 33.0, y_cruc - 28.0, cx - 65.0, y_cruc - 24.0, "Doble retenida pesada 5/16\"", num_item=6, layer=layer)

    items_pr3 = [
        (1, "Poste Concreto Centrifugado 13/400 (o 13/600)", "NTP 339.027", "1 und"),
        (2, "Doble cruceta retención F°G° 100x100x6.4x2000", "ASTM A123", "2 und"),
        (3, "Aislador polimérico suspensión 15 kV / 70 kN", "IEC 61109", "3 und"),
        (4, "Grapa anclaje pistola 3 pernos aleación Al", "ASTM A153", "3 und"),
        (5, "Perno doble armado F°G° 5/8\"x16\" c/tuercas", "ASTM A307", "4 und"),
        (6, "Retenida acero Siemens Martin 5/16\" doble", "ASTM A363", "2 jgo"),
        (7, "Aislador tracción nuez porcelana ANSI 54-1", "ANSI C29.4", "2 und"),
        (8, "Varilla ancla F°G° 3/4\"x2.4m c/guardacabo", "ASTM A153", "2 und"),
        (9, "Bloque concreto CAV 0.60x0.60x0.25 m", "DGE Lám.074", "2 und"),
        (10, "Conector bimetálico derivación puente MT", "NTP 370.258", "3 und")
    ]
    y_fin_t = dibujar_tabla_materiales_vectorial(msp, x0 + 198.0, y0 + h - 28.0, 138.0, items_pr3, "PLANILLA DE MATERIALES DGE — ARMADO PR-3")

    notas_pr = [
        "1. Estructura de fin de línea, retención angular y cruce especial fluvial.",
        "2. En el vano del río Chinchalamani (110 m), emplear poste reforzado 13/600.",
        "3. Doble anclaje pesado a contra-tiro empotrado a 1.80 m de profundidad.",
        "4. Catenarias de cuello muerto con holgura suficiente para evitar vibración."
    ]
    dibujar_notas_tecnicas(msp, x0 + 198.0, y_fin_t - 4.0, 138.0, notas_pr)


# -------------------------------------------------------------------------
# BLOQUE 4: SUBESTACIÓN AÉREA BIPOSTE (SAB 50 y 100 kVA)
# -------------------------------------------------------------------------
def generar_vector_sab(msp, x0, y0, w=340.0, h=250.0):
    dibujar_marco_lamina_detalle(msp, x0, y0, w, h, "SUBESTACIÓN SAB", "SUBESTACIÓN AÉREA BIPOSTE 10/0.38-0.22 kV (50 Y 100 kVA)", "R.D. N° 024-2003-EM/DGE LÁMINAS 064(1/2) Y 064(2/2)")
    layer = '10_DETALLES_ESTRUCTURAS_DGE'

    cx = x0 + 90.0
    y_base = y0 + 32.0
    y_ntn = y0 + 58.0
    y_cima = y0 + 220.0
    d_biposte = 32.0  # 2.00 m entre ejes a escala

    # Cimentaciones de ambos postes
    for xp in [cx - d_biposte/2.0, cx + d_biposte/2.0]:
        dibujar_cimentacion_ciclopea(msp, xp, y_base, y_ntn, w_cim=18.0)

    # Dos postes CAC 13/400
    r_base, r_cima = 3.8, 1.8
    for xp in [cx - d_biposte/2.0, cx + d_biposte/2.0]:
        msp.add_lwpolyline([
            (xp - r_base, y_base), (xp + r_base, y_base),
            (xp + r_cima, y_cima), (xp - r_cima, y_cima),
            (xp - r_base, y_base)
        ], dxfattribs={'layer': layer, 'color': colors.WHITE})
        msp.add_arc((xp, y_cima), radius=r_cima, start_angle=0, end_angle=180, dxfattribs={'layer': layer, 'color': colors.WHITE})

    # PLATAFORMA SOPORTE DE TRANSFORMADOR (UPN 120 x 2.40 m) a H = 3.50 m (Y = y_ntn + 50.0)
    y_plat = y_ntn + 52.0
    w_pl = d_biposte + 20.0
    msp.add_lwpolyline([
        (cx - w_pl/2.0, y_plat - 2.5), (cx + w_pl/2.0, y_plat - 2.5),
        (cx + w_pl/2.0, y_plat + 2.5), (cx - w_pl/2.0, y_plat + 2.5),
        (cx - w_pl/2.0, y_plat - 2.5)
    ], dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Abrazaderas CAS de soporte de plataforma en ambos postes
    for xp in [cx - d_biposte/2.0, cx + d_biposte/2.0]:
        msp.add_lwpolyline([(xp - 3.2, y_plat - 4.0), (xp + 3.2, y_plat - 4.0),
                            (xp + 3.2, y_plat + 4.0), (xp - 3.2, y_plat + 4.0), (xp - 3.2, y_plat - 4.0)],
                           dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # TRANSFORMADOR TRIFÁSICO DE DISTRIBUCIÓN
    w_tr, h_tr = 18.0, 22.0
    msp.add_lwpolyline([
        (cx - w_tr/2.0, y_plat + 2.5), (cx + w_tr/2.0, y_plat + 2.5),
        (cx + w_tr/2.0, y_plat + 2.5 + h_tr), (cx - w_tr/2.0, y_plat + 2.5 + h_tr),
        (cx - w_tr/2.0, y_plat + 2.5)
    ], dxfattribs={'layer': layer, 'color': colors.YELLOW})
    # Aletas radiadoras laterales
    for rad_x in [cx - w_tr/2.0 - 2.5, cx + w_tr/2.0]:
        msp.add_lwpolyline([(rad_x, y_plat + 5.0), (rad_x + 2.5, y_plat + 5.0),
                            (rad_x + 2.5, y_plat + h_tr - 2.0), (rad_x, y_plat + h_tr - 2.0), (rad_x, y_plat + 5.0)],
                           dxfattribs={'layer': layer, 'color': colors.YELLOW})
    # Pasatapas MT sobre la tapa (3 bornes de porcelana)
    y_tapa = y_plat + 2.5 + h_tr
    for bx in [cx - 5.0, cx, cx + 5.0]:
        msp.add_lwpolyline([(bx - 1.0, y_tapa), (bx + 1.0, y_tapa), (bx + 0.6, y_tapa + 5.0), (bx - 0.6, y_tapa + 5.0), (bx - 1.0, y_tapa)],
                           dxfattribs={'layer': layer, 'color': colors.RED})
    # Rótulo del trafo
    msp.add_text("TRAFO 100 kVA", dxfattribs={'layer': layer, 'height': 2.0, 'insert': (cx - 7.5, y_plat + 12.0), 'color': colors.WHITE})
    msp.add_text("Dyn5 10/0.38 kV", dxfattribs={'layer': layer, 'height': 1.6, 'insert': (cx - 7.0, y_plat + 8.0), 'color': colors.CYAN})

    # NIVEL SUPERIOR: CRUCETA DE SECCIONAMIENTO Y PROTECCIÓN (Cut-Out + Pararrayos)
    y_prot = y_cima - 16.0
    w_cr_p = d_biposte + 26.0
    msp.add_lwpolyline([
        (cx - w_cr_p/2.0, y_prot - 2.0), (cx + w_cr_p/2.0, y_prot - 2.0),
        (cx + w_cr_p/2.0, y_prot + 2.0), (cx - w_cr_p/2.0, y_prot + 2.0),
        (cx - w_cr_p/2.0, y_prot - 2.0)
    ], dxfattribs={'layer': layer, 'color': colors.WHITE})

    # 3 Seccionadores Cut-Out 15 kV / 100 A
    for sx in [cx - 16.0, cx, cx + 16.0]:
        msp.add_line((sx, y_prot + 2.0), (sx, y_prot + 10.0), dxfattribs={'layer': layer, 'color': colors.RED})
        msp.add_lwpolyline([(sx - 1.2, y_prot + 4.0), (sx + 2.5, y_prot + 8.0), (sx + 1.5, y_prot + 9.5), (sx - 1.2, y_prot + 4.0)],
                           dxfattribs={'layer': layer, 'color': colors.YELLOW})
    # 3 Pararrayos ZnO 12 kV / 10 kA
    for px_arr in [cx - 22.0, cx - 6.0, cx + 10.0]:
        msp.add_lwpolyline([(px_arr - 1.0, y_prot - 2.0), (px_arr + 1.0, y_prot - 2.0),
                            (px_arr + 0.8, y_prot - 8.0), (px_arr - 0.8, y_prot - 8.0), (px_arr - 1.0, y_prot - 2.0)],
                           dxfattribs={'layer': layer, 'color': colors.RED})

    # TABLERO DE DISTRIBUCIÓN EN BAJA TENSIÓN (BT IP54)
    # Adosado al poste derecho a H = 1.80 m (Y = y_ntn + 25.0)
    x_tab = cx + d_biposte/2.0 + 3.0
    y_tab = y_ntn + 15.0
    w_tb, h_tb = 14.0, 20.0
    msp.add_lwpolyline([(x_tab, y_tab), (x_tab + w_tb, y_tab),
                        (x_tab + w_tb, y_tab + h_tb), (x_tab, y_tab + h_tb), (x_tab, y_tab)],
                       dxfattribs={'layer': layer, 'color': colors.CYAN})
    msp.add_line((x_tab + w_tb/2.0, y_tab), (x_tab + w_tb/2.0, y_tab + h_tb), dxfattribs={'layer': layer, 'color': colors.CYAN})
    msp.add_text("Tablero BT", dxfattribs={'layer': layer, 'height': 1.8, 'insert': (x_tab + 1.5, y_tab + h_tb + 2.0), 'color': colors.CYAN})

    # Tubería F°G° 2" de bajada al tablero
    msp.add_line((cx + 5.0, y_tapa), (cx + d_biposte/2.0 + 10.0, y_tab + h_tb), dxfattribs={'layer': layer, 'color': colors.WHITE})

    # Cotas
    add_cota_h(msp, cx - d_biposte/2.0, cx + d_biposte/2.0, y_ntn - 8.0, "2.00 m (Entre Ejes)", layer=layer)
    add_cota_v(msp, y_ntn, y_plat, cx - d_biposte/2.0 - 15.0, "3.50 m (Plataforma)", layer=layer)
    add_cota_v(msp, y_base, y_cima, cx + d_biposte/2.0 + 28.0, "13.00 m (Ht)", layer=layer)

    # Llamadas
    add_llamada(msp, cx - d_biposte/2.0, y_cima - 5.0, cx - 60.0, y_cima + 6.0, "Biposte 2xCAC 13/400 daN", num_item=1, layer=layer)
    add_llamada(msp, cx - 16.0, y_prot + 6.0, cx - 60.0, y_prot + 8.0, "Cut-Out 15 kV / 100 A", num_item=2, layer=layer)
    add_llamada(msp, cx - 22.0, y_prot - 5.0, cx - 60.0, y_prot - 8.0, "Pararrayos ZnO 12 kV/10 kA", num_item=3, layer=layer)
    add_llamada(msp, cx, y_plat + 12.0, cx - 55.0, y_plat + 18.0, "Trafo Dyn5 50/100 kVA ONAN", num_item=4, layer=layer)
    add_llamada(msp, cx - w_pl/2.0, y_plat, cx - 55.0, y_plat + 4.0, "Plataforma UPN 120x2.4m", num_item=5, layer=layer)
    add_llamada(msp, x_tab + w_tb, y_tab + 10.0, cx + 55.0, y_tab + 12.0, "Tablero BT IP54 c/MCCB", num_item=6, layer=layer)

    items_sab = [
        (1, "Poste Concreto Centrifugado 13/400 (biposte)", "NTP 339.027", "2 und"),
        (2, "Plataforma soporte UPN 120 galvanizada", "ASTM A36", "1 jgo"),
        (3, "Transformador trifásico 100 kVA 10/0.38 kV", "NTP 370.002", "1 und"),
        (4, "Cortacircuito fusible Cut-Out 15 kV/100 A", "IEC 60282", "3 und"),
        (5, "Pararrayos óxido de zinc ZnO 12 kV / 10 kA", "IEC 60099", "3 und"),
        (6, "Cruceta maniobra F°G° 100x100x6.4x2.50 m", "ASTM A123", "1 und"),
        (7, "Tablero distribución BT IP54 c/termo 160A", "IEC 60439", "1 und"),
        (8, "Tubo acero galvanizado F°G° 2\" x 3.0 m", "ASTM A53", "2 und"),
        (9, "Cable de energía N2XOH 0.6/1 kV 3x70+35", "NTP 370.252", "16 m"),
        (10, "Sistema PAT doble (protección y neutro BT)", "CNE Regla 261", "2 jgo")
    ]
    y_fin_t = dibujar_tabla_materiales_vectorial(msp, x0 + 198.0, y0 + h - 28.0, 138.0, items_sab, "PLANILLA DE MATERIALES DGE — SUBESTACIÓN SAB")

    notas_sab = [
        "1. Estructura para SED-01 (50 kVA), SED-02 (100 kVA) y SED-03 (100 kVA).",
        "2. Altura libre mínima de la plataforma sobre el suelo: 3.50 m.",
        "3. Doble sistema PAT independiente separados más de 20 m (R <= 10 Ω).",
        "4. Enclavamiento mecánico en tablero BT y fusibles tipo K calibrados."
    ]
    dibujar_notas_tecnicas(msp, x0 + 198.0, y_fin_t - 4.0, 138.0, notas_sab)


# -------------------------------------------------------------------------
# BLOQUE 5: ESTRUCTURA E-1 RED SECUNDARIA CAAI Y ALUMBRADO PÚBLICO
# -------------------------------------------------------------------------
def generar_vector_e1_bt(msp, x0, y0, w=340.0, h=250.0):
    dibujar_marco_lamina_detalle(msp, x0, y0, w, h, "ESTRUCTURA E-1 BT", "RED SECUNDARIA CAAI 380/220 V Y ALUMBRADO PÚBLICO LED 50 W", "R.D. N° 023-2003-EM-DGE LÁMINA 001 Y 002")
    layer = '10_DETALLES_ESTRUCTURAS_DGE'

    cx = x0 + 85.0
    y_base = y0 + 35.0
    y_ntn = y0 + 58.0
    y_cima = y0 + 185.0

    dibujar_cimentacion_ciclopea(msp, cx, y_base, y_ntn, w_cim=18.0)

    # Poste CAC 8/200 o 9/300
    r_base, r_cima = 3.2, 1.5
    msp.add_lwpolyline([
        (cx - r_base, y_base), (cx + r_base, y_base),
        (cx + r_cima, y_cima), (cx - r_cima, y_cima),
        (cx - r_base, y_base)
    ], dxfattribs={'layer': layer, 'color': colors.WHITE})
    msp.add_arc((cx, y_cima), radius=r_cima, start_angle=0, end_angle=180, dxfattribs={'layer': layer, 'color': colors.WHITE})

    # PASTORAL Y LUMINARIA LED DE ALUMBRADO PÚBLICO EN LA CIMA
    # Brazo de tubo F°G° 1 1/2" curvado
    px_pastoral = cx + 24.0
    py_pastoral = y_cima + 14.0
    msp.add_lwpolyline([(cx, y_cima - 4.0), (cx + 8.0, y_cima + 6.0), (px_pastoral, py_pastoral)],
                       dxfattribs={'layer': layer, 'color': 30})
    # Abrazaderas del pastoral
    msp.add_lwpolyline([(cx - 2.5, y_cima - 5.0), (cx + 2.5, y_cima - 5.0),
                        (cx + 2.5, y_cima - 2.0), (cx - 2.5, y_cima - 2.0), (cx - 2.5, y_cima - 5.0)],
                       dxfattribs={'layer': layer, 'color': colors.YELLOW})
    # Luminaria LED 50 W IP66
    msp.add_lwpolyline([
        (px_pastoral, py_pastoral - 1.5), (px_pastoral + 10.0, py_pastoral - 1.5),
        (px_pastoral + 12.0, py_pastoral + 2.5), (px_pastoral, py_pastoral + 2.5),
        (px_pastoral, py_pastoral - 1.5)
    ], dxfattribs={'layer': layer, 'color': colors.YELLOW})
    # Fotocélula electrónica superior
    msp.add_circle((px_pastoral + 5.0, py_pastoral + 3.5), radius=1.0, dxfattribs={'layer': layer, 'color': colors.CYAN})
    # Haz luminoso cónico punteado
    msp.add_line((px_pastoral + 2.0, py_pastoral - 1.5), (px_pastoral - 15.0, y_ntn), dxfattribs={'layer': layer, 'color': 252})
    msp.add_line((px_pastoral + 10.0, py_pastoral - 1.5), (px_pastoral + 30.0, y_ntn), dxfattribs={'layer': layer, 'color': 252})

    # GRAPA DE SUSPENSIÓN Y HAZ DE CABLE AUTOPORTANTE CAAI A H = 7.0 m
    y_caai = y_cima - 18.0
    # Perno con ojo / abrazadera
    msp.add_lwpolyline([(cx - 2.2, y_caai - 1.2), (cx + 2.2, y_caai - 1.2),
                        (cx + 2.2, y_caai + 1.2), (cx - 2.2, y_caai + 1.2), (cx - 2.2, y_caai - 1.2)],
                       dxfattribs={'layer': layer, 'color': colors.YELLOW})
    # Grapa de suspensión termoplástica
    msp.add_circle((cx + 4.5, y_caai), radius=1.8, dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Conductor CAAI pasando perpendicularmente
    msp.add_circle((cx + 4.5, y_caai), radius=1.0, dxfattribs={'layer': layer, 'color': colors.GREEN})
    # Vano longitudinal del cable CAAI saliendo a ambos lados
    msp.add_line((cx + 4.5 - 20.0, y_caai), (cx + 4.5 + 20.0, y_caai), dxfattribs={'layer': layer, 'color': colors.GREEN})

    # Conectores IPC de derivación de alumbrado público
    msp.add_circle((cx + 4.5, y_caai + 3.5), radius=0.8, dxfattribs={'layer': layer, 'color': colors.YELLOW})
    msp.add_line((cx + 4.5, y_caai + 3.5), (cx + 2.0, y_cima - 2.0), dxfattribs={'layer': layer, 'color': colors.WHITE})

    # Cotas
    add_cota_v(msp, y_base, y_cima, cx + 45.0, "8.00 / 9.00 m (Ht)", layer=layer)
    add_cota_v(msp, y_base, y_ntn, cx + 32.0, "1.40 m (He)", layer=layer)
    add_cota_v(msp, y_ntn, y_caai, cx - 18.0, "6.80 m (H_caai)", layer=layer)
    add_cota_h(msp, cx, px_pastoral + 10.0, py_pastoral + 8.0, "1.50 m (Pastoral)", layer=layer)

    # Llamadas
    add_llamada(msp, cx + r_cima, y_cima - 8.0, cx - 45.0, y_cima - 2.0, "Poste CAC 8/200 o 9/300", num_item=1, layer=layer)
    add_llamada(msp, px_pastoral + 5.0, py_pastoral, cx + 45.0, py_pastoral + 6.0, "Luminaria LED 50 W IP66", num_item=2, layer=layer)
    add_llamada(msp, cx + 12.0, y_cima + 8.0, cx - 45.0, y_cima + 14.0, "Pastoral F°G° 1.5\" x 1.5 m", num_item=3, layer=layer)
    add_llamada(msp, cx + 4.5, y_caai, cx + 35.0, y_caai - 4.0, "Grapa suspensión neutro", num_item=4, layer=layer)
    add_llamada(msp, cx + 4.5 + 10.0, y_caai, cx + 35.0, y_caai + 8.0, "Cable CAAI 3x35+1x16+NA25", num_item=5, layer=layer)
    add_llamada(msp, cx + 4.5, y_caai + 3.5, cx - 45.0, y_caai + 6.0, "Conector IPC bimetálico", num_item=6, layer=layer)

    items_e1 = [
        (1, "Poste Concreto Centrifugado 8/200 o 9/300", "NTP 339.027", "1 und"),
        (2, "Cable autoportante CAAI 3x35+1x16+NA25", "NTP 370.254", "Vano m"),
        (3, "Grapa de suspensión termoplástica neutro", "IEC 61284", "1 und"),
        (4, "Brazo pastoral acero F°G° 1 1/2\" x 1.50 m", "ASTM A123", "1 und"),
        (5, "Luminaria LED 50 W 6,500 lm c/fotocélula", "R.D. 017-2003", "1 und"),
        (6, "Conector cuña / perforación IPC Al-Cu", "NTP 370.258", "2 und"),
        (7, "Abrazadera platina F°G° 2 vías p/poste", "ASTM A36", "1 jgo"),
        (8, "Cinta de acero inoxidable Band-It 3/4\"", "ASTM A240", "2 m")
    ]
    y_fin_t = dibujar_tabla_materiales_vectorial(msp, x0 + 198.0, y0 + h - 28.0, 138.0, items_e1, "PLANILLA DE MATERIALES DGE — ESTRUCTURA E-1")

    notas_e1 = [
        "1. Estructura de alineamiento para red secundaria urbana y alumbrado.",
        "2. Interdistancia media entre luminarias: 30.0 m (cumple RD 017-2003).",
        "3. Tensión exclusiva sobre neutro portador NA 25 mm² de aleación Al.",
        "4. Control fotosensible individual crepuscular por fotocélula electrónica."
    ]
    dibujar_notas_tecnicas(msp, x0 + 198.0, y_fin_t - 4.0, 138.0, notas_e1)


# -------------------------------------------------------------------------
# BLOQUE 6: RETENIDA MECÁNICA NORMALIZADA (CNE REGLA 261 / DGE)
# -------------------------------------------------------------------------
def generar_vector_retenida(msp, x0, y0, w=340.0, h=250.0):
    dibujar_marco_lamina_detalle(msp, x0, y0, w, h, "RETENIDA NORMALIZADA", "RETENIDA SIMPLE INCLINADA Y ELEMENTOS DE ANCLAJE", "CNE REGLA 261 / R.D. N° 024 LÁM. 074 / R.D. N° 023 LÁM. 014")
    layer = '10_DETALLES_ESTRUCTURAS_DGE'

    cx = x0 + 55.0
    y_base = y0 + 35.0
    y_ntn = y0 + 60.0
    y_cima = y0 + 205.0

    # Poste de concreto referencial
    msp.add_lwpolyline([(cx - 3.2, y_base), (cx + 3.2, y_base),
                        (cx + 1.8, y_cima), (cx - 1.8, y_cima), (cx - 3.2, y_base)],
                       dxfattribs={'layer': layer, 'color': colors.WHITE})
    msp.add_line((cx - 20.0, y_ntn), (cx + 120.0, y_ntn), dxfattribs={'layer': layer, 'color': colors.YELLOW})
    msp.add_text("Nivel de Terreno Natural (±0.00)", dxfattribs={'layer': layer, 'height': 2.1, 'insert': (cx + 35.0, y_ntn + 1.2), 'color': colors.YELLOW})

    # Abrazadera en poste a H = 10.0 m (Y = y_cima - 15.0)
    y_abraz = y_cima - 15.0
    msp.add_lwpolyline([(cx - 3.6, y_abraz - 2.0), (cx + 3.6, y_abraz - 2.0),
                        (cx + 3.6, y_abraz + 2.0), (cx - 3.6, y_abraz + 2.0), (cx - 3.6, y_abraz - 2.0)],
                       dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # Perno con ojal guardacabo
    msp.add_circle((cx + 4.5, y_abraz), radius=1.0, dxfattribs={'layer': layer, 'color': colors.WHITE})

    # Punto de anclaje en el suelo (ángulo 45°)
    px_ancla = cx + 80.0
    py_ancla = y_ntn

    # Cable de acero Siemens Martin 5/16"
    msp.add_line((cx + 4.5, y_abraz), (px_ancla, py_ancla), dxfattribs={'layer': layer, 'color': colors.MAGENTA})

    # 3 Grapas prensacables Crosby superiores en el lazo
    for g_f in [0.08, 0.12, 0.16]:
        gx = cx + 4.5 + g_f * (px_ancla - cx)
        gy = y_abraz - g_f * (y_abraz - py_ancla)
        msp.add_circle((gx, gy), radius=0.7, dxfattribs={'layer': layer, 'color': colors.WHITE})

    # Aislador nuez ANSI 54-1 a H >= 3.0 m (a 60% de longitud)
    px_nuez = cx + 4.5 + 0.58 * (px_ancla - cx)
    py_nuez = y_abraz - 0.58 * (y_abraz - py_ancla)
    # Dibujo detallado de la nuez de porcelana (rombo con gargantas cruzadas)
    msp.add_lwpolyline([
        (px_nuez, py_nuez + 3.2), (px_nuez + 3.2, py_nuez),
        (px_nuez, py_nuez - 3.2), (px_nuez - 3.2, py_nuez),
        (px_nuez, py_nuez + 3.2)
    ], dxfattribs={'layer': layer, 'color': colors.YELLOW})
    msp.add_circle((px_nuez, py_nuez), radius=1.0, dxfattribs={'layer': layer, 'color': colors.WHITE})

    # Tubo protector de PVC rígido amarillo 1.80 m
    px_pvc_top = px_ancla - 16.0
    py_pvc_top = py_ancla + 16.0
    pl_pvc = msp.add_lwpolyline([(px_pvc_top, py_pvc_top), (px_ancla, py_ancla)], dxfattribs={'layer': layer, 'color': colors.YELLOW})
    pl_pvc.dxf.const_width = 1.4

    # Varilla de ancla de 5/8" x 2.0 m prolongándose bajo tierra
    px_cav = px_ancla + 18.0
    py_cav = py_ancla - 22.0
    msp.add_line((px_ancla, py_ancla), (px_cav, py_cav), dxfattribs={'layer': layer, 'color': colors.WHITE})

    # Bloque de anclaje de concreto CAV 0.50x0.50x0.20 m
    msp.add_lwpolyline([
        (px_cav - 8.0, py_cav - 3.5), (px_cav + 8.0, py_cav - 3.5),
        (px_cav + 8.0, py_cav + 3.5), (px_cav - 8.0, py_cav + 3.5),
        (px_cav - 8.0, py_cav - 3.5)
    ], dxfattribs={'layer': layer, 'color': colors.MAGENTA})
    # Arandela y tuercas en el fondo
    msp.add_line((px_cav - 4.0, py_cav - 4.2), (px_cav + 4.0, py_cav - 4.2), dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # Excavación y terreno compactado
    msp.add_lwpolyline([
        (px_ancla + 6.0, py_ancla), (px_cav - 10.0, py_cav - 5.0),
        (px_cav + 10.0, py_cav - 5.0), (px_ancla + 24.0, py_ancla)
    ], dxfattribs={'layer': layer, 'color': 252})

    # Cotas
    add_cota_v(msp, py_ancla, py_nuez, px_nuez - 15.0, "H >= 3.00 m (Aislador)", layer=layer)
    add_cota_v(msp, py_cav, py_ancla, px_cav + 16.0, "h = 1.80 m (Empotramiento)", layer=layer)
    add_cota_h(msp, cx, px_ancla, py_ancla - 10.0, "d = 10.00 m (Ángulo 45°)", layer=layer)

    # Llamadas
    add_llamada(msp, cx + 4.5, y_abraz, cx - 25.0, y_abraz + 6.0, "Abrazadera CAS doble platina", num_item=1, layer=layer)
    add_llamada(msp, cx + 25.0, y_abraz - 20.0, cx - 25.0, y_abraz - 12.0, "Cable Siemens Martin 5/16\"", num_item=2, layer=layer)
    add_llamada(msp, px_nuez, py_nuez, px_nuez - 25.0, py_nuez + 12.0, "Aislador nuez ANSI 54-1", num_item=3, layer=layer)
    add_llamada(msp, px_ancla - 8.0, py_ancla + 8.0, px_ancla - 30.0, py_ancla + 25.0, "Protector PVC amarillo 1.8m", num_item=4, layer=layer)
    add_llamada(msp, px_ancla + 8.0, py_ancla - 10.0, px_ancla + 30.0, py_ancla - 4.0, "Varilla ancla F°G° 5/8\"x2.0m", num_item=5, layer=layer)
    add_llamada(msp, px_cav, py_cav, px_cav + 25.0, py_cav - 12.0, "Bloque concreto CAV 0.50x0.50", num_item=6, layer=layer)

    items_ret = [
        (1, "Cable acero galvanizado SM 5/16\" (7 hilos)", "ASTM A363", "25 m"),
        (2, "Aislador tracción nuez porcelana ANSI 54-1", "ANSI C29.4", "1 und"),
        (3, "Varilla ancla F°G° 5/8\"x2.0m c/guardacabo", "ASTM A153", "1 und"),
        (4, "Bloque anclaje concreto CAV 0.50x0.50x0.20", "DGE Lám.074", "1 und"),
        (5, "Tubo protector PVC rígido amarillo 1.5\"x1.8m", "NTP 399.002", "1 und"),
        (6, "Grapas prensacables Crosby 5/16\" forjadas", "Fed.Spec.", "6 und"),
        (7, "Guardacabo acero forjado galvanizado 5/16\"", "ASTM A153", "2 und"),
        (8, "Abrazadera partida CAS platina 50x6 mm", "ASTM A36", "1 jgo")
    ]
    y_fin_t = dibujar_tabla_materiales_vectorial(msp, x0 + 198.0, y0 + h - 28.0, 138.0, items_ret, "PLANILLA DE MATERIALES DGE — RETENIDA INCLINADA")

    notas_ret = [
        "1. Diseñada según Regla 261 del Código Nacional de Electricidad 2011.",
        "2. Aislador nuez ubicado obligatoriamente a más de 3.00 m de altura.",
        "3. Tubo protector amarillo garantiza visibilidad y advertencia peatonal.",
        "4. Bloque CAV empotrado a 1.80 m con relleno compactado al 95% Proctor."
    ]
    dibujar_notas_tecnicas(msp, x0 + 198.0, y_fin_t - 4.0, 138.0, notas_ret)


# -------------------------------------------------------------------------
# BLOQUE 7: POZO DE PUESTA A TIERRA (PAT)
# -------------------------------------------------------------------------
def generar_vector_pat(msp, x0, y0, w=340.0, h=250.0):
    dibujar_marco_lamina_detalle(msp, x0, y0, w, h, "PUESTA A TIERRA (PAT)", "POZO VERTICAL CON ELECTRODO Y TRATAMIENTO ELECTROLÍTICO", "R.D. N° 024-2003-EM/DGE LÁMINA 077 / RD 023 LÁM 012")
    layer = '10_DETALLES_ESTRUCTURAS_DGE'

    cx = x0 + 85.0
    y_fondo = y0 + 35.0
    y_ntn = y0 + 165.0

    # Terreno natural
    msp.add_line((cx - 50.0, y_ntn), (cx + 50.0, y_ntn), dxfattribs={'layer': layer, 'color': colors.YELLOW})
    msp.add_text("Nivel de Terreno Natural (±0.00)", dxfattribs={'layer': layer, 'height': 2.1, 'insert': (cx + 25.0, y_ntn + 1.5), 'color': colors.YELLOW})

    # POZO CILÍNDRICO EXCAVADO (D = 0.80 m x H = 2.60 m)
    w_pozo = 32.0  # 0.80 m a escala
    msp.add_lwpolyline([
        (cx - w_pozo/2.0, y_ntn), (cx - w_pozo/2.0, y_fondo),
        (cx + w_pozo/2.0, y_fondo), (cx + w_pozo/2.0, y_ntn)
    ], dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # Achurado de tierra de chacra cernida con bentonita sódica
    for py_h in range(int(y_fondo) + 5, int(y_ntn) - 15, 12):
        msp.add_line((cx - w_pozo/2.0 + 2.0, py_h), (cx + w_pozo/2.0 - 2.0, py_h), dxfattribs={'layer': layer, 'color': 252})
        msp.add_circle((cx - 6.0, py_h + 4.0), radius=0.6, dxfattribs={'layer': layer, 'color': colors.YELLOW})
        msp.add_circle((cx + 7.0, py_h + 6.0), radius=0.6, dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # CAJA DE REGISTRO DE CONCRETO PREFABRICADO (0.40 x 0.40 x 0.30 m)
    w_caj = 20.0
    h_caj = 15.0
    msp.add_lwpolyline([
        (cx - w_caj/2.0, y_ntn - h_caj), (cx + w_caj/2.0, y_ntn - h_caj),
        (cx + w_caj/2.0, y_ntn + 3.0), (cx - w_caj/2.0, y_ntn + 3.0),
        (cx - w_caj/2.0, y_ntn - h_caj)
    ], dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Tapa de concreto con asas de bronce
    msp.add_lwpolyline([
        (cx - w_caj/2.0 - 1.5, y_ntn + 3.0), (cx + w_caj/2.0 + 1.5, y_ntn + 3.0),
        (cx + w_caj/2.0 + 1.5, y_ntn + 5.5), (cx - w_caj/2.0 - 1.5, y_ntn + 5.5),
        (cx - w_caj/2.0 - 1.5, y_ntn + 3.0)
    ], dxfattribs={'layer': layer, 'color': colors.WHITE})
    msp.add_text("P.A.T.", dxfattribs={'layer': layer, 'height': 1.8, 'insert': (cx - 4.0, y_ntn + 3.6), 'color': colors.CYAN})

    # ELECTRODO VERTICAL COPPERWELD (5/8" x 2.40 m)
    pl_el = msp.add_lwpolyline([(cx, y_fondo + 4.0), (cx, y_ntn - 4.0)], dxfattribs={'layer': layer, 'color': colors.RED})
    pl_el.dxf.const_width = 1.2
    # Punta biselada en el fondo
    msp.add_lwpolyline([(cx - 1.0, y_fondo + 4.0), (cx + 1.0, y_fondo + 4.0), (cx, y_fondo), (cx - 1.0, y_fondo + 4.0)],
                       dxfattribs={'layer': layer, 'color': colors.RED})

    # CONECTOR DE BRONCE TIPO AB
    y_con = y_ntn - 6.0
    msp.add_lwpolyline([(cx - 2.5, y_con - 2.0), (cx + 2.5, y_con - 2.0),
                        (cx + 2.5, y_con + 2.0), (cx - 2.5, y_con + 2.0), (cx - 2.5, y_con - 2.0)],
                       dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # Conductor de cobre desnudo 35 mm² saliendo en tubo PVC
    msp.add_line((cx, y_con), (cx - 35.0, y_ntn + 25.0), dxfattribs={'layer': layer, 'color': colors.GREEN})
    msp.add_text("Tubo PVC 3/4\" hacia poste", dxfattribs={'layer': layer, 'height': 1.8, 'insert': (cx - 42.0, y_ntn + 15.0), 'color': colors.GREEN})

    # Cotas
    add_cota_v(msp, y_fondo, y_ntn, cx + w_pozo/2.0 + 12.0, "2.60 m (H pozo)", layer=layer)
    add_cota_v(msp, y_fondo + 4.0, y_ntn - 4.0, cx - w_pozo/2.0 - 12.0, "2.40 m (Electrodo)", layer=layer)
    add_cota_h(msp, cx - w_pozo/2.0, cx + w_pozo/2.0, y_fondo - 8.0, "0.80 m (Diámetro)", layer=layer)
    add_cota_h(msp, cx - w_caj/2.0, cx + w_caj/2.0, y_ntn + 10.0, "0.40 x 0.40 m", layer=layer)

    # Llamadas
    add_llamada(msp, cx - w_caj/2.0, y_ntn, cx - 45.0, y_ntn + 8.0, "Caja registro concreto prefabricado", num_item=1, layer=layer)
    add_llamada(msp, cx, y_con, cx + 25.0, y_con + 4.0, "Conector bronce alta presión AB", num_item=2, layer=layer)
    add_llamada(msp, cx, y_fondo + 60.0, cx + 25.0, y_fondo + 65.0, "Electrodo Copperweld 5/8\"x2.4m", num_item=3, layer=layer)
    add_llamada(msp, cx - 8.0, y_fondo + 35.0, cx - 45.0, y_fondo + 40.0, "Relleno bentonita sódica + gel", num_item=4, layer=layer)
    add_llamada(msp, cx - 20.0, y_ntn + 10.0, cx - 48.0, y_ntn + 22.0, "Cable Cu recocido desnudo 35 mm²", num_item=5, layer=layer)

    items_pat = [
        (1, "Electrodo cobre Copperweld 5/8\"x2.40 m", "NTP 370.053", "1 und"),
        (2, "Conector bronce alta presión tipo AB 5/8\"", "ASTM B148", "1 und"),
        (3, "Conductor cobre recocido desnudo 35 mm²", "NTP 370.043", "8 m"),
        (4, "Caja registro concreto 0.40x0.40x0.30 m c/tapa", "DGE Lám.077", "1 und"),
        (5, "Bentonita sódica para tratamiento (25 kg)", "API 13A", "2 sacos"),
        (6, "Dosis sales electrolíticas Thor-Gel / Lab-Gel", "Químico", "1 dosis"),
        (7, "Tierra de chacra cernida para relleno", "Agrícola", "1.5 m³"),
        (8, "Tubo de protección PVC pesado SAP 3/4\"x3m", "NTP 399.002", "1 und")
    ]
    y_fin_t = dibujar_tabla_materiales_vectorial(msp, x0 + 198.0, y0 + h - 28.0, 138.0, items_pat, "PLANILLA DE MATERIALES DGE — POZO P.A.T.")

    notas_pat = [
        "1. Resistencia máxima exigida: R <= 10 Ω en SEDs y R <= 25 Ω en redes BT.",
        "2. Aplicar dosis de bentonita y gel hidratados con agua desmineralizada.",
        "3. Conexión de cable al electrodo limpia y libre de óxido antes de apretar.",
        "4. Medición obligatoria con telurómetro calibrado previa a la puesta en marcha."
    ]
    dibujar_notas_tecnicas(msp, x0 + 198.0, y_fin_t - 4.0, 138.0, notas_pat)


# -------------------------------------------------------------------------
# BLOQUE 8: ACOMETIDA DOMICILIARIA MONOFÁSICA AÉREA TIPO L-T
# -------------------------------------------------------------------------
def generar_vector_acometida(msp, x0, y0, w=340.0, h=250.0):
    dibujar_marco_lamina_detalle(msp, x0, y0, w, h, "ACOMETIDA L-T", "ACOMETIDA DOMICILIARIA MONOFÁSICA AÉREA CON CABLE CONCÉNTRICO", "R.D. N° 023-2003-EM-DGE LÁMINAS 007 Y 008")
    layer = '10_DETALLES_ESTRUCTURAS_DGE'

    # Izquierda: Poste de red secundaria / Derecha: Fachada predial
    x_post = x0 + 35.0
    x_fach = x0 + 130.0
    y_ntn = y0 + 60.0
    y_red = y0 + 180.0

    # Terreno y vereda
    msp.add_line((x_post - 20.0, y_ntn), (x_fach + 45.0, y_ntn), dxfattribs={'layer': layer, 'color': colors.YELLOW})
    msp.add_text("Nivel de Calzada / Vereda (±0.00)", dxfattribs={'layer': layer, 'height': 2.1, 'insert': (x_post + 30.0, y_ntn + 1.2), 'color': colors.YELLOW})

    # Poste CAC referencial
    msp.add_lwpolyline([(x_post - 2.8, y_ntn - 15.0), (x_post + 2.8, y_ntn - 15.0),
                        (x_post + 1.6, y_red + 15.0), (x_post - 1.6, y_red + 15.0), (x_post - 2.8, y_ntn - 15.0)],
                       dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Red CAAI en el poste
    msp.add_circle((x_post + 3.0, y_red), radius=1.6, dxfattribs={'layer': layer, 'color': colors.GREEN})
    msp.add_text("Red CAAI", dxfattribs={'layer': layer, 'height': 1.8, 'insert': (x_post - 20.0, y_red), 'color': colors.GREEN})

    # Fachada de la vivienda (muro de ladrillo / concreto)
    msp.add_lwpolyline([(x_fach, y_ntn), (x_fach + 30.0, y_ntn),
                        (x_fach + 30.0, y0 + 215.0), (x_fach, y0 + 215.0), (x_fach, y_ntn)],
                       dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Líneas de textura muro
    for py_m in range(int(y_ntn) + 15, int(y0 + 210.0), 20):
        msp.add_line((x_fach, py_m), (x_fach + 30.0, py_m), dxfattribs={'layer': layer, 'color': 252})

    # MÁSTIL DE INGRESO TUBO F°G° 1" x 2.50 m
    y_anclaje_fach = y0 + 195.0
    msp.add_lwpolyline([(x_fach - 1.5, y_anclaje_fach - 35.0), (x_fach - 1.5, y_anclaje_fach),
                        (x_fach + 0.5, y_anclaje_fach), (x_fach + 0.5, y_anclaje_fach - 35.0)],
                       dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Gorreta de servicio / cabezal intemperie
    msp.add_arc((x_fach - 0.5, y_anclaje_fach), radius=2.5, start_angle=0, end_angle=180, dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # Catenaria de cable concéntrico SET 2x4 mm² desde el poste al mástil
    p_ini = (x_post + 3.0, y_red)
    p_fin = (x_fach - 1.5, y_anclaje_fach)
    # 5 segmentos aproximando catenaria
    pts_cat = [p_ini]
    for step in range(1, 5):
        f = step / 5.0
        xf = p_ini[0] + f * (p_fin[0] - p_ini[0])
        yf = p_ini[1] + f * (p_fin[1] - p_ini[1]) - 4.0 * math.sin(f * math.pi)
        pts_cat.append((xf, yf))
    pts_cat.append(p_fin)
    msp.add_lwpolyline(pts_cat, dxfattribs={'layer': layer, 'color': colors.CYAN})

    # Tubo de bajada adosado F°G° 3/4" hacia la caja portamedidor
    y_caja = y_ntn + 28.0  # H = 1.40 m sobre vereda
    msp.add_line((x_fach + 2.0, y_anclaje_fach - 35.0), (x_fach + 2.0, y_caja + 16.0), dxfattribs={'layer': layer, 'color': colors.WHITE})
    # Abrazaderas tipo omega cada 1.0 m
    for py_om in [y_caja + 22.0, y_caja + 40.0, y_anclaje_fach - 30.0]:
        msp.add_circle((x_fach + 2.0, py_om), radius=0.8, dxfattribs={'layer': layer, 'color': colors.YELLOW})

    # CAJA PORTAMEDIDOR MONOFÁSICA TIPO L-T (0.35 x 0.22 x 0.18 m)
    w_cj, h_cj = 12.0, 16.0
    x_cj = x_fach + 2.0
    msp.add_lwpolyline([(x_cj, y_caja), (x_cj + w_cj, y_caja),
                        (x_cj + w_cj, y_caja + h_cj), (x_cj, y_caja + h_cj), (x_cj, y_caja)],
                       dxfattribs={'layer': layer, 'color': colors.YELLOW})
    # Visor transparente de policarbonato
    msp.add_lwpolyline([(x_cj + 2.0, y_caja + 7.0), (x_cj + w_cj - 2.0, y_caja + 7.0),
                        (x_cj + w_cj - 2.0, y_caja + h_cj - 2.0), (x_cj + 2.0, y_caja + h_cj - 2.0),
                        (x_cj + 2.0, y_caja + 7.0)], dxfattribs={'layer': layer, 'color': colors.CYAN})
    # Símbolo medidor kWh
    msp.add_circle((x_cj + w_cj/2.0, y_caja + 11.0), radius=2.2, dxfattribs={'layer': layer, 'color': colors.WHITE})
    msp.add_text("kWh", dxfattribs={'layer': layer, 'height': 1.4, 'insert': (x_cj + 4.0, y_caja + 10.3), 'color': colors.WHITE})
    # Termomagnético 2x16A en la parte inferior
    msp.add_lwpolyline([(x_cj + 3.0, y_caja + 2.0), (x_cj + 9.0, y_caja + 2.0),
                        (x_cj + 9.0, y_caja + 5.5), (x_cj + 3.0, y_caja + 5.5), (x_cj + 3.0, y_caja + 2.0)],
                       dxfattribs={'layer': layer, 'color': colors.RED})

    # Puesta a tierra domiciliaria con varilla Cu 1/2" x 1.5 m
    msp.add_line((x_cj + w_cj/2.0, y_caja), (x_cj + w_cj/2.0, y_ntn - 12.0), dxfattribs={'layer': layer, 'color': colors.GREEN})

    # Cotas
    add_cota_v(msp, y_ntn, y_caja + h_cj/2.0, x_cj + w_cj + 6.0, "1.40 m (H visor)", layer=layer)
    add_cota_v(msp, y_ntn, y_anclaje_fach, x_fach - 12.0, "5.50 m (H ingreso)", layer=layer)
    add_cota_h(msp, x_post, x_fach, y_ntn - 8.0, "Vano L <= 15 m (Corta) / <= 30 m (Larga)", layer=layer)

    # Llamadas
    add_llamada(msp, x_post + 3.0, y_red, x_post - 25.0, y_red + 8.0, "Conector IPC bimetálico derivación", num_item=1, layer=layer)
    add_llamada(msp, (x_post + x_fach)/2.0, y_red - 5.0, (x_post + x_fach)/2.0 - 15.0, y_red + 16.0, "Cable concéntrico SET 2x4 mm²", num_item=2, layer=layer)
    add_llamada(msp, x_fach - 0.5, y_anclaje_fach, x_fach - 30.0, y_anclaje_fach + 10.0, "Mástil F°G° 1\" c/gorreta intemperie", num_item=3, layer=layer)
    add_llamada(msp, x_cj + w_cj/2.0, y_caja + 11.0, x_fach + 35.0, y_caja + 14.0, "Medidor estático 220V 5(60)A Cl.1", num_item=4, layer=layer)
    add_llamada(msp, x_cj + 6.0, y_caja + 3.5, x_fach + 35.0, y_caja + 4.0, "Termomagnético 2x16A Curva C", num_item=5, layer=layer)
    add_llamada(msp, x_cj, y_caja + 8.0, x_fach - 28.0, y_caja + 8.0, "Caja policarbonato tipo L-T", num_item=6, layer=layer)

    items_ac = [
        (1, "Caja portamedidor monofásica tipo L-T PRFV", "NTP 370.054", "1 und"),
        (2, "Medidor estático monofásico 220 V 5(60) A Cl.1", "IEC 62053-21", "1 und"),
        (3, "Interruptor termomagnético 2x16A 6kA Curva C", "IEC 60898", "1 und"),
        (4, "Cable concéntrico bipolar cobre SET 2x4 mm²", "NTP 370.050", "15 m"),
        (5, "Mástil soporte acometida F°G° 1\" x 2.50 m", "ASTM A53", "1 und"),
        (6, "Cabezal de servicio intemperie de Al 1\"", "ASTM A153", "1 und"),
        (7, "Conector perforación aislamiento IPC 25/4", "NTP 370.258", "2 und"),
        (8, "Electrodo puesta a tierra cobre 1/2\"x1.5 m", "NTP 370.053", "1 jgo")
    ]
    y_fin_t = dibujar_tabla_materiales_vectorial(msp, x0 + 198.0, y0 + h - 28.0, 138.0, items_ac, "PLANILLA DE MATERIALES DGE — ACOMETIDA L-T")

    notas_ac = [
        "1. Para los 587 predios catastrados (534 cortas y 53 largas).",
        "2. Altura de visor de caja L-T a 1.40 m sobre el nivel de vereda terminada.",
        "3. Caída de tensión máxima en la acometida más crítica: ΔV = 0.35% <= 1.50%.",
        "4. Interruptor termomagnético calibrado para demanda contratada de 350 W."
    ]
    dibujar_notas_tecnicas(msp, x0 + 198.0, y_fin_t - 4.0, 138.0, notas_ac)
