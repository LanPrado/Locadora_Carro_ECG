from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..database import get_db
# --- CORREÇÃO DE IMPORTS ---
from ..models.models import Veiculo                
from ..models.Cliente import ClienteResponse               
from ..models.Reservar import Reserva # O Modelo Correto
from ..models.Veiculos import StatusVeiculo, StatusLocacao 
from ..models.Adm import Admin # Para type hint
from ..Schemas.Dashboard import DashboardStats # O Schema Correto
from ..utils.dependencies import get_current_admin_user # A dependência Correta
# ---------------------------

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/stats", 
    response_model=DashboardStats,
    summary="Estatísticas do Dashboard (Admin)",
    description="Retorna as estatísticas do sistema. Requer Admin."
)
def obter_estatisticas(
    db: Session = Depends(get_db),
    admin_user: Admin = Depends(get_current_admin_user) # Protegido
):
    try:
        # Estatísticas de Veículos (nomes de coluna corretos)
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
        
        # Clientes
        total_clientes = db.query(Cliente).filter(Cliente.cli_ativo == True).count()
        
        # "Usuários ativos" (Locações ativas)
        locacoes_ativas = db.query(Reserva).filter(
            Reserva.res_status == StatusLocacao.ATIVA
        ).count()
        
        # Faturamento
        inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        faturamento_mensal = db.query(func.sum(Reserva.res_total)).filter(
            Reserva.res_status == StatusLocacao.FINALIZADA,
            Reserva.res_data_fim >= inicio_mes 
        ).scalar() or 0.0
        
        faturamento_total = db.query(func.sum(Reserva.res_total)).filter(
            Reserva.res_status == StatusLocacao.FINALIZADA
        ).scalar() or 0.0
        
        return DashboardStats(
            total_veiculos=total_veiculos,
            veiculos_disponiveis=veiculos_disponiveis,
            veiculos_manutencao=veiculos_manutencao,
            veiculos_locados=veiculos_locados,
            total_clientes=total_clientes,
            locacoes_ativas=locacoes_ativas,

        )
        
    except Exception as e:
        # Logar o erro real no seu console
        print(f"Erro no Dashboard: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao obter estatísticas do dashboard."
        )