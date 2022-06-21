# Changelog

## [Não lançado]

## [1.1.0] - 2026-03-16

### Adicionado
- Schemas de dados (src/schemas.py)
- Módulo __main__.py para execução como pacote
- Build para Windows (build.bat)
- Spec do PyInstaller

### Alterado
- Refatoração do pipeline principal
- Atualização do csv_writer com novos campos
- Ajustes de configuração em src/config.py

## [1.0.0] - 2023-01-01

### Adicionado
- Pipeline de ETL para dados do Stilingue Social Listening
- Coleta automática com agendamento (cron/Task Scheduler)
- Modo retroativo por intervalo de datas
- Exportação em CSV por tema
- Build executável multiplataforma (Linux e Windows)
- Suporte a variáveis de ambiente via .env
