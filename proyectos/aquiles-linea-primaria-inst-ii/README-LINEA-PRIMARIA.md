# Reproducción yestadoLP-R02

Leer [proyecto.yaml](proyecto.yaml) y [continuidad paraIA](documentacion/lp-r02/CONTINUIDAD_IA.md). La navegación porocho carpetas estáen [README](README.md).

```bash
python3 -m pip install -r proyectos/aquiles-linea-primaria-inst-ii/requirements-lp-r02.txt
python3 -m unittest herramientas.lineas_primarias.tests.test_revision -v
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/construir.py --salida build/aquiles-linea-primaria-inst-ii/lp-r02-reproduccion
python3 proyectos/aquiles-linea-primaria-inst-ii/scripts/lp_r02/verificar.py --salida build/aquiles-linea-primaria-inst-ii/lp-r02-reproduccion
```

Elconstructor rechazasobrescritura; utilizar unacarpeta nueva. Lasfuentes técnicas son `datos/lp-r02`, el motor genérico `herramientas/lineas_primarias/revision.py` ylos generadores `scripts/lp_r02`. ElPDFde planos se renderiza delDXFguardado; no se declaraDWG convertido sinreapertura nativa.

Para editar resultados, cambiar entradas verificadas yregenerar. Para texto, cambiar elgenerador editorial yrevisar elMarkdown exportado. La curvade fluencia, aisladoresrígidos yretenidas ideales son hipótesis explícitas. No confundir una comprobación informática con aprobación de ingeniería.

Los tresZIPde referencia se abrieron ycomprobaronCRC; elinventarioestá en `documentacion/lp-r02/inventarios`. EnSEACE se descargaron contratos ylaficha13/400; no se consiguióelETOcompleto desus procedimientos. Los planos comparables adicionales son recursosSINIA.
