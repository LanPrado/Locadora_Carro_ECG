from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.models import Veiculo
from ..models.Cliente import Cliente, ClienteResponse, ClienteCreate
from ..models.Veiculos import StatusLocacao, StatusVeiculo
from ..models.Reservar import Reserva
from ..models.Adm import Admin
from ..Schemas.Reservar import LocacaoResponse, ReservaRequest, MudarStatusRequest
from ..utils.dependencies import get_current_cliente_user, get_current_admin_user

router = APIRouter()

@router.post("/", 
    response_model=LocacaoResponse,
    summary="Reservar veículo (Cliente)",
    description="Realiza a reserva de um veículo para o cliente autenticado."
)
def reservar_veiculo(
    reserva: ReservaRequest,
    db: Session = Depends(get_db),
    current_user: Cliente = Depends(get_current_cliente_user)
):
    veiculo = db.query(Veiculo).filter(Veiculo.id == reserva.veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    if veiculo.status != StatusVeiculo.DISPONIVEL:
        raise HTTPException(status_code=400, detail="Veículo não disponível para reserva")
    
    locacoes_conflitantes = db.query(Reserva).filter(
        Reserva.res_vei_id == reserva.veiculo_id,
        Reserva.res_status.in_([StatusLocacao.RESERVADA, StatusLocacao.ATIVA]),
        Reserva.res_data_inicio <= reserva.data_fim,
        Reserva.res_data_fim >= reserva.data_inicio
    ).first()
    
    if locacoes_conflitantes:
        raise HTTPException(status_code=400, detail="Veículo já reservado neste período")
    
    dias_locacao = (reserva.data_fim - reserva.data_inicio).days
    if dias_locacao <= 0:
        raise HTTPException(status_code=400, detail="Período de locação inválido")
    
    valor_total = dias_locacao * veiculo.diaria
    
    nova_reserva = Reserva(
        res_cli_id=current_user.cli_id,
        res_vei_id=reserva.veiculo_id,
        res_data_inicio=reserva.data_inicio,
        res_data_fim=reserva.data_fim,
        res_total=valor_total,
        res_status=StatusLocacao.RESERVADA
    )
    
    veiculo.status = StatusVeiculo.LOCADO
    
    db.add(nova_reserva)
    db.commit()
    db.refresh(nova_reserva)
    
    return nova_reserva

@router.get("/minhas-reservas", 
    response_model=List[LocacaoResponse],
    summary="Minhas reservas (Cliente)",
    description="Retorna as reservas do cliente autenticado."
)
def minhas_locacoes(
    db: Session = Depends(get_db),
    current_user: Cliente = Depends(get_current_cliente_user)
):
    reservas = (
        db.query(Reserva)
        .filter(Reserva.res_cli_id == current_user.cli_id)
        .order_by(Reserva.res_data_inicio.desc())
        .all()
    )
    return reservas

@router.patch("/{reserva_id}/status",
    response_model=LocacaoResponse,
    summary="Alterar status da reserva/locação (Admin)",
    description="Altera o status de uma reserva (check-in, devolução/check-out, cancelar)."
)
def alterar_status_locacao(
    reserva_id: str,
    status_request: MudarStatusRequest,
    db: Session = Depends(get_db),
    admin_user: Admin = Depends(get_current_admin_user)
):
    reserva = db.query(Reserva).filter(Reserva.res_id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva/Locação não encontrada")
    
    veiculo = db.query(Veiculo).filter(Veiculo.id == reserva.res_vei_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo associado não encontrado")
    
    novo_status = status_request.status
    reserva.res_status = novo_status
    
    if novo_status == StatusLocacao.ATIVA:
        veiculo.status = StatusVeiculo.LOCADO
    elif novo_status in [StatusLocacao.FINALIZADA, StatusLocacao.CANCELADA]:
        veiculo.status = StatusVeiculo.DISPONIVEL
        if novo_status == StatusLocacao.FINALIZADA:
            reserva.data_devolucao = datetime.utcnow()
            # Opcional: Lógica de multa pode ser adicionada aqui

    db.commit()
    db.refresh(reserva)
    
    return reserva
