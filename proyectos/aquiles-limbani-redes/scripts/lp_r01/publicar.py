"""Copia entregables revisables; conserva las rutas históricas y prepara fuente activa."""
from pathlib import Path
import json,shutil,yaml
P=Path(__file__).resolve().parents[2];R=P.parents[1];O=R/'output/linea-primaria-limbani-huancasayani';T=P/'entregables/linea-primaria-r01'
def main():
    T.mkdir(parents=True,exist_ok=True)
    for suffix in ['expediente','calculos','planos']:
        f=R/f'output/pdf/Linea_Primaria_Limbani_Huancasayani_R01_{suffix}.pdf'
        if f.exists():shutil.copy2(f,T/f.name)
    for name in ['cad','qgis','tablas']:
        f=O/name
        if f.exists():shutil.copytree(f,T/name,dirs_exist_ok=True)
    config=dict(schema_version=2,id='aquiles-limbani-redes',revision='LP-R01',
                proyecto='Proyecto académico de línea primaria Limbani–Huancasayani',curso='Instalaciones Eléctricas II',
                autor='Aquiles Taylor Ramos Yapo',denominacion='Estudiante',codigo_estudiante='227368',docente=None,
                estado='Diseño académico revisable; verificaciones de campo y placas pendientes',modo='Aislado, sin SEIN',
                alcance='MCH y transformación de salida - línea primaria - SE llegada Huancasayani; excluye redes de usuarios',
                fuente_unica='datos/lp-r01/parametros.json',resultados='datos/lp-r01/resultados.json',
                documentos='expediente/lp-r01',entregables='entregables/linea-primaria-r01',
                antecedente_historico='fuentes/local/lp-r01/antecedente; archivos previos de entregables conservados')
    (P/'proyecto.yaml').write_text(yaml.safe_dump(config,allow_unicode=True,sort_keys=False),encoding='utf-8')
    (P/'datos/parametros_diseno.json').write_text(json.dumps(dict(revision='LP-R01',archivo_activo='lp-r01/parametros.json',
       aviso='El modelo urbano anterior se conserva en fuentes/local/lp-r01/antecedente/parametros_diseno.json. No usarlo para esta línea primaria.'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (P/'expediente/LEER_PRIMERO.md').write_text('# Expediente activo\n\nLa versión LP-R01 está en [lp-r01](lp-r01). Los archivos TeX anteriores describen el proyecto urbano histórico y no deben compilarse como entrega de la línea Limbani–Huancasayani. Se conservan como originales y referencia.\n',encoding='utf-8')
    print('Entrega copiada a',T)
if __name__=='__main__':main()
