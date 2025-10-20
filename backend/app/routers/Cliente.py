# Mude o nome deste arquivo para 'clientes.py' (plural)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
# --- CORREÇÃO DE IMPORTS ---
from ..models.Cliente import Cliente # O Modelo (para o DB)
from ..models.Adm import Admin # Para type hint da dependência
from ..Schemas.Cliente import ClienteCreate, ClienteResponse # Os Schemas (para a API)
from ..utils.dependencies import get_current_admin_user # A dependência de auth
# ---------------------------------

router = APIRouter()

# Esta rota é para o ADMIN criar clientes manualmente
@router.post("/", 
    response_model=ClienteResponse,
    summary="Criar cliente (Admin)",
    description="Cria um novo cliente no sistema. Requer autenticação como administrador."
)
def criar_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    admin_user: Admin = Depends(get_current_admin_user) # Protegido
):
    db_cliente = db.query(Cliente).filter(Cliente.cli_cpf == cliente.cli_cpf).first()
    if db_cliente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")

    db_cliente_email = db.query(Cliente).filter(Cliente.cli_email == cliente.cli_email).first()
    if db_cliente_email:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # O Schema 'ClienteCreate' já tem os campos corretos
    novo_cliente = Cliente(**cliente.dict())
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)

    return novo_cliente

@router.get("/", 
    response_model=List[ClienteResponse],
    summary="Listar clientes (Admin)",
    description="Retorna lista de todos os clientes ativos no sistema."
)
def listar_clientes(
    db: Session = Depends(get_db),
    admin_user: Admin = Depends(get_current_admin_user) # Protegido
):
    return db.query(Cliente).filter(Cliente.cli_ativo == True).all()

@router.get("/{cliente_id}", 
    response_model=ClienteResponse,
    summary="Obter cliente (Admin)",
    description="Retorna os dados de um cliente específico pelo ID."
)
def obter_cliente(
    cliente_id: str, # CORREÇÃO: ID é string (UUID)
    db: Session = Depends(get_db),
    admin_user: Admin = Depends(get_current_admin_user) # Protegido
):
    cliente = db.query(Cliente).filter(Cliente.cli_id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

# (O resto das suas rotas PUT de cliente seguiriam esta lógica)