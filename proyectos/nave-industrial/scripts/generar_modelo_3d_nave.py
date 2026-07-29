#!/usr/bin/env python3
"""
Generador de Modelo 3D / BIM en DXF (AutoCAD 3D R2010 + PDF Render)
para Nave Industrial 20m x 40m x 8m.
Crea entidades 3D:
- Columnas de acero 3D (HEB 300) y Zapatas
- Cerchas / Tijerales reticulados 3D a h=8.00m
- Trazado de Bandeja Portacables 3D a h=6.50m
- Grilla 3D de Luminarias High-Bay LED a h=7.50m
- Gabinetes 3D del Tablero TGD-Nave y Banco de Condensadores
- Red de Malla Puesta a Tierra en 3D bajo suelo
"""

import os
import sys
import math
import ezdxf
from ezdxf.enums import TextEntityAlignment
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

# Capas CAD 3D Estandarizadas
LAYERS_3D = {
    "3D_ESTRUCTURA_COLUMNAS": {"color": 7, "lineweight": 30},
    "3D_ESTRUCTURA_TIJERALES": {"color": 8, "lineweight": 18},
    "3D_MUROS": {"color": 9, "lineweight": 25},
    "3D_BANDEJA_PORTACABLES": {"color": 4, "lineweight": 25}, # Cian
    "3D_LUMINARIAS_HIGHBAY": {"color": 2, "lineweight": 25},  # Amarillo
    "3D_TABLEROS_TGD": {"color": 1, "lineweight": 35},        # Rojo
    "3D_STECKER_TOMAS": {"color": 5, "lineweight": 25},       # Azul
    "3D_MAQUINARIA": {"color": 6, "lineweight": 30},          # Magenta
    "3D_MALLA_TIERRA": {"color": 3, "lineweight": 25},        # Verde
    "3D_TEXTOS_EJES": {"color": 7, "lineweight": 15},
    "MARCO_CAJETIN": {"color": 7, "lineweight": 35},
}

def setup_layers(doc):
    for name, spec in LAYERS_3D.items():
        if name not in doc.layers:
            doc.layers.new(name, dxfattribs={"color": spec["color"]})

def add_box_3d(msp, x, y, z, dx, dy, dz, layer="3D_ESTRUCTURA_COLUMNAS"):
    # Caja 3D mediante polilínea 3D o líneas
    p0 = (x, y, z)
    p1 = (x + dx, y, z)
    p2 = (x + dx, y + dy, z)
    p3 = (x, y + dy, z)
    
    p4 = (x, y, z + dz)
    p5 = (x + dx, y, z + dz)
    p6 = (x + dx, y + dy, z + dz)
    p7 = (x, y + dy, z + dz)
    
    # Base inferior
    msp.add_polyline3d([p0, p1, p2, p3, p0], dxfattribs={"layer": layer})
    # Base superior
    msp.add_polyline3d([p4, p5, p6, p7, p4], dxfattribs={"layer": layer})
    # Columnas verticales
    msp.add_line(p0, p4, dxfattribs={"layer": layer})
    msp.add_line(p1, p5, dxfattribs={"layer": layer})
    msp.add_line(p2, p6, dxfattribs={"layer": layer})
    msp.add_line(p3, p7, dxfattribs={"layer": layer})

def generar_modelo_3d(output_dxf):
    doc = ezdxf.new("R2010", setup=True)
    setup_layers(doc)
    msp = doc.modelspace()
    
    NX, NY, NZ = 0.0, 0.0, 0.0
    NW, NL, NH = 20.0, 40.0, 8.0
    
    # 1. Zapatas y Columnas 3D de Acero (10 Columnas por lado)
    for y_pos in range(0, int(NL) + 1, 5):
        # Columnas Izquierda (X = NX)
        add_box_3d(msp, NX - 0.4, NY + y_pos - 0.2, NZ, 0.4, 0.4, NH, "3D_ESTRUCTURA_COLUMNAS")
        # Columnas Derecha (X = NX + NW)
        add_box_3d(msp, NX + NW, NY + y_pos - 0.2, NZ, 0.4, 0.4, NH, "3D_ESTRUCTURA_COLUMNAS")
        
        # Tijeral 3D en la parte superior (z = NH)
        # Brida inferior y superior
        z_inf = NH
        z_sup = NH + 1.2
        msp.add_line((NX, NY + y_pos, z_inf), (NX + NW, NY + y_pos, z_inf), dxfattribs={"layer": "3D_ESTRUCTURA_TIJERALES"})
        msp.add_line((NX, NY + y_pos, z_sup), (NX + NW/2, NY + y_pos, z_sup + 0.8), dxfattribs={"layer": "3D_ESTRUCTURA_TIJERALES"})
        msp.add_line((NX + NW/2, NY + y_pos, z_sup + 0.8), (NX + NW, NY + y_pos, z_sup), dxfattribs={"layer": "3D_ESTRUCTURA_TIJERALES"})
        
        # Diagonales del tijeral
        for tx in range(0, int(NW), 4):
            msp.add_line((NX + tx, NY + y_pos, z_inf), (NX + tx + 2, NY + y_pos, z_sup), dxfattribs={"layer": "3D_ESTRUCTURA_TIJERALES"})
            msp.add_line((NX + tx + 2, NY + y_pos, z_sup), (NX + tx + 4, NY + y_pos, z_inf), dxfattribs={"layer": "3D_ESTRUCTURA_TIJERALES"})

    # 2. Muros Perimetrales 3D
    add_box_3d(msp, NX - 0.25, NY - 0.25, NZ, NW + 0.5, 0.25, 4.0, "3D_MUROS")
    add_box_3d(msp, NX - 0.25, NY + NL, NZ, NW + 0.5, 0.25, 4.0, "3D_MUROS")
    add_box_3d(msp, NX - 0.25, NY, NZ, 0.25, NL, 4.0, "3D_MUROS")
    add_box_3d(msp, NX + NW, NY, NZ, 0.25, NL, 4.0, "3D_MUROS")
    
    # 3. Bandeja Portacables 3D Suspended a h = 6.50m
    z_bandeja = 6.50
    bp_x = NX + NW / 2.0
    # Canaleta 3D en U
    add_box_3d(msp, bp_x - 0.2, NY + 5.0, z_bandeja, 0.4, NL - 6.0, 0.1, "3D_BANDEJA_PORTACABLES")
    
    # Tirantes de suspensión desde los tijerales
    for y_pos in range(5, int(NL), 5):
        msp.add_line((bp_x - 0.2, NY + y_pos, z_bandeja), (bp_x - 0.2, NY + y_pos, NH), dxfattribs={"layer": "3D_BANDEJA_PORTACABLES"})
        msp.add_line((bp_x + 0.2, NY + y_pos, z_bandeja), (bp_x + 0.2, NY + y_pos, NH), dxfattribs={"layer": "3D_BANDEJA_PORTACABLES"})

    # 4. Luminarias High-Bay LED 3D Suspended a h = 7.50m
    z_lum = 7.50
    for ix in [3.5, 7.5, 12.5, 16.5]:
        for iy in range(7, int(NL), 4):
            lx, ly = NX + ix, NY + iy
            add_box_3d(msp, lx - 0.35, ly - 0.35, z_lum, 0.7, 0.7, 0.2, "3D_LUMINARIAS_HIGHBAY")
            msp.add_line((lx, ly, z_lum + 0.2), (lx, ly, NH), dxfattribs={"layer": "3D_LUMINARIAS_HIGHBAY"})

    # 5. Tablero General TGD-Nave 3D y Banco de Condensadores
    add_box_3d(msp, NX + 0.5, NY + 6.5, NZ, 1.2, 0.6, 1.8, "3D_TABLEROS_TGD")
    add_box_3d(msp, NX + 2.0, NY + 6.5, NZ, 0.8, 0.6, 1.8, "3D_TABLEROS_TGD")

    # 6. Malla de Puesta a Tierra en 3D (z = -0.80m bajo tierra)
    z_pat = -0.80
    pat_coords = [
        (NX - 1.5, NY - 1.5, z_pat), (NX + NW/2, NY - 1.5, z_pat), (NX + NW + 1.5, NY - 1.5, z_pat),
        (NX + NW + 1.5, NY + NL + 1.5, z_pat), (NX + NW/2, NY + NL + 1.5, z_pat), (NX - 1.5, NY + NL + 1.5, z_pat)
    ]
    pts_pat = pat_coords + [pat_coords[0]]
    msp.add_polyline3d(pts_pat, dxfattribs={"layer": "3D_MALLA_TIERRA"})
    
    # Pozos verticales 3D (varilla 2.4m de profundidad)
    for px, py, pz in pat_coords:
        msp.add_line((px, py, pz), (px, py, pz - 2.4), dxfattribs={"layer": "3D_MALLA_TIERRA"})
        msp.add_line((px, py, pz), (px, py, NZ), dxfattribs={"layer": "3D_MALLA_TIERRA"})

    doc.saveas(output_dxf)
    print(f"Modelo 3D BIM generado: {output_dxf}")

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
        print(f"PDF 3D generado: {pdf_path}")
        print(f"PNG 3D generado: {png_path}")
    except Exception as e:
        print(f"Error generando PDF/PNG 3D para {dxf_path}: {e}")

def main():
    base_dir = "/storage/emulated/0/universida-datos/instalacion-electrica/proyectos/nave-industrial/planos"
    os.makedirs(base_dir, exist_ok=True)
    
    modelo_dxf = os.path.join(base_dir, "IE-04_Modelo_3D_BIM_Nave.dxf")
    modelo_pdf = os.path.join(base_dir, "IE-04_Modelo_3D_BIM_Nave.pdf")
    
    generar_modelo_3d(modelo_dxf)
    exportar_dxf_a_pdf(modelo_dxf, modelo_pdf)

if __name__ == "__main__":
    main()
