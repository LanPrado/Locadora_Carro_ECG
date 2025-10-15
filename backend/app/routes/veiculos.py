from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.models import Veiculo, StatusVeiculo, CategoriaVeiculo
from ..schemas.user import VeiculoCreate, VeiculoResponse
from enum import Enum

# IMPORTE as funções de autenticação
from ..routes.auth import get_current_admin_user
from ..models.user import Usuario

router = APIRouter()

# Criar Enums para os parâmetros (usando os MESMOS valores do modelo)
class CategoriaFilter(str, Enum):
    ECONOMICO = "econômico"
    INTERMEDIARIO = "intermediário"
    LUXO = "luxo"
    SUV = "suv"

class StatusFilter(str, Enum):
    DISPONIVEL = "disponível"
    LOCADO = "locado"
    MANUTENCAO = "manutenção"

# ENDPOINT POST PARA CRIAR VEÍCULO (APENAS ADMIN)
@router.post("/", response_model=VeiculoResponse)
def criar_veiculo(
    veiculo: VeiculoCreate, 
    db: Session = Depends(get_db),
    usuario_admin: Usuario = Depends(get_current_admin_user)
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
    categoria: Optional[CategoriaFilter] = None,
    status: Optional[StatusFilter] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Veiculo)
        
        print(f"🔍 Filtros recebidos - categoria: {categoria}, status: {status}")
        
        # Filtro por categoria
        if categoria is not None:
            query = query.filter(Veiculo.categoria == categoria.value)  # type: ignore
            print(f"✅ Aplicando filtro de categoria: {categoria.value}")
        
        # Filtro por status
        if status is not None:
            query = query.filter(Veiculo.status == status.value)  # type: ignore
            print(f"✅ Aplicando filtro de status: {status.value}")
        
        veiculos = query.all()
        print(f"📊 Retornando {len(veiculos)} veículos")
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
    usuario_admin: Usuario = Depends(get_current_admin_user)
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

# ENDPOINT PATCH PARA ALTERAR APENAS O STATUS (MAIS SIMPLES)
@router.patch("/{veiculo_id}/status", response_model=VeiculoResponse)
def alterar_status_veiculo(
    veiculo_id: int,
    status: StatusFilter,
    db: Session = Depends(get_db),
    usuario_admin: Usuario = Depends(get_current_admin_user)
):
    db_veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not db_veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    # Mapeamento direto para strings
    status_map = {
        StatusFilter.DISPONIVEL: "disponível",
        StatusFilter.LOCADO: "locado",
        StatusFilter.MANUTENCAO: "manutenção"
    }
    
    # Ignorar warning do Pylance - isso funciona no SQLAlchemy
    db_veiculo.status = status_map[status]  # type: ignore
    db.commit()
    db.refresh(db_veiculo)
    
    return db_veiculo

# ENDPOINT PARA VERIFICAR TODOS OS VEÍCULOS (DEBUG)
@router.get("/debug/todos")
def listar_todos_veiculos(db: Session = Depends(get_db)):
    """Endpoint para debug - lista todos os veículos sem filtro"""
    veiculos = db.query(Veiculo).all()
    result = []
    for v in veiculos:
        result.append({
            "id": v.id,
            "placa": v.placa,
            "modelo": v.modelo,
            "marca": v.marca,
            "categoria": v.categoria.value if v.categoria else None, # type: ignore
            "status": v.status.value if v.status else None, # type: ignore
            "ano": v.ano,
            "diaria": v.diaria
        })
    return result

# ENDPOINT PARA ATUALIZAR STATUS EM MASSA
@router.post("/atualizar-status-em-massa")
def atualizar_status_em_massa(
    novo_status: StatusFilter,
    db: Session = Depends(get_db),
    usuario_admin: Usuario = Depends(get_current_admin_user)
):
    """Atualiza o status de TODOS os veículos para o status especificado"""
    # Mapeamento direto para strings
    status_map = {
        StatusFilter.DISPONIVEL: "disponível",
        StatusFilter.LOCADO: "locado", 
        StatusFilter.MANUTENCAO: "manutenção"
    }
    
    veiculos = db.query(Veiculo).all()
    status_value = status_map[novo_status]
    
    for veiculo in veiculos:
        # Ignorar warning do Pylance - isso funciona no SQLAlchemy
        veiculo.status = status_value  # type: ignore
    
    db.commit()
    
    return {"message": f"Status de {len(veiculos)} veículos atualizado para {novo_status.value}"}

# ENDPOINT DELETE PARA EXCLUIR VEÍCULO (APENAS ADMIN)
@router.delete("/{veiculo_id}")
def deletar_veiculo(
    veiculo_id: int,
    db: Session = Depends(get_db),
    usuario_admin: Usuario = Depends(get_current_admin_user)
):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    db.delete(veiculo)
    db.commit()
    
    return {"message": "Veículo deletado com sucesso"}