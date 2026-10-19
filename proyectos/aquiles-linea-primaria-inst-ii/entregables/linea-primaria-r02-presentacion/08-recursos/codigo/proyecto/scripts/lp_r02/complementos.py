from pathlib import Path
import json,csv,math,shutil,importlib.metadata,sys
from documentar import doc_outputs,num
from analizar import tabla,guardar
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from herramientas.lineas_primarias.revision import resolver_estado,perfil

def completar(P,O,r):
    C=json.loads((P/'datos/lp-r02/parametros.json').read_text());cfg=r['configuracion_mecanica'];c=C['conductor']
    from shapely.geometry import shape,Point,LineString
    from shapely.ops import unary_union
    from shapely import make_valid
    houses=json.loads((P/'datos/lp-r01/casas-originales.geojson').read_text())
    house=unary_union([make_valid(shape(f['geometry'])) for f in houses['features'] if f.get('geometry')])
    waterdata=json.loads((P/'datos/lp-r01/referencias-osm.geojson').read_text())
    water=unary_union([shape(f['geometry']) for f in waterdata['features'] if f['properties'].get('clase') in ['river','stream','canal','ditch','drain']])
    diagnostic=[]
    for g in r['retenidas']:
        p=next(p for p in r['postes'] if p['id']==g['poste']);pt=Point(g['e'],g['n']);seg=LineString([(p['e'],p['n']),(g['e'],g['n'])])
        g.update(distancia_casa_cartografica_m=pt.distance(house),distancia_cauce_cartografica_m=pt.distance(water),cruza_casa_cartografica=seg.intersects(house),cruza_cauce_cartografico=seg.intersects(water))
        g['alerta_cartografica']=bool(g['distancia_casa_cartografica_m']<4 or g['distancia_cauce_cartografica_m']<8 or g['cruza_casa_cartografica'] or g['cruza_cauce_cartografico'])
        if g['alerta_cartografica']:g['estado']='CONFLICTO CARTOGRAFICO: REPLANTEAR ANCLAJE/PREDIO; NO ACEPTAR POSICION IDEAL'
        diagnostic.append(dict(id=g['id'],poste=g['poste'],e=g['e'],n=g['n'],distancia_casa_m=g['distancia_casa_cartografica_m'],distancia_cauce_m=g['distancia_cauce_cartografica_m'],cruza_casa=g['cruza_casa_cartografica'],cruza_cauce=g['cruza_cauce_cartografico'],alerta=g['alerta_cartografica']))
    r['resumen']['retenidas_alerta_cartografica']=sum(g['alerta_cartografica'] for g in r['retenidas'])
    for p in r['postes']:
        p['DC_poste_13m_400dan_tipo']=p['DC_propuesta']*1.5 if p['poste_m']==13 else None
        p['anclajes_con_alerta']=sum(g['alerta_cartografica'] for g in r['retenidas'] if g['poste']==p['id'])
        if p['anclajes_con_alerta']:p['acciones']+='; REPLANTEAR ANCLAJES CON CONFLICTO CARTOGRAFICO'
    tabla(O/'07-evaluacion-y-pendientes/anclajes_conflictos_cartograficos.csv',diagnostic)
    tabla(O/'02-metrados/retenidas.csv',r['retenidas']);tabla(O/'02-metrados/postes.csv',r['postes'])
    guardar(O/'03-calculos/resultados.json',r)
    tens=[];creep=[]
    for v in r['vanos']:
        for T in [-5,0,5,10,15,20,25,30]:
            g=resolver_estado(v['longitud_m'],v['desnivel_m'],cfg['H0_N'],cfg['q0_N_m'],cfg['EA_N'],c['alpha_termica'],15,T,cfg['q0_N_m'])
            xyz=perfil(g);sag=max(xyz[:,0]/v['longitud_m']*v['desnivel_m']-xyz[:,2])
            tens.append(dict(vano=v['id'],temperatura_C=T,H_N=g['H'],T_extremo_max_N=max(g['T0_N'],g['T1_N']),flecha_vertical_m=float(sag),estado='ORIENTATIVO DEL MODELO; NO AUTORIZACION DE TENDIDO'))
        for eps in [230e-6,345e-6]:
            g=resolver_estado(v['longitud_m'],v['desnivel_m'],cfg['H0_N'],cfg['q0_N_m'],cfg['EA_N'],c['alpha_termica'],15,75,cfg['q0_N_m'],0,eps);xyz=perfil(g)
            creep.append(dict(vano=v['id'],creep_microstrain=eps*1e6,H_N=g['H'],flecha_vertical_m=float(max(xyz[:,0]/v['longitud_m']*v['desnivel_m']-xyz[:,2])),estado='SENSIBILIDAD; CURVA DE FABRICANTE PENDIENTE'))
    tabla(O/'03-calculos/tabla_tensado_orientativa.csv',tens);tabla(O/'03-calculos/sensibilidad_fluencia.csv',creep)
    questions=[
      ('¿Qué curso y tema se están evaluando?','Instalaciones Eléctricas II; línea primaria de una terna sin ramales. Grifo y minicentral tienen expedientes independientes.','Definido; rúbrica pendiente','proyecto.yaml / docs/curso'),
      ('¿La línea es primaria o transmisión de alta tensión?','Se trata como línea primaria de media tensión de transporte local. No se adopta una clasificación de alta tensión por el verbo transmitir.','Definido para estudio','Memoria1'),
      ('¿Cuál es el origen de energía?','MCH aislada según manifiestoR01. Confirmar con el usuario/placas antes de cambiar aElectroPuno.','Pendiente físico','Memoria1'),
      ('¿A cuánto sale realmente la subestación?','No hay placa verificada.10kV es hipótesis de compatibilidad.22.9kV es alternativa, no dato de salida.','Dato requerido','Memoria4 / parametros'),
      ('¿Por qué comparar22.9 y no llamar22 a ambos?','Son valores nominales distintos. Se calculan20,22,22.9 por separado; los equipos deben corresponder a la tensión elegida.','Calculado; decisión pendiente','comparacion_tensiones.csv'),
      ('¿Cuánto llega si salen exactamente10kV enMT?',f'Con cargaPQ de estudio y sólo línea llegan{r["linea_con_origen_MT_fijo"][0]["tension_llegada_kV"]:.4f}kV. No confundir con la frontera de generador+TX.','Calculado bajo hipótesis','origen_MT_fijo.csv'),
      ('¿La toma+5% está confirmada?','No. Es elevación efectiva ideal; falta relación real, sentido de toma,AVR y máximo en vacío.','Dato requerido','Memoria4.3'),
      ('¿Se necesita otro elevador en mitad de la línea?','No se ha justificado con el modelo. Evaluar primero origen,TX,AVR y demanda; añadir equipo sin comparación económica no es decisión sustentada.','Decisión condicionada','Memoria4.4'),
      ('¿Hay potencia paraHuancasayani yLimbani?','Los escenarios150/200kW yreservas0/25/50kW muestran déficits posibles. No hay potencia firme de estiaje comprobada.','Pendiente de recurso','balance_fuente.csv'),
      ('¿Las viviendas equivalen aabonados actuales?','No; se usan como usuarios potenciales proyectados. Categoría y servicios no tienen padrón verificado.','Hipótesis identificada','demanda.csv'),
      ('¿Las pérdidas incluyentransformadores?','Se tabulan por separado pérdidas de línea,P0,Pcu deT1/T2 yauxiliares. Se comprueba balanceP/Q.','Calculado bajo hipótesis','resultados.json'),
      ('¿La energía anual viene de mediciones?','No; curva sintética8760h. No dar retorno económico sin curva de carga yprecio real.','Hipótesis identificada','energia.csv'),
      ('¿13m/400daN equivale a400kg colgados?','No; es carga transversal equivalente. En el ejemplo tipo, momento de servicio43.8kNm; capacidad axial pendiente.','Aclarado','Memoria5.1 / fichaSEACE'),
      ('¿Qué distancia soporta unposte de13m?','Depende de tracción,clima,ángulo,altura,terreno ycapacidad. El ejemplo de vano plano no aprueba el corredor real.','Calculado de estudio','vanos_limite_ejemplo.csv'),
      ('¿Se consideró sólo elpeso delcable?','No; hay peso, tracción, hielo, viento, desnivel yángulo con dirección ysigno. Peso propio delposte requiere ficha.','Calculado; capacidad pendiente','fuerzas_por_apoyo.csv'),
      ('¿Aisladores rígidos permiten unH único porcantón?','Paraesta revisión se resuelve cada vano independiente. Confirmar tipo real; sihay cadenas móviles se requiere modelo compatible.','Hipótesis explícita','motor / Memoria5.3'),
      ('¿Se sumó eldesnivel siempre comopeso?','No; se conservan fuerzas con signo. Hay46apoyos con carga ascendente enalgún estado.','Calculado','postes.csv'),
      ('¿Lasretenciones propuestas yaestán aprobadas?','No;16cambios y160retenidas ideales totales son una propuesta por revisar con armadosCAC,predios ysuelo.','Propuesta revisable','postes / retenidas.csv'),
      ('¿La resistencia600daN es deunfabricante contratado?','No; se requiere certificado, punto de ensayo, sección crítica ycapacidadN-M.','Dato requerido','registro-parametros.csv'),
      ('¿Se verificó compresión yflexión simultánea?','Se calculan demandas exteriores, pero nohay capacidad axial ni curvaN-M. No se emite aprobación de postes.','Dato requerido','postes.csv'),
      ('¿La retenida elimina automáticamente el momento?','El modelo ideal neutraliza la componente de cuerda. Rigidez,pretensión,fijaciones ycimientos pueden cambiar el reparto.','Hipótesis explícita','Memoria5.4'),
      ('¿Los vientos se revisaron en todas direcciones?','Se muestrean24azimuts cada15grados bajo estados con viento; no es optimización angular continua.','Calculado con límite','fuerzas_por_apoyo.csv'),
      ('¿ElDEM valida alturas ycruces?','No; sólo permite unperfil de gabinete. Se requiere topografía real de lasfases yobstáculos, incluso si la separación modelada supera7.5m.','Campo requerido','Memoria5.8 / perfiles'),
      ('¿Cómo se resuelven giros mayores90°?','P003/P035/P057 quedan identificados: replantear o diseñar armado especial, sin atribuir equivalencia a unarmadoPIN.','Observación abierta','planilla de apoyos'),
      ('¿Los bloques de cimentación están calculados?','No; faltan suelo, geotecnia,anclaje ycurvaN-M. Se dejan vacíos volúmenes ydimensiones definitivos.','Dato requerido','civiles_pendientes.csv'),
      ('¿La puesta atierra acredita25ohm oseguridad?','No; faltan Wenner,corrientes/tiempos,fajas ypaso/contacto. No basta dibujar una malla.','Dato requerido','Memoria4.5'),
      ('¿Puede copiarse uncutout delSEIN?','No; unaMCH débil puede tenerfalla sostenida menorque lacarga. Faltan curvasAVR/decremento ycoordinación.','Estudio requerido','cortocircuito.csv'),
      ('¿Se conservan longitudes reales enmetrado?','Sí;ter na=3xΣcatenariaEDS, puentes provisionales separados,reserva3% identificada.','Trazable de estudio','metrado_detallado.csv'),
      ('¿Cada armado tienetodos suspernos?','No; conteo funcional porposte. El despiece final depende dearmadoCAC verificado.','Detalle requerido','Especificaciones'),
      ('¿Hay precio actualcotizado?','No;plantilla tiene precios vacíos yantecedenteR01 estimado separado.','Cotización requerida','Presupuesto.xlsx'),
      ('¿Se revisaron proyectos deSEACE?','Sí;contratosUbinas33kV/Carhuaz13.2kV yficha13/400. No se obtuvoETOcompleto deesos contratos. Planos comparables adicionales deSINIA.','Fuente delimitada','08-recursos'),
      ('¿Todos losarchivos delrepositorio están auditados técnicamente?','Se inventarió elrepositorio; revisión detallada dirigida aLimbani,motores,normas yejemplos pertinentes. No se certificarontodos losproyectos ajenos.','Alcance delimitado','inventario-repositorio.csv'),
      ('¿LosPDF yCAD derivan delmismo dibujo?','Sí;PDF renderizados de laspresentaciones delDXF guardado, con modeloUTM yatributos.','Verificar automáticamente yvisual','indice-planos / validacion'),
      ('¿OtraIA puede reproducir sinWindows?','Sí;constructorPython conentradas portables. No se presume disponibilidad deAutoCAD,QGIS ni originales locales deWindows.','Reproducible condependencias','CONTINUIDAD_IA.md')]
    questions.append(('¿Se comprobaron los nuevos anclajes contra cartografía?',f'{r["resumen"]["retenidas_alerta_cartografica"]} posiciones o segmentos presentan alertas frente a casas/cauces. Los puntos ideales con conflicto requieren replanteo; ausencia de conflicto no acredita predio libre.','Observación abierta','anclajes_conflictos_cartograficos.csv'))
    rows=[dict(numero=i,pregunta=q,respuesta=a,estado=e,evidencia=f) for i,(q,a,e,f) in enumerate(questions,1)];tabla(O/'07-evaluacion-y-pendientes/cuestionario_autoevaluacion.csv',rows)
    doc_outputs([('p','Cada pregunta se responde con evidencia o con eldato que falta. No se asigna una nota global que oculte observaciones de diseño abiertas.'),('table',['Nº / pregunta','Respuesta y estado','Evidencia'],[[str(x['numero'])+'. '+x['pregunta'],x['respuesta']+' ['+x['estado']+']',x['evidencia']] for x in rows])],O/'07-evaluacion-y-pendientes/Cuestionario_autoevaluacion','Cuestionario de autoevaluación técnica · LP-R02')
    # Copias portables de recursos y guías, manteniendo originales yhashes.
    Q=O/'08-recursos';Q.mkdir(parents=True,exist_ok=True);root=P.parents[1]
    refs=json.loads((P/'datos/lp-r02/fuentes.json').read_text());portable=[]
    for f in refs:
        dest=Q/'pdf'/Path(f['archivo']).name;dest.parent.mkdir(exist_ok=True);shutil.copy2(root/f['archivo'],dest);portable.append(dict(**f,ruta_paquete=str(dest.relative_to(O))))
    guardar(Q/'fuentes.json',portable)
    for name in ['parametros.json','geometria-base.json','registro-parametros.csv']:shutil.copy2(P/'datos/lp-r02'/name,Q/name)
    shutil.copytree(P/'documentacion/lp-r02',Q/'documentacion',dirs_exist_ok=True)
    for name in ['CONTINUIDAD_IA.md','PLANEACION.md','OBSERVACIONES_REPOSITORIO.md']:shutil.copy2(P/'documentacion/lp-r02'/name,O/'07-evaluacion-y-pendientes'/name)
    for name in ['rd024-2003-EM.pdf','rd023-2003-EM-DGE.pdf']:
        # Referencias normativas originales; no convertir en armadosCACde fabricación.
        src=root/'referencias/normativa/pdf'/name
        if src.exists():shutil.copy2(src,Q/'pdf'/name)
    (Q/'LEER_RECURSOS.md').write_text('''# Recursos consultados

`fuentes.json` registra las diez descargas nuevas conURL,fecha,SHA256,tamaño ylímites deuso. `pdf/` conserva documentos públicos originales sin modificarlos. Los dosPDFDGE dearmados se copian delrepositorio original como referencias deconsulta; no son armadosCACvalidados.

EnSEACE se recuperaron doscontratos ylaficha deunbien. Sus planos deingeniería completos no estaban incluidos enloscontratos; la carpeta no lospresenta como unETOdescargado. Losplanos deotras instalaciones que síse consultaron proceden deSINIA. Verlectura comparativaen07-evaluacion-y-pendientes yel inventario de páginas.

R01 se conserva enelrepositorio. No se reutilizan susarchivos dearchivo/red-urbana como fuentes activas. Elpaquete nuevo excluyeDW L/DWL2,temporales ydependencias deotros equipos.
''')
    (O/'LEER_PRIMERO.md').write_text('''# Línea primaria Limbani–Huancasayani · LP-R02

Abrir `01-expediente/Expediente_revisado_LP_R02.pdf`, `03-calculos/Memoria_calculo_explicita_LP_R02.pdf` y `04-planos/Planos_LP_R02_A3.pdf`.

Ocho carpetas:01expediente;02metrados;03cálculos;04planos;05especificaciones;06presupuesto ycronograma;07evaluación ypendientes;08recursos. LosPDF tienen copias editablesDOCX/Markdown y lasplanillasXLSX/CSV conservan cálculos,fuentes yestado.

Estado: revisión académica condecisiones pendientes. Se han separado casos10/20/22/22.9kV yfronteras deorigen, recalculado fuerzas deextremo con signo ypropuesto ajustesfuncionales. Lascoordenadas/topografía de gabinete noaprueban ubicaciones nivanos. Placas,potenciafirme, capacidadN-M, geotecnia,predios yprotección requieren datosreales.

`07-evaluacion-y-pendientes/CONTINUIDAD_IA.md` explica fuentes,reproducción ypróximos pasos. Laauditoría informática aparece en`validacion.json`; no es aprobación de ingeniería. Elpresupuestoqueda abiertopor faltadecotizaciones ydimensiones definitivas.
''')
    from prosa import humano
    for f in O.rglob('*.md'):
        f.write_text(humano(f.read_text()),encoding='utf-8')
    return rows

def guardar_codigo(P,O):
    """Incluye código e insumos mínimos para reconstruir sin archivos deWindows."""
    root=P.parents[1];dest=O/'08-recursos/codigo';frag=dest/'fragmento-repositorio'
    paths=[P/'scripts/lp_r02',P/'datos/lp-r02',P/'documentacion/lp-r02',P/'requirements-lp-r02.txt',P/'proyecto.yaml',P/'AGENTS.md',root/'herramientas/lineas_primarias',root/'AGENTS.md']
    paths += [P/'datos/lp-r01'/n for n in ['resultados.json','casas-originales.geojson','referencias-osm.geojson','curvas-dem.geojson']]
    for src in paths:
        if not src.exists():continue
        d=frag/src.relative_to(root);d.parent.mkdir(parents=True,exist_ok=True)
        if src.is_dir():shutil.copytree(src,d,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        else:shutil.copy2(src,d)
    (dest/'restaurar.py').write_text('''from pathlib import Path
import shutil,json,sys
source=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit("Uso: python3 restaurar.py CARPETA_NUEVA")
target=Path(sys.argv[1]).resolve()
if target.exists() and any(target.iterdir()):raise SystemExit("Elegir una carpeta nueva vacía para no sobrescribir trabajo")
shutil.copytree(source/"fragmento-repositorio",target,dirs_exist_ok=True)
resources=source.parent
for row in json.loads((resources/"fuentes.json").read_text()):
 dest=target/row["archivo"];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(resources/"pdf"/Path(row["archivo"]).name,dest)
for name in ["rd024-2003-EM.pdf","rd023-2003-EM-DGE.pdf"]:
 dest=target/"referencias/normativa/pdf"/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(resources/"pdf"/name,dest)
print("Reconstruir desde",target)
''')
    (dest/'README.md').write_text('''# Reconstrucción desde este paquete

`fragmento-repositorio` conserva el código e insumos mínimos usados en la revisión; no contiene credenciales ni historialGit. Permite reconstruir incluso si la ramaLP-R02 aún no se ha publicado.

1. Ejecutar `python3 restaurar.py /ruta/a/carpeta-nueva-vacia`.
2. Entrar en esa carpeta e instalar `proyectos/aquiles-linea-primaria-inst-ii/requirements-lp-r02.txt`.
3. Ejecutar `python3 -m unittest discover -s herramientas/lineas_primarias/tests -v`.
4. Ejecutar `python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/construir.py`.

Se reconstruye la revisión académica. Los datos pendientes de campo, placas y fabricantes siguen pendientes; el contenido no convierte la propuesta en diseño de obra.
''')
