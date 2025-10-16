from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models.models import Locacao, Veiculo, Cliente, StatusLocacao, StatusVeiculo
from ..schemas.user import LocacaoResponse, ReservaRequest, MudarStatusRequest
from .auth import get_current_user, get_current_admin_user

router = APIRouter()

@router.post("/reservar", 
    response_model=LocacaoResponse,
    summary="Reservar veículo",
    description="Realiza a reserva de um veículo. Cliente pode ser existente ou novo."
)
def reservar_veiculo(
    reserva: ReservaRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Verificar se veículo existe
    veiculo = db.query(Veiculo).filter(Veiculo.id == reserva.veiculo_id).first()
    if veiculo is None:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    # CORREÇÃO: Acessar o valor do status corretamente
    veiculo_status = veiculo.status
    if veiculo_status is None:
        veiculo_status_str = ""
    else:
        veiculo_status_str = str(veiculo_status.value)
    
    if veiculo_status_str != StatusVeiculo.DISPONIVEL.value:
        raise HTTPException(status_code=400, detail="Veículo não disponível para reserva")
    
    # Verifica se há conflito de datas
    locacoes_conflitantes = db.query(Locacao).filter(
        Locacao.veiculo_id == reserva.veiculo_id,
        Locacao.status.in_([StatusLocacao.RESERVADA.value, StatusLocacao.ATIVA.value]),
        Locacao.data_inicio <= reserva.data_fim,
        Locacao.data_fim >= reserva.data_inicio
    ).first()
    
    if locacoes_conflitantes is not None:
        raise HTTPException(status_code=400, detail="Veículo já reservado neste período")
    
    # Verifica se o cliente já existe
    cliente = db.query(Cliente).filter(Cliente.cpf == reserva.cpf).first()
    if cliente is None:
        # Criar novo cliente
        cliente = Cliente(
            cpf=reserva.cpf,
            nome=reserva.nome,
            email=reserva.email,
            telefone=reserva.telefone,
            cnh=reserva.cnh,
            endereco=reserva.endereco
        )
        db.add(cliente)
        db.flush()
    
    # Calcula valor total da locação
    dias_locacao = (reserva.data_fim - reserva.data_inicio).days
    if dias_locacao <= 0:
        raise HTTPException(status_code=400, detail="Período de locação inválido")
    
    valor_total = dias_locacao * veiculo.diaria
    
    # Aplicar descontos para períodos mais longos
    if dias_locacao >= 7:
        valor_total *= 0.9  # 10% de desconto
    elif dias_locacao >= 3:
        valor_total *= 0.95  # 5% de desconto
    
    # Criar nova locação
    nova_locacao = Locacao(
        cliente_id=cliente.id,
        veiculo_id=reserva.veiculo_id,
        data_inicio=reserva.data_inicio,
        data_fim=reserva.data_fim,
        quilometragem_inicial=veiculo.quilometragem,
        valor_total=valor_total,
        status=StatusLocacao.RESERVADA
    )
    
    # CORREÇÃO: Atualizar status do veículo usando setattr
    setattr(veiculo, 'status', StatusVeiculo.LOCADO)
    
    db.add(nova_locacao)
    db.commit()
    db.refresh(nova_locacao)
    
    return nova_locacao

@router.get("/", 
    response_model=List[LocacaoResponse],
    summary="Listar locações",
    description="Retorna todas as locações do sistema. Requer autenticação como administrador."
)
def listar_locacoes(
    status: Optional[StatusLocacao] = None,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    query = db.query(Locacao)
    
    if status:
        query = query.filter(Locacao.status == status)
    
    return query.order_by(Locacao.data_inicio.desc()).all()

@router.get("/minhas-locacoes", 
    response_model=List[LocacaoResponse],
    summary="Minhas locações",
    description="Retorna as locações do usuário autenticado."
)
def minhas_locacoes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Buscar locações pelo email do usuário autenticado
    locacoes = (
        db.query(Locacao)
        .join(Cliente)
        .filter(Cliente.email == current_user.email)
        .order_by(Locacao.data_inicio.desc())
        .all()
    )
    return locacoes

@router.patch("/{locacao_id}/status",
    response_model=LocacaoResponse,
    summary="Alterar status da locação",
    description="Altera o status de uma locação. Requer autenticação como administrador."
)
def alterar_status_locacao(
    locacao_id: int,
    status_request: MudarStatusRequest,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    locacao = db.query(Locacao).filter(Locacao.id == locacao_id).first()
    if locacao is None:
        raise HTTPException(status_code=404, detail="Locação não encontrada")
    
    veiculo = db.query(Veiculo).filter(Veiculo.id == locacao.veiculo_id).first()
    if veiculo is None:
        raise HTTPException(status_code=404, detail="Veículo associado não encontrado")
    
    # CORREÇÃO: Atualizar usando setattr
    setattr(locacao, 'status', status_request.status)
    
    # CORREÇÃO: Atualizar status do veículo baseado no status da locação usando setattr
    if status_request.status == StatusLocacao.ATIVA:
        setattr(veiculo, 'status', StatusVeiculo.LOCADO)
    elif status_request.status in [StatusLocacao.FINALIZADA, StatusLocacao.CANCELADA]:
        setattr(veiculo, 'status', StatusVeiculo.DISPONIVEL)
    
    db.commit()
    db.refresh(locacao)
    
    return locacao

@router.post("/{locacao_id}/checkin",
    response_model=LocacaoResponse,
    summary="Realizar check-in",
    description="Registra o check-in de uma locação. Requer autenticação como administrador."
)
def realizar_checkin(
    locacao_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    locacao = db.query(Locacao).filter(Locacao.id == locacao_id).first()
    if locacao is None:
        raise HTTPException(status_code=404, detail="Locação não encontrada")
    
    # CORREÇÃO: Acessar o valor do status corretamente
    locacao_status = locacao.status
    if locacao_status is None:
        locacao_status_str = ""
    else:
        locacao_status_str = str(locacao_status.value)
    
    if locacao_status_str != StatusLocacao.RESERVADA.value:
        raise HTTPException(status_code=400, detail="Check-in só pode ser realizado para locações reservadas")
    
    # CORREÇÃO: Atualizar usando setattr
    setattr(locacao, 'status', StatusLocacao.ATIVA)
    
    # CORREÇÃO: Atualizar status do veículo usando setattr
    veiculo = db.query(Veiculo).filter(Veiculo.id == locacao.veiculo_id).first()
    if veiculo:
        setattr(veiculo, 'status', StatusVeiculo.LOCADO)
    
    db.commit()
    db.refresh(locacao)
    
    return locacao

@router.post("/{locacao_id}/checkout",
    response_model=LocacaoResponse,
    summary="Realizar check-out",
    description="Registra o check-out de uma locação. Requer autenticação como administrador."
)
def realizar_checkout(
    locacao_id: int,
    quilometragem_final: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    locacao = db.query(Locacao).filter(Locacao.id == locacao_id).first()
    if locacao is None:
        raise HTTPException(status_code=404, detail="Locação não encontrada")
    
    # CORREÇÃO: Acessar o valor do status corretamente
    locacao_status = locacao.status
    if locacao_status is None:
        locacao_status_str = ""
    else:
        locacao_status_str = str(locacao_status.value)
    
    if locacao_status_str != StatusLocacao.ATIVA.value:
        raise HTTPException(status_code=400, detail="Check-out só pode ser realizado para locações ativas")
    
    # CORREÇÃO DEFINITIVA: Usar uma função auxiliar para verificar
    def _is_valid_quilometragem(loc: Locacao, km_final: int) -> bool:
        km_inicial = getattr(loc, 'quilometragem_inicial', None)
        if km_inicial is None:
            return False
        return km_final >= km_inicial
    
    def _has_atraso(loc: Locacao, data_devol: datetime) -> bool:
        data_fim = getattr(loc, 'data_fim', None)
        if isinstance(data_fim, datetime) and isinstance(data_devol, datetime):
            return data_devol > data_fim
        return False
    
    # Verificar quilometragem
    if not _is_valid_quilometragem(locacao, quilometragem_final):
        raise HTTPException(status_code=400, detail="Quilometragem final não pode ser menor que a inicial")
    
    data_devolucao = datetime.utcnow()
    multa = 0.0

    # Verificar atraso
    if _has_atraso(locacao, data_devolucao):
        dias_atraso = (data_devolucao - locacao.data_fim).days
        if dias_atraso > 0:
            dias_locacao = (locacao.data_fim - locacao.data_inicio).days
            if dias_locacao > 0:
                multa = dias_atraso * (locacao.valor_total / dias_locacao) * 0.5
    
    valor_total_final = locacao.valor_total + multa
    
    # CORREÇÃO: Atualizar usando setattr
    setattr(locacao, 'status', StatusLocacao.FINALIZADA)
    setattr(locacao, 'data_devolucao', data_devolucao)
    setattr(locacao, 'quilometragem_final', quilometragem_final)
    setattr(locacao, 'valor_total', valor_total_final)
    
    # CORREÇÃO: Atualizar status e quilometragem do veículo usando setattr
    veiculo = db.query(Veiculo).filter(Veiculo.id == locacao.veiculo_id).first()
    if veiculo:
        setattr(veiculo, 'status', StatusVeiculo.DISPONIVEL)
        setattr(veiculo, 'quilometragem', quilometragem_final)
    
    db.commit()
    db.refresh(locacao)
    
    return locacao

def calcular_multa_atraso(data_fim_previsto: datetime, data_devolucao: datetime, diaria: float) -> float:
    """
    Calcula multa por atraso na devolução do veículo.
    """
    if data_devolucao <= data_fim_previsto:
        return 0.0
    
    diferenca = data_devolucao - data_fim_previsto
    horas_atraso = diferenca.total_seconds() / 3600
    
    if horas_atraso <= 24:
        multa = (horas_atraso // 1 + (1 if horas_atraso % 1 > 0 else 0)) * 10.0
    else:
        multa = 240.0 + diaria
    
    return multa