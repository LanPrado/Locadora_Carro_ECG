from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
import uuid

# USE import absoluto em vez de relativo
from app.database import Base  # ← Mude para import absoluto

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    nome = Column(String, nullable=False)
    senha_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="cliente")
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, role={self.role})>"