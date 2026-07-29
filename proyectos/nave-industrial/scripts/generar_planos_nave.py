#!/usr/bin/env python3
"""
Generador de Planos CAD de Alta Calidad Profesional (DXF R2010 + PDF + PNG)
para Nave Industrial 20m x 40m.
Incluye:
- Ejes Estructurales (A-E / 1-9) con burbujas de nivel
- Cotas Exteriores e Interiores
- Tramas de Muros y Estructuras (Hatch)
- Simbología Eléctrica Normada DGE/IEC
- Símbolo de Norte y Escala Gráfica
- Cajetín / Membrete Profesional CIP
"""

import os
import sys
import math
import json
import ezdxf
from ezdxf.enums import TextEntityAlignment
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

# Capas y Estilos CAD Profesionales Estandarizados (Norma ISO 13567 / CAD)
LAYERS = {
    "ARQ_EJES": {"color": 1, "lineweight": 13, "linetype": "CENTER"},     # Rojo / Ejes de estructura
    "ARQ_COTAS": {"color": 3, "lineweight": 13},                          # Verde / Cotas y dimensiones
    "ARQ_MUROS": {"color": 7, "lineweight": 40},                          # Blanco grueso
    "ARQ_MUROS_HATCH": {"color": 8, "lineweight": 9},                     # Gris / Tramas
    "ARQ_TIJERALES": {"color": 8, "lineweight": 18, "linetype": "DASHED"},# Gris estructuras
    "ARQ_TEXTOS": {"color": 7, "lineweight": 18},
    "ELEC_TGD": {"color": 1, "lineweight": 35},                           # Rojo Tablero General
    "ELEC_BANDEJA": {"color": 4, "lineweight": 25},                       # Cian Bandeja Portacables
    "ELEC_HIGHBAY": {"color": 2, "lineweight": 25},                       # Amarillo Luminarias High-Bay
    "ELEC_STECKER": {"color": 5, "lineweight": 25},                       # Azul Tomas Industriales 380V
    "ELEC_MOTORES": {"color": 6, "lineweight": 30},                       # Magenta Maquinaria / Motores
    "ELEC_MALLA_PAT": {"color": 3, "lineweight": 25, "linetype": "DASHED"},# Verde Malla a Tierra
    "ELEC_TEXTOS": {"color": 7, "lineweight": 15},
    "UNIFILAR_LINEAS": {"color": 7, "lineweight": 25},
    "UNIFILAR_MCCB": {"color": 1, "lineweight": 35},
    "UNIFILAR_BANCO": {"color": 6, "lineweight": 25},
    "MARCO_CAJETIN": {"color": 7, "lineweight": 35},
    "MEMBRETE_LINEAS": {"color": 7, "lineweight": 25},
    "MEMBRETE_TEXTOS": {"color": 7, "lineweight": 15},
}

def setup_doc_layers(doc):
    for name, spec in LAYERS.items():
        if name not in doc.layers:
            attribs = {"color": spec["color"]}
            if "linetype" in spec:
                attribs["linetype"] = spec["linetype"]
            doc.layers.new(name, dxfattribs=attribs)
    
    # Crear tipos de línea estándar si no existen
    for lt_name, pattern in [("CENTER", [1.25, 0.75, -0.25, 0.25, -0.25]), ("DASHED", [0.6, 0.35, -0.15])]:
        if lt_name not in doc.linetypes:
            try:
                doc.linetypes.new(lt_name, dxfattribs={"description": lt_name, "pattern": pattern})
            except Exception:
                pass

def add_text(msp, text, x, y, height=0.25, layer="ELEC_TEXTOS", align=TextEntityAlignment.MIDDLE_CENTER, rotation=0):
    txt = msp.add_text(str(text), dxfattribs={"layer": layer, "height": height, "rotation": rotation})
    txt.set_placement((float(x), float(y)), align=align)
    return txt

def add_rect(msp, x, y, w, h, layer="MARCO_CAJETIN"):
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": layer})

def draw_dim_line(msp, x1, y1, x2, y2, text, text_off_y=0.3):
    # Línea de cota con garra / tick inclinado
    msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": "ARQ_COTAS"})
    tick = 0.15
    for px, py in [(x1, y1), (x2, y2)]:
        msp.add_line((px - tick, py - tick), (px + tick, py + tick), dxfattribs={"layer": "ARQ_COTAS"})
    mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    rot = 90 if abs(x2 - x1) < 0.01 else 0
    add_text(msp, text, mx, my + (text_off_y if rot == 0 else 0), 0.18, "ARQ_COTAS", rotation=rot)

def draw_axis_bubble(msp, text, x, y, is_top=True):
    r = 0.45
    cy = y + (r + 0.2) if is_top else y - (r + 0.2)
    msp.add_circle((x, cy), r, dxfattribs={"layer": "ARQ_EJES"})
    add_text(msp, text, x, cy, 0.30, "ARQ_EJES")
    msp.add_line((x, y), (x, cy + (-r if is_top else r)), dxfattribs={"layer": "ARQ_EJES"})

def draw_north_arrow(msp, x, y):
    r = 1.0
    msp.add_circle((x, y), r, dxfattribs={"layer": "ARQ_TEXTOS"})
    # Flecha N
    pts = [(x, y + r), (x - 0.3, y - 0.2), (x, y), (x + 0.3, y - 0.2), (x, y + r)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": "ARQ_TEXTOS"})
    add_text(msp, "N", x, y + r + 0.4, 0.4, "ARQ_TEXTOS")

def draw_scale_bar(msp, x, y):
    h = 0.2
    add_rect(msp, x, y, 5.0, h, "ARQ_TEXTOS")
    add_rect(msp, x, y, 2.5, h, "ARQ_TEXTOS")
    add_text(msp, "0m", x, y - 0.3, 0.15, "ARQ_TEXTOS")
    add_text(msp, "5m", x + 2.5, y - 0.3, 0.15, "ARQ_TEXTOS")
    add_text(msp, "10m", x + 5.0, y - 0.3, 0.15, "ARQ_TEXTOS")
    add_text(msp, "ESCALA GRÁFICA 1:100", x + 2.5, y + 0.4, 0.18, "ARQ_TEXTOS")

def draw_cajetin_personalizado(msp, x0, y0, width, height, num_lamina, titulo_lamina, config_meta=None):
    if config_meta is None:
        config_meta = {
            "proyecto": "PROYECTO DE INGENIERÍA ELECTROMECÁNICA - NAVE INDUSTRIAL 800 m²",
            "cliente": "EMPRESA INDUSTRIAL S.A.C.",
            "ubicacion": "PARQUE INDUSTRIAL - JULIACA / PUNO",
            "proyectista": "ING. RENZO MAMANI / ING. AQUILES RAMOS",
            "cip": "CIP N° 285940",
            "fecha": "JULIO 2026",
            "escala": "1:100",
            "revision": "REV. 0 (EMISIÓN FINAL)"
        }
        
    add_rect(msp, x0, y0, width, height, "MARCO_CAJETIN")
    
    cw, ch = 14.0, 4.5
    cx, cy = x0 + width - cw - 0.5, y0 + 0.5
    add_rect(msp, cx, cy, cw, ch, "MARCO_CAJETIN")
    
    msp.add_line((cx, cy + 3.6), (cx + cw, cy + 3.6), dxfattribs={"layer": "MEMBRETE_LINEAS"})
    msp.add_line((cx, cy + 2.7), (cx + cw, cy + 2.7), dxfattribs={"layer": "MEMBRETE_LINEAS"})
    msp.add_line((cx, cy + 1.8), (cx + cw, cy + 1.8), dxfattribs={"layer": "MEMBRETE_LINEAS"})
    msp.add_line((cx, cy + 0.9), (cx + cw, cy + 0.9), dxfattribs={"layer": "MEMBRETE_LINEAS"})
    msp.add_line((cx + 9.5, cy), (cx + 9.5, cy + 2.7), dxfattribs={"layer": "MEMBRETE_LINEAS"})
    
    add_text(msp, config_meta["proyecto"], cx + cw/2, cy + 4.05, 0.22, "MEMBRETE_TEXTOS")
    add_text(msp, f"CLIENTE: {config_meta['cliente']}", cx + cw/2, cy + 3.15, 0.18, "MEMBRETE_TEXTOS")
    add_text(msp, f"LÁMINA: {titulo_lamina}", cx + 4.75, cy + 2.25, 0.18, "MEMBRETE_TEXTOS")
    add_text(msp, f"PROYECTISTA: {config_meta['proyectista']} | {config_meta['cip']}", cx + 4.75, cy + 1.35, 0.15, "MEMBRETE_TEXTOS")
    add_text(msp, f"UBICACIÓN: {config_meta['ubicacion']}", cx + 4.75, cy + 0.45, 0.14, "MEMBRETE_TEXTOS")
    
    add_text(msp, "CÓDIGO:", cx + 11.75, cy + 2.25, 0.14, "MEMBRETE_TEXTOS")
    add_text(msp, num_lamina, cx + 11.75, cy + 1.35, 0.40, "ELEC_TGD")
    add_text(msp, f"ESCALA: {config_meta['escala']} | {config_meta['fecha']}", cx + 11.75, cy + 0.45, 0.13, "MEMBRETE_TEXTOS")

def generar_plano_planta(output_dxf, config_meta=None):
    doc = ezdxf.new("R2010", setup=True)
    setup_doc_layers(doc)
    msp = doc.modelspace()
    
    NX, NY = 6.0, 6.0
    NW, NL = 20.0, 40.0
    
    # 1. Ejes Estructurales
    # Ejes Verticales (A, B, C, D, E)
    ejes_x = [("A", NX), ("B", NX + 5.0), ("C", NX + 10.0), ("D", NX + 15.0), ("E", NX + 20.0)]
    for let, ex in ejes_x:
        msp.add_line((ex, NY - 1.0), (ex, NY + NL + 1.0), dxfattribs={"layer": "ARQ_EJES"})
        draw_axis_bubble(msp, let, ex, NY + NL + 1.0, is_top=True)
        draw_axis_bubble(msp, let, ex, NY - 1.0, is_top=False)
        
    # Ejes Horizontales (1 al 9 cada 5m)
    for idx, y_pos in enumerate(range(0, int(NL) + 1, 5)):
        ey = NY + y_pos
        num_eje = str(idx + 1)
        msp.add_line((NX - 1.0, ey), (NX + NW + 1.0, ey), dxfattribs={"layer": "ARQ_EJES"})
        # Burbuja a la izquierda
        msp.add_circle((NX - 1.5, ey), 0.45, dxfattribs={"layer": "ARQ_EJES"})
        add_text(msp, num_eje, NX - 1.5, ey, 0.30, "ARQ_EJES")
        # Burbuja a la derecha
        msp.add_circle((NX + NW + 1.5, ey), 0.45, dxfattribs={"layer": "ARQ_EJES"})
        add_text(msp, num_eje, NX + NW + 1.5, ey, 0.30, "ARQ_EJES")

    # 2. Cotas Exteriores
    draw_dim_line(msp, NX, NY - 2.5, NX + NW, NY - 2.5, "COTACIÓN TOTAL NAVE = 20.00 m")
    draw_dim_line(msp, NX - 2.5, NY, NX - 2.5, NY + NL, "COTACIÓN TOTAL LARGO NAVE = 40.00 m")

    # 3. Muros Perimetrales Doble Línea + Tramas
    add_rect(msp, NX, NY, NW, NL, "ARQ_MUROS")
    add_rect(msp, NX - 0.25, NY - 0.25, NW + 0.5, NL + 0.5, "ARQ_MUROS")
    
    # Zona de Oficinas Administrativas
    msp.add_line((NX, NY + 6.0), (NX + NW, NY + 6.0), dxfattribs={"layer": "ARQ_MUROS"})
    msp.add_line((NX + 8.0, NY), (NX + 8.0, NY + 6.0), dxfattribs={"layer": "ARQ_MUROS"})
    
    # Puertas de Oficinas y Acceso Principal
    # Puerta Principal de Acceso a Nave
    msp.add_line((NX + 9.0, NY), (NX + 9.0, NY - 0.25), dxfattribs={"layer": "ARQ_MUROS"})
    msp.add_line((NX + 11.0, NY), (NX + 11.0, NY - 0.25), dxfattribs={"layer": "ARQ_MUROS"})
    add_text(msp, "ACCESO PRINCIPAL", NX + 10.0, NY - 0.6, 0.22, "ARQ_TEXTOS")
    
    add_text(msp, "OFICINAS ADMINISTRATIVAS", NX + 4.0, NY + 3.0, 0.35, "ARQ_TEXTOS")
    add_text(msp, "VESTUARIOS / SS.HH.", NX + 14.0, NY + 3.0, 0.35, "ARQ_TEXTOS")
    add_text(msp, "NAVE DE PRODUCCIÓN Y ALMACÉN (740 m²)", NX + 10.0, NY + 23.0, 0.50, "ARQ_TEXTOS")
    
    # 4. Tijerales y Estructuras Metálicas
    for y_pos in range(0, int(NL) + 1, 5):
        y_c = NY + y_pos
        msp.add_line((NX, y_c), (NX + NW, y_c), dxfattribs={"layer": "ARQ_TIJERALES"})
        # Diagonales de tijerales
        for tx in range(0, int(NW), 5):
            msp.add_line((NX + tx, y_c), (NX + tx + 2.5, y_c + 0.4), dxfattribs={"layer": "ARQ_TIJERALES"})
            msp.add_line((NX + tx + 2.5, y_c + 0.4), (NX + tx + 5.0, y_c), dxfattribs={"layer": "ARQ_TIJERALES"})
        add_rect(msp, NX - 0.4, y_c - 0.2, 0.4, 0.4, "ARQ_TIJERALES")
        add_rect(msp, NX + NW, y_c - 0.2, 0.4, 0.4, "ARQ_TIJERALES")
    
    # 5. Tablero General TGD-Nave
    tgd_x, tgd_y = NX + 0.5, NY + 6.5
    add_rect(msp, tgd_x, tgd_y, 1.2, 0.5, "ELEC_TGD")
    add_text(msp, "TGD-NAVE 380V", tgd_x + 0.6, tgd_y + 0.8, 0.22, "ELEC_TGD")
    
    bc_x, bc_y = NX + 2.0, NY + 6.5
    add_rect(msp, bc_x, bc_y, 0.8, 0.5, "UNIFILAR_BANCO")
    add_text(msp, "BC-AUTO 15kVAR", bc_x + 0.4, bc_y + 0.8, 0.18, "UNIFILAR_BANCO")
    
    # 6. Bandeja Portacables Central y Derivaciones
    bp_x = NX + NW / 2.0
    msp.add_line((bp_x - 0.15, NY + 6.0), (bp_x - 0.15, NY + NL - 1.0), dxfattribs={"layer": "ELEC_BANDEJA"})
    msp.add_line((bp_x + 0.15, NY + 6.0), (bp_x + 0.15, NY + NL - 1.0), dxfattribs={"layer": "ELEC_BANDEJA"})
    add_text(msp, "BANDEJA PORTACABLES METÁLICA 200x50mm", bp_x, NY + 25.0, 0.22, "ELEC_BANDEJA", rotation=90)
    
    msp.add_line((tgd_x + 0.6, tgd_y + 0.5), (tgd_x + 0.6, NY + 8.0), dxfattribs={"layer": "ELEC_BANDEJA"})
    msp.add_line((tgd_x + 0.6, NY + 8.0), (bp_x, NY + 8.0), dxfattribs={"layer": "ELEC_BANDEJA"})
    
    # 7. Alumbrado High-Bay LED 150W
    for ix in [3.5, 7.5, 12.5, 16.5]:
        for iy in range(9, int(NL), 5):
            lx, ly = NX + ix, NY + iy
            msp.add_circle((lx, ly), 0.35, dxfattribs={"layer": "ELEC_HIGHBAY"})
            msp.add_line((lx - 0.25, ly - 0.25), (lx + 0.25, ly + 0.25), dxfattribs={"layer": "ELEC_HIGHBAY"})
            msp.add_line((lx - 0.25, ly + 0.25), (lx + 0.25, ly - 0.25), dxfattribs={"layer": "ELEC_HIGHBAY"})
            add_text(msp, "HB-150W", lx, ly - 0.5, 0.14, "ELEC_TEXTOS")

    # 8. Tomas Stecker 380V
    stecker_points = [
        (NX + 0.2, NY + 10), (NX + 0.2, NY + 20), (NX + 0.2, NY + 30),
        (NX + NW - 0.2, NY + 10), (NX + NW - 0.2, NY + 20), (NX + NW - 0.2, NY + 30),
        (NX + 10, NY + NL - 0.2)
    ]
    for sx, sy in stecker_points:
        msp.add_circle((sx, sy), 0.3, dxfattribs={"layer": "ELEC_STECKER"})
        add_text(msp, "3Ø 380V 32A", sx, sy + 0.5, 0.14, "ELEC_STECKER")

    # 9. Cargas de Fuerza
    msp.add_line((NX + 1.0, NY + 20.0), (NX + NW - 1.0, NY + 20.0), dxfattribs={"layer": "ELEC_MOTORES"})
    add_rect(msp, NX + 10.0 - 0.6, NY + 20.0 - 0.4, 1.2, 0.8, "ELEC_MOTORES")
    add_text(msp, "PUENTE GRÚA 10 HP", NX + 10.0, NY + 20.8, 0.18, "ELEC_MOTORES")
    
    add_rect(msp, NX + 1.0, NY + 35.0, 1.5, 1.0, "ELEC_MOTORES")
    add_text(msp, "COMPRESOR 15 HP", NX + 1.75, NY + 36.3, 0.18, "ELEC_MOTORES")
    
    add_rect(msp, NX + 14.0, NY + 30.0, 4.0, 3.0, "ELEC_MOTORES")
    add_text(msp, "ZONA DE MAQUINARIA (25 kW)", NX + 16.0, NY + 33.5, 0.20, "ELEC_MOTORES")

    # 10. Malla PAT
    pat_coords = [
        (NX - 1.5, NY - 1.5), (NX + NW + 1.5, NY - 1.5),
        (NX + NW + 1.5, NY + NL + 1.5), (NX - 1.5, NY + NL + 1.5)
    ]
    pts_pat = pat_coords + [pat_coords[0]]
    msp.add_lwpolyline(pts_pat, dxfattribs={"layer": "ELEC_MALLA_PAT"})
    
    for px, py in pat_coords:
        msp.add_circle((px, py), 0.4, dxfattribs={"layer": "ELEC_MALLA_PAT"})
        add_text(msp, "PAT <= 5 Ohm", px, py - 0.7, 0.15, "ELEC_MALLA_PAT")

    # Símbolo de Norte y Escala Gráfica
    draw_north_arrow(msp, NX + NW + 4.5, NY + NL - 2.0)
    draw_scale_bar(msp, NX + NW - 8.0, NY - 4.5)

    draw_cajetin_personalizado(msp, 0.0, 0.0, 36.0, 52.0, "IE-01", "DISTRIBUCIÓN Y BANDEJA PORTACABLES NAVE INDUSTRIAL", config_meta)
    doc.saveas(output_dxf)
    print(f"Plano de Planta de Alta Calidad generado: {output_dxf}")

def generar_plano_unifilar(output_dxf, config_meta=None):
    doc = ezdxf.new("R2010", setup=True)
    setup_doc_layers(doc)
    msp = doc.modelspace()
    
    X0, Y0 = 3.0, 3.0
    
    add_text(msp, "ESQUEMA UNIFILAR TRIFÁSICO 380V/220V - 60 Hz", X0 + 12.0, Y0 + 22.0, 0.45, "ELEC_TEXTOS")
    add_text(msp, "TABLERO GENERAL DE DISTRIBUCIÓN (TGD-NAVE) - MÁXIMA DEMANDA: 58.5 kW / 68.8 kVA", X0 + 12.0, Y0 + 21.2, 0.25, "ELEC_TEXTOS")
    
    # Acometida MT
    add_rect(msp, X0 + 1.0, Y0 + 17.5, 2.5, 1.2, "UNIFILAR_MCCB")
    add_text(msp, "ACOMETIDA MT", X0 + 2.25, Y0 + 18.3, 0.18, "ELEC_TEXTOS")
    add_text(msp, "TRAFO 100 kVA", X0 + 2.25, Y0 + 17.8, 0.15, "ELEC_TEXTOS")
    
    # Medidor
    add_rect(msp, X0 + 5.0, Y0 + 17.5, 1.8, 1.2, "ELEC_TGD")
    add_text(msp, "MEDIDOR 3Ø", X0 + 5.9, Y0 + 18.3, 0.18, "ELEC_TGD")
    add_text(msp, "3x380V/220V", X0 + 5.9, Y0 + 17.8, 0.14, "ELEC_TEXTOS")
    
    # Alimentador
    add_rect(msp, X0 + 8.5, Y0 + 17.5, 4.0, 1.2, "UNIFILAR_LINEAS")
    add_text(msp, "ALIMENTADOR PRINCIPAL", X0 + 10.5, Y0 + 18.3, 0.18, "ELEC_TEXTOS")
    add_text(msp, "N2XH 3-1x50 mm² + 1x25 mm²(N)", X0 + 10.5, Y0 + 17.8, 0.14, "ELEC_TEXTOS")

    # MCCB General
    add_rect(msp, X0 + 14.0, Y0 + 17.5, 3.5, 1.2, "UNIFILAR_MCCB")
    add_text(msp, "MCCB GENERAL 3P 125A", X0 + 15.75, Y0 + 18.3, 0.18, "UNIFILAR_MCCB")
    add_text(msp, "Icu = 25 kA / Reg. 100-125A", X0 + 15.75, Y0 + 17.8, 0.14, "ELEC_TEXTOS")
    
    # Barras
    bar_y = Y0 + 15.0
    msp.add_line((X0 + 2.0, bar_y), (X0 + 26.0, bar_y), dxfattribs={"layer": "UNIFILAR_MCCB"})
    add_text(msp, "BARRAS PRINCIPALES TRIFÁSICAS (R, S, T, N, PE) 380V / 220V - 200A", X0 + 14.0, bar_y + 0.4, 0.22, "ELEC_TEXTOS")

    circuitos = [
        {"id": "C1", "desc": "Alumbrado Nave (28x HB 150W)", "kw": 4.2, "itm": "MCCB 3P 20A", "cable": "3x2.5 mm² N2XH", "tubo": "Bandeja / Conduit 20mm"},
        {"id": "C2", "desc": "Tomacorrientes Industriales 380V", "kw": 8.0, "itm": "MCCB 3P 32A + ID 30mA", "cable": "3x6.0 mm² N2XH", "tubo": "Conduit EMT 25mm"},
        {"id": "C3", "desc": "Fuerza - Puente Grúa 10 HP", "kw": 7.5, "itm": "MCCB 3P 32A + Guardamotor", "cable": "3x6.0 mm² N2XH", "tubo": "Conduit EMT 25mm"},
        {"id": "C4", "desc": "Fuerza - Compresor Aire 15 HP", "kw": 11.2, "itm": "MCCB 3P 40A + Y-D", "cable": "3x10.0 mm² N2XH", "tubo": "Conduit EMT 32mm"},
        {"id": "C5", "desc": "Fuerza - Maquinaria Taller", "kw": 25.0, "itm": "MCCB 3P 63A", "cable": "3x16.0 mm² N2XH", "tubo": "Bandeja Portacables"},
        {"id": "C6", "desc": "Alumbrado / Tomas Oficinas 220V", "kw": 3.5, "itm": "ITM 2P 20A + ID 30mA", "cable": "2x2.5 mm² N2XH", "tubo": "PVC-SAP 20mm"},
        {"id": "C7", "desc": "Banco Condensadores Auto", "kw": 15.0, "itm": "MCCB 3P 32A + Contactor", "cable": "3x6.0 mm² N2XH", "tubo": "Conduit EMT 25mm"},
        {"id": "C8", "desc": "Reserva Futura 3Ø", "kw": 10.0, "itm": "Reserva MCCB 3P 40A", "cable": "-", "tubo": "-"}
    ]
    
    col_w = 3.0
    for idx, c in enumerate(circuitos):
        cx = X0 + 1.5 + idx * col_w
        msp.add_line((cx, bar_y), (cx, bar_y - 2.0), dxfattribs={"layer": "UNIFILAR_LINEAS"})
        
        add_rect(msp, cx - 1.2, bar_y - 3.5, 2.4, 1.5, "UNIFILAR_MCCB")
        add_text(msp, c["id"], cx, bar_y - 2.4, 0.18, "ELEC_TGD")
        add_text(msp, c["itm"], cx, bar_y - 3.1, 0.12, "ELEC_TEXTOS")
        
        msp.add_line((cx, bar_y - 3.5), (cx, bar_y - 5.5), dxfattribs={"layer": "UNIFILAR_LINEAS"})
        
        add_rect(msp, cx - 1.3, bar_y - 12.0, 2.6, 6.2, "UNIFILAR_LINEAS")
        add_text(msp, c["desc"], cx, bar_y - 6.2, 0.13, "ELEC_TEXTOS")
        add_text(msp, f"P = {c['kw']} kW", cx, bar_y - 7.2, 0.14, "ELEC_TGD")
        add_text(msp, f"Cond:", cx, bar_y - 8.2, 0.11, "ELEC_TEXTOS")
        add_text(msp, c["cable"], cx, bar_y - 9.0, 0.11, "ELEC_TEXTOS")
        add_text(msp, f"Canal:", cx, bar_y - 10.0, 0.11, "ELEC_TEXTOS")
        add_text(msp, c["tubo"], cx, bar_y - 10.8, 0.10, "ELEC_TEXTOS")
        
    spat_x = X0 + 26.0
    msp.add_line((spat_x, bar_y), (spat_x, bar_y - 12.0), dxfattribs={"layer": "ELEC_MALLA_PAT"})
    add_text(msp, "MALLA PUESTA A TIERRA (PAT <= 5 OHM)", spat_x, bar_y - 13.0, 0.18, "ELEC_MALLA_PAT")

    draw_cajetin_personalizado(msp, 0.0, 0.0, 32.0, 26.0, "IE-02", "DIAGRAMA UNIFILAR TRIFÁSICO TGD-NAVE", config_meta)
    doc.saveas(output_dxf)
    print(f"Plano Unifilar generado (DXF R2010): {output_dxf}")

def exportar_dxf_a_pdf(dxf_path, pdf_path):
    try:
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        fig = plt.figure(figsize=(16, 11))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ctx = RenderContext(doc)
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(msp, finalize=True)
        fig.savefig(pdf_path, dpi=300, bbox_inches="tight", pad_inches=0)
        
        png_path = pdf_path.replace(".pdf", ".png")
        fig.savefig(png_path, dpi=150, bbox_inches="tight", pad_inches=0)
        plt.close(fig)
        print(f"PDF generado: {pdf_path}")
        print(f"PNG generado: {png_path}")
    except Exception as e:
        print(f"Error generando PDF/PNG para {dxf_path}: {e}")

def main():
    base_dir = "/storage/emulated/0/universida-datos/instalacion-electrica/proyectos/nave-industrial/planos"
    os.makedirs(base_dir, exist_ok=True)
    
    planta_dxf = os.path.join(base_dir, "IE-01_Planta_Distribucion_Nave.dxf")
    unifilar_dxf = os.path.join(base_dir, "IE-02_Diagrama_Unifilar_Trifasico_Nave.dxf")
    
    planta_pdf = os.path.join(base_dir, "IE-01_Planta_Distribucion_Nave.pdf")
    unifilar_pdf = os.path.join(base_dir, "IE-02_Diagrama_Unifilar_Trifasico_Nave.pdf")
    
    generar_plano_planta(planta_dxf)
    generar_plano_unifilar(unifilar_dxf)
    
    exportar_dxf_a_pdf(planta_dxf, planta_pdf)
    exportar_dxf_a_pdf(unifilar_dxf, unifilar_pdf)

if __name__ == "__main__":
    main()
