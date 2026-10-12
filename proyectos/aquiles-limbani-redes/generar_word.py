#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_word.py
Genera el Expediente Técnico completo en formato Microsoft Word (.docx)
para el proyecto de Electrificación y Redes de Distribución de Limbani (200 kW),
cumpliendo estrictamente con las normas R.D. N° 024-2003-EM/DGE, R.D. N° 023-2003-EM-DGE,
R.D. N° 017-2003-EM/DGE, CNE Suministro 2011 y R.M. N° 091-2002-EM/VME.
"""

import os
import sys
import shutil
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
    run.font.color.rgb = RGBColor(180, 0, 0)
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
    run.font.color.rgb = RGBColor(0, 102, 153)
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
    normas_dir = os.path.join(fig_dir, "normas_dge")
    out_dir = os.path.join(base_dir, "entregables")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "expediente_limbani.docx")
    cadastre_sync_path = r"C:\Users\51949\Downloads\Catastro_Limbani\expediente_electrico\expediente_limbani.docx"

    print("[*] Iniciando generación de Expediente Técnico en formato Word...")
    doc = Document()

    # Configurar márgenes de página
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # -------------------------------------------------------------
    # PORTADA OFICIAL
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
        ("POTENCIA GENERACIÓN: ", "200 kW (MCH Limbani - Michell-Banki / Alternador 380 V)"),
        ("USUARIOS BENEFICIARIOS: ", "587 Lotes Catastrados y 587 Acometidas Domiciliarias Individuales"),
        ("NORMATIVA APLICADA: ", "CNE Suministro 2011, R.D. 024-2003-EM/DGE, R.D. 023-2003-EM-DGE, R.D. 017-2003-EM/DGE")
    ]
    for lbl, val in meta_items:
        r_lbl = p_meta.add_run(lbl)
        r_lbl.font.bold = True
        r_lbl.font.size = Pt(10)
        r_lbl.font.name = 'Arial'
        r_val = p_meta.add_run(val + "\n")
        r_val.font.size = Pt(10)
        r_val.font.name = 'Arial'

    p_pie = doc.add_paragraph()
    p_pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pie.paragraph_format.space_before = Pt(25)
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
    add_p(doc, "Para la concepción del presente proyecto se ha tomado como base territorial y física el Catastro Urbano Oficial Consolidado de Limbani, levantado en el sistema geodésico WGS 84 / UTM Zona 19 Sur, el cual registra con precisión milimétrica un total de 587 lotes catastrados de propiedad oficial y 87 manzanas urbanas, así como la delimitación inalterable del cauce del Río Limbani, Río Chinchalamani y los equipamientos urbanos (Plaza de Armas, Estadio Municipal, Piscina y centros educativos/salud).")

    add_heading_2(doc, "1.2 Alcance y Objeto del Proyecto")
    add_p(doc, "Se precisa que las características técnicas de la Minicentral Hidroeléctrica Limbani (turbina Michell-Banki de 200 kW y alternador síncrono trifásico a 380 V) constituyen parámetros y datos de entrada del suministro eléctrico. El objeto integral del presente expediente comprende:")
    add_bullet(doc, "Subestación Elevadora 250 kVA (0.38 / 10.0 kV, Dyn5) en casa de máquinas.", bold_prefix="1. Transformación Inicial: ")
    add_bullet(doc, "Línea Primaria 10 kV (1,967.87 m / 1.97 km) en conductor desnudo AAAC 35 mm² y 26 postes CAC 12m y 13m.", bold_prefix="2. Transmisión Primaria: ")
    add_bullet(doc, "Tres Subestaciones Aéreas Biposte (SED-01 Norte 50 kVA, SED-02 Centro 100 kVA, SED-03 Sur 100 kVA).", bold_prefix="3. Subestaciones de Distribución: ")
    add_bullet(doc, "Redes Secundarias 380/220 V con 6,206.73 m de cables autoportantes CAAI y 243 postes CAC 8m y 9m concentrados exclusivamente en el casco urbano.", bold_prefix="4. Redes de Distribución: ")
    add_bullet(doc, "Alumbrado Público LED con 166 luminarias de 50 W (flujo nominal 6,500 lm) y control fotocelular individual.", bold_prefix="5. Alumbrado Público: ")
    add_bullet(doc, "587 Acometidas domiciliarias monofásicas (534 cortas <= 15m y 53 largas 15-30m) con cable concéntrico SET 2x4 mm² y cajas L-T.", bold_prefix="6. Acometidas y Medición: ")

    add_heading_2(doc, "1.3 Ubicación Política, Geográfica y Cartografía Territorial")
    add_bullet(doc, "Puno", bold_prefix="Departamento: ")
    add_bullet(doc, "Sandia", bold_prefix="Provincia: ")
    add_bullet(doc, "Limbani", bold_prefix="Distrito: ")
    add_bullet(doc, "Casco urbano consolidado (Barrio Norte, Centro y Barrio Sur)", bold_prefix="Sector beneficiario: ")
    add_bullet(doc, "3,050 m.s.n.m. (rango 2,980 - 3,150 m.s.n.m.)", bold_prefix="Altitud media: ")
    add_bullet(doc, "Este: 425,250 a 425,700 m E | Norte: 8'434,750 a 8'436,650 m N", bold_prefix="Coordenadas UTM (WGS 84 Z19S): ")

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

    add_heading_2(doc, "1.4 Condiciones Ambientales y Climatológicas")
    add_bullet(doc, "-5.0 °C (noches de helada invernal)", bold_prefix="Temperatura mínima extrema: ")
    add_bullet(doc, "+12.0 °C", bold_prefix="Temperatura media anual: ")
    add_bullet(doc, "+35.0 °C (radiación diurna directa)", bold_prefix="Temperatura máxima extrema: ")
    add_bullet(doc, "90.0 km/h (25.0 m/s)", bold_prefix="Velocidad máxima de viento: ")
    add_bullet(doc, "850 mm/año (diciembre a marzo)", bold_prefix="Precipitación pluvial media: ")
    add_bullet(doc, "60 a 75 días de tormenta/año (nivel medio-alto)", bold_prefix="Nivel ceráunico: ")
    add_bullet(doc, "150 a 450 Ω·m (suelo rocoso y arcillo-arenoso)", bold_prefix="Resistividad de terreno: ")

    add_heading_2(doc, "1.5 Descripción de la Fuente: MCH Limbani (200 kW)")
    add_bullet(doc, "Central de pasada sobre el Río Limbani.", bold_prefix="Tipo de central: ")
    add_bullet(doc, "Michell-Banki (flujo transversal o cross-flow). Caudal de diseño Q = 0.55 m³/s, salto neto H = 45.0 m, rendimiento η = 82%.", bold_prefix="Turbina hidráulica: ")
    add_bullet(doc, "Síncrono trifásico sin escobillas, 200 kW (250 kVA a cos φ = 0.80), 380 V, 60 Hz, 1,800 RPM.", bold_prefix="Generador: ")
    add_bullet(doc, "250 kVA, 0.38 / 10.0 kV, Dyn5, ONAN, clase térmica A.", bold_prefix="Transformador Elevador: ")

    add_heading_2(doc, "1.6 Zonificación de Subestaciones y Redes Eléctricas")
    add_p(doc, "En el casco urbano se disponen tres (03) Subestaciones Aéreas Biposte (SAB) con una potencia agregada de 250 kVA:")
    
    t_sed = create_table_styled(doc, 5, 5, [1.4, 1.0, 1.4, 2.2, 0.8])
    h_sd = ["Código SED", "Potencia", "Relación (kV)", "Zona Urbana de Cobertura", "Lotes"]
    for i, h in enumerate(h_sd):
        t_sed.rows[0].cells[i].paragraphs[0].text = h
    style_header_row(t_sed.rows[0])
    
    sed_data = [
        ["SED-01 (Norte)", "50 kVA", "10.0 / 0.38-0.22", "Barrio Norte, Central Hidroeléctrica, Jr. Villa Hermosa", "112"],
        ["SED-02 (Centro)", "100 kVA", "10.0 / 0.38-0.22", "Plaza de Armas, Jr. Progreso, Jr. Lima, Comercio, Salud", "268"],
        ["SED-03 (Sur)", "100 kVA", "10.0 / 0.38-0.22", "Barrio Sur, Estadio Municipal, Piscina, Recreación", "207"],
        ["TOTAL SISTEMA", "250 kVA", "--", "Casco Urbano Consolidado de Limbani", "587"]
    ]
    for r_idx, r_data in enumerate(sed_data):
        row = t_sed.rows[r_idx + 1]
        for c_idx, val in enumerate(r_data):
            row.cells[c_idx].paragraphs[0].text = val
        style_body_row(row, is_even=(r_idx % 2 == 1))
        if "TOTAL" in r_data[0]:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.bold = True

    add_heading_2(doc, "1.7 Base Legal y Normativa Técnica Peruana")
    add_bullet(doc, "Código Nacional de Electricidad - Suministro 2011 (R.M. N.° 366-2011-MEM/DM).", bold_prefix="CNE: ")
    add_bullet(doc, "Soportes Normalizados para Líneas y Redes Primarias para Electrificación Rural (R.D. N.° 024-2003-EM/DGE).", bold_prefix="RD 024-2003: ")
    add_bullet(doc, "Soportes Normalizados para Líneas y Redes Secundarias para Electrificación Rural (R.D. N.° 023-2003-EM-DGE).", bold_prefix="RD 023-2003: ")
    add_bullet(doc, "Alumbrado de Vías Públicas en Áreas Rurales (R.D. N.° 017-2003-EM/DGE).", bold_prefix="RD 017-2003: ")
    add_bullet(doc, "Bases para el Diseño de Líneas Primarias para Electrificación Rural (R.D. N.° 018-2003-EM/DGE).", bold_prefix="RD 018-2003: ")
    add_bullet(doc, "Bases para el Diseño de Redes Secundarias con Conductores Autoportantes (R.D. N.° 016-2003-EM/DGE).", bold_prefix="RD 016-2003: ")
    add_bullet(doc, "Símbolos Gráficos en Electricidad - Sección 9: Retenidas, Puestas a Tierra y Postería (R.M. N.° 091-2002-EM/VME).", bold_prefix="RM 091-2002: ")
    add_bullet(doc, "Norma Técnica de Calidad de los Servicios Eléctricos - NTCSE (D.S. N.° 020-97-EM).", bold_prefix="NTCSE: ")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO II: CÁLCULOS JUSTIFICATIVOS
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO II: CÁLCULOS JUSTIFICATIVOS")

    add_heading_2(doc, "2.1 Estudio de Demanda y Balance Energético")
    add_bullet(doc, "350 W/lote (Norma DGE R.D. 016-2003-EM/DGE)", bold_prefix="Dotación unitaria por vivienda: ")
    add_bullet(doc, "587 predios catastrados de propiedad oficial", bold_prefix="Total usuarios catastrados: ")
    add_bullet(doc, "587 × 0.350 kW = 205.45 kW", bold_prefix="Potencia instalada doméstica: ")
    add_bullet(doc, "0.54 (para más de 500 abonados según DGE)", bold_prefix="Factor de simultaneidad: ")
    add_bullet(doc, "205.45 × 0.54 = 110.94 kW", bold_prefix="Máxima demanda doméstica coincidente: ")
    add_bullet(doc, "166 luminarias LED de 50 W = 8.30 kW (Fs = 1.0)", bold_prefix="Alumbrado Público (AP): ")
    add_bullet(doc, "Municipalidad (4.5 kW) + Centro de Salud (8.0 kW) + Plaza de Armas (3.0 kW) + Estadio Municipal (7.5 kW) + Piscina (5.0 kW) + Colegios (6.5 kW) = 34.50 kW", bold_prefix="Cargas Especiales y Servicios: ")
    
    add_p(doc, "MD_total = 110.94 kW + 8.30 kW + 34.50 kW = 153.74 kW", bold_prefix="Máxima Demanda Coincidente Total del Sistema: ")
    add_p(doc, "S_max = 153.74 / 0.90 = 170.82 kVA (cos φ = 0.90)", bold_prefix="Potencia Aparente Coincidente: ")
    add_p(doc, "Balance frente a la generación de la MCH Limbani (200 kW netos): La demanda de 153.74 kW representa el 76.87% de la capacidad nominal de la turbina Michell-Banki, garantizando una holgada reserva operativa del 23.13% (46.26 kW) para crecimiento vegetativo del distrito.")

    add_heading_2(doc, "2.2 Cálculos Fotométricos de Alumbrado Público (R.D. N° 017-2003-EM/DGE)")
    add_p(doc, "El diseño del sistema de alumbrado público para el casco urbano de Limbani se rige por la norma técnica oficial R.D. N° 017-2003-EM/DGE «Alumbrado de Vías Públicas en Áreas Rurales» y el CNE Suministro:")
    add_bullet(doc, "Vía Tipo Rural / Urbano Secundario Tipo P2 / M5 (ancho medio de vía W = 6.0 m).", bold_prefix="Clasificación de Vías: ")
    add_bullet(doc, "Iluminancia media mínima reglamentaria E_med >= 8.0 lux; Factor de Uniformidad Global Uo >= 0.20.", bold_prefix="Exigencia Normativa: ")
    add_bullet(doc, "Luminaria LED de 50 W, flujo luminoso útil Φ = 6,500 lm, factor de depreciación/mantenimiento fm = 0.81, factor de utilización Cu = 0.38 a interdistancia D = 30.0 m y altura H = 8.0 m.", bold_prefix="Parámetros Fotométricos: ")
    
    add_p(doc, "E_med = (Φ × Cu × fm) / (W × D) = (6,500 × 0.38 × 0.81) / (6.0 × 30.0) = 2,000.7 / 180 = 11.11 lux >= 8.0 lux  (CONFORME)", bold_prefix="Cálculo de Iluminancia Media (Método de los Lúmenes): ")
    add_p(doc, "E_min calculada punto por punto en el vértice más distante = 3.75 lux. Uniformidad: Uo = E_min / E_med = 3.75 / 11.11 = 0.337 >= 0.20  (CONFORME)", bold_prefix="Verificación de Uniformidad: ")

    add_heading_2(doc, "2.3 Cálculos Eléctricos de Acometidas Domiciliarias")
    add_bullet(doc, "Conductor concéntrico bipolar de cobre tipo SET 2 × 4 mm² con aislamiento de polietileno reticulado (XLPE) a 600 V.", bold_prefix="Cable Seleccionado: ")
    add_bullet(doc, "587 usuarios residenciales clasificados en: Acometida Corta (distancia <= 15 m): 534 unidades (longitud media 7.0 m); Acometida Larga (distancia 15 a 30 m): 53 unidades (longitud media 21.0 m). Longitud total de acometidas: 4,604.15 m.", bold_prefix="Población y Tipología: ")
    add_bullet(doc, "I_nom = 350 W / (220 V × 1.0) = 1.59 A. Capacidad admisible de corriente del cable SET 2×4 mm² en aire: I_adm = 35.0 A. Factor de seguridad térmico: FS = 35.0 / 1.59 = 22.0 >> 1.0.", bold_prefix="Capacidad de Corriente: ")
    add_bullet(doc, "Para el caso más desfavorable de acometida larga (L = 30.0 m): ΔV = 2 × I × (R cos φ) × L = 2 × 1.59 × (8.08 × 10^-3) × 30.0 = 0.77 V. Porcentualmente: ΔV% = (0.77 / 220) × 100 = 0.35% << 1.50% admisible por norma DGE.", bold_prefix="Caída de Tensión Crítica: ")

    add_heading_2(doc, "2.4 Cálculos Eléctricos de la Línea Primaria 10 kV")
    add_bullet(doc, "In = P / (√3 × Vn × cos φ) = 200.0 / (√3 × 10.0 × 0.90) = 12.83 A", bold_prefix="Corriente nominal máxima: ")
    add_bullet(doc, "AAAC 35 mm² (NTP 370.258). I_adm = 145.0 A. Factor de seguridad térmico FS = 145.0 / 12.83 = 11.30 >> 1.0.", bold_prefix="Capacidad térmica del conductor: ")
    add_bullet(doc, "ΔV = √3 × In × (R cos φ + X sin φ) × L = 46.14 V (L = 1,967.87 m)", bold_prefix="Caída de tensión absoluta: ")
    add_bullet(doc, "ΔV% = (46.14 / 10,000) × 100 = 0.461% << 5.0% (Ampliamente conforme a NTCSE)", bold_prefix="Caída de tensión porcentual: ")
    add_bullet(doc, "ΔP = 3 × In² × R × L = 3 × (12.83)² × 0.986 × 1.968 = 958 W = 0.96 kW (0.48% de la potencia generada)", bold_prefix="Pérdidas de potencia por efecto Joule: ")

    add_heading_2(doc, "2.5 Cálculos Eléctricos de Redes Secundarias CAAI en Baja Tensión")
    add_bullet(doc, "CAAI autoportante (3×35 + 1×16 + NA 25 mm² troncales; 2×16 + 1×16 + NA 25 mm² ramales).", bold_prefix="Conductor adoptado: ")
    add_bullet(doc, "Para la derivación más desfavorable de la SED-02 en Jr. Progreso (L = 240 m, Ib = 77.94 A): ΔV_BT = 3.82% <= 5.0% (Conforme a norma DGE y NTCSE).", bold_prefix="Caída de tensión máxima en BT: ")

    add_heading_2(doc, "2.6 Cálculo de Sistemas de Puesta a Tierra (Dwight)")
    add_p(doc, "R = (ρ / (2π L)) × [ ln(4L / d) - 1 ]")
    add_p(doc, "Para electrodo Copperweld de 5/8\" × 2.40 m y terreno tratado con bentonita sódica (ρ = 70 Ω·m): R_1 = 25.05 Ω. Con dos varillas en paralelo separadas 3.0 m conectadas con conductor de cobre desnudo de 35 mm²: R_SED = 8.14 Ω <= 10.0 Ω (Conforme a CNE-Suministro). En redes BT: R_BT <= 25.0 Ω.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO III: ESPECIFICACIONES DE MATERIALES
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO III: ESPECIFICACIONES TÉCNICAS DE MATERIALES Y EQUIPOS")
    add_heading_2(doc, "3.1 Conductores Eléctricos")
    add_bullet(doc, "Aleación Al 6201-T81, 7 alambres, diámetro 7.56 mm, carga de rotura 10.5 kN, R_20°C = 0.986 Ω/km, corriente admisible 145 A.", bold_prefix="AAAC 35 mm² (NTP 370.258): ")
    add_bullet(doc, "Fases de aluminio puro con aislamiento XLPE (3×35 mm²), neutro portador de aleación AAAC de 25 mm² y alumbrado 1×16 mm².", bold_prefix="Cable Autoportante CAAI (NTP 370.254): ")
    add_bullet(doc, "Cable concéntrico bipolar fase de cobre recocido y neutro helicoidal concéntrico aislado con XLPE a 600 V.", bold_prefix="Cable de Acometida SET 2×4 mm² (NTP 370.050): ")

    add_heading_2(doc, "3.2 Postes de Concreto Armado Centrifugado (CAC)")
    add_p(doc, "Fabricados según norma técnica peruana NTP 339.027:")
    add_bullet(doc, "CAC 12 m / 300 daN (12 unid), CAC 12 m / 400 daN (6 unid), CAC 13 m / 400 daN (6 unid en SAB) y CAC 13 m / 600 daN (2 unid en cruce fluvial Chinchalamani). Total: 26 postes MT.", bold_prefix="Media Tensión (10 kV): ")
    add_bullet(doc, "CAC 8 m / 200 daN (66 unid), CAC 8 m / 300 daN (38 unid) y CAC 9 m / 300 daN (139 unid). Total: 243 postes BT concentrados en casco urbano.", bold_prefix="Baja Tensión (380/220 V): ")

    add_heading_2(doc, "3.3 Transformadores de Distribución")
    t_trafo = create_table_styled(doc, 7, 4, [2.2, 1.4, 1.4, 1.4])
    h_tr = ["Parámetro", "SED-01 (Norte)", "SED-02 (Centro)", "SED-03 (Sur)"]
    for i, h in enumerate(h_tr):
        t_trafo.rows[0].cells[i].paragraphs[0].text = h
    style_header_row(t_trafo.rows[0])
    
    trafo_data = [
        ["Potencia nominal", "50 kVA", "100 kVA", "100 kVA"],
        ["Relación de transformación", "10,000 / 380-220 V", "10,000 / 380-220 V", "10,000 / 380-220 V"],
        ["Grupo de conexión", "Dyn5 (neutro accesible)", "Dyn5 (neutro accesible)", "Dyn5 (neutro accesible)"],
        ["Refrigeración / Aceite", "ONAN (Mineral libre PCB)", "ONAN (Mineral libre PCB)", "ONAN (Mineral libre PCB)"],
        ["Tensión cortocircuito (Ucc)", "4.0%", "4.5%", "4.5%"],
        ["Nivel de aislamiento (BIL)", "110 kV (3,050 msnm)", "110 kV (3,050 msnm)", "110 kV (3,050 msnm)"]
    ]
    for r_idx, r_data in enumerate(trafo_data):
        row = t_trafo.rows[r_idx + 1]
        for c_idx, val in enumerate(r_data):
            row.cells[c_idx].paragraphs[0].text = val
        style_body_row(row, is_even=(r_idx % 2 == 1))

    add_heading_2(doc, "3.4 Retenidas Mecánicas de Anclaje (CNE Regla 261 / DGE)")
    add_bullet(doc, "Cable de acero grado Siemens Martin de 5/16\" (7 hilos), resistencia a la rotura 27.5 kN, galvanizado pesado.", bold_prefix="Cable de Acero: ")
    add_bullet(doc, "Aislador de porcelana clase ANSI 54-1 (tipo nuez/tracción) instalado a más de 3.0 m de altura sobre el suelo.", bold_prefix="Aislador de Tracción: ")
    add_bullet(doc, "Tubo de PVC rígido color amarillo de 1 1/2\" × 1.80 m para advertencia y protección peatonal.", bold_prefix="Guarda Protectora: ")
    add_bullet(doc, "Varilla de anclaje de F°G° de 5/8\" × 2.0 m con ojo guardacabo y bloque de anclaje CAV 0.50 × 0.50 × 0.20 m empotrado a 1.80 m de profundidad.", bold_prefix="Anclaje de Concreto: ")

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO IV: ESPECIFICACIONES DE MONTAJE
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO IV: ESPECIFICACIONES TÉCNICAS DE MONTAJE ELECTROMECÁNICO")
    add_heading_2(doc, "4.1 Trazo, Replanteo y Georreferenciación")
    add_p(doc, "Se utiliza como base inalterable el Catastro Urbano Oficial de Limbani (WGS 84 Zona 19 Sur). La ubicación de cada poste y subestación respeta estrictamente los anchos de vía, bermas y límites de propiedad privada, eliminando cualquier poste en carreteras periféricas no habitadas.")
    
    add_heading_2(doc, "4.2 Excavación e Izaje de Postes CAC")
    add_bullet(doc, "He = Ht/10 + 0.50 m (1.80 m para postes de 13 m; 1.70 m para 12 m; 1.40 m para 9 m; 1.30 m para 8 m).", bold_prefix="Profundidad reglamentaria: ")
    add_bullet(doc, "Cimentación con solado de concreto simple e=0.15 m y macizo ciclópeo f'c = 140 kg/cm² + 30% piedra en laderas y terrenos rocosos.", bold_prefix="Concreto ciclópeo: ")

    add_heading_2(doc, "4.3 Protocolos de Pruebas Previas a la Puesta en Servicio")
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
        ["02.00", "Línea Primaria 10 kV (1.97 km)", "24.5%", "5.0%", "10.0%", "9.5%", "--"],
        ["03.00", "Subestaciones Biposte (3 SED, 250 kVA)", "21.0%", "--", "6.0%", "12.0%", "3.0%"],
        ["04.00", "Redes Secundarias y Alumbrado (6.21 km CAAI)", "26.0%", "3.0%", "8.0%", "10.0%", "5.0%"],
        ["05.00", "Acometidas y Medición (587 usuarios)", "14.0%", "--", "--", "6.0%", "8.0%"],
        ["06.00", "Pruebas Electromecánicas y Puesta en Servicio", "3.5%", "--", "--", "--", "3.5%"],
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
    add_heading_2(doc, "6.1 Resumen Consolidado de Metrados de Obra")

    t_met = create_table_styled(doc, 14, 4, [0.8, 3.2, 1.2, 1.2])
    h_me = ["Ítem", "Descripción de Partida / Material", "Unidad", "Metrado"]
    for i, h in enumerate(h_me):
        t_met.rows[0].cells[i].paragraphs[0].text = h
    style_header_row(t_met.rows[0])

    metrados_data = [
        ["01.01", "Conductor desnudo de aleación de aluminio AAAC 35 mm² (3 fases)", "m", "5,903.61"],
        ["01.02", "Postes de concreto armado centrifugado CAC 12m y 13m (MT 10 kV)", "unid", "26"],
        ["01.03", "Subestaciones aéreas biposte SAB (50 kVA y 100 kVA, 10/0.38-0.22 kV)", "unid", "3"],
        ["01.04", "Retenidas mecánicas de anclaje para media tensión (cable SM 5/16\")", "unid", "12"],
        ["02.01", "Conductor autoportante CAAI troncal (3x35+1x16+NA25 mm²)", "m", "3,980.15"],
        ["02.02", "Conductor autoportante CAAI ramal (2x16+1x16+NA25 mm²)", "m", "2,226.57"],
        ["02.03", "Postes de concreto armado centrifugado CAC 8m y 9m (BT urbano)", "unid", "243"],
        ["02.04", "Luminarias LED integradas 50 W IP66 con fotocélula y pastoral F°G°", "unid", "166"],
        ["02.05", "Retenidas mecánicas de anclaje para baja tensión (con aislador nuez)", "unid", "48"],
        ["03.01", "Acometidas domiciliarias cortas (L <= 15 m) con cable SET 2x4 mm²", "unid", "534"],
        ["03.02", "Acometidas domiciliarias largas (15 < L <= 30 m) con cable SET 2x4 mm²", "unid", "53"],
        ["03.03", "Cable concéntrico bipolar SET 2x4 mm² para acometidas particulares", "m", "4,604.15"],
        ["03.04", "Cajas portamedidor monofásicas de policarbonato reforzado tipo L-T", "unid", "587"]
    ]
    for r_idx, r_data in enumerate(metrados_data):
        row = t_met.rows[r_idx + 1]
        for c_idx, val in enumerate(r_data):
            row.cells[c_idx].paragraphs[0].text = val
        style_body_row(row, is_even=(r_idx % 2 == 1))

    add_heading_2(doc, "6.2 Presupuesto Referencial de Obra")
    t_pto = create_table_styled(doc, 13, 4, [0.8, 3.2, 1.4, 1.0])
    h_pt = ["Ítem", "Componente de Obra", "Costo Parcial (S/.)", "% Incid."]
    for i, h in enumerate(h_pt):
        t_pto.rows[0].cells[i].paragraphs[0].text = h
    style_header_row(t_pto.rows[0])

    presup = [
        ["01.00", "Obras Preliminares y Trabajos de Campo", "46,200.00", "5.23%"],
        ["02.00", "Línea Primaria en Media Tensión 10.0 kV (1.97 km)", "218,650.00", "24.75%"],
        ["03.00", "Subestaciones Aéreas Biposte (3 SED, 250 kVA)", "186,800.00", "21.14%"],
        ["04.00", "Redes Secundarias 380/220 V y Alumbrado Público", "242,500.00", "27.45%"],
        ["05.00", "Acometidas Domiciliarias y Medición (587 predios)", "135,410.00", "15.33%"],
        ["06.00", "Pruebas Electromecánicas y Puesta en Servicio", "28,000.00", "3.17%"],
        ["07.00", "Plan de Mitigación Ambiental y Seguridad (SST)", "26,000.00", "2.94%"],
        ["--", "COSTO DIRECTO TOTAL (CD)", "883,560.00", "100.00%"],
        ["--", "Gastos Generales (10.00% CD)", "88,356.00", "10.00%"],
        ["--", "Utilidad Empresarial (8.00% CD)", "70,684.80", "8.00%"],
        ["--", "SUBTOTAL", "1,042,600.80", "118.00%"],
        ["--", "Impuesto General a las Ventas (IGV 18.00%)", "187,668.14", "21.24%"],
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
    r_pt1 = p_ptot.add_run("PRESUPUESTO TOTAL DE OBRA: S/. 1,230,268.94\n")
    r_pt1.font.bold = True
    r_pt1.font.size = Pt(12)
    r_pt1.font.color.rgb = RGBColor(180, 0, 0)
    r_pt2 = p_ptot.add_run("Son: Un Millón Doscientos Treinta Mil Doscientos Sesenta y Ocho con 94/100 Soles.")
    r_pt2.font.italic = True
    r_pt2.font.size = Pt(10)

    doc.add_page_break()

    # -------------------------------------------------------------
    # CAPÍTULO VII: RELACIÓN DE PLANOS Y LÁMINAS NORMALIZADAS DGE
    # -------------------------------------------------------------
    add_heading_1(doc, "CAPÍTULO VII: RELACIÓN DE PLANOS Y DISEÑO CATASTRAL")
    add_heading_2(doc, "7.1 Catálogo Oficial de Láminas de Ingeniería")
    add_bullet(doc, "Plano Clave General: Redes MT 10 kV, SEDs, Redes BT CAAI, 587 Acometidas y Catastro Urbano (Escala 1:2,500)", bold_prefix="PL-01: ")
    add_bullet(doc, "Trazo y Perfil Longitudinal MT 10 kV con Catenarias de Conductor AAAC 35 mm² (Escala H: 1:2000, V: 1:200)", bold_prefix="PL-02: ")
    add_bullet(doc, "Detalle Electromecánico Subestaciones SAB (50 y 100 kVA, 10/0.38-0.22 kV, Escala 1:50 / 1:25)", bold_prefix="PL-03: ")
    add_bullet(doc, "Red de Distribución Secundaria CAAI, Alumbrado Público LED 50W y Cajas L-T (Escala 1:1,000)", bold_prefix="PL-04: ")
    add_bullet(doc, "Armados Normalizados DGE (PS-3, PA-3, PR-3, Retenidas, PAT y Acometidas, Escala Indicadas)", bold_prefix="PL-05: ")

    add_heading_2(doc, "7.2 Láminas Oficiales Escaneadas del MINEM / DGE")
    add_p(doc, "En cumplimiento de las resoluciones directorales R.D. N° 024-2003-EM/DGE y R.D. N° 023-2003-EM-DGE, a continuación se presentan los detalles técnicos normalizados que rigen el montaje físico de las redes:")

    laminas_dge = [
        ("rd024_pag_008.jpg", "Figura 7.1: Lámina 004 R.D. N° 024-2003-EM/DGE: Armado de Suspensión PS-3 para Red Primaria Trifásica 10 kV."),
        ("rd024_pag_012.jpg", "Figura 7.2: Lámina 008 R.D. N° 024-2003-EM/DGE: Armado de Ángulo PA-3 para Red Primaria Trifásica 10 kV."),
        ("rd024_pag_024.jpg", "Figura 7.3: Lámina 020 R.D. N° 024-2003-EM/DGE: Armado de Retención PR-3 para Red Primaria Trifásica 10 kV."),
        ("rd024_pag_071.jpg", "Figura 7.4: Lámina 064(1/2) R.D. N° 024-2003-EM/DGE: Subestación Aérea Biposte (SAB) 10 / 0.38-0.22 kV."),
        ("rd024_pag_090.jpg", "Figura 7.5: Lámina 074 R.D. N° 024-2003-EM/DGE: Retenida Simple Inclinada para Redes Eléctricas Rurales."),
        ("rd024_pag_094.jpg", "Figura 7.6: Lámina 077 R.D. N° 024-2003-EM/DGE: Pozo de Puesta a Tierra PAT con Electrodo Vertical."),
        ("rd023_pag_04.jpg", "Figura 7.7: Lámina 001 R.D. N° 023-2003-EM-DGE: Estructura E-1 para Conductor Autoportante CAAI en Red Secundaria."),
        ("rd023_pag_10.jpg", "Figura 7.8: Lámina 007 R.D. N° 023-2003-EM-DGE: Acometida Domiciliaria Monofásica Aérea y Caja Tipo L-T.")
    ]

    for fname, caption in laminas_dge:
        fpath = os.path.join(normas_dir, fname)
        if os.path.exists(fpath):
            p_img_dge = doc.add_paragraph()
            p_img_dge.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img_dge.paragraph_format.space_before = Pt(8)
            p_img_dge.paragraph_format.space_after = Pt(2)
            p_img_dge.add_run().add_picture(fpath, width=Inches(4.5))
            
            p_cap_dge = doc.add_paragraph()
            p_cap_dge.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap_dge.paragraph_format.space_after = Pt(10)
            r_cap = p_cap_dge.add_run(caption)
            r_cap.font.italic = True
            r_cap.font.size = Pt(8.5)
            r_cap.font.color.rgb = RGBColor(80, 80, 80)

    doc.add_page_break()

    add_heading_2(doc, "7.3 Vistas de Inspección Electromecánica en el Catastro Urbano")
    
    figuras_map = [
        ("07_redes_electricas_detalladas_catastro.png", "Figura 7.9: Plano General de Redes Eléctricas, Postería CAC y Subestaciones Aéreas Biposte georreferenciadas en Limbani (WGS 84 Z19S)."),
        ("08_zoom_norte_hidroelectrica_sed01.png", "Figura 7.10: Sector Norte: Casa de máquinas MCH Limbani (200 kW), pórtico elevador y cobertura de SED-01 (50 kVA)."),
        ("09_zoom_centro_plaza_sed02.png", "Figura 7.11: Sector Centro: Plaza de Armas de Limbani, núcleo cívico y cobertura de SED-02 (100 kVA)."),
        ("10_zoom_sur_cruce_estadio_sed03.png", "Figura 7.12: Sector Sur: Cruce fluvial reforzado Río Chinchalamani, Estadio Municipal y cobertura de SED-03 (100 kVA).")
    ]

    for fname, pie in figuras_map:
        fpath = os.path.join(fig_dir, fname)
        if os.path.exists(fpath):
            p_f = doc.add_paragraph()
            p_f.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_f.paragraph_format.space_before = Pt(10)
            p_f.paragraph_format.space_after = Pt(2)
            p_f.add_run().add_picture(fpath, width=Inches(5.8))
            
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
    add_bullet(doc, "La MCH Limbani con turbina Michell-Banki (200 kW netos) abastece la totalidad de la demanda urbana (MD = 153.74 kW coincidente, 76.87% de utilización) con una reserva del 23.13% (46.26 kW).", bold_prefix="1. Suficiencia Energética: ")
    add_bullet(doc, "Caída de tensión en línea de 10 kV de apenas 0.461% (límite 5.0%) y en baja tensión de 3.82% (límite 5.0%), cumpliendo holgadamente la NTCSE.", bold_prefix="2. Calidad de Tensión: ")
    add_bullet(doc, "Las 166 luminarias LED de 50 W cumplen la norma R.D. 017-2003-EM/DGE con una iluminancia media de 11.11 lux (exigido >= 8.0 lux) y uniformidad Uo = 0.337 (exigido >= 0.20).", bold_prefix="3. Alumbrado Público: ")
    add_bullet(doc, "Las 587 acometidas domiciliarias georreferenciadas con cable concéntrico SET 2x4 mm² registran caídas de tensión máximas de 0.35% (límite 1.50%).", bold_prefix="4. Conexión de Usuarios: ")
    add_bullet(doc, "Las retenidas mecánicas siguen rigurosamente el diseño normalizado CNE Regla 261 con cable de acero SM 5/16\", aislador nuez ANSI 54-1 a más de 3.0 m, tubo protector amarillo de 1.80 m y anclaje ciclópeo CAV empotrado a 1.80 m.", bold_prefix="5. Seguridad Mecánica: ")
    add_bullet(doc, "Presupuesto total estimado S/. 1,230,268.94 con un plazo de ejecución de 120 días calendario.", bold_prefix="6. Presupuesto y Plazo: ")

    add_heading_2(doc, "8.2 Recomendaciones de Operación y Mantenimiento")
    add_bullet(doc, "Inspección trimestral de rodete y álabes directrices contra desgaste erosivo por arenas silíceas del Río Limbani.", bold_prefix="1. Mantenimiento MCH: ")
    add_bullet(doc, "Monitoreo del caudal en meses de estiaje (julio-agosto) y plan de gestión de cargas no prioritarias si fuese necesario.", bold_prefix="2. Control Hidrológico: ")
    add_bullet(doc, "Medición semestral con telurómetro antes de la temporada de tormentas eléctricas (octubre).", bold_prefix="3. Pozos a Tierra: ")
    add_bullet(doc, "Poda periódica de árboles en la servidumbre de 6.0 m de ancho a lo largo de la línea de 10 kV.", bold_prefix="4. Servidumbre MT: ")
    add_bullet(doc, "Inspecciones termográficas anuales en bornes de transformadores y barras de tableros de distribución.", bold_prefix="5. Termografía Infrarroja: ")

    add_heading_2(doc, "8.3 Referencias Bibliográficas y Normativa Oficial")
    add_bullet(doc, "Código Nacional de Electricidad - Suministro 2011 (R.M. N.° 366-2011-MEM/DM).", bold_prefix="[1] MEM: ")
    add_bullet(doc, "Soportes Normalizados para Líneas y Redes Primarias para Electrificación Rural (R.D. N.° 024-2003-EM/DGE).", bold_prefix="[2] DGE/MEM: ")
    add_bullet(doc, "Soportes Normalizados para Líneas y Redes Secundarias para Electrificación Rural (R.D. N.° 023-2003-EM-DGE).", bold_prefix="[3] DGE/MEM: ")
    add_bullet(doc, "Alumbrado de Vías Públicas en Áreas Rurales (R.D. N.° 017-2003-EM/DGE).", bold_prefix="[4] DGE/MEM: ")
    add_bullet(doc, "Bases para el Diseño de Líneas Primarias (R.D. N.° 018-2003-EM/DGE).", bold_prefix="[5] DGE/MEM: ")
    add_bullet(doc, "Bases para el Diseño de Redes Secundarias con Conductores Autoportantes (R.D. N.° 016-2003-EM/DGE).", bold_prefix="[6] DGE/MEM: ")
    add_bullet(doc, "Símbolos Gráficos en Electricidad - Sección 9 (R.M. N.° 091-2002-EM/VME).", bold_prefix="[7] DGE/MEM: ")
    add_bullet(doc, "Norma Técnica de Calidad de los Servicios Eléctricos (NTCSE, D.S. N.° 020-97-EM).", bold_prefix="[8] MEM: ")
    add_bullet(doc, "NTP 370.258 (AAAC), NTP 370.254 (CAAI), NTP 339.027 (Postes CAC), NTP 370.002 (Transformadores).", bold_prefix="[9] INACAL: ")
    add_bullet(doc, "Catastro Urbano Oficial y Base Georreferenciada WGS 84 Zona 19 Sur, 2026.", bold_prefix="[10] Municipalidad de Limbani: ")

    doc.save(out_path)
    print(f"[OK] Documento Word generado exitosamente en: {out_path}")
    print(f"[OK] Tamano del archivo generado: {os.path.getsize(out_path)} bytes")

    # Sincronizar en Catastro_Limbani
    try:
        os.makedirs(os.path.dirname(cadastre_sync_path), exist_ok=True)
        shutil.copy2(out_path, cadastre_sync_path)
        print(f"[OK] Sincronizado en Catastro_Limbani: {cadastre_sync_path}")
    except Exception as e:
        print(f"[!] Advertencia al sincronizar en Catastro_Limbani: {e}")

if __name__ == "__main__":
    main()
