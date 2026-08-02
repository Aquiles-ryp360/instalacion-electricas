# Guia para elegir una tipologia no residencial

## Proposito

Ayudar a elegir un tema para la segunda unidad sin confundir dificultad
academica con cantidad de planos. La decision cambia las normas, los datos que
se deben levantar, los riesgos y el nivel de revision profesional.

## Comparacion inicial

| Alternativa | Contenido electrico aprovechable | Exigencias especiales | Complejidad relativa | Riesgo de bloquear el curso |
|---|---|---|---|---|
| Taller mecanico o metalmecanico pequeno | Alumbrado, tomas monofasicas/trifasicas, motores, compresor y soldadura | Placas de equipos, arranque de motores, ventilacion, posibles combustibles/pintura | Media | Bajo si se limita el proceso y se consiguen placas |
| Laboratorio educativo o de control de calidad | Alumbrado por tarea, tomas reguladas, equipos sensibles, UPS y fuerza menor | Definir sustancias, extraccion, humedad/corrosion y continuidad requerida | Media | Medio; depende de conseguir fichas reales |
| Clinica u hospital | Cargas generales y medicas, respaldo, UPS, sistemas esenciales e imagenes | CNE-U 140/240/260, EM.010, RNE A.050, MINSA, equipotencialidad y continuidad | Muy alta | Alto; no conviene sin planos y programa medico definidos |
| Grifo o estacion de servicio | Iluminacion, surtidores, bombas, tableros, emergencia y puesta a tierra | Areas peligrosas, CNE-U 110/120, equipos certificados y regulacion OSINERGMIN | Muy alta | Alto; no conviene como caso generico inventado |

## Recomendacion provisional

Si el docente no exige una tipologia de alto riesgo, el caso mas equilibrado
para el curso es un **taller pequeno con procesos bien delimitados** o un
**laboratorio educativo/de control sin atmosferas peligrosas**. Permiten
demostrar trifasico, fuerza, iluminacion, demanda y protecciones sin depender de
un sistema hospitalario completo ni de autorizaciones de hidrocarburos.

La recomendacion no selecciona el proyecto. La decision debe quedar registrada
por el grupo y, de ser posible, validada por el docente.

## Preguntas de seleccion

1. ¿Existe un plano real o una arquitectura que el docente permita usar?
2. ¿Se pueden conseguir placas o fichas de todos los equipos principales?
3. ¿El alcance exige media tension, transformador o solo baja tension?
4. ¿Hay gases, vapores, polvos, fibras, combustibles o corrosivos?
5. ¿Hay pacientes, equipos medicos o cargas cuya interrupcion comprometa vidas?
6. ¿Se requiere generador, UPS, transferencia automatica o bomba contra
   incendio?
7. ¿El grupo puede defender la normativa sectorial adicional?
8. ¿La consigna permite un caso academico con hipotesis o debe ser un local
   real?

## Regla de descarte

Se descarta temporalmente una alternativa si faltan datos que cambian la
clasificacion del riesgo, la arquitectura, la alimentacion o la potencia. No se
rellenan esos vacios copiando valores de `proyectos/nave-industrial/` ni de un
ejemplo de Internet.
