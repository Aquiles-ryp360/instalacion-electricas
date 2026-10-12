"""Construccion del modelo OpenDSS (.dss) desde la red canonica.

Convenciones verificadas en dss-python 0.15.7 / DSS C-API:
- Los buses se crean implicitamente; su kVBase se fija con
  `Set voltagebases=[...]` + `calcv` DESPUES de definir los elementos.
- Transformer kvs: tension de linea (p. ej. [22.9, 0.38]).
- Load kv: tension de linea (p. ej. 0.38), conn=wye.
- La fuente por defecto (Vsource.source en sourcebus) alimenta la
  red; no se crea una segunda fuente.
"""
from pathlib import Path

CONDUCTOR_CANONICO_AAAC35 = {
    "designacion": "AAAC 35 mm2",
    "r1_ohm_km": 0.986,
    "x1_ohm_km": 0.385,
    "capacidad_admisible_a": 145.0,
    "fuente": "matriz_maestra_datos.yaml (NTP 370.258 / ASTM B399)",
}


def escribir_modelo_dss(datos_red, calibre_conductor, kva_trafo, ruta_salida,
                        vnom_kv=22.9, vsecundaria_kv=0.38, frecuencia_hz=60,
                        conductor=None):
    """Genera el script OpenDSS de la linea primaria.

    datos_red: salida de extraer_red_gpkg/extraer_red_canonical.
    calibre_conductor: designacion del conductor; debe coincidir con
    `conductor['designacion']` (no se inventan parametros).
    kva_trafo: potencia del transformador de la SED (kVA).
    """
    cond = conductor or CONDUCTOR_CANONICO_AAAC35
    if calibre_conductor not in str(cond.get("designacion", "")):
        raise ValueError(
            f"Calibre '{calibre_conductor}' sin parametros verificados; "
            "proporcione un dict conductor con r1/x1/capacidad")

    out = Path(ruta_salida)
    out.parent.mkdir(parents=True, exist_ok=True)
    codigo_linea = cond["designacion"].replace(" ", "_")

    lineas = [
        f"New Circuit.CAPACHICA basekv={vnom_kv} pu=1.0001 "
        f"phases=3 freq={frecuencia_hz} angle=0",
        f"New LineCode.{codigo_linea} nphases=3 "
        f"r1={cond['r1_ohm_km']} x1={cond['x1_ohm_km']} "
        f"units=km normamps={cond['capacidad_admisible_a']} "
        f"emergamps={cond['capacidad_admisible_a'] * 1.5}",
    ]

    nodos = datos_red["nodos"]
    bus_raiz = nodos[0]["id"]
    lineas.append(f"New Line.FUENTE_DERIVACION bus1=sourcebus.1.2.3 "
                  f"bus2={bus_raiz}.1.2.3 length=0.0001 "
                  f"linecode={codigo_linea}")

    for t in datos_red["tramos"]:
        long_km = (t["longitud_m"] or 0.0) / 1000.0
        lineas.append(f"New Line.{t['id']} bus1={t['desde']}.1.2.3 "
                      f"bus2={t['hasta']}.1.2.3 length={long_km:.4f} "
                      f"linecode={codigo_linea}")

    cargas = datos_red.get("cargas", [])
    if cargas and cargas[0].get("kva"):
        bus_sed = cargas[0]["nodo"]
        kw = cargas[0].get("kw", 0.0)
        kvar = round((cargas[0]["kva"] ** 2 - kw ** 2) ** 0.5, 3)
        lineas.append(f"New Transformer.SED phases=3 windings=2 "
                      f"conns=[d,y] kvas=[{kva_trafo},{kva_trafo}] "
                      f"kvs=[{vnom_kv},{vsecundaria_kv}] "
                      f"buses=[{bus_sed}.1.2.3,{bus_sed}_BT.1.2.3]")
        lineas.append(f"New Load.SED_{bus_sed} phases=3 "
                      f"bus1={bus_sed}_BT.1.2.3 conn=wye "
                      f"kv={vsecundaria_kv} kw={kw:.3f} kvar={kvar:.3f}")

    lineas.append(f"Set voltagebases=[{vnom_kv}, {vsecundaria_kv}, "
                  f"{round(vsecundaria_kv / 3 ** 0.5, 4)}]")
    lineas.append("calcv")

    texto = "\n".join(lineas) + "\n"
    out.write_text(texto, encoding="utf-8")

    return {"ruta": str(out), "lineas_modelo": len(lineas),
            "conductor": cond["designacion"], "kva_trafo": kva_trafo,
            "resumen": texto}
