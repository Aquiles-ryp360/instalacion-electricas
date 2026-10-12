"""Ejecucion de flujo de carga con dss-python (motor C-API, sin win32com)."""
import dss


def ejecutar_flujo_opendss(ruta_dss):
    """Compila y resuelve el modelo OpenDSS.

    Retorna dict JSON-able: {voltajes: {bus: {fase_i_pu, min_pu}},
    corrientes_tramos: {linea: {fase_i_a}}, perdidas: {kw, kvar},
    convergencia: bool}.
    """
    e = dss.dss
    e.Text.Command = f"Compile [{ruta_dss}]"
    e.Text.Command = "Solve"

    circuit = e.ActiveCircuit
    resultado = {
        "fuente": str(ruta_dss),
        "convergencia": bool(circuit.Solution.Converged),
        "voltajes": {},
        "corrientes_tramos": {},
        "perdidas": {},
    }

    for bus in circuit.AllBusNames:
        circuit.SetActiveBus(bus)
        mag_ang = list(circuit.ActiveBus.puVmagAngle)
        v_pu = [mag_ang[i] for i in range(0, len(mag_ang), 2)]
        resultado["voltajes"][bus] = {
            f"fase_{i+1}_pu": round(v_pu[i], 5)
            for i in range(min(3, len(v_pu)))
        }
        resultado["voltajes"][bus]["min_pu"] = (
            round(min(v_pu), 5) if v_pu else None)

    for _linea in circuit.Lines:
        nombre = circuit.Lines.Name
        corrientes = list(circuit.ActiveCktElement.CurrentsMagAng)
        corrientes_fase = [corrientes[i]
                             for i in range(0, len(corrientes), 2)]
        resultado["corrientes_tramos"][nombre] = {
            f"fase_{i+1}_a": round(corrientes_fase[i], 3)
            for i in range(min(3, len(corrientes_fase)))
        }

    perdidas = list(circuit.Losses)
    resultado["perdidas"] = {
        "kw": round(float(perdidas[0]) / 1000.0, 4),
        "kvar": round(float(perdidas[1]) / 1000.0, 4),
    }

    return resultado
