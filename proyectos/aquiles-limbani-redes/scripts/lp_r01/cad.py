"""CAD editable, UTM en metros, bloques con atributos y láminas A3 verificables."""
from pathlib import Path
import sys,json,math
import numpy as np
import ezdxf
from ezdxf import units
from ezdxf.addons.drawing import RenderContext,Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration,BackgroundPolicy,ColorPolicy
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[2];R=P.parents[1];D=P/'datos/lp-r01';O=R/'output/linea-primaria-limbani-huancasayani'
A=json.loads((D/'resultados.json').read_text(encoding='utf-8'));posts=A['postes'];spans=A['vanos']
def text(space,s,x,y,h=2.7,layer='ROTULO'):
    return space.add_text(str(s),dxfattribs={'insert':(x,y),'height':h,'layer':layer,'style':'Arial'})
def line(space,a,b,layer='DETALLE'):return space.add_line(a,b,dxfattribs={'layer':layer})
def rect(space,x,y,w,h,layer='ROTULO'):
    return space.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],close=True,dxfattribs={'layer':layer})
def frame(doc,name,title,index):
    page=doc.layouts.new(name);page.page_setup(size=(420,297),margins=(0,0,0,0),units='mm')
    rect(page,8,8,404,281);line(page,(8,23),(412,23),'ROTULO')
    text(page,'INSTALACIONES ELÉCTRICAS II | Aquiles Taylor Ramos Yapo | 227368',13,15,3)
    text(page,f'{index} · LP-R01 · 14/10/2026 · PROYECTO ACADÉMICO',13,10,2.3)
    text(page,title,13,278,4);text(page,'NO APTO PARA CONSTRUCCIÓN SIN ESTUDIOS DE CAMPO',13,272,2.5)
    return page
def viewport(page,center,size,bounds,scale=None):
    xmin,ymin,xmax,ymax=bounds;w,h=size
    if scale is None:scale=math.ceil(max((xmax-xmin)/(w/1000),(ymax-ymin)/(h/1000))/500)*500
    vp=page.add_viewport(center=center,size=size,view_center_point=((xmin+xmax)/2,(ymin+ymax)/2),view_height=h*scale/1000,status=2)
    if scale>15000:
        for name in ['LP_ID','LP_POSTES','LP_RETENIDAS','LP_PAT']:vp.freeze(name)
    text(page,f'Planta 1:{scale} · UTM WGS84 / 19S · EPSG:32719',center[0]-w/2,center[1]-h/2-5,2.3)
    # Norte arriba del modelo; escala gráfica en m.
    x=center[0]+w/2-12;y=center[1]+h/2-25
    line(page,(x,y),(x,y+15));page.add_solid([(x-2,y+11),(x+2,y+11),(x,y+15),(x,y+15)],dxfattribs={'layer':'DETALLE'})
    text(page,'N',x-1.5,y+17,3)
    return scale
def legend(page,x=294,y=251):
    items=[('SUSPENSION','Suspensión 0-5°'),('ANGULO','Ángulo con retención'),('ANCLAJE','Anclaje / ángulo >30°'),('TERMINAL','Terminal de línea'),('SE','SE en proyección DGE 09-90-09'),('PAT','Puesta a tierra, símbolo'),('RET','Anclaje retenida, símbolo')]
    text(page,'LEYENDA',x,y,3.2)
    for i,(kind,label) in enumerate(items):
        yy=y-9-i*9;page.add_blockref('LP_'+kind,(x+3,yy),dxfattribs={'xscale':.4,'yscale':.4});text(page,label,x+10,yy-1,2.5)
    text(page,'Postes: simbología del proyecto.',x,y-80,2.2);text(page,'Armados basados en RD024-2003.',x,y-85,2.2)
    text(page,'No reproduce un plano de fabricante.',x,y-90,2.2)
def main():
    out=O/'cad';out.mkdir(parents=True,exist_ok=True);png=R/'build'/P.name/'lp-r01/planos';png.mkdir(parents=True,exist_ok=True)
    doc=ezdxf.new('R2018');doc.units=units.M;doc.header['$INSUNITS']=6;doc.header['$MEASUREMENT']=1
    doc.styles.new('Arial',dxfattribs={'font':'arial.ttf'})
    layers={'LP_EJE':1,'LP_CONDUCTORES':1,'LP_POSTES':1,'LP_ID':7,'LP_RETENIDAS':34,'LP_PAT':3,'LP_SE':5,'BASE_CASAS':8,'BASE_VIAS':8,'BASE_AGUA':4,'ROTULO':7,'DETALLE':7,'PERFIL_TERRENO':32,'PERFIL_CONDUCTOR':1}
    for name,col in layers.items():doc.layers.new(name,dxfattribs={'color':col,'lineweight':25 if name.startswith('LP_') else 13})
    for name,rgb in [('BASE_CASAS',(170,170,170)),('BASE_VIAS',(185,185,185)),('BASE_AGUA',(65,155,215)),('LP_EJE',(170,25,30)),('LP_CONDUCTORES',(170,25,30)),('PERFIL_TERRENO',(130,95,60)),('PERFIL_CONDUCTOR',(180,20,20)),('LP_ID',(60,45,45))]:doc.layers.get(name).rgb=rgb
    for kind in ['SUSPENSION','ANGULO','ANCLAJE','TERMINAL','SE','PAT','RET']:
        b=doc.blocks.new('LP_'+kind)
        if kind=='SUSPENSION':b.add_circle((0,0),3)
        elif kind=='ANGULO':b.add_lwpolyline([(-3,0),(0,3),(3,0),(0,-3)],close=True)
        elif kind in ['ANCLAJE','TERMINAL']:
            b.add_lwpolyline([(-3,-3),(3,-3),(3,3),(-3,3)],close=True)
            if kind=='TERMINAL':b.add_line((-3,-3),(3,3));b.add_line((-3,3),(3,-3))
        elif kind=='SE':
            b.add_lwpolyline([(-5,-3),(5,-3),(5,3),(-5,3)],close=True);b.add_lwpolyline([(5,3),(-5,0),(5,-3)])
        elif kind=='PAT':
            b.add_line((0,3),(0,0))
            for j in range(3):b.add_line((-3+j,-j),(3-j,-j))
        else:b.add_lwpolyline([(-2,-2),(2,-2),(0,2)],close=True)
        if kind in ['SUSPENSION','ANGULO','ANCLAJE','TERMINAL']:
            for tag in ['ID','ESTRUCTURA','E','N','POSTE_M']:b.add_attdef(tag,insert=(0,0),height=1,dxfattribs={'flags':1})
        elif kind=='SE':b.add_attdef('ID',insert=(0,0),height=1,dxfattribs={'flags':1})
    ms=doc.modelspace();coords=A['geometria']['coordinates']
    ms.add_lwpolyline(coords,dxfattribs={'layer':'LP_EJE'})
    # Tres fases horizontalmente separadas en planta; unión en vértices esquemática.
    from shapely.geometry import LineString
    axis=LineString(coords)
    for side in [-1.2,1.2]:
        g=axis.offset_curve(side,join_style=2)
        if g.geom_type=='LineString':ms.add_lwpolyline(list(g.coords),dxfattribs={'layer':'LP_CONDUCTORES'})
    houses=json.loads((R/'build'/P.name/'lp-r01/investigacion/casas-originales.geojson').read_text(encoding='utf-8'))
    for f in houses['features']:
        geo=f['geometry']
        if not geo:continue
        polys=[geo['coordinates']] if geo['type']=='Polygon' else geo['coordinates'] if geo['type']=='MultiPolygon' else []
        for poly in polys:
            for ring in poly:ms.add_lwpolyline([p[:2] for p in ring],close=True,dxfattribs={'layer':'BASE_CASAS'})
    refs=json.loads((D/'referencias-osm.geojson').read_text(encoding='utf-8'))
    for f in refs['features']:
        cls=f['properties']['clase'];lay='BASE_AGUA' if cls in ['river','stream','drain','ditch'] else 'BASE_VIAS'
        ms.add_lwpolyline(f['geometry']['coordinates'],dxfattribs={'layer':lay})
    for p in posts:
        ins=ms.add_blockref('LP_'+p['estructura'],(p['e'],p['n']),dxfattribs={'layer':'LP_POSTES'})
        ins.add_auto_attribs({tag:str(p[key]) for tag,key in [('ID','id'),('ESTRUCTURA','estructura'),('E','e'),('N','n'),('POSTE_M','poste_m')]})
        # Rótulos fuera del punto medido; centros de bloques conservan las coordenadas.
        i=int(p['id'][1:]);text(ms,p['id'],p['e']+8,p['n']+(8 if i%2 else -16),9,'LP_ID')
        ms.add_blockref('LP_PAT',(p['e']+6,p['n']-6),dxfattribs={'layer':'LP_PAT','xscale':.6,'yscale':.6})
    for g in A['retenidas']:
        p=next(p for p in posts if p['id']==g['poste']);line(ms,(p['e'],p['n']),(g['e'],g['n']),'LP_RETENIDAS');ms.add_blockref('LP_RET',(g['e'],g['n']),dxfattribs={'layer':'LP_RETENIDAS'})
    for p,name in [(posts[0],'SE-LIM'),(posts[-1],'SE-HUA')]:
        ins=ms.add_blockref('LP_SE',(p['e'],p['n']),dxfattribs={'layer':'LP_SE','xscale':2,'yscale':2});ins.add_auto_attribs({'ID':name});text(ms,name,p['e']+20,p['n']+25,14,'LP_SE')
    xyz=np.array(coords);bounds=(xyz[:,0].min()-90,xyz[:,1].min()-90,xyz[:,0].max()+90,xyz[:,1].max()+90)
    page=frame(doc,'LP-01_GENERAL','Ubicación y trazado general | MCH Limbani - Huancasayani','LP-01')
    viewport(page,(150,150),(270,235),bounds);legend(page)
    text(page,f'Longitud eje: {A["linea_longitud_m"]/1000:.3f} km',294,135,3)
    text(page,f'{len(posts)} apoyos | {len(spans)} vanos',294,127,3)
    text(page,'10 kV · 3 fases AAAC 50 mm²',294,119,3)
    text(page,'2 SE propuestas de 250 kVA',294,111,3)
    for j,s in enumerate(['Inicio: referencia de CAD anterior.','Llegada: ubicación OSM de localidad.','Predios de SE aún no confirmados.','Eje desplazado 20 m de vía OSM,','ajustado para evitar inmuebles.','Cotas: modelo público ~30m.','Geometría NO levantada en campo.','Operación aislada: SIN SEIN.']):text(page,s,294,95-j*6,2.5)
    n=math.ceil(A['linea_longitud_m']/1000)
    for k in range(n):
        a=k*1000;b=min((k+1)*1000,A['linea_longitud_m']);indices=[i for i,v in enumerate(spans) if posts[i+1]['progresiva_m']>=a and posts[i]['progresiva_m']<=b]
        ps=posts[indices[0]:indices[-1]+2];xy=np.array([(p['e'],p['n']) for p in ps])
        page=frame(doc,f'LP-{k+2:02}_PLANTA',f'Planta y perfil de gabinete | km {a/1000:.1f} a {b/1000:.1f}',f'LP-{k+2:02}')
        bb=(xy[:,0].min()-35,xy[:,1].min()-35,xy[:,0].max()+35,xy[:,1].max()+35);scale=viewport(page,(150,183),(270,170),bb)
        legend(page,y=251);text(page,f"{ps[0]['id']} a {ps[-1]['id']}",294,138,3)
        text(page,f'Vanos {spans[indices[0]]["id"]}-{spans[indices[-1]]["id"]}',294,131,2.7)
        text(page,'Curva roja: conductor caliente 75°C',294,121,2.3);text(page,'Terreno: DEM público, no topografía',294,115,2.3)
        xmin=ps[0]['progresiva_m'];xmax=ps[-1]['progresiva_m'];zz=[p['z_dem_m'] for p in ps];zmin=min(zz)-5;zmax=max(zz)+25
        def px(s):return 16+(s-xmin)/(xmax-xmin)*263
        def py(z):return 35+(z-zmin)/(zmax-zmin)*48
        rect(page,15,34,265,50,'DETALLE')
        for i in indices:
            v=spans[i];pa=posts[i];pb=posts[i+1];prof=v['perfil'];chain=pa['progresiva_m']+np.array(prof['fraction'])*v['longitud_m']
            for key,lay in [('terreno_dem_m','PERFIL_TERRENO'),('conductor_m','PERFIL_CONDUCTOR')]:
                page.add_lwpolyline([(px(s),py(z)) for s,z in zip(chain,prof[key])],dxfattribs={'layer':lay})
        for p in ps:line(page,(px(p['progresiva_m']),py(p['z_dem_m'])),(px(p['progresiva_m']),py(p['z_dem_m']+p['amarre_m'])))
        text(page,f'Perfil H 1:{round((xmax-xmin)/.263)} / V 1:{round((zmax-zmin)/.048)} | elevaciones DEM m',16,87,2.3)
        text(page,f"{xmin:.1f} m / {zmin:.1f} m",16,28,2.2);text(page,f"{xmax:.1f} m / {zmax:.1f} m",205,28,2.2)
    page=frame(doc,'LP-UNIFILAR','Diagrama unifilar, límites y protecciones | SIN ESCALA','LP-E01')
    y=210
    for x,label in [(35,'G: ref. 200 kW'),(110,'T1: 250 kVA'),(185,'10 kV: LP'),(265,'T2: 250 kVA'),(365,'Huancasayani')]:text(page,label,x-18,y+28,3)
    page.add_circle((35,y),10,dxfattribs={'layer':'DETALLE'});text(page,'G',31,y-2,5)
    line(page,(45,y),(90,y));page.add_circle((102,y),9);page.add_circle((115,y),9);line(page,(124,y),(246,y));page.add_circle((258,y),9);page.add_circle((271,y),9);line(page,(280,y),(382,y))
    for x,name in [(70,'QG'),(145,'Q1'),(230,'Q2'),(316,'QBT')]:
        rect(page,x-3,y-4,6,8,'DETALLE');text(page,name,x-5,y-14,2.8)
    for j,s in enumerate(['Generación y T1: 380 V / 10 kV; antecedentes sin placas verificadas.','T2: 10 kV / 380-220 V, Dyn11 propuesto; 250 kVA garantizados a altitud.','Q1: 50/51 + 51V; Q2: 87T, 50/51, 51V de respaldo. 59N/64 en MT.','MT delta: zigzag + NGR 5 A / 10 s propuesto en SE-LIM; R ~1155 ohm.','Generador: 27/59, 81, 46, 32, AVR y regulador; ajustes sujetos a curvas reales.','En llegada: tablero 400 A, medición, maniobra y protección BT, sin diseño de redes de usuarios.','Falla sostenida estimada ~7.7 A MT: 50/51 solos NO garantizan despeje.','Capacidad LP 250 kVA; demanda usuarios 171.5 kW; generación necesaria ~183.3 kW.','Toma efectiva +5% propuesta T1: salida MT 10.18 kV, llegada BT 371.1 V.','Reserva para Limbani no confirmada; el transporte disponible depende del recurso y despacho.']):text(page,s,20,165-j*10,3)
    page=frame(doc,'LP-ESTRUCTURAS','Estructuras, retenidas y separaciones | ESQUEMAS SIN ESCALA','LP-M01')
    for k,kind in enumerate(['SUSPENSION','ANGULO','ANCLAJE','TERMINAL']):
        x=55+k*99;line(page,(x,150),(x,240));line(page,(x-25,230),(x+25,230))
        for dx in [-25,0,25]:page.add_circle((x+dx,235),2.5)
        if kind!='SUSPENSION':line(page,(x,235),(x-40,150));line(page,(x,235),(x+40,150))
        text(page,kind,x-25,258,3);text(page,'1.2 m entre fases',x-28,244,2.7)
        text(page,'CAC 13 / 15 / 17 m',x-32,133,2.7);text(page,'600 daN tipo, por certificar',x-36,125,2.3)
    for j,s in enumerate(['Referencias RD024-2003: 004 suspensión, 008 angular, 012/016 ángulos mayores, 020 anclaje.','En LP-R01 los ángulos >5° se retienen, sin asumir armados de suspensión en curvas fuertes.','Retenidas longitudinales independientes por ramal; 45° de estudio y resistencia según CSV.','Suelo, bloques de anclaje, empotramiento y carga vertical requieren verificación geotécnica.','Alturas 15/17 m sólo en apoyos señalados en tabla; el esquema no fija cotas de campo.','Margen de estudio 7.5 m frente a DEM; no certifica cruces ni distancias a techos o vegetación.','Aisladores/descargadores: coordinación para altitud hasta 4000 m, sin factor universal inventado.']):text(page,s,20,107-j*11,3)
    page=frame(doc,'LP-TIERRAS','Puesta a tierra y subestaciones de llegada/salida | ESQUEMAS SIN ESCALA','LP-E02')
    rect(page,35,145,105,105,'DETALLE')
    for j in [1,2]:line(page,(35+j*35,145),(35+j*35,250));line(page,(35,145+j*35),(140,145+j*35))
    for x,y in [(35,145),(35,250),(140,145),(140,250)]:page.add_circle((x,y),2);text(page,'2.4m',x+4,y,2.5)
    text(page,'Malla SE 10 x 10 m · Cu 35 mm²',35,258,3);text(page,'Paso ~3.33m, profundidad propuesta 0.6m',35,134,2.6)
    rect(page,240,160,130,85,'DETALLE');rect(page,255,180,45,35,'DETALLE');text(page,'Transformador',253,224,3);rect(page,321,180,25,35,'DETALLE');text(page,'Celda',319,224,3)
    text(page,'Plataforma propuesta 6x4 m',240,253,3)
    for j,s in enumerate(['Cuatro varillas de 2.4m por SE; unir masas, cerco y descargadores bajo evaluación de tensiones.','PAT postes: dos varillas 2.4m / 16mm, enlace Cu 25mm² propuesto; no neutro MT continuo.','No equivale a garantía de 25 ohm: requiere resistividad Wenner y potenciales de paso/contacto.','NGR conecta neutro del zigzag a malla SE-LIM; no sustituye puesta a tierra de masas.','Clase de aislamiento 24kV propuesta para operación 10kV; proveedor debe garantizar a altitud.','Plano civil, derrames, drenaje, cerco y distancias internas pendientes de catálogo/geotecnia.']):text(page,s,20,111-j*12,3)
    doc.layouts.delete('Layout1')
    doc.set_modelspace_vport(height=6500,center=((bounds[0]+bounds[2])/2,(bounds[1]+bounds[3])/2))
    file=out/'LP_Limbani_Huancasayani_R01.dxf';doc.saveas(file);audit=ezdxf.readfile(file).audit();assert not audit.errors
    index=[]
    for k,page in enumerate(doc.layouts):
        if page.name=='Model':continue
        fig=plt.figure(figsize=(420/25.4,297/25.4));ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
        cfg=Configuration(background_policy=BackgroundPolicy.WHITE,color_policy=ColorPolicy.COLOR)
        Frontend(RenderContext(doc),MatplotlibBackend(ax),config=cfg).draw_layout(page,finalize=True)
        ax.set_xlim(0,420);ax.set_ylim(0,297);ax.set_aspect('equal',adjustable='box');f=png/f'{k:02}-{page.name}.png';fig.savefig(f,dpi=160);plt.close(fig)
        index.append(dict(layout=page.name,png=str(f),pagina=len(index)+1))
    (D/'indice-planos.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
    sys.path.insert(0,'G:/Aquiles/dependencias-linea-primaria')
    from reportlab.pdfgen.canvas import Canvas
    pdf=R/'output/pdf/Linea_Primaria_Limbani_Huancasayani_R01_planos.pdf';canvas=Canvas(str(pdf),pagesize=(420/25.4*72,297/25.4*72));canvas.setTitle('LP-R01 planos académicos editables en DXF/DWG')
    for entry in index:canvas.drawImage(entry['png'],0,0,width=420/25.4*72,height=297/25.4*72);canvas.showPage()
    canvas.save();print('CAD auditado:',len(posts),'bloques de postes;',len(index),'láminas A3; PDF',pdf)
if __name__=='__main__':main()
