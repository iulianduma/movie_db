import reflex as rx
import requests
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Dict

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
WATCHED_FILE = "watched_list.json"
WATCHLIST_FILE = "watchlist.json"

class Movie(BaseModel):
    id: str
    title: str
    overview: str
    poster_path: str
    vote_average: float
    yt_id: str = ""
    studio: str = ""
    genres: List[str] = []

class State(rx.State):
    movies: List[Movie] = []
    watched_ids: List[str] = []
    watchlist_ids: List[str] = []
    is_loading: bool = False
    
    show_mode: str = "Discover"
    y_start: str = "2020"
    y_end: str = "2026"
    min_rate: float = 0.0
    max_rate: float = 10.0
    actor_name: str = ""
    cert: str = ""
    company_ids: List[str] = []
    selected_genres: List[int] = []

    # Mapare fixa a ID-urilor pentru a asigura functionarea "Selecteaza Toate"
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
    GENRE_NAMES: List[str] = ["Acțiune", "Comedie", "Dramă", "Horror", "SF", "Thriller"]
    GENRE_MAP: Dict[str, int] = {"Acțiune": 28, "Comedie": 35, "Dramă": 18, "Horror": 27, "SF": 878, "Thriller": 53}

    def on_load(self):
        if os.path.exists(WATCHED_FILE):
            with open(WATCHED_FILE, "r") as f: self.watched_ids = json.load(f)
        if os.path.exists(WATCHLIST_FILE):
            with open(WATCHLIST_FILE, "r") as f: self.watchlist_ids = json.load(f)
        return State.fetch_movies

    def set_y_start(self, val): self.y_start = val
    def set_y_end(self, val): self.y_end = val
    def apply_filters(self): return State.fetch_movies
    def set_show_mode(self, mode): self.show_mode = mode; return State.fetch_movies
    def set_actor(self, val): self.actor_name = val; return State.fetch_movies
    def set_cert(self, val): self.cert = val; return State.fetch_movies
    def set_rating_range(self, val): 
        self.min_rate, self.max_rate = float(val[0]), float(val[1])
        return State.fetch_movies

    def reset_filters(self):
        self.y_start, self.y_end, self.min_rate, self.max_rate = "2020", "2026", 0.0, 10.0
        self.company_ids, self.selected_genres, self.actor_name, self.cert = [], [], "", ""
        return State.fetch_movies

    def fetch_movies(self):
        self.is_loading = True
        if not API_KEY: return
        raw_movies = []
        
        if self.show_mode in ["Watchlist", "Watched"]:
            target = self.watchlist_ids if self.show_mode == "Watchlist" else self.watched_ids
            for m_id in target:
                res = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}?api_key={API_KEY}&language=ro-RO").json()
                if res.get("id"): raw_movies.append(res)
        else:
            url = "https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": API_KEY, "language": "ro-RO", "sort_by": "popularity.desc",
                "primary_release_date.gte": f"{self.y_start}-01-01",
                "primary_release_date.lte": f"{self.y_end}-12-31",
                "vote_average.gte": self.min_rate, "vote_average.lte": self.max_rate,
                "with_genres": ",".join(map(str, self.selected_genres)) if self.selected_genres else None,
                "with_companies": "|".join(self.company_ids) if self.company_ids else None,
            }
            if self.cert: params["certification"] = self.cert
            if self.actor_name:
                a_res = requests.get(f"https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={self.actor_name}").json()
                if a_res.get("results"): params["with_cast"] = a_res["results"][0]["id"]
            res = requests.get(url, params=params).json()
            raw_movies = res.get("results", [])

        temp = []
        for m in raw_movies:
            m_id = str(m.get("id"))
            if self.show_mode == "Discover" and (m_id in self.watched_ids or m_id in self.watchlist_ids): continue
            g_names = [name for name, gid in self.GENRE_MAP.items() if gid in m.get("genre_ids", [])[:2]]
            temp.append(Movie(id=m_id, title=m.get("title", "N/A"), overview=m.get("overview", "")[:300] + "...",
                              poster_path=str(m.get("poster_path", "")), vote_average=float(m.get("vote_average", 0)),
                              studio="", genres=g_names))
        self.movies = temp
        self.is_loading = False

    def select_category(self, cat: str):
        # Folosim ID-urile pre-mapate pentru viteza instanta
        new_ids = [self.STUDIO_ID_MAP[s] for s in self.STUDIO_MAP[cat] if s in self.STUDIO_ID_MAP]
        self.company_ids = list(set(self.company_ids + new_ids))
        return State.fetch_movies

    def set_studio(self, s_name: str):
        sid = self.STUDIO_ID_MAP.get(s_name)
        if sid and sid not in self.company_ids: self.company_ids.append(sid)
        return State.fetch_movies

    def load_extra_info(self, m_id: str):
        for m in self.movies:
            if m.id == m_id:
                if m.studio != "": return
                details = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}?api_key={API_KEY}&language=ro-RO").json()
                companies = details.get("production_companies", [])
                m.studio = companies[0].get("name", "N/A")[:15] if companies else "N/A"
                break

    def toggle_watched(self, m_id: str):
        if m_id in self.watched_ids: self.watched_ids.remove(m_id)
        else:
            self.watched_ids.append(m_id)
            if m_id in self.watchlist_ids: self.watchlist_ids.remove(m_id)
        with open(WATCHED_FILE, "w") as f: json.dump(self.watched_ids, f)
        with open(WATCHLIST_FILE, "w") as f: json.dump(self.watchlist_ids, f)
        return State.fetch_movies

    def toggle_watchlist(self, m_id: str):
        if m_id in self.watchlist_ids: self.watchlist_ids.remove(m_id)
        else: self.watchlist_ids.append(m_id)
        with open(WATCHLIST_FILE, "w") as f: json.dump(self.watchlist_ids, f)
        return State.fetch_movies

    def toggle_genre(self, g_name: str):
        gid = self.GENRE_MAP.get(g_name)
        if gid in self.selected_genres: self.selected_genres.remove(gid)
        else: self.selected_genres.append(gid)
        return State.fetch_movies

    def load_trailer(self, m_id: str):
        v_res = requests.get(f"https://api.themoviedb.org/3/movie/{m_id}/videos?api_key={API_KEY}").json()
        key = next((v["key"] for v in v_res.get("results", []) if v["site"] == "YouTube"), "")
        for m in self.movies:
            if m.id == m_id: m.yt_id = key; break

def movie_card(m: Movie):
    return rx.card(
        rx.vstack(
            rx.box(
                rx.cond(m.yt_id != "",
                    rx.html(f'<iframe width="100%" height="220" src="https://www.youtube.com/embed/{m.yt_id}?autoplay=1" frameborder="0" allowfullscreen style="border-radius: 12px 12px 0 0;"></iframe>'),
                    rx.box(
                        rx.image(src="https://image.tmdb.org/t/p/w500" + m.poster_path, width="100%", height="220px", object_fit="cover", border_radius="12px 12px 0 0"),
                        rx.center(rx.button(rx.icon(tag="play", size=30), on_click=lambda: State.load_trailer(m.id), variant="ghost", color_scheme="gray"), position="absolute", top="0", left="0", width="100%", height="220px", background="rgba(0,0,0,0.4)", border_radius="12px 12px 0 0"),
                        position="relative"
                    )
                ), width="100%"
            ),
            rx.vstack(
                rx.hstack(
                    rx.heading(m.title, size="4", weight="bold", line_clamp=1, flex="1", color="white"),
                    rx.vstack(
                        rx.hstack(rx.text("Văzut", size="1", color="#aaa"), rx.checkbox(checked=State.watched_ids.contains(m.id), on_change=lambda _: State.toggle_watched(m.id), color_scheme="ruby")),
                        rx.hstack(rx.text("Later", size="1", color="#aaa"), rx.checkbox(checked=State.watchlist_ids.contains(m.id), on_change=lambda _: State.toggle_watchlist(m.id), color_scheme="blue")),
                        spacing="1", align_items="end"
                    ), width="100%"
                ),
                rx.hstack(
                    rx.badge(f"⭐ {m.vote_average}", color_scheme="yellow", variant="soft"),
                    rx.text(m.studio, style={"font_size": "8px", "color": "#ff0000", "font_weight": "bold", "text_transform": "uppercase"}),
                    rx.text("|", color="#444"),
                    rx.text(rx.foreach(m.genres, lambda g: g + " "), style={"font_size": "8px", "color": "#888"}),
                    spacing="2", align="center"
                ),
                rx.text(m.overview, style={"font_size": "8px", "text_align": "justify", "color": "#666", "line_height": "1.4"}),
                padding="15px", spacing="3", width="100%"
            )
        ),
        on_mouse_enter=lambda: State.load_extra_info(m.id),
        padding="0", background_color="#0d0d0d", border="1px solid #1a1a1a", border_radius="12px", width="100%"
    )

def sidebar():
    return rx.vstack(
        rx.heading("MOVIE_DB", style={"color": "#ff0000", "font_size": "42px", "font_weight": "900", "text_shadow": "0 0 20px rgba(255,0,0,0.5)", "letter_spacing": "-2px"}),
        rx.button("RESET FILTRE", on_click=State.reset_filters, color_scheme="ruby", variant="outline", width="100%", size="2"),
        rx.divider(alpha=0.1, margin_y="1em"),
        
        rx.vstack(
            rx.button("DISCOVER", on_click=lambda: State.set_show_mode("Discover"), variant=rx.cond(State.show_mode == "Discover", "solid", "ghost"), width="100%"),
            rx.button("WATCHLIST", on_click=lambda: State.set_show_mode("Watchlist"), variant=rx.cond(State.show_mode == "Watchlist", "solid", "ghost"), width="100%"),
            rx.button("WATCHED", on_click=lambda: State.set_show_mode("Watched"), variant=rx.cond(State.show_mode == "Watched", "solid", "ghost"), width="100%"),
            color_scheme="ruby", spacing="2", width="100%"
        ),

        rx.text("ANI PRODUCȚIE", weight="bold", size="1", color="#555", margin_top="1.5em"),
        rx.hstack(
            # Folosim on_blur pentru a nu bloca input-ul la fiecare tasta apasata
            rx.input(placeholder="Din", on_blur=State.set_y_start, default_value=State.y_start, width="100%"),
            rx.input(placeholder="La", on_blur=State.set_y_end, default_value=State.y_end, width="100%"),
        ),

        rx.text("ACTOR", weight="bold", size="1", color="#555"),
        rx.input(
            placeholder="Căutare actor...", 
            on_blur=State.set_actor, 
            # NU punem value= aici pentru a permite tastarea libera
            width="100%"
        ),

        rx.text("STUDIOURI", weight="bold", size="1", color="#555"),
        rx.accordion.root(
            rx.foreach(State.STUDIO_CATS, lambda cat: rx.accordion.item(
                rx.accordion.trigger(cat),
                rx.accordion.content(rx.vstack(
                    rx.button("Selectează Toate", size="1", on_click=lambda: State.select_category(cat), width="100%", color_scheme="ruby", variant="soft"),
                    rx.foreach(State.STUDIO_MAP[cat], lambda s: rx.button(s, size="1", variant="ghost", on_click=lambda: State.set_studio(s), width="100%")),
                    spacing="1"
                ))
            )), width="100%", variant="ghost"
        ),

        rx.text("GENURI", weight="bold", size="1", color="#555"),
        rx.flex(rx.foreach(State.GENRE_NAMES, lambda g: rx.button(g, size="1", variant=rx.cond(State.selected_genres.contains(State.GENRE_MAP[g]), "solid", "outline"), on_click=lambda: State.toggle_genre(g), margin="2px")), wrap="wrap"),
        
        rx.text("RATING", weight="bold", size="1", color="#555"),
        rx.slider(default_value=[0, 10], min=0, max=10, on_value_commit=State.set_rating_range, width="100%"),

        width="320px", height="100vh", padding="30px", background="rgba(10,10,10,0.6)", backdrop_filter="blur(20px)", position="fixed", left="0", border_right="1px solid #222", overflow_y="auto"
    )
    
def index():
    return rx.flex(sidebar(), rx.box(rx.vstack(rx.cond(State.is_loading, rx.center(rx.spinner(color="#ff0000", size="3"), width="100%", padding="2em")), rx.grid(rx.foreach(State.movies, movie_card), columns=rx.breakpoints(initial="1", sm="2", lg="3"), spacing="8", width="100%")), flex="1", margin_left="320px", padding="5em"), background="black", min_height="100vh")

app = rx.App(theme=rx.theme(appearance="dark", accent_color="ruby"))
app.add_page(index, on_load=State.on_load)