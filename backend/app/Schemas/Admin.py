from pydantic import BaseModel, Field
from typing import Optional

# Schema para registro de admin
class AdminCreate(BaseModel):
    codigo_admin: str = Field(..., pattern=r'^ADM\d{6}$') 
    adm_nome: str
    senha: str
    nivel_acesso: Optional[str] = "operador"  

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