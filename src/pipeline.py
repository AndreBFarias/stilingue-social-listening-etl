import sys
import time
from collections import defaultdict
from datetime import date, datetime, timedelta

from loguru import logger

from src.config import config
from src.api.client import HTTPClient
from src.api.endpoints import StillingueAPI
from src.extractors.visao_geral import extrair_visao_geral
from src.extractors.sentimento_grupos import extrair_sentimento_grupos
from src.extractors.sentimento_temas import extrair_sentimento_temas
from src.extractors.linechart import extrair_linechart
from src.extractors.publicacoes import extrair_publicacoes
from src.extractors.ranking_evolutivo import extrair_ranking_evolutivo
from src.loaders.csv_writer import salvar_csv


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


def _executar_dia(
    api: StillingueAPI,
    date_range: str,
    data_str: str,
    data_referencia: date,
) -> dict[str, dict]:
    resultados: dict[str, dict] = {}

    etapas = [
        ("visao_geral", lambda: extrair_visao_geral(api, date_range, data_referencia)),
        ("sentimento_grupos", lambda: extrair_sentimento_grupos(api, date_range, data_referencia)),
        ("sentimento_temas", lambda: extrair_sentimento_temas(api, date_range, data_referencia)),
        ("linechart", lambda: extrair_linechart(api, date_range)),
        ("publicacoes", lambda: extrair_publicacoes(api, date_range, data_referencia)),
        ("ranking_evolutivo", lambda: extrair_ranking_evolutivo(api, date_range)),
    ]

    for nome, extrator in etapas:
        try:
            logger.info(f"Executando: {nome}")
            registros = extrator()
            arquivo = salvar_csv(registros, nome, data_str)
            resultados[nome] = {"status": "sucesso", "linhas": len(registros), "arquivo": str(arquivo)}
            time.sleep(config.REQUEST_SLEEP_BETWEEN)
        except Exception as e:
            logger.error(f"Erro no endpoint {nome}: {e}")
            resultados[nome] = {"status": "falha", "erro": str(e)}

    return resultados


def _executar_retroativo(api: StillingueAPI, inicio: date, fim: date) -> dict[str, dict]:
    resultados_totais: dict[str, dict] = {}
    dia_atual = inicio

    endpoints_simples = [
        "visao_geral", "sentimento_grupos", "sentimento_temas",
        "linechart", "publicacoes",
    ]

    while dia_atual <= fim:
        data_str = dia_atual.strftime("%Y%m%d")
        date_range = _calcular_date_range_dia(dia_atual)
        logger.info(f"Retroativo: processando {data_str}")

        for nome in endpoints_simples:
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
                chave = f"{nome}_{data_str}"
                resultados_totais[chave] = {"status": "sucesso", "linhas": len(registros), "arquivo": str(arquivo)}
                time.sleep(config.REQUEST_SLEEP_BETWEEN)
            except Exception as e:
                logger.error(f"Erro no endpoint {nome} ({data_str}): {e}")
                resultados_totais[f"{nome}_{data_str}"] = {"status": "falha", "erro": str(e)}

        dia_atual += timedelta(days=1)

    logger.info("Retroativo: extraindo ranking_evolutivo (chamada unica para periodo completo)")
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
            resultados_totais[chave] = {"status": "sucesso", "linhas": len(regs), "arquivo": str(arquivo)}

        logger.info(f"ranking_evolutivo: {len(registros)} registros distribuidos em {len(registros_por_dia)} dias")
    except Exception as e:
        logger.error(f"Erro no ranking_evolutivo retroativo: {e}")
        resultados_totais["ranking_evolutivo"] = {"status": "falha", "erro": str(e)}

    return resultados_totais


def executar_pipeline() -> None:
    _configurar_logging()
    config.validate()

    logger.info("Iniciando pipeline Stilingue Social Listening")
    inicio_exec = time.time()

    client = HTTPClient()
    api = StillingueAPI(client)

    modo_retroativo = config.RETROATIVO_INICIO and config.RETROATIVO_FIM

    if modo_retroativo:
        logger.info(
            f"Modo retroativo: {config.RETROATIVO_INICIO} ate {config.RETROATIVO_FIM}"
        )
        resultados = _executar_retroativo(api, config.RETROATIVO_INICIO, config.RETROATIVO_FIM)
    else:
        ontem = datetime.now() - timedelta(days=config.DAYS_BACK)
        data_referencia = ontem.date()
        data_str = data_referencia.strftime("%Y%m%d")
        date_range = _calcular_date_range_dia(data_referencia)

        logger.info(f"Periodo: {date_range} | Data referencia: {data_str}")
        resultados = _executar_dia(api, date_range, data_str, data_referencia)

    client.close()

    duracao = round(time.time() - inicio_exec, 2)
    logger.info(f"Pipeline concluido em {duracao}s")
    logger.info("Resumo:")
    for nome, info in resultados.items():
        if info["status"] == "sucesso":
            logger.info(f"  {nome}: {info['linhas']} linhas")
        else:
            logger.error(f"  {nome}: FALHA - {info['erro']}")


if __name__ == "__main__":
    executar_pipeline()
