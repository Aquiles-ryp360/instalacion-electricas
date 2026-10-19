#!/usr/bin/env python3
"""Reproduce escenario LP-R03 de 22,9 kV a partir del modelo eléctrico LP-R02.
No escribe sobre entregables M01 ni declara ingeniería aprobada.
Invocar desde raíz repo: python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r03/evaluar_229kv.py --salida build/lp-r03-229
"""
import argparse, csv, json, math, sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parents[2]
ROOT = SCRIPT.parents[4]
sys.path.insert(0, str(ROOT))

from herramientas.lineas_primarias.revision import impedancia_linea, flujo_sistema

def leer_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def evaluar():
    c = leer_json(PROJECT / "datos/lp-r02/parametros.json")
    r = leer_json(PROJECT / "datos/lp-r03-229kv/escenario.json")
    assert abs(r["tension_nominal_linea_kv"] - 22.9) < 1e-12
    assert r["aprobado_para_construccion"] is False
    e = c["electrico"]; d = c["demanda"]; cn = c["conductor"]
    years = c["censo"]["anio_diseno"] - c["censo"]["anio"]
    demand = sum(
        math.ceil(loc["viviendas_ocupadas"]*(1+c["censo"]["r_anual"])**years)*
        (d["tipo_i_kw"] if loc["tipo"] == "I" else d["tipo_ii_kw"])*d["simultaneidad"]
        for loc in c["censo"]["localidades"]
    ) + d["ap_numero"] * d["ap_kw_unit"] + sum(s["kw"] for s in d["servicios"])
    # La longitud eléctrica se conserva como resultado publicado LP-R02: no se sustituye por 6.696 km horizontales.
    longitud_electrica_m = 6758.120297
    z, imp = impedancia_linea(cn, longitud_electrica_m, e["frecuencia_hz"],
                             [1.2,1.2,2.4],e["temperatura_conductor_c"])
    filas = []
    for tap in r["regulacion_fuente_sensibilidades_pu"]:
        flujo = flujo_sistema(22.9,demand,d["fp_transporte"],z,e,tap)
        filas.append(dict(tension_nominal_kv=22.9,regulacion_fuente_equivalente_pu=tap,
            BT_llegada_V=flujo["BT_llegada_V"], MT_salida_kV=flujo["MT_salida_kV"],
            MT_llegada_kV=flujo["MT_llegada_kV"], I_linea_A=flujo["corrientes_A"][1],
            perdida_linea_kW=flujo["perdida_linea_kW"],
            caida_linea_pct=flujo["caida_linea_pct"],
            P_generacion_requerida_kW=flujo["P_generacion_kW"],
            S_generador_kVA=flujo["S_generador_kVA"],
            desviacion_BT_pct=(flujo["BT_llegada_V"]/e["bt_v"]-1)*100,
            margen_sobre_200kW_sin_reserva=200-flujo["P_generacion_kW"],
            margen_sobre_200kW_con_25kW_Limbani=200-flujo["P_generacion_kW"]-25,
            residuo_balance_W=flujo["residuo_balance_W"],
            estado="ESTUDIO IDEALIZADO; NO APROBADO PARA OBRA"))
    # Coincidencia con LP-R02, que ya estudió 22.9 kV. Evita una falsa recalculación divergente.
    ruta = PROJECT / "revisiones/lp-r02/03-calculos/comparacion_tensiones.csv"
    with ruta.open(encoding="utf-8-sig",newline="") as f:
        original = [x for x in csv.DictReader(f) if abs(float(x["kV"])-22.9)<1e-6]
    assert len(original)==3
    for n in filas:
        antigua = next(x for x in original if abs(float(x["toma_pu"])-n["regulacion_fuente_equivalente_pu"])<1e-8)
        for nueva, previa, tol in [
            ("BT_llegada_V","BT_llegada_V",0.01),
            ("perdida_linea_kW","perdida_linea_kW",0.001),
            ("P_generacion_requerida_kW","P_generacion_kW",0.01)]:
            delta=abs(n[nueva]-float(antigua[previa]))
            assert delta<tol,(n["regulacion_fuente_equivalente_pu"],nueva,delta)
    return dict(estado="RECALCULO ELECTRICO PRELIMINAR 22.9 kV", revision="LP-R03-229KV",
        carga_kw=demand,impedancia=imp,fuente_kv_no_verificada=True,casos=filas,
        advertencia="No valida placas, regulación, protecciones, topografía, aislamiento ni mecánica.")

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--salida",required=True)
    args=pa.parse_args()
    destino=Path(args.salida).resolve()
    if destino.exists():
        raise FileExistsError("No se permite sobrescribir una salida anterior: "+str(destino))
    destino.mkdir(parents=True)
    res=evaluar()
    (destino/"resultado_229kv.json").write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (destino/"comparacion_229kv.csv").open("w",newline="",encoding="utf-8-sig") as f:
        wr=csv.DictWriter(f,fieldnames=list(res["casos"][0]))
        wr.writeheader();wr.writerows(res["casos"])
    print(json.dumps(dict(salida=str(destino),escenarios=len(res["casos"]),
                          prueba_contra_LP_R02="OK",estado=res["estado"]),ensure_ascii=False))

if __name__=="__main__":
    main()
