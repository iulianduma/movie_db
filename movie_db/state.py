import reflex as rx
import requests
import os
from .models import MovieEntry
from sqlmodel import select
from typing import List

class BaseState(rx.State):
    @rx.var
    def api_key(self) -> str:
        return os.environ.get("TMDB_API_KEY", "a70f38f45a8e036e4763619293111f18")

class MovieState(BaseState):
    movies: list[dict] = []
    is_loading: bool = False
    
    search_query: str = ""
    y_start: str = "1990"
    y_end: str = "2026"
    min_rating: float = 0.0

    def set_search_query(self, val: str): self.search_query = val
    def set_y_start(self, val: str): self.y_start = val
    def set_y_end(self, val: str): self.y_end = val
    
    def set_min_rating(self, val: List[float]): 
        if val: self.min_rating = float(val[0])

    async def fetch_movies(self):
        self.is_loading = True
        yield
        url = "https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": self.api_key, 
            "language": "ro-RO", 
            "sort_by": "popularity.desc",
            "primary_release_date.gte": f"{self.y_start}-01-01",
            "primary_release_date.lte": f"{self.y_end}-12-31",
            "vote_average.gte": self.min_rating
        }
        if self.search_query:
            url = "https://api.themoviedb.org/3/search/movie"
            params["query"] = self.search_query
        
        try:
            r = requests.get(url, params=params).json()
            results = r.get("results", [])
            self.movies = []
            for m in results:
                p_path = m.get("poster_path")
                # Construim URL-ul aici, în Python, nu în frontend
                img_url = f"https://image.tmdb.org/t/p/w500{p_path}" if p_path else "/no_image.png"
                self.movies.append({
                    "id": str(m.get("id")),
                    "title": m.get("title", "N/A"),
                    "overview": m.get("overview", ""),
                    "poster_path": img_url,
                    "vote_average": m.get("vote_average", 0.0),
                    "yt_id": ""
                })
        except:
            self.movies = []
        self.is_loading = False

    async def load_trailer(self, m_id: str):
        for m in self.movies:
            if m["id"] == m_id:
                try:
                    res = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}/videos", params={"api_key": self.api_key}).json()
                    videos = res.get("results", [])
                    # Luăm doar cheia YouTube
                    yt_key = next((v["key"] for v in videos if v["site"] == "YouTube"), "none")
                    m["yt_id"] = yt_key
                except:
                    m["yt_id"] = "none"
                break
        self.movies = list(self.movies)