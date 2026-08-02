# Matriz de cumplimiento del proyecto

Completar una fila por requisito concreto. `Fuente localizada` no equivale a
`Aplicado`.

| Item | Norma y version | Regla/articulo | Requisito resumido | Dato o decision del proyecto | Evidencia | Responsable | Estado |
|---|---|---|---|---|---|---|---|
| 1 | CNE-U, R.M. N.° 037-2006-MEM/DM | 050-100 y 050-102 | Calcular a 220/380 V; caida maxima 2,5 % por tramo y 4 % total | Suministro academico 380/220 V; longitudes por extraer | `datos/criterios-diseno.yaml`; guia normativa | Codex / revision profesional | En aplicacion |
| 2 | CNE-U | 060-712 | Resistencia de electrodo no mayor de 25 ohm y tension de contacto segura | Red nueva; resistividad no disponible | D-010; guia normativa | Requiere campo | Pendiente de medicion |
| 3 | CNE-U | 120-002 y 120-004 | Clasificar surtidores, llenado, venteos y cableado subterraneo | 6 surtidores, 4 llenados, 4 venteos extraidos del DXF | `arquitectura/datos/grifo.json` | Codex / especialista | En aplicacion |
| 4 | CNE-U | 120-006 y Seccion 110 | Usar alambrado/equipos aptos y union flexible en surtidores | Se incorporara en planos y especificaciones | Guia normativa | Codex / especialista | Pendiente de seleccion |
| 5 | CNE-U | 120-010 | Desconexion simultanea de conductores no puestos a tierra que llegan/pasan por bombas | Paro y contactores de fuerza previstos | DEC-008; guia normativa | Codex | En diseno |
| 6 | CNE-U | 120-012 | Sellos en entradas/salidas del surtidor y limites de clasificacion | Detalles IE-03/IE-06 previstos | Guia normativa | Codex / especialista | En diseno |
| 7 | CNE-U | 120-014 y Seccion 060 | Enlace equipotencial de bombas, canalizaciones y masas | Malla comun y punto de cisterna previstos | DEC-008; guia normativa | Codex | En diseno |
| 8 | RNE EM.010, R.M. N.° 083-2019-VIVIENDA | Art. 7 | Potencia instalada y maxima demanda justificadas | Metodo 1 adoptado; cargas por catalogar | `datos/criterios-diseno.yaml` | Codex | En aplicacion |
| 9 | RNE EM.010 | Art. 8 | Factibilidad, memoria, calculos, especificaciones y planos segun naturaleza | Estructura Aquiles adaptada; factibilidad no recibida | D-009; consigna WhatsApp | Aquiles / Codex | Parcial |
| 10 | RNE EM.010 | Art. 11.1 | Iluminacion de emergencia en rutas de evacuacion no residenciales | Incluida en edificio y salidas | Guia normativa | Codex | En diseno |
| 11 | RNE EM.010 | Tabla de iluminacion | Playa de suministro: 50 lx minimo, Uo 0,40; otras tareas segun fila | Simulacion luminica pendiente | Guia normativa | Codex | Pendiente de calculo |
| 12 | D.S. N.° 054-93-EM | Arts. 34 y 46 | Control de electricidad estatica en descarga y surtidores | Punto equipotencial de cisterna y enlaces previstos | Guia normativa | Codex / operador | En diseno |
| 13 | D.S. N.° 054-93-EM | Arts. 38, 39 y 41 | Equipos certificados y clasificacion por Divisiones para combustibles liquidos | Contraste con Zonas CNE-U documentado | Guia normativa; Guia 001 OSINERGMIN | Especialista | Requiere revision |
| 14 | D.S. N.° 054-93-EM | Art. 42 | Corte remoto visible; controles/tomas a mas de 3 m; principal exterior | Paro de emergencia y TGE exterior previstos | Guia normativa | Codex | En diseno |
| 15 | D.S. N.° 054-93-EM | Art. 43 | Evitar deslumbramiento; avisos a mas de 3 m; revision anual | Notas y fotometria previstas | Guia normativa | Codex / operador | En diseno |
| 16 | D.S. N.° 054-93-EM mod. D.S. N.° 037-2007-EM | Art. 47 | Separacion de lineas aereas: 7,6/10/12 m segun tension | No observadas en DXF; comprobar campo | D-009; guia normativa | Requiere campo | Pendiente de verificacion |
| 17 | D.S. N.° 054-93-EM / R.C.D. N.° 042-2016-OS/CD | Art. 67 / item 15 | Pararrayos donde puedan producirse tormentas electricas | Evaluacion y LPS coordinado previstos para Puno | Guia normativa | Codex / especialista | En diseno |
| 18 | D.S. N.° 054-93-EM | Art. 36 | Minimo de extintores y caracteristicas sectoriales | Fuente S-01 contiene SCI; se coordinara sin atribuirlo al alcance electrico | DXF S-01; guia normativa | Especialidad de seguridad | Coordinacion |
| 19 | Alcance aprobado | DEC-005 | Excluir GLP y GNV | Solo Diesel B5 S-50 y Gasohol Regular/Premium | `registro-decisiones.md` | Aquiles | Aplicado |

## Estados

- `Pendiente`: no revisado.
- `Fuente localizada`: existe enlace oficial, falta leer y aplicar.
- `En revision`: numeral leido, falta validar la interpretacion.
- `Aplicado`: existe evidencia concreta en el proyecto.
- `No aplica`: se justifico por que no corresponde.
- `Requiere especialista`: no puede cerrarse dentro del alcance academico sin
  revision competente.
