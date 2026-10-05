import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dados import ROOT, carregar_serie, salvar_dados
from src.modelos import (
    avaliar_e_prever,
    salvar_resumo,
    selecionar,
    testar_estacionariedade,
)


def main():
    (ROOT / "output/tables").mkdir(parents=True, exist_ok=True)
    salvar_dados()
    serie = carregar_serie()
    testes = testar_estacionariedade(serie.loc[:"2008"])
    testes.to_csv(ROOT / "output/tables/estacionariedade.csv", index=False)
    print(testes.to_string(index=False), flush=True)
    selecionados, ranking = selecionar(serie)
    scores, teste, futuro, diagnosticos = avaliar_e_prever(serie, selecionados)
    salvar_resumo(serie, selecionados, ranking, scores, diagnosticos)
    print(scores.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
