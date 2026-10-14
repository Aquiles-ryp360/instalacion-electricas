"""Archiva el recorte OSM efectivamente usado; no inventa caminos ni consultas exitosas."""
from pathlib import Path
import requests,json,hashlib,shutil,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[2];S=P/'fuentes/local/lp-r01';D=P/'datos/lp-r01'
def main():
    url='https://api.openstreetmap.org/api/0.6/map?bbox=-69.735,-14.215,-69.665,-14.125'
    S.mkdir(parents=True,exist_ok=True);file=S/'osm_bbox.xml'
    if not file.exists():
        if (D/file.name).exists():shutil.copy2(D/file.name,file)
        else:
            r=requests.get(url,timeout=60);r.raise_for_status();ET.fromstring(r.content);file.write_bytes(r.content)
    doc=ET.parse(file);shutil.copy2(file,D/file.name)
    meta=dict(url=url,fecha_snapshot='2026-10-14',sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
       datum='WGS84 EPSG:4326, convertido a EPSG:32719',nodos=len(doc.findall('node')),vias=len(doc.findall('way')),
       licencia='© OpenStreetMap contributors, ODbL 1.0',licencia_url='https://www.openstreetmap.org/copyright',
       estado='Cartografía colaborativa, no levantamiento; incluye coordenada de localidad, no predio SE')
    (D/'osm_consulta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('OSM archivado:',meta['nodos'],'nodos;',meta['vias'],'vías; SHA',meta['sha256'])
if __name__=='__main__':main()
