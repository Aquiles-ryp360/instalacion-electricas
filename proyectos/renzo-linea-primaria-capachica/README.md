# Proyecto: Línea Primaria y Subestación de Distribución — Capachica

**Curso:** Instalaciones Eléctricas II (MEC330)  
**Semestre Académico:** 2026-II | IX Ciclo  
**Facultad:** FIME — Escuela Profesional de Ingeniería Mecánica Eléctrica | UNA Puno  
**Docentes:** Ing. Leonidas Vilca Callata / Ing. Marcos José Villanueva Cornejo  
**Estudiante:** Renzo Gabriel Mamani Galindo (Cód. 228447)  

---

## 1. Resumen Ejecutivo del Proyecto

Diseño definitivo de una **Línea Primaria de Distribución en Media Tensión (22.9 kV)** y una **Subestación de Distribución Proyectada (SED)** para la electrificación de una localidad rural adyacente al sector **Chifrón, Distrito de Capachica, Puno**.

El punto de diseño y derivación está validado en la infraestructura oficial de **Electro Puno S.A.A.** extraída del geovisor **GISEM de OSINERGMIN**:
- **Tramo MT existente:** `TMT000012389` / `TMT001847370`
- **Punto de Conexión / Derivación (E-01):** Estructura en cresta del Cerro Chifrón (red existente Electro Puno).
  - Coordenadas UTM WGS-84 Zona 19S:
    - Este (X): `412,606.01 m E`
    - Norte (Y): `8,270,712.24 m N`
    - Cota: `3,924.17 msnm` (Progresiva `0+000.00 m`)
    - Latitud: `-15.640067° S`, Longitud: `-69.815400° W`
- **Subestación de Distribución Biposte Proyectada (SED E-04):**
  - Coordenadas UTM WGS-84 Zona 19S:
    - Este (X): `412,759.20 m E`
    - Norte (Y): `8,270,976.22 m N`
    - Cota: `3,839.56 msnm` (Progresiva `0+305.21 m`)
    - Potencia: `100 kVA`, $22.9 / 0.38 - 0.22\text{ kV}$, Grupo Dyn5
  - Altitud de diseño del proyecto: `3,817.04` a `3,924.17 msnm` (Media: `3,850 msnm`)

---

## 2. Flujo de Ingeniería y Automatización

```mermaid
flowchart LR
    A["Google Earth Pro
Ruta KML desde E0"] --> B["TopoMagic
Perfil Topográfico DEM"]
    B --> C["RedCAD
Cálculo Mecánico & Spotting"]
    C --> D["AutoCAD / QElectroTech
Planos Ejecutivos & Unifilar"]
    D --> E["Expediente Técnico
Memoria Descriptiva & Cálculos"]
```

1. **Google Earth Pro (`fuentes/kml/`):** Trazado de ruta siguiendo accesos rurales, minimizando ángulos y evitando zonas bajas/inundables del Lago Titicaca.
2. **TopoMagic (`datos/topografia/`):** Extracción de perfil longitudinal del terreno con cotas y progresivas.
3. **RedCAD (`diseno-electrico/` y `calculo-mecanico/`):**
   - Distribución de postes de Concreto Armado Centrifugado (C.A.C. 12/300 y 12/400).
   - Cálculo de vano peso, vano eólico y catenarias bajo 5 hipótesis climáticas del CNE Suministro para Puno (>3800 msnm).
   - Cálculo de caída de tensión ($\Delta V\% < 5.0\%$) y pérdidas en MT.
4. **Expediente Técnico (`expediente/`):**
   - Memoria Descriptiva.
   - Especificaciones Técnicas de Suministro y Montaje.
   - Memoria de Cálculos Eléctricos y Mecánicos.
   - Metrados y Presupuesto referencial.
   - Planos ejecutivos en `entregables/planos/`.

---

## 3. Estructura de Directorios

- `fuentes/`: Archivo KML original de Google Earth, datos de GISEM y archivos `.top` de TopoMagic.
- `datos/`: Parámetros canónicos del proyecto, tablas de conductores y catálogo de postes.
- `documentacion/`: Supuestos normativos (CNE Suministro 2011, Norma DGE ER) y registro de decisiones.
- `diseno-electrico/`: Memorias y scripts de caída de tensión y pérdidas.
- `calculo-mecanico/`: Hojas y scripts de catenaria y ecuación de cambio de estado.
- `expediente/`: Fuentes Markdown / LaTeX para el informe final.
- `entregables/`: PDF final del expediente y planos DWG listos para entrega.
- `scripts/`: Herramientas en Python para automatizar el cálculo de ingeniería.
