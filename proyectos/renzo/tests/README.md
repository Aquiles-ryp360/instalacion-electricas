# Tests del proyecto Renzo

Pruebas automatizadas especificas del proyecto. Validan reglas y calculos
locales antes de regenerar entregables.

- `test_circuitos.py`: consistencia de circuitos del modelo electrico.
- `test_conductores.py`: criterios de conductores y protecciones.
- `test_demanda.py`: calculo de demanda del proyecto.
- `test_presupuesto.py`: datos usados para presupuesto y metrados.

Ejecutar desde la raiz del repositorio:

```bash
python3 -m pytest -q proyectos/renzo/tests
```

Estas pruebas no sustituyen la revision tecnica del expediente ni la inspeccion
visual de planos generados en `build/renzo/`.
