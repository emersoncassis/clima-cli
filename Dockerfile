# Usando uma imagem oficial do Python bem leve (slim)
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Variáveis de ambiente para otimizar o Python no Docker:
# PYTHONDONTWRITEBYTECODE=1 evita a criação de arquivos .pyc no container
# PYTHONUNBUFFERED=1 garante que os logs e outputs apareçam no console em tempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copia apenas o requirements.txt primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .

# Instala as dependências de produção
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Define o Entrypoint para que o container se comporte diretamente como a CLI do clima
# Permitindo rodar: docker run <imagem> "São Paulo"
ENTRYPOINT ["python", "main.py"]
