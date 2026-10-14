# Dictamen de presentación auditada Rev. 1 — Capachica–Chifrón

**Fecha de consulta:** 14-10-2026 UTC. **Estado:** presentable para revisión académica; no es expediente aprobado para construcción, contratación o conexión.

## Resultado principal

Se consultó directamente la [capa oficial de tramos MT de GISEM/Osinergmin](https://gisem.osinergmin.gob.pe/serverosih/rest/services/OGC/PeruOsinergmin019RedesMediaTension/MapServer/22) por los códigos `TMT000012389` y `TMT001847370`. La respuesta íntegra, su URL y su SHA-256 se guardan en el paquete local `build/renzo-linea-primaria-capachica/presentacion_auditada_rev1/`.

| Elemento | Evidencia | Conclusión |
|---|---|---|
| Eje local E-01 a E-09 | `datos/topografia/planilla_vertices_lp.csv`, coordenadas EPSG:32719 | Longitud geométrica independiente: **816,60 m**; es un trazo documental propuesto. |
| Punto E-01 frente a tramos citados | Geometría actual de GISEM, transformada a EPSG:32719 | Separación mínima **131,76 m**. No está sustentada la conexión directa declarada en la memoria anterior. |
| Coordenadas E-01 y E-04 | Comparación UTM de la planilla con transformación de latitud/longitud publicadas localmente | Diferencias aprox. **4,49 m** y **5,09 m**. La fuente local requiere conciliación topográfica. |
| GeoJSON local de `fuentes/gisem/` | Comparación visual y numérica con respuesta directa del servicio oficial | Su geometría no reproduce los dos tramos actuales consultados. Se conserva como antecedente, no como prueba oficial del TAP. |
| Imagen satelital local | `entregables/imagenes/fig_traza_satelital_chifron.png` | Rotula la coordenada de E-01 como SED y mezcla red MT con circuitos BT. No se usa como sustento de ubicación en la carpeta activa. |
| Seis planos CAD previos | Reapertura estructural con `ezdxf`, seis archivos R2010, cero errores de auditor | Son editables y útiles para exposición, pero sus geometrías/modelos y notas técnicas siguen pendientes de verificación profesional. |

La lámina nueva **LP-00** separa en azul la geometría obtenida de GISEM y en naranja el eje local. El PNG tiene archivos `.pgw` y `.prj` para georreferenciación EPSG:32719; el DXF contiene la geometría en metros UTM en espacio modelo y una presentación A3. La imagen es un mapa vectorial propio con cuadrícula, **sin base satelital**, porque los JPG locales carecen de metadatos geográficos verificables.

## Contenido de presentación

1. `DOSSIER_PRESENTACION_ACADEMICA_REV3.pdf`: portada/dictamen, LP-00 y seis láminas existentes con aviso de revisión.
2. `LP-00_UBICACION_GISEM_A3.dxf` y `.pdf`: plano nuevo para AutoCAD y revisión impresa.
3. `LP-00_MAPA_GEOREFERENCIADO_GISEM.png`, `.pgw`, `.prj`: imagen georreferenciada.
4. `CAD_REFERENCIAL_NO_VERIFICADO/` dentro del ZIP: los seis DXF anteriores, preservados sin alterarlos.
5. `GISEM_TRAMOS_22_RESPUESTA.json` y `MANIFIESTO_PRESENTACION_REV1.json`: fuente y huellas.

## Condiciones para elevar el expediente

- Confirmación escrita del punto de conexión, tensión, capacidad, protecciones y condiciones de entrega por Electro Puno.
- Levantamiento topográfico de campo y conciliación de coordenadas, cotas, apoyos, cruces y servidumbres.
- Verificación independiente de demanda, transformador, conductor, mecánica, aislamiento, cortocircuito, PAT, metrados y costos.
- Revisión de la edición y reglas aplicables del [Código Nacional de Electricidad Suministro 2011](https://www.gob.pe/institucion/minem/normas-legales/108753-0214-2011-mem) y de las normas DGE correspondientes, con firma profesional.

Hasta cerrar esas condiciones, las afirmaciones anteriores de “expediente definitivo” y “factibilidad confirmada” no deben utilizarse para tramitar ni ejecutar la obra.
