from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db  
from app.models.Veiculos import Veiculo, StatusVeiculo, StatusLocacao             
from app.models.Cliente import Cliente              
from app.models.Reservar import Reserva
from app.models.Adm import Admin  
from app.Schemas.Dashboard import DashboardStats  
from app.utils.dependencies import get_current_admin_user 

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
            faturamento_mensal=float(faturamento_mensal),  # ADICIONADO
            faturamento_total=float(faturamento_total)     # ADICIONADO
        )
        
    except Exception as e:
        # Logar o erro real no seu console
        print(f"Erro no Dashboard: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro ao obter estatísticas do dashboard."
        )