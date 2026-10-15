"""Hojas de contacto de PDFs para inspección completa, nunca sustituyen el documento."""
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];R=P.parents[1];B=R/'build'/P.name/'lp-r01/investigacion'
def main():
    for prefix in ['expediente-pagina','calculos-pagina','planos-pagina']:
        files=sorted(B.glob(prefix+'-*.png'))
        for i in range(0,len(files),4):
            canvas=Image.new('RGB',(1700,2480),'#e8e8e8');draw=ImageDraw.Draw(canvas)
            for k,f in enumerate(files[i:i+4]):
                im=Image.open(f);im.thumbnail((810,1180));x=25+(k%2)*850;y=40+(k//2)*1240
                canvas.paste(im,(x,y));draw.text((x,y-20),f.name,fill='black')
            canvas.save(B/f'contacto-{prefix}-{i//4+1:02}.jpg',quality=94)
if __name__=='__main__':main()
