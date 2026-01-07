import reflex as rx
from .state import UserState, MovieState, FilterState
from .login_view import login_page

def main_app_layout():
    return rx.flex(
        sidebar(), # Funcția ta de sidebar
        rx.box(
            rx.vstack(
                rx.cond(
                    MovieState.is_loading, 
                    rx.center(rx.spinner(color="#ff0000")),
                    rx.grid(
                        rx.foreach(MovieState.movies, movie_card), # Cardurile tale
                        columns=rx.breakpoints(initial="1", sm="2", lg="3"),
                        spacing="8"
                    )
                )
            ),
            flex="1", margin_left="320px", padding="5em"
        ),
        background="black", min_height="100vh"
    )

@rx.page(route="/", on_load=MovieState.fetch_movies)
def index():
    return rx.cond(
        UserState.is_logged_in,
        main_app_layout(),
        login_page()
    )