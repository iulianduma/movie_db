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
    
    def set_show_mode(self, mode: str): self.show_mode = mode
    def set_y_start(self, val): self.y_start = val
    def set_y_end(self, val): self.y_end = val

class MovieState(BaseState):
    movies: list[dict] = []
    watched_ids: list[str] = []
    watchlist_ids: list[str] = []
    is_loading: bool = False

    async def fetch_movies(self):
        self.is_loading = True
        fs = await self.get_state(FilterState)
        
        # Actualizam listele de ID-uri pentru checkbox-uri
        with rx.session() as session:
            watched = session.exec(select(MovieEntry).where(MovieEntry.list_type == "watched")).all()
            self.watched_ids = [str(m.tmdb_id) for m in watched]
            watchlist = session.exec(select(MovieEntry).where(MovieEntry.list_type == "watchlist")).all()
            self.watchlist_ids = [str(m.tmdb_id) for m in watchlist]

        if fs.show_mode in ["Watchlist", "Watched"]:
            with rx.session() as session:
                target = fs.show_mode.lower()
                res = session.exec(select(MovieEntry).where(MovieEntry.list_type == target)).all()
                self.movies = [
                    {
                        "id": str(m.tmdb_id), "title": m.title, "overview": m.overview,
                        "poster_path": m.poster_path, "vote_average": m.vote_average, "yt_id": ""
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
                raw_data = resp.json().get("results", [])
                self.movies = [
                    {**m, "id": str(m["id"]), "yt_id": ""} for m in raw_data
                ]
        except Exception as e:
            print(f"Error: {e}")
        
        self.is_loading = False

    async def load_trailer(self, m_id: str):
        try:
            res = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}/videos?api_key={self.api_key}").json()
            key = next((v["key"] for v in res.get("results", []) if v["site"] == "YouTube"), "")
            for m in self.movies:
                if m["id"] == m_id:
                    m["yt_id"] = key
                    break
        except: pass

    async def toggle_movie(self, movie: dict, list_type: str):
        with rx.session() as session:
            m_id = int(movie["id"])
            existing = session.exec(select(MovieEntry).where((MovieEntry.tmdb_id == m_id) & (MovieEntry.list_type == list_type))).first()
            if existing:
                session.delete(existing)
            else:
                session.add(MovieEntry(
                    tmdb_id=m_id, title=movie["title"], overview=movie.get("overview", ""),
                    poster_path=movie.get("poster_path", ""), vote_average=movie.get("vote_average", 0.0),
                    list_type=list_type
                ))
            session.commit()
        return await self.fetch_movies()