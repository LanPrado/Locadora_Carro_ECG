from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from database.database import get_db
from backend.app.models.models import Locacao, Veiculo, Cliente, StatusLocacao, StatusVeiculo
from backend.app.schemas.user import LocacaoResponse, ReservaRequest, MudarStatusRequest
from auth import verificar_token

router = APIRouter()

@router.post("/reservar", response_model=LocacaoResponse)
def reservar_veiculo(
    reserva: ReservaRequest,
    db: Session = Depends(get_db),
    user_info: dict = Depends(verificar_token)
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

@router.get("/", response_model=List[LocacaoResponse])
def listar_locacoes(
    status: StatusLocacao = None,
    db: Session = Depends(get_db),
    user_info: dict = Depends(verificar_token)
):
    if user_info["tipo"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem ver todas locações")
    
    query = db.query(Locacao)
    
    if status:
        query = query.filter(Locacao.status == status)
    
    return query.all()

@router.get("/minhas-locacoes", response_model=List[LocacaoResponse])
def minhas_locacoes(
    db: Session = Depends(get_db),
    user_info: dict = Depends(verificar_token)
):
    locacoes = db.query(Locacao).join(Cliente).filter(Cliente.email == user_info["email"]).all()
    return locacoes

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