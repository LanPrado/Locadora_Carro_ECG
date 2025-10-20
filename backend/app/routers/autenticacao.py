from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm 

from ..database import get_db
from ..Services import auth_service 
from ..Schemas.Usuario import UsuarioCreate, UsuarioResponse 
from ..Schemas.Token import Token 
from ..utils.security import criar_access_token, criar_hash_senha
from app.Schemas.Admin import AdminCreate, AdminResponse  
from app.models.Adm import Admin  

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
    usuario: UsuarioCreate, # Usa o Schema de auto-registro
    db: Session = Depends(get_db)
):
    """Cria uma nova conta de usuário como cliente."""
    return auth_service.criar_novo_usuario(db, usuario)

@cliente_auth_router.post("/login", 
    response_model=Token,
    summary="Login de cliente (Cliente loga)"
)
def login_cliente(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Autentica cliente (username=email) e retorna token JWT."""
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
    """
    Registra um novo administrador no sistema.
    Código deve estar no formato: ADM000001 (ADM + 6 dígitos)
    Níveis de acesso: operador, supervisor, super
    """
    # Verificar se o código já existe
    admin_existente = db.query(Admin).filter(Admin.codigo_admin == admin.codigo_admin).first()
    if admin_existente:
        raise HTTPException(
            status_code=400,
            detail="Código de administrador já existe"
        )
    
    # Criar hash da senha
    senha_hash = criar_hash_senha(admin.senha)
    
    # Criar novo admin
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
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica administrador (username=adm_codigo) 
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
        data={"sub": admin.codigo_admin, "role": "admin"} # CORREÇÃO: Usar o campo correto do modelo Admin
    )
    
    return {"access_token": access_token, "token_type": "bearer"}