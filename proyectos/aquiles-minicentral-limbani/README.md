# Minicentral hidroeléctrica Limbani - Aquiles

Anteproyecto de primera unidad de **Centrales Hidroeléctricas**.

- Alumno: Aquiles Taylor Ramos Yapo, **227368**.
- Docente: **MEZA MAROCHO GREGORIO**.
- Sección: **GRUPO A**.
- Estado: **R02 académica, condicionada a datos de campo y fabricante**.
- Punto de entrada: [proyecto.yaml](proyecto.yaml).

## Resultado

Se revisó el borrador de 28 páginas físicas recibido el 13/10/2026. Hay 24 observaciones con páginas de origen. Se corrigieron contradicciones de geometría, salto, potencia, altitud, grupo Dyn5, puesta a tierra y referencias del CNE. Se separa el dato del borrador, la hipótesis y el resultado calculado.

R02 revisa además **nueve problemas de R01**: auxiliares sin modo definido, alternativa de 500 mm sin mecánica, margen sin sensibilidad, lectura de carga continua incompleta, distancias MT sin caso de consulta, ruta ANA parcial, servicios propios sin barra de arranque, cifras repetidas y área bruta de reja sin porosidad. Ver [validación R02](documentacion/validacion-r02.md).

Con 420 l/s y tubería de 220 m:

| Di interior | Generador | PCC con carga operativa R02 |
|---|---:|---:|
| 450 mm | 155.462 kW | 147.822 kW |
| 500 mm | 158.878 kW | 151.155 kW |
| 550 mm | 160.762 kW | 152.991 kW |

Los auxiliares de generación suman **5.10 kW** por inventario; sus pérdidas TSA son adicionales. El margen de 500 mm es **1.155 kW**, y caudal 5% menor reduce PCC a **143.845 kW**. Se desarrolla 500 mm como alternativa prioritaria de estudio, sin garantía de 150 kW ni selección comercial. La reconstrucción del borrador sigue dando 137.870 kW en bornes y geometría inválida.

Se incluyen cribados mecánicos de las tres alternativas, viga entre apoyos, térmica, balance completo, arranque desde red, sensibilidad y comparación económica marginal con tarifa/precios pendientes. El estudio conserva como `null` energía anual, caudales y datos de conexión no acreditados.

## Reproducir

Desde la raíz del repositorio:

```powershell
python -m unittest discover -s herramientas/hidroelectricas/tests -v
python proyectos/aquiles-minicentral-limbani/scripts/construir.py
```

Requiere Python 3.10+, Matplotlib y LaTeX con `pdflatex` y paquetes declarados en `expediente/preambulo.tex`. En esta máquina ya estaban disponibles; no se alteró la instalación de Python ni MiKTeX. Para cálculos y figuras sin compilar PDF, añadir `--sin-pdf`.

Salidas en `build/aquiles-minicentral-limbani/`:

- `expediente/main.pdf`: expediente de ocho capítulos y anexos normativos.
- `expediente/observaciones.pdf`: 24 hallazgos del borrador y nueve correcciones a R01.
- `calculos.json`, `comparacion.csv`: resultados reproducibles.
- `observaciones.md`, `manifest-entradas.json`: revisión y huellas de entradas.
- `metrados_calculados.csv`: cantidades derivadas del diámetro vigente; precios vacíos.

El constructor no escribe en `entregables/`. El pipeline residencial común está deshabilitado para este proyecto: se usa su constructor específico. Los gráficos son modelos, no mediciones ni curvas de duración del río.

## Entradas

- `datos/parametros.json`: valores, unidades, procedencia, confianza y datos faltantes.
- `datos/normativa.json`: fuentes y matriz regla-evidencia-estado.
- `datos/observaciones.json`: hallazgos del borrador.
- `datos/metrados.csv`: cantidades preliminares y precios pendientes.
- `datos/revision-r02.json`: auditoría de R01 y tratamiento R02.
- `datos/plantillas/`: estructuras vacías para aforos, hidrología, demanda y conexión; nunca se usan como mediciones.
- `expediente/capitulos/`: capítulos editables en LaTeX.
- `fuentes/local/`: copia inalterada del PDF recibido, ignorada por Git.
- `documentacion/`: decisiones, validaciones y registro de evidencia.

El escudo se reutiliza desde la vivienda de Aquiles. Las normas públicas descargadas están en `referencias/local/minicentral-limbani/`, ignoradas por Git; el registro de URL permite recuperarlas. El constructor puede funcionar sin los PDF normativos, pues no extrae números automáticamente de ellos.

R01 se conserva en `build/aquiles-minicentral-limbani/archivo-r01/` como antecedente local. Los PDF revisados de R02 se copian a `output/pdf/`, también ignorado; ninguna versión está publicada en `entregables/` como aprobada. Las salidas, motor y escudo forman parte de la trazabilidad. La recopilación legal no sustituye la consolidación administrativa antes de tramitar.

## Datos que condicionan el diseño final

Rúbrica y objetivo (bornes o PCC); aforos y series; caudal ecológico y derechos; topografía y sedimentos; demanda o contrato de exportación; punto de conexión y fallas; geotecnia y resistividad; curvas y garantías de fabricantes. Estos campos permanecen `null` donde falta evidencia. La presencia de una norma en el registro no equivale a cumplimiento.
