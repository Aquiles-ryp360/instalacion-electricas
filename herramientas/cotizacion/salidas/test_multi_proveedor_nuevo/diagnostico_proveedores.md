# Diagnostico de proveedores

**Estado global:** Cotizacion parcial: solo se obtuvo cobertura util en 1 proveedores.

| Proveedor | Material probado | URL | Estado HTTP | Redirect | Metodo | Resultados crudos | Resultados aceptados | Estado | Motivo de fallo |
|---|---|---|---:|---|---|---:|---:|---|---|
| maestro | Tubo PVC SAP 40 mm (alimentador) | [abrir](https://www.maestro.com.pe/maestro-pe/search?Ntt=tubo+electrico+40+mm+3+metros) | - | no | httpx_sodimac_legacy | 0 | 0 | timeout | ConnectTimeout: timed out |
| maestro | Tubo PVC SAP 40 mm (alimentador) | [abrir](https://www.falabella.com.pe/falabella-pe/search?Ntt=tubo+electrico+40+mm+3+metros) | 200 | no | httpx_catalogo_falabella | 10 | 0 | ok_precio | - |

## Hallazgos tecnicos

- **Promart:** expone un endpoint publico VTEX con productos, precios, stock y enlaces directos.
- **Sodimac:** la URL historica redirige a la portada; el fallback usa el catalogo unificado Falabella y conserva solo ofertas cuyo vendedor es SODIMAC.
- **Maestro:** el dominio historico puede agotar conexion; el fallback consulta el catalogo unificado y conserva solo ofertas identificadas con vendedor MAESTRO.
- **Mercado Libre:** la API publica puede responder 403 y el HTML puede mostrar verificacion de trafico. No se intentan saltar controles; se conserva el enlace de busqueda verificable.
- Los resultados con precio pero categoria, especificacion o unidad no confiable se mantienen como evidencia y no compiten por la recomendacion.
