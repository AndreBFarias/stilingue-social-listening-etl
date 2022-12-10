# Social Listening ETL + Dashboard

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.1-150458?style=flat-square&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Graficos-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/Licenca-GPL--3.0-blue?style=flat-square)

Pipeline ETL completa + dashboard analitico interativo para **monitoramento de marca em redes sociais**. Consome API REST de social listening, transforma dados em 6 tabelas estruturadas e apresenta os resultados em 4 paginas de analise com graficos interativos.

Projeto real de engenharia de dados aplicada, cobrindo todo o ciclo: **extracao -> transformacao -> carga -> visualizacao**.

---

## Quick Start

```bash
git clone https://github.com/[REDACTED]/stilingue-social-listening-etl.git
cd stilingue-social-listening-etl
pip install -r requirements.txt

# Gerar dados de demonstracao
python scripts/gerar_dados_amostra.py

# Abrir o dashboard
streamlit run dashboard/app.py
```

Acesse `http://localhost:8501` no navegador.

---

## Dashboard -- 4 Paginas de Analise

### Pagina 1: Visao Executiva

```
+------------------------------------------------------------------+
|  Social Listening -- Visao Executiva      [===periodo===]         |
+------------------------------------------------------------------+
| [OVERVIEW]   [MIDIA]   [CANAIS DE ATENDIMENTO]   [SAC/SOCIAL]    |
+------------------------------------------------------------------+
|                                                                   |
| +--------+ +--------+ +--------+ +--------+ +--------+ +-------+ |
| | Saude  | |Volume  | |Alcance | |Intera- | | Media  | |Posicao| |
| | -15,2% | |173.573 | | 26,7Mi | |1,2 Mi  | | Diaria | |  #1   | |
| | +1,9pts | |        | |        | |        | | 1.928  | |       | |
| +--------+ +--------+ +--------+ +--------+ +--------+ +-------+ |
|                                                                   |
| +---------------------------+ +----------------------------+      |
| | Interacoes x Saude        | | Favorabilidade por Mes     |      |
| | [barras empilhadas]       | | [barras empilhadas]        |      |
| | + linha Saude da Marca    | | + linha Favorabilidade %   |      |
| +---------------------------+ +----------------------------+      |
|                                                                   |
| +---------------------------+ +----------------------------+      |
| | Distribuicao por Canal    | | Sentimento Geral           |      |
| | [rosca interativa]        | | [rosca: pos/neu/neg]       |      |
| +---------------------------+ +----------------------------+      |
+------------------------------------------------------------------+
```

### Pagina 2: Midia

```
+------------------------------------------------------------------+
| +--------+ +--------+ +--------+ +--------+ +--------+ +-------+ |
| | Posts  | |Engaj.  | |Curtidas| |Comment.| |Compart.| | Share | |
| |165.246 | | /Post  | | 761k   | | 129k   | | 50k    | |of Voice|
| |        | |  2.464 | |        | |        | |        | | 17,2% | |
| +--------+ +--------+ +--------+ +--------+ +--------+ +-------+ |
|                                                                   |
| +---------------------------+ +----------------------------+      |
| | Volume por Canal          | | Engajamento por Canal      |      |
| | [barras horizontais]      | | [barras horizontais]       |      |
| | Top 10, cor ciano         | | Top 10, cor laranja        |      |
| +---------------------------+ +----------------------------+      |
|                                                                   |
| +---------------------------+ +----------------------------+      |
| | Canais x Saude [tabela]   | | Evolucao Diaria [linha]   |      |
| | Canal|Mencoes|%Pos|Saude  | | 90 dias, area preenchida  |      |
| +---------------------------+ +----------------------------+      |
+------------------------------------------------------------------+
```

### Pagina 3: Sentimento por Marca

```
+------------------------------------------------------------------+
| +----------+ +-----------+ +-------------+ +----------------+    |
| |Favorab.  | |Saude Conc.| |Polaridade   | |Polaridade      |    |
| | -15,8%   | | -14,5%    | |Marca Princ. | |Concorrentes    |    |
| +----------+ +-----------+ |[rosca]      | |[rosca]         |    |
|                             +-------------+ +----------------+    |
|                                                                   |
| +--------------------------------------------------------------+ |
| | Ranking Saude da Marca (todas as marcas)                      | |
| | [barras horizontais com cor condicional: verde > 0, verm < 0] | |
| +--------------------------------------------------------------+ |
|                                                                   |
| +--------------------------------------------------------------+ |
| | Saude Mensal por Marca [heatmap]                              | |
| | Linhas: marcas | Colunas: meses | Valores: score saude       | |
| | Escala: vermelho (-) -> branco (0) -> verde (+)               | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

### Pagina 4: Publicacoes e Temas

```
+------------------------------------------------------------------+
| +--------+ +--------+ +--------+ +--------+                      |
| |Total   | |Engaj.  | |Posts   | |Indice  |                      |
| |Posts   | |/Post   | |Alto    | |de Crise|                      |
| | 500    | | 2.464  | |Risco   | | 0      |                      |
| +--------+ +--------+ +--------+ +--------+                      |
|                                                                   |
| [Marca v]  [Sentimento v]  [Canal v]  [Tema v]   <- filtros      |
|                                                                   |
| +--------------------------------------------------------------+ |
| | DATA     | MARCA   | SENT. | CANAL | TEXTO      | INTERACOES | |
| |----------|---------|-------|-------|------------|------------| |
| | 23/03/26 | Marca D | Neg.  | Twit. | Atendim... | 4.521      | |
| | 23/03/26 | Marca A | Pos.  | Inst. | Excelente. | 1.203      | |
| | ...      | ...     | ...   | ...   | ...        | ...        | |
| +--------------------------------------------------------------+ |
|                                                                   |
| +---------------------------+ +----------------------------+      |
| | Top Temas por Sentimento  | | Temas de Crise             |      |
| | [barras empilhadas horiz] | | [tabela: tema, %, mencoes] |      |
| +---------------------------+ +----------------------------+      |
+------------------------------------------------------------------+
```

---

## Destaques Tecnicos

O que este projeto demonstra:

- **ETL completa** -- extracao paginada com retry exponencial, transformacao com Pandas, carga incremental com deduplicacao
- **Resiliencia** -- backoff exponencial, rate-limiting (HTTP 429), deteccao automatica de gaps e reconsolidacao
- **23 metricas analiticas** -- saude da marca, share of voice, favorabilidade, indice de crise, variacao MoM
- **Dashboard interativo** -- Streamlit com 4 paginas, filtros globais, paginacao, graficos Plotly
- **Relatorios HTML estaticos** -- self-contained, abrem no navegador sem servidor
- **Arquitetura em camadas** -- api/ extractors/ transformers/ loaders/ dashboard/
- **Observabilidade** -- logging rotacionado via Loguru, sem print()
- **Agendamento** -- cron (Linux) e Task Scheduler (Windows)
- **Configuracao via .env** -- marca principal auto-detectada, temas de alerta configuraveis
- **Dados de demonstracao** -- gerador de dados ficticios para portfolio

---

## Tecnologias

| Camada | Stack |
|--------|-------|
| Extracao | Python, Requests, Tenacity (retry com backoff) |
| Transformacao | Pandas, PyArrow |
| Armazenamento | CSV estruturado (`;` separador), Parquet (opcional) |
| Dashboard | Streamlit, Plotly |
| Relatorio | HTML estatico com Plotly embutido (CDN) |
| Observabilidade | Loguru (logging rotacionado) |
| Agendamento | cron (Linux), Task Scheduler (Windows) |

---

## Arquitetura

```
                  API Social Listening (REST)
                        |
                  [HTTPClient]
                  retry 3x + backoff exponencial
                        |
          +-------------+-------------+
          |             |             |
    [6 Extractors]  [Transformers]  [Loaders]
    visao_geral     normalizar      csv_writer
    sentimento      percentuais     consolidador
    publicacoes     sentimento      (merge + dedup)
    ranking
    linechart
    temas
          |             |             |
          +-------> CSVs diarios -----+
                        |
                  [Consolidador]
                  merge + dedup + schema enforcement
                        |
              +---------+---------+
              |                   |
        [Streamlit]         [HTML Estatico]
        4 paginas           4 relatorios
        interativo          abre no navegador
```

---

## Pipeline ETL

### Instalacao

```bash
git clone https://github.com/[REDACTED]/stilingue-social-listening-etl.git
cd stilingue-social-listening-etl
pip install -r requirements.txt
cp .env.example .env
```

### Execucao

```bash
python -m src
```

A pipeline detecta automaticamente o ultimo dia processado e extrai apenas os dias faltantes.

### Modo retroativo

```env
RETROATIVO_INICIO=2026-02-01
RETROATIVO_FIM=2026-03-04
```

### Relatorios HTML

```bash
python scripts/gerar_relatorio_html.py
```

Gera 4 arquivos HTML em `relatorios/` -- abrem direto no navegador, sem servidor.

---

## Estrutura do Projeto

```
stilingue-social-listening-etl/
  src/
    config.py                # Configuracao via .env
    api/
      client.py              # HTTP client com retry
      endpoints.py           # Wrapper dos 6 endpoints
    extractors/              # 1 extractor por endpoint
    transformers/            # Normalizacao e calculos
    loaders/
      csv_writer.py          # CSV diario com dedup
      consolidador.py        # Merge + ZIP LZMA
    pipeline.py              # Orquestrador principal
  dashboard/
    app.py                   # Streamlit entry point
    dados.py                 # Loader com cache
    metricas.py              # 23 metricas analiticas
    componentes.py           # Cards, graficos, tabelas
    tema.py                  # Paleta e formatacao PT-BR
    paginas/                 # 4 paginas do dashboard
  scripts/
    gerar_dados_amostra.py   # Gerador de dados ficticios
    gerar_relatorio_html.py  # Exportacao HTML estatica
  data/csv/                  # CSVs diarios (por endpoint/data)
  consolidado/               # CSVs consolidados
  relatorios/                # HTMLs gerados
  tests/                     # Testes unitarios
```

---

## 6 Tabelas de Dados

| Tabela | Granularidade | Descricao |
|--------|--------------|-----------|
| `visao_geral` | 1 linha/dia | KPIs globais: volume, usuarios, alcance, sentimento |
| `sentimento_grupos` | marca x canal/dia | Polaridade e saude da marca por grupo |
| `sentimento_temas` | tema x canal/dia | Polaridade por tema categorizado |
| `linechart` | 1 ponto/dia | Serie temporal de publicacoes |
| `publicacoes` | 1 linha/post | Texto, sentimento, engajamento, seguidores |
| `ranking_evolutivo` | marca/dia | Posicao no ranking e total de mencoes |

---

## Licenca

GPL-3.0-or-later

---

*"O que nao pode ser medido nao pode ser melhorado."*
