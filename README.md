Sistema de Recomendação com FastAPI e Docker
Este repositório contém a implementação do trabalho acadêmico "Desenvolvimento de um Sistema de Recomendação".

Escopo do Projeto
De acordo com os requisitos propostos, o projeto contempla:

Dataset: Utilização de um dataset público (MovieLens 100K).

Modelo de Recomendação: Implementação de um sistema de filtragem baseada em conteúdo (content-based), com flexibilidade para filtragem colaborativa ou híbrida.

API REST: Desenvolvimento de uma API utilizando FastAPI com as seguintes funcionalidades:

Adição de usuários e itens.

Geração de recomendações personalizadas para um usuário.

Atualização de preferências do usuário.

Infraestrutura: Conteinerização da aplicação utilizando Docker e docker-compose.

Documentação: Documentação interativa e automática da API gerada via Swagger UI.

Testes: Cobertura de testes unitários e de integração.

Status Atual
Estrutura inicial do projeto configurada.

API mínima funcional rodando em FastAPI.

Configuração base para Docker e ambiente de testes concluída.

Base do sistema de recomendação preparada e integrada ao dataset MovieLens 100K.

Sobre o Dataset
O projeto está configurado para consumir o MovieLens 100K. Caso o dataset não seja encontrado no ambiente local, o sistema possui um mecanismo de fallback para um catálogo reduzido, focado em facilitar o desenvolvimento e testes rápidos.

Cronograma de Entregas:

01/06 a 02/06: Organização do repositório, análise dos requisitos e definição de escopo.

03/06 a 04/06: Escolha do dataset e preparação do ambiente.

05/06 a 06/06: Estruturação da API e da arquitetura base do projeto.

07/06 a 08/06: Implementação da primeira versão do modelo de recomendação.

09/06 a 10/06: Integração do modelo de recomendação aos endpoints da API.

11/06 a 12/06: Criação do Dockerfile e do docker-compose.yml.

13/06 a 14/06: Escrita e execução dos testes unitários e de integração.

15/06 a 16/06: Refinamento da documentação (Swagger) e adição de exemplos de uso.

17/06 a 18/06: Ajustes de qualidade, tratamento de erros e validações da API.

19/06 a 20/06: Revisão geral e correção de bugs finais.

21/06 a 22/06: Preparação para a apresentação e entrega final.

Execução
Rodando Localmente

pip install -r requirements.txt

python scripts/download_movielens_100k.py

uvicorn app.main:app --reload

Rodando com Docker

docker compose up --build
