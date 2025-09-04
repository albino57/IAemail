# Usa uma imagem Python oficial e leve como base
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do seu código para o diretório de trabalho
COPY . .

# Expõe a porta que a aplicação vai usar
EXPOSE 7860

# O COMANDO FINAL: Diz ao container para iniciar usando Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:7860"]