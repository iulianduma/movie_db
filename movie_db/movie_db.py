import reflex as rx
from .state import UserState, MovieState, FilterState
from .login_view import login_page

def movie_card(m: rx.Var[dict]):
    return rx.card(
        rx.vstack(
            # Corecție TypeError: folosim rx.format pentru concatenare în frontend
            rx.image(
                src=rx.format("https://image.tmdb.org/t/p/w500{0}", m["poster_path"]),
                height="250px", 
                object_fit="cover"
            ),
            rx.vstack(
                rx.heading(m["title"], size="3"),
                rx.text(rx.format("⭐ {0}", m["vote_average"]), color="yellow"),
                rx.text(m["overview"], size="1", line_clamp=3, color="#888"),
                rx.hstack(
                    rx.button("Later", size="1", on_click=lambda: MovieState.toggle_movie(m, "watchlist")),
                    rx.button("Văzut", size="1", color_scheme="ruby", on_click=lambda: MovieState.toggle_movie(m, "watched")),
                ),
                padding="10px",
            )
        ),
        width="100%",
        background="#111"
    )

def main_layout():
    return rx.flex(
        rx.vstack(
            rx.heading("MOVIE_DB", color="red", size="6"),
            rx.button("Discover", on_click=lambda: [FilterState.set_show_mode("Discover"), MovieState.fetch_movies], width="100%"),
            rx.button("Watchlist", on_click=lambda: [FilterState.set_show_mode("Watchlist"), MovieState.fetch_movies], width="100%"),
            rx.button("Logout", on_click=UserState.logout, variant="ghost", width="100%"),
            width="250px", padding="20px", height="100vh", border_right="1px solid #222", spacing="4"
        ),
        rx.box(
            rx.cond(
                MovieState.is_loading,
                rx.center(rx.spinner(), width="100%", height="50vh"),
                rx.grid(
                    rx.foreach(MovieState.movies, movie_card),
                    columns=rx.breakpoints(initial="1", sm="2", lg="3"), 
                    spacing="4", 
                    padding="20px"
                )
            ),
            flex="1"
        ),
        background="black", min_height="100vh"
    )

@rx.page(route="/", on_load=MovieState.fetch_movies)
def index():
    return rx.cond(
        UserState.is_logged_in,
        main_layout(),
        login_page()
    )

app = rx.App()