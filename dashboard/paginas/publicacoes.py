import pandas as pd
import streamlit as st

from dashboard.componentes import (
    render_card, grafico_barras_empilhadas_h, render_tabela_html,
)
from dashboard.metricas import (
    total_posts, engajamento_por_post, posts_alto_risco, indice_crise,
)
from dashboard.tema import (
    formatar_numero, VERMELHO,
)


def render(dados: dict[str, pd.DataFrame]) -> None:
    pub = dados["publicacoes"]
    st_temas = dados["sentimento_temas"]

    n_posts = total_posts(pub)
    engaj = engajamento_por_post(pub)
    alto_risco = posts_alto_risco(pub)
    crise = indice_crise(st_temas)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_card("Total Posts", formatar_numero(n_posts))
    with c2:
        render_card("Engajamento/Post", formatar_numero(engaj, 0))
    with c3:
        cor = "vermelho" if alto_risco > 0 else ""
        render_card("Posts Alto Risco", formatar_numero(alto_risco), cor_delta=cor)
    with c4:
        cor_crise = "vermelho" if crise > 0 else ""
        render_card("Índice de Crise", formatar_numero(crise), cor_delta=cor_crise)

    st.markdown("<div style='height: 0.6rem'></div>", unsafe_allow_html=True)

    pub_filtrado = _render_filtros(pub)

    st.markdown("<div style='height: 0.4rem'></div>", unsafe_allow_html=True)

    _render_tabela_publicacoes(pub_filtrado)

    st.markdown("<div style='height: 0.8rem'></div>", unsafe_allow_html=True)

    _render_temas(st_temas)


def _render_filtros(pub: pd.DataFrame) -> pd.DataFrame:
    st.markdown(
        '<div style="display:flex;gap:1rem;margin-bottom:-0.5rem">'
        '<div style="flex:1"><p class="grafico-titulo">Marca</p></div>'
        '<div style="flex:1"><p class="grafico-titulo">Sentimento</p></div>'
        '<div style="flex:1"><p class="grafico-titulo">Canal</p></div>'
        '<div style="flex:1"><p class="grafico-titulo">Tema</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        marcas = ["Todas"] + sorted(pub["marca"].dropna().unique().tolist())
        marca_sel = st.selectbox("Marca", marcas, key="filtro_marca", label_visibility="collapsed")
    with c2:
        sentimentos = ["Todos", "Positivo", "Neutro", "Negativo"]
        sent_sel = st.selectbox("Sentimento", sentimentos, key="filtro_sentimento", label_visibility="collapsed")
    with c3:
        canais = ["Todos"] + sorted(pub["canal"].dropna().unique().tolist())
        canal_sel = st.selectbox("Canal", canais, key="filtro_canal", label_visibility="collapsed")
    with c4:
        temas_raw = pub["temas"].dropna().str.split("|").explode().str.strip()
        temas_unicos = sorted(temas_raw[temas_raw != ""].unique().tolist())
        temas_opcoes = ["Todos"] + temas_unicos[:50]
        tema_sel = st.selectbox("Tema", temas_opcoes, key="filtro_tema", label_visibility="collapsed")

    filtrado = pub.copy()
    if marca_sel != "Todas":
        filtrado = filtrado[filtrado["marca"] == marca_sel]
    if sent_sel != "Todos":
        filtrado = filtrado[filtrado["sentimento"] == sent_sel]
    if canal_sel != "Todos":
        filtrado = filtrado[filtrado["canal"] == canal_sel]
    if tema_sel != "Todos":
        filtrado = filtrado[filtrado["temas"].str.contains(tema_sel, case=False, na=False)]

    return filtrado


def _render_tabela_publicacoes(pub: pd.DataFrame) -> None:
    total = len(pub)
    linhas_por_pagina = 15

    if total == 0:
        st.info("Nenhuma publicação encontrada com os filtros selecionados.")
        return

    total_paginas = max(1, (total + linhas_por_pagina - 1) // linhas_por_pagina)

    pagina = 1
    if total_paginas > 1:
        _, col_pag, _ = st.columns([5, 2, 5])
        with col_pag:
            pagina = st.number_input(
                f"Página (de {total_paginas})",
                min_value=1, max_value=total_paginas, value=1,
                key="pagina_pub",
            )

    inicio = (pagina - 1) * linhas_por_pagina
    fatia = pub.iloc[inicio:inicio + linhas_por_pagina].copy()

    if "data_publicacao" in fatia.columns:
        fatia["data_fmt"] = fatia["data_publicacao"].dt.strftime("%d/%m/%Y %H:%M").fillna("")
    else:
        fatia["data_fmt"] = ""

    if "texto" in fatia.columns:
        fatia["texto_curto"] = fatia["texto"].fillna("").str[:150]
    else:
        fatia["texto_curto"] = ""

    fatia["interacoes_fmt"] = fatia["interacoes"].apply(lambda v: formatar_numero(v))
    fatia["seguidores_fmt"] = fatia["seguidores_autor"].apply(lambda v: formatar_numero(v))

    render_tabela_html(
        fatia,
        {
            "data_fmt": "Data",
            "marca": "Marca",
            "sentimento": "Sentimento",
            "canal": "Canal",
            "texto_curto": "Texto",
            "interacoes_fmt": "Interações",
            "seguidores_fmt": "Seguidores",
        },
        max_linhas=linhas_por_pagina,
        col_sentimento="sentimento",
    )

    if total_paginas > 1:
        st.markdown(
            f'<p style="font-size:0.72rem;color:#AAA;text-align:center">'
            f"Página {pagina} de {total_paginas}</p>",
            unsafe_allow_html=True,
        )


def _render_temas(st_temas: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)

    with col1:
        if not st_temas.empty:
            grafico_barras_empilhadas_h(
                st_temas,
                eixo_y="categoria_tema",
                col_positivo="qtd_positivo",
                col_neutro="qtd_neutro",
                col_negativo="qtd_negativo",
                titulo="Top Temas por Sentimento",
                top_n=10,
            )

    with col2:
        if not st_temas.empty:
            agg = st_temas.groupby("tema", as_index=False).agg(
                total_mencoes=("total_mencoes", "sum"),
                qtd_negativo=("qtd_negativo", "sum"),
            )
            agg["pct_negativo"] = (agg["qtd_negativo"] / agg["total_mencoes"] * 100).round(1)
            crise = agg[agg["pct_negativo"] >= 70].sort_values("qtd_negativo", ascending=False)

            if not crise.empty:
                st.markdown(
                    '<div class="grafico-container">'
                    '<p class="grafico-titulo">Temas de Crise (% Negativo >= 70%)</p>',
                    unsafe_allow_html=True,
                )
                render_tabela_html(
                    crise,
                    {
                        "tema": "Tema",
                        "total_mencoes": "Menções",
                        "pct_negativo": "% Negativo",
                    },
                    max_linhas=12,
                )
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Nenhum tema com mais de 70% de sentimento negativo.")
