from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .Routers import auth, veiculos, clientes, locacoes, dashboard
import uvicorn

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Loadora Veículos API",
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

# Registrar rotas
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(veiculos.router, prefix="/api/veiculos", tags=["Veículos"])
app.include_router(clientes.router, prefix="/api/clientes", tags=["Clientes"])
app.include_router(locacoes.router, prefix="/api/locacoes", tags=["Locações"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {
        "message": "Loadora Veículos API", 
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "loadora-backend"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)