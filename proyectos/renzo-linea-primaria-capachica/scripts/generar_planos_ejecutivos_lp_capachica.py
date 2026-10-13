# -*- coding: utf-8 -*-
"""
generar_planos_ejecutivos_lp_capachica.py
Generador Maestro de Planos Ejecutivos y Láminas Oficiales de Línea Primaria 22.9 kV:
Proyecto: Electrificación Rural Capachica a Chifrón (22.9 kV, 3Ø, AAAC 35 mm², SAB-1 100 kVA)
Normas Técnicas: DGE R.D. 018-2003-EM/DGE, CNE Suministro 2011, NTP 339.027, IEC 60071-2 / IEC 60076

Genera el paquete completo de 6 láminas ejecutivas en Formato A3 (420 x 297 mm) en DXF (AutoCAD R2010),
PDF de alta resolución vectorial (300 DPI) y PNG de vista previa:
- Lámina LP-01: Plano de Traza y Planta General de la Línea Primaria 22.9 kV (Capachica - Chifrón, Esc. 1:2000)
- Lámina PL-01: Perfil Longitudinal Topográfico y Spotting de Estructuras LP 22.9 kV (H: 1:2000, V: 1:500)
- Lámina U-01:  Diagrama Unifilar General y Esquema de Protecciones de Media Tensión (22.9 kV y SAB-1 100 kVA)
- Lámina D-01:  Detalles de Armados Normalizados DGE PS-1 y PA-1 en Media Tensión 22.9 kV
- Lámina D-02:  Detalles de Armado DGE PR-1 y Subestación Aérea Biposte SAB-1 100 kVA
- Lámina D-03:  Detalles de Cimentaciones Sulzberger, Retenidas Mecánicas R-1 y Puesta a Tierra PAT-3

Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
Curso: MEC330 - Instalaciones Eléctricas II | FIME - UNA Puno
Docentes: Ing. Leonidas Vilca Callata / Ing. Marcos José Villanueva Cornejo
"""

import os
import sys
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch
from matplotlib.lines import Line2D
import ezdxf
from ezdxf import colors

# -----------------------------------------------------------------------------
# 1. MATRIZ DE ESTRUCTURAS CANÓNICAS DE LA LÍNEA PRIMARIA CAPACHICA - CHIFRÓN
# -----------------------------------------------------------------------------
ESTRUCTURAS_LP = [
    {
        "id": "E-01", "prog": 0.00, "cota": 3924.17, "este": 412606.01, "norte": 8270712.24,
        "poste": "C.A.C. 12/400", "armado": "PR-1", "tipo": "Derivación MT (TAP)",
        "ang": 0.00, "ret": "Inclinada simple R-1", "pat": "PAT-3", "h_total": 12.0, "empot": 1.40,
        "desc": "Derivación en cresta Cerro Chifrón (Cut-Out 27 kV + ZnO 21 kV)"
    },
    {
        "id": "E-02", "prog": 105.00, "cota": 3895.00, "este": 412658.71, "norte": 8270803.07,
        "poste": "C.A.C. 12/300", "armado": "PS-1", "tipo": "Suspensión alineamiento",
        "ang": 0.00, "ret": "Ninguna", "pat": None, "h_total": 12.0, "empot": 1.40,
        "desc": "Suspensión en ladera pronunciada Cerro Chifrón"
    },
    {
        "id": "E-03", "prog": 210.00, "cota": 3865.00, "este": 412711.42, "norte": 8270893.91,
        "poste": "C.A.C. 12/300", "armado": "PS-1", "tipo": "Suspensión paso",
        "ang": 0.00, "ret": "Ninguna", "pat": None, "h_total": 12.0, "empot": 1.40,
        "desc": "Suspensión paso hacia caserío rural"
    },
    {
        "id": "E-04", "prog": 305.21, "cota": 3839.56, "este": 412759.20, "norte": 8270976.22,
        "poste": "2x C.A.C. 13/400 (Biposte)", "armado": "SAB-1", "tipo": "SED Biposte 100 kVA",
        "ang": -35.20, "ret": "Contraviento doble R-1", "pat": "PAT-3", "h_total": 13.0, "empot": 1.50,
        "desc": "SED Biposte SAB-1 100 kVA (22.9/0.38-0.22 kV Dyn5)"
    },
    {
        "id": "E-05", "prog": 402.43, "cota": 3817.04, "este": 412750.60, "norte": 8271073.06,
        "poste": "C.A.C. 12/400", "armado": "PA-1", "tipo": "Ángulo con retenida",
        "ang": -36.06, "ret": "Biselar simple R-1", "pat": None, "h_total": 12.0, "empot": 1.40,
        "desc": "Ángulo hacia camino secundario Chifrón"
    },
    {
        "id": "E-06", "prog": 518.02, "cota": 3827.27, "este": 412684.34, "norte": 8271166.70,
        "poste": "C.A.C. 12/400", "armado": "PA-1", "tipo": "Ángulo vano crítico",
        "ang": 31.35, "ret": "Biselar simple R-1", "pat": None, "h_total": 12.0, "empot": 1.40,
        "desc": "Ángulo vano crítico 115.59m cruce camino vecinal"
    },
    {
        "id": "E-07", "prog": 628.53, "cota": 3824.61, "este": 412677.31, "norte": 8271272.50,
        "poste": "C.A.C. 12/300", "armado": "PS-1", "tipo": "Suspensión alineamiento",
        "ang": -6.05, "ret": "Ninguna", "pat": None, "h_total": 12.0, "empot": 1.40,
        "desc": "Suspensión alineamiento tramo llano"
    },
    {
        "id": "E-08", "prog": 708.34, "cota": 3824.61, "este": 412646.16, "norte": 8271345.24,
        "poste": "C.A.C. 12/400", "armado": "PA-1", "tipo": "Ángulo reforzado",
        "ang": 32.95, "ret": "Biselar simple R-1", "pat": None, "h_total": 12.0, "empot": 1.40,
        "desc": "Ángulo reforzado acceso a playa Chifrón"
    },
    {
        "id": "E-09", "prog": 816.60, "cota": 3824.61, "este": 412659.90, "norte": 8271446.51,
        "poste": "C.A.C. 12/400", "armado": "PR-1", "tipo": "Terminal de línea",
        "ang": 0.00, "ret": "Terminal simple R-1", "pat": "PAT-3", "h_total": 12.0, "empot": 1.40,
        "desc": "Terminal de línea primaria fin de red Chifrón"
    }
]

# Datos de vanos vano a vano
VANOS_LP = [
    {"num": 1, "de": "E-01", "a": "E-02", "long": 105.00, "desnivel": -29.17, "flecha_max": 1.054, "galibo": 9.55},
    {"num": 2, "de": "E-02", "a": "E-03", "long": 105.00, "desnivel": -30.00, "flecha_max": 1.054, "galibo": 9.55},
    {"num": 3, "de": "E-03", "a": "E-04", "long": 95.21,  "desnivel": -25.44, "flecha_max": 0.889, "galibo": 10.16},
    {"num": 4, "de": "E-04", "a": "E-05", "long": 97.22,  "desnivel": -22.52, "flecha_max": 0.922, "galibo": 10.13},
    {"num": 5, "de": "E-05", "a": "E-06", "long": 115.59, "desnivel": 10.23,  "flecha_max": 1.244, "galibo": 9.36},
    {"num": 6, "de": "E-06", "a": "E-07", "long": 110.51, "desnivel": -2.66,  "flecha_max": 1.151, "galibo": 9.45},
    {"num": 7, "de": "E-07", "a": "E-08", "long": 79.81,  "desnivel": 0.00,   "flecha_max": 0.653, "galibo": 9.95},
    {"num": 8, "de": "E-08", "a": "E-09", "long": 108.26, "desnivel": 0.00,   "flecha_max": 1.111, "galibo": 9.49}
]

# Vía de acceso principal Capachica - Chifrón (coordenadas aproximadas eje camino)
CAMINO_CAPACHICA_CHIFRON = [
    (412580.0, 8270700.0), (412620.0, 8270770.0), (412660.0, 8270850.0),
    (412710.0, 8270940.0), (412735.0, 8271020.0), (412705.0, 8271120.0),
    (412670.0, 8271200.0), (412650.0, 8271300.0), (412630.0, 8271400.0),
    (412640.0, 8271500.0)
]

# -----------------------------------------------------------------------------
# 2. FUNCIONES DE MARCO Y RÓTULO OFICIAL NORMALIZADO (A3)
# -----------------------------------------------------------------------------
def dibujar_marco_a3(fig, titulo_l1: str, titulo_l2: str):
    """Crea el marco formal perimetral A3 con margen normalizado y franja de título."""
    ax_box = fig.add_axes([0.015, 0.015, 0.970, 0.970])
    ax_box.axis('off')
    
    # Bordes perimetrales de plano oficial
    rect_ext = patches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='#0F172A', linewidth=2.0)
    rect_int = patches.Rectangle((0.004, 0.004), 0.992, 0.992, facecolor='none', edgecolor='#0F172A', linewidth=0.8)
    ax_box.add_patch(rect_ext)
    ax_box.add_patch(rect_int)

    # Franja superior institucional
    ax_head = fig.add_axes([0.025, 0.938, 0.950, 0.040])
    ax_head.axis('off')
    rect_head = patches.Rectangle((0, 0), 1, 1, facecolor='#F8FAFC', edgecolor='#1E3A8A', linewidth=1.1)
    ax_head.add_patch(rect_head)
    ax_head.text(0.5, 0.68, titulo_l1, ha='center', va='center', fontsize=9.2, fontweight='bold', color='#1E3A8A')
    ax_head.text(0.5, 0.28, titulo_l2, ha='center', va='center', fontsize=6.8, fontweight='bold', color='#334155')


def dibujar_rotulo_oficial(ax, x0, y0, w, h, plano_cod, plano_nom_l1, plano_nom_l2, escala="1 : 2000"):
    """Dibuja el rótulo oficial de ingeniería conforme a normas DGE / UNA Puno."""
    ax.axis('off')
    ax.set_xlim(x0, x0 + w)
    ax.set_ylim(y0, y0 + h)
    
    rect_ext = patches.Rectangle((x0, y0), w, h, facecolor='#FFFFFF', edgecolor='#0F172A', linewidth=1.4, zorder=50)
    ax.add_patch(rect_ext)
    
    # Líneas divisorias horizontales
    h_filas = [0.18, 0.36, 0.52, 0.68, 0.84]
    for hf in h_filas:
        ax.plot([x0, x0 + w], [y0 + hf * h, y0 + hf * h], color='#334155', linewidth=0.7, zorder=51)
        
    ax.plot([x0 + w * 0.35, x0 + w * 0.35], [y0, y0 + 0.18 * h], color='#334155', linewidth=0.7, zorder=51)
    ax.plot([x0 + w * 0.68, x0 + w * 0.68], [y0, y0 + 0.18 * h], color='#334155', linewidth=0.7, zorder=51)
    
    # Textos Institucionales
    ax.text(x0 + w/2.0, y0 + 0.93 * h, "UNIVERSIDAD NACIONAL DEL ALTIPLANO — PUNO", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.88 * h, "FACULTAD DE INGENIERÍA MECÁNICA ELÉCTRICA, ELECTRÓNICA Y SISTEMAS", ha='center', va='center', fontsize=5.8, fontweight='bold', color='#1E3A8A', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.78 * h, "ESCUELA PROFESIONAL DE INGENIERÍA MECÁNICA ELÉCTRICA", ha='center', va='center', fontsize=6.3, fontweight='bold', color='#0F766E', zorder=52)
            
    # Título del Proyecto y Plano
    ax.text(x0 + w/2.0, y0 + 0.60 * h, "PROYECTO: LÍNEA PRIMARIA 22.9 kV Y SUBESTACIÓN SAB-1 100 kVA", ha='center', va='center', fontsize=5.5, fontweight='bold', color='#0F172A', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.55 * h, "SECTOR CHIFRÓN — DISTRITO DE CAPACHICA — PUNO", ha='center', va='center', fontsize=5.2, color='#334155', zorder=52)

    ax.text(x0 + w/2.0, y0 + 0.45 * h, f"PLANO: {plano_nom_l1}", ha='center', va='center', fontsize=6.2, fontweight='bold', color='#B45309', zorder=52)
    ax.text(x0 + w/2.0, y0 + 0.39 * h, plano_nom_l2, ha='center', va='center', fontsize=5.8, fontweight='bold', color='#B45309', zorder=52)
            
    # Datos Proyectista y Docentes
    ax.text(x0 + 0.03 * w, y0 + 0.27 * h, "PROYECTISTA:\nDOCENTES:", ha='left', va='center', fontsize=5.2, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.27 * w, y0 + 0.27 * h, "Br. Renzo Gabriel Mamani Galindo (Cód. 228447)\nIng. Leonidas Vilca Callata  /  Ing. Marcos José Villanueva Cornejo", ha='left', va='center', fontsize=5.2, color='#0F172A', zorder=52)
            
    # Casillas finales
    ax.text(x0 + 0.175 * w, y0 + 0.125 * h, "FECHA:", ha='center', va='center', fontsize=5.2, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.175 * w, y0 + 0.055 * h, "Octubre 2026", ha='center', va='center', fontsize=5.2, color='#334155', zorder=52)

    ax.text(x0 + 0.515 * w, y0 + 0.125 * h, "ESCALA:", ha='center', va='center', fontsize=5.2, fontweight='bold', color='#334155', zorder=52)
    ax.text(x0 + 0.515 * w, y0 + 0.055 * h, escala, ha='center', va='center', fontsize=5.2, color='#334155', zorder=52)

    ax.text(x0 + 0.840 * w, y0 + 0.125 * h, "LÁMINA:", ha='center', va='center', fontsize=5.4, fontweight='bold', color='#1E3A8A', zorder=52)
    ax.text(x0 + 0.840 * w, y0 + 0.055 * h, plano_cod, ha='center', va='center', fontsize=7.6, fontweight='bold', color='#1E3A8A', zorder=52)


# =============================================================================
# 3. GENERADOR DE LÁMINA LP-01: PLANTA Y TRAZA GENERAL LÍNEA PRIMARIA 22.9 kV
# =============================================================================
def generar_lamina_lp01_planta(pdf_path: str, png_path: str, dxf_path: str):
    """Genera la Lámina Oficial LP-01: Plano de Traza y Planta General de Línea Primaria 22.9 kV."""
    print("-> Generando Lámina LP-01 (Planta y Traza General LP 22.9 kV)...")
    
    # 1. GENERACIÓN GRÁFICA EN MATPLOTLIB (PDF A3 & PNG)
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    dibujar_marco_a3(fig,
                     "PROYECTO DE INGENIERÍA DE DETALLE — LÍNEA PRIMARIA 22.9 kV CAPACHICA A CHIFRÓN",
                     "PLANO DE TRAZA, REPLANTEO TOPOGRÁFICO, SERVIDUMBRE Y ESTRUCTURAS EN MEDIA TENSIÓN")

    # Ventana de Cartografía y Planta General (E: 412500 - 412900, N: 8270650 - 8271550)
    ax_mapa = fig.add_axes([0.035, 0.055, 0.590, 0.870])
    ax_mapa.set_facecolor('#F8FAFC')
    ax_mapa.set_xlim(412500, 412850)
    ax_mapa.set_ylim(8270650, 8271520)
    ax_mapa.set_xlabel("Coordenada UTM Este (m) - WGS84 Zona 19S", fontsize=7, fontweight='bold', color='#334155')
    ax_mapa.set_ylabel("Coordenada UTM Norte (m) - WGS84 Zona 19S", fontsize=7, fontweight='bold', color='#334155')
    ax_mapa.grid(True, linestyle='--', color='#CBD5E1', linewidth=0.5, alpha=0.7)
    ax_mapa.tick_params(labelsize=6)

    # Dibujar Camino Capachica - Chifrón
    cx = [p[0] for p in CAMINO_CAPACHICA_CHIFRON]
    cy = [p[1] for p in CAMINO_CAPACHICA_CHIFRON]
    ax_mapa.plot(cx, cy, color='#94A3B8', linewidth=4.0, zorder=3, alpha=0.6, label='Camino vecinal Capachica - Chifrón')
    ax_mapa.plot(cx, cy, color='#64748B', linewidth=1.2, linestyle='--', zorder=4)

    # Dibujar Faja de Servidumbre Legal (6.00 m = 3.00 m a cada lado)
    pts_mt = [(p["este"], p["norte"]) for p in ESTRUCTURAS_LP]
    for i in range(len(pts_mt) - 1):
        x1, y1 = pts_mt[i]
        x2, y2 = pts_mt[i+1]
        dx = x2 - x1
        dy = y2 - y1
        L = math.sqrt(dx**2 + dy**2)
        nx = -dy / L * 3.0
        ny = dx / L * 3.0
        # Polígono de faja
        faja_poly = Polygon([
            (x1 + nx, y1 + ny), (x2 + nx, y2 + ny),
            (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)
        ], closed=True, facecolor='#FEF08A', edgecolor='#EAB308', linewidth=0.6, linestyle=':', alpha=0.45, zorder=2)
        ax_mapa.add_patch(faja_poly)

    # Dibujar Traza Troncal de Línea Primaria (3x AAAC 35 mm²)
    px = [p[0] for p in pts_mt]
    py = [p[1] for p in pts_mt]
    ax_mapa.plot(px, py, color='#1D4ED8', linewidth=2.2, zorder=8, label='Línea Primaria 22.9 kV (AAAC 35 mm²)')

    # Resaltar vano critico E-05 - E-06 para sustentacion mecanica y galibo.
    e05 = next(p for p in ESTRUCTURAS_LP if p["id"] == "E-05")
    e06 = next(p for p in ESTRUCTURAS_LP if p["id"] == "E-06")
    ax_mapa.plot([e05["este"], e06["este"]], [e05["norte"], e06["norte"]],
                 color='#DC2626', linewidth=3.1, zorder=9, alpha=0.95,
                 label='Vano critico E-05 - E-06 (115.59 m)')
    xm = (e05["este"] + e06["este"]) / 2.0
    ym = (e05["norte"] + e06["norte"]) / 2.0
    ax_mapa.text(xm + 9.0, ym + 10.0, "VANO CRITICO\nE-05 - E-06\n115.59 m",
                 fontsize=5.8, fontweight='bold', color='#991B1B', ha='left',
                 bbox=dict(boxstyle='round,pad=0.18', fc='#FEF2F2', ec='#DC2626', lw=0.7, alpha=0.96),
                 zorder=22)

    # Dibujar Estructuras y Detalles
    for p in ESTRUCTURAS_LP:
        ex, ey = p["este"], p["norte"]
        pid = p["id"]
        arm = p["armado"]
        
        # Símbolo de poste
        if pid == "E-04":  # Biposte SAB-1
            c1 = Circle((ex - 2.5, ey), 2.2, facecolor='#FEE2E2', edgecolor='#DC2626', linewidth=1.2, zorder=15)
            c2 = Circle((ex + 2.5, ey), 2.2, facecolor='#FEE2E2', edgecolor='#DC2626', linewidth=1.2, zorder=15)
            plat = Rectangle((ex - 4.5, ey - 1.2), 9.0, 2.4, facecolor='#EF4444', edgecolor='#B91C1C', lw=0.8, zorder=14)
            ax_mapa.add_patch(c1)
            ax_mapa.add_patch(c2)
            ax_mapa.add_patch(plat)
        else:
            fc = '#DBEAFE' if arm == "PS-1" else ('#FEF3C7' if arm == "PA-1" else '#FEE2E2')
            ec = '#1D4ED8' if arm == "PS-1" else ('#D97706' if arm == "PA-1" else '#DC2626')
            c = Circle((ex, ey), 2.2, facecolor=fc, edgecolor=ec, linewidth=1.1, zorder=15)
            ax_mapa.add_patch(c)
            ax_mapa.plot(ex, ey, marker='.', color=ec, markersize=3, zorder=16)

        # Retenidas R-1 si existen
        if "R-1" in p["ret"]:
            dx_ret, dy_ret = -8.0, -8.0
            if p["ang"] > 0:
                dx_ret, dy_ret = 8.0, -8.0
            ax_mapa.plot([ex, ex + dx_ret], [ey, ey + dy_ret], color='#C2410C', linewidth=1.1, zorder=10)
            ax_mapa.plot(ex + dx_ret, ey + dy_ret, marker='s', color='#D97706', markersize=4, zorder=11)

        # Puesta a tierra PAT-3 si existe
        if p["pat"]:
            ax_mapa.plot([ex, ex], [ey, ey - 6.0], color='#16A34A', linewidth=0.9, zorder=10)
            for yo, wo in [(-6.0, 3.0), (-7.0, 2.0), (-8.0, 1.0)]:
                ax_mapa.plot([ex - wo, ex + wo], [ey + yo, ey + yo], color='#16A34A', linewidth=0.9, zorder=10)

        # Texto informativo de estructura
        off_x, off_y = (6.0, 3.0)
        ha = 'left'
        if pid in ["E-01", "E-05"]:
            off_x, ha = (-8.0, 'right')
        ax_mapa.text(ex + off_x, ey + off_y, f"{pid}\n({arm})", fontsize=5.8, fontweight='bold',
                     color='#0F172A', ha=ha, va='center',
                     bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='#64748B', lw=0.5, alpha=0.95), zorder=20)

    # Toponimia geográfica
    ax_mapa.text(412530, 8270720, "CERRO CHIFRÓN\nCresta EL 3924 msnm\n(Derivación Electro Puno)",
                 fontsize=6.2, fontweight='bold', color='#475569', ha='center',
                 bbox=dict(boxstyle='square,pad=0.2', fc='#F1F5F9', ec='#94A3B8', lw=0.6))
    ax_mapa.text(412790, 8270990, "E-04 SED SAB-1\nPunto de llegada MT\n100 kVA",
                 fontsize=6.2, fontweight='bold', color='#B91C1C', ha='left',
                 bbox=dict(boxstyle='square,pad=0.2', fc='#FEF2F2', ec='#DC2626', lw=0.6))
    ax_mapa.text(412540, 8271380, "PLAYA CHIFRÓN / LAGO TITICACA\n(Cota 3812 msnm - Zona Turística)",
                 fontsize=6.2, fontweight='bold', color='#0284C7', ha='center',
                 bbox=dict(boxstyle='square,pad=0.2', fc='#E0F2FE', ec='#0284C7', lw=0.6))

    # Rosa Náutica / Norte Geográfico
    ax_mapa.annotate('N', xy=(412535, 8271460), xytext=(412535, 8271420),
                     arrowprops=dict(facecolor='#1E3A8A', edgecolor='#0F172A', width=2.5, headwidth=7),
                     ha='center', va='center', fontsize=9, fontweight='bold', color='#1E3A8A', zorder=25)

    # PANEL DERECHO: CUADROS TÉCNICOS Y ESPECIFICACIONES (X: 0.640 a 0.970)
    # 1. Cuadro de Estructuras de Línea Primaria
    ax_tbl = fig.add_axes([0.640, 0.535, 0.330, 0.390])
    ax_tbl.axis('off')
    rect_tbl = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#1E3A8A', linewidth=1.1)
    ax_tbl.add_patch(rect_tbl)
    ax_tbl.text(0.5, 0.95, "CUADRO TÉCNICO DE ESTRUCTURAS LP 22.9 kV", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A')
    ax_tbl.plot([0.03, 0.97], [0.91, 0.91], color='#1E3A8A', linewidth=0.8)

    headers = ["ID", "Prog(m)", "Cota", "Poste", "Arm", "Ang(°)", "Retenida", "PAT"]
    x_cols = [0.03, 0.12, 0.23, 0.34, 0.54, 0.63, 0.74, 0.91]
    for hc, xc in zip(headers, x_cols):
        ax_tbl.text(xc, 0.86, hc, fontsize=4.9, fontweight='bold', color='#0F172A')
    ax_tbl.plot([0.03, 0.97], [0.83, 0.83], color='#CBD5E1', linewidth=0.6)

    y_pos = 0.76
    for p in ESTRUCTURAS_LP:
        vals = [
            p["id"], f"{p['prog']:.1f}", f"{p['cota']:.1f}",
            p["poste"].replace("C.A.C. ", ""), p["armado"],
            f"{p['ang']:+.1f}" if p["ang"] != 0 else "0.0",
            p["ret"].replace(" simple R-1", "").replace(" doble R-1", "x2").replace("Ninguna", "-"),
            p["pat"] if p["pat"] else "-"
        ]
        for v, xc in zip(vals, x_cols):
            ax_tbl.text(xc, y_pos, v, fontsize=4.6, color='#334155')
        y_pos -= 0.082

    # 2. Cuadro de Notas Técnicas de Línea Primaria y Leyenda
    ax_not = fig.add_axes([0.640, 0.295, 0.330, 0.225])
    ax_not.axis('off')
    rect_not = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.1)
    ax_not.add_patch(rect_not)
    ax_not.text(0.5, 0.92, "NOTAS TÉCNICAS Y LEYENDA NORMALIZADA DGE", ha='center', va='center', fontsize=6.5, fontweight='bold', color='#1E3A8A')
    ax_not.plot([0.03, 0.97], [0.85, 0.85], color='#334155', linewidth=0.7)

    notas = [
        "1. Tensión de Servicio: 22.9 kV trifásico, 3 hilos (3Ø), 60 Hz.",
        "2. Conductor de Fase: AAAC 35 mm² (sección real 34.36 mm², 7 hilos).",
        "3. Faja de Servidumbre Legal: 6.00 m (3.00 m a cada lado del eje de trazo).",
        "4. CNE Suministro Regla 219 y R.D. 018-2003-EM/DGE: Gálibo mínimo 6.50 m.",
        "5. Aislamiento Polimérico HTV 25 kV, línea de fuga mínima 810 mm.",
        "6. Cimentaciones en concreto ciclópeo f'c=140 kg/cm² + 30% PM (Sulzberger)."
    ]
    yn = 0.74
    for nt in notas:
        ax_not.text(0.04, yn, nt, fontsize=4.7, color='#0F172A')
        yn -= 0.120

    # 3. Rótulo Oficial de Ingeniería Lámina LP-01
    dibujar_rotulo_oficial(fig.add_axes([0.640, 0.045, 0.330, 0.235]), 0, 0, 1, 1,
                           plano_cod="LP-01",
                           plano_nom_l1="PLANO DE TRAZA, PLANTA GENERAL Y",
                           plano_nom_l2="SERVIDUMBRE DE LÍNEA PRIMARIA 22.9 kV",
                           escala="1 : 2000")

    fig.savefig(pdf_path, format='pdf', dpi=300)
    fig.savefig(png_path, format='png', dpi=300)
    plt.close(fig)
    print(f"  [OK PDF] {pdf_path}")
    print(f"  [OK PNG] {png_path}")

    # 2. GENERACIÓN DEL ARCHIVO CAD DXF (AUTOCAD R2010)
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    doc.layers.add("LP_EJE_MT_22KV", color=colors.BLUE)
    doc.layers.add("LP_FAJA_SERVIDUMBRE", color=colors.YELLOW)
    doc.layers.add("LP_POSTES_CAC", color=colors.CYAN)
    doc.layers.add("LP_RETENIDAS_R1", color=colors.RED)
    doc.layers.add("LP_PUESTA_A_TIERRA", color=colors.GREEN)
    doc.layers.add("LP_VIAS_ACCESO", color=colors.WHITE)
    doc.layers.add("LP_COTAS_Y_TEXTOS", color=colors.MAGENTA)

    # Eje de línea MT
    msp.add_lwpolyline(pts_mt, dxfattribs={"layer": "LP_EJE_MT_22KV", "lineweight": 50})

    # Camino
    msp.add_lwpolyline(CAMINO_CAPACHICA_CHIFRON, dxfattribs={"layer": "LP_VIAS_ACCESO", "lineweight": 25})

    # Estructuras
    for p in ESTRUCTURAS_LP:
        ex, ey = p["este"], p["norte"]
        msp.add_circle((ex, ey), radius=2.5, dxfattribs={"layer": "LP_POSTES_CAC"})
        msp.add_text(f"{p['id']} - {p['armado']} ({p['cota']:.1f}m)",
                     dxfattribs={"layer": "LP_COTAS_Y_TEXTOS", "height": 2.2}).set_placement((ex + 3.0, ey + 3.0))

        # Retenidas
        if "R-1" in p["ret"]:
            dxr = -8.0 if p["ang"] <= 0 else 8.0
            msp.add_line((ex, ey), (ex + dxr, ey - 8.0), dxfattribs={"layer": "LP_RETENIDAS_R1"})

    doc.saveas(dxf_path)
    print(f"  [OK DXF] {dxf_path}")


# =============================================================================
# 4. GENERADOR DE LÁMINA PL-01: PERFIL LONGITUDINAL Y SPOTTING LP 22.9 kV
# =============================================================================
def generar_lamina_pl01_perfil(pdf_path: str, png_path: str, dxf_path: str):
    """Genera la Lámina Oficial PL-01: Perfil Longitudinal Topográfico y Catenarias."""
    print("-> Generando Lámina PL-01 (Perfil Longitudinal y Spotting LP 22.9 kV)...")
    
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    dibujar_marco_a3(fig,
                     "PROYECTO DE INGENIERÍA DE DETALLE — LÍNEA PRIMARIA 22.9 kV CAPACHICA A CHIFRÓN",
                     "PLANO DE PERFIL LONGITUDINAL TOPOGRÁFICO, SPOTTING Y CATENARIAS (CNE SUMINISTRO)")

    # Gráfica Principal de Perfil (Progresiva 0 a 830 m, Cota 3810 a 3935 msnm)
    # Escala deformada H: 1/2000, V: 1/500 (relación 1:4)
    ax_prf = fig.add_axes([0.040, 0.280, 0.925, 0.640])
    ax_prf.set_facecolor('#FFFFFF')
    ax_prf.set_xlim(-20, 835)
    ax_prf.set_ylim(3810, 3940)
    ax_prf.set_ylabel("Cota Topográfica (msnm)", fontsize=7.5, fontweight='bold', color='#1E3A8A')
    ax_prf.grid(True, linestyle='--', color='#E2E8F0', linewidth=0.5)
    ax_prf.tick_params(labelsize=6)

    progs = [p["prog"] for p in ESTRUCTURAS_LP]
    cotas = [p["cota"] for p in ESTRUCTURAS_LP]

    # Terreno Natural con achurado de suelo
    ax_prf.plot(progs, cotas, color='#78350F', linewidth=1.8, label='Perfil del Terreno Natural', zorder=5)
    ax_prf.fill_between(progs, 3810, cotas, facecolor='#FEF3C7', alpha=0.35, zorder=2)

    # Postes y Catenarias vano a vano
    for i in range(len(ESTRUCTURAS_LP) - 1):
        p1 = ESTRUCTURAS_LP[i]
        p2 = ESTRUCTURAS_LP[i+1]
        x1, y1 = p1["prog"], p1["cota"]
        x2, y2 = p2["prog"], p2["cota"]
        h1 = 11.5 if p1["id"] == "E-04" else 10.6
        h2 = 11.5 if p2["id"] == "E-04" else 10.6

        # Catenaria Flecha Máxima (+35°C)
        f_max = VANOS_LP[i]["flecha_max"]
        xs = [x1 + k * (x2 - x1) / 30.0 for k in range(31)]
        ys_catenaria_max = []
        ys_galibo_min = []
        for x in xs:
            u = (x - x1) / (x2 - x1)
            # Recta cuerda + parábola de flecha
            y_cuerda = (y1 + h1) + u * ((y2 + h2) - (y1 + h1))
            flecha = 4.0 * f_max * u * (1.0 - u)
            y_cat = y_cuerda - flecha
            ys_catenaria_max.append(y_cat)
            ys_galibo_min.append(y_cat - 6.50)  # Límite CNE

        # Dibujar Catenaria Flecha Máxima (+35°C)
        ax_prf.plot(xs, ys_catenaria_max, color='#1D4ED8', linewidth=1.4, zorder=10,
                    label='Catenaria Flecha Máx. (+35°C)' if i == 0 else "")
        # Dibujar Catenaria con Hielo (-5°C, 6mm hielo)
        ys_cat_hielo = [yc + 0.18 for yc in ys_catenaria_max]
        ax_prf.plot(xs, ys_cat_hielo, color='#0284C7', linewidth=0.8, linestyle='-.', zorder=9,
                    label='Catenaria Hielo Máx. (-5°C)' if i == 0 else "")
        # Dibujar Envolvente de Gálibo
        ax_prf.plot(xs, ys_galibo_min, color='#16A34A', linewidth=0.7, linestyle=':', zorder=6,
                    label='Envolvente Gálibo CNE (6.50m)' if i == 0 else "")

    # Dibujar Fuste de Postes y Cruces
    for p in ESTRUCTURAS_LP:
        prg, cta, pid, arm = p["prog"], p["cota"], p["id"], p["armado"]
        h_util = 11.5 if pid == "E-04" else 10.6
        ax_prf.plot([prg, prg], [cta, cta + h_util], color='#0F172A', linewidth=2.2, zorder=12)
        # Cruceta en cima
        ax_prf.plot([prg - 2.5, prg + 2.5], [cta + h_util, cta + h_util], color='#D97706', linewidth=1.5, zorder=13)
        # Etiqueta de estructura
        ax_prf.text(prg, cta + h_util + 2.5, f"{pid}\n{arm}\nH={p['h_total']}m",
                    fontsize=5.3, fontweight='bold', color='#1E3A8A', ha='center', va='bottom',
                    bbox=dict(boxstyle='square,pad=0.15', fc='white', ec='#1E3A8A', lw=0.4, alpha=0.95), zorder=20)

    # Cruce de Camino en vano E-05 a E-06
    ax_prf.annotate('Cruce Camino Vecinal\n(Gálibo medido = 9.36 m > 7.00 m)',
                    xy=(460.0, 3822.0), xytext=(460.0, 3845.0),
                    arrowprops=dict(arrowstyle='->', color='#B91C1C', lw=1.0),
                    fontsize=5.5, fontweight='bold', color='#B91C1C', ha='center',
                    bbox=dict(boxstyle='round,pad=0.2', fc='#FEF2F2', ec='#DC2626', lw=0.5))

    ax_prf.legend(loc='upper right', fontsize=6.2, framealpha=0.95)

    # TABLA GUITARRA TÉCNICA INFERIOR (SPOT TABLE)
    ax_tbl_prf = fig.add_axes([0.040, 0.050, 0.585, 0.205])
    ax_tbl_prf.axis('off')
    rect_gt = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#1E3A8A', linewidth=1.1)
    ax_tbl_prf.add_patch(rect_gt)

    filas = [
        ("PROGRESIVA (m):", [f"{p['prog']:.1f}" for p in ESTRUCTURAS_LP]),
        ("COTA TERRENO (msnm):", [f"{p['cota']:.1f}" for p in ESTRUCTURAS_LP]),
        ("COTA CIMA (msnm):", [f"{(p['cota'] + (11.5 if p['id']=='E-04' else 10.6)):.1f}" for p in ESTRUCTURAS_LP]),
        ("VANO HORIZ. (m):", ["-"] + [f"{v['long']:.1f}" for v in VANOS_LP]),
        ("FLECHA MÁX. (m):", ["-"] + [f"{v['flecha_max']:.2f}" for v in VANOS_LP]),
        ("GÁLIBO NORM. (m):", ["-"] + [f"{v['galibo']:.2f}" for v in VANOS_LP]),
        ("ESTRUCTURA C.A.C.:", [p["poste"].replace("C.A.C. ", "") for p in ESTRUCTURAS_LP]),
        ("ARMADO DGE:", [p["armado"] for p in ESTRUCTURAS_LP]),
        ("CIMENTACIÓN:", ["Sulzb. 0.8m"]*3 + ["Sulzb. 0.9m"] + ["Sulzb. 0.8m"]*5)
    ]

    ax_tbl_prf.text(0.5, 0.96, "TABLA DE SPOTTING, VANOS Y VERIFICACIÓN DE GÁLIBOS (CNE REGLA 232)",
                    ha='center', va='center', fontsize=6.2, fontweight='bold', color='#1E3A8A')
    ax_tbl_prf.plot([0.01, 0.99], [0.91, 0.91], color='#1E3A8A', linewidth=0.7)

    y_f = 0.84
    x_pos = [0.22 + k * 0.082 for k in range(9)]
    for tit, dts in filas:
        ax_tbl_prf.text(0.02, y_f, tit, fontsize=4.7, fontweight='bold', color='#0F172A')
        for val, xp in zip(dts, x_pos):
            ax_tbl_prf.text(xp, y_f, val, fontsize=4.4, color='#334155', ha='center')
        y_f -= 0.092

    # Rótulo Oficial de Ingeniería Lámina PL-01
    dibujar_rotulo_oficial(fig.add_axes([0.640, 0.050, 0.325, 0.205]), 0, 0, 1, 1,
                           plano_cod="PL-01",
                           plano_nom_l1="PERFIL LONGITUDINAL TOPOGRÁFICO, SPOTTING",
                           plano_nom_l2="Y CATENARIAS DE LÍNEA PRIMARIA 22.9 kV",
                           escala="H: 1/2000, V: 1/500")

    fig.savefig(pdf_path, format='pdf', dpi=300)
    fig.savefig(png_path, format='png', dpi=300)
    plt.close(fig)
    print(f"  [OK PDF] {pdf_path}")
    print(f"  [OK PNG] {png_path}")

    # DXF PERFIL LONGITUDINAL
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    doc.layers.add("PL_TERRENO_NATURAL", color=colors.YELLOW)
    doc.layers.add("PL_POSTES_CAC", color=colors.CYAN)
    doc.layers.add("PL_CATENARIA_MAX", color=colors.BLUE)
    doc.layers.add("PL_GALIBO_MIN", color=colors.GREEN)
    doc.layers.add("PL_TEXTOS_Y_COTAS", color=colors.WHITE)

    pts_terr = [(p["prog"], p["cota"]) for p in ESTRUCTURAS_LP]
    msp.add_lwpolyline(pts_terr, dxfattribs={"layer": "PL_TERRENO_NATURAL", "lineweight": 35})

    for p in ESTRUCTURAS_LP:
        prg, cta, pid = p["prog"], p["cota"], p["id"]
        hl = 11.5 if pid == "E-04" else 10.6
        msp.add_line((prg, cta), (prg, cta + hl), dxfattribs={"layer": "PL_POSTES_CAC", "lineweight": 40})
        msp.add_text(f"{pid} {cta:.1f}m", dxfattribs={"layer": "PL_TEXTOS_Y_COTAS", "height": 1.8}).set_placement((prg, cta + hl + 1.2))

    doc.saveas(dxf_path)
    print(f"  [OK DXF] {dxf_path}")


# =============================================================================
# 5. GENERADOR DE LÁMINA U-01: DIAGRAMA UNIFILAR Y PROTECCIONES MT (22.9 kV)
# =============================================================================
def generar_lamina_u01_unifilar(pdf_path: str, png_path: str, dxf_path: str):
    """Genera la Lámina Oficial U-01: Diagrama Unifilar General y Esquema de Protecciones MT."""
    print("-> Generando Lámina U-01 (Diagrama Unifilar y Protecciones MT 22.9 kV)...")
    
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    dibujar_marco_a3(fig,
                     "PROYECTO DE INGENIERÍA DE DETALLE — LÍNEA PRIMARIA 22.9 kV CAPACHICA A CHIFRÓN",
                     "DIAGRAMA UNIFILAR GENERAL Y ESQUEMA DE PROTECCIONES DE MEDIA TENSIÓN Y SED 100 kVA")

    # PANEL IZQUIERDO: DIAGRAMA UNIFILAR VECTORIAL UNE-EN 60617
    ax_uni = fig.add_axes([0.035, 0.055, 0.585, 0.870])
    ax_uni.set_facecolor('#FFFFFF')
    ax_uni.axis('off')
    ax_uni.set_xlim(0, 1)
    ax_uni.set_ylim(0, 1)

    rect_u = patches.Rectangle((0.005, 0.005), 0.990, 0.990, facecolor='none', edgecolor='#1E3A8A', linewidth=1.2)
    ax_uni.add_patch(rect_u)

    ax_uni.text(0.5, 0.965, "DIAGRAMA UNIFILAR GENERAL DE MEDIA TENSIÓN 22.9 kV (UNE-EN 60617)",
                ha='center', va='center', fontsize=7.8, fontweight='bold', color='#1E3A8A')
    ax_uni.plot([0.05, 0.95], [0.940, 0.940], color='#1E3A8A', linewidth=0.9)

    # 1. Punto de Conexión / Derivación E-01 (Red Troncal Electro Puno)
    ax_uni.plot([0.15, 0.85], [0.890, 0.890], color='#1E3A8A', linewidth=2.5)
    ax_uni.text(0.50, 0.910, "RED TRONCAL MEDIA TENSIÓN 22.9 kV (ELECTRO PUNO S.A.A. - TRAMO GISEM TMT000012389)",
                ha='center', va='center', fontsize=5.8, fontweight='bold', color='#1E3A8A')

    # Derivación en E-01
    ax_uni.plot([0.50, 0.50], [0.890, 0.830], color='#1E3A8A', linewidth=1.8)
    ax_uni.text(0.53, 0.865, "Punto de Derivación TAP en E-01\n(Cresta Cerro Chifrón 3924 msnm)", fontsize=5.2, color='#334155')

    # Cortacircuito Fusible Seccionador Cut-Out 27 kV en cabecera
    # Símbolo fusible seccionador
    rect_co1 = patches.Rectangle((0.475, 0.770), 0.050, 0.060, facecolor='#FFFFFF', edgecolor='#DC2626', lw=1.2)
    ax_uni.add_patch(rect_co1)
    ax_uni.plot([0.475, 0.525], [0.770, 0.830], color='#DC2626', lw=1.0)
    ax_uni.text(0.55, 0.800, "03 Seccionadores Fusibles Cut-Out 27 kV, 100 A\nBIL 150 kV - Fusible Chicote K de 4 A",
                fontsize=5.1, fontweight='bold', color='#B91C1C', va='center')

    # Pararrayos ZnO 21 kV en nodo E-01
    ax_uni.plot([0.50, 0.40], [0.750, 0.750], color='#1E3A8A', lw=1.2)
    ax_uni.plot([0.40, 0.40], [0.750, 0.700], color='#1E3A8A', lw=1.2)
    rect_pa1 = patches.Rectangle((0.380, 0.660), 0.040, 0.040, facecolor='#FEF3C7', edgecolor='#D97706', lw=1.1)
    ax_uni.add_patch(rect_pa1)
    ax_uni.text(0.40, 0.680, "ZnO", ha='center', va='center', fontsize=4.5, fontweight='bold', color='#B45309')
    # Tierra de pararrayos
    ax_uni.plot([0.40, 0.40], [0.660, 0.630], color='#16A34A', lw=1.0)
    for w_t, y_t in [(0.02, 0.630), (0.014, 0.622), (0.008, 0.614)]:
        ax_uni.plot([0.40 - w_t/2, 0.40 + w_t/2], [y_t, y_t], color='#16A34A', lw=1.0)
    ax_uni.text(0.24, 0.680, "03 Pararrayos ZnO 21 kV\n10 kA (PAT-3: R <= 10 Ω)", fontsize=4.8, color='#15803D', ha='center')

    # Tramo de Línea Primaria 22.9 kV (816.60 m)
    ax_uni.plot([0.50, 0.50], [0.770, 0.520], color='#1D4ED8', linewidth=2.2)
    ax_uni.text(0.53, 0.600, "LÍNEA PRIMARIA MEDIA TENSIÓN 22.9 kV (3Ø)\nConductor: 3x AAAC 35 mm² (34.36 mm² real)\nLongitud: 816.60 m | ΔV = 0.046% | ΔP = 46.2 W\n9 Estructuras C.A.C. (E-01 a E-09)",
                fontsize=5.2, fontweight='bold', color='#1E3A8A', va='center',
                bbox=dict(boxstyle='square,pad=0.2', fc='#EFF6FF', ec='#3B82F6', lw=0.6))

    # Cabecera de Subestación SED E-04 (Chifrón)
    ax_uni.plot([0.50, 0.50], [0.520, 0.440], color='#1E3A8A', lw=1.8)
    rect_co2 = patches.Rectangle((0.475, 0.440), 0.050, 0.050, facecolor='#FFFFFF', edgecolor='#DC2626', lw=1.2)
    ax_uni.add_patch(rect_co2)
    ax_uni.plot([0.475, 0.525], [0.440, 0.490], color='#DC2626', lw=1.0)
    ax_uni.text(0.55, 0.465, "03 Seccionadores Fusibles Cut-Out 27 kV / 100 A (Cabecera SED)", fontsize=5.0, fontweight='bold', color='#B91C1C')

    # Pararrayos de protección trafo
    ax_uni.plot([0.50, 0.40], [0.420, 0.420], color='#1E3A8A', lw=1.2)
    ax_uni.plot([0.40, 0.40], [0.420, 0.380], color='#1E3A8A', lw=1.2)
    rect_pa2 = patches.Rectangle((0.380, 0.340), 0.040, 0.040, facecolor='#FEF3C7', edgecolor='#D97706', lw=1.1)
    ax_uni.add_patch(rect_pa2)
    ax_uni.text(0.40, 0.360, "ZnO", ha='center', va='center', fontsize=4.5, fontweight='bold', color='#B45309')
    ax_uni.plot([0.40, 0.40], [0.340, 0.315], color='#16A34A', lw=1.0)
    for w_t, y_t in [(0.02, 0.315), (0.014, 0.307), (0.008, 0.299)]:
        ax_uni.plot([0.40 - w_t/2, 0.40 + w_t/2], [y_t, y_t], color='#16A34A', lw=1.0)

    # Transformador de Distribución Trifásico 100 kVA (UNE 06-09-01)
    ax_uni.plot([0.50, 0.50], [0.440, 0.300], color='#1E3A8A', lw=1.8)
    c_prim = Circle((0.50, 0.275), 0.032, facecolor='none', edgecolor='#DC2626', lw=1.5)
    c_sec = Circle((0.50, 0.235), 0.032, facecolor='none', edgecolor='#1D4ED8', lw=1.5)
    ax_uni.add_patch(c_prim)
    ax_uni.add_patch(c_sec)
    ax_uni.text(0.50, 0.275, "Δ", ha='center', va='center', fontsize=6.5, fontweight='bold', color='#DC2626')
    ax_uni.text(0.50, 0.235, "Y", ha='center', va='center', fontsize=6.5, fontweight='bold', color='#1D4ED8')

    ax_uni.text(0.56, 0.255, "TRANSFORMADOR DE DISTRIBUCIÓN TRIFÁSICO\nPotencia Nominal: 100 kVA (ONAN)\nRelación de Tensión: 22.9 / 0.38 - 0.22 kV\nGrupo de Conexión: Dyn5 | 60 Hz\nAltitud de Servicio: 3,850 msnm",
                fontsize=5.2, fontweight='bold', color='#0F172A', va='center',
                bbox=dict(boxstyle='square,pad=0.2', fc='#FEF2F2', ec='#DC2626', lw=0.6))

    # Conexión Neutro a Tierra
    ax_uni.plot([0.468, 0.420], [0.235, 0.235], color='#16A34A', lw=1.1)
    ax_uni.plot([0.420, 0.420], [0.235, 0.170], color='#16A34A', lw=1.1)
    for w_t, y_t in [(0.02, 0.170), (0.014, 0.162), (0.008, 0.154)]:
        ax_uni.plot([0.420 - w_t/2, 0.420 + w_t/2], [y_t, y_t], color='#16A34A', lw=1.1)
    ax_uni.text(0.420, 0.135, "PAT-3 Neutro y Masa\n(R <= 10.0 Ω)", ha='center', fontsize=4.8, fontweight='bold', color='#15803D')

    # Limite de alcance: se muestra solo la SED como estructura de llegada de la LP.
    ax_uni.plot([0.50, 0.50], [0.203, 0.145], color='#1D4ED8', lw=1.5)
    ax_uni.plot([0.47, 0.53], [0.145, 0.145], color='#1D4ED8', lw=1.1)
    ax_uni.text(0.50, 0.105, "LIMITE DE ALCANCE\nLINEA PRIMARIA 22.9 kV\nSin desarrollo de red secundaria",
                ha='center', va='center', fontsize=4.9, fontweight='bold', color='#1E3A8A',
                bbox=dict(boxstyle='square,pad=0.18', fc='#EFF6FF', ec='#1E3A8A', lw=0.7))

    # PANEL DERECHO: ESPECIFICACIONES TÉCNICAS Y COORDINACIÓN DE AISLAMIENTO
    ax_esp = fig.add_axes([0.640, 0.320, 0.330, 0.605])
    ax_esp.axis('off')
    rect_e = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#334155', linewidth=1.2)
    ax_esp.add_patch(rect_e)
    ax_esp.text(0.5, 0.965, "ESPECIFICACIONES TÉCNICAS Y EQUIPAMIENTO MT", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')
    ax_esp.plot([0.04, 0.96], [0.935, 0.935], color='#334155', linewidth=0.8)

    especs = [
        ("Nivel de Tensión y Sistema", "22.9 kV entre fases, trifásico 3 hilos (3Ø), 60 Hz, neutro aislado."),
        ("Conductor de Línea", "AAAC 35 mm² (sección real 34.36 mm²), 7 hilos de 2.50 mm, Tr=1040 kgf."),
        ("Transformador de Distribución", "100 kVA, 22.9 / 0.38-0.22 kV, trifásico, Dyn5, ONAN, 60 Hz, Po<=280W, Pk<=1450W."),
        ("Cortacircuitos Fusibles Cut-Out", "03 unidades unipolar tipo expulsión, 27 kV, 100 A, 150 kV BIL, chicote K de 4 A."),
        ("Pararrayos de Distribución ZnO", "03 unidades poliméricos de óxido de zinc, 21 kV, descarga nominal 10 kA Clase 1."),
        ("Aisladores Poliméricos HTV", "Tipo suspensión 25 kV, 6 aletas, línea de fuga 810 mm (Ka=1.25 para 3,850 msnm)."),
        ("Aisladores Tipo Pin MT", "Porcelana vitrificada ANSI 56-3 (25 kV) con espiga de F°G° de 3/4\" x 12\"."),
        ("Sistema de Puesta a Tierra PAT-3", "03 electrodos Cu 5/8\"x2.40m en triángulo con bentonita sódica. R <= 10.0 Ω.")
    ]
    y_esp = 0.890
    for eq, desc in especs:
        ax_esp.text(0.04, y_esp, f"• {eq}:", fontsize=5.4, fontweight='bold', color='#B45309')
        ax_esp.text(0.06, y_esp - 0.038, desc, fontsize=4.9, color='#0F172A')
        y_esp -= 0.108

    # Rótulo Oficial de Ingeniería Lámina U-01
    dibujar_rotulo_oficial(fig.add_axes([0.640, 0.045, 0.330, 0.255]), 0, 0, 1, 1,
                           plano_cod="U-01",
                           plano_nom_l1="DIAGRAMA UNIFILAR GENERAL Y ESQUEMA DE",
                           plano_nom_l2="PROTECCIONES DE MEDIA TENSIÓN 22.9 kV",
                           escala="INDICADA")

    fig.savefig(pdf_path, format='pdf', dpi=300)
    fig.savefig(png_path, format='png', dpi=300)
    plt.close(fig)
    print(f"  [OK PDF] {pdf_path}")
    print(f"  [OK PNG] {png_path}")

    # DXF UNIFILAR
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    doc.layers.add("U_LINEAS_MT", color=colors.BLUE)
    doc.layers.add("U_EQUIPOS_MT", color=colors.RED)
    doc.layers.add("U_TIERRA_PAT", color=colors.GREEN)
    doc.layers.add("U_TEXTOS", color=colors.WHITE)

    msp.add_line((0, 100), (100, 100), dxfattribs={"layer": "U_LINEAS_MT", "lineweight": 50})
    msp.add_text("RED TRONCAL ELECTRO PUNO 22.9 kV", dxfattribs={"layer": "U_TEXTOS", "height": 3.0}).set_placement((10, 105))
    msp.add_line((50, 100), (50, 40), dxfattribs={"layer": "U_LINEAS_MT", "lineweight": 35})
    msp.add_circle((50, 30), radius=6.0, dxfattribs={"layer": "U_EQUIPOS_MT"})
    msp.add_circle((50, 20), radius=6.0, dxfattribs={"layer": "U_EQUIPOS_MT"})
    msp.add_text("TRANSFORMADOR SED 100 kVA (22.9 / 0.38-0.22 kV Dyn5)", dxfattribs={"layer": "U_TEXTOS", "height": 2.5}).set_placement((60, 25))

    doc.saveas(dxf_path)
    print(f"  [OK DXF] {dxf_path}")


# =============================================================================
# 6. GENERADOR DE LÁMINA D-01: ARMADOS DGE PS-1 Y PA-1 (22.9 kV)
# =============================================================================
def generar_lamina_d01_armados(pdf_path: str, png_path: str, dxf_path: str):
    """Genera la Lámina Oficial D-01: Detalles de Armados Normalizados DGE PS-1 y PA-1."""
    print("-> Generando Lámina D-01 (Armados DGE PS-1 y PA-1 22.9 kV)...")
    
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    dibujar_marco_a3(fig,
                     "PROYECTO DE INGENIERÍA DE DETALLE — LÍNEA PRIMARIA 22.9 kV CAPACHICA A CHIFRÓN",
                     "DETALLES CONSTRUCTIVOS DE ARMADOS NORMALIZADOS DGE PS-1 (SUSPENSIÓN) Y PA-1 (ÁNGULO)")

    # PANEL IZQUIERDO: ARMADO DGE PS-1 (ALINEAMIENTO / SUSPENSIÓN)
    ax_ps = fig.add_axes([0.035, 0.055, 0.450, 0.870])
    ax_ps.axis('off')
    rect_ps = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#1E3A8A', lw=1.2)
    ax_ps.add_patch(rect_ps)
    ax_ps.text(0.5, 0.965, "ARMADO NORMALIZADO DGE PS-1: SUSPENSIÓN 22.9 kV", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')
    ax_ps.text(0.5, 0.935, "Estructuras E-02, E-03, E-07 | Poste C.A.C. 12/300 daN (Escala 1:25)", ha='center', va='center', fontsize=5.5, color='#475569')
    ax_ps.plot([0.05, 0.95], [0.915, 0.915], color='#1E3A8A', lw=0.8)

    # Dibujo Técnico Frontal PS-1
    # Fuste de poste tronco-cónico
    fuste_ps = Polygon([(0.47, 0.08), (0.485, 0.85), (0.515, 0.85), (0.53, 0.08)], closed=True, facecolor='#E2E8F0', edgecolor='#0F172A', lw=1.2)
    ax_ps.add_patch(fuste_ps)
    ax_ps.plot([0.35, 0.65], [0.20, 0.20], color='#78350F', lw=1.2, linestyle='--')
    ax_ps.text(0.66, 0.20, "N.T.N. (Empotramiento t=1.40m)", fontsize=4.8, color='#78350F', va='center')

    # Cruceta de acero galvanizado L 75x75x6.4 mm x 1.50 m a 25 cm de la cima
    cruceta_ps = Rectangle((0.25, 0.78), 0.50, 0.022, facecolor='#FEF08A', edgecolor='#CA8A04', lw=1.0)
    ax_ps.add_patch(cruceta_ps)
    ax_ps.text(0.50, 0.791, "Cruceta F°G° L 75x75x6.4 mm x 1.50 m", ha='center', va='center', fontsize=4.3, fontweight='bold', color='#854D0E')

    # Aisladores tipo Pin ANSI 56-3 (Centro en cima y 2 en extremos)
    for xp in [0.28, 0.50, 0.72]:
        yp = 0.85 if xp == 0.50 else 0.802
        # Espiga F°G°
        ax_ps.plot([xp, xp], [yp - 0.02, yp], color='#475569', lw=1.8)
        # Campana aislador
        camp = Polygon([(xp - 0.025, yp), (xp + 0.025, yp), (xp + 0.015, yp + 0.04), (xp - 0.015, yp + 0.04)],
                       closed=True, facecolor='#DBEAFE', edgecolor='#1D4ED8', lw=0.9)
        ax_ps.add_patch(camp)
        # Conductor de fase AAAC 35 mm²
        ax_ps.plot([xp - 0.04, xp + 0.04], [yp + 0.04, yp + 0.04], color='#DC2626', lw=1.6)

    # Cuadro de Materiales PS-1
    ax_ps.text(0.08, 0.15, "LISTA DE MATERIALES NORMALIZADA (DGE PS-1):\n• 01 Poste C.A.C. 12 m / 300 daN (NTP 339.027)\n• 01 Cruceta angular F°G° L 75x75x6.4 mm x 1.50 m\n• 03 Aisladores tipo Pin de porcelana ANSI 56-3\n• 03 Espigas para cruceta y cima de F°G° 3/4\" x 12\"\n• 01 Perno maquinado de F°G° 5/8\" x 8\" con tuerca\n• 03 Ataduras preformadas para conductor AAAC 35 mm²",
               fontsize=4.8, color='#0F172A', bbox=dict(boxstyle='square,pad=0.2', fc='#F8FAFC', ec='#CBD5E1', lw=0.6))

    # PANEL CENTRAL-DERECHO: ARMADO DGE PA-1 (ÁNGULO)
    ax_pa = fig.add_axes([0.505, 0.320, 0.465, 0.605])
    ax_pa.axis('off')
    rect_pa = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#1E3A8A', lw=1.2)
    ax_pa.add_patch(rect_pa)
    ax_pa.text(0.5, 0.965, "ARMADO NORMALIZADO DGE PA-1: ÁNGULO 22.9 kV", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')
    ax_pa.text(0.5, 0.935, "Estructuras E-05, E-06, E-08 | Poste C.A.C. 12/400 daN + Retenida R-1", ha='center', va='center', fontsize=5.5, color='#475569')
    ax_pa.plot([0.05, 0.95], [0.915, 0.915], color='#1E3A8A', lw=0.8)

    # Fuste de poste PA-1
    fuste_pa = Polygon([(0.46, 0.08), (0.480, 0.85), (0.520, 0.85), (0.54, 0.08)], closed=True, facecolor='#E2E8F0', edgecolor='#0F172A', lw=1.2)
    ax_pa.add_patch(fuste_pa)

    # Cruceta de ángulo reforzada L 75x75x6.4 mm x 1.80 m
    cruceta_pa = Rectangle((0.20, 0.76), 0.60, 0.025, facecolor='#FEF08A', edgecolor='#CA8A04', lw=1.0)
    ax_pa.add_patch(cruceta_pa)

    # Cadenas poliméricas de suspensión 25 kV inclinadas por el ángulo
    for xp in [0.26, 0.50, 0.74]:
        yp = 0.76
        # Aislador polimérico (cuerpo + aletas)
        ax_pa.plot([xp, xp + 0.03], [yp, yp - 0.12], color='#0284C7', lw=2.2)
        for ka in range(5):
            ya = yp - 0.02 - ka * 0.02
            xa = xp + ka * 0.006
            ax_pa.plot([xa - 0.015, xa + 0.015], [ya, ya], color='#0284C7', lw=1.5)
        # Grapa de suspensión y conductor
        ax_pa.plot([xp + 0.03, xp + 0.03], [yp - 0.12, yp - 0.13], color='#0F172A', lw=2.0)
        ax_pa.plot([xp - 0.03, xp + 0.08], [yp - 0.13, yp - 0.13], color='#DC2626', lw=1.8)

    # Cable de Retenida R-1 a 45°
    ax_pa.plot([0.50, 0.10], [0.76, 0.36], color='#C2410C', lw=1.6, linestyle='--')
    ax_pa.text(0.24, 0.58, "Cable Retenida R-1 (SM 3/8\" a 45°)", fontsize=4.7, color='#C2410C', rotation=45)

    # Cuadro de Materiales PA-1
    ax_pa.text(0.08, 0.08, "LISTA DE MATERIALES NORMALIZADA (DGE PA-1):\n• 01 Poste C.A.C. 12 m / 400 daN (NTP 339.027)\n• 01 Cruceta angular reforzada F°G° L 75x75x6.4 mm x 1.80 m\n• 03 Cadenas aisladores poliméricos tipo suspensión 25 kV (HTV)\n• 03 Grapas de suspensión angular de aleación de aluminio\n• 01 Retenida mecánica simple R-1 (cable Siemens-Martin 3/8\")",
               fontsize=4.8, color='#0F172A', bbox=dict(boxstyle='square,pad=0.2', fc='#F8FAFC', ec='#CBD5E1', lw=0.6))

    # Rótulo Oficial de Ingeniería Lámina D-01
    dibujar_rotulo_oficial(fig.add_axes([0.505, 0.045, 0.465, 0.255]), 0, 0, 1, 1,
                           plano_cod="D-01",
                           plano_nom_l1="DETALLES DE ARMADOS NORMALIZADOS DGE",
                           plano_nom_l2="PS-1 (SUSPENSIÓN) Y PA-1 (ÁNGULO) 22.9 kV",
                           escala="1 : 25")

    fig.savefig(pdf_path, format='pdf', dpi=300)
    fig.savefig(png_path, format='png', dpi=300)
    plt.close(fig)
    print(f"  [OK PDF] {pdf_path}")
    print(f"  [OK PNG] {png_path}")

    # DXF ARMADOS D-01
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    doc.layers.add("D_ESTRUCTURA", color=colors.CYAN)
    doc.layers.add("D_CRUCETAS", color=colors.YELLOW)
    doc.layers.add("D_AISLADORES", color=colors.GREEN)
    doc.layers.add("D_CONDUCTOR", color=colors.RED)
    doc.layers.add("D_COTAS_TEXTOS", color=colors.WHITE)

    # Dibujar poste PS-1
    msp.add_lwpolyline([(-0.18, 0), (-0.09, 12.0), (0.09, 12.0), (0.18, 0), (-0.18, 0)], close=True, dxfattribs={"layer": "D_ESTRUCTURA"})
    msp.add_lwpolyline([(-0.75, 11.75), (0.75, 11.75), (0.75, 11.82), (-0.75, 11.82), (-0.75, 11.75)], close=True, dxfattribs={"layer": "D_CRUCETAS"})
    msp.add_text("ARMADO DGE PS-1 (SUSPENSION 22.9 kV)", dxfattribs={"layer": "D_COTAS_TEXTOS", "height": 0.4}).set_placement((-1.5, 12.5))

    doc.saveas(dxf_path)
    print(f"  [OK DXF] {dxf_path}")


# =============================================================================
# 7. GENERADOR DE LÁMINA D-02: ARMADOS DGE PR-1 Y SED BIPOSTE SAB-1 100 kVA
# =============================================================================
def generar_lamina_d02_sab1_pr1(pdf_path: str, png_path: str, dxf_path: str):
    """Genera la Lámina Oficial D-02: Detalles de Armado DGE PR-1 y SED Biposte SAB-1."""
    print("-> Generando Lámina D-02 (Armado PR-1 y SED Biposte SAB-1 100 kVA)...")
    
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    dibujar_marco_a3(fig,
                     "PROYECTO DE INGENIERÍA DE DETALLE — LÍNEA PRIMARIA 22.9 kV CAPACHICA A CHIFRÓN",
                     "DETALLES DE ARMADO DGE PR-1 (RETENCIÓN) Y SUBESTACIÓN AÉREA BIPOSTE SAB-1 100 kVA")

    # PANEL IZQUIERDO: DETALLE DE SUBESTACIÓN AÉREA BIPOSTE SAB-1 100 kVA
    ax_sab = fig.add_axes([0.035, 0.055, 0.485, 0.870])
    ax_sab.axis('off')
    rect_sab = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#1E3A8A', lw=1.2)
    ax_sab.add_patch(rect_sab)
    ax_sab.text(0.5, 0.965, "SUBESTACIÓN AÉREA BIPOSTE SAB-1 100 kVA (22.9 kV)", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')
    ax_sab.text(0.5, 0.935, "Estructura E-04 | 2x Postes C.A.C. 13/400 | Intereje = 2.00 m (Escala 1:30)", ha='center', va='center', fontsize=5.5, color='#475569')
    ax_sab.plot([0.05, 0.95], [0.915, 0.915], color='#1E3A8A', lw=0.8)

    # Dos Postes C.A.C. 13/400 (Intereje normalizado)
    fuste_izq = Polygon([(0.31, 0.08), (0.325, 0.85), (0.355, 0.85), (0.37, 0.08)], closed=True, facecolor='#E2E8F0', edgecolor='#0F172A', lw=1.2)
    fuste_der = Polygon([(0.63, 0.08), (0.645, 0.85), (0.675, 0.85), (0.69, 0.08)], closed=True, facecolor='#E2E8F0', edgecolor='#0F172A', lw=1.2)
    ax_sab.add_patch(fuste_izq)
    ax_sab.add_patch(fuste_der)

    # Nivel de Terreno Natural y Cimentaciones
    ax_sab.plot([0.15, 0.85], [0.20, 0.20], color='#78350F', lw=1.2, linestyle='--')
    ax_sab.text(0.86, 0.20, "N.T.N. (t=1.50m)", fontsize=4.8, color='#78350F', va='center')

    # Plataforma portatransformador a cota +6.00 m (nivel Y = 0.50)
    plat_vigas = Rectangle((0.26, 0.48), 0.48, 0.025, facecolor='#64748B', edgecolor='#0F172A', lw=1.1)
    ax_sab.add_patch(plat_vigas)
    ax_sab.text(0.50, 0.492, "Plataforma 2 UPN-120 x 2.60 m (F°G°)", ha='center', va='center', fontsize=4.3, fontweight='bold', color='#FFFFFF')

    # Transformador de distribución trifásico 100 kVA (Cuba con aletas)
    cuba_trafo = Rectangle((0.40, 0.505), 0.20, 0.15, facecolor='#FEF2F2', edgecolor='#DC2626', lw=1.3)
    ax_sab.add_patch(cuba_trafo)
    # Aletas radiadoras
    for xa in [0.41, 0.43, 0.45, 0.55, 0.57, 0.59]:
        ax_sab.plot([xa, xa], [0.52, 0.63], color='#DC2626', lw=0.9)
    ax_sab.text(0.50, 0.57, "TRAFO\n100 kVA\n22.9 kV", ha='center', va='center', fontsize=5.2, fontweight='bold', color='#991B1B')

    # Boquillas MT (3 aisladores sobre trafo)
    for xb in [0.44, 0.50, 0.56]:
        ax_sab.plot([xb, xb], [0.655, 0.695], color='#D97706', lw=2.2)

    # Cabecera de subestación: Cruceta con Cut-Outs y Pararrayos ZnO a cota +11.5 m (Y = 0.82)
    cruc_top = Rectangle((0.22, 0.82), 0.56, 0.022, facecolor='#FEF08A', edgecolor='#CA8A04', lw=1.0)
    ax_sab.add_patch(cruc_top)
    ax_sab.text(0.50, 0.831, "Cabecera: 03 Cut-Out 27 kV + 03 Pararrayos ZnO 21 kV", ha='center', va='center', fontsize=4.3, fontweight='bold', color='#854D0E')

    # Cuadro Materiales SAB-1
    ax_sab.text(0.08, 0.08, "LISTA DE MATERIALES NORMALIZADA (SED SAB-1 - ALCANCE MT):\n• 02 Postes C.A.C. 13 m / 400 daN (intereje 2.00 m)\n• 01 Transformador 100 kVA, 22.9/0.38-0.22 kV, Dyn5, ONAN\n• 01 Plataforma metálica F°G° 2 vigas UPN-120 x 2.60 m\n• 03 Cortacircuitos fusibles Cut-Out 27 kV / 100 A (150 kV BIL)\n• 03 Pararrayos poliméricos de óxido de zinc (ZnO) 21 kV\n• 01 Sistema PAT-3 para masa, pararrayos y neutro del transformador",
               fontsize=4.8, color='#0F172A', bbox=dict(boxstyle='square,pad=0.2', fc='#F8FAFC', ec='#CBD5E1', lw=0.6))

    # PANEL DERECHO: ARMADO DGE PR-1 (RETENCIÓN / DERIVACIÓN / TERMINAL)
    ax_pr = fig.add_axes([0.535, 0.320, 0.435, 0.605])
    ax_pr.axis('off')
    rect_pr = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#1E3A8A', lw=1.2)
    ax_pr.add_patch(rect_pr)
    ax_pr.text(0.5, 0.965, "ARMADO NORMALIZADO DGE PR-1: RETENCIÓN 22.9 kV", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1E3A8A')
    ax_pr.text(0.5, 0.935, "Estructuras E-01 (Derivación) y E-09 (Terminal) | Poste C.A.C. 12/400 daN", ha='center', va='center', fontsize=5.5, color='#475569')
    ax_pr.plot([0.05, 0.95], [0.915, 0.915], color='#1E3A8A', lw=0.8)

    # Poste y doble cruceta PR-1
    fuste_pr = Polygon([(0.46, 0.08), (0.480, 0.85), (0.520, 0.85), (0.54, 0.08)], closed=True, facecolor='#E2E8F0', edgecolor='#0F172A', lw=1.2)
    ax_pr.add_patch(fuste_pr)

    cruc_pr1 = Rectangle((0.18, 0.76), 0.64, 0.022, facecolor='#FEF08A', edgecolor='#CA8A04', lw=1.0)
    cruc_pr2 = Rectangle((0.18, 0.72), 0.64, 0.022, facecolor='#FEF08A', edgecolor='#CA8A04', lw=1.0)
    ax_pr.add_patch(cruc_pr1)
    ax_pr.add_patch(cruc_pr2)
    ax_pr.text(0.50, 0.741, "Doble Cruceta F°G° L 75x75x6.4 mm x 2.00 m", ha='center', va='center', fontsize=4.3, fontweight='bold', color='#854D0E')

    # Aisladores de retención y Cut-Outs de derivación
    for xp in [0.26, 0.50, 0.74]:
        # Aislador polimérico de retención horizontal
        ax_pr.plot([xp, xp + 0.12], [0.74, 0.74], color='#0284C7', lw=2.2)
        ax_pr.plot([xp + 0.12, xp + 0.18], [0.74, 0.74], color='#DC2626', lw=1.8)

    # Retenida terminal a 45°
    ax_pr.plot([0.50, 0.15], [0.74, 0.39], color='#C2410C', lw=1.6, linestyle='--')
    ax_pr.text(0.26, 0.58, "Retenida Simple R-1 (a 45°)", fontsize=4.8, color='#C2410C', rotation=45)

    # Cuadro Materiales PR-1
    ax_pr.text(0.08, 0.08, "LISTA DE MATERIALES NORMALIZADA (DGE PR-1):\n• 01 Poste C.A.C. 12 m / 400 daN (NTP 339.027)\n• 02 Crucetas angulares de F°G° L 75x75x6.4 mm x 2.00 m\n• 03 Aisladores poliméricos de retención 25 kV (HTV 6 aletas)\n• 03 Grapas de anclaje tipo pistola de aleación de aluminio\n• 03 Cortacircuitos fusibles Cut-Out 27 kV / 100 A (en E-01)\n• 03 Pararrayos poliméricos de óxido de zinc (ZnO) 21 kV (en E-01)",
               fontsize=4.8, color='#0F172A', bbox=dict(boxstyle='square,pad=0.2', fc='#F8FAFC', ec='#CBD5E1', lw=0.6))

    # Rótulo Oficial de Ingeniería Lámina D-02
    dibujar_rotulo_oficial(fig.add_axes([0.535, 0.045, 0.435, 0.255]), 0, 0, 1, 1,
                           plano_cod="D-02",
                           plano_nom_l1="DETALLES DE ARMADO NORMALIZADO DGE PR-1",
                           plano_nom_l2="Y SUBESTACIÓN AÉREA BIPOSTE SAB-1 100 kVA",
                           escala="1 : 30")

    fig.savefig(pdf_path, format='pdf', dpi=300)
    fig.savefig(png_path, format='png', dpi=300)
    plt.close(fig)
    print(f"  [OK PDF] {pdf_path}")
    print(f"  [OK PNG] {png_path}")

    # DXF D-02
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    doc.layers.add("D_ESTRUCTURA", color=colors.CYAN)
    doc.layers.add("D_EQUIPOS", color=colors.RED)
    doc.layers.add("D_TEXTOS", color=colors.WHITE)

    # Dibujar postes gemelos SAB-1
    msp.add_lwpolyline([(-1.18, 0), (-1.09, 13.0), (-0.91, 13.0), (-0.82, 0), (-1.18, 0)], close=True, dxfattribs={"layer": "D_ESTRUCTURA"})
    msp.add_lwpolyline([(0.82, 0), (0.91, 13.0), (1.09, 13.0), (1.18, 0), (0.82, 0)], close=True, dxfattribs={"layer": "D_ESTRUCTURA"})
    # Plataforma y transformador
    msp.add_line((-1.3, 6.0), (1.3, 6.0), dxfattribs={"layer": "D_ESTRUCTURA", "lineweight": 40})
    msp.add_lwpolyline([(-0.45, 6.1), (0.45, 6.1), (0.45, 7.3), (-0.45, 7.3), (-0.45, 6.1)], close=True, dxfattribs={"layer": "D_EQUIPOS"})
    msp.add_text("SUBESTACION AEREA BIPOSTE SAB-1 100 kVA", dxfattribs={"layer": "D_TEXTOS", "height": 0.4}).set_placement((-2.0, 13.5))

    doc.saveas(dxf_path)
    print(f"  [OK DXF] {dxf_path}")


# =============================================================================
# 8. GENERADOR DE LÁMINA D-03: CIMENTACIÓN SULZBERGER, RETENIDA Y PAT-3
# =============================================================================
def generar_lamina_d03_cimentacion_retenida_pat(pdf_path: str, png_path: str, dxf_path: str):
    """Genera la Lámina Oficial D-03: Cimentación Sulzberger, Retenidas R-1 y PAT-3."""
    print("-> Generando Lámina D-03 (Cimentación Sulzberger, Retenidas R-1 y PAT-3)...")
    
    fig = plt.figure(figsize=(16.54, 11.69), dpi=300)
    dibujar_marco_a3(fig,
                     "PROYECTO DE INGENIERÍA DE DETALLE — LÍNEA PRIMARIA 22.9 kV CAPACHICA A CHIFRÓN",
                     "DETALLES DE CIMENTACIONES (MÉTODO SULZBERGER), RETENIDAS R-1 Y PUESTA A TIERRA PAT-3")

    # PANEL 1: CIMENTACIÓN SULZBERGER PARA POSTES C.A.C. (X: 0.035 a 0.345)
    ax_cim = fig.add_axes([0.035, 0.055, 0.300, 0.870])
    ax_cim.axis('off')
    rect_cim = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#1E3A8A', lw=1.2)
    ax_cim.add_patch(rect_cim)
    ax_cim.text(0.5, 0.965, "CIMENTACIÓN SULZBERGER (POSTES C.A.C.)", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A')
    ax_cim.text(0.5, 0.935, "Concreto Ciclópeo f'c=140 kg/cm² + 30% PM (Escala 1:20)", ha='center', va='center', fontsize=5.0, color='#475569')
    ax_cim.plot([0.05, 0.95], [0.915, 0.915], color='#1E3A8A', lw=0.8)

    # Dibujo en corte de cimentación Sulzberger
    # Nivel de Terreno Natural
    ax_cim.plot([0.10, 0.90], [0.70, 0.70], color='#78350F', lw=1.5)
    ax_cim.text(0.50, 0.715, "Nivel de Terreno Natural (N.T.N.)", ha='center', fontsize=4.8, fontweight='bold', color='#78350F')

    # Cuello cónico de protección pluvial sobre NTN
    cuello = Polygon([(0.30, 0.70), (0.42, 0.75), (0.58, 0.75), (0.70, 0.70)], closed=True, facecolor='#CBD5E1', edgecolor='#0F172A', lw=1.0)
    ax_cim.add_patch(cuello)

    # Bloque de concreto ciclópeo bajo NTN (Excavación D=0.80m / 0.90m, Prof=1.40m / 1.50m)
    bloque_cim = Rectangle((0.28, 0.25), 0.44, 0.45, facecolor='#E2E8F0', edgecolor='#0F172A', lw=1.2)
    ax_cim.add_patch(bloque_cim)
    # Solera de fondo de concreto (e = 0.15 m)
    solera = Rectangle((0.28, 0.20), 0.44, 0.05, facecolor='#94A3B8', edgecolor='#0F172A', lw=1.1)
    ax_cim.add_patch(solera)
    ax_cim.text(0.50, 0.225, "Solera de Asiento (e = 0.15 m)", ha='center', va='center', fontsize=4.2, color='#FFFFFF')

    # Fuste de poste empotrado
    poste_emp = Polygon([(0.44, 0.25), (0.46, 0.88), (0.54, 0.88), (0.56, 0.25)], closed=True, facecolor='#F1F5F9', edgecolor='#1E3A8A', lw=1.2)
    ax_cim.add_patch(poste_emp)

    # Cotas de cimentación
    ax_cim.annotate('', xy=(0.20, 0.20), xytext=(0.20, 0.70), arrowprops=dict(arrowstyle='<->', color='#0F172A', lw=0.8))
    ax_cim.text(0.18, 0.45, "t = 1.40 m (12m)\nt = 1.50 m (13m)", ha='right', va='center', fontsize=4.7, color='#0F172A')

    ax_cim.annotate('', xy=(0.28, 0.16), xytext=(0.72, 0.16), arrowprops=dict(arrowstyle='<->', color='#0F172A', lw=0.8))
    ax_cim.text(0.50, 0.13, "D = 0.80 m (12m) / 0.90 m (13m)", ha='center', fontsize=4.7, color='#0F172A')

    # Notas Técnicas Sulzberger
    ax_cim.text(0.08, 0.03, "PARÁMETROS SULZBERGER:\n• Capacidad de carga suelo: C_t = 8.0 kg/cm³\n• Factor de seguridad al vuelco: FS >= 1.50\n• Concreto f'c = 140 kg/cm² + 30% P.M. 3\"-4\"",
                fontsize=4.6, color='#0F172A', bbox=dict(boxstyle='square,pad=0.2', fc='#F8FAFC', ec='#CBD5E1', lw=0.5))

    # PANEL 2: DETALLE RETENIDA MECÁNICA R-1 A TIERRA (X: 0.355 a 0.665)
    ax_ret = fig.add_axes([0.355, 0.055, 0.300, 0.870])
    ax_ret.axis('off')
    rect_ret = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#1E3A8A', lw=1.2)
    ax_ret.add_patch(rect_ret)
    ax_ret.text(0.5, 0.965, "RETENIDA MECÁNICA R-1 A TIERRA (45°)", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A')
    ax_ret.text(0.5, 0.935, "Cable Siemens-Martin 3/8\" + Bloque Concreto (Escala 1:25)", ha='center', va='center', fontsize=5.0, color='#475569')
    ax_ret.plot([0.05, 0.95], [0.915, 0.915], color='#1E3A8A', lw=0.8)

    # Nivel de terreno
    ax_ret.plot([0.10, 0.90], [0.65, 0.65], color='#78350F', lw=1.5)
    ax_ret.text(0.50, 0.665, "Nivel de Terreno Natural (N.T.N.)", ha='center', fontsize=4.8, fontweight='bold', color='#78350F')

    # Fuste de poste y tiro de retenida
    ax_ret.plot([0.20, 0.20], [0.65, 0.90], color='#0F172A', lw=3.0)
    ax_ret.text(0.20, 0.91, "Poste C.A.C.", ha='center', fontsize=4.8, color='#0F172A')

    # Cable de retenida a 45°
    ax_ret.plot([0.20, 0.65], [0.85, 0.40], color='#C2410C', lw=1.8)
    # Aislador tipo nuez ANSI 54-1 a 3.0 m de altura
    ax_ret.plot(0.35, 0.70, marker='s', color='#D97706', markersize=5)
    ax_ret.text(0.37, 0.72, "Aislador Nuez ANSI 54-1\n(H >= 3.00 m)", fontsize=4.4, color='#B45309')

    # Varilla de anclaje de F°G° 5/8" x 2.40 m y bloque de concreto
    ax_ret.plot([0.65, 0.80], [0.40, 0.25], color='#0F172A', lw=2.2)
    bloque_ancla = Rectangle((0.74, 0.20), 0.14, 0.08, facecolor='#64748B', edgecolor='#0F172A', lw=1.1)
    ax_ret.add_patch(bloque_ancla)
    ax_ret.text(0.81, 0.24, "Bloque Concreto\n0.40x0.40x0.20m", ha='center', va='center', fontsize=4.0, color='#FFFFFF')

    # Cono de arrancamiento de tierra a 30°
    cono_tierra = Polygon([(0.74, 0.24), (0.60, 0.65), (0.95, 0.65), (0.88, 0.24)], closed=True, facecolor='#FEF08A', edgecolor='#CA8A04', lw=0.8, linestyle=':', alpha=0.4)
    ax_ret.add_patch(cono_tierra)
    ax_ret.text(0.77, 0.55, "Cono de Resistencia\nal Arrancamiento (30°)", fontsize=4.3, color='#854D0E', ha='center')

    # Notas Técnicas Retenida
    ax_ret.text(0.08, 0.03, "PARÁMETROS RETENIDA R-1:\n• Cable Acero Galvanizado SM 3/8\" (Tr = 3,150 kgf)\n• Varilla anclaje F°G° 5/8\" x 2.40 m con guardacabo\n• Profundidad de enterramiento bloque: h = 1.80 m\n• Factor de seguridad al arrancamiento: FS >= 2.00",
                fontsize=4.6, color='#0F172A', bbox=dict(boxstyle='square,pad=0.2', fc='#F8FAFC', ec='#CBD5E1', lw=0.5))

    # PANEL 3: DETALLE SISTEMA DE PUESTA A TIERRA PAT-3 (X: 0.675 a 0.970)
    ax_pat = fig.add_axes([0.675, 0.320, 0.295, 0.605])
    ax_pat.axis('off')
    rect_pat = patches.Rectangle((0, 0), 1, 1, facecolor='#FFFFFF', edgecolor='#1E3A8A', lw=1.2)
    ax_pat.add_patch(rect_pat)
    ax_pat.text(0.5, 0.965, "SISTEMA PUESTA A TIERRA PAT-3", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#1E3A8A')
    ax_pat.text(0.5, 0.935, "03 Electrodos Cu 5/8\"x2.40m en Triángulo | R <= 10 Ω", ha='center', va='center', fontsize=4.8, color='#475569')
    ax_pat.plot([0.05, 0.95], [0.915, 0.915], color='#1E3A8A', lw=0.8)

    # Caja de registro de concreto
    caja = Rectangle((0.35, 0.72), 0.30, 0.12, facecolor='#F1F5F9', edgecolor='#0F172A', lw=1.1)
    ax_pat.add_patch(caja)
    ax_pat.text(0.50, 0.78, "Caja de Registro 0.40x0.40m\nCon tapa de concreto", ha='center', va='center', fontsize=4.3, color='#0F172A')

    # Electrodo de Cobre Puro 5/8" x 2.40 m
    ax_pat.plot([0.50, 0.50], [0.15, 0.72], color='#B45309', lw=3.0)
    ax_pat.text(0.53, 0.45, "Electrodo Cu puro\n5/8\" x 2.40 m", fontsize=4.8, fontweight='bold', color='#B45309', va='center')

    # Relleno de zanja tratada con bentonita sódica
    pozo_tierra = Rectangle((0.28, 0.12), 0.44, 0.60, facecolor='#DCFCE7', edgecolor='#16A34A', lw=0.8, linestyle='--', alpha=0.35)
    ax_pat.add_patch(pozo_tierra)
    ax_pat.text(0.50, 0.20, "Tierra vegetal cernida con bentonita", ha='center', fontsize=4.2, color='#15803D')

    # Conector Split-bolt / Soldadura Cadweld
    ax_pat.plot(0.50, 0.70, marker='o', color='#D97706', markersize=6)
    ax_pat.text(0.54, 0.70, "Conector Cadweld / Split-bolt", fontsize=4.3, color='#92400E', va='center')

    # Notas Técnicas PAT-3
    ax_pat.text(0.06, 0.04, "PARÁMETROS PUESTA A TIERRA PAT-3:\n• 03 Electrodos de cobre puro 5/8\" x 2.40 m en triángulo (S = 4.80 m)\n• Conductor enlace: Cable cobre desnudo 35 mm²\n• Resistividad de diseño Capachica: rho = 200.0 Ω·m\n• Resistencia equivalente calculada: R = 6.80 Ω <= 10.0 Ω",
                fontsize=4.5, color='#0F172A', bbox=dict(boxstyle='square,pad=0.2', fc='#F8FAFC', ec='#CBD5E1', lw=0.5))

    # Rótulo Oficial de Ingeniería Lámina D-03
    dibujar_rotulo_oficial(fig.add_axes([0.675, 0.045, 0.295, 0.255]), 0, 0, 1, 1,
                           plano_cod="D-03",
                           plano_nom_l1="DETALLES DE CIMENTACIÓN SULZBERGER,",
                           plano_nom_l2="RETENIDAS R-1 Y PUESTA A TIERRA PAT-3",
                           escala="1 : 20")

    fig.savefig(pdf_path, format='pdf', dpi=300)
    fig.savefig(png_path, format='png', dpi=300)
    plt.close(fig)
    print(f"  [OK PDF] {pdf_path}")
    print(f"  [OK PNG] {png_path}")

    # DXF D-03
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    doc.layers.add("D_CIMENTACION", color=colors.CYAN)
    doc.layers.add("D_RETENIDAS", color=colors.RED)
    doc.layers.add("D_TIERRA_PAT", color=colors.GREEN)
    doc.layers.add("D_TEXTOS", color=colors.WHITE)

    # Cimentación
    msp.add_lwpolyline([(-0.40, 0), (0.40, 0), (0.40, -1.40), (-0.40, -1.40), (-0.40, 0)], close=True, dxfattribs={"layer": "D_CIMENTACION"})
    msp.add_text("CIMENTACION SULZBERGER POSTE CAC 12M", dxfattribs={"layer": "D_TEXTOS", "height": 0.3}).set_placement((-1.5, 0.5))

    doc.saveas(dxf_path)
    print(f"  [OK DXF] {dxf_path}")


# =============================================================================
# 9. EJECUCIÓN PRINCIPAL Y COMPILACIÓN DE TODOS LOS ENTREGABLES
# =============================================================================
def generar_todos_los_planos():
    """Compila y genera las 6 láminas oficiales completas en PDF, PNG y DXF."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "entregables", "planos"))
    prev_dir = os.path.join(base_dir, "preview_png")
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(prev_dir, exist_ok=True)

    print("\n" + "="*80)
    print("COMPILADOR MAESTRO DE PLANOS EJECUTIVOS — LÍNEA PRIMARIA 22.9 kV")
    print("PROYECTO: CAPACHICA A CHIFRÓN (PUNO) | 9 ESTRUCTURAS | SAB-1 100 kVA")
    print("="*80)

    # 1. Lámina LP-01: Planta y Traza General
    pdf_lp01 = os.path.join(base_dir, "plano_LP01_planta_linea_primaria.pdf")
    png_lp01 = os.path.join(prev_dir, "plano_LP01_planta_linea_primaria.png")
    dxf_lp01 = os.path.join(base_dir, "PLANO_LP01_PLANTA_LINEA_PRIMARIA_22.9KV.dxf")
    generar_lamina_lp01_planta(pdf_lp01, png_lp01, dxf_lp01)

    # 2. Lámina PL-01: Perfil Longitudinal y Spotting
    pdf_pl01 = os.path.join(base_dir, "plano_PL01_perfil_longitudinal.pdf")
    png_pl01 = os.path.join(prev_dir, "plano_PL01_perfil_longitudinal.png")
    dxf_pl01 = os.path.join(base_dir, "PLANO_PL01_PERFIL_LONGITUDINAL_LP_CAPACHICA.dxf")
    generar_lamina_pl01_perfil(pdf_pl01, png_pl01, dxf_pl01)

    # 3. Lámina U-01: Diagrama Unifilar y Protecciones MT
    pdf_u01 = os.path.join(base_dir, "plano_U01_diagrama_unifilar_detalles.pdf")
    png_u01 = os.path.join(prev_dir, "plano_U01_diagrama_unifilar_detalles.png")
    dxf_u01 = os.path.join(base_dir, "PLANO_U01_DIAGRAMA_UNIFILAR_LP_SAB1.dxf")
    generar_lamina_u01_unifilar(pdf_u01, png_u01, dxf_u01)

    # 4. Lámina D-01: Armados DGE PS-1 y PA-1
    pdf_d01 = os.path.join(base_dir, "plano_D01_armados_dge_ps1_pa1.pdf")
    png_d01 = os.path.join(prev_dir, "plano_D01_armados_dge_ps1_pa1.png")
    dxf_d01 = os.path.join(base_dir, "PLANO_D01_ARMADOS_DGE_PS1_PA1.dxf")
    generar_lamina_d01_armados(pdf_d01, png_d01, dxf_d01)

    # 5. Lámina D-02: Armado DGE PR-1 y SED Biposte SAB-1
    pdf_d02 = os.path.join(base_dir, "plano_D02_armados_dge_pr1_sab1.pdf")
    png_d02 = os.path.join(prev_dir, "plano_D02_armados_dge_pr1_sab1.png")
    dxf_d02 = os.path.join(base_dir, "PLANO_D02_ARMADOS_DGE_PR1_SAB1.dxf")
    generar_lamina_d02_sab1_pr1(pdf_d02, png_d02, dxf_d02)

    # 6. Lámina D-03: Cimentaciones Sulzberger, Retenidas R-1 y PAT-3
    pdf_d03 = os.path.join(base_dir, "plano_D03_detalles_cimentacion_retenida_pat.pdf")
    png_d03 = os.path.join(prev_dir, "plano_D03_detalles_cimentacion_retenida_pat.png")
    dxf_d03 = os.path.join(base_dir, "PLANO_D03_DETALLES_CIMENTACION_RETENIDA_PAT.dxf")
    generar_lamina_d03_cimentacion_retenida_pat(pdf_d03, png_d03, dxf_d03)

    print("="*80)
    print(f"[EXITO] Paquete completo de 6 planos de Línea Primaria generado en:\n  {base_dir}\n")


if __name__ == "__main__":
    generar_todos_los_planos()
