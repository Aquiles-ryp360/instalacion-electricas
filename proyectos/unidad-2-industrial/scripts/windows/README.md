# Automatizacion de AutoCAD en Windows

Estas herramientas trabajan exclusivamente sobre copias regenerables de los
DXF ubicados en `build/`; nunca abren ni modifican `fuentes/local/`.

Preparacion del entorno:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r proyectos\unidad-2-industrial\requirements-windows.txt
```

Antes del primer uso desatendido, abra AutoCAD 2027 manualmente una vez,
complete cualquier dialogo de licencia/inicializacion y cierrelo. Luego genere
los seis planos y ejecute:

```powershell
powershell -ExecutionPolicy Bypass -File `
  proyectos\unidad-2-industrial\scripts\windows\auditar-planos-autocad.ps1
```

El script detecta `AcCoreConsole.exe`, copia `IE-*.dxf` a
`build/unidad-2-industrial/cad/autocad-audit/`, ejecuta `AUDIT` y guarda un log
por lamina. Un timeout o codigo de salida distinto de cero hace fallar el
comando. Las copias auditadas no sustituyen al generador canonico.

En la prueba del 2026-08-02 tanto Core Console como COM quedaron detenidos en
la inicializacion de AutoCAD. El wrapper queda preparado, pero no se declara
una auditoria de los planos hasta que la licencia se inicialice y se repita el
comando con los DXF reales.
