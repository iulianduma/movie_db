import reflex as rx
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

class State(rx.State):
    """Logica aplicatiei."""
    movies: list[dict] = []
    watched_ids: list[str] = []
    search_query: str = ""

    def fetch_trending(self):
        url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={API_KEY}&language=ro-RO"
        res = requests.get(url).json()
        self.movies = res.get("results", [])

    def toggle_watched(self, movie_id: str):
        if movie_id in self.watched_ids:
            self.watched_ids.remove(movie_id)
        else:
            self.watched_ids.append(movie_id)

def movie_card(movie: dict):
    """Componenta de design pentru un singur film."""
    return rx.box(
        rx.vstack(
            # Imaginea de referinta (Poster)
            rx.image(
                src=f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",
                border_radius="15px 15px 0 0",
                width="100%",
            ),
            rx.vstack(
                rx.heading(movie["title"], size="md", color="white"),
                rx.text(f"⭐ {movie['vote_average']}", color="yellow.400", font_weight="bold"),
                rx.text(movie["overview"], line_clamp=3, font_size="0.8em", color="gray.400"),
                
                # Trailerul incorporat (YouTube)
                rx.box(
                    rx.html(f'<iframe width="100%" src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allowfullscreen></iframe>'),
                    width="100%",
                    padding_top="10px",
                ),
                
                # Butonul de Agenda
                rx.button(
                    rx.cond(
                        State.watched_ids.contains(str(movie["id"])),
                        "Vizionat ✅",
                        "Marchează ca văzut",
                    ),
                    on_click=lambda: State.toggle_watched(str(movie["id"])),
                    color_scheme=rx.cond(State.watched_ids.contains(str(movie["id"])), "green", "red"),
                    width="100%",
                ),
                padding="15px",
                align_items="start",
            ),
        ),
        background="#1a1a1a",
        border_radius="15px",
        border="1px solid #333",
        _hover={"transform": "scale(1.02)", "border_color": "#e50914"},
        transition="all 0.2s ease-in-out",
    )

def index():
    return rx.center(
        rx.vstack(
            rx.heading("CineFlux Ultra", size="2xl", margin_bottom="2em", color="#e50914"),
            
            # Grid Responsive (1 coloana pe mobil, 3 pe desktop)
            rx.responsive_grid(
                rx.foreach(State.movies, movie_card),
                columns=[1, 2, 3],
                spacing="20px",
                width="90%",
            ),
            padding_y="5em",
            width="100%",
            background="#050505",
        ),
        width="100%",
    )

app = rx.App()
app.add_page(index, on_load=State.fetch_trending)