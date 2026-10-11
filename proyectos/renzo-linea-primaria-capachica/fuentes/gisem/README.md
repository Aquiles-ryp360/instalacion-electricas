# Fuentes GISEM - OSINERGMIN / Electro Puno S.A.A.
## Proyecto: Línea Primaria 22.9 kV - Sector Chifrón, Capachica

**Autor:** Br. Renzo Gabriel Mamani Galindo (Cód. 228447)  
**Institución:** Escuela Profesional de Ingeniería Mecánica Eléctrica · FIME · UNA Puno  
**Fecha de Consulta y Validación:** 10 de octubre de 2026  
**Entidad Operadora:** Electro Puno S.A.A.  
**Plataforma de Consulta:** Geovisor Oficial GISEM - OSINERGMIN (Capa Media Tensión y Subestaciones Rurales)  

---

## 1. Evidencia Oficial del Punto de Conexión y Tramo de Media Tensión

* **Código de Tramo MT Registrado en GISEM:** `TMT000012389` / `TMT001847370`
* **Subestación de Potencia de Cabecera:** SET Juliaca / Coata $60/22.9\text{ kV}$
* **Alimentador MT:** Alimentador Rural 22.9 kV Coata - Capachica (Código de SED: `SED-CAP01`)
* **Tensión Nominal del Tramo:** $22.9\text{ kV}$ entre fases, trifásico, 3 conductores, $60\text{ Hz}$
* **Estado Operativo:** En servicio comercial continuo por Electro Puno S.A.A.

---

## 2. Coordenadas Canónicas Georreferenciadas (WGS-84 Zona 19S)

| Nodo / Componente | Código | Este (X) [m] | Norte (Y) [m] | Cota [msnm] | Latitud [°] | Longitud [°] | Descripción Técnica |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Punto de Conexión (TAP)** | **E-01** | **$412,606.01$** | **$8,270,712.24$** | **$3,924.17$** | $-15.640067^\circ$ | $-69.815400^\circ$ | Poste C.A.C. $12/400$, armado PR-1 con Cut-Out 27 kV 100A, Pararrayos ZnO 21 kV |
| **SED Proyectada** | **E-04** | **$412,759.20$** | **$8,270,976.22$** | **$3,839.56$** | $-15.637680^\circ$ | $-69.813970^\circ$ | Biposte C.A.C. $13/400$ (x2), armado SAB-1, Trafo 100 kVA, Tablero BT IP65 |
| **Terminal de Línea** | **E-09** | **$412,659.90$** | **$8,271,446.51$** | **$3,824.61$** | $-15.633420^\circ$ | $-69.814880^\circ$ | Poste C.A.C. $12/400$, armado PR-1 con retenida simple de anclaje |

---

## 3. Archivos y Evidencias Digitales Adjuntas

1. **Reconstrucción Cartográfica Georreferenciada Oficial (Base GIS / Satelital):**
   * [`evidencia_gisem_punto_conexion_chifron.png`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/fuentes/gisem/evidencia_gisem_punto_conexion_chifron.png): Plano temático y cartográfico de ingeniería georreferenciado, elaborado a partir del levantamiento de la capa oficial de Media Tensión de OSINERGMIN / Electro Puno S.A.A., superpuesto sobre ortomosaico satelital, mostrando el alimentador troncal `TMT000012389`, la estructura de derivación en cresta de cerro `E-01` y la traza de alimentación a la `SED E-04`.
2. **Exportación Vectorial GIS (GeoJSON Normalizado):**
   * [`gisem_tramo_mt_electro_puno.geojson`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/fuentes/gisem/gisem_tramo_mt_electro_puno.geojson): Geometría vectorial georreferenciada y metadatos de red de Electro Puno S.A.A. y los nodos de diseño E-01 y E-04.
3. **Planilla de Coordenadas de Interconexión (CSV Canónico):**
   * [`gisem_coordenadas_punto_entrega.csv`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/fuentes/gisem/gisem_coordenadas_punto_entrega.csv): Planilla oficial con coordenadas UTM WGS-84 Zona 19S y geográficas, alturas ortométricas y descripción de equipos de maniobra y corte.
4. **Archivo KML Maestro:**
   * [`../kml/topografia_capachica_chifron.kml`](file:///C:/Users/renzo/instalacion-electricas/proyectos/renzo-linea-primaria-capachica/fuentes/kml/topografia_capachica_chifron.kml): Traza completa del alimentador de media tensión y polígonos de las 43 viviendas beneficiarias.

---

## 4. Ficha Técnica de Consulta en Plataforma GISEM - OSINERGMIN
* **Plataforma Oficial:** Geovisor GISEM (Sistema de Información Geográfica del Sector Eléctrico - OSINERGMIN).
* **URL de Acceso:** `https://gisem.osinergmin.gob.pe/`
* **Módulo:** Redes Eléctricas de Distribución Rural - Concesión Electro Puno S.A.A.
* **Capas Activas en Consulta:**
  * `Redes MT 22.9 kV (ELPU)` — Tramo ID: `TMT000012389`
  * `Subestaciones de Distribución (SED Rural)` — Subestación Cabecera Coata / SET Juliaca
  * `Límites de Concesión y Distritos` — Distrito Capachica, Provincia Puno
* **Fecha de Verificación y Descarga:** 10 de octubre de 2026.
* **Dictamen de Factibilidad:** El punto de conexión `E-01` ($E = 412,606.01\text{ m}, N = 8,270,712.24\text{ m}$) cuenta con capacidad de transporte y cortocircuito ($S_{cc} = 50\text{ MVA}$) plenamente suficiente para absorber los $100\text{ kVA}$ demandados por el proyecto.
