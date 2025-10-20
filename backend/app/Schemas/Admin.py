from pydantic import BaseModel, Field
from typing import Optional

# Schema para registro de admin
class AdminCreate(BaseModel):
    codigo_admin: str = Field(..., regex=r'^ADM\d{6}$')  # Formato: ADM + 6 dígitos
    adm_nome: str
    senha: str
    nivel_acesso: Optional[str] = "operador"  # operador, supervisor, super

    class Config:
        from_attributes = True

# Schema para resposta
class AdminResponse(BaseModel):
    adm_id: str
    codigo_admin: str
    adm_nome: str
    nivel_acesso: str
    ativo: bool

    class Config:
        from_attributes = True