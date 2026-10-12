"""
Armado Normalizado DGE PR-1: Estructura de Retención / Derivación / Terminal 22.9 kV
Componentes:
- Doble cruceta de retención F°G° L 75x75x6.4 mm x 2000 mm
- 03 Cortacircuitos fusibles tipo Cut-Out 27 kV / 100 A (BIL 150 kV)
- 03 Pararrayos poliméricos de óxido de zinc (ZnO) 21 kV / 10 kA
- 03 Cadenas de aisladores poliméricos de retención 25 kV
"""
import cadquery as cq

# Doble cruceta de retención separada 200 mm
cruceta_del = cq.Workplane("XY").box(2000.0, 75.0, 75.0).translate((0, 100.0, 0))
cruceta_tras = cq.Workplane("XY").box(2000.0, 75.0, 75.0).translate((0, -100.0, 0))
crucetas = cruceta_del.union(cruceta_tras)

# Soporte de cut-out y pararrayos
soporte_equipos = cq.Workplane("XY").box(1800.0, 50.0, 50.0).translate((0, 0, 600.0))

# Módulo de Cut-Out (Tubo aislante inclinado 20°)
def crear_cutout():
    cuerpo = cq.Workplane("XY").circle(25.0).extrude(400.0)
    aislador = cq.Workplane("XY").box(80.0, 80.0, 150.0).translate((0, 0, 150.0))
    return cuerpo.union(aislador).rotate((0,0,0), (1,0,0), 20)

# Módulo de Pararrayos ZnO
def crear_pararrayos_zno():
    cuerpo = cq.Workplane("XY").circle(35.0).extrude(380.0)
    for z in [60.0, 120.0, 180.0, 240.0, 300.0]:
        aleta = cq.Workplane("XY").workplane(offset=z).circle(55.0).extrude(15.0)
        cuerpo = cuerpo.union(aleta)
    return cuerpo

equipos = cq.Workplane("XY")
for x in [-600.0, 0.0, 600.0]:
    co = crear_cutout().translate((x, 150.0, 650.0))
    pa = crear_pararrayos_zno().translate((x, -150.0, 650.0))
    equipos = equipos.union(co).union(pa)

armado_pr1 = crucetas.union(soporte_equipos).union(equipos)
# cq.exporters.export(armado_pr1, "armado_dge_pr1_22_9kv.step")
