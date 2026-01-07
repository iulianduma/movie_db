FROM python:3.11-slim

WORKDIR /app

# Instalăm dependențele de sistem necesare
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Copiem fișierul de cerințe
COPY requirements.txt .

# Forțăm instalarea celei mai noi versiuni de Reflex
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade reflex requests sqlmodel

# Copiem restul proiectului
COPY . .

# Expunem porturile
EXPOSE 3000 8000

# Pornim aplicația în mod producție/backend
CMD ["reflex", "run", "--env", "prod"]