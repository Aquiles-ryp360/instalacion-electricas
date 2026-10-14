# Línea primaria Limbani–Huancasayani · LP-R01

Curso: **Instalaciones Eléctricas II**. Estudiante: **Aquiles Taylor Ramos Yapo, 227368**.

Este proyecto independiente transporta energía desde la transformación de salida de la minicentral hasta una SE de llegada en Huancasayani. Opera como sistema aislado. No diseña la distribución urbana de Limbani ni las redes de usuarios de Huancasayani.

## Documentos para revisar

- [Expediente PDF](entregables/linea-primaria-r01/Linea_Primaria_Limbani_Huancasayani_R01_expediente.pdf).
- [Memoria de cálculo PDF](entregables/linea-primaria-r01/Linea_Primaria_Limbani_Huancasayani_R01_calculos.pdf).
- [Planos A3 PDF](entregables/linea-primaria-r01/Linea_Primaria_Limbani_Huancasayani_R01_planos.pdf).
- [CAD y capas](entregables/linea-primaria-r01/).
- [Memoria editable por capítulos](expediente/lp-r01/memoria-completa.md).
- [Parámetros y fuentes](datos/lp-r01/).

### Estado de la revisión

El expediente y los cálculos tienen una primera revisión visual. La conversión nativa a DWG, la comprobación final del CAD y la portabilidad de QGIS están en revisión. La entrega es académica de gabinete y no autoriza construir.

El corredor propuesto mide 6,696 km, con 111 apoyos y 110 vanos. Demanda de estudio: 171,49 kW para 353 usuarios potenciales. El modelo de generación necesita aproximadamente 183,31 kW antes de reservar potencia para Limbani. **La referencia de 200 kW no garantiza abastecer ambas localidades ni disponibilidad en estiaje**.

La tensión de 10 kV es una elección condicionada al antecedente de transformación sin placa verificada. Debe cotejarse íntegramente RD 018 y el régimen de electrificación rural; se analiza 22,9 kV como alternativa. Las coordenadas de SE-HUA representan la localidad OSM, no un predio confirmado.

## Reproducción local

Ejecutar desde `G:\Aquiles\instalacion-electricas`:

```powershell
python proyectos/aquiles-limbani-redes/scripts/lp_r01/diseno.py
python proyectos/aquiles-limbani-redes/scripts/lp_r01/cad.py
python proyectos/aquiles-limbani-redes/scripts/lp_r01/documentos.py
& 'C:/Users/51949/AppData/Local/Programs/OSGeo4W/bin/python-qgis.bat' proyectos/aquiles-limbani-redes/scripts/lp_r01/gis.py
python proyectos/aquiles-limbani-redes/scripts/lp_r01/publicar.py
```

Dependencias: Python, numpy, shapely, pyproj, ezdxf, matplotlib, pypdf, PyYAML; reportlab se instaló aisladamente en `G:/Aquiles/dependencias-linea-primaria`. QGIS usa su propio Python. La geometría y los resultados se entregan también como CSV/GeoJSON y GPKG para revisión sin recalcular.

Los originales y fuentes locales permanecen en Descargas y en `fuentes/local/lp-r01/antecedente`, con manifiesto de hashes. No se sobrescribe el CAD original ni el proyecto hidroeléctrico de otro curso. Las rutas de los entregables QGIS son relativas dentro del paquete.

Créditos cartográficos: © OpenStreetMap contributors, ODbL 1.0; catastro local aportado; Mapzen Terrain Tiles y datos globales USGS. Los modelos no equivalen a levantamiento topográfico.
