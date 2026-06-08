#!/usr/bin/env python3
"""
Edición directa de DXF maestros v4 para crear v6.
NO regenera desde JSON. Copia el DXF maestro y edita sobre la copia.

Correcciones aplicadas:
1. Luminarias: cambiar "+" a "X" (aspa diagonal)
2. Puesta a tierra: agregar SPAT en Piso 1
3. Conductor PE: agregar ruta de tierra
4. Verificar simbología consistente en ambos pisos
"""

import sys
import os
import shutil
import math

try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment
except ImportError:
    print("ERROR: ezdxf no disponible. Usar el venv de ia-cad-casas.", file=sys.stderr)
    sys.exit(1)

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", ".."))

PISO1_MASTER = os.path.join(BASE_DIR, "electrico_piso1_v4.dxf")
PISO2_MASTER = os.path.join(BASE_DIR, "electrico_piso2_v4.dxf")
PISO1_OUTPUT = os.path.join(BASE_DIR, "electrico_piso1_v6.dxf")
PISO2_OUTPUT = os.path.join(BASE_DIR, "electrico_piso2_v6.dxf")


def is_plus_line(line, circle_center, circle_radius, tolerance=0.05):
    """Detecta si una línea forma parte de un patrón '+' (horizontal o vertical)
    pasando por el centro de un círculo de luminaria."""
    cx, cy = circle_center
    sx, sy = line.dxf.start.x, line.dxf.start.y
    ex, ey = line.dxf.end.x, line.dxf.end.y

    # Verificar que la línea está cerca del círculo
    mid_x = (sx + ex) / 2
    mid_y = (sy + ey) / 2
    dist = math.sqrt((mid_x - cx)**2 + (mid_y - cy)**2)
    if dist > circle_radius * 1.5:
        return False

    # Verificar si es horizontal (misma Y ~= center Y)
    is_horizontal = (abs(sy - cy) < tolerance and abs(ey - cy) < tolerance and
                     abs(sy - ey) < tolerance)
    # Verificar si es vertical (misma X ~= center X)
    is_vertical = (abs(sx - cx) < tolerance and abs(ex - cx) < tolerance and
                   abs(sx - ex) < tolerance)

    return is_horizontal or is_vertical


def find_luminaria_plus_lines(msp, circles_on_layer):
    """Para cada círculo de luminaria, encontrar las líneas '+' asociadas."""
    results = []
    # Collect all LINE entities on ELEC_LUMINARIAS
    all_lines = [e for e in msp if e.dxftype() == 'LINE' and
                 e.dxf.layer == 'ELEC_LUMINARIAS']

    for circle in circles_on_layer:
        cx = circle.dxf.center.x
        cy = circle.dxf.center.y
        r = circle.dxf.radius
        plus_lines = []
        for line in all_lines:
            if is_plus_line(line, (cx, cy), r):
                plus_lines.append(line)
        results.append({
            'circle': circle,
            'cx': cx, 'cy': cy, 'r': r,
            'plus_lines': plus_lines
        })
    return results


def replace_plus_with_x(msp, luminaria_data):
    """Elimina las líneas '+' y dibuja líneas 'X' (aspa diagonal)."""
    count = 0
    for lum in luminaria_data:
        cx, cy, r = lum['cx'], lum['cy'], lum['r']

        # Eliminar líneas '+' existentes
        for line in lum['plus_lines']:
            msp.delete_entity(line)

        # Dibujar aspa 'X' — líneas diagonales completas que cruzan el círculo
        # Factor para que las diagonales toquen el borde del círculo
        d = r * 0.707  # r * cos(45°) = r * sin(45°)

        # Diagonal inferior-izquierda a superior-derecha
        msp.add_line(
            (cx - d, cy - d), (cx + d, cy + d),
            dxfattribs={'layer': 'ELEC_LUMINARIAS'}
        )
        # Diagonal superior-izquierda a inferior-derecha
        msp.add_line(
            (cx - d, cy + d), (cx + d, cy - d),
            dxfattribs={'layer': 'ELEC_LUMINARIAS'}
        )
        count += 1
        print(f"  Luminaria en ({cx:.2f}, {cy:.2f}): "
              f"eliminadas {len(lum['plus_lines'])} líneas '+', "
              f"dibujadas 2 diagonales 'X'")

    return count


def add_spat_symbol(msp, doc, x, y, scale=1.0):
    """Dibuja símbolo de puesta a tierra estándar (3 líneas decrecientes).
    Ubicación: cerca del medidor/TG en zona exterior."""
    layer = "ELEC_PUESTA_TIERRA"

    # Crear capa si no existe
    if layer not in doc.layers:
        doc.layers.new(layer, dxfattribs={
            'color': 3,  # Verde
            'lineweight': 25,
        })
        print(f"  Capa '{layer}' creada")

    r = 0.20 * scale  # Radio base del símbolo

    # Línea vertical de conexión (hacia arriba, desde donde conectará la ruta)
    msp.add_line((x, y + r * 0.5), (x, y), dxfattribs={'layer': layer})

    # Tres líneas horizontales decrecientes (símbolo estándar de tierra)
    msp.add_line((x - r, y), (x + r, y), dxfattribs={'layer': layer})
    msp.add_line((x - r * 0.65, y - r * 0.35), (x + r * 0.65, y - r * 0.35),
                 dxfattribs={'layer': layer})
    msp.add_line((x - r * 0.30, y - r * 0.70), (x + r * 0.30, y - r * 0.70),
                 dxfattribs={'layer': layer})

    # Etiqueta SPAT
    text = msp.add_text(
        "SPAT",
        dxfattribs={
            'layer': layer,
            'height': 0.16 * scale,
        }
    )
    text.set_placement((x, y - r * 1.2), align=TextEntityAlignment.MIDDLE_CENTER)

    # Nota técnica pequeña debajo
    note = msp.add_text(
        "Puesta a tierra",
        dxfattribs={
            'layer': layer,
            'height': 0.10 * scale,
        }
    )
    note.set_placement((x, y - r * 1.7), align=TextEntityAlignment.MIDDLE_CENTER)

    print(f"  SPAT agregado en ({x:.2f}, {y:.2f})")


def add_pe_route(msp, doc, points, label="PE"):
    """Agrega ruta de conductor de protección (tierra)."""
    layer = "ELEC_PUESTA_TIERRA"

    # Asegurar capa
    if layer not in doc.layers:
        doc.layers.new(layer, dxfattribs={'color': 3, 'lineweight': 25})

    # Asegurar linetype DASHED
    if "DASHED" not in doc.linetypes:
        try:
            doc.linetypes.new(
                "DASHED",
                dxfattribs={
                    "description": "Dashed __ __ __",
                    "pattern": [0.60, 0.35, -0.15],
                },
            )
        except Exception:
            pass

    # Dibujar polilínea punteada
    msp.add_lwpolyline(
        points,
        dxfattribs={'layer': layer, 'linetype': 'DASHED'}
    )

    # Etiqueta en el punto medio
    mid_idx = len(points) // 2
    mx, my = points[mid_idx]
    text = msp.add_text(
        label,
        dxfattribs={
            'layer': 'ELEC_TEXTOS',
            'height': 0.12,
        }
    )
    text.set_placement((mx, my + 0.18), align=TextEntityAlignment.MIDDLE_CENTER)

    print(f"  Ruta PE agregada: {len(points)} puntos")


def process_piso1():
    """Procesa Piso 1: copiar v4 → v6, corregir luminarias, agregar SPAT."""
    print("=" * 60)
    print("PROCESANDO PISO 1")
    print("=" * 60)

    if not os.path.exists(PISO1_MASTER):
        print(f"ERROR: No existe el DXF maestro: {PISO1_MASTER}")
        return False

    # 1. Copiar maestro
    shutil.copy2(PISO1_MASTER, PISO1_OUTPUT)
    print(f"Copiado: {PISO1_MASTER} → {PISO1_OUTPUT}")

    # 2. Abrir la copia
    doc = ezdxf.readfile(PISO1_OUTPUT)
    msp = doc.modelspace()

    # 3. Encontrar luminarias con '+'
    print("\n--- Corrigiendo luminarias (+) → (X) ---")
    circles = [e for e in msp if e.dxftype() == 'CIRCLE' and
               e.dxf.layer == 'ELEC_LUMINARIAS']
    print(f"Encontradas {len(circles)} luminarias (círculos)")

    lum_data = find_luminaria_plus_lines(msp, circles)
    fixed = replace_plus_with_x(msp, lum_data)
    print(f"Luminarias corregidas: {fixed}")

    # 4. Agregar SPAT
    print("\n--- Agregando puesta a tierra (SPAT) ---")
    # Ubicación: exterior, cerca del medidor M(15.45, 4.75)
    # Poner el SPAT debajo del medidor, en la zona exterior
    spat_x = 15.45
    spat_y = 3.60  # debajo del medidor, zona exterior frontal
    add_spat_symbol(msp, doc, spat_x, spat_y)

    # 5. Agregar ruta de conductor PE: SPAT → TG
    print("\n--- Agregando conductor de protección PE ---")
    # Ruta: SPAT (15.45, 3.60+0.60=4.10) → baja a TG (14.35, 4.75)
    pe_points = [
        (spat_x, spat_y + 0.30),  # Desde arriba del símbolo SPAT
        (spat_x, 4.75),           # Sube al nivel del TG
        (14.35, 4.75),            # Conecta al TG
    ]
    add_pe_route(msp, doc, pe_points, label="PE")

    # 6. Guardar
    doc.saveas(PISO1_OUTPUT)
    print(f"\nGuardado: {PISO1_OUTPUT}")
    print(f"Tamaño: {os.path.getsize(PISO1_OUTPUT)} bytes")
    return True


def process_piso2():
    """Procesa Piso 2: copiar v4 → v6, corregir luminarias."""
    print("\n" + "=" * 60)
    print("PROCESANDO PISO 2")
    print("=" * 60)

    if not os.path.exists(PISO2_MASTER):
        print(f"ERROR: No existe el DXF maestro: {PISO2_MASTER}")
        return False

    # 1. Copiar maestro
    shutil.copy2(PISO2_MASTER, PISO2_OUTPUT)
    print(f"Copiado: {PISO2_MASTER} → {PISO2_OUTPUT}")

    # 2. Abrir la copia
    doc = ezdxf.readfile(PISO2_OUTPUT)
    msp = doc.modelspace()

    # 3. Encontrar luminarias con '+'
    print("\n--- Corrigiendo luminarias (+) → (X) ---")
    circles = [e for e in msp if e.dxftype() == 'CIRCLE' and
               e.dxf.layer == 'ELEC_LUMINARIAS']
    print(f"Encontradas {len(circles)} luminarias (círculos)")

    lum_data = find_luminaria_plus_lines(msp, circles)
    fixed = replace_plus_with_x(msp, lum_data)
    print(f"Luminarias corregidas: {fixed}")

    # 4. Crear capa ELEC_PUESTA_TIERRA (para consistencia, aunque
    # el SPAT físico está en piso 1)
    layer = "ELEC_PUESTA_TIERRA"
    if layer not in doc.layers:
        doc.layers.new(layer, dxfattribs={'color': 3, 'lineweight': 25})
        print(f"\nCapa '{layer}' creada para consistencia")

    # 5. Agregar nota de PE en el plano
    # El conductor PE sube desde el TG (piso 1) por el ducto VD hasta T2
    print("\n--- Agregando indicación de conductor PE ---")
    # VD está en (2.65, 4.80), T2 en (12.55, 4.25)
    # La ruta existente VD→T2 ya existe como canalización
    # Agregamos indicación textual de PE
    pe_note = msp.add_text(
        "PE (desde SPAT P1)",
        dxfattribs={
            'layer': layer,
            'height': 0.10,
        }
    )
    pe_note.set_placement((2.65, 4.45), align=TextEntityAlignment.MIDDLE_CENTER)

    # 6. Guardar
    doc.saveas(PISO2_OUTPUT)
    print(f"\nGuardado: {PISO2_OUTPUT}")
    print(f"Tamaño: {os.path.getsize(PISO2_OUTPUT)} bytes")
    return True


def verify_output(filepath, label):
    """Verifica el DXF generado."""
    print(f"\n--- Verificación: {label} ---")
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()

    # Verificar capas
    layers = [l.dxf.name for l in doc.layers]
    has_pat = 'ELEC_PUESTA_TIERRA' in layers
    print(f"  Capa ELEC_PUESTA_TIERRA: {'SÍ' if has_pat else 'NO'}")

    # Contar entidades por capa
    layer_counts = {}
    for e in msp:
        ln = e.dxf.layer
        layer_counts[ln] = layer_counts.get(ln, 0) + 1

    print(f"  Entidades por capa:")
    for ln in sorted(layer_counts.keys()):
        print(f"    {ln}: {layer_counts[ln]}")

    # Verificar luminarias
    circles = [e for e in msp if e.dxftype() == 'CIRCLE' and
               e.dxf.layer == 'ELEC_LUMINARIAS']
    lines_lum = [e for e in msp if e.dxftype() == 'LINE' and
                 e.dxf.layer == 'ELEC_LUMINARIAS']
    print(f"  Luminarias (círculos): {len(circles)}")
    print(f"  Líneas en ELEC_LUMINARIAS: {len(lines_lum)}")

    # Verificar que las líneas de luminaria son diagonales (no ortogonales)
    ortho_count = 0
    diag_count = 0
    for line in lines_lum:
        dx = abs(line.dxf.end.x - line.dxf.start.x)
        dy = abs(line.dxf.end.y - line.dxf.start.y)
        if dx < 0.01 or dy < 0.01:
            ortho_count += 1
        elif abs(dx - dy) < 0.02:
            diag_count += 1

    if ortho_count > 0:
        print(f"  ⚠️  ADVERTENCIA: {ortho_count} líneas ortogonales (posibles '+')")
    if diag_count > 0:
        print(f"  ✓ {diag_count} líneas diagonales (aspas 'X')")

    # Verificar textos SPAT
    spat_texts = [e for e in msp if e.dxftype() in ('TEXT', 'MTEXT')
                  and 'SPAT' in getattr(e.dxf, 'text', '').upper()]
    print(f"  Textos SPAT: {len(spat_texts)}")

    # Verificar TG/M/T2
    for keyword in ['TG', 'M', 'T2', 'VD']:
        found = [e for e in msp if e.dxftype() in ('TEXT', 'MTEXT')
                 and keyword in getattr(e.dxf, 'text', '').upper()]
        if found:
            print(f"  Texto '{keyword}' encontrado: {len(found)} veces")

    return True


if __name__ == '__main__':
    print("Script de edición directa de DXF maestros")
    print("NO regenera desde JSON — edita copias de los DXF v4")
    print()

    ok1 = process_piso1()
    ok2 = process_piso2()

    if ok1:
        verify_output(PISO1_OUTPUT, "Piso 1 v6")
    if ok2:
        verify_output(PISO2_OUTPUT, "Piso 2 v6")

    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    print(f"Piso 1: {'✓ OK' if ok1 else '✗ ERROR'} → {PISO1_OUTPUT}")
    print(f"Piso 2: {'✓ OK' if ok2 else '✗ ERROR'} → {PISO2_OUTPUT}")
    print()
    print("Nota: Los DXF maestros v4 NO fueron modificados.")
    print("Las nuevas versiones v6 contienen todas las correcciones.")
