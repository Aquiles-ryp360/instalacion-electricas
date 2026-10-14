# Motor hidroeléctrico académico

`calculos.py` usa unidades SI y no tiene dependencias externas. Resuelve pérdidas Darcy/Colebrook, cadena energética, geometría, régimen transitorio simplificado, flujo uniforme, magnitudes trifásicas, cargas por modo, pérdidas de transformadores, exportación, membrana/viga de tubería, reja y sedimentador. No selecciona automáticamente maquinaria ni certifica cumplimiento.

```powershell
python -m unittest discover -s herramientas/hidroelectricas/tests -v
```

Los nombres, parámetros, gráficos y documentos pertenecen al proyecto. Las funciones rechazan entradas físicas inválidas y régimen transitorio de Reynolds sin modelo. El cálculo de golpe de ariete es cribado y requiere MOC para diseño; no usarlo como certificado de espesor, presión o seguridad.

Integración: `proyectos/aquiles-minicentral-limbani/scripts/construir.py`.

13 pruebas verifican conservación, ecuaciones, escala física y rechazo de entradas inválidas. El balance de exportación omite la reactiva de dispersión/magnetización del transformador y el flujo AC completo. La viga horizontal simplemente apoyada no incluye flexión local de silletas, soldaduras, sismo ni estabilidad del terreno. Los valores de tolerancia/corrosión se suministran por el proyecto y no se atribuyen a una norma genérica.
