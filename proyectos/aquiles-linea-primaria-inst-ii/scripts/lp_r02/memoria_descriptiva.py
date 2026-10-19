"""Memoria independiente y capítulo común, con ubicación de fuente oficial."""
from pathlib import Path
import shutil
from pypdf import PdfReader, PdfWriter


def ampliar(original,r,c,tabla,tex,n):
    s=original+r'''
\section{Antecedentes, finalidad y objetivos}
El proyecto corresponde al curso de Instalaciones Eléctricas II. La finalidad del
escenario es evaluar el transporte de energía entre la transformación de salida de
Limbani y la llegada prevista en Huancasayani. El trazado y las obras se estudian
como una línea principal, sin derivaciones de distribución en el recorrido.
La necesidad real y el número de suministros deben contrastarse con el padrón y
la disponibilidad firme de la fuente; el censo permite construir el escenario académico.

Los objetivos son delimitar el corredor, comparar niveles de tensión, comprobar el
comportamiento eléctrico y mecánico del modelo y desarrollar los materiales por
armado y poste. El proyecto ordena memoria, cálculos, metrados, planos y presupuesto
para que sus cantidades puedan comprobarse desde una misma base.

\section{Ubicación política y geográfica}
'''
    from pyproj import Transformer
    tr=Transformer.from_crs(32719,4326,always_xy=True)
    a,b=r['postes'][0],r['postes'][-1];la,lb=tr.transform(a['e'],a['n']),tr.transform(b['e'],b['n'])
    s+=tabla(['Nivel','Ubicación / referencia'],[
        ['País','Perú'],['Departamento','Puno'],['Provincia','Sandia'],['Distrito','Limbani'],
        ['Ubigeo distrital','211203, atributo del servicio oficial IGN'],['Ámbito del proyecto','Corredor de gabinete Limbani--Huancasayani'],
        ['Sistema local','WGS 84 / UTM zona 19 Sur, EPSG:32719'],['Punto inicial P001 / T1',f"E {n(a['e'])} m; N {n(a['n'])} m"],
        ['Punto final P111 / T2',f"E {n(b['e'])} m; N {n(b['n'])} m"],
        ['Latitud / longitud inicial',tex(f'{la[1]:.6f}° / {la[0]:.6f}°')],
        ['Latitud / longitud final',tex(f'{lb[1]:.6f}° / {lb[0]:.6f}°')],
        ['Longitud horizontal del eje',n(r['longitud_horizontal_m'])+' m'],['Apoyos / vanos','111 / 110']], [1.3,3.2])
    s+=r'''
Los límites administrativos se obtuvieron del servicio oficial del Instituto
Geográfico Nacional (IGN), capas departamental, provincial y distrital. Se conservan
los archivos descargados, su consulta y sus huellas SHA256. Son límites referenciales;
su fuente oficial no convierte al plano elaborado para el curso en una demarcación
legal ni valida los emplazamientos de equipos. La comprobación espacial sitúa los
dos extremos del eje dentro del polígono referencial de Limbani.

\begin{figure}[H]\centering
\includegraphics[width=\linewidth]{figuras/ubicacion.pdf}
\caption{Ubicación Perú--Puno--Sandia--Limbani y corredor del proyecto. La lámina UB-01 se entrega también en A3 para lectura de detalle.}
\end{figure}

\section{Acceso, relieve y condiciones del emplazamiento}
El acceso a los frentes y el transporte de postes se consideran condiciones de
planificación. La cartografía aporta contexto del corredor, pero no se dispone de
un reconocimiento vial que certifique ruta de ingreso, ancho, pendientes,
capacidad de puentes o recorrido de maquinaria. No se asignan distancias ni
tiempos de viaje como datos medidos. Antes del montaje se define la logística con
inspección del acceso y autorización de los predios correspondientes.

El relieve se representa con el perfil DEM del modelo y no con cotas levantadas.
Los cruces con cauces, viviendas y otras interferencias son cartográficos. Las
excavaciones, cimentaciones y anclajes requieren caracterización de suelo y
replanteo; la memoria no atribuye una capacidad portante ensayada ni una resistividad
de terreno medida. La servidumbre y las posiciones definitivas de apoyo dependen
de esa verificación.

\section{Condiciones ambientales usadas en el cálculo}
Los valores siguientes son estados de diseño y sensibilidades del modelo, no una
serie climática observada en Limbani. El viento y el hielo se contrastan con el
CNE y con la clasificación aplicable al emplazamiento. La temperatura de conductor
de 75 grados Celsius corresponde al estado térmico adoptado, no a temperatura ambiente.
'''
    s+=tabla(['Estado','Temp. °C','Viento m/s','Hielo mm','Procedencia / estado'],[
        [tex(x['id']),n(x['temperatura_c'],1),n(x['viento_ms'],1),n(x['hielo_mm'],1),tex(x['fuente'])] for x in c['clima']],
        [1.3,.7,.8,.8,3.2],'footnotesize')
    s+=r'''
\section{Descripción de las instalaciones previstas}
La transformación de salida T1 eleva la tensión para el transporte y T2 reduce
la tensión en llegada. En el modelo ambas unidades son de 250 kVA netos disponibles
en el emplazamiento; sus placas y relaciones reales se mantienen por confirmar.
Se compara el transporte a 10, 20, 22 y 22.9 kV con la misma demanda y conductor.
No se declara confirmada una tensión real de generación o de subestación.

La línea aérea comprende una terna AAAC de 50 mm$^2$, apoyos de concreto armado
centrifugado (CAC), armados de suspensión, ángulo, retención y terminal,
aislamiento, herrajes, retenidas y puesta a tierra. Las alturas de apoyo son de
13, 15 y 17 m. La capacidad transversal tipo de 600 daN no equivale a una capacidad
vertical de 600 kg ni sustituye la revisión de flexocompresión y cimentación.
Las retenidas se especifican con rotura mínima de 60 kN, pendiente de certificado.

El detalle M01 desarrolla cada componente del metrado con una receta y una ficha
por poste. Las referencias DGE trifásicas sin neutro se adaptan académicamente a
CAC mediante los criterios declarados; no se toman los tirafondos de madera como
accesorios para concreto. Las masas del conjunto suministrado deben incorporarse
al cálculo mecánico antes de validar su configuración resistente.

\section{Alcance de las obras y organización del expediente}
'''
    s+=tabla(['Conjunto','Alcance del escenario'],[
        ['Transformación','T1 de salida y T2 de llegada; dos unidades de referencia de 250 kVA.'],
        ['Línea principal','111 apoyos y 110 vanos, sin ramificaciones; tres fases AAAC.'],
        ['Apoyos','72 CAC de 13 m, 30 de 15 m y 9 de 17 m.'],
        ['Armados','30 suspensión, 41 ángulo, 38 retención y 2 terminales.'],
        ['Retenidas','160 ramales; longitud geométrica ideal más provisión de montaje.'],
        ['Puesta a tierra','111 sistemas de apoyo en el metrado; dos mallas de subestación en partida independiente.'],
        ['Protección y operación','Esquema conceptual de protección y puesta a tierra; ajustes sujetos a la fuente real.'],
        ['Fuera del alcance','Redes secundarias, acometidas de usuarios y dimensionamiento de la central del otro curso.']], [1.3,3.5])
    s+=r'''
El expediente se organiza en ocho carpetas: expediente integrado, memoria
descriptiva, cálculos, metrados, planos, cartografía, presupuesto y recursos de
consulta. La memoria identifica el proyecto y sus bases; los capítulos de cálculo
desarrollan las ecuaciones; los metrados permiten comprobar piezas por apoyo y los
planos sitúan el corredor. El presupuesto conserva su carácter referencial académico.

\section{Secuencia prevista de ejecución}
La secuencia técnica comprende confirmar equipos y demanda, realizar topografía
y estudios de suelo/tierra, cerrar el diseño de apoyos y armados, obtener las
autorizaciones del corredor y preparar el suministro. La ejecución comprende
replanteo, accesos, excavación y cimentación, izado, montaje de armados y retenidas,
tendido y regulación, conexiones y tierra. Las verificaciones de aislamiento,
continuidad, puesta a tierra y protección preceden a la energización autorizada.
No se asigna un plazo contractual ni una cuadrilla real sin rendimiento y
programación de obra sustentados.

\section{Fuentes de la memoria y plano de ubicación}
La fuente cartográfica administrativa es el IGN, servicio
DATOS\_GEOESPACIALES/LÍMITES, consultado el 19 de octubre de 2026. El eje, las
coordenadas y los estados de cálculo proceden de la base LP-R02. La demanda usa
los registros INEI 2017 citados en el capítulo de demanda. Las láminas DGE de la
RD 024-2003-EM/DGE sirven como referencia documental de armados. El registro de
recursos identifica enlaces y alcance de uso para conservar la trazabilidad.
'''
    return s


def independiente(b):
    """Reutiliza exactamente el capítulo aprobado en la entrega integrada."""
    b=Path(b);src=b/'latex';t=b/'memoria-latex';t.mkdir(exist_ok=True)
    for n in ['plantilla','figuras']:shutil.copytree(src/n,t/n,dirs_exist_ok=True)
    meta=(src/'metadatos.tex').read_text().replace('EXPEDIENTE DEL PROYECTO ACADÉMICO','MEMORIA DESCRIPTIVA DEL PROYECTO')
    (t/'metadatos.tex').write_text(meta,encoding='utf-8')
    (t/'memoria.tex').write_text((src/'capitulos/01-memoria.tex').read_text(),encoding='utf-8')
    (t/'main.tex').write_text(r'''\documentclass[12pt,letterpaper]{report}
\input{metadatos}\input{plantilla/estilo}\decimalpoint
\begin{document}\hypersetup{pageanchor=false}\pagenumbering{gobble}
\input{plantilla/caratula}\clearpage
\hypersetup{pageanchor=true}\pagenumbering{arabic}
\begingroup\footnotesize\tableofcontents\endgroup\clearpage
\input{memoria}\end{document}
''',encoding='utf-8')
    from herramientas.documentos.formato_aquiles import compilar
    compilar(t)
    w=PdfWriter();w.append(PdfReader(t/'main.pdf'));w.append(PdfReader(b/'ubicacion/Plano_Ubicacion.pdf'),outline_item='UB-01 · Plano de ubicación A3')
    w.add_metadata({'/Title':'Memoria descriptiva · Línea primaria Limbani–Huancasayani','/Author':'Aquiles Taylor Ramos Yapo'})
    f=b/'Memoria_Descriptiva.pdf'
    with f.open('wb') as out:w.write(out)
    print('Memoria descriptiva independiente:',len(w.pages),'páginas.',flush=True)
    return f
