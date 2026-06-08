#!/usr/bin/env python3
"""
Comprehensive inspection of electrico_piso1_v4.dxf
Extracts: layers, luminaria geometry, ground symbols, TG/M locations, etc.
"""
import ezdxf
import math
from collections import defaultdict

DXF_PATH = "electrico_piso1_v4.dxf"

def main():
    doc = ezdxf.readfile(DXF_PATH)
    msp = doc.modelspace()

    # =========================================================================
    # 1. All layer names and their colors
    # =========================================================================
    print("=" * 80)
    print("1. ALL LAYERS AND COLORS")
    print("=" * 80)
    layers_sorted = sorted(doc.layers, key=lambda l: l.dxf.name)
    for layer in layers_sorted:
        name = layer.dxf.name
        color = layer.dxf.color
        linetype = layer.dxf.get("linetype", "Continuous")
        is_off = layer.is_off()
        is_frozen = layer.is_frozen()
        flags = []
        if is_off:
            flags.append("OFF")
        if is_frozen:
            flags.append("FROZEN")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        print(f"  Layer: {name:<40} Color: {color:<5} Linetype: {linetype}{flag_str}")

    # =========================================================================
    # 2. How luminarias are drawn
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. HOW LUMINARIAS ARE DRAWN")
    print("=" * 80)

    # Check for ELEC_LUMINARIAS layer
    lum_layers = [l.dxf.name for l in doc.layers if "LUMIN" in l.dxf.name.upper()]
    print(f"  Luminaria-related layers: {lum_layers}")

    # Count entity types on luminaria layers
    lum_entity_counts = defaultdict(int)
    lum_entities = []
    for entity in msp:
        layer = entity.dxf.get("layer", "0")
        if "LUMIN" in layer.upper():
            lum_entity_counts[entity.dxftype()] += 1
            lum_entities.append(entity)

    print(f"  Entity type counts on luminaria layers:")
    for etype, count in sorted(lum_entity_counts.items()):
        print(f"    {etype}: {count}")

    # Check if there are INSERT (block references) for luminarias
    insert_blocks = defaultdict(int)
    for entity in msp:
        if entity.dxftype() == "INSERT":
            layer = entity.dxf.get("layer", "0")
            block_name = entity.dxf.name
            if "LUMIN" in layer.upper() or "LUMIN" in block_name.upper():
                insert_blocks[block_name] += 1
    if insert_blocks:
        print(f"  Block references (INSERT) related to luminarias:")
        for bname, count in sorted(insert_blocks.items()):
            print(f"    Block '{bname}': {count} insertions")
    else:
        print(f"  No block references found for luminarias - likely loose geometry")

    # =========================================================================
    # 3. Whether ELEC_PUESTA_TIERRA layer exists
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. ELEC_PUESTA_TIERRA LAYER CHECK")
    print("=" * 80)
    tierra_layers = [l.dxf.name for l in doc.layers if "TIERRA" in l.dxf.name.upper()]
    if tierra_layers:
        print(f"  Found tierra-related layers: {tierra_layers}")
        for tl in tierra_layers:
            count = sum(1 for e in msp if e.dxf.get("layer", "0") == tl)
            print(f"    Layer '{tl}' has {count} entities")
    else:
        print("  NO layer containing 'TIERRA' found")

    puesta_tierra = any("PUESTA_TIERRA" in l.dxf.name.upper() for l in doc.layers)
    print(f"  ELEC_PUESTA_TIERRA exists: {puesta_tierra}")

    # =========================================================================
    # 4. Whether any ground/earth symbol exists
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. GROUND/EARTH SYMBOL CHECK")
    print("=" * 80)

    # Search for blocks that might be ground symbols
    ground_keywords = ["GROUND", "EARTH", "TIERRA", "GND", "SPAT", "PAT", "PUESTA"]
    ground_blocks = []
    for block in doc.blocks:
        bname = block.name.upper()
        for kw in ground_keywords:
            if kw in bname:
                ground_blocks.append(block.name)
                break
    if ground_blocks:
        print(f"  Ground-related blocks found: {ground_blocks}")
    else:
        print("  No ground-related blocks found by name")

    # Search for INSERT entities with ground-related block names
    ground_inserts = []
    for entity in msp:
        if entity.dxftype() == "INSERT":
            bname = entity.dxf.name.upper()
            for kw in ground_keywords:
                if kw in bname:
                    pos = entity.dxf.insert
                    ground_inserts.append((entity.dxf.name, entity.dxf.layer, pos))
                    break
    if ground_inserts:
        print(f"  Ground-related block insertions:")
        for bname, layer, pos in ground_inserts:
            print(f"    Block '{bname}' on layer '{layer}' at ({pos.x:.4f}, {pos.y:.4f})")
    else:
        print("  No ground-related block insertions found")

    # =========================================================================
    # 5. Location of TG (tablero general) and M (medidor)
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. TG (TABLERO GENERAL) AND M (MEDIDOR) LOCATIONS")
    print("=" * 80)

    # Search TEXT and MTEXT entities
    tg_texts = []
    m_texts = []
    for entity in msp:
        if entity.dxftype() in ("TEXT", "MTEXT"):
            if entity.dxftype() == "TEXT":
                text = entity.dxf.text
                pos = entity.dxf.get("insert", None)
            else:
                text = entity.text
                pos = entity.dxf.get("insert", None)

            text_upper = text.strip().upper()

            # TG detection
            if text_upper in ("TG", "TABLERO GENERAL") or "TABLERO" in text_upper:
                if pos:
                    tg_texts.append((text, entity.dxf.layer, pos.x, pos.y))
                else:
                    tg_texts.append((text, entity.dxf.layer, None, None))

            # M / Medidor detection
            if text_upper in ("M", "MEDIDOR") or ("MEDID" in text_upper):
                if pos:
                    m_texts.append((text, entity.dxf.layer, pos.x, pos.y))
                else:
                    m_texts.append((text, entity.dxf.layer, None, None))

    if tg_texts:
        print(f"  TG-related text entities:")
        for text, layer, x, y in tg_texts:
            print(f"    Text='{text}' Layer='{layer}' Position=({x:.4f}, {y:.4f})" if x else f"    Text='{text}' Layer='{layer}' Position=N/A")
    else:
        print("  No TG text entities found")

    if m_texts:
        print(f"  M/Medidor-related text entities:")
        for text, layer, x, y in m_texts:
            print(f"    Text='{text}' Layer='{layer}' Position=({x:.4f}, {y:.4f})" if x else f"    Text='{text}' Layer='{layer}' Position=N/A")
    else:
        print("  No M/Medidor text entities found")

    # Also search for TG/M block inserts
    tg_blocks = []
    m_blocks = []
    for entity in msp:
        if entity.dxftype() == "INSERT":
            bname = entity.dxf.name.upper()
            pos = entity.dxf.insert
            if "TG" in bname or "TABLERO" in bname:
                tg_blocks.append((entity.dxf.name, entity.dxf.layer, pos.x, pos.y))
            if bname == "M" or "MEDIDOR" in bname:
                m_blocks.append((entity.dxf.name, entity.dxf.layer, pos.x, pos.y))

    if tg_blocks:
        print(f"  TG-related block insertions:")
        for bname, layer, x, y in tg_blocks:
            print(f"    Block '{bname}' Layer='{layer}' at ({x:.4f}, {y:.4f})")
    if m_blocks:
        print(f"  M/Medidor-related block insertions:")
        for bname, layer, x, y in m_blocks:
            print(f"    Block '{bname}' Layer='{layer}' at ({x:.4f}, {y:.4f})")

    # Broader search: any text that is exactly "TG" or "M"
    print("\n  --- Broader text search for exact 'TG' and 'M' ---")
    for entity in msp:
        if entity.dxftype() == "TEXT":
            text = entity.dxf.text.strip()
            if text.upper() == "TG" or text.upper() == "M":
                pos = entity.dxf.get("insert", None)
                if pos:
                    print(f"    TEXT='{text}' Layer='{entity.dxf.layer}' at ({pos.x:.4f}, {pos.y:.4f})")
        elif entity.dxftype() == "MTEXT":
            text = entity.text.strip()
            # MTEXT can have formatting codes, strip them
            import re
            clean = re.sub(r'\\[A-Za-z][^;]*;', '', text)
            clean = clean.replace('{', '').replace('}', '').strip()
            if clean.upper() == "TG" or clean.upper() == "M":
                pos = entity.dxf.get("insert", None)
                if pos:
                    print(f"    MTEXT='{text}' (clean='{clean}') Layer='{entity.dxf.layer}' at ({pos.x:.4f}, {pos.y:.4f})")

    # =========================================================================
    # 6. All CIRCLE entities on ELEC_LUMINARIAS
    # =========================================================================
    print("\n" + "=" * 80)
    print("6. CIRCLE ENTITIES ON ELEC_LUMINARIAS")
    print("=" * 80)

    lum_circles = []
    for entity in msp:
        if entity.dxftype() == "CIRCLE" and "LUMIN" in entity.dxf.get("layer", "").upper():
            center = entity.dxf.center
            radius = entity.dxf.radius
            lum_circles.append((center.x, center.y, radius, entity.dxf.layer))
            print(f"  Circle center=({center.x:.4f}, {center.y:.4f}) radius={radius:.4f} layer={entity.dxf.layer}")

    print(f"\n  Total luminaria circles: {len(lum_circles)}")

    # =========================================================================
    # 7. For each luminaria circle, find nearby LINEs (+ or X pattern)
    # =========================================================================
    print("\n" + "=" * 80)
    print("7. NEARBY LINE ENTITIES FOR EACH LUMINARIA CIRCLE (within 0.3)")
    print("=" * 80)

    # Collect all LINE entities
    all_lines = []
    for entity in msp:
        if entity.dxftype() == "LINE":
            start = entity.dxf.start
            end = entity.dxf.end
            all_lines.append((start.x, start.y, end.x, end.y, entity.dxf.layer))

    search_radius = 0.3
    for i, (cx, cy, cr, clayer) in enumerate(lum_circles):
        nearby = []
        for (sx, sy, ex, ey, llayer) in all_lines:
            # Check if either endpoint is within search_radius of circle center
            d_start = math.sqrt((sx - cx)**2 + (sy - cy)**2)
            d_end = math.sqrt((ex - cx)**2 + (ey - cy)**2)
            # Also check midpoint
            mx, my = (sx + ex) / 2, (sy + ey) / 2
            d_mid = math.sqrt((mx - cx)**2 + (my - cy)**2)
            if d_start <= search_radius or d_end <= search_radius or d_mid <= search_radius:
                nearby.append((sx, sy, ex, ey, llayer))

        if nearby:
            print(f"\n  Circle #{i+1} center=({cx:.4f}, {cy:.4f}) r={cr:.4f}")
            for (sx, sy, ex, ey, llayer) in nearby:
                length = math.sqrt((ex - sx)**2 + (ey - sy)**2)
                # Determine orientation
                dx = ex - sx
                dy = ey - sy
                if abs(dx) < 0.001:
                    orient = "VERTICAL"
                elif abs(dy) < 0.001:
                    orient = "HORIZONTAL"
                else:
                    angle = math.degrees(math.atan2(dy, dx))
                    orient = f"ANGLED({angle:.1f}°)"
                print(f"    LINE ({sx:.4f},{sy:.4f})->({ex:.4f},{ey:.4f}) len={length:.4f} {orient} layer={llayer}")
        else:
            print(f"\n  Circle #{i+1} center=({cx:.4f}, {cy:.4f}) r={cr:.4f} - NO nearby lines")

    # =========================================================================
    # 8. TEXT entities containing 'SPAT', 'PAT', 'tierra'
    # =========================================================================
    print("\n" + "=" * 80)
    print("8. TEXT ENTITIES CONTAINING 'SPAT', 'PAT', 'TIERRA'")
    print("=" * 80)

    search_terms = ["SPAT", "PAT", "TIERRA"]
    found_any = False
    for entity in msp:
        if entity.dxftype() in ("TEXT", "MTEXT"):
            if entity.dxftype() == "TEXT":
                text = entity.dxf.text
            else:
                text = entity.text
            text_upper = text.upper()
            matched_terms = [t for t in search_terms if t in text_upper]
            if matched_terms:
                found_any = True
                pos = entity.dxf.get("insert", None)
                if pos:
                    print(f"  {entity.dxftype()} text='{text}' layer={entity.dxf.layer} at ({pos.x:.4f}, {pos.y:.4f}) matched: {matched_terms}")
                else:
                    print(f"  {entity.dxftype()} text='{text}' layer={entity.dxf.layer} matched: {matched_terms}")

    if not found_any:
        print("  No text entities found matching SPAT, PAT, or TIERRA")

    # =========================================================================
    # BONUS: Summary of all entity types and counts
    # =========================================================================
    print("\n" + "=" * 80)
    print("BONUS: ENTITY TYPE SUMMARY (entire modelspace)")
    print("=" * 80)
    entity_counts = defaultdict(int)
    for entity in msp:
        entity_counts[entity.dxftype()] += 1
    for etype, count in sorted(entity_counts.items()):
        print(f"  {etype}: {count}")

    # =========================================================================
    # BONUS: All block definitions
    # =========================================================================
    print("\n" + "=" * 80)
    print("BONUS: ALL BLOCK DEFINITIONS")
    print("=" * 80)
    for block in doc.blocks:
        if block.name.startswith("*"):
            continue  # skip anonymous blocks for brevity
        ent_count = len(list(block))
        if ent_count > 0:
            ent_types = defaultdict(int)
            for e in block:
                ent_types[e.dxftype()] += 1
            ent_str = ", ".join(f"{k}:{v}" for k, v in sorted(ent_types.items()))
            print(f"  Block '{block.name}': {ent_count} entities ({ent_str})")

    # =========================================================================
    # BONUS: All INSERT entities (block references) summary
    # =========================================================================
    print("\n" + "=" * 80)
    print("BONUS: ALL INSERT (BLOCK REF) ENTITIES IN MODELSPACE")
    print("=" * 80)
    insert_summary = defaultdict(list)
    for entity in msp:
        if entity.dxftype() == "INSERT":
            pos = entity.dxf.insert
            insert_summary[entity.dxf.name].append((entity.dxf.layer, pos.x, pos.y))
    for bname, instances in sorted(insert_summary.items()):
        print(f"\n  Block '{bname}' ({len(instances)} insertions):")
        for layer, x, y in instances:
            print(f"    Layer='{layer}' at ({x:.4f}, {y:.4f})")

    print("\n" + "=" * 80)
    print("INSPECTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
