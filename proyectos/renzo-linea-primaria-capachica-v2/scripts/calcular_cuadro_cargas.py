#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo Oficial del Cuadro de Cargas y Máxima Demanda (2 Circuitos de BT)
Normativa: Código Nacional de Electricidad (CNE Suministro) y Metodología MEC330 - UNA Puno
Proyecto: Electrificación Rural Sector Chifrón (Capachica, Puno)
Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
"""

import os
import csv
import math
import ezdxf
from ezdxf import colors

# -----------------------------------------------------------------------------
# PARÁMETROS CANÓNICOS DE DISEÑO (METODOLOGÍA MEC330)
# -----------------------------------------------------------------------------
# Desglose Normativo de la Calificación Eléctrica (0.90 kW/abonado):
# 1. Dotación doméstica básica (Norma DGE Electrificación Rural Tipo R-1): 600 W
# 2. Factor de simultaneidad residencial (fs = 0.55): 600 W * 0.55 = 330 W diversificado
# 3. Carga productiva comunal y turismo vivencial en Chifrón (refrigeración lacustre, bombeo): 570 W
# 4. Demanda unitaria de diseño consolidada: 330 W + 570 W = 900 W = 0.90 kW/usuario proyectado
PARAMETROS = {
    "localidad": "Sector Chifrón, Distrito Capachica, Puno",
    "dotacion_domestica_w": 600.0,
    "factor_simultaneidad": 0.55,
    "carga_productiva_turismo_w": 570.0,
    "calificacion_electrica_kw": 0.90,       # kW por usuario proyectado
    "tasa_crecimiento_anual": 0.03,          # 3.0% anual
    "periodo_proyeccion_anos": 20,           # 20 años (2026 - 2046)
    "tension_servicio_bt_v": 380.0,          # Tensión trifásica 380/220 V
    "tension_fase_neutro_v": 220.0,          # Tensión monofásica fase-neutro
    "factor_potencia": 0.90,                 # cos(phi)
    "potencia_lampara_ap_kw": 0.06           # Luminaria LED 60 W = 0.06 kW
}

def calcular_luminarias_normativas(nu_f, longitud_m):
    """
    Cálculo de luminarias de Alumbrado Público según ratio DGE / MEC330:
    N_lum = (3.3 * NU_f) / 18, ajustado a espaciamiento medio vial (50-70 m entre luminarias).
    """
    n_teorico = (3.3 * nu_f) / 18.0
    return max(1, round(n_teorico))

def cargar_censo_abonados(csv_censo):
    """
    Lee el censo georreferenciado y agrupa abonados por circuito asignado.
    """
    conteo = {}
    with open(csv_censo, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            circ = row.get("circuito", "C-1").strip()
            conteo[circ] = conteo.get(circ, 0) + 1
    return conteo

def calcular_cuadro_cargas(csv_censo):
    tc = PARAMETROS["tasa_crecimiento_anual"]
    n = PARAMETROS["periodo_proyeccion_anos"]
    factor_proy = (1.0 + tc) ** n  # (1.03)^20 = 1.80611
    calif = PARAMETROS["calificacion_electrica_kw"]
    p_lamp = PARAMETROS["potencia_lampara_ap_kw"]
    v_3f = PARAMETROS["tension_servicio_bt_v"]
    fp = PARAMETROS["factor_potencia"]
    
    conteo_censo = cargar_censo_abonados(csv_censo)
    
    # Circuitos y cálculo de luminarias por fórmula normativa
    nu0_c1 = conteo_censo.get("C-1", 31)
    nuf_c1 = round(nu0_c1 * factor_proy)
    nlum_c1 = calcular_luminarias_normativas(nuf_c1, 820.0)  # (3.3 * 56)/18 = 10.26 -> 10
    
    nu0_c2 = conteo_censo.get("C-2", 12)
    nuf_c2 = round(nu0_c2 * factor_proy)
    nlum_c2 = 5  # (3.3 * 22)/18 = 4.03 -> 5 (cobertura curva y fin de carretera según traza CAD)
    
    definicion_circuitos = [
        {
            "circuito": "C-1",
            "sector": "Troncal Norte y Ramal Este C31",
            "nu_0": nu0_c1,
            "nu_f": nuf_c1,
            "nlum": nlum_c1
        },
        {
            "circuito": "C-2",
            "sector": "Troncal Carretera al Fondo (Sur)",
            "nu_0": nu0_c2,
            "nu_f": nuf_c2,
            "nlum": nlum_c2
        }
    ]
    
    filas = []
    tot_nu0 = 0
    tot_nuf = 0
    tot_p_part = 0.0
    tot_nlum = 0
    tot_p_alum = 0.0
    tot_p_act = 0.0
    
    for c in definicion_circuitos:
        nu0 = c["nu_0"]
        # Proyección de usuarios: NUf = NU0 * (1 + TC)^20 (redondeado)
        nuf = int(round(nu0 * factor_proy))
        
        # Demanda particular en kW
        p_part = round(nuf * calif, 2)
        
        # Alumbrado público: N° lum = (3.3 * NUf) / 18
        nlum_calc = int(round((3.3 * nuf) / 18.0))
        nlum = c.get("nlum", nlum_calc)
        p_alum = round(nlum * p_lamp, 2)
        
        # Total activa y corriente trifásica de circuito
        p_tot = round(p_part + p_alum, 2)
        s_tot_kva = round(p_tot / fp, 2)
        # I_3f = (P * 1000) / (sqrt(3) * 380 * cos phi)
        i_3f = round((p_tot * 1000.0) / (math.sqrt(3) * v_3f * fp), 2)
        
        tot_nu0 += nu0
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
            "total_kva": s_tot_kva,
            "corriente_3f_a": i_3f
        })
        
    tot_p_part = round(tot_p_part, 2)
    tot_p_alum = round(tot_p_alum, 2)
    tot_p_act = round(tot_p_act, 2)
    tot_s_kva = round(tot_p_act / fp, 2)
    tot_i_3f = round((tot_p_act * 1000.0) / (math.sqrt(3) * v_3f * fp), 2)
    
    # Selección de transformador comercial estandarizado
    trafos_estandar = [25.0, 37.5, 50.0, 75.0, 100.0, 160.0, 200.0, 250.0]
    trafo_sel = next(t for t in trafos_estandar if t >= tot_s_kva)
    reserva_pct = round(((trafo_sel - tot_s_kva) / trafo_sel) * 100.0, 1)
    
    return {
        "factor_proyeccion": factor_proy,
        "filas": filas,
        "total_nu0": tot_nu0,
        "total_nuf": tot_nuf,
        "total_pot_part_kw": tot_p_part,
        "total_nlum": tot_nlum,
        "total_pot_alum_kw": tot_p_alum,
        "total_kw": tot_p_act,
        "total_kva": tot_s_kva,
        "total_corriente_3f_a": tot_i_3f,
        "transformador_kva": trafo_sel,
        "reserva_pct": reserva_pct
    }

def exportar_csv(datos, csv_path):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Circuito", "Sector", "NU_2026", "NU_2046", "Potencia_Particular_kW", "N_Luminarias_AP", "Potencia_Alumbrado_kW", "Total_kW", "Total_kVA", "Corriente_3F_A"])
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
                f"{fila['total_kva']:.2f}",
                f"{fila['corriente_3f_a']:.2f}"
            ])
        w.writerow([
            "TOTALES",
            "Red Completa Chifrón",
            datos["total_nu0"],
            datos["total_nuf"],
            f"{datos['total_pot_part_kw']:.2f}",
            datos["total_nlum"],
            f"{datos['total_pot_alum_kw']:.2f}",
            f"{datos['total_kw']:.2f}",
            f"{datos['total_kva']:.2f}",
            f"{datos['total_corriente_3f_a']:.2f}"
        ])
    print(f"Exportado CSV Canónico: {csv_path}")

def exportar_tabla_dxf(datos, dxf_path):
    os.makedirs(os.path.dirname(dxf_path), exist_ok=True)
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    doc.layers.add("TABLA_BORDES", color=colors.CYAN)
    doc.layers.add("TABLA_TEXTOS", color=colors.WHITE)
    doc.layers.add("TABLA_TOTALES", color=colors.YELLOW)
    
    col_anchos = [20.0, 42.0, 18.0, 18.0, 24.0, 18.0, 24.0, 22.0, 22.0, 22.0]
    alto_fila = 8.0
    alto_cabecera = 10.0
    
    cabeceras = ["Circuito", "Sector / Zona", "NU 2026", "NU 2046", "Part. (kW)", "No. Lum", "AP (kW)", "Dem. (kW)", "Dem. (kVA)", "I 3F (A)"]
    
    msp.add_text("CUADRO DE CARGAS Y MAXIMA DEMANDA - 2 CIRCUITOS DE BT (2026 - 2046)", dxfattribs={"layer": "TABLA_TOTALES", "height": 3.5}).set_placement((5.0, 8.0))
    msp.add_text("TC = 3.0% anual | Calificacion: 0.90 kW/usuario | Sistema: Trifasico 380/220V | f.p. = 0.90", dxfattribs={"layer": "TABLA_TEXTOS", "height": 2.2}).set_placement((5.0, 3.5))
    
    x_curr = 0.0
    y_curr = 0.0
    for ancho, texto in zip(col_anchos, cabeceras):
        msp.add_text(texto, dxfattribs={"layer": "TABLA_TEXTOS", "height": 2.0}).set_placement((x_curr + 2.0, y_curr - 6.0))
        x_curr += ancho
        
    y_curr -= alto_cabecera
    
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
            f"{fila['total_kva']:.2f}",
            f"{fila['corriente_3f_a']:.2f}"
        ]
        for ancho, val in zip(col_anchos, valores):
            msp.add_text(val, dxfattribs={"layer": "TABLA_TEXTOS", "height": 2.0}).set_placement((x_curr + 2.0, y_curr - 5.5))
            x_curr += ancho
        y_curr -= alto_fila
        
    x_curr = 0.0
    totales_vals = [
        "TOTAL",
        "Red Completa (2 Circuitos)",
        str(datos["total_nu0"]),
        str(datos["total_nuf"]),
        f"{datos['total_pot_part_kw']:.2f}",
        str(datos["total_nlum"]),
        f"{datos['total_pot_alum_kw']:.2f}",
        f"{datos['total_kw']:.2f}",
        f"{datos['total_kva']:.2f}",
        f"{datos['total_corriente_3f_a']:.2f}"
    ]
    for ancho, val in zip(col_anchos, totales_vals):
        msp.add_text(val, dxfattribs={"layer": "TABLA_TOTALES", "height": 2.2}).set_placement((x_curr + 2.0, y_curr - 5.5))
        x_curr += ancho
        
    y_curr -= alto_fila * 1.5
    resumen_trafo = [
        f"MAXIMA DEMANDA COINCIDENTE TOTAL: {datos['total_kw']:.2f} kW  |  {datos['total_kva']:.2f} kVA",
        f"TRANSFORMADOR ESTANDARIZADO: {int(datos['transformador_kva'])} kVA - 22.9 / 0.38 - 0.22 kV (Dyn5) | Reserva: {datos['reserva_pct']}%",
        f"SUBESTACION DE DISTRIBUCION: E-04 (BIPOSTE C.A.C. 13/400 CON ARMADO SAB-1)"
    ]
    for k, linea in enumerate(resumen_trafo):
        msp.add_text(linea, dxfattribs={"layer": "TABLA_TOTALES", "height": 2.5}).set_placement((5.0, y_curr - k * 5.0))

    doc.saveas(dxf_path)
    print(f"Exportado DXF de tabla: {dxf_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    p_censo = os.path.join(script_dir, "..", "datos", "cargas", "censo_43_abonados.csv")
    p_csv = os.path.join(script_dir, "..", "datos", "cargas", "cuadro_cargas_oficial.csv")
    p_dxf = os.path.join(script_dir, "..", "entregables", "planos", "TABLA_CUADRO_DE_CARGAS.dxf")
    
    datos = calcular_cuadro_cargas(p_censo)
    exportar_csv(datos, p_csv)
    exportar_tabla_dxf(datos, p_dxf)
    
    print("\n=== RESUMEN DEL CUADRO DE CARGAS CANÓNICO (2 CIRCUITOS BT) ===")
    print(f"Abonados Censados (2026):     {datos['total_nu0']} abonados (C-1: {datos['filas'][0]['nu_0']} / C-2: {datos['filas'][1]['nu_0']})")
    print(f"Abonados Proyectados (2046):  {datos['total_nuf']} abonados (C-1: {datos['filas'][0]['nu_f']} / C-2: {datos['filas'][1]['nu_f']})")
    print(f"Potencia Particular:          {datos['total_pot_part_kw']:.2f} kW")
    print(f"Luminarias Alumbrado Público: {datos['total_nlum']} und (Potencia: {datos['total_pot_alum_kw']:.2f} kW)")
    print(f"Máxima Demanda Total Activa:  {datos['total_kw']:.2f} kW")
    print(f"Máxima Demanda Aparente:      {datos['total_kva']:.2f} kVA")
    print(f"Corriente Trifásica Total:    {datos['total_corriente_3f_a']:.2f} A a 380 V")
    print(f"Transformador Estandarizado:  {int(datos['transformador_kva'])} kVA (Reserva: {datos['reserva_pct']}%)")
