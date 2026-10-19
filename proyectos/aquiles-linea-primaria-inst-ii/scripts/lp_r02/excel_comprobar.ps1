param([string]$Carpeta = 'G:/Aquiles/instalacion-electricas/build/aquiles-linea-primaria-inst-ii/presentacion-final/Proyecto_Linea_Primaria')
$ErrorActionPreference = 'Stop'
$base = [System.IO.Path]::GetFullPath($Carpeta)
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$report = [ordered]@{}
try {
    $book = $excel.Workbooks.Open((Join-Path $base '02_Metrados/Metrados.xlsx'), 0, $false)
    try {
        $res = $book.Worksheets.Item('Resumen')
        $ps = $book.Worksheets.Item('Postes')
        $ps.Range('E7').Value2 = [double]15
        $excel.CalculateFullRebuild()
        if ($res.Range('E7').Value2 -ne 71 -or $res.Range('E8').Value2 -ne 31) { throw 'No actualiza conteo de postes por altura' }
        $report['conteo_por_altura_actualiza'] = $true
        $ps.Range('E7').Value2 = [double]13
        $ps.Range('I8').Value2 = 'ANCLAJE'
        $excel.CalculateFullRebuild()
        if ($res.Range('E19').Value2 -ne 162 -or $res.Range('E25').Value2 -ne 972 -or $res.Range('E27').Value2 -ne 21885) { throw 'No actualiza retenidas, puentes y suministro' }
        $report['funcion_apoyo_actualiza_ramales_puentes_compra'] = $true
    } finally { $book.Close($false) }
    $book = $excel.Workbooks.Open((Join-Path $base '01_Calculos/Calculos.xlsx'), 0, $false)
    try {
        $book.Worksheets.Item('Parametros').Range('E36').Value2 = [double]0.95
        $excel.CalculateFullRebuild()
        $res = $book.Worksheets.Item('Resumen')
        $report['fp_095'] = [ordered]@{bt_v=$res.Range('D16').Value2;generacion_kw=$res.Range('D18').Value2;kva=$res.Range('D19').Value2}
        if ($res.Range('D18').Value2 -ge 183.326) { throw 'No actualiza balance al cambiar factor de potencia' }
    } finally { $book.Close($false) }
    $book = $excel.Workbooks.Open((Join-Path $base '05_Presupuesto/Presupuesto.xlsx'), 0, $false)
    try {
        $s = $book.Worksheets.Item('Presupuesto')
        $antes = $s.Range('F28').Value2
        $s.Range('E7').Value2 = [double]6.8
        $excel.CalculateFullRebuild()
        $delta = $s.Range('F28').Value2 - $antes
        if ([math]::Abs($delta - 31497.12) -gt 0.02) { throw 'No actualiza presupuesto desde precio unitario' }
        $report['delta_presupuesto_por_un_sol_conductor'] = $delta
    } finally { $book.Close($false) }
    $report['cambios_de_ensayo_guardados'] = $false
    $json = $report | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText((Join-Path (Split-Path $base -Parent) 'verificacion-excel-nativo.json'), $json, [System.Text.UTF8Encoding]::new($false))
    Write-Output $json
} finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
