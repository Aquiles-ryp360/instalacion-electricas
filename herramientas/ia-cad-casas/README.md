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

## 4. Estructura de Datos y Flujo de Croquis
* **Dónde colocar futuros croquis/imágenes**: Los bocetos hechos a mano, fotos de medidas o planos del catastro deben guardarse en la carpeta [input/](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/proyecto-casa/00-herramientas/ia-cad-casas/input/).
* **Dónde colocar datos estructurados**: Las medidas interpretadas de las habitaciones en metros, puertas y ventanas se escriben en [data/layout_example.json](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/proyecto-casa/00-herramientas/ia-cad-casas/data/layout_example.json).

---

## 5. ¿Cómo se genera el archivo DXF y PDF?
Desde la raíz del repositorio, simplemente ejecuta el comando automatizado:

```bash
./generar_plano.sh
```

Este script:
1. Activa el entorno virtual de Python local.
2. Instala la librería `ezdxf` si no está presente.
3. Llama a `scripts/dxf_generator.py` para procesar el JSON y generar el archivo DXF.
4. Llama a QCAD en modo headless (`-no-gui -platform offscreen`) para ejecutar `cad-scripts/dxf2pdf.js`, el cual abre el DXF, auto-ajusta el dibujo a una hoja A4 horizontal y lo exporta a PDF.

Los archivos generados se guardan en la carpeta [output/](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/proyecto-casa/00-herramientas/ia-cad-casas/output/).

---

## 6. Apertura y Edición en QCAD
Para abrir el plano DXF generado en la interfaz gráfica de QCAD, ejecuta en tu terminal:

```bash
qcad proyecto-casa/00-herramientas/ia-cad-casas/output/plan_distribucion.dxf
```
Desde QCAD podrás usar comandos avanzados de edición, configurar el orden de capas o añadir simbología eléctrica.

## 7. Apertura y Validación en LibreCAD
LibreCAD es una alternativa muy ligera para abrir y validar el dibujo DXF:

```bash
librecad proyecto-casa/00-herramientas/ia-cad-casas/output/plan_distribucion.dxf
```
Es ideal como visor y validador rápido de que los bloques y capas se exportaron con los colores y coordenadas correctas.

---

## 8. Arquitectura Técnica del Módulo

### Qué hace Python:
* **Lectura e interpretación**: Carga y procesa el archivo JSON en `data/`.
* **Validación**: Comprueba que los ambientes no contengan datos inválidos o falten campos requeridos.
* **Escritura DXF**: Usa `ezdxf` para estructurar el archivo vectorial organizándolo en capas (`MUROS`, `PUERTAS`, `VENTANAS`, `TEXTOS`, `COTAS`, `MARCO`).
* **Orquestación**: Llama a los procesos secundarios del sistema (QCAD) a través de scripts de bash.

### Qué hace QCAD:
* **Motor CAD de Renderizado**: QCAD actúa como el motor que procesa las entidades del DXF y calcula los límites matemáticos del plano (`getBoundingBox`).
* **Auto-Ajuste y Auto-Centrado**: El script `cad-scripts/dxf2pdf.js` realiza las transformaciones espaciales para centrar el plano en una hoja A4 y asignarle escala.
* **Generación de PDF**: Exporta el plano final en formato PDF vectorial conservando capas y grosores de línea.

---

## 9. ¿Por qué DXF es el formato maestro inicial?
* **Compatibilidad Universal**: DXF (Drawing Exchange Format) es un estándar abierto que se puede leer en QCAD, LibreCAD, AutoCAD, Revit, SolidWorks y cualquier otro software CAD.
* **Manipulación por código**: Es un formato de texto ASCII fácil de analizar, escribir y validar mediante librerías de programación, al contrario del formato binario cerrado de `.dwg`.

---

## 10. Cómo mover un plano generado al informe o entregables finales
La carpeta de desarrollo de la herramienta es `proyecto-casa/00-herramientas/ia-cad-casas/`. Cuando generes un plano útil para tu avance académico y desees que forme parte de los entregables del informe, debes copiarlo al directorio final:

```bash
# Copiar el archivo DXF final
cp proyecto-casa/00-herramientas/ia-cad-casas/output/plan_distribucion.dxf proyecto-casa/07-planos/IE-01-ubicacion-arquitectura.dxf

# Copiar el PDF final generado por QCAD
cp proyecto-casa/00-herramientas/ia-cad-casas/output/plan_distribucion.pdf proyecto-casa/07-planos/IE-01-ubicacion-arquitectura.pdf
```

Esto mantiene la separación limpia: el código vive en `00-herramientas/`, y el material definitivo del informe académico se almacena en `07-planos/`.

---

## 11. Futuro y Segunda Fase (Lo que no se incluye aún)
* **IA/OCR**: Lectura automatizada de bocetos escaneados mediante reconocimiento de bordes o LLM (se implementará en la siguiente fase).
* **Esquemas Eléctricos**: Dibujo automatizado de puntos de luz, tomacorrientes e interruptores sobre el plano de distribución base.
* **DWG Nativo**: Exportación o guardado automático directo en DWG desde la consola.
