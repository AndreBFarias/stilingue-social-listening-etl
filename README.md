# Social Listening ETL + Dashboard

Pipeline ETL completa que consome a API REST do Stilingue (social listening), transforma os dados em CSVs estruturados e apresenta os resultados em um **dashboard interativo** com Streamlit + Plotly e **relatorios HTML estaticos** que rodam direto no navegador.

Projeto construido como ferramenta real de monitoramento de marca em redes sociais, cobrindo desde a extracao de dados ate a visualizacao analitica.

## Tecnologias

| Camada | Stack |
|--------|-------|
| Extracao | Python, Requests, Tenacity (retry com backoff exponencial) |
| Transformacao | Pandas, PyArrow |
| Armazenamento | CSV estruturado, Parquet (opcional) |
| Dashboard | Streamlit, Plotly |
| Relatorio | HTML estatico com Plotly embutido |
| Observabilidade | Loguru (logging rotacionado) |
| Agendamento | cron (Linux), Task Scheduler (Windows) |

## Arquitetura

```
                  API Stilingue (REST)
                        |
                  [HTTPClient]
                  retry 3x + backoff
                        |
          +-------------+-------------+
          |             |             |
    [6 Extractors]  [Transformers]  [Loaders]
    visao_geral     normalizar      csv_writer
    sentimento      percentuais     consolidador
    publicacoes     sentimento
    ranking
    linechart
    temas
          |             |             |
          +-------> CSVs diarios -----+
                        |
                  [Consolidador]
                  merge + dedup + schema
                        |
              +---------+---------+
              |                   |
        [Streamlit]         [HTML Estatico]
        dashboard/app.py    gerar_relatorio_html.py
        4 paginas           4 arquivos .html
        interativo          abre no navegador
```

## Dashboard Interativo

O dashboard Streamlit oferece 4 paginas de analise:

| Pagina | Conteudo |
|--------|----------|
| **Visao Executiva** | 6 KPIs + combos de sentimento + roscas de canal e polaridade |
| **Midia** | Volume e engajamento por canal + tabela de saude + evolucao diaria |
| **Sentimento por Marca** | Benchmark competitivo + ranking + heatmap mensal |
| **Publicacoes e Temas** | Filtros interativos + tabela paginada + temas de crise |

### Como executar o dashboard

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Acesse `http://localhost:8501` no navegador.

### Relatorios HTML estaticos

```bash
python scripts/gerar_relatorio_html.py
```

Os 4 arquivos HTML serao gerados em `relatorios/` e podem ser abertos diretamente no navegador, sem servidor.

## Pipeline ETL

### Instalacao

```bash
git clone <repo-url>
cd stilingue-social-listening-etl
pip install -r requirements.txt
cp .env.example .env
```

Edite o `.env` com seu token da API Stilingue.

### Execucao

```bash
python -m src
```

A pipeline detecta automaticamente o ultimo dia processado e extrai apenas os dias faltantes.

### Modo retroativo

Para gerar CSVs historicos de um periodo passado:

```env
RETROATIVO_INICIO=2026-02-01
RETROATIVO_FIM=2026-03-04
```

### Dados de demonstracao

Para testar o dashboard sem acesso a API:

```bash
python scripts/gerar_dados_amostra.py
```

Gera ~500 registros ficticios distribuidos em 90 dias.

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
      consolidador.py        # Merge + ZIP
    pipeline.py              # Orquestrador principal
  dashboard/
    app.py                   # Streamlit entry point
    dados.py                 # Loader com cache
    metricas.py              # 23 metricas analiticas
    componentes.py           # Cards, graficos, tabelas
    tema.py                  # Paleta e formatacao
    paginas/                 # 4 paginas do dashboard
  scripts/
    gerar_dados_amostra.py   # Gerador de dados ficticios
    gerar_relatorio_html.py  # Exportacao HTML estatica
  data/csv/                  # CSVs diarios
  consolidado/               # CSVs consolidados
  relatorios/                # HTMLs gerados
  tests/                     # Testes unitarios
```

## CSVs gerados

| Tabela | Granularidade | Descricao |
|--------|--------------|-----------|
| `visao_geral` | 1 linha/dia | KPIs globais: volume, usuarios, alcance, sentimento |
| `sentimento_grupos` | marca x canal/dia | Polaridade e saude da marca por grupo |
| `sentimento_temas` | tema x canal/dia | Polaridade por tema categorizado |
| `linechart` | 1 ponto/dia | Serie temporal de publicacoes |
| `publicacoes` | 1 linha/post | Texto, sentimento, metricas de engajamento |
| `ranking_evolutivo` | marca/dia | Posicao no ranking e total de mencoes |

## Variaveis de ambiente

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `STILINGUE_API_TOKEN` | Token de autenticacao | (obrigatorio) |
| `STILINGUE_BASE_URL` | URL base da API | `https://api.stilingue.com.br` |
| `OUTPUT_DIR` | Diretorio de saida dos CSVs | `./data/csv` |
| `CONSOLIDADO_DIR` | Diretorio dos consolidados | `./consolidado` |
| `CONSOLIDADO_FORMATO` | Formato de saida: csv ou parquet | `csv` |
| `PUBLICATIONS_LIMIT` | Publicacoes por pagina | `100` |
| `REQUEST_TIMEOUT` | Timeout de requisicao (s) | `60` |
| `RANKING_EVOLUTIVO_DAYS` | Janela do ranking (dias) | `30` |
| `MARCA_PRINCIPAL` | Marca principal para o dashboard | (auto-detectada) |

## Licenca

GPL-3.0-or-later

---

*"O que nao pode ser medido nao pode ser melhorado."*
