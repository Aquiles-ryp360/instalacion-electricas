# Módulo IA-CAD-Casas: Generador Automático de Planos 2D

Módulo local para Linux para la modelación y generación automática de planos arquitectónicos 2D en formato DXF a partir de datos estructurados, con soporte para renderizado automático a PDF utilizando QCAD.

---

## 1. ¿Qué es `ia-cad-casas`?
Es un conjunto de herramientas y scripts integrados que enlazan código de Python con los motores de automatización de QCAD y LibreCAD. Permite describir la geometría y los componentes de una casa en un archivo legible (JSON) y transformarlos automáticamente en un plano CAD vectorial.

## 2. ¿Para qué sirve?
Sirve para simplificar la creación de planos de distribución arquitectónica (distribución de cuartos, muros, puertas, ventanas, cotas y membretes) sin necesidad de dibujarlos manualmente línea por línea. El plano generado sirve como base limpia y calibrada en metros para el posterior diseño de circuitos eléctricos.

## 3. ¿Qué problema resuelve?
* **Evita el dibujo manual repetitivo**: El estudiante o diseñador no tiene que trazar rectángulos, rotar hojas de puertas, dibujar paralelas para ventanas o escribir etiquetas centrándolas manualmente.
* **Consistencia de datos**: Garantiza que las cotas y el membrete del plano coincidan exactamente con la base de datos del proyecto.
* **Headless CAD**: Resuelve la necesidad de contar con AutoCAD o software pesado mediante herramientas nativas, gratuitas y de código abierto en Linux que se ejecutan directamente en segundo plano.

---

## 4. Estructura de Datos y Flujo de Trabajo
* **Carpeta de la Herramienta:** `herramientas/ia-cad-casas/`
* **Datos de Ejemplo:** [data/layout_example.json](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/ia-cad-casas/data/layout_example.json)
* **Script Generador Python:** [scripts/dxf_generator.py](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/ia-cad-casas/scripts/dxf_generator.py)
* **Script de Renderizado JS (QCAD):** [cad-scripts/dxf2pdf.js](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/ia-cad-casas/cad-scripts/dxf2pdf.js)
* **Salidas de Ejemplo:** [output/](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/ia-cad-casas/output/)

---

## 5. ¿Cómo se genera el archivo DXF y PDF?
El script `generar_plano.sh` es ahora un lanzador portátil y paramétrico. Puedes llamarlo desde cualquier directorio (incluyendo la raíz del repositorio):

### Ejecución con valores por defecto (Ejemplo)
```bash
./herramientas/ia-cad-casas/generar_plano.sh
```
Esto tomará el layout de ejemplo y guardará `plan_distribucion.dxf` y `plan_distribucion.pdf` en la carpeta `output/` del módulo.

### Ejecución con parámetros personalizados (Caso de Estudio)
Puedes pasarle un JSON de entrada y rutas de salida personalizadas:
```bash
./herramientas/ia-cad-casas/generar_plano.sh \
  Avanze-Proyecto-Aquiles/trabajo-cad-casa/layouts/layout_aquiles_v3.json \
  Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v3.dxf \
  Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v3.pdf
```

El script se encarga automáticamente de:
1. Activar el entorno virtual de Python local.
2. Instalar la librería `ezdxf` si no está presente en el entorno virtual.
3. Llamar a `scripts/dxf_generator.py` para procesar el JSON y escribir el archivo DXF.
4. Invocar QCAD en modo headless (`-no-gui -platform offscreen`) para ejecutar `cad-scripts/dxf2pdf.js`, el cual abre el DXF, auto-ajusta el dibujo a una hoja A4 horizontal y lo exporta a PDF vectorial.

---

## 6. Apertura y Edición en QCAD
Para abrir el plano DXF generado en la interfaz gráfica de QCAD, ejecuta en tu terminal:

```bash
qcad herramientas/ia-cad-casas/output/plan_distribucion.dxf
```
Desde QCAD podrás usar comandos avanzados de edición, configurar el orden de capas o añadir simbología eléctrica.

## 7. Apertura y Validación en LibreCAD
LibreCAD es una alternativa muy ligera para abrir y validar el dibujo DXF:

```bash
librecad herramientas/ia-cad-casas/output/plan_distribucion.dxf
```
Es ideal como visor y validador rápido de que los bloques y capas se exportaron con los colores y coordenadas correctas.

---

## 8. Superposicion electrica sobre una planta existente

El script `scripts/electrical_overlay.py` agrega simbologia electrica preliminar sobre un DXF arquitectonico ya generado. Esta pensado para casos como Aquiles, donde primero se corrige la planta arquitectonica y luego se colocan luminarias, interruptores, tomacorrientes, tablero, medidor, circuitos y leyenda.

Ejemplo:

```bash
herramientas/ia-cad-casas/.venv/bin/python \
  herramientas/ia-cad-casas/scripts/electrical_overlay.py \
  --base Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso1_v3.dxf \
  --electrical Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/data/electrico_piso1_v1.json \
  --output Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v1.dxf
```

El JSON electrico puede incluir `luminarias`, `interruptores`, `tomacorrientes`, `tableros`, `medidores`, `equipos`, `rutas`, `legend`, `circuit_summary` y `notes`. El script remapea las capas arquitectonicas a `ARQ_*` y agrega capas `ELEC_*` para mantener el DXF editable en QCAD/LibreCAD.

Para exportar el PDF se usa el mismo script QCAD:

```bash
qcad -no-gui -platform offscreen -quit \
  -autostart "$(realpath herramientas/ia-cad-casas/cad-scripts/dxf2pdf.js)" \
  -input "$(realpath Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v1.dxf)" \
  -output "$(realpath Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v1.pdf)"
```

Nota: `cad-scripts/dxf2pdf.js` fija una pagina A4 horizontal real y centra el dibujo con QCAD.

---

## 9. Arquitectura Técnica del Módulo

### Qué hace Python:
* **Lectura e interpretación**: Carga y procesa el archivo JSON de entrada.
* **Validación**: Comprueba que los ambientes no contengan datos inválidos o falten campos requeridos.
* **Muros de Doble Línea**: Genera automáticamente muros de doble trazo de espesor **0.15m (15 cm)**.
* **Muros manuales opcionales**: Permite desactivar los muros derivados de ambientes con `draw_room_walls: false` y dibujar segmentos explícitos en `walls`.
* **Generación de Escaleras**: Detecta habitaciones con la palabra `"escalera"` en su nombre y dibuja automáticamente los peldaños de subida/bajada y el descanso superior de 1.20m.
* **Elementos de apoyo visual**: Soporta `hatches`, `fixtures`, `texts` y `custom_dimensions` para tramas, mobiliario básico, notas y cotas adicionales.
* **Escritura DXF**: Usa `ezdxf` para estructurar el archivo vectorial organizándolo en capas (`MUROS`, `PUERTAS`, `VENTANAS`, `TEXTOS`, `COTAS`, `MARCO`).

### Qué hace QCAD:
* **Motor CAD de Renderizado**: QCAD actúa como el motor que procesa las entidades del DXF y calcula los límites matemáticos del plano (`getBoundingBox`).
* **Auto-Ajuste y Auto-Centrado**: El script `cad-scripts/dxf2pdf.js` realiza las transformaciones espaciales para centrar el plano en una hoja A4 y asignarle escala.
* **Generación de PDF**: Exporta el plano final en formato PDF vectorial conservando capas y grosores de línea.

---

## 10. Cómo mover un plano generado al informe o entregables finales
La carpeta de desarrollo de la herramienta es `herramientas/ia-cad-casas/`. Cuando generes un plano útil para tu avance académico y desees que forme parte de los entregables del informe, debes copiarlo al directorio final:

```bash
# Copiar el archivo DXF final
cp Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v3.dxf proyecto-casa/07-planos/IE-01-ubicacion-arquitectura.dxf

# Copiar el PDF final generado por QCAD
cp Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/croquis_aquiles_v3.pdf proyecto-casa/07-planos/IE-01-ubicacion-arquitectura.pdf
```

Esto mantiene la separación limpia: el código vive en `herramientas/`, y el material definitivo del informe académico se almacena en `proyecto-casa/07-planos/`.

---

## 11. Campos JSON adicionales

El formato base sigue siendo compatible con `dimensions`, `rooms`, `doors`, `windows` y `stairs`. Para croquis reales con contornos no rectangulares o huecos de puertas, se agregaron campos opcionales:

```json
{
  "draw_room_walls": false,
  "show_room_dimensions": false,
  "show_title_block": false,
  "wall_thickness": 0.15,
  "walls": [
    {"x1": 0.0, "y1": 0.0, "x2": 4.0, "y2": 0.0}
  ],
  "hatches": [
    {"x": 0.0, "y": 0.0, "width": 2.0, "height": 3.0, "spacing": 0.30}
  ],
  "fixtures": [
    {"type": "bed", "x": 1.0, "y": 1.0, "width": 1.0, "height": 2.0}
  ],
  "texts": [
    {"text": "AREA S/C", "x": 1.5, "y": 2.0, "height": 0.18}
  ],
  "custom_dimensions": [
    {"start": [0.0, 0.0], "end": [4.0, 0.0], "offset": -0.8, "label": "4.00 m", "direction": "horizontal"}
  ]
}
```

Uso recomendado:

- Usar `rooms` para etiquetas y proporciones.
- Usar `walls` cuando el croquis tenga forma en L, vacíos o puertas que deban quedar abiertas.
- Usar `hatches` solo para zonas rayadas o sin confirmar del croquis.
- Usar `fixtures` como apoyo visual arquitectónico, no para instalaciones eléctricas.
- Desactivar `show_title_block` si el cajetín se superpone con la planta en croquis de borde completo.
