PYTHON ?= python3
PROYECTO_INDUSTRIAL ?= nave-industrial

.PHONY: install test test-tools test-renzo aquiles renzo nave-industrial nave-industrial-planos nave-industrial-calculos nave-industrial-expediente nave-industrial-bom nave-industrial-test clean

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -q herramientas/cotizacion/v0_legacy/tests proyectos/renzo/tests proyectos/$(PROYECTO_INDUSTRIAL)/tests

test-tools:
	$(PYTHON) -m pytest -q herramientas/cotizacion/v0_legacy/tests

test-renzo:
	$(PYTHON) -m pytest -q proyectos/renzo/tests

aquiles:
	$(PYTHON) herramientas/pipeline_automatizado.py --proyecto aquiles

renzo:
	$(PYTHON) herramientas/pipeline_automatizado.py --proyecto renzo

nave-industrial: nave-industrial-calculos nave-industrial-planos nave-industrial-expediente nave-industrial-excel

nave-industrial-excel:
	$(PYTHON) proyectos/$(PROYECTO_INDUSTRIAL)/scripts/generar_excel_reportes.py

nave-industrial-planos:
	$(PYTHON) proyectos/$(PROYECTO_INDUSTRIAL)/scripts/generar_planos_industriales.py \
		--electrical proyectos/$(PROYECTO_INDUSTRIAL)/diseno-electrico/datos/cargas-industriales.json \
		--view completo \
		--output build/$(PROYECTO_INDUSTRIAL)/planos/
	mkdir -p proyectos/$(PROYECTO_INDUSTRIAL)/entregables
	cp build/$(PROYECTO_INDUSTRIAL)/planos/*.pdf proyectos/$(PROYECTO_INDUSTRIAL)/entregables/ 2>/dev/null || true

nave-industrial-calculos:
	$(PYTHON) proyectos/$(PROYECTO_INDUSTRIAL)/scripts/calcular_maxima_demanda.py \
		proyectos/$(PROYECTO_INDUSTRIAL)/diseno-electrico/datos/cargas-industriales.json \
		build/$(PROYECTO_INDUSTRIAL)/calculos/resultados.json

nave-industrial-expediente:
	mkdir -p proyectos/$(PROYECTO_INDUSTRIAL)/expediente/figuras
	cp build/$(PROYECTO_INDUSTRIAL)/planos/*.png proyectos/$(PROYECTO_INDUSTRIAL)/expediente/figuras/ 2>/dev/null || true
	cd proyectos/$(PROYECTO_INDUSTRIAL)/expediente && pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1; \
	mkdir -p ../../../build/$(PROYECTO_INDUSTRIAL)/expediente; \
	cp main.pdf ../../../build/$(PROYECTO_INDUSTRIAL)/expediente/expediente.pdf; \
	cp main.pdf ../../../proyectos/$(PROYECTO_INDUSTRIAL)/entregables/expediente.pdf

nave-industrial-bom:
	$(PYTHON) proyectos/$(PROYECTO_INDUSTRIAL)/scripts/generar_bom.py

nave-industrial-test:
	$(PYTHON) -m pytest -q proyectos/$(PROYECTO_INDUSTRIAL)/tests/

clean:
	rm -rf build
