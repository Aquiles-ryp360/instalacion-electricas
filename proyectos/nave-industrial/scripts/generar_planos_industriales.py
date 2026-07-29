#!/usr/bin/env python3
"""Generador de planos electricos industriales (DXF + PDF) segun normas ISO/DIN.

Planos:
  1. Diagrama unifilar general con 7 circuitos (C1-C7)
  2. Plano de distribucion 20x40m (zonas, equipos, malla SPAT, acometida)
  3. Diagrama de fuerza MCC (ITM + guardamotores + arranque)

Lineweights ISO/DIN:
  - IND_BUS / IND_TABLERO / IND_MARCO: 0.50 mm
  - IND_CABLE / IND_PROT / IND_MOTOR: 0.35 mm
  - IND_TIERRA / IND_TEXTO / IND_NOTE: 0.25 mm
"""
import argparse, json, math, os, sys, shutil
from pathlib import Path
try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment
except ImportError:
    ezdxf = None; TextEntityAlignment = None

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "herramientas" / "cad" / "scripts"))
try:
    from electrical_overlay import add_dge_symbol
except Exception:
    def add_dge_symbol(*_args, **_kwargs):
        return False

LW = {"MARCO":50,"BUS":50,"TABLERO":50,"MCC":50,"CABLE":35,"PROT":35,"MOTOR":35,
      "TRAFO":35,"COMP":35,"TIERRA":25,"TEXTO":25,"NOTE":25,"CARGA":25,"LUM":25}
LS = {}
for k,v in [("MARCO",7),("BUS",7),("CABLE",4),("TIERRA",3),("TEXTO",7),("TABLERO",1),
            ("MCC",5),("MOTOR",2),("PROT",6),("TRAFO",7),("CARGA",8),("COMP",6),
            ("LUM",2),("NOTE",8)]:
    LS[f"IND_{k}"] = {"color":v, "lineweight":LW.get(k,25)}

def el(doc,n,s=None):
    if n not in doc.layers: doc.layers.new(n,dxfattribs=s or {"color":7})
def sl(doc):
    for n,s in LS.items(): el(doc,n,s)
def at(m,t,x,y,h=0.15,l="IND_TEXTO",r=0):
    e=m.add_text(str(t),dxfattribs={"layer":l,"height":h,"rotation":r})
    e.set_placement((float(x),float(y)),align=TextEntityAlignment.MIDDLE_CENTER)
def am(m,t,x,y,h=0.14,l="IND_TEXTO",s=1.35):
    lines=str(t).splitlines() or [""]; sy=float(y)+(len(lines)-1)*h*s/2
    for i,ln in enumerate(lines): at(m,ln,x,sy-i*h*s,h,l)
def al(m,x1,y1,x2,y2,l="IND_CABLE"):
    m.add_line((x1,y1),(x2,y2),dxfattribs={"layer":l})
def ar(m,x,y,w,h,l="IND_TABLERO"):
    m.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)],dxfattribs={"layer":l})
def ac(m,x,y,r,l="IND_MOTOR"):
    m.add_circle((x,y),r,dxfattribs={"layer":l})
def ax(m,x,y,s=0.08,l="IND_NOTE"):
    al(m,x-s,y-s,x+s,y-s,l); al(m,x-s,y+s,x+s,y-s,l)

DGE = {
    "panel": "DGE_09_91_16_PANEL_DISTRIBUCION",
    "luminaria": "DGE_09_93_60_LUMINARIA_G",
    "toma_1f": "DGE_09_93_13_TOMACORRIENTE_MONOFASICO",
    "toma_3f": "DGE_09_93_15_TOMACORRIENTE_TRIFASICO",
    "tierra": "DGE_09_93_02_TIERRA_CONDUCTOR",
}

def dge(m,key,x,y,scale=1.0,l="IND_CARGA",r=0):
    return add_dge_symbol(m,DGE[key],x,y,scale=scale,layer=l,rotation=r)

def grid_points(x,y,w,h,count):
    if count <= 0: return []
    cols=max(1,math.ceil(math.sqrt(count*w/max(h,1))))
    rows=math.ceil(count/cols)
    return [(x+(i%cols+1)*w/(cols+1), y+(i//cols+1)*h/(rows+1)) for i in range(count)]

def zone_lookup(zones):
    return {zn.lower().replace(".","").replace(" ",""): (zx,zy,zw,zh)
            for zx,zy,zw,zh,zn in zones}

def zone_rect(name,zones):
    key=(name or "").lower().replace(".","").replace(" ","")
    z=zone_lookup(zones)
    for k in z:
        if key in k or k in key:
            return z[k]
    return None

def draw_trafo(m,x,y,lb="T1",p="100kVA"):
    ac(m,x,y,0.35,"IND_TRAFO"); ac(m,x,y,0.22,"IND_TRAFO")
    at(m,lb,x,y+0.45,0.14,"IND_TRAFO"); at(m,p,x,y-0.45,0.10,"IND_TRAFO")
def draw_tg(m,x,y,lb,ex=""):
    if not dge(m,"panel",x,y,scale=2.0,l="IND_TABLERO"):
        ar(m,x-0.6,y-0.25,1.2,0.5)
    at(m,lb,x,y,0.16,"IND_TABLERO")
    if ex: at(m,ex,x,y-0.35,0.08,"IND_TEXTO")
def draw_itm(m,x,y,r):
    ar(m,x-0.25,y-0.12,0.5,0.22,"IND_PROT"); at(m,f"{r}A",x,y,0.10,"IND_PROT")
def draw_motor_sk(m,x,y,lb,hp,tarr="DOL"):
    ac(m,x,y,0.22,"IND_MOTOR"); at(m,lb,x,y,0.11,"IND_MOTOR")
    at(m,f"{hp}HP",x,y+0.3,0.09,"IND_TEXTO"); at(m,tarr,x,y-0.3,0.07,"IND_NOTE")
def draw_carga(m,x,y,lb,kw=""):
    ar(m,x-0.25,y-0.15,0.5,0.3,"IND_CARGA"); at(m,lb,x,y,0.10,"IND_CARGA")
    if kw: at(m,f"{kw}kW",x,y-0.3,0.08,"IND_TEXTO")
def draw_gnd(m,x,y):
    dge(m,"tierra",x,y,scale=2.0,l="IND_TIERRA")
    al(m,x,y,x,y-0.3,"IND_TIERRA"); al(m,x-0.2,y-0.3,x+0.2,y-0.3,"IND_TIERRA")
    al(m,x-0.12,y-0.45,x+0.12,y-0.45,"IND_TIERRA")
    al(m,x-0.05,y-0.6,x+0.05,y-0.6,"IND_TIERRA")
    at(m,"SPAT",x,y-0.8,0.09,"IND_TIERRA")

def draw_toma(m,x,y,tt):
    key="toma_3f" if tt.get("fases",1) == 3 else "toma_1f"
    if not dge(m,key,x,y,scale=1.2,l="IND_CARGA"):
        ar(m,x-0.12,y-0.12,0.24,0.24,"IND_CARGA")
    at(m,tt["id"],x,y+0.32,0.08,"IND_CARGA")
    at(m,f"{tt.get('corriente_a','')}A {tt.get('tension_v','')}V",x,y-0.34,0.06,"IND_TEXTO")

def draw_luminarias(m,data,zones):
    for il in data.get("iluminacion",[]):
        rect=zone_rect(il.get("ubicacion_zona"),zones)
        if not rect: continue
        x,y,w,h=rect
        for lx,ly in grid_points(x+1.0,y+1.0,max(w-2.0,1.0),max(h-2.0,1.0),int(il.get("cantidad",0))):
            if not dge(m,"luminaria",lx,ly,scale=0.9,l="IND_LUM"):
                ax(m,lx,ly,0.16,"IND_LUM")
            at(m,il.get("circuito",""),lx,ly-0.32,0.06,"IND_TEXTO")

def draw_legend(m,x,y):
    at(m,"SIMBOLOGIA DGE",x+1.2,y+0.9,0.10,"IND_TEXTO")
    entries=[("panel","Tablero 09-91-16"),("luminaria","Luminaria 09-93-60"),
             ("toma_1f","Toma 1F 09-93-13"),("toma_3f","Toma 3F 09-93-15")]
    for i,(key,label) in enumerate(entries):
        yy=y-i*0.55
        dge(m,key,x,yy,scale=0.9,l="IND_NOTE")
        at(m,label,x+1.4,yy,0.075,"IND_NOTE")

def generar_unifilar(data,out):
    doc=ezdxf.new("R2010",setup=True); sl(doc); m=doc.modelspace()
    V=data.get("tension_v",380); X0,Y0=2.0,1.0; SP=1.8; BW=22.0
    at(m,"DIAGRAMA UNIFILAR - TGD NAVE INDUSTRIAL 20x40m",X0+BW/2,Y0+17.5,0.35,"IND_TEXTO")
    at(m,data.get("proyecto","Nave industrial"),X0+BW/2,Y0+16.8,0.16,"IND_TEXTO")
    at(m,f"{V}V | 3F ~ 60Hz | TN-S",X0,Y0+16.2,0.12,"IND_TEXTO")
    md_s=f"MD: {data.get('maxima_demanda_kw',0):.1f} kW | I: {data.get('corriente_total_a',0):.1f} A"
    at(m,md_s,X0+BW/2,Y0+15.7,0.12,"IND_NOTE")
    bx=X0+4.0; ys=Y0+1.0; ye=Y0+15.0
    for i,f in enumerate(["R","S","T"]):
        al(m,bx+i*0.4,ys,bx+i*0.4,ye,"IND_BUS"); at(m,f,bx+i*0.4,ye+0.3,0.10,"IND_TEXTO")
    nx=bx+1.5; al(m,nx,ys,nx,ye,"IND_CABLE"); at(m,"N",nx,ye+0.3,0.10,"IND_TEXTO")
    y=ye
    y-=SP*0.6; mx=bx+3.0
    at(m,"RED PUBLICA",mx,y+0.6,0.12,"IND_TEXTO")
    draw_trafo(m,mx,y,"T1","100kVA"); al(m,bx,y,mx,y,"IND_CABLE")
    y-=SP*0.7; draw_itm(m,mx,y,100); al(m,bx,y,mx,y,"IND_CABLE")
    y-=SP*0.5; draw_tg(m,mx,y,"TGD","100A / 50mm2"); al(m,bx,y,mx,y,"IND_CABLE")
    cfp=data.get("compensacion_fp",{})
    if cfp.get("requiere"):
        y-=SP*0.5; ar(m,mx-0.4,y-0.25,0.8,0.5,"IND_COMP")
        at(m,"BPF",mx,y,0.14,"IND_COMP"); at(m,f"{round(cfp.get('banco_kvar',0))}kVAr",mx,y-0.35,0.07,"IND_NOTE")
        al(m,bx,y,mx,y,"IND_CABLE")
    # Subcircuitos desde TGD
    subcx=mx-3.0; suby=y-SP*0.8
    subs=[
        ("TF1","FUERZA",63),
        ("TI1","ILUM.IND",16),
    ]
    for sid,snm,si in subs:
        suby-=SP*0.6; draw_itm(m,subcx,suby,si); al(m,bx,suby,subcx,suby,"IND_CABLE")
        draw_tg(m,subcx,suby,sid); al(m,bx,suby,subcx,suby,"IND_CABLE")
    # Circuitos directos desde TGD
    direct_cx=mx+3.0; diry=suby-SP*1.0
    for cd,ckw,citm in [("C2 - TOM.IND","6kW",25),("C6 - OFICINAS","3kW",16)]:
        diry-=SP*0.6; draw_itm(m,direct_cx,diry,citm); al(m,bx,diry,direct_cx,diry,"IND_CABLE")
        draw_carga(m,direct_cx,diry,cd,ckw); al(m,bx,diry,direct_cx,diry,"IND_CABLE")
    # Motores desde TF1
    mcx=bx+1.5; my=Y0+2.0
    for mo in data.get("motores",[]):
        h=mo.get("potencia_hp",0); kw=mo.get("potencia_kw",0)
        draw_itm(m,mcx,my,mo.get("itm_a",30))
        rt=mo.get("proteccion_termica",""); at(m,rt,mcx+2.2,my,0.07,"IND_NOTE")
        al(m,bx,my,mcx,my,"IND_CABLE")
        my2=my-SP*0.35; at(m,mo.get("tipo_arranque","DOL"),mcx,my2,0.07,"IND_NOTE")
        al(m,mcx,my,mcx,my2,"IND_CABLE")
        my3=my2-SP*0.35; draw_motor_sk(m,mcx,my3,mo["id"],h,mo.get("tipo_arranque","DOL"))
        al(m,mcx,my2,mcx,my3,"IND_CABLE"); my+=SP
    # C5 - Maquinaria taller
    draw_itm(m,mcx,my,63); al(m,bx,my,mcx,my,"IND_CABLE")
    my2=my-SP*0.35; draw_carga(m,mcx,my2,"C5 - MAQ.TALLER","25kW"); al(m,mcx,my,mcx,my2,"IND_CABLE")
    sy=ys-SP*0.3; draw_gnd(m,bx-2.0,sy)
    nts=[f"MD: {data.get('maxima_demanda_kw',0):.1f} kW",
         f"I_total: {data.get('corriente_total_a',0):.1f} A",
         f"Alim: {data.get('alimentador_principal_seccion_mm2',0):.0f}mm2 / ITM: {data.get('alimentador_principal_itm_a',0)}A",
         "7 circuitos: C1=HighBay, C2=Tom.Ind, C3=Grua, C4=Comp, C5=Maq, C6=Of, C7=BPF"]
    am(m,"NOTAS:\n"+"\n".join(f"  {x}" for x in nts),X0+15.0,ye-3.0,0.10,"IND_NOTE")
    ar(m,X0-0.5,Y0-0.5,BW+1.0,ye-Y0+2.5,"IND_MARCO")
    Path(out).parent.mkdir(parents=True,exist_ok=True); doc.saveas(out)
    print(f"Unifilar: {out}")

def generar_distribucion(data,out):
    doc=ezdxf.new("R2010",setup=True); sl(doc); m=doc.modelspace()
    zones=[(1,1,38,15,"PRODUCCION"),(1,16,20,12,"ALMACEN"),(22,16,10,6,"OFICINAS"),(33,17,5,3,"SS.HH.")]
    nw=42.0; nh=max(22.0,max(zy+zh for _,zy,_,zh,_ in zones)+1.0); X0=0.5; Y0=0.5
    at(m,"PLANO DE DISTRIBUCION - NAVE INDUSTRIAL 20x40m",nw/2,nh+0.8,0.30,"IND_TEXTO")
    at(m,data.get("proyecto","Nave industrial"),nw/2,nh+0.3,0.14,"IND_TEXTO")
    ar(m,X0,Y0,nw,nh,"IND_MARCO")
    for zx,zy,zw,zh,zn in zones:
        ar(m,zx,zy,zw,zh,"IND_NOTE"); at(m,zn,zx+zw/2,zy+zh/2,0.25,"IND_TEXTO")
    # Columnas 10 total
    for cx,cy in [(5,4),(13,4),(21,4),(29,4),(37,4),(5,11),(13,11),(21,11),(29,11),(37,11)]:
        ar(m,cx-0.15,cy-0.15,0.3,0.3,"IND_MARCO"); at(m,"+",cx,cy,0.08,"IND_NOTE")
    # Viga via puente grua
    al(m,2,8,38,8,"IND_NOTE"); at(m,"VIGA VIA PUENTE GRUA 5Tn",20,8.4,0.10,"IND_NOTE")
    # Acometida desde medidor hasta TGD
    al(m,18.5,9.0,18.0,8.0,"IND_CABLE"); ac(m,18.5,9.0,0.18,"IND_PROT")
    at(m,"MED",18.5,9.0,0.10,"IND_PROT")
    # Malla SPAT: 6 varillas en perimetro interconectadas
    gnd_pts = [(2,2),(2,10),(10,2),(20,2),(30,2),(40,2)]
    for gx,gy in gnd_pts:
        draw_gnd(m,gx,gy)
    for gx in [2,10,20,30,40]: al(m,gx,2,gx,10,"IND_TIERRA")
    al(m,2,2,40,2,"IND_TIERRA")
    at(m,"MALLA SPAT: 6 VARILLAS Cu 5/8''x2.4m | R<5ohm",21,1.5,0.10,"IND_TIERRA")
    # Tableros
    for tb in data.get("tableros",[]):
        u=tb.get("ubicacion",{}); tx,ty=u.get("x",2),u.get("y",2)
        draw_tg(m,tx,ty,tb["id"])
    draw_luminarias(m,data,zones)
    # Motores
    for mt in data.get("motores",[]):
        u=mt.get("ubicacion",{}); mx,my=u.get("x",5),u.get("y",5)
        ac(m,mx,my,0.22,"IND_MOTOR"); at(m,mt["id"],mx,my,0.10,"IND_MOTOR")
        at(m,f"{mt.get('potencia_hp',0)}HP",mx,my-0.4,0.09,"IND_TEXTO")
    # Tomas
    for tt in data.get("tomacorrientes",[]):
        u=tt.get("ubicacion",{}); tx,ty=u.get("x",3),u.get("y",3)
        draw_toma(m,tx,ty,tt)
    # Compensacion FP
    cfp=data.get("compensacion_fp",{})
    if cfp.get("requiere"):
        cx,cy=cfp.get("ubicacion",{}).get("x",35),cfp.get("ubicacion",{}).get("y",10)
        ar(m,cx-0.4,cy-0.3,0.8,0.6,"IND_COMP"); at(m,"BPF",cx,cy,0.12,"IND_COMP")
    draw_legend(m,34.5,nh-1.5)
    Path(out).parent.mkdir(parents=True,exist_ok=True); doc.saveas(out)
    print(f"Distribucion: {out}")

def generar_fuerza(data,out):
    doc=ezdxf.new("R2010",setup=True); sl(doc); m=doc.modelspace()
    at(m,"DIAGRAMA DE FUERZA - MCC NAVE 20x40m",11.0,14.5,0.30,"IND_TEXTO")
    X0,Y0=2.0,1.0; SP=2.2; bx=X0+3.0; ys=Y0+1.0; ye=Y0+12.0
    for i,f in enumerate(["R","S","T"]):
        al(m,bx+i*0.4,ys,bx+i*0.4,ye,"IND_BUS"); at(m,f,bx+i*0.4,ye+0.3,0.10,"IND_TEXTO")
    al(m,bx+1.5,ys,bx+1.5,ye,"IND_CABLE"); at(m,"N",bx+1.5,ye+0.3,0.10,"IND_TEXTO")
    y_motor=ys
    # Motores individuales (M1 puente grua, M2 compresor)
    for mo in data.get("motores",[]):
        cx=bx+4.0; cy=y_motor; h=mo.get("potencia_hp",0); kw=mo.get("potencia_kw",0)
        draw_itm(m,cx,cy,mo.get("itm_a",30)); al(m,bx,cy,cx,cy,"IND_CABLE")
        cy2=cy-SP*0.35; ar(m,cx-0.2,cy2-0.1,0.4,0.2,"IND_PROT")
        at(m,f"GM {mo.get('proteccion_termica','')}",cx,cy2,0.07,"IND_NOTE")
        al(m,cx,cy,cx,cy2,"IND_CABLE")
        cy3=cy2-SP*0.35; at(m,mo.get("tipo_arranque","DOL"),cx,cy3,0.08,"IND_NOTE")
        al(m,cx,cy2,cx,cy3,"IND_CABLE")
        cy4=cy3-SP*0.35; draw_motor_sk(m,cx,cy4,mo["id"],h,mo.get("tipo_arranque","DOL"))
        al(m,cx,cy3,cx,cy4,"IND_CABLE")
        at(m,f"{kw:.1f}kW | {mo.get('circuito','')}",cx+2.5,cy4,0.08,"IND_NOTE")
        y_motor+=SP
    # C5 - Maquinaria taller 25kW (grupo de maquinas)
    cx=bx+4.0; cy=y_motor
    draw_itm(m,cx,cy,63); al(m,bx,cy,cx,cy,"IND_CABLE")
    cy2=cy-SP*0.5; ar(m,cx-0.25,cy2-0.15,0.5,0.3,"IND_CARGA")
    at(m,"MAQ.TALLER 25kW",cx,cy2,0.12,"IND_CARGA")
    at(m,"C5: Torno + Fresadora + Plasma",cx,cy2-0.4,0.08,"IND_NOTE")
    al(m,cx,cy,cx,cy2,"IND_CABLE")
    ar(m,X0-0.5,Y0-0.5,18.0,ye-Y0+2.0,"IND_MARCO")
    Path(out).parent.mkdir(parents=True,exist_ok=True); doc.saveas(out)
    print(f"Fuerza: {out}")

def exportar_pdf(dxf):
    try:
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        pdf=dxf.replace(".dxf",".pdf")
        png=dxf.replace(".dxf",".png")
        d=ezdxf.readfile(dxf)
        fig=plt.figure(figsize=(16.53,11.69),dpi=200)
        ax=fig.add_axes([0,0,1,1]); ax.axis("off")
        Frontend(RenderContext(d),MatplotlibBackend(ax)).draw_layout(d.modelspace(),finalize=True)
        fig.savefig(pdf,dpi=200,bbox_inches="tight",pad_inches=0.2)
        fig.savefig(png,dpi=200,bbox_inches="tight",pad_inches=0.2)
        plt.close(fig)
        print(f"PDF: {pdf}")
        print(f"PNG: {png}")
    except Exception as e: print(f"PDF/PNG fail: {e}")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--electrical",required=True)
    p.add_argument("--view",default="completo",choices=["unifilar","distribucion","fuerza","completo"])
    p.add_argument("--output",default="build/")
    a=p.parse_args()
    if not ezdxf: print("Error: ezdxf no instalado"); sys.exit(1)
    with open(a.electrical) as f: data=json.load(f)
    od=os.path.dirname(a.output) or "build"
    if a.view in ("unifilar","completo"):
        du=os.path.join(od,"industrial_unifilar.dxf"); generar_unifilar(data,du); exportar_pdf(du)
    if a.view in ("distribucion","completo"):
        dd=os.path.join(od,"industrial_distribucion.dxf"); generar_distribucion(data,dd); exportar_pdf(dd)
    if a.view in ("fuerza","completo"):
        df=os.path.join(od,"industrial_fuerza.dxf"); generar_fuerza(data,df); exportar_pdf(df)
    if a.output.endswith(".dxf"):
        pe=a.output; pp=a.output.replace(".dxf",".pdf")
        shutil.copy2(os.path.join(od,"industrial_unifilar.dxf"),pe) if os.path.exists(os.path.join(od,"industrial_unifilar.dxf")) else None
        shutil.copy2(os.path.join(od,"industrial_unifilar.pdf"),pp) if os.path.exists(os.path.join(od,"industrial_unifilar.pdf")) else None
        print(f"Pipeline compat: {pe}")

if __name__=="__main__": main()
