from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Veiculo, Cliente, Locacao, StatusVeiculo, StatusLocacao
from ..schemas import DashboardStats
from ..auth import verificar_token

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def obter_estatisticas(
    db: Session = Depends(get_db),
    usuario_email: str = Depends(verificar_token)
):
    total_veiculos = db.query(Veiculo).count()
    
    veiculos_disponiveis = db.query(Veiculo).filter(
        Veiculo.status == StatusVeiculo.DISPONIVEL
    ).count()
    
    total_clientes = db.query(Cliente).filter(Cliente.ativo == True).count()
    
    locacoes_ativas = db.query(Locacao).filter(
        Locacao.status == StatusLocacao.ATIVA
    ).count()
    
    inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    faturamento_mensal = db.query(func.sum(Locacao.valor_total)).filter(
        Locacao.status == StatusLocacao.FINALIZADA,
        Locacao.data_devolucao >= inicio_mes
    ).scalar() or 0.0
    
    return DashboardStats(
        total_veiculos=total_veiculos,
        veiculos_disponiveis=veiculos_disponiveis,
        total_clientes=total_clientes,
        locacoes_ativas=locacoes_ativas,
        faturamento_mensal=float(faturamento_mensal)
    )