# Guia da apresentação em linguagem simples

Um slide por página, para estudar sem pressa. Leia primeiro a explicação e acompanhe o gráfico na apresentação. No fim de cada página, “O que falar” traz uma versão curta para você usar como apoio. Não é preciso decorar nem ler o guia inteiro na apresentação de 15-20 minutos.

## 1. Ilha Solteira e o rio Paraná

**Qual é a ideia deste slide?** Antes de mostrar números, queremos situar o professor: onde fica o lugar estudado e que tipo de informação vamos analisar. O mapa destaca Ilha Solteira, no noroeste de São Paulo, e a foto mostra a cidade.

**O que é vazão?** Pense na água passando por um ponto de um rio. Vazão é a quantidade de água que passa por unidade de tempo. Nosso arquivo traz uma média para cada mês. É como resumir o comportamento daquele mês em um número; não é a quantidade total de água acumulada no mês.

**Como ler o gráfico?** Cada barra representa um mês do ano. A barra de janeiro, por exemplo, reúne a média de todos os janeiros da base, de 1931 a 2016. Quanto mais alta a barra, maior a vazão média daquele mês. Fevereiro tem a maior média; setembro, a menor.

**Por que isso importa?** Existe uma época do ano em que as vazões costumam ser maiores e outra em que costumam ser menores. Essa repetição recebe o nome de sazonalidade. É parecido com observar que certas épocas do ano costumam ser mais quentes, embora a temperatura exata varie de um ano para outro. Aqui, o ciclo considerado tem 12 meses.

**O que falar:** “Nosso grupo estudou as vazões médias mensais de Ilha Solteira. O gráfico mostra um padrão ao longo do ano: fevereiro tem a maior média e setembro, a menor. Vamos investigar se usar esse padrão ajuda a prever as vazões.”

## 2. A base de dados em um olhar

**Qual é a ideia deste slide?** Mostrar com que material trabalhamos. Recebemos um PDF com uma tabela de vazões. Organizamos essa tabela para que o computador tivesse uma data e um valor de vazão para cada mês.

**De onde vêm os números do topo?** São 86 anos, de janeiro de 1931 a dezembro de 2016. Como cada ano tem 12 meses, temos 86 × 12 = 1.032 observações. “Observação” significa apenas um valor registrado: neste caso, a vazão média de um mês.

**O que conferimos?** Verificamos os números com a tabela original, procuramos meses faltando e datas repetidas. Não havia meses ausentes nem duplicados. Por isso, não precisamos inventar ou estimar valores para preencher lacunas.

**Como entender as estatísticas?** A média, aproximadamente 5.272, é a soma de todos os valores dividida pela quantidade. A mediana, 4.194, é o centro da lista depois de ordená-la. Por exemplo, em 2, 3 e 10, a mediana é 3 e a média é 5: o valor alto puxa a média para cima. O desvio padrão indica quanto os valores se espalham; não mede erro de previsão.

**Um cuidado ao apresentar:** O PDF não informa a unidade da vazão. Por isso, diga “na escala da tabela”, sem afirmar uma unidade que a fonte não confirmou.

**O que falar:** “A base contém 1.032 valores mensais, ao longo de 86 anos. Organizamos e conferimos os dados, sem precisar preencher meses faltantes. As estatísticas mostram que há bastante variação e que valores altos puxam a média para cima.”

## 3. Sazonalidade e extremos na série

**Qual é a ideia deste slide?** Agora vemos a história completa, mês a mês. No primeiro slide, resumimos os meses em 12 médias. Aqui, mostramos os 1.032 valores para enxergar o que aquele resumo não revela.

**Como ler o gráfico?** A posição horizontal indica a data. A altura indica a vazão daquele mês. Quando a linha sobe, a vazão aumenta; quando desce, diminui. Os picos mostram meses de valores altos. Observe que o padrão se repete, mas a altura dos picos não é sempre igual.

**Quais pontos destacar?** O maior valor foi 20.314, em fevereiro de 1983. O menor foi 1.212, em outubro de 2014. São extremos da base: o maior e o menor número registrado nela.

**Por que não apagamos os extremos?** Um valor muito diferente dos demais não é automaticamente um erro. Como esses números estão na tabela recebida, foram preservados. Apagá-los só por serem altos ou baixos mudaria a história que estamos tentando estudar.

**O que não podemos concluir só olhando?** O gráfico mostra quando houve aumentos e quedas, mas não explica a causa. Para atribuir uma queda à chuva ou à operação da usina, precisaríamos de informações adicionais que não estão nessa base.

**O que falar:** “O histórico mostra um padrão que se repete, mas também anos com picos muito diferentes. Mantivemos todos os valores, inclusive os extremos. Nosso desafio é prever uma série que tem repetição, mas não se comporta exatamente da mesma forma todo ano.”

## 4. Como os resultados foram avaliados

**Qual é a ideia deste slide?** Precisamos avaliar se o modelo consegue prever valores que ainda não usou. Se mostrássemos todas as respostas antes, a avaliação seria como fazer uma prova com o gabarito na mão.

**Pense em três etapas:** O treino é o momento de aprender com exemplos. A validação funciona como um simulado para escolher a melhor configuração. O teste é a prova final, usada depois dessa escolha. Essa comparação ajuda a entender os papéis, embora o computador aprenda por cálculos, não como uma pessoa.

**Como fizemos no projeto?** Primeiro, ajustamos os candidatos com dados até 2008. Depois, previmos 2009 usando o passado até 2008; previmos 2010 usando o passado até 2009; e repetimos esse processo até 2013. Assim, tivemos cinco avaliações anuais para escolher os modelos.

**E o teste final?** Com as configurações já escolhidas, ajustamos os modelos até dezembro de 2013 e previmos os 36 meses de 2014 a 2016 de uma vez. Não usamos os valores reais desses três anos para corrigir o modelo durante essa previsão.

**Por que manter as datas em ordem?** Porque, na prática, só conhecemos o passado quando prevemos o futuro. Misturar datas poderia deixar o modelo usar informações que ainda não estariam disponíveis. Também lembre: prever 12 meses e prever 36 meses são tarefas diferentes; os erros das duas etapas não são diretamente comparáveis.

**O que falar:** “Separamos os dados no tempo. Usamos o histórico para ajustar os modelos, cinco anos para escolher as configurações e um período reservado para a avaliação final. Assim, os valores do teste não ajudaram a escolher o modelo.”

## 5. Os modelos escolhidos na validação

**Qual é a ideia deste slide?** Escolher como o computador vai usar o passado para prever. ARIMA e SARIMA são duas formas de fazer isso. O ARIMA usa relações entre valores e erros anteriores. O SARIMA acrescenta uma estrutura para a repetição anual.

**Como escolhemos?** Imagine uma seleção de candidatos. Montamos 46 configurações e tentamos ajustá-las com os dados até 2008. Quando o cálculo encontra uma solução válida segundo o critério do programa, dizemos que o ajuste “convergiu”. Entre esses ajustes, usamos o AIC para filtrar candidatos e o RMSE da validação para escolher um de cada família.

**O que é AIC?** É um critério que pergunta: “Este modelo explica bem o histórico sem precisar de complexidade demais?” Acrescentar regras pode melhorar o ajuste ao passado sem melhorar a previsão. Por isso, o AIC penaliza a quantidade de parâmetros. Menor AIC é preferível entre modelos comparáveis. Os dois melhores de cada grupo com as mesmas ordens de diferenciação seguiram para a validação.

**O que é RMSE?** É uma medida de quanto a previsão se afastou do valor real, dando mais peso aos erros grandes. Quanto menor, melhor. Os valores do slide, 1.700 e 1.567, são médias dos erros medidos dessa forma nos cinco anos de validação. O SARIMA teve o menor valor entre os dois. Não são porcentagens nem vazões previstas.

**O que significa ARIMA (2,0,2)?** Pense nesses números como ajustes da máquina. O primeiro 2 permite usar diretamente valores dos dois meses anteriores. O 0 significa que não aplicamos diferenciação: trabalhar com a mudança entre meses, como passar de 3.000 para 3.500 e obter uma diferença de 500. O último 2 permite usar erros dos dois meses anteriores. O histórico inteiro do treino foi usado para aprender os pesos dessas relações, não apenas dois meses.

**E SARIMA (1,0,0) × (1,0,1)₁₂?** O primeiro bloco descreve a parte mensal. O segundo acrescenta relações com valores e erros no ciclo anual. O 12 indica o intervalo de 12 meses. Os zeros na diferenciação não significam ausência de sazonalidade.

**E o logaritmo?** É uma transformação que comprime a escala dos números, usada no ajuste. Depois, devolvemos as previsões à escala original para compará-las com os valores reais. Não é preciso explicar a fórmula na apresentação.

**O que falar:** “Comparamos configurações, filtramos pelo equilíbrio entre ajuste e complexidade e escolhemos pelo menor erro na validação. O SARIMA foi melhor nessa etapa. São os melhores dentro da seleção realizada, não entre todas as possibilidades.”

## 6. No teste, o ingênuo sazonal vence

**Qual é a ideia deste slide?** Ver se os modelos escolhidos realmente trazem vantagem. Para isso, comparamos ARIMA e SARIMA com duas maneiras simples de prever. É como perguntar se uma ferramenta mais elaborada resolve melhor a tarefa do que uma solução básica.

**O que é o ingênuo sazonal?** O nome significa uma regra simples: repetir o último ano conhecido. Usamos janeiro de 2013 para prever janeiro de 2014, 2015 e 2016, e fazemos o mesmo para os outros meses. Não usamos os valores reais de 2014 para prever 2015.

**E a média por mês?** Em vez de repetir o último janeiro, calculamos a média de todos os janeiros disponíveis até 2013. Essa média vira a previsão para janeiro. Repetimos o processo para os demais meses.

**Como ler as barras?** Elas mostram RMSE: quanto menor a barra, menor o erro segundo essa medida. O ingênuo sazonal teve cerca de 2.013; a média por mês, 2.215; o SARIMA, 2.234; e o ARIMA, 2.390. Portanto, a repetição de 2013 foi a melhor das quatro alternativas nessa avaliação.

**Como o RMSE é calculado?** Pegamos os erros, elevamos ao quadrado, fazemos a média e tiramos a raiz. Exemplo: erros de 100 e 300 dão RMSE de aproximadamente 224. Não significa que cada previsão errou 224. O número resume os erros e pesa mais os maiores. Ele fica na unidade dos dados, não em porcentagem.

**O que falar:** “No teste, repetir o último ano teve menor erro do que os modelos. O SARIMA foi melhor que o ARIMA, mas as duas referências simples foram melhores nessa janela. Usar uma técnica mais complexa não garantiu uma previsão melhor.”

## 7. As previsões superestimam parte do teste

**Qual é a ideia deste slide?** As barras anteriores resumiram o erro em um número. Agora olhamos mês a mês para entender como os modelos erraram: ficaram acima, abaixo ou próximos dos valores reais?

**Como ler as linhas?** Use a legenda para localizar o observado, que é o valor real, e as previsões de ARIMA e SARIMA. Escolha um mês e compare as alturas das linhas nessa mesma data. Quanto maior a distância entre a previsão e o observado, maior foi o erro naquele mês.

**O que significa superestimar?** É prever mais do que aconteceu. Se a vazão real foi 3.000 e o modelo previu 5.000, ele superestimou em 2.000. Se previsse 2.000, teria subestimado em 1.000. O RMSE mede o tamanho dos erros; o gráfico ajuda a enxergar sua direção.

**O que aconteceu aqui?** Em parte do teste, as previsões ficaram acima dos valores reais. O SARIMA desenha melhor a oscilação anual, mas ainda pode errar a altura dessa oscilação. Seguir o formato da curva não significa acertar seus valores.

**Por que mostramos as médias?** A média do teste foi aproximadamente 3.773, menor que os 5.326 do histórico até 2013. Isso ajuda a perceber que o período avaliado teve valores mais baixos. Não prova, sozinho, por que isso ocorreu nem qual foi a causa dos erros.

**O que falar:** “Os modelos reconheceram parte do padrão, mas previram valores altos demais em alguns meses. O teste teve vazões menores que a média anterior. Por isso, acompanhar a sazonalidade não foi suficiente para acertar o nível das vazões.”

## 8. ARIMA: intervalos preditivos de 95%

**Qual é a ideia deste slide?** Uma previsão é incerta. Em vez de mostrar só um número, apresentamos também uma faixa de valores. É parecido com estimar uma chegada entre 14h e 15h, em vez de prometer exatamente 14h30.

**Como ler o gráfico?** Localize a previsão central e os limites inferior e superior. Em cada mês, veja se o valor observado ficou entre os dois limites. Se ficou, o intervalo cobriu aquele valor. Se ficou acima do superior ou abaixo do inferior, não cobriu.

**O que significa 95%?** É a cobertura que o método pretende alcançar sob as hipóteses do modelo. Em muitas previsões feitas nessas condições, a ideia é que cerca de 95 em cada 100 intervalos contenham o valor futuro. Não é uma promessa de que exatamente 95% dos meses deste teste ficarão dentro.

**Qual foi o resultado do ARIMA?** Dos 36 meses, 33 ficaram dentro dos limites. Calculamos 33 dividido por 36, vezes 100: aproximadamente 91,7%. Essa é a cobertura observada no nosso teste.

**Uma faixa larga é sempre boa?** Não. Dizer que alguém chegará entre 8h e 20h pode aumentar a chance de incluir a chegada, mas ajuda pouco a planejar. Da mesma forma, um intervalo largo pode cobrir o valor real mesmo quando a previsão central fica distante dele.

**O que falar:** “Os intervalos representam a incerteza. No ARIMA, 33 dos 36 meses ficaram dentro dos limites, uma cobertura de 91,7%. Mas as faixas são largas: cobrir o valor não significa que a previsão central acertou bem.”

## 9. SARIMA: intervalos preditivos de 95%

**Qual é a ideia deste slide?** Repetimos a leitura dos intervalos, agora para o SARIMA. Queremos saber se ele representa bem a incerteza, além de produzir uma previsão central.

**Como ler o gráfico?** Acompanhe o valor real e os dois limites em cada mês. Observe que a distância entre os limites varia ao longo do ano. Procure também os meses em que o observado ficou fora da faixa.

**Qual foi o resultado?** O SARIMA cobriu 30 dos 36 meses. Isso equivale a 83,3%; portanto, seis meses ficaram fora. O ARIMA havia coberto 33 meses. Nesta avaliação, o SARIMA cobriu menos valores.

**Mas o SARIMA não tinha errado menos?** Sim, sua previsão central teve menor RMSE que a do ARIMA. Não há contradição: uma coisa é a distância entre a previsão central e o valor real; outra é verificar se a faixa contém esse valor. Um modelo pode ter menor erro central e, ao mesmo tempo, intervalos que cobrem menos meses.

**O que guardar?** Não escolha um vencedor só olhando a largura da faixa ou só contando quantos valores ela cobriu. Precisamos olhar as duas coisas, junto com os erros da previsão central.

**O que falar:** “O SARIMA teve menor erro central que o ARIMA, mas seus intervalos cobriram menos meses: 30 de 36, ou 83,3%. Isso mostra que acertar melhor a previsão central e representar bem a incerteza são aspectos diferentes.”

## 10. A cobertura ficou abaixo dos 95% nominais

**Qual é a ideia deste slide?** Colocar os resultados dos dois modelos lado a lado. Há duas perguntas: quantos valores ficaram dentro das faixas e quanto essas faixas eram largas?

**O que é cobertura?** É a porcentagem de valores reais que ficaram dentro dos intervalos. ARIMA: 33 de 36, ou 91,7%. SARIMA: 30 de 36, ou 83,3%. “95% nominais” significa o nível pretendido pelo método; “cobertura observada” é o que aconteceu neste teste.

**O que é largura média?** Em cada mês, subtraímos o limite inferior do superior. Uma faixa de 2.000 a 8.000 tem largura 6.000. Depois calculamos a média dessas larguras. No ARIMA, ela foi cerca de 10.908; no SARIMA, 6.026.

**Como juntar essas informações?** O ARIMA cobriu mais meses, mas ofereceu faixas mais largas. O SARIMA ofereceu faixas mais estreitas, mas deixou mais valores de fora. É o equilíbrio entre dar uma indicação útil e representar a incerteza sem estreitar demais os limites.

**Qual é o cuidado na conclusão?** Nenhum chegou a 95% nesse teste, mas avaliamos apenas 36 meses, que podem ter relação entre si. Essa contagem não prova que a cobertura será sempre assim em qualquer período.

**Se perguntarem “confiança ou previsão”?** Aqui são intervalos de previsão: faixas para vazões futuras. Um intervalo de confiança de um coeficiente descreve a incerteza sobre um número interno do modelo e não substitui essas faixas.

**O que falar:** “O ARIMA cobriu mais meses com intervalos mais largos. O SARIMA teve intervalos menores, mas menor cobertura. Precisamos avaliar cobertura e largura juntas, sem tratar os 95% como uma garantia.”

## 11. Os diagnósticos mostram limites dos modelos

**Qual é a ideia deste slide?** Depois de ajustar um modelo, olhamos o que ele ainda não conseguiu explicar. Essas diferenças que sobram recebem o nome de resíduos.

**Pense assim:** Imagine que você retirou de uma sequência tudo o que conseguiu reconhecer. Se ainda sobra um desenho que se repete, algo ficou para trás. Queremos saber se os resíduos ainda têm padrões que poderiam ter sido aproveitados pelo modelo.

**O que faz o Ljung-Box?** Ele verifica se os resíduos têm relação entre si ao longo do tempo. No nosso projeto, os resultados indicaram dependência restante nos dois modelos. Em linguagem simples: ainda sobrou uma organização nos erros que o modelo não capturou bem.

**O que faz o Jarque-Bera?** Verifica se a forma da distribuição dos resíduos é compatível com uma distribuição normal, a conhecida curva em sino. Nos dois modelos, houve evidência contra essa hipótese. Isso importa porque as faixas de previsão dependem de hipóteses estatísticas sobre o comportamento dos erros.

**O que significa p menor que 0,05?** Cada teste começa supondo algo: no primeiro, ausência de dependência; no segundo, normalidade. O valor de p indica quão incomum seria um resultado tão extremo ou mais se essa suposição valesse. Abaixo de 0,05, usamos a regra de rejeitar a suposição. Não significa “95% de chance de o modelo estar errado”.

**Esses resíduos são os erros do teste final?** Não são a mesma avaliação. Aqui analisamos os resíduos do ajuste feito com o histórico disponível até 2013. No teste final, comparamos previsões de 36 meses com valores que ficaram reservados.

**O que falar:** “Os diagnósticos mostram que ainda restaram padrões nos resíduos e que a hipótese de normalidade não foi adequada. Isso não apaga os resultados, mas mostra limitações e pede cuidado ao interpretar os intervalos.”

## 12. O que os modelos projetaram para 2017

**Qual é a ideia deste slide?** Depois de terminar a avaliação, usamos o histórico completo para produzir uma previsão do ano seguinte ao fim da base.

**Por que 2017?** Porque o último mês disponível é dezembro de 2016. Portanto, os próximos 12 meses são os de 2017. É uma projeção feita a partir daquele ponto do passado, não uma previsão para o ano atual.

**O que significa reajustar?** Pense em atualizar uma receita com mais exemplos. Mantivemos as configurações escolhidas, mas recalculamos seus pesos usando os dados até 2016. Isso não altera a avaliação anterior: o teste de 2014-2016 já foi feito separadamente, usando apenas o histórico até 2013.

**Como ler o gráfico?** A legenda identifica as médias previstas por ARIMA e SARIMA. Os dois limites de 95% desenhados são os do SARIMA. A projeção mostra valores maiores no começo e no fim do ano e menores no meio. As curvas representam o que os modelos estimaram, não medições reais de 2017.

**Podemos dizer que acertou?** Não. O arquivo não contém as vazões observadas de 2017 para comparar. Podemos mostrar o que foi previsto e sua incerteza, mas não afirmar o acerto dessa projeção.

**O que falar:** “Após avaliar os modelos, usamos todos os dados até 2016 para projetar 2017. O gráfico mostra as previsões e os limites do SARIMA. Como não temos os valores reais de 2017 nessa base, não podemos medir o acerto dessa etapa.”

## 13. O que os resultados mostram

**Qual é a ideia deste slide?** Encerrar com três respostas claras: o que aprendemos sobre os dados, qual alternativa funcionou melhor e quais limitações encontramos.

**Primeira resposta: existe um padrão anual.** Certos meses costumam ter vazões maiores e outros, menores. Mas repetir um padrão não significa repetir exatamente os valores. Os anos continuam diferentes entre si.

**Segunda resposta: a alternativa mais complexa não venceu.** Entre os ARIMA e SARIMA selecionados, o SARIMA teve menor erro na validação e no teste. Porém, entre as quatro alternativas comparadas no teste, repetir o ano de 2013 teve o menor RMSE. Essa conclusão vale para a janela e o critério usados.

**Terceira resposta: ainda existe incerteza.** Os intervalos foram largos, cobriram menos de 95% dos meses do teste e os resíduos ainda tinham padrões. Portanto, não devemos apresentar os modelos como se previssem as vazões com certeza.

**Se perguntarem por que o SARIMA não ganhou de todos:** Reconhecer a época do ano ajuda, mas não garante acertar a altura dos valores. O teste teve vazões menores que o histórico e avaliou 36 meses de uma vez, enquanto a validação avaliou 12 por vez. Isso dá contexto ao resultado, mas não prova uma causa única. Além disso, nossa busca de configurações foi limitada.

**O que falar:** “Encontramos sazonalidade, comparamos as previsões em dados reservados e avaliamos a incerteza. O SARIMA superou o ARIMA, mas a referência mais simples venceu no teste. O trabalho mostra por que precisamos comparar resultados, em vez de assumir que um modelo mais complexo será melhor.”
