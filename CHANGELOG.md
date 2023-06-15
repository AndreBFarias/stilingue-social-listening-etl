# Changelog

Todas as mudanças notáveis deste projeto serão documentadas aqui.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [2.0.0] - 2023-09-01

### Adicionado
- Dashboard interativo Streamlit com 4 páginas de análise
- 23 métricas analíticas (saúde da marca, share of voice, favorabilidade, índice de crise)
- Relatórios HTML estáticos self-contained (4 relatórios)
- Pipeline incremental com detecção automática de gaps
- Consolidação automática de CSVs com deduplicação
- Suporte a formato Parquet nos consolidados
- Reconsolidação com data mínima configurável
- Gerador de dados de demonstração para portfolio

### Alterado
- Whitelabel completo: referências corporativas removidas
- Renomeado para Whisper-Pulse
- Variáveis de ambiente padronizadas (SOCIAL_LISTENING_*)
- README reescrito com wireframes do dashboard

## [1.1.0] - 2023-06-01

### Adicionado
- Suporte a empacotamento PyInstaller para Linux e Windows
- Scripts de build para distribuição multiplataforma

## [1.0.0] - 2023-01-01

### Adicionado
- Pipeline ETL para API de social listening com exportação CSV
- 6 extractors (visão geral, sentimento, publicações, ranking, linechart, temas)
- HTTP client com retry exponencial e rate-limiting
- Schemas de validação de dados
- Configuração via .env
- Logging rotacionado via Loguru
