#!/usr/bin/env python3
"""
Generador de Plano de Perfil Longitudinal y Distribución de Estructuras (Spotting) en DXF
Reemplazo directo de RedCAD para generar planos directamente para AutoCAD.
Curso: MEC330 - Instalaciones Eléctricas II | FIME - UNA Puno
Autor: Renzo Gabriel Mamani Galindo
"""

import os
import math
import ezdxf
from ezdxf import colors

# 1. Definición de Postes del Proyecto (Spotting de Ingeniería para 816.6 m)
# Postes C.A.C. normalizados de 12m y 13m
ESTRUCTURAS = [
    {
        "id": "E-01",
        "prog": 0.00,
        "cota": 3924.17,
        "poste": "C.A.C. 12/400",
        "h_poste": 12.0,
        "empotramiento": 1.4,
        "armado": "PR-1 (Derivacion)",
        "funcion": "PUNTO DE CONEXION / SECCIONAMIENTO",
        "angulo": 0.0,
        "retenida": "Inclinada simple"
    },
    {
        "id": "E-02",
        "prog": 105.00,
        "cota": 3895.00,
        "poste": "C.A.C. 12/300",
        "h_poste": 12.0,
        "empotramiento": 1.4,
        "armado": "PS-1 (Alineamiento)",
        "funcion": "PASO / SUSPENSION",
        "angulo": 0.0,
        "retenida": "Ninguna"
    },
    {
        "id": "E-03",
        "prog": 210.00,
        "cota": 3865.00,
        "poste": "C.A.C. 12/300",
        "h_poste": 12.0,
        "empotramiento": 1.4,
        "armado": "PS-1 (Alineamiento)",
        "funcion": "PASO / SUSPENSION",
        "angulo": 0.0,
        "retenida": "Ninguna"
    },
    {
        "id": "E-04",
        "prog": 305.21,
        "cota": 3839.56,
        "poste": "C.A.C. 13/400 (Biposte)",
        "h_poste": 13.0,
        "empotramiento": 1.5,
        "armado": "SAB-1 / Trafo 100 kVA",
        "funcion": "SUBESTACION DE DISTRIBUCION (SED)",
        "angulo": -35.20,
        "retenida": "Contraviento doble"
    },
    {
        "id": "E-05",
        "prog": 402.43,
        "cota": 3817.04,
        "poste": "C.A.C. 12/400",
        "h_poste": 12.0,
        "empotramiento": 1.4,
        "armado": "PA-1 (Angulo)",
        "funcion": "CAMBIO DE DIRECCION",
        "angulo": -36.06,
        "retenida": "Biselar simple"
    },
    {
        "id": "E-06",
        "prog": 518.02,
        "cota": 3827.27,
        "poste": "C.A.C. 12/400",
        "h_poste": 12.0,
        "empotramiento": 1.4,
        "armado": "PA-1 (Angulo)",
        "funcion": "CAMBIO DE DIRECCION",
        "angulo": 31.35,
        "retenida": "Biselar simple"
    },
    {
        "id": "E-07",
        "prog": 628.53,
        "cota": 3824.61,
        "poste": "C.A.C. 12/300",
        "h_poste": 12.0,
        "empotramiento": 1.4,
        "armado": "PS-1 (Alineamiento)",
        "funcion": "PASO / SUSPENSION",
        "angulo": -6.05,
        "retenida": "Ninguna"
    },
    {
        "id": "E-08",
        "prog": 708.34,
        "cota": 3824.61,
        "poste": "C.A.C. 12/300",
        "h_poste": 12.0,
        "empotramiento": 1.4,
        "armado": "PS-1 (Alineamiento)",
        "funcion": "PASO / SUSPENSION",
        "angulo": 32.95,
        "retenida": "Biselar simple"
    },
    {
        "id": "E-09",
        "prog": 816.60,
        "cota": 3824.61,
        "poste": "C.A.C. 12/400",
        "h_poste": 12.0,
        "empotramiento": 1.4,
        "armado": "PR-1 (Terminal)",
        "funcion": "FIN DE LINEA PRIMARIA",
        "angulo": 0.0,
        "retenida": "Terminal simple"
    }
]

def generar_dxf_perfil(dxf_salida):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    # Crear capas organizadas
    capas = [
        ("TERRENO_NATURAL", colors.GREEN),
        ("CONDUCTOR_MT", colors.RED),
        ("ESTRUCTURAS_CAC", colors.CYAN),
        ("GUITARRA_RETICULA", colors.WHITE),
        ("TEXTOS_COTAS", colors.YELLOW),
        ("MARCO_ROTULO", colors.BLUE)
    ]
    for nombre, col in capas:
        if nombre not in doc.layers:
            doc.layers.add(nombre, color=col)
            
    # Factores de escala
    # H: 1:1 (X = progresiva real)
    # V: Exageracion vertical 5x (Y = (cota - cota_base) * 5)
    cota_base = 3800.0  # Linea de comparacion
    exag_v = 5.0
    
    def transform(prog, cota):
        return (prog, (cota - cota_base) * exag_v)
        
    # 2. Dibujar Linea de Terreno Natural
    pts_terreno = [transform(e["prog"], e["cota"]) for e in ESTRUCTURAS]
    msp.add_lwpolyline(pts_terreno, dxfattribs={"layer": "TERRENO_NATURAL", "lineweight": 35})
    
    # 3. Dibujar Postes y Catenarias
    pts_cabeza_poste = []
    for e in ESTRUCTURAS:
        cota_util = e["cota"] + (e["h_poste"] - e["empotramiento"])
        x_base, y_base = transform(e["prog"], e["cota"])
        x_top, y_top = transform(e["prog"], cota_util)
        pts_cabeza_poste.append((x_top, y_top))
        
        # Linea del poste
        msp.add_line((x_base, y_base), (x_top, y_top), dxfattribs={"layer": "ESTRUCTURAS_CAC", "lineweight": 50})
        # Cruceta representativa
        msp.add_line((x_top - 2.0, y_top), (x_top + 2.0, y_top), dxfattribs={"layer": "ESTRUCTURAS_CAC", "lineweight": 40})
        # Texto identificador sobre el poste
        msp.add_text(e["id"], dxfattribs={"layer": "TEXTOS_COTAS", "height": 3.0}).set_placement((x_top - 4.0, y_top + 4.0))

    # 4. Dibujar Catenarias entre postes (Parábola con flecha calculada)
    for i in range(len(ESTRUCTURAS) - 1):
        e1 = ESTRUCTURAS[i]
        e2 = ESTRUCTURAS[i+1]
        vano = e2["prog"] - e1["prog"]
        x1, y1 = pts_cabeza_poste[i]
        x2, y2 = pts_cabeza_poste[i+1]
        
        # Flecha maxima estimada para este vano con AAAC 35 mm2 a 35°C: f approx (0.0945 * vano^2) / (8 * 128)
        flecha_real = (0.0945 * (vano**2)) / (8.0 * 128.0)
        flecha_dibujo = flecha_real * exag_v
        
        # Puntos de la parábola
        n_sub = 20
        cat_pts = []
        for s in range(n_sub + 1):
            ts = s / float(n_sub)
            x_cat = x1 + ts * (x2 - x1)
            # Interpolacion lineal + parabola de flecha
            y_lin = y1 + ts * (y2 - y1)
            y_sag = 4.0 * flecha_dibujo * ts * (1.0 - ts)
            cat_pts.append((x_cat, y_lin - y_sag))
            
        msp.add_lwpolyline(cat_pts, dxfattribs={"layer": "CONDUCTOR_MT", "lineweight": 25})

    # 5. Dibujar "Guitarra" inferior (Cuadro de Bandas normalizado DGE)
    y_banda_base = -30.0
    ancho_banda = 15.0
    bandas = [
        ("COTA DE TERRENO (msnm)", 0),
        ("COTA DE CABEZA POSTE (msnm)", 1),
        ("PROGRESIVA (m)", 2),
        ("VANO (m)", 3),
        ("POSTE C.A.C.", 4),
        ("ARMADO DGE", 5),
        ("DESVIO ANGULAR", 6)
    ]
    
    x_min = 0.0
    x_max = ESTRUCTURAS[-1]["prog"]
    
    # Lineas horizontales de la guitarra
    for nombre, idx in bandas:
        y_pos = y_banda_base - idx * ancho_banda
        msp.add_line((x_min - 150.0, y_pos), (x_max + 30.0, y_pos), dxfattribs={"layer": "GUITARRA_RETICULA"})
        # Titulo de la banda
        msp.add_text(nombre, dxfattribs={"layer": "TEXTOS_COTAS", "height": 3.0}).set_placement((x_min - 145.0, y_pos + 5.0))
        
    y_pos_final = y_banda_base - len(bandas) * ancho_banda
    msp.add_line((x_min - 150.0, y_pos_final), (x_max + 30.0, y_pos_final), dxfattribs={"layer": "GUITARRA_RETICULA"})
    
    # Lineas verticales y llenado de datos por cada estructura
    for i, e in enumerate(ESTRUCTURAS):
        prog = e["prog"]
        cota_terr = e["cota"]
        cota_cab = e["cota"] + (e["h_poste"] - e["empotramiento"])
        vano_val = (ESTRUCTURAS[i]["prog"] - ESTRUCTURAS[i-1]["prog"]) if i > 0 else 0.0
        
        # Linea vertical desde el terreno hasta la base de la guitarra
        x_pt, y_pt = transform(prog, cota_terr)
        msp.add_line((prog, y_pt), (prog, y_pos_final), dxfattribs={"layer": "GUITARRA_RETICULA", "color": colors.GRAY})
        
        # Escribir textos en cada banda
        msp.add_text(f"{cota_terr:.2f}", dxfattribs={"layer": "TEXTOS_COTAS", "height": 2.5, "rotation": 90}).set_placement((prog - 1.5, y_banda_base - 13.0))
        msp.add_text(f"{cota_cab:.2f}", dxfattribs={"layer": "TEXTOS_COTAS", "height": 2.5, "rotation": 90}).set_placement((prog - 1.5, y_banda_base - 28.0))
        msp.add_text(f"{prog:.1f}", dxfattribs={"layer": "TEXTOS_COTAS", "height": 2.5, "rotation": 90}).set_placement((prog - 1.5, y_banda_base - 43.0))
        
        if i > 0:
            prog_mid = (ESTRUCTURAS[i-1]["prog"] + prog) / 2.0
            msp.add_text(f"{vano_val:.1f} m", dxfattribs={"layer": "TEXTOS_COTAS", "height": 2.5}).set_placement((prog_mid - 8.0, y_banda_base - 53.0))
            
        msp.add_text(e["poste"].split()[1], dxfattribs={"layer": "TEXTOS_COTAS", "height": 2.5, "rotation": 90}).set_placement((prog - 1.5, y_banda_base - 73.0))
        msp.add_text(e["armado"].split()[0], dxfattribs={"layer": "TEXTOS_COTAS", "height": 2.5, "rotation": 90}).set_placement((prog - 1.5, y_banda_base - 88.0))
        msp.add_text(f"{e['angulo']:.1f}°", dxfattribs={"layer": "TEXTOS_COTAS", "height": 2.5, "rotation": 90}).set_placement((prog - 1.5, y_banda_base - 103.0))

    # Guardar DXF
    os.makedirs(os.path.dirname(dxf_salida), exist_ok=True)
    doc.saveas(dxf_salida)
    print(f"=== PLANO DE PERFIL LONGITUDINAL GENERADO EN DXF: {dxf_salida} ===")

if __name__ == "__main__":
    dxf_dest = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\entregables\planos\PLANO_PERFIL_LONGITUDINAL_LP_CAPACHICA.dxf"
    generar_dxf_perfil(dxf_dest)
