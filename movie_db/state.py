import reflex as rx
import requests
import os
from .models import MovieEntry
from sqlmodel import select
from typing import List, Dict
from datetime import datetime

class MovieState(rx.State):
    movies: list[dict] = []
    watched_ids: list[str] = []
    watchlist_ids: list[str] = []
    is_loading: bool = False
    show_mode: str = "Discover"
    
    # FILTRE
    sort_by: str = "vote_average.desc"
    y_start: str = "1950"
    y_end: str = "2026"
    selected_genres: List[int] = []
    company_ids: List[str] = []
    original_language: str = ""
    content_type: str = "movie"

    GENRE_MAP: Dict[str, int] = {"Acțiune": 28, "Comedie": 35, "Dramă": 18, "Horror": 27, "SF": 878, "Thriller": 53, "Aventură": 12, "Documentar": 99}
    STUDIO_MAP: Dict[str, str] = {"Warner Bros": "174", "Disney": "2", "Netflix": "178464", "A24": "41077", "Castel Film": "2784"}

    @rx.var
    def genre_list(self) -> List[str]: return list(self.GENRE_MAP.keys())
    @rx.var
    def studio_list(self) -> List[str]: return list(self.STUDIO_MAP.keys())

    async def fetch_movies(self):
        self.is_loading = True
        yield
        with rx.session() as session:
            res = session.exec(select(MovieEntry)).all()
            self.watched_ids = [str(m.tmdb_id) for m in res if m.list_type == "watched"]
            self.watchlist_ids = [str(m.tmdb_id) for m in res if m.list_type == "watchlist"]

        if self.show_mode.lower() in ["watchlist", "watched"]:
            target = self.show_mode.lower()
            with rx.session() as session:
                entries = session.exec(select(MovieEntry).where(MovieEntry.list_type == target)).all()
                raw_data = [{"id": str(m.tmdb_id), "title": m.title, "overview": m.overview, "poster_path": f"https://image.tmdb.org/t/p/w500{m.poster_path}", "vote_average": m.vote_average, "yt_id": ""} for m in entries]
        else:
            base_url = f"https://api.themoviedb.org/3/discover/{self.content_type}"
            params = {
                "api_key": os.environ.get("TMDB_API_KEY"),
                "language": "ro-RO", "sort_by": self.sort_by, "vote_count.gte": 100,
                "primary_release_date.gte": f"{self.y_start}-01-01", "primary_release_date.lte": f"{self.y_end}-12-31",
                "with_genres": ",".join(map(str, self.selected_genres)) if self.selected_genres else None,
                "with_original_language": self.original_language if self.original_language else None,
            }
            r = requests.get(base_url, params=params).json()
            raw_data = []
            for m in r.get("results", []):
                m_id = str(m.get("id"))
                # REGULA: Dacă e vizionat, nu mai apare în Discover
                if m_id in self.watched_ids: continue
                path = m.get("poster_path")
                raw_data.append({
                    "id": m_id, "title": m.get("title") if self.content_type == "movie" else m.get("name"),
                    "vote_average": round(m.get("vote_average", 0), 1),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{path}" if path else "/no_image.png",
                    "overview": m.get("overview", "")[:150] + "...", "yt_id": ""
                })
        self.movies = raw_data
        self.is_loading = False

    async def toggle_status(self, movie: dict, target_list: str):
        with rx.session() as session:
            m_id = int(movie["id"])
            # Ștergem orice stare existentă a filmului pentru a permite mutarea între liste
            existing = session.exec(select(MovieEntry).where(MovieEntry.tmdb_id == m_id)).first()
            if existing:
                if existing.list_type == target_list:
                    session.delete(existing)
                else:
                    existing.list_type = target_list
                    existing.added_at = datetime.now()
            else:
                new_entry = MovieEntry(
                    tmdb_id=m_id, title=movie["title"], overview=movie["overview"],
                    poster_path=movie["poster_path"].replace("https://image.tmdb.org/t/p/w500", ""),
                    vote_average=movie["vote_average"], list_type=target_list, added_at=datetime.now()
                )
                session.add(new_entry)
            session.commit()
        return await self.fetch_movies()

    # Funcții setare stare
    def set_show_mode(self, mode): self.show_mode = mode; return MovieState.fetch_movies
    def set_sort_by(self, val): self.sort_by = val
    def set_y_start(self, val): self.y_start = val
    def set_y_end(self, val): self.y_end = val
    def toggle_genre(self, name: str):
        gid = self.GENRE_MAP[name]
        if gid in self.selected_genres: self.selected_genres.remove(gid)
        else: self.selected_genres.append(gid)

    async def load_trailer(self, m_id: str):
        res = requests.get(f"https://api.themoviedb.org/3/{self.content_type}/{m_id}/videos", params={"api_key": os.environ.get("TMDB_API_KEY")}).json()
        key = next((v["key"] for v in res.get("results", []) if v["site"] == "YouTube"), "none")
        for m in self.movies:
            if m["id"] == m_id: m["yt_id"] = key; break
        self.movies = list(self.movies)