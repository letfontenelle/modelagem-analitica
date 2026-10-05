# Ilha Solteira: vazões mensais, ARIMA e SARIMA
**Projeto reproduzível | 1931–2016 | previsão com intervalos de 95%**

Este notebook acompanha o caminho dos exemplos fornecidos: importar e organizar
os dados, explorar a série, investigar estacionariedade e sazonalidade, ajustar
ARIMA e SARIMA, analisar resíduos e comparar previsões com valores observados.
Corrigimos o período sazonal e a construção dos intervalos dos exemplos.
O documento `docs/como_seguimos_os_exemplos.md` relaciona cada adaptação às páginas.

**Pergunta:** incluir a sazonalidade anual melhora a previsão de vazões mensais?
Vamos responder com validação temporal e teste separado, sem presumir que SARIMA vence.

**Como executar:** na raiz do projeto, instale `requirements-lock.txt`, registre
o kernel com `python -m ipykernel install --user --name ilha-solteira
--display-name "Python (Ilha Solteira)"` e execute as células em ordem.
O notebook entregue já contém resultados. A opção `REFAZER_BUSCA=False` usa a
seleção salva, mas reajusta os dois modelos e recalcula previsões e métricas.
Para repetir a busca inteira, altere-a para `True`; isso leva mais tempo.

## 1. Da tabela do PDF à série temporal
O arquivo tem quatro páginas: as páginas 1 e 2 contêm 1931–1979; as páginas
3 e 4 contêm 1980–2016. Em cada par, janeiro a setembro aparecem na primeira
página e outubro a dezembro na segunda. `extrair_pdf()` une as linhas de cada
par pela posição, associa cada valor ao seu mês e guarda a página e a linha.

A data é uma **etiqueta mensal** no primeiro dia do mês (`MS`, month start),
não a indicação de uma medição diária. `carregar_serie()` lê o CSV auditável,
transforma a coluna de datas em índice e explicita essa frequência.
Conferimos abaixo todos os valores do CSV contra a extração independente do PDF.

**Limite da fonte:** o PDF não informa unidade, agência, método de medição nem
se a vazão é natural, afluente, defluente ou observada. m³/s é apenas uma hipótese
plausível; não a apresentamos como metadado confirmado. Não há interpolação,
suavização ou remoção de extremos nos dados usados para ajustar os modelos.

## 2. A regra mais importante: respeitar o tempo
Uma amostra embaralhada permitiria usar o futuro para prever o passado.
Separamos três etapas **antes de escolher os modelos**:

| Etapa | Dados disponíveis ao modelo | Como é usada |
|---|---|---|
| Busca inicial | jan/1931–dez/2008, 936 meses | AIC reduz a grade de candidatos |
| Validação | cinco origens em dez/2008 a dez/2012 | cada origem prevê o ano seguinte, até 2013 |
| Teste final | ajuste até dez/2013, 996 meses | previsão única dos 36 meses de 2014–2016 |
| Projeção histórica | ajuste até dez/2016, 1.032 meses | 12 meses de 2017, sem valores reais no arquivo |

As janelas de validação têm treino crescente. O teste não atualiza o modelo
a cada mês: mede uma previsão de três anos feita em dezembro de 2013.
Essa tarefa é mais difícil e diferente da validação de um ano; não confundir
os dois erros. As figuras da série completa são descritivas; testes,
decomposição e escolha de ordens usam apenas o período de desenvolvimento.

## 3. Distribuições e sazonalidade
O boxplot mostra mediana (linha interna), quartis (caixa), dispersão e valores
além dos bigodes (pontos). Um ponto isolado é extremo segundo essa regra gráfica;
isso **não prova erro de medição**. Os boxplots mensais comparam os mesmos meses
de anos diferentes. Os anuais comparam a distribuição dos 12 meses de cada ano.
A média e a mediana mensal abaixo usam apenas 1931–2008, evitando que o teste
determine a nossa interpretação da sazonalidade usada na modelagem.

## 4. Logaritmo, médias móveis e decomposição
Usamos `z = log(y)` porque todas as vazões são positivas e o logaritmo comprime
picos elevados. Uma diferença de log representa aproximadamente uma variação
relativa, e a transformação inversa garante previsões positivas.
Isso não garante variância constante nem normalidade: verificaremos os resíduos.

A média móvel de 12 meses suaviza o ciclo anual; o desvio móvel descreve mudanças
na dispersão local. Não são previsões nem dados substitutos para o ajuste.
A decomposição clássica é exploratória: aditiva, `y=T+S+R`, e multiplicativa,
`y=T×S×R`. O período correto para o ciclo anual mensal é **12**. Usar metade
da extensão da série, como em um exemplo, não representa esse ciclo.
A tendência centrada usa vizinhos dos dois lados dentro do treino; por isso
não a usamos como uma variável preditora disponível em tempo real.

## 5. Estacionariedade e diferenças
Uma série fracamente estacionária tem média e variância constantes e dependência
temporal que depende da distância entre observações, não da data. Uma série
sazonal pode ter dependência anual forte mesmo quando o ADF rejeita raiz unitária.

**ADF:** hipótese nula = existe raiz unitária; p < 0,05 fornece evidência contra
essa hipótese. **KPSS:** hipótese nula = estacionariedade em nível; p < 0,05
fornece evidência contra ela. Ambos são calculados com constante, sem tendência
determinística. Os testes têm limitações diante de quebras e mudanças históricas.
`testar_estacionariedade()` aplica os dois testes a quatro transformações,
escolhe defasagens do ADF por AIC e do KPSS automaticamente, e conserva avisos.
O p-valor do KPSS pode atingir os limites da tabela; não leia esses limites como
probabilidades exatas. Discordância entre testes exige inspeção e validação.

`diff(1)` calcula `log(y_t)−log(y_{t−1})`; `diff(12)` compara o mesmo mês
com o ano anterior. A ordem **d** é a diferença comum, **D** a sazonal.
**q** é o número de termos de médias móveis dos erros, não uma diferenciação.

## 6. ACF e PACF: pistas, não uma regra automática
A ACF mede correlação com valores anteriores; a PACF retira a contribuição das
defasagens intermediárias. Picos em 12, 24 e 36 sugerem dependência anual.
AR(p) pode produzir corte na PACF; MA(q), na ACF. Dados reais raramente exibem
um corte perfeito. As faixas de 95% são aproximadas e ponto a ponto; investigar
muitas defasagens pode produzir picos ao acaso. Fixamos `method='ywm'` na PACF.
O notebook mostra 36 meses para tornar três ciclos anuais visíveis.

## 7. O que significam ARIMA e SARIMA?
**ARIMA(p,d,q)** usa a persistência dos valores anteriores (AR), diferenças (I)
e erros passados (MA). **SARIMA(p,d,q)(P,D,Q)[12]** acrescenta relações sazonais,
como a dependência com 12 meses de distância. Ambos são ajustados sobre `log(y)`.
A classe `SARIMAX` de statsmodels implementa também o ARIMA quando a parte
sazonal é zero. Não usamos variáveis exógenas neste projeto.

`especificacoes()` gera uma grade deliberadamente pequena: ARIMA com p e q em
{0,1,2}, d em {0,1}; SARIMA com p,q,P,D,Q em {0,1}, d=0 e período 12,
excluindo P=D=Q=0. Portanto não alegamos encontrar o melhor modelo possível
entre todas as ordens. Para séries diferenciadas usamos `trend='n'` (sem deriva);
para d=D=0 usamos `trend='c'` (constante no modelo). A constante do SARIMAX
não é diretamente a média incondicional da série quando existem termos AR.

`ajustar()` estima os parâmetros por máxima verossimilhança, limita o otimizador
a 250 iterações e impõe estacionariedade/invertibilidade à parte ARMA, após as
diferenças. Ele rejeita ajustes sem convergência ou com AIC não finito e registra
os avisos, em vez de escondê-los.
Antes do ajuste, subtrai a média de log(y) calculada apenas no treino daquela
origem. Essa centralização melhora a escala numérica da otimização, especialmente
quando um coeficiente sazonal fica próximo de 1. Guardamos `centro_log` no ajuste
e o somamos de volta à média e aos limites logarítmicos antes da exponenciação.
O intercepto da tabela pertence à série logarítmica centralizada.

## 8. Escolha antes de olhar o teste
AIC = `−2 log L + 2k`: equilibra ajuste e complexidade. Só comparamos AIC de
candidatos da mesma família e mesmos d,D, na mesma série e janela inicial.
`selecionar()` leva os dois menores AIC de cada grupo para a validação. Em cada
uma das cinco origens, ele reajusta o candidato usando somente o passado e
prevê 12 meses. Um candidato precisa convergir nas cinco origens.
O menor **RMSE médio entre os cinco anos** escolhe um modelo de cada família.
O AIC não substitui erro fora da amostra; o teste 2014–2016 fica reservado.

No modo rápido, lemos as especificações registradas em `output/resumo.json` e
o ranking. Esses arquivos documentam a busca já executada. A seguir, os modelos
escolhidos serão reajustados de verdade; os resultados não serão apenas imagens.
Se faltarem os arquivos, execute `.venv/bin/python scripts/analisar.py` na raiz,
ou ative a busca completa nesta célula.

## 9. Ajustar novamente e interpretar os parâmetros
`ajustar(treino_teste, spec)` usa somente dados até dezembro de 2013. A tabela
mostra coeficiente, erro padrão, p-valor e intervalo de 95% **do parâmetro**.
`ar.L1` representa dependência AR na defasagem 1; `ma.L1` representa o efeito
de uma inovação passada; `ar.S.L12` e `ma.S.L12` são os equivalentes sazonais.
`sigma2` estima a variância das inovações na escala logarítmica.

Os p-valores pressupõem o modelo e suas hipóteses; significância individual não
prova capacidade preditiva. Tampouco o intervalo de um coeficiente é uma faixa
para vazões futuras. Essa distinção corrige o uso de `fitted.conf_int()` no exemplo.

## 10. Previsão e intervalo de 95% na escala original
`get_forecast(steps=h)` produz a distribuição preditiva para h meses.
O método `prever()` pede `conf_int(alpha=0.05)` **ao objeto de previsão**.
Se o log da vazão futura for aproximadamente normal, com média μ e variância v:

- mediana na escala original = `exp(μ)`;
- média na escala original = `exp(μ + v/2)`;
- limites = exponencial dos limites de 95% na escala logarítmica.

Usamos a média para calcular erros quadráticos. Exponenciar apenas μ daria a
mediana, geralmente menor. A transformação preserva a cobertura dos quantis,
mas produz faixas assimétricas, o que faz sentido em uma variável positiva.
São **intervalos de previsão pontuais de 95%**, não intervalos de confiança
da média nem garantia de conter 95% de uma trajetória inteira. São condicionais
ao modelo e aos parâmetros estimados e não incorporam toda a incerteza da seleção,
quebras estruturais ou novas condições hidrológicas.

## 11. Comparar com referências simples e medir os erros
O **ingênuo sazonal** repete os 12 meses de 2013 para cada ano do teste. A
**média por mês** usa a média histórica de cada mês, calculada até 2013.
Assim ambos conhecem exatamente o mesmo passado dos modelos. São referências
pontuais; não inventamos intervalos para elas.

`metricas()` transforma os valores em vetores alinhados e calcula:
**RMSE** = raiz do erro quadrático médio (penaliza picos);
**MAE** = erro absoluto médio (unidade da vazão);
**MAPE** = erro absoluto percentual médio (pode exagerar erros em vazões baixas);
**MASE** = MAE dividido pelo erro sazonal de um passo de 12 meses no treino.
MASE < 1 melhora essa escala histórica, não necessariamente o ingênuo sazonal
observado neste teste. Para comparar com ele, olhe as métricas das duas linhas.
A cobertura é a fração dos 36 valores dentro do intervalo; a largura média
mede o custo dessa cobertura. Faixas largas podem cobrir muito sem ser úteis.

## 12. Os resíduos guardam informação que o modelo deixou escapar?
Usamos inovações de um passo padronizadas pelo seu desvio previsto no filtro.
Descartamos os primeiros `max(24, loglikelihood_burn)` meses para reduzir o efeito
da inicialização. Idealmente a série oscila em torno de zero, sem padrões e com
dispersão estável. O Q–Q plot compara seus quantis com uma distribuição normal.

**Ljung–Box** testa ausência de autocorrelação conjunta até as defasagens 12 e 24;
descontamos p+q+P+Q graus de liberdade. p < 0,05 sugere dependência remanescente.
**Jarque–Bera** testa normalidade; p < 0,05 questiona a hipótese gaussiana usada
nos intervalos. p alto não prova que uma hipótese é verdadeira. Resíduos com
caudas pesadas podem prejudicar a cobertura mesmo quando a previsão pontual é boa.

## 13. Projetar 2017 usando todo o histórico disponível
Mantemos as ordens escolhidas antes do teste e reestimamos os parâmetros com
1931–2016. A primeira previsão é janeiro de 2017, exatamente um mês após o último
dado. Isso é uma **projeção histórica**, não uma previsão atual de 2026.
O material fornecido não permite calcular erro ou cobertura para 2017.
Os 12 valores, suas médias/medianas e limites ficam na tabela abaixo.

## 14. Conferir os resultados salvos e preparar a conclusão
A célula seguinte compara as previsões e métricas recalculadas neste notebook
com os CSVs gerados pelo script. A tolerância numérica permite pequenas diferenças
de arredondamento; qualquer diferença relevante interrompe a execução.
Na apresentação, explique primeiro o desenho de avaliação e depois o resultado.
Não escolha outro modelo com base no teste e volte a chamar esse teste de imparcial.

O resultado responde a uma grade pequena e a um único período de teste. Uma
diferença de médias entre períodos não identifica sozinha sua causa: atribuir
o comportamento a seca, operação de reservatório ou mudança climática exigiria
dados e referências adicionais. Extensões possíveis incluem origens mensais,
outros horizontes, variáveis hidrometeorológicas e modelos para mudanças de regime.

## 15. Guia para explicar o código e apresentar em 15–20 minutos
| Bloco de código | O que faz | Como explicar em voz alta |
|---|---|---|
| `src/dados.py: extrair_pdf` | une as páginas, associa meses e valida contagens | “Conferimos 86 anos completos, sem inventar observações.” |
| `salvar_dados` | exporta CSV com rastreio e JSON com hash SHA-256 da fonte | “Cada número pode ser localizado no PDF; o hash identifica o arquivo.” |
| `carregar_serie` | cria índice mensal regular | “Cada ponto representa a média de um mês.” |
| `testar_estacionariedade` | aplica ADF e KPSS a quatro transformações | “Os testes ajudam a investigar a necessidade de diferenças.” |
| `especificacoes` | enumera as ordens da grade | “Testamos alternativas simples dentro de limites explícitos.” |
| `ajustar` | estima por máxima verossimilhança sobre log(y) | “Os coeficientes são aprendidos apenas com o passado disponível.” |
| `selecionar` | AIC por grupo, depois validação com treino crescente | “Escolhemos antes de revelar 2014–2016.” |
| `prever` | média, mediana e intervalos na escala original | “A faixa mostra a incerteza do próximo valor mensal sob o modelo.” |
| `metricas` | RMSE, MAE, MAPE e MASE | “Não basta parecer bom: comparamos erros e referências simples.” |
| `avaliar_e_prever` | automatiza ajustes de teste e finais, resíduos e CSVs | “O script executa os mesmos cálculos mostrados aqui e guarda tabelas.” |
| `salvar_resumo` | reúne números, ordens e protocolo em JSON | “O relatório e os slides usam resultados rastreáveis.” |
| `scripts/analisar.py: main` | extrai dados, testa, seleciona, avalia e salva | “Um comando repete a análise completa na ordem correta.” |

**Distribuição do tempo:** problema e fonte (2 min); padrão sazonal e log (3 min);
ARIMA/SARIMA e protocolo (4 min); teste com gráficos e métricas (4 min);
intervalos/resíduos (3 min); projeção histórica e conclusão (2 min).
Mostre poucos números por vez, aponte os eixos e diga o que cada faixa significa.
Não leia as tabelas de coeficientes inteiras em voz alta; use-as para perguntas.

**Perguntas que você deve saber responder:** Por que 12? Porque há 12 meses no
ciclo anual. Por que não embaralhar? Porque o futuro não está disponível no
momento da previsão. Por que duas métricas de erro? Porque RMSE destaca extremos
e MAE descreve o erro absoluto típico. O que 95% garante? Nada sobre um evento
isolado; é a cobertura nominal pontual sob as hipóteses do modelo. Por que 2017?
Porque o arquivo termina em 2016. Por que não confirmar m³/s? Porque a fonte não
fornece esse metadado. Qual modelo ganhou? Consulte os números, inclusive baselines.

**Materiais de orientação:**
[DigitalOcean](https://www.digitalocean.com/community/tutorials/a-guide-to-time-series-forecasting-with-arima-in-python-3),
[GeeksforGeeks](https://www.geeksforgeeks.org/python-arima-model-for-time-series-forecasting/amp/) e
[AirPassengers de Aarshay Jain](https://github.com/aarshayj/analytics_vidhya/blob/master/Articles/Time_Series_Analysis/Time_Series_AirPassenger.ipynb).
Os exemplos locais são a referência de sequência didática; números, ordens,
frequência e cortes temporais pertencem exclusivamente à análise de Ilha Solteira.
