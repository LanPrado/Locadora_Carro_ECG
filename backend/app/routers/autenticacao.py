from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel  

from ..database import get_db
from ..Services import auth_service 
from ..Schemas.Usuario import UsuarioCreate, UsuarioResponse 
from ..Schemas.Token import Token 
from ..utils.security import criar_access_token, criar_hash_senha
from app.Schemas.Admin import AdminCreate, AdminResponse  
from app.models.Adm import Admin  

class AdminLoginRequest(BaseModel):
    codigo_admin: str
    senha: str

class ClienteLoginRequest(BaseModel):
    email: str
    senha: str

cliente_auth_router = APIRouter(
    prefix="/auth/cliente",
    tags=["Autenticação de Cliente"]
)

@cliente_auth_router.post("/registrar", 
    response_model=UsuarioResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo cliente (Cliente se registra)"
)
def registrar_cliente(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova conta de usuário como cliente."""
    return auth_service.criar_novo_usuario(db, usuario)

@cliente_auth_router.post("/login", 
    response_model=Token,
    summary="Login de cliente (Cliente loga)"
)
def login_cliente(
    login_data: ClienteLoginRequest, 
    db: Session = Depends(get_db)
):
    """Autentica cliente (email) e retorna token JWT."""
    usuario = auth_service.autenticar_usuario(
        db, login_data.email, login_data.senha  
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

# Rota de Autenticação de Admin 
admin_auth_router = APIRouter(
    prefix="/auth/admin",
    tags=["Autenticação de Admin"]
)

@admin_auth_router.post("/registrar", 
    response_model=AdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo administrador",
    description="Cria uma nova conta de administrador (apenas para desenvolvimento)"
)
def registrar_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db)
):
   
    admin_existente = db.query(Admin).filter(Admin.codigo_admin == admin.codigo_admin).first()
    if admin_existente:
        raise HTTPException(
            status_code=400,
            detail="Código de administrador já existe"
        )
    
    senha_hash = criar_hash_senha(admin.senha)
    
    novo_admin = Admin(
        codigo_admin=admin.codigo_admin,
        adm_nome=admin.adm_nome,
        senha_hash=senha_hash,
        nivel_acesso=admin.nivel_acesso
    )
    
    db.add(novo_admin)
    db.commit()
    db.refresh(novo_admin)
    
    return novo_admin

@admin_auth_router.post("/login", 
    response_model=Token,
    summary="Login de administrador (Admin loga)"
)
def login_admin(
    login_data: AdminLoginRequest, 
    db: Session = Depends(get_db)
):
    """Autentica administrador (código_admin) e retorna token JWT."""
    admin = auth_service.autenticar_admin(
        db, login_data.codigo_admin, login_data.senha  
    )
    
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de admin ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = criar_access_token(
        data={"sub": admin.codigo_admin, "role": "admin"}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}