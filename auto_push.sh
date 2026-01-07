#!/bin/bash

# Navigăm în folderul proiectului
cd ~/movie_db

# Actualizăm informațiile de pe GitHub pentru a preveni erori de sincronizare
git fetch origin main

# 1. Verificăm dacă există modificări locale pe server
if [ -n "$(git status --porcelain)" ]; then
    echo " [$(date)] Modificări detectate pe server. Se inițiază backup-ul..."

    # Adăugăm fișierele (folosim git add -A pentru a include ștergerile și fișierele noi)
    git add -A

    # Creăm commit-ul cu timestamp
    git commit -m "Auto-update server: $(date +'%Y-%m-%d %H:%M:%S')"

    # Trimitem către GitHub
    # Folosim --quiet pentru a nu polua log-urile dacă totul e ok
    if git push origin main --quiet; then
        echo " [$(date)] Succes: Modificările sunt acum pe GitHub."
    else
        echo " [$(date)] EROARE: Nu s-a putut face push. Verifică conexiunea sau token-ul."
    fi
else
    echo " [$(date)] Status: Serverul este sincronizat cu GitHub. Nicio modificare detectată."
fi