# Fuentes del proyecto

Guardar aqui, sin modificar:

- consigna y rubrica del docente;
- croquis, planos o fotografias originales;
- fichas y placas de equipos;
- factibilidad o datos de la empresa distribuidora;
- documentos sectoriales recibidos.

Registrar procedencia, fecha, autor y restricciones. Si un archivo es pesado o
privado, usar `fuentes/local/`, que esta ignorado por Git, y dejar aqui una
referencia sin datos sensibles.

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

La copia inmutable del plano se guarda localmente en:

```text
fuentes/local/cad/DISTRIBUCION Y CIRCULACION MIGUEL.dxf
```

Su procedencia, huella, laminas y datos observados se documentan en
[`inventario-cad.md`](inventario-cad.md). No editar este archivo: los recortes,
limpiezas y bases electricas se regeneran en `build/`.
