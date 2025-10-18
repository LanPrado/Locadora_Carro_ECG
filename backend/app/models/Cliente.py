from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
import uuid

from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    
    cli_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cli_email = Column(String(255), unique=True, index=True, nullable=False)
    nome = Column(String(100), nullable=False)
    cli_senha = Column(String(255), nullable=False)
    telefone = Column(String(20), nullable=True)
    cpf = Column(String(11), unique=True, nullable=True)
    
    # Campos de controle
    ativo = Column(Boolean, default=True)
    email_verificado = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, email={self.email}, nome={self.nome})>"
    
    def to_dict(self):
        """Converte para dicionário (útil para APIs)"""
        return {
            'id': self.id,
            'email': self.email,
            'nome': self.nome,
            'telefone': self.telefone,
            'ativo': self.ativo,
            'email_verificado': self.email_verificado,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }