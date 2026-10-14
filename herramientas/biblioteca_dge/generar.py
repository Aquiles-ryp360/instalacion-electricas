"""Biblioteca CAD derivada de fuentes DGE. No genera geometría de armados por IA.

Las hojas escaneadas se convierten con Potrace; los símbolos vectoriales se
extraen de la norma publicada. El CAD resultante NO fue emitido por el MINEM.
"""
from pathlib import Path
import sys, json, re, io, shutil, subprocess, hashlib, csv, math
sys.path.insert(0, 'G:/Aquiles/dependencias-linea-primaria')
import pymupdf as pdf
import ezdxf
from ezdxf import bbox
from ezdxf.addons import Importer
from ezdxf.math import Matrix44
from PIL import Image

R = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R))
S = R/'referencias/local/biblioteca-dge'
B = R/'build/biblioteca-dge'
T = B/'biblioteca'
V = S/'redlin-original/2025-12-REDLIN-2023-Peru-DGE'
POT = Path('G:/Aquiles/dependencias-linea-primaria/potrace/potrace-1.16.win64/potrace.exe')
PTMM = 25.4/72
SOURCES = [
 dict(id='DGE-MT', norma='RD 024-2003-EM/DGE', archivo='rd024-directo.pdf', url='https://intranet2.minem.gob.pe/web/archivos/dge/legislacion/dispositivos/rd024-2003-EM.pdf', origen='MINEM, descarga directa; láminas escaneadas'),
 dict(id='DGE-BT', norma='RD 023-2003-EM/DGE', archivo='rd023-gobpe.pdf', url='https://cdn.www.gob.pe/uploads/document/file/5327171/4775060-r-d-nro-023-2003-em-dge.pdf', origen='MINEM/gob.pe, descarga directa; láminas escaneadas'),
 dict(id='DGE-SIM', norma='RM 091-2002-EM/VME', archivo='simbologia-directo.pdf', url='https://www.minem.gob.pe/minem/archivos/file/electricidad/legislacion/rm091-2002-em-vme-SIMBOLOGIA.pdf', origen='MINEM, descarga directa; documento completo de 138 páginas'),
 dict(id='REDLIN', norma='Adaptación y copias de DGE; no norma propia del MINEM', archivo='REDLIN-Peru-DGE-2025-12.zip', url='https://www.esolutions.com.pe/download/12062/', pagina='https://www.esolutions.com.pe/recursos/base-de-datos/redlin/redlin-peru-dge/', origen='Esolutions S.A.C., edición 2025-12; copia de láminas de mayor resolución y plantilla CAD de terceros'),
]

def save_json(f, data):
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def newdoc():
    d=ezdxf.new('R2018'); d.units=4
    d.header['$MEASUREMENT']=1; d.header['$LWDISPLAY']=False
    d.styles.new('DGE_ARIAL', dxfattribs={'font':'arial.ttf'})
    for l in ['DGE_CONTORNOS','DGE_RELLENO','DGE_DATOS','DGE_SIMBOLOS','DGE_TEXTOS','DGE_GUIA']:
        d.layers.new(l, dxfattribs={'color':7, 'lineweight':0})
    return d

def parse_index(f, pages, kind):
    d=pdf.open(f); lines=[]
    for n in pages:
        for v in d[n-1].get_text().splitlines():
            v=v.strip()
            if not v:continue
            merged=re.match(r'^(\d{1,3}(?:-[AB])?(?:\([12]/2\))?)\s+([A-Z].+)$',v)
            lines += list(merged.groups()) if merged else [v]
    entries=[]; i=0
    while i<len(lines):
        code=lines[i]
        if re.fullmatch(r'\d{1,3}(?:-[AB])?(?:\([12]/2\))?',code) and int(re.match(r'\d+',code)[0])<=88:
            desc=[]; j=i+1
            while j<len(lines) and not re.fullmatch(r'\d{1,3}',lines[j]):desc.append(lines[j]);j+=1
            if desc and j<len(lines):
                page=int(lines[j]); num=re.match(r'\d+',code)[0]; norm=num.zfill(3)+code[len(num):]
                if (kind=='MT' and 5<=page<=106) or (kind=='BT' and 3<=page<=23):
                    entries.append(dict(familia=kind,lamina=norm,titulo=' '.join(desc),pagina_impresa=page,pagina_pdf=page+1,bloque=f'DGE_{kind}_{norm.replace("(","_").replace(")","").replace("/","_").replace("-","_")}'))
                    i=j+1;continue
        i+=1
    assert len(entries)==(102 if kind=='MT' else 21), (kind,len(entries))
    assert len({v['pagina_pdf'] for v in entries})==len(entries)
    assert len({v['bloque'] for v in entries})==len(entries)
    return entries

def text(layout,s,x,y,h=2.2):
    return layout.add_text(s,dxfattribs={'insert':(x,y),'height':h,'style':'DGE_ARIAL','layer':'DGE_DATOS'})

def sheet(entry, source_doc):
    """Traza el bitmap original completo, con tablas, llamadas, cotas y vistas."""
    p=source_doc[entry['pagina_pdf']-1]
    ims=p.get_image_info(xrefs=True)
    if not ims:
        from herramientas.biblioteca_dge.vector_pdf import convert
        d=convert(p);pw,ph=p.rect.width*PTMM,p.rect.height*PTMM
        f=T/'cad'/entry['familia']/(entry['bloque']+'.dxf');f.parent.mkdir(parents=True,exist_ok=True)
        d.set_modelspace_vport(300,center=(pw/2,ph/2));d.saveas(f)
        entry.update(cad=f.relative_to(T).as_posix(),contornos=len(list(d.modelspace().query('LWPOLYLINE'))),ancho_hoja_mm=pw,alto_hoja_mm=ph,raster_ancho=None,raster_alto=None,estado='Derivado de copia PDF vectorial; geometría y texto delineado editables como entidades, no DIMENSION',origen_conversion='Copia normativa vectorial suministrada por Esolutions; cotejar con fuente MINEM')
        return d
    assert len(ims)==1,entry
    info=ims[0]; raw=source_doc.extract_image(info['xref'])
    im=Image.open(io.BytesIO(raw['image'])).convert('L')
    name=entry['bloque']; work=B/'trazados'; work.mkdir(exist_ok=True)
    pbm=work/(name+'.pbm'); traced=work/(name+'.dxf')
    im.point(lambda x:0 if x<170 else 255,'1').save(pbm)
    subprocess.run([str(POT),str(pbm),'-b','dxf','-t','0','-a','0','-O','0.05','-o',str(traced)],check=True,stdout=subprocess.DEVNULL)
    td=ezdxf.readfile(traced); d=newdoc(); d.layers.get('DGE_CONTORNOS').off(); m=d.modelspace()
    # La transformación del PDF puede rotar el bitmap y la página de forma
    # independiente (hojas 077/078). Usar sólo bbox deformaría/cortaría la hoja.
    transform=pdf.Matrix(info['transform'])*p.rotation_matrix
    def pixel_to_cad(x,y):
        pos=pdf.Point(x/im.width,1-y/im.height)*transform
        return (pos.x*PTMM,(p.rect.height-pos.y)*PTMM)
    loops=[]; contours=0
    for e in td.modelspace():
        if e.dxftype()=='POLYLINE':vertices=[(*pixel_to_cad(v.dxf.location.x,v.dxf.location.y),float(v.dxf.get('bulge',0))) for v in e.vertices]
        elif e.dxftype()=='LWPOLYLINE':vertices=[(*pixel_to_cad(x,y),b) for x,y,_,_,b in e.get_points()]
        else:raise ValueError(e.dxftype())
        assert all(abs(v[2])<1e-12 for v in vertices),'Potrace alpha0 debe producir segmentos rectos'
        xy=[(round(v[0],4),round(v[1],4)) for v in vertices];m.add_lwpolyline(xy,close=True,dxfattribs={'layer':'DGE_CONTORNOS'});loops.append(xy); contours+=1
    h=m.add_hatch(color=7,dxfattribs={'layer':'DGE_RELLENO'});h.dxf.hatch_style=0
    for xy in loops:h.paths.add_polyline_path(xy,is_closed=True,flags=0)
    # Información editable añadida fuera del dibujo oficial; no altera sus rótulos.
    pw,ph=p.rect.width*PTMM,p.rect.height*PTMM
    text(m,f'{entry["familia"]} / LAMINA {entry["lamina"]} / {entry["bloque"]}',12,ph-8,2.1)
    text(m,'CAD derivado de lamina DGE. Contornos de escaneo; no DWG emitido por MINEM.',12,8,1.7)
    text(m,'mm de hoja. Cotas originales prevalecen. No usar contornos para medir piezas.',12,5,1.7)
    d.set_modelspace_vport(300,center=(pw/2,ph/2))
    f=T/'cad'/entry['familia']/(name+'.dxf');f.parent.mkdir(parents=True,exist_ok=True);d.saveas(f)
    entry.update(cad=f.relative_to(T).as_posix(),contornos=contours,ancho_hoja_mm=pw,alto_hoja_mm=ph,
                 raster_ancho=im.width,raster_alto=im.height,estado='CAD derivado; texto del escaneo como contornos, no TEXT ni cotas DIMENSION',origen_conversion='Copia normativa de mayor resolución suministrada por Esolutions; cotejar con fuente directa MINEM')
    return d

def add_to_master(master, source, entry, at):
    name=entry['bloque']; importer=Importer(source,master); target=master.blocks.new(name)
    importer.import_entities(source.modelspace(),target_layout=target);importer.finalize()
    # Atributos en cada inserción permiten identificar y filtrar la hoja.
    for tag,val,y in [('NORMA',entry['familia'], -5),('LAMINA',entry['lamina'],-8),('PAGINA_PDF',str(entry['pagina_pdf']),-11)]:
        target.add_attdef(tag,(12,y),text=val,height=1.5,dxfattribs={'layer':'DGE_DATOS','flags':1})
    master.modelspace().add_blockref(name,at).add_auto_attribs({'NORMA':entry['familia'],'LAMINA':entry['lamina'],'PAGINA_PDF':str(entry['pagina_pdf'])})
    lay=master.layouts.new(name);w,h=entry['ancho_hoja_mm'],entry['alto_hoja_mm']
    lay.page_setup(size=(w,h),margins=(0,0,0,0),units='mm')
    # Hoja idéntica en espacio papel: no depende de rutas de imágenes externas.
    lay.add_blockref(name,(0,0))

def inside(pt,rect,margin=0):
    return rect.x0+margin<=pt.x<=rect.x1-margin and rect.y0+margin<=pt.y<=rect.y1-margin

def symbols():
    """Extrae todos los registros de la sección 9 y sus vectores sin la retícula auxiliar."""
    d=pdf.open(S/'simbologia-directo.pdf'); master=newdoc(); records=[]
    for n in range(72,89):
        p=d[n];words=p.get_text('words')
        codes=[w for w in words if re.fullmatch(r'09-\d{2}-\d{2}',w[4]) and 75<w[0]<140]
        drawings=p.get_drawings()
        horizontal=sorted({round((dr['rect'].y0+dr['rect'].y1)/2,2) for dr in drawings if dr['rect'].x0>=254 and dr['rect'].width>240 and dr['rect'].height<1})
        for w in codes:
            code=w[4];cy=(w[1]+w[3])/2
            top=max((y for y in horizontal if y<cy),default=w[1]-10)
            bottom=min((y for y in horizontal if y>cy),default=w[3]+10)
            rect=pdf.Rect(144,top+.35,254,bottom-.35)
            # La sección mantiene código/símbolo/definición en tres columnas.
            label=p.get_textbox(pdf.Rect(256,top,520,bottom)).strip().replace('\n',' ')
            name='DGE_'+code.replace('-','_');bl=master.blocks.new(name)
            def xy(v):return ((v.x-199)*PTMM,(cy-v.y)*PTMM)
            entities=0
            for dr in drawings:
                if not pdf.Rect(dr['rect']).intersects(rect):continue
                if max(dr['rect'].width,dr['rect'].height)<.85:continue # puntos de la retícula auxiliar
                sub=[];fill_loops=[]
                def finish():
                    nonlocal entities,sub
                    if len(sub)<2:sub=[];return
                    closed=dr.get('fill') is not None or dr.get('closePath',False) or math.dist(sub[0],sub[-1])<.001
                    if dr.get('fill') is not None:fill_loops.append(sub)
                    weights=[0,5,9,13,15,18,20,25,30,35,40,50,53,60,70,80,90,100,106,120,140,158,200,211]
                    lw=min(weights,key=lambda w:abs(w-(dr.get('width') or .5)*PTMM*100))
                    if dr.get('color') is not None:
                        rgb=tuple(round(v*255) for v in dr['color'])
                        bl.add_lwpolyline(sub,close=closed,dxfattribs={'layer':'DGE_SIMBOLOS','lineweight':lw,'true_color':rgb[0]*65536+rgb[1]*256+rgb[2]})
                    entities+=1;sub=[]
                for it in dr['items']:
                    op=it[0]
                    if op=='l':pts=it[1:3]
                    elif op=='c':
                        a,b,c,z=it[1:5];pts=[]
                        for k in range(17):
                            t=k/16;u=1-t;pts.append(pdf.Point(u**3*a.x+3*u*u*t*b.x+3*u*t*t*c.x+t**3*z.x,u**3*a.y+3*u*u*t*b.y+3*u*t*t*c.y+t**3*z.y))
                    elif op=='re':
                        rr=it[1];pts=[rr.tl,rr.tr,rr.br,rr.bl,rr.tl]
                    elif op=='qu':q=it[1];pts=[q.ul,q.ur,q.lr,q.ll,q.ul]
                    else:raise ValueError(op)
                    if not all(inside(v,rect) for v in pts):finish();continue
                    pp=[xy(v) for v in pts]
                    if sub and math.dist(sub[-1],pp[0])>.001:finish()
                    sub+=pp if not sub else pp[1:]
                finish()
                if fill_loops:
                    rgb=tuple(round(v*255) for v in dr['fill'])
                    ha=bl.add_hatch(color=7,dxfattribs={'layer':'DGE_SIMBOLOS','true_color':rgb[0]*65536+rgb[1]*256+rgb[2]});ha.dxf.hatch_style=0
                    for loop in fill_loops:ha.paths.add_polyline_path(loop,is_closed=True,flags=0)
            for block in p.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line.get('spans',[]):
                        rr=pdf.Rect(span['bbox']);o=pdf.Point(span['origin'])
                        if rect.contains(rr) and span['text'].strip():
                            bl.add_text(span['text'],dxfattribs={'insert':xy(o),'height':span['size']*PTMM*.73,'style':'DGE_ARIAL','layer':'DGE_TEXTOS'});entities+=1
            if not entities:raise ValueError(('símbolo sin geometría',code))
            j=len(records);loc=(30+(j%5)*65,30-(j//5)*65)
            master.modelspace().add_blockref(name,loc)
            text(master.modelspace(),code,loc[0]-15,loc[1]-23,2.3)
            rec=dict(codigo=code,bloque=name,pagina_pdf=n+1,definicion=label,entidades=entities,origen='Extracción de vectores de PDF oficial MINEM, sección 9; sin retícula auxiliar',limites_pdf=list(rect))
            records.append(rec)
    assert len(records)==len({v['codigo'] for v in records}), 'codigos duplicados'
    master.set_modelspace_vport(220,center=(155,-90))
    f=T/'cad/SIMBOLOGIA_DGE_SECCION_9.dxf';master.saveas(f)
    save_json(T/'catalogo-simbolos.json',records)
    return records

def main():
    T.mkdir(parents=True,exist_ok=True)
    for src in SOURCES:
        f=S/src['archivo'];src.update(fecha_descarga='2026-10-14',bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest())
    save_json(T/'fuentes.json',SOURCES)
    for src in SOURCES[:3]:
        out=T/'fuentes';out.mkdir(exist_ok=True);shutil.copy2(S/src['archivo'],out/src['archivo'])
    third=T/'terceros/esolutions';third.mkdir(parents=True,exist_ok=True)
    for name in ['REDLIN-Plantilla-Peru.dxf','Leeme.txt']:shutil.copy2(V/name,third/name)
    shutil.copytree(V/'Armados Norma DGE',third/'Copias-normativas',dirs_exist_ok=True)
    for kind,official,indices,copy in [('MT','rd024-directo.pdf',[2,3,4,5],'Armados MT-Peru-DGE-RD024-2003.pdf'),('BT','rd023-gobpe.pdf',[2,3],'Armados BT-Peru-DGE-RD023-2003.pdf')]:
        entries=parse_index(S/official,indices,kind);source=pdf.open(V/'Armados Norma DGE'/copy);master=newdoc()
        for j,entry in enumerate(entries):
            sd=sheet(entry,source);add_to_master(master,sd,entry,((j%10)*320,-(j//10)*340))
            if j%10==0:print(kind,j+1,'/',len(entries),flush=True)
        if kind=='MT':master.layers.get('DGE_CONTORNOS').off()
        f=T/f'cad/BIBLIOTECA_DGE_{kind}_COMPLETA.dxf';master.set_modelspace_vport(2000,center=(1500,-1000));master.saveas(f)
        save_json(T/f'catalogo-armados-{kind}.json',entries)
        with (T/f'catalogo-armados-{kind}.csv').open('w',encoding='utf-8-sig',newline='') as stream:
            wr=csv.DictWriter(stream,fieldnames=list(entries[0]));wr.writeheader();wr.writerows(entries)
        print(kind,'master MB',f.stat().st_size/1e6,flush=True)
    sy=symbols();print('Símbolos',len(sy),flush=True)

if __name__=='__main__':main()
