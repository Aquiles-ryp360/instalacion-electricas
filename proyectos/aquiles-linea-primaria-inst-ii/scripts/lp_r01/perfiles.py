"""Perfiles explícitos de terreno, apoyos y vanos; cotas de modelo público."""
from pathlib import Path
import json,math,sys
import numpy as np
import ezdxf
P=Path(__file__).resolve().parents[2];R=P.parents[1];D=P/'datos/lp-r01';O=R/'output/linea-primaria-limbani-huancasayani';B=R/'build'/P.name/'lp-r01'
sys.path.insert(0,str(Path(__file__).parent));sys.path.insert(0,'G:/Aquiles/dependencias-linea-primaria')
from cad import frame,text,line,rect
from trazado import elevation
from reportlab.pdfgen.canvas import Canvas
from PIL import Image

def detail(page,v,pa,pb,x,y,w,h,doc):
    frac=np.array(v['perfil']['fraction']);chain=frac*v['longitud_m'];g=np.array(v['perfil']['terreno_dem_m']);z=np.array(v['perfil']['conductor_m'])
    lo=math.floor(min(g)/5)*5-2;hi=max(z)+3;hs=math.ceil(v['longitud_m']/(w/1000)/100)*100;vs=math.ceil((hi-lo)/(h/1000)/100)*100
    px=lambda s:x+s*1000/hs;py=lambda zz:y+(zz-lo)*1000/vs
    rect(page,x-1,y-1,w+2,h+2,'DETALLE')
    for vals,layer in [(g,'PERFIL_TERRENO'),(z,'PERFIL_CONDUCTOR')]:page.add_lwpolyline([(px(a),py(b)) for a,b in zip(chain,vals)],dxfattribs={'layer':layer})
    chord=(1-frac)*z[0]+frac*z[-1]
    line(page,(px(chain[0]),py(chord[0])),(px(chain[-1]),py(chord[-1])),'PF_COTA')
    fi=int(np.argmax(chord-z));fx=px(chain[fi]);line(page,(fx,py(z[fi])),(fx,py(chord[fi])),'PF_COTA')
    idx=int(np.argmin(z-g));xx=px(chain[idx]);line(page,(xx,py(g[idx])),(xx,py(z[idx])),'PF_COTA')
    text(page,f'g75 = {min(z-g):.2f} m',x,y-8,2.4);text(page,f'f75 = {v["estados"]["CALOR_FINAL"]["flecha_vertical_m"]:.2f} m',x,y-14,2.4)
    text(page,f'H 1:{hs} / V 1:{vs}',x,y+h+7,2.3)

def main():
    a=json.loads((D/'resultados.json').read_text(encoding='utf-8'));posts=a['postes'];spans=a['vanos'];f=O/'cad/LP_Limbani_Huancasayani_R01.dxf';doc=ezdxf.readfile(f)
    for name,color in [('PF_GRID',8),('PF_COTA',5),('PF_UMBRAL',30),('PF_EJE_DEM',3),('PF_COMPACTO',7)]:
        if name not in doc.layers:doc.layers.new(name,dxfattribs={'color':color,'lineweight':0})
    summaries=[]
    for k in range(math.ceil(a['linea_longitud_m']/1000)):
        low=k*1000;high=min((k+1)*1000,a['linea_longitud_m']);idx=[i for i,v in enumerate(spans) if posts[i+1]['progresiva_m']>=low and posts[i]['progresiva_m']<=high]
        ps=posts[idx[0]:idx[-1]+2];ss=[spans[i] for i in idx];xmin=ps[0]['progresiva_m'];xmax=ps[-1]['progresiva_m'];zlo=math.floor(min(min(s['perfil']['terreno_dem_m']) for s in ss)/50)*50;zhi=math.ceil(max(max(s['perfil']['conductor_m']) for s in ss)/50)*50+25
        hs=math.ceil((xmax-xmin)/.252/250)*250;vs=math.ceil((zhi-zlo)/.153/250)*250
        name=f'LP-PF-{k+1:02}'
        if name in doc.layouts:doc.layouts.delete(name)
        page=frame(doc,name,f'Perfil longitudinal y detalle de vanos | tramo {k+1}/7 | DEM ~30m',f'PF-{k+1:02}')
        x0,y0,w,h=32,96,252,153;px=lambda s:x0+(s-xmin)*1000/hs;py=lambda z:y0+(z-zlo)*1000/vs
        rect(page,x0,y0,w,h,'DETALLE')
        for z in np.arange(zlo,zhi+1,50):
            if py(z)>y0+h:continue
            line(page,(x0,py(z)),(x0+w,py(z)),'PF_GRID');text(page,f'{z:.0f}',14,py(z)-1,2.2)
        for ch in np.arange(math.ceil(xmin/100)*100,xmax+1,100):
            line(page,(px(ch),y0),(px(ch),y0+h),'PF_GRID');text(page,f'{ch/1000:.2f}',px(ch)-3,y0-7,2)
        for i in idx:
            v=spans[i];pa,pb=posts[i],posts[i+1];prof=v['perfil'];frac=np.array(prof['fraction']);ch=pa['progresiva_m']+frac*v['longitud_m']
            for key,layer in [('terreno_dem_m','PERFIL_TERRENO'),('conductor_m','PERFIL_CONDUCTOR')]:page.add_lwpolyline([(px(s),py(z)) for s,z in zip(ch,prof[key])],dxfattribs={'layer':layer})
            centre=[elevation(pa['e']+t*(pb['e']-pa['e']),pa['n']+t*(pb['n']-pa['n'])) for t in frac]
            page.add_lwpolyline([(px(s),py(z)) for s,z in zip(ch,centre)],dxfattribs={'layer':'PF_EJE_DEM'})
        for j,p in enumerate(ps):
            x=px(p['progresiva_m']);g=py(p['z_dem_m']);z=py(p['z_dem_m']+p['amarre_m']);line(page,(x,g),(x,z),'DETALLE');page.add_circle((x,z),.6,dxfattribs={'layer':'DETALLE'})
            ly=min(y0+h-3,z+5+(j%3)*4);text(page,p['id'],x-3,ly,1.8);line(page,(x,z),(x,ly-.6),'PF_COTA')
        text(page,'Cota DEM (m)',14,255,2.4);text(page,'Progresiva sobre eje UTM (km)',95,83,2.4)
        text(page,f'Escala horizontal 1:{hs}; vertical 1:{vs}; exageración H/V = {hs/vs:.2f}',32,77,2.2)
        critical=min(ss,key=lambda v:v['estados']['CALOR_FINAL']['distancia_dem_min_m']);i=int(critical['id'][1:])-1
        text(page,'DETALLE DEL VANO CRÍTICO DEL TRAMO',292,252,2.5);text(page,f"{critical['id']} | {critical['desde']} - {critical['hasta']}",292,241,2.5)
        detail(page,critical,posts[i],posts[i+1],295,155,105,65,doc)
        for j,s in enumerate(['Rojo: catenaria 75°C + fluencia.','Marrón: envolvente DEM bajo fases.','Verde: DEM del eje del trazado.','Azul: cuerda y cotas de f/g.','g75: separación vertical al DEM.','f75: flecha respecto a cuerda.','No acredita distancia al suelo real.']):text(page,s,292,121-j*5.5,2.1)
        # Planilla por vano: lectura inequívoca incluso donde los rótulos del gráfico se acercan.
        x,y=18,64;cell=382/len(ss)
        y=68
        labels=['Vano','Desde / hasta','L horiz. (m)','f75 (m)','g75 mín. (m)','Postes L (m)','Amarres H (m)']
        for j,l in enumerate(labels):text(page,l,18,y-j*5,1.85)
        left=51;cell=349/len(ss)
        for j,v in enumerate(ss):
            xx=left+j*cell
            vi=int(v['id'][1:])-1;va,vb=posts[vi],posts[vi+1]
            vals=[v['id'],v['desde'][1:]+' / '+v['hasta'][1:],f"{v['longitud_m']:.1f}",f"{v['estados']['CALOR_FINAL']['flecha_vertical_m']:.2f}",f"{v['estados']['CALOR_FINAL']['distancia_dem_min_m']:.2f}",f"{va['poste_m']}/{vb['poste_m']}",f"{va['amarre_m']:.1f}/{vb['amarre_m']:.1f}"]
            for r,val in enumerate(vals):text(page,val,xx,y-r*5,min(1.85,cell/8))
        text(page,'H amarre sobre DEM: 10.6 / 12.4 / 14.2 m según poste13 /15 /17m. Empotramiento y equipos: hipótesis de estudio.',18,31,2)
        summaries.append(dict(layout=name,tramo=k+1,postes=[p['id'] for p in ps],vanos=[v['id'] for v in ss],h_escala=hs,v_escala=vs,exageracion_hv=hs/vs,vano_critico_75=critical['id'],g75_m=critical['estados']['CALOR_FINAL']['distancia_dem_min_m']))
        # El perfil compacto conserva su escala y gana identificadores y longitudes.
        small=doc.layouts.get(f'LP-{k+2:02}_PLANTA');zz=[p['z_dem_m'] for p in ps];zl=min(zz)-5;zh=max(zz)+25;sh=math.ceil((xmax-xmin)/.263/500)*500;sv=math.ceil((zh-zl)/.048/250)*250
        for ent in list(small.query('*[layer=="PF_COMPACTO"]')):small.delete_entity(ent)
        for ent in list(small.query('TEXT')):
            if abs(ent.dxf.insert.y-28)<.01 and ' m / ' in ent.dxf.text:small.delete_entity(ent)
        for j,p in enumerate(ps):text(small,p['id'],16+(p['progresiva_m']-xmin)*1000/sh-2,31-(j%2)*3,1.45,'PF_COMPACTO')
        text(small,f'Detalle ampliado y planilla de vanos: PF-{k+1:02}',16,24,2,'PF_COMPACTO')
    doc.saveas(f)
    (D/'perfiles-explicitos.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2),encoding='utf-8')
    from estilo import main as aplicar_estilo
    doc=aplicar_estilo(doc)
    # PDF de19láminas: planos del proyecto; las23referencias DGE se entregan en el anexo.
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import Frontend,RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.addons.drawing.config import Configuration,BackgroundPolicy,ColorPolicy
    png=B/'perfiles-explicitos';png.mkdir(exist_ok=True,parents=True);index=[]
    canvas=Canvas(str(R/'output/pdf/Linea_Primaria_Limbani_Huancasayani_R01_planos.pdf'),pagesize=(420/25.4*72,297/25.4*72))
    for lay in doc.layouts:
        if lay.name=='Model' or lay.name.startswith('AN-'):continue
        fig=plt.figure(figsize=(420/25.4,297/25.4));ax=fig.add_axes([0,0,1,1]);ax.set_axis_off();cfg=Configuration(background_policy=BackgroundPolicy.WHITE,color_policy=ColorPolicy.COLOR)
        Frontend(RenderContext(doc),MatplotlibBackend(ax),config=cfg).draw_layout(lay,finalize=True);ax.set_xlim(0,420);ax.set_ylim(0,297);ax.set_aspect('equal',adjustable='box');fig.set_size_inches(420/25.4,297/25.4)
        out=png/f'{len(index)+1:02}-{lay.name}.png';fig.savefig(out,dpi=160);plt.close(fig);canvas.drawImage(str(out),0,0,width=420/25.4*72,height=297/25.4*72);canvas.showPage();index.append(dict(layout=lay.name,png=out.relative_to(R).as_posix(),pagina=len(index)+1))
    canvas.save();assert len(index)==19
    (D/'indice-planos.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8');print('19láminas,7perfiles explícitos;42layouts CAD',flush=True)
if __name__=='__main__':main()
