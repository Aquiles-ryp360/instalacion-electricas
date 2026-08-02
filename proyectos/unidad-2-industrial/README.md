# Unidad 2: instalacion electrica no residencial

## Estado actual

Se desarrolla un anteproyecto academico nuevo para un **grifo de combustibles
liquidos** en Caracoto. Aquiles Taylor Ramos Yapo es el unico autor. El DXF
recibido se utiliza como fuente arquitectonica/documental; no es un proyecto
electrico que se vaya a copiar. Miguel Mamani Chuquicallata figura como
propietario consignado en esa fuente facilitada por la DREM.

El alcance incluye Diesel B5 S-50, Gasohol Regular y Gasohol Premium. GLP y GNV
estan excluidos. La arquitectura fuente ya esta incorporada. El anteproyecto
cuenta con cargas, calculos electrico, de alumbrado y de metrados/presupuesto en
estado PASS, seis laminas A1 vectoriales cuyo rotulo original A-01 fue adaptado
con los datos academicos de Puno sin tapar el plano, un expediente
compilado con el formato grafico de la primera unidad de Aquiles y una guia
separada de sustentacion. El paquete completo permanece en `build/` para revision.

La consigna extraida de WhatsApp esta en
[`documentacion/consigna-extraida-whatsapp.md`](documentacion/consigna-extraida-whatsapp.md)
y el inventario de fuentes en
[`fuentes/inventario-whatsapp.md`](fuentes/inventario-whatsapp.md).
El CAD se documenta en
[`fuentes/inventario-cad.md`](fuentes/inventario-cad.md) y las preguntas que no
deben detener el avance se acumulan en
[`documentacion/dudas-pendientes.md`](documentacion/dudas-pendientes.md).
Las capturas y el criterio espacial se registran en
[`datos/ubicacion.yaml`](datos/ubicacion.yaml), y el flujo de cotización
automática está explicado en [`presupuesto/README.md`](presupuesto/README.md).

## Como debe empezar una nueva sesion de IA

1. Leer el [`AGENTS.md`](AGENTS.md) de esta carpeta y el de la raiz.
2. Leer [`proyecto.yaml`](proyecto.yaml); no deducir el estado por otros
   archivos.
3. Revisar [`documentacion/checklist-arranque.md`](documentacion/checklist-arranque.md).
4. Revisar la consigna y `documentacion/dudas-pendientes.md`; no detenerse por
   preguntas no criticas.
5. Registrar decisiones en
   [`documentacion/registro-decisiones.md`](documentacion/registro-decisiones.md).
6. Mantener `null`/`por confirmar` o usar un criterio adoptado explicito donde
   no exista evidencia; nunca presentarlo como dato observado.

## Estructura

```text
unidad-2-industrial/
├── AGENTS.md
├── proyecto.yaml
├── fuentes/                    documentos recibidos, sin modificar
├── arquitectura/datos/         geometria aprobada
├── diseno-electrico/datos/     cargas y circuitos aprobados
├── datos/                      criterios y parametros
├── documentacion/              decisiones, guias y matriz normativa
├── expediente/                 fuentes editables del informe
├── presupuesto/datos/          partidas, costos y fuentes del presupuesto
├── entregables/                solo resultados revisados
├── tests/                      validaciones especificas futuras
└── archivo/                    antecedentes fuera del flujo activo
```

## Estado de automatizacion

El paquete academico ya se puede regenerar con
`scripts/preparar_paquete_academico.py`. Antes de compilar la memoria se ejecuta
`scripts/preparar_recursos_ubicacion.py`. El presupuesto genera un BOM para el
cotizador reusable `herramientas/cotizacion/v1`; su modo `heuristico` funciona
sin clave externa y deja evidencia JSON/Markdown revisable. El pipeline de publicacion sigue
deshabilitado: faltan factibilidad e Icc de
Electro Puno, placas definitivas, verificacion de campo y revision profesional
de areas clasificadas. Las generaciones actuales permanecen en `build/`; solo
una revision humana completa autoriza copiarlas a `entregables/`.

Un clon nuevo recibe las tres fuentes indispensables de CAD/ubicación, el logo
vectorial y una evidencia comercial base. En Windows se prepara y comprueba con:

```powershell
powershell -ExecutionPolicy Bypass -File `
  .\proyectos\unidad-2-industrial\scripts\preparar_windows.ps1
```

La guía completa está en
[`documentacion/preparacion-windows.md`](documentacion/preparacion-windows.md).

Los proyectos `aquiles` y `renzo` pueden consultarse para entender la
estructura del flujo, pero sus dimensiones, tensiones, cargas, circuitos y
factores no son datos de este proyecto. El proyecto `renzo-industrial` de la
misma unidad es independiente y no comparte datos tecnicos.
