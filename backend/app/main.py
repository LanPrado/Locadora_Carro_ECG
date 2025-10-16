from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Imports do database
from .database import engine, Base, SessionLocal

# Importar TODOS os modelos ANTES de criar as tabelas
from .models.models import Veiculo, Cliente, Locacao
from .models.user import Usuario  # ← Garantir que está importado

print("🗄️ Criando tabelas do banco de dados...")

# Criar as tabelas - DEVE vir depois de importar todos os modelos
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")

print("🔧 Carregando rotas de autenticação...")
from .routes import auth, veiculos, clientes, locacoes, dashboard
print("✅ Rotas carregadas")

app = FastAPI(
    title="Locadora Veículos API",
    description="Sistema completo de locação de veículos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(veiculos.router, prefix="/api/veiculos", tags=["Veículos"])
app.include_router(clientes.router, prefix="/api/clientes", tags=["Clientes"])
app.include_router(locacoes.router, prefix="/api/locacoes", tags=["Locações"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {
        "message": "Locadora Veículos API", 
        "version": "1.0.0",
        "docs": "/docs"
    }

# Dependência para obter a sessão do banco de dados
@app.middleware("http")
async def db_session_middleware(request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    request.state.db.close()
    return response