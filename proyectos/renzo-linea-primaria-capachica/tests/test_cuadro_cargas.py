"""
Tests unitarios para el cuadro de cargas y censo de abonados
Proyecto: renzo-linea-primaria-capachica
"""
import pytest
import csv
from pathlib import Path

def test_censo_43_abonados_estructura():
    """Verifica que el censo contenga exactamente 43 abonados con asignación a C-1 y C-2."""
    censo_path = Path(__file__).parent.parent / "datos" / "cargas" / "censo_43_abonados.csv"
    assert censo_path.exists()
    
    with open(censo_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        filas = list(reader)
        
    assert len(filas) == 43
    c1 = [r for r in filas if r["circuito"] == "C-1"]
    c2 = [r for r in filas if r["circuito"] == "C-2"]
    
    assert len(c1) == 31  # C01 a C31
    assert len(c2) == 12  # C32 a C43

def test_cuadro_cargas_trafo_reserva():
    """Verifica la potencia total demandada y reserva del transformador 100 kVA."""
    cuadro_path = Path(__file__).parent.parent / "datos" / "cargas" / "cuadro_cargas_oficial.csv"
    assert cuadro_path.exists()
    
    with open(cuadro_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        filas = list(reader)
        
    total_fila = [r for r in filas if r["Circuito"] == "TOTALES"][0]
    pot_kw = float(total_fila["Total_kW"])
    pot_kva = float(total_fila["Total_kVA"])
    i_3f = float(total_fila["Corriente_3F_A"])
    
    assert abs(pot_kw - 71.10) < 0.1
    assert abs(pot_kva - 79.00) < 0.1
    assert abs(i_3f - 120.03) < 0.1
    
    # Trafo 100 kVA
    reserva_pct = ((100.0 - pot_kva) / 100.0) * 100.0
    assert abs(reserva_pct - 21.0) < 0.1
    assert reserva_pct >= 15.0  # Mínimo 15% de reserva
