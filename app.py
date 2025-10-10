import sys
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# =============================================================================
# CONFIGURAÇÃO DO PATH PARA IMPORTS
# =============================================================================

# Adiciona o backend ao path do Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Importações dos módulos do backend
from backend.app.database.database import engine, Base, get_db
from backend.app.models.models import (
    Usuario, Veiculo, Cliente, Locacao,
    TipoUsuario, CategoriaVeiculo, StatusVeiculo, StatusLocacao
)
from backend.app.schemas.user import (
    UsuarioCreate, UsuarioResponse, LoginRequest, Token,
    VeiculoCreate, VeiculoResponse,
    ClienteCreate, ClienteResponse,
    LocacaoCreate, LocacaoResponse, ReservaRequest,
    MudarStatusRequest, DashboardStats
)

# =============================================================================
# CONFIGURAÇÕES JWT E AUTENTICAÇÃO
# =============================================================================

SECRET_KEY = "loadora-secret-key-2024-mudar-em-producao"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def criar_hash_senha(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha: str, hash_senha: str):
    return pwd_context.verify(senha, hash_senha)

def criar_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verificar_token(token: str = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception

# =============================================================================
# INICIALIZAÇÃO DO FASTAPI
# =============================================================================

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

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def calcular_multa_atraso(data_fim_previsto: datetime, data_devolucao: datetime, diaria: float) -> float:
    if data_devolucao <= data_fim_previsto:
        return 0.0
    
    diferenca = data_devolucao - data_fim_previsto
    horas_atraso = diferenca.total_seconds() / 3600
    
    if horas_atraso <= 24:
        multa = (horas_atraso // 1 + (1 if horas_atraso % 1 > 0 else 0)) * 10.0
    else:
        multa = 240.0 + diaria
    
    return multa

# =============================================================================
# ENDPOINTS PÚBLICOS
# =============================================================================

@app.get("/")
def root():
    return {
        "message": "Loadora Veículos API", 
        "version": "1.0.0",
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "loadora-backend"}

# =============================================================================
# ENDPOINTS DE AUTENTICAÇÃO
# =============================================================================

@app.post("/api/auth/registrar", response_model=UsuarioResponse)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    novo_usuario = Usuario(
        email=usuario.email,
        nome=usuario.nome,
        senha_hash=criar_hash_senha(usuario.senha)
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return novo_usuario

@app.post("/api/auth/login", response_model=Token)
def login_usuario(login_data: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == login_data.email).first()
    
    if not usuario or not verificar_senha(login_data.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    
    access_token = criar_access_token(data={"sub": usuario.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

# =============================================================================
# ENDPOINTS DE VEÍCULOS
# =============================================================================

@app.post("/api/veiculos", response_model=VeiculoResponse)
def criar_veiculo(
    veiculo: VeiculoCreate,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    db_veiculo = db.query(Veiculo).filter(Veiculo.placa == veiculo.placa).first()
    if db_veiculo:
        raise HTTPException(status_code=400, detail="Placa já cadastrada")
    
    novo_veiculo = Veiculo(**veiculo.dict())
    db.add(novo_veiculo)
    db.commit()
    db.refresh(novo_veiculo)
    
    return novo_veiculo

@app.get("/api/veiculos", response_model=List[VeiculoResponse])
def listar_veiculos(
    categoria: Optional[str] = None,
    status: Optional[StatusVeiculo] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Veiculo)
    
    if categoria:
        query = query.filter(Veiculo.categoria == categoria)
    
    if status:
        query = query.filter(Veiculo.status == status)
    
    return query.all()

@app.get("/api/veiculos/{veiculo_id}", response_model=VeiculoResponse)
def obter_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo

@app.put("/api/veiculos/{veiculo_id}", response_model=VeiculoResponse)
def atualizar_veiculo(
    veiculo_id: int,
    veiculo: VeiculoCreate,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    db_veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not db_veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    for key, value in veiculo.dict().items():
        setattr(db_veiculo, key, value)
    
    db.commit()
    db.refresh(db_veiculo)
    
    return db_veiculo

@app.delete("/api/veiculos/{veiculo_id}")
def deletar_veiculo(
    veiculo_id: int,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    db.delete(veiculo)
    db.commit()
    
    return {"message": "Veículo deletado com sucesso"}

# =============================================================================
# ENDPOINTS DE CLIENTES
# =============================================================================

@app.post("/api/clientes", response_model=ClienteResponse)
def criar_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    db_cliente = db.query(Cliente).filter(Cliente.cpf == cliente.cpf).first()
    if db_cliente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    novo_cliente = Cliente(**cliente.dict())
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    
    return novo_cliente

@app.get("/api/clientes", response_model=List[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).filter(Cliente.ativo == True).all()

@app.get("/api/clientes/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@app.put("/api/clientes/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(
    cliente_id: int,
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    for key, value in cliente.dict().items():
        setattr(db_cliente, key, value)
    
    db.commit()
    db.refresh(db_cliente)
    
    return db_cliente

# =============================================================================
# ENDPOINTS DE LOCAÇÕES
# =============================================================================

@app.post("/api/locacoes/reservar", response_model=LocacaoResponse)
def reservar_veiculo(
    reserva: ReservaRequest,
    db: Session = Depends(get_db)
    # Removido temporariamente a autenticação para testes
    # user_info: dict = Depends(verificar_token)
):
    veiculo = db.query(Veiculo).filter(Veiculo.id == reserva.veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    if veiculo.status != StatusVeiculo.DISPONIVEL:
        raise HTTPException(status_code=400, detail="Veículo não disponível para reserva")
    
    locacoes_conflitantes = db.query(Locacao).filter(
        Locacao.veiculo_id == reserva.veiculo_id,
        Locacao.status.in_([StatusLocacao.RESERVADA, StatusLocacao.ATIVA]),
        Locacao.data_inicio <= reserva.data_fim,
        Locacao.data_fim >= reserva.data_inicio
    ).first()
    
    if locacoes_conflitantes:
        raise HTTPException(status_code=400, detail="Veículo já reservado neste período")
    
    cliente = db.query(Cliente).filter(Cliente.cpf == reserva.cpf).first()
    if not cliente:
        cliente = Cliente(
            cpf=reserva.cpf,
            nome=reserva.nome,
            email=reserva.email,
            telefone=reserva.telefone,
            cnh=reserva.cnh,
            data_validade_cnh=datetime.now() + timedelta(days=365*5),
            endereco=reserva.endereco
        )
        db.add(cliente)
        db.flush()
    
    dias_locacao = (reserva.data_fim - reserva.data_inicio).days
    valor_total = dias_locacao * veiculo.diaria
    
    if dias_locacao >= 7:
        valor_total *= 0.9
    elif dias_locacao >= 3:
        valor_total *= 0.95
    
    nova_locacao = Locacao(
        cliente_id=cliente.id,
        veiculo_id=reserva.veiculo_id,
        data_inicio=reserva.data_inicio,
        data_fim=reserva.data_fim,
        valor_total=valor_total,
        status=StatusLocacao.RESERVADA
    )
    
    veiculo.status = StatusVeiculo.LOCADO
    
    db.add(nova_locacao)
    db.commit()
    db.refresh(nova_locacao)
    
    return nova_locacao

@app.get("/api/locacoes", response_model=List[LocacaoResponse])
def listar_locacoes(
    status: StatusLocacao = None,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    query = db.query(Locacao)
    
    if status:
        query = query.filter(Locacao.status == status)
    
    return query.all()

@app.get("/api/locacoes/minhas-locacoes", response_model=List[LocacaoResponse])
def minhas_locacoes(
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    locacoes = db.query(Locacao).join(Cliente).filter(Cliente.email == usuario_email).all()
    return locacoes

@app.post("/api/locacoes/{locacao_id}/mudar-status")
def mudar_status_veiculo(
    locacao_id: int,
    mudanca_status: MudarStatusRequest,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    locacao = db.query(Locacao).filter(Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(status_code=404, detail="Locação não encontrada")
    
    veiculo = locacao.veiculo
    
    if mudanca_status.novo_status not in [status.value for status in StatusVeiculo]:
        raise HTTPException(
            status_code=400, 
            detail=f"Status inválido. Status permitidos: {[status.value for status in StatusVeiculo]}"
        )
    
    status_anterior = veiculo.status.value
    veiculo.status = StatusVeiculo(mudanca_status.novo_status)
    
    if (mudanca_status.novo_status == StatusVeiculo.DISPONIVEL.value and 
        locacao.status == StatusLocacao.ATIVA):
        
        locacao.status = StatusLocacao.FINALIZADA
        locacao.data_devolucao = datetime.utcnow()
        
        if locacao.data_devolucao > locacao.data_fim:
            multa = calcular_multa_atraso(locacao.data_fim, locacao.data_devolucao, veiculo.diaria)
            locacao.valor_total += multa
    
    db.commit()
    
    return {
        "message": "Status alterado com sucesso",
        "veiculo_id": veiculo.id,
        "placa": veiculo.placa,
        "status_anterior": status_anterior,
        "novo_status": veiculo.status.value,
        "locacao_status": locacao.status.value
    }

# =============================================================================
# ENDPOINTS DO DASHBOARD
# =============================================================================

@app.get("/api/dashboard/stats", response_model=DashboardStats)
def obter_estatisticas(
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    total_veiculos = db.query(Veiculo).count()
    
    veiculos_disponiveis = db.query(Veiculo).filter(
        Veiculo.status == StatusVeiculo.DISPONIVEL
    ).count()
    
    total_clientes = db.query(Cliente).filter(Cliente.ativo == True).count()
    
    locacoes_ativas = db.query(Locacao).filter(
        Locacao.status == StatusLocacao.ATIVA
    ).count()
    
    inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    faturamento_mensal = db.query(Locacao).filter(
        Locacao.status == StatusLocacao.FINALIZADA,
        Locacao.data_devolucao >= inicio_mes
    ).with_entities(Locacao.valor_total).all()
    
    faturamento_total = sum([faturamento[0] for faturamento in faturamento_mensal]) if faturamento_mensal else 0.0
    
    return DashboardStats(
        total_veiculos=total_veiculos,
        veiculos_disponiveis=veiculos_disponiveis,
        total_clientes=total_clientes,
        locacoes_ativas=locacoes_ativas,
        faturamento_mensal=float(faturamento_total)
    )

# =============================================================================
# INICIALIZAÇÃO DO SERVIDOR
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)