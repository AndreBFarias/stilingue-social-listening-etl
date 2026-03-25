"""Gerador de dados de amostra para demonstracao do dashboard.

Gera 6 CSVs ficticios em consolidado/ com ~500 registros
distribuidos em 90 dias. Dados realistas mas inventados.
"""
import random
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

PROJETO_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJETO_DIR))

CONSOLIDADO_DIR = PROJETO_DIR / "consolidado"
CONSOLIDADO_DIR.mkdir(exist_ok=True)

MARCAS = ["Marca A", "Marca B", "Marca C", "Marca D", "Marca E", "Marca F"]
CANAIS = ["Twitter", "Instagram", "Facebook", "YouTube", "Portais", "Blogs", "LinkedIn"]
TEMAS = [
    "Atendimento_Qualidade", "Atendimento_Tempo de resposta",
    "Produto_Preco", "Produto_Defeito", "Produto_Inovacao",
    "Marca_Imagem", "Marca_Promocao", "Marca_Sustentabilidade",
    "Servico_Entrega", "Servico_Suporte",
]
SENTIMENTOS = ["Negativo", "Neutro", "Positivo"]
PESOS_SENTIMENTO = [0.50, 0.20, 0.30]

random.seed(42)


def _gerar_datas(dias: int = 90) -> list[date]:
    fim = date(2026, 3, 23)
    return [fim - timedelta(days=i) for i in range(dias - 1, -1, -1)]


def _fmt_data(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _fmt_datetime(d: date) -> str:
    h = random.randint(0, 23)
    m = random.randint(0, 59)
    return d.strftime(f"%d/%m/%Y {h:02d}:{m:02d}:00")


def gerar_visao_geral() -> None:
    datas = _gerar_datas()
    registros = []
    for d in datas:
        pub = random.randint(800, 3000)
        neg = int(pub * random.uniform(0.35, 0.55))
        neu = int(pub * random.uniform(0.15, 0.25))
        pos = pub - neg - neu
        registros.append({
            "data_extracao": _fmt_datetime(d),
            "data_referencia": _fmt_data(d),
            "publicacoes_coletadas": pub,
            "variacao_publicacoes_pct": round(random.uniform(-40, 40), 4),
            "total_usuarios": int(pub * random.uniform(0.7, 0.95)),
            "variacao_usuarios_pct": round(random.uniform(-30, 30), 4),
            "alcance_potencial": random.randint(5_000_000, 30_000_000),
            "variacao_alcance_pct": round(random.uniform(-50, 50), 4),
            "indice_sentimento": round(random.uniform(-50, 10), 4),
            "variacao_sentimento_pts": round(random.uniform(-30, 30), 4),
            "sentimento_negativo_qtd": neg,
            "sentimento_neutro_qtd": neu,
            "sentimento_positivo_qtd": pos,
            "canal_twitter": int(pub * 0.35),
            "canal_facebook": int(pub * 0.15),
            "canal_noticias": int(pub * 0.20),
            "canal_instagram": int(pub * 0.10),
            "canal_youtube": int(pub * 0.08),
            "canal_blogs": int(pub * 0.02),
        })
    df = pd.DataFrame(registros)
    df.to_csv(CONSOLIDADO_DIR / "visao_geral.csv", sep=";", index=False, encoding="utf-8")


def gerar_sentimento_grupos() -> None:
    datas = _gerar_datas()
    registros = []
    for d in datas:
        for marca in MARCAS:
            total = random.randint(50, 500)
            neg = int(total * random.uniform(0.30, 0.60))
            pos = int(total * random.uniform(0.20, 0.40))
            neu = total - neg - pos
            saude = round((pos - neg) / total * 100, 2) if total > 0 else 0
            registros.append({
                "data_referencia": _fmt_data(d),
                "marca": marca,
                "canal": "all",
                "qtd_positivo": pos,
                "qtd_neutro": neu,
                "qtd_negativo": neg,
                "total_mencoes": total,
                "pct_positivo": round(pos / total * 100, 2),
                "pct_neutro": round(neu / total * 100, 2),
                "pct_negativo": round(neg / total * 100, 2),
                "saude_marca_score": saude,
            })
    df = pd.DataFrame(registros)
    df.to_csv(CONSOLIDADO_DIR / "sentimento_grupos.csv", sep=";", index=False, encoding="utf-8")


def gerar_sentimento_temas() -> None:
    datas = _gerar_datas()
    registros = []
    for d in datas:
        for tema in TEMAS:
            total = random.randint(10, 200)
            neg = int(total * random.uniform(0.20, 0.70))
            pos = int(total * random.uniform(0.10, 0.50))
            neu = total - neg - pos
            registros.append({
                "data_referencia": _fmt_data(d),
                "tema": tema,
                "canal": "all",
                "qtd_positivo": pos,
                "qtd_neutro": neu,
                "qtd_negativo": neg,
                "total_mencoes": total,
                "pct_positivo": round(pos / total * 100, 2),
                "pct_neutro": round(neu / total * 100, 2),
                "pct_negativo": round(neg / total * 100, 2),
            })
    df = pd.DataFrame(registros)
    df.to_csv(CONSOLIDADO_DIR / "sentimento_temas.csv", sep=";", index=False, encoding="utf-8")


def gerar_linechart() -> None:
    datas = _gerar_datas()
    registros = [
        {"data_referencia": _fmt_data(d), "total_publicacoes": random.randint(800, 3000), "hora": "00:00"}
        for d in datas
    ]
    df = pd.DataFrame(registros)
    df.to_csv(CONSOLIDADO_DIR / "linechart.csv", sep=";", index=False, encoding="utf-8")


def gerar_publicacoes() -> None:
    datas = _gerar_datas()
    registros = []
    textos_exemplo = [
        "Servico melhorou bastante nos ultimos meses",
        "Atendimento pessimo, esperei 40 minutos no telefone",
        "Produto chegou com defeito, precisei trocar",
        "Excelente promocao, recomendo a todos",
        "Nao consigo resolver meu problema pelo app",
        "Fui bem atendido na loja fisica",
        "Preco muito alto comparado a concorrencia",
        "Inovacao constante, estou satisfeito",
        "Demora absurda na entrega",
        "Suporte tecnico resolveu rapido",
    ]
    for i in range(500):
        d = random.choice(datas)
        sent_idx = random.choices([0, 1, 2], weights=PESOS_SENTIMENTO)[0]
        marca = random.choice(MARCAS)
        canal = random.choice(CANAIS)
        registros.append({
            "data_referencia": _fmt_data(d),
            "data_publicacao": _fmt_datetime(d),
            "data_extracao": _fmt_datetime(d),
            "marca": marca,
            "todas_marcas": marca,
            "sentimento": SENTIMENTOS[sent_idx],
            "sentimento_num": [-1, 0, 1][sent_idx],
            "post_url": f"https://exemplo.com/post/{i+1}",
            "texto": random.choice(textos_exemplo),
            "canal": canal,
            "interacoes": random.randint(0, 5000),
            "curtidas": random.randint(0, 3000),
            "comentarios": random.randint(0, 500),
            "compartilhamentos": random.randint(0, 200),
            "temas": random.choice(TEMAS),
            "tags": "",
            "pid": f"PID{i+1:06d}",
            "seguidores_autor": random.randint(100, 500_000),
            "score_aaa": round(random.uniform(0, 100), 1),
            "nivel_criticidade": 0,
        })
    df = pd.DataFrame(registros)
    df.to_csv(CONSOLIDADO_DIR / "publicacoes.csv", sep=";", index=False, encoding="utf-8")


def gerar_ranking_evolutivo() -> None:
    datas = _gerar_datas()
    registros = []
    for d in datas:
        mencoes = {m: random.randint(50, 500) for m in MARCAS}
        ranking = sorted(mencoes.items(), key=lambda x: -x[1])
        for pos, (marca, total) in enumerate(ranking, 1):
            registros.append({
                "data_referencia": _fmt_data(d),
                "marca": marca,
                "posicao_ranking": pos,
                "total_mencoes": total,
                "descritores": "Tema1|Tema2|Tema3",
            })
    df = pd.DataFrame(registros)
    df.to_csv(CONSOLIDADO_DIR / "ranking_evolutivo.csv", sep=";", index=False, encoding="utf-8")


def main() -> None:
    from loguru import logger
    logger.info("Gerando dados de amostra...")
    gerar_visao_geral()
    logger.info("  visao_geral.csv")
    gerar_sentimento_grupos()
    logger.info("  sentimento_grupos.csv")
    gerar_sentimento_temas()
    logger.info("  sentimento_temas.csv")
    gerar_linechart()
    logger.info("  linechart.csv")
    gerar_publicacoes()
    logger.info("  publicacoes.csv")
    gerar_ranking_evolutivo()
    logger.info("  ranking_evolutivo.csv")
    logger.info(f"Dados de amostra gerados em {CONSOLIDADO_DIR}")


if __name__ == "__main__":
    main()
