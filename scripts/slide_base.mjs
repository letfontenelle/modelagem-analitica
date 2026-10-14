/** Painel editável com as características e limitações da base recebida. */
export async function aplicarSlideBase(pres, { font, summary }) {
  const slide = pres.slides.items.find(s => s.shapes.items.some(sh =>
    ['86 anos de observações mensais', 'A base de dados em um olhar'].includes(String(sh.text))));
  if (!slide) throw new Error('Slide da base de dados não encontrado.');
  const index = pres.slides.items.indexOf(slide);
  const layout = await slide.export({ format: 'layout' });
  pres.delete(layout.elements.map(e => e.id));
  const C = { navy: '#102E3A', panel: '#1B414D', teal: '#007F80', mint: '#D5E9E4', paper: '#F6F3EB', gold: '#D9AC69', muted: '#A5C8CB' };
  slide.background.fill = C.navy;
  const box = (x, y, w, h, fill, name, geometry = 'roundRect') => slide.shapes.add({
    name, geometry, position: { left: x, top: y, width: w, height: h },
    fill, line: { fill: 'none', width: 0 }, ...(geometry === 'roundRect' ? { borderRadius: 18 } : {}),
  });
  const text = (str, x, y, w, h, size = 24, color = C.paper, bold = false) => {
    const sh = slide.shapes.add({ geometry: 'textbox', position: { left: x, top: y, width: w, height: h }, fill: 'none', line: { fill: 'none', width: 0 } });
    sh.text = str;
    sh.text.style = { typeface: font, fontSize: size, color, bold, autoFit: 'none' };
  };
  const f = n => Number(n).toLocaleString('pt-BR', { maximumFractionDigits: 0 });
  text('A base de dados em um olhar', 64, 44, 1152, 64, 44, C.paper, true);
  text('Vazões médias mensais fornecidas ao grupo', 68, 108, 1136, 30, 21, C.muted);

  box(64, 151, 368, 151, C.teal, 'Quantidade de observações');
  box(456, 151, 368, 151, C.panel, 'Período de observação');
  box(848, 151, 368, 151, C.mint, 'Frequência temporal');
  text(f(summary.n), 86, 164, 325, 73, 58, C.paper, true);
  text('observações mensais', 90, 247, 325, 36, 24);
  text('86 anos', 480, 172, 320, 65, 48, C.gold, true);
  text('jan/1931 a dez/2016', 480, 247, 320, 36, 24);
  text('12 por ano', 871, 172, 325, 65, 48, C.navy, true);
  text('frequência mensal regular', 873, 247, 325, 36, 22, C.navy);

  box(64, 326, 744, 248, C.panel, 'Estrutura e qualidade da base');
  text('Da tabela do PDF à série temporal', 86, 339, 700, 43, 28, C.paper, true);
  box(88, 398, 266, 82, '#285563', 'Formato original');
  box(410, 398, 374, 82, C.mint, 'Formato organizado');
  box(369, 425, 26, 27, C.gold, 'Transformação da tabela anual em série mensal', 'rightArrow');
  text('86 linhas anuais', 99, 407, 245, 34, 23, C.paper, true);
  text('12 colunas de meses', 99, 446, 245, 29, 21);
  text('1.032 linhas mensais', 423, 407, 347, 34, 23, C.navy, true);
  text('data, vazão + referência no PDF', 423, 446, 347, 29, 19, C.navy);
  text('Sem meses ausentes ou duplicados.\nTodos os valores são positivos.', 88, 502, 696, 65, 23);

  box(832, 326, 384, 248, C.paper, 'Estatísticas descritivas da série completa');
  text('Valores da série', 852, 339, 344, 43, 28, C.navy, true);
  text(`Média: ${f(summary.media)}\nMediana: ${f(summary.mediana)}\nDesvio padrão: ${f(summary.desvio)}\nMínimo: ${f(summary.minimo)} (out/2014)\nMáximo: ${f(summary.maximo)} (fev/1983)`, 853, 391, 344, 166, 22, C.navy);

  text(`${String(index + 1).padStart(2, '0')}  Ilha Solteira`, 64, 672, 300, 24, 16, C.muted);
  text('Fonte: ILHA_SOLTEIRA.pdf. Estatísticas na unidade da tabela, arredondadas.', 392, 672, 824, 24, 15, C.muted);
  slide.speakerNotes.text = 'Tempo: 85 segundos. Apresente os três números do topo: 1.032 observações, 86 anos de janeiro de 1931 a dezembro de 2016 e frequência de 12 valores por ano. Cada valor representa uma vazão média mensal. A fonte recebida é ILHA_SOLTEIRA.pdf. No documento, os anos e os meses estão organizados em uma tabela anual distribuída pelas páginas. A extração organiza uma linha por mês. O CSV tem as colunas data, vazao, pagina_pdf e linha_tabela, permitindo rastrear cada observação até sua origem. O índice é mensal, sem lacunas ou duplicatas, e todos os valores são positivos. Não foi necessário preencher meses ausentes. Explique o painel de estatísticas da série completa: média 5.271,65, mediana 4.194 e desvio padrão amostral 3.095,16. Os valores foram arredondados no slide para facilitar a leitura. O mínimo é 1.212 em outubro de 2014 e o máximo é 20.314 em fevereiro de 1983. As estatísticas descrevem a base e não são usadas para escolher parâmetros com os dados de teste. A fonte não explicita a unidade nem se a vazão é natural, afluente ou defluente. Não confirme m³/s sem outra documentação. A base termina em 2016 e não fornece observações de 2017. Fontes: data/raw/ILHA_SOLTEIRA.pdf, data/processed/ilha_solteira_mensal.csv, data/processed/metadados.json e output/resumo.json. Conferência independente dos valores e da regularidade: scripts/verificar.py.';
}
