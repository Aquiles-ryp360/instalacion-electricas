# Inventario de capacidades Windows

Fecha de prueba: 2026-08-02. Rama: `codex/windows-mejora-grifo`.

| Herramienta | Estado inicial | Uso concreto | Instalacion propuesta/realizada | Resultado probado |
|---|---|---|---|---|
| Windows | Instalado | Ejecucion nativa de CAD y PowerShell | Ninguna | Windows 10 Pro for Workstations 22H2, build 19045, 64 bits. |
| PowerShell | Instalado | Inventario y automatizacion CAD | Ninguna | Windows PowerShell 5.1.19041.7417. |
| Git | Instalado | Sincronizacion y rama experimental | Ninguna | 2.54.0; `main` actualizado por fast-forward a `3a3522f`. |
| Python del sistema | Alias sin runtime | Pipeline Python | Se reutilizo Python 3.12.13 incluido con Codex y se creo `.venv` local | Dependencias del repositorio y `pywin32` importan correctamente. |
| Node.js del sistema | No instalado | Ayudas de Codex, si fueran necesarias | Ninguna; se reutilizo el runtime incluido con Codex | El helper oficial descargo y verifico el manual actual de Codex. |
| winget | Instalado | Instalar solo dependencias justificadas | Ninguna instalacion global necesaria | 1.29.280. |
| GitHub CLI | Instalado | Inspeccion/autenticacion remota opcional | Ninguna | 2.92.0. |
| AutoCAD | Instalado | Revision visual, COM y trazado | Ninguna | AutoCAD 2027 R26.0 localizado en `C:\Program Files\Autodesk\AutoCAD 2027\acad.exe`. El arranque COM no respondio en 60 s; requiere inicializacion/licencia interactiva. |
| AcCoreConsole | Instalado | AUDIT reproducible sobre copias DXF | Se agrego `scripts/windows/auditar-planos-autocad.ps1` | Dos invocaciones quedaron bloqueadas hasta el timeout; ejecutable presente pero automatizacion desatendida no disponible antes de inicializar AutoCAD. |
| AutoCAD COM | Registrado | Automatizacion mediante `pywin32` | `pywin32` instalado solo en `.venv` | ProgID `AutoCAD.Application.26` registrado; la instancia `/Automation -Embedding` se creo pero no llego a responder antes del timeout. |
| MiKTeX / XeLaTeX | Instalado | Compilar expediente y guia | Ninguna | MiKTeX 26.5 y XeTeX 4.18 detectados. |
| Poppler | Parcial/disponible en PATH | `pdfinfo`, `pdfimages`, `pdftoppm` | Ninguna | `pdfimages` 24.04.0 disponible desde MiKTeX; las otras utilidades se verificaran al existir los PDF. |
| Ghostscript | No instalado | Alternativa de inspeccion/conversion PDF | No se propone: MiKTeX/Poppler cubren la necesidad actual | No probado. |
| LibreOffice | No instalado | Conversion ofimatica auxiliar | No se propone: el expediente usa LaTeX/PDF | No probado. |
| Navegador integrado | Disponible en Codex | Fuentes oficiales y fichas trazables | Ninguna | Usado para verificar las paginas oficiales del CNE-U y de la R.M. N.° 120-2026-MINEM/DM; no sustituye evidencia local ni revision humana. |
| Computer Use | No expuesto en esta sesion | Control grafico de AutoCAD | Ninguna | No se afirma control de escritorio; solo se probaron terminal, COM y Core Console. |
| Skills/plugins | Disponibles parcialmente | Flujos documentales y navegador | Ninguna | Se uso la skill oficial `openai-docs`; no se instalo software por acumulacion. |

## Fuentes locales faltantes

No se encontraron en el clon ni bajo `OneDrive\Documents`:

- `fuentes/local/cad/DISTRIBUCION Y CIRCULACION MIGUEL.dxf`
- `fuentes/local/ubicacion/2026-08-02-captura-catastro-municipal-caracoto.png`
- `fuentes/local/ubicacion/2026-08-02-captura-google-maps-caracoto.png`

Sin esos originales no se regenera A-01, no se deben inventar capturas y no es
posible cerrar honestamente la compilacion de 31 paginas y seis planos. El resto
del pipeline y las pruebas se ejecutan de manera independiente.
