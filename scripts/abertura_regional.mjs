import path from 'node:path';
import fs from 'node:fs/promises';

/** Atualiza a abertura, preservando os demais slides e seus gráficos. */
export async function aplicarAberturaRegional(pres, { root, font, raw }) {
  if (pres.slides.items.length !== 18) throw new Error('A abertura espera a base original de 18 slides.');
  const titles = ['Vazões de Ilha Solteira', 'O problema de previsão'];
  for (const [i, title] of titles.entries()) {
    if (!pres.slides.items[i].shapes.items.some(sh => String(sh.text) === title)) {
      throw new Error(`Slide ${i + 1} não corresponde à base esperada.`);
    }
  }
  const C = { paper: '#F6F3EB', ink: '#18343E', teal: '#007F80', gold: '#C48730', muted: '#5B7177', grid: '#D7DDD8' };
  const addText = (s, str, x, y, w, h, size, color = C.ink, bold = false) => {
    const shape = s.shapes.add({ geometry: 'textbox', position: { left: x, top: y, width: w, height: h }, fill: 'none', line: { fill: 'none', width: 0 } });
    shape.text = str;
    shape.text.style = { typeface: font, fontSize: size, color, bold, autoFit: 'none' };
    return shape;
  };
  for (const s of pres.slides.items.slice(0, 2)) {
    const layout = await s.export({ format: 'layout' });
    pres.delete(layout.elements.map(e => e.id));
    s.background.fill = C.paper;
  }
  const first = pres.slides.items[0];
  addText(first, 'Ilha Solteira e o rio Paraná', 64, 44, 1148, 70, 44, C.ink, true);
  addText(first, 'Vazões mensais de 1931 a 2016', 68, 117, 1136, 42, 26, C.muted);
  first.images.add({ blob: await fs.readFile(path.join(root, 'assets/fotos/usina_ilha_solteira.jpg')), contentType: 'image/jpeg', alt: 'Vertedouro da Usina Hidrelétrica Ilha Solteira, no rio Paraná. Foto de Carlos Alves.', fit: 'cover', position: { left: 72, top: 184, width: 420, height: 300 } });
  addText(first, 'A usina fica entre Ilha Solteira (SP)\ne Selvíria (MS), no rio Paraná.', 70, 500, 455, 84, 25);
  addText(first, 'Foto: Carlos Alves / CC BY 3.0', 72, 598, 455, 31, 16, C.muted);
  addText(first, 'Sazonalidade das vazões', 550, 178, 660, 48, 30, C.teal, true);
  const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
  const cycle = months.map((_, m) => {
    const values = raw.filter(row => Number(row.data.slice(5, 7)) === m + 1);
    if (values.length !== 86) throw new Error('O ciclo sazonal requer 86 observações por mês.');
    return Number((values.reduce((sum, row) => sum + row.vazao, 0) / values.length).toFixed(4));
  });
  first.charts.add('bar', {
    position: { left: 545, top: 237, width: 670, height: 310 },
    categories: months,
    series: [{ name: 'Média mensal histórica', values: cycle, valuesFormatCode: '0', fill: C.teal }],
    hasLegend: false,
    barOptions: { direction: 'column', grouping: 'clustered', gapWidth: 65 },
    chartFill: C.paper, plotAreaFill: C.paper,
    xAxis: { textStyle: { typeface: font, fontSize: 16, fill: C.ink }, majorGridlines: null, line: { fill: C.grid, width: 1 } },
    yAxis: { min: 0, max: 10000, numberFormatCode: '0', textStyle: { typeface: font, fontSize: 17, fill: C.ink }, majorGridlines: { fill: C.grid, width: 1 } },
  });
  addText(first, 'Maior média em fevereiro, menor em setembro.', 553, 557, 660, 40, 22, C.teal, true);
  addText(first, 'Média por mês, 1931–2016. Unidade da tabela.', 553, 602, 660, 33, 18, C.muted);
  addText(first, 'ARIMA e SARIMA', 995, 672, 215, 24, 16, C.muted);
  first.speakerNotes.text = 'Tempo: 85 segundos. Comece pela região. A Usina Ilha Solteira fica no rio Paraná, entre Ilha Solteira, em São Paulo, e Selvíria, em Mato Grosso do Sul. A foto mostra seu vertedouro. Passe ao gráfico: cada coluna reúne a média daquele mês nos 86 anos da série. Fevereiro tem a maior média e setembro a menor. Essa sazonalidade motiva considerar um ciclo de 12 meses. O gráfico descreve a base completa e não participa da seleção de parâmetros. A unidade e a natureza da vazão não foram informadas no PDF. A série começa antes da construção da usina, portanto não a apresente como uma série de medições da operação da usina. Fontes: https://www.ctgbr.com.br/unidade/uhe-ilha-solteira/ ; data/processed/ilha_solteira_mensal.csv. Foto: Carlos Alves, Wikimedia Commons, https://commons.wikimedia.org/wiki/File:Usina_UHE_Ilha_Solteira_-_panoramio_-_Carlos_Alves_(2).jpg . Licença CC BY 3.0, https://creativecommons.org/licenses/by/3.0/ . Foto recortada para o enquadramento do slide.';

  const second = pres.slides.items[1];
  addText(second, 'A cidade e a usina', 64, 44, 1148, 100, 44, C.ink, true);
  addText(second, '1968', 70, 180, 420, 91, 64, C.teal, true);
  addText(second, 'A cidade surge para receber\nos trabalhadores da usina.', 75, 288, 475, 105, 27);
  addText(second, '1973', 70, 418, 420, 91, 64, C.gold, true);
  addText(second, 'A primeira unidade geradora\nentra em operação em julho.', 75, 522, 475, 105, 27);
  second.images.add({ blob: await fs.readFile(path.join(root, 'assets/fotos/praca_paiaguas.jpg')), contentType: 'image/jpeg', alt: 'Praça Paiaguás, na cidade de Ilha Solteira, em fotografia de Mof0 de 2008.', fit: 'contain', position: { left: 565, top: 164, width: 643, height: 482.25 } });
  addText(second, 'Praça Paiaguás. Foto: Mof0 / CC BY-SA 2.0', 565, 648, 643, 24, 16, C.muted);
  second.speakerNotes.text = 'Tempo: 60 segundos. Use a foto da Praça Paiaguás para apresentar a cidade. Ilha Solteira surgiu em 1968 para abrigar trabalhadores da construção da hidrelétrica. Em 18 de julho de 1973, a primeira unidade geradora entrou em operação. A relação entre cidade, rio e geração de energia dá contexto ao estudo. Faça a transição: agora vamos conhecer a série de vazões que o grupo recebeu. Fonte: https://www.ctgbr.com.br/unidade/uhe-ilha-solteira/ . Foto: Praça Paiaguás em Ilha Solteira-SP, Brasil, Mof0, 25 de agosto de 2008, https://commons.wikimedia.org/wiki/File:Pra%C3%A7a_Paiagu%C3%A1s_em_Ilha_Solteira-SP,_Brasil.jpg . Licença CC BY-SA 2.0, https://creativecommons.org/licenses/by-sa/2.0/ . Imagem integral, redimensionada, sem recorte. As fotografias ilustram os locais e não representam um registro atual de 2026.';

  // O gráfico sazonal passou do antigo slide 5 para a abertura.
  pres.slides.keep(pres.slides.items.map((_, i) => i).filter(i => i !== 4));
  pres.slides.items.forEach((s, i) => {
    const footer = s.shapes.items.find(sh => /^\d{2}  Ilha Solteira$/.test(String(sh.text)));
    const label = `${String(i + 1).padStart(2, '0')}  Ilha Solteira`;
    if (footer) footer.text = label;
    else addText(s, label, 64, 672, 600, 24, 16, C.muted);
  });
}
