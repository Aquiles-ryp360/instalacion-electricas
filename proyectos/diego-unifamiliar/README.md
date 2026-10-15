# Vivienda unifamiliar de tres niveles · Diego

**Diego Jefferson Charaja Mamani · código 214254.** Se organiza el expediente existente de instalaciones eléctricas interiores: primer piso, segundo piso y azotea. La denominación exacta I/II del curso no se confirma en esta reorganización.

- [Expediente PDF existente](entregables/EXPEDIENTE_TECNICO_COMPLETO_INSTALACIONES_ELECTRICAS.pdf).
- [Memoria editable](expediente/EXPEDIENTE_TECNICO_COMPLETO_INSTALACIONES_ELECTRICAS.md) y [Word](entregables/EXPEDIENTE_TECNICO_COMPLETO_INSTALACIONES_ELECTRICAS.docx).
- [Memoria descriptiva y cálculos](expediente/01_MEMORIA_DESCRIPTIVA_Y_CALCULOS.md), [especificaciones](expediente/02_ESPECIFICACIONES_TECNICAS.md) y [matriz de inconsistencias](expediente/03_MATRIZ_INCONSISTENCIAS_Y_PROPUESTAS.md).
- [Unifilar CAD DXF](diseno-electrico/planos/plano_unifilar_diego_cad.dxf), [vista PDF](entregables/planos/plano_unifilar_diego_cad.pdf) y [QElectroTech](diseno-electrico/planos/plano_unifilar_diego.qet).
- [Datos de cálculo](datos/resultados_diego.json) y [fuentes originales](fuentes/).

Los archivos se reubican por función; las fuentes, las magnitudes de cálculo y los documentos publicados se conservan. Los enlaces de figuras y las rutas del [generador existente](scripts/run_diego_cad_unifilar.py) se adaptan a la nueva estructura. No se ejecutó ese generador ni se validó nuevamente el dimensionamiento eléctrico. Su diccionario de datos es estático y puede sobrescribir el JSON si se ejecuta: revisar sus entradas antes de regenerar.

[proyecto.yaml](proyecto.yaml) declara el estado documental. [Catálogo general](../README.md).
