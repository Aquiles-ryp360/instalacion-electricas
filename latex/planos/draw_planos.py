import ezdxf
import math
import os

def create_dxf():
    # Crear un nuevo dibujo DXF (formato AutoCAD R2010 para compatibilidad)
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Definir capas con colores específicos (colores estándar de AutoCAD)
    doc.layers.new(name='MUROS', dxfattribs={'color': 7})      # Blanco/Negro (15cm ext, 10cm int)
    doc.layers.new(name='PUERTAS', dxfattribs={'color': 2})    # Amarillo
    doc.layers.new(name='ESCALERAS', dxfattribs={'color': 5})  # Azul
    doc.layers.new(name='TEXTO', dxfattribs={'color': 3})      # Verde
    doc.layers.new(name='COTAS', dxfattribs={'color': 1})      # Rojo
    doc.layers.new(name='ROTULO', dxfattribs={'color': 4})     # Cian

    # Helper para dibujar muros como líneas dobles
    def add_wall_h(x1, x2, y, thickness=0.15):
        msp.add_line((x1, y - thickness/2), (x2, y - thickness/2), dxfattribs={'layer': 'MUROS'})
        msp.add_line((x1, y + thickness/2), (x2, y + thickness/2), dxfattribs={'layer': 'MUROS'})

    def add_wall_v(x, y1, y2, thickness=0.15):
        msp.add_line((x - thickness/2, y1), (x - thickness/2, y2), dxfattribs={'layer': 'MUROS'})
        msp.add_line((x + thickness/2, y1), (x + thickness/2, y2), dxfattribs={'layer': 'MUROS'})

    # Helper para dibujar puertas
    def add_door(x, y, size, angle_deg, swing_left=True):
        rad = math.radians(angle_deg)
        leaf_angle = angle_deg + (90 if swing_left else -90)
        leaf_rad = math.radians(leaf_angle)
        x_end = x + size * math.cos(leaf_rad)
        y_end = y + size * math.sin(leaf_rad)
        
        # Hoja de la puerta
        msp.add_line((x, y), (x_end, y_end), dxfattribs={'layer': 'PUERTAS'})
        
        # Arco de abatimiento
        if swing_left:
            start_a = angle_deg
            end_a = angle_deg + 90
        else:
            start_a = angle_deg - 90
            end_a = angle_deg
        msp.add_arc((x, y), size, start_a, end_a, dxfattribs={'layer': 'PUERTAS'})

    # Helper para dibujar escaleras
    def add_stairs(x1, x2, y1, y2, num_steps):
        width = x2 - x1
        height = y2 - y1
        step_h = height / num_steps
        
        # Contorno de la escalera
        msp.add_line((x1, y1), (x1, y2), dxfattribs={'layer': 'ESCALERAS'})
        msp.add_line((x2, y1), (x2, y2), dxfattribs={'layer': 'ESCALERAS'})
        msp.add_line((x1, y1), (x2, y1), dxfattribs={'layer': 'ESCALERAS'})
        msp.add_line((x1, y2), (x2, y2), dxfattribs={'layer': 'ESCALERAS'})
        
        # Pasos
        for i in range(1, num_steps):
            y_curr = y1 + i * step_h
            msp.add_line((x1, y_curr), (x2, y_curr), dxfattribs={'layer': 'ESCALERAS'})

    # Helper para agregar texto centrado
    def add_label(text, x, y, height=0.25):
        t = msp.add_text(text, dxfattribs={
            'layer': 'TEXTO',
            'height': height,
            'halign': 1, # Center
            'valign': 2  # Middle
        })
        t.dxf.insert = (x, y)
        t.dxf.align_point = (x, y)

    # Helper para agregar cotas
    def add_dimension(x1, y1, x2, y2, text_val, text_offset=0.3):
        # Dibujar línea de cota
        msp.add_line((x1, y1), (x2, y2), dxfattribs={'layer': 'COTAS'})
        # Pequeñas marcas en los extremos
        if x1 == x2: # Cota vertical
            msp.add_line((x1 - 0.1, y1), (x1 + 0.1, y1), dxfattribs={'layer': 'COTAS'})
            msp.add_line((x2 - 0.1, y2), (x2 + 0.1, y2), dxfattribs={'layer': 'COTAS'})
            add_label(text_val, x1 - text_offset, (y1 + y2)/2, height=0.2)
        else: # Cota horizontal
            msp.add_line((x1, y1 - 0.1), (x1, y1 + 0.1), dxfattribs={'layer': 'COTAS'})
            msp.add_line((x2, y2 - 0.1), (x2, y2 + 0.1), dxfattribs={'layer': 'COTAS'})
            add_label(text_val, (x1 + x2)/2, y1 - text_offset, height=0.2)

    # ----------------------------------------------------
    # DIBUJO DEL PRIMER PISO (Origen en X=0, Y=0)
    # Total Terreno: 4.5 m de ancho, 7.0 m de largo de cuartos + escalera (total 8.5 m)
    # ----------------------------------------------------
    X1, Y1 = 0.0, 0.0
    W1, H1 = 4.5, 7.0
    EXT_H = 8.5 # Incluyendo la parte de la escalera al fondo
    
    # Muros exteriores del Primer Piso
    add_wall_h(X1, X1 + W1, Y1, thickness=0.15) # Muro frontal (con abertura del portón más adelante)
    add_wall_h(X1, X1 + W1, Y1 + EXT_H, thickness=0.15) # Muro posterior
    add_wall_v(X1, Y1, Y1 + EXT_H, thickness=0.15) # Muro izquierdo
    add_wall_v(X1 + W1, Y1, Y1 + EXT_H, thickness=0.15) # Muro derecho

    # Muros interiores
    # Separación pasadizo / dormitorios a X = 3.0 m (ancho dormitorios = 3m, pasadizo = 1.5m)
    add_wall_v(X1 + 3.0, Y1, Y1 + 7.0, thickness=0.10)
    # Separación Dormitorio 1 (abajo) y Dormitorio 2 (medio) a Y = 3.5 m
    add_wall_h(X1, X1 + 3.0, Y1 + 3.5, thickness=0.10)
    # Separación Dormitorio 2 y Escalera a Y = 7.0 m
    add_wall_h(X1, X1 + 3.0, Y1 + 7.0, thickness=0.10)

    # Escalera Primer Piso (Y = 7.0 a 8.5, X = 0 a 2.5)
    add_stairs(X1 + 0.15, X1 + 2.5, Y1 + 7.0, Y1 + 8.5, 6)

    # Puertas Primer Piso
    # Portón exterior (X=3.0 a 4.5, Y=0)
    msp.add_line((X1 + 3.0, Y1), (X1 + 3.75, Y1 + 0.75), dxfattribs={'layer': 'PUERTAS'})
    msp.add_line((X1 + 4.5, Y1), (X1 + 3.75, Y1 + 0.75), dxfattribs={'layer': 'PUERTAS'})
    
    # Puerta Dormitorio 1 (del pasadizo al cuarto, en el muro X=3.0, Y=2.5 a 3.3)
    add_door(X1 + 3.0, Y1 + 3.3, 0.8, 270, swing_left=True)
    # Puerta Dormitorio 2 (del pasadizo al cuarto, en el muro X=3.0, Y=6.0 a 6.8)
    add_door(X1 + 3.0, Y1 + 6.8, 0.8, 270, swing_left=True)
    # Puerta principal de ingreso al Dormitorio 1 desde la calle (abajo a la izquierda)
    add_door(X1 + 0.15, Y1 + 0.15, 0.9, 0, swing_left=True)

    # Textos Primer Piso
    add_label("DORMITORIO 1", X1 + 1.5, Y1 + 1.75)
    add_label("DORMITORIO 2", X1 + 1.5, Y1 + 5.25)
    add_label("PASADIZO", X1 + 3.75, Y1 + 3.5)
    add_label("ESCALERA", X1 + 1.3, Y1 + 7.75, height=0.18)
    add_label("PRIMER PISO", X1 + 2.25, Y1 - 0.8, height=0.35)
    add_label("ESC: 1:50", X1 + 2.25, Y1 - 1.2, height=0.2)

    # Cotas Primer Piso
    add_dimension(X1, Y1 - 0.3, X1 + 4.5, Y1 - 0.3, "4.50 m")
    add_dimension(X1 - 0.3, Y1, X1 - 0.3, Y1 + 3.5, "3.50 m")
    add_dimension(X1 - 0.3, Y1 + 3.5, X1 - 0.3, Y1 + 7.0, "3.50 m")
    add_dimension(X1 - 0.3, Y1 + 7.0, X1 - 0.3, Y1 + 8.5, "1.50 m")
    add_dimension(X1 - 0.8, Y1, X1 - 0.8, Y1 + 8.5, "7.00 m (útil)")

    # ----------------------------------------------------
    # DIBUJO DEL SEGUNDO PISO (Origen en X=8.0, Y=0)
    # Total Terreno: 4.5 m de ancho, 7.5 m de largo + escalera (total 9.0 m)
    # ----------------------------------------------------
    X2, Y2 = 8.0, 0.0
    W2, H2 = 4.5, 7.5
    EXT_H2 = 9.0 # Incluyendo escalera y baño
    
    # Muros exteriores Segundo Piso
    add_wall_h(X2, X2 + W2, Y2, thickness=0.15)
    add_wall_h(X2, X2 + W2, Y2 + EXT_H2, thickness=0.15)
    add_wall_v(X2, Y2, Y2 + EXT_H2, thickness=0.15)
    add_wall_v(X2 + W2, Y2, Y2 + EXT_H2, thickness=0.15)

    # Muros interiores
    # Sala / Comedor ocupa todo el ancho abajo (4m de largo)
    add_wall_h(X2, X2 + W2, Y2 + 4.0, thickness=0.10)
    # Dormitorio en el medio (X = 8.0 a 11.0, Y = 4.0 a 7.5)
    add_wall_v(X2 + 3.0, Y2 + 4.0, Y2 + 7.5, thickness=0.10)
    add_wall_h(X2, X2 + 3.0, Y2 + 7.5, thickness=0.10)
    # Baño/Cocina al fondo a la derecha (X = 11.0 a 12.5, Y = 7.5 a 9.0)
    add_wall_h(X2 + 3.0, X2 + W2, Y2 + 7.5, thickness=0.10)

    # Escalera Segundo Piso (Y = 7.5 a 9.0, X = 8.0 a 11.0)
    add_stairs(X2 + 0.15, X2 + 2.5, Y2 + 7.5, Y2 + 9.0, 6)

    # Puertas Segundo Piso
    # Puerta de ingreso general (desde la escalera al pasadizo)
    add_door(X2 + 3.0, Y2 + 7.5, 0.8, 90, swing_left=True)
    # Puerta Sala a Dormitorio (en muro Y=4.0)
    add_door(X2 + 1.5, Y2 + 4.0, 0.8, 180, swing_left=True)
    # Puerta de Baño/Cocina (en muro Y=7.5)
    add_door(X2 + 3.5, Y2 + 7.5, 0.7, 0, swing_left=True)

    # Textos Segundo Piso
    add_label("SALA / COMEDOR", X2 + 2.25, Y2 + 2.0)
    add_label("DORMITORIO 3", X2 + 1.5, Y2 + 5.75)
    add_label("BAÑO / COCINA", X2 + 3.75, Y2 + 8.25, height=0.18)
    add_label("HALL", X2 + 3.75, Y2 + 5.75, height=0.18)
    add_label("ESCALERA", X2 + 1.3, Y2 + 8.25, height=0.18)
    add_label("SEGUNDO PISO", X2 + 2.25, Y2 - 0.8, height=0.35)
    add_label("ESC: 1:50", X2 + 2.25, Y2 - 1.2, height=0.2)

    # Cotas Segundo Piso
    add_dimension(X2, Y2 - 0.3, X2 + 4.5, Y2 - 0.3, "4.50 m")
    add_dimension(X2 - 0.3, Y2, X2 - 0.3, Y2 + 4.0, "4.00 m")
    add_dimension(X2 - 0.3, Y2 + 4.0, X2 - 0.3, Y2 + 7.5, "3.50 m")
    add_dimension(X2 - 0.3, Y2 + 7.5, X2 - 0.3, Y2 + 9.0, "1.50 m")
    add_dimension(X2 - 0.8, Y2, X2 - 0.8, Y2 + 9.0, "7.50 m (útil)")

    # ----------------------------------------------------
    # DIBUJO DEL TERCER PISO (Origen en X=16.0, Y=0)
    # Total Terreno: 4.5 m de ancho, 7.5 m de largo + escalera (total 9.0 m)
    # ----------------------------------------------------
    X3, Y3 = 16.0, 0.0
    W3, H3 = 4.5, 7.5
    EXT_H3 = 9.0 # Incluyendo escalera y baño
    
    # Muros exteriores Tercer Piso
    add_wall_h(X3, X3 + W3, Y3, thickness=0.15)
    add_wall_h(X3, X3 + W3, Y3 + EXT_H3, thickness=0.15)
    add_wall_v(X3, Y3, Y3 + EXT_H3, thickness=0.15)
    add_wall_v(X3 + W3, Y3, Y3 + EXT_H3, thickness=0.15)

    # Muros interiores
    # División vertical en dos dormitorios iguales (X=18.25 m, Y=0 a 7.5 m)
    add_wall_v(X3 + 2.25, Y3, Y3 + 7.5, thickness=0.10)
    # Muro horizontal divisorio de los dormitorios al fondo (Y=7.5 m)
    add_wall_h(X3, X3 + W3, Y3 + 7.5, thickness=0.10)
    # Cuarto chico/Baño al fondo a la derecha (X=18.25 a 20.5, Y=7.5 a 9.0)
    add_wall_v(X3 + 2.25, Y3 + 7.5, Y3 + 9.0, thickness=0.10)

    # Escalera Tercer Piso (Y=7.5 a 9.0, X=16.0 a 18.25)
    add_stairs(X3 + 0.15, X3 + 2.1, Y3 + 7.5, Y3 + 9.0, 6)

    # Puertas Tercer Piso
    # Puerta Dormitorio Izquierdo (en muro Y=7.5)
    add_door(X3 + 1.12, Y3 + 7.5, 0.8, 180, swing_left=True)
    # Puerta Dormitorio Derecho (en muro Y=7.5)
    add_door(X3 + 2.25, Y3 + 7.5, 0.8, 0, swing_left=True)
    # Puerta de Baño/Cuarto Chico (en muro Y=7.5)
    add_door(X3 + 3.37, Y3 + 7.5, 0.7, 0, swing_left=True)

    # Textos Tercer Piso
    add_label("DORMITORIO 4", X3 + 1.12, Y3 + 3.75, height=0.2)
    add_label("DORMITORIO 5", X3 + 3.37, Y3 + 3.75, height=0.2)
    add_label("CUARTO CHICO", X3 + 3.37, Y3 + 8.25, height=0.18)
    add_label("HALL", X3 + 2.25, Y3 + 6.8, height=0.18)
    add_label("ESCALERA", X3 + 1.1, Y3 + 8.25, height=0.18)
    add_label("TERCER PISO", X3 + 2.25, Y3 - 0.8, height=0.35)
    add_label("ESC: 1:50", X3 + 2.25, Y3 - 1.2, height=0.2)

    # Cotas Tercer Piso
    add_dimension(X3, Y3 - 0.3, X3 + 4.5, Y3 - 0.3, "4.50 m")
    add_dimension(X3 - 0.3, Y3, X3 - 0.3, Y3 + 7.5, "7.50 m")
    add_dimension(X3 - 0.3, Y3 + 7.5, X3 - 0.3, Y3 + 9.0, "1.50 m")

    # ----------------------------------------------------
    # DIBUJO DEL RÓTULO ACADÉMICO (Cuadro de datos a la derecha)
    # Ubicación: X = 21.5 a 24.5, Y = 0 a 9.0
    # ----------------------------------------------------
    XR, YR = 21.5, 0.0
    WR, HR = 3.0, 9.0
    
    # Líneas de contorno del rótulo
    msp.add_line((XR, YR), (XR + WR, YR), dxfattribs={'layer': 'ROTULO'})
    msp.add_line((XR + WR, YR), (XR + WR, YR + HR), dxfattribs={'layer': 'ROTULO'})
    msp.add_line((XR + WR, YR + HR), (XR, YR + HR), dxfattribs={'layer': 'ROTULO'})
    msp.add_line((XR, YR + HR), (XR, YR), dxfattribs={'layer': 'ROTULO'})

    # Divisiones horizontales en el rótulo
    for h in [1.5, 3.0, 4.5, 6.0, 7.5]:
        msp.add_line((XR, YR + h), (XR + WR, YR + h), dxfattribs={'layer': 'ROTULO'})

    # Textos del Rótulo
    add_label("UNIVERSIDAD NACIONAL", XR + WR/2, YR + 8.5, height=0.2)
    add_label("DEL ALTIPLANO - FIME", XR + WR/2, YR + 8.1, height=0.18)
    
    add_label("INSTALACIONES ELECTRICAS I", XR + WR/2, YR + 7.0, height=0.18)
    add_label("PROYECTO DOMICILIARIO", XR + WR/2, YR + 6.6, height=0.2)

    add_label("ESTUDIANTE:", XR + 0.2, YR + 5.6, height=0.15)
    msp.add_text("Aquiles Taylor", dxfattribs={'layer': 'TEXTO', 'height': 0.18, 'insert': (XR + 0.2, YR + 5.2)})
    msp.add_text("Ramos Yapo", dxfattribs={'layer': 'TEXTO', 'height': 0.18, 'insert': (XR + 0.2, YR + 4.9)})

    add_label("DIRECCION:", XR + 0.2, YR + 4.1, height=0.15)
    msp.add_text("Av. Horacio / Marineros", dxfattribs={'layer': 'TEXTO', 'height': 0.15, 'insert': (XR + 0.2, YR + 3.7)})
    msp.add_text("San Miguel - Puno", dxfattribs={'layer': 'TEXTO', 'height': 0.15, 'insert': (XR + 0.2, YR + 3.4)})

    add_label("FECHA: JUNIO 2026", XR + 0.2, YR + 2.5, height=0.15)
    add_label("PLANO: ARQUITECTURA", XR + 0.2, YR + 2.0, height=0.15)

    add_label("PLANO N°:", XR + 0.5, YR + 0.9, height=0.18)
    add_label("ARQ-01", XR + 2.0, YR + 0.7, height=0.35)

    # Guardar archivo DXF
    dxf_output_path = r"C:\Users\renzo\instalacion-electricas\latex\planos\AVANCE DEL PLANO ELECTRICO1.dxf"
    doc.saveas(dxf_output_path)
    print("SUCCESS: DXF file created at", dxf_output_path)

if __name__ == '__main__':
    create_dxf()
