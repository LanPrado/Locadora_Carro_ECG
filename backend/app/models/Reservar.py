from sqlalchemy import (
    String, DateTime, Float, func, Integer, Enum, ForeignKey)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from app.database import Base 
from .Veiculos import StatusLocacao 

if TYPE_CHECKING:
    from .Cliente import Cliente
    from .Veiculos import Veiculo

class Reserva(Base):
    __tablename__ = "reservas"
    
    res_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    
    # Chaves estrangeiras
    res_vei_id: Mapped[str] = mapped_column(
        ForeignKey("veiculos.id"), nullable=False, index=True
    )
    res_cli_id: Mapped[str] = mapped_column(
        ForeignKey("clientes.cli_id"), nullable=False, index=True
    )
    
    # Campos da reserva/locação
    res_data_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    res_data_fim: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    
    res_status: Mapped[StatusLocacao] = mapped_column(
        Enum(StatusLocacao), default=StatusLocacao.RESERVADA
    )
    res_total: Mapped[float | None] = mapped_column(Float, nullable=True)

    data_devolucao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relacionamentos (usando string literals para evitar circular imports)
    veiculo: Mapped["Veiculo"] = relationship("Veiculo", back_populates="reservas")
    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="reservas")
    
    def __repr__(self):
        return f"<Reserva(res_id={self.res_id}, res_status={self.res_status})>"