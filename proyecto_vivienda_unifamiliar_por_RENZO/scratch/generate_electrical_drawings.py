import os
import json
import shutil
import math
import sys

try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment
except ImportError:
    print("ezdxf is required. Please install it using pip.")
    sys.exit(1)

base_dir = r"C:\Users\renzo\instalacion-electricas\proyecto_vivienda_unifamiliar_por_RENZO"
layouts_dir = os.path.join(base_dir, "layouts")
planos_cad_dir = os.path.join(base_dir, "planos_cad")
planos_electricos_dir = os.path.join(base_dir, "planos_electricos")
diagramas_dir = os.path.join(base_dir, "diagramas")
planos_report_dir = os.path.join(base_dir, "planos")

os.makedirs(planos_electricos_dir, exist_ok=True)
os.makedirs(diagramas_dir, exist_ok=True)
os.makedirs(planos_report_dir, exist_ok=True)

# Helper to render PDF/SVG using Matplotlib
def render_dxf_to_pdf_and_svg(dxf_path):
    pdf_path = dxf_path.replace('.dxf', '.pdf')
    svg_path = dxf_path.replace('.dxf', '.svg')
    try:
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        
        print(f"Renderizando PDF/SVG para: {dxf_path} ...")
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        
        # Save PDF
        fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        
        ctx = RenderContext(doc)
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(msp, finalize=True)
        
        fig.savefig(pdf_path, dpi=300, bbox_inches='tight', pad_inches=0)
        # Save SVG
        fig.savefig(svg_path, format='svg', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        print(f"SUCCESS: Renderizado PDF y SVG completado para {dxf_path}")
    except Exception as e:
        print(f"Advertencia: No se pudo renderizar {dxf_path} a PDF/SVG: {e}")

# Helper to draw a standard architectural layout on modelspace from layout data
def draw_base_architecture(msp, data):
    wall_thickness = 0.15
    walls = set()
    
    # 1. Collect walls
    for room in data["rooms"]:
        rx, ry = room["x"], room["y"]
        rw, rh = room["width"], room["height"]
        
        seg_bottom = tuple(sorted([(rx, ry), (rx + rw, ry)]))
        seg_top = tuple(sorted([(rx, ry + rh), (rx + rw, ry + rh)]))
        seg_left = tuple(sorted([(rx, ry), (rx, ry + rh)]))
        seg_right = tuple(sorted([(rx + rw, ry), (rx + rw, ry + rh)]))
        
        walls.add(seg_bottom)
        walls.add(seg_top)
        walls.add(seg_left)
        walls.add(seg_right)
        
        # Room label
        x_center = rx + rw / 2
        y_center = ry + rh / 2
        
        if "escalera" in room["name"].lower():
            # Draw standard stair steps
            landing_depth = 1.2
            msp.add_line((x_center, ry), (x_center, ry + rh - landing_depth), dxfattribs={'layer': 'ESCALERAS', 'color': 8})
            msp.add_line((rx, ry + rh - landing_depth), (rx + rw, ry + rh - landing_depth), dxfattribs={'layer': 'ESCALERAS', 'color': 8})
            num_steps = 8
            tread_depth = (rh - landing_depth) / num_steps
            for i in range(1, num_steps):
                y_step = ry + i * tread_depth
                msp.add_line((rx, y_step), (x_center, y_step), dxfattribs={'layer': 'ESCALERAS', 'color': 8})
                msp.add_line((x_center, y_step), (rx + rw, y_step), dxfattribs={'layer': 'ESCALERAS', 'color': 8})
            text_y = ry + rh - (landing_depth / 2)
            dim_y = text_y - 0.25
        else:
            text_y = y_center
            dim_y = y_center - 0.25
            
        if room["name"] and not room["name"].startswith("_"):
            msp.add_text(room["name"].upper(), dxfattribs={'layer': 'TEXTOS', 'height': 0.18, 'color': 8}).set_placement((x_center, text_y), align=TextEntityAlignment.MIDDLE_CENTER)
            dim_text = f"{rw:.2f} x {rh:.2f} m"
            msp.add_text(dim_text, dxfattribs={'layer': 'TEXTOS', 'height': 0.12, 'color': 8}).set_placement((x_center, dim_y), align=TextEntityAlignment.MIDDLE_CENTER)

    # Ignored walls (removes lines where spaces merge)
    ignored_walls = set()
    if "ignored_walls" in data:
        for p in data["ignored_walls"]:
            p1, p2 = p
            seg = tuple(sorted([tuple(p1), tuple(p2)]))
            ignored_walls.add(seg)
            
    walls = walls - ignored_walls
    
    # Draw walls in light gray or white/black layer
    for start, end in walls:
        x1, y1 = start
        x2, y2 = end
        if abs(x1 - x2) < 1e-5:  # vertical
            msp.add_line((x1 - wall_thickness/2, y1), (x1 - wall_thickness/2, y2), dxfattribs={'layer': 'MUROS', 'color': 8})
            msp.add_line((x1 + wall_thickness/2, y1), (x1 + wall_thickness/2, y2), dxfattribs={'layer': 'MUROS', 'color': 8})
        elif abs(y1 - y2) < 1e-5:  # horizontal
            msp.add_line((x1, y1 - wall_thickness/2), (x2, y1 - wall_thickness/2), dxfattribs={'layer': 'MUROS', 'color': 8})
            msp.add_line((x1, y1 + wall_thickness/2), (x2, y1 + wall_thickness/2), dxfattribs={'layer': 'MUROS', 'color': 8})
        else:
            msp.add_line(start, end, dxfattribs={'layer': 'MUROS', 'color': 8})
            
    # 2. Draw doors (yellow / color 2)
    if "doors" in data:
        for door in data["doors"]:
            x, y = door["x"], door["y"]
            w = door["width"]
            ori = door["orientation"]
            swing = door["swing"]
            layer = "PUERTAS"
            
            if ori == "horizontal":
                if swing == "top-right":
                    msp.add_line((x, y), (x, y + w), dxfattribs={'layer': layer, 'color': 2})
                    msp.add_arc((x, y), w, 0, 90, dxfattribs={'layer': layer, 'color': 2})
                elif swing == "top-left":
                    msp.add_line((x + w, y), (x + w, y + w), dxfattribs={'layer': layer, 'color': 2})
                    msp.add_arc((x + w, y), w, 90, 180, dxfattribs={'layer': layer, 'color': 2})
                elif swing == "bottom-right":
                    msp.add_line((x, y), (x, y - w), dxfattribs={'layer': layer, 'color': 2})
                    msp.add_arc((x, y), w, 270, 360, dxfattribs={'layer': layer, 'color': 2})
                elif swing == "bottom-left":
                    msp.add_line((x + w, y), (x + w, y - w), dxfattribs={'layer': layer, 'color': 2})
                    msp.add_arc((x + w, y), w, 180, 270, dxfattribs={'layer': layer, 'color': 2})
            else:  # vertical
                if swing == "top-right":
                    msp.add_line((x, y), (x + w, y), dxfattribs={'layer': layer, 'color': 2})
                    msp.add_arc((x, y), w, 0, 90, dxfattribs={'layer': layer, 'color': 2})
                elif swing == "top-left":
                    msp.add_line((x, y), (x - w, y), dxfattribs={'layer': layer, 'color': 2})
                    msp.add_arc((x, y), w, 90, 180, dxfattribs={'layer': layer, 'color': 2})
                elif swing == "bottom-right":
                    msp.add_line((x, y + w), (x + w, y + w), dxfattribs={'layer': layer, 'color': 2})
                    msp.add_arc((x, y + w), w, 270, 360, dxfattribs={'layer': layer, 'color': 2})
                elif swing == "bottom-left":
                    msp.add_line((x, y + w), (x - w, y + w), dxfattribs={'layer': layer, 'color': 2})
                    msp.add_arc((x, y + w), w, 180, 270, dxfattribs={'layer': layer, 'color': 2})

    # 3. Draw windows (cyan / color 4)
    if "windows" in data:
        for win in data["windows"]:
            x, y = win["x"], win["y"]
            w = win["width"]
            ori = win["orientation"]
            layer = "VENTANAS"
            thick = 0.15
            if ori == "horizontal":
                msp.add_line((x, y - thick/2), (x + w, y - thick/2), dxfattribs={'layer': layer, 'color': 4})
                msp.add_line((x + w, y - thick/2), (x + w, y + thick/2), dxfattribs={'layer': layer, 'color': 4})
                msp.add_line((x + w, y + thick/2), (x, y + thick/2), dxfattribs={'layer': layer, 'color': 4})
                msp.add_line((x, y + thick/2), (x, y - thick/2), dxfattribs={'layer': layer, 'color': 4})
                msp.add_line((x, y), (x + w, y), dxfattribs={'layer': layer, 'color': 4})
            else:
                msp.add_line((x - thick/2, y), (x + thick/2, y), dxfattribs={'layer': layer, 'color': 4})
                msp.add_line((x + thick/2, y), (x + thick/2, y + w), dxfattribs={'layer': layer, 'color': 4})
                msp.add_line((x + thick/2, y + w), (x - thick/2, y + w), dxfattribs={'layer': layer, 'color': 4})
                msp.add_line((x - thick/2, y + w), (x - thick/2, y), dxfattribs={'layer': layer, 'color': 4})
                msp.add_line((x, y), (x, y + w), dxfattribs={'layer': layer, 'color': 4})

    # 4. Marco and Cajetín
    limit_w = data["dimensions"]["width"]
    limit_h = data["dimensions"]["height"]
    margin = data.get("dimensions", {}).get("margin", 1.5)
    
    mx1, my1 = -margin, -margin
    mx2, my2 = limit_w + margin, limit_h + margin
    
    # Outer frame
    msp.add_line((mx1, my1), (mx2, my1), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2, my1), (mx2, my2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2, my2), (mx1, my2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx1, my2), (mx1, my1), dxfattribs={'layer': 'MARCO', 'color': 7})
    
    # Inner decorative frame
    o = 0.08
    msp.add_line((mx1+o, my1+o), (mx2-o, my1+o), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2-o, my1+o), (mx2-o, my2-o), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2-o, my2-o), (mx1+o, my2-o), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx1+o, my2-o), (mx1+o, my1+o), dxfattribs={'layer': 'MARCO', 'color': 7})
    
    # Title Block
    c_w = 4.8
    c_h = 1.6
    cx1 = mx2 - o - c_w
    cy1 = my1 + o
    cx2 = mx2 - o
    cy2 = my1 + o + c_h
    
    msp.add_line((cx1, cy1), (cx1, cy2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy2), (cx2, cy2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy1 + 0.4), (cx2, cy1 + 0.4), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy1 + 0.8), (cx2, cy1 + 0.8), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy1 + 1.2), (cx2, cy1 + 1.2), dxfattribs={'layer': 'MARCO', 'color': 7})
    
    author = data.get("author", " Mamani Galindo Renzo Gabriel")
    project_name = data.get("project", "INSTALACIONES ELECTRICAS")
    date_str = data.get("date", "2026-06-03")
    
    msp.add_text("UNAP - ESCUELA INGENIERIA MECANICA ELECTRICA", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 1.35))
    msp.add_text(f"PROY: {project_name.upper()}", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 0.95))
    msp.add_text(f"ALUM: {author.upper()}", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 0.55))
    msp.add_text(f"FECHA: {date_str}  |  ESC: 1:50", dxfattribs={'layer': 'TEXTOS', 'height': 0.09, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 0.15))

# Helper to draw a circle center symbol
def draw_electric_center(msp, x, y, symbol_text="X", layer="ELEC", color=3, radius=0.15):
    # Draw circle
    msp.add_circle((x, y), radius, dxfattribs={'layer': layer, 'color': color})
    # Draw text inside
    msp.add_text(symbol_text, dxfattribs={'layer': layer, 'height': radius * 1.2, 'color': color}).set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)

def draw_switch(msp, x, y, label="S", layer="ELEC", color=3, radius=0.08):
    msp.add_circle((x, y), radius, dxfattribs={'layer': layer, 'color': color})
    # Lollipop line
    msp.add_line((x, y + radius), (x, y + radius + 0.12), dxfattribs={'layer': layer, 'color': color})
    msp.add_line((x, y + radius + 0.12), (x + 0.10, y + radius + 0.12), dxfattribs={'layer': layer, 'color': color})
    msp.add_text(label, dxfattribs={'layer': layer, 'height': 0.10, 'color': color}).set_placement((x + 0.15, y + radius + 0.10))

def draw_conduit(msp, p1, p2, layer="ELEC_CONDUIT", color=3):
    # Curve conduit represented by an arc or direct line for simplicity, or 3-point spline
    # Direct line in dashed pattern is standard in simple CAD overlays
    msp.add_line(p1, p2, dxfattribs={'layer': layer, 'color': color, 'linetype': 'DASHED'})

# ====================================================
# FLOOR 1: ALUMBRADO (IE-02-alumbrado)
# ====================================================
def build_floor1_electrical():
    layout_path = os.path.join(layouts_dir, "primer_piso_v3.json")
    with open(layout_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data["project"] = "Plano Alumbrado - Primer Piso (IE-02)"
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    
    # Layers
    doc.layers.new("MUROS", dxfattribs={'color': 8})
    doc.layers.new("PUERTAS", dxfattribs={'color': 8})
    doc.layers.new("VENTANAS", dxfattribs={'color': 8})
    doc.layers.new("TEXTOS", dxfattribs={'color': 8})
    doc.layers.new("MARCO", dxfattribs={'color': 7})
    doc.layers.new("ESCALERAS", dxfattribs={'color': 8})
    doc.layers.new("COTAS", dxfattribs={'color': 8})
    doc.layers.new("ELEC_ALUMBRADO", dxfattribs={'color': 3}) # Green for alumbrado
    doc.layers.new("ELEC_CONDUIT", dxfattribs={'color': 3})
    
    # Base layout
    draw_base_architecture(msp, data)
    
    # Add Tablero General TG-01 on the right wall of pasadizo
    tg_x, tg_y = 4.3, 1.2
    msp.add_lwpolyline([(tg_x - 0.1, tg_y - 0.2), (tg_x + 0.1, tg_y - 0.2), (tg_x + 0.1, tg_y + 0.2), (tg_x - 0.1, tg_y + 0.2)], close=True, dxfattribs={'layer': 'ELEC_ALUMBRADO', 'color': 1}) # Red TG-01
    msp.add_text("TG-01", dxfattribs={'layer': 'ELEC_ALUMBRADO', 'height': 0.11, 'color': 1}).set_placement((tg_x - 0.4, tg_y - 0.05))
    
    # Lights (Centro de Luz)
    lights = {
        "Tienda": (1.5, 1.75),
        "Cocina": (1.5, 5.25),
        "Pasadizo_1": (3.75, 2.0),
        "Pasadizo_2": (3.75, 5.0),
        "Escalera": (1.25, 7.75)
    }
    
    for l_name, (lx, ly) in lights.items():
        draw_electric_center(msp, lx, ly, symbol_text="L", layer="ELEC_ALUMBRADO", color=3, radius=0.14)
        
    # Switches
    switches = {
        "S_Tienda": ((2.8, 2.3), "S"),
        "S_Cocina": ((2.8, 5.8), "S"),
        "S3_Pasa1": ((3.2, 0.5), "S3"),
        "S3_Pasa2": ((3.2, 6.5), "S3"),
        "S3_Escalera": ((2.2, 7.2), "S3")
    }
    
    for sw_name, (pos, lbl) in switches.items():
        draw_switch(msp, pos[0], pos[1], label=lbl, layer="ELEC_ALUMBRADO", color=3)
        
    # Conduits
    # Connect TG-01 to Pasadizo_1 light
    draw_conduit(msp, (tg_x, tg_y), lights["Pasadizo_1"], color=3)
    # Connect Pasadizo_1 to Tienda light
    draw_conduit(msp, lights["Pasadizo_1"], lights["Tienda"], color=3)
    # Connect Tienda light to S_Tienda switch
    draw_conduit(msp, lights["Tienda"], (2.8, 2.3), color=3)
    # Connect Pasadizo_1 light to Pasadizo_2 light
    draw_conduit(msp, lights["Pasadizo_1"], lights["Pasadizo_2"], color=3)
    # Connect Pasadizo_2 light to Cocina light
    draw_conduit(msp, lights["Pasadizo_2"], lights["Cocina"], color=3)
    # Connect Cocina light to S_Cocina switch
    draw_conduit(msp, lights["Cocina"], (2.8, 5.8), color=3)
    # Connect Pasadizo_2 light to Escalera light
    draw_conduit(msp, lights["Pasadizo_2"], lights["Escalera"], color=3)
    # Connect Escalera light to S3_Escalera switch
    draw_conduit(msp, lights["Escalera"], (2.2, 7.2), color=3)
    # Connect Pasadizo_1 light to S3_Pasa1 switch
    draw_conduit(msp, lights["Pasadizo_1"], (3.2, 0.5), color=3)
    # Connect Pasadizo_2 light to S3_Pasa2 switch
    draw_conduit(msp, lights["Pasadizo_2"], (3.2, 6.5), color=3)
    
    # Legend panel on the left/bottom margins to make it look highly professional
    leg_x, leg_y = -1.2, 0.5
    msp.add_text("LEYENDA ALUMBRADO", dxfattribs={'layer': 'ELEC_ALUMBRADO', 'height': 0.12, 'color': 7}).set_placement((leg_x, leg_y + 1.2))
    
    # Light symbol in legend
    draw_electric_center(msp, leg_x + 0.2, leg_y + 0.8, symbol_text="L", layer="ELEC_ALUMBRADO", color=3, radius=0.10)
    msp.add_text("Pto. Luz LED (12W)", dxfattribs={'layer': 'ELEC_ALUMBRADO', 'height': 0.10, 'color': 7}).set_placement((leg_x + 0.5, leg_y + 0.75))
    
    # Switch simple
    draw_switch(msp, leg_x + 0.2, leg_y + 0.5, label="S", layer="ELEC_ALUMBRADO", color=3, radius=0.06)
    msp.add_text("Interruptor Simple", dxfattribs={'layer': 'ELEC_ALUMBRADO', 'height': 0.10, 'color': 7}).set_placement((leg_x + 0.5, leg_y + 0.45))
    
    # Switch conmutado
    draw_switch(msp, leg_x + 0.2, leg_y + 0.2, label="S3", layer="ELEC_ALUMBRADO", color=3, radius=0.06)
    msp.add_text("Interruptor 3-Vias (Conmutación)", dxfattribs={'layer': 'ELEC_ALUMBRADO', 'height': 0.10, 'color': 7}).set_placement((leg_x + 0.5, leg_y + 0.15))
    
    # Conduit line
    msp.add_line((leg_x + 0.1, leg_y - 0.1), (leg_x + 0.3, leg_y - 0.1), dxfattribs={'layer': 'ELEC_ALUMBRADO', 'color': 3, 'linetype': 'DASHED'})
    msp.add_text("Canalización Techo (PVC 3/4\")", dxfattribs={'layer': 'ELEC_ALUMBRADO', 'height': 0.10, 'color': 7}).set_placement((leg_x + 0.5, leg_y - 0.15))

    out_dxf = os.path.join(planos_electricos_dir, "plano_electrico_primer_piso.dxf")
    doc.saveas(out_dxf)
    render_dxf_to_pdf_and_svg(out_dxf)
    
    # Copy to report directory
    shutil.copy2(out_dxf.replace('.dxf', '.pdf'), os.path.join(planos_report_dir, "IE-02-alumbrado.pdf"))
    print("Primer Piso Electrical Alumbrado compiled.")

# ====================================================
# FLOOR 2: TOMACORRIENTES (IE-03-tomacorrientes)
# ====================================================
def build_floor2_electrical():
    layout_path = os.path.join(layouts_dir, "segundo_piso_v3.json")
    with open(layout_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    data["project"] = "Plano Tomacorrientes - Segundo Piso (IE-03)"
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    
    # Layers
    doc.layers.new("MUROS", dxfattribs={'color': 8})
    doc.layers.new("PUERTAS", dxfattribs={'color': 8})
    doc.layers.new("VENTANAS", dxfattribs={'color': 8})
    doc.layers.new("TEXTOS", dxfattribs={'color': 8})
    doc.layers.new("MARCO", dxfattribs={'color': 7})
    doc.layers.new("ESCALERAS", dxfattribs={'color': 8})
    doc.layers.new("COTAS", dxfattribs={'color': 8})
    doc.layers.new("ELEC_TOMACORRIENTES", dxfattribs={'color': 6}) # Magenta for tomacorrientes
    doc.layers.new("ELEC_CONDUIT", dxfattribs={'color': 6})
    
    draw_base_architecture(msp, data)
    
    # Add Tablero de Distribución TD-01 on the right wall of Hall
    td_x, td_y = 4.3, 4.5
    msp.add_lwpolyline([(td_x - 0.1, td_y - 0.2), (td_x + 0.1, td_y - 0.2), (td_x + 0.1, td_y + 0.2), (td_x - 0.1, td_y + 0.2)], close=True, dxfattribs={'layer': 'ELEC_TOMACORRIENTES', 'color': 1}) # Red TD-01
    msp.add_text("TD-01", dxfattribs={'layer': 'ELEC_TOMACORRIENTES', 'height': 0.11, 'color': 1}).set_placement((td_x - 0.4, td_y - 0.05))
    
    # Draw double tomacorrientes (circles with "TC" text inside)
    tcs = {
        "Dorm_Prin_1": (0.3, 1.0),
        "Dorm_Prin_2": (2.25, 0.3),
        "Dorm_Prin_3": (4.2, 2.0),
        "Dorm_3_1": (0.3, 5.5),
        "Dorm_3_2": (2.7, 6.0),
        "Sala_1": (4.2, 5.5),
        "Sala_2": (3.2, 4.2),
        "Bano_GFCI": (4.2, 8.2) # GFCI near basin
    }
    
    for tc_name, (tx, ty) in tcs.items():
        is_gfci = "GFCI" in tc_name
        lbl = "GFCI" if is_gfci else "TC"
        col = 1 if is_gfci else 6
        draw_electric_center(msp, tx, ty, symbol_text=lbl, layer="ELEC_TOMACORRIENTES", color=col, radius=0.13)
        
    # Conduits connecting tomacorrientes in a floor loop back to TD-01
    # Connect TD-01 to Sala_2, then to Dorm_Prin_3, Dorm_Prin_2, Dorm_Prin_1, Dorm_3_1, Dorm_3_2, Sala_1, and back to TD-01
    draw_conduit(msp, (td_x, td_y), tcs["Sala_2"], color=6)
    draw_conduit(msp, tcs["Sala_2"], tcs["Dorm_Prin_3"], color=6)
    draw_conduit(msp, tcs["Dorm_Prin_3"], tcs["Dorm_Prin_2"], color=6)
    draw_conduit(msp, tcs["Dorm_Prin_2"], tcs["Dorm_Prin_1"], color=6)
    draw_conduit(msp, tcs["Dorm_Prin_1"], tcs["Dorm_3_1"], color=6)
    draw_conduit(msp, tcs["Dorm_3_1"], tcs["Dorm_3_2"], color=6)
    draw_conduit(msp, tcs["Dorm_3_2"], tcs["Sala_1"], color=6)
    draw_conduit(msp, tcs["Sala_1"], (td_x, td_y), color=6)
    # Baño GFCI separately to TD-01
    draw_conduit(msp, tcs["Bano_GFCI"], (td_x, td_y), color=6)
    
    # Legend
    leg_x, leg_y = -1.2, 0.5
    msp.add_text("LEYENDA TOMACORRIENTES", dxfattribs={'layer': 'ELEC_TOMACORRIENTES', 'height': 0.12, 'color': 7}).set_placement((leg_x, leg_y + 1.2))
    
    # TC simple
    draw_electric_center(msp, leg_x + 0.2, leg_y + 0.8, symbol_text="TC", layer="ELEC_TOMACORRIENTES", color=6, radius=0.09)
    msp.add_text("T/C Doble General (Piso, H=0.30)", dxfattribs={'layer': 'ELEC_TOMACORRIENTES', 'height': 0.10, 'color': 7}).set_placement((leg_x + 0.5, leg_y + 0.75))
    
    # GFCI
    draw_electric_center(msp, leg_x + 0.2, leg_y + 0.5, symbol_text="GFCI", layer="ELEC_TOMACORRIENTES", color=1, radius=0.09)
    msp.add_text("T/C Protegido GFCI (Baño, H=1.10)", dxfattribs={'layer': 'ELEC_TOMACORRIENTES', 'height': 0.10, 'color': 7}).set_placement((leg_x + 0.5, leg_y + 0.45))
    
    # TD
    msp.add_lwpolyline([(leg_x + 0.1, leg_y + 0.1), (leg_x + 0.3, leg_y + 0.1), (leg_x + 0.3, leg_y + 0.3), (leg_x + 0.1, leg_y + 0.3)], close=True, dxfattribs={'layer': 'ELEC_TOMACORRIENTES', 'color': 1})
    msp.add_text("Tablero de Distribución", dxfattribs={'layer': 'ELEC_TOMACORRIENTES', 'height': 0.10, 'color': 7}).set_placement((leg_x + 0.5, leg_y + 0.15))
    
    # Conduit line
    msp.add_line((leg_x + 0.1, leg_y - 0.15), (leg_x + 0.3, leg_y - 0.15), dxfattribs={'layer': 'ELEC_TOMACORRIENTES', 'color': 6, 'linetype': 'DASHED'})
    msp.add_text("Canalización Piso (PVC 3/4\")", dxfattribs={'layer': 'ELEC_TOMACORRIENTES', 'height': 0.10, 'color': 7}).set_placement((leg_x + 0.5, leg_y - 0.20))

    out_dxf = os.path.join(planos_electricos_dir, "plano_electrico_segundo_piso.dxf")
    doc.saveas(out_dxf)
    render_dxf_to_pdf_and_svg(out_dxf)
    
    # Copy to report directory
    shutil.copy2(out_dxf.replace('.dxf', '.pdf'), os.path.join(planos_report_dir, "IE-03-tomacorrientes.pdf"))
    print("Segundo Piso Electrical Tomacorrientes compiled.")

# ====================================================
# FLOOR 3: CARGAS & CANALIZACIONES (IE-04-circuitos-canalizaciones)
# ====================================================
def build_floor3_electrical():
    layout_path = os.path.join(layouts_dir, "tercer_piso_v3.json")
    with open(layout_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    data["project"] = "Plano Cargas/Canalizaciones - Tercer Piso (IE-04)"
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    
    # Layers
    doc.layers.new("MUROS", dxfattribs={'color': 8})
    doc.layers.new("PUERTAS", dxfattribs={'color': 8})
    doc.layers.new("VENTANAS", dxfattribs={'color': 8})
    doc.layers.new("TEXTOS", dxfattribs={'color': 8})
    doc.layers.new("MARCO", dxfattribs={'color': 7})
    doc.layers.new("ESCALERAS", dxfattribs={'color': 8})
    doc.layers.new("COTAS", dxfattribs={'color': 8})
    doc.layers.new("ELEC_CARGAS", dxfattribs={'color': 5}) # Blue for charges & conduits
    doc.layers.new("ELEC_CONDUIT", dxfattribs={'color': 5})
    
    draw_base_architecture(msp, data)
    
    # Add Tablero de Distribución TD-02 on the left wall of Pasadizo
    td_x, td_y = 0.2, 8.0
    msp.add_lwpolyline([(td_x - 0.1, td_y - 0.2), (td_x + 0.1, td_y - 0.2), (td_x + 0.1, td_y + 0.2), (td_x - 0.1, td_y + 0.2)], close=True, dxfattribs={'layer': 'ELEC_CARGAS', 'color': 1}) # Red TD-02
    msp.add_text("TD-02", dxfattribs={'layer': 'ELEC_CARGAS', 'height': 0.11, 'color': 1}).set_placement((td_x + 0.2, td_y - 0.05))
    
    # Outlets and special loads
    tcs = {
        "Dorm_4_1": (0.3, 3.5),
        "Dorm_4_2": (2.0, 5.0),
        "Dorm_5_1": (2.5, 3.5),
        "Dorm_5_2": (4.2, 5.0),
        "Bano_GFCI": (4.2, 8.2),
        "Lavand_TC": (3.37, 8.0), # Washer outlet
        "BOMBA": (1.0, 8.2) # Special pump load
    }
    
    for name, (tx, ty) in tcs.items():
        if name == "BOMBA":
            # Draw special load (square B)
            msp.add_lwpolyline([(tx - 0.15, ty - 0.15), (tx + 0.15, ty - 0.15), (tx + 0.15, ty + 0.15), (tx - 0.15, ty + 0.15)], close=True, dxfattribs={'layer': 'ELEC_CARGAS', 'color': 1})
            msp.add_text("B", dxfattribs={'layer': 'ELEC_CARGAS', 'height': 0.16, 'color': 1}).set_placement((tx, ty), align=TextEntityAlignment.MIDDLE_CENTER)
            msp.add_text("BOMBA DE AGUA", dxfattribs={'layer': 'ELEC_CARGAS', 'height': 0.08, 'color': 7}).set_placement((tx - 0.4, ty - 0.3))
        else:
            is_gfci = "GFCI" in name
            lbl = "GFCI" if is_gfci else "TC"
            col = 1 if is_gfci else 5
            draw_electric_center(msp, tx, ty, symbol_text=lbl, layer="ELEC_CARGAS", color=col, radius=0.13)
            
    # Conduits
    draw_conduit(msp, (td_x, td_y), tcs["BOMBA"], color=5)
    draw_conduit(msp, (td_x, td_y), tcs["Dorm_4_2"], color=5)
    draw_conduit(msp, tcs["Dorm_4_2"], tcs["Dorm_4_1"], color=5)
    draw_conduit(msp, (td_x, td_y), tcs["Dorm_5_2"], color=5)
    draw_conduit(msp, tcs["Dorm_5_2"], tcs["Dorm_5_1"], color=5)
    draw_conduit(msp, (td_x, td_y), tcs["Lavand_TC"], color=5)
    draw_conduit(msp, tcs["Lavand_TC"], tcs["Bano_GFCI"], color=5)
    
    # Legend
    leg_x, leg_y = -1.2, 0.5
    msp.add_text("LEYENDA CARGAS / SERVICIOS", dxfattribs={'layer': 'ELEC_CARGAS', 'height': 0.11, 'color': 7}).set_placement((leg_x, leg_y + 1.2))
    
    # TC
    draw_electric_center(msp, leg_x + 0.2, leg_y + 0.8, symbol_text="TC", layer="ELEC_CARGAS", color=5, radius=0.09)
    msp.add_text("T/C Doble General", dxfattribs={'layer': 'ELEC_CARGAS', 'height': 0.10, 'color': 7}).set_placement((leg_x + 0.5, leg_y + 0.75))
    
    # Special load
    msp.add_lwpolyline([(leg_x + 0.1, leg_y + 0.4), (leg_x + 0.3, leg_y + 0.4), (leg_x + 0.3, leg_y + 0.6), (leg_x + 0.1, leg_y + 0.6)], close=True, dxfattribs={'layer': 'ELEC_CARGAS', 'color': 1})
    msp.add_text("B", dxfattribs={'layer': 'ELEC_CARGAS', 'height': 0.10, 'color': 1}).set_placement((leg_x + 0.2, leg_y + 0.5), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("Carga Especial Bomba (0.75kW)", dxfattribs={'layer': 'ELEC_CARGAS', 'height': 0.10, 'color': 7}).set_placement((leg_x + 0.5, leg_y + 0.45))
    
    # Conduit line
    msp.add_line((leg_x + 0.1, leg_y + 0.25), (leg_x + 0.3, leg_y + 0.25), dxfattribs={'layer': 'ELEC_CARGAS', 'color': 5, 'linetype': 'DASHED'})
    msp.add_text("Canalización Piso/Techo (PVC 3/4\")", dxfattribs={'layer': 'ELEC_CARGAS', 'height': 0.10, 'color': 7}).set_placement((leg_x + 0.5, leg_y + 0.20))

    out_dxf = os.path.join(planos_electricos_dir, "plano_electrico_tercer_piso.dxf")
    doc.saveas(out_dxf)
    render_dxf_to_pdf_and_svg(out_dxf)
    
    # Copy to report directory
    shutil.copy2(out_dxf.replace('.dxf', '.pdf'), os.path.join(planos_report_dir, "IE-04-circuitos-canalizaciones.pdf"))
    print("Tercer Piso Electrical Canalizaciones/Cargas compiled.")

# ====================================================
# DIAGRAMA UNIFILAR (IE-05-unifilar-cuadro-cargas)
# ====================================================
def build_diagrama_unifilar():
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    
    # Set up some layers
    doc.layers.new("DIAGRAMA", dxfattribs={'color': 7})
    doc.layers.new("TEXTOS", dxfattribs={'color': 7})
    doc.layers.new("TABLAS", dxfattribs={'color': 8})
    doc.layers.new("MARCO", dxfattribs={'color': 7})
    
    # Frame and title block
    # Frame width 14, height 9
    mx1, my1 = -1.5, -1.5
    mx2, my2 = 14.5, 9.5
    
    msp.add_line((mx1, my1), (mx2, my1), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2, my1), (mx2, my2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2, my2), (mx1, my2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx1, my2), (mx1, my1), dxfattribs={'layer': 'MARCO', 'color': 7})
    
    o = 0.08
    msp.add_line((mx1+o, my1+o), (mx2-o, my1+o), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2-o, my1+o), (mx2-o, my2-o), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2-o, my2-o), (mx1+o, my2-o), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx1+o, my2-o), (mx1+o, my1+o), dxfattribs={'layer': 'MARCO', 'color': 7})
    
    c_w, c_h = 4.8, 1.6
    cx1, cy1 = mx2 - o - c_w, my1 + o
    cx2, cy2 = mx2 - o, my1 + o + c_h
    msp.add_line((cx1, cy1), (cx1, cy2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy2), (cx2, cy2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy1 + 0.4), (cx2, cy1 + 0.4), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy1 + 0.8), (cx2, cy1 + 0.8), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy1 + 1.2), (cx2, cy1 + 1.2), dxfattribs={'layer': 'MARCO', 'color': 7})
    
    msp.add_text("UNAP - ESCUELA INGENIERIA MECANICA ELECTRICA", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 1.35))
    msp.add_text("PROY: DIAGRAMA UNIFILAR Y CARGAS (IE-05)", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 0.95))
    msp.add_text("ALUM: MAMANI GALINDO RENZO GABRIEL", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 0.55))
    msp.add_text("FECHA: 2026-06-03  |  ESC: S/E (MTS)", dxfattribs={'layer': 'TEXTOS', 'height': 0.09, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 0.15))
    
    # 1. Title
    msp.add_text("DIAGRAMA UNIFILAR GENERAL - TG-01", dxfattribs={'layer': 'TEXTOS', 'height': 0.28, 'color': 7}).set_placement((0.0, 8.5))
    
    # 2. Draw single line tree
    # Draw incoming line
    msp.add_line((1.0, 7.5), (1.0, 7.0), dxfattribs={'layer': 'DIAGRAMA', 'color': 7})
    msp.add_text("Suministro Monofásico 220V, 60Hz (Desde Red)", dxfattribs={'layer': 'TEXTOS', 'height': 0.12, 'color': 7}).set_placement((1.2, 7.3))
    
    # KWH Meter
    msp.add_circle((1.0, 6.7), 0.3, dxfattribs={'layer': 'DIAGRAMA', 'color': 7})
    msp.add_text("kWh", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((1.0, 6.7), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Connect meter to main breaker
    msp.add_line((1.0, 6.4), (1.0, 5.8), dxfattribs={'layer': 'DIAGRAMA', 'color': 7})
    
    # Main Breaker Symbol (box/termomagnetic)
    msp.add_lwpolyline([(0.85, 5.4), (1.15, 5.4), (1.15, 5.8), (0.85, 5.8)], close=True, dxfattribs={'layer': 'DIAGRAMA', 'color': 7})
    msp.add_text("ITM General", dxfattribs={'layer': 'TEXTOS', 'height': 0.10, 'color': 7}).set_placement((1.3, 5.65))
    msp.add_text("2P, 40A, 10kA", dxfattribs={'layer': 'TEXTOS', 'height': 0.10, 'color': 7}).set_placement((1.3, 5.5))
    
    # Connect Main Breaker to Differential Breaker
    msp.add_line((1.0, 5.4), (1.0, 4.8), dxfattribs={'layer': 'DIAGRAMA', 'color': 7})
    
    # Differential Breaker Symbol (box with oval/circle or labeled ID)
    msp.add_lwpolyline([(0.85, 4.4), (1.15, 4.4), (1.15, 4.8), (0.85, 4.8)], close=True, dxfattribs={'layer': 'DIAGRAMA', 'color': 7})
    msp.add_text("ID General", dxfattribs={'layer': 'TEXTOS', 'height': 0.10, 'color': 7}).set_placement((1.3, 4.65))
    msp.add_text("2P, 40A, 30mA", dxfattribs={'layer': 'TEXTOS', 'height': 0.10, 'color': 7}).set_placement((1.3, 4.50))
    
    # Connect to TG Busbar (horizontal thick line)
    msp.add_line((1.0, 4.4), (1.0, 3.8), dxfattribs={'layer': 'DIAGRAMA', 'color': 7})
    msp.add_line((0.5, 3.8), (11.0, 3.8), dxfattribs={'layer': 'DIAGRAMA', 'color': 7, 'lineweight': 50})
    msp.add_text("BARRA DE COBRE TABLERO GENERAL TG-01", dxfattribs={'layer': 'TEXTOS', 'height': 0.12, 'color': 7}).set_placement((0.5, 4.0))
    
    # Branch feeders: C1 to C5
    # Let's draw 5 vertical lines branching down at X = 1, 3, 5, 7, 9
    ctos = [
        {"x": 1.5, "lbl": "C1", "name": "Alumbrado", "itm": "2P, 10A", "cond": "3x1.5mm2", "desc": "Luz LED (132 W)"},
        {"x": 3.8, "lbl": "C2", "name": "Tomacorrientes Gral.", "itm": "2P, 16A", "cond": "3x2.5mm2", "desc": "TCs Sala/Dorm (2520 W)"},
        {"x": 6.1, "lbl": "C3", "name": "Cocina Especial", "itm": "2P, 20A", "cond": "3x2.5mm2", "desc": "Micro/Refri (1200 W)"},
        {"x": 8.4, "lbl": "C4", "name": "Lavandería", "itm": "2P, 16A", "cond": "3x2.5mm2", "desc": "Lavadora (360 W)"},
        {"x": 10.7, "lbl": "C5", "name": "Bomba de Agua", "itm": "2P, 16A", "cond": "3x2.5mm2", "desc": "Motor 1HP (750 W)"}
    ]
    
    for c in ctos:
        cx = c["x"]
        # Vertical branch line from busbar
        msp.add_line((cx, 3.8), (cx, 3.2), dxfattribs={'layer': 'DIAGRAMA', 'color': 7})
        
        # Individual branch breaker
        msp.add_lwpolyline([(cx - 0.15, 2.8), (cx + 0.15, 2.8), (cx + 0.15, 3.2), (cx - 0.15, 3.2)], close=True, dxfattribs={'layer': 'DIAGRAMA', 'color': 7})
        msp.add_text(c["itm"], dxfattribs={'layer': 'TEXTOS', 'height': 0.09, 'color': 7}).set_placement((cx + 0.25, 3.0), align=TextEntityAlignment.LEFT)
        
        # Connected to circuit details
        msp.add_line((cx, 2.8), (cx, 2.0), dxfattribs={'layer': 'DIAGRAMA', 'color': 7})
        
        # Text details below
        msp.add_text(f"{c['lbl']}: {c['name'].upper()}", dxfattribs={'layer': 'TEXTOS', 'height': 0.10, 'color': 7}).set_placement((cx, 1.8), align=TextEntityAlignment.MIDDLE_CENTER)
        msp.add_text(f"Cond: {c['cond']}", dxfattribs={'layer': 'TEXTOS', 'height': 0.08, 'color': 7}).set_placement((cx, 1.6), align=TextEntityAlignment.MIDDLE_CENTER)
        msp.add_text(c["desc"], dxfattribs={'layer': 'TEXTOS', 'height': 0.08, 'color': 7}).set_placement((cx, 1.4), align=TextEntityAlignment.MIDDLE_CENTER)

    # 3. Load Schedule Table (Cuadro de Cargas) at the bottom
    # We will draw a neat grid from Y = -0.8 to Y = 0.8, X = 0.0 to X = 11.5
    ty1, ty2 = -0.9, 0.8
    tx1, tx2 = 0.0, 11.5
    
    # Outer box
    msp.add_lwpolyline([(tx1, ty1), (tx2, ty1), (tx2, ty2), (tx1, ty2)], close=True, dxfattribs={'layer': 'TABLAS', 'color': 8})
    
    # Title of table
    msp.add_text("CUADRO DE CARGAS DE INSTALACIÓN ELÉCTRICA", dxfattribs={'layer': 'TEXTOS', 'height': 0.13, 'color': 7}).set_placement((tx1 + 0.2, ty2 + 0.1))
    
    # Headers
    cols = [
        {"w": 0.8, "name": "Cto"},
        {"w": 2.5, "name": "Descripción de Carga"},
        {"w": 1.4, "name": "Pot. Inst. (W)"},
        {"w": 1.4, "name": "F. Demanda"},
        {"w": 1.4, "name": "Máx. Dem. (W)"},
        {"w": 1.2, "name": "Int. ITM"},
        {"w": 2.8, "name": "Conductor Alimentador"}
    ]
    
    # Draw horizontal header line
    msp.add_line((tx1, ty2 - 0.35), (tx2, ty2 - 0.35), dxfattribs={'layer': 'TABLAS', 'color': 8})
    
    x_curr = tx1
    for c in cols:
        msp.add_text(c["name"], dxfattribs={'layer': 'TEXTOS', 'height': 0.09, 'color': 7}).set_placement((x_curr + c["w"]/2, ty2 - 0.22), align=TextEntityAlignment.MIDDLE_CENTER)
        x_curr += c["w"]
        if x_curr < tx2 - 0.01:
            msp.add_line((x_curr, ty1), (x_curr, ty2), dxfattribs={'layer': 'TABLAS', 'color': 8})
            
    # Table rows
    rows_data = [
        ["C1", "Alumbrado General (LED)", "132", "1.00", "132", "2P-10A", "3 x 1.5 mm2 Cu (PVC 3/4\")"],
        ["C2", "Tomacorrientes Generales", "2,520", "0.70", "1,764", "2P-16A", "3 x 2.5 mm2 Cu (PVC 3/4\")"],
        ["C3", "Tomacorrientes Especial Cocina", "1,200", "0.80", "960", "2P-20A", "3 x 2.5 mm2 Cu (PVC 3/4\")"],
        ["C4", "Servicio Lavandería", "360", "0.80", "288", "2P-16A", "3 x 2.5 mm2 Cu (PVC 3/4\")"],
        ["C5", "Bomba de Agua (Servicio)", "750", "1.00", "750", "2P-16A", "3 x 2.5 mm2 Cu (PVC 3/4\")"],
        ["Total", "MÁXIMA DEMANDA ESTIMADA", "4,962", "-", "3,894 W", "Idem: 19.67 A", "Llave Gral: 2P-40A"]
    ]
    
    y_curr = ty2 - 0.35
    row_height = 0.22
    for r in rows_data:
        y_curr -= row_height
        msp.add_line((tx1, y_curr), (tx2, y_curr), dxfattribs={'layer': 'TABLAS', 'color': 8})
        
        # Put values
        x_cell = tx1
        for idx, val in enumerate(r):
            col_width = cols[idx]["w"]
            msp.add_text(val, dxfattribs={'layer': 'TEXTOS', 'height': 0.08, 'color': 7}).set_placement((x_cell + col_width/2, y_curr + 0.07), align=TextEntityAlignment.MIDDLE_CENTER)
            x_cell += col_width

    out_dxf = os.path.join(diagramas_dir, "diagrama_unifilar.dxf")
    doc.saveas(out_dxf)
    render_dxf_to_pdf_and_svg(out_dxf)
    
    # Copy to report directory
    shutil.copy2(out_dxf.replace('.dxf', '.pdf'), os.path.join(planos_report_dir, "IE-05-unifilar-cuadro-cargas.pdf"))
    print("Diagrama Unifilar General compiled.")

# ====================================================
# PUESTA A TIERRA (IE-06-puesta-tierra)
# ====================================================
def build_puesta_a_tierra():
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    
    doc.layers.new("POZO", dxfattribs={'color': 7})
    doc.layers.new("TEXTOS", dxfattribs={'color': 7})
    doc.layers.new("MARCO", dxfattribs={'color': 7})
    
    # Frame and title block
    mx1, my1 = -1.5, -1.5
    mx2, my2 = 14.5, 9.5
    
    msp.add_line((mx1, my1), (mx2, my1), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2, my1), (mx2, my2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2, my2), (mx1, my2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx1, my2), (mx1, my1), dxfattribs={'layer': 'MARCO', 'color': 7})
    
    o = 0.08
    msp.add_line((mx1+o, my1+o), (mx2-o, my1+o), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2-o, my1+o), (mx2-o, my2-o), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx2-o, my2-o), (mx1+o, my2-o), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((mx1+o, my2-o), (mx1+o, my1+o), dxfattribs={'layer': 'MARCO', 'color': 7})
    
    c_w, c_h = 4.8, 1.6
    cx1, cy1 = mx2 - o - c_w, my1 + o
    cx2, cy2 = mx2 - o, my1 + o + c_h
    msp.add_line((cx1, cy1), (cx1, cy2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy2), (cx2, cy2), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy1 + 0.4), (cx2, cy1 + 0.4), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy1 + 0.8), (cx2, cy1 + 0.8), dxfattribs={'layer': 'MARCO', 'color': 7})
    msp.add_line((cx1, cy1 + 1.2), (cx2, cy1 + 1.2), dxfattribs={'layer': 'MARCO', 'color': 7})
    
    msp.add_text("UNAP - ESCUELA INGENIERIA MECANICA ELECTRICA", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 1.35))
    msp.add_text("PROY: DETALLE PUESTA A TIERRA (IE-06)", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 0.95))
    msp.add_text("ALUM: MAMANI GALINDO RENZO GABRIEL", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 0.55))
    msp.add_text("FECHA: 2026-06-03  |  ESC: S/E (MTS)", dxfattribs={'layer': 'TEXTOS', 'height': 0.09, 'color': 7}).set_placement((cx1 + 0.1, cy1 + 0.15))
    
    # Title
    msp.add_text("DETALLE CONSTRUCTIVO DE POZO DE PUESTA A TIERRA", dxfattribs={'layer': 'TEXTOS', 'height': 0.28, 'color': 7}).set_placement((0.0, 8.5))
    
    # Draw concrete cover (Tapa de registro) at top
    # Box from X = 2.0 to 4.0, Y = 6.8 to 7.2
    msp.add_lwpolyline([(2.0, 6.8), (4.0, 6.8), (4.0, 7.2), (2.0, 7.2)], close=True, dxfattribs={'layer': 'POZO', 'color': 7})
    msp.add_text("TAPA DE CONCRETO 0.40 x 0.40 m", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((4.2, 7.0))
    
    # Draw pit main body (pozo de tierra)
    # Pit from X = 2.2 to 3.8, Y = 2.0 to 6.8
    msp.add_line((2.2, 6.8), (2.2, 2.0), dxfattribs={'layer': 'POZO', 'color': 8})
    msp.add_line((3.8, 6.8), (3.8, 2.0), dxfattribs={'layer': 'POZO', 'color': 8})
    msp.add_line((2.2, 2.0), (3.8, 2.0), dxfattribs={'layer': 'POZO', 'color': 8})
    
    # Labeled dimension of the pit
    msp.add_text("Diámetro del Pozo: 0.80 m / Altura: 2.40 m", dxfattribs={'layer': 'TEXTOS', 'height': 0.10, 'color': 7}).set_placement((4.2, 4.5))
    
    # Draw copper electrode (bar de cobre en el centro)
    # X = 3.0, Y = 1.0 to 7.0 (height 6.0 representing rod)
    msp.add_line((3.0, 1.0), (3.0, 7.0), dxfattribs={'layer': 'POZO', 'color': 1, 'lineweight': 40}) # Red for copper rod
    msp.add_text("ELECTRODO DE COBRE 3/4\" x 2.40 m", dxfattribs={'layer': 'TEXTOS', 'height': 0.11, 'color': 7}).set_placement((3.2, 3.5))
    
    # Split-bolt copper connector at top of the rod
    msp.add_circle((3.0, 6.9), 0.08, dxfattribs={'layer': 'POZO', 'color': 1})
    msp.add_text("Conector Split-Bolt de Bronce", dxfattribs={'layer': 'TEXTOS', 'height': 0.10, 'color': 7}).set_placement((3.2, 6.8))
    
    # Copper wire going from connector to ground busbar
    msp.add_line((3.0, 6.9), (1.5, 7.8), dxfattribs={'layer': 'POZO', 'color': 1, 'linetype': 'DASHED'})
    msp.add_text("Cable de Cobre de Protección (10 mm2)", dxfattribs={'layer': 'TEXTOS', 'height': 0.10, 'color': 7}).set_placement((0.2, 7.5))
    
    # Soil filling (Tierra de chacra c/ aditivo gel)
    msp.add_text("Relleno: Tierra de cultivo tratada", dxfattribs={'layer': 'TEXTOS', 'height': 0.10, 'color': 7}).set_placement((4.2, 2.8))
    msp.add_text("con aditivos de conductividad (Bentonita/Gel)", dxfattribs={'layer': 'TEXTOS', 'height': 0.10, 'color': 7}).set_placement((4.2, 2.5))
    
    # Specifications list on the right
    spec_x, spec_y = 8.5, 3.5
    msp.add_text("ESPECIFICACIONES TÉCNICAS", dxfattribs={'layer': 'TEXTOS', 'height': 0.13, 'color': 7}).set_placement((spec_x, spec_y + 3.0))
    specs = [
        "1. Resistencia final del pozo: < 15 Ohms.",
        "2. Electrodo de cobre puro electrolítico al 99.9%.",
        "3. Conductor de tierra embutido en tubo PVC-SAP 3/4\".",
        "4. Tratamiento del terreno con sales higroscópicas.",
        "5. Caja de registro de concreto H=0.30 m.",
        "6. Conexión franca a barra de tierra en TG-01."
    ]
    for i, s in enumerate(specs):
        msp.add_text(s, dxfattribs={'layer': 'TEXTOS', 'height': 0.09, 'color': 7}).set_placement((spec_x, spec_y + 2.5 - i * 0.4))

    out_dxf = os.path.join(diagramas_dir, "puesta_a_tierra.dxf")
    doc.saveas(out_dxf)
    render_dxf_to_pdf_and_svg(out_dxf)
    
    # Copy to report directory
    shutil.copy2(out_dxf.replace('.dxf', '.pdf'), os.path.join(planos_report_dir, "IE-06-puesta-tierra.pdf"))
    print("Detalle Puesta a Tierra compiled.")

if __name__ == "__main__":
    print("Generando todos los planos eléctricos y diagramas...")
    build_floor1_electrical()
    build_floor2_electrical()
    build_floor3_electrical()
    build_diagrama_unifilar()
    build_puesta_a_tierra()
    print("¡Todos los entregables CAD generados con éxito!")
