import os

import pandas as pd

MARCA_PRINCIPAL = os.getenv("MARCA_PRINCIPAL", "")
MARCAS_BENCHMARK = set(os.getenv("MARCAS_BENCHMARK", "Mar Aberto").split(","))


def _detectar_marca_principal(sg: pd.DataFrame) -> str:
    if MARCA_PRINCIPAL:
        return MARCA_PRINCIPAL
    filtro = sg[sg["canal"] == "all"]
    if filtro.empty:
        return ""
    top = filtro.groupby("marca")["total_mencoes"].sum().idxmax()
    return str(top)


def saude_marca(sg: pd.DataFrame) -> float:
    marca = _detectar_marca_principal(sg)
    filtro = sg[(sg["canal"] == "all") & (sg["marca"] == marca)]
    if filtro.empty:
        return 0.0
    return round(filtro["saude_marca_score"].mean(), 2)


def saude_concorrentes(sg: pd.DataFrame) -> float:
    marca = _detectar_marca_principal(sg)
    excluir = {marca} | MARCAS_BENCHMARK
    filtro = sg[(sg["canal"] == "all") & (~sg["marca"].isin(excluir))]
    if filtro.empty:
        return 0.0
    return round(filtro["saude_marca_score"].mean(), 2)


def volume_publicacoes(vg: pd.DataFrame) -> int:
    return int(vg["publicacoes_coletadas"].sum())


def alcance_potencial(vg: pd.DataFrame) -> int:
    if vg.empty:
        return 0
    ultima = vg["data_referencia"].max()
    return int(vg[vg["data_referencia"] == ultima]["alcance_potencial"].sum())


def total_interacoes(pub: pd.DataFrame) -> int:
    return int(pub["interacoes"].sum())


def media_diaria_publicacoes(vg: pd.DataFrame) -> int:
    if vg.empty:
        return 0
    dias = vg["data_referencia"].nunique()
    if dias == 0:
        return 0
    return int(vg["publicacoes_coletadas"].sum() / dias)


def posicao_ranking(re: pd.DataFrame) -> int:
    if re.empty:
        return 0
    ultima = re["data_referencia"].max()
    marca = MARCA_PRINCIPAL if MARCA_PRINCIPAL else ""
    if marca:
        filtro = re[(re["data_referencia"] == ultima) & (re["marca"].str.contains(marca, case=False, na=False))]
    else:
        filtro = re[re["data_referencia"] == ultima].nsmallest(1, "posicao_ranking")
    if filtro.empty:
        return 0
    return int(filtro["posicao_ranking"].min())


def favorabilidade_pct(sg: pd.DataFrame, marca: str | None = None) -> float:
    filtro = sg[sg["canal"] == "all"]
    if marca:
        filtro = filtro[filtro["marca"] == marca]
    pos = filtro["qtd_positivo"].sum()
    neg = filtro["qtd_negativo"].sum()
    total = filtro["total_mencoes"].sum()
    if total == 0:
        return 0.0
    return round((pos - neg) / total * 100, 2)


def variacao_saude_mom(sg: pd.DataFrame) -> float:
    marca = _detectar_marca_principal(sg)
    filtro = sg[(sg["canal"] == "all") & (sg["marca"] == marca)]
    if filtro.empty:
        return 0.0
    filtro = filtro.copy()
    filtro["mes"] = filtro["data_referencia"].dt.to_period("M")
    meses = sorted(filtro["mes"].unique())
    if len(meses) < 2:
        return 0.0
    mes_atual = meses[-1]
    mes_anterior = meses[-2]
    saude_atual = filtro[filtro["mes"] == mes_atual]["saude_marca_score"].mean()
    saude_anterior = filtro[filtro["mes"] == mes_anterior]["saude_marca_score"].mean()
    return round(saude_atual - saude_anterior, 2)


def total_posts(pub: pd.DataFrame) -> int:
    return len(pub)


def engajamento_por_post(pub: pd.DataFrame) -> float:
    if pub.empty:
        return 0.0
    return round(pub["interacoes"].sum() / len(pub), 1)


def total_curtidas(pub: pd.DataFrame) -> int:
    return int(pub["curtidas"].sum())


def total_comentarios(pub: pd.DataFrame) -> int:
    return int(pub["comentarios"].sum())


def total_compartilhamentos(pub: pd.DataFrame) -> int:
    return int(pub["compartilhamentos"].sum())


def share_of_voice(sg: pd.DataFrame) -> float:
    marca = _detectar_marca_principal(sg)
    filtro = sg[sg["canal"] == "all"]
    total_geral = filtro["total_mencoes"].sum()
    if total_geral == 0:
        return 0.0
    total_marca = filtro[filtro["marca"] == marca]["total_mencoes"].sum()
    return round(total_marca / total_geral * 100, 2)


def pct_positivo(sg: pd.DataFrame, marca: str | None = None) -> float:
    filtro = sg[sg["canal"] == "all"]
    if marca:
        filtro = filtro[filtro["marca"] == marca]
    total = filtro["total_mencoes"].sum()
    if total == 0:
        return 0.0
    return round(filtro["qtd_positivo"].sum() / total * 100, 2)


def pct_negativo(sg: pd.DataFrame, marca: str | None = None) -> float:
    filtro = sg[sg["canal"] == "all"]
    if marca:
        filtro = filtro[filtro["marca"] == marca]
    total = filtro["total_mencoes"].sum()
    if total == 0:
        return 0.0
    return round(filtro["qtd_negativo"].sum() / total * 100, 2)


def pct_neutro(sg: pd.DataFrame, marca: str | None = None) -> float:
    filtro = sg[sg["canal"] == "all"]
    if marca:
        filtro = filtro[filtro["marca"] == marca]
    total = filtro["total_mencoes"].sum()
    if total == 0:
        return 0.0
    return round(filtro["qtd_neutro"].sum() / total * 100, 2)


def posts_alto_risco(pub: pd.DataFrame) -> int:
    return len(pub[(pub["seguidores_autor"] > 100_000) & (pub["sentimento"] == "Negativo")])


def indice_crise(st_df: pd.DataFrame) -> int:
    temas_alerta = set(os.getenv(
        "TEMAS_ALERTA",
        "Marca_Golpe,Atendimento_Corte de energia,Seguranca_Acidente,Atendimento_Desligamento,Segurança_Acidente",
    ).split(","))
    filtro = st_df[st_df["tema"].isin(temas_alerta)]
    return int(filtro["qtd_negativo"].sum())


def total_mencoes(sg: pd.DataFrame) -> int:
    return int(sg["total_mencoes"].sum())
