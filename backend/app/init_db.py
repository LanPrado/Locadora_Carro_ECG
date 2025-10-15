import os
import sys
sys.path.append('/app')

from sqlalchemy import create_engine
from backend.app.models.models import Base

# Adicionar o caminho para encontrar o database.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import SQLALCHEMY_DATABASE_URL

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    db_url = SQLALCHEMY_DATABASE_URL
    print(f"🔧 Conectando ao banco de dados: {db_url.split('@')[1] if '@' in db_url else db_url}")
    
    try:
        engine = create_engine(db_url)
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        
        # Fechar conexão
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

if __name__ == "__main__":
    init_database()