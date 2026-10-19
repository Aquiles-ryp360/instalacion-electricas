"""Cinco láminas A3 Rev. 4 desde primitivas compartidas DXF/PDF.

Las vistas describen cartografía y datos pendientes; no son planos constructivos.
"""
from __future__ import annotations

import math
from pathlib import Path

import ezdxf
import fitz
from pyproj import Transformer
from reportlab.pdfgen import canvas

MM = 72 / 25.4
ezdxf.options.write_fixed_meta_data_for_testing = True  # Evita fechas y GUID aleatorios en la entrega.
TO_UTM = Transformer.from_crs(4326, 32719, always_xy=True)
COLORS = {
    "KML": ((29, 91, 145), 5), "GIS": ((112, 112, 112), 8),
    "PC": ((198, 52, 52), 1), "PN": ((21, 120, 153), 4),
    "CV": ((205, 122, 25), 30), "NOTA": ((120, 40, 40), 1),
    "MARCO": ((30, 40, 54), 7), "TEXT": ((30, 40, 54), 7),
}


class Sheet:
    def __init__(self, code: str, title: str, directory: Path):
        self.code, self.title = code, title
        self.doc = ezdxf.new("R2010")
        self.doc.header["$INSUNITS"] = 6  # Modelo UTM en metros.
        for name, (_, aci) in COLORS.items():
            self.doc.layers.new(name, dxfattribs={"color": aci})
        self.paper = self.doc.layouts.new(code + "_A3")
        self.paper.page_setup(size=(420, 297), margins=(8, 8, 8, 8), units="mm")
        self.pdf_path = directory / (code + "_REV4.pdf")
        self.dxf_path = directory / (code + "_REV4.dxf")
        self.pdf = canvas.Canvas(str(self.pdf_path), pagesize=(420 * MM, 297 * MM), pageCompression=1, invariant=1)
        self.rect(8, 8, 404, 281, "MARCO")
        self.line(8, 38, 412, 38, "MARCO")
        self.text(14, 283, code + " | " + title, 5.0)
        self.text(14, 272, "CAPACHICA - LLACHON  |  REV 4  |  14 OCT 2026  |  A3 horizontal", 2.8)
        self.text(14, 27, "ANTEPROYECTO CARTOGRAFICO - NO APTO PARA CONSTRUCCION", 3.0, "NOTA")
        self.text(14, 16, "WGS84 / UTM 19S (EPSG:32719) | Modelo m | Presentacion mm | Autor: por designar", 2.3)

    def _color(self, layer: str):
        rgb, _ = COLORS[layer]
        self.pdf.setStrokeColorRGB(*(c / 255 for c in rgb))
        self.pdf.setFillColorRGB(*(c / 255 for c in rgb))

    def text(self, x, y, value, height=2.5, layer="TEXT"):
        value = str(value)
        self.paper.add_text(value, dxfattribs={"layer": layer, "height": height}).set_placement((x, y))
        self._color(layer)
        self.pdf.setFont("Helvetica", height * MM * .88)
        self.pdf.drawString(x * MM, y * MM, value)

    def line(self, x1, y1, x2, y2, layer="MARCO", width=.25):
        self.paper.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer})
        self._color(layer)
        self.pdf.setLineWidth(width * MM)
        self.pdf.line(x1 * MM, y1 * MM, x2 * MM, y2 * MM)

    def rect(self, x, y, w, h, layer="MARCO"):
        points = [(x, y), (x+w, y), (x+w, y+h), (x, y+h), (x, y)]
        self.poly(points, layer)

    def poly(self, points, layer="KML", width=.35):
        if len(points) < 2:
            return
        self.paper.add_lwpolyline(points, dxfattribs={"layer": layer})
        self._color(layer)
        self.pdf.setLineWidth(width * MM)
        path = self.pdf.beginPath()
        path.moveTo(points[0][0] * MM, points[0][1] * MM)
        for x, y in points[1:]:
            path.lineTo(x * MM, y * MM)
        self.pdf.drawPath(path)

    def circle(self, x, y, r=1.3, layer="PN"):
        self.paper.add_circle((x, y), r, dxfattribs={"layer": layer})
        self._color(layer)
        self.pdf.setLineWidth(.3 * MM)
        self.pdf.circle(x * MM, y * MM, r * MM)

    def finish(self, view_dir: Path):
        self.pdf.showPage()
        self.pdf.save()
        self.doc.saveas(self.dxf_path)
        doc = ezdxf.readfile(self.dxf_path)
        if doc.audit().has_errors or doc.header["$INSUNITS"] != 6:
            raise ValueError(f"DXF inválido: {self.dxf_path}")
        with fitz.open(self.pdf_path) as pdf:
            if len(pdf) != 1 or not (1180 < pdf[0].rect.width < 1200):
                raise ValueError(f"PDF A3 inválido: {self.pdf_path}")
            pix = pdf[0].get_pixmap(matrix=fitz.Matrix(150/72, 150/72), alpha=False)
            pix.save(view_dir / (self.code + "_REV4.png"))


def _transform(points, x, y, w, h, pad=5):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    sx = (w-2*pad)/max(xmax-xmin, 1)
    sy = (h-2*pad)/max(ymax-ymin, 1)
    scale = min(sx, sy)
    ox = x + (w-(xmax-xmin)*scale)/2
    oy = y + (h-(ymax-ymin)*scale)/2
    return lambda p: (ox+(p[0]-xmin)*scale, oy+(p[1]-ymin)*scale), scale, (xmin, xmax, ymin, ymax)


def make_plans(out_pdf: Path, out_dxf: Path, out_png: Path, lines, gis, pc, pn, cv, gaps, report):
    """Entrega láminas; DXF y PDF reciben los mismos comandos de hoja."""
    for folder in (out_pdf, out_dxf, out_png):
        folder.mkdir(parents=True, exist_ok=True)
    all_points = [xy for line in lines for xy in line] + list(gis)

    s = Sheet("CL-01", "Ubicacion y comparacion de ejes", out_pdf)
    f, scale, bounds = _transform(all_points, 20, 55, 285, 205)
    s.rect(18, 53, 290, 210)
    s.text(24, 255, "KML manual (azul) / eje GIS inferido (gris)", 2.8)
    s.poly([f(xy) for xy in gis], "GIS", .42)
    for line in lines:
        s.poly([f(xy) for xy in line], "KML", .55)
    for i, (a, b) in enumerate(gaps, 1):
        x, y = f(a)
        s.circle(x, y, 1.5, "NOTA")
        s.text(x+2, y+2, f"GAP-{i}", 2.1, "NOTA")
    x, y = f(TO_UTM.transform(-69.8316111, -15.6421333)); s.circle(x, y, 2.1, "NOTA")
    s.text(24, 242, "N ^", 4)
    scale_den = 1000 / scale
    bar = 1000 * scale
    s.line(25, 62, 25+bar, 62, "MARCO", .75)
    s.text(25, 65, f"1 km | escala aprox. 1:{scale_den:,.0f} en A3", 2.4)
    s.text(25, 57, f"E {bounds[0]:.0f}-{bounds[1]:.0f} m; N {bounds[2]:.0f}-{bounds[3]:.0f} m", 2.0)
    s.text(315, 253, "Fuentes y estado", 3)
    for y, label, layer in [(241,"KML original: 4 segmentos","KML"),(232,"GIS GISEM: eje alternativo","GIS"),
                            (223,"Punto TMT: candidato","NOTA")]:
        s.line(316,y,326,y,layer,.6); s.text(329,y-1,label,2.3)
    for y, label in [(207,f"KML: {report['longitud_kml_sin_empalmes_m']/1000:.3f} km"),
                     (198,f"GIS: {report['longitud_gis_m']/1000:.3f} km"),
                     (189,"Ejes distintos; no sumar brechas"),
                     (177,"Conexion no aprobada"),
                     (168,"Sin limites regionales certificados"),
                     (159,"Sin servidumbres verificadas")]:
        s.text(316,y,label,2.3,"NOTA" if y in (189,177) else "TEXT")
    s.text(315, 105, "No es trazado aprobado.", 2.8, "NOTA")
    s.text(315, 96, "Altitudes KML no utilizables.", 2.3)
    s.text(14, 44, "Fuente: KML original, GISEM; distancias UTM. Revisar continuidad y punto de conexion.", 2.5)
    s.finish(out_png); (out_dxf/s.dxf_path.name).write_bytes(s.dxf_path.read_bytes()); s.dxf_path.unlink()

    s = Sheet("CL-02", "Planta por segmentos: alertas de gabinete", out_pdf)
    panels = [(18,151),(219,151),(18,51),(219,51)]
    for i, (line, (x,y)) in enumerate(zip(lines, panels), 1):
        s.rect(x,y,185,95)
        s.text(x+3,y+88,f"SEGMENTO {i} | PN: {sum(int(z['segmento'])==i for z in pn)} | CV: {sum(int(z['segmento'])==i for z in cv)}",2.6)
        f, sc, _ = _transform(line,x+4,y+7,177,76,3)
        s.poly([f(v) for v in line],"KML",.5)
        for row in pc:
            if int(row['segmento']) == i:
                s.circle(*f((float(row['este_m']),float(row['norte_m']))),.75,"PC")
        placed=[]
        for row in pn:
            if int(row['segmento']) == i:
                xx,yy=f((float(row['este_utm19s_m']),float(row['norte_utm19s_m'])))
                s.circle(xx,yy,1.15,"PN")
                if all(math.dist((xx,yy), previous)>15 for previous in placed):
                    s.text(xx+1.5,yy+1,row['id'],1.7,"PN")
                    placed.append((xx,yy))
        for row in cv:
            if int(row['segmento']) == i:
                s.circle(*f((float(row['este_utm19s_m']),float(row['norte_utm19s_m']))),.55,"CV")
        s.text(x+4,y+3,"PN=por replantear  PC=GIS  CV=OSM | IDs completos CL-04/CSV",1.8)
    s.text(18,251,"N ^ | Segmentos sin empalme. Progresivas acumuladas excluyen brechas.",2.7)
    s.text(18,44,"3 empalmes por levantar; 27 PN, 40 PC y 44 CV: no constituyen diseno de apoyos/cruces.",2.35,"NOTA")
    s.finish(out_png); (out_dxf/s.dxf_path.name).write_bytes(s.dxf_path.read_bytes()); s.dxf_path.unlink()

    s = Sheet("CL-03", "Perfil longitudinal: topografia pendiente", out_pdf)
    s.rect(22,77,375,171)
    s.text(36,224,"ELEVACIONES NO DISPONIBLES PARA EL EJE KML",5,"NOTA")
    s.text(36,210,"No calcular flechas, alturas ni galibos con muestras SRTM del eje GIS.",3)
    total = report['longitud_kml_sin_empalmes_m']
    s.line(35,112,388,112,"MARCO",.5)
    starts=[0.0]
    for segment in lines[:-1]:
        starts.append(starts[-1]+sum(math.dist(a,b) for a,b in zip(segment,segment[1:])))
    for i, st in enumerate(starts,1):
        x=35+353*st/total
        s.line(x,103,x,122,"NOTA")
        s.text(x+1,126,f"S{i}",2.6)
        s.text(x+1,96,f"{st:.0f} m",2.2)
    s.text(354,96,f"FIN {total:.0f} m",2.2)
    s.text(32,160,"Referencia horizontal: suma de cuatro polilineas sin enlaces.",3)
    s.text(32,146,"GAP-1, GAP-2 y GAP-3 requieren levantamiento y decision de trazado.",2.7)
    s.text(32,133,"Datum vertical, perfiles transversales y puntos de cruce: pendientes.",2.7)
    s.text(22,54,"Esta lamina NO constituye un perfil topografico constructivo.",3,"NOTA")
    s.finish(out_png); (out_dxf/s.dxf_path.name).write_bytes(s.dxf_path.read_bytes()); s.dxf_path.unlink()

    s = Sheet("CL-04", "Inventario PC y sitios PN separados", out_pdf)
    s.text(17,254,"PC: estructuras publicadas GISEM; existencia/idoneidad sin verificar",2.65)
    s.text(215,254,"PN: sitios geometricos para replanteo; NO instalar",2.65,"NOTA")
    s.line(207,51,207,260,"MARCO")
    s.text(17,245,"ID      Codigo GISEM       PK m     Sep. m",2.8)
    s.text(215,245,"ID       Seg.     PK m       Funcion",2.8)
    for i,row in enumerate(pc):
        y=239-i*4.6
        s.text(17,y,f"{row['id']}  {row['codigo_gisem']}  {float(row['estacion_m']):7.1f}  {float(row['distancia_eje_m']):5.1f}",2.9)
    for i,row in enumerate(pn):
        y=239-i*6.4
        role="EXTREMO" if "extremo" in row['funcion_preliminar'] or "inicio" in row['funcion_preliminar'] or "fin" in row['funcion_preliminar'] else "GIRO"
        s.text(215,y,f"{row['id']}    {row['segmento']}     {float(row['progresiva_kml_m']):8.1f}    {role}",2.9,"PN")
    s.text(17,46,"Tablas completas y coordenadas: 08_DATOS_GIS_Y_CAMPO. PC y PN no son metrados de obra.",2.35,"NOTA")
    s.finish(out_png); (out_dxf/s.dxf_path.name).write_bytes(s.dxf_path.read_bytes()); s.dxf_path.unlink()

    s = Sheet("CL-05", "Esquema conceptual de conexion", out_pdf)
    for x,w,label1,label2 in [(25,101,"TRAMO GIS","TMT001868169"),
                               (158,107,"ALIMENTADOR /","PROTECCION PENDIENTES"),
                               (300,91,"DEMANDA / RED","POR DEFINIR")]:
        s.rect(x,151,w,42)
        s.text(x+6,177,label1,3.3)
        s.text(x+6,163,label2,2.6)
    for x1,x2 in [(126,158),(265,300)]:
        s.line(x1,172,x2,172,"NOTA",.7)
        s.line(x2-5,175,x2,172,"NOTA",.7)
        s.line(x2-5,169,x2,172,"NOTA",.7)
    s.text(28,123,"Representacion de dependencias de informacion; NO es unifilar operativo.",3.2,"NOTA")
    s.text(28,108,"Tension, fases, conductor, seccionamiento, protecciones, aislamiento y PAT: pendientes.",2.8)
    s.text(28,94,"Solicitar factibilidad, punto de diseno y unifilar oficial a Electro Puno.",2.8)
    s.text(28,59,"No se representa transformador, capacidad disponible ni conexion aprobada.",2.7,"NOTA")
    s.finish(out_png); (out_dxf/s.dxf_path.name).write_bytes(s.dxf_path.read_bytes()); s.dxf_path.unlink()

    # Geometría métrica editable: misma fuente, capas semánticas y coordenadas UTM.
    for code in ("CL-01","CL-02"):
        path=out_dxf/(code+"_REV4.dxf")
        doc=ezdxf.readfile(path)
        model=doc.modelspace()
        for line in lines:
            model.add_lwpolyline(line,dxfattribs={"layer":"KML"})
        model.add_lwpolyline(gis,dxfattribs={"layer":"GIS"})
        if code=="CL-01":
            model.add_circle(TO_UTM.transform(-69.8316111,-15.6421333),2,dxfattribs={"layer":"NOTA"})
        for row in pc:
            model.add_circle((float(row['este_m']),float(row['norte_m'])),2,dxfattribs={"layer":"PC"})
        for row in pn:
            model.add_circle((float(row['este_utm19s_m']),float(row['norte_utm19s_m'])),2,dxfattribs={"layer":"PN"})
        for row in cv:
            model.add_circle((float(row['este_utm19s_m']),float(row['norte_utm19s_m'])),1,dxfattribs={"layer":"CV"})
        doc.saveas(path)
    return ["CL-01","CL-02","CL-03","CL-04","CL-05"]
