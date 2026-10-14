# Entrega documental Rev. 4 — Línea primaria Capachica–Llachón

**Estado: categoría A de alcance parcial cartográfico y metodológico, con bloqueos de ingeniería. NO APTO PARA CONSTRUCCIÓN.**

Las láminas y tablas son utilizables para revisión del corredor y coordinación de levantamiento. No existe punto de conexión aprobado, eje continuo levantado, tensión/demanda confirmadas, conductor seleccionado, perfiles de vanos ni permisos. En consecuencia, las memorias de cálculo muestran modelos y datos requeridos, **no resultados de dimensionamiento**. El nombre de esta carpeta identifica la entrega Rev. 4, no una aprobación final de obra.

Orden de lectura: `01_INDICE_Y_CONTROL/INDICE_GENERAL.md` → `02_MEMORIA_DESCRIPTIVA/MEMORIA_DESCRIPTIVA.md` → memorias `03` → planos `04`/`05` → metrados `06` → normativa `07` → campo `08` → control `09`.

Geometría: KML original 13939.511910 m UTM en cuatro segmentos; GIS alternativo 13834.028618 m. Tres brechas no levantadas. PC=40 referencias GIS; PN=27 sitios de replanteo; CV=44 alertas OSM. Ninguna cifra es metrado de postes nuevos.

Reproducción desde la raíz del repositorio: `python proyectos/renzo-linea-primaria-capachica-llachon/scripts/generar_entrega_rev4.py --output RUTA_NUEVA`. Requiere el `requirements.txt` del proyecto. El generador falla si la salida existe. `--verify RUTA_EXISTENTE` verifica el paquete sin escribir. Los documentos editables son Markdown/CSV/JSON, los planos editables DXF R2010 con modelo UTM en metros y presentación A3 en milímetros. PDF/PNG proceden de los mismos comandos de dibujo de hoja. Autor y firmas: por designar; no se inventaron.
