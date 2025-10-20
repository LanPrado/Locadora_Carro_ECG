from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Schema para auto-registo de cliente (sem prefixos)
class UsuarioCreate(BaseModel):
    email: EmailStr
    nome: str
    senha: str # Senha pura, o serviço fará o hash

    class Config:
        from_attributes = True

# Schema de resposta para auto-registo
class UsuarioResponse(BaseModel):
    cli_id: str
    cli_email: EmailStr
    cli_nome: str
    cli_ativo: bool
    cli_criado_em: datetime

    class Config:
        from_attributes = True