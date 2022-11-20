import sys
from datetime import date
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

BASE_DIR = _PROJECT_ROOT

STORYTELLING = {
    "Overview": (
        "Como está a percepção da marca nas redes sociais? "
        "Visão executiva com indicadores-chave de marca, volume e sentimento."
    ),
    "Midia": (
        "Onde investir esforço de comunicação? Análise de volume e engajamento por canal, "
        "saúde da marca por canal e evolução diária de publicações."
    ),
    "Canais de Atendimento": (
        "Como a marca principal se compara aos concorrentes? "
        "Benchmark de saúde da marca, favorabilidade e polaridade de sentimento."
    ),
    "SAC / Social Listening": (
        "Quais posts precisam de atenção imediata? "
        "Identifique publicações de alto risco, temas em crise e padrões de sentimento por tema."
    ),
}

TITULOS = {
    "Overview": "Social Listening — Visão Executiva",
    "Midia": "Social Listening — Mídia",
    "Canais de Atendimento": "Social Listening — Sentimento por Marca",
    "SAC / Social Listening": "Social Listening — Publicações e Temas",
}


def _carregar_css() -> None:
    css_path = Path(__file__).parent / "style.css"
    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _render_header_com_slicer(
    titulo_pagina: str,
    storytelling: str,
    data_min: date,
    data_max: date,
) -> tuple[date, date]:
    col_titulo, col_slicer = st.columns([5, 4])

    with col_titulo:
        st.markdown(
            f'<div class="header-titulo">{titulo_pagina}</div>',
            unsafe_allow_html=True,
        )
    with col_slicer:
        periodo = st.slider(
            "Período",
            min_value=data_min,
            max_value=data_max,
            value=(data_min, data_max),
            format="DD/MM/YYYY",
            key="slicer_periodo",
            label_visibility="collapsed",
        )

    st.markdown(
        f'<p class="storytelling">{storytelling}</p>',
        unsafe_allow_html=True,
    )

    return periodo


def _render_navegacao() -> str:
    from dashboard.tema import CIANO, LARANJA, AMARELO_NAV, AZUL_ESCURO

    paginas = {
        "Overview": AZUL_ESCURO,
        "Midia": CIANO,
        "Canais de Atendimento": LARANJA,
        "SAC / Social Listening": AMARELO_NAV,
    }

    if "pagina_ativa" not in st.session_state:
        st.session_state["pagina_ativa"] = "Overview"

    cols = st.columns(len(paginas))
    for i, (nome, cor) in enumerate(paginas.items()):
        with cols[i]:
            ativa = st.session_state["pagina_ativa"] == nome
            borda = f"3px solid {cor}" if ativa else "3px solid transparent"
            opacidade = "1" if ativa else "0.75"
            st.markdown(
                f"""
                <style>
                    div[data-testid="stHorizontalBlock"] > div:nth-child({i+1}) > div > .stButton > button {{
                        background-color: {cor};
                        opacity: {opacidade};
                        border-bottom: {borda};
                    }}
                </style>
                """,
                unsafe_allow_html=True,
            )
            if st.button(nome, key=f"nav_{nome}", use_container_width=True):
                st.session_state["pagina_ativa"] = nome
                st.rerun()

    return st.session_state["pagina_ativa"]


def main() -> None:
    st.set_page_config(
        page_title="Social Listening Dashboard",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    _carregar_css()

    from dashboard.dados import carregar_todos, filtrar_por_periodo
    from dashboard.paginas import overview, midia, sentimento, publicacoes

    dados = carregar_todos()

    vg = dados["visao_geral"]
    data_min = vg["data_referencia"].min().date()
    data_max = vg["data_referencia"].max().date()

    pagina_ativa = st.session_state.get("pagina_ativa", "Overview")

    periodo = _render_header_com_slicer(
        TITULOS.get(pagina_ativa, ""),
        STORYTELLING.get(pagina_ativa, ""),
        data_min,
        data_max,
    )

    pagina_ativa = _render_navegacao()

    dados_filtrados = filtrar_por_periodo(dados, periodo[0], periodo[1])

    st.markdown(
        "<hr style='margin:0.2rem 0 0.6rem 0;border:none;border-top:1px solid #E0E0E0'>",
        unsafe_allow_html=True,
    )

    pagina_map = {
        "Overview": overview.render,
        "Midia": midia.render,
        "Canais de Atendimento": sentimento.render,
        "SAC / Social Listening": publicacoes.render,
    }

    render_fn = pagina_map.get(pagina_ativa)
    if render_fn:
        render_fn(dados_filtrados)


if __name__ == "__main__":
    main()
