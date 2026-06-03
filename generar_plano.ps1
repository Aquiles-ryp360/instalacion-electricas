# Generador de Planos CAD 2D - Script Automatizado para Windows (PowerShell)
# Ejecuta este script desde la raíz del repositorio

$ErrorActionPreference = "Stop"

$ScriptDir = "herramientas/ia-cad-casas"
$PythonScript = "$ScriptDir/scripts/dxf_generator.py"

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   Iniciando Generador Automático de Planos CAD 2D (Windows)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

# 1. Comprobar si Python está instalado
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "Python detectado: $pythonVersion"
} catch {
    Write-Error "Error: Python no está instalado en el sistema o no está en el PATH."
    Exit 1
}

# 2. Instalar dependencias si es necesario
Write-Host "Asegurando dependencias (ezdxf y matplotlib)..."
& python -m pip install --quiet ezdxf matplotlib

# 3. Definir los planos a generar
$Planos = @(
    @{
        Input = "$ScriptDir/data/layout_example.json"
        OutputDxf = "$ScriptDir/output/plan_distribucion.dxf"
        DestDxf = "proyecto_vivienda_unifamiliar_por_RENZO/planos/ejemplo-distribucion.dxf"
    },
    @{
        Input = "$ScriptDir/data/primer_piso.json"
        OutputDxf = "proyecto_vivienda_unifamiliar_por_RENZO/planos/primer-piso.dxf"
        DestDxf = $null
    },
    @{
        Input = "$ScriptDir/data/segundo_piso.json"
        OutputDxf = "proyecto_vivienda_unifamiliar_por_RENZO/planos/segundo-piso.dxf"
        DestDxf = $null
    },
    @{
        Input = "$ScriptDir/data/tercer_piso.json"
        OutputDxf = "proyecto_vivienda_unifamiliar_por_RENZO/planos/tercer-piso.dxf"
        DestDxf = $null
    }
)

# Crear carpetas de salida si no existen
if (-not (Test-Path "$ScriptDir/output")) {
    New-Item -ItemType Directory -Path "$ScriptDir/output" -Force | Out-Null
}
if (-not (Test-Path "proyecto_vivienda_unifamiliar_por_RENZO/planos")) {
    New-Item -ItemType Directory -Path "proyecto_vivienda_unifamiliar_por_RENZO/planos" -Force | Out-Null
}

# 4. Ejecutar la generación
foreach ($plano in $Planos) {
    $in = $plano.Input
    $outDxf = $plano.OutputDxf
    
    Write-Host "----------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "Generando plano para: $in" -ForegroundColor Cyan
    Write-Host "Archivo DXF de salida: $outDxf"
    
    & python $PythonScript --input $in --output $outDxf
    
    # Si se requiere copiar a otro destino
    if ($plano.DestDxf -ne $null) {
        $destDxf = $plano.DestDxf
        $destPdf = $destDxf.Replace(".dxf", ".pdf")
        $srcPdf = $outDxf.Replace(".dxf", ".pdf")
        
        Write-Host "Copiando a entregables: $destDxf"
        Copy-Item -Path $outDxf -Destination $destDxf -Force
        if (Test-Path $srcPdf) {
            Copy-Item -Path $srcPdf -Destination $destPdf -Force
        }
    }
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   ¡Proceso finalizado con éxito en Windows!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
