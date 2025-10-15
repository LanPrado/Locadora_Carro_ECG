# backend/tests/test_auth_e_veiculos.py

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#Importações necessárias do projeto
from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models.models import CategoriaVeiculo, StatusVeiculo

# Variável global para armazenar o token JWT para testes subsequentes
ADMIN_TOKEN = ""

# 1. SETUP DO BANCO DE DADOS DE TESTE
# Usamos SQLite em memória para testes rápidos
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria as tabelas para o banco de dados de teste (Apenas para este ambiente de teste)
Base.metadata.create_all(bind=engine)

# 2. FUNÇÃO DE SOBRESCRITA DA DEPENDÊNCIA get_db
def override_get_db():
    """Sobrescreve a dependência de sessão do FastAPI para usar o banco de dados de teste."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # Garante que a sessão é fechada após cada teste
        db.close()

# Aplica a sobrescrita de dependência (MUITO IMPORTANTE!)
app.dependency_overrides[get_db] = override_get_db

# Inicializa o cliente de teste
client = TestClient(app)

# 3. TESTES DE AUTENTICAÇÃO E VEÍCULOS
# NOTA: Usamos prefixos (a, b, c, d) para forçar a ordem de execução do pytest.

def test_a_registrar_primeiro_admin():
    """Testa o registro do primeiro usuário. Ele deve ser criado com role 'admin'."""
    response = client.post(
        "/api/auth/registrar",
        json={"email": "admin@locadora.com", "nome": "Admin Principal", "senha": "senhaforte"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@locadora.com"
    assert data["role"] == "admin"
    assert "id" in data

def test_b_login_admin_e_obter_token():
    """Testa o login do admin e o retorno do token de acesso (JWT)."""
    response = client.post(
        "/api/auth/login",
        # O FastAPI espera dados de formulário (form-data) para OAuth2PasswordRequestForm
        data={"username": "admin@locadora.com", "password": "senhaforte"},
    )
    
    # response = client.post("/api/auth/login", json={"email": "admin@locadora.com", "senha": "senhaforte"})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Armazena o token para uso nos testes que exigem autorização
    global ADMIN_TOKEN
    ADMIN_TOKEN = data["access_token"]

def test_c_criar_veiculo_como_admin():
    """Testa a criação de um veículo, rota protegida por Admin (Critério 7)."""
    veiculo_data = {
        "placa": "ABC1A23",
        "modelo": "Carro Teste",
        "marca": "Marca Teste",
        "ano": 2025,
        "categoria": CategoriaVeiculo.ECONOMICO.value,
        "diaria": 100.0,
        "quilometragem": 1000,
    }
    
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    
    response = client.post(
        "/api/veiculos/",
        json=veiculo_data,
        headers=headers
    )
    
    # Verifica o status code para sucesso
    assert response.status_code == 200
    data = response.json()
    assert data["placa"] == "ABC1A23"
    assert data["status"] == StatusVeiculo.DISPONIVEL.value
    assert "id" in data

def test_d_criar_veiculo_sem_token_deve_falhar():
    """Testa que a rota de criação de veículo deve ser bloqueada sem token (Critério 7)."""
    response = client.post(
        "/api/veiculos/",
        json={"placa": "XYZ1B34", "modelo": "Falha", "marca": "Falha", "ano": 2020, "categoria": CategoriaVeiculo.LUXO.value, "diaria": 1.0},
    )
    # Deve retornar 401 UNAUTHORIZED
    assert response.status_code == 401
    assert "detail" in response.json() and "Could not validate credentials" in response.json()["detail"]