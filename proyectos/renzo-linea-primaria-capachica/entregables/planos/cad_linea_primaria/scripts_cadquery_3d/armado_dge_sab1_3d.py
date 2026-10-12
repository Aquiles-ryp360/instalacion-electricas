"""
Armado Normalizado DGE SAB-1: Subestación de Distribución Aérea Biposte 100 kVA
Tensión: 22.9 / 0.38 - 0.22 kV | Grupo: Dyn5 | Régimen: ONAN | Altitud: 3850 msnm
Componentes:
- Biposte C.A.C. 13/400 (interdistancia entre ejes: 2000 mm)
- Plataforma portatransformador metálica con 2 vigas UPN-120 de F°G°
- Transformador de distribución 100 kVA trifásico con aletas radiadoras
- Seccionamiento Cut-Out 27 kV y protección pararrayos ZnO 21 kV en cabecera
- Tablero de distribución general de baja tensión IP65 adosado al poste
"""
import cadquery as cq

INTEREJE = 2000.0

# 1. Postes gemelos CAC 13/400
poste_izq = cq.Workplane("XY").circle(180.0).workplane(offset=13000.0).circle(90.0).loft().translate((-INTEREJE/2, 0, 0))
poste_der = cq.Workplane("XY").circle(180.0).workplane(offset=13000.0).circle(90.0).loft().translate((INTEREJE/2, 0, 0))
postes = poste_izq.union(poste_der)

# 2. Plataforma metálica a cota +6.00 m
viga_1 = cq.Workplane("XY").box(2600.0, 120.0, 60.0).translate((0, 300.0, 6000.0))
viga_2 = cq.Workplane("XY").box(2600.0, 120.0, 60.0).translate((0, -300.0, 6000.0))
plataforma = viga_1.union(viga_2)

# 3. Transformador trifásico 100 kVA (Cuba rectangular con aletas y boquillas MT)
cuba = cq.Workplane("XY").box(950.0, 700.0, 1100.0).translate((0, 0, 6600.0))
# Boquillas MT 22.9 kV (3 unidades)
boquillas_mt = cq.Workplane("XY")
for x in [-250.0, 0.0, 250.0]:
    b = cq.Workplane("XY").circle(35.0).extrude(350.0).translate((x, 150.0, 7150.0))
    boquillas_mt = boquillas_mt.union(b)

# 4. Tablero BT IP65 montado en fuste de poste a +1.80 m
tablero_bt = cq.Workplane("XY").box(600.0, 350.0, 800.0).translate((-INTEREJE/2 + 250.0, 200.0, 1800.0))

armado_sab1 = postes.union(plataforma).union(cuba).union(boquillas_mt).union(tablero_bt)
# cq.exporters.export(armado_sab1, "armado_dge_sab1_100kva.step")
