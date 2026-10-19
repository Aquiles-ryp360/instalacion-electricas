import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const require=createRequire(path.resolve('loader.cjs'));
const {Workbook,SpreadsheetFile,FileBlob}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const P=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const ROOT=path.resolve(P,'../..');
const B=path.join(ROOT,'build',path.basename(P),'presentacion-final');
const modo=process.argv[2]||'inspeccionar';
if(modo==='inspeccionar'){
 const w=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(P,'revisiones/lp-r02/02-metrados/Metrados_trazables_LP_R02.xlsx')));
 console.log((await w.inspect({kind:'sheet',include:'id,name',maxChars:2000})).ndjson);
 const hoja=w.worksheets.getItemAt(0);
 const png=await w.render({sheetName:hoja.name,range:'A1:F12',scale:1.5,format:'png'});
 await fs.writeFile(path.join(B,'metrado-anterior.png'),new Uint8Array(await png.arrayBuffer()));
 console.log('Inspección previa y render completados');
}

const BLUE='#5B9BD5',NAVY='#254D73',RED='#B51E25',INK='#20252B',PALE='#EEF4FA';
const r=JSON.parse(await fs.readFile(path.join(P,'revisiones/lp-r02/03-calculos/resultados.json'),'utf8'));
const c=JSON.parse(await fs.readFile(path.join(P,'datos/lp-r02/parametros.json'),'utf8'));
const OUT=path.join(B,'Proyecto_Linea_Primaria');
function set(s,cell,value){s.getRange(cell).values=[[value]];}
function formula(s,cell,value){s.getRange(cell).formulas=[[value]];}
function hoja(w,name,title,widths,rows=140){
 const s=w.worksheets.getItem(name);s.showGridLines=false;
 const end=col(widths.length-1);s.getRange(`A1:${end}${rows}`).format.font={name:'Arial',size:11,color:INK};
 s.getRange(`A1:${end}${rows}`).format.rowHeight=21;
 widths.forEach((v,i)=>s.getRange(`${col(i)}1:${col(i)}${rows}`).format.columnWidth=v);
 set(s,'A2',title);s.getRange(`A2:${end}2`).format.font={name:'Arial',size:16,bold:true,color:NAVY};
 s.getRange(`A4:${end}4`).format.borders={bottom:{style:'thin',color:BLUE}};
 return s;
}
function col(n){let v='';for(n++;n;n=Math.floor((n-1)/26))v=String.fromCharCode(65+(n-1)%26)+v;return v;}
function header(s,row,labels){
 const area=s.getRange(`A${row}:${col(labels.length-1)}${row}`);area.values=[labels];
 area.format={fill:NAVY,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},verticalAlignment:'center',horizontalAlignment:'center',wrapText:true,rowHeight:36};
}
function total(s,row,end='E'){
 s.getRange(`A${row}:${end}${row}`).format.fill=PALE;
 s.getRange(`A${row}:${end}${row}`).format.font={bold:true,color:NAVY};
 s.getRange(`A${row}:${end}${row}`).format.borders={top:{style:'thin',color:BLUE},bottom:{style:'thin',color:BLUE}};
}
function input(s,range){s.getRange(range).format.font.color='#225DA8';s.getRange(range).format.fill='#F3F7FC';}
function cuerpo(s,range,format='#,##0.000'){s.getRange(range).setNumberFormat(format);s.getRange(range).format.horizontalAlignment='right';}
function core(w,full=false){
 const q=hoja(w,'Parametros','PARÁMETROS DE DISEÑO',[10,47,15,3,17,58],full?55:25);q.tabColor=BLUE;
 set(q,'F2','Limbani – Huancasayani · 2026');
 const ps=[
 ['n','Número de fases','ud',3,'Terna AAAC 50 mm²'],['lp','Longitud por puente y ramal','m',2,'Asignación geométrica académica por fase'],
 ['s','Reserva de conductor','%',.03,'Reserva adicional sobre tendido y puentes'],['RTS','Carga de rotura del conductor','N',14700,'Dato tipo AAAC del modelo de diseño'],
 ['fEDS','Fracción de tracción inicial','%',.15,'Estado EDS, 15 °C'],['m','Masa lineal','kg/km',135,'Dato tipo AAAC 6201-T81'],
 ['g','Aceleración de gravedad','m/s²',9.80665,'Constante de cálculo'],['W','Carga transversal de poste','daN',600,'Capacidad tipo para verificación de flexión'],
 ['kr','Relación rotura/trabajo','-',2,'Hipótesis resistente del estudio'],['phi','Factor de resistencia','-',.65,'Hipótesis resistente del estudio'],
 ['e','Punto de ensayo bajo cima','m',.15,'Brazo de ensayo del poste tipo'],['Tu','Rotura mínima de retenida','kN',60,'Especificación de retenida de la línea'],
 ['phiR','Factor resistente de retenida','-',.9,'Hipótesis resistente del estudio'],['theta','Ángulo vertical de retenida','°',45,'Geometría ideal del cálculo']];
 if(full)ps.push(
 ['Dab','Separación fase A–B','m',1.2,'Disposición horizontal'],['Dbc','Separación fase B–C','m',1.2,'Disposición horizontal'],['Dca','Separación fase C–A','m',2.4,'Disposición horizontal'],
 ['R20','Resistencia a 20 °C','Ω/km',.671,'Dato tipo del conductor'],['aR','Coeficiente de resistencia','1/°C',.0036,'Dato tipo AAAC'],['T','Temperatura de cálculo eléctrico','°C',75,'Estado térmico de cálculo'],
 ['d','Diámetro del conductor','m',.009,'Dato tipo AAAC 50'],['f','Frecuencia','Hz',60,'Sistema de estudio'],['Vn','Tensión nominal del caso','kV',10,'Caso de compatibilidad académico; placa no verificada'],
 ['t','Elevación efectiva de fuente','pu',1.05,'Condición equivalente de regulación'],['Vbt','Tensión nominal secundaria','V',380,'Relación de transformación de cálculo'],['Sn','Potencia de cada transformador','kVA',250,'Capacidad neta de estudio a altitud local'],
 ['uk','Impedancia de cortocircuito TX','pu',.06,'Dato tipo de transformación'],['Pcu','Pérdida de cobre nominal TX','kW',3.1,'Dato tipo de transformación'],['P0','Pérdida en vacío TX','kW',.45,'Dato tipo de transformación'],['Q0','Reactiva en vacío TX','kvar',2.5,'Dato tipo de transformación'],
 ['Paux','Consumo auxiliar de generación','kW',5,'Balance del sistema aislado'],['FP','Factor de potencia de carga','-',.9,'Caso equilibrado'],['Ra','Resistencia de generador','pu',.02,'Modelo de fuente débil'],['Xdpp','Reactancia subtransitoria','pu',.2,'Modelo de fuente débil'],['Xdp','Reactancia transitoria','pu',.3,'Modelo de fuente débil'],['Xd','Reactancia sostenida','pu',1.8,'Modelo de fuente débil'],
 ['Pg','Potencia nominal de referencia','kW',200,'Referencia académica; no potencia firme certificada'],['af','Año de diseño','año',2026,'Proyección demográfica'],['a0','Año de censo','año',2017,'INEI Directorio 2017, tomo 4, pp. 1713–1714'],['r','Crecimiento anual','%',.01,'Proyección geométrica adoptada'],['fs','Simultaneidad residencial','-',.8,'Hipótesis de carga'],['Napu','Luminarias públicas','ud',60,'Hipótesis de alumbrado'],['Papu','Potencia por luminaria','kW',.0541,'Hipótesis de alumbrado'],['dv','Límite de caída de estudio','%',.05,'Criterio de evaluación del caso']);
 for(let i=0;i<ps.length;i++){
  const row=i+5;set(q,`A${row}`,ps[i][0]);set(q,`B${row}`,ps[i][1]);set(q,`C${row}`,ps[i][2]);set(q,`E${row}`,ps[i][3]);set(q,`F${row}`,ps[i][4]);
 }
 input(q,`E5:E${4+ps.length}`);cuerpo(q,`E5:E${4+ps.length}`,'0.000');
 for(const row of [7,9,31,44,48])if(row<5+ps.length)cuerpo(q,`E${row}`,'0.0%');
 const p=hoja(w,'Postes','PLANILLA DE POSTES Y ARMADOS',[10,17,18,13,11,13,12,13,26,13,10,10,16]);
 header(p,6,['Poste','Este (m)','Norte (m)','Cota DEM (m)','Altura (m)','Empotr. (m)','Amarre (m)','Ángulo (°)','Función','Ramales','Postes (ud)','Armados (jgo)','Puentes (m)']);
 p.getRange('A7:I117').values=r.postes.map(x=>[x.id,x.e,x.n,x.cota_dem_m,x.poste_m,x.empotramiento_estudio_m,x.amarre_m,x.angulo_deg,x.tipo_r02]);
 const fp=r.postes.map((_,i)=>{let n=i+7;return [`=IF(I${n}="SUSPENSION",0,IF(I${n}="TERMINAL",1,2))`,'=1','=1',`=J${n}*'Parametros'!$E$5*'Parametros'!$E$6`];});p.getRange('J7:M117').formulas=fp;
 p.freezePanes.freezeRows(6);p.freezePanes.freezeColumns(1);cuerpo(p,'B7:H117','#,##0.00');cuerpo(p,'J7:L117','0');cuerpo(p,'M7:M117','0.00');input(p,'B7:I117');
 p.getRange('I7:I117').dataValidation={rule:{type:'list',values:['SUSPENSION','ANGULO','ANCLAJE','ANCLAJE_PROPUESTO','TERMINAL']}};
 const v=hoja(w,'Vanos','LONGITUD DE CONDUCTOR POR CATENARIA EDS',[9,10,10,14,14,14,14,16,14,14,14,14,17,17]);
 header(v,6,['Vano','Inicial','Final','L horiz. (m)','Δz amarre (m)','H EDS (N)','q (N/m)','a = H/q (m)','u (–)','x0 (m)','u0 (–)','u1 (–)','Cable/fase (m)','Terna (m)']);
 v.getRange('A7:C116').values=r.vanos.map(x=>[x.id,x.desde,x.hasta]);
 const find=(co,id)=>`INDEX('Postes'!$${co}$7:$${co}$117,MATCH(${id},'Postes'!$A$7:$A$117,0))`;
 const fv=r.vanos.map((_,i)=>{let n=i+7;return [
  `=SQRT((${find('B',`C${n}`)}-${find('B',`B${n}`)})^2+(${find('C',`C${n}`)}-${find('C',`B${n}`)})^2)`,
  `=${find('D',`C${n}`)}+${find('G',`C${n}`)}-${find('D',`B${n}`)}-${find('G',`B${n}`)}`,
  `='Parametros'!$E$8*'Parametros'!$E$9`,`='Parametros'!$E$10/1000*'Parametros'!$E$11`,`=F${n}/G${n}`,
  `=ASINH(E${n}/(2*H${n}*SINH(D${n}/(2*H${n}))))`,`=D${n}/2-H${n}*I${n}`,`=-J${n}/H${n}`,`=(D${n}-J${n})/H${n}`,
  `=H${n}*(SINH(L${n})-SINH(K${n}))`,`=M${n}*'Parametros'!$E$5`];});
 v.getRange('D7:N116').formulas=fv;cuerpo(v,'D7:N116','#,##0.000');v.freezePanes.freezeRows(6);v.freezePanes.freezeColumns(3);
 return {p,v,q};
}
function resumenMetrado(w){
 const s=hoja(w,'Resumen','METRADOS DE LA LÍNEA PRIMARIA',[9,46,10,49,18],35);s.tabColor=NAVY;
 set(s,'B3','Limbani – Huancasayani · Sistema aislado');header(s,6,['Ítem','Descripción','Unidad','Desarrollo','Cantidad']);
 const filas=[
 [7,'01.01','Poste CAC 13 m / 600 daN','ud','Conteo por altura',`=COUNTIFS('Postes'!$E$7:$E$117,13)`],
 [8,'01.02','Poste CAC 15 m / 600 daN','ud','Conteo por altura',`=COUNTIFS('Postes'!$E$7:$E$117,15)`],
 [9,'01.03','Poste CAC 17 m / 600 daN','ud','Conteo por altura',`=COUNTIFS('Postes'!$E$7:$E$117,17)`],
 [10,'','TOTAL DE POSTES','ud','72 + 30 + 9','=SUM(E7:E9)'],
 [12,'02.01','Armado de suspensión','jgo','Conteo por función',`=COUNTIFS('Postes'!$I$7:$I$117,"SUSPENSION")`],
 [13,'02.02','Armado de ángulo','jgo','Conteo por función',`=COUNTIFS('Postes'!$I$7:$I$117,"ANGULO")`],
 [14,'02.03','Armado de anclaje','jgo','Conteo por función',`=COUNTIFS('Postes'!$I$7:$I$117,"ANCLAJE")`],
 [15,'02.04','Retención adicional','jgo','Conteo por función',`=COUNTIFS('Postes'!$I$7:$I$117,"ANCLAJE_PROPUESTO")`],
 [16,'02.05','Armado terminal','jgo','Conteo por función',`=COUNTIFS('Postes'!$I$7:$I$117,"TERMINAL")`],
 [17,'','TOTAL DE ARMADOS','jgo','30 + 41 + 22 + 16 + 2','=SUM(E12:E16)'],
 [19,'03.01','Retenida y anclaje por ramal','ud','Suma de ramales retenidos',`=SUM('Postes'!$J$7:$J$117)`],
 [20,'03.02','Transformación de salida y llegada','ud','1 de salida + 1 de llegada','=1+1'],
 [22,'04.01','Longitud horizontal del eje','m','Suma de longitudes XY de los 110 vanos',`=SUM('Vanos'!$D$7:$D$116)`],
 [23,'04.02','Conductor por fase (EDS)','m','Suma de longitudes de catenaria',`=SUM('Vanos'!$M$7:$M$116)`],
 [24,'04.03','Terna tendida','m','3 × longitud por fase',`=E23*'Parametros'!$E$5`],
 [25,'04.04','Puentes y colas','m','3 fases × 160 ramales × 2 m',`=SUM('Postes'!$M$7:$M$117)`],
 [26,'04.05','Reserva adicional','m','Redondeo superior de 3% de tendido + puentes',`=ROUNDUP(SUM(E24:E25)*'Parametros'!$E$7,0)`],
 [27,'','CONDUCTOR PARA SUMINISTRO','m','Redondeo superior de tendido + puentes + reserva','=ROUNDUP(SUM(E24:E26),0)']];
 for(const [n,id,desc,u,des,f]of filas){s.getRange(`A${n}:D${n}`).values=[[id,desc,u,des]];formula(s,`E${n}`,f);}
 cuerpo(s,'E7:E27','#,##0.000');for(const row of [7,8,9,10,12,13,14,15,16,17,19,20,26,27])cuerpo(s,`E${row}`,'#,##0');
 for(const row of [10,17,27])total(s,row);
 set(s,'B30','Cantidades del corredor de gabinete EPSG:32719.');set(s,'B31','Catenaria EDS a 15 °C y tracción inicial 15% RTS.');
 return s;
}
function demanda(w){
 const s=hoja(w,'Demanda','CÁLCULO DE DEMANDA',[35,15,14,15,14,16,19],30);header(s,6,['Localidad','Viviendas 2017','Años','Usuarios 2026','kW/usuario','Simultaneidad','Demanda (kW)']);
 s.getRange('A7:B9').values=c.censo.localidades.map(x=>[x.nombre,x.viviendas_ocupadas]);
 s.getRange('E7:E9').values=c.censo.localidades.map(x=>[x.tipo==='I'?.6:.4]);
 for(let n=7;n<=9;n++){
  formula(s,`C${n}`,`='Parametros'!$E$42-'Parametros'!$E$43`);formula(s,`D${n}`,`=ROUNDUP(B${n}*(1+'Parametros'!$E$44)^C${n},0)`);
  formula(s,`F${n}`,`='Parametros'!$E$45`);formula(s,`G${n}`,`=D${n}*E${n}*F${n}`);
 }
 set(s,'A11','Demanda doméstica');formula(s,'G11','=SUM(G7:G9)');set(s,'A13','Alumbrado público');formula(s,'G13',`='Parametros'!$E$46*'Parametros'!$E$47`);
 c.demanda.servicios.forEach((x,i)=>{set(s,`A${15+i}`,x.nombre);set(s,`G${15+i}`,x.kw);});
 set(s,'A21','DEMANDA MÁXIMA');formula(s,'G21','=G11+G13+SUM(G15:G19)');total(s,21,'G');
 set(s,'A23','Factor de potencia');formula(s,'G23',`='Parametros'!$E$36`);set(s,'A24','Potencia reactiva (kvar)');formula(s,'G24','=G21*TAN(ACOS(G23))');
 set(s,'A25','Potencia aparente (kVA)');formula(s,'G25','=G21/G23');set(s,'A27','Usuarios potenciales');formula(s,'G27','=SUM(D7:D9)');
 cuerpo(s,'C7:D9','0');cuerpo(s,'E7:G27','0.000');input(s,'B7:B9');input(s,'E7:E9');input(s,'G15:G19');
}
function electrico(w){
 const s=hoja(w,'Electrico','PARÁMETROS ELÉCTRICOS Y RESULTADOS',[52,17,17,48],37);header(s,6,['Magnitud','Valor','Unidad','Expresión']);
 const rows=[
 [7,'Longitud eléctrica por fase',`=SUM('Vanos'!$M$7:$M$116)`,'m','Suma de longitudes EDS'],
 [8,'Distancia media geométrica',`=('Parametros'!E19*'Parametros'!E20*'Parametros'!E21)^(1/3)`,'m','DMG = (Dab × Dbc × Dca)^(1/3)'],
 [9,'Radio medio geométrico',`=0.7788*'Parametros'!E25/2`,'m','GMR = 0.7788 × d / 2'],
 [10,'Resistencia de fase',`='Parametros'!E22*(1+'Parametros'!E23*('Parametros'!E24-20))*B7/1000`,'Ω','R = R20 [1 + αR (T − 20)] L'],
 [11,'Reactancia de fase',`=2*PI()*'Parametros'!E26*0.0002*LN(B8/B9)*B7/1000`,'Ω','X = 2πf × 2·10^-4 ln(DMG/GMR) L'],
 [13,'Resistencia del transformador',`='Parametros'!E32/'Parametros'!E30`,'pu','rTX = Pcu / Sn'],
 [14,'Reactancia del transformador',`=SQRT('Parametros'!E31^2-B13^2)`,'pu','xTX = √(uk² − rTX²)'],
 [15,'Impedancia base MT',`=('Parametros'!E27*1000)^2/('Parametros'!E30*1000)`,'Ω','Zb = Vn² / Sn'],
 [16,'Resistencia TX referida a MT','=B13*B15','Ω','RTX = rTX × Zb'],[17,'Reactancia TX referida a MT','=B14*B15','Ω','XTX = xTX × Zb'],
 [18,'Tensión de fuente por fase',`='Parametros'!E27*1000*'Parametros'!E28/SQRT(3)`,'V','Vfuente = Vn × t / √3'],
 [21,'Tensión BT de llegada',`='Flujo'!N66`,'V','√3 |V3| × Vbt/Vn'],[22,'Corriente en la línea',`='Flujo'!O66`,'A','|I2|'],[23,'Pérdida activa de línea',`='Flujo'!P66`,'kW','3 |I2|² R'],
 [24,'Potencia activa de generación',`=3*B18*'Flujo'!H66/1000+'Parametros'!E35`,'kW','Potencia de fuente más auxiliares'],
 [25,'Potencia reactiva de generación',`=-3*B18*'Flujo'!I66/1000`,'kvar','−3 Vfuente Im(I1)'],[26,'Potencia aparente del generador','=SQRT(B24^2+B25^2)','kVA','√(Pg² + Qg²)'],
 [27,'Margen frente a 200 kW',`='Parametros'!E41-B24`,'kW','Pg nominal − Pg requerida'],
 [28,'Carga relativa del generador',`=B26/'Parametros'!E30`,'pu','Sg / Sn'],
 [30,'Tensión MT de salida',`=SQRT('Flujo'!B66^2+'Flujo'!C66^2)*SQRT(3)/1000`,'kV','√3 |V1|'],
 [31,'Tensión MT de llegada',`=SQRT('Flujo'!D66^2+'Flujo'!E66^2)*SQRT(3)/1000`,'kV','√3 |V2|'],[32,'Caída de la línea','=(B30-B31)/B30','pu','(V1 − V2) / V1'],
 [33,'Residuo de iteración de tensión',`='Flujo'!Q66`,'V','Diferencia máxima de dos iteraciones']];
 for(const[n,label,f,u,note]of rows){set(s,`A${n}`,label);formula(s,`B${n}`,f);set(s,`C${n}`,u);set(s,`D${n}`,note);}
 cuerpo(s,'B7:B33','#,##0.000');cuerpo(s,'B28','0.0%');cuerpo(s,'B32','0.000%');for(const row of [21,24,26])total(s,row,'D');
 const f=hoja(w,'Flujo','BALANCE RADIAL POR BARRIDO ITERATIVO',[9,16,16,16,16,16,16,15,15,15,15,15,15,15,14,15,17],70);
 header(f,6,['Iteración','Re V1 (V)','Im V1 (V)','Re V2 (V)','Im V2 (V)','Re V3 (V)','Im V3 (V)','Re I1 (A)','Im I1 (A)','Re I2 (A)','Im I2 (A)','Re I3 (A)','Im I3 (A)','BT final (V)','I línea (A)','P línea (kW)','ΔV iter. (V)']);
 for(let n=7;n<=66;n++){
  set(f,`A${n}`,n-7);
  const prev=n-1,V=`'Electrico'!$B$18`,Rt=`'Electrico'!$B$16`,Xt=`'Electrico'!$B$17`,R=`'Electrico'!$B$10`,X=`'Electrico'!$B$11`;
  let volt;
  if(n===7)volt=[`=${V}`,'=0',`=${V}`,'=0',`=${V}`,'=0'];
  else volt=[`=0.7*(${V}-${Rt}*H${prev}+${Xt}*I${prev})+0.3*B${prev}`,`=0.7*(-${Rt}*I${prev}-${Xt}*H${prev})+0.3*C${prev}`,
    `=0.7*(${V}-${Rt}*H${prev}+${Xt}*I${prev}-${R}*J${prev}+${X}*K${prev})+0.3*D${prev}`,`=0.7*(-${Rt}*I${prev}-${Xt}*H${prev}-${R}*K${prev}-${X}*J${prev})+0.3*E${prev}`,
    `=0.7*(${V}-${Rt}*H${prev}+${Xt}*I${prev}-${R}*J${prev}+${X}*K${prev}-${Rt}*L${prev}+${Xt}*M${prev})+0.3*F${prev}`,
    `=0.7*(-${Rt}*I${prev}-${Xt}*H${prev}-${R}*K${prev}-${X}*J${prev}-${Rt}*M${prev}-${Xt}*L${prev})+0.3*G${prev}`];
  f.getRange(`B${n}:G${n}`).formulas=[volt];
  f.getRange(`H${n}:Q${n}`).formulas=[[
    `=J${n}+('Parametros'!$E$33*1000*B${n}+'Parametros'!$E$34*1000*C${n})/(3*(B${n}^2+C${n}^2))`,
    `=K${n}+('Parametros'!$E$33*1000*C${n}-'Parametros'!$E$34*1000*B${n})/(3*(B${n}^2+C${n}^2))`,
    `=L${n}+('Parametros'!$E$33*1000*D${n}+'Parametros'!$E$34*1000*E${n})/(3*(D${n}^2+E${n}^2))`,
    `=M${n}+('Parametros'!$E$33*1000*E${n}-'Parametros'!$E$34*1000*D${n})/(3*(D${n}^2+E${n}^2))`,
    `=('Demanda'!$G$21*1000*F${n}+'Demanda'!$G$24*1000*G${n})/(3*(F${n}^2+G${n}^2))`,
    `=('Demanda'!$G$21*1000*G${n}-'Demanda'!$G$24*1000*F${n})/(3*(F${n}^2+G${n}^2))`,
    `=SQRT(F${n}^2+G${n}^2)*SQRT(3)*'Parametros'!$E$29/('Parametros'!$E$27*1000)`,
    `=SQRT(J${n}^2+K${n}^2)`,`=3*O${n}^2*'Electrico'!$B$10/1000`,
    n===7?'=0':`=MAX(ABS(B${n}-B${prev}),ABS(C${n}-C${prev}),ABS(D${n}-D${prev}),ABS(E${n}-E${prev}),ABS(F${n}-F${prev}),ABS(G${n}-G${prev}))`]];
 }
 cuerpo(f,'B7:Q66','0.000000');f.freezePanes.freezeRows(6);total(f,66,'Q');
}
function cortocircuito(w){
 const s=hoja(w,'Cortocircuito','CORTOCIRCUITO TRIFÁSICO SIMÉTRICO',[18,20,19,15,16,16,18,19],28);
 header(s,6,['Estado de fuente','Punto','Xd (pu)','Vbase (V)','Re Z (Ω)','Im Z (Ω)','|Z| (Ω)','Ik3 (A)']);
 const keys=[['Subtransitorio',38],['Transitorio',39],['Sostenido',40]];
 let n=7;
 for(const[name,key]of keys)for(const [point,nt,line]of [['MT salida',1,0],['MT llegada',1,1],['BT llegada',2,1]]){
  set(s,`A${n}`,name);set(s,`B${n}`,point);formula(s,`C${n}`,`='Parametros'!$E$${key}`);formula(s,`D${n}`,`='Parametros'!$E$27*1000`);
  formula(s,`E${n}`,`='Parametros'!$E$37*'Electrico'!$B$15+${nt}*'Electrico'!$B$16+${line}*'Electrico'!$B$10`);
  formula(s,`F${n}`,`=C${n}*'Electrico'!$B$15+${nt}*'Electrico'!$B$17+${line}*'Electrico'!$B$11`);formula(s,`G${n}`,`=SQRT(E${n}^2+F${n}^2)`);
  formula(s,`H${n}`,`=D${n}/SQRT(3)/G${n}${point==='BT llegada'?`*D${n}/'Parametros'!$E$29`:''}`);n++;
 }
 cuerpo(s,'C7:H15','0.000');set(s,'A19','Fuente: impedancias tipo del generador y transformadores.');set(s,'A21','No incluye decremento temporal ni selección de ajustes del relé.');
}
function mecanica(w){
 const s=hoja(w,'Mecanica','VERIFICACIÓN DE POSTES Y RETENIDAS',[10,12,14,17,18,18,17,14,16,16,18,16],124);
 header(s,6,['Poste','Altura (m)','Empotr. (m)','Momento aplicado (kN·m)','Momento tipo (kN·m)','D/C','Vertical mín. (kN)','Ramales','Tiro (kN)','Rotura adopt. (kN)','T admisible (kN)','Utilización retenida']);
 s.getRange('A7:A117').values=r.postes.map(x=>[x.id]);
 for(let i=0;i<111;i++){
  let n=i+7,p=r.postes[i];set(s,`D${n}`,p.retenidas_r02?p.M_con_ideales_kNm:p.M_sin_retenidas_kNm);set(s,`G${n}`,p.vertical_min_kN);set(s,`I${n}`,p.retenida_tiro_kN);
  formula(s,`B${n}`,`='Postes'!E${n}`);formula(s,`C${n}`,`='Postes'!F${n}`);
  formula(s,`E${n}`,`='Parametros'!$E$14*'Parametros'!$E$12*10*'Parametros'!$E$13*(B${n}-C${n}-'Parametros'!$E$15)/1000`);
  formula(s,`F${n}`,`=D${n}/E${n}`);formula(s,`H${n}`,`='Postes'!J${n}`);
  formula(s,`J${n}`,`=IF(H${n}=0,0,ROUNDUP(MAX('Parametros'!$E$16,I${n}/'Parametros'!$E$17)/10,0)*10)`);
  formula(s,`K${n}`,`=J${n}*'Parametros'!$E$17`);formula(s,`L${n}`,`=IF(H${n}=0,0,I${n}/K${n})`);
 }
 cuerpo(s,'B7:L117','0.000');s.freezePanes.freezeRows(6);
 set(s,'A120','Momentos y fuerzas: envolvente del modelo 3D por vano, seis estados y viento cada 15°.');
 const e=hoja(w,'Estados','CATENARIA: DESARROLLO POR VANO Y ESTADO',[10,18,13,14,15,15,15,14,14,15,14,15,14,14,16,16,16],672);
 header(e,6,['Vano','Estado','L (m)','Δz (m)','H resuelto (N)','qv (N/m)','qw (N/m)','q (N/m)','dy (m)','dx (m)','a (m)','x0 (m)','u0','u1','Cable (m)','T inicial (N)','T final (N)']);
 const all=r.vanos.flatMap(v=>Object.values(v.estados));e.getRange('A7:G666').values=all.map(x=>[x.vano,x.estado,x.L_m,x.dz_m,x.H_N,x.q_vertical_N_m,x.q_viento_N_m]);
 const fe=all.map((x,i)=>{let n=i+7;return [`=SQRT(F${n}^2+G${n}^2)`,`=D${n}*F${n}/H${n}`,`=SQRT(C${n}^2+D${n}^2-I${n}^2)`,`=E${n}/H${n}`,
  `=J${n}/2-K${n}*ASINH(I${n}/(2*K${n}*SINH(J${n}/(2*K${n}))))`,`=-L${n}/K${n}`,`=(J${n}-L${n})/K${n}`,`=K${n}*(SINH(N${n})-SINH(M${n}))`,`=E${n}*COSH(M${n})`,`=E${n}*COSH(N${n})`];});
 e.getRange('H7:Q666').formulas=fe;cuerpo(e,'C7:Q666','0.000000');e.freezePanes.freezeRows(6);
 set(e,'A669','H: solución termoelástica del motor. Longitud y esfuerzos de extremo se desarrollan con fórmulas de Excel.');
}
function resumenCalculo(w){
 const s=hoja(w,'Resumen','RESUMEN DE CÁLCULOS',[8,47,15,19,47],37);s.tabColor=NAVY;header(s,6,['Ítem','Resultado','Unidad','Valor','Desarrollo']);
 const rows=[
 [7,'01','Usuarios potenciales','ud',`='Demanda'!G27`,'Proyección geométrica por localidad'],[8,'02','Demanda máxima','kW',`='Demanda'!G21`,'Doméstica + alumbrado + servicios'],
 [9,'03','Potencia aparente de carga','kVA',`='Demanda'!G25`,'P / FP'],[11,'04','Longitud eléctrica por fase','m',`='Electrico'!B7`,'Catenaria EDS de 110 vanos'],
 [12,'05','Resistencia de fase','Ω',`='Electrico'!B10`,'Temperatura de cálculo 75 °C'],[13,'06','Reactancia de fase','Ω',`='Electrico'!B11`,'Disposición horizontal 1.2 / 1.2 / 2.4 m'],
 [15,'07','Corriente de la línea','A',`='Electrico'!B22`,'Barrido radial con ambos transformadores'],[16,'08','Tensión BT de llegada','V',`='Electrico'!B21`,'Generador + T1 + línea + T2'],
 [17,'09','Pérdida activa de la línea','kW',`='Electrico'!B23`,'3 I² R'],[18,'10','Generación requerida','kW',`='Electrico'!B24`,'Carga + pérdidas + auxiliares'],
 [19,'11','Potencia aparente del generador','kVA',`='Electrico'!B26`,'Potencias activa y reactiva de fuente'],
 [21,'12','Ik3 subtransitoria MT de llegada','A',`='Cortocircuito'!H8`,'Impedancias de fuente, T1 y línea'],
 [22,'13','Ik3 subtransitoria BT de llegada','A',`='Cortocircuito'!H9`,'Incluye T2 y relación MT/BT'],
 [24,'14','D/C máximo de flexión tipo','-',`=MAX('Mecanica'!F7:F117)`,'Momentos de la envolvente del modelo'],
 [25,'15','Apoyos con carga ascendente','ud',`=COUNTIFS('Mecanica'!G7:G117,"<0")`,'Vertical mínima negativa'],
 [26,'16','Rotura mínima de retenida','kN',`='Parametros'!E16`,'Especificación de suministro'],
 [28,'17','Margen de potencia nominal','kW',`='Electrico'!B27`,'Referencia de 200 kW menos necesidad'],
 [29,'18','Margen con 25 kW para Limbani','kW','=D28-25','Balance de oferta compartida']];
 for(const[n,id,desc,u,f,note]of rows){s.getRange(`A${n}:C${n}`).values=[[id,desc,u]];formula(s,`D${n}`,f);set(s,`E${n}`,note);}
 cuerpo(s,'D7:D29','#,##0.000');for(const n of [7,25])cuerpo(s,`D${n}`,'0');for(const n of [8,16,18,19,24])total(s,n);
 set(s,'B32','Caso: 10 kV, fuente equivalente 1.05 pu.');set(s,'B33','Geometría de gabinete y datos tipo de equipos.');
}
function presupuesto(w){
 const s=hoja(w,'Presupuesto','PRESUPUESTO REFERENCIAL ACADÉMICO',[8,52,12,18,21,22],40);s.tabColor=NAVY;
 header(s,6,['Partida','Descripción','Unidad','Cantidad','Precio unitario (S/)','Parcial (S/)']);
 const items=[
 ['01.01','Conductor AAAC 50 mm²','m',`='Resumen'!E27`,5.8],['01.02','Poste CAC 13 m instalado','ud',`='Resumen'!E7`,3800],
 ['01.03','Poste CAC 15 m instalado','ud',`='Resumen'!E8`,Math.round(3800*15/13*100)/100],['01.04','Poste CAC 17 m instalado','ud',`='Resumen'!E9`,Math.round(3800*17/13*100)/100],
 ['02.01','Armado de suspensión','jgo',`='Resumen'!E12`,1200],['02.02','Armado de ángulo','jgo',`='Resumen'!E13`,1800],
 ['02.03','Armado de anclaje y retención adicional','jgo',`=SUM('Resumen'!E14:E15)`,2800],['02.04','Armado terminal','jgo',`='Resumen'!E16`,2800],
 ['03.01','Retenida y anclaje por ramal','ud',`='Resumen'!E19`,2600],['03.02','Puesta a tierra de apoyo','ud',`='Resumen'!E10`,1200],
 ['04.01','Transformador 250 kVA netos en sitio','ud',`='Resumen'!E20`,105000],['04.02','Celda de protección y maniobra','ud','=2',55000],
 ['04.03','Conjunto neutro artificial / NGR','jgo','=1',60000],['04.04','Malla de tierra de subestación','ud','=2',25000]];
 items.forEach((x,i)=>{let n=i+7;s.getRange(`A${n}:C${n}`).values=[[x[0],x[1],x[2]]];formula(s,`D${n}`,x[3]);set(s,`E${n}`,x[4]);formula(s,`F${n}`,`=ROUND(D${n}*E${n},2)`);});
 for(const[n,label,f]of [[22,'COSTO DIRECTO','=SUM(F7:F20)'],[24,'Logística y transporte','=ROUND(F22*E24,2)'],[25,'Ingeniería y supervisión','=ROUND(F22*E25,2)'],[26,'Contingencia académica','=ROUND(SUM(F22,F24:F25)*E26,2)'],[28,'TOTAL REFERENCIAL','=SUM(F22,F24:F26)']]){set(s,`B${n}`,label);formula(s,`F${n}`,f);}
 set(s,'E24',.12);set(s,'E25',.08);set(s,'E26',.20);cuerpo(s,'D7:D20','#,##0.000');cuerpo(s,'E7:F28','#,##0.00');cuerpo(s,'E24:E26','0.0%');input(s,'E7:E20');input(s,'E24:E26');total(s,22,'F');total(s,28,'F');
 set(s,'B31','Moneda: PEN. Precios estimados de octubre de 2026.');set(s,'B32','No son cotizaciones. Total sin IGV desagregado.');set(s,'B33','Poste instalado: incluye montaje y cimentación tipo.');set(s,'B34','Precios 15/17 m: escalamiento por longitud respecto a 13 m.');
}
async function exportar(w,name,folder,views){
 w.recalculate();
 console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:8},summary:name,maxChars:2000})).ndjson);
 await fs.mkdir(path.join(OUT,folder),{recursive:true});
 for(const[sn,range]of views){const png=await w.render({sheetName:sn,range,scale:1.3,format:'png'});await fs.writeFile(path.join(B,`${name}-${sn}.png`),new Uint8Array(await png.arrayBuffer()));}
 const x=await SpreadsheetFile.exportXlsx(w);await x.save(path.join(OUT,folder,name+'.xlsx'));
 console.log('Exportado',name,flush());
}
function flush(){return '';}
async function construir(){
 await fs.mkdir(OUT,{recursive:true});
 const libro=names=>{const w=Workbook.create();names.forEach(n=>w.worksheets.add(n));return w;};
 const m=libro(['Resumen','Postes','Vanos','Parametros']);
 resumenMetrado(m);core(m);await exportar(m,'Metrados','02_Metrados',[['Resumen','A1:E31'],['Postes','A1:M15'],['Vanos','A1:N15'],['Parametros','A1:F19']]);
 const k=libro(['Resumen','Demanda','Electrico','Flujo','Cortocircuito','Mecanica','Estados','Postes','Vanos','Parametros']);resumenCalculo(k);core(k,true);demanda(k);electrico(k);cortocircuito(k);mecanica(k);
 await exportar(k,'Calculos','01_Calculos',[['Resumen','A1:E33'],['Demanda','A1:G27'],['Electrico','A1:D33'],['Flujo','A1:Q13'],['Cortocircuito','A1:H21'],['Mecanica','A1:L15'],['Estados','A1:Q15'],['Parametros','A19:F49']]);
 const p=libro(['Presupuesto','Resumen','Postes','Vanos','Parametros']);presupuesto(p);resumenMetrado(p);core(p);await exportar(p,'Presupuesto','05_Presupuesto',[['Presupuesto','A1:F34']]);
}
if(modo==='construir')await construir();
if(modo==='presupuesto'){
 const w=Workbook.create();['Presupuesto','Resumen','Postes','Vanos','Parametros'].forEach(x=>w.worksheets.add(x));
 presupuesto(w);resumenMetrado(w);core(w);await exportar(w,'Presupuesto','05_Presupuesto',[['Presupuesto','A1:F34']]);
}
