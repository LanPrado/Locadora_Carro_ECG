from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from ..models.Veiculos import StatusLocacao

# Schema para fazer um pedido de reserva
class ReservaRequest(BaseModel):
    veiculo_id: str
    data_inicio: datetime
    data_fim: datetime
    
    class Config:
        from_attributes = True

# Schema de resposta para uma locação/reserva
class LocacaoResponse(BaseModel):
    res_id: str
    res_vei_id: str
    res_cli_id: str
    res_data_inicio: datetime
    res_data_fim: datetime
    res_status: StatusLocacao
    res_total: Optional[float] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True

# Schema para mudar o status de uma locação (suficiente para devolução)
class MudarStatusRequest(BaseModel):
    status: StatusLocacao
    class Config:
        use_enum_values = True
