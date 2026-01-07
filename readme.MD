# 🎬 MOVIE_DB - Discover & Manage

**MOVIE_DB** este o aplicație web Full-stack modernă dezvoltată integral în Python folosind framework-ul **Reflex**. Aplicația permite utilizatorilor să exploreze baza de date TMDB folosind filtre avansate și să își gestioneze listele personale de filme într-un mod eficient și persistent.

![Reflex](https://img.shields.io/badge/Framework-Reflex-red)
![Docker](https://img.shields.io/badge/Deployment-Docker-blue)
![Python](https://img.shields.io/badge/Language-Python%203.11-yellow)

## 🚀 Caracteristici Principale

* **Filtrare Granulară:** Căutare simultană după actori, intervale de ani, rating și certificări parentale.
* **Sistem de Studiouri:** Mapare inteligentă pentru studiouri majore (Hollywood), independente (A24, Neon) și europene/românești.
* **Management Watchlist:** Salvează filmele pe care vrei să le vezi sau marchează-le pe cele vizionate. Datele sunt persistente (stocare JSON).
* **Trailere Integrate:** Vizionează trailere YouTube direct în cardul filmului, fără redirecționare.
* **Performanță Optimizată:** Lazy loading pentru detaliile de producție și interfață asincronă pentru latență minimă.

## 🛠️ Arhitectura Tehnică

* **Frontend & Backend:** [Reflex](https://reflex.dev/) (Python-based framework care compilează la React/Next.js).
* **API:** Integrare cu [TMDB API](https://www.themoviedb.org/documentation/api) pentru date cinematografice în timp real.
* **Containere:** Docker & Docker Compose pentru consistența mediului de rulare.
* **Web Server:** Nginx Proxy Manager pentru Reverse Proxy și management SSL.

## 📦 Instalare și Rulare (Docker)

### Pre-cerințe
* Docker și Docker Compose instalate.
* O cheie API de la TMDB.

### Pasul 1: Clonarea proiectului
```bash
git clone [https://github.com/utilizator/movie_db.git](https://github.com/utilizator/movie_db.git)
cd movie_db
Pasul 2: Configurarea mediului
Creează un fișier .env în rădăcina proiectului:

Fragment de cod

TMDB_API_KEY=cheia_ta_api_aici
Modifică rxconfig.py pentru mediul tău:

Python

config = rx.Config(
    app_name="movie_db",
    api_url="http://adresa-ta-ip:9977",
)
Pasul 3: Pornirea aplicației
Bash

docker compose up -d --build
Aplicația va fi accesibilă la http://localhost:9988.

🔧 Detalii de Dezvoltare
Persistența datelor
Aplicația folosește volume Docker pentru a păstra listele de filme chiar și după restartarea containerului:

watched_list.json - ID-urile filmelor vizionate.

watchlist.json - ID-urile filmelor salvate pentru mai târziu.

Optimizări UI
on_blur Events: Input-urile de text trimit datele la server doar la pierderea focusului pentru a evita blocajele cauzate de latența rețelei.

State Management: Utilizarea variabilelor de stare Reflex pentru actualizarea instantanee a interfeței prin WebSockets.

🤝 Contribuții
Contribuțiile sunt binevenite! Simte-te liber să deschizi un Issue sau să trimiți un Pull Request.

10 Răspunsuri Tehnice pentru un Auditor
De ce JSON și nu SQL? Pentru prototipare rapidă, dar recunoaștem limitarea la scrieri concurente.

Cum protejați API-ul de abuz? Momentan prin obscuritate, dar planul e un rate-limiter în Nginx.

Ce se întâmplă dacă pică internetul pe server? Aplicația va rula, dar rezultatele căutărilor vor fi vide.

Cum gestionați imaginile sparte? Avem un placeholder implicit în rx.image.

De ce Docker și nu direct pe host? Izolarea versiunilor de Node/Python este critică pentru Reflex.

Cât de sigur este auto_deploy.sh? Este un risc de securitate dacă nu este protejat prin chei SSH criptate.

Ce versiune de React folosește în spate? Reflex folosește React 18/19 via Next.js.

Cum optimizați SEO? Folosim SitemapPlugin din rxconfig.py.

Care e consumul de memorie? ~300MB la idle, dar sare la 1GB în timpul compilării.

Este aplicația PWA? Nu încă, dar poate fi configurată prin manifest-ul de frontend.

Dezvoltat de Iulian Duma


---
