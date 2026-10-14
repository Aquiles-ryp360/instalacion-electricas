"""Recupera evidencia pública sin modificar originales existentes."""
from pathlib import Path
import requests,json,hashlib,time

P=Path(__file__).resolve().parents[2];ROOT=P.parents[1]
S=P/'fuentes/local/lp-r01';B=ROOT/'build'/P.name/'lp-r01/investigacion'

def main():
    S.mkdir(parents=True,exist_ok=True);B.mkdir(parents=True,exist_ok=True)
    target=S/'osm_corredor.json'
    query='[out:json][timeout:100];(way["highway"](-14.215,-69.735,-14.125,-69.665);way["waterway"](-14.215,-69.735,-14.125,-69.665);node["place"](-14.215,-69.735,-14.125,-69.665););out body;>;out skel qt;'
    if not target.exists():
        errors=[]
        for endpoint in ['https://overpass-api.de/api/interpreter','https://overpass.private.coffee/api/interpreter']:
            try:
                response=requests.get(endpoint,params={'data':query},timeout=150,
                    headers={'User-Agent':'LimbaniAcademicDesign/1.0'})
                response.raise_for_status();data=response.json()
                if not data.get('elements'):raise ValueError('Respuesta sin elementos')
                target.write_bytes(response.content)
                (S/'osm_consulta.json').write_text(json.dumps(dict(endpoint=endpoint,consulta=query,fecha='2026-10-14',licencia='OpenStreetMap contributors, ODbL',estado='Cartografia colaborativa, no levantamiento'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                break
            except Exception as error:errors.append(str(error))
        else:raise RuntimeError(errors)
    data=json.loads(target.read_text(encoding='utf-8'))
    print('OSM:',len(data['elements']),'elementos; SHA256',hashlib.sha256(target.read_bytes()).hexdigest())
    print('Localidades:',[(v['id'],v.get('tags')) for v in data['elements'] if v.get('tags',{}).get('place')])

if __name__=='__main__':main()
