PYTHON ?= python3
PROYECTO_INDUSTRIAL ?= nave-industrial

.PHONY: install test test-tools test-renzo aquiles renzo nave-industrial clean

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -q herramientas/cotizacion/v0_legacy/tests proyectos/renzo/tests

test-tools:
	$(PYTHON) -m pytest -q herramientas/cotizacion/v0_legacy/tests

test-renzo:
	$(PYTHON) -m pytest -q proyectos/renzo/tests

aquiles:
	$(PYTHON) herramientas/pipeline_automatizado.py --proyecto aquiles

renzo:
	$(PYTHON) herramientas/pipeline_automatizado.py --proyecto renzo

nave-industrial:
	$(PYTHON) herramientas/pipeline_automatizado.py --proyecto $(PROYECTO_INDUSTRIAL)

nave-industrial-planos:
	$(PYTHON) proyectos/$(PROYECTO_INDUSTRIAL)/scripts/generar_planos_industriales.py \
		--electrical proyectos/$(PROYECTO_INDUSTRIAL)/diseno-electrico/datos/cargas-industriales.json \
		--view completo \
		--output build/$(PROYECTO_INDUSTRIAL)/planos/

nave-industrial-calculos:
	$(PYTHON) proyectos/$(PROYECTO_INDUSTRIAL)/scripts/calcular_maxima_demanda.py \
		proyectos/$(PROYECTO_INDUSTRIAL)/diseno-electrico/datos/cargas-industriales.json \
		build/$(PROYECTO_INDUSTRIAL)/calculos/resultados.json

clean:
	rm -rf build
