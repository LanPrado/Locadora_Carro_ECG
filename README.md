# Locadora Veículos API 

Esta é a API backend para um sistema completo de gestão e locação de veículos, desenvolvida com **FastAPI** e **Python**.

# 📜 Descrição

O projeto consiste em uma API RESTful que gerencia o catálogo de veículos, clientes, o fluxo de locações e um painel de estatísticas administrativas. O sistema implementa um rigoroso controle de acesso baseado em funções (Admin e Cliente) para proteger rotas sensíveis e garantir a correta separação de responsabilidades.

# ✨ Funcionalidades Principais

* Autenticação e Autorização (JWT/RBAC):** Sistema completo de registro e login com tokens JWT. Rotas protegidas controlam o acesso: o Admin pode gerenciar veículos e clientes, enquanto o Cliente só pode realizar reservas e consultar suas próprias locações.
* Gestão de Veículos e Clientes:** Operações CRUD completas (Criar, Listar, Obter, Atualizar, Deletar), restritas ao administrador.
* Sistema de Locações (Reservas):**
    * Fluxo completo de reserva (`/reservar`) que inclui a verificação de conflito de datas e a criação de cliente se for novo.
    * Cálculo de diária com descontos progressivos para longos períodos.
    * Endpoints de *Check-in* e *Check-out* com cálculo de multa por atraso e atualização da quilometragem do veículo.
* **Dashboard de Estatísticas:** Endpoint protegido para administradores que retorna o total de veículos (por status), clientes ativos, locações ativas e faturamento mensal/total.
* **Ambiente em Contêiner:** O projeto está totalmente configurado para ser executado com Docker, garantindo um ambiente de desenvolvimento e produção consistente.

# 🛠️ Tecnologias Utilizadas

| Componente | Tecnologia | Uso/Detalhes |
| :--- | :--- | :--- |
| *Backend** | Python 3.12, FastAPI | Framework de alta performance. |
| *Banco de Dados** | PostgreSQL | Usado para persistência de dados. |
| *ORM** | SQLAlchemy 2.0 | Mapeamento Objeto-Relacional. |
| *Validação de Dados** | Pydantic | Utilizado para DTOs (Schemas) e validação automática. |
| *Autenticação** | Passlib (Bcrypt), python-jose (JWT) | Hashing seguro de senhas e geração/verificação de tokens. |
| *Contêiner** | Docker, Docker Compose | Orquestração do backend e do banco de dados. |

## 🚀 Como Executar o Projeto

A maneira mais simples de executar este projeto é utilizando **Docker** e **Docker Compose**, que configuram o ambiente e o banco de dados PostgreSQL automaticamente.

### Pré-requisitos

* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

### Passos para a Instalação

1.  **Variáveis de Ambiente:** Certifique-se de que o arquivo `.env` na raiz do projeto está configurado. O `docker-compose.yml` já fornece variáveis de ambiente padrão para o `postgres`.

2.  **Inicie os Contêineres:** Execute o comando abaixo na pasta raiz do projeto (onde está o `docker-compose.yml`):

    ```bash
    docker compose up --build
    ```
    Este comando irá:
    * Construir a imagem do backend.
    * Iniciar o PostgreSQL e criar as tabelas.
    * Executar o script de população inicial de veículos.
    * Iniciar o servidor Uvicorn/FastAPI.

A API estará disponível em `http://localhost:8000`.

## 📚 Documentação da API

Com a aplicação em execução, a documentação interativa (Swagger UI) gerada automaticamente pelo FastAPI estará disponível no seguinte endereço:

[http://localhost:8000/docs](http://localhost:8000/docs)

Lá, você pode visualizar todos os endpoints, seus modelos de dados (Schemas) e testá-los diretamente pelo navegador.

# ✅ Executando os Testes

Os testes de integração foram escritos com **Pytest** para garantir o correto funcionamento dos fluxos de autenticação e rotas protegidas.

Para executar os testes, com os contêineres em execução, abra um novo terminal e execute o seguinte comando:

```bash
docker compose exec backend pytest backend/tests/
