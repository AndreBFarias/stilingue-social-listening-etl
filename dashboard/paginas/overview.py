import pandas as pd
import streamlit as st

from dashboard.componentes import (
    render_card, grafico_combo, grafico_rosca,
)
from dashboard.metricas import (
    saude_marca, volume_publicacoes, alcance_potencial,
    total_interacoes, media_diaria_publicacoes, posicao_ranking,
    variacao_saude_mom, favorabilidade_pct,
    pct_positivo, pct_neutro, pct_negativo,
    _detectar_marca_principal,
)
from dashboard.tema import (
    formatar_numero, formatar_pct, formatar_milhoes,
    VERDE, AMARELO, VERMELHO, CORES_DADOS, COR_SENTIMENTO,
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


def render(dados: dict[str, pd.DataFrame]) -> None:
    vg = dados["visao_geral"]
    sg = dados["sentimento_grupos"]
    pub = dados["publicacoes"]
    re = dados["ranking_evolutivo"]

    saude = saude_marca(sg)
    delta_mom = variacao_saude_mom(sg)
    vol = volume_publicacoes(vg)
    alcance = alcance_potencial(vg)
    interacoes = total_interacoes(pub)
    media = media_diaria_publicacoes(vg)
    ranking = posicao_ranking(re)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        cor_saude = "verde" if saude >= 0 else "vermelho"
        delta_str = f"{delta_mom:+.1f} pts MoM" if delta_mom != 0 else ""
        render_card("Saúde da Marca", formatar_pct(saude), delta_str, cor_saude)
    with c2:
        render_card("Volume Publicações", formatar_numero(vol))
    with c3:
        render_card("Alcance Potencial", formatar_milhoes(alcance))
    with c4:
        render_card("Total Interações", formatar_milhoes(interacoes))
    with c5:
        render_card("Média Diária", formatar_numero(media))
    with c6:
        render_card("Posição Ranking", f"#{ranking}" if ranking > 0 else "N/A")

    st.markdown("<div style='height: 0.8rem'></div>", unsafe_allow_html=True)

    _render_combos(sg)

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    _render_roscas(sg, pub)


def _render_combos(sg: pd.DataFrame) -> None:
    marca = _detectar_marca_principal(sg)
    sg_marca = sg[(sg["canal"] == "all") & (sg["marca"] == marca)].copy()
    if sg_marca.empty:
        st.info("Sem dados de sentimento para a marca principal no período selecionado.")
        return

    mensal = sg_marca.groupby("mes_ano", as_index=False).agg(
        qtd_positivo=("qtd_positivo", "sum"),
        qtd_neutro=("qtd_neutro", "sum"),
        qtd_negativo=("qtd_negativo", "sum"),
        saude_marca_score=("saude_marca_score", "mean"),
        total_mencoes=("total_mencoes", "sum"),
    ).sort_values("mes_ano")

    mensal["mes_label"] = mensal["mes_ano"].apply(_label_mes)

    mensal["favorabilidade"] = mensal.apply(
        lambda r: round((r["qtd_positivo"] - r["qtd_negativo"]) / r["total_mencoes"] * 100, 1)
        if r["total_mencoes"] > 0 else 0,
        axis=1,
    )

    col1, col2 = st.columns(2)
    with col1:
        grafico_combo(
            mensal, "mes_label",
            "qtd_positivo", "qtd_neutro", "qtd_negativo",
            "saude_marca_score",
            titulo="Interações x Saúde da Marca",
            nome_linha="Saúde",
        )
    with col2:
        grafico_combo(
            mensal, "mes_label",
            "qtd_positivo", "qtd_neutro", "qtd_negativo",
            "favorabilidade",
            titulo="Favorabilidade por Mês",
            nome_linha="Favorabilidade %",
        )


def _render_roscas(sg: pd.DataFrame, pub: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)

    with col1:
        if not pub.empty:
            por_canal = pub.groupby("canal").size().reset_index(name="total")
            por_canal = por_canal.sort_values("total", ascending=False)
            top_canais = por_canal.head(8)
            outros = por_canal.iloc[8:]["total"].sum()
            if outros > 0:
                top_canais = pd.concat([
                    top_canais,
                    pd.DataFrame([{"canal": "Outros", "total": outros}]),
                ], ignore_index=True)

            grafico_rosca(
                top_canais["canal"].tolist(),
                top_canais["total"].tolist(),
                cores=CORES_DADOS[:len(top_canais)],
                titulo="Distribuição por Canal",
            )

    with col2:
        sg_all = sg[sg["canal"] == "all"]
        if not sg_all.empty:
            pos = int(sg_all["qtd_positivo"].sum())
            neu = int(sg_all["qtd_neutro"].sum())
            neg = int(sg_all["qtd_negativo"].sum())

            grafico_rosca(
                ["Positivo", "Neutro", "Negativo"],
                [pos, neu, neg],
                cores=[VERDE, AMARELO, VERMELHO],
                titulo="Sentimento Geral",
            )
