# Proyecto: Instalaciones electricas industriales - Nave industrial

Proyecto de instalaciones electricas para nave / galpon industrial en baja tension (380V trifasico).

## Estructura

```
nave-industrial/
├── proyecto.yaml                manifiesto del proyecto
├── fuentes/                     croquis, planos originales, documentacion recibida
├── arquitectura/datos/          layout de la nave, zonas, dimensiones
├── diseno-electrico/datos/      cargas industriales, motores, tableros
├── datos/                       parametros de calculo
├── documentacion/               decisiones, supuestos, revision tecnica
├── expediente/                  fuentes del documento tecnico (LaTeX)
├── entregables/                 resultados aprobados (PDF, DXF)
├── archivo/                     material historico fuera del flujo activo
├── scripts/
│   ├── generar_planos_industriales.py   generador CAD industrial
│   └── calcular_maxima_demanda.py       motor de calculos industrial
└── tests/                       pruebas especificas del proyecto
```

## Flujo

1. Completar `datos/parametros-proyecto.yaml` con datos reales
2. Completar `diseno-electrico/datos/cargas-industriales.json` con motores, tableros, iluminacion
3. Completar `arquitectura/datos/layout-nave.json` con dimensiones de la nave
4. Ejecutar calculos: `make nave-industrial-calculos`
5. Generar planos: `make nave-industrial-planos`
6. Pipeline completo: `make nave-industrial`
7. Revisar en `build/nave-industrial/`

## Planos generados

- `plano_unifilar.dxf/pdf` - Diagrama unifilar general (subestacion -> TG -> tableros -> motores)
- `plano_distribucion.dxf/pdf` - Layout de planta con ubicacion de equipos

## Formato

Los planos se generan en DXF (compatible con AutoCAD, LibreCAD, QCAD) y PDF.
