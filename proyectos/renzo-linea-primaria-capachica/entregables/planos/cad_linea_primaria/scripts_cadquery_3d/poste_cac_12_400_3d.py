"""
Poste C.A.C. Paramétrico 12/400 (NTP 339.027 / DGE)
Altura: 12.0 m | Carga de Trabajo: 400.0 daN
Empotramiento normalizado: 1.4 m
"""
import cadquery as cq

ALTURA = 12000.0
R_CIMA = 90.0
R_BASE = 180.0
EMPOTRAMIENTO = 1400.0

# Tronco de cono principal
poste = (
    cq.Workplane("XY")
    .circle(R_BASE)
    .workplane(offset=ALTURA)
    .circle(R_CIMA)
    .loft(combine=True)
)

# Anillo marcador de línea de tierra / empotramiento
marca_tierra = (
    cq.Workplane("XY")
    .workplane(offset=EMPOTRAMIENTO)
    .circle(R_BASE - ((R_BASE - R_CIMA) * (EMPOTRAMIENTO / ALTURA)) + 5.0)
    .rect(50.0, 50.0)
)

# Agujeros pasantes en la cima para fijación de pernos de cruceta (5/8")
poste = (
    poste.faces(">Z").workplane(offset=-250.0)
    .transformed(rotate=(90, 0, 0))
    .circle(18.0 / 2.0)
    .cutThruAll()
)

# Modelo consolidado listo para exportar STEP
# cq.exporters.export(poste, "poste_cac_12_400.step")
