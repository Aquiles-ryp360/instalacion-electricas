"""Prepara el registro vigente desde la base normativa conservada."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]


def main():
    n=json.loads((P/'datos/base-normativa.json').read_text(encoding='utf-8'))
    n['fecha_consulta']='2026-10-14'
    n['alcance']='Revisión dirigida de disposiciones aplicables al proyecto académico aislado R03; no certificado de cumplimiento ni permisos obtenidos. Se declara el alcance real de acceso a cada fuente.'
    new=[
      ('N21','R.D.108-2023-MINEM/DGE y anexo: redes secundarias rurales',
       'https://cdn.www.gob.pe/uploads/document/file/4595128/BASES%20PARA%20EL%20DISE%C3%91O%20DE%20REDES%20SECUNDARIAS%20CON%20CONDUCTORES%20AUTOPORTANTES%20PARA%20ELECTRIFICACI%C3%93N.pdf',
       'rd108-anexo2023.pdf','Resolución de2p y anexo22p descargados y leídos. Art2 derogaRD031-2003. Anexo3.2.1:600W/lote,3.2.2:400W/lote;4.7:simultaneidad0.80 residencial y1.0 AP/general;4.6:fp1 residencial/0.9AP. Cuadro3.1 LED50W+4.10W referencial. Cuadros4.1/4.2:35mm2 R40=0.930, I129A; mínimo25mm2.4.5:7.5%BT paraSER;9.2/9.3 tierra de red secundaria, sin extrapolar a central.'),
      ('N22','RNE E.030: R.M.183-2026-VIVIENDA, edición de3/05/2026',
       'https://cdn-web.construccion.org/normas/files/vivienda/RM_183-2026-VIVIENDA.pdf',
       'e030_2026_reproduccion.pdf','Reproducción de la separata oficial ElPeruano62p; artículo11/Tablefactor:zona2 Z0.25; AnexoII p62:Limbani zona2;artículo19/tabla categoríaA2 para generación/transformación U1.5. Suelo y sistema estructural no definidos. Se distingue publicación oficial reproducida de fuente editorial propia.'),
      ('N23','R.M.217-2026-VIVIENDA, disposición transitoria E.030',
       'https://busquedas.elperuano.pe/api/visor_html/2521423-1',
       'rm217_2026_visor.html','Texto de la modificación leído en visor oficial. No se usa una excepción para proyectos de edificación en curso como exoneración automática del diseño académico2026.'),
      ('N24','RNE E.050, R.M.406-2018-VIVIENDA, Suelos y Cimentaciones',
       'https://cdn.www.gob.pe/uploads/document/file/2366655/54%20E.050%20SUELOS%20Y%20CIMENTACIONES%20RM%20N%C2%B0%20406-2018-VIVIENDA.pdf',
       'e050_2018.pdf','Texto oficial descargado; artículo6 obligatoriedad del estudio y AnexoI resumen de condiciones de cimentación. No hay EMS ni presión admisible verificada de Limbani.'),
      ('N25','IEC60909-0:2026, Short-circuit currents, edición3',
       'https://webstore.iec.ch/en/publication/68454',None,
       'Catálogo oficial: publicación23/07/2026, edición3; sustituye2016. Alcance50/60Hz BT/AT confirmado. El cálculo R03 es aproximación física de reactancias; no se afirma aplicación integral de factores o disposiciones de un texto no adquirido.'),
      ('N26','ASCE MOP79, Steel Penstocks, segunda edición2012',
       'https://ascelibrary.org/doi/book/10.1061/9780784412169',None,
       'Catálogo editorial y contenido:cap3 criterios/admisibles,cap4 tubería expuesta,cap8 anclajes,cap11 soldadura,cap14 pruebas. Se propone como referencia complementaria específica para penstocks; no norma peruana ni texto íntegro leído. No se le atribuyen elFy,FS o eficiencia de unión supuestos del modelo.'),
      ('N27','IEC60076-1:2011, Power transformers, edición3',
       'https://webstore.iec.ch/en/publication/588',None,
       'Catálogo oficial vigente, edición y ámbito de transformadores comprobados. Aplicación contractual, altitud y ensayos deben verificarse con texto completo y fabricante; ninguna fórmula de desclasificación se inventa.'),
      ('N28','D.L.1002, disposiciones modificatorias deLCE',
       'https://www.osinergmin.gob.pe/seccion/centro_documental/PlantillaMarcoLegalBusqueda/DL-1002.pdf',
       'dl1002.pdf','Primera disposición modificatoria:artículos3,4,25 y38 deLCE; hidráulica/RER>500kW, distribución pública con demanda>500kW y autorización térmica>500kW. El planteamiento600kW cambia la ruta respecto deR02. Consolidación de todos los cambios posteriores y competencia dePuno se comprueban antes de tramitar.')]
    ids={f['id'] for f in n['fuentes']}
    for ident,title,url,local,scope in new:
        if ident not in ids:
            n['fuentes'].append(dict(id=ident,titulo=title,url=url,
                local=('proyectos/aquiles-central-michell-banki/fuentes/local/investigacion-r03/'+local) if local else None,
                lectura=scope))
    rows=[
      ('N01,011.A-F','Separar generación/suministro de utilización y exigir responsable competente para ejecución.','Caps.1,8,9; autor estudiante, sin firma de expediente ejecutivo.','Alcance académico definido; habilitación para obra pendiente'),
      ('N01,130.A/B/E','Regular velocidad, disparo independiente por sobrevelocidad y parada manual.','Cap.6 yPL06; gobernador,ELC y cierre independiente.','Funciones diseñadas; ajuste y pruebas de equipo pendientes'),
      ('N01,132','Poner a tierra neutro de generación mediante impedancia según sistema.','Cap.8 yPL07; barra de neutros/NGR y modos de paralelismo.','Esquema propuesto; corriente capacitiva y NGR pendientes'),
      ('N01,036.A-B','Evaluar paso, contacto y potenciales transferidos.','Cap.8; sensibilidad deRg y puesta a tierra.','Sin resistividad ni verificación de potenciales; no se acredita seguridad'),
      ('N01,036.D','No aplicar25ohm de un electrodo individual como seguridad de malla.','Cap.8; malla y casos de suelo.','Alcance de regla distinguido; medición pendiente'),
      ('N01,125.A/Tabla125-1','Espacios de trabajoBT por tensión a tierra y condición; ancho y altura mínimos.','Cap.8/PL05; pasillo frontal1.5m de estudio.','Tabla151-600V hasta1.2m; geometría de tablero a verificar'),
      ('N01,125.B/Tabla124-1','ParaMT aplicar protección correspondiente a tensión y partes expuestas.','PL05/PL07: patioMT cercado y celdas.','No se dimensiona la protección con espacioBT'),
      ('N01,113/114/116','Salidas, ventilación y protección frente a humedad/agua en estación.','Cap.5/8: accesos, drenaje, recinto y diesel exterior.','Esquema; crecida y ubicación real pendientes'),
      ('N01,Sección14','Disposición, ventilación y mantenimiento de acumuladores.','Cap.8:CC24V100Ah, autonomía y espacio.','Carga y batería hipotéticas; aceptación pendiente'),
      ('N01,130 yParte4','Maniobra y mantenimiento de máquinas con parada segura.','Cap.6/8 y secuencia de arranque sinSEIN.','Lógica académica; protocolo fabricante pendiente'),
      ('N02,030-004/050-104(3)-(7)','Cable según tabla, método de instalación, correcciones y carga continua.','Cap.8:dos paralelosCu240/grupo, conductor y placa.','Comparación térmica; disposición definitiva pendiente'),
      ('N02,050-106','Documentar exclusión y ciclos de cargas auxiliares.','Cap.4/8; una bomba de drenaje activa y gobernadores por unidad.','Inventario y enclavamientos propuestos'),
      ('N02,050-102','Caída de tensión de utilización2.5%individual/4%total.','Cap.8:alimentaciones auxiliares y cable de generador.','No se traslada a toda la red pública; circuitos interiores pendientes'),
      ('N03,020/060 modificaciones','Aplicar protección y tierra de interiores junto con texto base.','Cap.8;TSA con neutro independiente yPE.','Selección final por circuitos pendientes'),
      ('N01,232.A/Tabla232-1','Seleccionar distanciasMT por superficie, conductor y flecha crítica.','Cap.8;10kV expuesto, tabla hasta23kV.','Casos leídos; vanos/topografía no comprobados'),
      ('N01,232.C.1.b','No corregir por altitud indiscriminadamente todas las separaciones de10/22.9kV.','Cap.8;altitud de equipos por fabricante.','Alcance verificado; coordinación de aislamiento pendiente'),
      ('N01,234/Secciones24-27','Verificar cruces, resistencia, cargas y aislamiento de línea.','PL01 y8km de corredor, sin postes ejecutivos.','No se acredita línea construible con un corredor'),
      ('N21,art2 resolución','RetirarRD031-2003 como norma vigente deBT rural.','Cap.4/9;R.D.108-2023 y anexo.','Corrección incorporada'),
      ('N21,3.2.1/3.2.2/4.7','600/400W/lote y simultaneidad0.80; cambios requieren verificaciones.','Cap.4;1037usuarios potenciales, sin350W arbitrarios.','Limbani tipoI; clasificación deHuancasayani por confirmar'),
      ('N21,3.3/Cuadro3.1/3.4','Incluir pérdidasAP y sustentar cargas comunitarias/productivas.','Cap.4;LED54.1Wreferencial y cuadro32kWde servicios.','226luminarias y servicios son escenario, no inventario medido'),
      ('N21,Cuadros4.1/4.2/4.5','Autoportante:secciónmínima25mm2 y caídaBT ruralhasta7.5%.','Cap.8;3x35+16/25, rama25kW150m.','Parámetros norma; tramos reales y calidad global pendientes'),
      ('N21,9.2/9.3','Aplicar puesta a tierra equivalente deBT según categoríaSER.','Cap.8;neutrosSED yPEN por separado delNGR de generación.','Reglas deBT no sustituyen paso/contacto decentral'),
      ('N04/N28,art3LCE','600kWhidráulicos y demanda pública>500kW requieren analizar concesiones.','Cap.9;generación y distribución; comparar opción200kW.','Ninguna concesión obtenida; no reutilizar exención deR02'),
      ('N28,art4LCE','Respaldo térmico600kW superaumbral500kW de autorización.','Cap.8/9;grupo de respaldo académico.','Autorización sectorial y titular pendientes'),
      ('N04,art7','Cumplir seguridad,ambiente,patrimonio y comunicación incluso para potencia menor.','Cap.9:alternativas150/200.','No se declara autorización universal por pequeña potencia'),
      ('N05,44/47/53','Derecho,licencia y disponibilidad sin afectar caudal ecológico/terceros.','Caps.3/9;balance y fuentesANA.','Simulación no es acreditación ni licencia'),
      ('N06,153-155/N07,6','Estudio de caudal ecológico con método y categoría aplicables.','Cap.3;reserva15%estacional como hipótesis.','No aprobado; no es porcentaje legal universal'),
      ('N05,74/104/N19,79/81/84/85','Faja marginal, obras y procedimientos diferenciados.','Cap.9:ruta ANA, captación/restitución.','Predios/faja/autorización/licencia pendientes'),
      ('N08/N09,7-11/Anexo1','Clasificación ambiental según configuración, regulación y localización.','Cap.9;centraldepasada, sin asignarDIA automática.','Replanteamiento real podría exigir modificación/adecuación de instrumento'),
      ('N15,art48modificado','No confundir adecuación de actividadencurso con autorización de nuevasobras.','Cap.9;verificar situaciónjurídica decentralreferida.','Situación decentralexistente no acreditada'),
      ('N22,art11/AnexoII/TablaZ','Limbani zona2,Z0.25 enE0302026.','Cap.7;acciones sísmicas de edificio/soportes.','S,R,periodos ygeotecnia faltan'),
      ('N22,art19/tablaA2','Generación ytransformación como edificación esencial,U1.5.','Cap.7/PL05;casa de máquinas.','No es comprobación estructural ni permiso deobra'),
      ('N23,disposicióntransitoria','Verificar fecha/condiciones deproyectosencurso antes deexcepción.','Cap.9;se adoptaE0302026.','No se invocaexcepción automática'),
      ('N24,art6/AnexoI','EMS ycondiciones decimentación enplanos.','Caps.7/11;anclajes ysoportes.','SinEMS;anclajeenroca condicionado'),
      ('N16/N17','Seguridadlaboral,bloqueo deenergías,izaje,excavación yrescate.','Cap.9;plan deoperación ymantenimiento.','Procedimientos académicos; personal/obra no certificados'),
      ('N11,IEC60034-1:2026','Potencia/rendimiento de máquina aaltitud ytemperatura del sitio.','Cap.6;200kW/250kVA porgrupo acondicioneslocales.','Catálogo verificado;normacompleta/curvas pendientes'),
      ('N25,IEC60909-0:2026','Elegir edición actual yestudio de fallas máx/mín.','Cap.8;redaislada,reactancias supuestas,sinfuenteSEIN.','Cálculo simplificado, no aplicaciónnormativa integral'),
      ('N27,IEC60076-1:2011','Especificartransformación,grupo,placa,pérdidas ypruebas.','Cap.8;T1 800kVA,10/0.38kV,aislamiento24kV deestudio.','Texto íntegro,altitud e inrush pendientes'),
      ('N20/N26complementarios','Presión,vacío,térmica,soportes,anclajes ypruebas de penstock.','Cap.7;MOC,linealización ymembrana.','USBRhistórico leído;ASCEcontenido consultado,sinatribuiradmisibles'),
      ('N01/N04/operador futuro','Interconexión futura requiere estudios,requisitos yautorizaciones vigentes entonces.','Cap.8;horizonte2046-2076.','Sinpunto ni conexión aprobados;diseñoinicialaislado')]
    n['matriz']=[[f'M{i:02d}',ref,rule,evidence,status] for i,(ref,rule,evidence,status) in enumerate(rows,1)]
    (P/'datos/normativa-r03.json').write_text(json.dumps(n,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Registro R03:',len(n['fuentes']),'fuentes normativas y',len(rows),'requisitos')


if __name__=='__main__':main()
