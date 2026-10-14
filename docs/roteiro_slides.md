# Roteiro da apresentação

16 slides. Tempo sugerido de fala: 18 minutos e 10 segundos, com margem para transições até 20 minutos. As notas também estão no PPTX.

## 1. Ilha Solteira e o rio Paraná

Tempo: 85 segundos. Comece pelo mapa: ele destaca Ilha Solteira no noroeste do estado de São Paulo e mostra a posição do estado no Brasil em um detalhe. Logo abaixo, a fotografia aérea apresenta a cidade. As duas imagens foram fornecidas pelo grupo em 14/10/2026 e são exibidas integralmente, sem recorte. A fotografia contém a marca Ilha News, preservada no slide. Autoria original, data e licença não foram informadas nos anexos. Passe ao gráfico à direita: cada coluna reúne a média daquele mês nos 86 anos da série. Fevereiro tem a maior média e setembro a menor. Essa sazonalidade motiva considerar um ciclo de 12 meses. O gráfico descreve a base completa e não participa da seleção de parâmetros. A unidade e a natureza da vazão não foram informadas no PDF. Faça a transição para o próximo slide: agora vamos conhecer a base recebida pelo grupo. Fontes: imagens fornecidas pelo grupo, salvas em assets/fotos/mapa_ilha_solteira.png e assets/fotos/vista_aerea_ilha_solteira.png; data/processed/ilha_solteira_mensal.csv.

## 2. A base de dados em um olhar

Tempo: 85 segundos. Apresente os três números do topo: 1.032 observações, 86 anos de janeiro de 1931 a dezembro de 2016 e frequência de 12 valores por ano. Cada valor representa uma vazão média mensal. A fonte recebida é ILHA_SOLTEIRA.pdf. No documento, os anos e os meses estão organizados em uma tabela anual distribuída pelas páginas. A extração organiza uma linha por mês. O CSV tem as colunas data, vazao, pagina_pdf e linha_tabela, permitindo rastrear cada observação até sua origem. O índice é mensal, sem lacunas ou duplicatas, e todos os valores são positivos. Não foi necessário preencher meses ausentes. Explique o painel de estatísticas da série completa: média 5.271,65, mediana 4.194 e desvio padrão amostral 3.095,16. Os valores foram arredondados no slide para facilitar a leitura. O mínimo é 1.212 em outubro de 2014 e o máximo é 20.314 em fevereiro de 1983. As estatísticas descrevem a base e não são usadas para escolher parâmetros com os dados de teste. A fonte não explicita a unidade nem se a vazão é natural, afluente ou defluente. Não confirme m³/s sem outra documentação. A base termina em 2016 e não fornece observações de 2017. Fontes: data/raw/ILHA_SOLTEIRA.pdf, data/processed/ilha_solteira_mensal.csv, data/processed/metadados.json e output/resumo.json. Conferência independente dos valores e da regularidade: scripts/verificar.py.

## 3. A série combina sazonalidade e extremos

Tempo: 55 segundos. Mostre que o ciclo anual convive com picos e períodos de valores menores. O gráfico preserva todos os 1032 meses, sem agregação. A escala vertical mantém a unidade original da tabela, que não está especificada no PDF. O máximo e o mínimo são apenas descrições, sem atribuir causas. Fonte: data/processed/ilha_solteira_mensal.csv, extraído de ILHA_SOLTEIRA.pdf.

## 4. A avaliação respeita a ordem do tempo

Tempo: 75 segundos. No treino inicial, estimamos candidatos até 2008. Na validação, usamos cinco origens anuais e prevemos os próximos 12 meses de 2009 a 2013, expandindo o histórico. Depois fixamos um modelo de cada família. O teste usa uma única origem em dezembro de 2013 e 36 meses à frente. Assim nenhum valor de 2014–2016 escolhe parâmetros. O horizonte de teste é maior que o de validação. Fonte: src/modelos.py, selecionar e avaliar_e_prever.

## 5. ARIMA e SARIMA

Tempo: 70 segundos. AR representa dependência de valores passados, I representa diferenças e MA representa erros passados. SARIMA acrescenta dependência sazonal. p e q controlam ordens não sazonais, d as diferenças. P, D e Q são os equivalentes sazonais. O 12 corresponde ao ciclo anual. A constante aparece nos dois modelos selecionados. Fonte: statsmodels.tsa.statespace.sarimax.SARIMAX e src/modelos.py.

## 6. Logaritmo, diferenças e estacionariedade

Tempo: 75 segundos. Ajustamos log da vazão porque todos os valores são positivos. Isso reduz assimetria e permite intervalos positivos após exponenciar. Subtraímos a média do log calculada apenas no histórico de cada ajuste para melhorar a estabilidade numérica, e somamos esse centro antes de voltar à escala original. Diferença de ordem 1 compara meses consecutivos. Diferença sazonal compara o mês ao mesmo mês do ano anterior. No treino, ADF rejeita raiz unitária, mas KPSS rejeita estacionariedade em nível e log. Esse desacordo exige cautela. Comparamos d igual a zero ou um no ARIMA. No SARIMA, fixamos d=0 e comparamos D igual a zero ou um. A validação escolheu zero nas diferenças dos dois modelos. Fonte: output/tables/estacionariedade.csv e src/modelos.py.

## 7. Seleção dentro de cada família

Tempo: 65 segundos. AIC faz uma triagem dentro de grupos com a mesma família e as mesmas diferenças d e D. Os dois melhores convergentes de cada grupo seguem para validação. O RMSE médio das cinco origens escolhe um por família. O SARIMA ganha na validação, mas ainda precisa enfrentar o teste reservado. Fonte: output/tables/busca_modelos.csv e ranking_validacao.csv.

## 8. O ingênuo sazonal tem o menor erro no teste

Tempo: 70 segundos. Menor RMSE é melhor, e a medida penaliza erros grandes. O ingênuo sazonal repete os últimos 12 meses disponíveis, de 2013, para os três anos do teste. A média por mês usa todo o histórico até 2013. Ambos superam os modelos nesta janela. Isso impede concluir que maior complexidade produziu melhor previsão. Fonte: output/tables/metricas_teste.csv.

## 9. As previsões centrais superestimam parte do teste

Tempo: 70 segundos. A linha escura mostra os 36 valores observados. Compare a oscilação sazonal do SARIMA à trajetória do ARIMA. Durante parte do teste, os valores previstos ficam acima dos observados. A média do teste é menor que a média do período de ajuste. Isso é uma descrição, não uma prova de mudança estrutural ou causa climática. Fonte: output/tables/previsoes_teste.csv e output/resumo.json.

## 10. Intervalos preditivos de 95%: ARIMA

Tempo: 60 segundos. Os limites representam quantis condicionais do modelo para cada mês, e não garantem cobertura de toda a trajetória. A linha central é a média com correção de viés ao voltar do log: exp(mu + variância/2). A mediana seria exp(mu). Os limites vêm de exp dos limites no log. A largura na escala original depende também do nível previsto. Fonte: output/tables/previsoes_teste.csv. Fórmulas: src/modelos.py, prever.

## 11. Intervalos preditivos de 95%: SARIMA

Tempo: 60 segundos. A sazonalidade também altera os limites do SARIMA. Compare a faixa nos meses de valores altos. Uma faixa larga pode cobrir observações mesmo com previsão central ruim. Por isso lemos cobertura junto com a largura e o erro. Fonte: output/tables/previsoes_teste.csv.

## 12. A cobertura observada fica abaixo de 95%

Tempo: 65 segundos. O ARIMA cobriu 91,7% dos meses e o SARIMA cobriu 83,3%. O nominal é 95%, mas 36 observações são poucas e dependentes. Não afirmamos calibração apenas por esse número. A largura média foi maior no ARIMA. Não há intervalo calculado para as baselines neste projeto. Fonte: output/tables/metricas_teste.csv.

## 13. Os resíduos ainda contêm dependência

Tempo: 70 segundos. Ljung–Box verifica se resta autocorrelação conjunta. Os p-valores abaixo de 0,05 em 12 e 24 defasagens rejeitam a hipótese de ausência dessa dependência nos dois modelos. Jarque–Bera também rejeita normalidade nos dois. Esses resultados limitam a confiança nos intervalos paramétricos. Não escondemos os diagnósticos desfavoráveis. Fonte: output/tables/diagnosticos.csv.

## 14. Projeção histórica para 2017

Tempo: 75 segundos. Depois de medir o desempenho, reajustamos as estruturas selecionadas usando todos os dados até dezembro de 2016. O gráfico mostra SARIMA com seus limites e a média ARIMA para comparação. Os valores observados de 2017 não estão no arquivo. Portanto, esta é uma projeção histórica sem avaliação externa e nunca deve ser apresentada como previsão atual. Fonte: output/tables/previsoes_2017.csv.

## 15. O que os resultados permitem concluir

Tempo: 70 segundos. Resuma com transparência. Há sazonalidade anual, mas isso não garante que o SARIMA escolhido seja o melhor em qualquer período. A validação favoreceu SARIMA e o teste favoreceu o ingênuo sazonal. Os resíduos mostram inadequação dos modelos e os intervalos são largos. Melhorias futuras incluem validação com horizontes comparáveis e modelos com covariáveis, desde que dados adicionais existam. Fontes: métricas, diagnósticos e ranking em output/tables.

## 16. Código, exemplos e referências

Tempo: 40 segundos. Apresente o notebook como caminho para reproduzir cada etapa. A estrutura seguiu os dois PDFs de exemplos e a API oficial do statsmodels. Os três tutoriais fornecidos são referências indicadas. O conteúdo integral de DigitalOcean e GeeksforGeeks estava indisponível na consulta. Foram corrigidos o período sazonal, a separação temporal, a distinção de intervalos e chamadas antigas. URLs: https://www.digitalocean.com/community/tutorials/a-guide-to-time-series-forecasting-with-arima-in-python-3 ; https://www.geeksforgeeks.org/python-arima-model-for-time-series-forecasting/amp/ ; https://github.com/aarshayj/analytics_vidhya/blob/master/Articles/Time_Series_Analysis/Time_Series_AirPassenger.ipynb ; https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html ; https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAXResults.get_forecast.html . Fonte de dados: ILHA_SOLTEIRA.pdf.
