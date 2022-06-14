# Stilingue Social Listening ETL

Pipeline ETL que consome a API REST do Stilingue (social listening), transforma os dados e gera arquivos CSV estruturados para alimentar dashboards.

## Pré-requisitos

- Python 3.10+
- Git
- Acesso à API Stilingue (token gerado no Warroom)

## Instalação

```bash
git clone <repo-url>
cd stilingue-social-listening-etl
./install.sh
```

Edite o `.env` com seu token:

```env
STILINGUE_API_TOKEN=seu_token_aqui
```

## Execução manual

```bash
./run.sh
```

## Modo retroativo

Para gerar CSVs históricos de um período passado, configure no `.env`:

```env
RETROATIVO_INICIO=2026-02-01
RETROATIVO_FIM=2026-03-04
```

A pipeline itera dia a dia, gerando um CSV por dia por endpoint. O `ranking_evolutivo` é chamado uma única vez com o período completo e os registros são distribuídos por data automaticamente.

Para voltar ao modo normal (dia anterior), deixe as variáveis vazias ou remova-as.

## Agendamento

### Linux (cron)

```bash
0 6 * * * /caminho/para/stilingue-social-listening-etl/run.sh >> /caminho/para/logs/cron.log 2>&1
```

### Windows (Task Scheduler)

Execute como administrador:

```powershell
.\scripts\setup_task_scheduler.ps1
```

## Estrutura de pastas

```
stilingue-social-listening-etl/
  src/
    config.py              # Configuração via .env
    api/
      client.py            # HTTP client com retry
      endpoints.py         # Funções por endpoint
    extractors/            # Extração e mapeamento por endpoint
    transformers/          # Normalização e cálculos
    loaders/
      csv_writer.py        # Escrita de CSV
    pipeline.py            # Orquestrador principal
  data/csv/                # CSVs gerados (por endpoint/data)
  logs/                    # Logs diários
  tests/                   # Testes unitários
  scripts/                 # Scripts de deploy
```

## CSVs gerados

| Arquivo | Descrição |
|---------|-----------|
| `visao_geral/YYYYMMDD.csv` | KPIs de volume, sentimento e alcance |
| `sentimento_grupos/YYYYMMDD.csv` | Polaridade por marca e canal |
| `sentimento_temas/YYYYMMDD.csv` | Polaridade por tema |
| `linechart/YYYYMMDD.csv` | Série temporal de publicações |
| `publicacoes/YYYYMMDD.csv` | Tabela completa de publicações |
| `ranking_evolutivo/YYYYMMDD.csv` | Evolução do ranking de marcas por dia |

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `STILINGUE_API_TOKEN` | Token de autenticação da API | (obrigatório) |
| `STILINGUE_BASE_URL` | URL base da API | `https://api.stilingue.com.br` |
| `OUTPUT_DIR` | Diretório de saída dos CSVs | `./data/csv` |
| `LOG_DIR` | Diretório de logs | `./logs` |
| `DAYS_BACK` | Dias anteriores para extração (modo normal) | `1` |
| `PUBLICATIONS_LIMIT` | Limite de publicações por página | `100` |
| `REQUEST_TIMEOUT` | Timeout de requisição (segundos) | `60` |
| `REQUEST_SLEEP_BETWEEN` | Pausa entre requisições (segundos) | `1` |
| `RANKING_EVOLUTIVO_DAYS` | Janela do ranking evolutivo (dias) | `30` |
| `TEMAS_LIMIT` | Limite de temas por requisição | `50` |
| `RETROATIVO_INICIO` | Data início do modo retroativo (YYYY-MM-DD) | (vazio) |
| `RETROATIVO_FIM` | Data fim do modo retroativo (YYYY-MM-DD) | (vazio) |

## Troubleshooting

**Timeout da API:** A API tem timeout de 60s. A pipeline faz retry automático (3 tentativas com backoff exponencial). Na segunda tentativa os dados geralmente estão em cache.

**CSV vazio:** Verifique se o `date_range` no `.env` (`DAYS_BACK`) cobre um período com dados. Verifique o log em `logs/pipeline_YYYYMMDD.log`.

**Erro de token:** Confirme que `STILINGUE_API_TOKEN` está correto no `.env`. Tokens inativos são deletados periodicamente pela plataforma.

## Segurança e LGPD

- O token de acesso à API deve ser armazenado exclusivamente no `.env`, que está no `.gitignore`. Nunca versione credenciais.
- Textos de publicações podem conter dados pessoais. Os CSVs gerados devem ser tratados como dados sensíveis conforme LGPD.
- A API pode retornar campos de texto vazios quando a plataforma aplica anonimização. Isso é comportamento esperado.
- Restrinja o acesso aos diretórios `data/csv/` e `logs/` apenas a usuários autorizados.

---

## Licença

Distribuído sob a [GPLv3](LICENSE).
