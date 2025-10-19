from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from datetime import datetime
import uuid

from app.database import Base # Importando Base, conforme padrão dos outros arquivos

class Veiculo(Base):
    __tablename__ = "veiculos"
    
    # Chave primária
    vei_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cli_id = Column(String, ForeignKey("clientes.cli_id"), nullable=False, index=True)
    # Dados do Veículo
    placa = Column(String(10), unique=True, index=True, nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    ano_modelo = Column(Integer, nullable=True)
    descricao = Column(String(255), unique=True, index=True, nullable=True)
    
    # Campos de controle 
    ativo = Column(Boolean, default=True)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Veiculo(id={self.vei_id}, placa={self.placa}, modelo={self.modelo})>"

    def to_dict(self):
        """Converte para dicionário (útil para APIs)"""
        return {
            'vei_id': self.vei_id,
            'cli_id': self.cli_id,
            'placa': self.placa,
            'marca': self.marca,
            'modelo': self.modelo,
            'ano_modelo': self.ano_modelo,
            'descricao': self.descricao,
            'ativo': self.ativo,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }