/** Apresentação reproduzível: dados reais, gráficos nativos e notas de fala.
 * RUNTIME_NODE_MODULES e RUNTIME_PYTHON apontam para o runtime de documentos.
 * SKILL_DIR aponta para a skill presentations instalada. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { aplicarAberturaRegional, aplicarMapaCidade } from './abertura_regional.mjs';
import { aplicarSlideBase } from './slide_base.mjs';
import { aplicarEstiloResultados } from './estilo_resultados.mjs';
const root = path.resolve(import.meta.dirname, '..');
const modules = process.env.RUNTIME_NODE_MODULES;
const skill = process.env.SKILL_DIR;
if (!modules || !skill || !process.env.RUNTIME_PYTHON) throw new Error('Defina RUNTIME_NODE_MODULES, SKILL_DIR e RUNTIME_PYTHON.');
const { Presentation, PresentationFile, FileBlob } = await import(pathToFileURL(path.join(modules, '@oai/artifact-tool/dist/artifact_tool.mjs')));
const { PDFDocument } = await import(pathToFileURL(path.join(modules, 'pdf-lib/cjs/index.js')).href);
const { default: JSZip } = await import(pathToFileURL(path.join(modules,'jszip/lib/index.js')).href);
const { resolvePresentationFont, applyPresentationChartFont, finalizePresentation } = await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const font = resolvePresentationFont({fontFamily:'Arial'});
const tmp = path.join(root,'tmp/slides');
await fs.mkdir(tmp,{recursive:true});
await fs.mkdir(path.join(root,'docs'),{recursive:true});
await fs.mkdir(path.join(root,'output/pdf'),{recursive:true});
await fs.mkdir(path.join(root,'.codex-finalizer'),{recursive:true});
const read = async p => JSON.parse(await fs.readFile(path.join(root,p),'utf8'));
const csv = async p => { const lines=(await fs.readFile(path.join(root,p),'utf8')).trim().split(/\r?\n/); const keys=lines.shift().split(','); return lines.map(l=>Object.fromEntries(l.split(',').map((v,i)=>[keys[i],v!==''&&!isNaN(Number(v))?Number(v):v]))); };
const summary=await read('output/resumo.json');
const raw=await csv('data/processed/ilha_solteira_mensal.csv');
const test=await csv('output/tables/previsoes_teste.csv');
const future=await csv('output/tables/previsoes_2017.csv');
const metrics=summary.metricas_teste;
const f=(x,d=0)=>Number(x).toLocaleString('pt-BR',{maximumFractionDigits:d,minimumFractionDigits:d});
const months=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
const C={navy:'#102E3A',teal:'#007F80',gold:'#C48730',paper:'#F6F3EB',ink:'#18343E',muted:'#5B7177',grid:'#D7DDD8',light:'#F8FAF7',grey:'#8B9A9D'};
const referencePath=process.env.SLIDES_SOURCE ? path.resolve(root,process.env.SLIDES_SOURCE) : null;
const pres=referencePath ? await PresentationFile.importPptx(await FileBlob.load(referencePath)) : Presentation.create({slideSize:{width:1280,height:720}});
const notes=[];
const owners=[];
function text(s,str,x,y,w,h,size=28,color=C.ink,bold=false){const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});sh.text=str;sh.text.style={typeface:font,fontSize:size,color,bold,autoFit:'none'};return sh;}
function slide(title,note,dark=false){note=note.replace(/Tempo: (\d+) segundos/,(_,v)=>`Tempo: ${Math.round(Number(v)*0.85/5)*5} segundos`);const s=pres.slides.add();s.background.fill=dark?C.navy:C.paper;const num=pres.slides.items.length; text(s,title,64,44,1148,100,44,dark?C.light:C.ink,true);text(s,`${String(num).padStart(2,'0')}  Ilha Solteira`,64,672,600,24,16,dark?'#A5C8CB':C.muted);s.speakerNotes.textFrame.setText(note);notes.push({num,title,note});return s;}
function caption(s,str){text(s,str,70,610,1130,53,21,C.muted);}
function chart(s,categories,series,{kind='line',height=425,top=166,legend=true,ymax,labels=false}={}){owners.push(pres.slides.items.length);const ch=s.charts.add(kind,{position:{left:70,top,width:1130,height},categories,series:series.map(r=>({...r,valuesFormatCode:'0',values:r.values.map(v=>Number(v.toFixed(4)))})),hasLegend:legend,legend:{position:'bottom',overlay:false,textStyle:{typeface:font,fontSize:20,fill:C.ink}},lineOptions:{smooth:false},barOptions:{direction:'column',grouping:'clustered',gapWidth:65},chartFill:C.paper,plotAreaFill:C.paper,xAxis:{textStyle:{typeface:font,fontSize:17,fill:C.ink},majorGridlines:null,line:{fill:C.grid,width:1}},yAxis:{min:0,...(ymax?{max:ymax}:{}),numberFormatCode:'0',textStyle:{typeface:font,fontSize:18,fill:C.ink},majorGridlines:{fill:C.grid,width:1}},dataLabels:{showValue:labels,position:'outEnd',textStyle:{typeface:font,fontSize:20,fill:C.ink}}});applyPresentationChartFont(ch,{fontFamily:font});return ch;}
const line=(name,values,color,width=3)=>({name,values,fill:color,line:{fill:color,width},marker:{symbol:'none'}});
const source='Fonte: data/processed/ilha_solteira_mensal.csv, extraído de ILHA_SOLTEIRA.pdf.';
if (!referencePath) {
let s=slide('Vazões de Ilha Solteira','Tempo: 45 segundos. Apresente o objetivo: comparar ARIMA e SARIMA e quantificar a incerteza. A base termina em dezembro de 2016. Todas as projeções para 2017 são históricas. '+source,true);
text(s,'ARIMA e SARIMA',65,217,1100,100,72,C.light,true);
text(s,'Previsões mensais com intervalos de 95%',70,340,1050,70,35,'#A5C8CB');
text(s,'1931–2016',70,510,650,75,48,'#D9AC69');
s=slide('O problema de previsão','Tempo: 50 segundos. Queremos antecipar vazões mensais usando apenas o passado e apresentar uma faixa de valores plausíveis. Os intervalos são preditivos, pois se referem a novas observações. Um intervalo de confiança de coeficiente responde a outra pergunta. Os exemplos fornecidos orientam a exploração, diferenciação e modelagem, com APIs atuais. Fontes: EXEMPLO.pdf, EXEMPLO_01.pdf e statsmodels SARIMAXResults.get_forecast.');
text(s,'Quanto podemos prever\nusando o passado?',70,190,1050,150,51,C.teal,true);
text(s,'Comparação temporal entre modelos\nAvaliação do erro em meses reservados\nIncerteza para cada vazão futura',73,400,1090,165,30);
s=slide('86 anos de observações mensais','Tempo: 60 segundos. Explique a passagem da tabela anual com 12 colunas para uma série longa, com uma data por linha. A base tem 1032 valores positivos e completos. A unidade não está explicitada no PDF. Evite afirmar m³/s como unidade confirmada. O documento também não identifica se são vazões naturais, afluentes ou defluentes. '+source);
text(s,'1.032',70,175,530,120,90,C.teal,true);
text(s,'meses de janeiro de 1931\na dezembro de 2016',76,320,650,100,31);
text(s,'12 observações por ano\nSem meses ausentes\nValores positivos',760,200,460,190,28);
text(s,'Unidade e tipo de vazão não informados no PDF',75,505,1110,90,30,C.gold,true);
s=slide('A série combina sazonalidade e extremos','Tempo: 65 segundos. Mostre que o ciclo anual convive com picos e períodos de valores menores. O gráfico preserva todos os 1032 meses, sem agregação. A escala vertical mantém a unidade original da tabela, que não está especificada no PDF. O máximo e o mínimo são apenas descrições, sem atribuir causas. '+source);
chart(s,raw.map(r=>r.data.slice(0,7)),[line('Vazão mensal',raw.map(r=>r.vazao),C.teal,1.6)],{legend:false});
caption(s,`Mínimo: ${f(summary.minimo)} em out/2014. Máximo: ${f(summary.maximo)} em fev/1983. Unidade da tabela.`);
const cycle=months.map((_,m)=>{const a=raw.filter(r=>Number(r.data.slice(5,7))===m+1);return a.reduce((a,r)=>a+r.vazao,0)/a.length;});
s=slide('O ciclo anual orienta o período sazonal','Tempo: 65 segundos. Cada coluna é a média de todas as observações daquele mês, calculada apenas para descrição da base completa. Fevereiro tem a maior média e setembro a menor. A repetição anual de dados mensais justifica período sazonal 12. Este gráfico não participa da seleção de parâmetros, que usa treino e validação. '+source);
chart(s,months,[{name:'Média mensal histórica',values:cycle,fill:C.teal}],{kind:'bar',legend:false});caption(s,'Média por mês em 1931–2016. Período sazonal: 12 meses. Unidade da tabela.');
s=slide('A avaliação respeita a ordem do tempo','Tempo: 90 segundos. No treino inicial, estimamos candidatos até 2008. Na validação, usamos cinco origens anuais e prevemos os próximos 12 meses de 2009 a 2013, expandindo o histórico. Depois fixamos um modelo de cada família. O teste usa uma única origem em dezembro de 2013 e 36 meses à frente. Assim nenhum valor de 2014–2016 escolhe parâmetros. O horizonte de teste é maior que o de validação. Fonte: src/modelos.py, selecionar e avaliar_e_prever.');
text(s,'1931–2008',73,185,475,66,44,C.teal,true);text(s,'Treino inicial e triagem por AIC',555,195,650,63,29);
text(s,'2009–2013',73,300,475,66,44,C.teal,true);text(s,'5 origens anuais de validação\n12 meses previstos em cada origem',555,300,650,100,29);
text(s,'2014–2016',73,440,475,66,44,C.gold,true);text(s,'Teste final de 36 meses\nOrigem única: dezembro de 2013',555,440,650,100,29);
s=slide('ARIMA e SARIMA','Tempo: 85 segundos. AR representa dependência de valores passados, I representa diferenças e MA representa erros passados. SARIMA acrescenta dependência sazonal. p e q controlam ordens não sazonais, d as diferenças. P, D e Q são os equivalentes sazonais. O 12 corresponde ao ciclo anual. A constante aparece nos dois modelos selecionados. Fonte: statsmodels.tsa.statespace.sarimax.SARIMAX e src/modelos.py.');
text(s,'ARIMA (p, d, q)',75,180,1100,75,48,C.teal,true);text(s,'Dependência mensal e erros passados',78,273,1100,65,32);
text(s,'SARIMA (p, d, q) × (P, D, Q)₁₂',75,396,1120,80,44,C.gold,true);text(s,'Acrescenta a dependência entre anos',78,490,1110,65,32);
s=slide('Logaritmo, diferenças e estacionariedade','Tempo: 90 segundos. Ajustamos log da vazão porque todos os valores são positivos. Isso reduz assimetria e permite intervalos positivos após exponenciar. Subtraímos a média do log calculada apenas no histórico de cada ajuste para melhorar a estabilidade numérica, e somamos esse centro antes de voltar à escala original. Diferença de ordem 1 compara meses consecutivos. Diferença sazonal compara o mês ao mesmo mês do ano anterior. No treino, ADF rejeita raiz unitária, mas KPSS rejeita estacionariedade em nível e log. Esse desacordo exige cautela. Comparamos d igual a zero ou um no ARIMA. No SARIMA, fixamos d=0 e comparamos D igual a zero ou um. A validação escolheu zero nas diferenças dos dois modelos. Fonte: output/tables/estacionariedade.csv e src/modelos.py.');
text(s,'zₜ = log(vazãoₜ)',75,178,1100,70,48,C.teal,true);
text(s,'Diferença mensal: zₜ − zₜ₋₁\nDiferença anual: zₜ − zₜ₋₁₂',78,282,1090,123,35);
text(s,'ADF e KPSS discordam nos níveis\nA seleção compara modelos com e sem diferenças',78,463,1100,120,31,C.gold,true);
const selected=summary.selecionados;
s=slide('Seleção dentro de cada família','Tempo: 75 segundos. AIC faz uma triagem dentro de grupos com a mesma família e as mesmas diferenças d e D. Os dois melhores convergentes de cada grupo seguem para validação. O RMSE médio das cinco origens escolhe um por família. O SARIMA ganha na validação, mas ainda precisa enfrentar o teste reservado. Fonte: output/tables/busca_modelos.csv e ranking_validacao.csv.');
text(s,`ARIMA (${selected.ARIMA.order.join(', ')})`,75,183,1100,76,44,C.teal,true);text(s,`RMSE na validação: ${f(summary.ranking_validacao.find(r=>r.id===selected.ARIMA.id).RMSE)}`,80,280,1090,60,30);
text(s,`SARIMA (${selected.SARIMA.order.join(', ')}) × (${selected.SARIMA.seasonal_order.slice(0,3).join(', ')})₁₂`,75,402,1120,76,42,C.gold,true);text(s,`RMSE na validação: ${f(summary.ranking_validacao.find(r=>r.id===selected.SARIMA.id).RMSE)}`,80,500,1090,60,30);
s=slide('O ingênuo sazonal tem o menor erro no teste','Tempo: 80 segundos. Menor RMSE é melhor, e a medida penaliza erros grandes. O ingênuo sazonal repete os últimos 12 meses disponíveis, de 2013, para os três anos do teste. A média por mês usa todo o histórico até 2013. Ambos superam os modelos nesta janela. Isso impede concluir que maior complexidade produziu melhor previsão. Fonte: output/tables/metricas_teste.csv.');
const sorted=[...metrics].sort((a,b)=>a.RMSE-b.RMSE);chart(s,sorted.map(m=>m.modelo),[{name:'RMSE',values:sorted.map(m=>Math.round(m.RMSE)),fill:C.teal}],{kind:'bar',legend:false,labels:true});caption(s,'2014–2016, origem dez/2013. RMSE na unidade da tabela. Menor é melhor.');
s=slide('As previsões centrais superestimam parte do teste','Tempo: 80 segundos. A linha escura mostra os 36 valores observados. Compare a oscilação sazonal do SARIMA à trajetória do ARIMA. Durante parte do teste, os valores previstos ficam acima dos observados. A média do teste é menor que a média do período de ajuste. Isso é uma descrição, não uma prova de mudança estrutural ou causa climática. Fonte: output/tables/previsoes_teste.csv e output/resumo.json.');
const cats=test.map(r=>`${months[Number(r.data.slice(5,7))-1]}/${r.data.slice(2,4)}`);
chart(s,cats,[line('Observado',test.map(r=>r.observado),C.ink),line('ARIMA',test.map(r=>r.ARIMA_media),C.teal),line('SARIMA',test.map(r=>r.SARIMA_media),C.gold)]);caption(s,`Média até 2013: ${f(summary.media_ate_2013)}. Média no teste: ${f(summary.media_2014_2016)}. Unidade da tabela.`);
s=slide('Intervalos preditivos de 95%: ARIMA','Tempo: 70 segundos. Os limites representam quantis condicionais do modelo para cada mês, e não garantem cobertura de toda a trajetória. A linha central é a média com correção de viés ao voltar do log: exp(mu + variância/2). A mediana seria exp(mu). Os limites vêm de exp dos limites no log. A largura na escala original depende também do nível previsto. Fonte: output/tables/previsoes_teste.csv. Fórmulas: src/modelos.py, prever.');
chart(s,cats,[line('Observado',test.map(r=>r.observado),C.ink),line('Média ARIMA',test.map(r=>r.ARIMA_media),C.teal),line('Limite inferior 95%',test.map(r=>r.ARIMA_inferior_95),C.grey,1.5),line('Limite superior 95%',test.map(r=>r.ARIMA_superior_95),C.gold,1.5)]);caption(s,'Intervalos pontuais condicionais ao modelo. Limites desenhados como linhas. Unidade da tabela.');
s=slide('Intervalos preditivos de 95%: SARIMA','Tempo: 70 segundos. A sazonalidade também altera os limites do SARIMA. Compare a faixa nos meses de valores altos. Uma faixa larga pode cobrir observações mesmo com previsão central ruim. Por isso lemos cobertura junto com a largura e o erro. Fonte: output/tables/previsoes_teste.csv.');
chart(s,cats,[line('Observado',test.map(r=>r.observado),C.ink),line('Média SARIMA',test.map(r=>r.SARIMA_media),C.teal),line('Limite inferior 95%',test.map(r=>r.SARIMA_inferior_95),C.grey,1.5),line('Limite superior 95%',test.map(r=>r.SARIMA_superior_95),C.gold,1.5)]);caption(s,'A cobertura deve ser interpretada junto com a largura dos intervalos. Unidade da tabela.');
s=slide('A cobertura observada fica abaixo de 95%',`Tempo: 75 segundos. O ARIMA cobriu ${f(metrics[0].cobertura_95,1)}% dos meses e o SARIMA cobriu ${f(metrics[1].cobertura_95,1)}%. O nominal é 95%, mas 36 observações são poucas e dependentes. Não afirmamos calibração apenas por esse número. A largura média foi maior no ARIMA. Não há intervalo calculado para as baselines neste projeto. Fonte: output/tables/metricas_teste.csv.`);
text(s,`${f(metrics[0].cobertura_95,1)}%`,73,175,510,125,80,C.teal,true);text(s,`${f(metrics[1].cobertura_95,1)}%`,700,175,510,125,80,C.gold,true);
text(s,`ARIMA: ${Math.round(metrics[0].cobertura_95*36/100)} de 36 meses`,80,317,550,60,31);text(s,`SARIMA: ${Math.round(metrics[1].cobertura_95*36/100)} de 36 meses`,705,317,510,60,31);
text(s,`Largura média ARIMA: ${f(metrics[0].largura_media_95)}\nLargura média SARIMA: ${f(metrics[1].largura_media_95)}`,80,440,1100,125,33);
caption(s,'Cobertura nominal: 95%. A amostra de teste tem somente 36 meses.');
s=slide('Os resíduos ainda contêm dependência','Tempo: 80 segundos. Ljung–Box verifica se resta autocorrelação conjunta. Os p-valores abaixo de 0,05 em 12 e 24 defasagens rejeitam a hipótese de ausência dessa dependência nos dois modelos. Jarque–Bera também rejeita normalidade nos dois. Esses resultados limitam a confiança nos intervalos paramétricos. Não escondemos os diagnósticos desfavoráveis. Fonte: output/tables/diagnosticos.csv.');
text(s,'Ljung–Box: p < 0,05',75,181,1100,77,48,C.gold,true);text(s,'Nos dois modelos, em 12 e 24 defasagens',80,284,1100,65,30);
text(s,'Jarque–Bera: p < 0,05',75,405,1100,75,44,C.teal,true);text(s,'Normalidade rejeitada nos dois modelos',80,500,1100,65,30);
s=slide('Projeção histórica para 2017','Tempo: 90 segundos. Depois de medir o desempenho, reajustamos as estruturas selecionadas usando todos os dados até dezembro de 2016. O gráfico mostra SARIMA com seus limites e a média ARIMA para comparação. Os valores observados de 2017 não estão no arquivo. Portanto, esta é uma projeção histórica sem avaliação externa e nunca deve ser apresentada como previsão atual. Fonte: output/tables/previsoes_2017.csv.');
chart(s,months,[line('Média ARIMA',future.map(r=>r.ARIMA_media),C.ink),line('Média SARIMA',future.map(r=>r.SARIMA_media),C.teal),line('SARIMA inferior 95%',future.map(r=>r.SARIMA_inferior_95),C.grey,1.5),line('SARIMA superior 95%',future.map(r=>r.SARIMA_superior_95),C.gold,1.5)]);caption(s,'Origem: dez/2016. Sem observações de 2017 para conferir. Unidade da tabela.');
s=slide('O que os resultados permitem concluir','Tempo: 80 segundos. Resuma com transparência. Há sazonalidade anual, mas isso não garante que o SARIMA escolhido seja o melhor em qualquer período. A validação favoreceu SARIMA e o teste favoreceu o ingênuo sazonal. Os resíduos mostram inadequação dos modelos e os intervalos são largos. Melhorias futuras incluem validação com horizontes comparáveis e modelos com covariáveis, desde que dados adicionais existam. Fontes: métricas, diagnósticos e ranking em output/tables.',true);
text(s,'Sazonalidade anual evidente',74,182,1110,65,39,'#A5C8CB',true);text(s,'O modelo simples vence no teste',74,287,1110,65,39,C.light,true);text(s,'Resíduos limitam a confiança nas faixas',74,392,1110,85,37,'#D9AC69',true);text(s,'Resultado científico: comparar e reconhecer os limites',77,541,1100,75,28,C.light);
s=slide('Código, exemplos e referências','Tempo: 45 segundos. Apresente o notebook como caminho para reproduzir cada etapa. A estrutura seguiu os dois PDFs de exemplos e a API oficial do statsmodels. Os três tutoriais fornecidos são referências indicadas. O conteúdo integral de DigitalOcean e GeeksforGeeks estava indisponível na consulta. Foram corrigidos o período sazonal, a separação temporal, a distinção de intervalos e chamadas antigas. URLs: https://www.digitalocean.com/community/tutorials/a-guide-to-time-series-forecasting-with-arima-in-python-3 ; https://www.geeksforgeeks.org/python-arima-model-for-time-series-forecasting/amp/ ; https://github.com/aarshayj/analytics_vidhya/blob/master/Articles/Time_Series_Analysis/Time_Series_AirPassenger.ipynb ; https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html ; https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAXResults.get_forecast.html . Fonte de dados: ILHA_SOLTEIRA.pdf.');
text(s,'Base: ILHA_SOLTEIRA.pdf\nOrientação: EXEMPLO.pdf e EXEMPLO_01.pdf',76,180,1120,130,32);
text(s,'Tutoriais: DigitalOcean, GeeksforGeeks e Analytics Vidhya\nImplementação atual: documentação statsmodels',76,371,1120,120,27);
text(s,'Notebook e tabelas permitem reproduzir os resultados',76,550,1120,65,29,C.teal,true);
}
if (pres.slides.items.length===18) await aplicarAberturaRegional(pres,{root,font,raw});
else if (![13,16,17].includes(pres.slides.items.length)) throw new Error('Quantidade de slides não reconhecida.');
await aplicarSlideBase(pres,{font,summary});
await aplicarMapaCidade(pres,{root,font});
await aplicarEstiloResultados(pres,{font,summary});
notes.length=0;
owners.length=0;
for (const [i,s] of pres.slides.items.entries()) {
  const title=s.shapes.items.find(sh=>(sh.frame ?? sh.position).top===44 && String(sh.text).trim());
  notes.push({num:i+1,title:String(title.text),note:String(s.speakerNotes.text)});
  if (s.charts.items.length) owners.push(i+1);
}
const slideCount=pres.slides.items.length;
const duration=notes.reduce((a,n)=>a+Number(n.note.match(/Tempo: (\d+)/)[1]),0);
await fs.writeFile(path.join(tmp,'notas_slides.md'),`# Notas internas da apresentação\n\n${slideCount} slides. Tempo sugerido de fala: ${Math.floor(duration/60)} minutos e ${duration%60} segundos.\n\n`+notes.map(n=>`## ${n.num}. ${n.title}\n\n${n.note}\n`).join('\n'));
const candidate=path.join(tmp,'candidate.pptx');
await (await PresentationFile.exportPptx(pres)).save(candidate);
// Espaçamento nativo de rótulos preserva todas as datas na planilha editável.
const zip=await JSZip.loadAsync(await fs.readFile(candidate));
if (referencePath) {
  // A importação mantém os valores, mas não transporta as planilhas anexas.
  // Recuperamos os arquivos originais por correspondência exata dos dados.
  const original=await JSZip.loadAsync(await fs.readFile(referencePath));
  const chartNames=z=>Object.keys(z.files).filter(n=>/^ppt\/(slides\/)?charts\/chart\d+\.xml$/.test(n));
  const dataKey=xml=>JSON.stringify([...xml.matchAll(/<c:ser>([\s\S]*?)<\/c:ser>/g)].map(m=>[...m[1].matchAll(/<c:v>([\s\S]*?)<\/c:v>/g)].map(v=>v[1])));
  const originals=await Promise.all(chartNames(original).map(async name=>({name,xml:await original.file(name).async('string')})));
  for (const name of chartNames(zip)) {
    let xml=await zip.file(name).async('string');
    if (!xml.includes('<c:f>')) continue;
    const matches=originals.filter(item=>dataKey(item.xml)===dataKey(xml));
    if (matches.length!==1) throw new Error(`Não foi possível identificar a planilha original de ${name}.`);
    const sourceChart=matches[0];
    const relPath=n=>path.posix.join(path.posix.dirname(n),'_rels',path.posix.basename(n)+'.rels');
    let relations=await original.file(relPath(sourceChart.name)).async('string');
    const target=relations.match(/Target="([^"]+\.xlsx)"/)?.[1];
    if (!target) throw new Error(`Planilha original ausente em ${sourceChart.name}.`);
    const sourceWorkbook=path.posix.normalize(path.posix.join(path.posix.dirname(sourceChart.name),target));
    const preservedWorkbook='ppt/embeddings/source-'+path.posix.basename(sourceWorkbook);
    zip.file(preservedWorkbook,await original.file(sourceWorkbook).async('nodebuffer'));
    relations=relations.replace(target,path.posix.relative(path.posix.dirname(name),preservedWorkbook));
    zip.file(relPath(name),relations);
    const externalData=sourceChart.xml.match(/<c:externalData[\s\S]*?<\/c:externalData>/)?.[0];
    if (!externalData) throw new Error(`Referência à planilha ausente em ${sourceChart.name}.`);
    const namespacedData=externalData.includes('xmlns:r=') ? externalData : externalData.replace('<c:externalData','<c:externalData xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"');
    xml=xml.replace('</c:chartSpace>',namespacedData+'</c:chartSpace>');
    zip.file(name,xml);
  }
  let contentTypes=await zip.file('[Content_Types].xml').async('string');
  if (!contentTypes.includes('Extension="xlsx"')) contentTypes=contentTypes.replace('</Types>','<Default Extension="xlsx" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"/></Types>');
  zip.file('[Content_Types].xml',contentTypes);
}
for(const name of Object.keys(zip.files).filter(n=>/^ppt\/(slides\/)?charts\/chart\d+\.xml$/.test(n))){let xml=await zip.file(name).async('string');const count=Number(xml.match(/<c:ptCount val="(\d+)"/)?.[1]||0);const skip=count>100?120:count===36?3:1;xml=xml.replace(/<c:tick(?:Lbl|Mark)Skip\b[^>]*\/>/g,'').replace(/<\/c:catAx>/g,`<c:tickLblSkip val="${skip}"/><c:tickMarkSkip val="${skip}"/></c:catAx>`);zip.file(name,xml);}
await fs.writeFile(candidate,await zip.generateAsync({type:'nodebuffer'}));
const final=path.join(root,process.env.SLIDES_OUTPUT || 'output/apresentacao_ilha_solteira.pptx');
const revision=Date.now();
const validated=path.join(tmp,`validated-${revision}.pptx`);
const receipt=path.join(root,'.codex-finalizer',`apresentacao-${revision}.validation.json`);
// O gráfico da abertura usa dados literais completos e recebe uma nova planilha.
// Na edição, os demais gráficos conservam as planilhas originais recuperadas acima.
const fontPolicy=referencePath ? {basis:'reference',families:[font],referencePath,referenceSha256:createHash('sha256').update(await fs.readFile(referencePath)).digest('hex')} : {basis:'design',families:[font]};
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:validated,pythonExecutable:process.env.RUNTIME_PYTHON,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],explicitTotalSlideCount:slideCount,requiredNativeChartOwnerSlides:[...new Set(owners)],requiredNativeTableOwnerSlides:[],materializeLiteralChartWorkbooks:true,fontPolicy,verifyArtifactToolImport:true,receiptPath:receipt});
await fs.copyFile(validated,final);
await fs.copyFile(receipt,path.join(root,'.codex-finalizer/apresentacao.validation.json'));
const finalPres=await PresentationFile.importPptx(await FileBlob.load(final));
const pdf=await PDFDocument.create();
for (let i=0;i<finalPres.slides.items.length;i++){const blob=await finalPres.export({slide:finalPres.slides.items[i],format:'png',scale:1.5});const bytes=new Uint8Array(await blob.arrayBuffer());await fs.writeFile(path.join(tmp,`slide-${String(i+1).padStart(2,'0')}.png`),bytes);const img=await pdf.embedPng(bytes);const p=pdf.addPage([960,540]);p.drawImage(img,{x:0,y:0,width:960,height:540});}
await fs.writeFile(path.join(root,'output/pdf/apresentacao_ilha_solteira.pdf'),await pdf.save());
const zfinal=await JSZip.loadAsync(await fs.readFile(final));
const evidence={invocation:'RUNTIME_NODE_MODULES=<bundled>/node/node_modules RUNTIME_PYTHON=<bundled>/python/bin/python3 SKILL_DIR=<presentations> node scripts/criar_slides.mjs',scenario:`Build ${slideCount}-slide editable deck, native chart workbook snapshots, notes, rendered PDF`,observables:{slides:Object.keys(zfinal.files).filter(n=>/^ppt\/slides\/slide\d+\.xml$/.test(n)).length,charts:Object.keys(zfinal.files).filter(n=>/^ppt\/(slides\/)?charts\/chart\d+\.xml$/.test(n)).length,notes:Object.keys(zfinal.files).filter(n=>/^ppt\/notesSlides\/notesSlide\d+\.xml$/.test(n)).length,pdfPages:pdf.getPageCount(),durationSeconds:duration},artifacts:{pptx:final,pdf:path.join(root,'output/pdf/apresentacao_ilha_solteira.pdf'),renders:tmp,finalizer:path.join(root,'.codex-finalizer/apresentacao.validation.json')},inputHashes:{},outputHashes:{},limitations:['PDF consists of high-resolution rendered slides; edit charts in the PPTX.','PowerPoint interactive edit test unavailable; native objects and embedded workbooks validated structurally.','Chart values rounded to four decimal places in editable workbooks.']};
for(const p of ['output/resumo.json','output/tables/previsoes_teste.csv','output/tables/previsoes_2017.csv','data/processed/ilha_solteira_mensal.csv']) evidence.inputHashes[p]=createHash('sha256').update(await fs.readFile(path.join(root,p))).digest('hex');
for(const p of [final,path.join(root,'output/pdf/apresentacao_ilha_solteira.pdf')]) evidence.outputHashes[p]=createHash('sha256').update(await fs.readFile(p)).digest('hex');
await fs.mkdir(path.join(root,'.omo/evidence'),{recursive:true});
await fs.writeFile(path.join(root,'.omo/evidence/slides-build.json'),JSON.stringify(evidence,null,2));
console.log(JSON.stringify({slides:slideCount,nativeChartSlides:[...new Set(owners)],notes:notes.length,font,pptx:final,pdf:'output/pdf/apresentacao_ilha_solteira.pdf'},null,2));
