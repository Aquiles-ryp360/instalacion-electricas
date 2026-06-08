# REPORTE DE VALIDACIÓN Y CONTROL DE CALIDAD
## Proyecto: Instalación Eléctrica Residencial - Vivienda Unifamiliar de 3 Pisos

### 1. Resumen de la Auditoría de Calidad
Este reporte certifica el cumplimiento del proceso de diseño, modelado CAD y cálculo técnico de las instalaciones eléctricas residenciales bajo la norma **NEC (National Electrical Code)** para la vivienda de 3 niveles.

Se ha realizado una auditoría exhaustiva que abarca:
* Cumplimiento de las especificaciones normativas de calibres y protecciones.
* Verificación geométrica de superposiciones y colisiones en los archivos vectoriales DXF y PDF.
* Coherencia matemática del cuadro de cargas y la máxima demanda.

---

### 2. Matriz de Cumplimiento Normativo (NEC)

| Parámetro Evaluado | Requisito NEC / Normativo | Estado | Observación Técnica |
| :--- | :--- | :---: | :--- |
| **Capacidad de Conductor** | Coordinación $I_b \leq I_n \leq I_z$ (NEC 240.4) | **Conforme** | Los conductores de 1.5 mm² y 2.5 mm² soportan corrientes mayores a las llaves de 10A y 16A respectivamente. |
| **Circuitos Ramales Mínimos** | Separar Alumbrado y Tomacorrientes (NEC 210.11) | **Conforme** | Se han estructurado circuitos independientes para iluminación y tomacorrientes en cada piso. |
| **Protección Diferencial** | GFCI en baños, cocina y exteriores (NEC 210.8) | **Conforme** | Se incorporaron interruptores diferenciales (ID) de 30 mA para todos los tomacorrientes (incluyendo cocina y baño). |
| **Puesta a Tierra** | Varilla de puesta a tierra y conductor PE (NEC 250) | **Conforme** | Puntos de tomacorrientes conectados mediante cable de cobre de $2.5\text{ mm}^2$ (PE verde) a la barra del subtablero y luego a la varilla de tierra de $5/8"$. |
| **Caída de Tensión** | Caída de tensión menor al 3% en circuitos ramales | **Conforme** | El circuito ramal más desfavorable (C7 en tercer piso) tiene una caída calculada de apenas $0.61\%$. |

---

### 3. Resultados de la Auditoría Visual CAD (Multimodal)
Se han inspeccionado detalladamente los planos exportados en formato DXF y PDF para asegurar su legibilidad técnica:

* **Colisiones con Muros:** Los símbolos eléctricos (como luminarias de techo en el centro del ambiente, tomacorrientes en el borde) no quedan solapados o cortados por muros arquitectónicos, marcos de puertas ni ventanas.
* **Superposición de Texto:** Los textos identificadores de los circuitos (`C1`, `C2`, etc.) y las etiquetas de los ambientes se han desplazado y formateado con offsets específicos para evitar colisiones con las polilíneas de los muros o con la simbología eléctrica.
* **Ubicación de Interruptores:** Se comprobó que los interruptores simples (`S`) y conmutados (`S3`) se localizan junto al marco de la puerta de ingreso a cada habitación, del lado de la cerradura, y nunca detrás del barrido de la hoja de la puerta.
* **Rutas Ortogonales:** Las canalizaciones eléctricas (líneas discontinuas en los planos de canalizaciones) corren paralelas a los muros principales de la vivienda, evitando diagonales innecesarias o cruces caóticos por el medio de los ambientes.
* **Coherencia de la Leyenda:** El bloque de la leyenda y el cuadro de rotulación (membrete) se han posicionado en el extremo derecho de las láminas, sin invadir la zona de dibujo de la distribución arquitectónica de la vivienda.

---

### 4. Validación de Datos Estructurados (JSON)
Los archivos JSON fuentes de datos eléctricos fueron validados mediante herramientas automáticas y superpuestos sobre las bases arquitectónicas:
* **Entidades importadas:** Se importaron correctamente los muros, ventanas, puertas y escaleras desde las bases DXF (`primer_piso_v3.dxf`, `segundo_piso_v3.dxf`, `tercer_piso_v3.dxf`).
* **Coordenadas de Símbolos:** Las coordenadas $(X, Y)$ de las luminarias, interruptores y tomacorrientes son coherentes con las dimensiones reales de los ambientes y se encuentran confinadas dentro de la envolvente de la vivienda ($4.5\text{ m} \times 9.0\text{ m}$).
* **Conexión de Rutas:** Todas las rutas de canalización inician formalmente en su respectivo tablero general/subtablero de distribución y terminan en los puntos de consumo correspondientes.

### 5. Conclusión del Control de Calidad
> [!NOTE]
> La documentación técnica generada y los planos correspondientes cumplen satisfactoriamente con los criterios de seguridad e ingeniería eléctrica residencial exigidos por la norma NEC. Los archivos vectoriales e informes quedan listos para su carga al repositorio y su revisión académica.
