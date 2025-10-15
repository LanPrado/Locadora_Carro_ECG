from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..database import get_db
from ..models.models import Veiculo, Cliente, Locacao, StatusVeiculo, StatusLocacao
from ..schemas.user import DashboardStats
from .auth import get_current_admin_user

router = APIRouter()

@router.get("/stats", 
    response_model=DashboardStats,
    summary="Estatísticas do Dashboard",
    description="""
    Retorna as estatísticas completas do sistema para o dashboard administrativo.
    
    Inclui:
    - Total de veículos e status (disponíveis, em manutenção, locados)
    - Clientes ativos
    - Locações ativas
    - Faturamento mensal e total
    """
)
def obter_estatisticas(
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    """
    Obtém estatísticas completas do sistema para o dashboard administrativo.
    Requer autenticação como administrador.
    """
    try:
        # Estatísticas de Veículos
        total_veiculos = db.query(Veiculo).count()
        
        veiculos_disponiveis = db.query(Veiculo).filter(
            Veiculo.status == StatusVeiculo.DISPONIVEL
        ).count()
        
        veiculos_manutencao = db.query(Veiculo).filter(
            Veiculo.status == StatusVeiculo.MANUTENCAO
        ).count()
        
        veiculos_locados = db.query(Veiculo).filter(
            Veiculo.status == StatusVeiculo.LOCADO
        ).count()
        
        # Estatísticas de Clientes
        total_clientes = db.query(Cliente).filter(Cliente.ativo == True).count()
        
        # Estatísticas de Locações
        locacoes_ativas = db.query(Locacao).filter(
            Locacao.status == StatusLocacao.ATIVA
        ).count()
        
        # Faturamento Mensal
        inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        faturamento_mensal = db.query(func.sum(Locacao.valor_total)).filter(
            Locacao.status == StatusLocacao.FINALIZADA,
            Locacao.data_devolucao >= inicio_mes
        ).scalar() or 0.0
        
        # Faturamento Total (CORREÇÃO: adicionar este campo)
        faturamento_total = db.query(func.sum(Locacao.valor_total)).filter(
            Locacao.status == StatusLocacao.FINALIZADA
        ).scalar() or 0.0
        
        return DashboardStats(
            total_veiculos=total_veiculos,
            veiculos_disponiveis=veiculos_disponiveis,
            veiculos_manutencao=veiculos_manutencao,
            veiculos_locados=veiculos_locados,
            total_clientes=total_clientes,
            locacoes_ativas=locacoes_ativas,
            faturamento_mensal=float(faturamento_mensal),
            faturamento_total=float(faturamento_total)  # ← CORREÇÃO: Adicionar este campo
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao obter estatísticas do dashboard: {str(e)}"
        )