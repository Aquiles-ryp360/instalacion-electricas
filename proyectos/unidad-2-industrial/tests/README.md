# Pruebas del proyecto

`test_calculos.py` vuelve a ejecutar el calculo canonico y comprueba:

- demanda, reserva y balance de fases;
- ampacidad, caida de tension y diferenciales de cada circuito;
- capacidad del grupo electrogeno corregida por altitud;
- coherencia del rotulo UNAP, autor, propietario y exclusiones;
- integridad SHA-256 de la copia local del DXF, cuando esta disponible.
- reproduccion del metrado/presupuesto y su rotulo de costo referencial;
- consistencia de los datos clave de la guia de sustentacion.

Ejecutar desde la raiz del repositorio:

```bash
.venv/bin/pytest -q proyectos/unidad-2-industrial/tests
```
