#!/usr/bin/env python3
"""
Cálculo Oficial del Cuadro de Cargas y Máxima Demanda
Metodología oficial de MEC330 - Instalaciones Eléctricas II | FIME UNA Puno
Autor: Renzo Gabriel Mamani Galindo
"""

import os
import csv
import math
import ezdxf
from ezdxf import colors

# 1. Parámetros Iniciales del Proyecto
PARAMETROS = {
    "localidad": "Sector Chifrón, Distrito Capachica, Puno",
    "calificacion_electrica_kw": 0.90,  # kW por usuario
    "tasa_crecimiento_anual": 0.03,     # 3% anual
    "periodo_proyeccion_anos": 20,      # 20 años
    "tension_servicio_v": 220.0,        # V
    "factor_potencia": 0.90,            # cos(phi)
    "potencia_lampara_ap_kw": 0.06      # 60 W = 0.06 kW
}

# 2. Distribución de Circuitos (Censo real de 43 viviendas)
CIRCUITOS = [
    {
        "circuito": "C-1",
        "sector": "Sector Sur / Pasaje",
        "nu_0": 21
    },
    {
        "circuito": "C-2",
        "sector": "Sector Centro / Eje",
        "nu_0": 11
    },
    {
        "circuito": "C-3",
        "sector": "Sector Norte / Camino",
        "nu_0": 11
    }
]

def calcular_cuadro_cargas():
    tc = PARAMETROS["tasa_crecimiento_anual"]
    n = PARAMETROS["periodo_proyeccion_anos"]
    factor_proy = (1.0 + tc) ** n  # 1.80611
    calif = PARAMETROS["calificacion_electrica_kw"]
    p_lamp = PARAMETROS["potencia_lampara_ap_kw"]
    v = PARAMETROS["tension_servicio_v"]
    fp = PARAMETROS["factor_potencia"]
    
    filas = []
    tot_nu0 = sum(c["nu_0"] for c in CIRCUITOS)
    tot_nuf = 0
    tot_p_part = 0.0
    tot_nlum = 0
    tot_p_alum = 0.0
    tot_p_act = 0.0
    
    for c in CIRCUITOS:
        nu0 = c["nu_0"]
        # Proyección de usuarios (redondear a entero)
        nuf = int(round(nu0 * factor_proy))
        # Demanda particular
        p_part = round(nuf * calif, 2)
        # Luminarias AP: N° lum = (3.3 * NUf) / 18
        nlum = int(round((3.3 * nuf) / 18.0))
        p_alum = round(nlum * p_lamp, 2)
        # Total kW
        p_tot = round(p_part + p_alum, 2)
        # Corriente nominal I = (Total_kW * 1000) / (V * cos phi)
        i_nom = round((p_tot * 1000.0) / (v * fp), 2)
        
        tot_nuf += nuf
        tot_p_part += p_part
        tot_nlum += nlum
        tot_p_alum += p_alum
        tot_p_act += p_tot
        
        filas.append({
            "circuito": c["circuito"],
            "sector": c["sector"],
            "nu_0": nu0,
            "nu_f": nuf,
            "pot_part_kw": p_part,
            "nlum": nlum,
            "pot_alum_kw": p_alum,
            "total_kw": p_tot,
            "corriente_a": i_nom
        })
        
    tot_p_part = round(tot_p_part, 2)
    tot_p_alum = round(tot_p_alum, 2)
    tot_p_act = round(tot_p_act, 2)
    tot_i_nom = round((tot_p_act * 1000.0) / (v * fp), 2)
    tot_s_kva = round(tot_p_act / fp, 2)
    
    # Selección de transformador comercial estandarizado superior
    trafos_estandar = [25.0, 37.5, 50.0, 75.0, 100.0, 160.0, 200.0, 250.0]
    trafo_sel = next(t for t in trafos_estandar if t >= tot_s_kva)
    
    return {
        "factor_proyeccion": factor_proy,
        "filas": filas,
        "total_nu0": tot_nu0,
        "total_nuf": tot_nuf,
        "total_pot_part_kw": tot_p_part,
        "total_nlum": tot_nlum,
        "total_pot_alum_kw": tot_p_alum,
        "total_kw": tot_p_act,
        "total_corriente_a": tot_i_nom,
        "potencia_aparente_kva": tot_s_kva,
        "transformador_kva": trafo_sel
    }

def exportar_csv(datos, csv_path):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Circuito", "Sector", "NU_2026", "NU_2046", "Potencia_Particular_kW", "N_Luminarias_AP", "Potencia_Alumbrado_kW", "Total_kW", "Corriente_A"])
        for fila in datos["filas"]:
            w.writerow([
                fila["circuito"],
                fila["sector"],
                fila["nu_0"],
                fila["nu_f"],
                f"{fila['pot_part_kw']:.2f}",
                fila["nlum"],
                f"{fila['pot_alum_kw']:.2f}",
                f"{fila['total_kw']:.2f}",
                f"{fila['corriente_a']:.2f}"
            ])
        w.writerow([
            "TOTALES",
            "General",
            datos["total_nu0"],
            datos["total_nuf"],
            f"{datos['total_pot_part_kw']:.2f}",
            datos["total_nlum"],
            f"{datos['total_pot_alum_kw']:.2f}",
            f"{datos['total_kw']:.2f}",
            f"{datos['total_corriente_a']:.2f}"
        ])
    print(f"Exportado CSV: {csv_path}")

def exportar_tabla_dxf(datos, dxf_path):
    """Genera la tabla gráfica del Cuadro de Cargas en formato DXF para AutoCAD."""
    os.makedirs(os.path.dirname(dxf_path), exist_ok=True)
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    doc.layers.add("TABLA_BORDES", color=colors.CYAN)
    doc.layers.add("TABLA_TEXTOS", color=colors.WHITE)
    doc.layers.add("TABLA_TOTALES", color=colors.YELLOW)
    
    # Dimensiones de la tabla
    col_anchos = [20.0, 35.0, 18.0, 18.0, 24.0, 18.0, 24.0, 22.0, 22.0]
    alto_fila = 8.0
    alto_cabecera = 10.0
    ancho_total = sum(col_anchos)
    
    cabeceras = ["Circuito", "Sector / Zona", "NU 2026", "NU 2046", "Partic. (kW)", "N° Lum", "AP (kW)", "Total (kW)", "I Nom (A)"]
    
    # Dibujar Cabecera
    x_curr = 0.0
    y_curr = 0.0
    
    # Título principal de la tabla
    msp.add_text("CUADRO DE CARGAS Y MÁXIMA DEMANDA - CAPACHICA CHIFRÓN (2026 - 2046)", dxfattribs={"layer": "TABLA_TOTALES", "height": 3.5}).set_placement((5.0, 8.0))
    msp.add_text("TC = 3.0% anual | Calificación: 0.90 kW/usuario | V = 220V | cos phi = 0.90", dxfattribs={"layer": "TABLA_TEXTOS", "height": 2.2}).set_placement((5.0, 3.5))
    
    # Líneas y textos de encabezado
    for j, (ancho, texto) in enumerate(zip(col_anchos, cabeceras)):
        # Celda encabezado
        msp.add_text(texto, dxfattribs={"layer": "TABLA_TEXTOS", "height": 2.0}).set_placement((x_curr + 2.0, y_curr - 6.0))
        x_curr += ancho
        
    y_curr -= alto_cabecera
    
    # Filas de datos
    for fila in datos["filas"]:
        x_curr = 0.0
        valores = [
            fila["circuito"],
            fila["sector"],
            str(fila["nu_0"]),
            str(fila["nu_f"]),
            f"{fila['pot_part_kw']:.2f}",
            str(fila["nlum"]),
            f"{fila['pot_alum_kw']:.2f}",
            f"{fila['total_kw']:.2f}",
            f"{fila['corriente_a']:.2f}"
        ]
        for ancho, val in zip(col_anchos, valores):
            msp.add_text(val, dxfattribs={"layer": "TABLA_TEXTOS", "height": 2.0}).set_placement((x_curr + 2.0, y_curr - 5.5))
            x_curr += ancho
        y_curr -= alto_fila
        
    # Fila de Totales
    x_curr = 0.0
    totales_vals = [
        "TOTAL",
        "Red Completa",
        str(datos["total_nu0"]),
        str(datos["total_nuf"]),
        f"{datos['total_pot_part_kw']:.2f}",
        str(datos["total_nlum"]),
        f"{datos['total_pot_alum_kw']:.2f}",
        f"{datos['total_kw']:.2f}",
        f"{datos['total_corriente_a']:.2f}"
    ]
    for ancho, val in zip(col_anchos, totales_vals):
        msp.add_text(val, dxfattribs={"layer": "TABLA_TOTALES", "height": 2.2}).set_placement((x_curr + 2.0, y_curr - 5.5))
        x_curr += ancho
        
    # Recuadro inferior de Transformador
    y_curr -= alto_fila * 1.5
    resumen_trafo = [
        f"POTENCIA APARENTE CALCULADA: {datos['potencia_aparente_kva']:.2f} kVA",
        f"TRANSFORMADOR SELECCIONADO (ESTANDARIZADO): {int(datos['transformador_kva'])} kVA - 22.9 / 0.38 - 0.22 kV",
        f"ESTRUCTURA DE SUBESTACIÓN: E-04 (BIPOSTE CAC 13/400 CON ARMADO SAB-1)"
    ]
    for k, linea in enumerate(resumen_trafo):
        msp.add_text(linea, dxfattribs={"layer": "TABLA_TOTALES", "height": 2.5}).set_placement((5.0, y_curr - k * 5.0))

    doc.saveas(dxf_path)
    print(f"Exportado DXF de tabla: {dxf_path}")

if __name__ == "__main__":
    datos = calcular_cuadro_cargas()
    
    p_csv = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\datos\cargas\cuadro_cargas_oficial.csv"
    p_dxf = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\entregables\planos\TABLA_CUADRO_DE_CARGAS.dxf"
    
    exportar_csv(datos, p_csv)
    exportar_tabla_dxf(datos, p_dxf)
    
    print("\n=== RESUMEN OFICIAL DEL CUADRO DE CARGAS ===")
    print(f"Usuarios Iniciales (2026): {datos['total_nu0']} abonados")
    print(f"Usuarios Proyectados (2046): {datos['total_nuf']} abonados")
    print(f"Potencia Servicio Particular: {datos['total_pot_part_kw']:.2f} kW")
    print(f"Luminarias Alumbrado Público: {datos['total_nlum']} und (Potencia: {datos['total_pot_alum_kw']:.2f} kW)")
    print(f"Demanda Máxima Total: {datos['total_kw']:.2f} kW")
    print(f"Corriente Nominal Total: {datos['total_corriente_a']:.2f} A")
    print(f"Potencia Aparente: {datos['potencia_aparente_kva']:.2f} kVA")
    print(f"Transformador Normalizado: {int(datos['transformador_kva'])} kVA")
