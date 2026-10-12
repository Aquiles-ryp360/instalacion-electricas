"""Prueba de humo del pipeline completo con datos canonicos reales."""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\renzo\instalacion-electricas")

from herramientas.red_mt import (analizar_nodos_criticos,
                                 ejecutar_flujo_opendss,
                                 escribir_modelo_dss,
                                 extraer_red_canonical, generar_reportes)

BASE = Path(r"C:\Users\renzo\instalacion-electricas\proyectos"
              r"\renzo-linea-primaria-capachica")
BUILD = Path(r"C:\Users\renzo\instalacion-electricas\proyectos"
             r"\renzo-linea-primaria-capachica-v2\build")

red = extraer_red_canonical(BASE / "datos" / "matriz_maestra_datos.yaml")
print("NODOS:", len(red["nodos"]), "| TRAMOS:", len(red["tramos"]),
      "| CARGAS:", red["cargas"])

modelo = escribir_modelo_dss(red, "AAAC 35 mm2", 100.0,
                               BUILD / "smoke_test.dss")
print("MODELO DSS:", modelo["ruta"], "| lineas:", modelo["lineas_modelo"])

resultados = ejecutar_flujo_opendss(modelo["ruta"])
print("CONVERGENCIA:", resultados["convergencia"])
print("PERDIDAS:", resultados["perdidas"])
for bus, v in resultados["voltajes"].items():
    print(f"  {bus}: min_pu={v['min_pu']}")

diagnostico = analizar_nodos_criticos(resultados, limite_caida_tension=5.0)
print("CUMPLIMIENTO:", diagnostico["cumplimiento"],
      "| criticos:", diagnostico["resumen"]["n_nodos_criticos"])

reportes = generar_reportes(resultados, "ambos",
                             ruta_salida=BUILD / "reportes",
                             diagnosticos=diagnostico)
print("REPORTES:", reportes)

(BUILD / "resultados_smoke.json").write_text(
    json.dumps({"resultados": {k: v for k, v in resultados.items()
                               if k != "fuente"},
                "diagnostico": diagnostico},
               indent=2, default=str), encoding="utf-8")
