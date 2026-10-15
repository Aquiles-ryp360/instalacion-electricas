# Verificación de la organización · 14 de octubre de 2026

La revisión corresponde al traslado de carpetas, la navegación del repositorio y la adaptación de rutas. Se ejecutó en `G:\Aquiles\instalacion-electricas` antes de publicar el commit de organización.

| Comprobación | Resultado |
| --- | --- |
| Catálogo e identificadores | Once proyectos identificados y enlazados; cursos y autores diferenciados. |
| Navegación local | 166 enlaces de 20 documentos comprobados, sin destinos inexistentes. |
| Sintaxis de programas reubicados | 28 programas analizados sin errores de sintaxis. |
| Conservación de archivos previos | 543 archivos localizados: 525 idénticos por SHA-256 y 18 textos adaptados. |
| Datos JSON | 40 archivos comparados; se conservan sus datos, admitiendo únicamente la actualización de rutas. |
| Datos estáticos del generador de Diego | Diccionario idéntico al original; generador no ejecutado. |
| PDFs R03 de minicentral | Tres copias idénticas a las salidas revisadas: memoria 55 páginas, planos 8 y exposición 13. |
| Línea primaria LP-R01 | 53 controles aprobados tras el traslado; PDF integrado 69 páginas, cálculos 18 y planos 19. |
| Minicentral R03 | Reconstrucción de cálculos y figuras con `--sin-pdf`; 22 comprobaciones aprobadas y 93 entradas con huella verificadas. |
| Suites comunes del repositorio | 47 pruebas aprobadas en cotización v0/v1, vivienda Renzo y unidad 2 industrial. |

No se recompilaron ni redibujaron los PDF y CAD entregados. Las comprobaciones de geometría y balance vuelven a ejecutarse sobre los resultados existentes; no certifican topografía de campo, placas de equipos ni aprobación de obra. Los pendientes de ingeniería siguen en cada expediente.

Se instaló `pytest` y sus dependencias en `G:\Aquiles\dependencias-validacion-repo`, sin sustituir Python del sistema. La ejecución local de las suites utilizó ese directorio y las dependencias ya disponibles en `G:\Aquiles\dependencias-linea-primaria`. En CI se usa `requirements.txt`.

La comparación de conservación y su detalle se guardan en `build/organizacion-repositorio/conservacion.json`, ignorado por Git. El [verificador de navegación](../herramientas/verificar_organizacion.py) queda versionado para repetir los controles de organización.
