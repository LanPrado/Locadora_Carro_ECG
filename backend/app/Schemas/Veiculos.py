from pydantic import BaseModel
from typing import Optional
from ..models.Veiculos import CategoriaVeiculo, StatusVeiculo

# Schema para criar/atualizar um veículo
class VeiculoCreate(BaseModel):
    placa: str
    modelo: str
    marca: str
    ano: int
    categoria: CategoriaVeiculo
    diaria: float
    quilometragem: Optional[int] = 0
    descricao: Optional[str] = None
    imagem_url: Optional[str] = None
    status: Optional[StatusVeiculo] = StatusVeiculo.DISPONIVEL

    class Config:
        from_attributes = True

# Schema de resposta para um veículo
class VeiculoResponse(BaseModel):
    id: str
    placa: str
    modelo: str
    marca: str
    ano: int
    categoria: CategoriaVeiculo
    diaria: float
    status: StatusVeiculo
    descricao: Optional[str] = None
    
    class Config:
        from_attributes = True