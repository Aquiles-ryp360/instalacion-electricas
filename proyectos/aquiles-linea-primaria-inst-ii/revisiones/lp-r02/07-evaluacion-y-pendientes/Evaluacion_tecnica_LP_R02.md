# Evaluación técnica y datos pendientes · LP-R02

LP-R02 · 18/10/2026 · Diseño académico revisable

## 1. Alcance y decisión de diseño

Se revisa una sola línea primaria trifásica, sin ramificaciones, entre la transformación de salida de la minicentral de Limbani y una estación de llegada propuesta en Huancasayani. La red de usuarios posterior queda fuera del trazado. Las tres localidades de la demanda representan un ámbito potencial atendido aguas abajo; no tres ramales construidos por este proyecto.

El eje candidato heredado tiene 6,696.369 m en UTM WGS84 zona19S, 111 apoyos y 110 vanos. La longitud física EDS por fase es 6,758.120 m. Las coordenadas y cotas DEM proceden de LP-R01: no son levantamiento de campo. Se conservan para auditar el corredor; cada observación impide promoverlo a plano de construcción.

El manifiesto original fija sistema aislado alimentado por MCH. No se ha encontrado placa que confirme la tensión de salida ni potencia neta de estiaje. La referencia200 kW del proyecto de línea y el documento local de otra asignatura150 kW requieren conciliación. Se estudian ambos niveles de oferta, sin trasladar una potencia a la otra asignatura.

| Dato | Estado vigente |
| --- | --- |
| Tensión confirmada de salida | Pendiente: placa, relación de T1 y regulación AVR |
| Potencia neta de estiaje | Pendiente: recurso, máquina, auxiliares y reserva para Limbani |
| Demanda de estudio | 171.486 kW; viviendas proyectadas y cargas supuestas |
| Trazado y predios | Corredor de gabinete; dos SE propuestas, sin predios aprobados |
| Decisión de tensión | Pendiente. Comparar10 kV y22.9 kV;20/22 kV sólo sensibilidad |

## 2. Resultado de la evaluación

La revisión sustituye la tracción compartida por cantón por estados independientes de cada vano para la hipótesis de aisladores rígidos. Se hallan 0 apoyos que exceden la comprobación de flexión tipo al recalcular el esquema anterior y 46 apoyos con alguna carga ascendente de conductores. Se proponen 16 cambios funcionales a retención para estudiar. Las retenidas ideales totales pasan de 128 a 160; su terreno y anclaje siguen sin verificar.

El nuevo cálculo arroja 0 vanos con separación inferior al margen académico7.5 m respecto al perfil heredado. Separación mínima de esa comparación: 7.549 m. Esta cifra no demuestra gálibo real ni seguridad de ningún vano, incluso cuando supera7.5 m.

Con10 kV nominales equivalentes en origen de generación y sin elevación supuesta, la BT de llegada es 350.3 V. Con elevación efectiva1.05 pu resulta 371.1 V. El efecto de los transformadores se debe revisar antes de atribuir toda la caída a la línea.

## 9. Recursos y referencias de contraste

Se inventariaron los archivos del repositorio y se comprobaron los tres ZIP existentes medianteCRC. ElZIP de Capachica se abrió y sus seis DXF se analizaron; aporta organización planta/perfil/unifilar/detalles, no prueba las cargas de Limbani. ElZIPLP-R01 se conserva íntegro; incluye archivos de bloqueoDW L/DWL2 que no se incorporan al paquete nuevo. La bibliotecaDGE es referencia; no constituye adaptación validada aCAC.

Los términos de Electro Puno consultados utilizan once volúmenes y anexos. Las ocho carpetas aquí responden a organización académica, no a una exigencia universal de ocho capítulos. Se agrupan cálculos eléctricos/mecánicos/protección en03, armados en04 y especificaciones en05, preservando la correspondencia de contenido.

SEACE: se descargaron dos contratos oficiales comparables, Ubinas33 kV yCarhuaz13.2 kV, y la ficha de poste13/400. Los contratos no incluyen los planos completos del expediente. Para modelos gráficos se descargaron delSINIA el planos de componentesLircay, mapaTablachaca y planillaChoclococha. El buscadorSEACE redirige a una aplicación dinámica; los documentos directos pudieron recuperarse por descargaHTTP aunque la herramienta web devolvía403.

| ID y entidad | Documento local / límite |
| --- | --- |
| R02-F01 MINEM | rd018_2003.pdf · Bases primarias; texto aprobado2003. No sustituye consolidación normativa completa. |
| R02-F02 MINEM | cne_suministro_2011.pdf · Cargas, grados, distancias, factores. Revisar modificaciones aplicables al cierre. |
| R02-F03 SEACE/PERU COMPRAS | poste_seace_13_400.pdf · Ficha de bien13/400/2/180/375; rotulado daN. No certificado de poste600 daN ni ensayo axial. |
| R02-F04 Electro Puno | tdr_electropuno_lp.pdf · Referencia de estructura documental Tototani; normativa histórica requiere cotejo actual. |
| R02-F05 SEACE/Electrosur | seace_ubinas_contrato_023_2021.pdf · LP007-2020-ES. Línea33 kV. Contrato y resumen de presupuesto; no planos de ingeniería. |
| R02-F06 SEACE/Hidrandina | seace_carhuaz_contrato_091_2024.pdf · AS-SM44-2023-HDNA-3. Consultoría13.2 kV; no expediente técnico adjunto descargado. |
| R02-F07 SINIA/Municipalidad Huando | dia_tinyacclla_pachachaca.pdf · Referencia de componentes. Se observaron diferencias13.2/22.9 kV y presupuesto: requiere evaluación crítica. |
| R02-F08 SINIA | dia-hospital_lircay.pdf · DIA de sistema22.9 kV; se revisaron planos decomponentes/trazo/ubicación enanexos186–195. No trasladar1250 kVA ni ajustes. |
| R02-F09 SINIA | plano_trazo_tablachaca.pdf · Plano de ejes con coordenadas y cuadro de tramos. Referencia de presentación, no ruta de Limbani. |
| R02-F10 SINIA | dia_choclococha.pdf · Planilla de estructuras con poste/armado/vano/coordenadas. No transferir clima ni equipos. |

Cada fuente conserva URL, fecha, SHA-256, tamaño y uso permitido en 08-recursos/fuentes.json. Las referencias históricas pueden tener inconsistencias: se observaron diferencias de tensión/totales enTinyacclla y porcentajes del resumen deUbinas; no se trasladan sus cifras como reglas o precios actuales.

## 10. Datos necesarios para cerrar ingeniería

| Prioridad | Dato verificable | Decisión afectada |
| --- | --- | --- |
| 1 | Placas generador/T1/T2, ubicación y predios | Tensión nominal, potencia neta y transformación |
| 1 | Aforos/curva de disponibilidad y demanda horaria | Suficiencia150/200 kW, reserva y horizonte |
| 1 | Topografía de campo de terna y cruces | Ubicación, altura y distancia real entre postes |
| 1 | Ficha de poste y armadoCAC, cargasN-M | Soportes, retenidas y accesorios |
| 1 | Geotecnia y Wenner | Cimentaciones, anclajes y tensiones de paso/contacto |
| 1 | AVR/decremento, TC/TT y curvas de equipos | Coordinación de protecciones e inrush |
| 2 | Cotizaciones con logística y ensayos | Elección10/22.9 kV y presupuesto |
| 2 | Consigna/rúbrica y docente de esta asignatura | Formato de entrega y alcance de evaluación |

La ejecución informática y la revisión documental de esta entrega no equivalen a aprobación profesional ni a levantamiento. No se requiere permiso del usuario para continuar corrigiendo cálculos; sí se requieren datos técnicos reales para cerrar las decisiones dependientes. El archivoCONTINUIDAD_IA.md indica cómo reproducir y qué datos actualizar sin reactivar fuentes históricas.

