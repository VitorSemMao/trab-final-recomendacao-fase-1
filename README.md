# Sistema de Recomendacao com FastAPI e Docker

Este repositorio contem a implementacao do trabalho academico "Desenvolvimento de um Sistema de Recomendacao".

## Escopo do projeto

- Dataset publico MovieLens 100K.
- Modelo de recomendacao com base em conteudo e feedback hibrido.
- API REST com FastAPI para cadastrar usuarios e itens, gerar recomendacoes e atualizar preferencias.
- Containerizacao com Docker e `docker-compose`.
- Documentacao automatica via Swagger UI.
- Testes unitarios e de integracao.

## Status atual

- Estrutura do projeto configurada.
- API minima funcional em FastAPI.
- Base para Docker e ambiente de testes concluida.
- Base do sistema de recomendacao integrada ao dataset MovieLens 100K.
- Feedback de usuario ativo via notas e recomendacao hibrida.

## Dataset

O projeto usa o [MovieLens 100K](https://grouplens.org/datasets/movielens/100k/) e possui fallback para um catalogo reduzido quando o dataset nao estiver disponivel localmente.

## Feedback e recomendacao hibrida

A API aceita notas em `POST /users/{user_id}/ratings` e combina:

- perfil de conteudo baseado em preferencias e notas anteriores
- similaridade entre usuarios para reforcar itens aprovados por perfis parecidos

## Cronograma de entregas

| Periodo | Entrega |
| --- | --- |
| 01/06 a 02/06 | Organizacao do repositorio, analise dos requisitos e definicao de escopo |
| 03/06 a 04/06 | Escolha do dataset e preparacao do ambiente |
| 05/06 a 06/06 | Estruturacao da API e da arquitetura base do projeto |
| 07/06 a 08/06 | Implementacao da primeira versao do modelo de recomendacao |
| 09/06 a 10/06 | Integracao do modelo de recomendacao aos endpoints da API |
| 11/06 a 12/06 | Criacao do `Dockerfile` e do `docker-compose.yml` |
| 13/06 a 14/06 | Escrita e execucao dos testes unitarios e de integracao |
| 15/06 a 16/06 | Refinamento da documentacao e adicao de exemplos de uso |
| 17/06 a 18/06 | Ajustes de qualidade, tratamento de erros e validacoes da API |
| 19/06 a 20/06 | Revisao geral e correcao de bugs finais |
| 21/06 a 22/06 | Preparacao para a apresentacao e entrega final |

## Execucao

### Rodando localmente

```bash
pip install -r requirements.txt
python scripts/download_movielens_100k.py
uvicorn app.main:app --reload
```

### Rodando com Docker

```bash
docker compose up --build
```
