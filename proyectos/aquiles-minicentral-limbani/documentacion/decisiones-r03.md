# Registro de decisiones y evidencia — R03

Revisión del 13–14 de octubre de 2026. Trabajo local en `G:\Aquiles\instalacion-electricas`, rama `codex/minicentral-limbani`. Se preservaron borrador recibido, fuentes y catastro. Se archivaron entradas, capítulos, scripts y PDF R02 en `build/aquiles-minicentral-limbani/archivo-r02/`; Git conserva la historia. No se modificó el proyecto de línea primaria ni se publicó en GitHub.

## Decisiones de alcance

1. Proyecto académico estudiantil, no expediente constructivo. El docente pidió diseñar una minicentral sin rúbrica detallada. Se verificaron sus grados en H08/H09 para usar Mg. Ing.
2. Operación aislada; el modelo R02 conectado a red deja de ser vigente. La conexión futura 2046–2076 solo genera previsiones y estudios pendientes.
3. Antecedentes 200 kW, 50 m y Banki sin placa ni topografía independiente. CM-A y CM-B difieren 152 m; el punto Gemini queda retirado por incompatibilidad espacial. No se reemplaza la central por coordenadas del centro urbano.
4. Se adopta ámbito conservador de cuatro registros INEI, sin sumar el distrito. Ocupación censal no equivale a contrato activo. La tasa anual 1% y la clasificación de Huancasayani son supuestos, no proyecciones oficiales.
5. Se comparan 150/200/400/600 kW. Tres grupos de 200 kW son una envolvente de cobertura normativa, no inversión óptima demostrada. El tercer grupo aporta solo unos 62.7 MWh/año adicionales frente a dos. Se recomienda validar padrón y desarrollo por etapas.

## Hidrología y cartografía

- Se recuperaron completos PISCO ARNOVIC diario y GR2M mensual 1981–2025 desde HydroShare/SENAMHI, con COMID 9080887. Se conservaron unidades originales, fechas y huellas. La serie es **simulada y transpuesta**, sin calibración local.
- Se corrigió un error potencial de área: el atributo PISCO de 355.411 km² coincide con Web Mercator; el área geodésica WGS84 es 332.151 km². La cuenca de captación a 90 m da aproximadamente 135.31 km²; factor 0.407375. La resolución 30 m cambia menos del 1%, pero el ajuste de salida D8 no pasa el control por confluencia ambigua.
- La altitud media de captación es mayor que la del polígono PISCO. No se declara rendimiento específico uniforme validado: se ensayan factores de sesgo 0.5/0.7/1.0/1.3 sin interpretar probabilidades.
- La estación HLG Limbani 260501 se identificó en el mapa SENAMHI. El acceso público a series está protegido por CAPTCHA; no se eludió. Se obtuvieron boletines de **niveles**, sin curva de gasto. No se convirtió nivel en caudal ni se inventaron aforos.
- La licencia ANA 370-2017 de Phara informa 90 l/s para otra central; no es caudal natural ni derecho de Limbani. Se verificó además río Comunidad en la resolución ANA/TNRCH 1588-2018, de 28/09/2018: expediente de vertimientos de la Municipalidad de Phara. Fuente: https://www.ana.gob.pe/sites/default/files/normatividad/files/82-RTNRCH-1588-2018-003.pdf . No se adopta su caudal de vertimiento como caudal del río. “Para” permanece sin identificación oficial concluyente.
- La tesis UNA de Phara contiene cinco columnas de años sin calendario identificable; no se usa como serie oficial o regresión. La descarga válida es la API `server/api/core/bitstreams/.../content`; una respuesta HTML inicial archivada con extensión PDF queda excluida del análisis.
- El perfil SRTM90 aporta referencias de terreno 3285 y 3239 m. Se descuentan 0.7 m antes de cámara para estudiar Hb45.3, sin considerarlo nivel medido. Canal150/tubería350 son una propuesta que debe caber en ladera; no se altera el relieve para forzar potencia.
- El GeoPackage original Catastro-Limbani se abrió solo lectura. Sus 482 entidades Casas no son contratos. Las 282 huellas añadidas por herramientas previas para llegar a 764 no se utilizan como censo.

## Criterios actualizados

La RD108-2023 derogó las bases RD031-2003: 600/400 W por lote, simultaneidad doméstica0.80. La E.030 de2026 sitúa Limbani en zona2, Z0.25, y la generación/transformación en categoríaA2,U1.5. Faltan suelo y modelo estructural. Se identificó IEC60909-0:2026 como edición que reemplaza2016; su texto completo pagado no se obtuvo y el cálculo de reactancias se rotula simplificado. Los catálogos internacionales no se presentan como lectura integral de normas.

Reserva ecológica15%de media mensual y otros usos5l/s son **supuestos**; no porcentajes legales ni derechos acreditados. El proyecto600kW exige revisar ruta de concesión hidráulica y distribución, además de autorización térmica del respaldo. Ningún permiso está obtenido.

La tubería se comprueba con paredes compatibles de14/13mm, distintos diámetros internos y rugosidades. El MOC se detiene al detectar presión inferior al límite monofásico adoptado. No se presentan resultados negativos imposibles después de cavitación. PN40 solo es candidato. Los anclajes en roca, silletas, sismo, vacío y colapso de cavidades quedan condicionados a datos reales.

La protección contempla disminución de corriente de falla del generador: 50/51simple no basta; se proponen51V y diferenciales. Se calculan seis casos remotos trifásicos y se mantienen abiertas las fallas a tierra. La malla se estudia por sensibilidad; GPRno equivale a tensión de contacto y no se declara seguridad por alcanzar5ohm.

## Costos y entrega

Las32partidas usan cantidades vinculadas a dimensiones y equipos, con precios **estimados** en soles/octubre2026. El cemento minorista y los comparadores internacionales se registran como contrastes de alcance limitado. No se inventan cotizaciones de fabricante. La distribución ya instalada no recibe doble recargo de montaje. El presupuesto completo ronda S/16.06millones con sensibilidad±35%, y los VAN de escenarios son negativos. No se presume financiamiento ni subsidios.

Se generan memoria, ocho láminas y trece diapositivas desde las mismas entradas; se revisan todas las páginas renderizadas. Las figuras editables se conservan en SVG/PDF. Se usan PNG300dpi en los documentos para evitar defectos de trazado observados con el renderizador PDF local, manteniendo versiones vectoriales para edición.

## Reproducción de la investigación

`fuentes/local/investigacion-r03/` contiene originales públicos y no se modifica. Para repetir delimitación se necesitan `S15W070-mapzen.hgt.gz`, `tramos_candidatos.json` y `cuenca_9080887.geojson`, todos conservados. Ejecutar `analizar_dem_r03.py` y opcionalmente `--paso-arcsec 1`; después `analizar_hidrologia_r03.py` con los NetCDF originales. El constructor normal utiliza las series CSV extraídas y puede regenerar la figura de cuenca desde esas fuentes si falta el NPZ derivado. Las URLs están en los registros JSON.

Dependencias de extracción netCDF4/cftime instaladas con `--target G:\Aquiles\dependencias-minicentral --no-deps`. Se conservaron Python y MiKTeX existentes. Los scripts genéricos D8/MOC permanecen en `herramientas/hidroelectricas/`; datos exclusivos de Limbani están en su carpeta de proyecto.
