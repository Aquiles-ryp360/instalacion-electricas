"""Adjunta al expediente láminas DGE completas y los planos del proyecto.

La selección es una referencia de armados y piezas, no una homologación automática
de postes CAC ni una certificación de los armados especiales de LP-R01.
"""
from pathlib import Path
import sys,json,io,html,shutil,collections
sys.path.insert(0,'G:/Aquiles/dependencias-linea-primaria')
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from herramientas.biblioteca_dge.exportar_pdf import exportar
from pypdf import PdfReader,PdfWriter
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

P=Path(__file__).resolve().parents[2];R=P.parents[1];F=R/'output/pdf';B=R/'build/biblioteca-dge';L=B/'biblioteca';O=R/'output/linea-primaria-limbani-huancasayani'
SELECTED=['004','008','012','016','020','026','065','065-A','065-B','066','066-A','067','068','069','071','071-A','071-B','073-A','074','076','076-A','077','078-A']
EXTRA_F='Linea_Primaria_Limbani_Huancasayani_R01_anexo_armados.pdf'
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'));pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
ss=getSampleStyleSheet();ss.add(ParagraphStyle('A',fontName='Arial',fontSize=10,leading=14,spaceAfter=9));ss.add(ParagraphStyle('H',fontName='Arial-Bold',fontSize=20,leading=25,spaceAfter=18,textColor=colors.HexColor('#006699')));ss.add(ParagraphStyle('S',fontName='Arial',fontSize=8,leading=10.5))
def p(t,style='A'):return Paragraph(html.escape(str(t)),ss[style])
def table(headers,rows,widths):
    t=Table([[p(v,'S') for v in headers]]+[[p(v,'S') for v in row] for row in rows],colWidths=widths,repeatRows=1)
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e1edf3')),('LINEBELOW',(0,0),(-1,-1),.25,colors.HexColor('#cccccc')),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));return t
def footer(c,d):
    c.setFont('Arial',8);c.drawString(42,24,'LP-R01 | Anexo normativo de armados | Fuente DGE y adaptación pendiente');c.drawRightString(550,24,str(d.page))

def main():
    entries=json.loads((L/'catalogo-armados-MT.json').read_text(encoding='utf-8'));bycode={v['lamina']:v for v in entries};chosen=[bycode[v] for v in SELECTED]
    a=json.loads((P/'datos/lp-r01/resultados.json').read_text(encoding='utf-8'));counts=collections.Counter(v['armado'] for v in a['postes'])
    story=[Spacer(1,35),p('ANEXO DE ARMADOS Y COMPONENTES','H'),p('Línea primaria Limbani - Huancasayani'),p('Instalaciones Eléctricas II | Estudiante: Aquiles Taylor Ramos Yapo | Código 227368'),Spacer(1,20),
        p('Este anexo incorpora 23 láminas completas de la norma DGE RD 024-2003-EM/DGE: vistas, cotas, referencias de piezas, tablas de materiales y detalles de retenida y puesta a tierra. El expediente integrado incluye además 19 láminas A3 del proyecto, con siete perfiles longitudinales ampliados.'),
        p('Se conservan en la biblioteca las 102 láminas de la RD 024, las 21 láminas base de la RD 023 y la lámina 022 de identificación y codificación, aprobada por RD 002-2019-MEM/DGE. Esta última se recuperó del PDF oficial de El Peruano de 9 de enero de 2019.'),
        p('Las 23 hojas adjuntas se exportan directamente de los DXF vectorizados, en formato A3 y sin imágenes raster. Se respeta la orientación de cada lámina y se conservan todas las vistas, cotas, llamadas, tablas y el rótulo original. La vectorización de contornos utiliza Potrace sobre las copias normativas; no es un redibujo por IA. Los PDF originales permanecen en la biblioteca para contrastar la conversión.'),
        p('Los DXF y estos PDF derivados no son archivos CAD emitidos por MINEM. Las letras del escaneo son contornos editables, no TEXT, y las cotas no son objetos DIMENSION. Ampliar el PDF conserva los vectores, pero no recupera información que falte en el documento fuente.'),
        p('La plantilla REDLIN de Esolutions es un recurso de terceros, incluida con su atribución y condiciones. No se utilizó el proyecto de otro estudiante como fuente de armados.'),PageBreak(),
        p('APLICACIÓN AL PROYECTO','H'),
        p('Las láminas normalizadas muestran configuraciones y materiales concretos. En las hojas 004, 008 y 020 aparecen postes y crucetas de madera. LP-R01 estudia postes CAC de 13, 15 y 17 m: debe diseñarse la adaptación de abrazaderas, perforaciones, crucetas, aislamiento y fijación, además de comprobar todas las cargas. Adjuntar el dibujo normativo no convierte esa adaptación en un armado homologado.'),
        table(['Código en LP-R01','Cantidad','Referencia y condición'],[
            ['LP-S-004',counts['LP-S-004'],'004: PS1-3/PS1-3L sin neutro. Comparar geometría y distancias; sustitución madera/CAC pendiente.'],
            ['LP-A-008',counts['LP-A-008'],'008: PA1-3/PA1-3L 5°-30°. Código funcional del estudio. Sujeción PIN de la norma no equivale a retención; el modelo LP retiene los ramales. Cotejar 012/016/020 y definir variante CAC.'],
            ['LP-AN-020',counts['LP-AN-020'],'020: PR3-3/PR3-3L sin neutro. Tabla normativa de referencia, adaptación CAC pendiente.'],
            ['LP-T-026',counts['LP-T-026'],'026: terminal horizontal. Referencia de función; altura, herrajes y cruceta según cargas y fabricante.'],
            ['ESP-RET',counts['ESP-RET'],'P003, P035 y P057 superan 90°. No hay equivalencia automática con 012/016. Dos retenciones y puentes requieren detalle específico o replantear la curva.'],
        ],[88,40,382]),Spacer(1,12),
        p('Los dos transformadores de 250 kVA se estudian sobre instalaciones de piso, no sobre el armado aéreo biposte de la lámina 064. La 064 se conserva en la biblioteca general; no se adopta como soporte de estos equipos.'),
        p('Las retenidas y puestas a tierra de 074/076/077 son referencias. Conservan los componentes de la norma, pero sus resistencias, dimensiones y cantidades del proyecto dependen del cálculo, suelo y resistividad. El presupuesto de LP-R01 sigue siendo una estimación por conjuntos; no se afirma que sea un despiece definitivo de ferretería.'),PageBreak(),
        p('ÍNDICE DE LÁMINAS ADJUNTAS','H'),table(['Lámina','PDF fuente','Contenido'],[[v['lamina'],v['pagina_pdf'],v['titulo']] for v in chosen[:12]],[45,52,413]),PageBreak(),
        p('ÍNDICE DE LÁMINAS ADJUNTAS (CONTINUACIÓN)','H'),table(['Lámina','PDF fuente','Contenido'],[[v['lamina'],v['pagina_pdf'],v['titulo']] for v in chosen[12:]],[45,52,413]),Spacer(1,15),
        p('Lectura: código de componente en cada llamada -> fila correspondiente de la tabla -> variante del armado -> cantidad/unidad de esa columna. No sumar conjuntamente las columnas con neutro y sin neutro.'),
        p('Fuente directa de contraste: https://intranet2.minem.gob.pe/web/archivos/dge/legislacion/dispositivos/rd024-2003-EM.pdf','S'),
        p('Copia normativa de mayor resolución: https://www.esolutions.com.pe/recursos/base-de-datos/redlin/redlin-peru-dge/ (paquete 2025-12). Procedencia y hashes en la biblioteca.','S'),
        p('Simbología de plano: RM 091-2002-EM/VME, sección 9. Poste CAC 09-91-20, retenida 09-91-18, línea general 09-91-03 y subestación proyectada 09-90-09. Su tamaño es gráfico de representación, no dimensión del equipo.','S'),
    ]
    intro=B/'introduccion-anexo.pdf';SimpleDocTemplate(str(intro),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=44,bottomMargin=45).build(story,onFirstPage=footer,onLaterPages=footer)
    ann=PdfWriter();ann.append(intro,import_outline=False)
    intro_pages=len(ann.pages)
    for j,v in enumerate(chosen):
        page=PdfReader(exportar(v)).pages[0]
        # Nota fuera del dibujo, con la paginación de la copia fuente claramente identificada.
        w,h=float(page.mediabox.width),float(page.mediabox.height);buf=io.BytesIO();cv=Canvas(buf,pagesize=(w,h));cv.setFont('Arial',6.8)
        cv.drawRightString(w-42,h-22,f'LP-R01 / AN-{j+1:02} | Aquiles Taylor Ramos Yapo | 227368');cv.save();buf.seek(0)
        page.merge_page(PdfReader(buf).pages[0]);ann.add_page(page);ann.add_outline_item(f'AN-{j+1:02} / DGE {v["lamina"]}',intro_pages+j)
    ann.add_metadata({'/Title':'Anexo de armados CAD vectoriales LP Limbani - Huancasayani','/Author':'Aquiles Taylor Ramos Yapo','/Subject':'Láminas completas exportadas del DXF, sin imágenes raster; adaptación CAC pendiente'})
    ann_path=F/EXTRA_F
    with ann_path.open('wb') as f:ann.write(f)
    exp=F/'Linea_Primaria_Limbani_Huancasayani_R01_expediente.pdf';base=B/'expediente-base-R01.pdf'
    # Reejecución idempotente: evita adjuntar una segunda vez los mismos planos.
    current=PdfReader(exp)
    if current.metadata.get('/LPArmadosAdjuntos')!='1':shutil.copy2(exp,base)
    assert base.exists()
    full=PdfWriter();full.append(base,import_outline=True);base_n=len(full.pages)
    full.append(ann_path,import_outline=False);ann_n=len(full.pages)-base_n
    planos=F/'Linea_Primaria_Limbani_Huancasayani_R01_planos.pdf';full.append(planos,import_outline=False)
    full.add_outline_item('Memoria del proyecto',0);full.add_outline_item('Anexo: armados y componentes',base_n)
    for j,v in enumerate(chosen):full.add_outline_item(f'AN-{j+1:02} / DGE {v["lamina"]}',base_n+intro_pages+j)
    full.add_outline_item('Planos del proyecto: 19 láminas A3',base_n+ann_n)
    full.add_metadata({'/Title':'LP Limbani - Huancasayani: expediente, armados DGE y planos','/Author':'Aquiles Taylor Ramos Yapo','/LPArmadosAdjuntos':'1'})
    with exp.open('wb') as f:full.write(f)
    mapping=dict(estado='Referencias CAD vectoriales adjuntas; adaptación CAC y armados especiales pendientes',exportacion='23 hojas A3 vectoriales del DXF, sin raster',laminas=chosen,hojas_intro=intro_pages,hojas_anexo=ann_n,hojas_memoria=base_n,hojas_planos=len(PdfReader(planos).pages),hojas_expediente=len(full.pages))
    (P/'datos/lp-r01/armados-adjuntos.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
    shutil.copy2(ann_path,O/EXTRA_F)
    print('Anexo',ann_n,'p; expediente integrado',len(full.pages),'p',flush=True)

if __name__=='__main__':main()
