from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..database import get_db

from ..models.models import Veiculo                
from ..models.Cliente import Cliente               
from ..models.Reservar import Reserva               
from ..models.Veiculos import StatusVeiculo, StatusLocacao 

from .Cliente import DashboardStats
from .autenticacao import get_current_admin_user

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
            Veiculo.Vei_status == StatusVeiculo.DISPONIVEL # CORREÇÃO: Vei_status (como em models.py)
        ).count()
        
        veiculos_manutencao = db.query(Veiculo).filter(
            Veiculo.Vei_status == StatusVeiculo.MANUTENCAO # CORREÇÃO: Vei_status
        ).count()
        
        veiculos_locados = db.query(Veiculo).filter(
            Veiculo.Vei_status == StatusVeiculo.LOCADO # CORREÇÃO: Vei_status
        ).count()
        
        total_clientes = db.query(Cliente).filter(Cliente.cli_ativo == True).count() # CORREÇÃO: cli_ativo
        
        locacoes_ativas = db.query(Reserva).filter(
            Reserva.res_status == StatusLocacao.ATIVA # Usando os campos de Reservar.py
        ).count()
        
        return DashboardStats(
            total_veiculos=total_veiculos,
            veiculos_disponiveis=veiculos_disponiveis,
            veiculos_manutencao=veiculos_manutencao,
            veiculos_locados=veiculos_locados,
            total_clientes=total_clientes,
            locacoes_ativas=locacoes_ativas,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao obter estatísticas do dashboard: {str(e)}"
        )
}