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
    sort_by: str = "vote_average.desc"
    y_start: str = "1950"
    y_end: str = "2026"
    selected_genres: List[int] = []
    company_ids: List[str] = []
    original_language: str = ""
    content_type: str = "movie"

    STUDIO_ID_MAP: Dict[str, str] = {
        "Warner Bros": "174", "Universal": "33", "Paramount": "4", "Disney": "2",
        "Lionsgate": "1632", "MGM": "21", "A24": "41077", "Castel Film": "2784",
        "Mobra Films": "14382", "Mandragora": "11417", "Netflix": "178464"
    }
    GENRE_MAP: Dict[str, int] = {"Acțiune": 28, "Comedie": 35, "Dramă": 18, "Horror": 27, "SF": 878, "Thriller": 53}

    @rx.var
    def genre_names_list(self) -> List[str]: return list(self.GENRE_MAP.keys())
    @rx.var
    def studio_names_list(self) -> List[str]: return list(self.STUDIO_ID_MAP.keys())

    def set_sort_by(self, val): self.sort_by = val
    def set_y_start(self, val): self.y_start = val
    def set_y_end(self, val): self.y_end = val
    def set_show_mode(self, mode): 
        self.show_mode = mode
        return MovieState.fetch_movies

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
                raw = [{"id": str(m.tmdb_id), "title": m.title, "overview": m.overview, "poster_path": f"https://image.tmdb.org/t/p/w500{m.poster_path}", "vote_average": m.vote_average, "yt_id": ""} for m in entries]
        else:
            params = {"api_key": os.environ.get("TMDB_API_KEY"), "language": "ro-RO", "sort_by": self.sort_by, "vote_count.gte": 150, "primary_release_date.gte": f"{self.y_start}-01-01", "primary_release_date.lte": f"{self.y_end}-12-31", "with_genres": ",".join(map(str, self.selected_genres)) if self.selected_genres else None, "with_companies": "|".join(self.company_ids) if self.company_ids else None}
            r = requests.get(f"https://api.themoviedb.org/3/discover/{self.content_type}", params=params).json()
            raw = []
            for m in r.get("results", []):
                m_id = str(m.get("id"))
                if m_id in self.watched_ids: continue
                raw.append({"id": m_id, "title": m.get("title") if self.content_type == "movie" else m.get("name"), "vote_average": round(m.get("vote_average", 0), 1), "poster_path": f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}", "overview": m.get("overview", "")[:250] + "...", "yt_id": ""})
        self.movies = raw
        self.is_loading = False

    async def toggle_status(self, movie: dict, target_list: str):
        with rx.session() as session:
            m_id = int(movie["id"])
            existing = session.exec(select(MovieEntry).where(MovieEntry.tmdb_id == m_id)).first()
            if existing:
                if existing.list_type == target_list: session.delete(existing)
                else: existing.list_type = target_list
            else:
                session.add(MovieEntry(tmdb_id=m_id, title=movie["title"], overview=movie["overview"], poster_path=movie["poster_path"].replace("https://image.tmdb.org/t/p/w500", ""), vote_average=movie["vote_average"], list_type=target_list))
            session.commit()
        # REPARARE: Nu folosim await pe fetch_movies deoarece este un generator (are yield)
        return MovieState.fetch_movies

    async def load_trailer(self, m_id: str):
        res = requests.get(f"https://api.themoviedb.org/3/{self.content_type}/{m_id}/videos", params={"api_key": os.environ.get("TMDB_API_KEY")}).json()
        key = next((v["key"] for v in res.get("results", []) if v["site"] == "YouTube"), "none")
        for m in self.movies:
            if m["id"] == m_id: m["yt_id"] = key; break
        self.movies = list(self.movies)

    def close_trailer(self, m_id: str):
        for m in self.movies:
            if m["id"] == m_id: m["yt_id"] = ""; break
        self.movies = list(self.movies)

    def toggle_genre(self, name: str):
        gid = self.GENRE_MAP[name]
        if gid in self.selected_genres: self.selected_genres.remove(gid)
        else: self.selected_genres.append(gid)

    def toggle_studio(self, name: str):
        sid = self.STUDIO_ID_MAP[name]
        if sid in self.company_ids: self.company_ids.remove(sid)
        else: self.company_ids.append(sid)

    def reset_filters(self):
        self.y_start, self.y_end, self.selected_genres, self.company_ids = "1950", "2026", [], []
        return MovieState.fetch_movies