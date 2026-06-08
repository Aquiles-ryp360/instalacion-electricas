# Diagnostico de proveedores

**Estado global:** Comparativa con cobertura util en al menos dos proveedores.

| Proveedor | Material probado | URL | Estado HTTP | Redirect | Metodo | Resultados crudos | Resultados aceptados | Estado | Motivo de fallo |
|---|---|---|---:|---|---|---:|---:|---|---|
| sodimac | Caja rectangular/octogonal - C1 | [abrir](https://www.sodimac.com.pe/sodimac-pe/search?Ntt=paquete+caja+rectangular) | - | no | httpx_sodimac_legacy | 0 | 0 | parser_fallo | TypeError: Cannot mix str and non-str arguments |
| sodimac | Caja rectangular/octogonal - C1 | [abrir](https://www.falabella.com.pe/falabella-pe/search?Ntt=paquete+caja+rectangular) | 200 | no | httpx_catalogo_falabella | 28 | 0 | ok_precio | - |
| maestro | Caja rectangular/octogonal - C1 | [abrir](https://www.maestro.com.pe/maestro-pe/search?Ntt=paquete+caja+rectangular) | - | no | httpx_sodimac_legacy | 0 | 0 | timeout | ConnectTimeout: timed out |
| maestro | Caja rectangular/octogonal - C1 | [abrir](https://www.falabella.com.pe/falabella-pe/search?Ntt=paquete+caja+rectangular) | 200 | no | httpx_catalogo_falabella | 10 | 0 | ok_precio | - |

## Hallazgos tecnicos

- **Promart:** expone un endpoint publico VTEX con productos, precios, stock y enlaces directos.
- **Sodimac:** la URL historica redirige a la portada; el fallback usa el catalogo unificado Falabella y conserva solo ofertas cuyo vendedor es SODIMAC.
- **Maestro:** el dominio historico puede agotar conexion; el fallback consulta el catalogo unificado y conserva solo ofertas identificadas con vendedor MAESTRO.
- **Mercado Libre:** la API publica puede responder 403 y el HTML puede mostrar verificacion de trafico. No se intentan saltar controles; se conserva el enlace de busqueda verificable.
- Los resultados con precio pero categoria, especificacion o unidad no confiable se mantienen como evidencia y no compiten por la recomendacion.
