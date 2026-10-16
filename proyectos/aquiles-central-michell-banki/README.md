# Minicentral Limbani y Huancasayani — R03

Proyecto académico de diseño para **Centrales Hidroeléctricas**, primera unidad. Estudiante: **Aquiles Taylor Ramos Yapo, 227368, Grupo A**. Docente: **Mg. Ing. Gregorio Meza Marocho**, grados contrastados con documentos de UNA Puno. Presentación: 14/10/2026, 07:00, Perú.

La versión vigente parte de [proyecto.yaml](proyecto.yaml). La operación inicial es **aislada, sin SEIN**. Se comparan 150, 200, 400 y 600 kW; se dimensiona el caso conservador de tres grupos de 200 kW, con respaldo modular. No se presenta como una inversión óptima ni como expediente listo para construir.

## Mejora en desarrollo · 16/10/2026

[Diagnóstico y alcance propuesto R04](documentacion/MEJORA_PROPUESTA_R04.md): memoria más directa, planos dimensionados y desarrollo académico de un grupo Banki de 200 kW. Se incorpora un [contraste reproducible con el T12 de SKAT](datos/turbina/contraste-t12-r04.json); no se atribuye automáticamente el rendimiento supuesto de R03 a ese modelo.

Ya está disponible una [primera lámina geográfica de revisión, con PDF, DXF y Google Earth](entregables/r04-avance/README.md). Muestra relieve, curvas y las dos casas de máquinas candidatas, con coordenadas y procedencia. **Es un avance; todavía no constituye el expediente R04 completo ni sustituye los tres PDF R03.**

## Resultados y alcance

- PISCO/SENAMHI 1981–2025: 16 436 días y 540 meses recuperados. COMID 9080887; transposición exploratoria por área geodésica, sin calibración local. Caudales simulados, **no aforos oficiales en captación**.
- INEI 2017: 2046 habitantes y 946 viviendas ocupadas en cuatro registros. Escenario 2026 de 1037 conexiones potenciales; no se suma el total distrital ni se confunde vivienda con contrato.
- Demanda máxima de estudio: **526.79 kW** usando las bases rurales de 2023. Oferta nominal de 600 kW en bornes: **544.28 kW en usuarios**.
- Estiaje: potencia diaria P95 de estudio **37.43 kW** y mínimo **0 kW**. No se garantiza suministro hidroeléctrico continuo de 150–200 kW.
- Energía hidro servida: **1316.57 MWh/año**; déficit hidro **384.53 MWh/año** para el perfil 2026 supuesto. Se examinan respaldo y reducción de cargas.
- Salto bruto de gabinete 45.3 m; tubería de 350 m y Di 1000 mm. Cotas y trazado requieren nivelación. Se modela cierre lento y se detiene MOC donde aparece cavitación.
- Presupuesto completo estimado **S/16.06 millones**, con sensibilidad ±35%. Los precios de partidas son estimaciones; los escenarios financieros examinados son desfavorables.

Las referencias de la central existente (200 kW, unos 50 m y Banki) siguen sin placa o medición independiente. Las dos posiciones de casa de máquinas difieren 152 m; toma, cámara y restitución no están levantadas. Estas limitaciones están descritas en la memoria y en cada plano pertinente.

## Documentos para presentar

Copias revisables disponibles directamente en GitHub:

1. [Memoria R03](entregables/r03/Minicentral_Limbani_R03_proyecto_academico.pdf): doce capítulos y anexos, 55 páginas.
2. [Planos R03](entregables/r03/Minicentral_Limbani_R03_planos_academicos.pdf): ocho láminas A3.
3. [Exposición R03](entregables/r03/Minicentral_Limbani_R03_exposicion.pdf): trece diapositivas 16:9.

Los originales editables están en `expediente/r03/`, `expediente/main-r03.tex`, `planos-r03.tex` y `exposicion-r03.tex`. Las figuras vectoriales SVG/PDF y los cálculos/tablas se generan en `build/aquiles-central-michell-banki/r03/`. El [guion](documentacion/GUION_EXPOSICION_R03.md) y los [pendientes](documentacion/PENDIENTES_PRESENTACION.md) facilitan la sustentación.

## Reproducir

Desde la raíz del repositorio:

```powershell
python -m unittest discover -s herramientas/hidroelectricas/tests -v
python proyectos/aquiles-central-michell-banki/scripts/construir.py
python proyectos/aquiles-central-michell-banki/scripts/verificar_r03.py
```

Se requieren Python, NumPy, Matplotlib, Shapely, PyProj y LaTeX. Para regenerar solo cálculos/figuras, añadir `--sin-pdf`. En esta máquina los paquetes adicionales netCDF4/cftime están aislados en `G:\Aquiles\dependencias-minicentral`; no se sustituyó Python del sistema. La extracción hidrológica usa ese directorio.

La reconstrucción normal usa los CSV ya extraídos. Para repetir la investigación espacial se conservan los NetCDF, GeoPackage, tesela DEM y respuestas públicas originales en `fuentes/local/investigacion-r03/`, ignorados por Git. `analizar_dem_r03.py` y `analizar_hidrologia_r03.py` documentan el método. Las copias de fuentes grandes deben estar disponibles; no se sustituyen por cifras inventadas. Las dependencias de investigación espacial y su recuperación se detallan en el [registro R03](documentacion/decisiones-r03.md).

## Trazabilidad y estado

Entradas canónicas: `datos/parametros-r03.json`, `normativa-r03.json`, `fuentes-r03.json`, `topografia-r03.json` y `hidrologia-r03.json`. Series diarias/mensuales en `datos/hidrologia/`. Precios y criterios en `datos/precios-r03.csv`. Las entradas anteriores se conservan en [archivo/r02/](archivo/r02/README.md) y no alimentan el constructor vigente. `datos/base-normativa.json` es el catálogo semilla usado para actualizar la matriz R03.

Los originales aportados y el catastro permanecen sin modificación. R01/R02 se conservan en los archivos locales y en Git. La revisión y evidencia están en [validacion-r03.md](documentacion/validacion-r03.md). Los tres PDF de `entregables/r03/` son copias idénticas de las salidas revisadas; su estado es **para revisión académica**, sin aprobación para ejecución. Los recursos de identidad y ubicación se consultan en [recursos/](../../recursos/README.md).

El trabajo de [línea primaria de Instalaciones Eléctricas II](../aquiles-linea-primaria-inst-ii/README.md) tiene expediente, hipótesis y entregables independientes. [Catálogo general](../README.md).

Prioridades posteriores: aforos y curva de gasto, topografía, padrón y demanda medida, placas, crecidas/sedimentos, geotecnia/resistividad, curvas de fabricante, cotizaciones y permisos. No se requiere inventar una rúbrica adicional del docente: su encargo fue diseñar una minicentral y se definió un alcance académico coherente.
