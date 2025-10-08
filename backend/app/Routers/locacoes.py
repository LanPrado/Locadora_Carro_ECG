from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import Locacao, Veiculo, Cliente, StatusLocacao, StatusVeiculo
from ..schemas import LocacaoCreate, LocacaoResponse, CheckinRequest, CheckoutRequest
from ..auth import verificar_token

router = APIRouter()

@router.post("/", response_model=LocacaoResponse)
def criar_locacao(
    locacao: LocacaoCreate,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    cliente = db.query(Cliente).filter(Cliente.id == locacao.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    veiculo = db.query(Veiculo).filter(Veiculo.id == locacao.veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    if veiculo.status != StatusVeiculo.DISPONIVEL:
        raise HTTPException(status_code=400, detail="Veículo não disponível")
    
    locacoes_conflitantes = db.query(Locacao).filter(
        Locacao.veiculo_id == locacao.veiculo_id,
        Locacao.status.in_([StatusLocacao.RESERVADA, StatusLocacao.ATIVA]),
        Locacao.data_inicio <= locacao.data_fim,
        Locacao.data_fim >= locacao.data_inicio
    ).first()
    
    if locacoes_conflitantes:
        raise HTTPException(status_code=400, detail="Veículo já reservado neste período")
    
    dias_locacao = (locacao.data_fim - locacao.data_inicio).days
    valor_total = dias_locacao * veiculo.diaria
    
    if dias_locacao >= 7:
        valor_total *= 0.9
    elif dias_locacao >= 3:
        valor_total *= 0.95
    
    nova_locacao = Locacao(
        **locacao.dict(),
        valor_total=valor_total,
        quilometragem_inicial=veiculo.quilometragem
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
    usuario_email: str = Depends(verificar_token)
):
    query = db.query(Locacao)
    
    if status:
        query = query.filter(Locacao.status == status)
    
    return query.all()

@router.post("/{locacao_id}/checkin")
def realizar_checkin(
    locacao_id: int,
    checkin: CheckinRequest,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    locacao = db.query(Locacao).filter(Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(status_code=404, detail="Locação não encontrada")
    
    if locacao.status != StatusLocacao.RESERVADA:
        raise HTTPException(status_code=400, detail="Locação não está reservada")
    
    locacao.veiculo.quilometragem = checkin.quilometragem_atual
    locacao.quilometragem_inicial = checkin.quilometragem_atual
    locacao.status = StatusLocacao.ATIVA
    
    db.commit()
    
    return {"message": "Check-in realizado com sucesso"}

@router.post("/{locacao_id}/checkout")
def realizar_checkout(
    locacao_id: int,
    checkout: CheckoutRequest,
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    locacao = db.query(Locacao).filter(Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(status_code=404, detail="Locação não encontrada")
    
    if locacao.status != StatusLocacao.ATIVA:
        raise HTTPException(status_code=400, detail="Locação não está ativa")
    
    locacao.data_devolucao = datetime.utcnow()
    locacao.quilometragem_final = checkout.quilometragem_final
    locacao.veiculo.quilometragem = checkout.quilometragem_final
    locacao.veiculo.status = StatusVeiculo.DISPONIVEL
    locacao.status = StatusLocacao.FINALIZADA
    
    km_rodados = checkout.quilometragem_final - locacao.quilometragem_inicial
    if km_rodados > 100:
        km_excedente = km_rodados - 100
        locacao.valor_total += km_excedente * 0.5
    
    db.commit()
    
    return {"message": "Check-out realizado com sucesso", "valor_final": locacao.valor_total}