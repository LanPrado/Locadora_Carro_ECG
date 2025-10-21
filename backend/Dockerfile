FROM python:3.12

WORKDIR /app

# Copia e instala as dependências primeiro
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia TODO o conteúdo da pasta backend atual
COPY . .

# Comando padrão
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]