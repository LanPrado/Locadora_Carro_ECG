from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.Veiculos import CategoriaVeiculo, StatusVeiculo

# Schema para criar um veículo
class VeiculoCreate(BaseModel):
    placa: str
    modelo: str
    marca: str
    ano: int
    cor: str
    categoria: CategoriaVeiculo
    valor_diaria: float  # Mudei de 'diaria' para 'valor_diaria'
    descricao: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True

# Schema para atualizar um veículo
class VeiculoUpdate(BaseModel):
    placa: Optional[str] = None
    modelo: Optional[str] = None
    marca: Optional[str] = None
    ano: Optional[int] = None
    cor: Optional[str] = None
    categoria: Optional[CategoriaVeiculo] = None
    valor_diaria: Optional[float] = None
    status: Optional[StatusVeiculo] = None
    descricao: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True

# Schema de resposta para um veículo
class VeiculoResponse(BaseModel):
    id: str
    placa: str
    modelo: str
    marca: str
    ano: int
    categoria: CategoriaVeiculo
    valor_diaria: float  # Mudei de 'diaria' para 'valor_diaria'
    status: StatusVeiculo
    descricao: Optional[str] = None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True
        use_enum_values = True