# Guía de Simbología Eléctrica e Instrucciones de Diseño para Asistentes de IA

Este directorio contiene las especificaciones y lineamientos técnicos para la modelación y generación automática de planos de instalaciones eléctricas domiciliarias. Está diseñado para guiar a cualquier Inteligencia Artificial que asista en el diseño o auditoría de planos eléctricos del proyecto.

> [!IMPORTANT]
> Todos los planos generados por la IA en este repositorio deben apegarse estrictamente a la simbología gráfica y las reglas lógicas detalladas a continuación, utilizando la extensión de datos estructurada `.json` para compilarse a planos vectoriales `.dxf` y archivos de renderizado `.pdf`.

---

## 📂 Archivos de Simbología y Datos

* **Especificación JSON de Símbolos:** [simbologia_ia.json](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/simbologia-ia/simbologia_ia.json) (Define la biblioteca estándar de símbolos, claves JSON y capas de AutoCAD/QCAD).
* **Biblioteca Vectorial de la Norma DGE:** [simbologia_normativa_dge.json](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/simbologia-ia/simbologia_normativa_dge.json) (Contiene la definición geométrica vectorial paramétrica de más de 30 símbolos extraídos de la Sección 9 del CNE/DGE para dibujar mediante primitivas CAD).
* **Compilador 1 (Proyecto Aquiles):** [electrical_overlay.py](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/ia-cad-casas/scripts/electrical_overlay.py) (Procesa plano individual por archivo JSON).
* **Compilador 2 (Proyecto Renzo):** [electrical_overlay_renzo.py](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/ia-cad-casas/scripts/electrical_overlay_renzo.py) (Procesa múltiples pisos consolidados en un único archivo JSON).

---

## 🎨 Catálogo DXF y Regeneración de la Biblioteca

Disponemos de un catálogo tipo catálogo A0/A1 con todos los símbolos dibujados vectorialmente según la Norma DGE:
* **Catálogo Vectorial DXF:** [simbologia_dge_completa.dxf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/simbologia-ia/salidas/simbologia_dge_completa.dxf)
* **Catálogo Renderizado PDF:** [simbologia_dge_completa.pdf](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/simbologia-ia/salidas/simbologia_dge_completa.pdf)
* **Reporte de Auditoría de Símbolos:** [revision_visual_simbologia_dge.md](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/simbologia-ia/revision_visual_simbologia_dge.md)
* **Script Generador Portátil:** [generar_simbologia_dge_dxf.py](file:///home/kimdokja/Documents/Instalaciones-electricas/instalacion-electricas/herramientas/simbologia-ia/scripts/generar_simbologia_dge_dxf.py)

### ¿Cómo regenerar la biblioteca sin editar a mano?
Ejecuta el script generador utilizando el entorno de Python virtual del repositorio:
```bash
herramientas/ia-cad-casas/.venv/bin/python herramientas/simbologia-ia/scripts/generar_simbologia_dge_dxf.py
```
Este comando leerá la especificación geométrica del JSON, creará los bloques vectoriales ordenados por capas y reescribirá la lámina catálogo en formato DXF y PDF.

### ¿Cómo usar los bloques en planos eléctricos?
Cada símbolo en el catálogo se define como un `BLOCK` de AutoCAD/QCAD. Los nombres siguen la estructura `DGE_[Codigo]_[Nombre]`, por ejemplo:
* `DGE_09_93_28_INTERRUPTOR`
* `DGE_09_93_17_TOMACORRIENTE_TIERRA`
* `DGE_09_93_69_TERMA`

Al diseñar un plano eléctrico en formato JSON:
1. Define las coordenadas del componente (X, Y).
2. Asigna la propiedad de bloque correspondiente mediante su identificador único.
3. El compilador de planos importará automáticamente el bloque desde esta biblioteca y lo insertará a escala en la capa CAD correspondiente, garantizando el cumplimiento normativo DGE.

---

## ⚡ Estándar de Simbología Eléctrica

La simbología gráfica utilizada en el repositorio está normalizada en metros sobre el espacio del modelo y responde a los requisitos del Código Nacional de Electricidad - Utilización (CNE-U) de Perú y la RM N° 091-2002-EM/VME:

| Elemento | Símbolo DXF / Representación Visual | Capa DXF (Layer) | Formato JSON (Aquiles) | Formato JSON (Renzo) |
| :--- | :--- | :--- | :--- | :--- |
| **Luminaria de techo** | Círculo con cruz interna fina (+) | `ELEC_LUMINARIAS` | `"luminarias": [{"circuit": "C1", "x": X, "y": Y}]` | `"luminarias": [{"circuito": "C1", "pos": [X, Y]}]` |
| **Interruptor simple** | Círculo pequeño con trazo oblicuo. Rotula texto `S` | `ELEC_INTERRUPTORES` | `"interruptores": [{"circuit": "C1", "kind": "simple", ...}]` | `"interruptores": [{"circuito": "C1", "tipo": "simple", ...}]` |
| **Interruptor conmutado** | Círculo pequeño con trazo oblicuo. Rotula texto `S3` | `ELEC_INTERRUPTORES` | `"interruptores": [{"circuit": "C1", "kind": "conmutado", ...}]` | `"interruptores": [{"circuito": "C1", "tipo": "conmutado", ...}]` |
| **Tomacorriente doble** | Círculo con dos líneas paralelas horizontales | `ELEC_TOMACORRIENTES` | `"tomacorrientes": [{"circuit": "C2", "kind": "doble", ...}]` | `"tomacorrientes": [{"circuito": "C2", "tipo": "doble", ...}]` |
| **Tomacorriente con tierra**| Círculo con dos líneas horizontales y pin vertical | `ELEC_TOMACORRIENTES` | `"tomacorrientes": [{"circuit": "C2", "kind": "tierra", ...}]` | `"tomacorrientes": [{"circuito": "C2", "tipo": "tierra", ...}]` |
| **Carga / Toma Especial** | Rombo (para cocina, termo o cargas de fuerza) | `ELEC_TOMACORRIENTES` | `"tomacorrientes": [{"circuit": "C3", "kind": "especial", ...}]` | `"tomacorrientes": [{"circuito": "C3", "tipo": "especial", ...}]` |
| **Tablero General (TG)** | Rectángulo con la etiqueta centrado (ej: `TG` o `TD`) | `ELEC_TABLERO(S)` | `"tableros": [{"label": "TG", "x": X, "y": Y}]` | `"tableros": [{"id": "TG", "pos": [X, Y]}]` |
| **Medidor (M)** | Círculo con la letra `M` en su interior | `ELEC_MEDIDOR` | `"medidores": [{"label": "M", "x": X, "y": Y}]` | `"medidores": [{"pos": [X, Y]}]` |
| **Puesta a Tierra (SPAT)** | Símbolo estándar de tierra (3 líneas decrecientes) | `ELEC_PUESTA_TIERRA`| (No soportado directamente en JSON) | `"puesta_tierra": [{"pos": [X, Y]}]` |
| **Canalización empotrada** | Polilínea discontinua (`linetype`: `DASHED`) | `ELEC_CANALIZACION` o `ELEC_CIRCUITO_CX` | `"rutas": [{"circuit": "C1", "points": [[X1, Y1], ...], "linetype": "DASHED"}]` | `"canalizaciones": [{"circuito": "C1", "puntos": [[X1, Y1], ...]}]` |

---

## 👁️ Auditoría Visual Obligatoria (Capacidad Multimodal)

> [!WARNING]
> La generación puramente algorítmica de planos a través de coordenadas JSON suele producir colisiones visuales entre textos, muros y símbolos. **Cualquier IA que genere o modifique un plano eléctrico en este repositorio TIENE LA OBLIGACIÓN de realizar una auditoría visual usando sus capacidades multimodales (visión).**

### Instrucciones de Revisión de Calidad Visual:

1. **Compilación y Renderizado:**
   Una vez generado o modificado el archivo `.json`, compila el plano a DXF y exporta el archivo a PDF utilizando el script del repositorio:
   ```bash
   # Ejemplo para el Proyecto Aquiles
   herramientas/ia-cad-casas/.venv/bin/python herramientas/ia-cad-casas/scripts/electrical_overlay.py --base Avanze-Proyecto-Aquiles/trabajo-cad-casa/salidas/piso1_v3.dxf --electrical Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/data/electrico_piso1_v4.json --output Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v4.dxf
   
   # O usando el renderizador de QCAD
   qcad -no-gui -platform offscreen -quit -autostart "$(realpath herramientas/ia-cad-casas/cad-scripts/dxf2pdf.js)" -input "$(realpath Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v4.dxf)" -output "$(realpath Avanze-Proyecto-Aquiles/trabajo-cad-casa/electricos/salidas/electrico_piso1_v4.pdf)"
   ```
   *Nota: También puedes convertir los PDFs generados a imágenes PNG usando herramientas del sistema como `pdftoppm`.*

2. **Inspección Multimodal con Zoom:**
   Abre visualmente el archivo renderizado final (PDF, PNG o captura) y valida:
   * **Colisiones con Muros:** Los símbolos eléctricos (como luminarias de techo en el centro del ambiente, tomacorrientes en el borde) no deben quedar solapados o cortados por muros arquitectónicos, marcos de puertas ni ventanas.
   * **Superposición de Texto:** Verifica que los textos descriptivos (`C1`, `C2`, anotaciones, nombres de ambientes) no queden encima de los muros o de los símbolos de interruptor/luminaria/tomacorriente. La legibilidad de los circuitos es primordial. Si hay solapamiento, desplaza ligeramente las coordenadas de los textos o del símbolo en el JSON de entrada.
   * **Ubicación de Interruptores:** Asegúrate visualmente de que los interruptores estén en la pared correcta al entrar al cuarto, **siempre al lado de la cerradura/manija** y nunca detrás del barrido de la puerta abierta ni encima de una ventana.
   * **Rutas Ortogonales y Limpias:** Confirma que las tuberías (canalizaciones discontinuas) viajen de manera ortogonal (paralela a los muros), evitando diagonales arbitrarias que crucen los ambientes de forma desordenada o pasen a través de vacíos de escaleras.
   * **Coherencia de la Leyenda:** Revisa visualmente que el cuadro de la leyenda no tape partes del plano arquitectónico y que los símbolos en la leyenda se visualicen con el grosor y color correctos de acuerdo con la capa asignada.
