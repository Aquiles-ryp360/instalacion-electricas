# Ficha: Código Nacional de Electricidad - Suministro 2011

- Aprobación: **R.M. 214-2011-MEM/DM**, 29 de abril de 2011.
- [Ficha oficial MINEM](https://www.gob.pe/institucion/minem/normas-legales/108753-0214-2011-mem).
- [Texto oficial completo](https://cdn.www.gob.pe/uploads/document/file/95751/RM_214_2011_DM.pdf).
- Consulta: 2026-10-13. Lectura dirigida de disposiciones pertinentes; no certificación de proyectos.
- El texto de 2011 sustituye la edición aprobada mediante R.M. 366-2001-EM/VME. La identificación anterior «366-2011» era incorrecta.

## Alcance y mapa de lectura correcto

| Referencia | Materia | Aplicación y evidencia requerida |
|---|---|---|
| 010, 011 y 012 | Objetivo, alcance obligatorio y responsabilidades | Delimitar suministro/utilización y responsabilidad. El CNE no es un manual completo de diseño. |
| Sección 3; 032 a 038 | Puesta a tierra | Estudio de neutros, electrodos, equipotencialidad y fallas. |
| 036.A y 036.B | Seguridad de tierra y estaciones | Limitar tensiones de toque, paso y transferidas. Una resistencia baja no prueba por sí sola seguridad. |
| 036.D | Sistema con un solo electrodo | Requisito de 25 ohm en ese supuesto; no crea un límite universal de 5 o 10 ohm para estaciones. |
| Parte 1, secciones 10 a 19 | Estaciones y equipos | Recinto, humedad, iluminación, fuego, rotativos, baterías, transformadores, maniobra y sobretensiones. |
| 130.A, B y E; 132 | Generación | Disparo por sobrevelocidad además del regulador cuando corresponde; parada manual y control protegido. Resolver impedancia del neutro del generador según sistema. |
| Parte 2, sección 23; 230, 232, 234 y tablas | Distancias de líneas aéreas | Elegir fila, columna, notas, tensión y condiciones de cada cruce. Verificar flecha crítica y perfil. |
| Secciones 24, 25, 26 y 27 | Grados de construcción, cargas, resistencia y aislamiento | Calcular vanos, estructuras, cimentación y aislamiento con condiciones del sitio. |
| Parte 3, secciones 30 a 39 | Líneas subterráneas | No es una sección exclusiva de subestaciones aéreas. |
| Regla 362 | Subida de tuberías en poste | No establece límite general de resistencia de puesta a tierra. |
| Parte 4, secciones 40 a 44 | Operación y trabajo | Procedimientos, personal, distancias y protección durante intervención. |

## Altitud: leer el supuesto de cada regla

La regla 232.C.1.b incrementa la distancia **adicional** definida en 232.C.1.a para tensiones que sobrepasan 33 kV. No se aplica como incremento uniforme a todas las distancias de una línea de 22.9 kV. Otras separaciones tienen sus propios supuestos.

La coordinación de aislamiento de equipos se verifica con altitud, tensión máxima, impulso, contaminación y ficha del fabricante. No identificar distancia en aire y línea de fuga ni imponer 28% a ambas por una expresión exponencial sin norma y alcance documentados.

## Corrección de la ficha anterior

Se retiraron materias asignadas a secciones incorrectas, límites universales sin sustento y parámetros climáticos de un proyecto particular. Cada proyecto debe construir su matriz requisito-evidencia-estado. La revisión de Limbani está en `proyectos/aquiles-minicentral-limbani/datos/normativa.json`; los datos de campo siguen pendientes.
