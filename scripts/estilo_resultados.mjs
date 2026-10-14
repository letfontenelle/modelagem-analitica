/** Reorganiza os resultados com a identidade visual do painel da base. */
export async function aplicarEstiloResultados(pres, { font, summary }) {
  const titleOf = s => String(s.shapes.items.find(sh => (sh.frame ?? sh.position).top === 44 && String(sh.text).trim())?.text ?? '');
  const remove = new Set(['ARIMA e SARIMA', 'Logaritmo, diferenças e estacionariedade', 'Código, exemplos e referências']);
  pres.slides.keep(pres.slides.items.map((s, i) => remove.has(titleOf(s)) ? -1 : i).filter(i => i >= 0));
  const C = { navy: '#102E3A', panel: '#1B414D', teal: '#007F80', mint: '#D5E9E4', paper: '#F6F3EB', gold: '#D9AC69', muted: '#A5C8CB' };
  const f = (n, d = 0) => Number(n).toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const metrics = Object.fromEntries(summary.metricas_teste.map(m => [m.modelo, m]));
  const ar = metrics.ARIMA, sar = metrics.SARIMA;
  function box(s, x, y, w, h, fill) {
    return s.shapes.add({ geometry: 'roundRect', position: { left: x, top: y, width: w, height: h }, fill, line: { fill: 'none', width: 0 }, borderRadius: 18 });
  }
  function text(s, str, x, y, w, h, size = 26, color = C.paper, bold = false) {
    const sh = s.shapes.add({ geometry: 'textbox', position: { left: x, top: y, width: w, height: h }, fill: 'none', line: { fill: 'none', width: 0 } });
    sh.text = str;
    sh.text.style = { typeface: font, fontSize: size, color, bold, autoFit: 'none' };
  }
  function heading(s, title, subtitle) {
    text(s, title, 64, 44, 1152, 68, 42, C.paper, true);
    text(s, subtitle, 68, 113, 1140, 36, 22, C.muted);
  }
  function takeaway(s, str, fill = C.teal) {
    box(s, 64, 612, 1152, 50, fill);
    text(s, str, 82, 619, 1116, 37, 23, fill === C.teal ? C.paper : C.navy, true);
  }
  const specs = [
    ['A série combina sazonalidade e extremos', 'Sazonalidade e extremos na série', '1.032 observações mensais, de 1931 a 2016', `Menor valor: ${f(summary.minimo)} (out/2014). Maior valor: ${f(summary.maximo)} (fev/1983).`],
    ['O ingênuo sazonal tem o menor erro no teste', 'No teste, o ingênuo sazonal vence', '2014–2016, origem dez/2013. RMSE menor indica menor erro.', `RMSE: ${f(metrics['Ingênuo sazonal'].RMSE)} no ingênuo sazonal, ${f(sar.RMSE)} no SARIMA e ${f(ar.RMSE)} no ARIMA.`],
    ['As previsões centrais superestimam parte do teste', 'As previsões superestimam parte do teste', 'Valores observados e médias previstas para os 36 meses de 2014–2016', `Média no teste: ${f(summary.media_2014_2016)}. Média do histórico até 2013: ${f(summary.media_ate_2013)}.`],
    ['Intervalos preditivos de 95%: ARIMA', 'ARIMA: intervalos preditivos de 95%', 'Teste de 36 meses, com origem em dezembro de 2013', `33 de 36 meses dentro dos intervalos. Cobertura observada: ${f(ar.cobertura_95, 1)}%.`],
    ['Intervalos preditivos de 95%: SARIMA', 'SARIMA: intervalos preditivos de 95%', 'Teste de 36 meses, com origem em dezembro de 2013', `30 de 36 meses dentro dos intervalos. Cobertura observada: ${f(sar.cobertura_95, 1)}%.`],
    ['Projeção histórica para 2017', 'O que os modelos projetaram para 2017', 'Reajuste com dados até dezembro de 2016. Projeção histórica.', 'Os valores reais de 2017 não estão na base para conferir essas projeções.'],
  ];
  for (const s of pres.slides.items.slice(2)) {
    const oldTitle = titleOf(s);
    const oldNote = String(s.speakerNotes.text);
    const layout = await s.export({ format: 'layout' });
    pres.delete(layout.elements.filter(e => e.kind !== 'chart').map(e => e.id));
    s.background.fill = C.navy;
    const spec = specs.find(row => row[0] === oldTitle || row[1] === oldTitle);
    if (spec) {
      if (s.charts.items.length !== 1) throw new Error(`Gráfico ausente em ${oldTitle}.`);
      heading(s, spec[1], spec[2]);
      box(s, 64, 155, 1152, 447, C.paper).sendToBack();
      s.charts.items[0].position = { left: 72, top: 166, width: 1136, height: 425 };
      takeaway(s, spec[3], spec[1].includes('2017') ? C.gold : C.teal);
      text(s, 'Valores de vazão e erros na unidade da tabela.', 680, 672, 536, 24, 15, C.muted);
      if (spec[1].startsWith('ARIMA:')) {
        s.speakerNotes.text = `Tempo: 60 segundos. Acompanhe o observado junto da média e dos dois limites do ARIMA. Dos 36 meses do teste, 33 ficaram dentro dos intervalos, cobertura de ${f(ar.cobertura_95, 1)}%, abaixo do nível nominal de 95%. A largura média foi ${f(ar.largura_media_95)} na unidade da tabela. Mostre que os intervalos são largos e que uma previsão central pode se afastar do observado mesmo quando os limites o contêm. São intervalos para cada mês, condicionais ao modelo. Fonte: output/tables/previsoes_teste.csv e output/tables/metricas_teste.csv.`;
      }
    } else if (['A avaliação respeita a ordem do tempo', 'Como os resultados foram avaliados'].includes(oldTitle)) {
      heading(s, 'Como os resultados foram avaliados', 'Os meses do teste final ficaram fora da escolha dos modelos.');
      const rows = [
        { x: 64, fill: C.panel, color: C.paper, year: '1931–2008', label: 'Treino inicial', body: 'Histórico usado para\najustar os candidatos.' },
        { x: 456, fill: C.teal, color: C.paper, year: '2009–2013', label: 'Validação', body: '5 origens anuais.\n12 meses previstos\nem cada origem.' },
        { x: 848, fill: C.mint, color: C.navy, year: '2014–2016', label: 'Teste final', body: '36 meses à frente.\nOrigem única:\ndezembro de 2013.' },
      ];
      for (const r of rows) {
        box(s, r.x, 184, 368, 374, r.fill);
        text(s, r.label, r.x + 22, 207, 324, 50, 30, r.color, true);
        text(s, r.year, r.x + 20, 282, 328, 65, 42, r.color, true);
        text(s, r.body, r.x + 22, 390, 324, 130, 26, r.color);
      }
      takeaway(s, 'A validação avalia 12 meses por origem; o teste final avalia 36 meses.', C.gold);
    } else if (['Seleção dentro de cada família', 'Os modelos escolhidos na validação'].includes(oldTitle)) {
      heading(s, 'Os modelos escolhidos na validação', 'Um modelo selecionado em cada família, antes do teste de 2014–2016.');
      const rows = [
        { x: 64, name: 'ARIMA', fill: C.panel, color: C.paper, order: `(${summary.selecionados.ARIMA.order.join(', ')})` },
        { x: 656, name: 'SARIMA', fill: C.mint, color: C.navy, order: `(${summary.selecionados.SARIMA.order.join(', ')}) × (${summary.selecionados.SARIMA.seasonal_order.slice(0,3).join(', ')})₁₂` },
      ];
      for (const r of rows) {
        const score = summary.ranking_validacao.find(item => item.id === summary.selecionados[r.name].id).RMSE;
        box(s, r.x, 180, 560, 383, r.fill);
        text(s, r.name, r.x + 28, 205, 504, 65, 44, r.color, true);
        text(s, r.order, r.x + 30, 280, 500, 50, 31, r.color);
        text(s, 'RMSE na validação', r.x + 30, 369, 500, 44, 26, r.color);
        text(s, f(score), r.x + 26, 430, 506, 95, 68, r.color, true);
      }
      takeaway(s, 'O SARIMA teve menor erro na validação. O teste reservado vem a seguir.');
    } else if (['A cobertura observada fica abaixo de 95%', 'A cobertura ficou abaixo dos 95% nominais'].includes(oldTitle)) {
      heading(s, 'A cobertura ficou abaixo dos 95% nominais', 'Quantidade de meses observados dentro dos intervalos de cada modelo.');
      for (const r of [{x:64,name:'ARIMA',m:ar,fill:C.panel,color:C.paper},{x:656,name:'SARIMA',m:sar,fill:C.mint,color:C.navy}]) {
        box(s, r.x, 180, 560, 383, r.fill);
        text(s, r.name, r.x + 28, 203, 504, 55, 36, r.color, true);
        text(s, `${f(r.m.cobertura_95,1)}%`, r.x + 24, 275, 510, 112, 80, r.color, true);
        text(s, `${Math.round(r.m.cobertura_95 * 36 / 100)} de 36 meses`, r.x + 30, 408, 500, 48, 30, r.color);
        text(s, `Largura média: ${f(r.m.largura_media_95)}`, r.x + 30, 489, 500, 45, 27, r.color);
      }
      takeaway(s, 'O ARIMA cobriu mais meses, com intervalos mais largos. Teste com 36 meses.', C.gold);
    } else if (['Os resíduos ainda contêm dependência', 'Os diagnósticos mostram limites dos modelos'].includes(oldTitle)) {
      heading(s, 'Os diagnósticos mostram limites dos modelos', 'Resultados encontrados tanto no ARIMA quanto no SARIMA.');
      box(s,64,180,560,383,C.panel);
      box(s,656,180,560,383,C.mint);
      text(s,'Dependência restante',90,212,508,53,32,C.paper,true);
      text(s,'p < 0,05',90,303,508,97,65,C.gold,true);
      text(s,'Ljung–Box, em 12 e 24 defasagens\nNos dois modelos',92,447,504,85,25,C.paper);
      text(s,'Normalidade rejeitada',682,212,508,53,32,C.navy,true);
      text(s,'p < 0,05',682,303,508,97,65,C.navy,true);
      text(s,'Jarque–Bera\nNos dois modelos',684,447,504,85,25,C.navy);
      takeaway(s, 'Os resíduos ainda têm padrões que os modelos não conseguiram explicar.', C.gold);
    } else if (['O que os resultados permitem concluir', 'O que os resultados mostram'].includes(oldTitle)) {
      heading(s, 'O que os resultados mostram', 'A comparação reúne sazonalidade, desempenho e incerteza.');
      const rows = [
        { x:64, fill:C.panel, color:C.paper, title:'Sazonalidade', body:'O ciclo anual aparece\nnas vazões mensais.' },
        { x:456, fill:C.teal, color:C.paper, title:'Desempenho', body:'SARIMA vence na\nvalidação. O ingênuo\nsazonal vence no teste.' },
        { x:848, fill:C.mint, color:C.navy, title:'Incerteza', body:'Os intervalos são largos\ne os resíduos ainda\ncontêm dependência.' },
      ];
      for(const [i,r] of rows.entries()) {
        box(s,r.x,184,368,374,r.fill);
        text(s,String(i+1).padStart(2,'0'),r.x+22,205,324,66,44,r.color,true);
        text(s,r.title,r.x+22,304,324,54,31,r.color,true);
        text(s,r.body,r.x+22,395,324,125,25,r.color);
      }
      takeaway(s, 'A sazonalidade descreve a série, mas não garante a melhor previsão.', C.gold);
    } else {
      throw new Error(`Slide de resultados não reconhecido: ${oldTitle}`);
    }
    if (!String(s.speakerNotes.text)) s.speakerNotes.text = oldNote;
  }
  pres.slides.items.forEach((s,i) => {
    const label = `${String(i+1).padStart(2,'0')}  Ilha Solteira`;
    const footer = s.shapes.items.find(sh => /^\d{2}  Ilha Solteira$/.test(String(sh.text)));
    if(footer) footer.text = label;
    else text(s,label,64,672,600,24,16,C.muted);
  });
}
