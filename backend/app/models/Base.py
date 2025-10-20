from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Enum as SQLEnum,
    Boolean, UniqueConstraint, func, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base
from datetime import datetime
import uuid

from .Veiculos import CategoriaVeiculo, StatusVeiculo, StatusLocacao

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
    descricao = Column(String(255), nullable=True)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # O relacionamento agora pode referenciar a classe diretamente
    reservas = relationship("Reserva", back_populates="veiculo")

# --- Modelo Cliente ---
class Cliente(Base):
    __tablename__ = "clientes"
    
    __table_args__ = (
        UniqueConstraint("cli_email", name="uq_clientes_email"),
        UniqueConstraint("cli_cpf", name="uq_clientes_cpf"),
    )
    
    cli_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cli_email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    cli_nome: Mapped[str] = mapped_column(String(100), nullable=False)
    cli_senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    cli_telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cli_cpf: Mapped[str | None] = mapped_column(String(11), index=True, nullable=True)
    cli_ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    cli_criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    reservas: Mapped[list["Reserva"]] = relationship(back_populates="cliente")

# --- Modelo Reserva ---
class Reserva(Base):
    __tablename__ = "reservas"
    
    res_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    res_vei_id: Mapped[str] = mapped_column(ForeignKey("veiculos.id"), nullable=False, index=True)
    res_cli_id: Mapped[str] = mapped_column(ForeignKey("clientes.cli_id"), nullable=False, index=True)
    res_data_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    res_data_fim: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    res_status: Mapped[StatusLocacao] = mapped_column(SQLEnum(StatusLocacao), default=StatusLocacao.RESERVADA)
    res_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_devolucao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    veiculo: Mapped["Veiculo"] = relationship(back_populates="reservas")
    cliente: Mapped["Cliente"] = relationship(back_populates="reservas")

# --- Modelo Admin ---
class Admin(Base):
    __tablename__ = "admins"
    
    adm_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo_admin = Column(String(9), unique=True, index=True, nullable=False)
    adm_nome = Column(String(100), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    nivel_acesso = Column(String(20), nullable=False, default="operador")
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    ultimo_login = Column(DateTime, nullable=True)
    
    __table_args__ = (
        CheckConstraint("codigo_admin ~ '^ADM\\d{6}$'", name="ck_admin_codigo_formato"),
    )
