import locale
from typing import Union

import plotly.graph_objects as go
import plotly.io as pio


LARANJA = "#E87722"
CIANO = "#00BCD4"
VERDE = "#2ECC71"
AMARELO = "#F1C40F"
VERMELHO = "#E74C3C"
CINZA_ESCURO = "#4A4A4A"
CINZA_CLARO = "#F5F5F5"
AZUL_ESCURO = "#2C3E50"
ROXO = "#9B59B6"
AZUL = "#3498DB"
BRANCO = "#FFFFFF"
CINZA_BORDA = "#E0E0E0"
CINZA_LABEL = "#888888"
CINZA_TEXTO = "#333333"
AMARELO_NAV = "#F1A91B"

CORES_DADOS = [LARANJA, CIANO, VERDE, AMARELO, VERMELHO, CINZA_ESCURO, ROXO, AZUL]

COR_SENTIMENTO = {
    "Positivo": VERDE,
    "Neutro": AMARELO,
    "Negativo": VERMELHO,
}

FONTE_FAMILIA = "'Inter', 'Segoe UI', 'Roboto', -apple-system, sans-serif"


def formatar_numero(valor: Union[int, float], casas: int = 0) -> str:
    if valor is None:
        return "0"
    if casas == 0:
        return f"{int(valor):,.0f}".replace(",", ".")
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_pct(valor: Union[int, float], casas: int = 1) -> str:
    if valor is None:
        return "0%"
    formatado = f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{formatado}%"


def formatar_milhoes(valor: Union[int, float]) -> str:
    if valor is None:
        return "0"
    if abs(valor) >= 1_000_000_000:
        return f"{valor / 1_000_000_000:,.1f} Bi".replace(",", "X").replace(".", ",").replace("X", ".")
    if abs(valor) >= 1_000_000:
        return f"{valor / 1_000_000:,.1f} Mi".replace(",", "X").replace(".", ",").replace("X", ".")
    if abs(valor) >= 1_000:
        return f"{valor / 1_000:,.1f} mil".replace(",", "X").replace(".", ",").replace("X", ".")
    return formatar_numero(valor)


def criar_layout_plotly(titulo: str = "", altura: int = 350) -> go.Layout:
    return go.Layout(
        title=dict(
            text=titulo,
            font=dict(family=FONTE_FAMILIA, size=14, color=CINZA_ESCURO),
            x=0.02,
            y=0.97,
        ),
        font=dict(family=FONTE_FAMILIA, size=11, color=CINZA_ESCURO),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=altura,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor=CINZA_BORDA,
            tickfont=dict(size=10, color="#666666"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.05)",
            showline=False,
            tickfont=dict(size=10, color="#666666"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
        ),
        hoverlabel=dict(
            bgcolor=BRANCO,
            bordercolor=CINZA_BORDA,
            font=dict(family=FONTE_FAMILIA, size=12, color=CINZA_ESCURO),
        ),
    )


PLOTLY_CONFIG = {
    "displayModeBar": False,
    "staticPlot": False,
    "responsive": True,
}
