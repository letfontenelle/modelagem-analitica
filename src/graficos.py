from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.dates import date2num
from scipy.stats import probplot
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose

from src.dados import ROOT, carregar_serie

CORES = {"texto": "#173847", "SARIMA": "#137F83", "ARIMA": "#D48A35", "observado": "#172D3E"}
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
UNIDADE = "Vazão (m³/s; unidade assumida)"


def estilo():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.titlesize": 16,
                         "axes.labelsize": 11, "axes.titleweight": "bold", "axes.titlepad": 16,
                         "text.color": CORES["texto"], "axes.labelcolor": CORES["texto"],
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": True, "grid.alpha": 0.15, "figure.facecolor": "#FCFAF5",
                         "axes.facecolor": "#FCFAF5", "savefig.facecolor": "#FCFAF5"})


def salvar(fig, nome):
    destino = ROOT / "output/figures"
    destino.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino / f"{nome}.png", dpi=180, bbox_inches="tight")
    fig.savefig(destino / f"{nome}.svg", bbox_inches="tight")
    plt.close(fig)


def gerar_graficos():
    estilo()
    y = carregar_serie()
    treino = y.loc[:"2008"]
    teste = pd.read_csv(ROOT / "output/tables/previsoes_teste.csv", index_col=0, parse_dates=True)
    futuro = pd.read_csv(ROOT / "output/tables/previsoes_2017.csv", index_col=0, parse_dates=True)
    metricas = pd.read_csv(ROOT / "output/tables/metricas_teste.csv")

    fig, ax = plt.subplots(figsize=(13, 4.8), layout="constrained")
    ax.plot(y.index, y, color=CORES["SARIMA"], lw=0.85, alpha=0.8, label="Vazão mensal")
    ax.plot(y.index, y.rolling(12).mean(), color=CORES["observado"], lw=1.5, label="Média móvel de 12 meses")
    ax.axvspan(date2num(date(2014, 1, 1)), date2num(date(2016, 12, 1)), color=CORES["ARIMA"], alpha=0.18, label="Teste: 2014–2016")
    ax.set(title="86 anos de vazões mensais", ylabel=UNIDADE, xlabel="Ano")
    ax.legend(ncol=3, frameon=False, loc="upper left")
    salvar(fig, "01_serie_historica")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), layout="constrained")
    grupos = [treino[treino.index.month == mes].values for mes in range(1, 13)]
    bp = axes[0].boxplot(grupos, tick_labels=MESES, patch_artist=True,
                         flierprops={"markersize": 2, "alpha": 0.4})
    for caixa in bp["boxes"]:
        caixa.set_facecolor("#91C9C4")
    axes[0].set(title="Distribuição por mês", ylabel=UNIDADE)
    media = treino.groupby(treino.index.month).mean()
    axes[1].plot(MESES, media, marker="o", color=CORES["SARIMA"], lw=2.5)
    axes[1].set(title="Ciclo médio anual", ylabel=UNIDADE)
    fig.suptitle("Sazonalidade no treino inicial (1931–2008)", fontsize=19, fontweight="bold")
    salvar(fig, "02_sazonalidade")

    fig, ax = plt.subplots(figsize=(15, 5), layout="constrained")
    anos = sorted(y.index.year.unique())
    bp = ax.boxplot([y[y.index.year == a].values for a in anos], patch_artist=True,
                    showfliers=False, widths=0.6)
    for caixa in bp["boxes"]:
        caixa.set_facecolor("#91C9C4")
    ax.set_xticks(range(1, len(anos)+1, 5), anos[::5], rotation=45)
    ax.set(title="Distribuição dos 12 meses em cada ano", ylabel=UNIDADE,
           xlabel="Ano (extremos não desenhados neste boxplot; todos os dados foram preservados)")
    salvar(fig, "03_boxplot_anual")

    for modelo, numero in [("additive", "04"), ("multiplicative", "05")]:
        resultado = seasonal_decompose(treino, model=modelo, period=12)
        fig, axes = plt.subplots(4, 1, figsize=(13, 8), sharex=True, layout="constrained")
        for ax, valores, titulo in zip(axes, [resultado.observed, resultado.trend, resultado.seasonal, resultado.resid],
                                      ["Observado", "Tendência suavizada", "Sazonalidade", "Resíduo da decomposição"]):
            ax.plot(valores.index, valores, color=CORES["SARIMA"], lw=0.9)
            ax.set_ylabel(titulo)
        axes[-1].set_xlabel("Ano")
        rotulo = "aditiva" if modelo == "additive" else "multiplicativa"
        fig.suptitle(f"Decomposição {rotulo}, período de 12 meses (1931–2008)", fontsize=18)
        salvar(fig, f"{numero}_decomposicao_{rotulo}")

    log = np.log(treino)
    fig, axes = plt.subplots(3, 2, figsize=(13, 10), layout="constrained")
    for linha, (titulo, valores) in enumerate([("Log da vazão", log), ("Diferença de 1 mês", log.diff().dropna()),
                                               ("Diferença de 12 meses", log.diff(12).dropna())]):
        plot_acf(valores, lags=36, ax=axes[linha, 0], zero=False, title=f"ACF · {titulo}", color=CORES["SARIMA"])
        plot_pacf(valores, lags=36, ax=axes[linha, 1], zero=False, method="ywm", title=f"PACF · {titulo}", color=CORES["SARIMA"])
        for ax in axes[linha]:
            ax.set_xlabel("Defasagem em meses")
    salvar(fig, "06_acf_pacf")

    for familia, numero in [("ARIMA", "07"), ("SARIMA", "08")]:
        fig, ax = plt.subplots(figsize=(12, 5.4), layout="constrained")
        ax.fill_between(teste.index, teste[f"{familia}_inferior_95"], teste[f"{familia}_superior_95"],
                        color=CORES[familia], alpha=0.2, label="Intervalo de previsão nominal de 95%")
        ax.plot(teste.index, teste.observado, color=CORES["observado"], lw=2.2, marker="o", ms=3, label="Observado")
        ax.plot(teste.index, teste[f"{familia}_media"], color=CORES[familia], lw=2.3, label=f"Média prevista · {familia}")
        ax.set(title=f"{familia}: previsão de 36 meses a partir de dezembro de 2013", ylabel=UNIDADE, xlabel="Mês do teste (2014–2016)")
        ax.legend(frameon=False, fontsize=10, ncol=1, loc="upper right")
        salvar(fig, f"{numero}_teste_{familia.lower()}")

    fig, ax = plt.subplots(figsize=(11, 4.5), layout="constrained")
    ordem = metricas.sort_values("RMSE", ascending=False)
    bars = ax.barh(ordem.modelo, ordem.RMSE, color=[CORES.get(m, "#799096") for m in ordem.modelo], height=0.6)
    ax.bar_label(bars, labels=[f"{v:,.0f}".replace(",", ".") for v in ordem.RMSE], padding=8, fontsize=13)
    ax.set_xlim(0, ordem.RMSE.max() * 1.18)
    ax.set(title="Erro no teste de 2014–2016: menor é melhor", xlabel="RMSE (m³/s; unidade assumida)")
    salvar(fig, "09_comparacao_rmse")

    for familia, numero in [("ARIMA", "10"), ("SARIMA", "11")]:
        resid = pd.read_csv(ROOT / f"output/tables/residuos_{familia.lower()}.csv", index_col=0, parse_dates=True).iloc[:, 0]
        fig, axes = plt.subplots(2, 2, figsize=(12, 7.5), layout="constrained")
        axes[0, 0].plot(resid.index, resid, lw=0.7, color=CORES[familia])
        axes[0, 0].axhline(0, color="#777777", lw=0.8)
        axes[0, 0].set_title("Inovações padronizadas no tempo")
        axes[0, 1].hist(resid, bins=35, density=True, color=CORES[familia], alpha=0.8)
        axes[0, 1].set_title("Distribuição dos resíduos")
        probplot(resid, dist="norm", plot=axes[1, 0])
        axes[1, 0].set(title="QQ-plot: comparação com a normal", xlabel="Quantis da normal", ylabel="Quantis observados")
        plot_acf(resid, lags=36, zero=False, ax=axes[1, 1], title="ACF dos resíduos")
        axes[1, 1].set_xlabel("Defasagem em meses")
        fig.suptitle(f"Diagnóstico do {familia} ajustado até dezembro de 2013", fontsize=18)
        salvar(fig, f"{numero}_residuos_{familia.lower()}")

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, layout="constrained")
    for ax, familia in zip(axes, ["ARIMA", "SARIMA"]):
        historico = y.loc["2014":]
        ax.plot(historico.index, historico, color=CORES["observado"], lw=1.8, label="Histórico fornecido")
        ax.fill_between(futuro.index, futuro[f"{familia}_inferior_95"], futuro[f"{familia}_superior_95"], color=CORES[familia], alpha=0.2)
        ax.plot(futuro.index, futuro[f"{familia}_media"], color=CORES[familia], lw=2.3, label=f"{familia}: média e intervalo de 95%")
        ax.axvline(pd.Timestamp("2016-12-15"), color="#777777", linestyle="--", lw=1)
        ax.set(ylabel=UNIDADE, title=f"{familia} · projeção histórica para 2017")
        ax.legend(frameon=False, loc="upper left", fontsize=10)
    axes[-1].set_xlabel("Sem valores observados de 2017 no arquivo: não é previsão para a data atual")
    salvar(fig, "12_previsao_2017")
    return sorted((ROOT / "output/figures").glob("*.png"))


if __name__ == "__main__":
    print("\n".join(str(p.relative_to(ROOT)) for p in gerar_graficos()))
