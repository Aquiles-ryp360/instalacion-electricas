"""
Retenida Mecánica Inclinada R-1 para Línea Primaria 22.9 kV
Componentes:
- Perno de ojo de F°G° 5/8" en cabeza de poste
- Cable de acero galvanizado Siemens-Martin 3/8" (Carga rotura 3150 kgf)
- Aislador de tracción tipo nuez ANSI 54-1 (a 3.0 m de altura)
- Varilla de anclaje de F°G° 5/8" x 2.40 m con guardacabo
- Bloque de concreto ciclópeo de anclaje 0.40 x 0.40 x 0.20 m enterrado a 1.80 m
"""
import cadquery as cq
import math

# Bloque de anclaje de concreto
bloque = cq.Workplane("XY").box(400.0, 400.0, 200.0).translate((8000.0, 0, -1800.0))

# Varilla de anclaje a 45°
varilla = (
    cq.Workplane("XY")
    .circle(16.0 / 2.0)
    .extrude(2400.0)
    .rotate((0,0,0), (0,1,0), -45)
    .translate((8000.0, 0, -1800.0))
)

# Cable de retenida
cable = (
    cq.Workplane("XY")
    .circle(9.52 / 2.0)
    .extrude(11500.0)
    .rotate((0,0,0), (0,1,0), -45)
    .translate((0, 0, 10500.0))
)

# Aislador tipo nuez
aislador_nuez = (
    cq.Workplane("XY")
    .box(110.0, 80.0, 140.0)
    .rotate((0,0,0), (0,1,0), -45)
    .translate((5500.0, 0, 3000.0))
)

retenida = bloque.union(varilla).union(cable).union(aislador_nuez)
# cq.exporters.export(retenida, "retenida_mecanica_r1.step")
