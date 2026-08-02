# Preparación completa en Windows

## Actualizar el clon

Desde la terminal integrada de Codex:

```powershell
git status --short
git fetch --all --prune
git switch main
git pull --ff-only origin main
```

No ejecutar el `pull` si existen cambios sin guardar. En ese caso, conservarlos
y usar un worktree o integrar `origin/main` en la rama experimental.

## Comprobar todas las fuentes

```powershell
powershell -ExecutionPolicy Bypass -File `
  .\proyectos\unidad-2-industrial\scripts\preparar_windows.ps1 -SoloFuentes
```

El resultado correcto es `READY` para seis recursos: DXF, dos capturas, logo
SVG/PDF y evidencia comercial base. El verificador comprueba existencia,
seguimiento por Git y SHA-256; no acepta archivos sustitutos.

## Preparar Python

```powershell
powershell -ExecutionPolicy Bypass -File `
  .\proyectos\unidad-2-industrial\scripts\preparar_windows.ps1
```

El script crea `.venv`, instala `requirements.txt` y vuelve a verificar. Para
la compilación completa deben estar disponibles `latexmk` y `pdflatex`; pueden
obtenerse instalando MiKTeX o TeX Live. AutoCAD 2027, COM, AcCoreConsole y las
herramientas Poppler aparecen como opcionales porque mejoran auditoría y
diagnóstico, pero el generador Python no depende de ellos.

## Regenerar desde cero

```powershell
.\.venv\Scripts\python.exe `
  .\proyectos\unidad-2-industrial\scripts\compilar_expediente.py `
  --regenerar-planos

.\.venv\Scripts\python.exe `
  .\proyectos\unidad-2-industrial\scripts\preparar_paquete_academico.py

make test PYTHON=.venv\Scripts\python.exe
```

Si `make` no está instalado, ejecutar directamente:

```powershell
.\.venv\Scripts\python.exe -m pytest -q `
  herramientas\cotizacion\v0_legacy\tests `
  herramientas\cotizacion\v1\tests `
  proyectos\renzo\tests `
  proyectos\unidad-2-industrial\tests
```

La compilación usa el logo y la evidencia comercial base versionados cuando no
hay red. Una consulta Promelsa nueva continúa siendo opcional y nunca modifica
automáticamente el presupuesto instalado.
