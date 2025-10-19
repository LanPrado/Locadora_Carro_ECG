from sqlalchemy import String, Boolean, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid

from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    
    # Constraints únicos definidos em __table_args__, como no exemplo
    __table_args__ = (
        UniqueConstraint("cli_email", name="uq_clientes_email"),
        UniqueConstraint("cli_cpf", name="uq_clientes_cpf"),
    )
    
    # Colunas atualizadas para o padrão Mapped/mapped_column
    cli_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    cli_email: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False
    )
    cli_nome: Mapped[str] = mapped_column(String(100), nullable=False)
    cli_senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Use 'Mapped[str | None]' para colunas que podem ser nulas
    cli_telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cli_cpf: Mapped[str | None] = mapped_column(String(11), index=True, nullable=True)
    
    # Colunas de controle
    cli_ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Usando server_default=func.now() como no exemplo (boa prática)
    cli_criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamento atualizado
    reservas: Mapped[list["Reserva"]] = relationship(back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(cli_id={self.cli_id}, cli_email={self.cli_email})>"