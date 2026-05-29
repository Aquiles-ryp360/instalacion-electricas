# Proyecto en LaTeX

Esta carpeta contiene el informe del mini proyecto en formato LaTeX, seccion por seccion, siguiendo el orden del proyecto guia:

1. Memoria descriptiva.
2. Calculos justificativos.
3. Especificaciones tecnicas de suministro de materiales.
4. Especificaciones tecnicas de montaje.
5. Cronograma de obra.
6. Metrado.
7. Planos y laminas de detalle.
8. Anexos.

## Archivo principal

Compilar:

```powershell
pdflatex -interaction=nonstopmode -output-directory=build main.tex
pdflatex -interaction=nonstopmode -output-directory=build main.tex
```

El PDF queda en:

```text
latex/build/main.pdf
```

## Donde editar

- Portada: `capitulos/00-portada.tex`
- Memoria: `capitulos/01-memoria-descriptiva.tex`
- Calculos: `capitulos/02-calculos-justificativos.tex`
- Especificaciones: `capitulos/03-especificaciones-materiales.tex`
- Montaje: `capitulos/04-especificaciones-montaje.tex`
- Cronograma: `capitulos/05-cronograma.tex`
- Metrado: `capitulos/06-metrado.tex`
- Planos: `capitulos/07-planos.tex`

Busca `EDITAR AQUI` para completar datos reales.

## Planos

Coloca los planos en `latex/planos/` con estos nombres:

- `IE-01-ubicacion-arquitectura.pdf`
- `IE-02-alumbrado.pdf`
- `IE-03-tomacorrientes.pdf`
- `IE-04-circuitos-canalizaciones.pdf`
- `IE-05-unifilar-cuadro-cargas.pdf`
- `IE-06-puesta-tierra.pdf`

