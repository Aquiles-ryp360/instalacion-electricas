# Expediente preliminar Capachica–Llachón, Rev. 1

Este es un **borrador técnico para revisión**, con siete capítulos editables y dos planos A3. La compilación local produce un PDF de 12 páginas y un ZIP con los DXF, fuentes y datos trazables. No es un expediente definitivo de construcción.

| Orden | Capítulo |
|---|---|
| 00 | [Portada y control](00_portada_control.md) |
| 01 | [Memoria descriptiva](01_memoria_descriptiva.md) |
| 02 | [Bases de diseño y cálculos](02_bases_y_calculos.md) |
| 03 | [Especificaciones y levantamiento](03_especificaciones_y_levantamiento.md) |
| 04 | [Metrados, presupuesto y cronograma](04_metrados_presupuesto_cronograma.md) |
| 05 | [Planos y anexos](05_planos_y_anexos.md) |
| 06 | [Observaciones y cierre](06_observaciones_y_cierre.md) |

En la máquina de trabajo, el PDF y ZIP compilados están en `build/renzo-linea-primaria-capachica-llachon/`. Para compilar desde una copia donde no existan esas salidas:

```powershell
python proyectos/renzo-linea-primaria-capachica-llachon/scripts/compilar_expediente.py
```

Se necesitan Python con las dependencias del [proyecto](../requirements.txt) y `pandoc` disponible en `PATH`. El script **no sobrescribe** un paquete Rev. 1 existente. Las cantidades y precios de obra siguen pendientes; [matriz de metrados](../datos/matriz_metrados_pendientes.csv).
