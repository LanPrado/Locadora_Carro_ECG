from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from typing import TYPE_CHECKING, Optional

from app.database import Base

if TYPE_CHECKING:
    from .Reservar import Reserva

class Cliente(Base):
    __tablename__ = "clientes"
    
    cli_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    cli_email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    cli_nome: Mapped[str] = mapped_column(String, nullable=False)
    cli_senha_hash: Mapped[str] = mapped_column(String, nullable=False)
    cli_telefone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cli_cpf: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cli_ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    cli_criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relacionamento com reservas
    reservas: Mapped[list["Reserva"]] = relationship("Reserva", back_populates="cliente")
    
    def __repr__(self):
        return f"<Cliente(cli_id={self.cli_id}, cli_email={self.cli_email})>"