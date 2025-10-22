from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db  
from app.models.Veiculos import Veiculo, StatusVeiculo, CategoriaVeiculo  
from app.models.Adm import Admin 

from app.Schemas.Veiculos import VeiculoCreate, VeiculoResponse  
from app.utils.dependencies import get_current_admin_user  
from enum import Enum

router = APIRouter()

class CategoriaFilter(str, Enum):
    ECONOMICO = "ECONOMICO"
    INTERMEDIARIO = "INTERMEDIARIO"
    LUXO = "LUXO"
    SUV = "SUV"

class StatusFilter(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    LOCADO = "LOCADO"
    MANUTENCAO = "MANUTENCAO"

@router.post("/", response_model=VeiculoResponse, summary="Adicionar novo veículo (Admin)")
def criar_veiculo(
    veiculo: VeiculoCreate, 
    db: Session = Depends(get_db),
    usuario_admin: Admin = Depends(get_current_admin_user) # Protegido
):
    # Nomes de coluna corretos (sem prefixo)
    db_veiculo = db.query(Veiculo).filter(Veiculo.placa == veiculo.placa).first()
    if db_veiculo:
        raise HTTPException(status_code=400, detail="Placa já cadastrada")
    
    novo_veiculo = Veiculo(**veiculo.dict())
    db.add(novo_veiculo)
    db.commit()
    db.refresh(novo_veiculo)
    
    return novo_veiculo

@router.get("/", response_model=List[VeiculoResponse], summary="Listar veículos (Público/Cliente)")
def listar_veiculos(
    categoria: Optional[CategoriaFilter] = None,
    status: Optional[StatusFilter] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Veiculo)
        
        if categoria is not None:
            categoria_enum = CategoriaVeiculo(categoria.value)
            query = query.filter(Veiculo.categoria == categoria_enum)
        
        if status is not None:
            status_enum = StatusVeiculo(status.value)
            query = query.filter(Veiculo.status == status_enum)
        
        veiculos = query.all()
        return veiculos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/{veiculo_id}", response_model=VeiculoResponse, summary="Obter um veículo (Público/Cliente)")
def obter_veiculo(veiculo_id: str, db: Session = Depends(get_db)):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo

@router.put("/{veiculo_id}", response_model=VeiculoResponse, summary="Atualizar veículo (Admin)")
def atualizar_veiculo(
    veiculo_id: str, 
    veiculo: VeiculoCreate,
    db: Session = Depends(get_db),
    usuario_admin: Admin = Depends(get_current_admin_user)
):
    db_veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not db_veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    if veiculo.placa != db_veiculo.placa:
        placa_existente = db.query(Veiculo).filter(Veiculo.placa == veiculo.placa).first()
        if placa_existente:
            raise HTTPException(status_code=400, detail="Placa já cadastrada")
    
    # Atualiza descrição, status, etc.
    for key, value in veiculo.dict(exclude_unset=True).items():
        setattr(db_veiculo, key, value)
    
    db.commit()
    db.refresh(db_veiculo)
    
    return db_veiculo

@router.patch("/{veiculo_id}/status", response_model=VeiculoResponse, summary="Alterar status do veículo (Admin)")
def alterar_status_veiculo(
    veiculo_id: str,
    status: StatusFilter,
    db: Session = Depends(get_db),
    usuario_admin: Admin = Depends(get_current_admin_user)
):
    db_veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not db_veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    status_enum = StatusVeiculo(status.value)
    db_veiculo.status = status_enum
    db.commit()
    db.refresh(db_veiculo)
    
    return db_veiculo

@router.delete("/{veiculo_id}", summary="Deletar veículo (Admin)")
def deletar_veiculo(
    veiculo_id: str,
    db: Session = Depends(get_db),
    usuario_admin: Admin = Depends(get_current_admin_user)
):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    db.delete(veiculo)
    db.commit()
    
    return {"message": "Veículo deletado com sucesso"}