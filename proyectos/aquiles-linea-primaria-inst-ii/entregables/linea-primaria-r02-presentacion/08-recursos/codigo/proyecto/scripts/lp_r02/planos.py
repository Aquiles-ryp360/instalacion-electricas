"""CAD georreferenciado y láminas A3; PDF se renderiza del propio DXF."""
from pathlib import Path
from prosa import humano
import json,math,zipfile,xml.etree.ElementTree as ET
import numpy as np
import ezdxf
from ezdxf.enums import TextEntityAlignment
from ezdxf.addons.drawing import Frontend,RenderContext,layout
from ezdxf.addons.drawing.pymupdf import PyMuPdfBackend,PyMuPdfRenderBackend
import pymupdf,copy
from ezdxf.addons.drawing.config import Configuration,BackgroundPolicy,ColorPolicy
from ezdxf.math import BoundingBox2d
from pypdf import PdfReader,PdfWriter
from pyproj import Transformer
from ezdxf.fonts import fonts
from shapely.geometry import LineString,box as geom_box

class ExactA3Backend(PyMuPdfBackend):
    """Conserva milímetros exactos: ezdxf1.4.5 trunca el tamañoPDF a puntos enteros."""
    @staticmethod
    def make_backend(page,settings):
        backend=PyMuPdfRenderBackend(page,settings)
        backend.page_width_in_pt=page.width_in_mm*72/25.4
        backend.page_height_in_pt=page.height_in_mm*72/25.4
        backend.page.set_mediabox(pymupdf.Rect(0,0,backend.page_width_in_pt,backend.page_height_in_pt))
        backend.content_shape=backend.page.new_shape()
        return backend
    def get_replay(self,page,*,settings=layout.Settings(),render_box=None):
        player=self.player()
        if render_box is None:render_box=player.bbox()
        output_layout=layout.Layout(render_box,flip_y=self._init_flip_y)
        page=output_layout.get_final_page(page,settings)
        settings=copy.copy(settings)
        settings.output_coordinate_space=max(page.width_in_mm,page.height_in_mm)*72/25.4
        player.transform(output_layout.get_placement_matrix(page,settings=settings,top_origin=True))
        if settings.crop_at_margins:
            p1,p2=page.get_margin_rect(top_origin=True);scale=settings.page_output_scale_factor(page)
            player.crop_rect(p1*scale,p2*scale,.1*72/25.4)
        self._init_flip_y=False;backend=self.make_backend(page,settings);player.replay(backend)
        return backend

COL={'TEXTO':0x163B55,'EJE':0x087F8C,'POSTES':0x244C65,'ALERTA':0xC56B20,'TERRENO':0x777777,'CABLE':0x087F8C,'RETENIDA':0xA77738,'GRILLA':0xD2DCE3,'MARCO':0x163B55,'CASAS':0xC9C9C9,'AGUA':0x5BA3C5,'VIA':0xA7A7A7}

def texto(l,s,x,y,h=2.4,layer='TEXTO',rot=0):
    return l.add_text(humano(s),dxfattribs={'height':h,'style':'LP-TEXTO','layer':layer,'rotation':rot}).set_placement((x,y))
def linea(l,pts,layer='EJE',close=False):return l.add_lwpolyline(pts,close=close,dxfattribs={'layer':layer})
def caja(l,x,y,w,h,layer='MARCO'):linea(l,[(x,y),(x+w,y),(x+w,y+h),(x,y+h)],layer,True)
def nota(l,s,x,y,width=85,h=2.3):
    font=fonts.make_font('DejaVuSans.ttf',cap_height=h)
    words=humano(s).split();lines=[];line=''
    for word in words:
        trial=(line+' '+word).strip()
        if line and font.text_width(trial)>width:
            lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    for row in lines:texto(l,row,x,y,h);y-=h*1.55
    return y-3

def marco(doc,code,title,scale='S/E'):
    l=doc.layouts.new(code);l.page_setup(size=(420,297),margins=(0,0,0,0),units='mm')
    caja(l,10,10,400,277);linea(l,[(10,42),(410,42)],'MARCO');linea(l,[(10,274),(410,274)],'MARCO')
    texto(l,'LÍNEA PRIMARIA LIMBANI – HUANCASAYANI',16,279,4);texto(l,title,16,265,3.2)
    texto(l,code,356,280,4);texto(l,'LP-R02 | 18/10/2026',323,269,2.2)
    texto(l,'INSTALACIONES ELÉCTRICAS II | Aquiles Taylor Ramos Yapo | 227368',16,32,2.7)
    texto(l,'REVISIÓN ACADÉMICA · CAMPO, EQUIPOS Y PREDIOS PENDIENTES',16,23,2.7,'ALERTA')
    texto(l,'UTM WGS84 / 19S · EPSG:32719 | Modelo CAD en metros',16,15,2.)
    texto(l,'Escala al imprimir A3: '+scale,287,15,2.)
    return l

def map_transform(ps,box,scale=None):
    x,y,w,h=box;xx=[p['e'] for p in ps];yy=[p['n'] for p in ps];dx=max(xx)-min(xx);dy=max(yy)-min(yy)
    need=max(dx/max(w-14,1),dy/max(h-14,1)) # m por mm = escala /1000
    if scale is None:scale=next((v for v in [1,2,2.5,5,7.5,10,15,20,25,30,50] if v>=need),math.ceil(need/10)*10)
    cx=(max(xx)+min(xx))/2;cy=(max(yy)+min(yy))/2
    return lambda e,n:(x+w/2+(e-cx)/scale,y+h/2+(n-cy)/scale),int(scale*1000)

def dibujar_mapa(l,ps,allp,guys,box,extra=None):
    transform,scale=map_transform(ps,box);x,y,w,h=box;caja(l,x,y,w,h,'GRILLA')
    if extra:
        clip=geom_box(x+1,y+1,x+w-1,y+h-1)
        for feature in extra.get('features',[]):
            g=feature.get('geometry') or {};pts=g.get('coordinates',[])
            if g.get('type')!='LineString' or len(pts)<2:continue
            tp=[transform(*p[:2]) for p in pts]
            clipped=LineString(tp).intersection(clip)
            parts=list(clipped.geoms) if hasattr(clipped,'geoms') else [clipped]
            cl=feature['properties'].get('clase')
            layer='TERRENO' if cl=='curva_dem' else ('AGUA' if cl in ['river','stream'] else 'VIA')
            for part in parts:
                if part.geom_type=='LineString' and part.length>0:linea(l,list(part.coords),layer)
    cx=(max(p['e'] for p in ps)+min(p['e'] for p in ps))/2
    cy=(max(p['n'] for p in ps)+min(p['n'] for p in ps))/2
    sm=scale/1000;step=1000 if scale>=15000 else 200
    for east in np.arange(math.ceil((cx-w*sm/2)/step)*step,cx+w*sm/2,step):
        gx,_=transform(east,cy);linea(l,[(gx,y+1),(gx,y+h-1)],'GRILLA');texto(l,f'E{east:.0f}',gx+1,y+h-3,1.5)
    for north in np.arange(math.ceil((cy-h*sm/2)/step)*step,cy+h*sm/2,step):
        _,gy=transform(cx,north);linea(l,[(x+1,gy),(x+w-1,gy)],'GRILLA');texto(l,f'N{north:.0f}',x+1,gy+1,1.5)
    linea(l,[transform(p['e'],p['n']) for p in ps],'EJE')
    ids={p['id'] for p in ps}
    for g in guys:
        if g['poste'] not in ids:continue
        p=next(p for p in ps if p['id']==g['poste']);linea(l,[transform(p['e'],p['n']),transform(g['e'],g['n'])],'RETENIDA')
    labels=[]
    for i,p in enumerate(ps):
        a,b=transform(p['e'],p['n']);layer='ALERTA' if p['vertical_min_kN']<0 else 'POSTES'
        l.add_circle((a,b),.7,dxfattribs={'layer':layer})
        if len(ps)<=40 or i%5==0 or i in [0,len(ps)-1] or p['angulo_deg']>90:labels.append([b,a,p,layer])
    labels.sort(key=lambda row:row[0]);last=y+3
    for row in labels:row.append(max(last,row[0]));last=row[4]+2.9
    overflow=max(0,last-(y+h-3))
    for b,a,p,layer,labely in labels:
        labely-=overflow;labelx=min(x+w-14,a+3)
        if abs(labely-b)>1:linea(l,[(a,b),(labelx-.6,labely)],'GRILLA')
        texto(l,p['id'],labelx,labely,1.8,layer)
    texto(l,'N',x+w-10,y+h-11,3);linea(l,[(x+w-9,y+h-23),(x+w-9,y+h-14)],'TEXTO');linea(l,[(x+w-11,y+h-17),(x+w-9,y+h-14),(x+w-7,y+h-17)],'TEXTO')
    meters=100 if scale<=10000 else 500;length=meters/(scale/1000)
    linea(l,[(x+7,y+7),(x+7+length,y+7)],'TEXTO');texto(l,f'{meters} m',x+7,y+10,1.9)
    texto(l,f'1:{scale}',x+w-30,y+5,2)
    return scale

def planos(P,O,r):
    F=O/'04-planos';F.mkdir(parents=True,exist_ok=True);doc=ezdxf.new('R2018');doc.units=6
    for name,col in COL.items():doc.layers.new(name,dxfattribs={'true_color':col,'lineweight':18 if name in ['EJE','CABLE'] else 13})
    doc.styles.new('LP-TEXTO',dxfattribs={'font':'DejaVuSans.ttf'})
    model=doc.modelspace();ps=r['postes'];guys=r['retenidas'];linea(model,[(p['e'],p['n']) for p in ps],'EJE')
    b=doc.blocks.new('LP_POSTE_R02');b.add_circle((0,0),1,dxfattribs={'layer':'POSTES'})
    for j,tag in enumerate(['ID','POSTE_M','TIPO','DC','ESTADO']):b.add_attdef(tag,(2,-j*2),height=1.5)
    for p in ps:
        ins=model.add_blockref('LP_POSTE_R02',(p['e'],p['n']),dxfattribs={'layer':'POSTES'})
        ins.add_auto_attribs({'ID':p['id'],'POSTE_M':str(p['poste_m']),'TIPO':p['tipo_r02'],'DC':f'{p["DC_propuesta"]:.4f}','ESTADO':'CANDIDATO; CAMPO/AXIAL/SUELO PENDIENTES'})
    for g in guys:
        p=next(p for p in ps if p['id']==g['poste']);linea(model,[(p['e'],p['n']),(g['e'],g['n'])],'RETENIDA')
    for p,name in [(ps[0],'SE-LIM'),(ps[-1],'SE-HUA')]:
        caja(model,p['e']-3,p['n']-2,6,4,'POSTES');texto(model,name+' PROPUESTA',p['e']+5,p['n']+3,3)
    extra=json.loads((P/'datos/lp-r01/referencias-osm.geojson').read_text())
    curves=json.loads((P/'datos/lp-r01/curvas-dem.geojson').read_text())
    for f in curves['features']:
        if f['properties'].get('elev_m',0)%100==0:
            extra['features'].append(dict(type='Feature',geometry=f['geometry'],properties=dict(clase='curva_dem')))
    l=marco(doc,'LP-01','Planta general del corredor candidato','según barra');dibujar_mapa(l,ps,ps,[],(15,50,270,204),extra)
    y=250
    for text in [f'Un solo eje representa la terna: 3 x AAAC 50 mm2. Longitud horizontal {r["longitud_horizontal_m"]:.2f} m.',f'{len(ps)} apoyos y {len(r["vanos"])} vanos. Las posiciones se conservan para revisar la propuesta R01.', 'Círculo naranja: apoyo con carga ascendente en algún estado. No indica aprobación o rechazo de la cimentación.', 'Cotas: DEM de gabinete heredado, resolución aproximada30 m. No certifica gálibos, cauces ni predios.', 'SE-LIM y SE-HUA: posiciones propuestas. La tensión real queda pendiente de placas y decisión10/22.9 kV.', 'Origen de cartografía: OSM, catastro aportado y DEM deR01. Fuente y hashes en08-recursos.']:
        y=nota(l,text,297,y,104)
    # Unifilar sin ramificaciones y frontera visible.
    l=marco(doc,'LP-02','Unifilar funcional y alternativas de tensión')
    yy=204;nodes=[(38,'G'),(92,'T1'),(194,'LP'),(295,'T2'),(376,'BT')]
    linea(l,[(38,yy),(376,yy)],'EJE');l.add_circle((38,yy),8,dxfattribs={'layer':'POSTES'});texto(l,'G',35,yy-2,4)
    for x,name in [(92,'T1'),(295,'T2')]:
        l.add_circle((x-3,yy),6,dxfattribs={'layer':'POSTES'});l.add_circle((x+3,yy),6,dxfattribs={'layer':'POSTES'});texto(l,name,x-5,yy+13,3)
        texto(l,'250 kVA tipo',x-15,yy-17,2.5)
    for x in [119,265]:caja(l,x-2,yy-3,4,6,'POSTES');texto(l,'Protección',x-10,yy+12,2.1)
    texto(l,'MCH LIMBANI',20,237,3);texto(l,'SE SALIDA',75,237,3);texto(l,'LÍNEA PRINCIPAL SIN RAMALES',143,227,3);texto(l,'SE LLEGADA',275,237,3);texto(l,'HUANCASAYANI',344,237,3)
    texto(l,'380 V tipo',20,177,2.5);texto(l,'3 x AAAC 50 mm2',162,190,3);texto(l,'380/220 V tipo',345,177,2.5)
    y=152
    for text in ['Escenario de compatibilidad: T1 0.38/10 kV y T2 10/0.38 kV, ambas relaciones sin placa verificada.', 'Alternativa rural nueva a estudiar: T1 0.38/22.9 kV y T2 22.9/0.38 kV. Requiere oferta y selección integral de equipos.', '380 V,250 kVA y potencia200 kW son hipótesis del modelo; no datos confirmados de la instalación. La oferta150 kW se contrasta como sensibilidad.', 'Si los devanadosMT son delta, la puesta a tierra del neutroMT exige transformador de puesta a tierra compatible; NGR no puede conectarse a un neutro inexistente.', 'Esquema funcional. Grupos, tomas, relacionesTC/TT, aislamiento y ajustes de protección quedan pendientes. VerCSV de cortocircuito y memoria4.5.']:
        y=nota(l,text,20,y,375,2.6)
    # Comparaciones: tabla legible.
    l=marco(doc,'LP-03','Tensión y pérdidas: separar la línea de la transformación')
    heads=['kV nominal','Fuente pu','MT salida kV','MT llegada kV','BT llegada V','P línea kW','P gener. kW'];xs=[18,72,118,175,233,291,351]
    for x,h in zip(xs,heads):texto(l,h,x,246,2.6)
    for k,f in enumerate(r['comparacion_tensiones']):
        y=232-k*11
        for x,val in zip(xs,[str(f['kV']),f'{f["toma_pu"]:.3f}',f'{f["MT_salida_kV"]:.3f}',f'{f["MT_llegada_kV"]:.3f}',f'{f["BT_llegada_V"]:.1f}',f'{f["perdida_linea_kW"]:.3f}',f'{f["P_generacion_kW"]:.2f}']):texto(l,val,x,y,2.8)
    nota(l,'La fuente1.05pu representa elevación efectiva ideal de estudio. No es una orden de cambio de tap. Sin elevación, el caso10kV presentaBT inferior al objetivo académico±5%. VerificarAVR, tomas, máximos en vacío y pérdidas reales.',18,84,375,2.5)
    # Mecánica de poste.
    l=marco(doc,'LP-04','Poste, retenida y capacidad: esquema de cálculo')
    linea(l,[(82,70),(82,239)],'POSTES');linea(l,[(35,96),(139,96)],'TERRENO');linea(l,[(82,230),(25,96)],'RETENIDA');linea(l,[(82,226),(130,226)],'EJE')
    texto(l,'13 m total',90,198,3);texto(l,'1.9 m supuesto',88,78,2.6);texto(l,'amarre10.6 m',90,216,2.6);texto(l,'guy45 grados',18,159,2.5);texto(l,'Cota de terreno',25,101,2.4)
    y=247
    for t in ['La designación400daN es carga transversal equivalente. No representa peso vertical disponible.', 'M trabajo =4000N x10.95m =43.80kN m. Con rotura2 yphi0.65, M resistente tipo56.94kN m. Para600daN:85.41kN m.', 'Peso de terna85m, sin hielo:34.425kg. TracciónEDS de tres fases en terminal:6615N antes de factores.', 'Por apoyo: sumar vectores de extremos de vanos. No sumar todos los desniveles como pesos positivos.', f'Apoyos con carga ascendente: {r["resumen"]["apoyos_carga_ascendente"]}. Retenciones adicionales propuestas: {r["resumen"]["apoyos_refuerzo_propuesto"]}.', 'Retenida ideal: Tg=Fh/cos45. La comprobación real exige pretensión, rigidez, grapas, varilla, bloque y terreno.', 'No se acota un bloque de cimentación definitivo sin geotecnia. No se certifica capacidad axial por tener600daN transversal.']:
        y=nota(l,t,160,y,238,2.7)
    # Siete hojas planta/perfil con misma tabla por vano.
    chunks=np.array_split(np.arange(len(r['vanos'])),7)
    for k,indices in enumerate(chunks,5):
        start,end=int(indices[0]),int(indices[-1])+1;subset=ps[start:end+1];vs=r['vanos'][start:end]
        l=marco(doc,f'LP-{k:02}',f'Planta y perfil de gabinete: {subset[0]["id"]} – {subset[-1]["id"]}')
        dibujar_mapa(l,subset,ps,guys,(15,170,272,86),extra)
        # Perfil con escalas exactas y exageración vertical declarada.
        x0,y0,w,h=15,55,272,100;ch0=subset[0]['progresiva_m'];ch1=subset[-1]['progresiva_m'];zmin=min(min(v['perfil']['terreno_m']) for v in vs)-3;zmax=max(max(v['perfil']['conductor_m']) for v in vs)+3
        hs=next(v for v in [2.5,5,7.5,10,15,20] if (ch1-ch0)/v<w-12);vscale=next(v for v in [.25,.5,1,2,2.5,5] if (zmax-zmin)/v<h-18)
        def tx(x):return x0+8+(x-ch0)/hs
        def ty(z):return y0+8+(z-zmin)/vscale
        caja(l,x0,y0,w,h,'GRILLA')
        for i,v in enumerate(vs,start):
            xp=[ps[i]['progresiva_m']+f*v['longitud_m'] for f in v['perfil']['fraccion']]
            linea(l,list(zip([tx(x) for x in xp],[ty(z) for z in v['perfil']['terreno_m']])),'TERRENO');linea(l,list(zip([tx(x) for x in xp],[ty(z) for z in v['perfil']['conductor_m']])),'CABLE')
        for p in subset:
            x=tx(p['progresiva_m']);zz=p['cota_dem_m'];linea(l,[(x,ty(zz)),(x,ty(zz+p['amarre_m']))],'POSTES');texto(l,p['id'],x,ty(zz+p['amarre_m'])+1,1.6,rot=90)
        texto(l,f'H 1:{int(hs*1000)} | V 1:{int(vscale*1000)} | CALOR_FINAL75C + fluencia345microstrain',20,158,2)
        for z in np.arange(math.ceil(zmin/20)*20,zmax,20):texto(l,f'{z:.0f}',16,ty(z),1.6)
        for ch in np.arange(math.ceil(ch0/200)*200,ch1,200):texto(l,f'{ch:.0f}',tx(ch),56,1.6)
        y=251
        for text in [f'Progresiva {ch0:.1f}–{ch1:.1f}m. Un solo eje representa tres conductores.', 'Naranja: carga ascendente en algún estado. Retenidas dibujadas como posiciones ideales pendientes.', 'Terreno gris: perfil DEM heredado. Conductor verde: cálculo por vano; no es medición ni gálibo certificado.', 'Las cotas DEM tienen resolución~30m. Topografía lateral y de cruces pendiente.', 'Vanos de esta lámina:']:
            y=nota(l,text,298,y,101,2.2)
        for v in vs:
            if y<60:break
            y=nota(l,f'{v["id"]}: L{v["longitud_m"]:.1f}m, f{v["estados"]["CALOR_FINAL"]["flecha_vertical_m"]:.2f}m',298,y,101,1.9)
    # Tabla111apoyos en páginas de24filas.
    for j in range(0,len(ps),24):
        code=f'LP-{12+j//24:02}';l=marco(doc,code,f'Planilla de apoyos candidatos {j+1}–{min(j+24,len(ps))}')
        xs=[16,40,76,122,165,199,248,283,330,369];heads=['ID','Prog.m','Este m','Norte m','Poste m','Amarre m','Vmin kN','D/C tipo','Ret. ud','Acción']
        for x,s in zip(xs,heads):texto(l,s,x,247,2.2)
        for idx,p in enumerate(ps[j:j+24]):
            y=236-idx*7.1;vals=[p['id'],f'{p["progresiva_m"]:.1f}',f'{p["e"]:.1f}',f'{p["n"]:.1f}',p['poste_m'],f'{p["amarre_m"]:.1f}',f'{p["vertical_min_kN"]:.2f}',f'{p["DC_propuesta"]:.3f}',p['retenidas_r02'],'REV' if p['vertical_min_kN']<0 or p['angulo_deg']>90 else 'CAMPO']
            for x,s in zip(xs,vals):texto(l,str(s),x,y,2.1,'ALERTA' if p['vertical_min_kN']<0 else 'TEXTO')
        texto(l,'D/C bajo capacidades supuestas. Vmin negativa: carga ascendente; capacidad axial, fijaciones y suelo pendientes.',17,54,2.2)
    l=marco(doc,'LP-17','Armados: funciones y esfuerzos que debe verificar el fabricante')
    for center,label in [(95,'SOPORTE RÍGIDO DE PASO'),(290,'RETENCIÓN POR RAMALES')]:
        linea(l,[(center,100),(center,220)],'POSTES');linea(l,[(center-40,211),(center+40,211)],'POSTES')
        texto(l,label,center-55,243,3.)
        for off in [-28,0,28]:
            l.add_circle((center+off,217),2.2,dxfattribs={'layer':'POSTES'})
            linea(l,[(center+off,217),(center+off,231)],'ALERTA')
        texto(l,'Tres fases; separación propuesta1.2 m',center-65,188,2.4)
        texto(l,'Esquema funcional sin despiece de fabricación',center-76,176,2.1,'ALERTA')
    linea(l,[(290,198),(355,100)],'RETENIDA');linea(l,[(290,198),(225,100)],'RETENIDA')
    nota(l,'Paso: verificar grapa/PIN frente a fuerzas ascendentes y longitudinales por vanos desiguales. Retención: verificar dos ramales, puentes, aisladores, crucetas y pernos. No asignar una capacidad de hoja de madera aCAC sin comprobar fijación y sección.',20,82,376,2.6)
    l=marco(doc,'LP-18','Cimentación y puesta a tierra: datos necesarios para dimensionar')
    linea(l,[(70,100),(70,230)],'POSTES');linea(l,[(25,152),(130,152)],'TERRENO');caja(l,47,90,46,62,'GRILLA')
    texto(l,'Dexc y geometría por geotecnia',20,78,2.6);texto(l,'h = empotramiento por cálculo',20,65,2.6)
    y=249
    for t in ['Plantilla de cálculo, no detalle de obra: q suelo, cohesión, fricción, nivel freático, estabilidad de talud y cargas de diseño faltan.', 'Excavación cilíndrica: Vexc=pi xDexc^2 xh/4. Concreto neto: volumen excavado menos volumen real desplazado por el poste. No cerrar metrado sin dimensiones.', 'Anclaje de retenida: verificar arrancamiento, vuelco, deslizamiento, varilla, placa y concreto bajo el tiro delCSV. Los puntos dibujados son posiciones ideales.', 'PAT: medir resistividadWenner; seleccionar geometría, corriente y tiempo de falla. Comprobar paso, contacto, transferencia y cerco. No se garantiza resistencia por un número de varillas.', 'La información geométrica, la capacidad axial y el peso del fabricante deben incorporarse antes de emitir cálculoN-M y cimentación.']:
        y=nota(l,t,151,y,245,2.7)
    l=marco(doc,'LP-19','Cruces cartográficos y verificaciones de campo')
    B=json.loads((P/'datos/lp-r02/geometria-base.json').read_text());xs=[18,55,103,151,212,278]
    for x,head in zip(xs,['ID','Tipo','Vano','Este m','Norte m','Progresiva m']):texto(l,head,x,247,2.8)
    for i,row in enumerate(B['cruces']):
        for x,val in zip(xs,[row['id'],row['tipo'],row['vano'],f'{row["e"]:.2f}',f'{row["n"]:.2f}',f'{row["progresiva_m"]:.2f}']):texto(l,val,x,229-i*15,2.8)
    y=133
    for text in ['Cruces detectados enR01 por intersección con geometríaOSM; no equivalen a permisos ni a inventario exhaustivo de obstáculos.', 'En vía: levantar calzada, bordes, circulación y obstáculos; aplicar elgálibo correspondiente bajo temperatura ybalanceo. En cauce: levantar crecida, faja, talud, socavación yaccesos.', 'Verificar cruces ypredios de los160anclajes ideales deesta revisión; no trasladar las comprobaciones cartográficas de128anclajes deR01 a losanclajes nuevos.', 'Si se desplaza unposte o anclaje, actualizar geometría,cálculo de fuerzas,perfiles,metrados yestas láminas desde una misma revisión.']:
        y=nota(l,text,20,y,373,2.6)
    # Guardar y volver a leer: los PDF se producen del mismo DXF guardado.
    dest=F/'LP_Limbani_Huancasayani_R02.dxf';doc.saveas(dest);doc=ezdxf.readfile(dest);audit=doc.audit()
    if audit.errors:raise ValueError('AuditoríaDXF: '+str(audit.errors))
    cfg=Configuration(background_policy=BackgroundPolicy.WHITE,color_policy=ColorPolicy.COLOR,min_lineweight=.05)
    pdf=PdfWriter();index=[]
    for l in doc.layouts:
        if not l.name.startswith('LP-'):continue
        backend=ExactA3Backend();ctx=RenderContext(doc);Frontend(ctx,backend,config=cfg).draw_layout(l,finalize=True)
        data=backend.get_pdf_bytes(layout.Page(420,297),settings=layout.Settings(fit_page=False,scale=1,output_layers=True),render_box=BoundingBox2d([(0,0),(420,297)]))
        name=F/(l.name+'.pdf');name.write_bytes(data);pdf.append(PdfReader(name));index.append(dict(codigo=l.name,archivo=name.name,formato='A3 420x297mm',estado='REVISION ACADEMICA',origen='Render del layout enDXF guardado'))
    with (F/'Planos_LP_R02_A3.pdf').open('wb') as out:pdf.write(out)
    (F/'indice-planos.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n');(F/'auditoria-dxf.json').write_text(json.dumps(dict(errores=len(audit.errors),correcciones=len(audit.fixes),unidades=doc.units,postes=len(list(doc.modelspace().query('INSERT'))),laminas=len(index)),indent=2))
    # GeoJSON y KMZcon el mismo eje y atributos. No se elevan coordenadas a terreno certificado.
    features=[dict(type='Feature',geometry=dict(type='Point',coordinates=[p['e'],p['n']]),properties=p) for p in ps]
    gj=dict(type='FeatureCollection',crs={'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::32719'}},features=features)
    (F/'postes_R02_UTM19S.geojson').write_text(json.dumps(gj,ensure_ascii=False,indent=2)+'\n')
    route=dict(type='FeatureCollection',crs=gj['crs'],features=[dict(type='Feature',geometry=dict(type='LineString',coordinates=[[p['e'],p['n']] for p in ps]),properties=dict(estado='CANDIDATO; TENSION PENDIENTE',terna='3xAAAC50',revision='LP-R02'))])
    (F/'eje_R02_UTM19S.geojson').write_text(json.dumps(route,ensure_ascii=False,indent=2)+'\n')
    ns='http://www.opengis.net/kml/2.2';ET.register_namespace('',ns);root=ET.Element('{'+ns+'}kml');d=ET.SubElement(root,'Document');ET.SubElement(d,'name').text='LP-R02 · revisión de gabinete'
    t=Transformer.from_crs(32719,4326,always_xy=True)
    pm=ET.SubElement(d,'Placemark');ET.SubElement(pm,'name').text='Terna candidata · tensión pendiente';ls=ET.SubElement(pm,'LineString');ET.SubElement(ls,'tessellate').text='1';ET.SubElement(ls,'coordinates').text=' '.join(f'{t.transform(p["e"],p["n"])[0]:.9f},{t.transform(p["e"],p["n"])[1]:.9f},0' for p in ps)
    for p in ps:
        pm=ET.SubElement(d,'Placemark');ET.SubElement(pm,'name').text=p['id']+' / '+p['tipo_r02'];ET.SubElement(pm,'description').text=f'Gabinete. Poste{p["poste_m"]}m. Vmin{p["vertical_min_kN"]:.3f}kN. {p["acciones"]}. Sin validación de terreno.';pt=ET.SubElement(pm,'Point');lon,lat=t.transform(p['e'],p['n']);ET.SubElement(pt,'coordinates').text=f'{lon:.9f},{lat:.9f},0'
    kml=ET.tostring(root,encoding='utf-8',xml_declaration=True);(F/'LP_R02.kml').write_bytes(kml)
    with zipfile.ZipFile(F/'LP_R02.kmz','w',zipfile.ZIP_DEFLATED) as z:z.writestr('doc.kml',kml)
    return index
