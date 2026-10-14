"""Hojas de contacto para inspeccionar todas las páginas ya renderizadas."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

P=Path(__file__).resolve().parents[1]
p=P.parents[1]/'build'/P.name/'r03/qa'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for name,cols,rows,w,h in [('memoria',4,3,420,545),('planos',2,2,920,660),('exposicion',2,2,850,495)]:
    files=sorted((p/name).glob('pagina-*.png'))
    for start in range(0,len(files),cols*rows):
        canvas=Image.new('RGB',(cols*w,rows*(h+30)),'#dddddd');draw=ImageDraw.Draw(canvas)
        for j,file in enumerate(files[start:start+cols*rows]):
            pic=Image.open(file).convert('RGB');pic.thumbnail((w-12,h-12))
            x=(j%cols)*w+(w-pic.width)//2;y=(j//cols)*(h+30)+28
            canvas.paste(pic,(x,y))
            draw.text(((j%cols)*w+10,(j//cols)*(h+30)+3),name+' '+file.stem,font=font,fill='black')
        path=p/(name+'-contacto-'+str(start//(cols*rows)+1)+'.jpg')
        canvas.save(path,quality=92)
        print(path)
