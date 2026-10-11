# -*- coding: utf-8 -*-
"""
generar_memoria_descriptiva_pdf.py
Compila la Memoria Descriptiva oficial del proyecto en formato PDF de alta calidad
utilizando ReportLab (A4, encabezados institucionales, numeración dinámica de páginas,
tablas formateadas y diseño editorial de ingeniería).

Autor: Renzo Gabriel Mamani Galindo (Cód. 228447)
Curso: MEC330 - Instalaciones Eléctricas II (FIME - UNA Puno)
Docentes: Ing. Leonidas Vilca Callata & Ing. Marcos José Villanueva Cornejo
"""

import sys
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Canvas de dos pasadas para calcular dinámicamente el número total de páginas
    y estampar encabezados y pies de página institucionales en cada hoja (excepto portada).
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, total_pages):
        # Omitir encabezado y pie en la portada (página 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Encabezado
        self.drawString(2.0 * cm, 28.2 * cm, "UNIVERSIDAD NACIONAL DEL ALTIPLANO — PUNO  |  FIME · MEC330")
        self.drawRightString(A4[0] - 2.0 * cm, 28.2 * cm, "EXPEDIENTE TÉCNICO · MEMORIA DESCRIPTIVA")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(2.0 * cm, 28.0 * cm, A4[0] - 2.0 * cm, 28.0 * cm)

        # Pie de página
        self.line(2.0 * cm, 1.8 * cm, A4[0] - 2.0 * cm, 1.8 * cm)
        self.drawString(2.0 * cm, 1.4 * cm, "L.P. 22.9 kV & SED 100 kVA Chifrón — Capachica  |  Renzo G. Mamani Galindo")
        self.drawRightString(A4[0] - 2.0 * cm, 1.4 * cm, f"Página {self._pageNumber} de {total_pages}")
        self.restoreState()


def build_pdf(output_pdf_path):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.2 * cm
    )

    base_styles = getSampleStyleSheet()

    # Colores temáticos institucionales
    c_primary = colors.HexColor("#1E3A8A")    # Azul institucional oscuro
    c_secondary = colors.HexColor("#0D9488")  # Verde azulado de ingeniería
    c_dark = colors.HexColor("#0F172A")       # Texto principal
    c_muted = colors.HexColor("#475569")      # Texto secundario
    c_accent = colors.HexColor("#D97706")     # Resaltado ámbar
    c_bg_light = colors.HexColor("#F8FAFC")   # Fondo sutil

    # Estilos de párrafos
    univ_style = ParagraphStyle(
        'UnivStyle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        alignment=1, # Centrado
        textColor=c_primary
    )
    fac_style = ParagraphStyle(
        'FacStyle',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        alignment=1,
        textColor=c_muted
    )
    cover_title_style = ParagraphStyle(
        'CoverTitleStyle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=19,
        alignment=1,
        textColor=c_primary
    )
    cover_sub_style = ParagraphStyle(
        'CoverSubStyle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=15,
        alignment=1,
        textColor=c_secondary
    )
    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=c_dark
    )
    meta_val = ParagraphStyle(
        'MetaVal',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark
    )

    h1_style = ParagraphStyle(
        'H1Style',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2Style',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_secondary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    h3_style = ParagraphStyle(
        'H3Style',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=c_dark,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_dark,
        alignment=4, # Justificado
        spaceAfter=5
    )
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=13,
        textColor=c_dark,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )
    math_box_style = ParagraphStyle(
        'MathBoxStyle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=c_primary,
        alignment=1 # Centrado
    )
    th_style = ParagraphStyle(
        'ThStyle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )
    td_center = ParagraphStyle(
        'TdCenter',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10,
        textColor=c_dark,
        alignment=1
    )
    td_left = ParagraphStyle(
        'TdLeft',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10,
        textColor=c_dark,
        alignment=0
    )
    td_right = ParagraphStyle(
        'TdRight',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10,
        textColor=c_dark,
        alignment=2
    )

    story = []

    # =========================================================================
    # PORTADA OFICIAL
    # =========================================================================
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("UNIVERSIDAD NACIONAL DEL ALTIPLANO — PUNO", univ_style))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("FACULTAD DE INGENIERÍA MECÁNICA ELÉCTRICA, ELECTRÓNICA Y SISTEMAS", fac_style))
    story.append(Paragraph("ESCUELA PROFESIONAL DE INGENIERÍA MECÁNICA ELÉCTRICA", fac_style))
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="90%", thickness=1.5, color=c_primary, spaceBefore=2, spaceAfter=8))
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("CURSO: MEC330 — INSTALACIONES ELÉCTRICAS II", cover_sub_style))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("EXPEDIENTE TÉCNICO DE INGENIERÍA", ParagraphStyle(
        'SubtitleExp', parent=base_styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=15, alignment=1, textColor=c_muted
    )))
    story.append(Spacer(1, 6 * mm))

    # Caja del Título
    titulo_texto = (
        "«INSTALACIÓN DEL SISTEMA DE ELECTRIFICACIÓN RURAL MEDIANTE "
        "LÍNEA PRIMARIA EN MEDIA TENSIÓN 22.9 kV Y SUBESTACIÓN DE DISTRIBUCIÓN "
        "BIPOSTE 100 kVA PARA EL SECTOR CHIFRÓN, DISTRITO DE CAPACHICA — PUNO»"
    )
    story.append(Paragraph(titulo_texto, cover_title_style))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("CAPÍTULO I: MEMORIA DESCRIPTIVA", ParagraphStyle(
        'Cap1', parent=base_styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1, textColor=c_secondary
    )))
    story.append(Spacer(1, 15 * mm))

    # Tabla de Metadatos del Proyecto
    meta_data = [
        [Paragraph("Docentes del Curso:", meta_label), Paragraph("Ing. Leonidas Vilca Callata<br/>Ing. Marcos José Villanueva Cornejo", meta_val)],
        [Paragraph("Estudiante Proyectista:", meta_label), Paragraph("Renzo Gabriel Mamani Galindo", meta_val)],
        [Paragraph("Código Universitario:", meta_label), Paragraph("228447", meta_val)],
        [Paragraph("Ciclo y Semestre:", meta_label), Paragraph("IX Ciclo  |  Semestre Académico 2026-II", meta_val)],
        [Paragraph("Ubicación del Proyecto:", meta_label), Paragraph("Sector Chifrón, Península de Capachica, Puno (3,817 – 3,924 msnm)", meta_val)],
        [Paragraph("Punto de Conexión MT:", meta_label), Paragraph("Red Troncal 22.9 kV Electro Puno S.A.A. (Alimentador TMT000012389)", meta_val)],
        [Paragraph("Población Beneficiaria:", meta_label), Paragraph("43 Viviendas Censadas  |  78 Abonados Proyectados (Año 20)", meta_val)],
        [Paragraph("Potencia SED Seleccionada:", meta_label), Paragraph("100 kVA (22.9 / 0.38 - 0.22 kV, trifásico, conexión Dyn5)", meta_val)],
        [Paragraph("Fecha de Elaboración:", meta_label), Paragraph("Octubre de 2026", meta_val)],
    ]
    t_meta = Table(meta_data, colWidths=[5.5 * cm, 11.0 * cm])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_primary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15 * mm))
    story.append(Paragraph("PUNO — PERÚ<br/>2026", ParagraphStyle(
        'PieU', parent=base_styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, alignment=1, textColor=c_primary
    )))
    story.append(PageBreak())

    # =========================================================================
    # CAPÍTULO I: MEMORIA DESCRIPTIVA
    # =========================================================================
    story.append(Paragraph("CAPÍTULO I: MEMORIA DESCRIPTIVA", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=1, spaceAfter=8))

    # 1. GENERALIDADES
    story.append(Paragraph("1. GENERALIDADES", h2_style))
    story.append(Paragraph("1.1 Introducción", h3_style))
    story.append(Paragraph(
        "El presente proyecto corresponde al diseño definitivo a nivel de ingeniería de detalle de la "
        "<b>Línea Primaria en Media Tensión (22.9 kV, 3Ø)</b> y la <b>Subestación de Distribución Proyectada (SED Biposte, 100 kVA)</b>, "
        "destinada a suministrar energía eléctrica continua, eficiente y segura a las viviendas e infraestructura comunal del "
        "sector <b>Chifrón</b>, ubicado en la península de Capachica, provincia y departamento de Puno.", body_style
    ))
    story.append(Paragraph(
        "El desarrollo del presente expediente técnico se enmarca en la asignatura de especialidad <b>MEC330 — Instalaciones Eléctricas II</b>, "
        "dictada en la Escuela Profesional de Ingeniería Mecánica Eléctrica (FIME) de la Universidad Nacional del Altiplano (UNA Puno), "
        "bajo la cátedra de los ingenieros <b>Leonidas Vilca Callata</b> y <b>Marcos José Villanueva Cornejo</b>.", body_style
    ))

    story.append(Paragraph("1.2 Objetivos del Proyecto", h3_style))
    story.append(Paragraph("• <b>Suministro eléctrico integral:</b> Dotar de servicio eléctrico continuo y de calidad a las <b>43 familias censadas</b> en el sector Chifrón (denominadas C1 a C43), cubriendo consumos domiciliarios, alumbrado público y soporte a pequeños emprendimientos rurales.", bullet_style))
    story.append(Paragraph("• <b>Cumplimiento normativo estricto:</b> Aplicar las prescripciones técnicas del <i>Código Nacional de Electricidad (CNE Suministro 2011)</i>, la <i>Norma DGE 'Bases para el Diseño de Líneas y Redes Primarias para Electrificación Rural' (R.D. 018-2003-EM/DGE)</i> y las especificaciones técnicas de <i>Electro Puno S.A.A.</i>", bullet_style))
    story.append(Paragraph("• <b>Optimización electromecánica:</b> Dimensionar con precisión mecánica y eléctrica los conductores de aleación de aluminio AAAC de 35 mm², los esfuerzos en postes de concreto armado centrifugado (C.A.C.), y las distancias de seguridad vertical ante las rigurosas condiciones climáticas del Altiplano peruano (>3,800 msnm).", bullet_style))

    # 2. UBICACIÓN GEOGRÁFICA Y POLÍTICA
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("2. UBICACIÓN GEOGRÁFICA Y POLÍTICA", h2_style))
    story.append(Paragraph(
        "El proyecto se ubica geográficamente en la vertiente oriental de la península de Capachica, a orillas del Lago Titicaca:", body_style
    ))
    story.append(Paragraph("• <b>Departamento:</b> Puno", bullet_style))
    story.append(Paragraph("• <b>Provincia:</b> Puno", bullet_style))
    story.append(Paragraph("• <b>Distrito:</b> Capachica", bullet_style))
    story.append(Paragraph("• <b>Sector:</b> Chifrón", bullet_style))
    story.append(Paragraph("• <b>Altitud de Trabajo:</b> 3,817.04 msnm a 3,924.17 msnm (Cota media de cálculo: 3,850 msnm).", bullet_style))
    story.append(Paragraph("• <b>Sistema de Coordenadas:</b> UTM WGS-84, Zona 19 Sur.", bullet_style))

    story.append(Paragraph("Coordenadas Clave del Trazo:", h3_style))
    story.append(Paragraph("• <b>Punto de Derivación (E-01):</b> Este: 412,606.01 m E  |  Norte: 8,270,712.24 m N  |  Cota: 3,924.17 msnm", bullet_style))
    story.append(Paragraph("• <b>Subestación Proyectada (E-04):</b> Este: 412,759.20 m E  |  Norte: 8,270,976.22 m N  |  Cota: 3,839.56 msnm", bullet_style))
    story.append(Paragraph("• <b>Fin de Traza Primaria (E-09):</b> Este: 412,659.90 m E  |  Norte: 8,271,446.51 m N  |  Cota: 3,824.61 msnm", bullet_style))

    story.append(Paragraph("Vías de Acceso:", h3_style))
    story.append(Paragraph(
        "Desde la ciudad de Puno se accede por la carretera asfaltada Puno – Paucarcolla – Capachica (62.0 km), y desde el cercado distrital "
        "de Capachica hasta el sector Chifrón mediante una trocha afirmada transitable de 4.5 km, idónea para el traslado de grúas, "
        "postes de 12 y 13 metros, y transformadores.", body_style
    ))

    # 3. CONDICIONES CLIMÁTICAS Y AMBIENTALES
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("3. CONDICIONES CLIMÁTICAS Y AMBIENTALES DE DISEÑO", h2_style))
    story.append(Paragraph(
        "Conforme a la zonificación del CNE Suministro 2011 y las Normas DGE para zonas de gran altitud (>3,000 msnm):", body_style
    ))
    story.append(Paragraph("• <b>Zona Meteorológica:</b> Zona 2 / 3 (Altiplano > 3,000 msnm).", bullet_style))
    story.append(Paragraph("• <b>Temperatura Máxima Absoluta:</b> +35.0 °C", bullet_style))
    story.append(Paragraph("• <b>Temperatura Mínima Absoluta:</b> -15.0 °C", bullet_style))
    story.append(Paragraph("• <b>Temperatura Media Anual (EDS / Templado):</b> +15.0 °C", bullet_style))
    story.append(Paragraph("• <b>Velocidad Máxima de Viento de Diseño:</b> 75.0 km/h (20.83 m/s) a 10 m de altura.", bullet_style))
    story.append(Paragraph("• <b>Manguito de Hielo:</b> 6.0 mm (a -5.0 °C con viento de 37.5 km/h).", bullet_style))
    story.append(Paragraph("• <b>Nivel de Contaminación Ambiental:</b> Ligero a Medio (entorno rural no salino ni industrial).", bullet_style))
    story.append(Paragraph("• <b>Nivel Isoceráunico:</b> 40 a 50 días tormenta/año (justifica uso obligatorio de pararrayos ZnO 21 kV en derivación y subestación).", bullet_style))

    # 4. PUNTO DE DISEÑO Y ALIMENTACIÓN ELÉCTRICA
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("4. PUNTO DE DISEÑO Y ALIMENTACIÓN ELÉCTRICA", h2_style))
    story.append(Paragraph(
        "La alimentación eléctrica proviene de la infraestructura de media tensión de la concesionaria <b>Electro Puno S.A.A.</b>, "
        "identificada y contrastada en el geovisor oficial <b>GISEM de OSINERGMIN</b>:", body_style
    ))
    story.append(Paragraph("• <b>Código de Alimentador / Tramo:</b> Alimentador Chifrón — Código TMT000012389 / TMT001847370.", bullet_style))
    story.append(Paragraph("• <b>Tensión Nominal:</b> 22.9 kV (Trifásica, 60 Hz).", bullet_style))
    story.append(Paragraph(
        "• <b>Estructura de Derivación (E-01):</b> Poste C.A.C. 12m/400 daN con armado de retención PR-1, equipado con seccionamiento "
        "mediante tres (03) cortacircuitos fusibles cut-out de 27 kV, 100 A, 150 kV BIL y tres (03) pararrayos de óxido de zinc (ZnO) "
        "de 21 kV, 10 kA, garantizando seccionamiento y protección ante sobretensiones atmosféricas.", bullet_style
    ))

    story.append(PageBreak())

    # 5. ESTUDIO DE MERCADO, PROYECCIÓN Y CUADRO DE CARGAS
    story.append(Paragraph("5. ESTUDIO DE DEMANDA Y CUADRO OFICIAL DE CARGAS", h2_style))
    story.append(Paragraph(
        "El dimensionamiento de la carga y la potencia del transformador se rigen estrictamente por la metodología oficial del docente "
        "del curso <i>MEC330 — Instalaciones Eléctricas II</i> (Ing. Leonidas Vilca Callata e Ing. Marcos Villanueva Cornejo):", body_style
    ))

    story.append(Paragraph("5.1 Parámetros Base de Partida", h3_style))
    story.append(Paragraph("• <b>Usuarios Iniciales (NU<sub>0</sub>):</b> 43 viviendas (Censo georreferenciado de abonados C1 a C43).", bullet_style))
    story.append(Paragraph("• <b>Tasa de Crecimiento Anual (TC):</b> 3.0 % anual (0.03).", bullet_style))
    story.append(Paragraph("• <b>Periodo de Proyección (n):</b> 20 años (Horizonte de diseño: 2026 – 2046).", bullet_style))
    story.append(Paragraph("• <b>Factor de Crecimiento Compuesto:</b> (1 + TC)<sup>n</sup> = (1 + 0.03)<sup>20</sup> = <b>1.80611</b>.", bullet_style))
    story.append(Paragraph("• <b>Calificación Eléctrica Asignada:</b> 0.90 kW / usuario.", bullet_style))
    story.append(Paragraph("• <b>Tensión de Distribución BT:</b> Sistema trifásico 380/220 V (Dyn5, 60 Hz).", bullet_style))
    story.append(Paragraph("• <b>Factor de Potencia de Diseño:</b> cos φ = 0.90.", bullet_style))
    story.append(Paragraph("• <b>Alumbrado Público:</b> Lámparas LED normalizadas de 60 W (0.06 kW).", bullet_style))

    story.append(Paragraph("5.2 Algoritmo de Cálculo Paso a Paso", h3_style))
    f_box = [
        [Paragraph("1. Proyección de Usuarios:", meta_label), Paragraph("NU<sub>f</sub> = NU<sub>0</sub> · (1 + TC)<sup>n</sup> = 43 · 1.80611 = 77.66 → <b>78 usuarios</b>", meta_val)],
        [Paragraph("2. Servicio Particular:", meta_label), Paragraph("Potencia<sub>part</sub> = NU<sub>f</sub> · Calificación = 78 · 0.90 kW = <b>70.20 kW</b>", meta_val)],
        [Paragraph("3. Alumbrado Público (Lámparas):", meta_label), Paragraph("N° lum = (3.3 · NU<sub>f</sub>) / 18 = (3.3 · 78) / 18 = 14.30 → <b>15 luminarias</b>", meta_val)],
        [Paragraph("4. Potencia Alumbrado:", meta_label), Paragraph("Potencia<sub>alum</sub> = N° lum · 0.06 kW = 15 · 0.06 kW = <b>0.90 kW</b>", meta_val)],
        [Paragraph("5. Demanda Máxima Total Activa:", meta_label), Paragraph("Total<sub>kW</sub> = Potencia<sub>part</sub> + Potencia<sub>alum</sub> = 70.20 + 0.90 = <b>71.10 kW</b>", meta_val)],
        [Paragraph("6. Corriente Nominal Trifásica de Servicio:", meta_label), Paragraph("I<sub>3φ</sub> = (Total<sub>kW</sub> · 1000) / (√3 · V<sub>L</sub> · cos φ) = (71.10 · 1000) / (√3 · 380 · 0.90) = <b>120.03 A</b>", meta_val)],
        [Paragraph("7. Potencia Aparente Requerida:", meta_label), Paragraph("Potencia<sub>kVA</sub> = Total<sub>kW</sub> / cos φ = 71.10 / 0.90 = <b>79.00 kVA</b>", meta_val)],
        [Paragraph("8. Selección del Transformador:", meta_label), Paragraph("Comercial normalizado inmediato superior: <b>S<sub>nom</sub> = 100 kVA (22.9 / 0.38 - 0.22 kV)</b>", meta_val)],
    ]
    t_fbox = Table(f_box, colWidths=[5.5 * cm, 11.5 * cm])
    t_fbox.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_fbox)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("5.3 Cuadro Oficial de Cargas y Máxima Demanda por Circuitos", h3_style))
    tabla_cargas_data = [
        [
            Paragraph("Circuito", th_style),
            Paragraph("Sector / Zona de Red", th_style),
            Paragraph("NU<sub>0</sub><br/>(2026)", th_style),
            Paragraph("NU<sub>f</sub><br/>(2046)", th_style),
            Paragraph("Pot. Part.<br/>(kW)", th_style),
            Paragraph("N° Lum.<br/>(AP)", th_style),
            Paragraph("Pot. AP<br/>(kW)", th_style),
            Paragraph("Demanda<br/>Total (kW)", th_style),
            Paragraph("Corriente<br/>I<sub>3φ</sub> (A)", th_style)
        ],
        [
            Paragraph("<b>C-1</b>", td_center),
            Paragraph("Sector Troncal Norte + Lote C31 (Playa y Muelle)", td_left),
            Paragraph("31", td_center),
            Paragraph("56", td_center),
            Paragraph("50.40", td_right),
            Paragraph("10", td_center),
            Paragraph("0.60", td_right),
            Paragraph("51.00", td_right),
            Paragraph("86.13", td_right)
        ],
        [
            Paragraph("<b>C-2</b>", td_center),
            Paragraph("Carretera al Fondo / Pasaje Sur", td_left),
            Paragraph("12", td_center),
            Paragraph("22", td_center),
            Paragraph("19.80", td_right),
            Paragraph("5", td_center),
            Paragraph("0.30", td_right),
            Paragraph("20.10", td_right),
            Paragraph("33.95", td_right)
        ],
        [
            Paragraph("<b>TOTAL</b>", td_center),
            Paragraph("<b>Red Completa Chifrón (2 Circuitos BT)</b>", td_left),
            Paragraph("<b>43</b>", td_center),
            Paragraph("<b>78</b>", td_center),
            Paragraph("<b>70.20</b>", td_right),
            Paragraph("<b>15</b>", td_center),
            Paragraph("<b>0.90</b>", td_right),
            Paragraph("<b>71.10</b>", td_right),
            Paragraph("<b>120.03</b>", td_right)
        ]
    ]
    t_cargas = Table(tabla_cargas_data, colWidths=[1.5*cm, 4.3*cm, 1.4*cm, 1.4*cm, 2.0*cm, 1.4*cm, 1.6*cm, 2.0*cm, 1.8*cm])
    t_cargas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, c_primary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cargas)
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        "<i>Nota Técnica de Reserva: Con la potencia nominal estandarizada de 100 kVA, el factor de utilización al año 20 es de "
        "79.00 / 100 = 79.0%, dejando una reserva operativa del 21.0% para contingencias y sobrecargas de arranque de motores rurales.</i>",
        ParagraphStyle('NotaRes', parent=base_styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=11, textColor=c_muted)
    ))

    # 6. DESCRIPCIÓN TÉCNICA DE LA LÍNEA PRIMARIA (22.9 kV)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("6. DESCRIPCIÓN TÉCNICA DE LA LÍNEA PRIMARIA (22.9 kV)", h2_style))
    story.append(Paragraph("6.1 Características del Trazado y Vano", h3_style))
    story.append(Paragraph("• <b>Longitud Total de la Troncal:</b> 816.60 metros (0.817 km).", bullet_style))
    story.append(Paragraph("• <b>Número de Estructuras:</b> 9 postes (E-01 a E-09).", bullet_style))
    story.append(Paragraph("• <b>Vano Promedio:</b> 102.08 m (Vano mínimo: 79.81 m entre E-07 y E-08; Vano máximo: 115.59 m entre E-05 y E-06).", bullet_style))
    story.append(Paragraph("• <b>Perfil del Terreno:</b> Descenso abrupto desde la cumbre en E-01 (cota 3,924.17 msnm) hasta la subestación E-04 (cota 3,839.56 msnm), con pendiente media del 27.7%, regularizándose luego en el sector plano del caserío.", bullet_style))

    story.append(Paragraph("6.2 Conductor Seleccionado (AAAC 35 mm²)", h3_style))
    story.append(Paragraph(
        "Se seleccionó conductor desnudo de aleación de aluminio <b>AAAC 35 mm²</b> (All Aluminium Alloy Conductor), "
        "conforme a las especificaciones DGE para electrificación rural en zonas de altura:", body_style
    ))
    story.append(Paragraph("• <b>Sección Nominal / Real:</b> 35 mm² / 34.36 mm² (7 hilos de Ø 2.50 mm).", bullet_style))
    story.append(Paragraph("• <b>Diámetro Exterior:</b> 7.50 mm  |  <b>Peso Propio:</b> 0.0945 kg/m.", bullet_style))
    story.append(Paragraph("• <b>Tiro de Rotura Nominal:</b> 1,040.0 kgf (10.20 kN).", bullet_style))
    story.append(Paragraph("• <b>Módulo de Elasticidad:</b> 6,000 kg/mm²  |  <b>Coeficiente de Dilatación:</b> 23.0 × 10<sup>-6</sup> °C<sup>-1</sup>.", bullet_style))
    story.append(Paragraph("• <b>Resistencia Eléctrica (20 °C):</b> 0.963 Ω/km  |  <b>Resistencia a 50 °C:</b> 0.986 Ω/km.", bullet_style))
    story.append(Paragraph("• <b>Reactancia Inductiva (DMG 1.20 m):</b> 0.385 Ω/km.", bullet_style))

    story.append(PageBreak())

    story.append(Paragraph("6.3 Soportes de Concreto Armado Centrifugado (C.A.C.)", h3_style))
    story.append(Paragraph(
        "Los postes empleados son de concreto armado centrifugado (C.A.C.), conicidad 1.5%, acabado liso y alta durabilidad contra la helada altiplánica:", body_style
    ))
    story.append(Paragraph("• <b>Postes de Suspensión / Alineamiento:</b> C.A.C. 12 m / 300 daN (E-02, E-03, E-07).", bullet_style))
    story.append(Paragraph("• <b>Postes de Ángulo y Anclaje:</b> C.A.C. 12 m / 400 daN (E-01, E-05, E-06, E-08, E-09).", bullet_style))
    story.append(Paragraph("• <b>Estructura Biposte de Subestación:</b> 02 Postes C.A.C. 13 m / 400 daN (E-04).", bullet_style))
    story.append(Paragraph("• <b>Profundidad de Empotramiento:</b> t = 0.10·H + 0.20 m (1.40 m para postes de 12 m; 1.50 m para postes de 13 m).", bullet_style))

    story.append(Paragraph("6.4 Aislamiento, Ferretería y Armados Normalizados DGE", h3_style))
    story.append(Paragraph(
        "Toda la ferretería galvanizada en caliente bajo norma ASTM A-153 y los armados normalizados DGE se corresponden con las láminas del archivo "
        "oficial <code>laminas_de_detalle.dwg</code>:", body_style
    ))
    story.append(Paragraph("• <b>Armado PS-1 (Suspensión):</b> Cruceta angular F°G° 2.0 m, aisladores poliméricos/pin de silicona clase 25 kV con línea de fuga extendida (>720 mm) apta para altitud de 3,850 msnm.", bullet_style))
    story.append(Paragraph("• <b>Armado PA-1 (Alineamiento / Ángulo Leve):</b> Estructura con cruceta reforzada y aisladores tipo pin ANSI 56-3 con espiga de 1 3/8'' × 10''.", bullet_style))
    story.append(Paragraph("• <b>Armado PR-1 (Retención / Anclaje Terminal):</b> Estructura de anclaje con aisladores poliméricos de suspensión y grapas pistolas de aleación de aluminio.", bullet_style))
    story.append(Paragraph("• <b>Armado SAB-1 (Subestación Aérea Biposte):</b> Montaje en dos postes de 13 m con plataforma de perfiles UPN para transformador de 100 kVA, cortacircuitos cut-out 27 kV, pararrayos ZnO 21 kV y tablero general BT.", bullet_style))
    story.append(Paragraph("• <b>Sistema de Puesta a Tierra (PAT-3):</b> Electrodo vertical de cobre 5/8'' × 2.40 m, conductor de cobre desnudo 35 mm², conectores de compresión y bentonita sódica (R<sub>pat</sub> ≤ 10 Ω en SED y ≤ 15 Ω en derivación).", bullet_style))

    # 7. RESUMEN DE LA PLANILLA DE ESTRUCTURAS
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("7. PLANILLA OFICIAL DE ESTRUCTURAS DE LA LÍNEA PRIMARIA", h2_style))
    story.append(Paragraph(
        "Distribución espacial y funcional de las 9 estructuras a lo largo de la traza de 816.60 m:", body_style
    ))

    tabla_est_data = [
        [
            Paragraph("N°", th_style),
            Paragraph("Poste", th_style),
            Paragraph("Progresiva<br/>(m)", th_style),
            Paragraph("Cota<br/>(msnm)", th_style),
            Paragraph("Poste C.A.C.<br/>(m / daN)", th_style),
            Paragraph("Armado<br/>DGE", th_style),
            Paragraph("Función en la Red y Accesorios", th_style)
        ],
        [
            Paragraph("1", td_center),
            Paragraph("<b>E-01</b>", td_center),
            Paragraph("0+000.00", td_center),
            Paragraph("3,924.17", td_right),
            Paragraph("12 / 400", td_center),
            Paragraph("<b>PR-1</b>", td_center),
            Paragraph("Derivación con cut-out 27 kV y pararrayos ZnO (Electro Puno)", td_left)
        ],
        [
            Paragraph("2", td_center),
            Paragraph("<b>E-02</b>", td_center),
            Paragraph("0+105.00", td_center),
            Paragraph("3,895.00", td_right),
            Paragraph("12 / 300", td_center),
            Paragraph("<b>PS-1</b>", td_center),
            Paragraph("Suspensión en fuerte bajada de ladera rocosa", td_left)
        ],
        [
            Paragraph("3", td_center),
            Paragraph("<b>E-03</b>", td_center),
            Paragraph("0+210.00", td_center),
            Paragraph("3,865.00", td_right),
            Paragraph("12 / 300", td_center),
            Paragraph("<b>PS-1</b>", td_center),
            Paragraph("Suspensión y transición de pendiente hacia subestación", td_left)
        ],
        [
            Paragraph("4", td_center),
            Paragraph("<b>E-04</b>", td_center),
            Paragraph("0+305.21", td_center),
            Paragraph("3,839.56", td_right),
            Paragraph("13 / 400 (x2)", td_center),
            Paragraph("<b>SAB-1</b>", td_center),
            Paragraph("<b>Subestación Biposte (Trafo 100 kVA 22.9/0.38-0.22 kV)</b>", td_left)
        ],
        [
            Paragraph("5", td_center),
            Paragraph("<b>E-05</b>", td_center),
            Paragraph("0+402.43", td_center),
            Paragraph("3,817.04", td_right),
            Paragraph("12 / 400", td_center),
            Paragraph("<b>PA-1</b>", td_center),
            Paragraph("Vértice de ángulo (-36.06°) con retenida inclinada simple", td_left)
        ],
        [
            Paragraph("6", td_center),
            Paragraph("<b>E-06</b>", td_center),
            Paragraph("0+518.02", td_center),
            Paragraph("3,827.27", td_right),
            Paragraph("12 / 400", td_center),
            Paragraph("<b>PA-1</b>", td_center),
            Paragraph("Vértice de ángulo (+31.35°) con retenida contraviento", td_left)
        ],
        [
            Paragraph("7", td_center),
            Paragraph("<b>E-07</b>", td_center),
            Paragraph("0+628.53", td_center),
            Paragraph("3,824.61", td_right),
            Paragraph("12 / 300", td_center),
            Paragraph("<b>PS-1</b>", td_center),
            Paragraph("Alineamiento y suspensión a lo largo de calle principal", td_left)
        ],
        [
            Paragraph("8", td_center),
            Paragraph("<b>E-08</b>", td_center),
            Paragraph("0+708.34", td_center),
            Paragraph("3,824.61", td_right),
            Paragraph("12 / 300", td_center),
            Paragraph("<b>PA-1</b>", td_center),
            Paragraph("Ángulo de desvío suave (+32.95°) con retenida", td_left)
        ],
        [
            Paragraph("9", td_center),
            Paragraph("<b>E-09</b>", td_center),
            Paragraph("0+816.60", td_center),
            Paragraph("3,824.61", td_right),
            Paragraph("12 / 400", td_center),
            Paragraph("<b>PR-1</b>", td_center),
            Paragraph("Retención terminal con retenida terminal simple", td_left)
        ],
    ]
    t_est = Table(tabla_est_data, colWidths=[0.8*cm, 1.4*cm, 1.8*cm, 1.8*cm, 2.2*cm, 1.6*cm, 7.6*cm])
    t_est.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_est)

    # 8. RESULTADOS DE LOS CÁLCULOS JUSTIFICATIVOS
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("8. SÍNTESIS DE CÁLCULOS JUSTIFICATIVOS", h2_style))
    story.append(Paragraph("8.1 Comprobación Eléctrica en Media Tensión", h3_style))
    story.append(Paragraph("• <b>Caída de Tensión Porcentual (ΔV %):</b> <b>0.12 %</b> (26.88 V) en el punto terminal E-09, frente al límite reglamentario del CNE de <b>5.0 %</b>. El diseño ofrece una reserva de calidad del 97.6%.", bullet_style))
    story.append(Paragraph("• <b>Pérdidas de Potencia Activa (ΔP):</b> 0.183 kW, representando apenas un <b>0.12 %</b> de la potencia transmitida.", bullet_style))
    story.append(Paragraph("• <b>Corriente de Carga MT a Plena Capacidad (100 kVA):</b> I<sub>MT</sub> = 2.52 A nominal (4.20 A con sobrecarga admisible).", bullet_style))

    story.append(Paragraph("8.2 Comprobación Mecánica de Conductores (Ecuación de Estado de Truxa)", h3_style))
    story.append(Paragraph("• <b>Hipótesis Base EDS (+15 °C sin viento):</b> T<sub>EDS</sub> = 187.20 kgf (18.0 % del tiro de rotura, cumpliendo holgadamente el límite normativo DGE ≤ 18 % a 20 %).", bullet_style))
    story.append(Paragraph("• <b>Hipótesis de Temperatura Máxima (+35 °C):</b> Flecha máxima en vano crítico de 115.6 m: <b>f<sub>máx</sub> = 1.33 m</b>.", bullet_style))
    story.append(Paragraph("• <b>Distancia de Seguridad al Terreno:</b> Altura libre útil en el centro del vano = 10.60 m - 1.33 m = <b>9.27 m</b>, muy superior a los <b>6.50 m</b> exigidos por la Regla 232 del CNE Suministro para caminos rurales.", bullet_style))

    # 9. PLANOS Y ENTREGABLES
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("9. PLANOS Y ENTREGABLES TÉCNICOS ASOCIADOS", h2_style))
    story.append(Paragraph("1. <b>Plano de Perfil Longitudinal y Spotting de Postes:</b> <code>PLANO_PERFIL_LONGITUDINAL_LP_CAPACHICA.dxf</code> (con terreno natural, catenaria y guitarra inferior normalizada DGE).", bullet_style))
    story.append(Paragraph("2. <b>Tabla Vectorial de Cuadro de Cargas:</b> <code>TABLA_CUADRO_DE_CARGAS.dxf</code> (bloque vectorial para insertar en membretes AutoCAD).", bullet_style))
    story.append(Paragraph("3. <b>Láminas de Detalle de Ferretería y Armados:</b> <code>laminas_de_detalle.dwg</code> (armados PS-1, PA-1, PR-1, SAB-1 y PAT-3).", bullet_style))
    story.append(Paragraph("4. <b>Diagrama Unifilar de Subestación:</b> <code>DIAGRAMAUNIFILAR.dwg</code> (esquema unifilar 22.9 / 0.38 - 0.22 kV).", bullet_style))
    story.append(Paragraph("5. <b>Bases de Datos Topográficas y de Cargas:</b> <code>censo_43_abonados.csv</code>, <code>cuadro_cargas_oficial.csv</code> y <code>planilla_estructuras_lp_capachica.csv</code>.", bullet_style))

    # Firma y cierre
    story.append(Spacer(1, 8 * mm))
    story.append(KeepTogether([
        HRFlowable(width="60%", thickness=0.8, color=c_muted, spaceBefore=4, spaceAfter=4),
        Paragraph("<b>Renzo Gabriel Mamani Galindo</b><br/>Estudiante de Ingeniería Mecánica Eléctrica<br/>Código Universitario: 228447<br/>Facultad de Ingeniería Mecánica Eléctrica, Electrónica y Sistemas<br/>Universidad Nacional del Altiplano — Puno", ParagraphStyle(
            'Firma', parent=base_styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, alignment=1, textColor=c_dark
        )),
        Spacer(1, 2 * mm),
        Paragraph("Puno, Octubre de 2026", ParagraphStyle(
            'FechaFin', parent=base_styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=10, alignment=1, textColor=c_muted
        ))
    ]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado exitosamente en: {output_pdf_path}")


if __name__ == "__main__":
    out_dir = r"C:\Users\renzo\instalacion-electricas\proyectos\renzo-linea-primaria-capachica\entregables"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "memoria_descriptiva.pdf")
    build_pdf(target)
