# Zona de Trabajo CAD: Vivienda de Aquiles (Segundo Piso)

Esta carpeta contiene el espacio de trabajo específico para el diseño y la modelación CAD 2D de la vivienda unifamiliar de Aquiles Taylor Ramos Yapo, separada del motor genérico de generación.

---

## 1. Fuentes de Entrada Utilizadas

### Croquis Real de la Vivienda
- **Imagen Base:** [20260602_195759.jpg.jpeg](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/Full-Imagenes/Croquis-de-plano de la casa/20260602_195759.jpg.jpeg)
- **Descripción:** Dibujo a mano alzada en cuaderno cuadriculado que representa la distribución del Segundo Piso (Piso 2) de la casa.
- **Plantilla de Referencia Estética (No de Distribución):** [prefabricadascasasdemadera_com.jpg](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/Full-Imagenes/Plantillas-como-deve-verse-el-cad/prefabricadascasasdemadera_com.jpg) (usada para calificar grosores de muros, puertas y representación de ventanas).

---

## 2. Interpretación de Medidas y Supuestos

- **Cuadrícula del Cuaderno:** Se identificó que cada celda del cuaderno en el croquis equivale a **0.75 metros**.
- **Dimensiones Exteriores:** El segundo piso mide **15.00 m de ancho** por **9.00 m de alto**.
- **Muros (Espesor):** En el croquis se dibujan como líneas simples. En el plano CAD (desde v2) se asume un espesor estándar de **0.15 m** (muro de ladrillo tarrajeado) con representación de doble línea, según la plantilla estética.
- **Escalera:** El croquis muestra un espacio de 4 cuadrículas (3.0m) para la escalera. Se asume que es una **escalera tipo U** de dos tramos simétricos con un descanso (desembarque) de 1.20m al fondo y llegada al Pasadizo a nivel de Y=4.5m. En el plano se redujo su ancho a **2.40 m** para que sea realista.
- **Cocina grande:** Se asume un ancho de **3.60 m** en Y=4.5m para albergar adecuadamente las cargas de la cocina (microondas, waflera, cocina, refrigeradora).
- **Zonas Libres:** El área del primer piso en el extremo inferior izquierdo es un patio/jardín abierto, por lo que el espacio homólogo en el segundo piso se representa vacío (vacío sobre patio).

---

## 3. Zonas Dudosas o Pendientes de Confirmar
1. **Medidas Reales de los Ambientes:** Como las dimensiones se obtuvieron contando cuadrículas de un dibujo manual, las distancias exactas deben validarse en la vivienda con una cinta métrica o distanciómetro láser.
2. **Puntos Eléctricos:** Este plano representa la arquitectura limpia. En la siguiente fase se debe incorporar la ubicación del Tablero de Distribución y el trazado de los circuitos de Alumbrado y Tomacorrientes.
3. **Ubicación del Medidor y Acometida:** Se debe verificar si el medidor exterior de Electro Puno se empotrará en muro propio o en murete.

---

## 4. Archivos de Trabajo y Resultados

### JSON de Entrada (Estructura de Datos)
- **v1 (Directo de croquis):** [layouts/layout_aquiles_v1.json](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/layouts/layout_aquiles_v1.json)
- **v2 (Proporciones refinadas):** [layouts/layout_aquiles_v2.json](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/layouts/layout_aquiles_v2.json)
- **v3 (Pulido final - Vigente):** [layouts/layout_aquiles_v3.json](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/layouts/layout_aquiles_v3.json)

### Salidas Generadas (CAD y PDF)
- **Planos DXF (Editables en QCAD/LibreCAD):**
  - [salidas/croquis_aquiles_v1.dxf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v1.dxf)
  - [salidas/croquis_aquiles_v2.dxf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v2.dxf)
  - **[Vigente]** [salidas/croquis_aquiles_v3.dxf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v3.dxf)
- **Renderizados en PDF (Imprimibles A4):**
  - [salidas/croquis_aquiles_v1.pdf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v1.pdf)
  - [salidas/croquis_aquiles_v2.pdf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v2.pdf)
  - **[Vigente]** [salidas/croquis_aquiles_v3.pdf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v3.pdf)

---

## 5. Instrucciones para Ejecutar y Editar

### Cómo Regenerar las Salidas
Para compilar un layout específico desde la raíz del repositorio, utiliza el entorno virtual del motor de la siguiente manera:

```bash
# 1. Activar el entorno virtual
source herramientas/ia-cad-casas/.venv/bin/activate

# 2. Ejecutar la generación DXF (ejemplo para v3)
python herramientas/ia-cad-casas/scripts/dxf_generator.py \
  --input Avanze-Proyecto-Aquiles/trabajo-cad-casa/layouts/layout_aquiles_v3.json \
  --output Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v3.dxf

# 3. Exportar a PDF usando QCAD headless
qcad -no-gui -platform offscreen -quit \
  -autostart $(realpath herramientas/ia-cad-casas/cad-scripts/dxf2pdf.js) \
  -input $(realpath Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v3.dxf) \
  -output $(realpath Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v3.pdf)
```

### Cómo abrir los planos para su edición
- **QCAD:** Abre el plano directamente con:
  ```bash
  qcad Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v3.dxf
  ```
- **LibreCAD:** Abre el plano directamente con:
  ```bash
  librecad Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v3.dxf
  ```
