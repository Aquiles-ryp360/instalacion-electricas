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
    config=dict(schema_version=2,id='aquiles-linea-primaria-inst-ii',revision='LP-R01',
                proyecto='Proyecto académico de línea primaria Limbani–Huancasayani',curso='Instalaciones Eléctricas II',
                autor='Aquiles Taylor Ramos Yapo',denominacion='Estudiante',codigo_estudiante='227368',docente=None,
                estado='Diseño académico revisable; verificaciones de campo y placas pendientes',modo='Aislado, sin SEIN',
                alcance='MCH y transformación de salida - línea primaria - SE llegada Huancasayani; excluye redes de usuarios',
                fuente_unica='datos/lp-r01/parametros.json',resultados='datos/lp-r01/resultados.json',
                documentos='expediente/lp-r01',entregables='entregables/linea-primaria-r01',
                cad_dwg_activo='entregables/linea-primaria-r01/cad/LP_Limbani_Huancasayani_R01_Armados_Perfiles.dwg',
                google_earth='entregables/linea-primaria-r01/google-earth/LP_Limbani_Huancasayani_R01.kmz',
                biblioteca_normativa='../../herramientas/biblioteca_dge/README.md',
                antecedente_historico='archivo/red-urbana',
                originales_locales='fuentes/local/lp-r01/antecedente')
    (P/'proyecto.yaml').write_text(yaml.safe_dump(config,allow_unicode=True,sort_keys=False),encoding='utf-8')
    (P/'datos/parametros_diseno.json').write_text(json.dumps(dict(revision='LP-R01',archivo_activo='lp-r01/parametros.json',
       aviso='El modelo urbano anterior se conserva en fuentes/local/lp-r01/antecedente/parametros_diseno.json. No usarlo para esta línea primaria.'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (P/'expediente/README.md').write_text('# Memoria editable · Instalaciones Eléctricas II\n\nLos capítulos activos están en [lp-r01/](lp-r01/); [memoria-completa.md](lp-r01/memoria-completa.md) permite revisar el texto conjunto. Su generación utiliza los parámetros y resultados de `datos/lp-r01/`.\n\nLos [PDF y archivos gráficos](../entregables/linea-primaria-r01/) corresponden al transporte Limbani–Huancasayani. Los capítulos antiguos de distribución urbana se conservan en [archivo/red-urbana/](../archivo/red-urbana/README.md).\n',encoding='utf-8')
    print('Entrega copiada a',T)
if __name__=='__main__':main()
