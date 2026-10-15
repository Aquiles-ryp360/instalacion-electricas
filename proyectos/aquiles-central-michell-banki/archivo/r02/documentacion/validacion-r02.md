# Validación R02 - 13 de octubre de 2026

## Resultado y cambios respecto de R01

R01 contenía trabajo útil de revisión, pero no cerraba inventario operativo con exportación ni extendía la alternativa de 500 mm a mecánica y metrado. R02 conserva el original y los dos PDF R01 en `build/aquiles-minicentral-limbani/archivo-r01/`. Los datos vigentes están en `datos/parametros.json`; el informe de auditoría proviene de `datos/revision-r02.json`.

- Generación auxiliar: 5.10 kW y 3.280 kvar por equipos activos. Mantenimiento: 9.30 kW, con grupo parado. Reserva de drenaje condicionada a exclusión de una bomba.
- Pérdida TSA de generación: 0.120855 kW, con placa/pérdidas hipotéticas. No se confunde con carga.
- Di450: 147.822103 kW PCC; Di500: 151.154637 kW; Di550: 152.991269 kW.
- Q para 150 kW PCC: 426.760 l/s con Di450; 416.668 l/s con Di500. Q para sensibilidad 157.5 kW en Di500: 438.416 l/s.
- En Di500, cierre lento de 4 s: cribado 7.454 bar. Cierre abrupto ideal: 28.326 bar. No constituyen presiones aprobadas por MOC.
- Espesor efectivo de sensibilidad: 4.55625 mm, desde nominal 6.35 mm, tolerancia 12.5% y corrosión 1 mm (hipótesis, no norma de producto).
- Masa envolvente Di500: 17444.830 kg; aumento frente a Di450: 1722.606 kg. No incluye accesorios ni masas de catálogo.
- Reja: porosidad 0.60 añadida; área bruta mínima de estudio 1.94444 m². El valor R01 de 1.17 m² omitía la fracción abierta.

## Evidencia normativa y lectura

- CNE-S Tabla 232-1: PDF físico 131 / página impresa 126. Columna conductor expuesto >750 V a 23 kV. Se leen filas 2.a, 2.b, 4, 5.a y 5.b. Valores 7.0, 6.5, 6.5, 5.0 y 6.5 m, condicionados al encabezado, notas y demás reglas; no son distancias medidas.
- CNE-S 232.C.1.b: página impresa 123; el aumento por altitud tiene alcance específico, no toda separación a 22.9 kV.
- CNE-U 050-104(3)-(7), 050-106(3),(5) y nota de Anexo B. Se desarrollan marcado y carga continua sin imponer 1.25 universal.
- CNE-U D8A: PDF físico 737 / Anexo D pág. 3; D8B: físico 738 / Anexo D pág. 4. Para Cu240 detalle 4: D8A446 y D8B442; detalle 7: D8A390 y D8B386. Configuración y condiciones térmicas pendientes.
- CNE-U Tabla 2: B2/PVC70/tres cargados/Cu6 -> 34 A; ejemplo de utilización, no cable de generación seleccionado.
- D.S. 023-2014-MINAGRI: texto SPIJ descargado, artículos modificados 79, 81, 84, 85. La aprobación de RJ007-2015 no contiene el reglamento y los 24 formatos completos; no se afirma haberlos leído íntegramente.
- USBR EM03: referencia técnica histórica, páginas impresas 11 (ariete) y 19 (apoyos/térmica); no reglamento peruano ni admisibles modernos.

## Verificación de implementación

13 pruebas de `unittest` pasaron: Colebrook, conservación hidráulica, geometría imposible, régimen transitorio, flujo uniforme, trifásico, cargas/reactiva por equipo, cierre de exportación, sensibilidad de auxiliares, escala de viga, porosidad, sedimentación e inválidos/no finitos. No se interpreta como comprobación de seguridad de una central real.

El libro de energía cierra con residuo menor que 1e-9 kW. Las cantidades TF01, TF02 y MT01 se derivan del escenario en `metrados_calculados.csv`; no se copian manualmente al capítulo 7. El manifiesto incluye motor genérico, scripts, entradas, escudo y fuentes locales disponibles.

## Límites que siguen abiertos

No hay serie de caudales, aforos, demanda externa, topografía, geotecnia, resistividad, condiciones de red ni garantías de equipos. Las eficiencias permanecen constantes solo para sensibilidad. La magnetización y reactiva de dispersión de transformadores no se modelan; el balance es aproximación activa, no flujo AC. El transitorio no incluye MOC, perfil real, vacío ni sobrevelocidad. La viga no incluye esfuerzos locales, juntas, suelo ni sismo. No hay presupuesto definitivo ni renta calculada. Los esquemas son conceptuales.

La revisión de documentos legales es dirigida y trazada, sin afirmar consolidación total ni permisos otorgados. La elección de emplazamiento, meta en PCC y modo de red sigue pendiente de rúbrica docente.
