# Expediente academico del grifo

Las fuentes LaTeX de esta carpeta documentan el anteproyecto nuevo de Aquiles
Taylor Ramos Yapo. La presentacion reutiliza el lenguaje grafico del expediente
Aquiles de la primera unidad: papel carta, portada azul/verde, encabezado
enmarcado, titulos rojos y pie tecnico. Los valores numericos no se copian a
mano: `../scripts/generar_fragmentos_expediente.py` los toma de resultados PASS.

Compilacion desde la raiz del repositorio:

```bash
.venv/bin/python proyectos/unidad-2-industrial/scripts/calcular_proyecto.py
.venv/bin/python proyectos/unidad-2-industrial/scripts/calcular_alumbrado.py
.venv/bin/python proyectos/unidad-2-industrial/scripts/calcular_metrados_presupuesto.py
.venv/bin/python proyectos/unidad-2-industrial/scripts/preparar_recursos_expediente.py
.venv/bin/python proyectos/unidad-2-industrial/scripts/generar_fragmentos_expediente.py
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -outdir=build/unidad-2-industrial/expediente \
  -cd proyectos/unidad-2-industrial/expediente/main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -jobname=guia-sustentacion \
  -outdir=build/unidad-2-industrial/expediente \
  -cd proyectos/unidad-2-industrial/expediente/guia-sustentacion.tex
.venv/bin/python proyectos/unidad-2-industrial/scripts/preparar_paquete_academico.py
```

El PDF se conserva en `build/` hasta terminar la revision. La portada distingue
al estudiante, al propietario consignado en la referencia y al docente actual;
no afirma aprobacion de la DREM ni consigna CIP, sello o firma inventados.
Los planos anexos se incorporan como PDF vectorial A1; no deben convertirse a
PNG/JPEG para la entrega. Las PNG generadas son solo vistas previas. La
composicion conserva el formato Aquiles, pero sustituye su escudo raster de
113 x 124 px por el SVG publicado en el dominio oficial de la UNAP, con huella
verificada por `preparar_recursos_expediente.py`.

El expediente sigue la secuencia de la primera unidad: memoria, calculos,
especificaciones/ejecucion, cronograma, metrados y presupuesto, planos,
conclusiones y anexos. La guia de sustentacion se compila aparte para uso
personal y no se adjunta automaticamente al informe que se entrega.
