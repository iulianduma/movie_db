import reflex as rx
import requests
import os
from .models import MovieEntry
from sqlmodel import select

class BaseState(rx.State):
    @rx.var
    def api_key(self) -> str:
        return os.environ.get("TMDB_API_KEY", "a70f38f45a8e036e4763619293111f18")

class MovieState(BaseState):
    movies: list[dict] = []
    watched_ids: list[str] = []
    watchlist_ids: list[str] = []
    is_loading: bool = False
    show_mode: str = "Discover"
    
    # Filtre
    y_start: str = "2020"
    y_end: str = "2026"
    selected_genres: list[int] = []
    
    GENRE_MAP: dict = {"Acțiune": 28, "Comedie": 35, "Dramă": 18, "SF": 878, "Horror": 27}

    async def fetch_movies(self):
        self.is_loading = True
        yield
        
        # Sincronizare ID-uri din baza de date pentru checkbox-uri
        with rx.session() as session:
            res = session.exec(select(MovieEntry)).all()
            self.watched_ids = [str(m.tmdb_id) for m in res if m.list_type == "watched"]
            self.watchlist_ids = [str(m.tmdb_id) for m in res if m.list_type == "watchlist"]

        if self.show_mode in ["Watchlist", "Watched"]:
            with rx.session() as session:
                target = self.show_mode.lower()
                entries = session.exec(select(MovieEntry).where(MovieEntry.list_type == target)).all()
                self.movies = [{
                    "id": str(m.tmdb_id), "title": m.title, "overview": m.overview,
                    "poster_path": m.poster_path, "vote_average": m.vote_average, 
                    "yt_id": "", "studio": "Salvat", "genres": []
                } for m in entries]
        else:
            url = "https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": self.api_key, "language": "ro-RO", "sort_by": "popularity.desc",
                "primary_release_date.gte": f"{self.y_start}-01-01",
                "primary_release_date.lte": f"{self.y_end}-12-31",
                "with_genres": ",".join(map(str, self.selected_genres))
            }
            resp = requests.get(url, params=params).json()
            self.movies = [{**m, "id": str(m["id"]), "yt_id": "", "studio": ""} for m in resp.get("results", [])]
        
        self.is_loading = False

    async def load_extra(self, m_id: str):
        """Încarcă trailerul și studioul când pui mouse-ul pe card (On Demand)"""
        for m in self.movies:
            if m["id"] == m_id and (m["yt_id"] == "" or m["studio"] == ""):
                # Video/Trailer
                v_res = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}/videos?api_key={self.api_key}").json()
                m["yt_id"] = next((v["key"] for v in v_res.get("results", []) if v["site"] == "YouTube"), "")
                # Detalii/Studio
                d_res = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}?api_key={self.api_key}").json()
                studios = d_res.get("production_companies", [])
                m["studio"] = studios[0]["name"] if studios else "N/A"
                break

    async def toggle_list(self, movie: dict, l_type: str):
        with rx.session() as session:
            m_id = int(movie["id"])
            exist = session.exec(select(MovieEntry).where((MovieEntry.tmdb_id == m_id) & (MovieEntry.list_type == l_type))).first()
            if exist:
                session.delete(exist)
            else:
                session.add(MovieEntry(
                    tmdb_id=m_id, title=movie["title"], overview=movie.get("overview", ""),
                    poster_path=movie.get("poster_path", ""), vote_average=movie.get("vote_average", 0.0),
                    list_type=l_type
                ))
            session.commit()
        return await self.fetch_movies()