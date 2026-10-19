# 2. Bases de diseño y memorias de cálculo

## 2.1 Marco técnico a comprobar

La [R.M. 0214-2011-MEM](https://www.gob.pe/institucion/minem/normas-legales/108753-0214-2011-mem) aprobó el Código Nacional de Electricidad - Suministro 2011. La [R.D. 018-2003-EM/DGE](https://www.gob.pe/institucion/minem/normas-legales/4775002-018-2003-em-dge) aprobó bases para diseño de líneas y redes primarias **dentro de su ámbito de electrificación rural**. La [R.D. 030-2003-EM/DGE](https://www.gob.pe/institucion/minem/normas-legales/4775130-030-2003-em-dge) aborda levantamientos topográficos rurales. Estas páginas identifican documentos oficiales; antes de aprobar ingeniería deben verificarse edición aplicable, modificatorias, reglas concretas y ámbito jurídico del proyecto. No se declara cumplimiento.

## 2.2 Parámetros de entrada y bloqueo de resultados

| Grupo | Entradas indispensables pendientes | Resultado que depende de ellas |
|---|---|---|
| Operación | Tensión y fases reales, unifilar, impedancia aguas arriba, protecciones, historial de carga | Modelo de red y punto de conexión |
| Demanda | Usuarios, potencias, simultaneidad, crecimiento y factor de potencia | Corriente, caída de tensión y potencia de transformación |
| Conductor y equipos | Material/sección existentes, temperatura, resistencia/reactancia, ampacidad, estado y fichas | Capacidad térmica, pérdidas y protección |
| Topografía | Eje medido, progresivas, cotas de apoyo y terreno, cruces, obstáculos | Vanos, flecha, gálibos y emplazamiento |
| Mecánica/geotecnia | Conductor, tracción, viento, temperatura, hielo según zona, postes, cimentación y suelo | Tensiones, cargas, fundación y seguridad |
| Seguridad | Neutro, corrientes de falla, resistividad, equipos y partes accesibles | Puesta a tierra y tensiones de contacto/paso |

El archivo `datos/parametros_diseno_pendientes.json` guarda estas entradas como `null`. No se reemplazan por un número escogido solo para completar tablas.

## 2.3 Memoria eléctrica: procedimiento pendiente

1. Validar unifilar, tensión nominal por tramo, nivel de cortocircuito y transformadores asociados con el titular. Modelar red real y cargas por nodo.
2. Para carga trifásica equilibrada conocida, calcular corriente con `I = S / (sqrt(3) · V_LL)`, cuidando que `S` esté en VA y `V_LL` en V. Para alimentador con cargas distribuidas, resolver flujo de potencia por secciones; una carga total ficticia en el extremo no sustituye el modelo.
3. Evaluar caída de tensión, pérdidas y capacidad térmica con impedancias y temperatura del conductor **medidos o documentados**. El límite admisible debe tomarse de la norma y condiciones de conexión que correspondan.
4. Calcular niveles de falla mínimo y máximo, capacidad interruptiva y coordinación de protecciones a partir del estudio del operador.
5. Verificar aislamiento, sobretensiones y selección de equipos con tensión, altitud, contaminación y exposición medidas. La cota SRTM sirve solo para identificar la necesidad de este estudio.

**Resultados del corredor:** corriente `null`; caída de tensión `null`; pérdidas `null`; cortocircuito `null`; coordinación `pendiente`. No se asignan conductor, transformador ni protección hasta disponer de demanda y condiciones de diseño confirmadas.

## 2.4 Memoria mecánica: procedimiento pendiente

1. Levantar posiciones y cotas reales de cada apoyo existente, vanos, cambios de dirección y cruces.
2. Identificar material y ficha del conductor, carga de rotura, masa, módulo elástico y coeficiente de dilatación.
3. Definir hipótesis ambientales y combinaciones de carga conforme a norma aplicable y emplazamiento real; confirmar con información climática y operador.
4. Resolver estados de tensión y flecha por cantón y caso crítico; verificar cargas en herrajes, estructuras, retenidas y cimentaciones.
5. Comprobar distancias de seguridad en cada cruce con perfil levantado. El perfil SRTM y la polilínea GISEM no tienen precisión ni información suficiente para ese control.

**Resultados mecánicos:** número de apoyos nuevos `null`; vanos `null`; flecha máxima `null`; tensión mecánica `null`; gálibo mínimo `null`. No se deben insertar catenarias en CL-02 hasta obtener topografía y sistema de apoyos.

## 2.5 Puesta a tierra y subestaciones

No se propone subestación ni PAT sin comprobar si hay instalación nueva, conocer el esquema de neutro y fallas, medir resistividad y determinar requisitos de seguridad de personas y equipos. El diseño de electrodos, medición de resistencia y verificación de tensiones de contacto/paso corresponden a la ingeniería de detalle. **Resistencia objetivo y número de electrodos: por definir.**

## 2.6 Verificación independiente

La longitud geométrica se recalculó sumando los 27 tramos proyectados a UTM 19S y se contrastó con la polilínea de ruta. El cuadro CSV conserva los cálculos por tramo y el reporte CAD registra SHA-256 de las entradas. Esta verificación controla la geometría digital, **no** verifica una magnitud eléctrica o mecánica.
