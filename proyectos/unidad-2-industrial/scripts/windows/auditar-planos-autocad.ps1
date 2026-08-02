[CmdletBinding()]
param(
    [string]$SourceDirectory,
    [string]$OutputDirectory,
    [string]$AcCoreConsole,
    [ValidateRange(10, 1800)]
    [int]$TimeoutSeconds = 180
)

$ErrorActionPreference = 'Stop'
$scriptDirectory = Split-Path -Parent $PSCommandPath
$repository = (git -C $scriptDirectory rev-parse --show-toplevel).Trim()
if (-not $repository) {
    throw 'No se pudo determinar la raiz del repositorio.'
}

if (-not $SourceDirectory) {
    $SourceDirectory = Join-Path $repository 'build\unidad-2-industrial\cad\planos'
}
if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $repository 'build\unidad-2-industrial\cad\autocad-audit'
}
if (-not $AcCoreConsole) {
    $AcCoreConsole = Get-ChildItem 'C:\Program Files\Autodesk' -Filter accoreconsole.exe -File -Recurse -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        Select-Object -First 1 -ExpandProperty FullName
}
if (-not $AcCoreConsole -or -not (Test-Path -LiteralPath $AcCoreConsole)) {
    throw 'No se encontro AcCoreConsole.exe. Indique su ruta con -AcCoreConsole.'
}
if (-not (Test-Path -LiteralPath $SourceDirectory)) {
    throw "No existe el directorio de planos: $SourceDirectory"
}

$drawings = @(Get-ChildItem -LiteralPath $SourceDirectory -Filter 'IE-*.dxf' -File | Sort-Object Name)
if (-not $drawings) {
    throw "No se encontraron planos IE-*.dxf en $SourceDirectory"
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$auditScript = Join-Path $scriptDirectory 'audit.scr'
$results = foreach ($drawing in $drawings) {
    $copy = Join-Path $OutputDirectory $drawing.Name
    $log = Join-Path $OutputDirectory ($drawing.BaseName + '.log')
    $errorLog = Join-Path $OutputDirectory ($drawing.BaseName + '.stderr.log')
    Copy-Item -LiteralPath $drawing.FullName -Destination $copy -Force

    $process = Start-Process -FilePath $AcCoreConsole `
        -ArgumentList @('/i', $copy, '/s', $auditScript, '/l', 'en-US') `
        -RedirectStandardOutput $log -RedirectStandardError $errorLog `
        -WindowStyle Hidden -PassThru
    $finished = $process.WaitForExit($TimeoutSeconds * 1000)
    if (-not $finished) {
        $process.Kill()
        $process.WaitForExit()
    }
    $logText = if (Test-Path -LiteralPath $log) {
        Get-Content -LiteralPath $log -Encoding Unicode -Raw
    } else {
        ''
    }
    $auditMatch = [regex]::Match(
        $logText,
        'Total de errores encontrados\s+(\d+), corregidos\s+(\d+)'
    )
    $fatalDxfError = $logText -match 'Entrada DXF no válida|Invalid DXF input|ERROR:'
    $auditCompleted = $auditMatch.Success -and -not $fatalDxfError
    [PSCustomObject]@{
        plano = $drawing.Name
        copia_auditada = $copy
        estado = if (-not $finished) { 'TIMEOUT' } elseif ($auditCompleted) { 'PASS' } else { 'ERROR' }
        codigo_salida = if ($finished) { $process.ExitCode } else { $null }
        errores_encontrados = if ($auditMatch.Success) { [int]$auditMatch.Groups[1].Value } else { $null }
        errores_corregidos = if ($auditMatch.Success) { [int]$auditMatch.Groups[2].Value } else { $null }
        log = $log
        errores = $errorLog
    }
}

$results | Format-Table plano, estado, codigo_salida, errores_encontrados, errores_corregidos -AutoSize
if ($results.estado -contains 'TIMEOUT' -or $results.estado -contains 'ERROR') {
    exit 1
}
