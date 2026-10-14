## 8. Cortocircuito, protección y puesta a tierra

Se estudia una fuente síncrona aislada 250 kVA. Hipótesis de reactancias xd″=.20, xd′=.30, xd=1.80 pu y ra=.02 pu, sumando impedancias de T1, línea y T2 según punto. Se calcula falla trifásica simétrica por Vfase/|Z|; sin aporte de motores ni tolerancias/corrección de tensión. No es un cortocircuito del SEIN ni ajuste final IEC 60909.

En llegada MT: Ik3 subtransitoria 53.4 A y sostenida 7.73 A. Esta última puede quedar por debajo de la corriente de carga. Fusibles y50/51 sin supervisión de tensión pueden no despejarla; se incorporan 51 V, protección diferencial de TX y protección de tierra sensible.

Q1/Q2:interruptores MT, TC25/5 o25/1 de clase/VA por comprobar, 50/51 y51 V, 87 T por TX, 59 N/64 con detección homopolar. Propuesta orientativa 51 V: pickupprimario 5 A si U<.70 pu, tiempo 0.60 s cabeza; llegada BT100 A con U<.70 pu y0.20 s; respaldo generador 0.90 s. No son ajustes aprobados: arranque, AVR, saturación TC, corrientes decrecientes, poder de corte y coordinación necesitan curvas reales.

La lámina LP-E03 identifica control/medición, órdenes de disparo y conexión funcional MT→zigzag→neutro→NGR→malla. No sustituye planos de bornes/cableado. Exige alimentación DC respaldada para disparar cuando cae la tensión. Energizar inicialmente sin carga y comprobar inrush de ambos TX; evaluar excitación progresiva con AVR y supervisión de frecuencia, sin bloquear indiscriminadamente las protecciones.

Para MTdelta se propone zigzag y resistencia de neutro en SE-LIM:5 A/10 s, R≈1155 ohm, energía térmica≈289 k J. Capacitancia supuesta 7 n F/km/fase da corriente capacitiva total~0.306 A; debe medirse/calcularse con geometría y accesorios. CBCT/59 N y control del NGR deben detectar tierra; el valor 5 A no es norma universal ni estudio definitivo de secuencia cero.

Puesta a tierra de SE: malla 10×10 m, cuatro líneas por dirección, paso 3.33 m, profundidad 0.6 m, Cu 35 mm² y cuatro varillas 2.4 m/16 mm. PAT de poste: dos varillas y enlace Cu 25 mm², sin neutro continuo MT. Equipotencialidad, cercos, descargadores y pantallas deben verificarse frente a paso/contacto/transferencia, CNE 036.

Una varilla 2.4 m/16 mm tiene R aproximada ρ/(2πL)[ln(4 L/d)-1]; paraρ100/300/1000 ohm·m resultan~35.8/107.3/357.9 ohm. Dos varillas no equivalen automáticamente a R/2 por resistencia mutua. Se adjunta sensibilidad de malla; no se promete 25 ohm ni seguridad por resistencia baja aislada.

Cu 35 mm² de malla y PE se proponen por robustez mecánica/corrosión y margen térmico. Verificar ensayo de resistividad, corriente realmente inyectada a terreno, tiempo de despeje, factor de reparto y tensiones admisibles. Bajo NGR 5 A y resistencia provisional, contacto transferido puede dominar aun con falla limitada.

Descargadores Zn O y aisladores requieren coordinación con tensión máxima a tierra durante falla, resistencia NGR, contaminación y altitud. Se propone clase 24 kV de equipos para 10 kV, pero 125 kV de impulso no se considera garantía en sitio sin proveedor. No se reproduce el factor de altitud 1.28 del expediente anterior sin sustento.
