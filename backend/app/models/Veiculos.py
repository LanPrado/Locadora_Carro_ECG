import uuid
import enum

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