from sqlalchemy import Column, String, Boolean, DateTime, CheckConstraint
from datetime import datetime
import uuid

from app.database import Base

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo_admin = Column(String(9), unique=True, index=True, nullable=False)
    nome = Column(String(100), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    nivel_acesso = Column(String(20), nullable=False, default="operador")
    
    # Campos de controle
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    ultimo_login = Column(DateTime, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "codigo_admin ~ '^ADM\\d{6}$'", 
            name="ck_admin_codigo_formato"
        ),
    )
    
    def __repr__(self):
        return f"<Admin(id={self.id}, codigo={self.codigo_admin}, nome={self.nome})>"