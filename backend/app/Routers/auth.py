from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

#importações necessárias
from ..database import get_db
from ..models import Usuario
from ..schemas import UsuarioCreate, UsuarioResponse, LoginRequest, Token
from ..auth import criar_hash_senha, verificar_senha, criar_access_token

router = APIRouter()

@router.post("/registrar", response_model=UsuarioResponse)
def registrar(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    novo_usuario = Usuario(
        email=usuario.email,
        nome=usuario.nome,
        senha_hash=criar_hash_senha(usuario.senha)
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return novo_usuario

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == login_data.email).first()
    
    if not usuario or not verificar_senha(login_data.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    
    access_token = criar_access_token(data={"sub": usuario.email})
    
    return {"access_token": access_token, "token_type": "bearer"}