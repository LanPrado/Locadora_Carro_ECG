from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
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

# Funções de utilitário (mantidas as existentes)
def criar_hash_senha(senha: str) -> str:
    if len(senha.encode('utf-8')) > 72:
        senha_bytes = senha.encode('utf-8')[:72]
        senha = senha_bytes.decode('utf-8', 'ignore')
    return pwd_context.hash(senha)

def verificar_senha(senha: str, hash_senha: str) -> bool:
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

#  FUNÇÕES DE AUTENTICAÇÃO COM SISTEMA DE SEGURANÇA
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
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
        
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if usuario is None:
            raise credentials_exception
        return usuario
    except JWTError:
        raise credentials_exception

def get_current_admin_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: acesso restrito a administradores"
        )
    return current_user

def get_primeiro_admin_user(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)) -> Usuario:
    """
    Verifica se o usuário é o PRIMEIRO admin do sistema
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: acesso restrito a administradores"
        )
    
    # Encontrar o primeiro usuário admin criado
    primeiro_admin = db.query(Usuario).filter(Usuario.role == "admin").order_by(Usuario.criado_em.asc()).first()
    
    if not primeiro_admin or primeiro_admin.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: apenas o administrador principal pode executar esta ação"
        )
    
    return current_user

def get_current_cliente_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.role != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: acesso restrito a clientes"
        )
    return current_user

def extrair_sobrenome(nome_completo: str) -> str:
    partes = nome_completo.strip().split()
    if len(partes) == 0:
        return "User"
    elif len(partes) == 1:
        return partes[0]
    else:
        return partes[-1]

def gerar_id_unico(sobrenome: str, db: Session, max_tentativas: int = 100) -> str:
    sobrenome_limpo = ''.join(c for c in sobrenome if c.isalnum())
    sobrenome_base = sobrenome_limpo[:12]
    
    if not sobrenome_base:
        sobrenome_base = "User"
    
    for tentativa in range(max_tentativas):
        numeros_aleatorios = ''.join(random.choices(string.digits, k=8))
        id_gerado = f"{sobrenome_base}{numeros_aleatorios}"
        
        usuario_existente = db.query(Usuario).filter(Usuario.id == id_gerado).first()
        if not usuario_existente:
            return id_gerado
    
    letras_extra = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{sobrenome_base}{numeros_aleatorios}{letras_extra}"

# Cria o router
router = APIRouter()

@router.post("/registrar", response_model=UsuarioResponse)
def registrar(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario_email = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario_email:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    sobrenome = extrair_sobrenome(usuario.nome)
    id_unico = gerar_id_unico(sobrenome, db)
    hashed_senha = criar_hash_senha(usuario.senha)
    
    total_usuarios = db.query(Usuario).count()
    role = "admin" if total_usuarios == 0 else "cliente"
    
    novo_usuario = Usuario(
        id=id_unico,
        email=usuario.email,
        nome=usuario.nome,
        senha_hash=hashed_senha,
        role=role
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return novo_usuario

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == login_data.email).first()
    
    if not usuario:
        usuario = db.query(Usuario).filter(Usuario.id == login_data.email).first()
    
    if not usuario or not verificar_senha(login_data.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    
    access_token = criar_access_token(
        data={
            "sub": usuario.email,
            "role": usuario.role,
            "user_id": usuario.id
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UsuarioResponse)
def obter_perfil_usuario(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.get("/admins", response_model=List[UsuarioResponse])
def listar_administradores(
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_current_admin_user)
):
    """
    Lista todos os administradores do sistema
    """
    admins = db.query(Usuario).filter(Usuario.role == "admin").all()
    return admins

@router.post("/promover-admin/{user_id}")
def promover_para_admin(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: Usuario = Depends(get_current_admin_user)
):
    """
    Promove um usuário comum para administrador
    Qualquer admin pode promover
    """
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if usuario.role == "admin":
        raise HTTPException(status_code=400, detail="Usuário já é administrador")
    
    usuario.role = "admin"
    db.commit()
    db.refresh(usuario)
    
    return {"message": f"Usuário {usuario.nome} promovido a administrador"}

#"@router.post("/rebaixar-admin/{user_id}")
#def rebaixar_para_cliente(
    #user_id: str,
   # db: Session = Depends(get_db),
   # admin_user: Usuario = Depends(get_current_admin_user)
#):
    """
    Rebaixa um administrador para cliente
    Qualquer admin pode rebaixar, exceto a si mesmo
    """
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=400, 
            detail="Você não pode rebaixar a si mesmo"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if usuario.role != "admin":
        raise HTTPException(status_code=400, detail="Usuário não é administrador")
    
    usuario.role = "cliente"
    db.commit()
    db.refresh(usuario)
    
    return {"message": f"Usuário {usuario.nome} rebaixado para cliente"}

@router.delete("/admin/{user_id}")
def excluir_conta_admin(
    user_id: str,
    db: Session = Depends(get_db),
    primeiro_admin: Usuario = Depends(get_primeiro_admin_user)
):
    """
     Apenas o PRIMEIRO admin pode excluir contas de outros admins
    Usado quando um funcionário admin é demitido
    """
    if user_id == primeiro_admin.id:
        raise HTTPException(
            status_code=400, 
            detail="Você não pode excluir sua própria conta"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if usuario.role != "admin":
        raise HTTPException(
            status_code=400, 
            detail="Apenas contas de administradores podem ser excluídas por este endpoint"
        )
    
    # Verificar quantos admins restam
    total_admins = db.query(Usuario).filter(Usuario.role == "admin").count()
    if total_admins <= 1:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir o último administrador do sistema"
        )
    
    # ⭐ LOG de auditoria (poderia salvar em uma tabela de logs)
    print(f"🚨 ADMIN EXCLUÍDO: {usuario.nome} ({usuario.email}) por {primeiro_admin.nome} em {datetime.utcnow()}")
    
    db.delete(usuario)
    db.commit()
    
    return {
        "message": f"Conta administrativa de {usuario.nome} excluída com sucesso",
        "detelhes": "Funcionário demitido removido do sistema"
    }

@router.delete("/minha-conta")
def excluir_minha_conta(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Qualquer usuário pode excluir sua própria conta
    """
    # Verificar se é o último admin
    if current_user.role == "admin":
        total_admins = db.query(Usuario).filter(Usuario.role == "admin").count()
        if total_admins <= 1:
            raise HTTPException(
                status_code=400,
                detail="Não é possível excluir a única conta administrativa do sistema"
            )
    
    db.delete(current_user)
    db.commit()
    
    return {"message": "Sua conta foi excluída com sucesso"}