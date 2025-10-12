import os
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def wait_for_postgres():
    """Aguarda o PostgreSQL ficar disponível"""
    db_url = os.getenv('DATABASE_URL')
    
    print("🕒 Aguardando PostgreSQL ficar disponível...")
    
    for i in range(30):  # Tentar por 30 segundos
        try:
            conn = psycopg2.connect(db_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            conn.close()
            print("✅ PostgreSQL está disponível!")
            return True
        except Exception as e:
            print(f"⏳ Tentativa {i+1}/30 - PostgreSQL ainda não está pronto...")
            time.sleep(1)
    
    print("❌ Timeout: PostgreSQL não ficou disponível em 30 segundos")
    return False

if __name__ == "__main__":
    wait_for_postgres()