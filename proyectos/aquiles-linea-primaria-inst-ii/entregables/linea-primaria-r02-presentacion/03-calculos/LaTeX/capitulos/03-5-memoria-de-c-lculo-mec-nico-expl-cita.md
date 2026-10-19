## 5. Memoria de cálculo mecánico explícita

### 5.1 Un poste 13 m: qué puede soportar

Longitud total 13 m, empotramiento de estudio 1.9 m, longitud libre 11.1 m y amarre 10.6 m. Para 13/400,400 daN=4000 N≈407.9 kgf de carga transversal equivalente; no400 kg de peso colgado. Con aplicación a 0.15 m bajo cima, brazo=13−1.9−0.15=10.95 m. El punto de ensayo y el empotramiento deben confirmarse con proveedor.

Momento de trabajo tipo 4000×10.95=43.80 kN·m. Si la rotura garantizada fuese 2×trabajo: Mrot=87.60 kN·m. Método de estudio gradoB, phi0.65: resistencia de comparación 56.94 kN·m. Para 600 daN,85.41 kN·m. Se comparan cargas factorizadas con resistencia reducida; no se aplica además otro divisor 2 a esta misma verificación. Peso propio, interacción axial-flexión, fisuración, anclajes y suelo aún requieren comprobación.

### 5.2 Peso, tracción y ángulo son cargas distintas

Peso lineal por fase=0.135×9.80665=1.323898 N/m. En dos vanos iguales 85 m y terreno horizontal, un apoyo interior recibe aproximadamente el peso de 85 m por fase:3×0.135×85=34.425 kg de cable sin hielo. Eso no incluye aisladores ni poste. La tracción EDS por fase es0.15×14700=2205 N; en un terminal, tres fases ejercen 6615 N horizontales antes de factores. En un ángulo 30°, resultante ideal 3×2×2205×sin 15°=3424.2 N. Por eso dividir 400 entre kg/m no determina el vano.

### 5.3 Catenaria y cambio de estado

Se resuelve cada vano por separado bajo la hipótesis de aisladores rígidos. Para apoyo inclinado y viento, se rota al plano de carga. a=H/q; dy=Δz×qv/q; dx=sqrt(L²+Δz²−dy²); x0=dx/2−a×asinh[dy/(2a×sinh(dx/2a))]. y(x)=a[cosh((x−x0)/a)−cosh(x0/a)]. La longitud y las fuerzas tangenciales se calculan con hiperbólicas, sin asumir parábola para desniveles grandes.

Compatibilidad termoelástica: Lnatural≈Lc−∫Tds/(EA). En el nuevo estado Lnatural_2=Lnatural_ref×[1+αΔT+ε_creep]. Se obtiene H por bisección y se exporta el residuo. Se conserva la sensibilidad heredada 345 microstrain; la alternativa normativa histórica de temperatura equivalente 10°C corresponde 230 microstrain con α23×10^-6/K y debe contrastarse con curva de proveedor. No se suma simultáneamente 10°C y 345 microstrain.

| Estado | T°C | V m/s | Hielo mm | Fluencia m/m |
| --- | --- | --- | --- | --- |
| EDS | 15 | 0 | 0 | 0 |
| VIENTO | 5 | 29 | 0 | 0 |
| HIELO | 0 | 0 | 6 | 0 |
| COMBINADO | 0 | 14.5 | 3 | 0 |
| FRIO | -5 | 0 | 0 | 0 |
| CALOR_FINAL | 75 | 0 | 0 | 0.000345 |

### 5.4 Fuerzas con signo, viento y retenidas

Las fuerzas de extremo se convierten de cada vano a Este/Norte/Vertical y se suman en el poste. La parte paralela a la cuerda recibe factor 1.65; la reacción distribuida horizontal 2.5 y vertical 1.5. Se muestrea viento 0–345° cada 15°. No es búsqueda continua exacta del azimut crítico. Se integra el viento sobre un poste cónico tipo 180/375 mm; dimensiones de 15/17 m son sensibilidad geométrica, no catálogo certificado.

Fvertical negativa en la convención del CSV es carga ascendente de los conductores/aisladores. No se reemplaza el desnivel por su valor absoluto. Retenida ideal por ramal: neutraliza el componente horizontal de tracción a 45°, Tg=Fh/cos45°; agrega Fh×tan45° hacia abajo. Resistencia mínima rotura≥Tg/0.90 y se conserva el mínimo 60 kN de la especificación inicial. El modelo ideal no incluye pretensión, rigidez, deslizamiento ni transferencia real de carga: no demuestra estabilidad ni capacidad de anclaje.

Comparación del esquema de apoyos: 0 excedencias de flexión tipo en la base recalculada; 16 apoyos con retención adicional propuesta. Después de esas retenidas ideales quedan 0 excedencias de flexión de estudio. Todos mantienen la capacidad axial y de cimentación pendiente; pasar una relación D/C no equivale a aprobación.

El cruce de los 160 anclajes ideales y sus segmentos con casas/cauces heredados identifica 1 alertas cartográficas. Sus posiciones deben replantearse y recalcularse antes de aceptar el sistema de retenidas. La ausencia de alerta tampoco demuestra disponibilidad del predio.

### 5.5 Vano admisible: ejemplo controlado

| Poste tipo | Último vano que pasa m | Primero que falla m | Restricción |
| --- | --- | --- | --- |
| 13 m/400 daN | 128 | 129 | FLECHA/GALIBO DE ESTUDIO |
| 13 m/600 daN | 128 | 129 | FLECHA/GALIBO DE ESTUDIO |

La tabla anterior corresponde sólo a dos vanos iguales en terreno plano, amarre 10.6 m, hipótesis de cable 50mm² y estados indicados. Se recorre 10–300 m y se exige flexión tipo, separación 7.5 m de estudio y T/RTS≤40% de estudio. No se transfiere ese vano límite a quebradas, giros, cruces ni terrenos inclinados. En el corredor real cada vano conserva su resultado individual y su observación.

### 5.6 Cálculo desarrollado de un vano

Ejemplo V037, P037–P038: L=30.4171 m; desnivel de amarres=20.6474 m. H inicial 2205 N. EA=62×10^9×49.5×10^-6=3069000 N. La pendiente relativa|Δz|/L=0.6788 exige conservar la inclinación. Cada fila siguiente procede de una solución independiente del cambio de estado.

| Estado | H N | T mayor N | Flecha m | Separación modelo m |
| --- | --- | --- | --- | --- |
| EDS | 2,205.0 | 2,678.8 | 0.084 | 9.013 |
| VIENTO | 3,450.4 | 3,536.9 | 0.063 | 9.033 |
| HIELO | 3,155.8 | 3,854.6 | 0.171 | 8.926 |
| COMBINADO | 3,305.2 | 3,788.7 | 0.105 | 8.992 |
| FRIO | 3,358.3 | 4,072.7 | 0.055 | 9.041 |
| CALOR_FINAL | 220.5 | 281.2 | 0.839 | 8.258 |

### 5.7 Apoyos que requieren más atención

P024: poste 17 m; ángulo 4.38°; M sin retenidas=68.765 kN·m; M con retenidas ideales=49.968 kN·m; M resistente tipo=115.050 kN·m. D/C base recalculado=0.598; D/C propuesta=0.598. Vertical exterior mínima=1.339 kN. Acciones: CONSERVAR COMO CANDIDATO; CONFIRMAR CAMPO Y CERTIFICADOS.

P040: poste 17 m; ángulo 0.00°; M sin retenidas=56.022 kN·m; M con retenidas ideales=55.983 kN·m; M resistente tipo=115.050 kN·m. D/C base recalculado=0.487; D/C propuesta=0.487. Vertical exterior mínima=-2.148 kN. Acciones: PROPONER RETENCION Y RETENIDAS; VERIFICAR ARMADO; CARGA ASCENDENTE; COMPROBAR FIJACION Y HERREJES.

P031: poste 17 m; ángulo 0.00°; M sin retenidas=55.285 kN·m; M con retenidas ideales=55.282 kN·m; M resistente tipo=115.050 kN·m. D/C base recalculado=0.481; D/C propuesta=0.481. Vertical exterior mínima=1.079 kN. Acciones: CONSERVAR COMO CANDIDATO; CONFIRMAR CAMPO Y CERTIFICADOS.

P029: poste 13 m; ángulo 3.88°; M sin retenidas=40.625 kN·m; M con retenidas ideales=23.942 kN·m; M resistente tipo=85.410 kN·m. D/C base recalculado=0.476; D/C propuesta=0.280. Vertical exterior mínima=-1.951 kN. Acciones: PROPONER RETENCION Y RETENIDAS; VERIFICAR ARMADO; CARGA ASCENDENTE; COMPROBAR FIJACION Y HERREJES.

P039: poste 17 m; ángulo 10.23°; M sin retenidas=97.852 kN·m; M con retenidas ideales=53.948 kN·m; M resistente tipo=115.050 kN·m. D/C base recalculado=0.469; D/C propuesta=0.469. Vertical exterior mínima=-0.447 kN. Acciones: CARGA ASCENDENTE; COMPROBAR FIJACION Y HERREJES.

### 5.8 Ubicación de postes y perfiles pendientes

La ubicación definitiva se obtiene sobre topografía del eje y sus fases, con cotas de cruce, obstáculos, techo/vegetación, terreno bajo balanceo, fajas y predios. Se recalcula flecha y fuerzas al mover un apoyo. Las alertas actuales identifican dónde insertar apoyo, elevarlo o replantear tramo; no se inventa una coordenada aprobada para ocultar la falta de topografía. Los girosP003/P035/P057 mayores 90° exigen replanteo o armado especial. No se presenta hoja 008 como una retención equivalente para CAC.

