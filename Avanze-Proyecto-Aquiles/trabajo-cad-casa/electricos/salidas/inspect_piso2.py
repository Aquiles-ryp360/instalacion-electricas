#!/usr/bin/env python3
"""
Comprehensive inspection of electrico_piso2_v4.dxf
Extracts layer info, luminaria geometry, ground symbols, tablero/ducto locations,
and compares symbol style with piso 1.
"""

import ezdxf
import math
from collections import defaultdict

BASE = "/home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas"
PISO2 = f"{BASE}/electrico_piso2_v4.dxf"
PISO1 = f"{BASE}/electrico_piso1_v5.dxf"

def color_name(c):
    """Map ACI color index to a human-readable name."""
    names = {
        0: "BYBLOCK", 1: "Red", 2: "Yellow", 3: "Green", 4: "Cyan",
        5: "Blue", 6: "Magenta", 7: "White/Black", 8: "DarkGrey",
        9: "LightGrey", 10: "Red(10)", 30: "Orange(30)", 40: "Gold(40)",
        256: "BYLAYER"
    }
    return names.get(c, f"ACI-{c}")

def inspect_dxf(filepath, label="DXF"):
    """Inspect a DXF file and return structured data."""
    print(f"\n{'='*80}")
    print(f"  INSPECTING: {label}")
    print(f"  File: {filepath}")
    print(f"{'='*80}")

    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()

    # ─────────────────────────────────────────────
    # 1. ALL LAYERS WITH COLORS
    # ─────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("1. ALL LAYERS AND THEIR COLORS")
    print(f"{'─'*60}")
    layers_info = {}
    for layer in doc.layers:
        c = layer.color
        layers_info[layer.dxf.name] = c
        print(f"  Layer: {layer.dxf.name:40s}  Color: {c:3d} ({color_name(c)})")
    print(f"  Total layers: {len(layers_info)}")

    # ─────────────────────────────────────────────
    # 2. ENTITY TYPE CENSUS PER LAYER
    # ─────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("2. ENTITY TYPE CENSUS PER LAYER")
    print(f"{'─'*60}")
    census = defaultdict(lambda: defaultdict(int))
    all_entities = list(msp)
    for e in all_entities:
        layer = e.dxf.layer
        etype = e.dxftype()
        census[layer][etype] += 1

    for layer_name in sorted(census.keys()):
        types = census[layer_name]
        parts = ", ".join(f"{t}:{n}" for t, n in sorted(types.items()))
        print(f"  {layer_name:40s}  {parts}")

    # ─────────────────────────────────────────────
    # 3. HOW LUMINARIAS ARE DRAWN
    # ─────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("3. LUMINARIA ANALYSIS - How are they drawn?")
    print(f"{'─'*60}")

    lum_layers = [l for l in layers_info if 'LUMIN' in l.upper()]
    print(f"  Luminaria-related layers: {lum_layers}")

    # Check for INSERT (block references) on luminaria layers
    lum_inserts = [e for e in all_entities if e.dxftype() == 'INSERT' and 'LUMIN' in e.dxf.layer.upper()]
    if lum_inserts:
        print(f"  Found {len(lum_inserts)} INSERT (block reference) entities on luminaria layers:")
        block_names = set()
        for ins in lum_inserts:
            block_names.add(ins.dxf.name)
            print(f"    Block: {ins.dxf.name}, Position: ({ins.dxf.insert.x:.4f}, {ins.dxf.insert.y:.4f})")
        print(f"  Block names used: {block_names}")
    else:
        print("  No INSERT entities on luminaria layers - luminarias use loose geometry.")

    # Circles on luminaria layers
    lum_circles = [e for e in all_entities if e.dxftype() == 'CIRCLE' and 'LUMIN' in e.dxf.layer.upper()]
    print(f"\n  CIRCLE entities on luminaria layers: {len(lum_circles)}")
    for i, c in enumerate(lum_circles):
        cx, cy = c.dxf.center.x, c.dxf.center.y
        r = c.dxf.radius
        print(f"    Circle #{i+1}: center=({cx:.4f}, {cy:.4f}), radius={r:.4f}, layer={c.dxf.layer}")

    # Lines on luminaria layers
    lum_lines = [e for e in all_entities if e.dxftype() == 'LINE' and 'LUMIN' in e.dxf.layer.upper()]
    print(f"\n  LINE entities on luminaria layers: {len(lum_lines)}")
    for i, l in enumerate(lum_lines[:30]):  # cap display
        sx, sy = l.dxf.start.x, l.dxf.start.y
        ex, ey = l.dxf.end.x, l.dxf.end.y
        print(f"    Line #{i+1}: ({sx:.4f},{sy:.4f}) -> ({ex:.4f},{ey:.4f}), layer={l.dxf.layer}")
    if len(lum_lines) > 30:
        print(f"    ... and {len(lum_lines)-30} more lines")

    # Arcs on luminaria layers
    lum_arcs = [e for e in all_entities if e.dxftype() == 'ARC' and 'LUMIN' in e.dxf.layer.upper()]
    print(f"\n  ARC entities on luminaria layers: {len(lum_arcs)}")
    for i, a in enumerate(lum_arcs[:20]):
        cx, cy = a.dxf.center.x, a.dxf.center.y
        print(f"    Arc #{i+1}: center=({cx:.4f},{cy:.4f}), r={a.dxf.radius:.4f}, start={a.dxf.start_angle:.1f}°, end={a.dxf.end_angle:.1f}°")

    # ─────────────────────────────────────────────
    # 4. ELEC_PUESTA_TIERRA LAYER CHECK
    # ─────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("4. ELEC_PUESTA_TIERRA LAYER CHECK")
    print(f"{'─'*60}")
    tierra_layers = [l for l in layers_info if 'TIERRA' in l.upper() or 'GROUND' in l.upper() or 'EARTH' in l.upper()]
    if tierra_layers:
        print(f"  Found ground/earth layers: {tierra_layers}")
    else:
        print("  ⚠ NO layer with 'TIERRA', 'GROUND', or 'EARTH' found.")

    pat_layers = [l for l in layers_info if 'PAT' in l.upper() or 'SPAT' in l.upper()]
    if pat_layers:
        print(f"  Found PAT/SPAT layers: {pat_layers}")
    else:
        print("  No PAT/SPAT layers found.")

    # ─────────────────────────────────────────────
    # 5. GROUND/EARTH SYMBOL SEARCH
    # ─────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("5. GROUND/EARTH SYMBOL SEARCH (blocks, text, entities)")
    print(f"{'─'*60}")

    # Check block definitions
    ground_blocks = []
    for block in doc.blocks:
        bname = block.name.upper()
        if any(kw in bname for kw in ['TIERRA', 'GROUND', 'EARTH', 'GND', 'PAT', 'SPAT']):
            ground_blocks.append(block.name)
    if ground_blocks:
        print(f"  Block definitions related to ground: {ground_blocks}")
    else:
        print("  No block definitions with ground-related names found.")

    # Check all INSERT for ground-related block names
    ground_inserts = []
    for e in all_entities:
        if e.dxftype() == 'INSERT':
            bname = e.dxf.name.upper()
            if any(kw in bname for kw in ['TIERRA', 'GROUND', 'EARTH', 'GND', 'PAT', 'SPAT']):
                ground_inserts.append(e)
                print(f"  Ground INSERT: block={e.dxf.name}, pos=({e.dxf.insert.x:.4f},{e.dxf.insert.y:.4f}), layer={e.dxf.layer}")
    if not ground_inserts:
        print("  No INSERT entities with ground-related block names.")

    # ─────────────────────────────────────────────
    # 6. T2 AND VD LOCATIONS
    # ─────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("6. T2 (TABLERO SEGUNDO PISO) AND VD (DUCTO VERTICAL) LOCATIONS")
    print(f"{'─'*60}")

    # Search all text entities (TEXT, MTEXT, ATTRIB)
    text_entities = []
    for e in all_entities:
        etype = e.dxftype()
        if etype == 'TEXT':
            text_entities.append((e.dxf.text, e.dxf.insert.x, e.dxf.insert.y, e.dxf.layer, etype))
        elif etype == 'MTEXT':
            text_entities.append((e.text, e.dxf.insert.x, e.dxf.insert.y, e.dxf.layer, etype))
        elif etype == 'INSERT':
            # Check ATTRIB entities inside block references
            if hasattr(e, 'attribs'):
                for attr in e.attribs:
                    text_entities.append((attr.dxf.text, attr.dxf.insert.x, attr.dxf.insert.y, attr.dxf.layer, 'ATTRIB'))

    t2_found = []
    vd_found = []
    for txt, x, y, layer, etype in text_entities:
        txt_upper = txt.upper().strip()
        if 'T2' in txt_upper or 'TABLERO' in txt_upper:
            t2_found.append((txt, x, y, layer, etype))
            print(f"  T2 match: text='{txt}', pos=({x:.4f},{y:.4f}), layer={layer}, type={etype}")
        if 'VD' in txt_upper or 'DUCTO' in txt_upper or 'VERTICAL' in txt_upper:
            vd_found.append((txt, x, y, layer, etype))
            print(f"  VD match: text='{txt}', pos=({x:.4f},{y:.4f}), layer={layer}, type={etype}")

    if not t2_found:
        print("  ⚠ No text containing 'T2' or 'TABLERO' found.")
    if not vd_found:
        print("  ⚠ No text containing 'VD', 'DUCTO', or 'VERTICAL' found.")

    # Also check block names for T2/VD
    for e in all_entities:
        if e.dxftype() == 'INSERT':
            bname = e.dxf.name.upper()
            if 'T2' in bname or 'TABLERO' in bname:
                print(f"  T2 block INSERT: block={e.dxf.name}, pos=({e.dxf.insert.x:.4f},{e.dxf.insert.y:.4f}), layer={e.dxf.layer}")
            if 'VD' in bname or 'DUCTO' in bname:
                print(f"  VD block INSERT: block={e.dxf.name}, pos=({e.dxf.insert.x:.4f},{e.dxf.insert.y:.4f}), layer={e.dxf.layer}")

    # ─────────────────────────────────────────────
    # 7. ALL CIRCLES ON ELEC_LUMINARIAS + NEARBY LINES (+ or X pattern)
    # ─────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("7. CIRCLES ON ELEC_LUMINARIAS + NEARBY LINE PATTERNS")
    print(f"{'─'*60}")

    elec_lum_circles = [e for e in all_entities if e.dxftype() == 'CIRCLE' and e.dxf.layer == 'ELEC_LUMINARIAS']
    print(f"  Total CIRCLE entities on ELEC_LUMINARIAS: {len(elec_lum_circles)}")

    # Collect ALL lines in the file for proximity search
    all_lines = [e for e in all_entities if e.dxftype() == 'LINE']
    print(f"  Total LINE entities in file: {len(all_lines)}")

    SEARCH_RADIUS = 0.3

    def line_near_point(line, cx, cy, radius):
        """Check if a line's midpoint or endpoints are within radius of (cx,cy)."""
        sx, sy = line.dxf.start.x, line.dxf.start.y
        ex, ey = line.dxf.end.x, line.dxf.end.y
        mx, my = (sx+ex)/2, (sy+ey)/2
        for px, py in [(sx, sy), (ex, ey), (mx, my)]:
            d = math.sqrt((px - cx)**2 + (py - cy)**2)
            if d <= radius:
                return True
        return False

    def classify_line_angle(line):
        """Return the angle of a line in degrees [0, 180)."""
        sx, sy = line.dxf.start.x, line.dxf.start.y
        ex, ey = line.dxf.end.x, line.dxf.end.y
        angle = math.degrees(math.atan2(ey - sy, ex - sx)) % 180
        return angle

    luminaria_data = []
    for i, c in enumerate(elec_lum_circles):
        cx, cy = c.dxf.center.x, c.dxf.center.y
        r = c.dxf.radius
        nearby = [l for l in all_lines if line_near_point(l, cx, cy, SEARCH_RADIUS)]
        angles = [classify_line_angle(l) for l in nearby]

        # Classify pattern
        has_horiz = any(abs(a) < 10 or abs(a - 180) < 10 for a in angles)
        has_vert = any(abs(a - 90) < 10 for a in angles)
        has_diag1 = any(abs(a - 45) < 10 for a in angles)
        has_diag2 = any(abs(a - 135) < 10 for a in angles)

        if has_horiz and has_vert:
            pattern = "PLUS (+)"
        elif has_diag1 and has_diag2:
            pattern = "X-CROSS (×)"
        elif has_horiz or has_vert or has_diag1 or has_diag2:
            pattern = "PARTIAL"
        elif len(nearby) == 0:
            pattern = "NO LINES"
        else:
            pattern = f"OTHER ({len(nearby)} lines)"

        nearby_layers = set(l.dxf.layer for l in nearby)

        print(f"\n  Luminaria #{i+1}:")
        print(f"    Center: ({cx:.4f}, {cy:.4f}), Radius: {r:.4f}")
        print(f"    Nearby lines (r<{SEARCH_RADIUS}): {len(nearby)}")
        print(f"    Line angles: {[f'{a:.1f}°' for a in angles]}")
        print(f"    Pattern: {pattern}")
        print(f"    Nearby line layers: {nearby_layers}")
        for j, l in enumerate(nearby):
            sx, sy = l.dxf.start.x, l.dxf.start.y
            ex, ey = l.dxf.end.x, l.dxf.end.y
            print(f"      Line {j+1}: ({sx:.4f},{sy:.4f})->({ex:.4f},{ey:.4f}) layer={l.dxf.layer}")

        luminaria_data.append({
            'index': i+1, 'cx': cx, 'cy': cy, 'r': r,
            'pattern': pattern, 'nearby_count': len(nearby),
            'nearby_layers': nearby_layers
        })

    # ─────────────────────────────────────────────
    # 8. TEXT ENTITIES CONTAINING KEY TERMS
    # ─────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("8. TEXT ENTITIES CONTAINING KEY TERMS")
    print(f"{'─'*60}")
    keywords = ['SPAT', 'PAT', 'TIERRA', 'T2', 'VD', 'TABLERO', 'DUCTO', 'GROUND', 'EARTH']
    for txt, x, y, layer, etype in text_entities:
        txt_upper = txt.upper().strip()
        matched = [kw for kw in keywords if kw in txt_upper]
        if matched:
            print(f"  Text: '{txt}' | pos=({x:.4f},{y:.4f}) | layer={layer} | type={etype} | matched={matched}")

    # If nothing found at all
    any_match = any(any(kw in txt.upper().strip() for kw in keywords) for txt, *_ in text_entities)
    if not any_match:
        print("  ⚠ No text entities match any of the keywords.")

    # ─────────────────────────────────────────────
    # EXTRA: ALL TEXT ENTITIES (for context)
    # ─────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("EXTRA: ALL TEXT ENTITIES IN FILE")
    print(f"{'─'*60}")
    for txt, x, y, layer, etype in text_entities:
        print(f"  '{txt}' | pos=({x:.4f},{y:.4f}) | layer={layer} | type={etype}")
    if not text_entities:
        print("  No text entities found.")

    # ─────────────────────────────────────────────
    # EXTRA: ALL BLOCK DEFINITIONS
    # ─────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("EXTRA: ALL BLOCK DEFINITIONS")
    print(f"{'─'*60}")
    for block in doc.blocks:
        entities_in_block = list(block)
        etypes = defaultdict(int)
        for e in entities_in_block:
            etypes[e.dxftype()] += 1
        parts = ", ".join(f"{t}:{n}" for t, n in sorted(etypes.items()))
        print(f"  Block: '{block.name}' | entities: {len(entities_in_block)} | types: {parts}")

    # ─────────────────────────────────────────────
    # EXTRA: ALL INSERT entities
    # ─────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("EXTRA: ALL INSERT (BLOCK REFERENCE) ENTITIES")
    print(f"{'─'*60}")
    for e in all_entities:
        if e.dxftype() == 'INSERT':
            x, y = e.dxf.insert.x, e.dxf.insert.y
            print(f"  Block: '{e.dxf.name}' | pos=({x:.4f},{y:.4f}) | layer={e.dxf.layer}")

    return {
        'layers': layers_info,
        'census': dict(census),
        'lum_circles': elec_lum_circles,
        'luminaria_data': luminaria_data,
        'text_entities': text_entities,
    }


# ──────────────────────────────────────────────────────────────
# MAIN: Inspect both files and compare
# ──────────────────────────────────────────────────────────────
print("╔══════════════════════════════════════════════════════════════╗")
print("║  COMPREHENSIVE DXF INSPECTION - PISO 2 (v4)                ║")
print("║  With comparison to PISO 1 (v5)                            ║")
print("╚══════════════════════════════════════════════════════════════╝")

p2_data = inspect_dxf(PISO2, "PISO 2 (electrico_piso2_v4.dxf)")

print("\n\n")
print("╔══════════════════════════════════════════════════════════════╗")
print("║  PISO 1 REFERENCE INSPECTION (for comparison)              ║")
print("╚══════════════════════════════════════════════════════════════╝")

try:
    p1_data = inspect_dxf(PISO1, "PISO 1 (electrico_piso1_v5.dxf)")

    # ─────────────────────────────────────────────
    # 9. COMPARISON: PISO 1 vs PISO 2
    # ─────────────────────────────────────────────
    print(f"\n\n{'='*80}")
    print("9. COMPARISON: PISO 1 vs PISO 2 - SYMBOL STYLE CONSISTENCY")
    print(f"{'='*80}")

    # Layer comparison
    p1_layers = set(p1_data['layers'].keys())
    p2_layers = set(p2_data['layers'].keys())
    print(f"\n  Layers only in PISO 1: {p1_layers - p2_layers}")
    print(f"  Layers only in PISO 2: {p2_layers - p1_layers}")
    print(f"  Common layers: {p1_layers & p2_layers}")

    # Color comparison for common layers
    print(f"\n  Layer color comparison (common layers):")
    for l in sorted(p1_layers & p2_layers):
        c1, c2 = p1_data['layers'][l], p2_data['layers'][l]
        match = "✓" if c1 == c2 else "✗ MISMATCH"
        print(f"    {l:40s}  P1={c1:3d}  P2={c2:3d}  {match}")

    # Luminaria pattern comparison
    print(f"\n  Luminaria patterns comparison:")
    p1_patterns = set(d['pattern'] for d in p1_data['luminaria_data'])
    p2_patterns = set(d['pattern'] for d in p2_data['luminaria_data'])
    print(f"    PISO 1 patterns: {p1_patterns}")
    print(f"    PISO 2 patterns: {p2_patterns}")

    p1_radii = set(round(d['r'], 4) for d in p1_data['luminaria_data'])
    p2_radii = set(round(d['r'], 4) for d in p2_data['luminaria_data'])
    print(f"    PISO 1 radii: {p1_radii}")
    print(f"    PISO 2 radii: {p2_radii}")
    if p1_radii == p2_radii:
        print("    ✓ Circle radii are consistent between floors.")
    else:
        print("    ✗ Circle radii DIFFER between floors!")

    # Nearby line layers comparison
    p1_line_layers = set()
    for d in p1_data['luminaria_data']:
        p1_line_layers.update(d['nearby_layers'])
    p2_line_layers = set()
    for d in p2_data['luminaria_data']:
        p2_line_layers.update(d['nearby_layers'])
    print(f"    PISO 1 nearby line layers: {p1_line_layers}")
    print(f"    PISO 2 nearby line layers: {p2_line_layers}")

except FileNotFoundError:
    print(f"\n  ⚠ PISO 1 file not found at {PISO1}, skipping comparison.")
except Exception as ex:
    print(f"\n  ⚠ Error inspecting PISO 1: {ex}")

print(f"\n{'='*80}")
print("  INSPECTION COMPLETE")
print(f"{'='*80}")
