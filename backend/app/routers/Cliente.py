from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db

from ..models.Cliente import Cliente 

from Schemas.Cliente import ClienteCreate, ClienteResponse 

from .autenticacao import get_current_admin_user
# ---------------------------------

router = APIRouter()

@router.post("/", 
    response_model=ClienteResponse,
    summary="Criar cliente",
    description="Cria um novo cliente no sistema. Requer autenticação como administrador."
)
def criar_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    # Verificar se CPF já existe
    db_cliente = db.query(Cliente).filter(Cliente.cli_cpf == cliente.cli_cpf).first()
    if db_cliente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")

    # Verificar se email já existe
    db_cliente_email = db.query(Cliente).filter(Cliente.cli_email == cliente.cli_email).first()
    if db_cliente_email:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Criar novo cliente
    novo_cliente = Cliente(**cliente.dict())
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)

    return novo_cliente

@router.get("/", 
    response_model=List[ClienteResponse],
    summary="Listar clientes",
    description="Retorna lista de todos os clientes ativos no sistema."
)
def listar_clientes(
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    return db.query(Cliente).filter(Cliente.cli_ativo == True).all()

# ... (o resto das rotas GET, PUT, etc. também precisam usar os nomes corretos das colunas
# como cli_id, cli_cpf, cli_email de Cliente.py)