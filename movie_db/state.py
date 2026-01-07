import reflex as rx
import requests
import time
import os
from .models import MovieEntry
from sqlmodel import select

class BaseState(rx.State):
    """Starea de bază care încarcă cheia din .env."""
    @rx.var
    def api_key(self) -> str:
        return os.environ.get("TMDB_API_KEY", "")

class UserState(BaseState):
    """Gestionează Login-ul."""
    is_logged_in: bool = False
    username: str = ""
    password: str = ""

    def login(self):
        # Aici poți pune orice parolă dorești
        if self.username == "admin" and self.password == "1234":
            self.is_logged_in = True
            return rx.redirect("/")
        return rx.window_alert("Credentiale invalide!")

    def logout(self):
        self.is_logged_in = False
        return rx.redirect("/")

class MovieState(BaseState):
    """Gestionează datele de la TMDB și Caching-ul."""
    movies: list[dict] = []
    _cache: dict = {}

    def fetch_movies(self, params: dict):
        if not self.api_key:
            return
        
        # Generăm o cheie de cache bazată pe parametrii de căutare
        cache_key = str(params)
        now = time.time()

        if cache_key in self._cache:
            if now - self._cache[cache_key]['time'] < 3600: # 1 oră
                self.movies = self._cache[cache_key]['data']
                return

        params["api_key"] = self.api_key
        resp = requests.get("https://api.themoviedb.org/3/discover/movie", params=params)
        if resp.status_code == 200:
            data = resp.json().get("results", [])
            self.movies = data
            self._cache[cache_key] = {'time': now, 'data': data}

    def toggle_movie(self, movie: dict, list_type: str):
        """Salvează sau șterge din SQLite."""
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