# Guia normativa aplicada al grifo

Fecha de comprobacion: 2026-08-02.
Alcance: anteproyecto academico nuevo para combustibles liquidos; GLP y GNV no
aplican.

Esta guia resume criterios de proyecto. No reemplaza el texto oficial ni la
revision de un ingeniero habilitado para un expediente constructivo.

## Fuentes oficiales verificadas

1. [Codigo Nacional de Electricidad - Utilizacion, R.M. N.° 037-2006-MEM/DM](https://www.gob.pe/institucion/osinergmin/normas-legales/738607-037-2006-mem-dm).
2. [RNE, Norma EM.010 Instalaciones electricas interiores, R.M. N.° 083-2019-VIVIENDA](https://www.gob.pe/institucion/vivienda/normas-legales/266383-083-2019-vivienda).
3. [D.S. N.° 054-93-EM, Reglamento de seguridad para establecimientos de venta de combustibles](https://www.gob.pe/institucion/minem/normas-legales/5136516-054-93-em).
4. [D.S. N.° 037-2007-EM, modificacion de distancias sectoriales](https://www.osinergmin.gob.pe/seccion/centro_documental/Institucional/CRO/Normas/DS-037-2007-EM.pdf).
5. [Guia Tecnica N.° 001-OS/DSR-UTH de OSINERGMIN](https://www.osinergmin.gob.pe/seccion/centro_documental/hidrocarburos/Documentos/Comercializacion/Documentos-Tecnicos/Guia-Tecnica-001-OS-DSR-UTH.pdf), de caracter orientativo para areas clasificadas.
6. [Listado de condiciones de seguridad de criticidad alta en grifos y estaciones de servicio, R.C.D. N.° 042-2016-OS/CD](https://busquedas.elperuano.pe/dispositivo/NL/1353511-1), usado como control complementario de fiscalizacion.
7. [R.M. N.° 120-2026-MINEM/DM, publicacion oficial del proyecto normativo](https://www.gob.pe/institucion/minem/normas-legales/7912689-120-2026-minem-dm), verificada en el navegador integrado y contrastada con las cinco paginas del proyecto de decreto supremo.

En marzo de 2026 se publico para comentarios la R.M. N.° 120-2026-MINEM/DM,
un **proyecto** que modifica el articulo 31 del D.S. N.° 054-93-EM para el
registro tecnologico de las mediciones diarias de volumen y agrega el articulo
55A al D.S. N.° 045-2001-EM para publicar informacion de procedencia y calidad
de combustibles. A la fecha de consulta no se identifico una norma final que
sustituya los requisitos electricos aqui aplicados; el proyecto publicado no se
trata como norma vigente ni cambia los criterios electricos de este anteproyecto.

## Jerarquia de uso en este proyecto

- El CNE-U gobierna el diseno electrico: demanda, conductores, proteccion,
  puesta a tierra, alambrado y equipos en lugares peligrosos.
- EM.010 define el contenido del expediente, demanda, iluminacion y suministro
  de emergencia en edificaciones.
- El D.S. N.° 054-93-EM y su modificatoria incorporan obligaciones sectoriales
  propias del grifo.
- La Guia 001 de OSINERGMIN ayuda a interpretar la clasificacion, pero no se
  presenta como reemplazo del CNE-U ni del reglamento.
- Cuando el reglamento sectorial usa `Division` y el CNE-U para obra nueva usa
  `Zona`, ambos criterios se muestran. No se afirma una equivalencia automatica.

## Reglas CNE-U que deben aparecer en calculos y planos

### Demanda y caida de tension

- Regla 050-100: para calculos de baja tension se emplean 220 V o 380 V, segun
  corresponda. Es coherente con el suministro academico 380/220 V adoptado.
- Regla 050-102: alimentador y circuito derivado no deben exceder 2,5 % cada
  uno; el recorrido total hasta el punto mas alejado no debe exceder 4 %.
- EM.010 art. 7: el expediente debe mostrar potencia instalada y maxima
  demanda. Se usara el metodo de cargas realmente proyectadas, con factores de
  demanda/simultaneidad justificados. Una potencia de catalogo adoptada no se
  presentara como placa observada.

### Puesta a tierra y equipotencialidad

- Regla 060-712: la resistencia debe limitar las tensiones de contacto y no ser
  mayor de 25 ohm. Si un electrodo simple supera 25 ohm, se requiere otro a no
  menos de 2 m o a una distancia equivalente a su longitud, o un metodo
  alternativo.
- Regla 120-014: bombas de surtidores, canalizaciones y demas partes metalicas
  que normalmente no transportan corriente deben enlazarse a tierra conforme a
  la Seccion 060.
- D.S. N.° 054-93-EM arts. 34 y 46: la descarga de cisterna y los surtidores
  requieren control operativo de electricidad estatica. El plano debe incluir
  punto de conexion equipotencial para cisterna y enlace de surtidores,
  marquesina, tuberias y tanques.
- Regla 060-710: los electrodos exclusivos del sistema de proteccion contra el
  rayo no deben utilizarse por si solos como puesta a tierra del alambrado u
  otros equipos; las interconexiones se resolveran conforme al sistema completo.

### Surtidores y lugares peligrosos

La Seccion 120, reglas 120-002 a 120-014, aplica a puestos de venta de
combustibles y estaciones de servicio. Para proyecto nuevo se adopta el sistema
de zonas de la regla 120-004:

| Fuente | Clasificacion CNE-U propuesta | Extension que debe dibujarse |
|---|---|---|
| Receptor de la pistola dentro del surtidor | Clase I, Zona 0 | Volumen interno del receptor |
| Interior de la cubierta del surtidor | Clase I, Zona 1 | Hasta 1,20 m sobre la base, incluido espacio inferior con equipo/cableado |
| Espacio interior inmediato a la Zona 1 | Clase I, Zona 1 | Hasta 0,45 m horizontal segun configuracion de la cubierta |
| Parte separada por tabique hermetico y espacio superior | Clase I, Zona 2 | Segun construccion certificada del surtidor |
| Exterior de cada surtidor | Clase I, Zona 2 | Hasta 6,00 m horizontal y 0,45 m sobre pavimento/suelo |
| Tuberia/boca de llenado | Clase I, Zona 2 | Hasta 3,00 m horizontal y 0,45 m sobre pavimento/suelo |
| Venteo que descarga hacia arriba | Clase I, Zona 1 | Esfera de radio 0,90 m desde la descarga |
| Venteo, envolvente exterior | Clase I, Zona 2 | Entre radios 0,90 m y 1,50 m |
| Alambrado/equipo bajo zonas definidas | Clase I, Zona 1 | Hasta el punto donde emerge del suelo |

Una pared sin aberturas puede limitar la extension indicada para venteos. La
geometria final depende de las alturas y configuraciones reales, por lo que el
plano de anteproyecto llevara una nota de verificacion en campo.

Otras consecuencias directas:

- Regla 120-006: alambrado/equipos dentro del area clasificada cumplen la
  Seccion 110. Si el surtidor se alimenta con conducto metalico, se instala una
  union y un accesorio flexible que admita movimiento relativo.
- Regla 120-010: cada circuito que llega o atraviesa una bomba de surtidor debe
  desconectar simultaneamente todos los conductores no puestos a tierra.
- Regla 120-012: se requieren sellos en cada conducto que entra o sale del
  surtidor o comunica con su cavidad, y en limites verticales/horizontales segun
  las reglas aplicables de la Seccion 110.
- La seleccion final de luminarias, cajas, sellos, motores y accesorios requiere
  certificado y marcado compatible con la zona, grupo de gas y clase de
  temperatura; no basta rotular un equipo como “antiexplosivo”.

## Contraste sectorial por divisiones

El D.S. N.° 054-93-EM, arts. 38, 39 y 41, usa Clase I, Division 1/2. La Guia
001 de OSINERGMIN ilustra, para combustibles liquidos, el interior del surtidor
y fosas/conexiones bajo nivel como Division 1; el contorno de 6 m y 0,5 m de
altura, el entorno de llenado de 3 m y 0,5 m de altura y el anillo exterior de
venteos como Division 2. Sus dimensiones no coinciden exactamente en todos los
casos con el sistema de zonas del CNE-U (por ejemplo 0,90 m frente a 1,00 m en
el venteo).

En este anteproyecto:

1. el plano principal usa Zona 0/1/2 porque es diseno nuevo bajo CNE-U;
2. una nota/cuadro de contraste conserva las exigencias sectoriales por
   divisiones para revision de OSINERGMIN;
3. la envolvente mas exigente se usa para ubicar equipos ordinarios fuera de
   riesgo cuando las reglas se superponen;
4. el profesional revisor debe confirmar la marcacion de cada equipo con su
   certificado, sin asumir que `Zona 1` y `Division 1` son sinonimos perfectos.

## Paro de emergencia y ubicacion de equipos

- D.S. N.° 054-93-EM art. 42: debe existir un corte electrico remoto, visible y
  operativo para unidades de suministro y bombas remotas.
- Las cajas de control, interruptores y tomas deben quedar a mas de 3 m de
  venteos, bocas de llenado e islas de surtidores.
- El interruptor principal se ubica en la parte exterior del edificio en panel
  metalico protegido.
- Art. 43: anuncios electricos iluminados quedan a mas de 3 m de venteos y
  llenado; los reflectores se orientan para no deslumbrar conductores; la
  instalacion requiere inspeccion por lo menos anual.
- Art. 49: el surtidor debe permitir desconexion exterior; cuando opere con
  bombas remotas requiere la valvula de cierre automatico sectorial. Esta
  valvula es parte del sistema de combustible y se coordina, pero no se inventa
  como partida electrica sin ficha.

## Lineas aereas, rayos e intemperie

El art. 47 modificado por el D.S. N.° 037-2007-EM exige, desde la proyeccion
horizontal de una linea aerea hasta surtidores, dispensadores o tanques:

| Tension de linea | Distancia minima |
|---|---:|
| Hasta 1 kV | 7,60 m |
| Mayor de 1 kV hasta 36 kV | 7,60 m |
| Mayor de 36 kV hasta 145 kV | 10,00 m |
| Mayor de 145 kV hasta 220 kV | 12,00 m |

No se observa una linea aerea dentro del predio en el DXF; la verificacion de
campo queda obligatoria. El art. 67 del reglamento y la matriz de criticidad de
OSINERGMIN exigen sistema de pararrayos donde puedan producirse tormentas
electricas. Para el caso expuesto en Puno se incluira evaluacion de riesgo y un
sistema coordinado con proteccion contra sobretensiones; no se colocara un
captor aislado sin calculo ni enlace equipotencial.

Los equipos exteriores se seleccionan por intemperie, radiacion UV, polvo,
agua y temperatura del lugar, ademas de su aptitud para area clasificada cuando
corresponda.

## Iluminacion y emergencia

- EM.010 art. 11.1: toda edificacion no residencial debe tener iluminacion de
  emergencia en rutas de evacuacion.
- La tabla de EM.010 indica 50 lx para planta de suministro de combustible,
  uniformidad 0,40 y reconocimiento de colores de seguridad; este es el minimo
  de referencia para la playa. Las tareas de caja, oficina, minimarket, cuarto
  de maquinas, escaleras y circulacion se calculan con sus filas especificas.
- EM.010 art. 11.2 no enumera a todo grifo como edificacion que obligatoriamente
  deba tener grupo electrogeno automatico. El grupo electrogeno del proyecto es
  un criterio de continuidad adoptado (DEC-008), no una atribucion falsa a ese
  articulo.

## Contenido minimo del expediente

EM.010 arts. 7 y 8 obligan a justificar potencia instalada/maxima demanda y, de
acuerdo con la naturaleza del proyecto, presentar factibilidad, memoria
descriptiva, memoria de calculo, especificaciones y planos de instalaciones,
iluminacion, protecciones, sobretensiones, rayo, generacion y otras cargas. El
expediente academico seguira esa estructura y añadira metrados/presupuesto por
la consigna del curso.

## Advertencias que deben repetirse en las laminas

- `PROYECTO ACADEMICO NUEVO - NO CONSTRUIR SIN FACTIBILIDAD, VERIFICACION DE
  CAMPO, FICHAS CERTIFICADAS Y REVISION PROFESIONAL`.
- La arquitectura procede de CAD-001; la DREM no se presenta como aprobadora
  del nuevo proyecto electrico.
- Potencia de cortocircuito y configuracion exacta de la acometida: pendientes
  de Electro Puno.
- Limites de areas clasificadas: propuesta academica trazada sobre puntos
  extraidos; confirmar elevaciones y configuracion real.
- GLP y GNV: fuera del alcance.
