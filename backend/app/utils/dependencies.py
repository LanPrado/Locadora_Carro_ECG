from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from ..models.Adm import Admin
from ..models.Cliente import Cliente
from ..database import get_db
from ..utils.security import verificar_token

# Aponta para a rota de login do CLIENTE
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/cliente/login")

# Dependência para obter usuário (Cliente) atual
def get_current_cliente_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Cliente:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verificar_token(token)
    if token_data is None:
        raise credentials_exception
    
    # O email (sub) do token é usado para encontrar o cliente
    usuario = db.query(Cliente).filter(Cliente.cli_email == token_data.get("sub")).first()
    if usuario is None:
        raise credentials_exception
    
    # Verifica se o token é de cliente
    if token_data.get("role") != "cliente":
         raise credentials_exception
    
    return usuario

# Dependência para validar administrador
def get_current_admin_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais de admin",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verificar_token(token)
    if token_data is None:
        raise credentials_exception
    
    # --- CORREÇÃO: Lógica de validação de Admin ---
    # 1. O token DEVE ter a role "admin"
    if token_data.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: acesso restrito a administradores"
        )
    
    admin = db.query(Admin).filter(Admin.codigo_admin == token_data.get("sub")).first()
    if admin is None:
        
        raise credentials_exception
    
    return admin