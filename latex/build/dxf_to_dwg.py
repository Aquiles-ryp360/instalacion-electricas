import subprocess
import os

dxf_path = r"C:\Users\renzo\instalacion-electricas\latex\planos\AVANCE DEL PLANO ELECTRICO1.dxf"
dwg_path = r"C:\Users\renzo\instalacion-electricas\latex\planos\AVANCE DEL PLANO ELECTRICO1.dwg"
scr_path = r"C:\Users\renzo\instalacion-electricas\latex\build\dxf_to_dwg.scr"
cad_exe = r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"

# Eliminar el DWG antiguo para evitar avisos de sobreescritura
if os.path.exists(dwg_path):
    try:
        os.remove(dwg_path)
        print("Old DWG deleted.")
    except Exception as e:
        print("Error deleting old DWG:", e)

# Script de AutoCAD (SCR)
script_content = f"""FILEDIA
0
CMDDIA
0
DXFIN
"{dxf_path}"
SAVEAS

"{dwg_path}"
QUIT
"""

with open(scr_path, "w", encoding="utf-8") as f:
    f.write(script_content)

print("Starting AutoCAD accoreconsole to convert DXF to DWG...")
cmd = [cad_exe, "/s", scr_path]
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

print("Exit code:", result.returncode)
print("STDOUT:")
stdout_clean = result.stdout.replace("\x00", "").replace("   ", " ").replace("  ", " ")
print(stdout_clean[:5000])

if os.path.exists(dwg_path):
    print("SUCCESS: DWG generated at", dwg_path)
else:
    print("FAILURE: DWG not generated!")
