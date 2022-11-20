import pandas as pd
import streamlit as st

from dashboard.componentes import (
    render_card, grafico_rosca, grafico_barras_h_condicional, grafico_heatmap,
)
from dashboard.metricas import (
    saude_marca, saude_concorrentes, favorabilidade_pct,
    pct_positivo, pct_neutro, pct_negativo,
    _detectar_marca_principal, MARCAS_BENCHMARK,
)
from dashboard.tema import (
    formatar_pct, VERDE, AMARELO, VERMELHO,
)


def render(dados: dict[str, pd.DataFrame]) -> None:
    sg = dados["sentimento_grupos"]
    marca = _detectar_marca_principal(sg)

    saude_e = saude_marca(sg)
    saude_c = saude_concorrentes(sg)
    fav_e = favorabilidade_pct(sg, marca=marca)

    c1, c2, c3, c4 = st.columns([1, 1, 2, 2])
    with c1:
        cor = "verde" if fav_e >= 0 else "vermelho"
        render_card("Favorabilidade", formatar_pct(fav_e), cor_delta=cor)
    with c2:
        cor_c = "verde" if saude_c >= 0 else "vermelho"
        render_card("Saude Concorrentes", formatar_pct(saude_c), cor_delta=cor_c)
    with c3:
        _render_rosca_polaridade(sg, marca=marca, titulo=f"Polaridade {marca}")
    with c4:
        _render_rosca_concorrentes(sg, marca_principal=marca, titulo="Polaridade Concorrentes")

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    _render_ranking_saude(sg)

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    _render_heatmap_mensal(sg)


def _render_rosca_polaridade(
    sg: pd.DataFrame,
    marca: str = "",
    titulo: str = "",
) -> None:
    pos = pct_positivo(sg, marca=marca)
    neu = pct_neutro(sg, marca=marca)
    neg = pct_negativo(sg, marca=marca)

    grafico_rosca(
        ["Positivo", "Neutro", "Negativo"],
        [pos, neu, neg],
        cores=[VERDE, AMARELO, VERMELHO],
        titulo=titulo,
        altura=240,
    )


def _render_rosca_concorrentes(
    sg: pd.DataFrame,
    marca_principal: str = "",
    titulo: str = "",
) -> None:
    excluir = {marca_principal} | MARCAS_BENCHMARK
    sg_conc = sg[(sg["canal"] == "all") & (~sg["marca"].isin(excluir))]
    if sg_conc.empty:
        st.info("Sem dados de concorrentes.")
        return

    total = sg_conc["total_mencoes"].sum()
    if total == 0:
        return

    pos = round(sg_conc["qtd_positivo"].sum() / total * 100, 1)
    neu = round(sg_conc["qtd_neutro"].sum() / total * 100, 1)
    neg = round(sg_conc["qtd_negativo"].sum() / total * 100, 1)

    grafico_rosca(
        ["Positivo", "Neutro", "Negativo"],
        [pos, neu, neg],
        cores=[VERDE, AMARELO, VERMELHO],
        titulo=titulo,
        altura=240,
    )


def _render_ranking_saude(sg: pd.DataFrame) -> None:
    sg_all = sg[sg["canal"] == "all"]
    if sg_all.empty:
        return

    ranking = sg_all.groupby("marca", as_index=False).agg(
        saude_media=("saude_marca_score", "mean"),
    )
    ranking["saude_media"] = ranking["saude_media"].round(1)

    grafico_barras_h_condicional(
        ranking, "marca", "saude_media",
        titulo="Ranking Saúde da Marca (todas as marcas)",
        altura=320,
    )


MESES_PT = {
    "01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr",
    "05": "Mai", "06": "Jun", "07": "Jul", "08": "Ago",
    "09": "Set", "10": "Out", "11": "Nov", "12": "Dez",
}


def _label_mes(mes_ano: str) -> str:
    partes = str(mes_ano).split("-")
    if len(partes) == 2:
        return f"{MESES_PT.get(partes[1], partes[1])}/{partes[0][2:]}"
    return str(mes_ano)


def _render_heatmap_mensal(sg: pd.DataFrame) -> None:
    sg_all = sg[sg["canal"] == "all"].copy()
    if sg_all.empty:
        return

    sg_all["mes_label"] = sg_all["mes_ano"].apply(_label_mes)

    pivot = sg_all.pivot_table(
        index="marca",
        columns="mes_label",
        values="saude_marca_score",
        aggfunc="mean",
    ).round(1)

    if pivot.empty:
        return

    meses_ordenados = sorted(sg_all["mes_ano"].unique())
    labels_ordenados = [_label_mes(m) for m in meses_ordenados]
    labels_presentes = [l for l in labels_ordenados if l in pivot.columns]
    pivot = pivot.reindex(columns=labels_presentes)

    grafico_heatmap(pivot, titulo="Saúde Mensal por Marca", altura=380)
