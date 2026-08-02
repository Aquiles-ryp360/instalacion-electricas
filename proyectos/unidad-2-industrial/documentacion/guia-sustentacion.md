# Guia de sustentacion del proyecto de grifo

Autor: Aquiles Taylor Ramos Yapo.
Docente: Mg. Gregorio Meza Marocho.
Tiempo esperado: 10 a 15 minutos.
Estado: preparada con los resultados reproducibles del 2026-08-02.

## Exposicion sugerida de 7 minutos

1. **Problema y fuente (45 s):** es un proyecto electrico academico nuevo para
   un grifo de combustibles liquidos en Caracoto. El DXF facilitado por la DREM
   solo aporta arquitectura, propietario consignado, tanques, islas y surtidores.
2. **Alcance (45 s):** incluye Diesel B5 S-50, Gasohol Regular y Premium; excluye
   GLP y GNV. Comprende baja tension, fuerza, alumbrado, tableros, respaldo, PAT,
   proteccion contra rayo y propuesta de areas peligrosas.
3. **Arquitectura y cargas (60 s):** 5983 m2 de terreno, 2167 m2 de proyecto,
   cuatro tanques, tres islas, seis surtidores y edificio administrativo de tres
   niveles. El modelo tiene 35 circuitos.
4. **Resultados de calculo (90 s):** 34.80 kW instalados, 28.40 kW y 33.31 kVA de
   maxima demanda; 39.97 kVA con 20 % de reserva. Se propone suministro de 50 kVA,
   interruptor 4P-80 A y alimentador Cu 4x35 mm2 + PE 16 mm2.
5. **Seguridad (90 s):** RCBO de 30 mA, paro de emergencia, equipotencialidad,
   objetivo PAT de 10 ohm sin exceder 25 ohm, SPD y proteccion contra rayo. La
   lamina IE-06 aplica las envolventes del CNE-U 120 como propuesta academica,
   pendiente de revision especializada.
6. **Continuidad e iluminacion (60 s):** grupo standby de 37.5 kVA con correccion
   por altitud, ATS 4P y UPS separadas para combustible e IT. Todas las zonas
   cumplen el calculo medio por lumenes; falta simulacion IES/LDT punto por punto.
7. **Entregables y limites (30 s):** expediente con formato de la primera unidad,
   metrados/presupuesto y seis planos A1 vectoriales. No es un expediente para
   construir hasta contar con factibilidad, placas, campo y revision profesional.

## Datos que conviene memorizar

| Dato | Valor |
|---|---:|
| Sistema | 3 x 380/220 V, 60 Hz, 3F+N+PE |
| Circuitos | 35 |
| Potencia instalada | 34.80 kW / 40.77 kVA |
| Maxima demanda | 28.40 kW / 33.31 kVA |
| Demanda con reserva | 39.97 kVA |
| Suministro propuesto | 50 kVA |
| Principal | 80 A, 4P, Icu minimo 25 kA sujeto a Icc real |
| Alimentador principal | Cu 4 x 35 mm2 + PE 16 mm2 |
| Caida principal | 0.39 % |
| Peor caida total | 3.17 % |
| Desbalance | 3.74 % |
| Grupo | 37.5 kVA standby; 31.13 kVA disponibles con factor 0.8302 |
| Carga critica permanente | 12.47 kVA |
| Presupuesto referencial | S/ 394,665.70, incluido IGV |
| Planos | IE-01 a IE-06, PDF A1 vectorial y DXF editable |

## Preguntas probables y respuestas cortas

### 1. ¿El proyecto electrico ya existia en el DXF?

No. El DXF es una referencia arquitectonica/documental. La distribucion
electrica, las cargas, los calculos y las seis laminas electricas son nuevos.

### 2. ¿Por que figura Miguel Mamani Chuquicallata?

Porque aparece como propietario en la documentacion tecnica facilitada por la
DREM. Se cita como dato rescatado, sin afirmar verificacion registral ni aprobacion
de este proyecto.

### 3. ¿Que combustibles abarca?

Diesel B5 S-50, Gasohol Regular y Gasohol Premium. GLP y GNV estan excluidos del
alcance, cargas, planos y clasificacion especifica.

### 4. ¿Por que se adopta 380/220 V trifasico?

Porque existen motores, cargas distribuidas y un nivel de demanda propio de un
establecimiento comercial-industrial. Es un criterio de diseño condicionado a la
factibilidad de Electro Puno.

### 5. ¿Como se obtuvo la maxima demanda?

Se sumaron las demandas de 35 circuitos aplicando los factores declarados por uso
segun el metodo 1 del articulo 7 de la EM.010, y despues se agrego 20 % de reserva
para comprobar servicio y principal.

### 6. ¿Por que el servicio es de 50 kVA?

La demanda con reserva es 39.97 kVA. Un servicio de 50 kVA deja margen razonable,
pero no sustituye la potencia que autorice la concesionaria.

### 7. ¿Por que el interruptor general es de 80 A?

La corriente maxima de fase con reserva es 61.88 A. El interruptor de 80 A queda
por encima de la corriente de diseño y por debajo de la ampacidad corregida del
alimentador, 97.60 A.

### 8. ¿Por que se usa 35 mm2 en el alimentador?

Cumple ampacidad corregida y caida de tension con el metodo de instalacion adoptado.
Ademas conserva margen ante temperatura, agrupamiento y futura confirmacion del
suministro.

### 9. ¿Cumple caida de tension?

Si en el modelo academico: 0.39 % en el principal y 3.17 % en el peor recorrido
total, por debajo del criterio de 2.5 % parcial y 4 % total de la Regla 050-102.

### 10. ¿Como se equilibro el sistema?

Las cargas monofasicas se repartieron entre R, S y T. El desbalance de demanda
resultante es 3.74 %, menor al objetivo de 10 %.

### 11. ¿Que proteccion diferencial se uso?

RCBO de sensibilidad no mayor de 30 mA por circuito de utilizacion. Esto limita el
impacto de una falla a un solo circuito y mejora continuidad frente a un diferencial
comun para todo el tablero.

### 12. ¿El Icu de 25 kA es definitivo?

No. Es un minimo conservador de anteproyecto en cabecera. Debe verificarse con la
corriente de cortocircuito real de Electro Puno y con tablas de coordinacion del
fabricante.

### 13. ¿Que son las areas clasificadas?

Son zonas donde puede existir una atmosfera inflamable y el equipo electrico debe
tener un metodo de proteccion certificado. Se propone Zona 0 en interiores con vapor,
Zona 1 cerca de escapes primarios y Zona 2 en envolventes secundarias.

### 14. ¿Por que se dibuja 6 m alrededor de surtidores?

Es la envolvente horizontal aplicada desde las reglas de la Seccion 120 del CNE-U
para el caso academico. La altura, ventilacion y equipo final deben ser revisados por
un especialista antes de construir.

### 15. ¿Un IP66 sirve automaticamente en una zona peligrosa?

No. El IP protege contra ingreso de polvo/agua; no reemplaza el marcado y certificado
para atmosfera explosiva, grupo de gas y clase de temperatura.

### 16. ¿Que hace el paro de emergencia?

Desenergiza bombas y surtidores mediante circuitos de control, manteniendo alarma,
comunicaciones de emergencia y alumbrado seguro. Se proyecta accesible y fuera de la
envolvente peligrosa.

### 17. ¿Cual es el criterio de puesta a tierra?

Un anillo comun de cobre, ocho electrodos iniciales y equipotencialidad de tanques,
tuberias, surtidores, marquesina, tableros y grupo. Se diseña a 10 ohm y no debe
exceder 25 ohm, pero manda la medicion real.

### 18. ¿Por que no se dejan tierras separadas?

Porque potenciales distintos pueden producir chispas o tensiones peligrosas. PAT,
equipotencialidad, SPD y proteccion contra rayo deben coordinarse como un sistema.

### 19. ¿Se requiere pararrayos obligatoriamente?

El proyecto lo adopta por exposicion y criticidad, pero el diseño final depende del
analisis de riesgo IEC 62305, geometria, altura y datos del sitio.

### 20. ¿Por que hay SPD Tipo 1+2 y Tipo 2?

El Tipo 1+2 en TGE limita impulsos de origen atmosferico/conmutacion en la entrada;
los Tipo 2 aguas abajo protegen tableros sensibles. Deben coordinarse con distancia,
proteccion de respaldo y PAT.

### 21. ¿El grupo electrogeno es obligatorio para todo grifo?

No se afirma eso. Se adopta como criterio de continuidad para bombas seleccionadas,
control, caja, alarma, comunicaciones y alumbrado critico.

### 22. ¿Como se selecciono el grupo?

La carga critica permanente es 12.47 kVA. Con arranque secuencial de la mayor STP y
25 % de margen se requieren 27.69 kVA en sitio. Al corregir por 3830 m, el equipo debe
tener al menos 33.36 kVA de placa; se seleccionan 37.5 kVA standby.

### 23. ¿Por que el ATS es de cuatro polos?

Para conmutar tambien el neutro, evitar uniones no controladas entre fuentes y mantener
la separacion N/PE del esquema adoptado.

### 24. ¿Para que sirven las dos UPS?

La UPS-FUEL de 3 kVA mantiene cabezales y control de combustible; la UPS-IT de 2 kVA
mantiene POS, comunicaciones y CCTV. Separarlas evita que una falla de TI afecte el
control de combustible.

### 25. ¿Como se calculo la iluminacion?

Con el metodo de lumenes: flujo por numero de luminarias, factor de utilizacion y
mantenimiento dividido entre area. Las oficinas y minimarket se contrastan con
EM.010; marquesina/exterior usan criterios de ingenieria declarados.

### 26. ¿El calculo luminico ya es definitivo?

No. Cumple iluminancia media, pero faltan archivos IES/LDT, uniformidad, deslumbramiento,
alturas y reflectancias reales para una simulacion punto por punto.

### 27. ¿Que incluye el presupuesto?

La instalacion electrica representada: canalizaciones, conductores, tableros,
protecciones, alumbrado, dispositivos, PAT/rayo, respaldo, pruebas y entrega.

### 28. ¿Por que no incluye surtidores, STP ni tanques?

Porque son equipos del proceso de hidrocarburos y requieren proveedor/ficha definitiva.
El presupuesto electrico si incluye alimentacion, proteccion, control y equipotencialidad.

### 29. ¿El total S/ 394,665.70 es una cotizacion?

Es un presupuesto referencial con fecha base, gastos generales, utilidad e IGV;
no una cotizacion.
Antes de comprar se reemplazan estimaciones por proformas y se corrigen metrados de campo.

### 30. ¿Que falta para construir?

Factibilidad e Icc de Electro Puno, placas definitivas, levantamiento de campo,
resistividad/PAT, fotometria, cortocircuito-selectividad y revision/firma de un
profesional competente, especialmente para areas clasificadas.

## Respuestas que no deben darse

- No decir que la DREM aprobo el proyecto; solo facilito documentos de referencia.
- No decir que 25 kA, 50 kVA, 10 ohm o el grupo son datos observados; son criterios
  calculados/adoptados sujetos a verificacion.
- No decir que IP65/IP66 equivale a equipo a prueba de explosion.
- No afirmar que GLP o GNV forman parte del establecimiento diseñado.
- No presentar el presupuesto referencial como cotizacion o costo de obra definitivo.
