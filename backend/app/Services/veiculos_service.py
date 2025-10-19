from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import VeiculoCreate, Veiculo
from app.models.models import VeiculoCreate, VeiculoUpdate, VeiculoResponse, VeiculoListResponse

class VeiculoService:
    def __init__(self, db: Session):
        self.db = db
    
    def criar_veiculo(self, veiculo_data: VeiculoCreate) -> VeiculoResponse:
        """201 Created: O dado foi criado com sucesso"""
        # Verificar se placa já existe
        veiculo_existente = self.db.query(Veiculo).filter(
            Veiculo.placa == veiculo_data.placa.upper()
        ).first()
        
        if veiculo_existente:
            raise ValueError("Já existe um veículo com esta placa")
        
        # Verificar se descrição já existe (se fornecida)
        if veiculo_data.descricao:
            descricao_existente = self.db.query(Veiculo).filter(
                Veiculo.descricao == veiculo_data.descricao
            ).first()
            if descricao_existente:
                raise ValueError("Já existe um veículo com esta descrição")
        
        db_veiculo = Veiculo(**veiculo_data.model_dump())
        self.db.add(db_veiculo)
        self.db.commit()
        self.db.refresh(db_veiculo)
        
        return VeiculoResponse.model_validate(db_veiculo)
    
    def buscar_veiculo_por_id(self, veiculo_id: int) -> Optional[VeiculoResponse]:  # ✅ Agora é int
        """200 OK: Deu tudo certo | 404 Not Found: Recurso não encontrado"""
        db_veiculo = self.db.query(Veiculo).filter(Veiculo.vei_id == veiculo_id).first()
        
        if not db_veiculo:
            return None
        
        return VeiculoResponse.model_validate(db_veiculo)
    
    def buscar_veiculo_por_placa(self, placa: str) -> Optional[VeiculoResponse]:
        """200 OK: Deu tudo certo | 404 Not Found: Recurso não encontrado"""
        db_veiculo = self.db.query(Veiculo).filter(
            Veiculo.placa == placa.upper()
        ).first()
        
        if not db_veiculo:
            return None
        
        return VeiculoResponse.model_validate(db_veiculo)
    
    def listar_veiculos(self, skip: int = 0, limit: int = 100) -> VeiculoListResponse:
        """200 OK: Deu tudo certo"""
        veiculos = self.db.query(Veiculo).offset(skip).limit(limit).all()
        total = self.db.query(Veiculo).count()
        
        return VeiculoListResponse(
            veiculos=[VeiculoResponse.model_validate(v) for v in veiculos],
            total=total,
            pagina=(skip // limit) + 1,
            por_pagina=limit
        )
    
    def listar_veiculos_ativos(self, skip: int = 0, limit: int = 100) -> VeiculoListResponse:
        """200 OK: Deu tudo certo"""
        veiculos = self.db.query(Veiculo).filter(
            Veiculo.ativo == True
        ).offset(skip).limit(limit).all()
        
        total_ativos = self.db.query(Veiculo).filter(
            Veiculo.ativo == True
        ).count()
        
        return VeiculoListResponse(
            veiculos=[VeiculoResponse.model_validate(v) for v in veiculos],
            total=total_ativos,
            pagina=(skip // limit) + 1,
            por_pagina=limit
        )
    
    def listar_veiculos_por_cliente(self, cli_id: str, skip: int = 0, limit: int = 100) -> VeiculoListResponse:
        """200 OK: Deu tudo certo"""
        veiculos = self.db.query(Veiculo).filter(
            Veiculo.cli_id == cli_id
        ).offset(skip).limit(limit).all()
        
        total_cliente = self.db.query(Veiculo).filter(
            Veiculo.cli_id == cli_id
        ).count()
        
        return VeiculoListResponse(
            veiculos=[VeiculoResponse.model_validate(v) for v in veiculos],
            total=total_cliente,
            pagina=(skip // limit) + 1,
            por_pagina=limit
        )
    
    def atualizar_veiculo(self, veiculo_id: int, veiculo_update: VeiculoUpdate) -> Optional[VeiculoResponse]:  # ✅ Agora é int
        """200 OK: Deu tudo certo | 404 Not Found: Recurso não encontrado"""
        db_veiculo = self.db.query(Veiculo).filter(Veiculo.vei_id == veiculo_id).first()
        
        if not db_veiculo:
            return None
        
        # Verificar conflito de placa se estiver sendo atualizada
        if veiculo_update.placa:
            veiculo_com_placa = self.db.query(Veiculo).filter(
                Veiculo.placa == veiculo_update.placa.upper(),
                Veiculo.vei_id != veiculo_id
            ).first()
            
            if veiculo_com_placa:
                raise ValueError("Já existe outro veículo com esta placa")
        
        # Verificar conflito de descrição se estiver sendo atualizada
        if veiculo_update.descricao:
            veiculo_com_descricao = self.db.query(Veiculo).filter(
                Veiculo.descricao == veiculo_update.descricao,
                Veiculo.vei_id != veiculo_id
            ).first()
            
            if veiculo_com_descricao:
                raise ValueError("Já existe outro veículo com esta descrição")
        
        update_data = veiculo_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_veiculo, field, value)
        
        self.db.commit()
        self.db.refresh(db_veiculo)
        
        return VeiculoResponse.model_validate(db_veiculo)
    
    def deletar_veiculo(self, veiculo_id: int) -> bool:  # ✅ Agora é int
        """204 No Content: Deletado com sucesso | 404 Not Found: Recurso não encontrado"""
        db_veiculo = self.db.query(Veiculo).filter(Veiculo.vei_id == veiculo_id).first()
        
        if not db_veiculo:
            return False
        
        self.db.delete(db_veiculo)
        self.db.commit()
        return True
    
    def desativar_veiculo(self, veiculo_id: int) -> Optional[VeiculoResponse]:  # ✅ Agora é int
        """200 OK: Deu tudo certo | 404 Not Found: Recurso não encontrado"""
        db_veiculo = self.db.query(Veiculo).filter(Veiculo.vei_id == veiculo_id).first()
        
        if not db_veiculo:
            return None
        
        db_veiculo.ativo = False
        self.db.commit()
        self.db.refresh(db_veiculo)
        
        return VeiculoResponse.model_validate(db_veiculo)