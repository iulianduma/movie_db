import reflex as rx
import requests
import os
from .models import MovieEntry
from sqlmodel import select
from typing import List, Dict

class MovieState(rx.State):
    movies: list[dict] = []
    watched_ids: list[str] = []
    watchlist_ids: list[str] = []
    is_loading: bool = False
    show_mode: str = "Discover"
    
    # Filtre preluate din Backup
    y_start: str = "2020"
    y_end: str = "2026"
    min_rate: float = 0.0
    max_rate: float = 10.0
    actor_name: str = ""
    company_ids: List[str] = []
    selected_genres: List[int] = []

    STUDIO_ID_MAP: Dict[str, str] = {
        "MediaPro": "2525", "Animafilm": "11417", "Moldova-Film": "10555", "Buftea": "129758", 
        "Gaumont": "9", "Canal+": "104", "Babelsberg": "334",
        "Marvel Studios": "420", "Warner Bros": "174", "Walt Disney Pictures": "2", 
        "Universal Pictures": "33", "Paramount": "4", "Sony Pictures": "57",
        "A24": "41077", "Lionsgate": "1632", "MGM": "21", "Miramax": "14", 
        "Legendary": "923", "Amblin": "56", "Neon": "83006"
    }

    STUDIO_CATS: List[str] = ["🇪🇺 EU - RO", "🇺🇸 US - HOLLYWOOD", "🎬 Independente"]
    STUDIO_MAP: Dict[str, List[str]] = {
        "🇪🇺 EU - RO": ["MediaPro", "Animafilm", "Moldova-Film", "Buftea", "Gaumont", "Canal+", "Babelsberg"],
        "🇺🇸 US - HOLLYWOOD": ["Marvel Studios", "Warner Bros", "Walt Disney Pictures", "Universal Pictures", "Paramount", "Sony Pictures"],
        "🎬 Independente": ["A24", "Lionsgate", "MGM", "Miramax", "Legendary", "Amblin", "Neon"]
    }
    GENRE_MAP: Dict[str, int] = {"Acțiune": 28, "Comedie": 35, "Dramă": 18, "Horror": 27, "SF": 878, "Thriller": 53}

    @rx.var
    def api_key(self) -> str:
        return os.environ.get("TMDB_API_KEY", "")

    def set_y_start(self, val): self.y_start = val
    def set_y_end(self, val): self.y_end = val
    def set_actor(self, val): self.actor_name = val
    def set_show_mode(self, mode): 
        self.show_mode = mode
        return MovieState.fetch_movies

    def set_rating_range(self, val: List[float]): 
        self.min_rate, self.max_rate = float(val[0]), float(val[1])

    async def fetch_movies(self):
        self.is_loading = True
        yield
        
        # Sincronizare ID-uri din DB
        with rx.session() as session:
            res = session.exec(select(MovieEntry)).all()
            self.watched_ids = [str(m.tmdb_id) for m in res if m.list_type == "watched"]
            self.watchlist_ids = [str(m.tmdb_id) for m in res if m.list_type == "watchlist"]

        if self.show_mode in ["Watchlist", "Watched"]:
            target = "watchlist" if self.show_mode == "Watchlist" else "watched"
            with rx.session() as session:
                entries = session.exec(select(MovieEntry).where(MovieEntry.list_type == target)).all()
                self.movies = [{
                    "id": str(m.tmdb_id), "title": m.title, "overview": m.overview,
                    "poster_path": f"https://image.tmdb.org/t/p/w500{m.poster_path}",
                    "vote_average": m.vote_average, "yt_id": "", "studio": "Salvat", "genres": []
                } for m in entries]
        else:
            url = "https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": self.api_key, "language": "ro-RO", "sort_by": "popularity.desc",
                "primary_release_date.gte": f"{self.y_start}-01-01",
                "primary_release_date.lte": f"{self.y_end}-12-31",
                "vote_average.gte": self.min_rate, "vote_average.lte": self.max_rate,
                "with_genres": ",".join(map(str, self.selected_genres)) if self.selected_genres else None,
                "with_companies": "|".join(self.company_ids) if self.company_ids else None,
            }
            if self.actor_name:
                a_res = requests.get(f"https://api.themoviedb.org/3/search/person?api_key={self.api_key}&query={self.actor_name}").json()
                if a_res.get("results"): params["with_cast"] = a_res["results"][0]["id"]
            
            resp = requests.get(url, params=params).json()
            self.movies = []
            for m in resp.get("results", []):
                p_path = m.get("poster_path")
                m_id = str(m.get("id"))
                # Excludem ce e deja în liste în modul Discover
                if m_id in self.watched_ids or m_id in self.watchlist_ids: continue
                
                self.movies.append({
                    "id": m_id, "title": m.get("title"), "overview": m.get("overview", "")[:200] + "...",
                    "poster_path": f"https://image.tmdb.org/t/p/w500{p_path}" if p_path else "/no_image.png",
                    "vote_average": m.get("vote_average"), "yt_id": "", "studio": "", "genres": []
                })
        self.is_loading = False

    async def load_trailer(self, m_id: str):
        for m in self.movies:
            if m["id"] == m_id:
                res = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}/videos", params={"api_key": self.api_key}).json()
                m["yt_id"] = next((v["key"] for v in res.get("results", []) if v["site"] == "YouTube"), "none")
                break
        self.movies = list(self.movies)

    async def toggle_list(self, movie: dict, l_type: str):
        with rx.session() as session:
            m_id = int(movie["id"])
            exist = session.exec(select(MovieEntry).where((MovieEntry.tmdb_id == m_id) & (MovieEntry.list_type == l_type))).first()
            if exist: session.delete(exist)
            else:
                session.add(MovieEntry(tmdb_id=m_id, title=movie["title"], overview=movie["overview"], 
                                      poster_path=movie["poster_path"].replace("https://image.tmdb.org/t/p/w500", ""), 
                                      vote_average=movie["vote_average"], list_type=l_type))
            session.commit()
        return MovieState.fetch_movies

    def toggle_genre(self, g_name: str):
        gid = self.GENRE_MAP.get(g_name)
        if gid in self.selected_genres: self.selected_genres.remove(gid)
        else: self.selected_genres.append(gid)