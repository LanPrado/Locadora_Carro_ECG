# app/services/auth_service.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional

# Importe seus modelos e schemas
from ..models.Cliente import Cliente as Usuario
from ..models.Adm import Admin as UsuarioAdmin
from ..schemas.usuario import UsuarioCreate # (Estou assumindo que você tem um schema.py)

# Importe suas funções de segurança
from ..utils.security import (
    criar_hash_senha, 
    verificar_senha, 
    criar_access_token
)

def autenticar_usuario(db: Session, username: str, senha: str) -> Optional[Usuario]:
    """Autentica um usuário (Cliente) por email e senha"""
    # Seu código original usava 'email' ou 'id', mas o modelo Cliente
    # que fizemos usa 'cli_email' e 'cli_id' (UUID).
    # Vamos focar no email para o login.
    usuario = db.query(Usuario).filter(Usuario.cli_email == username).first()
    
    if usuario is None:
        return None
    
    if not verificar_senha(senha, str(usuario.cli_senha_hash)):
        return None
        
    return usuario

def autenticar_admin(db: Session, username: str, senha: str) -> Optional[UsuarioAdmin]:
    """Autentica um usuário (Admin) por código e senha"""
    # Admins fazem login com o 'adm_codigo'
    admin = db.query(UsuarioAdmin).filter(UsuarioAdmin.adm_codigo == username).first()
    
    if admin is None:
        return None
    
    if not verificar_senha(senha, str(admin.adm_senha_hash)):
        return None
        
    return admin

def criar_novo_usuario(db: Session, usuario_data: UsuarioCreate) -> Usuario:
    """Cria um novo usuário (Cliente) no sistema"""
    
    hashed_senha = criar_hash_senha(usuario_data.senha)
    
    novo_usuario = Usuario(
        # ID é gerado automaticamente (não passe 'id=' aqui)
        cli_email=usuario_data.email.lower(),
        cli_nome=usuario_data.nome,
        cli_senha_hash=hashed_senha
        # O resto (cli_ativo, cli_criado_em) usa os 'defaults' do modelo
    )
    
    db.add(novo_usuario)
    try:
        db.commit()
        db.refresh(novo_usuario)
    except IntegrityError:
        # Isso é o que seu colega faz
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Um usuário com este e-mail já existe."
        )
    
    return novo_usuario