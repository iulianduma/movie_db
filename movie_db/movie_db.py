import reflex as rx
from .state import MovieState

def movie_card(m: rx.Var[dict]):
    return rx.card(
        rx.vstack(
            rx.image(src=m["poster_path"], height="250px", width="100%", object_fit="cover"),
            rx.vstack(
                rx.heading(m["title"], size="3", line_clamp=1),
                rx.badge("⭐ " + m["vote_average"].to_string(), color_scheme="yellow"),
                rx.text(m["overview"], size="1", line_clamp=2, color="#aaa"),
                padding="10px", spacing="1"
            ),
        ), background="#111", border="1px solid #222", padding="0"
    )

def sidebar():
    return rx.vstack(
        rx.heading("MOVIE_DB", color="red", size="7"),
        rx.input(placeholder="Caută...", on_change=MovieState.set_search_query),
        rx.button("CAUTĂ", on_click=MovieState.fetch_movies, width="100%", color_scheme="ruby"),
        rx.divider(),
        rx.text("ANI", size="1"),
        rx.hstack(rx.input(placeholder="Din", on_blur=MovieState.set_y_start), rx.input(placeholder="La", on_blur=MovieState.set_y_end)),
        rx.divider(),
        rx.text("RATING MINIM", size="1"),
        rx.slider(default_value=[0], min=0, max=10, on_change=MovieState.set_min_rating, width="100%"),
        width="280px", height="100vh", padding="2em", background="#050505", position="fixed"
    )

def index():
    return rx.flex(
        sidebar(),
        rx.box(
            rx.cond(MovieState.is_loading, rx.center(rx.spinner()),
                rx.grid(rx.foreach(MovieState.movies, movie_card), columns=rx.breakpoints(initial="1", sm="2", lg="4"), spacing="4")
            ), flex="1", margin_left="280px", padding="2em"
        ), background="black", min_height="100vh"
    )

app = rx.App()
app.add_page(index, on_load=MovieState.fetch_movies)