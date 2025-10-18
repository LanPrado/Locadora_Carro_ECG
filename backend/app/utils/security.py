# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import random
import string
from sqlalchemy import or_

# Configurações para JWT
SECRET_KEY = "sua_chave_secreta_super_segura_aqui_altere_em_producao"  # Altere em produção!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuração para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funções para senhas
def criar_hash_senha(senha: str) -> str:
    """Cria hash bcrypt da senha"""
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash_senha: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return pwd_context.verify(senha, hash_senha)


# Funções para JWT
def criar_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Cria token JWT de acesso"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verificar_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifica e decodifica token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# Funções para geração de ID único
def extrair_sobrenome(nome_completo: str) -> str:
    """Extrai o sobrenome do nome completo"""
    partes = nome_completo.strip().split()
    if len(partes) >= 2:
        return partes[-1].lower()
    return partes[0].lower() if partes else "user"


def gerar_id_unico(sobrenome: str, db: Session, tentativa: int = 0) -> str:
    """Gera um ID único baseado no sobrenome"""
    if tentativa > 5:  # Limite de tentativas para evitar loop infinito
        # Fallback: gera ID aleatório
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"user_{random_suffix}"
    
    # Para primeira tentativa, tenta apenas o sobrenome
    if tentativa == 0:
        id_candidato = sobrenome
    else:
        # Para tentativas subsequentes, adiciona números
        random_suffix = ''.join(random.choices(string.digits, k=3))
        id_candidato = f"{sobrenome}{random_suffix}"
    
    # Verifica se o ID já existe
    from ..models.Cliente import Usuario  # Importação local para evitar circular
    usuario_existente = db.query(Usuario).filter(
        or_(Usuario.id == id_candidato, Usuario.email == id_candidato)
    ).first()
    
    if usuario_existente is None:
        return id_candidato
    else:
        # Recursivamente tenta novamente com sufixo diferente
        return gerar_id_unico(sobrenome, db, tentativa + 1)


def gerar_codigo_confirmacao() -> str:
    """Gera código de confirmação para email"""
    return ''.join(random.choices(string.digits, k=6))


# Funções para verificação de permissões
def verificar_permissao_admin(token_data: Dict[str, Any]) -> bool:
    """Verifica se o usuário tem permissão de admin"""
    return token_data.get("role") == "admin"


def verificar_permissao_cliente(token_data: Dict[str, Any]) -> bool:
    """Verifica se o usuário tem permissão de cliente"""
    return token_data.get("role") in ["cliente", "admin"]


# Função para extrair informações do token
def extrair_info_token(token: str) -> Optional[Dict[str, Any]]:
    """Extrai informações do token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("sub"),
            "role": payload.get("role")
        }
    except JWTError:
        return None