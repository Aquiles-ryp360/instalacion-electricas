import subprocess
import os
import time

dwg_path = r"C:\Users\renzo\instalacion-electricas\latex\planos\AVANCE DEL PLANO ELECTRICO1.dwg"
pdf_path = r"C:\Users\renzo\instalacion-electricas\latex\planos\AVANCE DEL PLANO ELECTRICO1.pdf"
scr_path = r"C:\Users\renzo\instalacion-electricas\latex\build\plot_plano.scr"
cad_exe = r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"

# If PDF already exists, let's delete it so we are sure a new one is generated
if os.path.exists(pdf_path):
    try:
        os.remove(pdf_path)
    except Exception as e:
        print("Error deleting old PDF:", e)

# SCR content
# We add BACKGROUNDPLOT 0 to force synchronous plot writing
script_content = f"""FILEDIA
0
CMDDIA
0
BACKGROUNDPLOT
0
-PLOT
Y
Model
DWG To PDF.pc3
ISO full bleed A3 (420.00 x 297.00 MM)
Millimeters
Landscape
No
Extents
Fit
Center
Yes
monochrome.ctb
Yes
As displayed
Yes
"{pdf_path}"
No
Yes
QUIT
Y
"""

with open(scr_path, "w", encoding="utf-8") as f:
    f.write(script_content)

print("Starting AutoCAD accoreconsole...")
cmd = [cad_exe, "/i", dwg_path, "/s", scr_path]
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

print("Exit code:", result.returncode)
print("STDOUT (first 5000 chars):")
# Let's clean the double space in unicode outputs from accoreconsole
stdout_clean = result.stdout.replace("\x00", "").replace("   ", " ").replace("  ", " ")
print(stdout_clean[:5000])

# Wait up to 5 seconds just in case there's any file writing delay
for _ in range(5):
    if os.path.exists(pdf_path):
        break
    time.sleep(1)

if os.path.exists(pdf_path):
    print("SUCCESS: PDF generated at", pdf_path)
else:
    print("FAILURE: PDF not generated!")
