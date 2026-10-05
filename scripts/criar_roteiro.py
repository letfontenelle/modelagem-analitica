import json
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib.font_manager as fm
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]


def numero(valor, casas=1):
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def criar_roteiro():
    r = json.loads((ROOT / "output/resumo.json").read_text())
    met = pd.read_csv(ROOT / "output/tables/metricas_teste.csv").set_index("modelo")
    diag = pd.read_csv(ROOT / "output/tables/diagnosticos.csv").set_index("modelo")
    est = pd.read_csv(ROOT / "output/tables/estacionariedade.csv")
    busca = pd.read_csv(ROOT / "output/tables/busca_modelos.csv")
    rank = pd.read_csv(ROOT / "output/tables/ranking_validacao.csv")
    prev = pd.read_csv(ROOT / "output/tables/previsoes_2017.csv")
    for nome, prop in [("Texto", fm.FontProperties(family="DejaVu Sans")),
                        ("TextoBold", fm.FontProperties(family="DejaVu Sans", weight="bold")),
                        ("Mono", fm.FontProperties(family="DejaVu Sans Mono"))]:
        pdfmetrics.registerFont(TTFont(nome, fm.findfont(prop)))
    pdfmetrics.registerFontFamily("Texto", normal="Texto", bold="TextoBold", italic="Texto", boldItalic="TextoBold")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Corpo", fontName="Texto", fontSize=10.2, leading=16.4,
                              textColor=colors.HexColor("#173847"), spaceAfter=12))
    styles.add(ParagraphStyle(name="TituloGuia", fontName="TextoBold", fontSize=24, leading=29,
                              textColor=colors.HexColor("#173847"), spaceAfter=22))
    styles.add(ParagraphStyle(name="SubGuia", fontName="TextoBold", fontSize=13.5, leading=19,
                              textColor=colors.HexColor("#137F83"), spaceAfter=10, spaceBefore=9))
    styles.add(ParagraphStyle(name="LegendaGuia", fontName="Texto", fontSize=8, leading=11,
                              textColor=colors.HexColor("#526C76"), spaceAfter=12))
    styles.add(ParagraphStyle(name="TabelaGuia", fontName="Texto", fontSize=8.7, leading=12))
    styles.add(ParagraphStyle(name="CodigoGuia", fontName="Mono", fontSize=8, leading=12,
                              textColor=colors.HexColor("#173847"), backColor=colors.HexColor("#E8EFEC"),
                              borderPadding=10, spaceBefore=6, spaceAfter=16))
    story = []
    width = A4[0] - 100

    def p(text):
        story.append(Paragraph(text, styles["Corpo"]))

    def h(text):
        story.append(Paragraph(text, styles["SubGuia"]))

    def page(title):
        if story:
            story.append(PageBreak())
        story.append(Paragraph(title, styles["TituloGuia"]))

    def chart(name, max_height=360):
        path = ROOT / "output/figures" / name
        from PIL import Image as PILImage
        with PILImage.open(path) as im:
            w, hei = im.size
        scale = min(width / w, max_height / hei)
        story.append(Image(str(path), width=w * scale, height=hei * scale))
        story.append(Spacer(1, 12))

    def table(rows, widths=None):
        cells = [[Paragraph(escape(str(c)), styles["TabelaGuia"]) for c in row] for row in rows]
        t = Table(cells, colWidths=widths, hAlign="LEFT", repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D7E7E2")),
                               ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F4F5EF"), colors.white]),
                               ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 8),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
        story.extend([t, Spacer(1, 14)])

    def code(text):
        story.append(Preformatted(text, styles["CodigoGuia"]))

    page("Ilha Solteira\nVazões, memória e previsão")
    story.append(Spacer(1, 8))
    p("<b>Guia de estudo e roteiro de apresentação</b><br/>Modelagem ARIMA e SARIMA com intervalos de previsão de 95%")
    chart("01_serie_historica.png", 265)
    p("Uma análise de 1.032 meses, de janeiro de 1931 a dezembro de 2016. Este guia conecta cada decisão do código à interpretação dos resultados e à fala da apresentação de 15–20 minutos.")
    p("<b>Leia junto com:</b> notebooks/ilha_solteira.ipynb, a apresentação e as tabelas em output/tables. O notebook contém código executado, saídas e explicações em português.")
    p("<b>Contexto temporal:</b> a projeção começa em janeiro de 2017 porque o arquivo termina em 2016. É um exercício histórico, não uma previsão atualizada para 2026.")
    p("Fonte: ILHA_SOLTEIRA.pdf fornecido pelo grupo. Unidade m³/s adotada como hipótese: a tabela não declara unidade, agência produtora ou natureza das vazões.")

    page("Como estudar e apresentar")
    p("O objetivo é prever vazões médias mensais usando o comportamento passado da própria série. Um modelo útil precisa acertar valores que não viu e representar a incerteza; ajustar bem o histórico não basta.")
    table([["Etapa", "Pergunta que você precisa responder"],
           ["Dados", "O que mede cada linha? Há meses faltando? O que a fonte não informa?"],
           ["Exploração", "Há repetição anual, extremos ou mudanças de nível?"],
           ["Transformação", "Por que log, diferença e sazonalidade são coisas diferentes?"],
           ["Modelos", "O que significam p, d, q e P, D, Q, 12?"],
           ["Seleção", "Como escolher parâmetros sem usar o teste?"],
           ["Avaliação", "Qual modelo errou menos? Os intervalos cobriram o observado?"],
           ["Conclusão", "O que esses resultados permitem afirmar e o que fica em aberto?"]], [90, width-90])
    p("Na primeira leitura, acompanhe gráficos e frases em negrito. Na segunda, execute as células do notebook em ordem. Na terceira, ensaie usando as notas dos slides. Evite decorar números isolados: saiba explicar o que está sendo comparado.")
    p("A versão .py usa separadores <b># %%</b> para execução por células no Zed. O .ipynb pode ser aberto no JupyterLab e no GitHub. Ambos apresentam a mesma análise didática.")

    page("O que existe no dataset")
    table([["Característica", "Valor / interpretação"],
           ["Variável", "Vazão média mensal; um número por mês"],
           ["Estação / identificação", "ILHA SOLTEIRA (34), como aparece no cabeçalho"],
           ["Cobertura", "Jan/1931 a dez/2016; 86 anos e 1.032 observações"],
           ["Frequência", "Mensal regular; data no primeiro dia, frequência MS"],
           ["Ausentes / duplicatas", "Nenhum na tabela extraída"],
           ["Média / mediana", f"{numero(r['media'])} / {numero(r['mediana'])}"],
           ["Desvio padrão amostral", numero(r["desvio"])],
           ["Mínimo", f"{numero(r['minimo'],0)}, em {r['data_minimo'][:7]}"],
           ["Máximo", f"{numero(r['maximo'],0)}, em {r['data_maximo'][:7]}"],
           ["Unidade e natureza", "m³/s é hipótese. Vazão natural, afluente, defluente ou observada não é especificada."]], [150, width-150])
    p("<b>Como interpretar:</b> a média é superior à mediana, coerente com valores altos que puxam a média para cima. Isso ajuda a motivar uma análise em log, mas não prova sozinho qual distribuição descreve os dados.")
    p("Não confundimos média mensal com volume mensal: vazão expressa uma taxa. Não multiplicamos pelos dias do mês, pois a variável alvo continua sendo a vazão média.")

    page("Como o PDF virou uma série")
    p("A tabela está dividida horizontalmente. Nas páginas 1 e 3 aparecem ano e janeiro a setembro; nas páginas 2 e 4, outubro a dezembro. Ler as páginas como uma sequência única deslocaria os meses.")
    table([["Par de páginas", "Anos", "Como unir"], ["1 + 2", "1931–1979", "Mesma posição de linha"],
           ["3 + 4", "1980–2016", "Mesma posição de linha"]], [110, 120, width-230])
    p("<b>extrair_pdf()</b> lê os números com pdfplumber. Aceita tanto ano em linha própria quanto ano seguido dos nove valores. Exige três valores nas páginas da direita, a mesma quantidade de linhas nos pares e todos os meses de 1931 a 2016.")
    p("Cada registro guarda <b>data</b>, <b>vazao</b>, <b>pagina_pdf</b> e <b>linha_tabela</b>. O arquivo metadados.json registra o hash SHA-256 da fonte, permitindo conferir se o PDF é o mesmo. Os valores são os inteiros publicados, sem interpolação e sem exclusão de extremos.")
    p("A verificação reconstrói a tabela também a partir das células delimitadas pelas linhas do PDF e compara os 1.032 números com a extração textual. Essa segunda rota reduz o risco de erro de alinhamento.")
    code("df = extrair_pdf()\nserie = df.set_index('data')['vazao']\n# O arquivo salvo é lido com parse_dates e asfreq('MS').")
    p("O primeiro dia funciona como rótulo do mês, não como afirmação de que a medição ocorreu naquele dia. MS significa início do mês.")

    page("Como ler o histórico")
    chart("01_serie_historica.png", 320)
    p("A linha fina mostra todas as vazões mensais. A média móvel usa uma janela de 12 meses encerrada no mês mostrado para suavizar oscilações e revelar variações mais lentas. Ela é um recurso descritivo, não uma variável fornecida ao modelo.")
    p(f"A média até 2013 foi {numero(r['media_ate_2013'])}; em 2014–2016 foi {numero(r['media_2014_2016'])}. A queda é de {numero(100*(1-r['media_2014_2016']/r['media_ate_2013']))}%. O período de teste é mais baixo que o histórico anterior.")
    p("<b>Fala sugerida:</b> “Há um ciclo anual claro, mas os ciclos não têm sempre a mesma altura. O teste contém um período de vazões menores, o que torna a extrapolação do passado um desafio.”")
    p("A diferença entre médias é uma descrição. Não atribuímos a causa a chuva, operação de reservatórios, uso do solo ou mudança climática: essas variáveis e metadados não estão no arquivo.")

    page("O ciclo anual")
    chart("02_sazonalidade.png", 320)
    p("Cada boxplot reúne observações do mesmo mês no treino inicial. A linha dentro da caixa é a mediana; a caixa vai do primeiro ao terceiro quartil. Os pontos fora dos bigodes são valores extremos segundo a regra do boxplot, não erros a apagar.")
    p("O gráfico da direita calcula a média por mês do ano. Meses de maiores vazões voltam a aparecer aproximadamente a cada 12 meses; por isso usamos <b>s = 12</b> no componente sazonal.")
    p("O perfil de um mês é uma distribuição, não uma previsão determinística. Janeiro de dois anos distintos pode ter vazões muito diferentes. A sazonalidade descreve a repetição de um padrão, não a repetição exata do valor.")
    p("<b>Fala sugerida:</b> “ARIMA usa dependência entre meses próximos. SARIMA acrescenta dependência entre o mesmo mês de anos diferentes. A comparação vai dizer se essa estrutura ajuda fora da amostra.”")

    page("Decomposição aditiva")
    chart("04_decomposicao_aditiva.png", 385)
    p("A representação aditiva é <b>observado = tendência + sazonalidade + resíduo</b>. A tendência suaviza; a sazonalidade repete o perfil de 12 meses; o resíduo reúne o que sobra dessa decomposição.")
    p("Nos exemplos, uma chamada usava metade do tamanho da série como período. Aqui o período é 12 porque a frequência é mensal e o ciclo analisado é anual. A decomposição usa somente o treino inicial.")
    p("A suavização clássica usa uma janela centrada e pode deixar pontas sem tendência estimada. Isso não significa que existam vazões faltantes. A decomposição é exploratória e não alimenta o ajuste nem seleciona os parâmetros.")

    page("Decomposição multiplicativa")
    chart("05_decomposicao_multiplicativa.png", 385)
    p("A representação multiplicativa é <b>observado = tendência × sazonalidade × resíduo</b>. Os fatores sazonais e residuais são adimensionais, próximos de 1. Ela é adequada como exploração quando amplitudes crescem com o nível.")
    p("O log transforma multiplicações em somas. Comparar as duas decomposições ajuda a entender a transformação, mas não garante que o modelo lognormal seja verdadeiro. A comparação preditiva continua sendo necessária.")
    p("Não tratamos o resíduo desta figura como o erro do ARIMA ou SARIMA. Cada método define um resíduo diferente; o diagnóstico dos modelos será calculado a partir de suas inovações padronizadas.")

    page("Treino, validação e teste")
    table([["Parte", "Período", "Função"], ["Treino inicial", "1931–2008\n936 meses", "Diagnósticos iniciais e busca por AIC"],
           ["Validação", "2009–2013\n5 janelas de 12 meses", "Escolher uma ordem por família"],
           ["Ajuste antes do teste", "1931–2013\n996 meses", "Estimar os parâmetros das ordens já escolhidas"],
           ["Teste final", "2014–2016\n36 meses", "Avaliação em uma única origem, dez/2013"],
           ["Reajuste final", "1931–2016", "Projetar os 12 meses de 2017"]], [120, 140, width-260])
    p("Na validação, prevemos 2009 usando até 2008, depois 2010 usando até 2009, e assim por diante. É uma janela crescente: cada ajuste conhece somente o passado disponível naquela origem.")
    p("O teste tem horizonte de 36 meses, sem atualizar o modelo com os valores observados de 2014 ou 2015. Todos os modelos e baselines recebem a mesma informação nessa comparação.")
    p("<b>Limitação deliberada:</b> a validação usa 12 passos, mas o teste usa 36. Isso avalia extrapolação mais longa e pode mudar a ordem dos modelos. Os RMSE de validação e teste não são comparações perfeitamente equivalentes.")
    p("Não sorteamos treino e teste. Em séries temporais, embaralhar dados permite que o futuro ajude a prever o passado e gera uma avaliação artificialmente favorável.")

    page("Log, centragem e diferenças")
    p("Todos os valores são positivos. Modelamos <b>z = log(vazão) − média do log no treino</b>. O log reduz a influência relativa de picos e permite intervalos positivos após a transformação inversa.")
    p("A centragem usa somente a amostra do ajuste. Subtrair uma constante ajuda o otimizador quando há intercepto e termos sazonais próximos da fronteira. A constante é guardada em <b>ajuste.centro_log</b> e somada à previsão antes da exponencial. A centragem não remove sazonalidade nem tendência.")
    table([["Operação", "Expressão", "Interpretação"], ["Diferença comum", "log(y[t]) − log(y[t−1])", "Mudança proporcional entre meses próximos"],
           ["Diferença sazonal", "log(y[t]) − log(y[t−12])", "Mudança em relação ao mesmo mês do ano anterior"]], [110, 170, width-280])
    p("<b>d</b> conta as diferenças comuns; <b>D</b> conta as diferenças sazonais. Diferenciar não é uma obrigação de todo ARIMA: d=0 também é permitido. Diferenciar demais pode criar dependência artificial e aumentar o erro.")
    p("No código, as diferenças das figuras são exploratórias. O SARIMAX recebe o log centrado e aplica a diferenciação especificada no próprio modelo. Não fornecemos uma série já diferenciada e pedimos a mesma diferença novamente.")

    page("Estacionariedade: dois testes")
    table([["Série no treino", "p ADF", "p KPSS"]] + [[row["serie"], f"{row['ADF_p']:.3g}", f"{row['KPSS_p']:.3g}"] for _, row in est.iterrows()], [240, 120, width-360])
    p("<b>ADF:</b> a hipótese nula é a presença de raiz unitária. Um p pequeno é evidência contra essa hipótese. <b>KPSS:</b> a hipótese nula é estacionariedade em nível; p pequeno é evidência contra ela. Usamos intercepto em ambos, sem tendência determinística.")
    p("Na série original e no log, ADF rejeita raiz unitária, enquanto KPSS rejeita estacionariedade em nível. Isso é um sinal de diagnóstico inconclusivo, não uma contradição a esconder. Os testes verificam hipóteses diferentes e podem reagir a sazonalidade, mudanças lentas e quebras.")
    p("As diferenças comum e sazonal apresentam ADF pequeno e KPSS no limite superior da tabela. Isso apoia examiná-las como candidatas, sem provar que toda dependência desapareceu.")
    p("O p do KPSS exibido como 0,01 ou 0,10 é um limite da tabela, não necessariamente um valor exato. Os avisos completos ficam em estacionariedade.csv. Nenhum resultado é decidido somente pelo menor p.")
    p("<b>Fala sugerida:</b> “Os testes motivam comparar especificações. A decisão final de ordem usa previsões em validação temporal, e os resíduos mostram o que ainda ficou sem explicar.”")

    page("O significado de ARIMA e SARIMA")
    p("<b>ARIMA(p,d,q)</b> combina autorregressão (AR), integração por diferenças (I) e médias móveis dos erros (MA). O termo MA usa choques passados estimados, não é a média móvel de 12 meses desenhada no histórico.")
    table([["Parâmetro", "Significado"], ["p", "Quantidade de defasagens autorregressivas comuns"],
           ["d", "Número de diferenças comuns"], ["q", "Quantidade de defasagens dos choques comuns"],
           ["P, D, Q", "Equivalentes sazonais, associados a múltiplos de s"], ["s = 12", "Um ciclo anual em uma série mensal"]], [100, width-100])
    p("<b>SARIMA(p,d,q)(P,D,Q)[12]</b> acrescenta a estrutura sazonal. Um termo AR sazonal relaciona a série ao valor de 12 meses atrás; um termo MA sazonal relaciona choques separados por 12 meses.")
    code("phi(B) Phi(B^12) (1-B)^d (1-B^12)^D z[t]\n    = c + theta(B) Theta(B^12) erro[t]")
    p("B é o operador que recua um mês. As letras minúsculas representam polinômios comuns e as maiúsculas os sazonais. O software usa SARIMAX para as duas famílias; sem exógenas, ele implementa ARIMA/SARIMA. Não adicionamos chuva nem um índice sazonal artificial como exógena.")
    p("Com d=D=0, o intercepto não é automaticamente a média da série: a relação depende dos coeficientes AR. As previsões usam a implementação completa, não uma interpretação isolada do intercepto.")

    page("ACF e PACF: pistas, não receitas")
    chart("06_acf_pacf.png", 395)
    p("A ACF mede a associação com valores defasados. A PACF mede a associação em uma defasagem controlando as intermediárias. Barras em 12, 24 e 36 meses ajudam a detectar repetição anual.")
    p("As faixas são referências aproximadas de 95% sob hipóteses estatísticas, não limites absolutos. Várias barras são examinadas ao mesmo tempo. Cortes perfeitos de livros raramente aparecem em uma série hidrológica longa.")
    p("Usamos essas figuras para entender a memória da série e definir uma busca pequena. Não confundimos segunda diferença com q=2, nem usamos ACF/PACF para justificar uma ordem depois de ver o teste.")

    page("Como os parâmetros foram escolhidos")
    p(f"Foram avaliadas {len(busca)} especificações no treino inicial: 18 ARIMA e 28 SARIMA. {int(busca.convergiu.sum())} convergiram. O registro da busca guarda AIC, BIC, especificação, avisos e convergência.")
    table([["Família", "Grade"], ["ARIMA", "p e q em {0,1,2}; d em {0,1}"],
           ["SARIMA", "p,q,P,D,Q em {0,1}; d=0; s=12; exclui P=D=Q=0"]], [100, width-100])
    p("1. Em cada grupo de família e ordens de diferenciação (d,D), selecionamos os dois menores AIC. AIC equilibra ajuste e número de parâmetros; menor é melhor dentro da comparação pertinente.")
    p("2. Cada candidato pré-selecionado é ajustado nas cinco origens de validação. Calculamos RMSE de cada ano e a média aritmética desses cinco RMSE. Isso não é idêntico à raiz de um único MSE agrupado.")
    p("3. Escolhemos a menor média de RMSE em cada família, exigindo convergência nas cinco janelas. As ordens ficam congeladas antes do teste. Depois estimamos novamente os coeficientes até dezembro de 2013.")
    p("<b>Escopo da busca:</b> não é uma busca exaustiva. SARIMA mantém d=0 e compara D=0/1, evitando introduzir dupla diferenciação nesta grade reduzida. Isso não demonstra que todas as alternativas com d=1 são piores.")
    p("Não comparamos os AIC de modelos em escala original e log. A seleção final entre grupos usa erro de previsão na escala original. Modelos com falha numérica são registrados e excluídos, nunca aceitos silenciosamente.")

    page("Modelos selecionados")
    for familia in ["ARIMA", "SARIMA"]:
        spec = r["selecionados"][familia]
        ordem = str(tuple(spec["order"]))
        saz = str(tuple(spec["seasonal_order"])) if familia == "SARIMA" else "sem termos sazonais"
        linha = rank[rank.id == spec["id"]].iloc[0]
        h(f"{familia} {ordem} · {saz}")
        p(f"Identificador auditável: <b>{spec['id']}</b>. RMSE médio da validação: <b>{numero(linha.RMSE)}</b>. MAE médio: {numero(linha.MAE)}. Intercepto: {'incluído' if spec['trend']=='c' else 'não incluído'}.")
    p("A seleção automática pode escolher d=0 ou D=0. Isso não contradiz a sigla ARIMA/SARIMA e não comprova estacionariedade perfeita. As ordens são candidatas empiricamente selecionadas, sujeitas a diagnóstico e teste.")
    table([["Candidato", "RMSE médio de validação"]] + [[row["id"], numero(row["RMSE"])] for _, row in rank.head(6).iterrows()], [width-170, 170])
    p("O notebook mostra a tabela completa. Os resumos de coeficientes ficam em ajuste_arima_teste.txt e ajuste_sarima_teste.txt. Os arquivos com sufixo final correspondem ao reajuste até 2016 para a projeção de 2017.")

    page("ARIMA no teste")
    chart("07_teste_arima.png", 325)
    p(f"O ARIMA apresentou RMSE de <b>{numero(met.loc['ARIMA','RMSE'])}</b>, MAE de {numero(met.loc['ARIMA','MAE'])} e MAPE de {numero(met.loc['ARIMA','MAPE'])}%. A previsão sai de dezembro de 2013 e percorre 36 meses sem receber observações novas.")
    p("A linha escura é o observado. A linha colorida é a média condicional prevista na escala original. A área sombreada é o intervalo nominal de 95% para uma observação mensal futura, condicionado ao modelo e aos parâmetros estimados.")
    p("Conforme o horizonte cresce, o modelo perde informação sobre choques recentes e sua previsão pode suavizar o padrão. A forma exata depende das raízes e ordens estimadas; não se deve exigir que a linha copie cada pico observado.")
    p("<b>Fala sugerida:</b> “O modelo usou apenas o passado até 2013. A diferença entre as linhas mede o erro genuíno de previsão nesse experimento, e a faixa mostra a incerteza que o modelo estima.”")

    page("SARIMA no teste")
    chart("08_teste_sarima.png", 325)
    p(f"O SARIMA apresentou RMSE de <b>{numero(met.loc['SARIMA','RMSE'])}</b>, MAE de {numero(met.loc['SARIMA','MAE'])} e MAPE de {numero(met.loc['SARIMA','MAPE'])}%. Ele inclui repetição de 12 meses, mas isso não garante adaptação a um novo nível de vazão.")
    p("Olhe o desenho do ciclo e também sua altura. Capturar os meses de alta e baixa é diferente de acertar a intensidade. O teste permite avaliar os dois aspectos; uma figura visualmente sazonal pode ainda ter erro elevado.")
    p("As comparações usam a média prevista corrigida da transformação log, o mesmo período e as mesmas observações reais. Assim, uma diferença de desempenho não vem de períodos diferentes de teste.")
    p("Não alteramos as ordens após ver esse gráfico. Qualquer melhoria guiada pelo teste exigiria uma nova amostra futura para avaliação independente.")

    page("Comparação com regras simples")
    chart("09_comparacao_rmse.png", 240)
    table([["Modelo", "RMSE", "MAE", "MAPE (%)", "MASE"]] + [[nome, numero(row.RMSE), numero(row.MAE), numero(row.MAPE), numero(row.MASE,3)] for nome,row in met.iterrows()], [155,85,85,85,width-410])
    p("<b>Ingênuo sazonal:</b> repete os 12 meses de 2013 para todo o teste. <b>Média por mês:</b> usa a média histórica de janeiro, fevereiro etc., calculada somente até 2013. Eles dão referências concretas para julgar a complexidade dos modelos.")
    melhor = met.RMSE.idxmin()
    p(f"<b>Resultado deste experimento:</b> {melhor} teve o menor RMSE, {numero(met.loc[melhor,'RMSE'])}. A conclusão está limitada ao teste de 2014–2016 e à grade avaliada; não prova superioridade universal.")

    page("O que cada métrica quer dizer")
    p("Considere erro = observado − previsto. Métricas menores indicam maior precisão pontual no conjunto avaliado.")
    table([["Métrica", "Cálculo", "Leitura"],
           ["MAE", "média de |erro|", "Erro absoluto típico, na unidade da vazão"],
           ["RMSE", "raiz da média de erro²", "Penaliza erros grandes; critério de seleção"],
           ["MAPE", "100 × média de |erro| / observado", "Erro relativo em porcentagem; cresce em vazões baixas"],
           ["MASE", "MAE / média de |y[t]−y[t−12]| no treino", "Erro escalado pelo erro sazonal histórico"]], [70,205,width-275])
    p("MAPE de 40 significa 40%, e não 0,40%. A métrica não é definida em observações iguais a zero; aqui não há zeros. Vazões baixas aumentam o peso relativo de um erro absoluto, por isso o MAPE pode parecer grande.")
    p("MASE menor que 1 indica erro abaixo da escala sazonal calculada dentro do treino. Não garante que o modelo bateu o ingênuo no teste; para essa afirmação compare diretamente as linhas de RMSE ou MAE.")
    p("O RMSE médio de cinco anos na validação é a média dos cinco RMSE anuais, conforme declarado. No teste calculamos um RMSE único sobre os 36 meses. Essas duas agregações e horizontes devem ser mencionados ao comparar números.")
    p("A cobertura e a largura dos intervalos avaliam outro aspecto: qualidade da incerteza. Um modelo pode ter ponto central impreciso e cobertura alta graças a uma faixa muito larga.")

    page("Intervalos de previsão de 95%")
    p("O enunciado usa “intervalo de confiança”. Para um valor mensal futuro, o termo mais preciso é <b>intervalo de previsão</b>. Ele incorpora a incerteza dos choques futuros sob o modelo; não é o intervalo de um coeficiente como AR(1).")
    code("f = ajuste.get_forecast(steps=36)\nmu = f.predicted_mean + ajuste.centro_log\nv = f.var_pred_mean\nlimites = f.conf_int(alpha=0.05) + ajuste.centro_log\nmedia = np.exp(mu + v / 2)\nmediana = np.exp(mu)\ninferior = np.exp(limites.iloc[:, 0])\nsuperior = np.exp(limites.iloc[:, 1])")
    p("Se log(Y) é normal com média mu e variância v, a mediana de Y é exp(mu), mas a média é exp(mu+v/2). Usamos essa média para RMSE e MAE; salvamos também a mediana. Sem a correção, chamar exp(mu) de média seria incorreto.")
    p("Os limites são transformados pela exponencial, que é monotônica. Isso preserva os quantis do modelo e evita vazão negativa. Não calculamos intervalo simétrico na escala original nem cortamos limites em zero.")
    p("“95%” é o nível nominal de cada horizonte sob as hipóteses do modelo. Não significa que todo o caminho de 36 meses tenha 95% de probabilidade de caber simultaneamente na faixa, nem que 95% das observações deste pequeno teste obrigatoriamente cairão dentro.")
    p("Os intervalos são condicionais aos parâmetros ajustados e à especificação escolhida. Não incluem plenamente a incerteza da seleção do modelo, de possíveis quebras estruturais ou de metadados incorretos. Os diagnósticos abaixo são parte da interpretação.")

    page("Cobertura não basta")
    table([["Modelo", "Dentro da faixa", "Cobertura", "Largura média"]] + [[m, f"{round(met.loc[m,'cobertura_95']*36/100)}/36", f"{numero(met.loc[m,'cobertura_95'])}%", numero(met.loc[m,'largura_media_95'])] for m in ["ARIMA","SARIMA"]], [95,115,105,width-315])
    p("A cobertura conta quantos valores reais ficaram entre os limites. A largura média calcula a média de superior − inferior. Ler as duas juntas ajuda a distinguir um intervalo informativo de uma faixa tão larga que quase tudo cabe.")
    p("Com somente 36 meses correlacionados, não podemos concluir calibração geral a partir de uma proporção isolada. O desempenho pode mudar por estação do ano, horizonte e regime de vazão. Não tratamos os 36 acertos como ensaios independentes.")
    p("As baselines foram usadas apenas para comparação pontual. Não inventamos intervalos de 95% para elas sem especificar e validar um modelo de erro próprio. Por isso as colunas de intervalo dessas linhas ficam vazias.")
    p("<b>Fala sugerida:</b> “A faixa de 95% é uma declaração do modelo. Nós também verificamos a cobertura observada e a largura. Um intervalo largo pode cobrir o real mesmo quando o centro está longe.”")

    page("Resíduos: o que ainda sobra")
    chart("11_residuos_sarima.png", 320)
    table([["Modelo", "p Ljung–Box 12", "p Ljung–Box 24", "p Jarque–Bera"]] + [[m, f"{diag.loc[m,'LB12_p']:.3g}", f"{diag.loc[m,'LB24_p']:.3g}", f"{diag.loc[m,'JB_p']:.3g}"] for m in ["ARIMA","SARIMA"]], [95,135,135,width-365])
    p("O diagnóstico usa inovações padronizadas, descartando os 24 meses iniciais de inicialização. Ljung–Box testa ausência de autocorrelação até a defasagem indicada, com graus de liberdade ajustados pelo número de termos AR/MA. Jarque–Bera verifica normalidade.")
    p("p menor que 0,05 sinaliza rejeição da hipótese nula correspondente. ACF residual relevante indica memória não capturada; caudas no QQ-plot questionam a hipótese normal. Esses sinais impedem apresentar as faixas nominais como garantia de cobertura.")

    page("Projeção histórica para 2017")
    chart("12_previsao_2017.png", 385)
    p("Após encerrar o teste, mantemos as ordens escolhidas e reajustamos os coeficientes usando todos os meses até dezembro de 2016. Projetamos janeiro a dezembro de 2017. Esse reajuste pode mudar as previsões e a largura das faixas.")
    p("O arquivo fornecido não contém 2017. Portanto, aqui há projeção, não avaliação: não é possível calcular RMSE dessa previsão sem observações adicionais. A tabela completa está em previsoes_2017.csv, com média, mediana e limites para cada família.")
    p("<b>Fala sugerida:</b> “Se estivéssemos em dezembro de 2016, estas seriam as projeções condicionais aos modelos. A série não foi atualizada até hoje, então não chamamos isso de previsão atual.”")

    for modelo in ["ARIMA", "SARIMA"]:
        page(f"Previsões de 2017: {modelo}")
        table([["Mês", "Média", "Limite inferior 95%", "Limite superior 95%"]] + [[row["data"][:7], numero(row[f"{modelo}_media"],0), numero(row[f"{modelo}_inferior_95"],0), numero(row[f"{modelo}_superior_95"],0)] for _,row in prev.iterrows()], [75,100,160,width-335])
        p("Unidade assumida: m³/s. Os valores arredondados aqui são apenas para leitura; o CSV preserva a precisão dos cálculos. As medianas estão no CSV e no notebook.")
        p("Cada linha se refere a um mês projetado a partir de dezembro de 2016. Não há observações de 2017 no arquivo para conferir estas previsões. A probabilidade nominal de 95% refere-se a cada horizonte sob o modelo, e não a todas as linhas simultaneamente.")

    page("O que foi seguido e corrigido")
    table([["Referência", "Seguimos", "Correção / adaptação"],
           ["EXEMPLO_01, pp.1–3", "Tabela larga para série mensal", "Não excluir últimas três linhas por posição; validar estrutura real"],
           ["EXEMPLO, pp.1–7", "Série, boxplots, log, ADF e decomposição", "Período sazonal 12; separar treino; acrescentar KPSS"],
           ["EXEMPLO, pp.8–21", "Diferenças, ACF/PACF, ARIMA, resíduos", "d não é q; diagnosticar resíduos além do ajuste visual"],
           ["EXEMPLO, pp.22–29", "Teste, métricas, busca automática", "Intervalo de previsão; datas alinhadas; busca apenas no treino"],
           ["EXEMPLO, pp.30–37", "SARIMA e previsão com faixa", "Não inventar exógenas; comparar no mesmo teste"]], [115,150,width-265])
    p("O primeiro exemplo tem 37 páginas físicas. O segundo contém apenas cinco páginas físicas, apesar dos rodapés indicarem partes de um documento de 20 páginas. Não inferimos o conteúdo ausente.")
    p("As referências usam Sobradinho; os números e ordens daqueles exemplos não foram transferidos para Ilha Solteira. Usamos statsmodels atual e busca transparente em grade, cumprindo o objetivo de seleção que o exemplo realiza com auto_arima.")
    p("O documento docs/como_seguimos_os_exemplos.md apresenta o mapeamento por páginas. O notebook detalha onde cada etapa entra nesta análise.")

    page("Código: dados e estimação")
    table([["Função / arquivo", "Entradas, operação e saída"],
           ["extrair_pdf()\nsrc/dados.py", "Recebe o PDF; lê os pares de páginas; valida 1.032 meses; retorna DataFrame com rastreabilidade"],
           ["salvar_dados()", "Salva CSV e metadados com hash da fonte; não altera valores"],
           ["carregar_serie()", "Lê datas e valores do CSV, converte para float e define frequência MS"],
           ["especificacoes()\nsrc/modelos.py", "Gera a grade declarada, incluindo ordem, sazonalidade, intercepto e ID"],
           ["ajustar(serie, spec)", "Calcula log e centro somente da série recebida; estima por máxima verossimilhança; exige convergência e AIC finito"],
           ["prever(ajuste, passos)", "Obtém distribuição preditiva, desfaz centro e log; retorna média, mediana, inferior_95 e superior_95"]], [160,width-160])
    p("<b>Máxima verossimilhança:</b> o ajuste procura parâmetros que tornem a sequência observada plausível sob o modelo. O filtro de Kalman calcula as previsões internas e erros usados na verossimilhança.")
    p("enforce_stationarity e enforce_invertibility restringem parâmetros AR/MA admissíveis. Isso não demonstra que a série histórica seja estacionária: são restrições da parametrização. maxiter=250 limita iterações; avisos são capturados e salvos, e falhas não são usadas como resultado.")

    page("Código: seleção e avaliação")
    table([["Função", "Responsabilidade"], ["testar_estacionariedade()", "Calcula ADF e KPSS na série original, log e duas diferenças; salva avisos e p-valores"],
           ["selecionar()", "Faz busca até 2008, AIC por grupo, validação anual até 2013 e escolha por família"],
           ["metricas()", "Converte valores para arrays alinhados; calcula RMSE, MAE, MAPE e MASE"],
           ["avaliar_e_prever()", "Estima até 2013, prevê 36 meses, calcula cobertura/resíduos/baselines; reajusta até 2016 e projeta 2017"],
           ["salvar_resumo()", "Consolida estatísticas e resultados em JSON para documentação e slides"],
           ["gerar_graficos()\nsrc/graficos.py", "Lê a mesma série e as mesmas tabelas; exporta gráficos PNG/SVG com rótulos consistentes"]], [165,width-165])
    p("scripts/analisar.py coordena a análise. O notebook executa as etapas didáticas e pode repetir a busca usando sua configuração REFAZER_BUSCA. A opção rápida reutiliza as ordens salvas e refaz os ajustes e previsões; ela não inventa novas saídas.")
    p("scripts/criar_roteiro.py lê o JSON e CSV para gerar este PDF. scripts/criar_slides.mjs usa os resultados para a apresentação. Separar cálculo de apresentação evita transcrever manualmente números e facilita atualizar os materiais juntos.")
    p("As explicações célula a célula estão no notebook. Os comentários do código documentam decisões e transformação dos dados; a lógica executável fica em funções pequenas para permitir inspeção e reprodução.")

    page("Como executar no seu computador")
    code("python3 -m venv .venv\nsource .venv/bin/activate\npython -m pip install -r requirements-lock.txt\npython -m ipykernel install --user --name ilha-solteira\npython scripts/analisar.py\npython -m src.graficos\npython scripts/criar_roteiro.py\npython scripts/verificar.py")
    p("As versões usadas nesta execução estão em requirements-lock.txt. requirements.txt registra faixas de versões diretas. Usamos Python 3.12; uma versão compatível e o ambiente virtual evitam misturar dependências de projetos diferentes.")
    h("No Zed")
    p("Abra a pasta e notebooks/ilha_solteira.py. Selecione o kernel Python (Ilha Solteira). Use <b>Ctrl+Shift+Enter</b> para executar a célula # %% atual. Se o kernel não aparecer, use o comando repl: refresh kernelspecs. A seleção de toolchain e a seleção de kernel são controles distintos.")
    h("No JupyterLab")
    code("python -m jupyterlab notebooks/ilha_solteira.ipynb")
    p("Execute as células de cima para baixo. Não use um resultado de uma célula antiga após mudar parâmetros sem executar as dependências anteriores. Para repetir toda a seleção, ative a opção indicada no notebook ou rode scripts/analisar.py.")
    p("O README traz o comando e os requisitos separados para regenerar os slides. Os arquivos PPTX e PDF finais já estão prontos para abrir e apresentar.")

    page("Roteiro para 15–20 minutos")
    table([["Tempo", "Assunto", "Mensagem principal"],
           ["0–2 min", "Problema e dados", "Queremos prever vazão mensal; temos 1931–2016 e limitações de metadados"],
           ["2–5 min", "Histórico e sazonalidade", "Há repetição anual e variação entre anos"],
           ["5–8 min", "ARIMA/SARIMA e preparo", "Log, diferenças e termos sazonais têm funções distintas"],
           ["8–11 min", "Protocolo e seleção", "O teste ficou fora da escolha; ordens vieram da validação"],
           ["11–15 min", "Teste e incerteza", "Comparar números, baselines, faixas e resíduos"],
           ["15–18 min", "Projeção e conclusão", "2017 é histórico; sintetizar alcance e limitações"],
           ["18–20 min", "Perguntas", "Justificar decisões e localizar evidências no notebook"]], [85,145,width-230])
    p("Abertura sugerida: “Nosso grupo analisou as vazões médias mensais de Ilha Solteira. Vamos mostrar como transformamos a tabela em uma série, como comparamos ARIMA e SARIMA e o que o teste nos diz sobre precisão e incerteza.”")
    p("Ao apresentar cada gráfico, siga três passos: nomeie os eixos, indique a comparação e diga a conclusão sustentada. Evite ler a legenda inteira. No gráfico do teste, a primeira frase deve esclarecer que o modelo não conhecia os valores de 2014–2016.")
    p("As notas do apresentador no PPTX e docs/roteiro_slides.md trazem a fala por slide. Use-as para ensaiar; os slides mantêm apenas o necessário para a audiência acompanhar.")

    page("Perguntas que você deve saber responder")
    perguntas = [
        ("Por que SARIMA?", "Porque há padrão anual em dados mensais. SARIMA representa dependência sazonal explicitamente; sua utilidade é verificada, não presumida."),
        ("Por que usar log?", "Para trabalhar com variações relativas, reduzir assimetria e obter limites positivos. É uma hipótese de modelagem; os resíduos mostram seus limites."),
        ("O 95% garante a previsão?", "Não. É um nível nominal por horizonte sob o modelo, condicionado aos parâmetros. A cobertura observada e os diagnósticos precisam ser analisados."),
        ("Por que não usaram todos os dados para escolher?", "Porque medir erro nos dados usados para escolher favorece o modelo. A escolha usa o passado; o teste mede generalização."),
        ("d=0 significa que não é ARIMA?", "Não. ARIMA permite d=0. O modelo vira ARMA na parte comum, mas permanece um caso válido da família."),
        ("O modelo mais complexo deve vencer?", "Não. Baselines podem superar modelos em determinados períodos. A comparação é parte do resultado científico."),
        ("Vocês previram as vazões de hoje?", "Não. A fonte termina em 2016 e a projeção é para 2017. Seria preciso atualizar a série e repetir a avaliação para falar do presente.")]
    for pergunta, resposta in perguntas:
        h(pergunta)
        p(resposta)

    page("Conclusão e limites")
    melhor = met.RMSE.idxmin()
    p(f"<b>Precisão:</b> no teste fixo de 2014–2016, {melhor} obteve o menor RMSE. O resultado vale para esta amostra, horizonte e grade de candidatos. O notebook documenta ARIMA e SARIMA mesmo quando uma referência simples é mais precisa.")
    p("<b>Incerteza:</b> ambos os modelos produzem intervalos nominais de 95%. A largura, a cobertura observada e os testes de resíduos mostram por que não se deve tratar a faixa como garantia hidrológica.")
    p("<b>Dados:</b> a frequência foi verificada e todos os valores foram preservados. A fonte não explicita unidade, agência ou tipo de vazão; não é possível resolver essas lacunas apenas olhando os números.")
    p("<b>Modelagem:</b> o lognormal é uma aproximação; a grade é reduzida; o período de treino é longo; a validação usa 12 meses e o teste 36. A análise não incorpora chuva, operação de reservatórios ou mudanças estruturais explicitamente.")
    p("<b>Se o trabalho continuar:</b> confirmar metadados, obter anos posteriores, alinhar horizontes de validação e aplicação, testar janelas mais recentes e modelos com exógenas conhecidas no momento da previsão. Essas são extensões, não resultados já obtidos.")
    p("Encerramento sugerido: “A contribuição do projeto não é só gerar uma curva. É mostrar de onde os dados vieram, como a avaliação foi feita e quanta confiança os resultados permitem. O histórico tem sazonalidade, mas prever a intensidade de cada ciclo continua sendo o desafio.”")

    page("Fontes e onde conferir cada resultado")
    p("<b>Dados:</b> ILHA_SOLTEIRA.pdf, quatro páginas, fornecido pelo grupo; cópia em data/raw. <b>Exemplos:</b> EXEMPLO.pdf (37 páginas) e EXEMPLO_01.pdf (cinco páginas físicas), cópias em referencias.")
    fontes = [
        ("Tutorial indicado: DigitalOcean", "https://www.digitalocean.com/community/tutorials/a-guide-to-time-series-forecasting-with-arima-in-python-3"),
        ("Tutorial indicado: GeeksforGeeks", "https://www.geeksforgeeks.org/python-arima-model-for-time-series-forecasting/amp/"),
        ("Notebook indicado: AirPassenger", "https://github.com/aarshayj/analytics_vidhya/blob/master/Articles/Time_Series_Analysis/Time_Series_AirPassenger.ipynb"),
        ("statsmodels: SARIMAX", "https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html"),
        ("statsmodels: get_forecast", "https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.mlemodel.MLEResults.get_forecast.html"),
        ("Zed: REPL e kernels", "https://zed.dev/docs/repl")]
    for nome, url in fontes:
        p(f'<link href="{escape(url)}" color="#137F83">{escape(nome)}</link>')
    p("Na consulta, os links DigitalOcean e GeeksforGeeks não forneceram o texto integral do tutorial. As decisões de implementação foram conferidas na documentação oficial do statsmodels e nos PDFs anexados. Os links indicados permanecem registrados para consulta.")
    table([["Arquivo", "Conteúdo"], ["output/resumo.json", "Resultados consolidados para documentação"],
           ["output/tables/busca_modelos.csv", "Todos os candidatos e avisos"], ["output/tables/validacao_rolling.csv", "Cada modelo em cada origem de validação"],
           ["output/tables/previsoes_teste.csv", "Observados, previsões e intervalos do teste"],
           ["output/tables/diagnosticos.csv", "Testes de resíduos"], ["output/tables/previsoes_2017.csv", "Projeção histórica de 12 meses"]], [265,width-265])

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#137F83"))
        canvas.rect(0, A4[1]-10, A4[0], 10, fill=1, stroke=0)
        canvas.setFont("Texto", 8)
        canvas.setFillColor(colors.HexColor("#526C76"))
        canvas.drawString(50, 27, "ILHA SOLTEIRA  /  GUIA DE ESTUDO")
        canvas.drawRightString(A4[0]-50, 27, str(doc.page))
        canvas.restoreState()

    destino = ROOT / "output/pdf/roteiro_ilha_solteira.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(destino), pagesize=A4, rightMargin=50, leftMargin=50,
                            topMargin=45, bottomMargin=50, title="Ilha Solteira - guia de estudo e apresentação",
                            author="Projeto Modelagem Analítica", pageCompression=1)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(destino)


if __name__ == "__main__":
    criar_roteiro()
