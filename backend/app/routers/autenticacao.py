# app/routers/autenticacao.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm 

from ..database import get_db
# Importe os serviços, como seu colega faz
from Services import auth_service 
# Importe os schemas (Pydantic models)
from ..models.Cliente import UsuarioCreate, UsuarioResponse
from ..schemas.token import Token
# Importe as utils
from ..utils.security import criar_access_token

# --- Rota de Autenticação de Cliente ---
cliente_auth_router = APIRouter(
    prefix="/auth/cliente",
    tags=["Autenticação de Cliente"]
)

@cliente_auth_router.post("/registrar", 
    response_model=UsuarioResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo cliente"
)
def registrar_cliente(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova conta de usuário como cliente."""
    # Chama o serviço, assim como seu colega
    return auth_service.criar_novo_usuario(db, usuario)

@cliente_auth_router.post("/login", 
    response_model=Token,
    summary="Login de cliente"
)
def login_cliente(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Autentica cliente e retorna token JWT."""
    # Chama o serviço
    usuario = auth_service.autenticar_usuario(
        db, form_data.username, form_data.password
    )
    
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha de cliente incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = criar_access_token(
        data={"sub": usuario.cli_email, "role": "cliente"}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# --- Rota de Autenticação de Admin ---
admin_auth_router = APIRouter(
    prefix="/auth/admin",
    tags=["Autenticação de Admin"]
)

@admin_auth_router.post("/login", 
    response_model=Token,
    summary="Login de administrador"
)
def login_admin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica administrador (usando 'adm_codigo' como username) 
    e retorna token JWT.
    """
    admin = auth_service.autenticar_admin(
        db, form_data.username, form_data.password
    )
    
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de admin ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = criar_access_token(
        data={"sub": admin.adm_codigo, "role": "admin"}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}