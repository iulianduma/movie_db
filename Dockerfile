# Folosim o imagine de Python stabilă
FROM python:3.11-slim

# Instalăm dependențele de sistem necesare pentru Node.js (necesar pentru Reflex)
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Setăm directorul de lucru
WORKDIR /app

# Copiem fișierele de dependențe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiem restul codului (inclusiv .env dacă vrei să fie în container)
COPY . .

# Inițializăm reflex (compilarea inițială)
RUN reflex init

# Expunem porturile: 3000 (Frontend) și 8000 (Backend)
EXPOSE 3000 8000

# Comanda de start pentru producție
CMD ["reflex", "run", "--env", "prod", "--frontend-port", "3000", "--backend-port", "8000"]