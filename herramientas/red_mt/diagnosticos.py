"""Diagnostico de nodos criticos frente a limite de caida de tension."""


def analizar_nodos_criticos(resultados_dss, limite_caida_tension=5.0,
                            vnom_kv=22.9):
    """Evalua desviaciones de tension y sobrecargas.

    Retorna {cumplimiento: bool, nodos_criticos: [...],
    sobrecargas: [...], resumen: {...}}.
    La caida de tension se mide como desviacion respecto a 1.0 pu
    en la fase mas desfavorable.
    """
    nodos_criticos = []
    sobrecargas = []
    limite_inf = 1.0 - limite_caida_tension / 100.0
    limite_sup = 1.0 + limite_caida_tension / 100.0

    for bus, fases in resultados_dss.get("voltajes", {}).items():
        min_pu = fases.get("min_pu")
        if min_pu is None:
            continue
        desviacion_pct = (min_pu - 1.0) * 100.0
        if not (limite_inf <= min_pu <= limite_sup):
            nodos_criticos.append({
                "nodo": bus,
                "vmin_pu": min_pu,
                "desviacion_pct": round(desviacion_pct, 3),
                "motivo": "caida_excesiva" if min_pu < limite_inf
                          else "elevacion_excesiva",
            })

    conductor_normamps = None
    for tramo, fases in resultados_dss.get("corrientes_tramos", {}).items():
        corrientes = [v for v in fases.values() if isinstance(v, (int, float))]
        if not corrientes:
            continue
        imax = max(corrientes)
        sobrecargas.append({
            "tramo": tramo,
            "imax_a": imax,
            "utilizacion_pct": None,
        })

    cumplimiento = not nodos_criticos
    return {
        "cumplimiento": cumplimiento,
        "limite_caida_tension_pct": limite_caida_tension,
        "nodos_criticos": nodos_criticos,
        "sobrecargas": sobrecargas,
        "resumen": {
            "n_nodos_evaluados": len(resultados_dss.get("voltajes", {})),
            "n_nodos_criticos": len(nodos_criticos),
            "perdidas_kw": resultados_dss.get("perdidas", {}).get("kw"),
        },
    }
