param(
    [switch]$SoloFuentes
)

$ErrorActionPreference = "Stop"
$Repo = (git rev-parse --show-toplevel).Trim()
if (-not $Repo) {
    throw "No se pudo determinar la raiz Git. Abra Codex en el repositorio."
}
Set-Location -LiteralPath $Repo

$Python = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not $SoloFuentes -and -not (Test-Path -LiteralPath $Python)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -m venv (Join-Path $Repo ".venv")
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv (Join-Path $Repo ".venv")
    } else {
        throw "Falta Python. Instale una version compatible y vuelva a ejecutar."
    }
}

if ($SoloFuentes) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 "proyectos\unidad-2-industrial\scripts\verificar_preparacion.py" --solo-fuentes
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python "proyectos\unidad-2-industrial\scripts\verificar_preparacion.py" --solo-fuentes
    } else {
        throw "Falta Python para ejecutar el verificador de huellas."
    }
    exit $LASTEXITCODE
}

& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt
& $Python "proyectos\unidad-2-industrial\scripts\verificar_preparacion.py"
exit $LASTEXITCODE
