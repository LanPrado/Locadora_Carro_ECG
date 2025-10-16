from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm 

from ..database import get_db
from ..models.user import Usuario
from ..models.models import Locacao, Cliente
from ..schemas.user import UsuarioCreate, UsuarioResponse, Token, LocacaoResponse
from ..core.dependencies import (
    get_current_user, 
    get_current_admin_user, 
    get_current_cliente_user,
    get_primeiro_admin_user
)
from ..core.security import (
    criar_hash_senha, 
    verificar_senha, 
    criar_access_token,
    gerar_id_unico, 
    extrair_sobrenome
)

# ROUTERS PRINCIPAIS
router = APIRouter(tags=["Autenticação"])
cliente_router = APIRouter(tags=["Cliente"])
admin_router = APIRouter(tags=["Administração"])

class UsuarioService:
    """Serviço para operações relacionadas a usuários"""
    
    @staticmethod
    def autenticar_usuario(db: Session, username: str, senha: str) -> Optional[Usuario]:
        """Autentica um usuário por email/ID e senha"""
        # Buscar usuário por email ou ID
        usuario = db.query(Usuario).filter(
            or_(Usuario.email == username, Usuario.id == username)
        ).first()
        
        if usuario is None:
            return None
        
        # CORREÇÃO: Acessar o valor da senha_hash, não a coluna
        senha_hash_valor = usuario.senha_hash
        if senha_hash_valor is None:
            return None
            
        if not verificar_senha(senha, str(senha_hash_valor)):
            return None
            
        return usuario
    
    @staticmethod
    def criar_novo_usuario(db: Session, usuario_data: UsuarioCreate, is_admin: bool = False) -> Usuario:
        """Cria um novo usuário no sistema"""
        # Verificar se email já existe
        usuario_existente = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
        if usuario_existente is not None:
            raise HTTPException(status_code=400, detail="Email já registrado")
        
        # Gerar ID único e hash da senha
        sobrenome = extrair_sobrenome(usuario_data.nome)
        id_unico = gerar_id_unico(sobrenome, db)
        hashed_senha = criar_hash_senha(usuario_data.senha)
        
        # Determinar role baseado em is_admin
        role = "admin" if is_admin else "cliente"
        
        # Criar novo usuário
        novo_usuario = Usuario(
            id=id_unico,
            email=usuario_data.email,
            nome=usuario_data.nome,
            senha_hash=hashed_senha,
            role=role,
            ativo=True
        )
        
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        return novo_usuario
    
    @staticmethod
    def alterar_role_usuario(db: Session, user_id: str, nova_role: str) -> Usuario:
        """Altera a role de um usuário"""
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        if usuario is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # CORREÇÃO: Acessar o valor atual da role
        role_atual = usuario.role
        if role_atual is None:
            role_atual_str = ""
        else:
            role_atual_str = str(role_atual)
            
        if role_atual_str == nova_role:
            raise HTTPException(status_code=400, detail=f"Usuário já é {nova_role}")
        
        # CORREÇÃO: Usar setattr para evitar problemas de tipo
        setattr(usuario, 'role', nova_role)
        db.commit()
        db.refresh(usuario)
        
        return usuario
    
    @staticmethod
    def promover_para_admin(db: Session, user_id: str) -> Usuario:
        """Promove um usuário para administrador"""
        return UsuarioService.alterar_role_usuario(db, user_id, "admin")
    
    @staticmethod
    def rebaixar_para_cliente(db: Session, user_id: str) -> Usuario:
        """Rebaixa um administrador para cliente"""
        return UsuarioService.alterar_role_usuario(db, user_id, "cliente")
    
    @staticmethod
    def excluir_usuario_admin(db: Session, user_id: str, admin_executor: Usuario) -> dict:
        """Exclui um usuário administrador (apenas para admin)"""
        if user_id == admin_executor.id:
            raise HTTPException(status_code=400, detail="Você não pode excluir sua própria conta")
        
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        if usuario is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # CORREÇÃO: Acessar o valor da role
        role_atual = usuario.role
        if role_atual is None:
            role_atual_str = ""
        else:
            role_atual_str = str(role_atual)
            
        if role_atual_str != "admin":
            raise HTTPException(
                status_code=400, 
                detail="Apenas contas de administradores podem ser excluídas por este endpoint"
            )
        
        # Verificar se não é o último admin
        total_admins = db.query(Usuario).filter(Usuario.role == "admin").count()
        if total_admins <= 1:
            raise HTTPException(
                status_code=400,
                detail="Não é possível excluir o último administrador do sistema"
            )
        
        # Log da exclusão
        print(f"ADMIN EXCLUÍDO: {usuario.nome} ({usuario.email}) por {admin_executor.nome} em {datetime.now(timezone.utc)}")
        
        db.delete(usuario)
        db.commit()
        
        return {
            "message": f"Conta administrativa de {usuario.nome} excluída com sucesso",
            "detalhes": "Funcionário demitido removido do sistema"
        }

class ValidacaoUsuario:
    """Classe para validações de usuários"""
    
    @staticmethod
    def validar_auto_rebaixamento(user_id: str, current_user: Usuario) -> None:
        """Valida se o usuário não está tentando rebaixar a si mesmo"""
        if user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Você não pode rebaixar a si mesmo")
    
    @staticmethod
    def validar_ultimo_admin(db: Session, current_user: Usuario) -> None:
        """Valida se não é o último admin ao excluir conta"""
        total_admins = db.query(Usuario).filter(Usuario.role == "admin").count()
        if total_admins <= 1:
            raise HTTPException(
                status_code=400,
                detail="Não é possível excluir a única conta administrativa do sistema"
            )

# ROTAS PÚBLICAS DE AUTENTICAÇÃO
@router.post("/registrar", 
    response_model=UsuarioResponse,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário como cliente."
)
def registrar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """Registra um novo usuário no sistema como cliente."""
    return UsuarioService.criar_novo_usuario(db, usuario, is_admin=False)

@router.post("/login", 
    response_model=Token,
    summary="Login de usuário",
    description="Autentica usuário e retorna token JWT usando OAuth2."
)
def login_usuario(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica usuário usando email/ID e senha.
    Retorna token JWT para acesso às rotas protegidas.
    """
    usuario = UsuarioService.autenticar_usuario(db, form_data.username, form_data.password)
    
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # CORREÇÃO: Acessar o valor da role
    role_atual = usuario.role
    if role_atual is None:
        role_usuario = "cliente"
    else:
        role_usuario = str(role_atual)
    
    # Criar token JWT
    access_token = criar_access_token(
        data={
            "sub": usuario.email,
            "role": role_usuario
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# ROTAS DE CLIENTE
@cliente_router.get("/me", 
    response_model=UsuarioResponse,
    summary="Obter perfil do cliente"
)
def obter_perfil_cliente(current_user: Usuario = Depends(get_current_cliente_user)):
    return current_user

@cliente_router.get("/minhas-reservas", 
    response_model=List[LocacaoResponse],
    summary="Obter minhas reservas"
)
def obter_minhas_reservas_cliente(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_cliente_user)
):
    return (
        db.query(Locacao)
        .join(Cliente)
        .filter(Cliente.email == current_user.email)
        .all()
    )

@cliente_router.delete("/minha-conta",
    summary="Excluir minha conta"
)
def excluir_minha_conta_cliente(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_cliente_user)
):
    db.delete(current_user)
    db.commit()
    return {"message": "Sua conta foi excluída com sucesso"}

# ROTAS DE ADMINISTRAÇÃO
@admin_router.get("/me",
    response_model=UsuarioResponse,
    summary="Obter perfil do administrador"
)
def obter_perfil_admin(current_user: Usuario = Depends(get_current_admin_user)):
    return current_user

@admin_router.get("/admins",
    response_model=List[UsuarioResponse],
    summary="Listar administradores"
)
def listar_administradores(
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_current_admin_user)
):
    return db.query(Usuario).filter(Usuario.role == "admin").all()

@admin_router.post("/promover-admin/{user_id}",
    summary="Promover para administrador"
)
def promover_para_admin(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_current_admin_user)
):
    usuario_atualizado = UsuarioService.promover_para_admin(db, user_id)
    return {"message": f"Usuário {usuario_atualizado.nome} promovido a administrador"}

@admin_router.post("/rebaixar-admin/{user_id}",
    summary="Rebaixar para cliente"
)
def rebaixar_para_cliente(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_current_admin_user)
):
    ValidacaoUsuario.validar_auto_rebaixamento(user_id, admin_user)
    usuario_atualizado = UsuarioService.rebaixar_para_cliente(db, user_id)
    return {"message": f"Usuário {usuario_atualizado.nome} rebaixado para cliente"}

@admin_router.post("/criar-admin",
    response_model=UsuarioResponse,
    summary="Criar novo administrador"
)
def criar_novo_admin(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_current_admin_user)
):
    """Cria uma nova conta de administrador."""
    return UsuarioService.criar_novo_usuario(db, usuario, is_admin=True)

@admin_router.delete("/conta/{user_id}",
    summary="Excluir conta administrativa"
)
def excluir_conta_admin(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_current_admin_user)
):
    return UsuarioService.excluir_usuario_admin(db, user_id, admin_user)

@admin_router.delete("/minha-conta",
    summary="Excluir minha conta administrativa"
)
def excluir_minha_conta_admin(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin_user)
):
    ValidacaoUsuario.validar_ultimo_admin(db, current_user)
    db.delete(current_user)
    db.commit()
    return {"message": "Sua conta administrativa foi excluída com sucesso"}

# Incluir rotas
router.include_router(cliente_router, prefix="/clientes")
router.include_router(admin_router, prefix="/admin")