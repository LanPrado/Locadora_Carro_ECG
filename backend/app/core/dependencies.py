from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Importações absolutas
import sys
from pathlib import Path

# Adiciona o diretório app ao path do Python
sys.path.append(str(Path(__file__).parent.parent))

from database import get_db
from models.user import Usuario

# Importação do security
try:
    from .security import verificar_token
except ImportError:
    # Fallback para desenvolvimento
    try:
        from app.core.security import verificar_token
    except ImportError:
        # Último fallback
        from core.security import verificar_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Dependência para obter usuário atual
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verificar_token(token)
    if token_data is None:
        raise credentials_exception
    
    # O email está no campo "sub" do token JWT
    usuario = db.query(Usuario).filter(Usuario.email == token_data.get("sub")).first()
    if usuario is None:
        raise credentials_exception
    
    return usuario

# Dependência para validar administrador
def get_current_admin_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    # CORREÇÃO: Acessar o valor da role corretamente
    role_atual = current_user.role
    if role_atual is None:
        role_str = ""
    else:
        role_str = str(role_atual)
        
    if role_str != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: acesso restrito a administradores"
        )
    return current_user

# Dependência para validar cliente
def get_current_cliente_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    # CORREÇÃO: Acessar o valor da role corretamente
    role_atual = current_user.role
    if role_atual is None:
        role_str = ""
    else:
        role_str = str(role_atual)
        
    if role_str != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: acesso restrito a clientes"
        )
    return current_user

# Dependência para validar primeiro admin
def get_primeiro_admin_user(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)) -> Usuario:
    # CORREÇÃO: Acessar o valor da role corretamente
    role_atual = current_user.role
    if role_atual is None:
        role_str = ""
    else:
        role_str = str(role_atual)
        
    if role_str != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: acesso restrito a administradores"
        )
    
    # Encontrar o primeiro usuário admin criado
    # Se não houver campo criado_em, usar id como fallback
    primeiro_admin = db.query(Usuario).filter(Usuario.role == "admin").order_by(Usuario.id).first()
    
    if primeiro_admin is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nenhum administrador encontrado no sistema"
        )
    
    # CORREÇÃO: Acessar o ID corretamente
    primeiro_admin_id = primeiro_admin.id
    current_user_id = current_user.id
    
    if str(primeiro_admin_id) != str(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: apenas o administrador principal pode executar esta ação"
        )
    return current_user