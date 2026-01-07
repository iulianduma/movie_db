import reflex as rx
import requests
import os
from .models import MovieEntry
from sqlmodel import select
from typing import List

class BaseState(rx.State):
    @rx.var
    def api_key(self) -> str:
        return os.environ.get("TMDB_API_KEY", "")

class MovieState(BaseState):
    movies: list[dict] = []
    watched_ids: list[str] = []
    watchlist_ids: list[str] = []
    is_loading: bool = False
    show_mode: str = "Discover"
    
    search_query: str = ""
    y_start: str = "2020"
    y_end: str = "2026"
    min_rating: float = 0.0

    def set_search_query(self, val: str): self.search_query = val
    def set_y_start(self, val: str): self.y_start = val
    def set_y_end(self, val: str): self.y_end = val
    def set_show_mode(self, val: str): self.show_mode = val
    def set_min_rating(self, val: List[float]): 
        if val: self.min_rating = float(val[0])

    async def fetch_movies(self):
        self.is_loading = True
        yield
        
        with rx.session() as session:
            res = session.exec(select(MovieEntry)).all()
            self.watched_ids = [str(m.tmdb_id) for m in res if m.list_type == "watched"]
            self.watchlist_ids = [str(m.tmdb_id) for m in res if m.list_type == "watchlist"]

        if self.show_mode in ["Watchlist", "Watched"]:
            target = self.show_mode.lower()
            with rx.session() as session:
                entries = session.exec(select(MovieEntry).where(MovieEntry.list_type == target)).all()
                self.movies = [{
                    "id": str(m.tmdb_id), "title": m.title, "overview": m.overview,
                    "poster_path": m.poster_path, "vote_average": m.vote_average,
                    "yt_id": "", "studio": "Salvat", "genre_names": ""
                } for m in entries]
        else:
            url = "https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": self.api_key, "language": "ro-RO", "sort_by": "popularity.desc",
                "primary_release_date.gte": f"{self.y_start}-01-01",
                "primary_release_date.lte": f"{self.y_end}-12-31",
                "vote_average.gte": self.min_rating
            }
            if self.search_query:
                url = "https://api.themoviedb.org/3/search/movie"
                params["query"] = self.search_query
            
            resp = requests.get(url, params=params).json()
            self.movies = [{**m, "id": str(m.get("id")), "yt_id": "", "studio": "", "genre_names": ""} for m in resp.get("results", [])]
        
        self.is_loading = False

    async def get_by_mood(self, mood: str):
        self.is_loading = True
        yield
        url = "https://api.themoviedb.org/3/discover/movie"
        params = {"api_key": self.api_key, "language": "ro-RO", "sort_by": "popularity.desc"}
        
        if mood == "Adrenalină": params.update({"with_genres": "28,12"})
        elif mood == "Relaxare": params.update({"with_genres": "35,10751", "vote_average.gte": "7"})
        elif mood == "Mister": params.update({"with_genres": "96,53"})
        elif mood == "Futuristic": params.update({"with_genres": "878", "primary_release_date.gte": "2025-01-01"})
        
        resp = requests.get(url, params=params).json()
        self.movies = [{**m, "id": str(m.get("id")), "yt_id": "", "studio": "", "genre_names": ""} for m in resp.get("results", [])]
        self.is_loading = False

    async def load_extra(self, m_id: str):
        for m in self.movies:
            if m["id"] == m_id and m["yt_id"] == "":
                v = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}/videos?api_key={self.api_key}").json()
                m["yt_id"] = next((vid["key"] for vid in v.get("results", []) if vid["site"] == "YouTube"), "none")
                d = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}?api_key={self.api_key}&language=ro-RO").json()
                m["studio"] = d.get("production_companies", [{}])[0].get("name", "N/A")
                m["genre_names"] = ", ".join([g["name"] for g in d.get("genres", [])[:2]])
                break

    async def toggle_list(self, movie: dict, l_type: str):
        with rx.session() as session:
            m_id = int(movie["id"])
            exist = session.exec(select(MovieEntry).where((MovieEntry.tmdb_id == m_id) & (MovieEntry.list_type == l_type))).first()
            if exist: session.delete(exist)
            else:
                session.add(MovieEntry(tmdb_id=m_id, title=movie["title"], overview=movie.get("overview", ""), 
                                      poster_path=movie.get("poster_path", ""), vote_average=movie.get("vote_average", 0.0), 
                                      list_type=l_type))
            session.commit()
        return await self.fetch_movies()