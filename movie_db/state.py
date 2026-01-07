import reflex as rx
import requests
import os
from .models import MovieEntry
from sqlmodel import select

class BaseState(rx.State):
    @rx.var
    def api_key(self) -> str:
        # Folosește cheia ta sau variabila de mediu
        return os.environ.get("TMDB_API_KEY", "a70f38f45a8e036e4763619293111f18")

class MovieState(BaseState):
    movies: list[dict] = []
    watched_ids: list[str] = []
    watchlist_ids: list[str] = []
    is_loading: bool = False
    show_mode: str = "Discover"
    current_mood: str = ""

    async def fetch_movies(self):
        self.is_loading = True
        yield
        
        # Sincronizăm ID-urile din DB pentru checkbox-uri
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
                    "poster_path": m.poster_path, "vote_average": m.vote_average, "yt_id": ""
                } for m in entries]
        else:
            await self.get_discover_movies()
        
        self.is_loading = False

    async def get_discover_movies(self, mood: str = ""):
        self.current_mood = mood
        url = "https://api.themoviedb.org/3/discover/movie"
        params = {"api_key": self.api_key, "language": "ro-RO", "sort_by": "popularity.desc"}
        
        if mood == "Adrenalină": params.update({"with_genres": "28,12"})
        elif mood == "Relaxare": params.update({"with_genres": "35,10751", "vote_average.gte": "7"})
        elif mood == "Mister": params.update({"with_genres": "96,53"})
        elif mood == "Futuristic": params.update({"with_genres": "878", "primary_release_date.gte": "2024-01-01"})
        
        try:
            resp = requests.get(url, params=params).json()
            self.movies = [{**m, "id": str(m["id"]), "yt_id": ""} for m in resp.get("results", [])]
        except: pass

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

    def set_mode(self, mode: str):
        self.show_mode = mode
        return MovieState.fetch_movies