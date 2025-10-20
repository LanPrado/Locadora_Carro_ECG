from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Schema para Admins criarem clientes (usado em routers/clientes.py)
class ClienteCreate(BaseModel):
    cli_email: EmailStr
    cli_nome: str
    cli_senha_hash: str # Admin define o hash
    cli_telefone: Optional[str] = None
    cli_cpf: Optional[str] = None

    class Config:
        from_attributes = True 

class ClienteResponse(BaseModel):
    cli_id: str
    cli_email: EmailStr
    cli_nome: str
    cli_telefone: Optional[str] = None
    cli_cpf: Optional[str] = None
    cli_ativo: bool
    cli_criado_em: datetime

    class Config:
        from_attributes = True