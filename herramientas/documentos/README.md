# Presentación de expedientes

`formato_aquiles.py` convierte capítulos Markdown a fuentes LaTeX portables y compila sus PDF con el formato compartido de `recursos/plantillas/expediente-aquiles/`. Requiere Python y pdfLaTeX. Los metadatos se pasan desde cada proyecto; no asigna docente, potencia ni alcance.

La limpieza editorial verifica que toda la secuencia de números permanezca idéntica. La compilación hace tres pasadas y rechaza desbordamientos y glifos ausentes. La revisión visual del PDF sigue siendo necesaria antes de publicar. Los constructores de cada proyecto deciden dónde guardar la salida; esta herramienta no reemplaza cálculos ni cambia rótulos CAD.
