from sqlalchemy import (
    String, DateTime, Float, func, Integer, Enum, ForeignKey)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from models import Veiculo, Cliente
from app.database import Base 
from .Veiculos import StatusLocacao

class Reserva(Base):
    __tablename__ = "reservas"
    
    res_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    
    # Chaves estrangeiras
    res_vei_id: Mapped[str] = mapped_column(
        ForeignKey("veiculos.id"), nullable=False, index=True # CORREÇÃO: Aponta para veiculos.id
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

    # --- ADIÇÃO: Campos que faltavam mas eram usados no router ---
    data_devolucao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    quilometragem_inicial: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quilometragem_final: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Relacionamentos
    veiculo: Mapped["Veiculo"] = relationship(back_populates="reservas")
    cliente: Mapped["Cliente"] = relationship(back_populates="reservas")
    
    def __repr__(self):
        return f"<Reserva(res_id={self.res_id}, res_status={self.res_status})>"