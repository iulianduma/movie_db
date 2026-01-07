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
    is_loading: bool = False
    show_mode: str = "Discover"
    
    # --- FILTRE AVANSATE ---
    y_start: str = "1950"
    y_end: str = "2026"
    selected_genres: List[int] = []
    company_ids: List[str] = []
    sort_by: str = "vote_average.desc"
    content_type: str = "movie" # movie sau tv
    certification_country: str = "US"
    certification: str = "" # R, PG-13, etc.
    original_language: str = "" # ro, en, fr

    # --- DICȚIONARE EXTINSE ---
    GENRE_MAP: Dict[str, int] = {
        "Acțiune": 28, "Aventură": 12, "Dramă": 18, "Comedie": 35, "Horror": 27,
        "Thriller": 53, "SF": 878, "Fantasy": 14, "Mister": 9648, "Romantic": 10749,
        "Crime": 80, "Western": 37, "Război": 10752, "Istoric": 36, "Biografic": 1, # Biografic nu e gen nativ, e adesea sub-gen
        "Familie": 10751, "Muzical": 10402, "Sport": 10770, "Documentar": 99
    }

    STUDIO_MAP: Dict[str, str] = {
        "Disney": "2", "Warner Bros": "174", "Universal": "33", "Paramount": "4",
        "A24": "41077", "MGM": "21", "Lionsgate": "1632", "Gaumont": "9",
        "StudioCanal": "104", "Castel Film": "2784", "Mobra Films": "14382"
    }

    @rx.var
    def genre_names_list(self) -> List[str]:
        return list(self.GENRE_MAP.keys())

    @rx.var
    def studio_names_list(self) -> List[str]:
        return list(self.STUDIO_MAP.keys())

    def set_content_type(self, val): self.content_type = val
    def set_language(self, val): self.original_language = val
    def set_certification(self, val): self.certification = val

    async def fetch_movies(self):
        self.is_loading = True
        yield
        
        with rx.session() as session:
            res = session.exec(select(MovieEntry)).all()
            self.watched_ids = [str(m.tmdb_id) for m in res]

        base_url = f"https://api.themoviedb.org/3/discover/{self.content_type}"
        params = {
            "api_key": os.environ.get("TMDB_API_KEY"),
            "language": "ro-RO",
            "sort_by": self.sort_by,
            "vote_count.gte": 50,
            "primary_release_date.gte": f"{self.y_start}-01-01",
            "primary_release_date.lte": f"{self.y_end}-12-31",
            "with_genres": ",".join(map(str, self.selected_genres)) if self.selected_genres else None,
            "with_companies": "|".join(self.company_ids) if self.company_ids else None,
            "with_original_language": self.original_language if self.original_language else None,
        }
        
        if self.certification:
            params["certification_country"] = self.certification_country
            params["certification"] = self.certification

        try:
            r = requests.get(base_url, params=params).json()
            self.movies = []
            for m in r.get("results", []):
                m_id = str(m.get("id"))
                if m_id in self.watched_ids: continue
                path = m.get("poster_path")
                self.movies.append({
                    "id": m_id,
                    "title": m.get("title") if self.content_type == "movie" else m.get("name"),
                    "overview": m.get("overview", "")[:150] + "...",
                    "poster_path": f"https://image.tmdb.org/t/p/w500{path}" if path else "/no_image.png",
                    "vote_average": round(m.get("vote_average", 0), 1),
                    "yt_id": ""
                })
        except: self.movies = []
        self.is_loading = False