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

