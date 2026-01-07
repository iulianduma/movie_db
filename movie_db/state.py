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
    
    # Filtre noi
    y_start: str = "2020"
    y_end: str = "2026"
    search_query: str = ""

    async def fetch_movies(self):
        self.is_loading = True
        yield
        
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
                    "yt_id": "", "studio": "Salvat", "genre_names": "Personal"
                } for m in entries]
        else:
            url = "https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": self.api_key, "language": "ro-RO", "sort_by": "popularity.desc",
                "primary_release_date.gte": f"{self.y_start}-01-01",
                "primary_release_date.lte": f"{self.y_end}-12-31"
            }
            if self.search_query:
                url = "https://api.themoviedb.org/3/search/movie"
                params["query"] = self.search_query

            resp = requests.get(url, params=params).json()
            # Aici curățăm datele și pregătim câmpurile pentru UI
            self.movies = []
            for m in resp.get("results", []):
                self.movies.append({
                    "id": str(m.get("id")),
                    "title": m.get("title"),
                    "overview": m.get("overview", ""),
                    "poster_path": m.get("poster_path", ""),
                    "vote_average": m.get("vote_average", 0),
                    "yt_id": "",
                    "studio": "",
                    "genre_names": ""
                })
        
        self.is_loading = False

    async def load_extra(self, m_id: str):
        """Încarcă trailerul și studioul la interacțiune"""
        for m in self.movies:
            if m["id"] == m_id and m["studio"] == "":
                # Trailer
                v_req = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}/videos?api_key={self.api_key}").json()
                m["yt_id"] = next((v["key"] for v in v_req.get("results", []) if v["site"] == "YouTube"), "none")
                # Studio & Genuri
                d_req = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}?api_key={self.api_key}&language=ro-RO").json()
                m["studio"] = d_req.get("production_companies", [{}])[0].get("name", "N/A")
                m["genre_names"] = ", ".join([g["name"] for g in d_req.get("genres", [])[:2]])
                break

    async def toggle_list(self, movie: dict, l_type: str):
        with rx.session() as session:
            m_id = int(movie["id"])
            exist = session.exec(select(MovieEntry).where((MovieEntry.tmdb_id == m_id) & (MovieEntry.list_type == l_type))).first()
            if exist: session.delete(exist)
            else: session.add(MovieEntry(tmdb_id=m_id, title=movie["title"], overview=movie.get("overview", ""), poster_path=movie.get("poster_path", ""), vote_average=movie.get("vote_average", 0.0), list_type=l_type))
            session.commit()
        return await self.fetch_movies()