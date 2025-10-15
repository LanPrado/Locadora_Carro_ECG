from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, timezone

from ..database import get_db
from ..models.user import Usuario
from ..models.models import Locacao, Cliente
from ..schemas.user import UsuarioCreate, UsuarioResponse, LoginRequest, Token, LocacaoResponse
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
    def criar_novo_usuario(db: Session, usuario_data: UsuarioCreate) -> Usuario:
        """Cria um novo usuário no sistema"""
        # Verificar se email já existe
        usuario_existente = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
        if usuario_existente is not None:
            raise HTTPException(status_code=400, detail="Email já registrado")
        
        # Gerar ID único e hash da senha
        sobrenome = extrair_sobrenome(usuario_data.nome)
        id_unico = gerar_id_unico(sobrenome, db)
        hashed_senha = criar_hash_senha(usuario_data.senha)
        
        # Definir role (primeiro usuário é admin)
        total_usuarios = db.query(Usuario).count()
        role = "admin" if total_usuarios == 0 else "cliente"
        
        # Criar novo usuário
        novo_usuario = Usuario(
            id=id_unico,
            email=usuario_data.email,
            nome=usuario_data.nome,
            senha_hash=hashed_senha,
            role=role
        )
        
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        return novo_usuario
    
    @staticmethod
    def autenticar_usuario(db: Session, email: str, senha: str) -> Optional[Usuario]:
        """Autentica um usuário com email/ID e senha"""
        usuario = db.query(Usuario).filter(
            or_(Usuario.email == email, Usuario.id == email)
        ).first()
        
        if usuario is None or not verificar_senha(senha, str(usuario.senha_hash)):
            return None
        
        return usuario
    
    @staticmethod
    def alterar_role_usuario(db: Session, user_id: str, nova_role: str) -> Usuario:
        """Altera a role de um usuário"""
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        if usuario is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        if str(usuario.role) == nova_role:
            raise HTTPException(status_code=400, detail=f"Usuário já é {nova_role}")
        
        db.query(Usuario).filter(Usuario.id == user_id).update({"role": nova_role})
        db.commit()
        
        # Recarregar usuário atualizado
        usuario_atualizado = db.query(Usuario).filter(Usuario.id == user_id).first()
        if usuario_atualizado is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado após atualização")
        
        return usuario_atualizado
    
    @staticmethod
    def excluir_usuario_admin(db: Session, user_id: str, admin_executor: Usuario) -> dict:
        """Exclui um usuário administrador (apenas para primeiro admin)"""
        # CORREÇÃO: Converter para string antes da comparação
        if user_id == str(admin_executor.id):
            raise HTTPException(status_code=400, detail="Você não pode excluir sua própria conta")
        
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        if usuario is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        if str(usuario.role) != "admin":
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
        # CORREÇÃO: Receber o objeto usuário completo e converter para string
        if user_id == str(current_user.id):
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
    description="Cria uma nova conta de usuário. O primeiro usuário se torna administrador."
)
def registrar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """
    Registra um novo usuário no sistema.
    O primeiro usuário registrado automaticamente se torna administrador.
    """
    return UsuarioService.criar_novo_usuario(db, usuario)

@router.post("/login", 
    response_model=Token,
    summary="Login de usuário",
    description="Autentica usuário e retorna token JWT para acesso às rotas protegidas."
)
def login_usuario(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Autentica usuário usando email/ID e senha.
    Retorna token JWT para acesso às rotas protegidas.
    """
    usuario = UsuarioService.autenticar_usuario(db, login_data.email, login_data.senha)
    
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    
    # Criar token JWT
    access_token = criar_access_token(
        data={
            "sub": usuario.email,
            "role": usuario.role,
            "user_id": usuario.id
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# ROTAS DE CLIENTE (ÁREA DO CLIENTE)

@cliente_router.get("/me", 
    response_model=UsuarioResponse,
    summary="Obter perfil do cliente",
    description="Retorna os dados do perfil do cliente autenticado."
)
def obter_perfil_cliente(current_user: Usuario = Depends(get_current_cliente_user)):
    """Retorna o perfil do cliente autenticado"""
    return current_user


@cliente_router.get("/minhas-reservas", 
    response_model=List[LocacaoResponse],
    summary="Obter minhas reservas",
    description="Retorna todas as reservas/locações do cliente autenticado."
)
def obter_minhas_reservas_cliente(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_cliente_user)
):
    """Retorna todas as locações do cliente autenticado"""
    return (
        db.query(Locacao)
        .join(Cliente)
        .filter(Cliente.email == current_user.email)
        .all()
    )


@cliente_router.delete("/minha-conta",
    summary="Excluir minha conta",
    description="Exclui permanentemente a conta do cliente autenticado."
)
def excluir_minha_conta_cliente(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_cliente_user)
):
    """Exclui a conta do cliente autenticado"""
    db.delete(current_user)
    db.commit()
    return {"message": "Sua conta foi excluída com sucesso"}

# ROTAS DE ADMINISTRAÇÃO (ÁREA DO ADMIN)

@admin_router.get("/me",
    response_model=UsuarioResponse,
    summary="Obter perfil do administrador",
    description="Retorna os dados do perfil do administrador autenticado."
)
def obter_perfil_admin(current_user: Usuario = Depends(get_current_admin_user)):
    """Retorna o perfil do administrador autenticado"""
    return current_user


@admin_router.get("/admins",
    response_model=List[UsuarioResponse],
    summary="Listar administradores",
    description="Retorna lista de todos os administradores do sistema."
)
def listar_administradores(
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_current_admin_user)
):
    """Retorna todos os administradores do sistema"""
    return db.query(Usuario).filter(Usuario.role == "admin").all()


@admin_router.post("/promover-admin/{user_id}",
    summary="Promover para administrador",
    description="Promove um usuário comum para administrador."
)
def promover_para_admin(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_current_admin_user)
):
    """Promove um usuário comum para administrador"""
    usuario_atualizado = UsuarioService.alterar_role_usuario(db, user_id, "admin")
    return {"message": f"Usuário {usuario_atualizado.nome} promovido a administrador"}


@admin_router.post("/rebaixar-admin/{user_id}",
    summary="Rebaixar para cliente",
    description="Rebaixa um administrador para cliente (exceto a si mesmo)."
)
def rebaixar_para_cliente(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_current_admin_user)
):
    """Rebaixa um administrador para cliente"""
    ValidacaoUsuario.validar_auto_rebaixamento(user_id, admin_user)
    usuario_atualizado = UsuarioService.alterar_role_usuario(db, user_id, "cliente")
    return {"message": f"Usuário {usuario_atualizado.nome} rebaixado para cliente"}

@admin_router.delete("/conta/{user_id}",
    summary="Excluir conta administrativa",
    description="Apenas o PRIMEIRO admin pode excluir contas de outros admins."
)
def excluir_conta_admin(
    user_id: str,
    db: Session = Depends(get_db),
    primeiro_admin: Usuario = Depends(get_primeiro_admin_user)
):
    """Exclui uma conta administrativa (apenas para primeiro admin)"""
    return UsuarioService.excluir_usuario_admin(db, user_id, primeiro_admin)


@admin_router.delete("/minha-conta",
    summary="Excluir minha conta administrativa",
    description="Admin exclui sua própria conta (verifica se não é o último admin)."
)
def excluir_minha_conta_admin(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin_user)
):
    """Exclui a conta do administrador autenticado"""
    ValidacaoUsuario.validar_ultimo_admin(db, current_user)
    db.delete(current_user)
    db.commit()
    return {"message": "Sua conta administrativa foi excluída com sucesso"}

# Incluir rotas de cliente com prefixo /clientes
router.include_router(cliente_router, prefix="/clientes")

# Incluir rotas de admin com prefixo /admin  
router.include_router(admin_router, prefix="/admin")