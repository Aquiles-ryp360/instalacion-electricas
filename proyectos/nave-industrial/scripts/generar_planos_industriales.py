#!/usr/bin/env python3
"""Generador de planos electricos industriales (DXF + PDF) segun normas ISO/DIN.

Planos:
  1. Diagrama unifilar general (red -> T1 -> TG -> tableros -> motores)
  2. Plano de distribucion en planta (nave, zonas, equipos, malla SPAT, acometida)
  3. Diagrama de fuerza MCC (ITM + reles termicos + arranque por motor)

Lineweights ISO/DIN:
  - IND_BUS / IND_TABLERO / IND_MARCO: 0.50 mm (linea gruesa)
  - IND_CABLE / IND_PROT / IND_MOTOR: 0.35 mm (linea media)
  - IND_TIERRA / IND_TEXTO / IND_NOTE: 0.25 mm (linea fina)
"""
import argparse, json, math, os, sys, shutil
from pathlib import Path
try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment
except ImportError:
    ezdxf = None; TextEntityAlignment = None

# ISO/DIN lineweights: 0.50=50, 0.35=35, 0.25=25 (en unidades ezdxf*100)
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
    al(m,x-s,y-s,x+s,y+s,l); al(m,x-s,y+s,x+s,y-s,l)

def draw_trafo(m,x,y,lb="T1",p="100kVA"):
    ac(m,x,y,0.35,"IND_TRAFO"); ac(m,x,y,0.22,"IND_TRAFO")
    at(m,lb,x,y+0.45,0.14,"IND_TRAFO"); at(m,p,x,y-0.45,0.10,"IND_TRAFO")
def draw_tg(m,x,y,lb,ex=""):
    ar(m,x-0.6,y-0.25,1.2,0.5); at(m,lb,x,y,0.16,"IND_TABLERO")
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
    al(m,x,y,x,y-0.3,"IND_TIERRA"); al(m,x-0.2,y-0.3,x+0.2,y-0.3,"IND_TIERRA")
    al(m,x-0.12,y-0.45,x+0.12,y-0.45,"IND_TIERRA")
    al(m,x-0.05,y-0.6,x+0.05,y-0.6,"IND_TIERRA")
    at(m,"SPAT",x,y-0.8,0.09,"IND_TIERRA")

def generar_unifilar(data,out):
    doc=ezdxf.new("R2010",setup=True); sl(doc); m=doc.modelspace()
    V=data.get("tension_v",380); X0,Y0=2.0,1.0; SP=1.8; BW=22.0
    at(m,"DIAGRAMA UNIFILAR INDUSTRIAL",X0+BW/2,Y0+17.5,0.35,"IND_TEXTO")
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
    y-=SP*0.7; draw_itm(m,mx,y,80); al(m,bx,y,mx,y,"IND_CABLE")
    y-=SP*0.5; draw_tg(m,mx,y,"TG","80A / 35mm2"); al(m,bx,y,mx,y,"IND_CABLE")
    cfp=data.get("compensacion_fp",{})
    if cfp.get("requiere"):
        y-=SP*0.5; ar(m,mx-0.4,y-0.25,0.8,0.5,"IND_COMP")
        at(m,"BPF",mx,y,0.14,"IND_COMP"); at(m,f"{round(cfp.get('fp_actual',0.85)*100)}%",mx,y-0.35,0.07,"IND_NOTE")
        al(m,bx,y,mx,y,"IND_CABLE")
    sts=[t for t in data.get("tableros",[]) if t.get("nivel")=="distribucion"]
    ysub=y-SP*0.7
    for st in sts:
        cx=mx+2.0; cy=ysub
        draw_itm(m,cx,cy,100 if "fuerza" in st.get("nombre","").lower() else 25)
        al(m,bx,cy,cx,cy,"IND_CABLE"); ysub-=SP*0.5
        draw_tg(m,cx,cy,st["nombre"]); al(m,bx,cy,cx,cy,"IND_CABLE"); ysub-=SP*0.7
    ym=ys+1.0
    for mo in data.get("motores",[]):
        cx=bx+4.5; cy=ym; h=mo.get("potencia_hp",0)
        draw_itm(m,cx,cy,mo.get("itm_a",30))
        rt=mo.get("proteccion_termica",""); at(m,rt,cx+1.8,cy,0.07,"IND_NOTE")
        al(m,bx,cy,cx,cy,"IND_CABLE")
        cy2=cy-SP*0.35; at(m,mo.get("tipo_arranque","DOL"),cx,cy2,0.07,"IND_NOTE")
        al(m,cx,cy,cx,cy2,"IND_CABLE")
        cy3=cy2-SP*0.35; draw_motor_sk(m,cx,cy3,mo["id"],h,mo.get("tipo_arranque","DOL"))
        al(m,cx,cy2,cx,cy3,"IND_CABLE"); ym+=SP
    sy=ys-SP*0.3; draw_gnd(m,bx-2.0,sy)
    ny=ye-3.0
    nts=[f"MD: {data.get('maxima_demanda_kw',0):.1f} kW",
         f"I_total: {data.get('corriente_total_a',0):.1f} A",
         f"Alim: {data.get('alimentador_principal_seccion_mm2',0):.0f}mm2 / ITM: {data.get('alimentador_principal_itm_a',0)}A"]
    am(m,"NOTAS:\n"+"\n".join(f"  {x}" for x in nts),X0+15.0,ny,0.10,"IND_NOTE")
    ar(m,X0-0.5,Y0-0.5,BW+1.0,ye-Y0+2.5,"IND_MARCO")
    Path(out).parent.mkdir(parents=True,exist_ok=True); doc.saveas(out)
    print(f"Unifilar: {out}")

def generar_distribucion(data,out):
    doc=ezdxf.new("R2010",setup=True); sl(doc); m=doc.modelspace()
    nw=32.0; nh=16.0; X0=0.5; Y0=0.5
    at(m,"PLANO DE DISTRIBUCION - NAVE INDUSTRIAL",nw/2,nh+0.8,0.30,"IND_TEXTO")
    at(m,data.get("proyecto","Nave industrial"),nw/2,nh+0.3,0.14,"IND_TEXTO")
    ar(m,X0,Y0,nw,nh,"IND_MARCO")
    zones=[(1,1,18,12,"PRODUCCION"),(19,1,10,12,"ALMACEN"),(1,13,12,3,"OFICINAS"),(13,14,4,2,"SS.HH.")]
    for zx,zy,zw,zh,zn in zones:
        ar(m,zx,zy,zw,zh,"IND_NOTE"); at(m,zn,zx+zw/2,zy+zh/2,0.20,"IND_TEXTO")
    for cx,cy in [(6,4),(12,4),(6,9),(12,9),(20,4),(20,9)]:
        ac(m,cx,cy,0.12,"IND_NOTE"); at(m,"+",cx,cy,0.08,"IND_NOTE")

    # Acometida desde medidor hasta TG
    al(m,14.5,7.0,14.0,6.0,"IND_CABLE")  # acometida
    ac(m,14.5,7.0,0.18,"IND_PROT"); at(m,"MED",14.5,7.0,0.10,"IND_PROT")
    al(m,14.5,7.0,15.5,7.0,"IND_CABLE")  # linea hacia TG

    # Malla SPAT: 4 varillas en perímetro interconectadas
    gnd_pts = [(3,2), (3,10), (12,2), (12,10)]
    for gx,gy in gnd_pts:
        draw_gnd(m,gx,gy)
    al(m,3,2,3,10,"IND_TIERRA"); al(m,12,2,12,10,"IND_TIERRA")
    al(m,3,2,12,2,"IND_TIERRA"); al(m,3,10,12,10,"IND_TIERRA")
    at(m,"MALLA SPAT: 4 VARILLAS Cu 5/8''x2.4m | R<5ohm",7.5,1.5,0.10,"IND_TIERRA")

    # Tableros
    for tb in data.get("tableros",[]):
        u=tb.get("ubicacion",{}); tx,ty=u.get("x",2),u.get("y",2)
        ar(m,tx-0.4,ty-0.25,0.8,0.5,"IND_TABLERO"); at(m,tb["id"],tx,ty,0.12,"IND_TABLERO")
    # Motores
    for mt in data.get("motores",[]):
        u=mt.get("ubicacion",{}); mx,my=u.get("x",5),u.get("y",5)
        ac(m,mx,my,0.22,"IND_MOTOR"); at(m,mt["id"],mx,my,0.10,"IND_MOTOR")
        at(m,f"{mt.get('potencia_hp',0)}HP",mx,my-0.35,0.08,"IND_TEXTO")
    # Tomas
    for tt in data.get("tomacorrientes",[]):
        u=tt.get("ubicacion",{}); tx,ty=u.get("x",3),u.get("y",3)
        ar(m,tx-0.12,ty-0.12,0.24,0.24,"IND_CARGA"); at(m,tt["id"],tx,ty,0.08,"IND_CARGA")
    # Compensacion FP
    cfp=data.get("compensacion_fp",{})
    if cfp.get("requiere"):
        cx,cy=cfp.get("ubicacion",{}).get("x",16),cfp.get("ubicacion",{}).get("y",7)
        ar(m,cx-0.4,cy-0.3,0.8,0.6,"IND_COMP"); at(m,"BPF",cx,cy,0.12,"IND_COMP")
    Path(out).parent.mkdir(parents=True,exist_ok=True); doc.saveas(out)
    print(f"Distribucion: {out}")

def generar_fuerza(data,out):
    doc=ezdxf.new("R2010",setup=True); sl(doc); m=doc.modelspace()
    at(m,"DIAGRAMA DE FUERZA - MCC",11.0,14.5,0.30,"IND_TEXTO")
    X0,Y0=2.0,1.0; SP=2.2; bx=X0+3.0; ys=Y0+1.0; ye=Y0+12.0
    for i,f in enumerate(["R","S","T"]):
        al(m,bx+i*0.4,ys,bx+i*0.4,ye,"IND_BUS"); at(m,f,bx+i*0.4,ye+0.3,0.10,"IND_TEXTO")
    al(m,bx+1.5,ys,bx+1.5,ye,"IND_CABLE"); at(m,"N",bx+1.5,ye+0.3,0.10,"IND_TEXTO")
    y_motor=ys
    for mo in data.get("motores",[]):
        cx=bx+4.0; cy=y_motor; h=mo.get("potencia_hp",0); kw=mo.get("potencia_kw",0)
        draw_itm(m,cx,cy,mo.get("itm_a",30)); al(m,bx,cy,cx,cy,"IND_CABLE")
        cy2=cy-SP*0.35; ar(m,cx-0.2,cy2-0.1,0.4,0.2,"IND_PROT")
        at(m,f"RT {mo.get('proteccion_termica','')}",cx,cy2,0.07,"IND_NOTE")
        al(m,cx,cy,cx,cy2,"IND_CABLE")
        cy3=cy2-SP*0.35; at(m,mo.get("tipo_arranque","DOL"),cx,cy3,0.08,"IND_NOTE")
        al(m,cx,cy2,cx,cy3,"IND_CABLE")
        cy4=cy3-SP*0.35; draw_motor_sk(m,cx,cy4,mo["id"],h,mo.get("tipo_arranque","DOL"))
        al(m,cx,cy3,cx,cy4,"IND_CABLE")
        at(m,f"{kw:.1f}kW | {h}HP | {mo.get('fp',0.85)*100:.0f}%FP",cx+2.0,cy4,0.08,"IND_NOTE")
        y_motor+=SP
    ar(m,X0-0.5,Y0-0.5,18.0,ye-Y0+2.0,"IND_MARCO")
    Path(out).parent.mkdir(parents=True,exist_ok=True); doc.saveas(out)
    print(f"Fuerza: {out}")

def exportar_pdf(dxf):
    try:
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        pdf=dxf.replace(".dxf",".pdf"); d=ezdxf.readfile(dxf)
        fig=plt.figure(figsize=(16.53,11.69),dpi=200)
        ax=fig.add_axes([0,0,1,1]); ax.axis("off")
        Frontend(RenderContext(d),MatplotlibBackend(ax)).draw_layout(d.modelspace(),finalize=True)
        fig.savefig(pdf,dpi=200,bbox_inches="tight",pad_inches=0.2); plt.close(fig)
        print(f"PDF: {pdf}")
    except Exception as e: print(f"PDF fail: {e}")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--electrical",required=True)
    p.add_argument("--view",default="completo",choices=["unifilar","distribucion","fuerza","completo"])
    p.add_argument("--output",default="build/")
    p.add_argument("--pdf",default="")
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
    # Compatibilidad con pipeline_automatizado.py: crear plano_electrico.dxf/pdf
    if a.output.endswith(".dxf"):
        pe=a.output; pp=a.pdf or a.output.replace(".dxf",".pdf")
        shutil.copy2(os.path.join(od,"industrial_unifilar.dxf"),pe) if os.path.exists(os.path.join(od,"industrial_unifilar.dxf")) else None
        shutil.copy2(os.path.join(od,"industrial_unifilar.pdf"),pp) if os.path.exists(os.path.join(od,"industrial_unifilar.pdf")) else None
        print(f"Pipeline compat: {pe}")

if __name__=="__main__": main()
