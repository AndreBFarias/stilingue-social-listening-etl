import pandas as pd
import streamlit as st

from dashboard.componentes import (
    render_card, grafico_barras_h, grafico_linha, render_tabela_html,
)
from dashboard.metricas import (
    total_posts, engajamento_por_post, total_curtidas,
    total_comentarios, total_compartilhamentos, share_of_voice,
    _detectar_marca_principal,
)
from dashboard.tema import (
    formatar_numero, formatar_pct, formatar_milhoes,
    CIANO, LARANJA,
)


def render(dados: dict[str, pd.DataFrame]) -> None:
    pub = dados["publicacoes"]
    sg = dados["sentimento_grupos"]
    lc = dados["linechart"]

    posts = total_posts(pub)
    engaj = engajamento_por_post(pub)
    curtidas = total_curtidas(pub)
    coments = total_comentarios(pub)
    compartilh = total_compartilhamentos(pub)
    sov = share_of_voice(sg)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_card("Total Posts", formatar_numero(posts))
    with c2:
        render_card("Engajamento/Post", formatar_numero(engaj, 0))
    with c3:
        render_card("Total Curtidas", formatar_milhoes(curtidas))
    with c4:
        render_card("Total Comentários", formatar_milhoes(coments))
    with c5:
        render_card("Compartilhamentos", formatar_milhoes(compartilh))
    with c6:
        render_card("Share of Voice", formatar_pct(sov))

    st.markdown("<div style='height: 0.8rem'></div>", unsafe_allow_html=True)

    _render_barras_canal(pub)

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    _render_tabela_e_linha(sg, lc)


def _render_barras_canal(pub: pd.DataFrame) -> None:
    if pub.empty:
        return

    col1, col2 = st.columns(2)

    with col1:
        volume = pub.groupby("canal").size().reset_index(name="total")
        grafico_barras_h(volume, "canal", "total", cor=CIANO, titulo="Volume por Canal", top_n=10)

    with col2:
        engaj_canal = pub.groupby("canal", as_index=False).agg(
            interacoes=("interacoes", "sum"),
            posts=("canal", "count"),
        )
        engaj_canal["engaj_por_post"] = (engaj_canal["interacoes"] / engaj_canal["posts"]).round(0).astype(int)
        grafico_barras_h(
            engaj_canal, "canal", "engaj_por_post",
            cor=LARANJA, titulo="Engajamento por Canal (interações/post)", top_n=10,
        )


def _render_tabela_e_linha(sg: pd.DataFrame, lc: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)

    with col1:
        marca = _detectar_marca_principal(sg)
        sg_canais = sg[(sg["marca"] == marca) & (sg["canal"] != "all")].copy()
        if not sg_canais.empty:
            agg = sg_canais.groupby("canal", as_index=False).agg(
                total_mencoes=("total_mencoes", "sum"),
                qtd_positivo=("qtd_positivo", "sum"),
                qtd_negativo=("qtd_negativo", "sum"),
                saude_marca_score=("saude_marca_score", "mean"),
            )
            agg["pct_positivo"] = (agg["qtd_positivo"] / agg["total_mencoes"] * 100).round(1)
            agg["pct_negativo"] = (agg["qtd_negativo"] / agg["total_mencoes"] * 100).round(1)
            agg["saude_marca_score"] = agg["saude_marca_score"].round(1)
            agg = agg.sort_values("total_mencoes", ascending=False)

            st.markdown(
                '<div class="grafico-container">'
                f'<p class="grafico-titulo">Canais x Saúde ({marca})</p>',
                unsafe_allow_html=True,
            )
            render_tabela_html(
                agg,
                {
                    "canal": "Canal",
                    "total_mencoes": "Menções",
                    "pct_positivo": "% Positivo",
                    "pct_negativo": "% Negativo",
                    "saude_marca_score": "Saúde",
                },
                max_linhas=12,
            )
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if not lc.empty:
            grafico_linha(
                lc, "data_referencia", "total_publicacoes",
                cor=LARANJA, titulo="Evolução Diária de Publicações",
            )
