# Fuentes del proyecto

Guardar aqui, sin modificar:

- consigna y rubrica del docente;
- croquis, planos o fotografias originales;
- fichas y placas de equipos;
- factibilidad o datos de la empresa distribuidora;
- documentos sectoriales recibidos.

Registrar procedencia, fecha, autor y restricciones. Si un archivo es pesado o
privado, normalmente se usa `fuentes/local/`. Por DEC-019 existe una excepción
explícita para reproducir Unidad 2 en Windows: el DXF arquitectónico y las dos
capturas de ubicación están versionados en sus rutas exactas. El resto de
`fuentes/local/`, incluido WhatsApp, continúa ignorado.

## Fuentes recibidas del grupo de WhatsApp

Los archivos del 2026-08-01 se organizaron localmente en:

```text
fuentes/local/whatsapp/
├── consigna/         capturas y fotografias de pizarra
├── normativa/        copias de clase del CNE-U y EM.010
└── material-clase/   selectividad, iluminacion y elaboracion de proyecto
```

Consulta [`inventario-whatsapp.md`](inventario-whatsapp.md) para nombres,
paginas, clasificacion y huellas de integridad. Las copias de normativa
compartidas en clase no sustituyen la comprobacion de vigencia en las fuentes
oficiales.

## Fuente CAD recibida

La copia inmutable del plano se distribuye con el repositorio en:

```text
fuentes/local/cad/DISTRIBUCION Y CIRCULACION MIGUEL.dxf
```

Su procedencia, huella, laminas y datos observados se documentan en
[`inventario-cad.md`](inventario-cad.md). No editar este archivo: los recortes,
limpiezas y bases electricas se regeneran en `build/`.

## Comprobación de un clon nuevo

Desde la raíz, Linux/macOS:

```bash
python proyectos/unidad-2-industrial/scripts/verificar_preparacion.py --solo-fuentes
```

En Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File `
  .\proyectos\unidad-2-industrial\scripts\preparar_windows.ps1 -SoloFuentes
```
