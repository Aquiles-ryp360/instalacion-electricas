# Revisión v2: Corrección de Proporciones y Dibujo Gráfico

## 1. Ajustes de Proporciones (Arquitectura)
- **Escalera:** Se redujo el ancho de la caja de escalera de **3.0m a 2.4m**, espacio óptimo para una escalera residencial de dos tramos en U (1.10m por tramo + 0.20m de ojo central).
- **Cocina grande:** Se expandió el ancho de **3.0m a 3.6m**, ganando espacio para encimeras y áreas de trabajo que cumplan con la iluminación mínima del RNE.
- **Baño:** Se redujo el ancho de **3.0m a 2.4m** (2.4m x 3.0m), lo que representa un baño familiar amplio y optimizado.
- **Cuarto con cama 2 (Dormitorio Principal):** Se expandió el ancho de **6.0m a 6.6m** (6.6m x 3.0m), aprovechando el espacio recuperado del baño.

## 2. Mejoras del Motor CAD (`dxf_generator.py`)
- **Muros de Doble Línea:** El motor ahora genera muros con doble trazo de espesor **0.15m (15 cm)**, separando las caras interna y externa. Esto le da una presencia gráfica idéntica a la plantilla de referencia visual (`prefabricadascasasdemadera_com.jpg`).
- **Dibujo de Peldaños de Escalera:** Si una habitación contiene el término `"escalera"` en su nombre, el motor dibuja automáticamente:
  - Un descanso de 1.2m al fondo.
  - El ojo central divisor de los dos tramos.
  - Los 9 peldaños o huellas horizontales de subida y bajada.
- **Evitación de Colisión de Textos:** En las escaleras, las etiquetas de texto del nombre y la cota de la habitación se desplazan de manera automatizada al área del descanso, evitando dibujarse encima de los peldaños.

## 3. Salidas Generadas
- **JSON de Entrada:** [layout_aquiles_v2.json](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/layouts/layout_aquiles_v2.json)
- **DXF de Salida:** [croquis_aquiles_v2.dxf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v2.dxf)
- **PDF Exportado:** [croquis_aquiles_v2.pdf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v2.pdf)
