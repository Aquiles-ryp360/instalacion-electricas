"""Deriva la matriz Rev. 4 sin alterar el registro de hallazgos Rev. 3."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "documentacion/auditoria_independiente_rev3"
SOURCE = BASE / "MATRIZ_HALLAZGOS_REV3.csv"
TARGET = BASE / "MATRIZ_HALLAZGOS_REV4.csv"

corrections = {
    "AI-06": ("corregido en nuevo plano Rev. 4", "CL-04 Rev. 4 contiene 40 PC y 27 PN en DXF y PDF; Rev. 2 queda como antecedente"),
    "AI-07": ("corregido en nuevo plano Rev. 4", "CL-05 Rev. 4 dibuja cajas, flechas y etiquetas compartidas en DXF y PDF"),
    "AI-08": ("corregido en modelo Rev. 4; legado abierto", "calculos_condicionales_rev4_propuesta.py rechaza no finitos; calculos_condicionales.py Rev. 3 permanece intacto"),
    "AI-09": ("corregido mediante flujo adicional Rev. 4", "generar_entrega_rev4.py genera y verifica DXF/PDF/PNG y expediente; reproducir_rev3.py conserva su alcance anterior"),
    "AI-13": ("corregido parcialmente; pendiente de campo", "CL-01 compara ambos ejes y CL-02 separa PN/PC/CV; escala y posición finales requieren levantamiento"),
}
with SOURCE.open(encoding="utf-8-sig", newline="") as fh:
    reader = csv.DictReader(fh)
    rows = list(reader)
    cols = list(reader.fieldnames) + ["estado_rev4", "evidencia_rev4"]
for row in rows:
    row["estado_rev4"], row["evidencia_rev4"] = corrections.get(
        row["id"], ("pendiente de validación externa", "Sin nueva evidencia que cierre el hallazgo"))
with TARGET.open("w", encoding="utf-8-sig", newline="") as fh:
    writer = csv.DictWriter(fh, fieldnames=cols)
    writer.writeheader()
    writer.writerows(rows)
print(f"{len(rows)} hallazgos derivados en {TARGET}")
