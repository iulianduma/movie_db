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
    def login(self, username, password):
        if username == "admin" and password == "1234":
            self.is_logged_in = True
            return rx.redirect("/")

class FilterState(BaseState):
    show_mode: str = "Discover"
    y_start: str = "2020"
    y_end: str = "2026"
    actor_name: str = ""
    company_ids: list[str] = []
    selected_genres: list[int] = []
    
    STUDIO_ID_MAP = {"Marvel Studios": "420", "Warner Bros": "174", "A24": "41077"} # ... restul mapărilor tale
    GENRE_MAP = {"Acțiune": 28, "SF": 878} # ... restul mapărilor tale

class MovieState(BaseState):
    movies: list[dict] = []
    is_loading: bool = False
    _cache: dict = {}

    def fetch_movies(self, filters: dict):
        self.is_loading = True
        # Aici vine logica ta de requests.get de la TMDB
        # Folosind self.api_key și caching-ul discutat
        self.is_loading = False