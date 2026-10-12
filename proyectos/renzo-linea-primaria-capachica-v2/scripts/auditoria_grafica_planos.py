# -*- coding: utf-8 -*-
"""
auditoria_grafica_planos.py
Analiza el PDF P-01 y U-01 con PyMuPDF para detectar superposiciones de texto.
"""
import fitz

def auditar_pdf(pdf_path):
    print(f"\n==========================================")
    print(f"AUDITORIA: {pdf_path}")
    print(f"==========================================")
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    rect = page.rect
    print(f"Dimensiones de pagina (pt): ancho={rect.width:.1f}, alto={rect.height:.1f} (A3: 1190.9 x 841.7 pt)")
    
    words = page.get_text("words")
    print(f"Total palabras detectadas: {len(words)}")
    
    # Revisar colisiones entre palabras
    solapes = []
    for i in range(len(words)):
        w1 = words[i]
        for j in range(i + 1, len(words)):
            w2 = words[j]
            # Si estan en bloques diferentes pero sus rectangulos colisionan
            if w1[5] != w2[5]:
                dx = max(0, min(w1[2], w2[2]) - max(w1[0], w2[0]))
                dy = max(0, min(w1[3], w2[3]) - max(w1[1], w2[1]))
                if dx > 0.5 and dy > 0.5:
                    solapes.append((w1[4], w2[4], (w1[0], w1[1], w1[2], w1[3]), (w2[0], w2[1], w2[2], w2[3])))
    
    print(f"Solapes detectados entre bloques de texto: {len(solapes)}")
    for s in solapes[:20]:
        print(f"  Colision: '{s[0]}' con '{s[1]}' en pos ({s[2][0]:.1f}, {s[2][1]:.1f})")

auditar_pdf("proyectos/renzo-linea-primaria-capachica-v2/entregables/planos/plano_P01_redes_planta.pdf")
auditar_pdf("proyectos/renzo-linea-primaria-capachica-v2/entregables/planos/plano_PL01_perfil_longitudinal.pdf")
auditar_pdf("proyectos/renzo-linea-primaria-capachica-v2/entregables/planos/plano_U01_diagrama_unifilar_detalles.pdf")
