# Contribuindo com Social Listening ETL

## Configuracao do ambiente

1. Clone o repositorio
2. Instale as dependencias: `pip install -r requirements.txt`
3. Configure as variaveis de ambiente conforme `.env.example`

## Fluxo de contribuicao

1. Abra uma issue descrevendo a mudanca proposta
2. Faca fork do repositorio
3. Crie um branch: `git checkout -b fix/nome-da-correcao`
4. Implemente as mudancas
5. Abra um Pull Request referenciando a issue

## Padroes de codigo

- Python 3.10+
- Type hints obrigatorios
- Logging via loguru (nunca `print()`)
- Formatacao: seguir PEP 8

## Mensagens de commit

Formato: `tipo: descricao imperativa em PT-BR`

Tipos: `feat`, `fix`, `refactor`, `docs`, `test`, `perf`, `chore`

## Licenca

Ao contribuir, voce concorda que suas contribuicoes serao licenciadas sob GPLv3.
