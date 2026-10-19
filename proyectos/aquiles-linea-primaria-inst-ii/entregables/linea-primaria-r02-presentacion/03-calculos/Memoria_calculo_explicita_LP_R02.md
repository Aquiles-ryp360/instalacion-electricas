# Memoria de cálculo explícita · LP-R02

LP-R02 · 18/10/2026 · Diseño académico revisable

## 3. Demanda, horizonte y suficiencia de generación

Se proyectan viviendas base de 2017 al año de estudio 2026 usando 1% anual. Usuarios potenciales = ceil(viviendas×1.01^(2026−2017)). Las categoríasI/I/II, simultaneidad 0.80,60 luminarias y 14 kW de servicios son hipótesis sin padrón. El resultado no acredita nuevas conexiones ni su distribución secundaria.

| Localidad | Viviendas 2017 | Usuarios potenciales | kW |
| --- | --- | --- | --- |
| Huancasayani Centro | 95 | 104 | 49.920 |
| Huancasayani Bellavista | 140 | 154 | 73.920 |
| Huancasayani Lince | 86 | 95 | 30.400 |

P_doméstica =154.240 kW; P_AP=60×0.0541=3.246 kW; P_servicios=14 kW. P_total=171.486 kW. Con FP0.90: Q=P×tan(acos0.9)=83.054kvar; S=P/0.9=190.540 kVA. La carga se concentra en T2 para calcular el transporte, sin inventar ramales de usuario.

| Oferta | Reserva Limbani | Necesidad10 kV | Margen |
| --- | --- | --- | --- |
| 150 kW | 0 kW | 183.33 | -33.33 |
| 150 kW | 25 kW | 208.33 | -58.33 |
| 150 kW | 50 kW | 233.33 | -83.33 |
| 200 kW | 0 kW | 183.33 | 16.67 |
| 200 kW | 25 kW | 208.33 | -8.33 |
| 200 kW | 50 kW | 233.33 | -33.33 |

La oferta debe contrastarse con la curva de disponibilidad y con la carga horaria simultánea de ambas localidades. Elevar tensión reduce pérdidas; no compensa un déficit de potencia activa de la central. La proyección a 10/20 años se exporta con cargas, potencia de generación y kVA para verificar también la capacidad aparente a la altitud del emplazamiento.

## 4. Memoria de cálculo eléctrico explícita

### 4.1 Datos, resistencia y reactancia

Conductor propuesto AAAC 6201-T81,50mm² nominales,49.5mm² efectivos, diámetro 9 mm, masa 135 kg/km, R20=0.671 ohm/km. Masa y diámetro concuerdan con la tabla de referencia DGE; resistencia, RTS 14.7 kN, E62 GPa y curva de fluencia siguen como datos tipo sin fabricante contratado.

R75 = R20×[1+αR×(75−20)]×Lc/1000 =0.671×(1+0.0036×55)×6.758120 = 5.432569 ohm/fase. Se usa longitud física de conductor; R01 usaba proyección horizontal y subestimaba ligeramente R.

DMG=(Dab×Dbc×Dca)^(1/3)=(1.2×1.2×2.4)^(1/3)=1.511905 m. GMR≈0.7788×d/2=0.0035046 m, aproximación a sustituir por GMR de cable trenzado. X=2πf×2×10^-4×ln(DMG/GMR)×Lc(km)=3.091467 ohm/fase, a 60 Hz.

### 4.2 Qué significa que la salida sea 10 kV

Primera frontera: si se fijan exactamente 10 kV entre fases en el extremo MT de salida, se calcula sólo línea y carga. Segunda frontera: si se fijan 380 V nominales en la barra equivalente del generador, T1 y T2 agregan sus propias impedancias y pérdidas; la MT inicial ya no es exactamente 10 kV. Ambas fronteras se tabulan por separado para evitar respuestas incompatibles.

| MT salida fija kV | MT llegada kV | Corriente A | Pérdida kW |
| --- | --- | --- | --- |
| 10 | 9.8797 | 11.135 | 2.0206 |
| 20 | 19.9404 | 5.517 | 0.4960 |
| 22 | 21.9458 | 5.013 | 0.4095 |
| 22.9 | 22.8480 | 4.815 | 0.3778 |

### 4.3 Flujo con ambos transformadores

Base 250 kVA. rTX=Pcu/Sn=3.1/250=0.0124 pu; xTX=sqrt(0.06²−0.0124²)=0.058705 pu. Zbase=Vnom²/Sbase; ZTX=(r+jx)×Zbase. P0=0.45 kW y Q0=2.5kvar por TX son supuestos constantes. Los equipos alternativos se comparan con las mismas pérdidas pu; ofertas reales pueden cambiar el resultado.

Barrido por fase: i_carga=conj[S_trifásica/(3v)]; corriente de rama=suma de cargas aguas abajo; v_receptor=v_emisor−Z×i; iterar hasta residuo<10^-8 V. P_Joule=3|i|²R; Q_serie=3|i|²X. Comprobar P_fuente=P_carga+P0_T1+P0_T2+ΣP_Joule y Q equivalente. Añadir5 kW de auxiliares sólo al balance de generación; su FP se supone 1.

| kV nominal | Fuente pu | MT salida/llegada kV | BT V | P línea kW | P generación kW |
| --- | --- | --- | --- | --- | --- |
| 10 | 1.0 | 9.660 / 9.530 | 350.3 | 2.359 | 184.05 |
| 10 | 1.025 | 9.921 / 9.795 | 360.7 | 2.224 | 183.67 |
| 10 | 1.05 | 10.181 / 10.059 | 371.1 | 2.102 | 183.33 |
| 20 | 1.0 | 19.329 / 19.265 | 354.3 | 0.576 | 182.17 |
| 20 | 1.025 | 19.850 / 19.788 | 364.6 | 0.544 | 181.91 |
| 20 | 1.05 | 20.370 / 20.309 | 374.8 | 0.515 | 181.66 |
| 22 | 1.0 | 21.263 / 21.204 | 354.5 | 0.476 | 182.07 |
| 22 | 1.025 | 21.836 / 21.779 | 364.8 | 0.449 | 181.81 |
| 22 | 1.05 | 22.407 / 22.352 | 375.0 | 0.425 | 181.57 |
| 22.9 | 1.0 | 22.133 / 22.076 | 354.6 | 0.439 | 182.03 |
| 22.9 | 1.025 | 22.729 / 22.675 | 364.9 | 0.414 | 181.77 |
| 22.9 | 1.05 | 23.324 / 23.271 | 375.1 | 0.392 | 181.53 |

La elevación efectiva 1.025/1.05 pu es una sensibilidad del modelo ideal; no ordena cambiar un tap. Comprobar relación real, sentido del selector, impedancias por toma, máximo en vacío, rango AVR y garantía a la altitud. Debe evaluarse carga mínima y máxima y toda la red posterior. El objetivo±5% de estudio no constituye certificación de calidad en medidores.

### 4.4 Comparación económica y necesidad de regulación

A 1.05 pu,10 kV pierde 2.102 kW en línea y 22.9 kV pierde 0.392 kW: ahorro de pico 1.710 kW. La mejora de BT también depende de T1/T2. No aparece justificación de un elevador intermedio sólo por 6.7km: primero resolver tensión nominal, transformadores, AVR y perfil de carga. La inversión adicional no puede decidirse por menor pérdida sin precio de equipos y energía.

Energía anual de pérdidas =Σ(P_perdida_i×horas_i), con 8760horas repartidas 25/50/75/100% del pico. Esta curva es sintética. La hoja energia.csv conserva cada bloque. Recuperación simple de sobrecosto: ΔCAPEX/(ΔE_kWh×costo_energía−ΔOPEX); faltan cotizaciones y curva horaria para dar un plazo válido.

### 4.5 Cortocircuito, protección y puesta a tierra

Ik3≈VLL/[sqrt(3)|Zg+ZT1+Zlínea|]; se distinguen Xd″0.20 pu, Xd′0.30 pu y Xd1.80 pu de estudio. La corriente de falla sostenida puede ser menor que la corriente de carga: no basta elegir fusible o50/51 copiando un proyecto SEIN. Requiere curva de decremento/AVR, arranque de motores, inrush, TC/TT, lógica 51V u otra protección y coordinación real. El CSV no es ajuste de relés.

Si se mantiene MT delta en ambos TX, no hay neutro MT accesible; NGR exige transformador de puesta a tierra. Para 5 A: RN=VLL/(sqrt3×5); a 10 kV=1154.7 ohm y 22.9 kV=2644.3 ohm. Energía nominal 10s=Vfase×5×10; dimensionar equipos y verificar régimen, capacitancias y protección. No sumar un NGR simbólico sin definir el neutro.

La resistencia de tierra, tensiones de paso/contacto y cimentaciones quedan pendientes. Se requieren Wenner, corriente/tiempo de falla y modelo del terreno. La ampacidad del conductor requiere datos de proveedor y balance térmico a la altitud. Una corrida con h supuesto o el bajo valor de corriente no acredita por sí sola capacidad garantizada.

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

