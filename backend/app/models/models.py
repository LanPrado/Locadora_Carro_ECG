# app/models/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

from .Veiculos import CategoriaVeiculo, StatusVeiculo

class Veiculo(Base):
    __tablename__ = "veiculos"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    placa = Column(String(10), unique=True, index=True, nullable=False)
    modelo = Column(String(50), nullable=False)
    marca = Column(String(50), nullable=False)
    ano = Column(Integer)
    
    categoria = Column(SQLEnum(CategoriaVeiculo), nullable=False)
    diaria = Column(Float, nullable=False)
    status = Column(SQLEnum(StatusVeiculo), default=StatusVeiculo.DISPONIVEL)
    
    quilometragem = Column(Integer, default=0)
    imagem_url = Column(String(255), nullable=True)
    
    descricao = Column(String(255), nullable=True)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reservas = relationship("Reserva", back_populates="veiculo")
    
    def __repr__(self):
        return f"<Veiculo(id={self.id}, placa={self.placa})>"