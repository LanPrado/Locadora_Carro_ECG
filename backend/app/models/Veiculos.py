import uuid
import enum
from sqlalchemy import String, Float, Boolean, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from datetime import datetime

from app.database import Base

if TYPE_CHECKING:
    from .Reservar import Reserva

class CategoriaVeiculo(enum.Enum):
    ECONOMICO = "ECONOMICO"
    INTERMEDIARIO = "INTERMEDIARIO"
    LUXO = "LUXO"
    SUV = "SUV"

class StatusVeiculo(enum.Enum):
    DISPONIVEL = "DISPONIVEL"
    LOCADO = "LOCADO"
    MANUTENCAO = "MANUTENCAO"

class StatusLocacao(enum.Enum):
    RESERVADA = "RESERVADA"
    ATIVA = "ATIVA"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"

class Veiculo(Base):
    __tablename__ = "veiculos"
    
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    marca: Mapped[str] = mapped_column(String(100), nullable=False)
    ano: Mapped[int] = mapped_column(nullable=False)
    placa: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    cor: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Usando as enums
    categoria: Mapped[CategoriaVeiculo] = mapped_column(
        Enum(CategoriaVeiculo), nullable=False
    )
    status: Mapped[StatusVeiculo] = mapped_column(
        Enum(StatusVeiculo), default=StatusVeiculo.DISPONIVEL
    )
    
    # Informações de locação
    valor_diaria: Mapped[float] = mapped_column(Float, nullable=False)
    quilometragem: Mapped[float] = mapped_column(Float, default=0.0)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Controles
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relacionamento com reservas
    reservas: Mapped[list["Reserva"]] = relationship(
        "Reserva", back_populates="veiculo"
    )
    
    def __repr__(self):
        return f"<Veiculo(id={self.id}, modelo={self.modelo}, placa={self.placa})>"