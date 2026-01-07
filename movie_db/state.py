import reflex as rx
import requests
import os
from .models import MovieEntry
from sqlmodel import select
from typing import List, Dict
from datetime import datetime

class MovieState(rx.State):
    movies: list[dict] = []
    watched_ids: list[str] = []
    watchlist_ids: list[str] = []
    is_loading: bool = False
    show_mode: str = "Discover"
    
    # --- NOILE VARIABILE PENTRU FILTRE ---
    # Slidere Duble (Range)
    year_range: List[int] = [1990, 2026]
    rate_range: List[float] = [5.0, 10.0]
    
    # Selecții
    selected_genres: List[int] = []
    company_ids: List[str] = []
    
    # Actori (Search & Tag)
    actor_input: str = ""
    selected_actors: List[str] = [] # Stocăm numele pentru UI, API-ul ar necesita ID-uri (logică avansată necesară)

    # Tip Conținut
    content_type: str = "movie" # 'movie' sau 'tv'

    # --- LISTE ȘI MAPĂRI ---
    # Genuri
    GENRE_MAP: Dict[str, int] = {
        "Acțiune": 28, "Aventură": 12, "Animație": 16, "Comedie": 35, "Crime": 80, 
        "Documentar": 99, "Dramă": 18, "Familie": 10751, "Fantasy": 14, "Istoric": 36, 
        "Horror": 27, "Muzical": 10402, "Mister": 9648, "Romantic": 10749, "SF": 878, 
        "Sport": 999, "Thriller": 53, "Război": 10752, "Western": 37
    }

    # Studiouri (Mapping Nume -> ID TMDB). 
    # Notă: ID-urile sunt fictive sau aproximative pentru demo. În producție, trebuie ID-urile exacte de la TMDB.
    STUDIO_MAP: Dict[str, str] = {
        # SUA
        "Warner Bros": "174", "Universal Pictures": "33", "Paramount": "4", "Disney": "2", 
        "20th Century Studios": "127928", "Columbia Pictures": "5", "Lionsgate": "1632", 
        "MGM": "8411", "Legendary": "923",
        # Independente
        "A24": "41077", "Blumhouse": "3172", "Neon": "93375", "Focus Features": "10146", 
        "Miramax": "14", "Annapurna": "10405", "IFC Films": "307",
        # Europa
        "StudioCanal": "183", "Pathé": "297", "BBC Films": "18", "Working Title": "10163", 
        "Gaumont": "9", "Constantin Film": "47", "Zentropa": "76", "Canal+": "5358",
        # România
        "Castel Film": "2784", "Libra Film": "13632", "Mandragora": "1678", 
        "HiFilm": "14457", "Mobra Films": "10842", "Parada Film": "19421", "Saga Film": "15324"
    }

    # Liste pentru UI (Doar cheile)
    @rx.var
    def genre_names(self) -> List[str]: return list(self.GENRE_MAP.keys())

    # Liste Grupate pentru Interfață
    studios_us: List[str] = ["Warner Bros", "Universal Pictures", "Paramount", "Disney", "20th Century Studios", "Columbia Pictures", "Lionsgate", "MGM", "Legendary"]
    studios_eu: List[str] = ["StudioCanal", "Pathé", "BBC Films", "Working Title", "Gaumont", "Constantin Film", "Zentropa", "Canal+"]
    studios_ro: List[str] = ["Castel Film", "Libra Film", "Mandragora", "HiFilm", "Mobra Films", "Parada Film", "Saga Film"]
    studios_indie: List[str] = ["Blumhouse", "Annapurna", "Neon", "Focus Features", "Miramax", "IFC Films", "A24"]

    # --- LOGICĂ SLIDERE & INPUTS ---
    def set_year_range(self, val: list): self.year_range = val
    def set_rate_range(self, val: list): self.rate_range = val
    def set_content_type(self, val: str): 
        self.content_type = val
        return MovieState.fetch_movies

    def set_actor_input(self, val: str): self.actor_input = val

    def add_actor(self):
        if self.actor_input and self.actor_input not in self.selected_actors:
            self.selected_actors.append(self.actor_input)
            self.actor_input = ""

    def remove_actor(self, val: str):
        if val in self.selected_actors:
            self.selected_actors.remove(val)

    def toggle_genre(self, name: str):
        gid = self.GENRE_MAP.get(name)
        if gid in self.selected_genres: self.selected_genres.remove(gid)
        else: self.selected_genres.append(gid)

    def toggle_studio(self, name: str):
        sid = self.STUDIO_MAP.get(name)
        if sid in self.company_ids: self.company_ids.remove(sid)
        else: self.company_ids.append(sid)

    # --- RESET TOTAL ---
    def reset_filters(self):
        self.year_range = [1950, 2026]
        self.rate_range = [0.0, 10.0]
        self.selected_genres = []
        self.company_ids = []
        self.selected_actors = []
        self.content_type = "movie"
        return MovieState.fetch_movies

    # --- FETCH MOVIES ---
    async def fetch_movies(self):
        self.is_loading = True
        
        # 1. Încarcă starea locală (Vizionat / De văzut)
        with rx.session() as session:
            res = session.exec(select(MovieEntry)).all()
            self.watched_ids = [str(m.tmdb_id) for m in res if m.list_type == "watched"]
            self.watchlist_ids = [str(m.tmdb_id) for m in res if m.list_type == "watchlist"]

        # 2. Modul Local (Watchlist/Watched)
        if self.show_mode.lower() in ["watchlist", "watched"]:
            target = self.show_mode.lower()
            with rx.session() as session:
                entries = session.exec(select(MovieEntry).where(MovieEntry.list_type == target)).all()
                raw = [{"id": str(m.tmdb_id), "title": m.title, "overview": m.overview, 
                        "poster_path": f"https://image.tmdb.org/t/p/w500{m.poster_path}", 
                        "vote_average": m.vote_average, "yt_id": ""} for m in entries]
            self.movies = raw
            self.is_loading = False
            return

        # 3. Modul Discover (API TMDB)
        params = {
            "api_key": os.environ.get("TMDB_API_KEY"),
            "language": "ro-RO", 
            "sort_by": "vote_average.desc", 
            "vote_count.gte": 50,
            # Noile filtre Range
            "vote_average.gte": self.rate_range[0], 
            "vote_average.lte": self.rate_range[1],
            "primary_release_date.gte": f"{self.year_range[0]}-01-01", 
            "primary_release_date.lte": f"{self.year_range[1]}-12-31",
            
            "with_genres": ",".join(map(str, self.selected_genres)) if self.selected_genres else None,
            "with_companies": "|".join(self.company_ids) if self.company_ids else None,
        }
        
        # Logica pentru Actori este complexă în API (necesită person_id). 
        # Pentru simplitate, aici o omitem din call-ul direct, dar UI-ul o pregătește.

        try:
            r = requests.get(f"https://api.themoviedb.org/3/discover/{self.content_type}", params=params).json()
            raw = []
            for m in r.get("results", []):
                m_id = str(m.get("id"))
                if m_id in self.watched_ids: continue
                path = m.get("poster_path")
                raw.append({
                    "id": m_id, 
                    "title": m.get("title") if self.content_type == "movie" else m.get("name"), 
                    "vote_average": round(m.get("vote_average", 0), 1), 
                    "poster_path": f"https://image.tmdb.org/t/p/w500{path}" if path else "/no_image.png", 
                    "overview": m.get("overview", "")[:200] + "...", 
                    "yt_id": ""
                })
            self.movies = raw
        except Exception:
            self.movies = []
            
        self.is_loading = False

    # Restul funcțiilor auxiliare rămân neschimbate
    def set_show_mode(self, mode): 
        self.show_mode = mode
        return MovieState.fetch_movies

    async def toggle_status(self, movie: dict, target_list: str):
        with rx.session() as session:
            m_id = int(movie["id"])
            existing = session.exec(select(MovieEntry).where(MovieEntry.tmdb_id == m_id)).first()
            if existing:
                if existing.list_type == target_list: session.delete(existing)
                else:
                    existing.list_type = target_list
                    existing.added_at = datetime.now()
            else:
                session.add(MovieEntry(tmdb_id=m_id, title=movie["title"], overview=movie["overview"], poster_path=movie["poster_path"].replace("https://image.tmdb.org/t/p/w500", ""), vote_average=movie["vote_average"], list_type=target_list, added_at=datetime.now()))
            session.commit()
        return MovieState.fetch_movies

    async def load_trailer(self, m_id: str):
        res = requests.get(f"https://api.themoviedb.org/3/{self.content_type}/{m_id}/videos", params={"api_key": os.environ.get("TMDB_API_KEY")}).json()
        key = next((v["key"] for v in res.get("results", []) if v["site"] == "YouTube"), "none")
        for m in self.movies:
            if m["id"] == m_id: m["yt_id"] = key; break
        self.movies = list(self.movies)

    def close_trailer(self, m_id: str):
        for m in self.movies:
            if m["id"] == m_id: m["yt_id"] = ""; break
        self.movies = list(self.movies)