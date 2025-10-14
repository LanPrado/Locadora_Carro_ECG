from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import random
import string

from ..database import get_db
from ..models.user import Usuario
from ..schemas.user import UsuarioCreate, UsuarioResponse, LoginRequest, Token

# Configurações
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "sua_chave_secreta_super_segura_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Funções de utilitário
def criar_hash_senha(senha: str) -> str:
    # CORREÇÃO: Truncar senha para 72 bytes se for muito longa
    if len(senha.encode('utf-8')) > 72:
        # Converter para bytes, truncar, e voltar para string
        senha_bytes = senha.encode('utf-8')[:72]
        senha = senha_bytes.decode('utf-8', 'ignore')
    return pwd_context.hash(senha)

def verificar_senha(senha: str, hash_senha: str) -> bool:
    # CORREÇÃO: Aplicar o mesmo truncamento na verificação
    if len(senha.encode('utf-8')) > 72:
        senha_bytes = senha.encode('utf-8')[:72]
        senha = senha_bytes.decode('utf-8', 'ignore')
    return pwd_context.verify(senha, hash_senha)

def criar_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verificar_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Verifica e decodifica o token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return {"email": email}
    except JWTError:
        raise credentials_exception

def extrair_sobrenome(nome_completo: str) -> str:
    """
    Extrai o sobrenome do nome completo
    """
    partes = nome_completo.strip().split()
    if len(partes) == 0:
        return "User"  # Fallback se não houver nome
    elif len(partes) == 1:
        return partes[0]  # Retorna o único nome disponível
    else:
        return partes[-1]  # Retorna o último nome (sobrenome)

def gerar_id_unico(sobrenome: str, db: Session, max_tentativas: int = 100) -> str:
    """
    Gera um ID único baseado no sobrenome + 8 números aleatórios
    """
    # Limitar o sobrenome a 12 caracteres para não ultrapassar 20 no total
    sobrenome_limpo = ''.join(c for c in sobrenome if c.isalnum())
    sobrenome_base = sobrenome_limpo[:12]
    
    if not sobrenome_base:
        sobrenome_base = "User"
    
    for tentativa in range(max_tentativas):
        # Gerar 8 números aleatórios
        numeros_aleatorios = ''.join(random.choices(string.digits, k=8))
        
        # Combinar sobrenome + números
        id_gerado = f"{sobrenome_base}{numeros_aleatorios}"
        
        # Verificar se já existe no banco
        usuario_existente = db.query(Usuario).filter(Usuario.id == id_gerado).first()
        if not usuario_existente:
            return id_gerado
    
    # Se não conseguir gerar um único após várias tentativas, adiciona letras
    letras_extra = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{sobrenome_base}{numeros_aleatorios}{letras_extra}"

# Cria o router
router = APIRouter()

@router.post("/registrar", response_model=UsuarioResponse)
def registrar(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar se email já existe
    db_usuario_email = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario_email:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    # Gerar ID único baseado no sobrenome
    sobrenome = extrair_sobrenome(usuario.nome)
    id_unico = gerar_id_unico(sobrenome, db)
    
    # Criar hash da senha
    hashed_senha = criar_hash_senha(usuario.senha)
    
    # Criar novo usuário
    novo_usuario = Usuario(
        id=id_unico,  # Usar o ID gerado automaticamente
        email=usuario.email,
        nome=usuario.nome,
        senha_hash=hashed_senha,
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return novo_usuario

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # Primeiro tentar encontrar por email
    usuario = db.query(Usuario).filter(Usuario.email == login_data.email).first()
    
    # Se não encontrar por email, tentar encontrar por ID
    if not usuario:
        usuario = db.query(Usuario).filter(Usuario.id == login_data.email).first()
    
    # Verificar se usuário existe e senha está correta
    if not usuario or not verificar_senha(login_data.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    
    access_token = criar_access_token(data={"sub": usuario.email})
    return {"access_token": access_token, "token_type": "bearer"}