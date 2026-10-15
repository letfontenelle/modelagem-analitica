# Roteiro de apresentação e guia de estudo

Guia dos 13 slides. “O que falar” é a fala curta; “Como interpretar” orienta a leitura do slide; os demais blocos explicam o que você precisa entender e ajudam a responder ao professor. Não é necessário ler todas as explicações durante a apresentação de 15-20 minutos.

## 1. Ilha Solteira e o rio Paraná

**O que falar:** “Nosso grupo estudou as vazões médias mensais de Ilha Solteira, no rio Paraná. O mapa localiza a cidade no noroeste de São Paulo, e a foto mostra a região urbana. Queremos comparar as previsões de ARIMA e SARIMA para essa série.”

**Como interpretar:** Cada barra é a média de um mês do ano entre 1931 e 2016. Fevereiro tem a maior média e setembro, a menor. Esse padrão indica sazonalidade anual; não significa que todos os anos sejam iguais.

**Para entender - série e sazonalidade:** Uma série temporal é uma sequência de valores em ordem de data. Sazonalidade é um padrão que tende a se repetir em intervalos regulares. Aqui, 12 observações correspondem a um ano; por isso o ciclo sazonal usado foi 12. O gráfico de médias mensais mostra o padrão típico, mas esconde a variação entre anos.

## 2. A base de dados em um olhar

**O que falar:** “Recebemos uma tabela em PDF com 1.032 observações mensais, de 1931 a 2016: são 86 anos. Organizamos os dados por data e conferimos os valores. Não encontramos meses ausentes nem duplicados, e não foi necessário preencher dados.”

**Como interpretar:** Os cartões resumem a base. A média é aproximadamente 5.272 e a mediana, 4.194; valores altos puxam a média para cima. Os números mantêm a escala da tabela original, cuja unidade não foi informada.

**Para entender - estatísticas da base:** A média soma os valores e divide pela quantidade. A mediana é o valor central depois de ordenar a amostra. O desvio padrão resume quanto os valores se espalham em torno da média; ele não é um erro de previsão. Vazão média mensal é a média da vazão de um mês, não o volume total de água desse mês.

## 3. Sazonalidade e extremos na série

**O que falar:** “O histórico mostra que as vazões oscilam ao longo dos anos. Existe um padrão sazonal, mas a intensidade dos picos varia bastante. Mantivemos todos os valores, inclusive os extremos.”

**Como interpretar:** No eixo horizontal estão as datas; no vertical, as vazões. Cada ponto corresponde a um mês. O maior valor foi 20.314, em fevereiro de 1983, e o menor, 1.212, em outubro de 2014. O gráfico descreve essas variações, sem identificar suas causas.

**Se perguntarem sobre os extremos:** Um valor muito alto ou baixo não é automaticamente um erro. Os valores foram conferidos com a tabela original e preservados. Sem dados adicionais de chuva ou operação da usina, não podemos atribuir uma causa aos picos ou às quedas.

## 4. Como os resultados foram avaliados

**O que falar:** “Respeitamos a ordem do tempo. Usamos os dados até 2008 no treino inicial, 2009 a 2013 para escolher os modelos e 2014 a 2016 para o teste final. Os dados do teste não participaram da escolha.”

**Como interpretar:** Os três blocos mostram etapas diferentes. Na validação, previmos 12 meses por vez, ampliando o histórico a cada ano. No teste, previmos os 36 meses de uma vez. Por isso, os erros dessas duas etapas não são diretamente comparáveis.

**Para entender - treino, validação e teste:** Treino serve para estimar o modelo; validação serve para escolher a configuração; teste serve para avaliar a escolha em dados que ficaram reservados. Exemplo: para prever 2009, usamos o histórico até 2008; para prever 2010, até 2009. Esse processo se repete até 2013. No teste, usamos somente o histórico até 2013 e prevemos 2014-2016 sem atualizar o modelo com os valores desses anos.

**Por que não misturar as datas?** Porque isso permitiria usar informações do futuro para prever o passado. Essa utilização indevida é chamada vazamento de informação e produziria uma avaliação pouco realista.

## 5. Os modelos escolhidos na validação

**O que falar:** “Comparamos diferentes configurações e selecionamos uma de cada família. O ARIMA escolhido foi (2,0,2), e o SARIMA foi (1,0,0)(1,0,1), com ciclo de 12 meses. Entre os dois, o SARIMA teve menor erro na validação.”

**Como interpretar:** Os cartões mostram RMSE de aproximadamente 1.700 para ARIMA e 1.567 para SARIMA. RMSE resume o erro e dá mais peso a erros grandes: quanto menor, melhor. Esse resultado ainda precisava ser confirmado no teste reservado.

**Como chegamos a essas configurações:** Definimos uma busca limitada de 46 candidatos e os ajustamos até 2008. Entre os que convergiram, os dois menores AIC de cada grupo com a mesma família e as mesmas ordens de diferenciação seguiram para validação. Escolhemos o menor RMSE médio dos cinco anos, entre candidatos com ajustes válidos em todas as janelas. Portanto, são os melhores nessa seleção, não entre todas as configurações possíveis.

**AIC - Critério de Informação de Akaike:** Equilibra a qualidade do ajuste e a quantidade de parâmetros. Um modelo mais complexo recebe uma penalização e precisa melhorar o ajuste para compensá-la. Menor AIC é preferível entre modelos comparáveis. Ele não é porcentagem nem erro de previsão; pode até ser negativo. No projeto, serviu como filtro inicial, não como decisão final.

**O que significam p, d e q?** p indica a ordem dos termos que usam valores anteriores; d, quantas diferenciações são aplicadas; q, a ordem dos termos ligados aos erros anteriores. Diferenciar uma vez é calcular a diferença entre um valor e o anterior. Em (2,0,2), usamos duas defasagens autorregressivas, nenhuma diferenciação e duas defasagens dos erros. Não significa que o modelo foi treinado com apenas dois meses.

**E a parte sazonal do SARIMA?** As letras P, D e Q representam as ordens equivalentes no ciclo anual. Em (1,0,0) × (1,0,1)₁₂, há um termo autorregressivo mensal e, na parte sazonal, um autorregressivo e um de erros, sem diferenciação sazonal. O 12 indica o ciclo anual. d e D iguais a zero não significam ausência de sazonalidade nem provam que a série é estacionária.

**Se perguntarem sobre a transformação:** Os modelos foram ajustados no logaritmo da vazão, para trabalhar com variações relativas e reduzir o peso de diferenças de escala. As previsões foram convertidas de volta à escala original antes de calcular os erros. Os números entre parênteses definem a estrutura; os coeficientes dessa estrutura são estimados com os dados.

## 6. No teste, o ingênuo sazonal vence

**O que falar:** “No teste, também comparamos os modelos com duas referências simples: repetir o último ano e usar a média histórica de cada mês. A repetição do último ano, chamada ingênuo sazonal, teve o menor erro.”

**Como interpretar:** Quanto menor a barra, melhor. O RMSE foi cerca de 2.013 no ingênuo sazonal, 2.215 na média por mês, 2.234 no SARIMA e 2.390 no ARIMA. O SARIMA superou o ARIMA, mas as duas referências simples foram melhores nessa janela.

**RMSE - Raiz do Erro Quadrático Médio:** Calculamos a diferença entre cada valor previsto e o real, elevamos os erros ao quadrado, fazemos a média e tiramos a raiz. Erros grandes pesam mais. O resultado está na mesma unidade da vazão e não é uma porcentagem. Exemplo ilustrativo: erros de 100 e 300 geram RMSE de aproximadamente 224. Isso não quer dizer que cada previsão errou exatamente 224.

**AIC e RMSE no nosso projeto:** AIC filtrou candidatos pelo ajuste e pela complexidade; RMSE decidiu a seleção pelo desempenho na validação. Os valores 1.700 e 1.567 do slide anterior são médias dos RMSEs dos cinco anos de validação, arredondadas. Aqui, o RMSE é calculado sobre os 36 meses do teste. Compare modelos dentro da mesma etapa.

**O que é o ingênuo sazonal?** Ele repete os valores de 2013 para cada ano do teste: janeiro de 2013 vira a previsão de janeiro de 2014, 2015 e 2016, e assim por diante. Já a média por mês usa todos os janeiros disponíveis até 2013 para prever janeiro. São referências simples para verificar se a complexidade dos modelos trouxe ganho.

## 7. As previsões superestimam parte do teste

**O que falar:** “Comparando as previsões com o que realmente aconteceu, vemos que os modelos estimaram vazões acima das observadas em parte do teste. O SARIMA reproduz melhor a oscilação sazonal, mas também erra o nível dos valores.”

**Como interpretar:** Acompanhe a legenda e compare, no mesmo mês, a linha observada com cada previsão. Quanto maior a distância, maior o erro. A média do teste foi 3.773, abaixo dos 5.326 do histórico até 2013. Isso descreve o período, sem explicar a causa da queda.

**Para entender - superestimação:** Se o observado é 3.000 e a previsão é 5.000, o modelo superestima em 2.000. Se prevê 2.000, subestima em 1.000. O RMSE mede o tamanho dos erros, mas não mostra sua direção. O gráfico permite enxergar quando as previsões ficam acima ou abaixo do observado.

## 8. ARIMA: intervalos preditivos de 95%

**O que falar:** “Além de um valor previsto, calculamos limites para representar a incerteza. No ARIMA, 33 dos 36 meses ficaram dentro desses limites: uma cobertura observada de 91,7%.”

**Como interpretar:** Compare a linha observada com os limites inferior e superior em cada mês. Entre eles, o valor foi coberto; fora deles, não. Os limites são largos: conter o valor observado não significa que a previsão central ficou próxima. O nível de 95% é nominal, não uma garantia.

**Para entender - previsão central e intervalo:** A previsão central é um único valor estimado. O intervalo apresenta um limite inferior e um superior para um valor futuro. O nível nominal de 95% é a cobertura pretendida pelo método sob as hipóteses do modelo, não uma garantia de acerto em 95% dos 36 meses. Cada intervalo vale para um mês; não significa 95% de chance de toda a trajetória ficar dentro dos limites.

**Por que chamamos de intervalo preditivo?** Porque queremos representar a incerteza da vazão futura. Um intervalo de confiança de um coeficiente descreve a incerteza sobre um parâmetro do modelo e não pode substituí-lo.

## 9. SARIMA: intervalos preditivos de 95%

**O que falar:** “No SARIMA, as previsões e seus limites acompanham o ciclo sazonal. Porém, apenas 30 dos 36 meses ficaram dentro dos intervalos, uma cobertura de 83,3%.”

**Como interpretar:** Observe como a distância entre os limites varia ao longo dos meses. Depois, procure os valores observados que ficaram fora deles. O SARIMA teve menor erro central que o ARIMA, mas seus intervalos cobriram menos meses.

**Se perguntarem qual modelo é melhor:** Depende do aspecto avaliado nesta janela. O SARIMA teve menor RMSE que o ARIMA, ou seja, menor erro da previsão central segundo essa medida. O ARIMA teve maior cobertura dos intervalos, mas também limites mais largos. São resultados diferentes, que precisam ser apresentados juntos.

## 10. A cobertura ficou abaixo dos 95% nominais

**O que falar:** “Este slide reúne a comparação dos intervalos. O ARIMA cobriu mais meses, mas apresentou intervalos mais largos. O SARIMA teve intervalos mais estreitos e menor cobertura. Nenhum atingiu 95% neste teste.”

**Como interpretar:** Leia cobertura e largura juntas: ARIMA, 91,7% e largura média de 10.908; SARIMA, 83,3% e 6.026. Cobertura maior, sozinha, não torna a previsão mais precisa. São apenas 36 meses de avaliação, portanto a conclusão vale para esta janela.

**Como calcular cobertura e largura:** Cobertura é o número de observações dentro dos limites dividido pelo total: 33/36 × 100 = 91,7% no ARIMA; 30/36 × 100 = 83,3% no SARIMA. A largura de cada intervalo é o limite superior menos o inferior; depois fazemos a média das larguras. Por exemplo, um intervalo de 2.000 a 8.000 tem largura 6.000.

**O que isso permite concluir?** Os intervalos cobriram menos de 95% dos meses neste teste. Só essa contagem, com 36 meses dependentes, não basta para provar que o método sempre terá cobertura inferior a 95%. Intervalos muito largos podem cobrir muitos valores e ainda ser pouco úteis para decisões.

## 11. Os diagnósticos mostram limites dos modelos

**O que falar:** “Também analisamos os resíduos, que são os erros que sobraram após o ajuste. Nos dois modelos, ainda encontramos padrões nesses erros e rejeitamos a hipótese de normalidade. Isso mostra que o ajuste tem limitações.”

**Como interpretar:** Os valores de p abaixo de 0,05 indicam dependência restante no teste Ljung-Box e rejeição da normalidade no Jarque-Bera. A mensagem principal é que os modelos não explicaram toda a estrutura da série, o que pede cautela ao interpretar seus intervalos.

**Para entender - resíduos e testes:** Os diagnósticos analisam os resíduos padronizados do ajuste; eles são diferentes dos erros das previsões de 36 meses do teste. O Ljung-Box procura dependência entre resíduos ao longo do tempo. Aqui, rejeitou a ausência dessa dependência em 12 e 24 defasagens. O Jarque-Bera avalia compatibilidade com uma distribuição normal, a conhecida curva em sino; também houve rejeição.

**O que significa p < 0,05?** Sob a hipótese testada, um resultado tão extremo ou mais seria pouco provável. Usamos 0,05 como limite para rejeitar essa hipótese. Não significa “95% de chance de o modelo estar errado”. A conclusão prática é que restaram padrões e que as hipóteses dos intervalos merecem cautela.

## 12. O que os modelos projetaram para 2017

**O que falar:** “Depois da avaliação, reajustamos os modelos escolhidos com todos os dados até 2016 e projetamos os 12 meses de 2017. Essa é uma projeção histórica, pois a base termina em 2016.”

**Como interpretar:** O gráfico compara as médias previstas por ARIMA e SARIMA; os limites de 95% mostrados são os do SARIMA. Há valores maiores no começo e no fim do ano e menores no meio. Não temos os valores reais de 2017 na base para avaliar o acerto dessas projeções.

**Por que reajustar?** Depois de encerrar a avaliação, podemos usar o histórico completo para projetar o próximo ano disponível. Mantivemos as configurações escolhidas e reestimamos seus coeficientes com dados até 2016. Isso não altera os resultados do teste, que foram calculados separadamente usando apenas dados até 2013.

## 13. O que os resultados mostram

**O que falar:** “Concluímos que a série tem sazonalidade anual. O SARIMA foi melhor que o ARIMA, mas repetir o último ano foi a melhor alternativa no teste. Os intervalos e os diagnósticos mostram que ainda existe bastante incerteza.”

**Como interpretar:** Use os três cartões para encerrar: identificamos um padrão nos dados, comparamos o desempenho fora do treino e avaliamos a incerteza. A principal conclusão é que um modelo mais complexo não garantiu a melhor previsão neste caso.

**Se perguntarem por que o SARIMA não venceu no teste:** Capturar a sazonalidade não garante acertar o nível das vazões. O teste teve valores menores que o histórico e um horizonte maior que o da validação. Essas diferenças ajudam a contextualizar o desempenho, mas não isolam sua causa. Além disso, a busca de configurações foi limitada.

**Frase para guardar:** “Selecionamos os modelos com dados anteriores ao teste e avaliamos tanto os erros quanto os intervalos. O resultado mais importante foi mostrar, com comparação, que a alternativa mais complexa não foi a melhor nessa janela.”
