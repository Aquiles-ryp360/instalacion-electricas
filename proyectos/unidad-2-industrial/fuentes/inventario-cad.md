# Inventario de la fuente CAD

## CAD-001

- Archivo recibido: `/home/kimdokja/Downloads/DISTRIBUCION Y CIRCULACION MIGUEL.dxf`
- Copia local inmutable: `fuentes/local/cad/DISTRIBUCION Y CIRCULACION MIGUEL.dxf`
- Fecha de incorporacion: 2026-08-01
- Tamano: 48 638 066 bytes
- SHA-256 original: `7980dda84d5ea40ed85e5458b487edfc219584d8c4b6e62f7fd9442e7443d805`
- SHA-256 copia: `7980dda84d5ea40ed85e5458b487edfc219584d8c4b6e62f7fd9442e7443d805`
- Integridad: verificada; ambas huellas coinciden
- Formato interno: DXF AutoCAD 2018 (`AC1032`)
- `$INSUNITS`: 4 (milimetros), aunque la escala impresa, las cotas y las
  coordenadas utiles se comportan como metros; esta discrepancia se registra
  como condicion de interpretacion, no se corrige en la fuente.
- Autor/ultima escritura informado por metadato: Aquiles
- Restriccion: conservar sin modificar; las copias recortadas o limpiadas son
  productos regenerables y se guardan en `build/`.

## Contenido observado

El espacio modelo contiene tres laminas completas:

| Lamina | Titulo | Marco aproximado en coordenadas del DXF |
|---|---|---|
| A-01 | Distribucion y circulacion | X 1596.7895--1764.9895; Y 1521.3837--1640.1837 |
| S-01 | Seguridad y SCI | X 1791.8270--1960.0270; Y 1521.3837--1640.1837 |
| M-01 | Monitoreo | X 1982.3884--2150.5884; Y 1518.1668--1636.9668 |

Datos principales transcritos:

- proyecto fuente: `CONSTRUCCION DE EE.SS`;
- propietario consignado: Miguel Mamani Chuquicallata;
- ubicacion: predio rustico Reumita, parcelas B-8/B-9, Comunidad Campesina
  San Francisco de Buenavista, carretera Juliaca-Puno, Caracoto, San Roman,
  Puno;
- tres islas y seis surtidores;
- cuatro tanques: dos de Diesel B5 S-50 de 9 200 galones, uno de Gasohol
  Regular de 6 580 galones y uno de Gasohol Premium de 6 580 galones;
- no se observo infraestructura geometrica de GLP ni GNV.

La lamina S-01 contiene una referencia generica a GLP en una tabla de seguridad.
No se hereda al nuevo proyecto porque el alcance fue excluido expresamente en
la decision DEC-005.
