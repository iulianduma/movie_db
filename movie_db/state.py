import reflex as rx
import requests
import time
import os
from .models import MovieEntry
from sqlmodel import select

class BaseState(rx.State):
    """Starea părinte care inițializează cheia API."""
    @rx.var
    def tmdb_key(self) -> str:
        return os.environ.get("TMDB_API_KEY", "")

class UserState(BaseState):
    """Sub-stare pentru Securitate."""
    is_logged_in: bool = False
    username: str = ""
    password: str = ""

    def login(self):
        if self.username == "admin" and self.password == "1234": # Schimbă parola aici
            self.is_logged_in = True
            return rx.redirect("/")
        return rx.window_alert("Date incorecte!")

class MovieState(BaseState):
    """Sub-stare pentru Date și Caching."""
    movies: list[dict] = []
    _cache: dict = {}
    
    def fetch_movies(self, params: dict):
        if not self.tmdb_key:
            print("EROARE: Cheia API lipsește din .env")
            return

        cache_key = str(params)
        # Logica de Caching (1 oră)
        if cache_key in self._cache:
            if time.time() - self._cache[cache_key]['time'] < 3600:
                self.movies = self._cache[cache_key]['data']
                return

        params["api_key"] = self.tmdb_key
        resp = requests.get("https://api.themoviedb.org/3/discover/movie", params=params)
        
        if resp.status_code == 200:
            data = resp.json().get("results", [])
            self.movies = data
            self._cache[cache_key] = {'time': time.time(), 'data': data}

    def toggle_movie(self, movie: dict, list_type: str):
        """Salvare în SQLite în loc de JSON."""
        with rx.session() as session:
            existing = session.exec(
                select(MovieEntry).where(
                    (MovieEntry.tmdb_id == movie["id"]) & 
                    (MovieEntry.list_type == list_type)
                )
            ).first()
            
            if existing:
                session.delete(existing)
            else:
                session.add(MovieEntry(
                    tmdb_id=movie["id"],
                    title=movie["title"],
                    poster_path=movie.get("poster_path", ""),
                    list_type=list_type
                ))
            session.commit()