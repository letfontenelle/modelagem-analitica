# Roteiro resumido da apresentação

Guia de estudo dos 13 slides. Use as falas como apoio, sem decorar: mostre no slide o resultado que está comentando. Para apresentar em 15-20 minutos, faça pausas nos gráficos e explique as comparações com calma.

## 1. Ilha Solteira e o rio Paraná

**O que falar:** “Nosso grupo estudou as vazões médias mensais de Ilha Solteira, no rio Paraná. O mapa localiza a cidade no noroeste de São Paulo, e a foto mostra a região urbana. Queremos comparar as previsões de ARIMA e SARIMA para essa série.”

**Como interpretar:** Cada barra é a média de um mês do ano entre 1931 e 2016. Fevereiro tem a maior média e setembro, a menor. Esse padrão indica sazonalidade anual; não significa que todos os anos sejam iguais.

## 2. A base de dados em um olhar

**O que falar:** “Recebemos uma tabela em PDF com 1.032 observações mensais, de 1931 a 2016: são 86 anos. Organizamos os dados por data e conferimos os valores. Não encontramos meses ausentes nem duplicados, e não foi necessário preencher dados.”

**Como interpretar:** Os cartões resumem a base. A média é aproximadamente 5.272 e a mediana, 4.194; valores altos puxam a média para cima. Os números mantêm a escala da tabela original, cuja unidade não foi informada.

## 3. Sazonalidade e extremos na série

**O que falar:** “O histórico mostra que as vazões oscilam ao longo dos anos. Existe um padrão sazonal, mas a intensidade dos picos varia bastante. Mantivemos todos os valores, inclusive os extremos.”

**Como interpretar:** No eixo horizontal estão as datas; no vertical, as vazões. Cada ponto corresponde a um mês. O maior valor foi 20.314, em fevereiro de 1983, e o menor, 1.212, em outubro de 2014. O gráfico descreve essas variações, sem identificar suas causas.

## 4. Como os resultados foram avaliados

**O que falar:** “Respeitamos a ordem do tempo. Usamos os dados até 2008 no treino inicial, 2009 a 2013 para escolher os modelos e 2014 a 2016 para o teste final. Os dados do teste não participaram da escolha.”

**Como interpretar:** Os três blocos mostram etapas diferentes. Na validação, previmos 12 meses por vez, ampliando o histórico a cada ano. No teste, previmos os 36 meses de uma vez. Por isso, os erros dessas duas etapas não são diretamente comparáveis.

## 5. Os modelos escolhidos na validação

**O que falar:** “Comparamos diferentes configurações e selecionamos uma de cada família. O ARIMA escolhido foi (2,0,2), e o SARIMA foi (1,0,0)(1,0,1), com ciclo de 12 meses. Entre os dois, o SARIMA teve menor erro na validação.”

**Como interpretar:** Os cartões mostram RMSE de aproximadamente 1.700 para ARIMA e 1.567 para SARIMA. RMSE resume o erro e dá mais peso a erros grandes: quanto menor, melhor. Esse resultado ainda precisava ser confirmado no teste reservado.

## 6. No teste, o ingênuo sazonal vence

**O que falar:** “No teste, também comparamos os modelos com duas referências simples: repetir o último ano e usar a média histórica de cada mês. A repetição do último ano, chamada ingênuo sazonal, teve o menor erro.”

**Como interpretar:** Quanto menor a barra, melhor. O RMSE foi cerca de 2.013 no ingênuo sazonal, 2.215 na média por mês, 2.234 no SARIMA e 2.390 no ARIMA. O SARIMA superou o ARIMA, mas as duas referências simples foram melhores nessa janela.

## 7. As previsões superestimam parte do teste

**O que falar:** “Comparando as previsões com o que realmente aconteceu, vemos que os modelos estimaram vazões acima das observadas em parte do teste. O SARIMA reproduz melhor a oscilação sazonal, mas também erra o nível dos valores.”

**Como interpretar:** Acompanhe a legenda e compare, no mesmo mês, a linha observada com cada previsão. Quanto maior a distância, maior o erro. A média do teste foi 3.773, abaixo dos 5.326 do histórico até 2013. Isso descreve o período, sem explicar a causa da queda.

## 8. ARIMA: intervalos preditivos de 95%

**O que falar:** “Além de um valor previsto, calculamos limites para representar a incerteza. No ARIMA, 33 dos 36 meses ficaram dentro desses limites: uma cobertura observada de 91,7%.”

**Como interpretar:** Compare a linha observada com os limites inferior e superior em cada mês. Entre eles, o valor foi coberto; fora deles, não. Os limites são largos: conter o valor observado não significa que a previsão central ficou próxima. O nível de 95% é nominal, não uma garantia.

## 9. SARIMA: intervalos preditivos de 95%

**O que falar:** “No SARIMA, as previsões e seus limites acompanham o ciclo sazonal. Porém, apenas 30 dos 36 meses ficaram dentro dos intervalos, uma cobertura de 83,3%.”

**Como interpretar:** Observe como a distância entre os limites varia ao longo dos meses. Depois, procure os valores observados que ficaram fora deles. O SARIMA teve menor erro central que o ARIMA, mas seus intervalos cobriram menos meses.

## 10. A cobertura ficou abaixo dos 95% nominais

**O que falar:** “Este slide reúne a comparação dos intervalos. O ARIMA cobriu mais meses, mas apresentou intervalos mais largos. O SARIMA teve intervalos mais estreitos e menor cobertura. Nenhum atingiu 95% neste teste.”

**Como interpretar:** Leia cobertura e largura juntas: ARIMA, 91,7% e largura média de 10.908; SARIMA, 83,3% e 6.026. Cobertura maior, sozinha, não torna a previsão mais precisa. São apenas 36 meses de avaliação, portanto a conclusão vale para esta janela.

## 11. Os diagnósticos mostram limites dos modelos

**O que falar:** “Também analisamos os resíduos, que são os erros que sobraram após o ajuste. Nos dois modelos, ainda encontramos padrões nesses erros e rejeitamos a hipótese de normalidade. Isso mostra que o ajuste tem limitações.”

**Como interpretar:** Os valores de p abaixo de 0,05 indicam dependência restante no teste Ljung-Box e rejeição da normalidade no Jarque-Bera. A mensagem principal é que os modelos não explicaram toda a estrutura da série, o que pede cautela ao interpretar seus intervalos.

## 12. O que os modelos projetaram para 2017

**O que falar:** “Depois da avaliação, reajustamos os modelos escolhidos com todos os dados até 2016 e projetamos os 12 meses de 2017. Essa é uma projeção histórica, pois a base termina em 2016.”

**Como interpretar:** O gráfico compara as médias previstas por ARIMA e SARIMA; os limites de 95% mostrados são os do SARIMA. Há valores maiores no começo e no fim do ano e menores no meio. Não temos os valores reais de 2017 na base para avaliar o acerto dessas projeções.

## 13. O que os resultados mostram

**O que falar:** “Concluímos que a série tem sazonalidade anual. O SARIMA foi melhor que o ARIMA, mas repetir o último ano foi a melhor alternativa no teste. Os intervalos e os diagnósticos mostram que ainda existe bastante incerteza.”

**Como interpretar:** Use os três cartões para encerrar: identificamos um padrão nos dados, comparamos o desempenho fora do treino e avaliamos a incerteza. A principal conclusão é que um modelo mais complexo não garantiu a melhor previsão neste caso.
