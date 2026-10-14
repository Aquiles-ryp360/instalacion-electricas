# Validación R03 — proyecto académico

Fecha: 14/10/2026, Perú. Esta revisión distingue consistencia del modelo y legibilidad de los documentos de una comprobación de campo o cumplimiento constructivo. Ninguna de las siguientes verificaciones convierte las hipótesis en datos medidos.

## Comprobaciones realizadas

- Veinte pruebas unitarias del motor hidráulico/eléctrico, conservación D8, relleno de depresiones, primer pico de Joukowsky, estabilidad estacionaria, refinamiento espacial y detención por cavitación: correctas.
- Extracción de 16 436 días y 540 meses PISCO, fechas únicas y continuas, COMID único, unidades originales m³/s, sin negativos ni faltantes. No se rellenan vacíos artificialmente.
- Área geodésica frente al atributo Web Mercator; contraste 30/90m. Se identifica el control de salida D8 **no aceptado** y no se presenta como validación del recurso.
- Conservación de agua día por día entre reservas, caudal posible de turbinar y remanente. No hay extracción negativa ni potencia por encima de placa.
- Balance de bornes a usuarios con pérdidas separadas y residual numérico despreciable. Energía hidro servida más déficit coincide con demanda del perfil supuesto.
- Caudal nominal inferior al límite hidráulico, inventario auxiliar coherente, malla152m, seis casos trifásicos remotos y correspondencia entre partidas y geometrías/equipos.
- Presupuesto con recargos expresos y sin volver a montar las redes ya valoradas instaladas. Precios estimados y alcance de referencias comerciales declarados.
- Compilación y revisión de memoria, ocho láminas y trece diapositivas. Renderizado de todas las páginas; corrección de tablas partidas, superposición del rótulo de malla y defectos de líneas del renderizador local. Gráficos incorporados a300dpi, SVG/PDF editables conservados.
- Verificación automática de errores LaTeX, páginas, balances y huellas de entradas con `scripts/verificar_r03.py`. El resultado y conteos exactos están en `build/aquiles-minicentral-limbani/r03/verificacion-r03.json`; las inspecciones se conservan en `qa/`.

## Resultados centrales

| Magnitud de escenario | Resultado |
|---|---:|
| Potencia hidro instalada estudiada | 600kW, tres unidades |
| Potencia nominal en usuarios | 544.28kW |
| Demanda máxima conservadora | 526.79kW |
| Potencia diaria de excedencia95% | 37.43kW, no potencia firme certificada |
| Mínimo hidro del modelo | 0kW |
| Energía hidro servida | 1316.57MWh/año |
| Déficit hidro | 384.53MWh/año |
| Presupuesto completo estimado | S/16.06millones, sensibilidad±35% |

La comparación no demuestra viabilidad financiera de la solución completa. La alternativa600kW representa cobertura conservadora y debe revisarse con padrón, recurso y rehabilitación. No se oculta el resultado desfavorable ni se fuerza un salto o caudal para recuperar200kW en estiaje.

## Límites de validación

No se obtuvieron aforos/curva de gasto local, placas, topografía de campo, rasante, caudales extremos de diseño, caracterización de sedimentos, EMS, resistividad, curvas de fabricante ni cotizaciones integrales. Tampoco se consolidaron administrativamente todos los permisos de la instalación existente. Los textos internacionales de pago no se presentan como leídos íntegramente. El alcance de cada norma consultada está en el registro.

La seguridad ante separación de columna, pandeo, fatiga, silletas/anclajes, sismo, contacto/paso y fallas de secuencia requiere datos adicionales. Los planos son académicos, las coordenadas candidatas están identificadas y la posible conexión futura alSEIN no está aprobada.

## Conservación de fuentes

El PDF aportado y el GeoPackage original del catastro se leen sin modificarlos. Las fuentes públicas quedan archivadas con manifestación de URL y SHA-256. Se conservan R01/R02, y la entrada estable cambia aR03. Los documentos revisados se copian a `output/pdf/`; no se marcan como aprobados para construcción ni se publican automáticamente enGitHub.
