from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from starlette.responses import FileResponse 
import os 
from pathlib import Path

from .database import engine, Base, SessionLocal

from .models.models import Veiculo
from .models.Cliente import Cliente
from .models.Reservar import Reserva
from .models.Adm import Admin
from .models.Veiculos import CategoriaVeiculo, StatusVeiculo

from .routers import autenticacao, veiculos, dashboard
from .routers import clientes as router_clientes
from .routers import reservas as router_reservas

# Criar tabelas
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas verificadas/criadas com sucesso.")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
   
app = FastAPI(
    title="Locadora Veículos API",
    description="Sistema completo de locação de veículos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ... (Middleware CORS) ...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (Static files) ...
static_dir = Path(__file__).parent / "static" 
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# --- CORREÇÃO: Incluir os routers com prefixo /api ---
app.include_router(autenticacao.cliente_auth_router, prefix="/api", tags=["Autenticação"])
app.include_router(autenticacao.admin_auth_router, prefix="/api", tags=["Autenticação"])
app.include_router(veiculos.router, prefix="/api/veiculos", tags=["Veículos"])
app.include_router(router_clientes.router, prefix="/api/clientes", tags=["Clientes (Admin)"])
app.include_router(router_reservas.router, prefix="/api/reservas", tags=["Reservas/Locações"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard (Admin)"])
@app.get("/", include_in_schema=False)
async def root():
    html_file_path = Path(__file__).parent / "static" / "apresentacao.html"
    if html_file_path.exists():
        return FileResponse(html_file_path)
    return {
        "message": "Locadora Veículos API", 
        "version": "1.0.0",
        "docs": "/docs"
    }

