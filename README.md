# Locadora Veículos API (ECG - Engenharia de Software)

Este é o backend de uma aplicação de locadora de veículos construída com **FastAPI**, **SQLAlchemy (ORM)** e **PostgreSQL**.

## 🚀 Tecnologias

* **Framework:** FastAPI
* **ORM:** SQLAlchemy 2.0
* **Banco de Dados:** PostgreSQL (via Docker)
* **Autenticação:** JWT (JSON Web Tokens) com Hash de Senha (Bcrypt/Passlib)
* **Containerização:** Docker e Docker Compose

## ⚙️ Configuração e Execução

O projeto é configurado para ser executado integralmente via Docker Compose, que gerencia o serviço da API e o banco de dados PostgreSQL.

### Pré-requisitos

Certifique-se de ter o **Docker** e o **Docker Compose** instalados em sua máquina.

### Passos para Inicialização

1.  **Variáveis de Ambiente:**
    Crie um arquivo `.env` na raiz do projeto (o que você já tem) e configure as variáveis de ambiente. As configurações padrão (do `docker-compose.yml`) já devem ser suficientes, mas se for rodar localmente, use:

    ```bash
    # Conteúdo do .env
    DATABASE_URL="postgresql://locadora_user:password@postgres:5432/locadora_db"
    JWT_SECRET_KEY="sua_chave_secreta_super_segura_aqui_altere_em_producao"
    # ... outras variáveis como em .env
    ```

2.  **Iniciar a Aplicação:**
    Execute o comando abaixo na pasta raiz do projeto (onde está o `docker-compose.yml`):

    ```bash
    docker compose up --build
    ```
    Este comando irá:
    * Construir a imagem do backend (Python/FastAPI).
    * Criar e iniciar o container do PostgreSQL.
    * Executar os scripts de inicialização (criação de tabelas e população de veículos).
    * Iniciar o servidor Uvicorn/FastAPI na porta `8000`.

3.  **Acesso à API:**
    * **Documentação Interativa (Swagger UI):** `http://localhost:8000/docs`
    * **Ponto de Acesso Base:** `http://localhost:8000/api/`

---

## 2. Completando o Critério 9: Testes e Robustez (Integração)

Para cobrir o requisito de testes, criaremos um arquivo simples de testes de integração (`test_auth_e_veiculos.py`) que utiliza o `TestClient` do FastAPI para simular requisições HTTP.

Você precisará garantir que a biblioteca `pytest` esteja instalada, o que já deve estar se você usa o `requirements.txt` fornecido.

### Passo 1: Estrutura do Arquivo de Teste

Crie um novo diretório chamado `tests` dentro da pasta `backend`: