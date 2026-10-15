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
    vp.freeze('LP_ID')
    if scale>15000:
        for name in ['LP_ID','LP_POSTES','LP_RETENIDAS','LP_PAT']:vp.freeze(name)
    # Cuadrícula y coordenadas calculadas del mismo viewport, unidades UTM en metros.
    cx=(xmin+xmax)/2;cy=(ymin+ymax)/2;left=center[0]-w/2;bottom=center[1]-h/2
    worldw=w*scale/1000;worldh=h*scale/1000;step=1000 if scale>15000 else 200
    for e in np.arange(math.ceil((cx-worldw/2)/step)*step,cx+worldw/2,step):
        px=center[0]+(e-cx)*1000/scale;line(page,(px,bottom),(px,bottom+h),'CUADRICULA');text(page,f'{e:.0f} E',px+1,bottom+2,2,'CUADRICULA_TEXTO')
    for n in np.arange(math.ceil((cy-worldh/2)/step)*step,cy+worldh/2,step):
        py=center[1]+(n-cy)*1000/scale;line(page,(left,py),(left+w,py),'CUADRICULA');text(page,f'{n:.0f} N',left+1,py+1,2,'CUADRICULA_TEXTO')
    if scale<=15000:
        occupied=[]
        for p in posts:
            px=center[0]+(p['e']-cx)*1000/scale;py=center[1]+(p['n']-cy)*1000/scale
            if not left+3<px<left+w-3 or not bottom+3<py<bottom+h-3:continue
            fun='ESP' if p.get('armado')=='ESP-RET' else {'SUSPENSION':'S','ANGULO':'A','ANCLAJE':'AN','TERMINAL':'T'}[p['estructura']]
            label=p['id']+' '+fun;lw=len(label)*1.35;lh=2.5
            options=[(px+4,py+3),(px-lw-4,py+3),(px+4,py-6),(px-lw-4,py-6),(px+7,py+8),(px-lw-7,py-11)]
            chosen=options[0]
            for tx,ty in options:
                if not (left+2<=tx and tx+lw<=left+w-2 and bottom+3<=ty and ty+lh<=bottom+h-3):continue
                box=(tx,ty,tx+lw,ty+lh+1)
                if any(box[0]<z[2]+1 and box[2]>z[0]-1 and box[1]<z[3]+1 and box[3]>z[1]-1 for z in occupied):continue
                chosen=(tx,ty);break
            tx,ty=chosen;occupied.append((tx,ty,tx+lw,ty+lh+1));line(page,(px,py),(tx,ty+.8),'LP_MAPA_ETIQUETAS');text(page,label,tx,ty,lh,'LP_MAPA_ETIQUETAS')
    text(page,f'Planta 1:{scale} · UTM WGS84 / 19S · EPSG:32719',center[0]-w/2,center[1]-h/2-5,2.3)
    # Norte arriba del modelo; escala gráfica en m.
    x=center[0]+w/2-12;y=center[1]+h/2-25
    line(page,(x,y),(x,y+15));page.add_solid([(x-2,y+11),(x+2,y+11),(x,y+15),(x,y+15)],dxfattribs={'layer':'DETALLE'})
    text(page,'N',x-1.5,y+17,3)
    return scale
def legend(page,x=294,y=251):
    items=[('SUSPENSION','Poste CAC · DGE 09-91-20'),('SE','SE proyectada · DGE 09-90-09'),('PAT','Tierra · DGE 03-31-44'),('RET','Retenida · DGE 09-91-18'),('LINEA','Línea aérea · DGE 09-91-03')]
    text(page,'LEYENDA',x,y,3.2)
    for i,(kind,label) in enumerate(items):
        yy=y-9-i*9;page.add_blockref('LP_'+kind,(x+3,yy),dxfattribs={'xscale':.4,'yscale':.4});text(page,label,x+10,yy-1,2.5)
    text(page,'Un eje = 3 fases; 3 x AAAC 50 mm².',x,y-57,2.4)
    text(page,'Función de armado mediante rótulo:',x,y-64,2.2)
    text(page,'S suspensión / A ángulo / AN anclaje / T terminal',x,y-70,2.1)
    text(page,'Armados RD024: detalles de estudio.',x,y-76,2.2)
    text(page,'ESP: armado especial para ángulo >90°.',x,y-82,2.2)
def main():
    out=O/'cad';out.mkdir(parents=True,exist_ok=True);png=R/'build'/P.name/'lp-r01/planos';png.mkdir(parents=True,exist_ok=True)
    doc=ezdxf.new('R2018');doc.units=units.M;doc.header['$INSUNITS']=6;doc.header['$MEASUREMENT']=1
    doc.styles.new('Arial',dxfattribs={'font':'arial.ttf'})
    layers={'LP_EJE':1,'LP_POSTES':1,'LP_ID':7,'LP_MAPA_ETIQUETAS':7,'LP_RETENIDAS':34,'LP_PAT':3,'LP_SE':5,'LP_CRUCES':5,'BASE_CASAS':8,'BASE_VIAS':8,'BASE_AGUA':4,'ROTULO':7,'DETALLE':7,'CUADRICULA':8,'CUADRICULA_TEXTO':8,'PERFIL_TERRENO':32,'PERFIL_CONDUCTOR':1}
    for name,col in layers.items():doc.layers.new(name,dxfattribs={'color':col,'lineweight':25 if name.startswith('LP_') else 13})
    for name,rgb in [('BASE_CASAS',(170,170,170)),('BASE_VIAS',(185,185,185)),('BASE_AGUA',(65,155,215)),('LP_EJE',(170,25,30)),('PERFIL_TERRENO',(130,95,60)),('PERFIL_CONDUCTOR',(180,20,20)),('LP_ID',(60,45,45)),('CUADRICULA',(225,225,225)),('CUADRICULA_TEXTO',(140,140,140))]:doc.layers.get(name).rgb=rgb
    for kind in ['SUSPENSION','ANGULO','ANCLAJE','TERMINAL','SE','PAT','RET','LINEA']:
        b=doc.blocks.new('LP_'+kind)
        if kind in ['SUSPENSION','ANGULO','ANCLAJE','TERMINAL']:
            # El material CAC se representa siempre por círculo, sin alterar el glifo por función.
            hatch=b.add_hatch(dxfattribs={'true_color':16777215});hatch.paths.add_polyline_path([(4*math.cos(t),4*math.sin(t)) for t in np.linspace(0,2*math.pi,41)[:-1]],is_closed=True)
            b.add_circle((0,0),4)
        elif kind=='SE':
            b.add_lwpolyline([(-5,-3),(5,-3),(5,3),(-5,3)],close=True);b.add_lwpolyline([(5,3),(-5,0),(5,-3)])
        elif kind=='PAT':
            b.add_line((0,3),(0,0))
            for j in range(3):b.add_line((-3+j,-j),(3-j,-j))
        elif kind=='RET':
            b.add_line((0,0),(10.6,0));b.add_lwpolyline([(8.8,-1.7),(10.6,0),(8.8,1.7)])
        elif kind=='LINEA':b.add_line((-6,0),(6,0));b.add_line((-1.5,-2),(1.5,2));b.add_text('3',dxfattribs={'insert':(0,3),'height':2.5})
        if kind in ['SUSPENSION','ANGULO','ANCLAJE','TERMINAL']:
            for tag in ['ID','ESTRUCTURA','ARMADO','E','N','POSTE_M']:b.add_attdef(tag,insert=(0,0),height=1,dxfattribs={'flags':1})
        elif kind=='SE':b.add_attdef('ID',insert=(0,0),height=1,dxfattribs={'flags':1})
    ms=doc.modelspace();coords=A['geometria']['coordinates']
    ms.add_lwpolyline(coords,dxfattribs={'layer':'LP_EJE'})
    # Un único eje cartográfico: tres conductores explicitados en leyenda y detalles.
    housefile=D/'casas-originales.geojson'
    if not housefile.exists():housefile=R/'build'/P.name/'lp-r01/investigacion/casas-originales.geojson'
    houses=json.loads(housefile.read_text(encoding='utf-8'))
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
        ins.add_auto_attribs({tag:str(p[key]) for tag,key in [('ID','id'),('ESTRUCTURA','estructura'),('ARMADO','armado'),('E','e'),('N','n'),('POSTE_M','poste_m')]})
        # Rótulos fuera del punto medido; centros de bloques conservan las coordenadas.
        i=int(p['id'][1:]);function={'SUSPENSION':'S','ANGULO':'A','ANCLAJE':'AN','TERMINAL':'T'}[p['estructura']]
        if p['armado']=='ESP-RET':function='ESP'
        text(ms,p['id']+' '+function,p['e']+8,p['n']+(8 if i%2 else -16),9,'LP_ID')
        ms.add_blockref('LP_PAT',(p['e']+6,p['n']-6),dxfattribs={'layer':'LP_PAT','xscale':.6,'yscale':.6})
    for g in A['retenidas']:
        p=next(p for p in posts if p['id']==g['poste']);dx=g['e']-p['e'];dy=g['n']-p['n']
        ms.add_blockref('LP_RET',(p['e'],p['n']),dxfattribs={'layer':'LP_RETENIDAS','rotation':math.degrees(math.atan2(dy,dx)),'xscale':math.hypot(dx,dy)/10.6,'yscale':math.hypot(dx,dy)/10.6})
    for cross in A.get('cruces',[]):text(ms,cross['id']+' '+cross['tipo'],cross['e']+10,cross['n']+15,9,'LP_CRUCES')
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
        text(page,'Curva roja: conductor caliente 75°C',294,121,2.3);text(page,'Terreno: envolvente DEM, no topografía',294,115,2.3)
        xmin=ps[0]['progresiva_m'];xmax=ps[-1]['progresiva_m'];zz=[p['z_dem_m'] for p in ps];zmin=min(zz)-5;zmax=max(zz)+25
        hs=math.ceil((xmax-xmin)/.263/500)*500;vs=math.ceil((zmax-zmin)/.048/250)*250
        def px(s):return 16+(s-xmin)*1000/hs
        def py(z):return 35+(z-zmin)*1000/vs
        rect(page,15,34,265,50,'DETALLE')
        for i in indices:
            v=spans[i];pa=posts[i];pb=posts[i+1];prof=v['perfil'];chain=pa['progresiva_m']+np.array(prof['fraction'])*v['longitud_m']
            for key,lay in [('terreno_dem_m','PERFIL_TERRENO'),('conductor_m','PERFIL_CONDUCTOR')]:
                page.add_lwpolyline([(px(s),py(z)) for s,z in zip(chain,prof[key])],dxfattribs={'layer':lay})
        for p in ps:line(page,(px(p['progresiva_m']),py(p['z_dem_m'])),(px(p['progresiva_m']),py(p['z_dem_m']+p['amarre_m'])))
        text(page,f'Perfil H 1:{hs} / V 1:{vs} | elevaciones DEM m | fases extremas/viento',16,87,2.3)
        text(page,f"{xmin:.1f} m / {zmin:.1f} m",16,28,2.2);text(page,f"{xmax:.1f} m / {zmax:.1f} m",205,28,2.2)
        text(page,'APOYOS: ID / poste m / función / retenidas',294,105,2.4)
        for j,p in enumerate(ps):
            f={'SUSPENSION':'S','ANGULO':'A','ANCLAJE':'AN','TERMINAL':'T'}[p['estructura']]
            if p['armado']=='ESP-RET':f='ESP'
            text(page,f"{p['id']}     {p['poste_m']}      {f}       {p['retenidas_num']}",294,98-j*4.1,2.2)
    page=frame(doc,'LP-UNIFILAR','Diagrama unifilar, límites y protecciones | SIN ESCALA','LP-E01')
    y=210
    for x,label in [(35,'G: ref. 200 kW'),(110,'T1: 250 kVA'),(185,'10 kV: LP'),(265,'T2: 250 kVA'),(365,'Huancasayani')]:text(page,label,x-18,y+28,3)
    page.add_circle((35,y),10,dxfattribs={'layer':'DETALLE'});text(page,'GS',28,y-2,5)
    # Líneas se interrumpen en contactos; círculo por devanado (DGE06-62-01).
    for a,b in [(45,64),(79,90),(124,139),(154,224),(239,246),(280,310),(325,382)]:line(page,(a,y),(b,y))
    page.add_circle((102,y),9);page.add_circle((115,y),9);page.add_circle((258,y),9);page.add_circle((271,y),9)
    for x,name in [(70,'QG'),(145,'Q1'),(230,'Q2'),(316,'QBT')]:
        line(page,(x-6,y),(x-1,y));line(page,(x-1,y),(x+4,y+3));line(page,(x+5,y),(x+9,y))
        line(page,(x-2.2,y-1.2),(x+.2,y+1.2));line(page,(x-2.2,y+1.2),(x+.2,y-1.2));text(page,name,x-5,y-14,2.8)
    text(page,'DGE: GS06-61-05; T06-62-01; contacto07-71-01 + función automática07-70-02.',20,40,2.5)
    for j,s in enumerate(['Generación y T1: 380 V / 10 kV; antecedentes sin placas verificadas.','T2: 10 kV / 380-220 V, Dyn11 propuesto; 250 kVA garantizados a altitud.','Q1: 50/51 + 51V; Q2: 87T, 50/51, 51V de respaldo. 59N/64 en MT.','MT delta: zigzag + NGR 5 A / 10 s propuesto en SE-LIM; R ~1155 ohm.','Generador: 27/59, 81, 46, 32, AVR y regulador; ajustes sujetos a curvas reales.','En llegada: tablero 400 A, medición, maniobra y protección BT, sin diseño de redes de usuarios.','Falla sostenida estimada ~7.7 A MT: 50/51 solos NO garantizan despeje.','Capacidad LP 250 kVA; demanda usuarios 171.5 kW; generación necesaria ~183.3 kW.','Toma efectiva +5% propuesta T1: salida MT 10.18 kV, llegada BT 371.1 V.','Reserva para Limbani no confirmada; el transporte disponible depende del recurso y despacho.']):text(page,s,20,165-j*10,3)
    page=frame(doc,'LP-ESTRUCTURAS','Estructuras, retenidas y separaciones | ESQUEMAS SIN ESCALA','LP-M01')
    for k,kind in enumerate(['SUSPENSION','ANGULO','ANCLAJE','TERMINAL']):
        x=55+k*99;line(page,(x,150),(x,240));line(page,(x-25,230),(x+25,230))
        for dx in [-25,0,25]:page.add_circle((x+dx,235),2.5)
        if kind!='SUSPENSION':line(page,(x,235),(x-40,150));line(page,(x,235),(x+40,150))
        text(page,kind,x-25,258,3);text(page,'1.2 m entre fases',x-28,244,2.7)
        text(page,'CAC 13 / 15 / 17 m',x-32,133,2.7);text(page,'600 daN tipo, por certificar',x-36,125,2.3)
    for j,s in enumerate(['Referencias RD024-2003: 004 suspensión, 008 angular, 012/016 ángulos mayores, 020 anclaje.','En LP-R01 los ángulos >5° se retienen; la función no cambia el círculo de poste CAC.','ESP: P003 / P035 / P057, ángulos >90°, armado especial de dos retenciones y puentes.','ESP no se atribuye a láminas012/016: proveedor debe verificar herrajes y separación de fases.','Retenidas independientes por ramal a45° de estudio; resistencia y cargas según CSV.','Suelo, bloques, capacidad axial y alturas13/15/17m requieren certificados y campo.','MargenDEM7.5m; aislamiento/descargadores garantizados a altitud hasta4000m.']):text(page,s,20,107-j*11,3)
    page=frame(doc,'LP-TIERRAS','Puesta a tierra y subestaciones de llegada/salida | ESQUEMAS SIN ESCALA','LP-E02')
    rect(page,35,145,105,105,'DETALLE')
    for j in [1,2]:line(page,(35+j*35,145),(35+j*35,250));line(page,(35,145+j*35),(140,145+j*35))
    for x,y in [(35,145),(35,250),(140,145),(140,250)]:page.add_circle((x,y),2);text(page,'2.4m',x+4,y,2.5)
    text(page,'Malla SE 10 x 10 m · Cu 35 mm²',35,258,3);text(page,'Paso ~3.33m, profundidad propuesta 0.6m',35,134,2.6)
    rect(page,240,160,130,85,'DETALLE');rect(page,255,180,45,35,'DETALLE');text(page,'Transformador',253,224,3);rect(page,321,180,25,35,'DETALLE');text(page,'Celda',319,224,3)
    text(page,'Plataforma propuesta 6x4 m',240,253,3)
    for j,s in enumerate(['Cuatro varillas de 2.4m por SE; unir masas, cerco y descargadores bajo evaluación de tensiones.','PAT postes: dos varillas 2.4m / 16mm, enlace Cu 25mm² propuesto; no neutro MT continuo.','No equivale a garantía de 25 ohm: requiere resistividad Wenner y potenciales de paso/contacto.','NGR conecta neutro del zigzag a malla SE-LIM; no sustituye puesta a tierra de masas.','Clase de aislamiento 24kV propuesta para operación 10kV; proveedor debe garantizar a altitud.','Plano civil, derrames, drenaje, cerco y distancias internas pendientes de catálogo/geotecnia.']):text(page,s,20,111-j*12,3)
    page=frame(doc,'LP-PROTECCIONES','Control, disparos y neutro MT | ESQUEMA FUNCIONAL SIN ESCALA','LP-E03')
    text(page,'Bloques funcionales identificados; la simbología eléctrica principal está en LP-E01.',20,255,2.8)
    line(page,(22,235),(393,235));text(page,'SE-LIM / Q1',25,242,3);text(page,'LP 10 kV · 3 fases',168,242,3);text(page,'SE-HUA / Q2 / T2',305,242,3)
    rect(page,30,165,113,40,'DETALLE');text(page,'MEDICIÓN Y CONTROL CABEZA',35,194,3)
    for j,s in enumerate(['TC/TT1: I, U y diferencial87T1','50/51 +51V; 27/59; 59N/64','DisparoQ1 / respaldoQG / alarma']):text(page,s,35,184-j*7,2.7)
    rect(page,262,165,132,40,'DETALLE');text(page,'MEDICIÓN Y CONTROL LLEGADA',267,194,3)
    for j,s in enumerate(['TC/TT2 y BT: I, U; 87T2','51V +50/51; maniobraQ2/QBT','Disparo local; comunicaciones/alarma']):text(page,s,267,184-j*7,2.7)
    for x in [90,325]:line(page,(x,235),(x,205));text(page,'I/U',x+3,218,2.5)
    rect(page,175,172,55,35,'DETALLE');text(page,'ZT: ZIGZAG',178,195,3);text(page,'Bloque funcional',178,185,2.5);text(page,'MT3F / neutroN',178,176,2.5)
    line(page,(202,235),(202,207));line(page,(202,172),(202,160));text(page,'N',208,160,3)
    rect(page,195,135,15,25,'DETALLE');text(page,'NGR',215,148,3);text(page,'1155 Ω · 5 A / 10 s',215,140,2.7)
    line(page,(202,135),(202,117));page.add_blockref('LP_PAT',(202,114),dxfattribs={'xscale':1.2,'yscale':1.2});text(page,'MallaSE-LIM',215,114,2.7)
    rect(page,30,113,125,35,'DETALLE');text(page,'CONTROL DE TIERRA Y NGR',35,139,3);text(page,'CBCT / U0 / continuidadNGR',35,130,2.7);text(page,'59N/64 → disparoQ1 / alarma',35,121,2.7)
    line(page,(155,131),(195,148));text(page,'I0/U0',164,143,2.5)
    for j,s in enumerate(['Estudio de selectividad: llegada0.20s, cabeza0.60s, generador0.90s; valores provisionales.','51V exige supervisiónU<0.70pu y corrientes de arranque/decremento comprobadas, sin ajustes aprobados.','MTsin neutro corrido; tierra de masas y neutro artificial son funciones diferentes.','Control y disparo con alimentaciónDC respaldada; capacidad de batería/UPS por fabricante.','Energizar sin carga y verificar inrush de ambosTX, regulaciónAVR y frecuencia antes de conectar usuarios.']):text(page,s,20,94-j*12,2.8)
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
        index.append(dict(layout=page.name,png=f.relative_to(R).as_posix(),pagina=len(index)+1))
    (D/'indice-planos.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
    sys.path.insert(0,'G:/Aquiles/dependencias-linea-primaria')
    from reportlab.pdfgen.canvas import Canvas
    pdf=R/'output/pdf/Linea_Primaria_Limbani_Huancasayani_R01_planos.pdf';canvas=Canvas(str(pdf),pagesize=(420/25.4*72,297/25.4*72));canvas.setTitle('LP-R01 planos académicos editables en DXF/DWG')
    for entry in index:canvas.drawImage(str(R/entry['png']),0,0,width=420/25.4*72,height=297/25.4*72);canvas.showPage()
    canvas.save();print('CAD auditado:',len(posts),'bloques de postes;',len(index),'láminas A3; PDF',pdf)
if __name__=='__main__':main()
