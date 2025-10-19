# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

from .Veiculos import CategoriaVeiculo, StatusVeiculo


class Veiculo(Base):
    __tablename__ = "veiculos"
    
    # Chave corrigida para String (UUID)
    Vei_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    Vei_placa = Column(String(10), unique=True, index=True, nullable=False)
    Vei_modelo = Column(String(50), nullable=False)
    Vei_marca = Column(String(50), nullable=False)
    Vei_ano = Column(Integer)
    
    # Enums corrigidos
    Vei_categoria = Column(SQLEnum(CategoriaVeiculo), nullable=False)
    Vei_diaria = Column(Float, nullable=False)
    Vei_status = Column(SQLEnum(StatusVeiculo), default=StatusVeiculo.DISPONIVEL)
    
    descricao = Column(String(255), nullable=True)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # --- RELACIONAMENTO ATUALIZADO ---
    # Agora aponta para a classe 'Reserva' (em Reservar.py)
    reservas = relationship("Reserva", back_populates="veiculo")
    
    def __repr__(self):
        return f"<Veiculo(Vei_id={self.Vei_id}, Vei_placa={self.Vei_placa})>"