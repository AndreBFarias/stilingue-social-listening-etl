from typing import Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st

from dashboard.tema import (
    LARANJA, CIANO, VERDE, AMARELO, VERMELHO, CINZA_ESCURO,
    AZUL_ESCURO, BRANCO, CINZA_BORDA, CINZA_LABEL, FONTE_FAMILIA,
    CORES_DADOS, COR_SENTIMENTO, PLOTLY_CONFIG, criar_layout_plotly,
    formatar_numero, formatar_pct,
)


def render_card(titulo: str, valor: str, delta: str = "", cor_delta: str = "") -> None:
    classe_delta = ""
    if cor_delta == "verde":
        classe_delta = "positivo"
    elif cor_delta == "vermelho":
        classe_delta = "negativo"

    delta_html = ""
    if delta:
        delta_html = f'<div class="card-delta {classe_delta}">{delta}</div>'

    st.markdown(
        f"""
        <div class="card-kpi">
            <div class="card-label">{titulo}</div>
            <div class="card-valor">{valor}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def grafico_combo(
    df: pd.DataFrame,
    eixo_x: str,
    col_positivo: str,
    col_neutro: str,
    col_negativo: str,
    col_linha: str,
    titulo: str,
    nome_linha: str = "Score",
    altura: int = 340,
) -> None:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=df[eixo_x], y=df[col_positivo], name="Positivo",
            marker_color=VERDE, marker_cornerradius=4,
            hovertemplate="%{y:,.0f}<extra>Positivo</extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=df[eixo_x], y=df[col_neutro], name="Neutro",
            marker_color=AMARELO, marker_cornerradius=4,
            hovertemplate="%{y:,.0f}<extra>Neutro</extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=df[eixo_x], y=df[col_negativo], name="Negativo",
            marker_color=VERMELHO, marker_cornerradius=4,
            hovertemplate="%{y:,.0f}<extra>Negativo</extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df[eixo_x], y=df[col_linha], name=nome_linha,
            mode="lines+markers",
            line=dict(color=LARANJA, width=3, shape="spline"),
            marker=dict(size=7, color=LARANJA, line=dict(width=2, color=BRANCO)),
            hovertemplate="%{y:.1f}<extra>" + nome_linha + "</extra>",
        ),
        secondary_y=True,
    )

    layout = criar_layout_plotly("", altura)
    fig.update_layout(
        layout,
        barmode="stack",
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.04)", title=None),
        yaxis2=dict(showgrid=False, title=None, overlaying="y", side="right"),
        xaxis=dict(showgrid=False, title=None, type="category"),
    )

    st.markdown(f'<div class="grafico-container"><p class="grafico-titulo">{titulo}</p>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown('</div>', unsafe_allow_html=True)


def grafico_rosca(
    labels: list[str],
    values: list[float],
    cores: list[str] | None = None,
    titulo: str = "",
    altura: int = 320,
) -> None:
    if cores is None:
        cores = CORES_DADOS[:len(labels)]

    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=cores, line=dict(color=BRANCO, width=2)),
            textinfo="label+percent",
            textposition="outside",
            textfont=dict(size=11, family=FONTE_FAMILIA),
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>",
            pull=[0.02] * len(labels),
        )
    ])

    layout = criar_layout_plotly("", altura)
    layout.update(
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    fig.update_layout(layout)

    st.markdown(f'<div class="grafico-container"><p class="grafico-titulo">{titulo}</p>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown('</div>', unsafe_allow_html=True)


def grafico_barras_h(
    df: pd.DataFrame,
    eixo_y: str,
    eixo_x: str,
    cor: str = CIANO,
    titulo: str = "",
    top_n: int = 10,
    altura: int = 340,
) -> None:
    df_top = df.nlargest(top_n, eixo_x).sort_values(eixo_x, ascending=True)

    fig = go.Figure(data=[
        go.Bar(
            y=df_top[eixo_y],
            x=df_top[eixo_x],
            orientation="h",
            marker_color=cor,
            marker_cornerradius=4,
            text=df_top[eixo_x].apply(lambda v: formatar_numero(v)),
            textposition="outside",
            textfont=dict(size=10, family=FONTE_FAMILIA, color=CINZA_ESCURO),
            hovertemplate="<b>%{y}</b>: %{x:,.0f}<extra></extra>",
        )
    ])

    layout = criar_layout_plotly("", altura)
    layout.update(
        xaxis=dict(showticklabels=False, showgrid=False, showline=False),
        yaxis=dict(showgrid=False, showline=False, tickfont=dict(size=11)),
        margin=dict(l=20, r=60, t=20, b=20),
    )
    fig.update_layout(layout)

    st.markdown(f'<div class="grafico-container"><p class="grafico-titulo">{titulo}</p>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown('</div>', unsafe_allow_html=True)


def grafico_linha(
    df: pd.DataFrame,
    eixo_x: str,
    eixo_y: str,
    cor: str = LARANJA,
    titulo: str = "",
    altura: int = 340,
) -> None:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df[eixo_x], y=df[eixo_y],
        mode="lines",
        line=dict(color=cor, width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor=f"rgba({int(cor[1:3],16)},{int(cor[3:5],16)},{int(cor[5:7],16)},0.08)",
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>%{y:,.0f}<extra></extra>",
    ))

    layout = criar_layout_plotly("", altura)
    layout.update(
        xaxis=dict(
            showgrid=False, showline=True, linecolor=CINZA_BORDA,
            tickformat="%d/%m",
        ),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.04)"),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    fig.update_layout(layout)

    st.markdown(f'<div class="grafico-container"><p class="grafico-titulo">{titulo}</p>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown('</div>', unsafe_allow_html=True)


def grafico_barras_empilhadas_h(
    df: pd.DataFrame,
    eixo_y: str,
    col_positivo: str,
    col_neutro: str,
    col_negativo: str,
    titulo: str = "",
    top_n: int = 10,
    altura: int = 340,
) -> None:
    df_agg = df.groupby(eixo_y, as_index=False)[[col_positivo, col_neutro, col_negativo]].sum()
    df_agg["total"] = df_agg[col_positivo] + df_agg[col_neutro] + df_agg[col_negativo]
    df_top = df_agg.nlargest(top_n, "total").sort_values("total", ascending=True)

    fig = go.Figure()
    for col, nome, cor in [
        (col_positivo, "Positivo", VERDE),
        (col_neutro, "Neutro", AMARELO),
        (col_negativo, "Negativo", VERMELHO),
    ]:
        fig.add_trace(go.Bar(
            y=df_top[eixo_y], x=df_top[col], name=nome,
            orientation="h", marker_color=cor, marker_cornerradius=3,
            hovertemplate="<b>%{y}</b><br>" + nome + ": %{x:,.0f}<extra></extra>",
        ))

    layout = criar_layout_plotly("", altura)
    layout.update(
        barmode="stack",
        xaxis=dict(showticklabels=False, showgrid=False, showline=False),
        yaxis=dict(showgrid=False, showline=False, tickfont=dict(size=10)),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    fig.update_layout(layout)

    st.markdown(f'<div class="grafico-container"><p class="grafico-titulo">{titulo}</p>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown('</div>', unsafe_allow_html=True)


def grafico_heatmap(
    df_pivot: pd.DataFrame,
    titulo: str = "",
    altura: int = 350,
) -> None:
    x_labels = [str(c) for c in df_pivot.columns]
    y_labels = [str(r) for r in df_pivot.index]
    z_data = df_pivot.values.tolist()
    z_text = [[round(float(v), 1) if v == v else 0.0 for v in row] for row in df_pivot.values]

    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0, VERMELHO],
            [0.35, "#FDEDEC"],
            [0.5, "#FAFAFA"],
            [0.65, "#EAFAF1"],
            [1, VERDE],
        ],
        zmid=0,
        text=z_text,
        texttemplate="%{text:.1f}",
        textfont=dict(size=10, family=FONTE_FAMILIA),
        hovertemplate="<b>%{y}</b> | %{x}<br>Score: %{z:.1f}<extra></extra>",
        colorbar=dict(
            title=dict(text="Score", font=dict(size=10)),
            tickfont=dict(size=9),
            thickness=12,
            len=0.8,
        ),
    ))

    layout = criar_layout_plotly("", altura)
    layout.update(
        xaxis=dict(showgrid=False, showline=False, side="top", tickfont=dict(size=10), type="category"),
        yaxis=dict(showgrid=False, showline=False, autorange="reversed", tickfont=dict(size=10), type="category"),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    fig.update_layout(layout)

    st.markdown(f'<div class="grafico-container"><p class="grafico-titulo">{titulo}</p>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown('</div>', unsafe_allow_html=True)


def grafico_barras_h_condicional(
    df: pd.DataFrame,
    eixo_y: str,
    eixo_x: str,
    titulo: str = "",
    altura: int = 340,
) -> None:
    df_sorted = df.sort_values(eixo_x, ascending=True)
    cores = [VERDE if v >= 0 else VERMELHO for v in df_sorted[eixo_x]]

    fig = go.Figure(data=[
        go.Bar(
            y=df_sorted[eixo_y],
            x=df_sorted[eixo_x],
            orientation="h",
            marker_color=cores,
            marker_cornerradius=4,
            text=df_sorted[eixo_x].apply(lambda v: f"{v:+.1f}"),
            textposition="outside",
            textfont=dict(size=10, family=FONTE_FAMILIA),
            hovertemplate="<b>%{y}</b>: %{x:.1f}<extra></extra>",
        )
    ])

    layout = criar_layout_plotly("", altura)
    layout.update(
        xaxis=dict(showticklabels=False, showgrid=False, showline=False, zeroline=True, zerolinecolor=CINZA_BORDA),
        yaxis=dict(showgrid=False, showline=False, tickfont=dict(size=11)),
        margin=dict(l=20, r=60, t=20, b=20),
    )
    fig.update_layout(layout)

    st.markdown(f'<div class="grafico-container"><p class="grafico-titulo">{titulo}</p>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown('</div>', unsafe_allow_html=True)


def render_tabela_html(
    df: pd.DataFrame,
    colunas: dict[str, str],
    max_linhas: int = 15,
    col_sentimento: str | None = None,
) -> None:
    html = '<div class="tabela-container"><table class="tabela-estilizada"><thead><tr>'
    for col_original, col_display in colunas.items():
        html += f"<th>{col_display}</th>"
    html += "</tr></thead><tbody>"

    for _, row in df.head(max_linhas).iterrows():
        html += "<tr>"
        for col_original in colunas:
            valor = row.get(col_original, "")
            if col_original == col_sentimento and isinstance(valor, str):
                classe = valor.lower() if valor.lower() in ("positivo", "neutro", "negativo") else ""
                html += f'<td><span class="badge-sentimento {classe}">{valor}</span></td>'
            else:
                if isinstance(valor, float):
                    valor = f"{valor:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
                elif isinstance(valor, str) and len(valor) > 120:
                    valor = valor[:120] + "..."
                html += f"<td>{valor}</td>"
        html += "</tr>"

    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)
