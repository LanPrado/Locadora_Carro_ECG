from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ClienteCreate(BaseModel):
    cli_email: EmailStr
    cli_nome: str
    cli_senha_hash: str 
    cli_telefone: Optional[str] = None
    cli_cpf: Optional[str] = None

    class Config:
        orm_mode = True


    cli_id: str
    cli_email: EmailStr
    cli_nome: str
    cli_telefone: Optional[str] = None
    cli_cpf: Optional[str] = None
    cli_ativo: bool
    cli_criado_em: datetime

    class Config:
        orm_mode = True 