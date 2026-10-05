# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python (Ilha Solteira)
#     language: python
#     name: ilha-solteira
# ---

# %%
import json
import sys
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Markdown, display
from scipy.stats import jarque_bera
from statsmodels.graphics.gofplots import qqplot
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.seasonal import seasonal_decompose


def carregar_projeto():
    raiz_candidata = Path.cwd()
    if not (raiz_candidata / "src").is_dir():
        raiz_candidata = raiz_candidata.parent
    if not (raiz_candidata / "src/dados.py").is_file():
        raise FileNotFoundError("Abra este notebook na pasta notebooks/ ou na raiz do projeto.")
    sys.path.insert(0, str(raiz_candidata))
    from src.dados import carregar_serie, extrair_pdf
    from src.modelos import (
        ajustar,
        especificacoes,
        metricas,
        prever,
        selecionar,
        testar_estacionariedade,
    )

    return (raiz_candidata, carregar_serie, extrair_pdf, ajustar, especificacoes,
            metricas, prever, selecionar, testar_estacionariedade)


(ROOT, carregar_serie, extrair_pdf, ajustar, especificacoes,
 metricas, prever, selecionar, testar_estacionariedade) = carregar_projeto()

REFAZER_BUSCA = False
TABELAS = ROOT / "output/tables"
CORES = {"ARIMA": "#C46A39", "SARIMA": "#008F88", "observado": "#203B53"}
UNIDADE = "Vazão (unidade não informada no PDF)"
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
plt.rcParams.update({
    "figure.figsize": (12, 4.5), "figure.dpi": 120, "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.facecolor": "#F5F7F8", "figure.facecolor": "white",
    "axes.grid": True, "grid.alpha": 0.2,
})
pd.set_option("display.max_columns", 14)

# %%
if not (ROOT / "data/processed/ilha_solteira_mensal.csv").exists():
    raise FileNotFoundError("Na raiz do projeto, execute: .venv/bin/python scripts/analisar.py")
auditavel = extrair_pdf()
serie = carregar_serie()
assert len(serie) == 1032
assert serie.index.equals(pd.date_range("1931-01-01", "2016-12-01", freq="MS"))
assert serie.index.is_unique and not serie.isna().any() and (serie > 0).all()
np.testing.assert_array_equal(serie.to_numpy(), auditavel.vazao.to_numpy())
display(auditavel.head(12))
display(serie.describe().to_frame("Vazão"))
print(f"{len(serie):,} meses; {serie.index.min():%m/%Y} a {serie.index.max():%m/%Y}; "
      f"{serie.isna().sum()} ausentes; {serie.index.duplicated().sum()} datas duplicadas.")
print("Conferência PDF → CSV: todos os 1.032 valores coincidem.")

# %%
treino_inicial = serie.loc[:"2008-12-01"]
treino_teste = serie.loc[:"2013-12-01"]
teste = serie.loc["2014-01-01":]
assert (len(treino_inicial), len(treino_teste), len(teste)) == (936, 996, 36)
fig, ax = plt.subplots(figsize=(13, 4))
ax.plot(serie, color=CORES["observado"], linewidth=0.8)
ax.axvspan(mdates.date2num(date(2009, 1, 1)), mdates.date2num(date(2014, 1, 1)), color="#E7B95D", alpha=0.3, label="Validação: 2009–2013")
ax.axvspan(mdates.date2num(date(2014, 1, 1)), mdates.date2num(date(2017, 1, 1)), color="#C46A39", alpha=0.2, label="Teste: 2014–2016")
ax.set(title="86 anos de vazões mensais: contexto e divisão temporal", ylabel=UNIDADE, xlabel="Ano")
ax.legend(loc="upper left")
plt.tight_layout()
plt.show()

# %%
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
axes[0].boxplot([treino_inicial[treino_inicial.index.month == m] for m in range(1, 13)],
                tick_labels=MESES, patch_artist=True,
                boxprops={"facecolor": "#9CD7D0"}, medianprops={"color": "#203B53"})
axes[0].set(title="Distribuição por mês | treino 1931–2008", ylabel=UNIDADE)
por_mes = treino_inicial.groupby(treino_inicial.index.month).agg(["mean", "median"])
axes[1].plot(range(1, 13), por_mes["mean"], "o-", color=CORES["SARIMA"], label="Média")
axes[1].plot(range(1, 13), por_mes["median"], "o--", color=CORES["ARIMA"], label="Mediana")
axes[1].set(xticks=range(1, 13), xticklabels=MESES, title="Perfil anual no treino", ylabel=UNIDADE)
axes[1].legend()
plt.tight_layout()
plt.show()
print(f"Maior média mensal no treino: {MESES[por_mes['mean'].idxmax()-1]}; "
      f"menor: {MESES[por_mes['mean'].idxmin()-1]}.")

# %%
fig, axes = plt.subplots(2, 1, figsize=(15, 7), sharey=True)
for ax, anos in zip(axes, [range(1931, 1974), range(1974, 2017)]):
    ax.boxplot([serie[serie.index.year == ano] for ano in anos], tick_labels=list(anos),
               showfliers=True, medianprops={"color": CORES["SARIMA"]})
    ax.tick_params(axis="x", rotation=90, labelsize=8)
    ax.set(ylabel=UNIDADE, title=f"Boxplots anuais: {anos.start}–{anos.stop-1} | descritivo")
plt.tight_layout()
plt.show()

# %%
log_treino = np.log(treino_inicial)
fig, axes = plt.subplots(2, 1, figsize=(13, 6), sharex=True)
axes[0].plot(treino_inicial, color=CORES["observado"], alpha=0.5, linewidth=0.7, label="Mensal")
axes[0].plot(treino_inicial.rolling(12).mean(), color=CORES["ARIMA"], label="Média móvel 12 meses")
axes[0].set(ylabel=UNIDADE, title="Suavização descritiva no treino inicial")
axes[0].legend()
axes[1].plot(log_treino.rolling(12).mean(), color=CORES["SARIMA"], label="Média móvel de log(y)")
axes[1].plot(log_treino.rolling(12).std(), color=CORES["ARIMA"], label="Desvio móvel de log(y)")
axes[1].set(ylabel="Escala logarítmica", xlabel="Ano")
axes[1].legend()
plt.tight_layout()
plt.show()

# %%
decomposicoes = {
    nome: seasonal_decompose(treino_inicial, model=nome, period=12)
    for nome in ("additive", "multiplicative")
}
fig, axes = plt.subplots(4, 2, figsize=(14, 10), sharex=True)
for coluna, (nome, decomposicao) in enumerate(decomposicoes.items()):
    for linha, atributo in enumerate(["observed", "trend", "seasonal", "resid"]):
        axes[linha, coluna].plot(getattr(decomposicao, atributo), color=CORES["SARIMA"])
        axes[linha, coluna].set_ylabel(["Observado", "Tendência", "Sazonal", "Resíduo"][linha])
    axes[0, coluna].set_title(f"Decomposição {'aditiva' if nome == 'additive' else 'multiplicativa'} | período 12")
plt.tight_layout()
plt.show()

# %%
estacionariedade = testar_estacionariedade(treino_inicial)
display(estacionariedade.drop(columns="avisos").round(6))
for _, linha in estacionariedade.iterrows():
    if linha.avisos:
        print(f"{linha.serie}: {linha.avisos}")
transformacoes = {"log(y)": log_treino, "Diferença comum de log(y)": log_treino.diff().dropna(),
                  "Diferença sazonal de log(y)": log_treino.diff(12).dropna()}
fig, axes = plt.subplots(3, 1, figsize=(13, 7), sharex=True)
for ax, (nome, valores) in zip(axes, transformacoes.items()):
    ax.plot(valores, color=CORES["observado"], linewidth=0.7)
    ax.set_title(nome)
plt.tight_layout()
plt.show()

# %%
fig, axes = plt.subplots(3, 2, figsize=(13, 9))
for linha, (nome, valores) in enumerate(transformacoes.items()):
    plot_acf(valores, lags=36, zero=False, ax=axes[linha, 0], title=f"ACF | {nome}")
    plot_pacf(valores, lags=36, zero=False, method="ywm", ax=axes[linha, 1], title=f"PACF | {nome}")
    for ax in axes[linha]:
        ax.set_xticks([1, 6, 12, 18, 24, 30, 36])
        ax.set_xlabel("Defasagem em meses")
plt.tight_layout()
plt.show()

# %%
grade = pd.DataFrame(especificacoes())
display(grade.groupby("familia")["id"].count().to_frame("Candidatos"))
display(grade.head())

# %%
if REFAZER_BUSCA:
    selecionados, ranking = selecionar(serie)
else:
    if not (ROOT / "output/resumo.json").is_file():
        raise FileNotFoundError("Execute .venv/bin/python scripts/analisar.py ou use REFAZER_BUSCA=True.")
    resumo = json.loads((ROOT / "output/resumo.json").read_text())
    selecionados = resumo["selecionados"]
    ranking = pd.read_csv(TABELAS / "ranking_validacao.csv")
display(ranking.round(3))
display(pd.DataFrame(selecionados).T)
for familia, spec in selecionados.items():
    melhor_validacao = ranking.loc[ranking.familia == familia].sort_values("RMSE").iloc[0]
    assert spec["id"] == melhor_validacao.id
    registrado = next(item for item in especificacoes() if item["id"] == spec["id"])
    assert tuple(spec["order"]) == registrado["order"]
    assert tuple(spec["seasonal_order"]) == registrado["seasonal_order"]
busca = pd.read_csv(TABELAS / "busca_modelos.csv")
print(f"Convergiram {busca.convergiu.sum()} de {len(busca)} candidatos na busca inicial.")
if (~busca.convergiu).any():
    display(busca.loc[~busca.convergiu, ["id", "avisos"]])

# %%
ajustes = {}
for familia, spec in selecionados.items():
    ajuste, avisos = ajustar(treino_teste, spec)
    ajustes[familia] = ajuste
    parametros = pd.DataFrame({"coeficiente": ajuste.params, "erro_padrao": ajuste.bse,
                               "p_valor": ajuste.pvalues})
    parametros[["inferior_95", "superior_95"]] = ajuste.conf_int().to_numpy()
    display(Markdown(f"### {familia} {tuple(spec['order'])} × {tuple(spec['seasonal_order'])}"))
    display(parametros.round(6))
    print("Convergência:", ajuste.mle_retvals["converged"], "| Avisos:", avisos or "nenhum")

# %%
previsoes = {familia: prever(ajuste, len(teste)) for familia, ajuste in ajustes.items()}
for familia, previsao in previsoes.items():
    assert previsao.index.equals(teste.index)
    assert np.isfinite(previsao.to_numpy()).all()
    assert (previsao.inferior_95 > 0).all()
    assert (previsao.inferior_95 < previsao.superior_95).all()
    assert (previsao.media >= previsao.mediana).all()
display(previsoes["SARIMA"].head().round(2))

# %%
fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True, sharey=True)
for ax, (familia, previsao) in zip(axes, previsoes.items()):
    ax.plot(serie.loc["2011":], color=CORES["observado"], label="Observado", linewidth=1.5)
    ax.plot(previsao.media, color=CORES[familia], linewidth=2, label=f"{familia}: média prevista")
    ax.fill_between(previsao.index, previsao.inferior_95, previsao.superior_95,
                    color=CORES[familia], alpha=0.2, label="Intervalo de previsão de 95%")
    ax.axvline(pd.Timestamp("2014-01-01"), color="#627582", linestyle="--")
    ax.set(title=f"{familia} | origem dez/2013, horizonte de 36 meses", ylabel=UNIDADE)
    ax.legend(fontsize=9, loc="upper left")
axes[-1].set_xlabel("Mês previsto: teste 2014–2016")
plt.tight_layout()
plt.show()

# %%
baselines = {
    "Ingênuo sazonal": pd.Series(np.tile(treino_teste.iloc[-12:].to_numpy(), 3), index=teste.index),
    "Média por mês": pd.Series(treino_teste.groupby(treino_teste.index.month).mean()
                              .reindex(teste.index.month).to_numpy(), index=teste.index),
}
linhas_metricas = []
for familia, prev in previsoes.items():
    linhas_metricas.append({"modelo": familia, **metricas(teste, prev.media, treino_teste),
        "cobertura_95": 100 * teste.between(prev.inferior_95, prev.superior_95).mean(),
        "largura_media_95": (prev.superior_95 - prev.inferior_95).mean()})
for nome, prev in baselines.items():
    linhas_metricas.append({"modelo": nome, **metricas(teste, prev, treino_teste)})
scores = pd.DataFrame(linhas_metricas).set_index("modelo")
display(scores.round(2))
fig, ax = plt.subplots(figsize=(10, 4))
ordenado = scores.RMSE.sort_values()
barras = ax.barh(ordenado.index, ordenado.values, color=[CORES.get(m, "#8094A1") for m in ordenado.index])
ax.bar_label(barras, fmt="%.0f", padding=5)
ax.invert_yaxis()
ax.set(title="Erro no teste de 36 meses: menor RMSE é melhor", xlabel="RMSE (unidade original)")
ax.margins(x=0.15)
plt.tight_layout()
plt.show()
print("Menor RMSE no teste:", scores.RMSE.idxmin())
print("Média até 2013:", round(treino_teste.mean(), 2), "| Média em 2014–2016:", round(teste.mean(), 2))

# %%
residuos = {}
diagnosticos = []
for familia, ajuste in ajustes.items():
    spec = selecionados[familia]
    descarte = max(24, ajuste.loglikelihood_burn)
    resid = pd.Series(ajuste.filter_results.standardized_forecasts_error[0, descarte:],
                      index=treino_teste.index[descarte:]).dropna()
    residuos[familia] = resid
    graus = spec["order"][0] + spec["order"][2] + spec["seasonal_order"][0] + spec["seasonal_order"][2]
    lb = acorr_ljungbox(resid, lags=[12, 24], model_df=graus, return_df=True)
    estatistica_jb, p_valor_jb = jarque_bera(resid)
    diagnosticos.append({"modelo": familia, "LB12_p": lb.lb_pvalue.iloc[0],
                         "LB24_p": lb.lb_pvalue.iloc[1], "JB_p": p_valor_jb,
                         "media_residuo": resid.mean(), "descarte": descarte})
    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    axes[0, 0].plot(resid, color=CORES[familia], linewidth=0.6)
    axes[0, 0].axhline(0, color="black", linewidth=0.5)
    axes[0, 0].set_title("Inovações padronizadas")
    axes[0, 1].hist(resid, bins=40, density=True, color=CORES[familia], alpha=0.7)
    axes[0, 1].set_title("Distribuição")
    plot_acf(resid, lags=36, zero=False, ax=axes[1, 0], title="ACF dos resíduos")
    qqplot(resid, line="45", ax=axes[1, 1], markerfacecolor=CORES[familia], markeredgecolor=CORES[familia], alpha=0.5)
    axes[1, 1].set_title("Q–Q: referência normal")
    fig.suptitle(f"Diagnóstico {familia} | ajuste até dez/2013", fontsize=14)
    plt.tight_layout()
    plt.show()
diagnosticos = pd.DataFrame(diagnosticos).set_index("modelo")
display(diagnosticos)

# %%
futuro = {}
for familia, spec in selecionados.items():
    ajuste_final, avisos_final = ajustar(serie, spec)
    futuro[familia] = prever(ajuste_final, 12)
    assert futuro[familia].index.equals(pd.date_range("2017-01-01", periods=12, freq="MS"))
    print(f"{familia}: ajuste final convergiu; avisos = {avisos_final or 'nenhum'}")
display(pd.concat(futuro, axis=1).round(2))
fig, axes = plt.subplots(2, 1, figsize=(13, 7), sharex=True, sharey=True)
for ax, (familia, prev) in zip(axes, futuro.items()):
    ax.plot(serie.loc["2014":], color=CORES["observado"], label="Histórico observado")
    ax.plot(prev.media, color=CORES[familia], linewidth=2, label=f"{familia}: média prevista")
    ax.fill_between(prev.index, prev.inferior_95, prev.superior_95, color=CORES[familia], alpha=0.2, label="Intervalo de previsão de 95%")
    ax.axvline(pd.Timestamp("2017-01-01"), linestyle="--", color="#627582")
    ax.set(title=f"{familia} | projeção histórica de 2017, origem dez/2016", ylabel=UNIDADE)
    ax.legend(loc="upper left", fontsize=9)
plt.tight_layout()
plt.show()

# %%
salvo_teste = pd.read_csv(TABELAS / "previsoes_teste.csv", index_col="data", parse_dates=True)
salvo_futuro = pd.read_csv(TABELAS / "previsoes_2017.csv", index_col="data", parse_dates=True)
salvo_metricas = pd.read_csv(TABELAS / "metricas_teste.csv", index_col="modelo")
for familia in selecionados:
    for coluna in ["media", "mediana", "inferior_95", "superior_95"]:
        np.testing.assert_allclose(previsoes[familia][coluna], salvo_teste[f"{familia}_{coluna}"], rtol=1e-6)
        np.testing.assert_allclose(futuro[familia][coluna], salvo_futuro[f"{familia}_{coluna}"], rtol=1e-6)
np.testing.assert_allclose(scores[salvo_metricas.columns], salvo_metricas.loc[scores.index], rtol=1e-6, equal_nan=True)
print("VERIFICADO: 1.032 dados, 36 previsões de teste e 12 de 2017 por modelo; métricas coincidem com os CSVs.")
melhor_familia = scores.loc[["ARIMA", "SARIMA"], "RMSE"].idxmin()
ganho = 100 * (1 - scores.loc["SARIMA", "RMSE"] / scores.loc["ARIMA", "RMSE"])
display(Markdown(
    f"**Conclusão observada:** entre ARIMA e SARIMA, {melhor_familia} teve menor RMSE no teste. "
    f"A redução relativa do RMSE de SARIMA frente a ARIMA foi {ganho:.1f}%. "
    f"Considerando também as referências simples, o menor RMSE foi de **{scores.RMSE.idxmin()}**. "
    "A interpretação dos intervalos deve acompanhar a cobertura observada e os diagnósticos dos resíduos."
))
