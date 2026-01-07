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
    is_loading: bool = False
    show_mode: str = "Discover"
    
    y_start: str = "1950"
    y_end: str = "2026"
    selected_genres: List[int] = []
    company_ids: List[str] = []
    sort_by: str = "vote_average.desc"
    content_type: str = "movie"
    original_language: str = ""
    certification: str = ""

    GENRE_MAP: Dict[str, int] = {
        "Acțiune": 28, "Aventură": 12, "Animație": 16, "Comedie": 35, 
        "Crime": 80, "Documentar": 99, "Dramă": 18, "Familie": 10751, 
        "Fantasy": 14, "Istoric": 36, "Horror": 27, "Muzical": 10402, 
        "Mister": 9648, "Romantic": 10749, "SF": 878, "Thriller": 53, "Război": 10752
    }

    STUDIO_MAP: Dict[str, str] = {
        "Disney": "2", "Warner Bros": "174", "Universal": "33", "Paramount": "4",
        "A24": "41077", "MGM": "21", "Lionsgate": "1632", "Gaumont": "9",
        "Castel Film": "2784", "Mobra Films": "14382", "Netflix": "178464"
    }

    @rx.var
    def genre_names_list(self) -> List[str]: return list(self.GENRE_MAP.keys())
    
    @rx.var
    def studio_names_list(self) -> List[str]: return list(self.STUDIO_MAP.keys())

    def set_sort_by(self, val): self.sort_by = val
    def set_y_start(self, val): self.y_start = val
    def set_y_end(self, val): self.y_end = val
    def set_content_type(self, val): self.content_type = val
    def set_language(self, val): self.original_language = val
    def set_certification(self, val): self.certification = val

    def reset_filters(self):
        self.y_start, self.y_end, self.sort_by = "1950", "2026", "vote_average.desc"
        self.selected_genres, self.company_ids, self.original_language, self.certification = [], [], "", ""
        return MovieState.fetch_movies

    def toggle_genre(self, name: str):
        gid = self.GENRE_MAP[name]
        if gid in self.selected_genres: self.selected_genres.remove(gid)
        else: self.selected_genres.append(gid)

    def toggle_studio(self, name: str):
        sid = self.STUDIO_MAP[name]
        if sid in self.company_ids: self.company_ids.remove(sid)
        else: self.company_ids.append(sid)

    async def fetch_movies(self):
        self.is_loading = True
        yield
        with rx.session() as session:
            res = session.exec(select(MovieEntry)).all()
            self.watched_ids = [str(m.tmdb_id) for m in res]

        base_url = f"https://api.themoviedb.org/3/discover/{self.content_type}"
        params = {
            "api_key": os.environ.get("TMDB_API_KEY"),
            "language": "ro-RO",
            "sort_by": self.sort_by,
            "vote_count.gte": 100,
            "primary_release_date.gte": f"{self.y_start}-01-01",
            "primary_release_date.lte": f"{self.y_end}-12-31",
            "with_genres": ",".join(map(str, self.selected_genres)) if self.selected_genres else None,
            "with_companies": "|".join(self.company_ids) if self.company_ids else None,
            "with_original_language": self.original_language if self.original_language else None,
        }
        if self.certification:
            params["certification_country"] = "US"
            params["certification"] = self.certification

        r = requests.get(base_url, params=params).json()
        self.movies = []
        for m in r.get("results", []):
            m_id = str(m.get("id"))
            if m_id in self.watched_ids: continue
            path = m.get("poster_path")
            self.movies.append({
                "id": m_id,
                "title": m.get("title") if self.content_type == "movie" else m.get("name"),
                "overview": m.get("overview", "")[:150] + "...",
                "poster_path": f"https://image.tmdb.org/t/p/w500{path}" if path else "/no_image.png",
                "vote_average": round(m.get("vote_average", 0), 1),
                "yt_id": ""
            })
        self.is_loading = False

    async def load_trailer(self, m_id: str):
        res = requests.get(f"https://api.themoviedb.org/3/{self.content_type}/{m_id}/videos", params={"api_key": os.environ.get("TMDB_API_KEY")}).json()
        key = next((v["key"] for v in res.get("results", []) if v["site"] == "YouTube"), "none")
        for m in self.movies:
            if m["id"] == m_id: m["yt_id"] = key; break
        self.movies = list(self.movies)

    async def toggle_list(self, movie: dict, l_type: str):
        with rx.session() as session:
            m_id = int(movie["id"])
            exist = session.exec(select(MovieEntry).where(MovieEntry.tmdb_id == m_id)).first()
            if exist: session.delete(exist)
            else: session.add(MovieEntry(tmdb_id=m_id, title=movie["title"], overview=movie["overview"], poster_path=movie["poster_path"].replace("https://image.tmdb.org/t/p/w500", ""), vote_average=movie["vote_average"], list_type=l_type, added_at=datetime.now()))
            session.commit()
        return await self.fetch_movies()