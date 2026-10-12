"""
Armado Normalizado DGE PA-1: Estructura de Ángulo en Media Tensión 22.9 kV
Componentes:
- Poste C.A.C. 12/400
- Cruceta angular de arriostre y retención L 75x75x6.4 mm
- Cadenas de aisladores poliméricos de suspensión 25 kV (6 aletas HTV, longitud 450 mm)
- Grapas de anclaje de aleación de aluminio tipo pistola
"""
import cadquery as cq

# Cruceta de ángulo reforzada
cruceta = cq.Workplane("XY").box(1800.0, 80.0, 80.0)

# Cadena de aislador polimérico (cilindro de núcleo + 6 aletas)
def crear_aislador_polimerico():
    nucleo = cq.Workplane("XY").circle(15.0).extrude(450.0)
    aletas = cq.Workplane("XY")
    for z in [80.0, 140.0, 200.0, 260.0, 320.0, 380.0]:
        aleta = (
            cq.Workplane("XY")
            .workplane(offset=z)
            .circle(60.0)
            .extrude(12.0)
        )
        nucleo = nucleo.union(aleta)
    return nucleo

aislador_1 = crear_aislador_polimerico().rotate((0, 0, 0), (1, 0, 0), 90).translate((-750.0, 250.0, 0))
aislador_2 = crear_aislador_polimerico().rotate((0, 0, 0), (1, 0, 0), 90).translate((0.0, 250.0, 0))
aislador_3 = crear_aislador_polimerico().rotate((0, 0, 0), (1, 0, 0), 90).translate((750.0, 250.0, 0))

armado_pa1 = cruceta.union(aislador_1).union(aislador_2).union(aislador_3)
# cq.exporters.export(armado_pa1, "armado_dge_pa1_22_9kv.step")
