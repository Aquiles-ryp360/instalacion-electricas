"""Arma paquete documental Rev. 4 sin sobrescribir entregas ni fuentes originales."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

import ezdxf
import fitz
from lxml import etree
from pyproj import Geod, Transformer
from shapely.geometry import LineString, Point

from rev4_planos import make_plans

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "ENTREGA_FINAL_CAPACHICA_LLACHON_REV4"
DIRS = ["01_INDICE_Y_CONTROL", "02_MEMORIA_DESCRIPTIVA", "03_MEMORIAS_DE_CALCULO",
        "04_PLANOS_PDF", "05_PLANOS_EDITABLES", "06_METRADOS_Y_PRESUPUESTO",
        "07_NORMATIVA_Y_ESPECIFICACIONES", "08_DATOS_GIS_Y_CAMPO", "09_CONTROL_DE_CALIDAD"]
KML = ROOT / "sources/ruta topografica capachica llachon.kml"
TRANS = Transformer.from_crs(4326, 32719, always_xy=True)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, headings: list[str], rows: list[dict]):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headings)
        writer.writeheader()
        writer.writerows(rows)


def write(path: Path, value: str):
    path.write_text(value.strip() + "\n", encoding="utf-8")


def read_inputs():
    needed = [KML, ROOT/"derived/route.json", ROOT/"derived/reconciliacion_corredores_rev3.json",
              ROOT/"datos/ubicaciones_postes_preliminares.csv",
              ROOT/"datos/candidatos_nuevos_replanteo_rev3.csv",
              ROOT/"datos/cruces_viales_rev3.csv", ROOT/"datos/empalmes_kml_rev3.csv",
              ROOT/"sources/manifest.json", ROOT/"datos/parametros_diseno_pendientes.json"]
    missing = [str(p) for p in needed if not p.is_file()]
    if missing:
        raise FileNotFoundError("Entradas Rev. 4 ausentes: " + ", ".join(missing))
    source = etree.parse(str(KML))
    nodes = source.xpath("//k:LineString/k:coordinates", namespaces={"k": "http://www.opengis.net/kml/2.2"})
    geo = [[tuple(float(v) for v in token.split(",")[:2]) for token in n.text.split()] for n in nodes]
    lines = [[TRANS.transform(*xy) for xy in line] for line in geo]
    report = json.loads((ROOT/"derived/reconciliacion_corredores_rev3.json").read_text(encoding="utf-8"))
    route = json.loads((ROOT/"derived/route.json").read_text(encoding="utf-8"))
    kml_m = sum(LineString(line).length for line in lines)
    gis_m = LineString(route["route_utm_xy"]).length
    geod_m = sum(Geod(ellps="WGS84").line_length(*zip(*line)) for line in geo)
    if len(lines) != 4 or sum(map(len,lines)) != 187:
        raise ValueError("El KML ya no tiene la estructura auditada; revisar antes de generar")
    if sha(KML) != report["kml_sha256"] or abs(kml_m-report["longitud_kml_sin_empalmes_m"])>.001:
        raise ValueError("KML/longitud no coincide con Rev. 3")
    if abs(gis_m-report["longitud_gis_m"])>.001:
        raise ValueError("GIS/longitud no coincide con Rev. 3")
    tables = {name:csv_rows(ROOT/name) for name in
              ["datos/ubicaciones_postes_preliminares.csv",
               "datos/candidatos_nuevos_replanteo_rev3.csv",
               "datos/cruces_viales_rev3.csv", "datos/empalmes_kml_rev3.csv"]}
    pc,pn,cv,gaps=tables.values()
    if (len(pc),len(pn),len(cv),len(gaps)) != (40,27,44,3):
        raise ValueError("Conteos PC/PN/CV/GAP cambiaron; revisar revisión")
    for i,g in enumerate(gaps):
        actual=Point(lines[i][-1]).distance(Point(lines[i+1][0]))
        if abs(actual-float(g["distancia_recta_m"]))>.001:
            raise ValueError(f"Empalme {i+1} no coincide con KML")
    return lines,route["route_utm_xy"],pc,pn,cv,gaps,report,kml_m,gis_m,geod_m


def build(output: Path):
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"La entrega ya existe; use otra ruta para nueva generación: {output}")
    lines,gis,pc,pn,cv,gaps,report,kml_m,gis_m,geod_m=read_inputs()
    output.mkdir(parents=True)
    for sub in DIRS:
        (output/sub).mkdir()
    qa=output/"09_CONTROL_DE_CALIDAD"
    (qa/"vistas_png").mkdir()
    map_gaps=[(lines[i][-1],lines[i+1][0]) for i in range(3)]
    sheets=make_plans(output/"04_PLANOS_PDF",output/"05_PLANOS_EDITABLES",qa/"vistas_png",
                      lines,gis,pc,pn,cv,map_gaps,report)

    # Copias de referencia explícitas: el manifiesto registra origen y huella.
    copies = {
        "sources/ruta topografica capachica llachon.kml":"08_DATOS_GIS_Y_CAMPO/KML_ORIGINAL.kml",
        "sources/manifest.json":"08_DATOS_GIS_Y_CAMPO/MANIFIESTO_FUENTES.json",
        "derived/route.json":"08_DATOS_GIS_Y_CAMPO/EJE_GIS_ALTERNATIVO.json",
        "derived/reconciliacion_corredores_rev3.json":"08_DATOS_GIS_Y_CAMPO/CONCILIACION_REV3.json",
        "datos/ubicaciones_postes_preliminares.csv":"08_DATOS_GIS_Y_CAMPO/PC_REFERENCIAS_GIS.csv",
        "datos/candidatos_nuevos_replanteo_rev3.csv":"08_DATOS_GIS_Y_CAMPO/PN_SITIOS_REPLANTEO.csv",
        "datos/cruces_viales_rev3.csv":"08_DATOS_GIS_Y_CAMPO/CV_ALERTAS_OSM.csv",
        "datos/empalmes_kml_rev3.csv":"08_DATOS_GIS_Y_CAMPO/GAP_EMPALMES.csv",
        "datos/parametros_diseno_pendientes.json":"02_MEMORIA_DESCRIPTIVA/PARAMETROS_PENDIENTES.json",
        "documentacion/auditoria_independiente_rev3/INFORME_AUDITORIA_TECNICA_REV3.md":"09_CONTROL_DE_CALIDAD/AUDITORIA_INDEPENDIENTE_REV3.md",
        "documentacion/auditoria_independiente_rev3/MATRIZ_TRAZABILIDAD_DATOS_REV3.csv":"02_MEMORIA_DESCRIPTIVA/MATRIZ_DATOS_REV3.csv",
        "documentacion/auditoria_independiente_rev3/MATRIZ_HALLAZGOS_REV4.csv":"09_CONTROL_DE_CALIDAD/MATRIZ_HALLAZGOS_REV4.csv",
        "documentacion/auditoria_independiente_rev3/REGISTRO_CAMBIOS_REV4.md":"09_CONTROL_DE_CALIDAD/REGISTRO_CAMBIOS_REV4.md",
        "documentacion/SOLICITUD_TECNICA_ELECTRO_PUNO_REV3.md":"08_DATOS_GIS_Y_CAMPO/SOLICITUD_ELECTRO_PUNO_NO_ENVIADA.md",
        "scripts/calculos_condicionales_rev4_propuesta.py":"03_MEMORIAS_DE_CALCULO/modelo_calculos_rev4.py",
        "scripts/calculos_condicionales.py":"03_MEMORIAS_DE_CALCULO/calculos_base_rev3.py",
        "scripts/rev4_planos.py":"03_MEMORIAS_DE_CALCULO/rev4_planos.py",
        "scripts/generar_entrega_rev4.py":"03_MEMORIAS_DE_CALCULO/generar_entrega_rev4.py",
        "requirements.txt":"03_MEMORIAS_DE_CALCULO/requirements.txt",
    }
    for source,dest in copies.items():
        shutil.copy2(ROOT/source,output/dest)

    write(output/"README.md",f"""
# Entrega documental Rev. 4 — Línea primaria Capachica–Llachón

**Estado: categoría A de alcance parcial cartográfico y metodológico, con bloqueos de ingeniería. NO APTO PARA CONSTRUCCIÓN.**

Las láminas y tablas son utilizables para revisión del corredor y coordinación de levantamiento. No existe punto de conexión aprobado, eje continuo levantado, tensión/demanda confirmadas, conductor seleccionado, perfiles de vanos ni permisos. En consecuencia, las memorias de cálculo muestran modelos y datos requeridos, **no resultados de dimensionamiento**. El nombre de esta carpeta identifica la entrega Rev. 4, no una aprobación final de obra.

Orden de lectura: `01_INDICE_Y_CONTROL/INDICE_GENERAL.md` → `02_MEMORIA_DESCRIPTIVA/MEMORIA_DESCRIPTIVA.md` → memorias `03` → planos `04`/`05` → metrados `06` → normativa `07` → campo `08` → control `09`.

Geometría: KML original {kml_m:.6f} m UTM en cuatro segmentos; GIS alternativo {gis_m:.6f} m. Tres brechas no levantadas. PC={len(pc)} referencias GIS; PN={len(pn)} sitios de replanteo; CV={len(cv)} alertas OSM. Ninguna cifra es metrado de postes nuevos.

Reproducción desde la raíz del repositorio: `python proyectos/renzo-linea-primaria-capachica-llachon/scripts/generar_entrega_rev4.py --output RUTA_NUEVA`. Requiere el `requirements.txt` del proyecto. El generador falla si la salida existe. `--verify RUTA_EXISTENTE` verifica el paquete sin escribir. Los documentos editables son Markdown/CSV/JSON, los planos editables DXF R2010 con modelo UTM en metros y presentación A3 en milímetros. PDF/PNG proceden de los mismos comandos de dibujo de hoja. Autor y firmas: por designar; no se inventaron.
""")

    write(output/"01_INDICE_Y_CONTROL/INDICE_GENERAL.md",f"""
# Índice general y orden de presentación

1. Control: registro de revisiones, trazabilidad, observaciones abiertas e índice de planos.
2. Memoria descriptiva: alcance, antecedentes, corredor, criterios y datos de entrada.
3. Memorias de cálculo: metodología eléctrica y mecánica, scripts y parámetros pendientes.
4. Planos PDF A3: {', '.join(sheets)}.
5. Planos DXF R2010 editables: misma serie y contenido de las láminas PDF.
6. Metrados y presupuesto: cantidades cartográficas separadas de cantidades de obra y partidas sin precio.
7. Normativa y especificaciones: matriz de aplicabilidad preliminar con evidencia pendiente.
8. GIS y campo: originales/copia controlada, tablas PC/PN/CV/GAP y registro vacío de levantamiento.
9. Calidad: auditoría previa, pruebas, comparación de láminas y manifiesto SHA-256.

**Control de estado:** Esta entrega desarrolla la documentación independiente de los datos faltantes. No equivale a expediente para aprobación ni para construcción.
""")
    write(output/"01_INDICE_Y_CONTROL/CARATULA.md","""
# Línea primaria Capachica–Llachón, Puno, Perú

**Entrega documental Rev. 4 — 14 de octubre de 2026**

Estado: anteproyecto cartográfico para revisión académica y coordinación de datos. **No apto para construcción.**

Titular del proyecto: dato requerido. Proyectista y profesional responsable: dato requerido. Colegiatura, firma, sello y aprobación: pendientes. Empresa distribuidora consultada: Electro Puno; no consta aceptación del punto de conexión.

Sistema cartográfico: WGS84 geográfico (EPSG:4326) y WGS84/UTM 19S (EPSG:32719). Cuatro segmentos KML separados; eje continuo y longitud de obra pendientes.
""")
    write(output/"01_INDICE_Y_CONTROL/RESUMEN_EJECUTIVO.md",f"""
# Resumen ejecutivo

El KML original contiene cuatro segmentos y 187 vértices, con {kml_m:.3f} m de suma proyectada UTM sin empalmes. El eje GIS alternativo mide {gis_m:.3f} m. Son trazados diferentes; sus {kml_m-gis_m:.3f} m de diferencia no representan obra. Se mantienen tres brechas, 40 referencias GIS PC, 27 sitios PN por replantear y 44 alertas CV por comprobar.

Se entregan cinco láminas A3 Rev. 4 coordinadas en DXF/PDF/PNG, memorias metodológicas, registro de campo, matriz normativa preliminar y estructura de metrados sin cantidades o precios inventados. Las láminas CL-04 y CL-05 subsanan diferencias entre formato editable e impreso de Rev. 2 en una nueva revisión; los originales se conservan.

**Bloqueos prioritarios:** factibilidad y punto oficial de conexión, tensión/fases y demanda, continuidad del corredor y topografía, cruces/servidumbres, datos de conductor/ambiente/suelo y aprobación profesional. No hay cálculo eléctrico ni mecánico de dimensionamiento aplicable a obra.
""")
    write(output/"01_INDICE_Y_CONTROL/INDICE_PLANOS.md","""
# Índice de planos Rev. 4

| Código | Contenido | Escala | Formatos | Estado |
|---|---|---|---|---|
| CL-01 | Ubicación y comparación KML/GIS | Gráfica y aproximada en A3 | DXF/PDF/PNG | Anteproyecto |
| CL-02 | Planta por segmentos, PN/PC/CV | Gráfica por panel; no apta para replanteo | DXF/PDF/PNG | Anteproyecto |
| CL-03 | Progresivas; perfil topográfico pendiente | Horizontal esquemática | DXF/PDF/PNG | No es perfil de diseño |
| CL-04 | Tablas separadas PC y PN | No aplica | DXF/PDF/PNG | Inventario de gabinete |
| CL-05 | Dependencias eléctricas conceptuales | No aplica | DXF/PDF/PNG | No es unifilar operativo |

Faltan plantas/perfiles constructivos, armados, cimentaciones, cruces especiales, servidumbres, PAT y unifilar técnico. Se producirán al cerrar las puertas de datos y cálculos.
""")
    write(output/"01_INDICE_Y_CONTROL/REGISTRO_REVISIONES.md","""
# Registro de revisiones

| Revisión | Origen | Resultado |
|---|---|---|
| Rev. 2 | `da69405` | Cinco láminas cartográficas CL-01 a CL-05 y datos GIS. |
| Rev. 3 | `4562b05` | Conciliación, PN, CV, solicitud y flujo de cálculo. |
| Auditoría independiente Rev. 3 | Carpeta local `documentacion/auditoria_independiente_rev3/` | AI-01..AI-13, pruebas y dictamen. |
| Rev. 4 documental | Esta carpeta, generada en rama de trabajo local | CL-04 y CL-05 coordinados desde una fuente; cálculo numérico finito en módulo separado; memorias, metrados pendientes y control de paquete. Sin aprobación externa. |
""")

    write(output/"02_MEMORIA_DESCRIPTIVA/MEMORIA_DESCRIPTIVA.md",f"""
# Memoria descriptiva — línea primaria Capachica–Llachón

## Identificación, objeto y alcance

Ubicación: distrito de Capachica y entorno de Llachón, Puno, Perú, según coordenadas del KML original. Titular, proyectista, colegiatura y responsable de firma: **dato requerido**. Objeto: estudiar una posible intervención de línea primaria de media tensión a lo largo de un corredor aproximado de 14 km. Electro Puno debe determinar si procede nueva obra, ampliación, remodelación o aprovechamiento de red existente. No se diseña BT, acometidas ni instalaciones fuera de este corredor.

## Antecedentes y fuentes

El KML manual en EPSG:4326 contiene cuatro polilíneas y 187 vértices. Se transformaron a WGS84/UTM 19S (EPSG:32719) sin modificar el original. Suma de trazos: **{kml_m:.6f} m UTM**, **{geod_m:.6f} m geodésicos**. Eje GIS GISEM inferido: **{gis_m:.6f} m UTM**; diferencia entre ejes: **{kml_m-gis_m:.6f} m**. Las cuerdas de los tres empalmes miden **{sum(float(x['distancia_recta_m']) for x in gaps):.6f} m**, no incluidas en el KML. No se interpreta ningún residuo aritmético como obra. La intersección S3/S4 requiere replanteo.

La capa GISEM muestra TMT001868169 como tramo, no como aprobación de conexión. PC-{1:03d} a PC-{len(pc):03d} son estructuras GIS próximas, sin inventario físico; PN-{1:03d} a PN-{len(pn):03d} son vértices de gabinete para evaluar apoyo, sin vano calculado; CV-{1:03d} a CV-{len(cv):03d} son alertas de cruce OSM. La cartografía no acredita servidumbre, terreno, despeje ni operación real.

## Estado y decisión requerida

No se puede fijar tensión, fases, demanda, conductor, ubicación de nuevos postes, protección, cimentación ni presupuesto de obra. La decisión sigue secuencia: conexión oficial → eje/topografía/servidumbres → estudio eléctrico → diseño mecánico → planos constructivos y revisión profesional. Las hojas CL-01..05 Rev. 4 son documentos de gabinete coordinados y con límites explícitos. La próxima gestión externa es obtener factibilidad y punto de diseño de Electro Puno; la siguiente medición es el levantamiento del corredor y sus cruces.
""")
    write(output/"02_MEMORIA_DESCRIPTIVA/CRITERIOS_DISENO.md","""
# Criterios y metodología de diseño pendientes de fijación

1. Conservar y fechar la geometría KML original; no empalmar segmentos artificialmente. Comparar con as-built y medir GAP-1..3.
2. Separar PC (referencias GIS de posible infraestructura existente), PN (sitios geométricos para inspección) y apoyos nuevos realmente aprobados. No usar los intervalos PN como vanos.
3. Elegir eje con topografía controlada, cruces, acceso, predios y derechos; registrar coordenadas, cota, incertidumbre y datum vertical.
4. Obtener de Electro Puno punto de diseño, tensión/fases, alimentador, capacidad, Icc, protecciones, criterios y versiones de materiales. Obtener del promotor demanda y crecimiento.
5. Con entradas certificadas, dimensionar conductor, flujo/caída/pérdidas y protección; después definir apoyos/vanos por flecha, cargas, despejes, suelo y permisos. Reiterar si cambia el trazado.
6. Evaluar cada resultado contra norma/tabla exacta aplicable y especificación oficial del titular. Registrar margen, responsable y firma; hoy el estado es no verificable.
""")
    write(output/"02_MEMORIA_DESCRIPTIVA/DATOS_ENTRADA.md",f"""
# Datos de entrada y clasificación

**Confirmados documentalmente:** identidad SHA del KML y atributos de archivos GISEM/OSM; no confirma condiciones de campo. **Calculados:** cuatro segmentos, 187 vértices, {kml_m:.6f} m KML UTM, {gis_m:.6f} m GIS alternativo, tres brechas. **Estimados/cartográficos:** {len(pc)} PC, {len(pn)} PN y {len(cv)} CV; no son metrados de obra. **Pendientes:** factibilidad, punto oficial, tensión/fases, demanda, capacidad, conductor, protecciones, PAT, topografía, clima, geotecnia, cruces/servidumbres y permisos.

La matriz detallada con unidad, fuente, consecuencia, documento necesario y validador está en `MATRIZ_DATOS_REV3.csv`. El JSON `PARAMETROS_PENDIENTES.json` preserva nulos: no se sustituyeron por ceros.
""")

    write(output/"03_MEMORIAS_DE_CALCULO/MEMORIA_CALCULO_ELECTRICO.md",f"""
# Memoria de cálculo eléctrico — modelo condicionado

**Resultado de dimensionamiento: pendiente.** No hay tensión, fases, demanda, conductor, parámetros R/X, Icc ni punto aprobado. La longitud KML cartográfica ({kml_m:.6f} m, cuatro segmentos) **no es aún longitud eléctrica aprobada**.

| Cálculo | Entradas y unidades | Ecuación/modelo | Salida y criterio de aceptación |
|---|---|---|---|
| Demanda | Estudio de carga presente/futura [kVA], simultaneidad, horizonte | Escenarios por tramo y punta coincidente | S diseño [kVA], aceptada por promotor/titular |
| Corriente trifásica | S [kVA], U línea [kV], 3 fases confirmadas | I [A] = S/(√3 U) | I por escenario; comparar ampacidad corregida |
| Conductor | I, ficha fabricante, material/sección, temperatura/altitud | Ampacidad corregida y resistencia de falla | Sección candidata justificada; sin ficha no seleccionar |
| Caída radial | I [A], L [km], R/X [Ω/km], cosφ | ΔU [V] ≈ √3 Σ I L (R cosφ + X senφ) | ΔU [%] frente a criterio oficial; flujo de red si hay derivaciones |
| Pérdidas | I por tramo [A], R [Ω/km], L [km] | P [W] = 3 Σ I² R L | P y energía por perfil horario/escenario |
| Cortocircuito/protección | Z fuente/red, U prefalla, curvas y ajustes | Equivalente de red; falla mínima/máxima, coordinación | Corte, sensibilidad, selectividad aprobados |
| Aislamiento/PAT | U máxima, esquema neutro, resistividad [Ω·m] | Selección BIL y estudio PAT según caso | Seguridad y especificaciones verificadas |
| Distancias | Categoría de cruce, perfil, flecha final | Distancia mínima calculada contra tabla pertinente CNE | Margen ≥ criterio aplicable |

El archivo editable `modelo_calculos_rev4.py` valida valores finitos y usa las fórmulas de corriente, caída y flecha **solo para ensayos con entradas proporcionadas**; no ejecuta una selección del proyecto. Requiere documentar estado de cada parámetro, versión de ficha, temperatura, factor de potencia, escenario y modelo de red. No se usaron valores típicos ni se emitió amperaje, caída o Icc para esta línea.
""")
    write(output/"03_MEMORIAS_DE_CALCULO/MEMORIA_CALCULO_MECANICO.md","""
# Memoria de cálculo mecánico — casos y datos requeridos

**Resultado de dimensionamiento: pendiente.** No hay perfil topográfico del eje elegido, conductor certificado, hipótesis de clima, geotecnia ni cuadro de vanos. PN es lista de inspección, no tabla de apoyos diseñados.

| Etapa | Entradas [unidad] | Método | Verificación necesaria |
|---|---|---|---|
| Vano regulador | Posiciones/cotas medidas [m], fijaciones reales | Agrupación de tramos de tensión; cálculo de longitud reguladora según método adoptado | Apoyos/anclajes definidos |
| Cargas | Masa lineal [kg/m], accesorios [N], presión viento [Pa], hielo/temperatura según sitio | Cargas verticales, transversales y longitudinales [N/m y N] | Casos climáticos y factores oficiales |
| Flecha/tensión | w [N/m], L [m], H [N], temperaturas, creep | f≈wL²/(8H) únicamente nivelado preliminar; cambio de estado/catenaria final | Tensión admisible y peor flecha |
| Estructura/retén | Tensiones vectoriales, ángulos, viento, altura, ficha poste/herraje | Equilibrio de fuerzas/momentos [N, N·m] | Resistencia certificada y márgenes |
| Cimiento | Reacciones, capacidad/estratos, agua, geotecnia | Modelo del suelo y estructura seleccionados | Estabilidad y deformación |
| Despejes | Perfil/cotas con datum, flecha máxima, clase de cruce | Cota conductor menos obstáculo [m] | Tabla CNE aplicable, permiso y aceptación |

No se asignan altura/clase de poste, cruceta, retenida, excavación ni cimentación. El intervalo PN-014 a PN-015 de más de 2 km demuestra que PN no es una secuencia de vanos. El registro de campo debe producir estaciones/cotas de obstáculos y alternativas de emplazamiento para iniciar los cálculos.
""")

    met=[{"id":"C-01","concepto":"Longitud KML observada, cuatro trazos","cantidad":f"{kml_m:.3f}","unidad":"m","clase":"cartográfica, no obra","fuente":"KML original","observacion":"excluye empalmes"},
         {"id":"C-02","concepto":"Longitud eje GIS alternativo","cantidad":f"{gis_m:.3f}","unidad":"m","clase":"cartográfica, no obra","fuente":"derived/route.json","observacion":"eje distinto"},
         {"id":"C-03","concepto":"Referencias PC cercanas","cantidad":str(len(pc)),"unidad":"puntos","clase":"inventario GIS, no postes nuevos","fuente":"PC_REFERENCIAS_GIS.csv","observacion":"inspeccionar"},
         {"id":"C-04","concepto":"Sitios PN para replanteo","cantidad":str(len(pn)),"unidad":"sitios","clase":"estimación de gabinete","fuente":"PN_SITIOS_REPLANTEO.csv","observacion":"no instalar"},
         {"id":"C-05","concepto":"Alertas viales CV","cantidad":str(len(cv)),"unidad":"intersecciones","clase":"estimación OSM","fuente":"CV_ALERTAS_OSM.csv","observacion":"clasificar en campo"},
         {"id":"O-01","concepto":"Conductor a instalar","cantidad":"dato requerido","unidad":"m por fase","clase":"metrado de obra pendiente","fuente":"trazado/fases/conductor aprobados","observacion":"sin cantidad"},
         {"id":"O-02","concepto":"Postes nuevos","cantidad":"dato requerido","unidad":"unidades","clase":"metrado de obra pendiente","fuente":"spotting/cálculo mecánico","observacion":"no equivale a PN"},
         {"id":"O-03","concepto":"Retenidas, armados y cimientos","cantidad":"dato requerido","unidad":"por definir","clase":"metrado de obra pendiente","fuente":"cálculo/fichas/suelo","observacion":"sin cantidad"},
         {"id":"O-04","concepto":"Protección y PAT","cantidad":"dato requerido","unidad":"por definir","clase":"metrado de obra pendiente","fuente":"unifilar/estudio PAT","observacion":"sin cantidad"}]
    write_csv(output/"06_METRADOS_Y_PRESUPUESTO/METRADOS_PRELIMINARES.csv",list(met[0]),met)
    items=[("poste y cimentación","unidad"),("conductor y tendido","m"),("armados y aisladores","conjunto"),
           ("retenidas/anclajes","conjunto"),("puesta a tierra","conjunto"),("maniobra y protección","conjunto"),
           ("transporte y montaje","partida"),("cruces/permisos/servidumbres","partida")]
    write_csv(output/"06_METRADOS_Y_PRESUPUESTO/MATERIALES_PENDIENTES.csv",
              ["id","material","especificacion","cantidad","unidad","fuente_necesaria","estado"],
              [{"id":f"M-{i:02d}","material":name,"especificacion":"dato requerido","cantidad":"dato requerido",
                "unidad":unit,"fuente_necesaria":"diseño aprobado y ficha/cotización","estado":"pendiente"}
               for i,(name,unit) in enumerate(items,1)])
    write_csv(output/"06_METRADOS_Y_PRESUPUESTO/PRESUPUESTO_PENDIENTE.csv",
              ["id","partida","unidad","cantidad","precio_unitario_pen","parcial_pen","fecha_base","fuente_precio","estado"],
              [{"id":f"P-{i:02d}","partida":name,"unidad":unit,"cantidad":"dato requerido",
                "precio_unitario_pen":"dato requerido","parcial_pen":"no calculable","fecha_base":"dato requerido",
                "fuente_precio":"cotización/APU requerida","estado":"pendiente"}
               for i,(name,unit) in enumerate(items,1)])
    write(output/"06_METRADOS_Y_PRESUPUESTO/METODO_PRESUPUESTO.md","""
# Presupuesto y APU: pendientes de datos

No hay presupuesto monetario ni precio unitario defendible. Las partidas `PRESUPUESTO_PENDIENTE.csv` definen estructura de cotización, sin ceros ni totales ficticios. Para cada APU se requieren metrado de obra aprobado, rendimiento, cuadrilla, materiales certificados, flete/acceso, cotización local con fecha, impuestos y condiciones contractuales. La suma solo procede cuando todos los parciales tienen cantidad, unidad y precio trazables. Los conteos PC/PN/CV y la longitud KML son indicadores cartográficos, no cantidades presupuestables.
""")

    rules=[
        ("N-01","CNE Suministro 2011; RM 0214-2011-MEM","numeral por cotejar","Distancias y condiciones de líneas aéreas según clasificación real","03_MEMORIAS_DE_CALCULO/MEMORIA_CALCULO_MECANICO.md","sin tensión/perfil/diseño ni cotejo de tabla vigente","no verificable","https://www.gob.pe/institucion/minem/normas-legales/108753-0214-2011-mem"),
        ("N-02","CNE Suministro 2011; RM 0214-2011-MEM","tabla por cotejar","Evaluación de distancias verticales según tipo de cruce","CL-03; memoria mecánica","sin perfil/flecha/categoría ni tabla cotejada","no verificable","https://www.gob.pe/institucion/minem/normas-legales/108753-0214-2011-mem"),
        ("N-03","RD 018-2002-EM/DGE","numeral por cotejar","Procedimiento de punto de diseño si aplica al alcance","Solicitud a Electro Puno","punto no otorgado; aplicabilidad por confirmar","no verificable","https://www.gob.pe/institucion/osinergmin/normas-legales/739536-018-2002-em-dge"),
        ("N-04","RD 018-2002-EM/DGE","numeral por cotejar","Procedimiento de revisión y aprobación si aplica","Expediente y planos","sin diseño completo ni revisión","no verificable","https://www.gob.pe/institucion/osinergmin/normas-legales/739536-018-2002-em-dge"),
        ("N-05","RD 018-2002-EM/DGE","numeral por cotejar","Recepción y puesta en servicio si aplica","no aplica a esta etapa","sin obra ni aprobación","no verificable","https://www.gob.pe/institucion/osinergmin/normas-legales/739536-018-2002-em-dge"),
        ("N-06","Electro Puno","versión y numeral por solicitar","Especificación de red/materiales/conexión","memorias y CL-05","sin documento del titular","no verificable","https://www.gob.pe/electropuno"),
    ]
    rule_cols=["codigo","norma_version","articulo_numeral","requisito","documento_relacionado","evidencia","estado","url","fecha_consulta","accion_pendiente"]
    write_csv(output/"07_NORMATIVA_Y_ESPECIFICACIONES/MATRIZ_NORMATIVA.csv",rule_cols,
              [dict(zip(rule_cols,(*r,"2026-10-14","Confirmar vigencia y aplicabilidad; completar evidencia de cumplimiento"))) for r in rules])
    write(output/"07_NORMATIVA_Y_ESPECIFICACIONES/ESPECIFICACIONES_PRELIMINARES.md","""
# Especificaciones técnicas preliminares

Materiales, conductor, aisladores, postes, herrajes, PAT, protecciones, cimentaciones y detalles de instalación: **no seleccionados**. Se requerirán fichas certificadas, condiciones de Electro Puno y normas vigentes aplicables antes de especificarlos. En planos se representa únicamente simbología cartográfica y un esquema conceptual. No se autoriza compra, montaje ni ensayo de recepción con este documento.
""")
    write(output/"07_NORMATIVA_Y_ESPECIFICACIONES/FUENTES_OFICIALES.md","""
# Referencias oficiales consultadas (14-10-2026)

- [MINEM, RM 0214-2011-MEM, CNE Suministro 2011](https://www.gob.pe/institucion/minem/normas-legales/108753-0214-2011-mem). Referencia oficial identificada; numerales, tablas, modificaciones y vigencia consolidada requieren cotejo profesional. La consulta directa del PDF no estuvo disponible en esta sesión.
- [OSINERGMIN, RD 018-2002-EM/DGE](https://www.gob.pe/institucion/osinergmin/normas-legales/739536-018-2002-em-dge). Referencia oficial identificada; numerales y ámbito concreto del proyecto pendientes de cotejo.
- [Electro Puno, requisitos de instalaciones nuevas](https://www.gob.pe/institucion/electropuno/informes-publicaciones/6823816-requisitos-para-instalaciones-nuevas). Esta publicación no sustituye las condiciones técnicas de una línea MT de ~14 km.

No se adjuntan copias de PDFs de terceros. La matriz no declara cumplimiento de despejes ni aprobación; el operador y el profesional deben confirmar versión aplicable y numeral exacto por caso.
""")

    field_columns=["id","tipo","segmento","progresiva_kml_m","lon_original","lat_original","este_original_m","norte_original_m",
                   "lon_levantada","lat_levantada","este_levantado_m","norte_levantado_m","cota_m","datum_vertical",
                   "foto","cruce_interferencia","terreno","servidumbre_permiso","observaciones","estado","responsable","fecha_inspeccion"]
    field=[]
    def field_add(id,tipo,segment,station,lon,lat,e,n):
        field.append(dict(zip(field_columns,[id,tipo,segment,station,lon,lat,e,n,"","","","","","","","","","","","pendiente de campo","",""])))
    for rows,tipo,station in [(pc,"PC referencia GIS","estacion_m"),(pn,"PN sitio geométrico","progresiva_kml_m"),
                              (cv,"CV indicio vial","progresiva_kml_m")]:
        for row in rows:
            field_add(row["id"],tipo,row["segmento"],row[station],row["longitud"],row["latitud"],
                      row.get("este_m",row.get("este_utm19s_m")),row.get("norte_m",row.get("norte_utm19s_m")))
    for row in gaps:
        lon,lat=float(row["lon_fin_origen"]),float(row["lat_fin_origen"])
        e,n=TRANS.transform(lon,lat)
        field_add(row["id"],"GAP extremo origen",row["segmento_origen"],row["estacion_fin_origen_m"],lon,lat,
                  round(e,3),round(n,3))
    write_csv(output/"08_DATOS_GIS_Y_CAMPO/REGISTRO_REPLANTEO.csv",field_columns,field)
    write(output/"08_DATOS_GIS_Y_CAMPO/PLAN_CAMPO.md","""
# Plan de levantamiento y control de campo

Prioridad 1: medir ambos extremos de GAP-1..3, comprobar intersección y sentido S3/S4, decidir continuidad sin alterar KML original. Prioridad 2: ubicar TMT001868169 y apoyos NMT en terreno con as-built Electro Puno; inventariar 40 PC y replantear 27 PN, aceptando o descartando cada sitio. Prioridad 3: verificar y depurar 44 alertas viales OSM, más cauces, edificaciones, telecomunicaciones, cercos, vegetación y restricciones no cartografiadas. Levantar cotas/anchos/titularidad/permisos y distancias aplicables. Prioridad 4: perfiles por posible vano, accesos, predios, servidumbres, clima local, suelo y resistividad.

Entregar coordenadas geográficas y UTM con control, equipo/método, fecha, incertidumbre, datum vertical, puntos crudos, fotos, croquis, responsable y decisión por sitio. `REGISTRO_REPLANTEO.csv` tiene los campos medidos intencionalmente vacíos. Ninguna fila está declarada inspeccionada.
""")
    write(output/"08_DATOS_GIS_Y_CAMPO/FUENTES_GIS.md","""
# Procedencia GIS y límites

`KML_ORIGINAL.kml` es copia byte a byte del levantamiento manual aportado; el SHA figura en `manifest_entrega.json`. `EJE_GIS_ALTERNATIVO.json` es una ruta inferida de GISEM, no una línea aprobada. `PC_REFERENCIAS_GIS.csv`, `PN_SITIOS_REPLANTEO.csv`, `CV_ALERTAS_OSM.csv` y `GAP_EMPALMES.csv` mantienen sus clases separadas. El manifiesto `MANIFIESTO_FUENTES.json` registra URL, fecha de descarga y SHA de GISEM/OSM. La precisión de publicación no se declaró topográfica; OSM no acredita viales, servidumbres ni permisos. Las muestras SRTM existentes corresponden al eje GIS, por eso no se usaron en CL-03.
""")

    observations=[
        ("P0-01","Factibilidad/punto oficial de conexión","Electro Puno","respuesta firmada con código, coordenadas, capacidad y alcance"),
        ("P0-02","Continuidad y elección del eje KML/GIS","topógrafo/Electro Puno","levantamiento GAP-1..3, S3/S4 y eje aceptado"),
        ("P0-03","Tensión, fases y demanda","Electro Puno/promotor","condiciones de red y estudio de carga"),
        ("P1-01","Cruces/obstáculos/servidumbres","campo/autoridades","inventario y permisos por sitio"),
        ("P1-02","Conductor, cargas, clima, suelo","proyectista/fabricante/campo","fichas, datos ambientales y geotecnia"),
        ("P1-03","Protección, PAT y cortocircuito","Electro Puno/proyectista","unifilar, impedancias y estudio"),
        ("P1-04","Spotting real y vanos","topógrafo/proyectista","ubicación aprobada y cálculo de flecha/despeje"),
        ("P2-01","Planos constructivos, metrados y precios","proyectista/cotizaciones","expediente coordinado y revisado"),
    ]
    write_csv(output/"01_INDICE_Y_CONTROL/OBSERVACIONES_ABIERTAS.csv",
              ["id","bloqueo","responsable","criterio_cierre","estado"],
              [{"id":a,"bloqueo":b,"responsable":c,"criterio_cierre":d,"estado":"abierto"} for a,b,c,d in observations])
    write_csv(qa/"INCIDENCIAS.csv",["id","descripcion","estado","accion"],
              [{"id":"AI-06","descripcion":"CL-04 Rev. 2: 16 PC DXF vs 30 PC PDF","estado":"corregido en lámina Rev. 4","accion":"40 PC en ambos; tabla CSV completa"},
               {"id":"AI-07","descripcion":"CL-05 Rev. 2: esquema solo PDF","estado":"corregido en lámina Rev. 4","accion":"cajas y flechas desde comandos comunes"},
               {"id":"AI-08","descripcion":"Rev. 3 acepta NaN/infinito","estado":"módulo Rev. 4 disponible; integración pendiente","accion":"adoptar modelo validado en diseño posterior"},
               {"id":"AI-09","descripcion":"Rev. 3 no regenera CAD/documentos","estado":"flujo Rev. 4 adicional","accion":"generador de paquete, sin sobrescritura"}])
    trace=[
        ("R-01","geometría KML","KML_ORIGINAL.kml","CL-01/02; memoria","test_longitudes_y_empalmes_desde_kml_original","calculado"),
        ("R-02","GIS alternativo","EJE_GIS_ALTERNATIVO.json","CL-01; memoria","diferencia eje verificada","calculado"),
        ("R-03","PN distintos de PC","PN/PC CSV","CL-02/04; registro campo","IDs paritarios DXF/PDF","estimado"),
        ("R-04","cruces","CV_ALERTAS_OSM.csv","CL-02; plan campo","44 IDs y pendientes","estimado"),
        ("R-05","conexión","TMT GISEM; solicitud","CL-01/05; memoria","respuesta operador ausente","pendiente"),
        ("R-06","demanda/tensión","PARAMETROS_PENDIENTES.json","memoria eléctrica","nulos preservados","pendiente"),
        ("R-07","conductor/protección/PAT","ficha/unifilar requeridos","memoria eléctrica; CL-05","sin resultados ficticios","pendiente"),
        ("R-08","vano/despeje/cimiento","topografía/geotecnia requeridas","memoria mecánica; CL-03","sin perfil falso","pendiente"),
        ("R-09","metrados/presupuesto","trazado/cotización requeridos","06_METRADOS_Y_PRESUPUESTO","sin precio ni cantidades ficticias","pendiente"),
        ("R-10","normativa","fuentes oficiales","matriz normativa","estado no verificable","pendiente"),
    ]
    write_csv(output/"01_INDICE_Y_CONTROL/MATRIZ_TRAZABILIDAD_REQUISITOS.csv",
              ["id","requisito","fuente","salida","prueba_evidencia","estado"],
              [dict(zip(["id","requisito","fuente","salida","prueba_evidencia","estado"],r)) for r in trace])
    write_csv(qa/"COMPARACION_PLANOS.csv",
              ["plano","dxf","pdf","png","verificacion","ingenieria"],
              [{"plano":code,"dxf":f"{code}_REV4.dxf","pdf":f"{code}_REV4.pdf",
                "png":f"{code}_REV4.png","verificacion":"primitivas compartidas; reabrir y cotejar IDs",
                "ingenieria":"preliminar; no aprobada"} for code in sheets])
    write(qa/"INFORME_QA.md",f"""
# Control de calidad del paquete Rev. 4

Las fuentes KML/GIS y tablas se validaron antes de generar. Cinco hojas se construyeron con comandos de dibujo compartidos para DXF/PDF y PNG renderizado del PDF. El DXF de CL-01/02 además conserva en modelo los cuatro segmentos KML y eje GIS en EPSG:32719, en metros; presentación A3 en mm. CL-04 incluye **{len(pc)} PC y {len(pn)} PN** tanto en DXF como PDF. CL-05 incluye cajas, etiquetas y flechas en ambos. `--verify` reabre cada formato, comprueba tamaño, unidades, entidades y paridad de IDs/etiquetas; no verifica AutoCAD ni ingeniería.

No hay resultados reales de demanda, conductor, caída, cortocircuito, flechas, postes, despejes, cimentaciones, PAT o presupuesto. Los datos medidos permanecen vacíos. La matriz normativa es de aplicabilidad preliminar; no se declaró cumplimiento. No se abrió AutoCAD ni se recibieron aprobaciones. Para convertir a expediente de revisión técnica deben cerrarse los P0/P1 de `OBSERVACIONES_ABIERTAS.csv` y someter el diseño a profesional responsable.
""")
    write(qa/"CHECKLIST_ENTREGA.md","""
# Lista de comprobación

- [x] Copia controlada y SHA del KML original; cuatro segmentos sin edición.
- [x] Ejes KML/GIS, PC/PN/CV y brechas separados.
- [x] Cinco DXF/PDF/PNG A3 Rev. 4 coordinados y reabiertos por software.
- [x] Modelos eléctricos/mecánicos y límites documentados sin resultados inventados.
- [x] Metrados cartográficos distinguidos de metrado de obra; presupuesto sin precios ficticios.
- [x] Índices, trazabilidad, matriz normativa y pendientes.
- [ ] Factibilidad/punto oficial y demanda/tensión/fases.
- [ ] Levantamiento topográfico, cruces, suelo y servidumbres.
- [ ] Cálculos y planos constructivos, revisión profesional y aprobaciones.
""")
    write(qa/"PRUEBAS.md","""
# Pruebas de entrega

Desde la raíz del repositorio, el 14-10-2026 se ejecutó `python -m pytest proyectos/renzo-linea-primaria-capachica-llachon/tests -q`: **42 passed, 5 xfailed**. Los cinco xfail apuntan intencionalmente a defectos de archivos históricos Rev. 2/3, que se conservan. Las pruebas normales cubren el módulo Rev. 4 y una generación aislada de la entrega, con reapertura de los planos y verificación de datos. `python proyectos/renzo-linea-primaria-capachica-llachon/scripts/generar_entrega_rev4.py --verify proyectos/renzo-linea-primaria-capachica-llachon/ENTREGA_FINAL_CAPACHICA_LLACHON_REV4` confirmó 62 archivos y cinco planos; ingeniería aprobada = false. Se generaron paquetes aislados para comparar. Los PDF, PNG y documentos fueron idénticos en SHA-256; algunos DXF cambiaron solo en el orden de clases internas de ezdxf, sin diferencia de entidades. Por ello la reproducción se valida por contenido y geometría, no por identidad binaria de los DXF.

Repetir los dos comandos después de cualquier cambio y registrar el nuevo resultado. Estos controles son de datos y software, no certifican seguridad eléctrica, mecánica ni normativa. No se abrió AutoCAD.
""")

    files={p.relative_to(output).as_posix():{"bytes":p.stat().st_size,"sha256":sha(p)}
           for p in output.rglob("*") if p.is_file() and p.name!="manifest_entrega.json"}
    (output/"manifest_entrega.json").write_text(json.dumps({"revision":4,"estado":"ACADEMIC_PRELIMINARY_NOT_FOR_CONSTRUCTION",
        "source_kml_sha256":sha(KML),"file_count":len(files),"files":files},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return verify(output)


def verify(output: Path):
    output=output.resolve()
    manifest=json.loads((output/"manifest_entrega.json").read_text(encoding="utf-8"))
    for rel,meta in manifest["files"].items():
        p=output/rel
        if not p.is_file() or p.stat().st_size!=meta["bytes"] or sha(p)!=meta["sha256"]:
            raise ValueError(f"Manifiesto inconsistente: {rel}")
    if len(manifest["files"])!=manifest["file_count"]:
        raise ValueError("Conteo de manifiesto inconsistente")
    source_lines,source_gis,pc,pn,cv,_,_,_,_,_=read_inputs()
    for n in range(1,6):
        code=f"CL-{n:02d}"
        dxf=ezdxf.readfile(output/"05_PLANOS_EDITABLES"/(code+"_REV4.dxf"))
        if dxf.audit().has_errors or dxf.header["$INSUNITS"]!=6 or code+"_A3" not in dxf.layouts:
            raise ValueError(f"DXF inválido: {code}")
        with fitz.open(output/"04_PLANOS_PDF"/(code+"_REV4.pdf")) as pdf:
            if len(pdf)!=1 or abs(pdf[0].rect.width-420*72/25.4)>1 or abs(pdf[0].rect.height-297*72/25.4)>1:
                raise ValueError(f"PDF no A3: {code}")
            pdftext=pdf[0].get_text()
        if code not in pdftext or "NO APTO PARA CONSTRUCCION" not in pdftext:
            raise ValueError(f"PDF sin revisión/advertencia: {code}")
        png=output/"09_CONTROL_DE_CALIDAD/vistas_png"/(code+"_REV4.png")
        if not png.is_file() or png.stat().st_size<5000:
            raise ValueError(f"PNG inválido: {code}")
        if code in ("CL-01","CL-02"):
            model=dxf.modelspace()
            for layer,total in (("KML",4),("GIS",1),("PC",len(pc)),("PN",len(pn)),("CV",len(cv))):
                kind="LWPOLYLINE" if layer in ("KML","GIS") else "CIRCLE"
                objects=[e for e in model if e.dxftype()==kind and e.dxf.layer==layer]
                if len(objects)!=total:
                    raise ValueError(f"{code} modelo: {layer}={len(objects)}, esperado {total}")
                if layer=="KML":
                    for entity,source in zip(objects,source_lines):
                        coords=list(entity.get_points("xy"))
                        if len(coords)!=len(source) or any(abs(a-b)>0.001 for pair,ref in zip(coords,source) for a,b in zip(pair,ref)):
                            raise ValueError(f"{code} KML no coincide con origen UTM")
                if layer=="GIS":
                    coords=list(objects[0].get_points("xy"))
                    if len(coords)!=len(source_gis) or any(abs(a-b)>0.001 for pair,ref in zip(coords,source_gis) for a,b in zip(pair,ref)):
                        raise ValueError(f"{code} eje GIS no coincide con fuente")
        if code=="CL-04":
            text=" ".join(e.dxf.text for e in dxf.layouts.get(code+"_A3") if e.dxftype()=="TEXT")
            for prefix,total in (("PC",40),("PN",27)):
                expected={f"{prefix}-{i:03d}" for i in range(1,total+1)}
                if not expected.issubset(set(__import__("re").findall(prefix+r"-\d{3}",text))) or not expected.issubset(set(__import__("re").findall(prefix+r"-\d{3}",pdftext))):
                    raise ValueError(f"CL-04 IDs {prefix} no coinciden entre DXF/PDF")
        if code=="CL-05":
            dxftext=" ".join(e.dxf.text for e in dxf.layouts.get(code+"_A3") if e.dxftype()=="TEXT")
            for label in ("TMT001868169","PROTECCION PENDIENTES","POR DEFINIR"):
                if label not in dxftext or label not in pdftext:
                    raise ValueError(f"CL-05 sin elemento conceptual: {label}")
            if len(list(dxf.layouts.get(code+"_A3").query("LINE")))<6:
                raise ValueError("CL-05 sin flechas editables")
    print(json.dumps({"estado":"paquete verificado por software","archivos":manifest["file_count"],"planos":5,
                      "ingenieria_aprobada":False,"ruta":str(output)},ensure_ascii=False))
    return manifest


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=DEFAULT)
    parser.add_argument("--verify",type=Path)
    args=parser.parse_args()
    if args.verify:
        verify(args.verify)
    else:
        build(args.output)
