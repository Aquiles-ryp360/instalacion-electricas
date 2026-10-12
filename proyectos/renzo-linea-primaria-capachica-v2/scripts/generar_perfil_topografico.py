#!/usr/bin/env python3
"""
Generador de Perfiles Topográficos para RedCAD / DLT-CAD
Reemplazo automatizado de TopoMagic a partir del KML de Google Earth.
Curso: MEC330 - Instalaciones Eléctricas II | FIME - UNA Puno
Autor: Renzo Gabriel Mamani Galindo
"""

import math
import csv
import os

# 13 Vértices de la Línea Primaria (ruta electrica 1)
# Coordenadas UTM Zona 19S y Cotas DEM SRTM (msnm)
VERTICES = [
    ("E0_INICIO", 412606.01, 8270712.24, 3924.17, "PUNTO_DERIVACION_ELECTRO_PUNO"),
    ("V1_BIFURC", 412759.20, 8270976.22, 3839.56, "SED_PROYECTADA_Y_DERIVACION"),
    ("V2",        412750.60, 8271073.06, 3817.04, "ANGULO_MT"),
    ("V3",        412705.51, 8271124.69, 3817.04, "ANGULO_MT"),
    ("V4",        412684.34, 8271166.70, 3827.27, "ANGULO_MT"),
    ("V5",        412688.54, 8271218.86, 3827.27, "ANGULO_MT"),
    ("V6",        412694.09, 8271235.85, 3824.61, "ANGULO_MT"),
    ("V7",        412677.31, 8271272.50, 3824.61, "ANGULO_MT"),
    ("V8",        412656.92, 8271306.91, 3824.61, "ANGULO_MT"),
    ("V9",        412646.16, 8271345.24, 3824.61, "ANGULO_MT"),
    ("V10",       412660.46, 8271391.24, 3824.61, "ANGULO_MT"),
    ("V11",       412670.90, 8271430.79, 3824.61, "ANGULO_MT"),
    ("V12_FIN",   412659.90, 8271446.51, 3824.61, "POSTE_TERMINAL_MT")
]

def generar_perfiles(salida_dir, paso_m=10.0):
    os.makedirs(salida_dir, exist_ok=True)
    
    # 1. Calcular progresivas y ángulos de deflexión en vértices
    v_info = []
    prog_acum = 0.0
    for i, (name, e, n, z, desc) in enumerate(VERTICES):
        if i > 0:
            d = math.hypot(e - VERTICES[i-1][1], n - VERTICES[i-1][2])
            prog_acum += d
        
        # Deflexión
        if 0 < i < len(VERTICES) - 1:
            vin = (e - VERTICES[i-1][1], n - VERTICES[i-1][2])
            vout = (VERTICES[i+1][1] - e, VERTICES[i+1][2] - n)
            azin = math.degrees(math.atan2(vin[0], vin[1])) % 360
            azout = math.degrees(math.atan2(vout[0], vout[1])) % 360
            deflex = azout - azin
            if deflex > 180: deflex -= 360
            elif deflex < -180: deflex += 360
        else:
            deflex = 0.0
            
        v_info.append({
            "idx": i + 1,
            "nombre": name,
            "este": e,
            "norte": n,
            "cota": z,
            "prog": prog_acum,
            "deflex": deflex,
            "desc": desc
        })

    # Archivo 1: Planilla de Vértices Principales
    f_vertices = os.path.join(salida_dir, "planilla_vertices_lp.csv")
    with open(f_vertices, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["punto", "nombre", "progresiva_m", "cota_msnm", "angulo_deflexion_deg", "este_m", "norte_m", "descripcion"])
        for v in v_info:
            w.writerow([v["idx"], v["nombre"], f"{v['prog']:.2f}", f"{v['cota']:.2f}", f"{v['deflex']:.2f}", f"{v['este']:.2f}", f"{v['norte']:.2f}", v["desc"]])

    # 2. Generar muestreo de terreno cada paso_m (10 m)
    puntos_perfil = []
    pto_id = 1
    
    for i in range(len(VERTICES) - 1):
        p1 = v_info[i]
        p2 = v_info[i+1]
        dist_tramo = p2["prog"] - p1["prog"]
        n_pasos = max(1, int(round(dist_tramo / paso_m)))
        
        for k in range(n_pasos if i == len(VERTICES)-2 else n_pasos):
            t = k / float(n_pasos)
            curr_prog = p1["prog"] + t * dist_tramo
            curr_e = p1["este"] + t * (p2["este"] - p1["este"])
            curr_n = p1["norte"] + t * (p2["norte"] - p1["norte"])
            curr_z = p1["cota"] + t * (p2["cota"] - p1["cota"])
            
            # Si coincide con vértice, poner su ángulo y descripción
            if k == 0:
                codigo = p1["nombre"]
                deflex = p1["deflex"]
            else:
                codigo = "TN"  # Terreno Natural
                deflex = 0.0
                
            puntos_perfil.append({
                "id": pto_id,
                "prog": curr_prog,
                "cota": curr_z,
                "deflex": deflex,
                "este": curr_e,
                "norte": curr_n,
                "codigo": codigo
            })
            pto_id += 1
            
    # Añadir último vértice
    p_last = v_info[-1]
    puntos_perfil.append({
        "id": pto_id,
        "prog": p_last["prog"],
        "cota": p_last["cota"],
        "deflex": 0.0,
        "este": p_last["este"],
        "norte": p_last["norte"],
        "codigo": p_last["nombre"]
    })

    # Archivo 2: Formato estándar CSV RedCAD (Progresiva, Cota, Deflexión, Código)
    f_redcad_csv = os.path.join(salida_dir, "perfil_terreno_redcad.csv")
    with open(f_redcad_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Progresiva", "Cota", "Deflexion", "Codigo", "Este", "Norte"])
        for p in puntos_perfil:
            w.writerow([f"{p['prog']:.2f}", f"{p['cota']:.2f}", f"{p['deflex']:.2f}", p["codigo"], f"{p['este']:.2f}", f"{p['norte']:.2f}"])

    # Archivo 3: Formato P, E, N, Z, D (Coordenadas Topográficas estándar de estación total)
    f_penzd = os.path.join(salida_dir, "topografia_coordenadas_PENZD.csv")
    with open(f_penzd, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Punto", "Este", "Norte", "Cota", "Descripcion"])
        for p in puntos_perfil:
            w.writerow([p["id"], f"{p['este']:.2f}", f"{p['norte']:.2f}", f"{p['cota']:.2f}", p["codigo"]])

    # Archivo 4: Formato .TOP (DLT-CAD / RedCAD nativo delimitado por tabuladores)
    f_top = os.path.join(salida_dir, "perfil_linea_primaria.top")
    with open(f_top, "w", encoding="utf-8") as f:
        f.write("# ARCHIVO DE PERFIL TOPOGRAFICO PARA REDCAD / DLT-CAD\n")
        f.write("# PROGRESIVA(m)\tCOTA(m)\tANGULO(deg)\tCODIGO\n")
        for p in puntos_perfil:
            f.write(f"{p['prog']:.2f}\t{p['cota']:.2f}\t{p['deflex']:.2f}\t{p['codigo']}\n")

    print(f"=== PERFILES GENERADOS EXITOSAMENTE EN: {salida_dir} ===")
    print(f"1. Planilla de vértices: {f_vertices}")
    print(f"2. Perfil RedCAD CSV:    {f_redcad_csv}")
    print(f"3. Coordenadas PENZD:    {f_penzd}")
    print(f"4. Perfil RedCAD .TOP:   {f_top}")
    print(f"Total puntos de perfil generados: {len(puntos_perfil)}")

if __name__ == "__main__":
    directorio_destino = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica-v2\datos\topografia"
    generar_perfiles(directorio_destino, paso_m=10.0)
