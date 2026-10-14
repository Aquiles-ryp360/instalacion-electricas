"""Genera una entrega académica Rev. 5 separada, trazable y sin entradas inventadas."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import shutil
import sys
from pathlib import Path

import ezdxf
import fitz
from pyproj import Transformer
from reportlab.pdfgen import canvas
from shapely.geometry import LineString, Point, box

from generar_entrega_rev4 import read_inputs, verify as verify_rev4
from rev5_modelos import sensitivity_rows

ROOT = Path(__file__).resolve().parents[1]
REV4 = ROOT / "ENTREGA_FINAL_CAPACHICA_LLACHON_REV4"
DEFAULT = ROOT / "ENTREGA_ACADEMICA_REV5"
MM = 72 / 25.4
TO_GEO = Transformer.from_crs(32719, 4326, always_xy=True)
FOLDERS = ["00_INDICE_Y_RESUMEN", "01_MEMORIA_DESCRIPTIVA", "02_DATOS_Y_CRITERIOS",
           "03_CALCULO_ELECTRICO", "04_CALCULO_MECANICO", "05_PLANOS_PDF",
           "06_PLANOS_EDITABLES", "07_METRADOS_Y_PRESUPUESTO",
           "08_NORMATIVA_Y_TRAZABILIDAD", "09_CONTROL_DE_CALIDAD",
           "10_PENDIENTES_DE_CAMPO_Y_ELECTRO_PUNO"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: str):
    path.write_text(content.strip() + "\n", encoding="utf-8")


def table(path: Path, headings: list[str], rows: list[dict]):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headings)
        writer.writeheader()
        writer.writerows(rows)


def read_table(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class Sheet:
    """Mismas primitivas en presentación A3 DXF y PDF; modelo separado UTM m."""

    def __init__(self, output: Path):
        self.code = "CL-06"
        self.dxf_path = output / "06_PLANOS_EDITABLES/CL-06_REV5.dxf"
        self.pdf_path = output / "05_PLANOS_PDF/CL-06_REV5.pdf"
        self.png_path = output / "09_CONTROL_DE_CALIDAD/CL-06_REV5.png"
        self.doc = ezdxf.new("R2010")
        self.doc.header["$INSUNITS"] = 6
        for layer, aci in [("KML", 5), ("GIS", 8), ("BRECHA", 1),
                           ("PUNTO", 4), ("MARCO", 7), ("NOTA", 1)]:
            self.doc.layers.new(layer, dxfattribs={"color": aci})
        self.paper = self.doc.layouts.new("CL-06_A3")
        self.paper.page_setup(size=(420, 297), margins=(8, 8, 8, 8), units="mm")
        self.pdf = canvas.Canvas(str(self.pdf_path), pagesize=(420*MM, 297*MM), invariant=1)
        self.colors = {"KML": (0.12,.34,.63), "GIS": (.5,.5,.5),
                       "BRECHA": (.73,.13,.13), "PUNTO": (.05,.44,.52),
                       "MARCO": (.12,.18,.25), "NOTA": (.73,.13,.13)}

    def color(self, layer):
        self.pdf.setFillColorRGB(*self.colors[layer])
        self.pdf.setStrokeColorRGB(*self.colors[layer])

    def text(self, x, y, text, size=2.8, layer="MARCO"):
        self.paper.add_text(str(text), dxfattribs={"layer": layer, "height": size}).set_placement((x,y))
        self.color(layer)
        self.pdf.setFont("Helvetica", size * MM * .9)
        self.pdf.drawString(x*MM, y*MM, str(text))

    def line(self, a, b, layer="MARCO", width=.3):
        self.paper.add_line(a,b,dxfattribs={"layer":layer})
        self.color(layer)
        self.pdf.setLineWidth(width*MM)
        self.pdf.line(a[0]*MM,a[1]*MM,b[0]*MM,b[1]*MM)

    def rect(self,x,y,w,h):
        for a,b in [((x,y),(x+w,y)),((x+w,y),(x+w,y+h)),
                    ((x+w,y+h),(x,y+h)),((x,y+h),(x,y))]:
            self.line(a,b)

    def circle(self,p,r,layer="PUNTO"):
        self.paper.add_circle(p,r,dxfattribs={"layer":layer})
        self.color(layer)
        self.pdf.circle(p[0]*MM,p[1]*MM,r*MM,stroke=1,fill=0)

    def poly(self, coords, layer="KML"):
        if len(coords)<2:
            return
        self.paper.add_lwpolyline(coords,dxfattribs={"layer":layer})
        self.color(layer)
        self.pdf.setLineWidth(.6*MM)
        path=self.pdf.beginPath()
        path.moveTo(coords[0][0]*MM,coords[0][1]*MM)
        for x,y in coords[1:]:
            path.lineTo(x*MM,y*MM)
        self.pdf.drawPath(path)

    def finish(self):
        self.pdf.showPage(); self.pdf.save()
        self.doc.saveas(self.dxf_path)
        with fitz.open(self.pdf_path) as pdf:
            pdf[0].get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False).save(self.png_path)


def make_gap_plan(output: Path, lines: list[list[tuple]], gis: list,
                  gaps: list[dict], intersection: Point):
    s=Sheet(output)
    s.rect(8,8,404,281)
    s.line((8,40),(412,40))
    s.text(15,280,"CL-06 | Empalmes del KML e interseccion S3/S4",5)
    s.text(15,270,"CAPACHICA - LLACHON | REV 5 | A3 | 14 OCT 2026",2.8)
    s.text(15,255,"EPSG:32719 | azul: KML | rojo: cuerda NO LEVANTADA | turquesa: extremos",2.8)
    s.text(375,255,"N ^",3.2)
    s.text(15,47,"Los 3 recuadros son ampliaciones locales independientes; escala grafica propia.",2.7)
    s.text(15,29,"ANTEPROYECTO ACADEMICO - NO APTO PARA CONSTRUCCION",3,"NOTA")
    s.text(15,18,"UTM WGS84 zona 19S, modelo m; presentacion mm. Ver coordenadas completas en CSV.",2.4)
    for i,(g,(x,y)) in enumerate(zip(gaps,[(17,170),(217,170),(17,64)]),1):
        a=lines[i-1][-1]; b=lines[i][0]
        mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
        radius=120 if i<3 else 45
        clip=box(mid[0]-radius,mid[1]-radius,mid[0]+radius,mid[1]+radius)
        s.rect(x,y,185,76)
        s.text(x+4,y+68,f"GAP-{i} | cuerda {float(g['distancia_recta_m']):.3f} m",3)
        scale=49/(2*radius)
        f=lambda p:(x+8+(169-2*radius*scale)/2+(p[0]-(mid[0]-radius))*scale,
                    y+9+(p[1]-(mid[1]-radius))*scale)
        for ls in (LineString(lines[i-1]),LineString(lines[i])):
            clipped=ls.intersection(clip)
            parts=[clipped] if clipped.geom_type=="LineString" else list(getattr(clipped,"geoms",[]))
            for part in parts:
                if part.geom_type=="LineString":
                    s.poly([f(p) for p in part.coords])
        s.line(f(a),f(b),"BRECHA",.55)
        s.circle(f(a),1.8); s.circle(f(b),1.8)
        s.text(x+5,y+3,f"E {mid[0]:.0f} N {mid[1]:.0f} | 100 m = {100*scale:.1f} mm",2.0)
        if i==3:
            s.circle(f((intersection.x,intersection.y)),2,"BRECHA")
            s.text(x+70,y+60,"Cruce S3/S4: verificar orden y eje",2.3,"NOTA")
    s.rect(217,64,185,76)
    s.text(222,127,"Diagnostico geometrico",3.3)
    s.text(222,114,"Los enlaces rectos son solo cuerdas de medicion.",2.5)
    s.text(222,104,"S3 y S4 se intersectan antes de sus extremos.",2.5)
    s.text(222,94,"Elegir continuidad requiere topografia y campo.",2.5,"NOTA")
    s.text(222,78,"PC, PN y CV no son apoyos ni cruces aprobados.",2.4)
    model=s.doc.modelspace()
    for coords in lines:
        model.add_lwpolyline(coords,dxfattribs={"layer":"KML"})
    model.add_lwpolyline(gis,dxfattribs={"layer":"GIS"})
    for i in range(3):
        model.add_line(lines[i][-1],lines[i+1][0],dxfattribs={"layer":"BRECHA"})
    model.add_circle((intersection.x,intersection.y),2,dxfattribs={"layer":"PUNTO"})
    s.finish()


def build(output: Path):
    output=output.resolve()
    if output.exists():
        raise FileExistsError(f"La salida ya existe; use una ruta nueva: {output}")
    rev4_manifest=digest(REV4/"manifest_entrega.json")
    verify_rev4(REV4)
    lines,gis,pc,pn,cv,gaps,report,kml_m,gis_m,geod_m=read_inputs()
    inter=LineString(lines[2]).intersection(LineString(lines[3]))
    if inter.geom_type!="Point":
        raise ValueError("Intersección S3/S4 cambió; revisar antes de dibujar")
    output.mkdir(parents=True)
    for folder in FOLDERS:
        (output/folder).mkdir()
    (output/"02_DATOS_Y_CRITERIOS/fuentes").mkdir()
    # Los cinco planos anteriores son referencias de edición Rev. 4, con su código original.
    for n in range(1,6):
        code=f"CL-{n:02d}_REV4"
        for source_folder,target_folder,ext in [("04_PLANOS_PDF","05_PLANOS_PDF","pdf"),
                                                ("05_PLANOS_EDITABLES","06_PLANOS_EDITABLES","dxf")]:
            shutil.copy2(REV4/source_folder/f"{code}.{ext}",output/target_folder/f"{code}.{ext}")
    references={
        "08_DATOS_GIS_Y_CAMPO/KML_ORIGINAL.kml":"KML_ORIGINAL.kml",
        "08_DATOS_GIS_Y_CAMPO/EJE_GIS_ALTERNATIVO.json":"EJE_GIS_ALTERNATIVO.json",
        "08_DATOS_GIS_Y_CAMPO/PC_REFERENCIAS_GIS.csv":"PC_REFERENCIAS_GIS.csv",
        "08_DATOS_GIS_Y_CAMPO/PN_SITIOS_REPLANTEO.csv":"PN_SITIOS_REPLANTEO.csv",
        "08_DATOS_GIS_Y_CAMPO/CV_ALERTAS_OSM.csv":"CV_ALERTAS_OSM.csv",
        "08_DATOS_GIS_Y_CAMPO/GAP_EMPALMES.csv":"GAP_EMPALMES.csv",
        "08_DATOS_GIS_Y_CAMPO/CONCILIACION_REV3.json":"CONCILIACION_REV3.json",
        "02_MEMORIA_DESCRIPTIVA/PARAMETROS_PENDIENTES.json":"PARAMETROS_PENDIENTES.json",
    }
    for rel,name in references.items():
        shutil.copy2(REV4/rel,output/"02_DATOS_Y_CRITERIOS/fuentes"/name)
    shutil.copy2(ROOT/"scripts/rev5_modelos.py",output/"03_CALCULO_ELECTRICO/rev5_modelos.py")
    shutil.copy2(ROOT/"scripts/generar_entrega_rev5.py",output/"00_INDICE_Y_RESUMEN/generar_entrega_rev5.py")
    shutil.copy2(ROOT/"requirements.txt",output/"00_INDICE_Y_RESUMEN/requirements.txt")
    make_gap_plan(output,lines,gis,gaps,inter)

    # Fuente única de parámetros. Confirmado significa documento visto, no realidad en terreno.
    inputs=[]
    def add(variable,symbol,value,unit,source,method,status,effect):
        inputs.append(dict(variable=variable,simbolo=symbol,valor=value,unidad=unit,
                           fuente_archivo=source,metodo=method,estado=status,efecto_diseno=effect))
    src="02_DATOS_Y_CRITERIOS/fuentes/"
    add("CRS de KML","CRS_KML","EPSG:4326","-",src+"KML_ORIGINAL.kml","convención KML y orden lon,lat","confirmado documental","transformación métrica")
    add("CRS proyectado","CRS_UTM","EPSG:32719","-","scripts/generar_entrega_rev5.py","transformación pyproj WGS84/UTM 19S","calculado","longitudes y coordenadas")
    add("segmentos KML","n_seg",len(lines),"segmentos",src+"KML_ORIGINAL.kml","conteo LineString","calculado","continuidad no demostrada")
    add("vértices KML","n_v",sum(map(len,lines)),"vértices",src+"KML_ORIGINAL.kml","conteo pares lon,lat","calculado","muestras geométricas, no apoyos")
    add("longitud KML sin empalmes","L_KML",f"{kml_m:.6f}","m",src+"KML_ORIGINAL.kml","suma LineString UTM","calculado","no es longitud eléctrica de obra")
    add("longitud KML geodésica","L_geo",f"{geod_m:.6f}","m",src+"KML_ORIGINAL.kml","Geod WGS84 por segmento","calculado","contraste métrico")
    add("longitud eje GIS alternativo","L_GIS",f"{gis_m:.6f}","m",src+"EJE_GIS_ALTERNATIVO.json","LineString UTM","calculado","eje diferente, no aprobado")
    add("diferencia de ejes","Delta_L",f"{kml_m-gis_m:.6f}","m",src+"KML_ORIGINAL.kml; "+src+"EJE_GIS_ALTERNATIVO.json","L_KML-L_GIS","calculado","no es tramo localizado")
    add("brechas de segmentos","n_gap",3,"brechas",src+"GAP_EMPALMES.csv","distancias de extremos UTM","calculado","levantar continuidad")
    for i,g in enumerate(gaps,1):
        add(f"cuerda GAP-{i}",f"g_{i}",g["distancia_recta_m"],"m",src+"GAP_EMPALMES.csv","distancia recta UTM entre extremos","calculado","no sumar como eje aprobado")
    add("cruce S3/S4 E","E_X",f"{inter.x:.3f}","m",src+"KML_ORIGINAL.kml","intersección Shapely UTM","calculado","orden/continuidad por verificar")
    add("cruce S3/S4 N","N_X",f"{inter.y:.3f}","m",src+"KML_ORIGINAL.kml","intersección Shapely UTM","calculado","orden/continuidad por verificar")
    for title,n,filename,impact in [("PC referencias GIS",len(pc),"PC_REFERENCIAS_GIS.csv","no inventario de postes aptos"),
                                    ("PN sitios geométricos",len(pn),"PN_SITIOS_REPLANTEO.csv","no ubicación aprobada"),
                                    ("CV alertas OSM",len(cv),"CV_ALERTAS_OSM.csv","verificar cruces en campo")]:
        add(title,title.split()[0],n,"registros",src+filename,"conteo CSV","estimado cartográfico",impact)
    add("punto TMT candidato","TMT","TMT001868169","código","sources/gisem_mt_tramos.geojson","atributo GIS","confirmado documental","conexión no autorizada")
    add("latitud candidata","lat_c","-15.6421333","°","dato facilitado por usuario","conversión DMS","confirmado como dato informado","identificar en campo")
    add("longitud candidata","lon_c","-69.8316111","°","dato facilitado por usuario","conversión DMS","confirmado como dato informado","identificar en campo")
    required=json.loads((ROOT/"datos/parametros_diseno_pendientes.json").read_text(encoding="utf-8"))["design_inputs_required"]
    units={"nominal_voltage_kv":"kV", "frequency_hz":"Hz", "present_peak_demand_kva":"kVA",
           "forecast_peak_demand_kva":"kVA", "power_factor":"-", "soil_resistivity_ohm_m":"Ω·m"}
    for key,value in required.items():
        if value is not None:
            raise ValueError(f"Se esperaba pendiente {key}; revisar clasificación")
        add(key,key,"dato requerido",units.get(key,"según documento"),
            "datos/parametros_diseno_pendientes.json","revisión de nulo","pendiente",
            "bloquea dimensionamiento o aprobación; solicitar a operador/promotor/campo")
    table(output/"02_DATOS_Y_CRITERIOS/DATOS_MAESTROS.csv",list(inputs[0]),inputs)
    scenarios=sensitivity_rows()
    table(output/"03_CALCULO_ELECTRICO/ESCENARIOS_ADIMENSIONALES.csv",list(scenarios[0]),scenarios)
    elec_names=[("S_demanda_kva","kVA","promotor"),("U_ll_kv","kV","Electro Puno"),
                ("numero_fases","-","Electro Puno"),("factor_potencia","-","estudio de carga"),
                ("L_electrica_km","km","eje aprobado"),("R_ohm_km","Ω/km","ficha conductor a temperatura de caso"),
                ("X_ohm_km","Ω/km","configuración y ficha"),("I_catalogo_a","A","ficha conductor"),
                ("factores_ampacidad","-","ficha/norma"),("Zth_r_ohm","Ω","Electro Puno"),
                ("Zth_x_ohm","Ω","Electro Puno"),("curvas_proteccion","-","Electro Puno")]
    table(output/"03_CALCULO_ELECTRICO/ENTRADAS_PENDIENTES.csv",
          ["variable","valor","unidad","fuente_necesaria","estado"],
          [{"variable":a,"valor":"","unidad":b,"fuente_necesaria":c,"estado":"pendiente"} for a,b,c in elec_names])
    mech=[]
    for row in pn:
        mech.append({"sitio_id":row["id"],"segmento":row["segmento"],
                     "pk_kml_m":row["progresiva_kml_m"],"E_UTM_m":row["este_utm19s_m"],
                     "N_UTM_m":row["norte_utm19s_m"],"cota_levantada_m":"",
                     "apoyo_aprobado":"","vano_anterior_m":"","vano_siguiente_m":"",
                     "fijacion_conductor_m":"","H_conductor_N":"","w_conductor_N_m":"",
                     "presion_viento_Pa":"","suelo":"","despeje_calculado_m":"",
                     "estado":"sitio por inspeccionar; no apoyo aprobado"})
    table(output/"04_CALCULO_MECANICO/SITIOS_PARA_INGRESO_CAMPO.csv",list(mech[0]),mech)
    geo=[]
    progress=0.0
    for i,line in enumerate(lines,1):
        length=LineString(line).length
        lon0,lat0=TO_GEO.transform(*line[0]); lon1,lat1=TO_GEO.transform(*line[-1])
        geo.append({"segmento":i,"vertices":len(line),"pk_inicio_m":f"{progress:.3f}",
                    "pk_fin_m":f"{progress+length:.3f}","longitud_utm_m":f"{length:.6f}",
                    "E_inicio_m":f"{line[0][0]:.3f}","N_inicio_m":f"{line[0][1]:.3f}",
                    "lon_inicio":f"{lon0:.9f}","lat_inicio":f"{lat0:.9f}",
                    "E_fin_m":f"{line[-1][0]:.3f}","N_fin_m":f"{line[-1][1]:.3f}",
                    "lon_fin":f"{lon1:.9f}","lat_fin":f"{lat1:.9f}",
                    "eje":"KML original, no continuo","estado":"calculado; pendiente de campo"})
        progress+=length
    table(output/"02_DATOS_Y_CRITERIOS/SEGMENTOS_GEOMETRIA.csv",list(geo[0]),geo)
    records=[]
    for i,g in enumerate(gaps,1):
        a=lines[i-1][-1]; b=lines[i][0]
        records.append({"id":f"GAP-{i}","E_fin_origen_m":f"{a[0]:.3f}",
                        "N_fin_origen_m":f"{a[1]:.3f}","E_inicio_siguiente_m":f"{b[0]:.3f}",
                        "N_inicio_siguiente_m":f"{b[1]:.3f}",
                        "distancia_recta_m":f"{math.dist(a,b):.6f}",
                        "eje_levantado_m":"","interseccion_S3_S4":str(i==3),
                        "estado":"pendiente de campo"})
    table(output/"02_DATOS_Y_CRITERIOS/BRECHAS.csv",list(records[0]),records)

    write(output/"README.md",f"""
# Entrega académica Rev. 5 — línea primaria Capachica–Llachón

**Estado: anteproyecto académico documentado, no apto para construcción.** La Rev. 5 incorpora modelos eléctricos/mecánicos condicionados, sensibilidad adimensional, tabla maestra de entradas y plano CL-06 de brechas. CL-01 a CL-05 son copias identificadas **Rev. 4**, conservadas como planos de referencia, no reemitidas como diseño Rev. 5.

Resultado geométrico: KML original de cuatro segmentos, {kml_m:.3f} m UTM sin uniones; eje GIS alternativo {gis_m:.3f} m; diferencia {kml_m-gis_m:.3f} m entre ejes, no metrado. El KML tiene 187 vértices. PC={len(pc)} referencias GIS, PN={len(pn)} sitios por replantear y CV={len(cv)} alertas OSM. Ninguno es una estructura nueva aprobada.

**Sin resultados de dimensionamiento del proyecto:** no constan punto oficial, tensión, fases, demanda, conductor, parámetros de red, topografía de vanos, clima/terreno o permisos. Los factores de `ESCENARIOS_ADIMENSIONALES.csv` son hipótesis matemáticas, no voltajes, cargas ni materiales asignados.

Desde raíz del repositorio: `python proyectos/renzo-linea-primaria-capachica-llachon/scripts/generar_entrega_rev5.py --output RUTA_NUEVA`. No sobrescribe rutas existentes. Verificar con `--verify RUTA_EXISTENTE`. Dependencias en `00_INDICE_Y_RESUMEN/requirements.txt`; usar un entorno virtual. La copia del generador en el paquete es de referencia: requiere las fuentes originales y Rev. 4 en este repositorio. `manifest_rev5.json` da SHA-256 por archivo y la huella del manifiesto Rev. 4 de partida.
""")
    write(output/"00_INDICE_Y_RESUMEN/INDICE.md","""
# Índice de lectura

00 resumen, índice, revisión y script; 01 memoria del corredor; 02 datos maestros, geometría y copias controladas; 03 modelo y sensibilidad eléctrica; 04 modelo mecánico y registro de sitios; 05/06 planos PDF/DXF; 07 cantidades y presupuesto; 08 normativa y trazabilidad; 09 pruebas y manifiesto; 10 solicitudes y plan de campo.

CL-01 a CL-05 conservan **REV4** en el nombre y cajetín. CL-06 es el único plano nuevo REV5. Los originales Rev. 4 no fueron editados.
""")
    write(output/"00_INDICE_Y_RESUMEN/RESUMEN.md",f"""
# Resultados y estado Rev. 5

**Demostrado por cálculo sobre las fuentes:** {kml_m:.6f} m de KML UTM, {geod_m:.6f} m geodésicos, {gis_m:.6f} m de eje GIS alternativo; tres brechas rectas de {', '.join(f'{float(x["distancia_recta_m"]):.3f}' for x in gaps)} m; intersección S3/S4 en E {inter.x:.3f} m, N {inter.y:.3f} m. Estas magnitudes no completan el trazado de obra.

**Preliminar cartográfico:** {len(pc)} PC, {len(pn)} PN, {len(cv)} CV. **Hipótesis:** multiplicadores de sensibilidad sin unidades. **Pendiente:** 21 entradas esenciales registradas como nulos; cálculos de corriente/caída/pérdidas/protecciones, vanos/flechas/despejes/estructuras y presupuesto del proyecto. **Validación profesional:** requiere fuentes oficiales, mediciones y memoria revisada; no se solicitó aprobación.
""")
    write(output/"00_INDICE_Y_RESUMEN/REGISTRO_CAMBIOS.md","""
# Registro Rev. 5 respecto a Rev. 4

- Tabla maestra única con procedencia, método, estado y efecto de cada variable relevante.
- Modelos condicionados de corriente, caída, pérdidas, ampacidad corregida, Icc ideal, vano regulador, flecha parabólica, viento y resultante angular; datos sintéticos solo en pruebas.
- Sensibilidad adimensional de demanda y longitud; cero selección de conductor o protección.
- CL-06 nuevo para las tres brechas y la intersección S3/S4; CL-01..05 Rev. 4 permanecen como referencia sin cambiar de estado.
- Plantillas vacías de entrada y campo, matriz requisito–cálculo–plano–evidencia y verificación de integridad por SHA.
""")
    write(output/"01_MEMORIA_DESCRIPTIVA/MEMORIA.md",f"""
# Memoria descriptiva del alcance académico

La fuente principal es el KML manual original en WGS84 geográfico. Los cálculos métricos usan WGS84/UTM 19S. Los cuatro segmentos no forman aún un eje de obra continuo: las tres cuerdas entre extremos miden {sum(float(g['distancia_recta_m']) for g in gaps):.6f} m y el tercer par se cruza. La diferencia KML–GIS ({kml_m-gis_m:.6f} m) corresponde a trazados distintos; no se localiza como partida.

Electro Puno no ha confirmado conexión ni alcance de intervención. La geometría GIS puede representar infraestructura existente, pero las 40 PC no demuestran existencia/idoneidad en campo. Las 27 PN se derivan de geometría y no son spotting de postes; los intervalos entre PN no son vanos. Las 44 CV proceden de intersección con cartografía OSM y requieren clasificación y medición.

El paquete organiza datos y prepara modelos para completar el diseño tras la factibilidad, levantamiento, selección técnica y revisión profesional. No contempla BT, acometidas ni otras localidades.
""")
    write(output/"02_DATOS_Y_CRITERIOS/CRITERIOS.md","""
# Clasificación y criterios

`confirmado documental` significa que un archivo o dato informado existe y fue leído; no acredita realidad en campo. `calculado` significa operación reproducible sobre esa fuente. `estimado cartográfico` identifica referencias GIS/OSM que aún pueden contener errores u omisiones. `supuesto` queda reservado a los multiplicadores adimensionales de sensibilidad. `pendiente` bloquea decisiones de ingeniería.

La longitud física/electrica de diseño debe provenir del eje elegido y levantado, con cruces, apoyos y fases definidos. Las distancias rectas GAP no se suman a la línea como trabajo aprobado. La intersección S3/S4 se usa como alerta geométrica, no para alterar el KML.
""")
    write(output/"03_CALCULO_ELECTRICO/MEMORIA.md","""
# Cálculo eléctrico condicionado

**Resultado del proyecto: pendiente**, por falta de tensión, fases, demanda, conductor R/X/ampacidad, longitud eléctrica aprobada y equivalente de red. `rev5_modelos.py` no contiene parámetros por defecto del proyecto. `ENTRADAS_PENDIENTES.csv` conserva vacíos.

| Cálculo | Entrada y ecuación | Validez y aceptación |
|---|---|---|
| Corriente trifásica | I [A] = S [kVA]/(√3 U_LL [kV]) | Solo S coincidente y red trifásica equilibrada confirmadas; I ≤ ampacidad corregida. |
| Caída aproximada | ΔU [V] ≈ √3 I [A] L [km] (R [Ω/km] cosφ ± X [Ω/km] senφ) | Alimentador radial equilibrado, corriente uniforme, R a temperatura del caso; `+` inductivo. Se requiere flujo por tramo para cargas repartidas. Comparar ΔU/U con criterio oficial. |
| Pérdida Joule | P [W] = 3 I² R [Ω/km] L [km] | Corriente constante por tramo; sumar con perfil de carga para energía. |
| Ampacidad | I_perm [A] = I_cat [A] ∏f_i | Solo factores f>0 con ficha/criterio trazado; algunos pueden superar 1. Comparar I de punta y contingencia aplicable. |
| Icc trifásica ideal | Icc [A] = U_LL [V]/(√3 |Z_th| [Ω]) | Falla franca y equivalente de secuencia positiva. No resuelve mínimos, asimetría, monofásica ni coordinación. |

`ESCENARIOS_ADIMENSIONALES.csv` considera multiplicadores hipotéticos de demanda λ y longitud μ, con U, R, X, cosφ y topología constantes: I/I₀=λ; ΔU/ΔU₀=λμ; P/P₀=λ²μ. Por ejemplo λ=1,5 y μ=1,1 da 1,5; 1,65; 2,475 respectivamente. **No son amperios, voltios ni watts de esta línea.** No se emitió conductor ni protección elegidos.
""")
    write(output/"04_CALCULO_MECANICO/MEMORIA.md","""
# Cálculo mecánico condicionado

**Sin vanos ni apoyos de proyecto aprobados.** `SITIOS_PARA_INGRESO_CAMPO.csv` conserva las 27 PN como sitios geométricos y deja vacías cota, aceptación de apoyo, vanos y fuerzas. No se presentan flechas o despejes reales.

| Modelo | Ecuación y unidades | Límite de validez / criterio |
|---|---|---|
| Vano regulador | L_r [m]=√(ΣL_i³/ΣL_i), L_i>0 [m] | Tramo entre anclajes con conductor/carga/tensión uniforme; definir primero apoyos reales. |
| Flecha nivelada | f [m]≈w [N/m] L² [m²]/(8H [N]) | Parábola, apoyos a igual cota y flecha pequeña; usar catenaria/cambio de estado con topografía y temperatura para diseño. |
| Viento lineal | q [N/m]=p [Pa] d [m] C_d | Requiere presión de caso, diámetro y coeficiente justificables. |
| Ángulo de deflexión | F [N]=2H sin(θ/2) | Solo tensiones horizontales iguales; sumar viento, peso, desequilibrios y factores para estructura. |
| Despeje nivelado muestreado | z_c(x)=z_fijación-4f x(L-x)/L²; g_mín=min(z_c-z_obstáculo) [m] | Apoyos a igual cota y obstáculos con mismo datum; no considera oscilación ni perfil continuo. Comparar contra tabla vigente por tipo de cruce. |

Casos a resolver: temperatura extrema, viento aplicable, estados de tendido/rotura según norma y titular, esfuerzos longitudinales/transversales, aisladores/herrajes, poste y retenidas. Para despeje se necesita perfil con datum vertical, cota de conductor bajo flecha crítica y obstáculo/clase de cruce; para cimentación, reacciones y geotecnia. Sin esas entradas no se asigna altura, clase, cimentación ni retenida.
""")
    met=[("C-01","Longitud KML de cuatro segmentos",f"{kml_m:.3f}","m","calculado cartográfico; no obra"),
         ("C-02","Eje GIS alternativo",f"{gis_m:.3f}","m","calculado cartográfico; no obra"),
         ("C-03","Referencias PC",str(len(pc)),"registros","estimado GIS; no postes nuevos"),
         ("C-04","Sitios PN",str(len(pn)),"sitios","estimado geométrico; no postes nuevos"),
         ("C-05","Alertas CV",str(len(cv)),"alertas","estimado OSM; no cruces aprobados"),
         ("O-01","Postes/conductor/armados/protección","dato requerido","por definir","metrado de obra pendiente")]
    table(output/"07_METRADOS_Y_PRESUPUESTO/CANTIDADES_CLASIFICADAS.csv",
          ["id","concepto","cantidad","unidad","estado"],
          [dict(zip(["id","concepto","cantidad","unidad","estado"],r)) for r in met])
    shutil.copy2(REV4/"06_METRADOS_Y_PRESUPUESTO/PRESUPUESTO_PENDIENTE.csv",
                 output/"07_METRADOS_Y_PRESUPUESTO/PRESUPUESTO_PENDIENTE.csv")
    write(output/"07_METRADOS_Y_PRESUPUESTO/CRITERIO.md","""
# Cantidades y presupuesto

Las cinco primeras filas de `CANTIDADES_CLASIFICADAS.csv` son métricas cartográficas o conteos de registros, no cantidades de instalación. No hay metrado de obra, APU, precios, fecha base ni total calculable. `PRESUPUESTO_PENDIENTE.csv` mantiene el esquema de partidas Rev. 4 con campos explícitamente requeridos. Completar únicamente después de trazado, estructuras, materiales y cotizaciones trazables.
""")
    normative=read_table(REV4/"07_NORMATIVA_Y_ESPECIFICACIONES/MATRIZ_NORMATIVA.csv")
    trace=[]
    for row in normative:
        trace.append({"codigo":row["codigo"],"norma_url":row["url"],
                      "numeral":row["articulo_numeral"],"requisito":row["requisito"],
                      "calculo":"03_CALCULO_ELECTRICO/MEMORIA.md; 04_CALCULO_MECANICO/MEMORIA.md",
                      "plano":"05_PLANOS_PDF/CL-03_REV4.pdf; 05_PLANOS_PDF/CL-05_REV4.pdf; 05_PLANOS_PDF/CL-06_REV5.pdf",
                      "evidencia":"fuente identificada; cumplimiento sin demostrar",
                      "estado":"no verificable","accion":"cotejar versión/numeral y calcular con datos reales"})
    table(output/"08_NORMATIVA_Y_TRAZABILIDAD/MATRIZ_REQUISITOS.csv",list(trace[0]),trace)
    write(output/"08_NORMATIVA_Y_TRAZABILIDAD/FUENTES.md","""
# Fuentes normativas identificadas, consulta 14-10-2026

- MINEM, RM 0214-2011-MEM, aprobación de CNE Suministro 2011: https://www.gob.pe/institucion/minem/normas-legales/108753-0214-2011-mem
- OSINERGMIN, referencia RD 018-2002-EM/DGE de procedimientos de proyectos/obras: https://www.gob.pe/institucion/osinergmin/normas-legales/739536-018-2002-em-dge
- Electro Puno, requisitos publicados para instalaciones nuevas: https://www.gob.pe/institucion/electropuno/informes-publicaciones/6823816-requisitos-para-instalaciones-nuevas

Se verificó por índice público la identidad de esas publicaciones. No se pudo cotejar aquí el texto consolidado vigente, numerales específicos, modificación aplicable ni especificación MT del operador. Por ello la matriz no afirma cumplimiento. La página de suministro nuevo tampoco se toma como autorización de conexión de una línea MT.
""")
    shutil.copy2(REV4/"08_DATOS_GIS_Y_CAMPO/SOLICITUD_ELECTRO_PUNO_NO_ENVIADA.md",
                 output/"10_PENDIENTES_DE_CAMPO_Y_ELECTRO_PUNO/SOLICITUD_ELECTRO_PUNO_NO_ENVIADA.md")
    write(output/"10_PENDIENTES_DE_CAMPO_Y_ELECTRO_PUNO/PLAN_CAMPO.md","""
# Medición requerida

1. Control GNSS/estación total con datum horizontal y vertical, error, fecha y puntos crudos. Levantar GAP-1..3 y resolver intersección S3/S4; definir eje completo sin alterar el KML original.
2. Inventario físico con fotos/código/as-built de PC, inspección de 27 PN y alternativas de apoyos dentro de servidumbre comprobada. No construir según PN.
3. Depurar las 44 alertas CV e inventariar carreteras, cauces, edificios, telecomunicaciones, cercos y vegetación. Medir cota, ancho, gálibo, propietario/autoridad y permisos por cruce.
4. Levantar perfiles y obstáculos por posibles vanos, accesos, terreno y fundación; obtener ambiente de diseño y geotecnia/resistividad con métodos y laboratorio trazables.

El proyecto requiere respuesta formal de Electro Puno: factibilidad, punto/código/coordenadas oficiales, alimentador, tensión máxima/nominal, fases, capacidad disponible, parámetros de cortocircuito, protección/seccionamiento/PAT, configuración y especificaciones. El promotor debe entregar estudio de demanda actual y futura. No se enviaron solicitudes ni se realizaron visitas.
""")
    write(output/"09_CONTROL_DE_CALIDAD/CONTROL.md","""
# Control de calidad de Rev. 5

`--verify` reabre PDF, DXF, CSV y manifiesto, compara entidades métricas de CL-06 con KML, verifica las 21 entradas pendientes y diferencia clases de datos. Las pruebas unitarias usan valores sintéticos con solución analítica, validación de no finitos y escenarios adimensionales. Esto demuestra funcionamiento del software y coherencia de geometría; no sustituye revisión eléctrica, mecánica, legal o inspección de campo. CL-01..05 son copias idénticas por hash de Rev. 4. CL-06 se revisa visualmente mediante PNG. No se abrió AutoCAD.
""")
    write(output/"09_CONTROL_DE_CALIDAD/PRUEBAS_EJECUTADAS.md","""
# Pruebas ejecutadas en la preparación Rev. 5 (14-10-2026)

Comando: `python -m pytest proyectos/renzo-linea-primaria-capachica-llachon/tests/test_rev5_modelos.py proyectos/renzo-linea-primaria-capachica-llachon/tests/test_entrega_rev5.py -q` → **13 passed**. Tras añadir el norte y coordenadas de extremos a CL-06/tabla de segmentos, se repitió la prueba de integración afectada: **4 passed**. `--verify` se ejecuta al generar el paquete; reabre seis PDF y seis DXF, coteja la geometría KML/las tres brechas, hashes y 21 entradas pendientes. Las 42 pruebas Rev. 4 con 5 xfail históricos habían pasado en la revisión precedente y no se repitieron porque sus fuentes y código no cambiaron.

Se inspeccionó visualmente el PNG renderizado de CL-06. No se realizó inspección física, revisión profesional ni apertura en AutoCAD. Las pruebas sintéticas no son cálculos del alimentador real.
""")
    versions={name:importlib.metadata.version(name) for name in
              ("ezdxf","PyMuPDF","pyproj","shapely","reportlab","pytest")}
    (output/"09_CONTROL_DE_CALIDAD/DEPENDENCIAS_EJECUCION.json").write_text(
        json.dumps({"python":sys.version.split()[0],"paquetes":versions},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    indexed=[]
    for path in sorted(p for p in output.rglob("*") if p.is_file()):
        rel=path.relative_to(output).as_posix()
        indexed.append({"ruta":rel,"bytes":path.stat().st_size,
                        "clase":"plano Rev4 conservado" if "CL-0" in rel and "REV4" in rel else
                                "plano nuevo Rev5" if "CL-06_REV5" in rel else "documento o dato Rev5"})
    table(output/"00_INDICE_Y_RESUMEN/INDICE_ARCHIVOS.csv",["ruta","bytes","clase"],indexed)
    files={p.relative_to(output).as_posix():{"bytes":p.stat().st_size,"sha256":digest(p)}
           for p in output.rglob("*") if p.is_file() and p.name!="manifest_rev5.json"}
    (output/"manifest_rev5.json").write_text(json.dumps({"revision":5,"estado":"ACADEMICO_NO_CONSTRUCTIVO",
        "rev4_manifest_sha256":rev4_manifest,"original_kml_sha256":digest(ROOT/"sources/ruta topografica capachica llachon.kml"),
        "file_count":len(files),"files":files},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return verify(output)


def verify(output: Path):
    output=output.resolve()
    m=json.loads((output/"manifest_rev5.json").read_text(encoding="utf-8"))
    source_lines,source_gis,_,_,_,_,_,_,_,_=read_inputs()
    if m["file_count"]!=len(m["files"]):
        raise ValueError("conteo manifiesto inválido")
    actual={p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file() and p.name!="manifest_rev5.json"}
    if actual!=set(m["files"]):
        raise ValueError("archivos agregados/ausentes fuera de manifiesto")
    for rel,info in m["files"].items():
        path=output/rel
        if path.stat().st_size!=info["bytes"] or digest(path)!=info["sha256"]:
            raise ValueError(f"hash/tamaño alterado: {rel}")
    if digest(output/"02_DATOS_Y_CRITERIOS/fuentes/KML_ORIGINAL.kml")!=m["original_kml_sha256"]:
        raise ValueError("KML no corresponde a fuente")
    if digest(REV4/"manifest_entrega.json")!=m["rev4_manifest_sha256"]:
        raise ValueError("Rev. 4 cambió respecto a fuente Rev. 5")
    for n in range(1,7):
        code=f"CL-{n:02d}_REV{5 if n==6 else 4}"
        dxf=ezdxf.readfile(output/"06_PLANOS_EDITABLES"/(code+".dxf"))
        if dxf.audit().has_errors or dxf.header["$INSUNITS"]!=6:
            raise ValueError(f"DXF inválido: {code}")
        with fitz.open(output/"05_PLANOS_PDF"/(code+".pdf")) as pdf:
            if len(pdf)!=1 or abs(pdf[0].rect.width-420*MM)>1 or abs(pdf[0].rect.height-297*MM)>1:
                raise ValueError(f"PDF no A3: {code}")
            if n==6 and ("GAP-1" not in pdf[0].get_text() or "GAP-3" not in pdf[0].get_text()):
                raise ValueError("CL-06 no documenta brechas")
        if n<=5:
            for ext,fromdir,todir in [("pdf","04_PLANOS_PDF","05_PLANOS_PDF"),
                                        ("dxf","05_PLANOS_EDITABLES","06_PLANOS_EDITABLES")]:
                if digest(REV4/fromdir/(code+"."+ext))!=digest(output/todir/(code+"."+ext)):
                    raise ValueError(f"Rev. 4 alterada en copia: {code}")
        else:
            model=dxf.modelspace()
            kml_entities=[x for x in model if x.dxftype()=="LWPOLYLINE" and x.dxf.layer=="KML"]
            if len(kml_entities)!=4:
                raise ValueError("CL-06 requiere 4 segmentos KML")
            for entity,source in zip(kml_entities,source_lines):
                coords=list(entity.get_points("xy"))
                if len(coords)!=len(source) or any(abs(a-b)>.001 for pair,ref in zip(coords,source) for a,b in zip(pair,ref)):
                    raise ValueError("CL-06 coordenadas KML no coinciden")
            gis_entities=[x for x in model if x.dxftype()=="LWPOLYLINE" and x.dxf.layer=="GIS"]
            if len(gis_entities)!=1 or len(list(gis_entities[0].get_points("xy")))!=len(source_gis):
                raise ValueError("CL-06 eje GIS incompleto")
            gap_entities=[x for x in model if x.dxftype()=="LINE" and x.dxf.layer=="BRECHA"]
            if len(gap_entities)!=3:
                raise ValueError("CL-06 requiere 3 brechas")
            for i,entity in enumerate(gap_entities):
                for point,source in [(entity.dxf.start,source_lines[i][-1]),
                                     (entity.dxf.end,source_lines[i+1][0])]:
                    if math.dist(tuple(point)[:2],source)>.001:
                        raise ValueError("CL-06 brecha no coincide con KML")
    data=read_table(output/"02_DATOS_Y_CRITERIOS/DATOS_MAESTROS.csv")
    if sum(r["estado"]=="pendiente" for r in data)!=21:
        raise ValueError("datos pendientes mal clasificados")
    if len(read_table(output/"03_CALCULO_ELECTRICO/ESCENARIOS_ADIMENSIONALES.csv"))!=9:
        raise ValueError("escenarios incompletos")
    if len(read_table(output/"04_CALCULO_MECANICO/SITIOS_PARA_INGRESO_CAMPO.csv"))!=27:
        raise ValueError("sitios mecánicos incompletos")
    for row in read_table(output/"08_NORMATIVA_Y_TRAZABILIDAD/MATRIZ_REQUISITOS.csv"):
        for field in ("calculo","plano"):
            for rel in row[field].split("; "):
                if not (output/rel).is_file():
                    raise ValueError(f"referencia rota en {row['codigo']}: {rel}")
    print(json.dumps({"estado":"verificado por software","archivos":m["file_count"],"planos":6,
                      "dimensionamiento_proyecto":"pendiente","ruta":str(output)},ensure_ascii=False))
    return m


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=DEFAULT)
    parser.add_argument("--verify",type=Path)
    args=parser.parse_args()
    verify(args.verify) if args.verify else build(args.output)
