from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Importações absolutas
import sys
from pathlib import Path

# Adiciona o diretório app ao path do Python
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.models import Adm
from database import get_db
from backend.app.models.Cliente import Cliente

# Importação do security
try:
    from .security import verificar_token
except ImportError:
    # Fallback para desenvolvimento
    try:
        from security import verificar_token
    except ImportError:
        # Último fallback
        from security import verificar_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Dependência para obter usuário atual
def get_current_Cliente(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Cliente:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verificar_token(token)
    if token_data is None:
        raise credentials_exception
    
    # O email está no campo "sub" do token JWT
    usuario = db.query(Cliente).filter(Cliente.email == token_data.get("sub")).first()
    if usuario is None:
        raise credentials_exception
    
    return usuario

# Dependência para validar administrador
def get_current_admin_user(current_user: Cliente = Depends(get_current_user)) -> Adm:
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

    
  