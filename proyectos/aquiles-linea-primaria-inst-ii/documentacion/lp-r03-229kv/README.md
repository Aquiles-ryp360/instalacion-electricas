# LP-R03-229KV — Carpeta de trabajo profesional

**Adoptado:** diseño nominal trifásico de **22,9 kV**. **Estado:** ingeniería en revisión (no aprobado para construcción).
**Rama de trabajo:** `aquiles/lp-229kv-profesional-r03` en fork `Aquiles-ryp360/instalacion-electricas`.

## Qué se incorporó sin alterar M01
- `proyecto.yaml`: tensión **de diseño adoptada**, distinta de `tension_confirmada_kv: null` porque no hay placas.
- `datos/lp-r03-229kv/escenario.json`: entradas seleccionadas y pendientes.
- `datos/lp-r03-229kv/resultados_referenciales_229kv.json`: tres casos 22,9 kV tomados del cálculo eléctrico del R02, con balance de potencia y variación BT.
- `DECISION_TENSION_229KV.md`: sustentación, riesgos, normas aplicables y cierres requeridos.
- `MATRIZ_111_ARMADOS_CAC_229KV.csv`: correspondencia por poste del inventario M01 a referencias DGE y alertas geométricas.
- `ALERTAS_ARMADOS_229KV.json`: ocho incidencias, incluidas las retenciones de giros altos y P019.
- `scripts/lp_r03/evaluar_229kv.py`: recálculo eléctrico reproducible con cotejo de tres resultados M01.
- `scripts/lp_r03/estilo_cad_229kv.py`: genera copia DXF con jerarquía por capas, ocho leyendas, control de revisión y LP-20 a 22,9 kV; no modifica coordenadas ni referencias DGE.

## Ejecutar sin tocar los entregables actuales
Desde la raíz del repositorio, después de instalar las dependencias de LP-R02:

```bash
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r03/evaluar_229kv.py --salida build/lp-r03-229kv-calculos
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r03/estilo_cad_229kv.py \
  proyectos/aquiles-linea-primaria-inst-ii/entregables/proyecto-final/04_Planos/Linea_Primaria.dxf \
  build/lp-r03-229kv-planos/Linea_Primaria_R03_229kv.dxf \
  --informe build/lp-r03-229kv-planos/control.json
```

Estos programas **no sobrescriben** archivos ni editan `main`. El DXF generado **no es el plano definitivo**: LP-01..LP-19 contienen datos históricos de M01 / 10 kV; LP-20 muestra el criterio adoptado para iniciar la actualización. No publicar un expediente mezclando ambas tensiones.

## Entrega ejecutiva pendiente — no marcar como cerrada sin evidencias
1. Verificar entradas reales (placas de generador/T1/T2, P firme de estiaje, demanda, regulación, condición de neutro).
2. Calcular y documentar diseño a 22,9 kV: flujo, cortocircuito 3F/1F/2F, selectividad, coordinación de aislamiento y descargadores, PAT y régimen aislado.
3. Desarrollar armados CAC de 22,9 kV dimensionales con códigos, BOM, esfuerzos, aislamiento y referencias del fabricante; confirmar P003/P035/P057 y los 46 apoyos con carga ascendente.
4. Topografía, perfiles, gálibos, cruzamientos, pedestales/cimentaciones, anclajes, predios, accesos y geotecnia.
5. Recalcular de las mismas entradas `Metrados.xlsx`, `Calculos.xlsx`, `Presupuesto.xlsx`, los 111 inventarios, memoria y planos; comprobar diferencias y retirar declaraciones de 10 kV de toda lámina vigente.
6. Imprimir A3 de prueba, revisar grosor pluma, contraste, escalas, CAD/XREF, bloque de revisión, cajetín, leyendas y compatibilidad DWG; verificar apertura DWG real si se convierte.
7. Aprobar revisión de ingeniería mediante profesional competente, con evidencias y registros.

**No alterar** el proyecto de Centrales Hidroeléctricas, ni inferir que 22,9 kV asegura potencia hídrica firme. Los anteriores 200 kW/250 kVA son solo hipótesis mientras no se verifican equipos.
