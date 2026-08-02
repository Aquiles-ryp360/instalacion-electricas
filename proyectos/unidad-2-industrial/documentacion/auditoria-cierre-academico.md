# Auditoria de cierre academico

Fecha: 2026-08-02.
Alcance auditado: consigna de WhatsApp, respuestas del estudiante, DXF recibido,
formato del expediente Aquiles de la primera unidad y resultados reproducibles.

## Cumplimiento de la consigna

| Requisito | Evidencia activa | Estado |
|---|---|---|
| Trabajo individual | Autor unico en `proyecto.yaml`, portada y rotulos | CUMPLE |
| Tema industrial: grifo | Arquitectura canonica, memoria y seis laminas | CUMPLE |
| Memoria descriptiva | Capitulo 1 con datos, catastro, contexto satelital y croquis A-01 | CUMPLE CON UBICACION APROXIMADA |
| Estudio de cargas | 35 circuitos, cuadro reproducible, capitulos 1 y 2 | CUMPLE |
| Calculo de iluminacion | Ocho zonas con estado PASS y capitulo 2 | CUMPLE A NIVEL ANTEPROYECTO |
| Calculo de conductores | Ampacidad, PE y caida por circuito/alimentador | CUMPLE |
| Especificaciones tecnicas | Capitulos 3 y 4, materiales, montaje y pruebas | CUMPLE |
| Metrados y presupuesto | 46 partidas, CSV, capitulo 6 y fecha base | CUMPLE COMO REFERENCIAL |
| Cronograma | Capitulo 5, ocho semanas e hitos de control | CUMPLE |
| Planos | IE-01 a IE-06 en DXF y PDF A1 vectorial | CUMPLE |
| Formato de primera unidad | Carta, portada curva azul/verde, cabecera, pie e indice Aquiles | CUMPLE |
| Sustentacion personalizada | Guia de 30 preguntas y PDF personal | CUMPLE |

## Decisiones del estudiante verificadas

| Decision | Tratamiento | Estado |
|---|---|---|
| Autor Aquiles Taylor Ramos Yapo | Portada, metadatos y rotulos | CUMPLE |
| Docente Mg. Gregorio Meza Marocho | Portada, rotulos y guia | CUMPLE |
| Propietario Miguel Mamani Chuquicallata | Cita como dato de referencia DREM, sin afirmar aprobacion | CUMPLE |
| Proyecto electrico nuevo | Memoria distingue DXF arquitectonico de diseño electrico | CUMPLE |
| Diesel, Regular y Premium | Tanques, cargas y memoria | CUMPLE |
| Excluir GLP/GNV | Portada, memoria, rotulos, planos y guia | CUMPLE |
| Rotulo adaptado a Puno | Bloque original A-01, sin mascara ni superposicion; datos academicos sustituidos dentro de su huella | CUMPLE |
| PDF sin borrosidad | Seis PDF A1 vectoriales, cero imagenes raster | CUMPLE |
| Rutas y circuitos legibles | Carriles separados, etiquetas de circuito y unifilar ortogonal | CUMPLE |
| Cotizacion automatica | BOM separado, evidencia JSON/CSV/Markdown y filtros seguros | CUMPLE COMO CONSULTA COMERCIAL |
| Reproduccion en Windows | Seis entradas versionadas, preparador PowerShell y verificador SHA-256 | CUMPLE |

## Resultados de control

- Calculo electrico: PASS.
- Alumbrado por lumenes: PASS.
- Metrados/presupuesto reproducible: PASS.
- Cotizacion automatica: 41 consultas; 4 `OK`, 30 `SIN_SELECCION` y 7 `NO_ENCONTRADO`; todas requieren revision.
- Expediente y guia: compilacion LaTeX sin error fatal.
- Expediente: 31 paginas; las capturas de ubicacion son evidencia raster y las seis paginas de planos A1 permanecen vectoriales.
- Planos: seis paginas A1 vectoriales, sin `WIPEOUT`; los PNG son solo previsualizacion.
- Pruebas automatizadas: 45 PASS (cotizacion v0/v1, Renzo y Unidad 2).

## Limite del cierre

El cierre es **academico**. No es posible declarar el diseño constructivo porque
no se recibieron factibilidad e Icc, placas definitivas, verificacion de campo,
resistividad/fotometria ni revision profesional de areas clasificadas. Estas
ausencias estan visibles en el expediente y no anulan la entrega academica; si
el caso se ejecutara, si son condiciones obligatorias previas.
