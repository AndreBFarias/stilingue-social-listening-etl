from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
CONSOLIDADO_DIR = BASE_DIR / "consolidado"

import os

_marcas_excluir_env = os.getenv("MARCAS_EXCLUIR", "")
MARCAS_EXCLUIR = set(m.strip() for m in _marcas_excluir_env.split(",") if m.strip())


@st.cache_data(show_spinner="Carregando visao_geral...")
def carregar_visao_geral() -> pd.DataFrame:
    df = pd.read_csv(
        CONSOLIDADO_DIR / "visao_geral.csv",
        sep=";",
        encoding="utf-8",
        dtype=str,
    )
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], dayfirst=True)
    df["data_extracao"] = pd.to_datetime(df["data_extracao"], dayfirst=True, errors="coerce")

    colunas_num = [
        "publicacoes_coletadas", "total_usuarios", "alcance_potencial",
        "sentimento_negativo_qtd", "sentimento_neutro_qtd", "sentimento_positivo_qtd",
        "canal_twitter", "canal_facebook", "canal_noticias",
        "canal_instagram", "canal_youtube", "canal_blogs",
    ]
    for col in colunas_num:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    colunas_float = [
        "variacao_publicacoes_pct", "variacao_usuarios_pct",
        "variacao_alcance_pct", "indice_sentimento", "variacao_sentimento_pts",
    ]
    for col in colunas_float:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["mes_ano"] = df["data_referencia"].dt.to_period("M").astype(str)
    return df.sort_values("data_referencia").reset_index(drop=True)


@st.cache_data(show_spinner="Carregando sentimento_grupos...")
def carregar_sentimento_grupos() -> pd.DataFrame:
    df = pd.read_csv(
        CONSOLIDADO_DIR / "sentimento_grupos.csv",
        sep=";",
        encoding="utf-8",
        dtype=str,
    )
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], dayfirst=True)

    colunas_int = ["qtd_positivo", "qtd_neutro", "qtd_negativo", "total_mencoes"]
    for col in colunas_int:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    colunas_float = ["pct_positivo", "pct_neutro", "pct_negativo", "saude_marca_score"]
    for col in colunas_float:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df = df[~df["marca"].isin(MARCAS_EXCLUIR)].copy()
    df["mes_ano"] = df["data_referencia"].dt.to_period("M").astype(str)
    return df.sort_values("data_referencia").reset_index(drop=True)


@st.cache_data(show_spinner="Carregando sentimento_temas...")
def carregar_sentimento_temas() -> pd.DataFrame:
    df = pd.read_csv(
        CONSOLIDADO_DIR / "sentimento_temas.csv",
        sep=";",
        encoding="utf-8",
        dtype=str,
    )
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], dayfirst=True)

    colunas_int = ["qtd_positivo", "qtd_neutro", "qtd_negativo", "total_mencoes"]
    for col in colunas_int:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    colunas_float = ["pct_positivo", "pct_neutro", "pct_negativo"]
    for col in colunas_float:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["categoria_tema"] = df["tema"].apply(
        lambda t: t.split("_")[0] if isinstance(t, str) and "_" in t else t
    )
    df["mes_ano"] = df["data_referencia"].dt.to_period("M").astype(str)
    return df.sort_values("data_referencia").reset_index(drop=True)


@st.cache_data(show_spinner="Carregando linechart...")
def carregar_linechart() -> pd.DataFrame:
    df = pd.read_csv(
        CONSOLIDADO_DIR / "linechart.csv",
        sep=";",
        encoding="utf-8",
        dtype=str,
    )
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], dayfirst=True)
    df["total_publicacoes"] = pd.to_numeric(df["total_publicacoes"], errors="coerce").fillna(0).astype(int)
    df["mes_ano"] = df["data_referencia"].dt.to_period("M").astype(str)
    return df.sort_values("data_referencia").reset_index(drop=True)


@st.cache_data(show_spinner="Carregando publicacoes (165k registros)...")
def carregar_publicacoes() -> pd.DataFrame:
    df = pd.read_csv(
        CONSOLIDADO_DIR / "publicacoes.csv",
        sep=";",
        encoding="utf-8",
        dtype=str,
        on_bad_lines="skip",
    )
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], dayfirst=True, errors="coerce")
    df["data_publicacao"] = pd.to_datetime(df["data_publicacao"], dayfirst=True, errors="coerce")

    colunas_int = ["interacoes", "curtidas", "comentarios", "compartilhamentos", "seguidores_autor"]
    for col in colunas_int:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["sentimento_num"] = pd.to_numeric(df["sentimento_num"], errors="coerce").fillna(0).astype(int)
    df["score_aaa"] = pd.to_numeric(df["score_aaa"], errors="coerce").fillna(0.0)

    df["mes_ano"] = df["data_referencia"].dt.to_period("M").astype(str)
    return df.sort_values("data_referencia", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner="Carregando ranking_evolutivo...")
def carregar_ranking_evolutivo() -> pd.DataFrame:
    df = pd.read_csv(
        CONSOLIDADO_DIR / "ranking_evolutivo.csv",
        sep=";",
        encoding="utf-8",
        dtype=str,
    )
    df["data_referencia"] = pd.to_datetime(df["data_referencia"], dayfirst=True)
    df["posicao_ranking"] = pd.to_numeric(df["posicao_ranking"], errors="coerce").fillna(0).astype(int)
    df["total_mencoes"] = pd.to_numeric(df["total_mencoes"], errors="coerce").fillna(0).astype(int)
    df["mes_ano"] = df["data_referencia"].dt.to_period("M").astype(str)
    return df.sort_values("data_referencia").reset_index(drop=True)


def carregar_todos() -> dict[str, pd.DataFrame]:
    return {
        "visao_geral": carregar_visao_geral(),
        "sentimento_grupos": carregar_sentimento_grupos(),
        "sentimento_temas": carregar_sentimento_temas(),
        "linechart": carregar_linechart(),
        "publicacoes": carregar_publicacoes(),
        "ranking_evolutivo": carregar_ranking_evolutivo(),
    }


def filtrar_por_periodo(
    dados: dict[str, pd.DataFrame],
    data_inicio: Any,
    data_fim: Any,
) -> dict[str, pd.DataFrame]:
    inicio = pd.Timestamp(data_inicio)
    fim = pd.Timestamp(data_fim)
    filtrados = {}
    for nome, df in dados.items():
        if "data_referencia" in df.columns:
            mask = (df["data_referencia"] >= inicio) & (df["data_referencia"] <= fim)
            filtrados[nome] = df.loc[mask].copy()
        else:
            filtrados[nome] = df.copy()
    return filtrados
