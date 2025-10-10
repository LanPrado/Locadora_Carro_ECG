from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime
import enum

class CategoriaVeiculo(enum.Enum):
    ECONOMICO = "econômico"
    INTERMEDIARIO = "intermediário"
    LUXO = "luxo"
    SUV = "suv"

class StatusVeiculo(enum.Enum):
    DISPONIVEL = "disponível"
    LOCADO = "locado"
    MANUTENCAO = "manutenção"

class StatusLocacao(enum.Enum):
    RESERVADA = "reservada"
    ATIVA = "ativa"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"

class Veiculo(Base):
    __tablename__ = "veiculos"
    
    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String, unique=True, index=True)
    modelo = Column(String)
    marca = Column(String)
    ano = Column(Integer)
    categoria = Column(Enum(CategoriaVeiculo))
    diaria = Column(Float)
    quilometragem = Column(Integer, default=0)
    status = Column(Enum(StatusVeiculo), default=StatusVeiculo.DISPONIVEL)
    imagem_url = Column(String, nullable=True)
    descricao = Column(String, nullable=True)
    
    locacoes = relationship("Locacao", back_populates="veiculo")

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String, unique=True, index=True)
    nome = Column(String)
    email = Column(String)
    telefone = Column(String)
    cnh = Column(String)
    data_validade_cnh = Column(DateTime)
    endereco = Column(String)
    ativo = Column(Boolean, default=True)
    
    locacoes = relationship("Locacao", back_populates="cliente")

class Locacao(Base):
    __tablename__ = "locacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"))
    data_inicio = Column(DateTime)
    data_fim = Column(DateTime)
    data_devolucao = Column(DateTime, nullable=True)
    quilometragem_inicial = Column(Integer)
    quilometragem_final = Column(Integer, nullable=True)
    valor_total = Column(Float)
    status = Column(Enum(StatusLocacao), default=StatusLocacao.RESERVADA)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    cliente = relationship("Cliente", back_populates="locacoes")
    veiculo = relationship("Veiculo", back_populates="locacoes")