import reflex as rx
from typing import List, Dict, Optional
import time

# Modelul pentru baza de date
class MovieEntry(rx.Model, table=True):
    user_id: str
    tmdb_id: int
    list_type: str  # "watchlist" sau "watched"

class BaseState(rx.State):
    """Starea de bază care conține datele comune."""
    user_id: str = "guest_1" # Identificator temporar

class UserState(BaseState):
    """Gestionează autentificarea și preferințele utilizatorului."""
    is_logged_in: bool = False
    username: str = ""

    def login(self, username, password):
        if username == "admin" and password == "parola_ta":
            self.is_logged_in = True
            self.username = username
            return rx.redirect("/")
        return rx.window_alert("Date incorecte!")

class FilterState(BaseState):
    """Gestionează exclusiv logica de filtrare."""
    y_start: str = ""
    y_end: str = ""
    actor_name: str = ""
    selected_genres: List[int] = []
    
    def set_y_start(self, val): self.y_start = val

class MovieState(BaseState):
    """Gestionează datele de la TMDB și interacțiunea cu DB."""
    movies: List[Dict] = []
    # Cache simplu în memorie: {query_url: (timestamp, data)}
    _cache: Dict[str, tuple] = {}
    CACHE_EXPIRATION = 3600  # 1 oră

    def get_cached_data(self, url: str):
        now = time.time()
        if url in self._cache:
            ts, data = self._cache[url]
            if now - ts < self.CACHE_EXPIRATION:
                return data
        return None

    def add_to_db(self, movie_id: int, list_type: str):
        with rx.session() as session:
            session.add(MovieEntry(user_id=self.user_id, tmdb_id=movie_id, list_type=list_type))
            session.commit()