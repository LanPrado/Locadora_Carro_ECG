from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from ..database import Base  # ← CORRIGIDO
from datetime import datetime
import enum

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    nome = Column(String)
    senha_hash = Column(String)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)