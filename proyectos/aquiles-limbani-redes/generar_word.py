#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_word.py
Genera el Expediente Técnico completo en formato Microsoft Word (.docx)
para el proyecto de Electrificación y Redes de Distribución de Limbani (200 kW).
"""

import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Establece color de fondo de una celda en formato HEX (ej: '006699')."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Establece márgenes internos de una celda en dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_table_styled(doc, rows, cols, col_widths=None):
    """Crea una tabla con bordes estilizados."""
    table = doc.add_table(rows=rows, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    if col_widths:
        for r in table.rows:
            for i, w in enumerate(col_widths):
                r.cells[i].width = Inches(w)
    return table

def style_header_row(row, fill_hex="006699", font_color="FFFFFF"):
    for cell in row.cells:
        set_cell_background(cell, fill_hex)
        set_cell_margins(cell, 120, 120, 150, 150)
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.bold = True
                run.font.size = Pt(9.5)
                run.font.name = 'Arial'
                run.font.color.rgb = RGBColor.from_string(font_color)

def style_body_row(row, is_even=False, font_size=9.0):
    fill = "F4F6F9" if is_even else "FFFFFF"
    for cell in row.cells:
        if fill != "FFFFFF":
            set_cell_background(cell, fill)
        set_cell_margins(cell, 90, 90, 140, 140)
        for p in cell.paragraphs:
            for run in p.runs:
                run.font.size = Pt(font_size)
                run.font.name = 'Arial'

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(15)
    run.font.bold = True
    run.font.color.rgb = RGBColor(180, 0, 0) # Heading red
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(12.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0, 102, 153) # Model blue
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGBColor(50, 50, 50)
    return p

def add_p(doc, text="", bold_prefix=None, space_after=5):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.name = 'Arial'
        r_b.font.size = Pt(10)
        r_b.font.bold = True
    if text:
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(10)
    return p

def add_bullet(doc, text="", bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.name = 'Arial'
        r_b.font.size = Pt(10)
        r_b.font.bold = True
    if text:
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(10)
    return p

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fig_dir = os.path.join(base_dir, "expediente", "figuras")
    out_dir = os.path.join(base_dir, "entregables")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "expediente_limbani.docx")

    print("[*] Iniciando generación de Expediente Técnico en formato Word...")
    doc = Document()

    # Configurar márgenes
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # -------------------------------------------------------------
    # PORTADA
    # -------------------------------------------------------------
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    escudo_path = os.path.join(fig_dir, "escudo-unap.png")
    if os.path.exists(escudo_path):
        p_img.add_run().add_picture(escudo_path, width=Inches(1.5))
    
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_uni.paragraph_format.space_before = Pt(8)
    p_uni.paragraph_format.space_after = Pt(2)
    r = p_uni.add_run("UNIVERSIDAD NACIONAL DEL ALTIPLANO - PUNO\n")
    r.font.bold = True
    r.font.size = Pt(14)
    r.font.name = 'Arial'
    r2 = p_uni.add_run("FACULTAD DE INGENIERÍA MECÁNICA ELÉCTRICA, ELECTRÓNICA Y SISTEMAS\n")
    r2.font.bold = True
    r2.font.size = Pt(12)
    r2.font.name = 'Arial'
    r3 = p_uni.add_run("ESCUELA PROFESIONAL DE INGENIERÍA MECÁNICA ELÉCTRICA")
    r3.font.bold = True
    r3.font.size = Pt(11)
    r3.font.name = 'Arial'

    p_line1 = doc.add_paragraph()
    p_line1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_l1 = p_line1.add_run("―" * 55)
    r_l1.font.color.rgb = RGBColor(0, 102, 153)
    r_l1.font.bold = True

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(10)
    p_tit.paragraph_format.space_after = Pt(6)
    r_t1 = p_tit.add_run("EXPEDIENTE TÉCNICO DE INGENIERÍA\n")
    r_t1.font.bold = True
    r_t1.font.size = Pt(18)
    r_t1.font.color.rgb = RGBColor(180, 0, 0)
    r_t1.font.name = 'Arial'

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_after = Pt(10)
    r_p = p_proj.add_run("«ELECTRIFICACIÓN Y REDES DE DISTRIBUCIÓN EN MEDIA TENSIÓN (10 kV) Y BAJA TENSIÓN (380/220 V) DESDE LA MINICENTRAL HIDROELÉCTRICA LIMBANI (200 kW, TURBINA MICHELL-BANKI)»\n\n")
    r_p.font.bold = True
    r_p.font.size = Pt(13)
    r_p.font.color.rgb = RGBColor(0, 102, 153)
    r_p.font.name = 'Arial'
    r_loc = p_proj.add_run("CASCO URBANO DEL DISTRITO DE LIMBANI ― SANDIA ― PUNO")
    r_loc.font.bold = True
    r_loc.font.size = Pt(11)
    r_loc.font.name = 'Arial'

    p_line2 = doc.add_paragraph()
    p_line2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_l2 = p_line2.add_run("―" * 55)
    r_l2.font.color.rgb = RGBColor(0, 102, 153)
    r_l2.font.bold = True

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(15)
    p_meta.paragraph_format.space_after = Pt(20)
    
    meta_items = [
        ("CURSO: ", "Instalaciones Eléctricas II / Redes Eléctricas y Subestaciones"),
        ("DOCENTE: ", "Docente del Curso (FIME - UNAP)"),
        ("AUTOR / RESPONSABLE: ", "Br. Aquiles Taylor Ramos Yapo (Cód. 227368)"),
        ("SEMESTRE ACADÉMICO: ", "2026-II"),
        ("SISTEMA GEODÉSICO: ", "WGS 84 / UTM Zona 19 Sur (EPSG:32719)"),
        ("POTENCIA GENERACIÓN: ", "200 kW (Turbina Michell-Banki / Alternador 380 V)"),
        ("POBLACIÓN BENEFICIARIA: ", "764 Viviendas Consolidadas / 623 Lotes Catastrados")
    ]
    for lbl, val in meta_items:
        r_lbl = p_meta.add_run(lbl)
        r_lbl.font.bold = True
        r_lbl.font.size = Pt(10.5)
        r_lbl.font.name = 'Arial'
        r_val = p_meta.add_run(val + "\n")
        r_val.font.size = Pt(10.5)
        r_val.font.name = 'Arial'

    p_pie = doc.add_paragraph()
    p_pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pie.paragraph_format.space_before = Pt(30)
    r_pie = p_pie.add_run("PUNO ― PERÚ\n2026")
    r_pie.font.bold = True
    r_pie.font.size = Pt(11)
    r_pie.font.name = 'Arial'

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO I: MEMORIA DESCRIPTIVA
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO I: MEMORIA DESCRIPTIVA")
    
    add_heading_2(doc, "1.1 Generalidades y Antecedentes")
    add_p(doc, "El presente Expediente Técnico de Ingeniería ha sido elaborado para el dimensionamiento, diseño y especificación electromecánica del proyecto: «Electrificación y Redes de Distribución en Media Tensión (10 kV) y Baja Tensión (380/220 V) desde la Minicentral Hidroeléctrica Limbani (200 kW, Turbina Michell-Banki)», ubicado en el distrito de Limbani, provincia de Sandia, departamento de Puno.")
    add_p(doc, "Históricamente, los centros poblados y distritos situados en las vertientes orientales de la cordillera de Carabaya y Sandia han enfrentado limitaciones en el suministro continuo y de calidad de energía eléctrica, debido a la topografía accidentada y la lejanía de las grandes troncales del Sistema Eléctrico Interconectado Nacional (SEIN). En este contexto, el aprovechamiento del abundante potencial hídrico de la cuenca del Río Limbani mediante la operación de una minicentral hidroeléctrica de pasada con turbina Michell-Banki de 200 kW representa una solución técnica, económica y ambientalmente sostenible para garantizar la soberanía energética del casco urbano de Limbani.")
    add_p(doc, "Para la concepción del presente proyecto se ha tomado como base territorial y física el Catastro Urbano Oficial Consolidado de Limbani, levantado en el sistema geodésico WGS 84 / UTM Zona 19 Sur, el cual registra con precisión milimétrica un total de 623 lotes de propiedad oficial, 87 manzanas catastrales y 764 viviendas consolidadas, así como la delimitación inalterable del cauce del Río Limbani, Río Chinchalamani y los equipamientos urbanos (Plaza de Armas, Estadio Municipal, Piscina y centros educativos/salud).")

    add_heading_2(doc, "1.2 Alcance y Objeto del Proyecto")
    add_p(doc, "Se precisa que las características técnicas de la Minicentral Hidroeléctrica Limbani (turbina Michell-Banki de 200 kW y alternador síncrono trifásico a 380 V) constituyen parámetros y datos de entrada del suministro eléctrico. El objeto integral del presente expediente comprende:")
    add_bullet(doc, "Subestación Elevadora 250 kVA (0.38 / 10.0 kV, Dyn5) en casa de máquinas.", bold_prefix="1. Transformación Inicial: ")
    add_bullet(doc, "Línea Primaria 10 kV (2.15 km) en conductor desnudo AAAC 35 mm² y postes CAC 12m y 13m.", bold_prefix="2. Transmisión Primaria: ")
    add_bullet(doc, "Tres Subestaciones Aéreas Biposte (SED-01 Norte 50 kVA, SED-02 Centro 100 kVA, SED-03 Sur 100 kVA).", bold_prefix="3. Subestaciones de Distribución: ")
    add_bullet(doc, "Redes Secundarias 380/220 V con cables autoportantes CAAI y postes CAC 8m y 9m.", bold_prefix="4. Redes de Distribución: ")
    add_bullet(doc, "Alumbrado Público LED (165 luminarias de 50 W con control fotocelular).", bold_prefix="5. Alumbrado Público: ")
    add_bullet(doc, "764 Acometidas domiciliarias monofásicas con medición estática y cajas IP54.", bold_prefix="6. Acometidas y Medición: ")

    add_heading_2(doc, "1.3 Ubicación Política, Geográfica y Cartografía Territorial")
    add_bullet(doc, "Puno", bold_prefix="Departamento: ")
    add_bullet(doc, "Sandia", bold_prefix="Provincia: ")
    add_bullet(doc, "Limbani", bold_prefix="Distrito: ")
    add_bullet(doc, "Casco urbano consolidado (Barrio Norte, Centro y Barrio Sur)", bold_prefix="Sector beneficiario: ")
    add_bullet(doc, "3,050 m.s.n.m. (rango 2,980 - 3,150 m.s.n.m.)", bold_prefix="Altitud media: ")
    add_bullet(doc, "Este: 425,250 a 425,700 m E | Norte: 8'434,750 a 8'436,650 m N", bold_prefix="Coordenadas UTM (WGS 84 Z19S): ")

    # Insertar imágenes de ubicación territorial
    img_ub_puno = os.path.join(fig_dir, "ubicacion_departamento_puno.jpg")
    img_ub_sandia = os.path.join(fig_dir, "ubicacion_provincia_sandia.jpg")
    img_ub_macro = os.path.join(fig_dir, "ubicacion_macrorregional.png")
    
    if os.path.exists(img_ub_puno) and os.path.exists(img_ub_sandia):
        p_u1 = doc.add_paragraph()
        p_u1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_u1.paragraph_format.space_before = Pt(8)
        p_u1.paragraph_format.space_after = Pt(2)
        p_u1.add_run().add_picture(img_ub_puno, width=Inches(2.8))
        p_u1.add_run("   ")
        p_u1.add_run().add_picture(img_ub_sandia, width=Inches(2.8))
        
        p_pie_u1 = doc.add_paragraph()
        p_pie_u1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_pie_u1.paragraph_format.space_after = Pt(8)
        r_pu1 = p_pie_u1.add_run("Figura 1.1: Localización del Departamento de Puno y de la Provincia de Sandia.")
        r_pu1.font.italic = True
        r_pu1.font.size = Pt(9)
        r_pu1.font.color.rgb = RGBColor(80, 80, 80)

    if os.path.exists(img_ub_macro):
        p_u2 = doc.add_paragraph()
        p_u2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_u2.paragraph_format.space_before = Pt(6)
        p_u2.paragraph_format.space_after = Pt(2)
        p_u2.add_run().add_picture(img_ub_macro, width=Inches(5.8))
        
        p_pie_u2 = doc.add_paragraph()
        p_pie_u2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_pie_u2.paragraph_format.space_after = Pt(10)
        r_pu2 = p_pie_u2.add_run("Figura 1.2: Relieve y localización orográfica del Distrito de Limbani en los Andes Orientales.")
        r_pu2.font.italic = True
        r_pu2.font.size = Pt(9)
        r_pu2.font.color.rgb = RGBColor(80, 80, 80)

    add_heading_3(doc, "Ruta de Acceso Terrestre")
    t_acc = create_table_styled(doc, 5, 5, [1.5, 1.8, 1.0, 1.3, 0.9])
    headers_acc = ["Tramo", "Tipo de Vía", "Distancia (km)", "Estado", "Tiempo"]
    for i, h in enumerate(headers_acc):
        t_acc.rows[0].cells[i].paragraphs[0].text = h
    style_header_row(t_acc.rows[0])
    
    rutas = [
        ["Puno – Juliaca", "Asfaltada (Red Nacional)", "44.0", "Bueno", "0.8 h"],
        ["Juliaca – Huancané – Ananea", "Asfaltada / Afirmada", "128.0", "Regular", "2.5 h"],
        ["Ananea – Crucero – Limbani", "Afirmada / Trocha afirmada", "62.0", "Tránsito moderado", "2.2 h"],
        ["Total Itinerario Terrestre", "Ruta Departamental / Local", "234.0 km", "Operativo", "≈ 5.5 h"]
    ]
    for r_idx, r_data in enumerate(rutas):
        row = t_acc.rows[r_idx + 1]
        for c_idx, val in enumerate(r_data):
            row.cells[c_idx].paragraphs[0].text = val
        style_body_row(row, is_even=(r_idx % 2 == 1))

    add_heading_2(doc, "1.3 Condiciones Ambientales y Climatológicas")
    add_p(doc, "Conforme a la zonificación bioclimática y la Parte 2 del CNE - Suministro 2011 (Zona 2: Sierra y Altiplano):")
    add_bullet(doc, "-5.0 °C (noches de helada invernal)", bold_prefix="Temperatura mínima extrema: ")
    add_bullet(doc, "+12.0 °C", bold_prefix="Temperatura media anual: ")
    add_bullet(doc, "+35.0 °C (radiación diurna directa)", bold_prefix="Temperatura máxima extrema: ")
    add_bullet(doc, "90.0 km/h (25.0 m/s)", bold_prefix="Velocidad máxima de viento: ")
    add_bullet(doc, "850 mm/año (diciembre a marzo)", bold_prefix="Precipitación pluvial media: ")
    add_bullet(doc, "60 a 75 días de tormenta/año (nivel medio-alto)", bold_prefix="Nivel ceráunico: ")
    add_bullet(doc, "150 a 450 Ω·m (suelo rocoso y arcillo-arenoso)", bold_prefix="Resistividad de terreno: ")

    add_heading_2(doc, "1.4 Descripción de la Fuente: MCH Limbani (200 kW)")
    add_bullet(doc, "Central de pasada sobre el Río Limbani.", bold_prefix="Tipo de central: ")
    add_bullet(doc, "Michell-Banki (flujo transversal o cross-flow). Caudal de diseño Q = 0.55 m³/s, salto neto H = 45.0 m, rendimiento η = 82%.", bold_prefix="Turbina hidráulica: ")
    add_bullet(doc, "Síncrono trifásico sin escobillas, 200 kW (250 kVA a cos φ = 0.80), 380 V, 60 Hz, 1,800 RPM.", bold_prefix="Generador: ")
    add_bullet(doc, "250 kVA, 0.38 / 10.0 kV, Dyn5, ONAN, clase térmica A.", bold_prefix="Transformador Elevador: ")

    add_heading_2(doc, "1.5 Descripción de las Redes de Media y Baja Tensión")
    add_p(doc, "La energía se transporta desde la casa de máquinas de la MCH Limbani hacia el casco urbano mediante una línea primaria trifásica en 10.0 kV de 2.15 km de longitud tendida con conductor desnudo de aleación de aluminio AAAC 35 mm² sobre postes de concreto armado centrifugado (CAC) de 12 m y 13 m.")
    add_p(doc, "En el casco urbano se disponen tres (03) Subestaciones Aéreas Biposte (SAB) con una potencia agregada de 250 kVA:")
    add_bullet(doc, "SAB 50 kVA (10/0.38-0.22 kV), abastece 142 lotes y cargas del sector septentrional.", bold_prefix="SED-01 (Sector Norte): ")
    add_bullet(doc, "SAB 100 kVA (10/0.38-0.22 kV), abastece 348 lotes, Plaza de Armas, Municipalidad y Centro de Salud.", bold_prefix="SED-02 (Sector Centro): ")
    add_bullet(doc, "SAB 100 kVA (10/0.38-0.22 kV), abastece 274 lotes, complejo recreacional, piscina y expansión sur.", bold_prefix="SED-03 (Sector Sur): ")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO II: CÁLCULOS JUSTIFICATIVOS
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO II: CÁLCULOS JUSTIFICATIVOS")

    add_heading_2(doc, "2.1 Estudio de Demanda y Máxima Demanda Coincidente")
    add_bullet(doc, "350 W/lote (Norma DGE R.D. 016-2003-EM/DGE)", bold_prefix="Dotación unitaria por vivienda: ")
    add_bullet(doc, "764 predios consolidados", bold_prefix="Total viviendas catastradas: ")
    add_bullet(doc, "764 × 0.350 kW = 267.40 kW", bold_prefix="Potencia instalada doméstica: ")
    add_bullet(doc, "0.52 (para más de 500 abonados según DGE)", bold_prefix="Factor de simultaneidad: ")
    add_bullet(doc, "267.40 × 0.52 = 139.05 kW", bold_prefix="Máxima demanda doméstica: ")
    add_bullet(doc, "165 luminarias LED de 50 W = 8.25 kW (Fs = 1.0)", bold_prefix="Alumbrado Público (AP): ")
    add_bullet(doc, "Municipalidad (4.5 kW) + Salud (8.0 kW) + Plaza (3.0 kW) + Estadio (7.5 kW) + Piscina (5.0 kW) + Colegios (6.5 kW) = 34.50 kW", bold_prefix="Cargas Especiales: ")
    
    add_p(doc, "MD_total = 139.05 kW + 8.25 kW + 34.50 kW = 181.80 kW", bold_prefix="Máxima Demanda Coincidente Total: ")
    add_p(doc, "S_max = 181.80 / 0.90 = 202.00 kVA (cos φ = 0.90)", bold_prefix="Potencia Aparente Coincidente: ")
    add_p(doc, "Balance frente a la generación de la MCH Limbani (200 kW netos): La demanda de 181.80 kW representa el 90.9% de la capacidad nominal de la minicentral hidroeléctrica, garantizando un margen de reserva operativa del 9.1% (18.2 kW).")

    add_heading_2(doc, "2.2 Cálculos Eléctricos de la Línea Primaria 10 kV")
    add_bullet(doc, "In = P / (√3 × Vn × cos φ) = 200.0 / (√3 × 10.0 × 0.90) = 12.83 A", bold_prefix="Corriente nominal máxima: ")
    add_bullet(doc, "AAAC 35 mm² (NTP 370.258). I_adm = 145.0 A. Factor de seguridad térmico FS = 145.0 / 12.83 = 11.30 >> 1.0.", bold_prefix="Capacidad térmica del conductor: ")
    add_bullet(doc, "ΔV = √3 × In × (R cos φ + X sin φ) × L = 50.41 V", bold_prefix="Caída de tensión absoluta: ")
    add_bullet(doc, "ΔV% = (50.41 / 10,000) × 100 = 0.504% << 5.0% (Ampliamente conforme a NTCSE)", bold_prefix="Caída de tensión porcentual: ")
    add_bullet(doc, "ΔP = 3 × In² × R × L = 3 × (12.83)² × 0.986 × 2.15 = 1,047 W = 1.05 kW (0.52% de la potencia generada)", bold_prefix="Pérdidas de potencia por efecto Joule: ")

    add_heading_2(doc, "2.3 Cálculos Eléctricos de las Redes Secundarias en Baja Tensión")
    add_bullet(doc, "CAAI autoportante (3×35 + 1×16 + NA 25 mm² troncales; 2×16 + 1×16 + NA 25 mm² derivados).", bold_prefix="Conductor adoptado: ")
    add_bullet(doc, "Para la derivación más desfavorable de la SED-02 (L = 240 m, Ib = 77.94 A): ΔV_BT = 3.82% <= 5.0% (Conforme a norma DGE y NTCSE).", bold_prefix="Caída de tensión máxima en BT: ")

    add_heading_2(doc, "2.4 Cálculos Mecánicos y Esfuerzos en Estructuras")
    add_bullet(doc, "Viento 90 km/h (Pv = 40 daN/m²); Temp. mínima -5 °C; Temp. máxima +35 °C (flecha máx = 0.48 m para vano de 85 m).", bold_prefix="Hipótesis climáticas Zona 2 CNE: ")
    add_bullet(doc, "CAC 12 m / 300 daN (alineamiento) y 13 m / 400 daN (anclaje/retención). FS >= 2.0.", bold_prefix="Postes Media Tensión: ")
    add_bullet(doc, "CAC 8 m / 200 daN y 9 m / 300 daN. FS >= 2.2.", bold_prefix="Postes Baja Tensión: ")

    add_heading_2(doc, "2.5 Cálculo de Sistemas de Puesta a Tierra (Fórmula de Dwight)")
    add_p(doc, "R = (ρ / (2π L)) × [ ln(4L / d) - 1 ]")
    add_p(doc, "Para electrodo de cobre de 5/8\" × 2.40 m y terreno tratado con bentonita (ρ = 70 Ω·m): R_1 = 25.05 Ω. Con dos varillas en paralelo separadas 3.0 m conectadas con conductor de cobre de 35 mm²: R_SED = 8.14 Ω <= 10.0 Ω (Conforme a CNE-Suministro).")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO III: ESPECIFICACIONES DE MATERIALES
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO III: ESPECIFICACIONES TÉCNICAS DE MATERIALES Y EQUIPOS")
    add_heading_2(doc, "3.1 Conductores Eléctricos")
    add_bullet(doc, "Aleación Al 6201-T81, 7 alambres, diámetro 7.56 mm, rotura 10.5 kN, R_20°C = 0.986 Ω/km, corriente admisible 145 A.", bold_prefix="AAAC 35 mm² (NTP 370.258): ")
    add_bullet(doc, "Fases de aluminio puro con aislamiento XLPE (3×35 mm²), neutro mensajero de aleación AAAC de 25 mm² y alumbrado 1×16 mm².", bold_prefix="Cable Autoportante CAAI (NTP 370.254): ")

    add_heading_2(doc, "3.2 Postes de Concreto Armado Centrifugado (CAC)")
    add_p(doc, "Fabricados según norma técnica NTP 339.027:")
    add_bullet(doc, "CAC 12 m / 300 daN (alineamiento) y CAC 13 m / 400 daN (anclajes y SAB). Cima 150-180 mm, base 330-375 mm.", bold_prefix="Media Tensión (10 kV): ")
    add_bullet(doc, "CAC 8 m / 200 daN (pasajes), CAC 8 m / 300 daN (retención) y CAC 9 m / 300 daN (mixtos con luminarias).", bold_prefix="Baja Tensión (380/220 V): ")

    add_heading_2(doc, "3.3 Transformadores de Distribución")
    t_trafo = create_table_styled(doc, 7, 4, [2.2, 1.4, 1.4, 1.4])
    h_tr = ["Parámetro", "SED-01 (Norte)", "SED-02 (Centro)", "SED-03 (Sur)"]
    for i, h in enumerate(h_tr):
        t_trafo.rows[0].cells[i].paragraphs[0].text = h
    style_header_row(t_trafo.rows[0])
    
    trafo_data = [
        ["Potencia nominal", "50 kVA", "100 kVA", "100 kVA"],
        ["Relación de transformación", "10,000 / 380-220 V", "10,000 / 380-220 V", "10,000 / 380-220 V"],
        ["Grupo de conexión", "Dyn5 (neutro fuera)", "Dyn5 (neutro fuera)", "Dyn5 (neutro fuera)"],
        ["Refrigeración / Aceite", "ONAN (Mineral libre PCB)", "ONAN (Mineral libre PCB)", "ONAN (Mineral libre PCB)"],
        ["Tensión cortocircuito (Ucc)", "4.0%", "4.5%", "4.5%"],
        ["Nivel de aislamiento (BIL)", "110 kV (3,050 msnm)", "110 kV (3,050 msnm)", "110 kV (3,050 msnm)"]
    ]
    for r_idx, r_data in enumerate(trafo_data):
        row = t_trafo.rows[r_idx + 1]
        for c_idx, val in enumerate(r_data):
            row.cells[c_idx].paragraphs[0].text = val
        style_body_row(row, is_even=(r_idx % 2 == 1))

    add_heading_2(doc, "3.4 Equipos de Protección y Maniobra MT")
    add_bullet(doc, "15 kV, 100 A continuo, BIL 110 kV, corte simétrico 8 kA, fusibles chicote tipo K (3 A y 6 A).", bold_prefix="Cortacircuitos Cut-Out: ")
    add_bullet(doc, "Óxido de Zinc (ZnO), poliméricos, Ur = 12 kV, MCOV = 10.2 kV, corriente de descarga 10 kA clase distribución pesada.", bold_prefix="Pararrayos de ZnO: ")

    add_heading_2(doc, "3.5 Luminarias de Alumbrado Público y Medición")
    add_bullet(doc, "Luminarias LED integradas de 50 W, 6,500 lm, IP66, 4,000 K (blanco neutro), pastoral de acero galvanizado 1 1/2\" × 1.5 m y fotocélula electrónica omnidireccional.", bold_prefix="Alumbrado Público: ")
    add_bullet(doc, "Cajas poliméricas monofásicas IP54 tipo L-T, medidor digital clase 1.0 (IEC 62053-21) 220 V 5(60) A, termo 2×16 A e hilo concéntrico SET 2×4 mm².", bold_prefix="Acometidas y Medición: ")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO IV: ESPECIFICACIONES DE MONTAJE
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO IV: ESPECIFICACIONES TÉCNICAS DE MONTAJE ELECTROMECÁNICO")
    add_heading_2(doc, "4.1 Trazo, Replanteo y Georreferenciación")
    add_p(doc, "Se utiliza como base inalterable el Catastro Urbano Oficial de Limbani (WGS 84 Zona 19 Sur). La ubicación de cada poste y subestación debe respetar rigurosamente los anchos de calzada, veredas y límites de propiedad privada.")
    
    add_heading_2(doc, "4.2 Excavación e Izaje de Postes CAC")
    add_bullet(doc, "He = Ht/10 + 0.50 m (1.80 m para postes de 13 m; 1.70 m para 12 m; 1.40 m para 9 m; 1.30 m para 8 m).", bold_prefix="Profundidad reglamentaria: ")
    add_bullet(doc, "Cimentación con solado de concreto simple e=0.15 m y macizo ciclópeo f'c = 140 kg/cm² + 30% piedra en laderas y terrenos rocosos.", bold_prefix="Concreto ciclópeo: ")

    add_heading_2(doc, "4.3 Tendido y Flechado")
    add_bullet(doc, "Con poleas de aluminio protegidas con neopreno, cabestrante y dinamómetro calibrado según temperatura ambiente registrada con termómetro de contacto.", bold_prefix="Línea 10 kV: ")
    add_bullet(doc, "Tendido traccionando exclusivamente el neutro portador NA 25, utilizando grapas cónicas de aleación de aluminio y poleas de nilón.", bold_prefix="Cables BT CAAI: ")

    add_heading_2(doc, "4.4 Protocolos de Pruebas Previas a la Puesta en Servicio")
    t_pru = create_table_styled(doc, 7, 4, [2.2, 1.6, 1.8, 1.0])
    h_pr = ["Prueba Electromecánica", "Instrumento", "Criterio de Aceptación", "Norma"]
    for i, h in enumerate(h_pr):
        t_pru.rows[0].cells[i].paragraphs[0].text = h
    style_header_row(t_pru.rows[0])

    pruebas = [
        ["Aislamiento Media Tensión", "Megóhmetro 2,500 V DC", "R >= 1,000 MΩ a 20 °C", "IEC 60076"],
        ["Aislamiento Baja Tensión", "Megóhmetro 1,000 V DC", "R >= 10.0 MΩ", "CNE 2011"],
        ["Resistencia de Puesta a Tierra", "Telurómetro digital 3 bornes", "R_SED <= 10 Ω / R_BT <= 25 Ω", "CNE 2011"],
        ["Secuencia y rotación fases", "Fasímetro digital", "Secuencia directa (R-S-T)", "IEC 60034"],
        ["Rigidez dieléctrica aceite", "Chispómetro normalizado", "V_rup >= 35 kV / 2.5 mm", "ASTM D877"],
        ["Tensión en vacío transformador", "Voltímetro digital RMS", "380 / 220 V ± 2.5%", "IEC 60076"]
    ]
    for r_idx, r_data in enumerate(pruebas):
        row = t_pru.rows[r_idx + 1]
        for c_idx, val in enumerate(r_data):
            row.cells[c_idx].paragraphs[0].text = val
        style_body_row(row, is_even=(r_idx % 2 == 1))

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO V: CRONOGRAMA DE EJECUCIÓN
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO V: CRONOGRAMA DE EJECUCIÓN DE OBRA")
    add_p(doc, "Plazo contractual de ejecución física: Ciento veinte (120) días calendario (4 meses consecutivos).")
    
    t_cro = create_table_styled(doc, 9, 7, [0.6, 2.5, 0.7, 0.7, 0.7, 0.7, 0.7])
    h_cr = ["Ítem", "Partida", "Pond.", "Mes 1", "Mes 2", "Mes 3", "Mes 4"]
    for i, h in enumerate(h_cr):
        t_cro.rows[0].cells[i].paragraphs[0].text = h
    style_header_row(t_cro.rows[0])

    cronog = [
        ["01.00", "Obras Preliminares y Replanteo", "8.5%", "6.0%", "2.5%", "--", "--"],
        ["02.00", "Línea Primaria 10 kV (2.15 km)", "24.5%", "5.0%", "10.0%", "9.5%", "--"],
        ["03.00", "Subestaciones Biposte (3 SED)", "21.0%", "--", "6.0%", "12.0%", "3.0%"],
        ["04.00", "Redes Secundarias y Alumbrado", "26.0%", "3.0%", "8.0%", "10.0%", "5.0%"],
        ["05.00", "Acometidas y Medición (764 viv)", "14.0%", "--", "--", "6.0%", "8.0%"],
        ["06.00", "Pruebas y Puesta en Servicio", "3.5%", "--", "--", "--", "3.5%"],
        ["07.00", "Gestión Ambiental y SST", "2.5%", "0.6%", "0.7%", "0.6%", "0.6%"],
        ["TOTAL", "Avance Físico Acumulado", "100.0%", "14.6%", "41.8%", "79.9%", "100.0%"]
    ]
    for r_idx, r_data in enumerate(cronog):
        row = t_cro.rows[r_idx + 1]
        for c_idx, val in enumerate(r_data):
            row.cells[c_idx].paragraphs[0].text = val
        is_total = (r_idx == len(cronog) - 1)
        style_body_row(row, is_even=(r_idx % 2 == 1))
        if is_total:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.bold = True

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO VI: METRADOS Y PRESUPUESTO ESTIMADO
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO VI: METRADOS Y PRESUPUESTO ESTIMADO")
    add_heading_2(doc, "6.1 Resumen del Presupuesto Referencial de Obra")

    t_pto = create_table_styled(doc, 13, 4, [0.8, 3.2, 1.4, 1.0])
    h_pt = ["Ítem", "Componente de Obra", "Costo Parcial (S/.)", "% Incid."]
    for i, h in enumerate(h_pt):
        t_pto.rows[0].cells[i].paragraphs[0].text = h
    style_header_row(t_pto.rows[0])

    presup = [
        ["01.00", "Obras Preliminares y Trabajos de Campo", "48,500.00", "5.17%"],
        ["02.00", "Línea Primaria en Media Tensión 10.0 kV", "225,400.00", "24.03%"],
        ["03.00", "Subestaciones Aéreas Biposte (3 SED, 250 kVA)", "186,800.00", "19.92%"],
        ["04.00", "Redes Secundarias 380/220 V y Alumbrado Público", "258,900.00", "27.60%"],
        ["05.00", "Acometidas Domiciliarias y Medición (764 viviendas)", "164,260.00", "17.51%"],
        ["06.00", "Pruebas Electromecánicas y Puesta en Servicio", "28,000.00", "2.99%"],
        ["07.00", "Plan de Mitigación Ambiental y Seguridad (SST)", "26,000.00", "2.77%"],
        ["--", "COSTO DIRECTO TOTAL (CD)", "937,860.00", "100.00%"],
        ["--", "Gastos Generales (10.00% CD)", "93,786.00", "10.00%"],
        ["--", "Utilidad Empresarial (8.00% CD)", "75,028.80", "8.00%"],
        ["--", "SUBTOTAL", "1,106,674.80", "118.00%"],
        ["--", "Impuesto General a las Ventas (IGV 18.00%)", "199,201.46", "21.24%"],
    ]
    for r_idx, r_data in enumerate(presup):
        row = t_pto.rows[r_idx + 1]
        for c_idx, val in enumerate(r_data):
            row.cells[c_idx].paragraphs[0].text = val
        style_body_row(row, is_even=(r_idx % 2 == 1))
        if "TOTAL" in r_data[1] or "SUBTOTAL" in r_data[1]:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.bold = True

    p_ptot = doc.add_paragraph()
    p_ptot.paragraph_format.space_before = Pt(8)
    r_pt1 = p_ptot.add_run("PRESUPUESTO TOTAL DE OBRA: S/. 1,305,876.26\n")
    r_pt1.font.bold = True
    r_pt1.font.size = Pt(12)
    r_pt1.font.color.rgb = RGBColor(180, 0, 0)
    r_pt2 = p_ptot.add_run("Son: Un Millón Trescientos Cinco Mil Ochocientos Setenta y Seis con 26/100 Soles.")
    r_pt2.font.italic = True
    r_pt2.font.size = Pt(10)

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO VII: RELACIÓN DE PLANOS Y DISEÑO CATASTRAL
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO VII: RELACIÓN DE PLANOS Y DISEÑO CATASTRAL")
    add_p(doc, "El expediente técnico incluye cinco láminas normalizadas en formato A1 georreferenciadas en WGS 84 / UTM Zona 19 Sur:")
    add_bullet(doc, "Plano Clave General: Redes MT, SEDs y Catastro Urbano (Escala 1:2,500)", bold_prefix="PL-01: ")
    add_bullet(doc, "Trazo y Perfil Longitudinal de Línea Primaria 10 kV (Escala H: 1:2000, V: 1:200)", bold_prefix="PL-02: ")
    add_bullet(doc, "Detalle Electromecánico de Subestaciones Aéreas Biposte (SAB 50 y 100 kVA, Escala 1:50)", bold_prefix="PL-03: ")
    add_bullet(doc, "Red de Distribución Secundaria 380/220 V y Alumbrado Público (Escala 1:1,000)", bold_prefix="PL-04: ")
    add_bullet(doc, "Detalles Típicos de Armados BT, Puestas a Tierra y Acometidas (Escala 1:25)", bold_prefix="PL-05: ")

    figuras_map = [
        ("01_superposicion_ortofoto_completa.png", "Figura 7.1: Superposición ortofotogramétrica y delimitación de manzanas catastrales en Limbani."),
        ("02_modelo_autocad_completo.png", "Figura 7.2: Modelo geométrico y base catastral vectorial en formato CAD/DXF."),
        ("07_redes_electricas_detalladas_catastro.png", "Figura 7.3: Plano General de Redes Eléctricas, Postería CAC y Subestaciones Aéreas Biposte georreferenciadas en Limbani (WGS 84 Z19S)."),
        ("03_zoom_sector_norte_hidroelectrica.png", "Figura 7.4: Sector Norte: Casa de máquinas MCH Limbani (200 kW) y cobertura de SED-01."),
        ("04_zoom_sector_centro_plaza_puno.png", "Figura 7.5: Sector Centro: Plaza de Armas de Limbani y cobertura de SED-02."),
        ("05_zoom_sector_confluencia_estadio.png", "Figura 7.6: Sector de confluencia fluvial y área de expansión recreacional/deportiva."),
        ("06_zoom_sector_sur_piscina_salida.png", "Figura 7.7: Sector Sur: Complejo recreacional, piscina y cobertura de SED-03.")
    ]

    for fname, pie in figuras_map:
        fpath = os.path.join(fig_dir, fname)
        if os.path.exists(fpath):
            p_f = doc.add_paragraph()
            p_f.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_f.paragraph_format.space_before = Pt(10)
            p_f.paragraph_format.space_after = Pt(2)
            p_f.add_run().add_picture(fpath, width=Inches(6.0))
            
            p_pie_f = doc.add_paragraph()
            p_pie_f.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_pie_f.paragraph_format.space_after = Pt(12)
            r_pie_f = p_pie_f.add_run(pie)
            r_pie_f.font.italic = True
            r_pie_f.font.size = Pt(9)
            r_pie_f.font.color.rgb = RGBColor(80, 80, 80)

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO VIII: CONCLUSIONES, RECOMENDACIONES Y BIBLIOGRAFÍA
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO VIII: CONCLUSIONES, RECOMENDACIONES Y BIBLIOGRAFÍA")
    add_heading_2(doc, "8.1 Conclusiones Técnicas")
    add_bullet(doc, "La MCH Limbani con turbina Michell-Banki (200 kW netos) abastece la totalidad de la demanda urbana (MD = 181.80 kW coincidente, 90.9% de utilización) con una reserva del 9.1%.", bold_prefix="1. Suficiencia Energética: ")
    add_bullet(doc, "Caída de tensión en línea de 10 kV de apenas 0.504% (límite 5.0%) y en baja tensión de 3.82% (límite 5.0%), cumpliendo holgadamente la NTCSE.", bold_prefix="2. Calidad de Tensión: ")
    add_bullet(doc, "Pérdidas Joule en línea primaria de sólo 1.05 kW (0.52% de la potencia generada) gracias al uso del nivel de 10 kV.", bold_prefix="3. Eficiencia Técnica: ")
    add_bullet(doc, "Diseño electromecánico corregido por altitud ka = 1.28 (3,050 msnm) y cargas mecánicas para Zona 2 (viento 90 km/h, -5 °C a +35 °C).", bold_prefix="4. Adaptación Normativa: ")
    add_bullet(doc, "Resistencia de puesta a tierra en subestaciones de 8.14 Ω con bentonita sódica (cumple norma <= 10.0 Ω).", bold_prefix="5. Seguridad Operativa: ")
    add_bullet(doc, "Presupuesto total estimado S/. 1,305,876.26 con un plazo de ejecución de 120 días calendario.", bold_prefix="6. Presupuesto y Plazo: ")

    add_heading_2(doc, "8.2 Recomendaciones de Operación y Mantenimiento")
    add_bullet(doc, "Inspección trimestral de rodete y álabes directrices contra desgaste erosivo por arenas silíceas del Río Limbani.", bold_prefix="1. Mantenimiento MCH: ")
    add_bullet(doc, "Monitoreo del caudal en meses de estiaje (julio-agosto) y plan de gestión de cargas no prioritarias si fuese necesario.", bold_prefix="2. Control Hidrológico: ")
    add_bullet(doc, "Medición semestral con telurómetro antes de la temporada de tormentas eléctricas (octubre).", bold_prefix="3. Pozos a Tierra: ")
    add_bullet(doc, "Poda periódica de árboles en la servidumbre de 6.0 m de ancho a lo largo de la línea de 10 kV.", bold_prefix="4. Servidumbre MT: ")
    add_bullet(doc, "Inspecciones termográficas anuales en bornes de transformadores y barras de tableros de distribución.", bold_prefix="5. Termografía Infrarroja: ")

    add_heading_2(doc, "8.3 Referencias Bibliográficas y Normativa Oficial")
    add_bullet(doc, "Código Nacional de Electricidad - Suministro 2011 (R.M. N.° 366-2011-MEM/DM).", bold_prefix="[1] MEM: ")
    add_bullet(doc, "Bases para el Diseño de Líneas Primarias (R.D. N.° 018-2003-EM/DGE).", bold_prefix="[2] DGE/MEM: ")
    add_bullet(doc, "Bases para el Diseño de Redes Secundarias con Conductores Autoportantes (R.D. N.° 016-2003-EM/DGE).", bold_prefix="[3] DGE/MEM: ")
    add_bullet(doc, "Especificaciones Técnicas para el Montaje de Líneas y Redes (R.D. N.° 026-2003-EM/DGE).", bold_prefix="[4] DGE/MEM: ")
    add_bullet(doc, "Norma Técnica de Calidad de los Servicios Eléctricos (NTCSE, D.S. N.° 020-97-EM).", bold_prefix="[5] MEM: ")
    add_bullet(doc, "Reglamento de Seguridad y Salud en el Trabajo con Electricidad (RESESATE, R.M. N.° 111-2013-MEM/DM).", bold_prefix="[6] MEM: ")
    add_bullet(doc, "NTP 370.258 (AAAC), NTP 370.254 (CAAI), NTP 339.027 (Postes CAC), NTP 370.002 (Transformadores).", bold_prefix="[7] INACAL: ")
    add_bullet(doc, "IEC 60076 (Power Transformers), IEC 60502 (Cables), IEC 61089 (AAAC).", bold_prefix="[8] IEC: ")
    add_bullet(doc, "Catastro Urbano Oficial y Base Georreferenciada WGS 84 Zona 19 Sur, 2026.", bold_prefix="[9] Municipalidad de Limbani: ")

    doc.save(out_path)
    print(f"[OK] Documento Word generado exitosamente en: {out_path}")
    print(f"[OK] Tamano del archivo generado: {os.path.getsize(out_path)} bytes")

if __name__ == "__main__":
    main()
