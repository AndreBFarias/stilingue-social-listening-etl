"""Gera relatorios HTML estaticos a partir dos CSVs consolidados.

Cada HTML e self-contained (Plotly JS via CDN) e abre direto no navegador.
Reutiliza os modulos dashboard.dados, dashboard.metricas e dashboard.tema.
"""
import sys
from pathlib import Path

PROJETO_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJETO_DIR))

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard.tema import (
    LARANJA, CIANO, VERDE, AMARELO, VERMELHO, CINZA_ESCURO,
    AZUL_ESCURO, BRANCO, FONTE_FAMILIA, CORES_DADOS,
    formatar_numero, formatar_pct, formatar_milhoes,
)

RELATORIOS_DIR = PROJETO_DIR / "relatorios"
CONSOLIDADO_DIR = PROJETO_DIR / "consolidado"

MESES_PT = {
    "01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr",
    "05": "Mai", "06": "Jun", "07": "Jul", "08": "Ago",
    "09": "Set", "10": "Out", "11": "Nov", "12": "Dez",
}

NAV_PAGINAS = [
    ("01_overview.html", "Overview"),
    ("02_midia.html", "Midia"),
    ("03_sentimento.html", "Sentimento"),
    ("04_publicacoes.html", "Publicacoes"),
]

CSS_INLINE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
body { font-family: 'Inter', sans-serif; background: #F5F5F5; margin: 0; padding: 1.5rem 3rem; color: #2C3E50; }
h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.3rem; }
.storytelling { font-size: 0.82rem; color: #888; font-style: italic; margin-bottom: 1rem; }
.nav { display: flex; gap: 0.5rem; margin-bottom: 1.2rem; }
.nav a { text-decoration: none; padding: 0.5rem 1.5rem; border-radius: 8px; color: white; font-weight: 600;
         font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.4px; }
.nav a.active { opacity: 1; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.nav a:not(.active) { opacity: 0.7; }
.cards { display: flex; gap: 1rem; margin-bottom: 1.2rem; flex-wrap: wrap; }
.card { background: white; border-radius: 12px; padding: 1rem 1.2rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        text-align: center; flex: 1; min-width: 140px; }
.card .label { font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 0.3rem; }
.card .valor { font-size: 1.5rem; font-weight: 700; color: #2C3E50; }
.card .delta { font-size: 0.72rem; font-weight: 500; }
.delta.pos { color: #2ECC71; } .delta.neg { color: #E74C3C; }
.row { display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
.col { flex: 1; min-width: 300px; }
.chart-box { background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.chart-title { font-size: 0.85rem; font-weight: 600; color: #4A4A4A; margin: 0 0 0.5rem 0.3rem; }
hr { border: none; border-top: 1px solid #E0E0E0; margin: 0.5rem 0 1rem 0; }
</style>
"""


def _label_mes(mes_ano: str) -> str:
    partes = str(mes_ano).split("-")
    if len(partes) == 2:
        return f"{MESES_PT.get(partes[1], partes[1])}/{partes[0][2:]}"
    return str(mes_ano)


def _carregar_dados() -> dict[str, pd.DataFrame]:
    def _ler(nome: str) -> pd.DataFrame:
        df = pd.read_csv(CONSOLIDADO_DIR / f"{nome}.csv", sep=";", encoding="utf-8", dtype=str)
        if "data_referencia" in df.columns:
            df["data_referencia"] = pd.to_datetime(df["data_referencia"], dayfirst=True)
        return df

    sg = _ler("sentimento_grupos")
    for col in ["qtd_positivo", "qtd_neutro", "qtd_negativo", "total_mencoes"]:
        sg[col] = pd.to_numeric(sg[col], errors="coerce").fillna(0).astype(int)
    sg["saude_marca_score"] = pd.to_numeric(sg["saude_marca_score"], errors="coerce").fillna(0.0)
    sg["mes_ano"] = sg["data_referencia"].dt.to_period("M").astype(str)

    vg = _ler("visao_geral")
    for col in ["publicacoes_coletadas", "alcance_potencial", "sentimento_negativo_qtd", "sentimento_neutro_qtd", "sentimento_positivo_qtd"]:
        vg[col] = pd.to_numeric(vg[col], errors="coerce").fillna(0).astype(int)
    vg["indice_sentimento"] = pd.to_numeric(vg["indice_sentimento"], errors="coerce").fillna(0.0)

    pub = _ler("publicacoes")
    for col in ["interacoes", "curtidas", "comentarios", "compartilhamentos", "seguidores_autor"]:
        if col in pub.columns:
            pub[col] = pd.to_numeric(pub[col], errors="coerce").fillna(0).astype(int)

    lc = _ler("linechart")
    lc["total_publicacoes"] = pd.to_numeric(lc["total_publicacoes"], errors="coerce").fillna(0).astype(int)

    re = _ler("ranking_evolutivo")
    re["posicao_ranking"] = pd.to_numeric(re["posicao_ranking"], errors="coerce").fillna(0).astype(int)
    re["total_mencoes"] = pd.to_numeric(re["total_mencoes"], errors="coerce").fillna(0).astype(int)

    st_t = _ler("sentimento_temas")
    for col in ["qtd_positivo", "qtd_neutro", "qtd_negativo", "total_mencoes"]:
        st_t[col] = pd.to_numeric(st_t[col], errors="coerce").fillna(0).astype(int)
    st_t["pct_negativo"] = pd.to_numeric(st_t["pct_negativo"], errors="coerce").fillna(0.0)
    st_t["categoria_tema"] = st_t["tema"].apply(
        lambda t: t.split("_")[0] if isinstance(t, str) and "_" in t else t
    )

    return {
        "visao_geral": vg, "sentimento_grupos": sg, "linechart": lc,
        "publicacoes": pub, "ranking_evolutivo": re, "sentimento_temas": st_t,
    }


def _nav_html(ativo: str) -> str:
    cores = {"Overview": AZUL_ESCURO, "Midia": CIANO, "Sentimento": LARANJA, "Publicacoes": "#F1A91B"}
    links = []
    for arquivo, nome in NAV_PAGINAS:
        cor = cores.get(nome, CINZA_ESCURO)
        classe = "active" if nome == ativo else ""
        links.append(f'<a href="{arquivo}" class="{classe}" style="background:{cor}">{nome}</a>')
    return f'<div class="nav">{"".join(links)}</div>'


def _card_html(titulo: str, valor: str, delta: str = "") -> str:
    delta_html = ""
    if delta:
        classe = "pos" if delta.startswith("+") else "neg"
        delta_html = f'<div class="delta {classe}">{delta}</div>'
    return f'<div class="card"><div class="label">{titulo}</div><div class="valor">{valor}</div>{delta_html}</div>'


def _fig_to_div(fig: go.Figure) -> str:
    return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})


def _pagina_html(titulo: str, nav_ativo: str, storytelling: str, corpo: str) -> str:
    nav = _nav_html(nav_ativo)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo}</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
{CSS_INLINE}
</head>
<body>
<h1>{titulo}</h1>
<p class="storytelling">{storytelling}</p>
{nav}
<hr>
{corpo}
</body>
</html>"""


def gerar_overview(dados: dict[str, pd.DataFrame]) -> None:
    vg = dados["visao_geral"]
    sg = dados["sentimento_grupos"]
    pub = dados["publicacoes"]

    vol = int(vg["publicacoes_coletadas"].sum())
    alcance = int(vg.iloc[-1]["alcance_potencial"]) if not vg.empty else 0
    interacoes = int(pub["interacoes"].sum()) if "interacoes" in pub.columns else 0

    cards = '<div class="cards">'
    cards += _card_html("Volume Publicacoes", formatar_numero(vol))
    cards += _card_html("Alcance Potencial", formatar_milhoes(alcance))
    cards += _card_html("Total Interacoes", formatar_milhoes(interacoes))
    cards += '</div>'

    sg_all = sg[sg["canal"] == "all"]
    pos = int(sg_all["qtd_positivo"].sum())
    neu = int(sg_all["qtd_neutro"].sum())
    neg = int(sg_all["qtd_negativo"].sum())

    fig_rosca = go.Figure(data=[go.Pie(
        labels=["Positivo", "Neutro", "Negativo"], values=[pos, neu, neg],
        hole=0.55, marker=dict(colors=[VERDE, AMARELO, VERMELHO]),
        textinfo="label+percent",
    )])
    fig_rosca.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20), showlegend=False,
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    corpo = cards
    corpo += '<div class="row"><div class="col"><div class="chart-box">'
    corpo += '<p class="chart-title">Sentimento Geral</p>'
    corpo += _fig_to_div(fig_rosca) + '</div></div></div>'

    html = _pagina_html("Social Listening -- Visao Executiva", "Overview",
                        "Visao executiva com indicadores-chave de marca, volume e sentimento.", corpo)
    (RELATORIOS_DIR / "01_overview.html").write_text(html, encoding="utf-8")


def gerar_midia(dados: dict[str, pd.DataFrame]) -> None:
    pub = dados["publicacoes"]
    lc = dados["linechart"]

    posts = len(pub)
    engaj = round(pub["interacoes"].sum() / max(posts, 1), 1)
    curtidas = int(pub["curtidas"].sum())

    cards = '<div class="cards">'
    cards += _card_html("Total Posts", formatar_numero(posts))
    cards += _card_html("Engajamento/Post", formatar_numero(engaj, 0))
    cards += _card_html("Total Curtidas", formatar_milhoes(curtidas))
    cards += '</div>'

    fig_linha = go.Figure()
    fig_linha.add_trace(go.Scatter(
        x=lc["data_referencia"], y=lc["total_publicacoes"],
        mode="lines", line=dict(color=LARANJA, width=2.5),
        fill="tozeroy", fillcolor="rgba(232,119,34,0.08)",
    ))
    fig_linha.update_layout(height=350, margin=dict(l=40, r=20, t=30, b=40),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(tickformat="%d/%m"), yaxis=dict(gridcolor="rgba(0,0,0,0.05)"))

    corpo = cards
    corpo += '<div class="row"><div class="col"><div class="chart-box">'
    corpo += '<p class="chart-title">Evolucao Diaria de Publicacoes</p>'
    corpo += _fig_to_div(fig_linha) + '</div></div></div>'

    html = _pagina_html("Social Listening -- Midia", "Midia",
                        "Volume e engajamento por canal, evolucao diaria de publicacoes.", corpo)
    (RELATORIOS_DIR / "02_midia.html").write_text(html, encoding="utf-8")


def gerar_sentimento(dados: dict[str, pd.DataFrame]) -> None:
    sg = dados["sentimento_grupos"]
    sg_all = sg[sg["canal"] == "all"]

    ranking = sg_all.groupby("marca", as_index=False).agg(
        saude_media=("saude_marca_score", "mean"),
    ).round(1).sort_values("saude_media", ascending=True)

    cores = [VERDE if v >= 0 else VERMELHO for v in ranking["saude_media"]]

    fig_rank = go.Figure(data=[go.Bar(
        y=ranking["marca"], x=ranking["saude_media"],
        orientation="h", marker_color=cores,
        text=ranking["saude_media"].apply(lambda v: f"{v:+.1f}"),
        textposition="outside",
    )])
    fig_rank.update_layout(height=350, margin=dict(l=20, r=60, t=30, b=20),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(showticklabels=False, showgrid=False, zeroline=True),
                           yaxis=dict(showgrid=False))

    corpo = '<div class="row"><div class="col"><div class="chart-box">'
    corpo += '<p class="chart-title">Ranking Saude da Marca</p>'
    corpo += _fig_to_div(fig_rank) + '</div></div></div>'

    html = _pagina_html("Social Listening -- Sentimento por Marca", "Sentimento",
                        "Benchmark de saude da marca entre concorrentes.", corpo)
    (RELATORIOS_DIR / "03_sentimento.html").write_text(html, encoding="utf-8")


def gerar_publicacoes(dados: dict[str, pd.DataFrame]) -> None:
    st_t = dados["sentimento_temas"]

    agg = st_t.groupby("categoria_tema", as_index=False)[["qtd_positivo", "qtd_neutro", "qtd_negativo"]].sum()
    agg["total"] = agg["qtd_positivo"] + agg["qtd_neutro"] + agg["qtd_negativo"]
    agg = agg.nlargest(10, "total").sort_values("total", ascending=True)

    fig_temas = go.Figure()
    for col, nome, cor in [("qtd_positivo", "Positivo", VERDE), ("qtd_neutro", "Neutro", AMARELO), ("qtd_negativo", "Negativo", VERMELHO)]:
        fig_temas.add_trace(go.Bar(y=agg["categoria_tema"], x=agg[col], name=nome, orientation="h", marker_color=cor))
    fig_temas.update_layout(barmode="stack", height=400, margin=dict(l=20, r=20, t=30, b=20),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(showticklabels=False, showgrid=False),
                            yaxis=dict(showgrid=False),
                            legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0.5, xanchor="center"))

    corpo = '<div class="row"><div class="col"><div class="chart-box">'
    corpo += '<p class="chart-title">Top Temas por Sentimento</p>'
    corpo += _fig_to_div(fig_temas) + '</div></div></div>'

    html = _pagina_html("Social Listening -- Publicacoes e Temas", "Publicacoes",
                        "Temas em crise e padroes de sentimento por tema.", corpo)
    (RELATORIOS_DIR / "04_publicacoes.html").write_text(html, encoding="utf-8")


def gerar_relatorios() -> None:
    from loguru import logger
    RELATORIOS_DIR.mkdir(exist_ok=True)
    logger.info("Gerando relatorios HTML estaticos...")
    dados = _carregar_dados()
    gerar_overview(dados)
    logger.info("  01_overview.html")
    gerar_midia(dados)
    logger.info("  02_midia.html")
    gerar_sentimento(dados)
    logger.info("  03_sentimento.html")
    gerar_publicacoes(dados)
    logger.info("  04_publicacoes.html")
    logger.info(f"Relatorios gerados em {RELATORIOS_DIR}")


if __name__ == "__main__":
    gerar_relatorios()
