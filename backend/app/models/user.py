from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from ..database import Base
from datetime import datetime
import enum

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(String(20), primary_key=True, index=True)  # ← DEVE SER String(20)
    email = Column(String, unique=True, index=True)
    nome = Column(String)
    senha_hash = Column(String)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)