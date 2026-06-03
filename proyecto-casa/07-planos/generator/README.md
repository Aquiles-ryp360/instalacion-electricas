# Generador de Planos Arquitectónicos 2D a DXF

Este módulo permite generar automáticamente planos arquitectónicos 2D básicos (distribución de ambientes, muros, puertas, ventanas, cotas y marco/cajetín de datos) a partir de un archivo de datos estructurado en formato JSON.

El objetivo es contar con un flujo de trabajo local en Linux, ágil y programable, para bosquejar distribuciones antes del diseño final o exportación en CAD profesional.

---

## 🛠️ Requisitos e Instalación

El generador está escrito en **Python 3** y requiere la librería `ezdxf` para la manipulación y escritura de archivos DXF.

1. **Crear y activar el entorno virtual de Python** (opcional pero recomendado):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Instalar dependencias**:
   ```bash
   pip install ezdxf
   ```

---

## 📂 Estructura de Archivos del Módulo

* [layout_example.json](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/proyecto-casa/07-planos/generator/layout_example.json): Archivo JSON de ejemplo con las dimensiones, ambientes, puertas y ventanas de la vivienda.
* [dxf_generator.py](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/proyecto-casa/07-planos/generator/dxf_generator.py): Script de Python que valida el diseño, procesa el JSON y escribe el plano final en formato DXF.

---

## 🚀 Uso del Generador

Puedes ejecutar el generador de la siguiente manera:

```bash
# Con el entorno virtual activo
python3 proyecto-casa/07-planos/generator/dxf_generator.py --input proyecto-casa/07-planos/generator/layout_example.json --output proyecto-casa/07-planos/IE-01-ubicacion-arquitectura.dxf
```

Esto generará el archivo `IE-01-ubicacion-arquitectura.dxf` en el directorio de planos del proyecto.

---

## 📐 Estructura de Datos (JSON)

El archivo JSON de entrada debe seguir la siguiente estructura:

* **`dimensions`**: Bounding box o límites generales de la vivienda (`width` y `height` en metros).
* **`rooms`**: Lista de ambientes. Cada ambiente requiere:
  - `name`: Nombre descriptivo (e.g. "SALA", "COCINA").
  - `x`, `y`: Coordenada de inicio (esquina inferior izquierda) en metros.
  - `width`, `height`: Dimensiones en metros.
* **`doors`**: Lista de puertas. Cada puerta requiere:
  - `x`, `y`: Ubicación de la bisagra/punto de origen.
  - `width`: Ancho de la hoja (puerta) en metros.
  - `orientation`: `"horizontal"` o `"vertical"` en alineación con el muro.
  - `swing`: Dirección del giro (`"top-right"`, `"top-left"`, `"bottom-right"`, `"bottom-left"`).
* **`windows`**: Lista de ventanas. Cada ventana requiere:
  - `x`, `y`: Punto de inicio.
  - `width`: Ancho de la ventana.
  - `orientation`: `"horizontal"` o `"vertical"`.

---

## 🎨 Capas CAD Generadas

El archivo DXF se genera con capas lógicas ordenadas para facilitar la edición posterior en aplicaciones como QCAD o LibreCAD:

1. **`MUROS`** (Color Blanco/Negro, grosor 0.35 mm): Representa todos los contornos de ambientes y muros divisorios. Evita duplicaciones de líneas en paredes contiguas.
2. **`PUERTAS`** (Color Rojo): Representa el panel de la puerta en posición abierta y la trayectoria curva (arco de giro) del abatimiento.
3. **`VENTANAS`** (Color Cian): Representa las ventanas detalladas como marcos estrechos con una línea intermedia (vidrio).
4. **`TEXTOS`** (Color Amarillo): Contiene los nombres de los ambientes y sus dimensiones en metros, centrados de forma automática en cada habitación.
5. **`COTAS`** (Color Gris): Contiene las líneas de cota exterior principal con marcas oblicuas (ticks) y medidas automáticas.
6. **`MARCO`** (Color Blanco/Negro, grosor 0.50 mm): Dibuja un marco perimetral con un cajetín técnico en la esquina inferior derecha con los datos del proyecto, dibujante (estudiante), escala y fecha.

---

## 🖥️ Apertura en QCAD / LibreCAD en Linux

Una vez generado el archivo DXF, puedes abrirlo con tu software CAD preferido:

```bash
qcad proyecto-casa/07-planos/IE-01-ubicacion-arquitectura.dxf
# o bien
librecad proyecto-casa/07-planos/IE-01-ubicacion-arquitectura.dxf
```

Desde el software podrás:
- Apagar/encender capas para aislar elementos (por ejemplo, ocultar cotas o textos).
- Cambiar los colores de visualización o los grosores de línea si deseas imprimirlos.
- Convertir o guardar como `.dwg` si es necesario para exportar a AutoCAD.
- Utilizar las líneas base generadas para diseñar sobre ellas los circuitos eléctricos (alumbrado y tomacorrientes) de las fases posteriores.

---

## ⚠️ Advertencia Técnica

Este generador es una herramienta de asistencia académica y de prototipado rápido. Los planos generados representan distribuciones funcionales y de volumetría preliminar para diagramación de circuitos, y **no constituyen planos de ejecución ni expedientes de obra firmados**.
