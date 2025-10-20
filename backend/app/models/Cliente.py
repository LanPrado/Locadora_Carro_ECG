from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Schema para Admins criarem clientes
class ClienteCreate(BaseModel):
    cli_email: EmailStr
    cli_nome: str
    cli_senha_hash: str 

    class Config:
        from_attributes = True 


# Schema para a API responder com dados do cliente
class ClienteResponse(BaseModel):
    cli_id: str
    cli_email: EmailStr
    cli_nome: str
    cli_ativo: bool
    cli_criado_em: datetime

    class Config:
        from_attributes = True