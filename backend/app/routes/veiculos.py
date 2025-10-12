from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.models import Veiculo, StatusVeiculo
from ..schemas.user import VeiculoCreate, VeiculoResponse

router = APIRouter()

@router.post("/", response_model=VeiculoResponse)
def criar_veiculo(
    veiculo: VeiculoCreate, 
    db: Session = Depends(get_db),
    #usuario_email: str = Depends(verificar_token)
):
    db_veiculo = db.query(Veiculo).filter(Veiculo.placa == veiculo.placa).first()
    if db_veiculo:
        raise HTTPException(status_code=400, detail="Placa já cadastrada")
    
    novo_veiculo = Veiculo(**veiculo.dict())
    db.add(novo_veiculo)
    db.commit()
    db.refresh(novo_veiculo)
    
    return novo_veiculo

@router.get("/", response_model=List[VeiculoResponse])
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

@router.get("/{veiculo_id}", response_model=VeiculoResponse)
def obter_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo

@router.put("/{veiculo_id}", response_model=VeiculoResponse)
def atualizar_veiculo(
    veiculo_id: int,
    veiculo: VeiculoCreate,
    db: Session = Depends(get_db),
   # usuario_email: str = Depends(verificar_token)
):
    db_veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not db_veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    for key, value in veiculo.dict().items():
        setattr(db_veiculo, key, value)
    
    db.commit()
    db.refresh(db_veiculo)
    
    return db_veiculo

@router.delete("/{veiculo_id}")
def deletar_veiculo(
    veiculo_id: int,
    db: Session = Depends(get_db),
   # usuario_email: str = Depends(verificar_token)
):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    db.delete(veiculo)
    db.commit()
    
    return {"message": "Veículo deletado com sucesso"}