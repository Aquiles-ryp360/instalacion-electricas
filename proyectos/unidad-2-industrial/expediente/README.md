# Expediente academico del grifo

Las fuentes LaTeX de esta carpeta documentan el anteproyecto nuevo de Aquiles
Taylor Ramos Yapo. La presentacion reutiliza el lenguaje grafico del expediente
Aquiles de la primera unidad: papel carta, portada azul/verde, encabezado
enmarcado, titulos rojos y pie tecnico. Los valores numericos no se copian a
mano: `../scripts/generar_fragmentos_expediente.py` los toma de resultados PASS.

Compilacion desde la raiz del repositorio:

```bash
.venv/bin/python proyectos/unidad-2-industrial/scripts/compilar_expediente.py
.venv/bin/python proyectos/unidad-2-industrial/scripts/preparar_paquete_academico.py
```

Para regenerar tambien las seis laminas antes de compilar:

```bash
.venv/bin/python proyectos/unidad-2-industrial/scripts/compilar_expediente.py \
  --regenerar-planos
```

`--regenerar-planos` reextrae primero A-01 del DXF local y genera su vista PDF
directamente como vector. Para actualizar solo esa base use
`--regenerar-base-cad`.

El script usa un `outdir` absoluto. No usar `latexmk -cd` con un `outdir`
relativo, porque crea por error una carpeta `build/` dentro de `expediente/`.
La consulta comercial se actualiza por separado con los comandos de
`../presupuesto/README.md`; compilar no debe depender de la red ni cambiar
precios del presupuesto academico.

El PDF se conserva en `build/` hasta terminar la revision. La portada distingue
al estudiante, al propietario consignado en la referencia y al docente actual;
no afirma aprobacion de la DREM ni consigna CIP, sello o firma inventados.
Las capturas catastral y satelital son raster porque constituyen evidencia
recibida; el croquis A-01 y los planos anexos se mantienen vectoriales. Los
planos A1 no deben convertirse a PNG/JPEG para la entrega. Las PNG generadas
son solo vistas previas. La
composicion conserva el formato Aquiles, pero sustituye su escudo raster de
113 x 124 px por el SVG publicado en el dominio oficial de la UNAP, con huella
verificada por `preparar_recursos_expediente.py`.

El expediente sigue la secuencia de la primera unidad: memoria, calculos,
especificaciones/ejecucion, cronograma, metrados y presupuesto, planos,
conclusiones y anexos. La guia de sustentacion se compila aparte para uso
personal y no se adjunta automaticamente al informe que se entrega.
