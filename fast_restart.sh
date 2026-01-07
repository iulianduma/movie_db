#!/bin/bash

# Culori pentru vizibilitate
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}# 1. Oprire rapidă containere...${NC}"
docker compose stop

echo -e "${CYAN}# 2. Curățare cache (.web & pycache)...${NC}"
sudo rm -rf .web
find . -type d -name "__pycache__" -exec rm -rf {} +

echo -e "${CYAN}# 3. Pornire servicii...${NC}"
docker compose up -d

echo -e "${CYAN}# 4. Sincronizare automată bază de date...${NC}"
# Încercăm o migrare rapidă în caz că ai schimbat modelele
docker exec movie_db_container reflex db migrate 2>/dev/null

echo -e "${GREEN}# 5. Restart complet!${NC}"
echo -e "${YELLOW}--- ULTIMELE 30 LINII DIN LOGURI ---${NC}"
# Afișează ultimele 30 de linii și închide fluxul (fără -f)
docker logs --tail 50 movie_db_container

echo -e "${CYAN}------------------------------------${NC}"
echo -e "${GREEN}Verifică dacă apare eroarea de 'TypeError' sau 'weight' în liniile de mai sus.${NC}"