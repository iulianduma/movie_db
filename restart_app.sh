#!/bin/bash

# Culori pentru vizibilitate
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}# 1. Oprire containere și eliminare orfani...${NC}"
# --remove-orphans șterge containerele vechi care nu mai sunt în docker-compose.yml
docker compose down --remove-orphans

echo -e "${GREEN}# 2. Curățare reziduuri Docker...${NC}"
# Șterge imagini, rețele și cache-uri de build care nu mai sunt folosite
docker system prune -f

echo -e "${GREEN}# 3. Curățare cache Reflex și Python...${NC}"
sudo rm -rf .web
find . -type d -name "__pycache__" -exec rm -rf {} +

echo -e "${GREEN}# 4. Reconstrucție și pornire containere...${NC}"
docker compose up -d --build

echo -e "${GREEN}# 5. Așteptare inițializare (7 secunde)...${NC}"
sleep 7

echo -e "${GREEN}# 6. Aplicare migrări bază de date...${NC}"
# Folosim -i pentru interactivitate minimă în script
docker exec movie_db_container reflex db makemigrations
docker exec movie_db_container reflex db migrate

echo -e "${GREEN}# 7. Status final...${NC}"
docker ps

echo -e "${GREEN}# Aplicația a fost resetată complet și orfanii au fost eliminați.${NC}"