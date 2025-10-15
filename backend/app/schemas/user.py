from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from ..models.models import CategoriaVeiculo, StatusVeiculo, StatusLocacao

# Esquemas de Autenticação
class UsuarioCreate(BaseModel):
    email: EmailStr
    nome: str
    senha: str

class UsuarioResponse(BaseModel):
    id: str
    email: str
    nome: str
    ativo: bool
    role: str
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str = Field(..., description="Email ou ID do usuário")  # ← Adicione description
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str
# Esquemas de Veículos
class VeiculoCreate(BaseModel):
    placa: str
    modelo: str
    marca: str
    ano: int
    categoria: CategoriaVeiculo
    diaria: float
    quilometragem: int = 0
    imagem_url: Optional[str] = None
    descricao: Optional[str] = None

class VeiculoResponse(BaseModel):
    id: int
    placa: str
    modelo: str
    marca: str
    ano: int
    categoria: CategoriaVeiculo
    diaria: float
    quilometragem: int
    status: StatusVeiculo
    imagem_url: Optional[str] = None
    descricao: Optional[str] = None
    
    class Config:
        from_attributes = True

# Esquemas de Clientes
class ClienteCreate(BaseModel):
    cpf: str
    nome: str
    email: EmailStr
    telefone: str
    cnh: str
    endereco: str

class ClienteResponse(BaseModel):
    id: int
    cpf: str
    nome: str
    email: str
    telefone: str
    cnh: str
    endereco: str
    ativo: bool
    
    class Config:
        from_attributes = True

# Esquemas de Locações
class LocacaoCreate(BaseModel):
    cliente_id: int
    veiculo_id: int
    data_inicio: datetime
    data_fim: datetime

class LocacaoResponse(BaseModel):
    id: int
    cliente_id: int
    veiculo_id: int
    data_inicio: datetime
    data_fim: datetime
    data_devolucao: Optional[datetime]
    quilometragem_inicial: int
    quilometragem_final: Optional[int]
    valor_total: float
    status: StatusLocacao
    criado_em: datetime
    cliente: ClienteResponse
    veiculo: VeiculoResponse
    
    class Config:
        from_attributes = True

class CheckinRequest(BaseModel):
    quilometragem_atual: int

class CheckoutRequest(BaseModel):
    quilometragem_final: int

# Esquema do Dashboard
class DashboardStats(BaseModel):
    total_veiculos: int
    veiculos_disponiveis: int
    veiculos_manutencao: int
    veiculos_locados: int
    total_clientes: int
    locacoes_ativas: int
    faturamento_mensal: float
    faturamento_total: float
    #locacoes: List[LocacaoResponse]

    class Config:
        from_attributes = True
class ReservaRequest(BaseModel):
    veiculo_id: int
    cpf: str
    nome: str
    email: EmailStr
    telefone: str
    cnh: str
    endereco: str
    data_inicio: datetime
    data_fim: datetime

class MudarStatusRequest(BaseModel):
    status: StatusLocacao