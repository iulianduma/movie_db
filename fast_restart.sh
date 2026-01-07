#!/bin/bash

# Culori pentru status
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${CYAN}# 1. Oprire rapidă containere...${NC}"
docker compose stop

echo -e "${CYAN}# 2. Curățare cache frontend (fără ștergere DB)...${NC}"
# Ștergem doar folderul de compilare pentru a forța refresh-ul UI
sudo rm -rf .web
find . -type d -name "__pycache__" -exec rm -rf {} +

echo -e "${CYAN}# 3. Pornire servicii...${NC}"
docker compose up -d

echo -e "${CYAN}# 4. Verificare rapidă migrări...${NC}"
# Rulăm migrările doar dacă sunt modificări noi în modele
docker exec movie_db_container reflex db migrate 2>/dev/null

echo -e "${GREEN}# 5. Aplicația repornită! Afișez logurile (Ctrl+C pentru a ieși din loguri):${NC}"
echo -e "${YELLOW}--- LOGURI BACKEND ---${NC}"
docker logs -f --tail 20 movie_db_container
