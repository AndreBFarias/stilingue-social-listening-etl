# Whisper-Pulse

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.1-150458?style=flat-square&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Gráficos-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/Licença-GPL--3.0-blue?style=flat-square)
[![CI](https://github.com/AndreBFarias/Whisper-Pulse/actions/workflows/ci.yml/badge.svg)](https://github.com/AndreBFarias/Whisper-Pulse/actions/workflows/ci.yml)

Pipeline ETL completa + dashboard analítico interativo para **monitoramento de marca em redes sociais**. Consome API REST de social listening, transforma dados em 6 tabelas estruturadas e apresenta os resultados em 4 páginas de análise com gráficos interativos.

Projeto real de engenharia de dados aplicada, cobrindo todo o ciclo: **extração -> transformação -> carga -> visualização**.

---

## Quick Start

```bash
git clone https://github.com/AndreBFarias/Whisper-Pulse.git
cd Whisper-Pulse
pip install -r requirements.txt

# Gerar dados de demonstração
python scripts/gerar_dados_amostra.py

# Abrir o dashboard
streamlit run dashboard/app.py
```

Acesse `http://localhost:8501` no navegador.

---

## Dashboard -- 4 Páginas de Análise

### Página 1: Visão Executiva

```
+------------------------------------------------------------------+
|  Social Listening -- Visão Executiva      [===período===]         |
+------------------------------------------------------------------+
| [OVERVIEW]   [MÍDIA]   [CANAIS DE ATENDIMENTO]   [SAC/SOCIAL]    |
+------------------------------------------------------------------+
|                                                                   |
| +--------+ +--------+ +--------+ +--------+ +--------+ +-------+ |
| | Saúde  | |Volume  | |Alcance | |Intera- | | Média  | |Posição| |
| | -15,2% | |173.573 | | 26,7Mi | |1,2 Mi  | | Diária | |  #1   | |
| | +1,9pts | |        | |        | |        | | 1.928  | |       | |
| +--------+ +--------+ +--------+ +--------+ +--------+ +-------+ |
|                                                                   |
| +---------------------------+ +----------------------------+      |
| | Interações x Saúde        | | Favorabilidade por Mês     |      |
| | [barras empilhadas]       | | [barras empilhadas]        |      |
| | + linha Saúde da Marca    | | + linha Favorabilidade %   |      |
| +---------------------------+ +----------------------------+      |
|                                                                   |
| +---------------------------+ +----------------------------+      |
| | Distribuição por Canal    | | Sentimento Geral           |      |
| | [rosca interativa]        | | [rosca: pos/neu/neg]       |      |
| +---------------------------+ +----------------------------+      |
+------------------------------------------------------------------+
```

### Página 2: Mídia

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
| | Canais x Saúde [tabela]   | | Evolução Diária [linha]   |      |
| | Canal|Menções|%Pos|Saúde  | | 90 dias, área preenchida  |      |
| +---------------------------+ +----------------------------+      |
+------------------------------------------------------------------+
```

### Página 3: Sentimento por Marca

```
+------------------------------------------------------------------+
| +----------+ +-----------+ +-------------+ +----------------+    |
| |Favorab.  | |Saúde Conc.| |Polaridade   | |Polaridade      |    |
| | -15,8%   | | -14,5%    | |Marca Princ. | |Concorrentes    |    |
| +----------+ +-----------+ |[rosca]      | |[rosca]         |    |
|                             +-------------+ +----------------+    |
|                                                                   |
| +--------------------------------------------------------------+ |
| | Ranking Saúde da Marca (todas as marcas)                      | |
| | [barras horizontais com cor condicional: verde > 0, verm < 0] | |
| +--------------------------------------------------------------+ |
|                                                                   |
| +--------------------------------------------------------------+ |
| | Saúde Mensal por Marca [heatmap]                              | |
| | Linhas: marcas | Colunas: meses | Valores: score saúde       | |
| | Escala: vermelho (-) -> branco (0) -> verde (+)               | |
| +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

### Página 4: Publicações e Temas

```
+------------------------------------------------------------------+
| +--------+ +--------+ +--------+ +--------+                      |
| |Total   | |Engaj.  | |Posts   | |Índice  |                      |
| |Posts   | |/Post   | |Alto    | |de Crise|                      |
| | 500    | | 2.464  | |Risco   | | 0      |                      |
| +--------+ +--------+ +--------+ +--------+                      |
|                                                                   |
| [Marca v]  [Sentimento v]  [Canal v]  [Tema v]   <- filtros      |
|                                                                   |
| +--------------------------------------------------------------+ |
| | DATA     | MARCA   | SENT. | CANAL | TEXTO      | INTERAÇÕES | |
| |----------|---------|-------|-------|------------|------------| |
| | 23/03/26 | Marca D | Neg.  | Twit. | Atendim... | 4.521      | |
| | 23/03/26 | Marca A | Pos.  | Inst. | Excelente. | 1.203      | |
| | ...      | ...     | ...   | ...   | ...        | ...        | |
| +--------------------------------------------------------------+ |
|                                                                   |
| +---------------------------+ +----------------------------+      |
| | Top Temas por Sentimento  | | Temas de Crise             |      |
| | [barras empilhadas horiz] | | [tabela: tema, %, menções] |      |
| +---------------------------+ +----------------------------+      |
+------------------------------------------------------------------+
```

---

## Destaques Técnicos

O que este projeto demonstra:

- **ETL completa** -- extração paginada com retry exponencial, transformação com Pandas, carga incremental com deduplicação
- **Resiliência** -- backoff exponencial, rate-limiting (HTTP 429), detecção automática de gaps e reconsolidação
- **23 métricas analíticas** -- saúde da marca, share of voice, favorabilidade, índice de crise, variação MoM
- **Dashboard interativo** -- Streamlit com 4 páginas, filtros globais, paginação, gráficos Plotly
- **Relatórios HTML estáticos** -- self-contained, abrem no navegador sem servidor
- **Arquitetura em camadas** -- api/ extractors/ transformers/ loaders/ dashboard/
- **Observabilidade** -- logging rotacionado via Loguru, sem print()
- **Agendamento** -- cron (Linux) e Task Scheduler (Windows)
- **Configuração via .env** -- marca principal auto-detectada, temas de alerta configuráveis
- **Dados de demonstração** -- gerador de dados fictícios para portfolio

---

## Tecnologias

| Camada | Stack |
|--------|-------|
| Extração | Python, Requests, Tenacity (retry com backoff) |
| Transformação | Pandas, PyArrow |
| Armazenamento | CSV estruturado (`;` separador), Parquet (opcional) |
| Dashboard | Streamlit, Plotly |
| Relatório | HTML estático com Plotly embutido (CDN) |
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
          +-------> CSVs diários ----+
                        |
                  [Consolidador]
                  merge + dedup + schema enforcement
                        |
              +---------+---------+
              |                   |
        [Streamlit]         [HTML Estático]
        4 páginas           4 relatórios
        interativo          abre no navegador
```

---

## Pipeline ETL

### Instalação

```bash
git clone https://github.com/AndreBFarias/Whisper-Pulse.git
cd Whisper-Pulse
pip install -r requirements.txt
cp .env.example .env
```

### Execução

```bash
python -m src
```

A pipeline detecta automaticamente o último dia processado e extrai apenas os dias faltantes.

### Modo retroativo

```env
RETROATIVO_INICIO=2026-02-01
RETROATIVO_FIM=2026-03-04
```

### Relatórios HTML

```bash
python scripts/gerar_relatorio_html.py
```

Gera 4 arquivos HTML em `relatorios/` -- abrem direto no navegador, sem servidor.

---

## Estrutura do Projeto

```
Whisper-Pulse/
  src/
    config.py                # Configuração via .env
    api/
      client.py              # HTTP client com retry
      endpoints.py           # Wrapper dos 6 endpoints
    extractors/              # 1 extractor por endpoint
    transformers/            # Normalização e cálculos
    loaders/
      csv_writer.py          # CSV diário com dedup
      consolidador.py        # Merge + ZIP LZMA
    pipeline.py              # Orquestrador principal
  dashboard/
    app.py                   # Streamlit entry point
    dados.py                 # Loader com cache
    metricas.py              # 23 métricas analíticas
    componentes.py           # Cards, gráficos, tabelas
    tema.py                  # Paleta e formatação PT-BR
    paginas/                 # 4 páginas do dashboard
  scripts/
    gerar_dados_amostra.py   # Gerador de dados fictícios
    gerar_relatorio_html.py  # Exportação HTML estática
  data/csv/                  # CSVs diários (por endpoint/data)
  consolidado/               # CSVs consolidados
  relatorios/                # HTMLs gerados
  tests/                     # Testes unitários
```

---

## 6 Tabelas de Dados

| Tabela | Granularidade | Descrição |
|--------|--------------|-----------|
| `visao_geral` | 1 linha/dia | KPIs globais: volume, usuários, alcance, sentimento |
| `sentimento_grupos` | marca x canal/dia | Polaridade e saúde da marca por grupo |
| `sentimento_temas` | tema x canal/dia | Polaridade por tema categorizado |
| `linechart` | 1 ponto/dia | Série temporal de publicações |
| `publicacoes` | 1 linha/post | Texto, sentimento, engajamento, seguidores |
| `ranking_evolutivo` | marca/dia | Posição no ranking e total de menções |

---

## Licença

GPL-3.0-or-later

---

*"O que não pode ser medido não pode ser melhorado."*
