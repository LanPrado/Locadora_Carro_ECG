import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models.models import Veiculo, CategoriaVeiculo, StatusVeiculo

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
                "placa": "ECO1234",
                "modelo": "Onix",
                "marca": "Chevrolet",
                "ano": 2023,
                "categoria": CategoriaVeiculo.ECONOMICO,
                "diaria": 89.90,
                "quilometragem": 15000,
                "status": StatusVeiculo.DISPONIVEL,
                "imagem_url": "https://example.com/onix.jpg",
                "descricao": "Carro econômico, ideal para cidade. Baixo consumo de combustível."
            },
            {
                "placa": "ECO5678",
                "modelo": "Gol",
                "marca": "Volkswagen", 
                "ano": 2024,
                "categoria": CategoriaVeiculo.ECONOMICO,
                "diaria": 79.90,
                "quilometragem": 5000,
                "status": StatusVeiculo.DISPONIVEL,
                "imagem_url": "https://example.com/gol.jpg",
                "descricao": "Clássico brasileiro, manutenção acessível e econômico."
            },
            {
                "placa": "ECO9012",
                "modelo": "HB20",
                "marca": "Hyundai",
                "ano": 2023,
                "categoria": CategoriaVeiculo.ECONOMICO,
                "diaria": 95.00,
                "quilometragem": 12000,
                "status": StatusVeiculo.MANUTENCAO,
                "imagem_url": "https://example.com/hb20.jpg",
                "descricao": "Design moderno e tecnologia. Excelente custo-benefício."
            },
            
            # 🟡 CATEGORIA INTERMEDIÁRIO (3 veículos)
            {
                "placa": "INT3456",
                "modelo": "Corolla",
                "marca": "Toyota",
                "ano": 2024,
                "categoria": CategoriaVeiculo.INTERMEDIARIO,
                "diaria": 159.90,
                "quilometragem": 8000,
                "status": StatusVeiculo.DISPONIVEL,
                "imagem_url": "https://example.com/corolla.jpg",
                "descricao": "Conforto e confiabilidade. Ideal para viagens longas."
            },
            {
                "placa": "INT7890",
                "modelo": "Civic",
                "marca": "Honda",
                "ano": 2023,
                "categoria": CategoriaVeiculo.INTERMEDIARIO,
                "diaria": 169.90,
                "quilometragem": 20000,
                "status": StatusVeiculo.LOCADO,
                "imagem_url": "https://example.com/civic.jpg",
                "descricao": "Esportivo e elegante. Performance e conforto combinados."
            },
            {
                "placa": "INT2345",
                "modelo": "Sentra",
                "marca": "Nissan",
                "ano": 2024,
                "categoria": CategoriaVeiculo.INTERMEDIARIO,
                "diaria": 149.90,
                "quilometragem": 3000,
                "status": StatusVeiculo.DISPONIVEL,
                "imagem_url": "https://example.com/sentra.jpg",
                "descricao": "Conforto premium e tecnologia avançada."
            },
            
            # 🔵 CATEGORIA SUV (3 veículos)
            {
                "placa": "SUV6789",
                "modelo": "CR-V",
                "marca": "Honda",
                "ano": 2024,
                "categoria": CategoriaVeiculo.SUV,
                "diaria": 229.90,
                "quilometragem": 5000,
                "status": StatusVeiculo.DISPONIVEL,
                "imagem_url": "https://example.com/crv.jpg",
                "descricao": "SUV espaçoso e confortável. Perfeito para família."
            },
            {
                "placa": "SUV1235",
                "modelo": "Tiguan",
                "marca": "Volkswagen",
                "ano": 2023,
                "categoria": CategoriaVeiculo.SUV,
                "diaria": 219.90,
                "quilometragem": 18000,
                "status": StatusVeiculo.DISPONIVEL,
                "imagem_url": "https://example.com/tiguan.jpg",
                "descricao": "SUV alemão com acabamento premium e tecnologia."
            },
            {
                "placa": "SUV4678",
                "modelo": "RAV4",
                "marca": "Toyota",
                "ano": 2024,
                "categoria": CategoriaVeiculo.SUV,
                "diaria": 239.90,
                "quilometragem": 2000,
                "status": StatusVeiculo.MANUTENCAO,
                "imagem_url": "https://example.com/rav4.jpg",
                "descricao": "SUV híbrido econômico e espaçoso. Ideal para aventuras."
            },
            
            # 🔴 CATEGORIA LUXO (3 veículos)
            {
                "placa": "LUX9999",
                "modelo": "BMW Série 3",
                "marca": "BMW",
                "ano": 2024,
                "categoria": CategoriaVeiculo.LUXO,
                "diaria": 399.90,
                "quilometragem": 1000,
                "status": StatusVeiculo.DISPONIVEL,
                "imagem_url": "https://example.com/bmw3.jpg",
                "descricao": "Esportividade e luxo alemão. Performance incomparável."
            },
            {
                "placa": "LUX8888",
                "modelo": "Mercedes Classe C",
                "marca": "Mercedes-Benz",
                "ano": 2024,
                "categoria": CategoriaVeiculo.LUXO,
                "diaria": 429.90,
                "quilometragem": 1500,
                "status": StatusVeiculo.LOCADO,
                "imagem_url": "https://example.com/mercedesc.jpg",
                "descricao": "Conforto e elegância premium. Tecnologia de ponta."
            },
            {
                "placa": "LUX7777",
                "modelo": "Audi A4",
                "marca": "Audi",
                "ano": 2023,
                "categoria": CategoriaVeiculo.LUXO,
                "diaria": 389.90,
                "quilometragem": 12000,
                "status": StatusVeiculo.DISPONIVEL,
                "imagem_url": "https://example.com/audia4.jpg",
                "descricao": "Design sofisticado e tecnologia Quattro. Experiência única."
            }
        ]
        
        # Inserir veículos no banco
        for vehicle_data in vehicles_data:
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