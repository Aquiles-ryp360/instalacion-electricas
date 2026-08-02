# Inventario de capacidades Windows

Fecha de prueba: 2026-08-02. Rama: `codex/windows-mejora-grifo`.

| Herramienta | Estado inicial | Uso concreto | Instalacion propuesta/realizada | Resultado probado |
|---|---|---|---|---|
| Windows | Instalado | Ejecucion nativa de CAD y PowerShell | Ninguna | Windows 10 Pro for Workstations 22H2, build 19045, 64 bits. |
| PowerShell | Instalado | Inventario y automatizacion CAD | Ninguna | Windows PowerShell 5.1.19041.7417. |
| Git | Instalado | Sincronizacion y rama experimental | Ninguna | 2.54.0; rama de trabajo rebasada sobre `3599e3d`. |
| Python del sistema | Alias sin runtime | Pipeline Python | Se reutilizo Python 3.12.13 incluido con Codex y se creo `.venv` local | Dependencias del repositorio y `pywin32` importan correctamente. |
| Node.js del sistema | No instalado | Ayudas de Codex, si fueran necesarias | Ninguna; se reutilizo el runtime incluido con Codex | El helper oficial descargo y verifico el manual actual de Codex. |
| winget | Instalado | Instalar solo dependencias justificadas | Ninguna instalacion global necesaria | 1.29.280. |
| GitHub CLI | Instalado | Inspeccion/autenticacion remota opcional | Ninguna | 2.92.0. |
| AutoCAD | Instalado | Revision visual, COM y trazado | Ninguna | AutoCAD 2027 R26.0 inicializado; sesion visible conservada y accesible por COM. |
| AcCoreConsole | Instalado | AUDIT reproducible sobre copias DXF | Se corrigio `scripts/windows/auditar-planos-autocad.ps1` para evaluar el log y salir sin guardar copias | Seis DXF abiertos y auditados: seis `PASS`, cero entradas descartadas y cero objetos borrados. |
| AutoCAD COM | Registrado | Automatizacion mediante `pywin32` | `pywin32` instalado solo en `.venv` | ProgID `AutoCAD.Application.26` conectado a AutoCAD 2027, version `26.0s (LMS Tech)`. |
| MiKTeX / pdfLaTeX | Instalado | Compilar expediente y guia | Se agrego fallback directo de tres pasadas cuando Perl no esta disponible | MiKTeX 26.5 genero expediente de 31 paginas y guia de 5 paginas. |
| Poppler | Disponible | `pdfinfo`, `pdfimages`, `pdftoppm` | Ninguna | Se verificaron seis PDF A1 y su union con cero imagenes raster; el expediente contiene solo las dos capturas esperadas. |
| Ghostscript | No instalado | Alternativa de inspeccion/conversion PDF | No se propone: MiKTeX/Poppler cubren la necesidad actual | No probado. |
| LibreOffice | No instalado | Conversion ofimatica auxiliar | No se propone: el expediente usa LaTeX/PDF | No probado. |
| Navegador integrado | Disponible en Codex | Fuentes oficiales y fichas trazables | Ninguna | Usado para verificar las paginas oficiales del CNE-U y de la R.M. N.° 120-2026-MINEM/DM; no sustituye evidencia local ni revision humana. |
| Computer Use | No expuesto en esta sesion | Control grafico de AutoCAD | Ninguna | No se afirma control de escritorio; solo se probaron terminal, COM y Core Console. |
| Skills/plugins | Disponibles parcialmente | Flujos documentales y navegador | Ninguna | Se uso la skill oficial `openai-docs`; no se instalo software por acumulacion. |

## Fuentes locales

Las seis entradas requeridas estan versionadas desde `3599e3d` y el verificador
devuelve `READY` para DXF, dos capturas, logo SVG/PDF y evidencia Promelsa. La
huella del JSON textual se normaliza a LF para que Git no produzca falsos fallos
al usar CRLF en Windows.
