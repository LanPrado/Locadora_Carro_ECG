from pydantic import BaseModel

class DashboardStats(BaseModel):
    total_veiculos: int
    veiculos_disponiveis: int
    veiculos_manutencao: int
    veiculos_locados: int
    total_clientes: int
    locacoes_ativas: int

    class Config:
        from_attributes = True