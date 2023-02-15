import sys
import time
from collections import defaultdict
from datetime import date, datetime, timedelta

from loguru import logger

from src.config import config
from src.api.client import HTTPClient
from src.api.endpoints import SocialListeningAPI
from src.extractors.visao_geral import extrair_visao_geral
from src.extractors.sentimento_grupos import extrair_sentimento_grupos
from src.extractors.sentimento_temas import extrair_sentimento_temas
from src.extractors.linechart import extrair_linechart
from src.extractors.publicacoes import extrair_publicacoes
from src.extractors.ranking_evolutivo import extrair_ranking_evolutivo
from src.loaders.csv_writer import salvar_csv, csv_ja_existe
from src.loaders.consolidador import consolidar_todos
from src.schemas import ENDPOINT_SCHEMAS


def _configurar_logging() -> None:
    logger.remove()
    data_str = datetime.now().strftime("%Y%m%d")
    log_path = config.LOG_DIR / f"pipeline_{data_str}.log"
    logger.add(
        log_path,
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
    )
    logger.add(
        sys.stderr,
        format="{time:HH:mm:ss} | {level:<8} | {message}",
    )


def _calcular_date_range_dia(dia: date) -> str:
    inicio = f"{dia.strftime('%Y%m%d')}0000"
    fim = f"{dia.strftime('%Y%m%d')}2359"
    return f"{inicio}:{fim}"


def _calcular_date_range_periodo(inicio: date, fim: date) -> str:
    dr_inicio = f"{inicio.strftime('%Y%m%d')}0000"
    dr_fim = f"{fim.strftime('%Y%m%d')}2359"
    return f"{dr_inicio}:{dr_fim}"


def _data_maxima_csvs() -> date | None:
    data_max: date | None = None
    for ep in ENDPOINT_SCHEMAS:
        pasta = config.OUTPUT_DIR / ep
        if not pasta.exists():
            return None
        csvs = list(pasta.glob("*.csv"))
        if not csvs:
            return None
        for csv in csvs:
            try:
                dt = datetime.strptime(csv.stem, "%Y%m%d").date()
                if data_max is None or dt > data_max:
                    data_max = dt
            except ValueError:
                continue
    return data_max


def _calcular_dias_faltantes(inicio: date, fim: date) -> list[date]:
    dias: list[date] = []
    dia = inicio
    while dia <= fim:
        faltante = False
        for ep in ENDPOINT_SCHEMAS:
            if not csv_ja_existe(ep, dia.strftime("%Y%m%d")):
                faltante = True
                break
        if faltante:
            dias.append(dia)
        dia += timedelta(days=1)
    return dias


def _executar_periodo(api: SocialListeningAPI, inicio: date, fim: date) -> dict[str, dict]:
    resultados_totais: dict[str, dict] = {}

    endpoints_simples = [
        "visao_geral", "sentimento_grupos", "sentimento_temas",
        "linechart", "publicacoes",
    ]

    dia_atual = inicio
    while dia_atual <= fim:
        data_str = dia_atual.strftime("%Y%m%d")
        date_range = _calcular_date_range_dia(dia_atual)
        logger.info(f"Processando {data_str}")

        for nome in endpoints_simples:
            chave = f"{nome}_{data_str}"
            if csv_ja_existe(nome, data_str):
                logger.info(f"Pulando {nome} ({data_str}): CSV ja existe")
                resultados_totais[chave] = {"status": "pulado"}
                continue
            etapa_map = {
                "visao_geral": lambda: extrair_visao_geral(api, date_range, dia_atual),
                "sentimento_grupos": lambda: extrair_sentimento_grupos(api, date_range, dia_atual),
                "sentimento_temas": lambda: extrair_sentimento_temas(api, date_range, dia_atual),
                "linechart": lambda: extrair_linechart(api, date_range),
                "publicacoes": lambda: extrair_publicacoes(api, date_range, dia_atual),
            }
            try:
                logger.info(f"Executando: {nome} ({data_str})")
                registros = etapa_map[nome]()
                arquivo = salvar_csv(registros, nome, data_str)
                resultados_totais[chave] = {
                    "status": "sucesso", "linhas": len(registros), "arquivo": str(arquivo),
                }
                time.sleep(config.REQUEST_SLEEP_BETWEEN)
            except Exception as e:
                logger.error(f"Erro no endpoint {nome} ({data_str}): {e}")
                resultados_totais[chave] = {"status": "falha", "erro": str(e)}

        dia_atual += timedelta(days=1)

    logger.info("Extraindo ranking_evolutivo (chamada unica para periodo completo)")
    date_range_completo = _calcular_date_range_periodo(inicio, fim)
    try:
        registros = extrair_ranking_evolutivo(api, date_range_completo)
        registros_por_dia: dict[str, list] = defaultdict(list)
        for reg in registros:
            data_ref = reg["data_referencia"].replace("-", "")
            registros_por_dia[data_ref].append(reg)

        for data_str_ranking, regs in registros_por_dia.items():
            arquivo = salvar_csv(regs, "ranking_evolutivo", data_str_ranking)
            chave = f"ranking_evolutivo_{data_str_ranking}"
            resultados_totais[chave] = {
                "status": "sucesso", "linhas": len(regs), "arquivo": str(arquivo),
            }

        logger.info(
            f"ranking_evolutivo: {len(registros)} registros "
            f"distribuidos em {len(registros_por_dia)} dias"
        )
    except Exception as e:
        logger.error(f"Erro no ranking_evolutivo: {e}")
        resultados_totais["ranking_evolutivo"] = {"status": "falha", "erro": str(e)}

    return resultados_totais


def executar_pipeline() -> None:
    _configurar_logging()
    config.validate()

    logger.info("Iniciando pipeline de social listening")
    inicio_exec = time.time()

    client = HTTPClient()
    api = SocialListeningAPI(client)

    ontem = date.today() - timedelta(days=1)
    modo_retroativo = config.RETROATIVO_INICIO and config.RETROATIVO_FIM

    if modo_retroativo:
        logger.info(
            f"Modo retroativo manual: {config.RETROATIVO_INICIO} ate {config.RETROATIVO_FIM}"
        )
        resultados = _executar_periodo(api, config.RETROATIVO_INICIO, config.RETROATIVO_FIM)
    else:
        data_max = _data_maxima_csvs()

        if data_max is None:
            inicio = config.CONSOLIDADO_DATA_MINIMA
            logger.info(f"Primeira execucao: baixando de {inicio} ate {ontem}")
            resultados = _executar_periodo(api, inicio, ontem)
        elif data_max >= ontem:
            logger.info("Dados atualizados, nenhum dia faltante")
            resultados = {}
        else:
            proximo_dia = data_max + timedelta(days=1)
            dias_faltantes = _calcular_dias_faltantes(proximo_dia, ontem)
            if dias_faltantes:
                logger.info(
                    f"{len(dias_faltantes)} dias faltantes: "
                    f"{dias_faltantes[0]} ate {dias_faltantes[-1]}"
                )
                resultados = _executar_periodo(api, dias_faltantes[0], dias_faltantes[-1])
            else:
                logger.info("Todos os CSVs individuais ja existem")
                resultados = {}

    client.close()

    logger.info(f"Consolidando arquivos (formato: {config.CONSOLIDADO_FORMATO})")
    caminhos = consolidar_todos()
    for ep, caminho in caminhos.items():
        logger.info(f"  {ep}: {caminho}")

    duracao = round(time.time() - inicio_exec, 2)
    logger.info(f"Pipeline concluido em {duracao}s")
    if resultados:
        logger.info("Resumo:")
        for nome, info in resultados.items():
            status = info["status"]
            if status == "sucesso":
                logger.info(f"  {nome}: {info['linhas']} linhas")
            elif status == "pulado":
                logger.info(f"  {nome}: pulado (CSV ja existe)")
            else:
                logger.error(f"  {nome}: FALHA - {info['erro']}")


if __name__ == "__main__":
    executar_pipeline()
