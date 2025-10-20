import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models.models import Veiculo, CategoriaVeiculo, StatusVeiculo
from app.models.Cliente import Cliente 
from app.models.Reservar import Reserva 

def populate_vehicles():
    db = SessionLocal()
    
    try:
        # Verificar se já existem veículos
        existing_vehicles = db.query(Veiculo).count()
        if existing_vehicles > 0:
            print("⚠️  Já existem veículos no banco. Pulando população...")
            return
        
        vehicles_data = [
            # 🟢 CATEGORIA ECONÔMICO (3 veículos)
            {
                "placa": "ECO1234", "modelo": "Onix", "marca": "Chevrolet", "ano": 2023,
                "categoria": CategoriaVeiculo.ECONOMICO, "diaria": 89.90, "status": StatusVeiculo.DISPONIVEL,
                "descricao": "Carro econômico, ideal para cidade. Baixo consumo de combustível."
            },
            {
                "placa": "ECO5678", "modelo": "Gol", "marca": "Volkswagen", "ano": 2024,
                "categoria": CategoriaVeiculo.ECONOMICO, "diaria": 79.90, "status": StatusVeiculo.DISPONIVEL,
                "descricao": "Clássico brasileiro, manutenção acessível e econômico."
            },
            {
                "placa": "ECO9012", "modelo": "HB20", "marca": "Hyundai", "ano": 2023,
                "categoria": CategoriaVeiculo.ECONOMICO, "diaria": 95.00, "status": StatusVeiculo.MANUTENCAO,
                "descricao": "Design moderno e tecnologia. Excelente custo-benefício."
            },
            
            # 🟡 CATEGORIA INTERMEDIÁRIO (3 veículos)
            {
                "placa": "INT3456", "modelo": "Corolla", "marca": "Toyota", "ano": 2024,
                "categoria": CategoriaVeiculo.INTERMEDIARIO, "diaria": 159.90, "status": StatusVeiculo.DISPONIVEL,
                "descricao": "Conforto e confiabilidade. Ideal para viagens longas."
            },
            {
                "placa": "INT7890", "modelo": "Civic", "marca": "Honda", "ano": 2023,
                "categoria": CategoriaVeiculo.INTERMEDIARIO, "diaria": 169.90, "status": StatusVeiculo.LOCADO,
                "descricao": "Esportivo e elegante. Performance e conforto combinados."
            },
            {
                "placa": "INT2345", "modelo": "Sentra", "marca": "Nissan", "ano": 2024,
                "categoria": CategoriaVeiculo.INTERMEDIARIO, "diaria": 149.90, "status": StatusVeiculo.DISPONIVEL,
                "descricao": "Conforto premium e tecnologia avançada."
            },
            
            # 🔵 CATEGORIA SUV (3 veículos)
            {
                "placa": "SUV6789", "modelo": "CR-V", "marca": "Honda", "ano": 2024,
                "categoria": CategoriaVeiculo.SUV, "diaria": 229.90, "status": StatusVeiculo.DISPONIVEL,
                "descricao": "SUV espaçoso e confortável. Perfeito para família."
            },
            {
                "placa": "SUV1235", "modelo": "Tiguan", "marca": "Volkswagen", "ano": 2023,
                "categoria": CategoriaVeiculo.SUV, "diaria": 219.90, "status": StatusVeiculo.DISPONIVEL,
                "descricao": "SUV alemão com acabamento premium e tecnologia."
            },
            {
                "placa": "SUV4678", "modelo": "RAV4", "marca": "Toyota", "ano": 2024,
                "categoria": CategoriaVeiculo.SUV, "diaria": 239.90, "status": StatusVeiculo.MANUTENCAO,
                "descricao": "SUV híbrido econômico e espaçoso. Ideal para aventuras."
            },
            
            # 🔴 CATEGORIA LUXO (3 veículos)
            {
                "placa": "LUX9999", "modelo": "BMW Série 3", "marca": "BMW", "ano": 2024,
                "categoria": CategoriaVeiculo.LUXO, "diaria": 399.90, "status": StatusVeiculo.DISPONIVEL,
                "descricao": "Esportividade e luxo alemão. Performance incomparável."
            },
            {
                "placa": "LUX8888", "modelo": "Mercedes Classe C", "marca": "Mercedes-Benz", "ano": 2024,
                "categoria": CategoriaVeiculo.LUXO, "diaria": 429.90, "status": StatusVeiculo.LOCADO,
                "descricao": "Conforto e elegância premium. Tecnologia de ponta."
            },
            {
                "placa": "LUX7777", "modelo": "Audi A4", "marca": "Audi", "ano": 2023,
                "categoria": CategoriaVeiculo.LUXO, "diaria": 389.90, "status": StatusVeiculo.DISPONIVEL,
                "descricao": "Design sofisticado e tecnologia Quattro. Experiência única."
            }
        ]
        
        # Inserir veículos no banco
        for vehicle_data in vehicles_data:
            # O **vehicle_data já corresponde aos campos do modelo
            vehicle = Veiculo(**vehicle_data)
            db.add(vehicle)
        
        db.commit()
        print("✅ 12 veículos inseridos com sucesso!")
        print("📊 Distribuição por categoria:")
        print("   🟢 Econômico: 3 veículos")
        print("   🟡 Intermediário: 3 veículos") 
        print("   🔵 SUV: 3 veículos")
        print("   🔴 Luxo: 3 veículos")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao popular veículos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_vehicles()

