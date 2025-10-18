from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.models import Cliente
from ..schemas.user import ClienteCreate, ClienteResponse
from .auth import get_current_admin_user  # ← CORREÇÃO: Usar dependência de admin

router = APIRouter()

@router.post("/", 
    response_model=ClienteResponse,
    summary="Criar cliente",
    description="Cria um novo cliente no sistema. Requer autenticação como administrador."
)
def criar_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)  # ← CORREÇÃO: Apenas admins podem criar
):
    # Verificar se CPF já existe
    db_cliente = db.query(Cliente).filter(Cliente.cpf == cliente.cpf).first()
    if db_cliente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    # Verificar se email já existe
    db_cliente_email = db.query(Cliente).filter(Cliente.email == cliente.email).first()
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
    admin_user = Depends(get_current_admin_user)  # ← CORREÇÃO: Apenas admins podem listar
):
    return db.query(Cliente).filter(Cliente.ativo == True).all()

@router.get("/{cliente_id}", 
    response_model=ClienteResponse,
    summary="Obter cliente",
    description="Retorna os dados de um cliente específico pelo ID."
)
def obter_cliente(
    cliente_id: int, 
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)  # ← CORREÇÃO: Apenas admins podem acessar
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.put("/{cliente_id}", 
    response_model=ClienteResponse,
    summary="Atualizar cliente",
    description="Atualiza os dados de um cliente existente. Requer autenticação como administrador."
)
def atualizar_cliente(
    cliente_id: int,
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)  # ← CORREÇÃO: Apenas admins podem atualizar
):
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Verificar se CPF já existe (para outro cliente)
    if cliente.cpf != db_cliente.cpf:
        cpf_existente = db.query(Cliente).filter(
            Cliente.cpf == cliente.cpf, 
            Cliente.id != cliente_id
        ).first()
        if cpf_existente:
            raise HTTPException(status_code=400, detail="CPF já cadastrado para outro cliente")
    
    # Verificar se email já existe (para outro cliente)
    if cliente.email != db_cliente.email:
        email_existente = db.query(Cliente).filter(
            Cliente.email == cliente.email, 
            Cliente.id != cliente_id
        ).first()
        if email_existente:
            raise HTTPException(status_code=400, detail="Email já cadastrado para outro cliente")
    
    # Atualizar campos
    for key, value in cliente.dict().items():
        setattr(db_cliente, key, value)
    
    db.commit()
    db.refresh(db_cliente)
    
    return db_cliente