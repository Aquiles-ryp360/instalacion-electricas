"""
Armado Normalizado DGE PS-1: Estructura de Alineamiento y Suspensión en Media Tensión 22.9 kV
Componentes:
- Poste C.A.C. 12 m
- Cruceta simétrica de acero galvanizado en caliente L 75x75x6.4 mm x 1.50 m
- Aisladores tipo Pin ANSI 56-3 (25 kV) con espiga de F°G° 3/4"
- Conductor AAAC 35 mm² fijado con atadura preformada
"""
import cadquery as cq

# 1. Cruceta angular L 75x75x6.4 mm x 1500 mm
CRUCETA_L = 1500.0
L_ALA = 75.0
E_CHAPA = 6.4

cruceta = (
    cq.Workplane("XY")
    .rect(CRUCETA_L, L_ALA)
    .extrude(E_CHAPA)
)

# 2. Espigas y aisladores tipo Pin (Fase central en cima, laterales en extremos)
def crear_aislador_pin():
    cuerpo = (
        cq.Workplane("XY")
        .circle(120.0)
        .extrude(80.0)
        .faces(">Z").workplane()
        .circle(90.0)
        .extrude(70.0)
        .faces(">Z").workplane()
        .circle(50.0)
        .extrude(60.0)
    )
    return cuerpo

aislador_izq = crear_aislador_pin().translate((-650.0, 0, E_CHAPA))
aislador_der = crear_aislador_pin().translate((650.0, 0, E_CHAPA))
aislador_cen = crear_aislador_pin().translate((0.0, 0, E_CHAPA + 250.0))

armado_ps1 = cruceta.union(aislador_izq).union(aislador_der).union(aislador_cen)
# cq.exporters.export(armado_ps1, "armado_dge_ps1_22_9kv.step")
