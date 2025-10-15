from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from ..database import get_db
from ..models.user import Usuario
from .security import SECRET_KEY, ALGORITHM, verificar_token_jwt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Dependência para obter usuário atual
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verificar_token_jwt(token)
    if token_data is None:
        raise credentials_exception
    
    usuario = db.query(Usuario).filter(Usuario.email == token_data["email"]).first()
    if usuario is None:
        raise credentials_exception
    
    return usuario

# Dependência para validar administrador
def get_current_admin_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if str(current_user.role) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: acesso restrito a administradores"
        )
    return current_user

# Dependência para validar cliente
def get_current_cliente_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if str(current_user.role) != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: acesso restrito a clientes"
        )
    return current_user

# Dependência para validar primeiro admin
def get_primeiro_admin_user(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)) -> Usuario:
    if str(current_user.role) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: acesso restrito a administradores"
        )
    
    # Encontrar o primeiro usuário admin criado
    primeiro_admin = db.query(Usuario).filter(Usuario.role == "admin").order_by(Usuario.criado_em.asc()).first()
    
    if primeiro_admin is None or str(primeiro_admin.id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: apenas o administrador principal pode executar esta ação"
        )
    return current_user