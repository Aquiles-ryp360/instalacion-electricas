param([string]$Carpeta = 'G:/Aquiles/instalacion-electricas/build/aquiles-linea-primaria-inst-ii/presentacion-final/Proyecto_Linea_Primaria', [switch]$SoloPresupuesto)
$ErrorActionPreference = 'Stop'
$base = [System.IO.Path]::GetFullPath($Carpeta)
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$excel.AskToUpdateLinks = $false
try {
    $items = @(
        @('02_Metrados/Metrados.xlsx', 'Resumen', 'A1:E31', '02_Metrados/Resumen_Metrados.pdf'),
        @('01_Calculos/Calculos.xlsx', 'Resumen', 'A1:E33', '01_Calculos/Resumen_Calculos.pdf'),
        @('05_Presupuesto/Presupuesto.xlsx', 'Presupuesto', 'A1:F34', '05_Presupuesto/Resumen_Presupuesto.pdf')
    )
    foreach ($item in $items) {
        if ($SoloPresupuesto -and $item[1] -ne 'Presupuesto') { continue }
        $file = Join-Path $base $item[0]
        $book = $excel.Workbooks.Open($file, 0, $false)
        try {
            $excel.CalculateFullRebuild()
            foreach ($sheet in $book.Worksheets) {
                $sheet.Activate()
                $excel.ActiveWindow.DisplayGridlines = $false
                $excel.ActiveWindow.Zoom = 85
                $used = $sheet.UsedRange
                $sheet.PageSetup.PrintArea = $used.Address()
                $sheet.PageSetup.Orientation = 2
                $sheet.PageSetup.PaperSize = 8
                $sheet.PageSetup.Zoom = $false
                $sheet.PageSetup.FitToPagesWide = 1
                $sheet.PageSetup.FitToPagesTall = $false
                $sheet.PageSetup.PrintTitleRows = '$1:$6'
                $sheet.PageSetup.LeftMargin = $excel.CentimetersToPoints(1.0)
                $sheet.PageSetup.RightMargin = $excel.CentimetersToPoints(1.0)
                $sheet.PageSetup.TopMargin = $excel.CentimetersToPoints(1.4)
                $sheet.PageSetup.BottomMargin = $excel.CentimetersToPoints(1.4)
                $sheet.PageSetup.CenterFooter = ('Instalaciones El' + [char]0x00E9 + 'ctricas II | Aquiles Taylor Ramos Yapo | 227368')
                $sheet.PageSetup.RightFooter = 'Hoja &P'
                $sheet.Range('A1').Select() | Out-Null
                [System.Runtime.InteropServices.Marshal]::ReleaseComObject($used) | Out-Null
                [System.Runtime.InteropServices.Marshal]::ReleaseComObject($sheet) | Out-Null
            }
            $summary = $book.Worksheets.Item($item[1])
            $summary.Activate()
            $summary.PageSetup.PrintArea = $item[2]
            $summary.PageSetup.PrintTitleRows = ''
            $summary.PageSetup.FitToPagesTall = 1
            $summary.PageSetup.PaperSize = 9
            $summary.PageSetup.Orientation = 2
            $summary.ExportAsFixedFormat(0, (Join-Path $base $item[3]))
            $book.Save()
            Write-Output ('Recalculado y exportado con Excel: ' + $item[0])
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($summary) | Out-Null
        } finally {
            $book.Close($false)
            [System.Runtime.InteropServices.Marshal]::ReleaseComObject($book) | Out-Null
        }
    }
} finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
