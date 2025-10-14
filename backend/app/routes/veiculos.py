from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.models import Veiculo, StatusVeiculo, CategoriaVeiculo
from ..schemas.user import VeiculoCreate, VeiculoResponse

#  IMPORTE as funções de autenticação
from ..routes.auth import get_current_admin_user
from ..models.user import Usuario

router = APIRouter()

#  ENDPOINT POST PARA CRIAR VEÍCULO (APENAS ADMIN)
@router.post("/", response_model=VeiculoResponse)
def criar_veiculo(
    veiculo: VeiculoCreate, 
    db: Session = Depends(get_db),
    usuario_admin: Usuario = Depends(get_current_admin_user)  # ⭐ Só admin pode criar
):
    # Verificar se placa já existe
    db_veiculo = db.query(Veiculo).filter(Veiculo.placa == veiculo.placa).first()
    if db_veiculo:
        raise HTTPException(status_code=400, detail="Placa já cadastrada")
    
    # Criar novo veículo
    novo_veiculo = Veiculo(**veiculo.dict())
    db.add(novo_veiculo)
    db.commit()
    db.refresh(novo_veiculo)
    
    return novo_veiculo

@router.get("/", response_model=List[VeiculoResponse])
def listar_veiculos(
    categoria: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Veiculo)
        
        # Mapear categoria string para Enum
        if categoria:
            categoria_map = {
                "econômico": CategoriaVeiculo.ECONOMICO,
                "economico": CategoriaVeiculo.ECONOMICO,  # alternativa sem acento
                "intermediário": CategoriaVeiculo.INTERMEDIARIO,
                "intermediario": CategoriaVeiculo.INTERMEDIARIO,  # alternativa sem acento
                "luxo": CategoriaVeiculo.LUXO,
                "suv": CategoriaVeiculo.SUV
            }
            if categoria.lower() in categoria_map:
                query = query.filter(Veiculo.categoria == categoria_map[categoria.lower()])
            else:
                # Retorna lista vazia se categoria não existe
                return []
        
        # Mapear status string para Enum
        if status:
            status_map = {
                "disponível": StatusVeiculo.DISPONIVEL,
                "disponivel": StatusVeiculo.DISPONIVEL,  # alternativa sem acento
                "locado": StatusVeiculo.LOCADO,
                "manutenção": StatusVeiculo.MANUTENCAO,
                "manutencao": StatusVeiculo.MANUTENCAO  # alternativa sem acento
            }
            if status.lower() in status_map:
                query = query.filter(Veiculo.status == status_map[status.lower()])
            else:
                # Retorna lista vazia se status não existe
                return []
        
        veiculos = query.all()
        return veiculos
        
    except Exception as e:
        print(f"Erro ao buscar veículos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/{veiculo_id}", response_model=VeiculoResponse)
def obter_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo

# ENDPOINT PUT PARA ATUALIZAR VEÍCULO (APENAS ADMIN)
@router.put("/{veiculo_id}", response_model=VeiculoResponse)
def atualizar_veiculo(
    veiculo_id: int,
    veiculo: VeiculoCreate,
    db: Session = Depends(get_db),
    usuario_admin: Usuario = Depends(get_current_admin_user)  # ⭐ Só admin pode atualizar
):
    db_veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not db_veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    # Verificar se a nova placa já existe (se foi alterada)
    if veiculo.placa != db_veiculo.placa:
        placa_existente = db.query(Veiculo).filter(Veiculo.placa == veiculo.placa).first()
        if placa_existente:
            raise HTTPException(status_code=400, detail="Placa já cadastrada")
    
    for key, value in veiculo.dict().items():
        setattr(db_veiculo, key, value)
    
    db.commit()
    db.refresh(db_veiculo)
    
    return db_veiculo

#  ENDPOINT DELETE PARA EXCLUIR VEÍCULO (APENAS ADMIN)
@router.delete("/{veiculo_id}")
def deletar_veiculo(
    veiculo_id: int,
    db: Session = Depends(get_db),
    usuario_admin: Usuario = Depends(get_current_admin_user)  # ⭐ Só admin pode excluir
):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    db.delete(veiculo)
    db.commit()
    
    return {"message": "Veículo deletado com sucesso"}