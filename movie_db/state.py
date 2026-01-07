import reflex as rx
import requests
import os
import time
from .models import MovieEntry
from sqlmodel import select

class BaseState(rx.State):
    @rx.var
    def api_key(self) -> str:
        return os.environ.get("TMDB_API_KEY", "")

class UserState(BaseState):
    is_logged_in: bool = False
    username: str = ""
    password: str = ""

    def set_username(self, val): self.username = val
    def set_password(self, val): self.password = val

    def login(self):
        if self.username == "admin" and self.password == "1234":
            self.is_logged_in = True
            return rx.redirect("/")
        return rx.window_alert("Credențiale incorecte!")

    def logout(self):
        self.is_logged_in = False
        return rx.redirect("/")

class FilterState(BaseState):
    show_mode: str = "Discover"
    y_start: str = "2020"
    y_end: str = "2026"
    
    def set_show_mode(self, mode: str):
        self.show_mode = mode

class MovieState(BaseState):
    movies: list[dict] = []
    is_loading: bool = False
    _cache: dict = {}

    async def fetch_movies(self):
        self.is_loading = True
        # Corecția principală: await pentru get_state
        fs = await self.get_state(FilterState)
        
        if fs.show_mode in ["Watchlist", "Watched"]:
            with rx.session() as session:
                target = fs.show_mode.lower()
                res = session.exec(select(MovieEntry).where(MovieEntry.list_type == target)).all()
                self.movies = [
                    {
                        "id": m.tmdb_id, "title": m.title, "overview": m.overview,
                        "poster_path": m.poster_path, "vote_average": m.vote_average
                    } for m in res
                ]
            self.is_loading = False
            return

        params = {
            "api_key": self.api_key,
            "language": "ro-RO",
            "primary_release_date.gte": f"{fs.y_start}-01-01",
            "primary_release_date.lte": f"{fs.y_end}-12-31",
        }
        
        try:
            resp = requests.get("https://api.themoviedb.org/3/discover/movie", params=params)
            if resp.status_code == 200:
                self.movies = resp.json().get("results", [])
        except Exception as e:
            print(f"Error fetching: {e}")
        
        self.is_loading = False

    async def fetch_movies(self):  # Adaugă async aici
        self.is_loading = True
        # Adaugă await aici - este obligatoriu în versiunile noi de Reflex
        fs = await self.get_state(FilterState) 
        
        if fs.show_mode in ["Watchlist", "Watched"]:
            with rx.session() as session:
                target = fs.show_mode.lower()
                res = session.exec(select(MovieEntry).where(MovieEntry.list_type == target)).all()
                self.movies = [
                    {
                        "id": m.tmdb_id, "title": m.title, "overview": m.overview,
                        "poster_path": m.poster_path, "vote_average": m.vote_average
                    } for m in res
                ]
            self.is_loading = False
            return