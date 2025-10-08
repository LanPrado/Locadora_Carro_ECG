from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Cliente
from ..schemas import ClienteCreate, ClienteResponse
from ..auth import verificar_token

router = APIRouter()

@router.post("/", response_model=ClienteResponse)
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

@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).filter(Cliente.ativo == True).all()

@router.get("/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.put("/{cliente_id}", response_model=ClienteResponse)
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