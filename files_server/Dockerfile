FROM python:3.11-slim

WORKDIR /app

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto (incluindo as pastas formatter/)
COPY . .

# Comando padrão
CMD ["python", "main.py"]